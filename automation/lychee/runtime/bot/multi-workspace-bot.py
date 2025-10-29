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
PID_FILE = STATE_DIR / "bot.pid"
WORKFLOWS_REGISTRY = STATE_DIR / "workflows.json"  # Phase 3 - v4.0.0

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

IDLE_TIMEOUT_SECONDS = 1800  # 30 minutes
POLL_INTERVAL = 1.0  # seconds
POLL_TIMEOUT = 10  # API request timeout
PROGRESS_POLL_INTERVAL = 2.0  # Progress updates every 2 seconds

# Track active progress updates: (workspace_id, session_id, workflow_id) → message_id
active_progress_updates: Dict[tuple, int] = {}

# Cache session summaries for workflow selection: (workspace_id, session_id) → summary_data
# Needed because bot deletes summary files before user clicks workflow buttons
summary_cache: Dict[tuple, Dict[str, Any]] = {}

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID", file=sys.stderr)
    sys.exit(1)

# Global shutdown flag for signal handlers
shutdown_requested = False
last_activity_time: Optional[float] = None

# Phase 3 - v4.0.0: Workflow registry
workflow_registry: Optional[Dict[str, Any]] = None

# Import workspace helpers
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


# Event Logging
def log_event(
    correlation_id: str,
    workspace_id: str,
    session_id: str,
    component: str,
    event_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log event to SQLite event store via event_logger.py.

    Args:
        correlation_id: ULID for request tracing
        workspace_id: Workspace hash or ULID
        session_id: Claude Code session UUID
        component: Component name (bot)
        event_type: Event type (e.g., notification.received)
        metadata: Event-specific data

    Raises:
        subprocess.CalledProcessError: Event logging failed
    """
    event_logger = Path.home() / ".claude" / "automation" / "lychee" / "runtime" / "lib" / "event_logger.py"
    metadata_json = json.dumps(metadata) if metadata else "{}"

    try:
        subprocess.run(
            [str(event_logger), correlation_id, workspace_id, session_id, component, event_type, metadata_json],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to log event {event_type}: {e.stderr}", file=sys.stderr)
        raise


# Phase 3 - v4.0.0: Workflow Registry Functions
def load_workflow_registry() -> Dict[str, Any]:
    """
    Load workflow registry from workflows.json.

    Returns:
        Workflow registry dictionary

    Raises:
        FileNotFoundError: Registry file not found
        json.JSONDecodeError: Invalid JSON
        ValueError: Invalid registry schema
    """
    if not WORKFLOWS_REGISTRY.exists():
        raise FileNotFoundError(f"Workflow registry not found: {WORKFLOWS_REGISTRY}")

    with open(WORKFLOWS_REGISTRY) as f:
        registry = json.load(f)

    # Validate required fields
    if "version" not in registry or "workflows" not in registry:
        raise ValueError("Invalid registry: missing 'version' or 'workflows'")

    print(f"✅ Loaded workflow registry v{registry['version']} ({len(registry['workflows'])} workflows)")
    return registry


def filter_workflows_by_triggers(summary: Dict[str, Any]) -> list[Dict[str, Any]]:
    """
    Filter workflows based on trigger conditions from session summary.

    Args:
        summary: SessionSummary data

    Returns:
        List of workflow manifests that match trigger conditions

    Trigger Logic:
        - lychee_errors: true → Only if lychee_status.error_count > 0
        - git_modified: true → Only if git_status.modified_files > 0
        - always: true → Always available
    """
    if workflow_registry is None:
        raise RuntimeError("Workflow registry not loaded")

    available = []
    lychee_errors = summary.get("lychee_status", {}).get("error_count", 0)
    modified_files = summary.get("git_status", {}).get("modified_files", 0)

    for wf_id, workflow in workflow_registry["workflows"].items():
        triggers = workflow.get("triggers", {})

        # Check lychee_errors trigger
        if triggers.get("lychee_errors"):
            if lychee_errors > 0:
                available.append(workflow)
            continue  # Skip other checks if this trigger exists

        # Check git_modified trigger
        if triggers.get("git_modified"):
            if modified_files > 0:
                available.append(workflow)
            continue

        # Check always trigger
        if triggers.get("always"):
            available.append(workflow)

    return available


# PID File Management
def create_pid_file() -> None:
    """
    Create PID file atomically.

    Raises:
        FileExistsError: Another bot instance is already running
        OSError: File system error
    """
    try:
        # Atomic create with O_EXCL (fails if file exists)
        fd = os.open(str(PID_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        try:
            os.write(fd, f"{os.getpid()}\n".encode())
            print(f"✅ Created PID file: {PID_FILE} (PID: {os.getpid()})")
        finally:
            os.close(fd)
    except FileExistsError:
        print(f"❌ PID file already exists: {PID_FILE}", file=sys.stderr)
        print(f"   Another bot instance is likely running", file=sys.stderr)
        raise
    except Exception as e:
        print(f"❌ Failed to create PID file: {type(e).__name__}: {e}", file=sys.stderr)
        raise


def cleanup_pid_file() -> None:
    """Remove PID file if it exists and belongs to this process."""
    try:
        if PID_FILE.exists():
            # Verify PID file contains our PID before removing
            try:
                stored_pid = int(PID_FILE.read_text().strip())
                if stored_pid == os.getpid():
                    PID_FILE.unlink()
                    print(f"🗑️  Removed PID file: {PID_FILE}")
                else:
                    print(f"⚠️  PID file belongs to different process ({stored_pid}), not removing", file=sys.stderr)
            except (ValueError, OSError) as e:
                # Corrupted PID file, remove it anyway
                PID_FILE.unlink()
                print(f"🗑️  Removed corrupted PID file: {e}")
    except Exception as e:
        print(f"⚠️  Failed to cleanup PID file: {type(e).__name__}: {e}", file=sys.stderr)


def signal_handler(signum: int, frame) -> None:
    """Handle termination signals."""
    global shutdown_requested
    sig_name = signal.Signals(signum).name
    print(f"\n🛑 Received {sig_name}, shutting down...")
    shutdown_requested = True


def update_activity() -> None:
    """Update last activity timestamp."""
    global last_activity_time
    last_activity_time = asyncio.get_event_loop().time()


def get_idle_time() -> float:
    """Get seconds since last activity."""
    if last_activity_time is None:
        return 0.0
    return asyncio.get_event_loop().time() - last_activity_time


class NotificationHandler:
    """Handles notification requests from any workspace."""

    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

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
            try:
                workspace_id = get_workspace_id_from_path(workspace_path)
                registry = load_registry()
                workspace = registry["workspaces"][workspace_id]
                emoji = workspace["emoji"]
                ws_name = workspace["name"]
            except (ValueError, FileNotFoundError, KeyError):
                # Unregistered workspace - use defaults
                workspace_id = request.get("workspace_hash", "unknown")
                emoji = "📁"
                ws_name = workspace_path.name
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
            self._cleanup_notification(notification_file)

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

    def _cleanup_notification(self, notification_file: Path) -> None:
        """Delete consumed notification file."""
        try:
            notification_file.unlink()
            print(f"🗑️  Consumed: {notification_file.name}")
        except FileNotFoundError:
            pass


class CompletionHandler:
    """Handles completion notifications from orchestrator."""

    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

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
            print(f"   📋 Loading workspace registry...")
            try:
                registry = load_registry()
                workspace = registry["workspaces"][workspace_id]
                emoji = workspace["emoji"]
                print(f"   ✓ Workspace config loaded: emoji={emoji}")
            except (FileNotFoundError, KeyError):
                # Unregistered workspace - use defaults
                workspace_path = Path(completion.get("workspace_path", "/unknown"))
                emoji = "📁"
                print(f"   ⚠️  Workspace not in registry, using defaults: emoji={emoji}, path={workspace_path.name}")

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
            self._cleanup_completion(completion_file)

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

    def _cleanup_completion(self, completion_file: Path) -> None:
        """Delete consumed completion file."""
        try:
            completion_file.unlink()
            print(f"🗑️  Consumed: {completion_file.name}")
        except FileNotFoundError:
            pass


class WorkflowExecutionHandler:
    """
    Handles workflow execution completion notifications (Phase 4 - v4.0.0).

    Sends final completion messages WITHOUT buttons after workflows complete.
    Key distinction: Stop hook messages have workflow selection buttons,
    execution completions show results only.
    """

    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

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
            print(f"   📋 Loading workspace registry...")
            try:
                registry = load_registry()
                workspace = registry["workspaces"][workspace_id]
                emoji = workspace["emoji"]
                print(f"   ✓ Workspace config loaded: emoji={emoji}")
            except (FileNotFoundError, KeyError):
                # Unregistered workspace - use defaults
                workspace_path = Path(execution.get("workspace_path", "/unknown"))
                emoji = "📁"
                print(f"   ⚠️  Workspace not in registry, using defaults: emoji={emoji}, path={workspace_path.name}")

            # Phase 3: Check if we're tracking this workflow (single-message pattern)
            progress_key = (workspace_id, session_id, workflow_id)
            status = execution["status"]
            duration = execution.get("duration_seconds", 0)

            if progress_key in active_progress_updates:
                # Single-message pattern: replace document in existing progress message
                tracking_context = active_progress_updates[progress_key]
                message_id = tracking_context["message_id"]
                git_branch = tracking_context.get("git_branch", "unknown")
                repository_root = tracking_context.get("repository_root", "unknown")
                working_dir = tracking_context.get("working_directory", ".")
                workflow_name = tracking_context.get("workflow_name", workflow_id)
                git_modified = tracking_context.get("git_modified", 0)
                git_untracked = tracking_context.get("git_untracked", 0)
                git_staged = tracking_context.get("git_staged", 0)

                # Replace home directory with ~ for cleaner display
                repo_display = str(repository_root).replace(str(Path.home()), "~")

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
                git_status_line = f"M:{git_modified} S:{git_staged} U:{git_untracked}"

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
                del active_progress_updates[progress_key]

                # Remove tracking file
                tracking_dir = Path.home() / ".claude/automation/lychee/state/tracking"
                tracking_file = tracking_dir / f"{workspace_id}_{session_id}_{workflow_id}_tracking.json"
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
            self._cleanup_execution(execution_file)

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

    def _cleanup_execution(self, execution_file: Path) -> None:
        """Delete consumed execution file."""
        try:
            execution_file.unlink()
            print(f"🗑️  Consumed: {execution_file.name}")
        except FileNotFoundError:
            pass


class SummaryHandler:
    """
    Handles session summaries and presents workflow menu (Phase 3 - v4.0.0).

    Filters workflows by triggers, builds dynamic keyboard, handles selections.
    """

    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

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
            available_workflows = filter_workflows_by_triggers(summary)

            if not available_workflows:
                print(f"⚠️  No workflows available for session {session_id} (no triggers matched)")
                # Don't send message if no workflows available
                return

            # Always compute workspace hash for tracking consistency
            workspace_hash = compute_workspace_hash(workspace_path)

            # ALWAYS use workspace hash for tracking consistency
            # (Execution files from orchestrator use hash, so tracking must too)
            workspace_id = workspace_hash

            # Load workspace config for display only (emoji, name)
            try:
                registered_id = get_workspace_id_from_path(workspace_path)
                registry = load_registry()
                workspace = registry["workspaces"][registered_id]
                emoji = workspace["emoji"]
                ws_name = workspace["name"]
            except (ValueError, FileNotFoundError, KeyError):
                # Unregistered workspace - use defaults
                emoji = "📁"
                ws_name = workspace_path.name

            # Format message with session context
            lychee_status = summary.get("lychee_status", {})
            git_status = summary.get("git_status", {})
            duration = summary.get("duration_seconds", 0)

            # Cache summary data for workflow selection (needed because we delete summary file)
            cache_key = (workspace_id, session_id)
            summary_cache[cache_key] = {
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
                # Use plain text instead of code block to avoid markdown parsing issues
                git_porcelain_display = f"\n{porcelain_text}"

            # Extract repository root and working directory (industry standard distinction)
            repository_root = summary.get("repository_root", str(workspace_path))
            working_dir = summary.get("working_directory", ".")

            # Replace home directory with ~ for cleaner display
            repo_display = str(repository_root).replace(str(Path.home()), "~")

            # Extract user prompt to remind what was asked
            user_prompt = summary.get("last_user_prompt", "")
            if user_prompt:
                # Truncate if too long
                if len(user_prompt) > 100:
                    user_prompt = user_prompt[:97] + "..."
                # Escape markdown
                user_prompt = user_prompt.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')

            # Use last Claude CLI response as title (industry standard: show what was just done)
            last_response = summary.get("last_response", "Session completed")
            # Truncate if too long, keep first line
            if len(last_response) > 100:
                last_response = last_response[:97] + "..."
            # Escape markdown
            last_response = last_response.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')

            # Build compact git status line (always show all counters)
            modified = git_status.get('modified_files', 0)
            staged = git_status.get('staged_files', 0)
            untracked = git_status.get('untracked_files', 0)

            # Show all counters even when zero for clarity
            git_compact = f"M:{modified} S:{staged} U:{untracked}"

            # Escape lychee details
            lychee_details = lychee_status.get('details', 'Not run')
            lychee_details = lychee_details.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')

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
            self._cleanup_summary(summary_file)

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

    def _cleanup_summary(self, summary_file: Path) -> None:
        """Delete consumed summary file."""
        try:
            summary_file.unlink()
            print(f"🗑️  Consumed: {summary_file.name}")
        except FileNotFoundError:
            pass


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
    summary_data = summary_cache.get(cache_key)
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
    try:
        registry = load_registry()
        emoji = registry["workspaces"][workspace_id]["emoji"]
    except (FileNotFoundError, KeyError):
        # Unregistered workspace - use default emoji
        emoji = "📁"

    # Get workflow details
    if workflow_registry and workflow_id in workflow_registry["workflows"]:
        workflow = workflow_registry["workflows"][workflow_id]
        workflow_name = f"{workflow['icon']} {workflow['name']}"
        estimated_duration = workflow.get("estimated_duration", "unknown")

        # Extract session context from cached summary
        git_status = summary_data.get("git_status", {})
        lychee_status = summary_data.get("lychee_status", {})

        git_branch = git_status.get("branch", "unknown")
        git_modified = git_status.get("modified_files", 0)
        git_untracked = git_status.get("untracked_files", 0)
        git_staged = git_status.get("staged_files", 0)
        git_porcelain_lines = git_status.get('porcelain', [])

        # Extract repository root and working directory (industry standard)
        repository_root = summary_data.get("repository_root", summary_data.get("workspace_path", workspace_path))
        working_dir = summary_data.get("working_directory", ".")
        repo_display = str(repository_root).replace(str(Path.home()), "~")

        # Extract user prompt and last response
        user_prompt = summary_data.get("last_user_prompt", "")
        if user_prompt and len(user_prompt) > 100:
            user_prompt = user_prompt[:97] + "..."

        last_response = summary_data.get("last_response", "Session completed")
        if len(last_response) > 100:
            last_response = last_response[:97] + "..."

        duration = summary_data.get("duration_seconds", 0)

        # Build git porcelain display (truncate to avoid huge messages)
        git_porcelain_display = ""
        if git_porcelain_lines:
            # Limit to first 10 lines to avoid huge messages
            display_lines = git_porcelain_lines[:10]
            porcelain_text = "\n".join(display_lines)
            if len(git_porcelain_lines) > 10:
                porcelain_text += f"\n... and {len(git_porcelain_lines) - 10} more"
            # Use plain text instead of code block to avoid markdown parsing issues
            git_porcelain_display = f"\n{porcelain_text}"

        # Compact git status (always show all counters)
        git_compact = f"M:{git_modified} S:{git_staged} U:{git_untracked}"

        # Escape markdown in user_prompt and last_response
        if user_prompt:
            user_prompt = user_prompt.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
        if last_response:
            last_response = last_response.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')

        # Build message with full context
        prompt_line = f"❓ _{user_prompt}_\n" if user_prompt else ""

        # Escape lychee details
        lychee_details = lychee_status.get('details', 'Not run')
        if lychee_details:
            lychee_details = lychee_details.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')

        initial_message = (
            f"{prompt_line}{emoji} **{last_response}**\n\n"
            f"`{repo_display}` | `{working_dir}`\n"
            f"`{session_id}` ({duration}s)\n"
            f"**↯**: `{git_branch}` | {git_compact}{git_porcelain_display}\n\n"
            f"**Lychee**: {lychee_details}\n\n"
            f"⏳ **Workflow: {workflow_name}**\n"
            f"**Stage**: starting | **Progress**: 0%\n"
            f"**Status**: Starting..."
        )

        # Delete the original callback message
        await query.message.delete()

        # Send new text message
        sent_message = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=initial_message,
            parse_mode="Markdown"
        )

        message_id = sent_message.message_id
    else:
        # Fallback for unknown workflow
        # Extract session context from cached summary
        git_status = summary_data.get("git_status", {})
        lychee_status = summary_data.get("lychee_status", {})

        git_branch = git_status.get("branch", "unknown")
        git_modified = git_status.get("modified_files", 0)
        git_untracked = git_status.get("untracked_files", 0)
        git_staged = git_status.get("staged_files", 0)
        git_porcelain_lines = git_status.get('porcelain', [])

        # Extract repository root and working directory (industry standard)
        repository_root = summary_data.get("repository_root", summary_data.get("workspace_path", workspace_path))
        working_dir = summary_data.get("working_directory", ".")
        repo_display = str(repository_root).replace(str(Path.home()), "~")

        # Extract user prompt and last response
        user_prompt = summary_data.get("last_user_prompt", "")
        if user_prompt and len(user_prompt) > 100:
            user_prompt = user_prompt[:97] + "..."

        last_response = summary_data.get("last_response", "Session completed")
        if len(last_response) > 100:
            last_response = last_response[:97] + "..."

        duration = summary_data.get("duration_seconds", 0)

        # Build git porcelain display (truncate to avoid huge messages)
        git_porcelain_display = ""
        if git_porcelain_lines:
            # Limit to first 10 lines to avoid huge messages
            display_lines = git_porcelain_lines[:10]
            porcelain_text = "\n".join(display_lines)
            if len(git_porcelain_lines) > 10:
                porcelain_text += f"\n... and {len(git_porcelain_lines) - 10} more"
            # Use plain text instead of code block to avoid markdown parsing issues
            git_porcelain_display = f"\n{porcelain_text}"

        # Compact git status (always show all counters)
        git_compact = f"M:{git_modified} S:{git_staged} U:{git_untracked}"

        workflow_name = workflow_id

        # Escape markdown in user_prompt and last_response
        if user_prompt:
            user_prompt = user_prompt.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
        if last_response:
            last_response = last_response.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')

        # Build message with full context
        prompt_line = f"❓ _{user_prompt}_\n" if user_prompt else ""

        # Escape lychee details
        lychee_details = lychee_status.get('details', 'Not run')
        if lychee_details:
            lychee_details = lychee_details.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')

        initial_message = (
            f"{prompt_line}{emoji} **{last_response}**\n\n"
            f"`{repo_display}` | `{working_dir}`\n"
            f"`{session_id}` ({duration}s)\n"
            f"**↯**: `{git_branch}` | {git_compact}{git_porcelain_display}\n\n"
            f"**Lychee**: {lychee_details}\n\n"
            f"⏳ **Workflow: {workflow_id}**\n"
            f"**Stage**: starting | **Progress**: 0%\n"
            f"**Status**: Processing..."
        )

        # Delete the original callback message
        await query.message.delete()

        # Send new text message
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
        "workflow_name": workflow_name if workflow_registry and workflow_id in workflow_registry["workflows"] else workflow_id,
        "session_id": session_id
    }

    active_progress_updates[progress_key] = tracking_data

    # Persist tracking data to survive bot restarts (watchexec)
    tracking_dir = Path.home() / ".claude/automation/lychee/state/tracking"
    tracking_dir.mkdir(parents=True, exist_ok=True)
    tracking_file = tracking_dir / f"{workspace_hash}_{session_id}_{workflow_id}_tracking.json"  # Use hash in filename
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
    try:
        registry = load_registry()
        emoji = registry["workspaces"][workspace_id]["emoji"]
    except (FileNotFoundError, KeyError):
        # Unregistered workspace - use default emoji
        emoji = "📁"

    await query.edit_message_text(
        text=f"{emoji} **Action Received**: {action}\n\n"
             f"Workspace: `{workspace_id}`\n"
             f"Session: `{session_id}`\n\n"
             f"Processing...",
        parse_mode="Markdown"
    )

    print(f"✅ Routed to workspace: {workspace_id}")
    update_activity()  # Track activity for idle timeout


async def process_pending_notifications(app: Application) -> None:
    """Process all pending notification files on startup (no watching)."""
    handler = NotificationHandler(app.bot, int(CHAT_ID))

    # Scan notification directory once
    if not NOTIFICATION_DIR.exists():
        print("📂 No notification directory found")
        return

    notification_files = sorted(NOTIFICATION_DIR.glob("notify_*.json"))
    if not notification_files:
        print("📂 No pending notifications")
        return

    print(f"📬 Found {len(notification_files)} pending notification(s)")
    for notification_file in notification_files:
        try:
            print(f"   Processing: {notification_file.name}")
            await handler.send_notification(notification_file)
        except Exception as e:
            print(f"   ❌ Failed to process {notification_file.name}: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)


async def process_pending_completions(app: Application) -> None:
    """Process all pending completion files on startup (no watching)."""
    handler = CompletionHandler(app.bot, int(CHAT_ID))

    # Scan completion directory once
    if not COMPLETION_DIR.exists():
        print("📂 No completion directory found")
        return

    completion_files = sorted(COMPLETION_DIR.glob("completion_*.json"))
    if not completion_files:
        print("📂 No pending completions")
        return

    print(f"📬 Found {len(completion_files)} pending completion(s)")
    for completion_file in completion_files:
        try:
            print(f"   Processing: {completion_file.name}")
            await handler.send_completion(completion_file)
        except Exception as e:
            print(f"   ❌ Failed to process {completion_file.name}: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)


async def process_pending_executions(app: Application) -> None:
    """Process all pending execution files on startup (no watching)."""
    handler = WorkflowExecutionHandler(app.bot, int(CHAT_ID))

    # Scan execution directory once
    if not EXECUTIONS_DIR.exists():
        print("📂 No execution directory found")
        return

    execution_files = sorted(EXECUTIONS_DIR.glob("execution_*.json"))
    if not execution_files:
        print("📂 No pending executions")
        return

    print(f"📬 Found {len(execution_files)} pending execution(s)")
    for execution_file in execution_files:
        try:
            print(f"   Processing: {execution_file.name}")
            await handler.send_execution_completion(execution_file)
        except Exception as e:
            print(f"   ❌ Failed to process {execution_file.name}: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)


async def periodic_file_scanner(app: Application) -> None:
    """Periodically scan for new notification, completion, summary, and execution files (dual-mode)."""
    global shutdown_requested

    print(f"📂 Periodic file scanner started (every 5s)")

    notification_handler = NotificationHandler(app.bot, int(CHAT_ID))
    completion_handler = CompletionHandler(app.bot, int(CHAT_ID))
    summary_handler = SummaryHandler(app.bot, int(CHAT_ID))  # Phase 3 - v4.0.0
    execution_handler = WorkflowExecutionHandler(app.bot, int(CHAT_ID))  # Phase 4 - WorkflowExecution completion

    while not shutdown_requested:
        await asyncio.sleep(5)  # Scan every 5 seconds

        # Phase 3 - v4.0.0: Scan for new summaries (prioritize over notifications)
        if SUMMARIES_DIR.exists():
            summary_files = sorted(SUMMARIES_DIR.glob("summary_*.json"))
            for summary_file in summary_files:
                try:
                    print(f"📬 Found summary: {summary_file.name}")
                    await summary_handler.send_workflow_menu(summary_file)
                except Exception as e:
                    print(f"❌ Failed to process {summary_file.name}: {type(e).__name__}: {e}", file=sys.stderr)

        # v3 backward compat: Scan for new notifications
        if NOTIFICATION_DIR.exists():
            notification_files = sorted(NOTIFICATION_DIR.glob("notify_*.json"))
            for notification_file in notification_files:
                try:
                    print(f"📬 Found notification: {notification_file.name}")
                    await notification_handler.send_notification(notification_file)
                except Exception as e:
                    print(f"❌ Failed to process {notification_file.name}: {type(e).__name__}: {e}", file=sys.stderr)

        # Scan for new completions (v3 backward compat)
        if COMPLETION_DIR.exists():
            completion_files = sorted(COMPLETION_DIR.glob("completion_*.json"))
            for completion_file in completion_files:
                try:
                    print(f"📬 Found completion: {completion_file.name}")
                    await completion_handler.send_completion(completion_file)
                except Exception as e:
                    print(f"❌ Failed to process {completion_file.name}: {type(e).__name__}: {e}", file=sys.stderr)

        # Phase 4 - v4.0.0: Scan for workflow execution completions
        if EXECUTIONS_DIR.exists():
            execution_files = sorted(EXECUTIONS_DIR.glob("execution_*.json"))
            for execution_file in execution_files:
                try:
                    print(f"📬 Found execution: {execution_file.name}")
                    await execution_handler.send_execution_completion(execution_file)
                except Exception as e:
                    print(f"❌ Failed to process {execution_file.name}: {type(e).__name__}: {e}", file=sys.stderr)


async def progress_poller(app: Application) -> None:
    """Poll progress files and update Telegram messages with streaming progress."""
    global shutdown_requested, active_progress_updates

    print(f"📊 Progress poller started (every {PROGRESS_POLL_INTERVAL}s)")
    print(f"   Progress directory: {PROGRESS_DIR}")
    print(f"   Active tracking: {len(active_progress_updates)} workflows")

    while not shutdown_requested:
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
                if progress_key not in active_progress_updates:
                    print(f"   ⏭️  Not tracking this workflow (no message_id registered)")
                    continue

                # Extract tracking context (message_id + repository/git info)
                tracking_context = active_progress_updates[progress_key]
                message_id = tracking_context["message_id"]
                git_branch = tracking_context.get("git_branch", "unknown")
                repository_root = tracking_context.get("repository_root", "unknown")
                working_dir = tracking_context.get("working_directory", ".")
                workflow_name = tracking_context.get("workflow_name", workflow_id)
                git_modified = tracking_context.get("git_modified", 0)
                git_untracked = tracking_context.get("git_untracked", 0)
                git_staged = tracking_context.get("git_staged", 0)

                # Replace home directory with ~ for cleaner display
                repo_display = str(repository_root).replace(str(Path.home()), "~")

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
                git_status_line = f"M:{git_modified} S:{git_staged} U:{git_untracked}"

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
    global shutdown_requested

    print(f"⏱️  Idle timeout monitor started ({IDLE_TIMEOUT_SECONDS}s)")

    while not shutdown_requested:
        await asyncio.sleep(30)  # Check every 30 seconds

        idle_time = get_idle_time()
        if idle_time >= IDLE_TIMEOUT_SECONDS:
            print(f"\n⏱️  Idle timeout reached ({idle_time:.0f}s >= {IDLE_TIMEOUT_SECONDS}s)")
            print("   Shutting down...")
            shutdown_requested = True
            break

        # Log progress every 5 minutes
        if int(idle_time) % 300 == 0 and idle_time > 0:
            remaining = IDLE_TIMEOUT_SECONDS - idle_time
            print(f"⏱️  Idle: {idle_time:.0f}s, auto-shutdown in {remaining:.0f}s")


async def main() -> int:
    """Main entry point - on-demand polling with auto-shutdown."""
    global shutdown_requested, last_activity_time, workflow_registry

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
        workflow_registry = load_workflow_registry()
    except Exception as e:
        print(f"❌ Failed to load workflow registry: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"   Registry path: {WORKFLOWS_REGISTRY}", file=sys.stderr)
        return 1

    # Phase 4 - v4.1.0: Restore progress tracking state (survives watchexec restarts)
    print("\n🔄 Restoring progress tracking state...")
    tracking_dir = Path.home() / ".claude/automation/lychee/state/tracking"
    if tracking_dir.exists():
        restored_count = 0
        for tracking_file in tracking_dir.glob("*_tracking.json"):
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
                active_progress_updates[progress_key] = tracking_data
                restored_count += 1
                print(f"   ✓ Restored: {workspace_id}/{workflow_id} (msg {tracking_data['message_id']})")
            except Exception as e:
                print(f"   ⚠️  Failed to restore {tracking_file.name}: {e}")
        print(f"   ✅ Restored {restored_count} tracked workflow(s)")
    else:
        print(f"   ℹ️  No tracking state to restore")

    try:
        # Create PID file (fails if another instance running)
        create_pid_file()

        # Initialize activity tracking
        last_activity_time = asyncio.get_event_loop().time()
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

        while not shutdown_requested:
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
        cleanup_pid_file()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
