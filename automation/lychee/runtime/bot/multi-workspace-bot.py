#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-telegram-bot[rate-limiter]>=21.0",
#     "jsonschema>=4.0.0",
# ]
# ///
"""
Multi-Workspace Telegram Bot - Workflow Orchestration

Processes session summaries, notifications, and completion files.
Presents dynamic workflow menu based on trigger conditions.
Polls Telegram API for button clicks with idle timeout.
Auto-shuts down after 10 minutes of inactivity.

Version: 4.0.0
Specification: ~/.claude/specifications/telegram-workflows-orchestration-v4.yaml

Changes from v3.0.0:
- Loads workflow registry from workflows.json
- Scans summaries/ directory for SessionSummary files
- Filters workflows by triggers (lychee_errors, git_modified, always)
- Builds dynamic keyboard with available workflows
- Handles workflow selections and creates selection files
- Maintains dual-mode: summaries (v4) + notifications (v3 backward compat)
"""

import asyncio
import json
import os
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, AIORateLimiter

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Configuration
STATE_DIR = Path.home() / ".claude" / "automation" / "lychee" / "state"
NOTIFICATION_DIR = STATE_DIR / "notifications"
APPROVAL_DIR = STATE_DIR / "approvals"
COMPLETION_DIR = STATE_DIR / "completions"
SUMMARIES_DIR = STATE_DIR / "summaries"  # Phase 3 - v4.0.0
SELECTIONS_DIR = STATE_DIR / "selections"  # Phase 3 - v4.0.0
EXECUTIONS_DIR = STATE_DIR / "executions"  # Phase 4 - WorkflowExecution results
PROGRESS_DIR = STATE_DIR / "progress"  # Phase 4 - P2 streaming progress
TRACKING_DIR = STATE_DIR / "tracking"  # Phase 4 - Progress tracking persistence
PID_FILE = STATE_DIR / "bot.pid"
WORKFLOWS_REGISTRY = STATE_DIR / "workflows.json"  # Phase 3 - v4.0.0

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

IDLE_TIMEOUT_SECONDS = 1800  # 30 minutes
POLL_INTERVAL = 1.0  # seconds
POLL_TIMEOUT = 10  # API request timeout
PROGRESS_POLL_INTERVAL = 2.0  # Progress updates every 2 seconds

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID", file=sys.stderr)
    sys.exit(1)

# Import workspace helpers and state management
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from workspace_helpers import (
    load_registry,
    get_workspace_id_from_path,
    compute_workspace_hash,
    create_callback_data,
    resolve_callback_data,
    cleanup_expired_files,
    STATE_TTL_MINUTES
)
from format_utils import (
    format_git_status_compact,
    format_repo_display,
    escape_markdown,
    get_workspace_config
)
from workflow_utils import (
    load_workflow_registry,
    filter_workflows_by_triggers
)
from bot_utils import (
    log_event,
    create_pid_file,
    cleanup_pid_file
)
from message_builders import (
    build_workflow_start_message
)
import bot_state
from bot_state import (
    update_activity,
    get_idle_time
)


def signal_handler(signum: int, frame) -> None:
    """Handle termination signals."""
    sig_name = signal.Signals(signum).name
    print(f"\n🛑 Received {sig_name}, shutting down...")
    bot_state.shutdown_requested = True


class BaseHandler:
    """Base class for all file-based handlers with shared functionality."""

    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

    def _cleanup_file(self, file_path: Path, file_type: str = "file") -> None:
        """
        Delete consumed file.

        Args:
            file_path: Path to file to delete
            file_type: Human-readable file type for logging
        """
        try:
            file_path.unlink()
            print(f"🗑️  Consumed: {file_path.name}")
        except FileNotFoundError:
            pass


class NotificationHandler(BaseHandler):
    """Handles notification requests from any workspace."""

    async def send_notification(self, notification_file: Path) -> None:
        """
        Send Telegram notification with workspace identification.

        Args:
            notification_file: Path to notification request JSON

        Raises:
            All errors propagate to caller
        """
        try:
            # Read notification request
            request = self._read_notification(notification_file)

            # Extract correlation ID for distributed tracing
            correlation_id = request.get("correlation_id", "unknown")
            session_id = request["session_id"]
            workspace_path = Path(request["workspace_path"])
            workspace_hash = compute_workspace_hash(workspace_path)

            # Log notification received event
            log_event(
                correlation_id,
                workspace_hash,
                session_id,
                "bot",
                "notification.received",
                {"notification_file": notification_file.name, "error_count": request["error_count"]}
            )

            # Load workspace config (with fallback for unregistered workspaces)
            config = get_workspace_config(workspace_path=workspace_path, include_name=True)
            emoji = config["emoji"]
            ws_name = config["name"]

            # Fallback workspace_id if not in registry
            try:
                workspace_id = get_workspace_id_from_path(workspace_path)
            except (ValueError, FileNotFoundError, KeyError):
                workspace_id = request.get("workspace_hash", "unknown")

            error_count = request["error_count"]
            details = request["details"]

            # Parse error_details for file-level breakdown (progressive disclosure)
            details_lines = []
            if "error_details" in request and request["error_details"]:
                error_details_str = request["error_details"]
                for line in error_details_str.strip().split('\n'):
                    if ':' in line:
                        file_path, count = line.split(':', 1)
                        # Shorten path relative to workspace
                        short_path = file_path.replace(str(workspace_path), '').lstrip('/')
                        details_lines.append(f"• {short_path} ({count} errors)")

            # Format files affected section
            files_section = ""
            if details_lines:
                files_section = f"\n\nFiles affected:\n" + '\n'.join(details_lines)

            message = f"""{emoji} **Link Validation** - {ws_name}

**Workspace**: `{workspace_path}`
**Session**: `{session_id}`

{details}{files_section}

Choose action:
"""

            # Create buttons with hash-mapped callbacks (including correlation_id)
            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ Auto-Fix All",
                        callback_data=create_callback_data(
                            workspace_id=workspace_id,
                            workspace_path=str(workspace_path),
                            session_id=session_id,
                            action="auto_fix_all",
                            correlation_id=correlation_id
                        )
                    ),
                    InlineKeyboardButton(
                        "❌ Reject",
                        callback_data=create_callback_data(
                            workspace_id=workspace_id,
                            workspace_path=str(workspace_path),
                            session_id=session_id,
                            action="reject",
                            correlation_id=correlation_id
                        )
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📋 View Details",
                        callback_data=create_callback_data(
                            workspace_id=workspace_id,
                            workspace_path=str(workspace_path),
                            session_id=session_id,
                            action="view_details",
                            correlation_id=correlation_id
                        )
                    )
                ]
            ]

            # Send message (AIORateLimiter handles rate limiting automatically)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

            print(f"📤 Sent notification for {workspace_id} ({session_id})")
            update_activity()  # Track activity for idle timeout

            # Log notification processed event
            log_event(
                correlation_id,
                workspace_hash,
                session_id,
                "bot",
                "notification.processed",
                {"workspace_id": workspace_id}
            )

        finally:
            # Cleanup consumed notification
            self._cleanup_file(notification_file)

    def _read_notification(self, notification_file: Path) -> Dict[str, Any]:
        """Read and validate notification request."""
        with notification_file.open() as f:
            request = json.load(f)

        # Validate required fields
        required = ["workspace_path", "session_id", "error_count", "details", "timestamp"]
        missing = [f for f in required if f not in request]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return request



class CompletionHandler(BaseHandler):
    """Handles completion notifications from orchestrator."""

    async def send_completion(self, completion_file: Path) -> None:
        """
        Send Telegram completion notification.

        Args:
            completion_file: Path to completion notification JSON

        Raises:
            All errors propagate to caller
        """
        session_id = None
        workspace_id = None

        try:
            print(f"🔄 Processing completion: {completion_file.name}")

            # Read completion notification
            print(f"   📖 Reading completion file...")
            completion = self._read_completion(completion_file)
            session_id = completion.get("session_id", "unknown")
            workspace_id = completion.get("workspace_id", "unknown")

            print(f"   ✓ Loaded: workspace={workspace_id}, session={session_id}, status={completion.get('status')}")

            # Load workspace config (with fallback for unregistered workspaces)
            workspace_path = Path(completion.get("workspace_path", "/unknown"))
            config = get_workspace_config(workspace_id=workspace_id, workspace_path=workspace_path, verbose=True)
            emoji = config["emoji"]

            # Format message based on status
            print(f"   ✍️  Formatting completion message...")
            message = self._format_completion_message(completion, emoji)
            print(f"   ✓ Message formatted ({len(message)} chars)")

            # Send message with rate limiting and markdown safety
            print(f"   📡 Sending to Telegram (chat_id={self.chat_id})...")
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown"
            )

            print(f"📤 ✅ Sent completion for {workspace_id} ({session_id})")
            update_activity()  # Track activity for idle timeout

        except Exception as e:
            error_msg = f"❌ Failed to send completion"
            if workspace_id:
                error_msg += f" for {workspace_id}"
            if session_id:
                error_msg += f" ({session_id})"
            error_msg += f": {type(e).__name__}: {e}"
            print(error_msg, file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Re-raise to let caller handle
            raise

        finally:
            # Cleanup consumed completion
            self._cleanup_file(completion_file)

    def _read_completion(self, completion_file: Path) -> Dict[str, Any]:
        """Read and validate completion notification."""
        with completion_file.open() as f:
            completion = json.load(f)

        # Validate required fields
        required = ["workspace_id", "session_id", "status", "exit_code",
                   "duration_seconds", "summary", "timestamp"]
        missing = [f for f in required if f not in completion]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return completion

    def _format_completion_message(self, completion: Dict[str, Any], emoji: str) -> str:
        """Format completion data as Telegram message."""
        status = completion["status"]
        workspace_id = completion["workspace_id"]
        session_id = completion["session_id"]
        duration = completion["duration_seconds"]
        summary = completion["summary"]
        exit_code = completion["exit_code"]

        # Choose emoji and title based on status
        if status == "success":
            status_emoji = "✅"
            title = "Auto-Fix Completed"
            status_line = f"**Duration**: {duration}s"
        elif status == "error":
            status_emoji = "❌"
            title = "Auto-Fix Failed"
            status_line = f"**Duration**: {duration}s | **Exit Code**: {exit_code}"
        elif status == "timeout":
            status_emoji = "⏱️"
            title = "Auto-Fix Timeout"
            status_line = f"**Duration**: {duration}s (limit reached)"
        else:
            status_emoji = "⚠️"
            title = "Unknown Status"
            status_line = f"**Status**: {status}"

        message = f"""{emoji} {status_emoji} **{title}**

**Workspace**: `{workspace_id}`
**Session**: `{session_id}`
{status_line}

**Summary**:
{summary}
"""

        # Add stdout for success cases (truncated to avoid huge messages)
        if status == "success" and completion.get("stdout"):
            stdout = completion["stdout"].strip()
            if stdout:
                # Extract readable content from JSON (if applicable)
                readable_content = stdout
                try:
                    result_data = json.loads(stdout)
                    if isinstance(result_data, dict) and 'result' in result_data:
                        readable_content = result_data['result']
                except json.JSONDecodeError:
                    pass  # Use raw output if not JSON

                # Truncate to 500 chars
                if len(readable_content) > 500:
                    readable_content = readable_content[:500] + "..."

                message += f"\n**Details**:\n```\n{readable_content}\n```"

        # Add stderr for error cases (truncated to avoid huge messages)
        if status == "error" and completion.get("stderr"):
            stderr = completion["stderr"].strip()
            if stderr:
                # Truncate to 500 chars
                if len(stderr) > 500:
                    stderr = stderr[:500] + "..."

                message += f"\n**Error**:\n```\n{stderr}\n```"

        return message



class WorkflowExecutionHandler(BaseHandler):
    """
    Handles workflow execution completion notifications (Phase 4 - v4.0.0).

    Sends final completion messages WITHOUT buttons after workflows complete.
    Key distinction: Stop hook messages have workflow selection buttons,
    execution completions show results only.
    """

    async def send_execution_completion(self, execution_file: Path) -> None:
        """
        Send Telegram execution completion message (no buttons).

        Args:
            execution_file: Path to WorkflowExecution JSON

        Raises:
            All errors propagate to caller
        """
        session_id = None
        workspace_id = None

        try:
            print(f"🔄 Processing execution: {execution_file.name}")

            # Read execution notification
            print(f"   📖 Reading execution file...")
            execution = self._read_execution(execution_file)
            session_id = execution.get("session_id", "unknown")
            workspace_id = execution.get("workspace_id", "unknown")
            workflow_id = execution.get("workflow_id", "unknown")
            workflow_name = execution.get("workflow_name", "unknown")

            print(f"   ✓ Loaded: workspace={workspace_id}, session={session_id}, workflow={workflow_id}, status={execution.get('status')}")

            # Load workspace config (with fallback for unregistered workspaces)
            workspace_path = Path(execution.get("workspace_path", "/unknown"))
            config = get_workspace_config(workspace_id=workspace_id, workspace_path=workspace_path, verbose=True)
            emoji = config["emoji"]

            # Phase 3: Check if we're tracking this workflow (single-message pattern)
            progress_key = (workspace_id, session_id, workflow_id)
            status = execution["status"]
            duration = execution.get("duration_seconds", 0)

            if progress_key in bot_state.active_progress_updates:
                # Single-message pattern: replace document in existing progress message
                tracking_context = bot_state.active_progress_updates[progress_key]
                message_id = tracking_context["message_id"]
                git_branch = tracking_context.get("git_branch", "unknown")
                repository_root = tracking_context.get("repository_root", "unknown")
                working_dir = tracking_context.get("working_directory", ".")
                workflow_name = tracking_context.get("workflow_name", workflow_id)
                git_modified = tracking_context.get("git_modified", 0)
                git_untracked = tracking_context.get("git_untracked", 0)
                git_staged = tracking_context.get("git_staged", 0)

                # Replace home directory with ~ for cleaner display
                repo_display = format_repo_display(repository_root)

                print(f"   📝 Updating tracked message (message_id={message_id})")

                # Build final caption
                status_emoji_map = {"success": "✅", "error": "❌", "timeout": "⏱️"}
                status_emoji = status_emoji_map.get(status, "❓")

                # Extract summary from execution
                summary = "Workflow completed"
                if status == "success" and execution.get("stdout"):
                    stdout = execution["stdout"].strip()
                    if stdout:
                        lines = [l.strip() for l in stdout.split('\n') if l.strip()]
                        summary = lines[0] if lines else "Workflow completed"
                        if len(summary) > 100:
                            summary = summary[:97] + "..."

                # Build git status line
                # Compact git status (always show all counters)
                git_status_line = format_git_status_compact(git_modified, git_staged, git_untracked)

                # Build session info (show both original + headless)
                headless_session_id = execution.get("headless_session_id")
                if headless_session_id:
                    session_info = f"**Session**: `{session_id}`\n**Headless**: `{headless_session_id}`"
                else:
                    session_info = f"**Session**: `{session_id}`"

                final_caption = (
                    f"{status_emoji} **Workflow: {workflow_name}**\n\n"
                    f"**Repository**: `{repo_display}`\n"
                    f"**Directory**: `{working_dir}`\n"
                    f"**Branch**: `{git_branch}`\n"
                    f"**↯**: {git_status_line}\n\n"
                    f"{session_info}\n"
                    f"**Status**: {status}\n"
                    f"**Duration**: {duration}s\n"
                    f"**Output**: {summary}"
                )

                # Update message text with final status
                print(f"   📝 Updating message with final status...")
                await self.bot.edit_message_text(
                    chat_id=self.chat_id,
                    message_id=message_id,
                    text=final_caption,
                    parse_mode="Markdown"
                )
                print(f"   ✅ Message updated successfully")

                # Cleanup tracking (memory + file)
                del bot_state.active_progress_updates[progress_key]

                # Remove tracking file
                tracking_file = TRACKING_DIR / f"{workspace_id}_{session_id}_{workflow_id}_tracking.json"
                if tracking_file.exists():
                    tracking_file.unlink()
                    print(f"   🗑️  Progress tracking cleaned up (memory + file)")
                else:
                    print(f"   🗑️  Progress tracking cleaned up (memory only)")

            else:
                # No active progress tracking - this shouldn't happen in normal operation
                print(f"   ⚠️  WARNING: No progress tracking found for {progress_key}")
                print(f"   Execution completion will not be sent (single-message mode requires tracking)")
                print(f"   This may indicate the workflow selection didn't initialize tracking properly")

            print(f"📤 ✅ Sent execution completion for {workspace_id} ({session_id}): {workflow_name}")
            update_activity()  # Track activity for idle timeout

        except Exception as e:
            error_msg = f"❌ Failed to send execution completion"
            if workspace_id:
                error_msg += f" for {workspace_id}"
            if session_id:
                error_msg += f" ({session_id})"
            error_msg += f": {type(e).__name__}: {e}"
            print(error_msg, file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Re-raise to let caller handle
            raise

        finally:
            # Cleanup consumed execution
            self._cleanup_file(execution_file)

    def _read_execution(self, execution_file: Path) -> Dict[str, Any]:
        """Read and validate WorkflowExecution file."""
        with execution_file.open() as f:
            execution = json.load(f)

        # Validate required fields
        required = ["correlation_id", "workspace_id", "session_id", "workflow_id",
                   "workflow_name", "status", "exit_code", "duration_seconds", "timestamp"]
        missing = [f for f in required if f not in execution]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return execution

    def _format_execution_message(self, execution: Dict[str, Any], emoji: str, workflow_name: str) -> str:
        """Format WorkflowExecution data as Telegram message (no buttons)."""
        status = execution["status"]
        workspace_id = execution["workspace_id"]
        session_id = execution["session_id"]
        duration = execution["duration_seconds"]
        exit_code = execution["exit_code"]

        # Get workflow metadata
        metadata = execution.get("metadata", {})
        workflow_icon = metadata.get("icon", "📋")
        full_workflow_name = f"{workflow_icon} {workflow_name}"

        # Choose emoji and title based on status
        if status == "success":
            status_emoji = "✅"
            title = "Workflow Completed"
            status_line = f"**Duration**: {duration}s"
        elif status == "error":
            status_emoji = "❌"
            title = "Workflow Failed"
            status_line = f"**Duration**: {duration}s | **Exit Code**: {exit_code}"
        elif status == "timeout":
            status_emoji = "⏱️"
            title = "Workflow Timeout"
            status_line = f"**Duration**: {duration}s (limit reached)"
        else:
            status_emoji = "⚠️"
            title = "Unknown Status"
            status_line = f"**Status**: {status}"

        message = f"""{emoji} {status_emoji} **{title}**

**Workflow**: {full_workflow_name}
**Workspace**: `{workspace_id}`
**Session**: `{session_id}`
{status_line}
"""

        # Add stdout for success cases (truncated)
        if status == "success" and execution.get("stdout"):
            stdout = execution["stdout"].strip()
            if stdout:
                # Extract readable content from JSON (if applicable)
                readable_content = stdout
                try:
                    result_data = json.loads(stdout)
                    if isinstance(result_data, dict) and 'result' in result_data:
                        readable_content = result_data['result']
                except json.JSONDecodeError:
                    pass  # Use raw output if not JSON

                # Get first meaningful line as summary
                lines = [l.strip() for l in readable_content.split('\n') if l.strip()]
                summary = lines[0] if lines else "Completed"

                # Truncate if too long
                if len(summary) > 200:
                    summary = summary[:200] + "..."

                message += f"\n**Summary**: {summary}"

        # Add stderr for error cases (truncated)
        if status == "error" and execution.get("stderr"):
            stderr = execution["stderr"].strip()
            if stderr:
                # Get first line only
                error_lines = stderr.split('\n')
                error_preview = error_lines[0] if error_lines else stderr

                # Truncate if too long
                if len(error_preview) > 200:
                    error_preview = error_preview[:200] + "..."

                message += f"\n**Error**: {error_preview}"

        return message



class SummaryHandler(BaseHandler):
    """
    Handles session summaries and presents workflow menu (Phase 3 - v4.0.0).

    Filters workflows by triggers, builds dynamic keyboard, handles selections.
    """

    async def send_workflow_menu(self, summary_file: Path) -> None:
        """
        Send workflow menu based on session summary.

        Args:
            summary_file: Path to SessionSummary JSON

        Raises:
            All errors propagate to caller
        """
        try:
            # Read and validate summary
            summary = self._read_summary(summary_file)

            # Extract metadata
            correlation_id = summary.get("correlation_id", "unknown")
            session_id = summary["session_id"]
            workspace_path = Path(summary["workspace_path"])
            workspace_hash = summary["workspace_id"]

            # Log summary received event
            log_event(
                correlation_id,
                workspace_hash,
                session_id,
                "bot",
                "summary.received",
                {"summary_file": summary_file.name}
            )

            # Filter available workflows
            available_workflows = filter_workflows_by_triggers(bot_state.workflow_registry, summary)

            if not available_workflows:
                print(f"⚠️  No workflows available for session {session_id} (no triggers matched)")
                # Don't send message if no workflows available
                return

            # Always compute workspace hash for tracking consistency
            workspace_hash = compute_workspace_hash(workspace_path)

            # ALWAYS use workspace hash for tracking consistency
            # (Execution files from orchestrator use hash, so tracking must too)
            workspace_id = workspace_hash
            print(f"   🔍 DEBUG: workspace_hash={workspace_hash}, workspace_id={workspace_id}")

            # Load workspace config for display only (emoji, name)
            config = get_workspace_config(workspace_path=workspace_path, include_name=True)
            emoji = config["emoji"]
            ws_name = config["name"]

            # Format message with session context
            lychee_status = summary.get("lychee_status", {})
            git_status = summary.get("git_status", {})
            duration = summary.get("duration_seconds", 0)

            # Extract repository root and working directory (industry standard distinction)
            repository_root = summary.get("repository_root", str(workspace_path))
            working_dir = summary.get("working_directory", ".")

            # Extract user prompt and last response BEFORE caching
            user_prompt = summary.get("last_user_prompt", "")
            last_response = summary.get("last_response", "Session completed")

            # Cache summary data for workflow selection (needed because we delete summary file)
            cache_key = (workspace_id, session_id)
            bot_state.summary_cache[cache_key] = {
                "session_id": session_id,
                "correlation_id": correlation_id,
                "git_status": git_status,
                "lychee_status": lychee_status,
                "workspace_path": str(workspace_path),
                "duration_seconds": duration,
                "repository_root": repository_root,
                "working_directory": working_dir,
                "last_user_prompt": user_prompt,
                "last_response": last_response
            }
            print(f"   📦 Cached summary for {cache_key}")

            # Build git porcelain display (up to 10 lines)
            git_porcelain_lines = git_status.get('porcelain', [])
            git_porcelain_display = ""
            if git_porcelain_lines:
                # Limit to first 10 lines to avoid huge messages
                display_lines = git_porcelain_lines[:10]
                porcelain_text = "\n".join(display_lines)
                if len(git_porcelain_lines) > 10:
                    porcelain_text += f"\n... and {len(git_porcelain_lines) - 10} more"
                # Wrap in code block for proper formatting
                git_porcelain_display = f"\n```\n{porcelain_text}\n```"

            # Replace home directory with ~ for cleaner display
            repo_display = format_repo_display(repository_root)

            # Process user prompt for display (truncate and escape)
            if user_prompt:
                # Truncate if too long
                if len(user_prompt) > 100:
                    user_prompt = user_prompt[:97] + "..."
                # Escape markdown
                user_prompt = escape_markdown(user_prompt)

            # Process last response for display (truncate and escape)
            # Truncate if too long, keep first line
            if len(last_response) > 100:
                last_response = last_response[:97] + "..."
            # Escape markdown
            last_response = escape_markdown(last_response)

            # Build compact git status line (always show all counters)
            modified = git_status.get('modified_files', 0)
            staged = git_status.get('staged_files', 0)
            untracked = git_status.get('untracked_files', 0)

            # Show all counters even when zero for clarity
            git_compact = format_git_status_compact(modified, staged, untracked)

            # Escape lychee details
            lychee_details = lychee_status.get('details', 'Not run')
            lychee_details = escape_markdown(lychee_details)

            # Build message with user prompt as first line if available
            prompt_line = f"❓ _{user_prompt}_\n" if user_prompt else ""

            message = f"""{prompt_line}{emoji} **{last_response}**

`{repo_display}` | `{working_dir}`
`{session_id}` ({duration}s)
**↯**: `{git_status.get('branch', 'unknown')}` | {git_compact}{git_porcelain_display}

**Lychee**: {lychee_details}

**Available Workflows** ({len(available_workflows)}):
"""

            # Build dynamic keyboard
            print(f"   🔍 DEBUG: Before _build_workflow_keyboard, workspace_id={workspace_id}")
            keyboard = self._build_workflow_keyboard(
                available_workflows,
                workspace_id,
                workspace_path,
                session_id,
                correlation_id
            )

            # Send message (AIORateLimiter handles rate limiting automatically)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

            print(f"📤 Sent workflow menu for {workspace_id} ({session_id}): {len(available_workflows)} workflows")
            update_activity()

            # Log summary processed event
            log_event(
                correlation_id,
                workspace_hash,
                session_id,
                "bot",
                "summary.processed",
                {"workspace_id": workspace_id, "workflows_count": len(available_workflows)}
            )

        finally:
            # Cleanup consumed summary
            self._cleanup_file(summary_file)

    def _read_summary(self, summary_file: Path) -> Dict[str, Any]:
        """Read and validate session summary."""
        try:
            with summary_file.open() as f:
                content = f.read()
                summary = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON PARSE ERROR in {summary_file.name}:")
            print(f"   Error: {e}")
            print(f"   File content:")
            for i, line in enumerate(content.split('\n'), 1):
                marker = " <-- ERROR" if i == e.lineno else ""
                print(f"   {i:3d}: {line}{marker}")
            raise

        # Validate required fields
        required = ["correlation_id", "workspace_path", "workspace_id", "session_id",
                   "timestamp", "duration_seconds", "git_status", "lychee_status"]
        missing = [f for f in required if f not in summary]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return summary

    def _build_workflow_keyboard(
        self,
        workflows: list[Dict[str, Any]],
        workspace_id: str,
        workspace_path: Path,
        session_id: str,
        correlation_id: str
    ) -> list[list[InlineKeyboardButton]]:
        """
        Build dynamic workflow keyboard with custom prompt option.

        Returns:
            Telegram keyboard layout (list of button rows)
        """
        keyboard = []

        # Add workflow buttons (2 per row for compact layout)
        for i in range(0, len(workflows), 2):
            row = []
            for workflow in workflows[i:i+2]:
                row.append(
                    InlineKeyboardButton(
                        f"{workflow['icon']} {workflow['name']}",
                        callback_data=create_callback_data(
                            workspace_id=workspace_id,
                            workspace_path=str(workspace_path),
                            session_id=session_id,
                            action=f"workflow_{workflow['id']}",
                            correlation_id=correlation_id
                        )
                    )
                )
            keyboard.append(row)

        # Add custom prompt option (always available)
        keyboard.append([
            InlineKeyboardButton(
                "✏️ Custom Prompt",
                callback_data=create_callback_data(
                    workspace_id=workspace_id,
                    workspace_path=str(workspace_path),
                    session_id=session_id,
                    action="custom_prompt",
                    correlation_id=correlation_id
                )
            )
        ])

        return keyboard


async def handle_view_details(query, workspace_path: str, session_id: str, correlation_id: str):
    """
    Handle "View Details" button click - send detailed error breakdown.

    Args:
        query: Telegram CallbackQuery object
        workspace_path: Absolute path to workspace
        session_id: Session identifier
        correlation_id: Correlation ID for tracing

    Raises:
        All errors propagate (fail-fast)
    """
    await query.answer("Loading details...")

    # Read lychee JSON output for structured errors
    json_results = Path(workspace_path) / ".lychee-results.json"

    if not json_results.exists():
        await query.message.reply_text(
            "❌ Detailed results not available\n\n"
            "The lychee JSON output file was not found. This may happen if:\n"
            "• Validation was run before progressive disclosure was implemented\n"
            "• Results file was manually deleted\n"
            "• Workspace path changed",
            parse_mode="Markdown"
        )
        return

    try:
        with open(json_results, 'r') as f:
            lychee_data = json.load(f)
    except json.JSONDecodeError as e:
        await query.message.reply_text(
            f"❌ Failed to parse lychee JSON output\n\n"
            f"Error: {e}\n\n"
            f"File: `{json_results}`",
            parse_mode="Markdown"
        )
        raise  # Fail-fast

    # Format error_map as readable text
    error_map = lychee_data.get("error_map", {})

    if not error_map:
        await query.message.reply_text(
            "✅ No detailed errors found\n\n"
            "The error_map is empty. All links may have been fixed.",
            parse_mode="Markdown"
        )
        return

    # Build detailed breakdown
    details_lines = []
    for file_path, errors in error_map.items():
        # Shorten path relative to workspace
        short_path = file_path.replace(workspace_path, '').lstrip('/')
        details_lines.append(f"\n**{short_path}** ({len(errors)} errors):")

        for error in errors[:5]:  # Limit to 5 errors per file to avoid huge messages
            url = error.get("url", "unknown")
            status = error.get("status", {})
            error_text = status.get("text", "Unknown error")

            # Shorten URL for display
            display_url = url.replace("file://", "").replace(workspace_path, "...")
            details_lines.append(f"  • `{display_url}`")
            details_lines.append(f"    {error_text}")

        if len(errors) > 5:
            details_lines.append(f"  ... and {len(errors) - 5} more errors")

    details_text = '\n'.join(details_lines)

    # Truncate if too long (Telegram has 4096 char limit for messages)
    if len(details_text) > 3800:
        details_text = details_text[:3800] + "\n\n... (truncated)"

    await query.message.reply_text(
        f"📋 **Detailed Error Breakdown**\n{details_text}",
        parse_mode='Markdown'
    )

    print(f"📋 Sent detailed breakdown for session {session_id}")


async def handle_workflow_selection(
    query,
    workspace_id: str,
    workspace_path: str,
    session_id: str,
    action: str,
    correlation_id: str,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle workflow selection button click (Phase 3 - v4.0.0).

    Creates WorkflowSelection file for orchestrator to process.

    Args:
        query: Telegram CallbackQuery object
        workspace_id: Workspace identifier
        workspace_path: Absolute path to workspace
        session_id: Session identifier
        action: Selected action (workflow_<id> or custom_prompt)
        correlation_id: Correlation ID for tracing
        context: Bot context for accessing bot instance

    Raises:
        All errors propagate (fail-fast)
    """
    workspace_hash = compute_workspace_hash(Path(workspace_path))

    # Extract workflow ID from action
    if action == "custom_prompt":
        # TODO Phase 4: Implement custom prompt handler
        # For now, acknowledge and return
        await query.edit_message_text(
            text="✏️ Custom Prompt\n\n"
                 "Custom workflow prompts will be available in Phase 4.\n"
                 "For now, please select a preset workflow.",
            parse_mode="Markdown"
        )
        return

    workflow_id = action.replace("workflow_", "")

    # Create selection file
    selection_file = SELECTIONS_DIR / f"selection_{session_id}_{workspace_hash}.json"

    # Retrieve cached summary data (needed for orchestrator prompt rendering)
    cache_key = (workspace_id, session_id)
    summary_data = bot_state.summary_cache.get(cache_key)
    if not summary_data:
        print(f"   ⚠️  Summary not found in cache for {cache_key}, orchestrator may fail")
        summary_data = {}

    selection_state = {
        "workspace_path": workspace_path,
        "workspace_id": workspace_hash,
        "session_id": session_id,
        "workflows": [workflow_id],  # Single workflow for Phase 3 (multi-select in future)
        "correlation_id": correlation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary_data": summary_data,  # Include cached summary for orchestrator
        "metadata": {
            "workspace_name": workspace_id,
            "callback_id": query.data
        }
    }

    SELECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    selection_file.write_text(json.dumps(selection_state, indent=2))

    print(f"✅ Selection file written: {selection_file.name}")

    # Log selection created event
    log_event(
        correlation_id,
        workspace_hash,
        session_id,
        "bot",
        "selection.created",
        {"workflow_id": workflow_id, "selection_file": selection_file.name}
    )

    # Start orchestrator in background to process selection
    orchestrator_script = Path.home() / ".claude" / "automation" / "lychee" / "runtime" / "orchestrator" / "multi-workspace-orchestrator.py"
    print(f"🚀 Starting orchestrator: {orchestrator_script}")

    try:
        # Start orchestrator in background (one-shot execution)
        # Propagate correlation_id via environment for distributed tracing
        env = os.environ.copy()
        env["CORRELATION_ID"] = correlation_id

        # Redirect stdout/stderr to orchestrator log file (avoid pipe blocking)
        log_file = Path.home() / ".claude" / "automation" / "lychee" / "logs" / "orchestrator.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a') as log_fd:
            process = await asyncio.create_subprocess_exec(
                str(orchestrator_script),
                str(selection_file),
                stdout=log_fd,
                stderr=log_fd,
                env=env
            )
            print(f"   ✓ Orchestrator started (PID: {process.pid})")
            # Don't wait for completion - orchestrator runs independently
    except Exception as e:
        print(f"   ❌ Failed to start orchestrator: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    # Confirm to user (with fallback for unregistered workspaces)
    config = get_workspace_config(workspace_id=workspace_id)
    emoji = config["emoji"]

    # Get workflow details and build confirmation message
    if bot_state.workflow_registry and workflow_id in bot_state.workflow_registry["workflows"]:
        workflow = bot_state.workflow_registry["workflows"][workflow_id]
        workflow_name = f"{workflow['icon']} {workflow['name']}"
    else:
        # Fallback for unknown workflow
        workflow_name = workflow_id

    # Build initial workflow message
    initial_message = build_workflow_start_message(
        emoji=emoji,
        workflow_name=workflow_name,
        session_id=session_id,
        summary_data=summary_data,
        workspace_path=workspace_path
    )

    # Delete the original callback message and send new tracking message
    await query.message.delete()
    sent_message = await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=initial_message,
        parse_mode="Markdown"
    )
    message_id = sent_message.message_id

    print(f"✅ Workflow selected: {workflow_id} for workspace: {workspace_id}")

    # Track message_id and context for progress updates
    # MUST use workspace_hash to match execution files from orchestrator
    progress_key = (workspace_hash, session_id, workflow_id)

    # Extract git context from cached summary
    git_branch = summary_data.get("git_status", {}).get("branch", "unknown")
    git_modified = summary_data.get("git_status", {}).get("modified_files", 0)
    git_untracked = summary_data.get("git_status", {}).get("untracked_files", 0)
    git_staged = summary_data.get("git_status", {}).get("staged_files", 0)

    # Extract repository root and working directory (industry standard)
    repository_root = summary_data.get("repository_root", summary_data.get("workspace_path", workspace_path))
    working_dir = summary_data.get("working_directory", ".")

    tracking_data = {
        "message_id": message_id,
        "workspace_id": workspace_hash,  # Use hash to match execution files
        "repository_root": repository_root,
        "working_directory": working_dir,
        "git_branch": git_branch,
        "git_modified": git_modified,
        "git_untracked": git_untracked,
        "git_staged": git_staged,
        "workflow_name": workflow_name if bot_state.workflow_registry and workflow_id in bot_state.workflow_registry["workflows"] else workflow_id,
        "session_id": session_id
    }

    bot_state.active_progress_updates[progress_key] = tracking_data

    # Persist tracking data to survive bot restarts (watchexec)
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    tracking_file = TRACKING_DIR / f"{workspace_hash}_{session_id}_{workflow_id}_tracking.json"  # Use hash in filename
    tracking_file.write_text(json.dumps(tracking_data, indent=2))
    print(f"   📌 Tracking progress updates (message_id={message_id}, branch={git_branch})")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Route callback to correct workspace.

    Args:
        update: Telegram update with callback query
        context: Bot context

    Raises:
        All errors propagate (will be caught by error handler)
    """
    query = update.callback_query
    await query.answer()  # Acknowledge immediately

    # Resolve callback to full context
    try:
        ctx = resolve_callback_data(query.data)
    except ValueError as e:
        await query.edit_message_text(text=f"❌ {e}", parse_mode="Markdown")
        return

    workspace_id = ctx["workspace_id"]
    workspace_path = ctx["workspace_path"]
    session_id = ctx["session_id"]
    action = ctx["action"]
    correlation_id = ctx.get("correlation_id", "unknown")

    print(f"📥 Callback received: {action} for {workspace_id} ({session_id})")

    # Handle "View Details" action separately (no orchestrator needed)
    if action == "view_details":
        await handle_view_details(query, workspace_path, session_id, correlation_id)
        update_activity()
        return

    # Phase 3 - v4.0.0: Handle workflow selection actions
    if action.startswith("workflow_") or action == "custom_prompt":
        await handle_workflow_selection(query, workspace_id, workspace_path, session_id, action, correlation_id, context)
        update_activity()
        return

    # Write approval state (v3 backward compatibility)
    workspace_hash = compute_workspace_hash(Path(workspace_path))
    approval_file = APPROVAL_DIR / f"approval_{session_id}_{workspace_hash}.json"

    approval_state = {
        "workspace_path": workspace_path,
        "session_id": session_id,
        "decision": action,
        "correlation_id": correlation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "workspace_hash": workspace_hash,
            "workspace_id": workspace_id,
            "callback_id": query.data
        }
    }

    APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
    approval_file.write_text(json.dumps(approval_state, indent=2))

    print(f"✅ Approval file written: {approval_file.name}")

    # Log approval created event
    log_event(
        correlation_id,
        workspace_hash,
        session_id,
        "bot",
        "approval.created",
        {"action": action, "approval_file": approval_file.name}
    )

    # Start orchestrator in background to process approval
    orchestrator_script = Path.home() / ".claude" / "automation" / "lychee" / "runtime" / "orchestrator" / "multi-workspace-orchestrator.py"
    print(f"🚀 Starting orchestrator: {orchestrator_script}")

    try:
        # Start orchestrator in background (one-shot execution)
        # Propagate correlation_id via environment for distributed tracing
        env = os.environ.copy()
        env["CORRELATION_ID"] = correlation_id

        process = await asyncio.create_subprocess_exec(
            str(orchestrator_script),
            str(approval_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        print(f"   ✓ Orchestrator started (PID: {process.pid})")
        # Don't wait for completion - orchestrator runs independently
    except Exception as e:
        print(f"   ❌ Failed to start orchestrator: {type(e).__name__}: {e}", file=sys.stderr)

    # Confirm to user (with fallback for unregistered workspaces)
    config = get_workspace_config(workspace_id=workspace_id)
    emoji = config["emoji"]

    await query.edit_message_text(
        text=f"{emoji} **Action Received**: {action}\n\n"
             f"Workspace: `{workspace_id}`\n"
             f"Session: `{session_id}`\n\n"
             f"Processing...",
        parse_mode="Markdown"
    )

    print(f"✅ Routed to workspace: {workspace_id}")
    update_activity()  # Track activity for idle timeout


async def _process_pending_files(
    directory: Path,
    file_pattern: str,
    handler_class: type,
    handler_method: str,
    file_type: str,
    app: Application
) -> None:
    """
    Generic processor for pending files on startup.

    Args:
        directory: Directory to scan
        file_pattern: Glob pattern for files (e.g., "notify_*.json")
        handler_class: Handler class to instantiate
        handler_method: Method name to call on handler
        file_type: Human-readable file type for logging
        app: Telegram Application instance
    """
    handler = handler_class(app.bot, int(CHAT_ID))

    # Check if directory exists
    if not directory.exists():
        print(f"📂 No {file_type} directory found")
        return

    # Scan for files
    files = sorted(directory.glob(file_pattern))
    if not files:
        print(f"📂 No pending {file_type}s")
        return

    print(f"📬 Found {len(files)} pending {file_type}(s)")
    for file in files:
        try:
            print(f"   Processing: {file.name}")
            # Call handler method dynamically
            await getattr(handler, handler_method)(file)
        except Exception as e:
            print(f"   ❌ Failed to process {file.name}: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)


async def process_pending_notifications(app: Application) -> None:
    """Process all pending notification files on startup."""
    await _process_pending_files(
        NOTIFICATION_DIR, "notify_*.json",
        NotificationHandler, "send_notification",
        "notification", app
    )


async def process_pending_completions(app: Application) -> None:
    """Process all pending completion files on startup."""
    await _process_pending_files(
        COMPLETION_DIR, "completion_*.json",
        CompletionHandler, "send_completion",
        "completion", app
    )


async def process_pending_executions(app: Application) -> None:
    """Process all pending execution files on startup."""
    await _process_pending_files(
        EXECUTIONS_DIR, "execution_*.json",
        WorkflowExecutionHandler, "send_execution_completion",
        "execution", app
    )


async def _scan_and_process(
    directory: Path,
    file_pattern: str,
    handler,
    handler_method: str,
    file_type: str
) -> None:
    """
    Scan directory for files and process with handler.

    Args:
        directory: Directory to scan
        file_pattern: Glob pattern for files
        handler: Handler instance
        handler_method: Method name to call
        file_type: File type name for logging
    """
    if not directory.exists():
        return

    files = sorted(directory.glob(file_pattern))
    for file in files:
        try:
            print(f"📬 Found {file_type}: {file.name}")
            await getattr(handler, handler_method)(file)
        except Exception as e:
            print(f"❌ Failed to process {file.name}: {type(e).__name__}: {e}", file=sys.stderr)


async def periodic_file_scanner(app: Application) -> None:
    """Periodically scan for new notification, completion, summary, and execution files (dual-mode)."""
    print(f"📂 Periodic file scanner started (every 5s)")

    notification_handler = NotificationHandler(app.bot, int(CHAT_ID))
    completion_handler = CompletionHandler(app.bot, int(CHAT_ID))
    summary_handler = SummaryHandler(app.bot, int(CHAT_ID))  # Phase 3 - v4.0.0
    execution_handler = WorkflowExecutionHandler(app.bot, int(CHAT_ID))  # Phase 4 - WorkflowExecution completion

    while not bot_state.shutdown_requested:
        await asyncio.sleep(5)  # Scan every 5 seconds

        # Phase 3 - v4.0.0: Scan for new summaries (prioritize over notifications)
        await _scan_and_process(SUMMARIES_DIR, "summary_*.json", summary_handler, "send_workflow_menu", "summary")

        # v3 backward compat: Scan for new notifications
        await _scan_and_process(NOTIFICATION_DIR, "notify_*.json", notification_handler, "send_notification", "notification")

        # Scan for new completions (v3 backward compat)
        await _scan_and_process(COMPLETION_DIR, "completion_*.json", completion_handler, "send_completion", "completion")

        # Phase 4 - v4.0.0: Scan for workflow execution completions
        await _scan_and_process(EXECUTIONS_DIR, "execution_*.json", execution_handler, "send_execution_completion", "execution")


async def progress_poller(app: Application) -> None:
    """Poll progress files and update Telegram messages with streaming progress."""
    print(f"📊 Progress poller started (every {PROGRESS_POLL_INTERVAL}s)")
    print(f"   Progress directory: {PROGRESS_DIR}")
    print(f"   Active tracking: {len(bot_state.active_progress_updates)} workflows")

    while not bot_state.shutdown_requested:
        await asyncio.sleep(PROGRESS_POLL_INTERVAL)

        if not PROGRESS_DIR.exists():
            continue

        # Get all JSON files in progress directory
        all_json_files = list(PROGRESS_DIR.glob("*.json"))

        # Filter out schema.json
        progress_files = [f for f in all_json_files if f.name != "schema.json"]

        # Extensive logging for debugging
        if all_json_files:
            print(f"\n📂 Progress directory scan:")
            print(f"   Total JSON files: {len(all_json_files)}")
            print(f"   Files found: {[f.name for f in all_json_files]}")
            print(f"   After filtering schema.json: {len(progress_files)} files")
            if progress_files:
                print(f"   Processing: {[f.name for f in progress_files]}")

        for progress_file in progress_files:
            try:
                print(f"\n📊 Processing progress file: {progress_file.name}")

                # Read progress data
                with open(progress_file, "r") as f:
                    content = f.read()
                    print(f"   File size: {len(content)} bytes")
                    progress = json.load(open(progress_file, "r"))

                print(f"   JSON parsed successfully")
                print(f"   Keys in progress: {list(progress.keys())}")

                # Extract required fields with detailed logging
                if "workspace_id" not in progress:
                    print(f"   ⚠️  Missing workspace_id field!")
                    print(f"   Progress content: {progress}")
                    continue

                workspace_id = progress["workspace_id"]
                session_id = progress["session_id"]
                workflow_id = progress["workflow_id"]
                status = progress["status"]
                stage = progress["stage"]
                progress_percent = progress["progress_percent"]
                message = progress["message"]

                print(f"   ✅ Extracted fields:")
                print(f"      workspace_id: {workspace_id}")
                print(f"      session_id: {session_id}")
                print(f"      workflow_id: {workflow_id}")
                print(f"      status: {status}")
                print(f"      stage: {stage} ({progress_percent}%)")

                # Check if we're tracking this workflow
                progress_key = (workspace_id, session_id, workflow_id)
                if progress_key not in bot_state.active_progress_updates:
                    print(f"   ⏭️  Not tracking this workflow (no message_id registered)")
                    continue

                # Extract tracking context (message_id + repository/git info)
                tracking_context = bot_state.active_progress_updates[progress_key]
                message_id = tracking_context["message_id"]
                git_branch = tracking_context.get("git_branch", "unknown")
                repository_root = tracking_context.get("repository_root", "unknown")
                working_dir = tracking_context.get("working_directory", ".")
                workflow_name = tracking_context.get("workflow_name", workflow_id)
                git_modified = tracking_context.get("git_modified", 0)
                git_untracked = tracking_context.get("git_untracked", 0)
                git_staged = tracking_context.get("git_staged", 0)

                # Replace home directory with ~ for cleaner display
                repo_display = format_repo_display(repository_root)

                print(f"   📝 Updating message_id: {message_id} (branch: {git_branch})")

                # Build progress caption (Phase 2: edit caption instead of text)
                stage_emoji = {
                    "starting": "🎬",
                    "rendering": "📝",
                    "executing": "⚙️",
                    "waiting": "⏳",
                    "completed": "✅" if status == "success" else "❌"
                }
                emoji = stage_emoji.get(stage, "📊")

                # Build git status line
                # Compact git status (always show all counters)
                git_status_line = format_git_status_compact(git_modified, git_staged, git_untracked)

                progress_text = (
                    f"{emoji} **Workflow: {workflow_name}**\n\n"
                    f"**Repository**: `{repo_display}`\n"
                    f"**Directory**: `{working_dir}`\n"
                    f"**Branch**: `{git_branch}`\n"
                    f"**↯**: {git_status_line}\n\n"
                    f"**Stage**: {stage}\n"
                    f"**Progress**: {progress_percent}%\n"
                    f"**Status**: {message}"
                )

                # Update message text
                await app.bot.edit_message_text(
                    chat_id=int(CHAT_ID),
                    message_id=message_id,
                    text=progress_text,
                    parse_mode="Markdown"
                )
                print(f"   ✅ Message updated successfully")

                # Clean up progress file (but keep tracking for execution completion)
                if stage == "completed":
                    print(f"   🗑️  Removing completed progress file: {progress_file.name}")
                    progress_file.unlink()
                    print(f"   ℹ️  Keeping tracking active for execution completion handler")

            except KeyError as e:
                print(f"❌ Missing field in {progress_file.name}: {e}", file=sys.stderr)
                print(f"   File content preview: {content[:500]}", file=sys.stderr)
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error in {progress_file.name}: {e}", file=sys.stderr)
                print(f"   File content: {content}", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to process progress {progress_file.name}: {type(e).__name__}: {e}", file=sys.stderr)
                import traceback
                print(f"   Full traceback:", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)


async def idle_timeout_monitor() -> None:
    """Monitor idle time and request shutdown if timeout exceeded."""
    print(f"⏱️  Idle timeout monitor started ({IDLE_TIMEOUT_SECONDS}s)")

    while not bot_state.shutdown_requested:
        await asyncio.sleep(30)  # Check every 30 seconds

        idle_time = get_idle_time()
        if idle_time >= IDLE_TIMEOUT_SECONDS:
            print(f"\n⏱️  Idle timeout reached ({idle_time:.0f}s >= {IDLE_TIMEOUT_SECONDS}s)")
            print("   Shutting down...")
            bot_state.shutdown_requested = True
            break

        # Log progress every 5 minutes
        if int(idle_time) % 300 == 0 and idle_time > 0:
            remaining = IDLE_TIMEOUT_SECONDS - idle_time
            print(f"⏱️  Idle: {idle_time:.0f}s, auto-shutdown in {remaining:.0f}s")


def _restore_progress_tracking() -> None:
    """
    Restore progress tracking state from disk (survives watchexec restarts).

    Reads tracking JSON files and populates bot_state.active_progress_updates dictionary.
    """
    print("\n🔄 Restoring progress tracking state...")

    if not TRACKING_DIR.exists():
        print(f"   ℹ️  No tracking state to restore")
        return

    restored_count = 0
    for tracking_file in TRACKING_DIR.glob("*_tracking.json"):
        try:
            tracking_data = json.loads(tracking_file.read_text())
            # Get IDs from tracking data (more reliable than filename parsing)
            workspace_id = tracking_data["workspace_id"]
            session_id = tracking_data["session_id"]
            # Extract workflow_id from filename: {workspace}_{session}_{workflow}_tracking.json
            # UUIDs use dashes (not underscores), so split is simple:
            # Example: 81e622b5_fb77a731-3922-4da4-bc54-4b2db9de6e40_commit-changes_tracking.json
            filename_parts = tracking_file.stem.replace("_tracking", "").split("_")
            # parts[0] = workspace_id (8 chars hash)
            # parts[1] = session_id (UUID with dashes)
            # parts[2:] = workflow_id (might contain underscores)
            workflow_id = "_".join(filename_parts[2:])

            progress_key = (workspace_id, session_id, workflow_id)
            bot_state.active_progress_updates[progress_key] = tracking_data
            restored_count += 1
            print(f"   ✓ Restored: {workspace_id}/{workflow_id} (msg {tracking_data['message_id']})")
        except Exception as e:
            print(f"   ⚠️  Failed to restore {tracking_file.name}: {e}")

    print(f"   ✅ Restored {restored_count} tracked workflow(s)")


async def main() -> int:
    """Main entry point - on-demand polling with auto-shutdown."""
    print("=" * 70)
    print("Multi-Workspace Telegram Bot - Workflow Orchestration Mode")
    print("=" * 70)
    print(f"Version: 4.0.0")
    print(f"PID: {os.getpid()}")
    print(f"PID file: {PID_FILE}")
    print(f"Idle timeout: {IDLE_TIMEOUT_SECONDS}s ({IDLE_TIMEOUT_SECONDS // 60} minutes)")
    print()
    print(f"Notification dir: {NOTIFICATION_DIR}")
    print(f"Approval dir: {APPROVAL_DIR}")
    print(f"Completion dir: {COMPLETION_DIR}")
    print(f"State TTL: {STATE_TTL_MINUTES} minutes")
    print()

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    print("✅ Signal handlers registered (SIGTERM, SIGINT)")

    # Phase 3 - v4.0.0: Load workflow registry
    print("\n📋 Loading workflow registry...")
    try:
        bot_state.workflow_registry = load_workflow_registry(WORKFLOWS_REGISTRY)
    except Exception as e:
        print(f"❌ Failed to load workflow registry: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"   Registry path: {WORKFLOWS_REGISTRY}", file=sys.stderr)
        return 1

    # Phase 4 - v4.1.0: Restore progress tracking state (survives watchexec restarts)
    _restore_progress_tracking()

    try:
        # Create PID file (fails if another instance running)
        create_pid_file(PID_FILE)

        # Initialize activity tracking
        bot_state.last_activity_time = asyncio.get_event_loop().time()
        print(f"⏱️  Activity timer initialized")

        # Initialize Telegram bot with AIORateLimiter
        print("\n📱 Initializing Telegram bot...")
        rate_limiter = AIORateLimiter(
            overall_max_rate=30,    # 30 requests/sec overall (Telegram limit)
            overall_time_period=1,  # 1 second window
            group_max_rate=20,      # 20 requests/min per group (Telegram limit)
            group_time_period=60,   # 60 second window
            max_retries=3           # Retry 3 times on RetryAfter
        )
        app = (
            Application.builder()
            .token(BOT_TOKEN)
            .rate_limiter(rate_limiter)
            .build()
        )
        app.add_handler(CallbackQueryHandler(handle_callback))

        await app.initialize()
        await app.start()
        print("✅ Telegram bot initialized")

        # Log bot started event
        bot_correlation_id = subprocess.run(
            [str(Path.home() / ".claude" / "automation" / "lychee" / "runtime" / "lib" / "ulid_gen.py")],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()

        log_event(
            bot_correlation_id,
            "system",
            f"bot-{os.getpid()}",
            "bot",
            "bot.started",
            {"pid": os.getpid(), "idle_timeout_seconds": IDLE_TIMEOUT_SECONDS}
        )

        # Start polling
        print(f"📡 Starting Telegram API polling (interval: {POLL_INTERVAL}s, timeout: {POLL_TIMEOUT}s)...")
        await app.updater.start_polling(
            poll_interval=POLL_INTERVAL,
            timeout=POLL_TIMEOUT,
            allowed_updates=["message", "callback_query"]
        )
        print("✅ Polling started")
        update_activity()  # Track polling start as activity

        # Process pending files on startup
        print("\n📂 Processing pending files...")
        await process_pending_notifications(app)
        await process_pending_completions(app)
        await process_pending_executions(app)
        print("✅ Pending files processed")

        # Start background tasks
        print()
        monitor_task = asyncio.create_task(idle_timeout_monitor())
        scanner_task = asyncio.create_task(periodic_file_scanner(app))
        progress_task = asyncio.create_task(progress_poller(app))

        # Event loop - wait for shutdown
        print("\n✅ Bot running (polling for updates + scanning for files + progress updates)")
        print(f"   Auto-shutdown after {IDLE_TIMEOUT_SECONDS // 60} minutes idle")
        print("   Press Ctrl+C to stop manually")
        print()

        while not bot_state.shutdown_requested:
            await asyncio.sleep(1)

        # Log bot shutdown event
        log_event(
            bot_correlation_id,
            "system",
            f"bot-{os.getpid()}",
            "bot",
            "bot.shutdown",
            {"reason": "idle_timeout" if get_idle_time() >= IDLE_TIMEOUT_SECONDS else "manual"}
        )

        # Cleanup
        print("\n🛑 Shutdown initiated")
        monitor_task.cancel()
        scanner_task.cancel()
        progress_task.cancel()

        print("   Stopping polling...")
        await app.updater.stop()
        print("   Stopping bot...")
        await app.stop()
        print("   Shutting down bot...")
        await app.shutdown()
        print("✅ Bot shutdown complete")

        return 0

    except FileExistsError:
        print("\n❌ Another bot instance is already running", file=sys.stderr)
        print("   Check PID file for details", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user (Ctrl+C)")
        return 0
    except Exception as e:
        print(f"\n❌ Fatal error: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1
    finally:
        # Always cleanup PID file
        cleanup_pid_file(PID_FILE)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
