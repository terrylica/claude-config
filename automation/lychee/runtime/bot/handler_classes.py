"""
Telegram bot handler classes.

File-based handlers for notifications, completions, executions, and summaries.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from workspace_helpers import (
    get_workspace_id_from_path,
    compute_workspace_hash,
    create_callback_data
)
from format_utils import (
    get_workspace_config,
    format_repo_display,
    format_git_status_compact,
    escape_markdown,  # DEPRECATED: Use escape_html
    escape_html,
    truncate_markdown_safe,
    extract_conversation_from_transcript,
    convert_to_telegram_markdown
)
from bot_utils import log_event
from message_builders import (
    build_completion_message,
    build_execution_message
)
from file_validators import (
    validate_notification_file,
    validate_completion_file,
    validate_execution_file,
    validate_summary_file
)
from keyboard_builders import build_workflow_keyboard
from workflow_utils import filter_workflows_by_triggers
import bot_state
from bot_state import update_activity


# Module-level constant (shared with main file)
TRACKING_DIR = Path.home() / ".claude" / "automation" / "lychee" / "state" / "tracking"


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

            # Session + debug log lines (two lines, no emoji)
            # Use separate inline code blocks - single backticks can't contain newlines in MarkdownV2
            session_line = f"`session={session_id}`"
            debug_line = f"`debug=~/.claude/debug/${{session}}.txt`"

            markdown_message = f"""{emoji} **Link Validation** - {ws_name}

**Workspace**: `{workspace_path}`
{session_line}
{debug_line}

{details}{files_section}

Choose action:
"""
            message = convert_to_telegram_markdown(markdown_message)

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
                parse_mode="MarkdownV2"
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
        return validate_notification_file(notification_file)



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
                parse_mode="MarkdownV2"
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
        return validate_completion_file(completion_file)

    def _format_completion_message(self, completion: Dict[str, Any], emoji: str) -> str:
        """Format completion data as Telegram message."""
        return build_completion_message(completion, emoji)



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

                # Extract preserved context from initial workflow start message
                user_prompt = tracking_context.get("user_prompt", "")
                last_response = tracking_context.get("last_response", "")

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

                # Session + debug log lines (show both original + headless if present)
                # Use separate inline code blocks - single backticks can't contain newlines in MarkdownV2
                headless_session_id = execution.get("headless_session_id")
                if headless_session_id:
                    session_line = f"`session={session_id}`"
                    headless_line = f"`headless={headless_session_id}`"
                    debug_line = f"`debug=~/.claude/debug/${{session}}.txt`"
                    session_debug_lines = f"{session_line}\n{headless_line}\n{debug_line}"
                else:
                    session_line = f"`session={session_id}`"
                    debug_line = f"`debug=~/.claude/debug/${{session}}.txt`"
                    session_debug_lines = f"{session_line}\n{debug_line}"

                # Build original context section (user prompt + assistant response)
                original_context = ""
                if user_prompt and last_response:
                    # Use plain text without markdown formatting to avoid MarkdownV2 parsing issues
                    # Replace newlines with spaces for single-line display
                    original_context = f"❓ {user_prompt.replace(chr(10), ' ').strip()}\n{emoji} **{last_response}**\n\n"

                markdown_caption = (
                    f"{original_context}"  # Preserve original conversation context
                    f"{status_emoji} **Workflow: {workflow_name}**\n\n"
                    f"**Repository**: `{repo_display}`\n"
                    f"**Directory**: `{working_dir}`\n"
                    f"**Branch**: `{git_branch}`\n"
                    f"**↯**: {git_status_line}\n\n"
                    f"{session_debug_lines}\n"
                    f"**Status**: {status}\n"
                    f"**Duration**: {duration}s\n"
                    f"**Output**: {summary}"
                )
                final_caption = convert_to_telegram_markdown(markdown_caption)

                # Update message text with final status
                print(f"   📝 Updating message with final status...")
                await self.bot.edit_message_text(
                    chat_id=self.chat_id,
                    message_id=message_id,
                    text=final_caption,
                    parse_mode="MarkdownV2"
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
                # No active progress tracking - send fallback notification
                print(f"   ⚠️  WARNING: No progress tracking found for {progress_key}")
                print(f"   Sending fallback notification (new message without progress context)")

                # Build fallback message (without git status or progress context)
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

                # Session + debug log lines (two or three lines, no emoji)
                # Use separate inline code blocks - single backticks can't contain newlines in MarkdownV2
                headless_session_id = execution.get("headless_session_id")
                if headless_session_id:
                    session_line = f"`session={session_id}`"
                    headless_line = f"`headless={headless_session_id}`"
                    debug_line = f"`debug=~/.claude/debug/${{session}}.txt`"
                    session_debug_lines = f"{session_line}\n{headless_line}\n{debug_line}"
                else:
                    session_line = f"`session={session_id}`"
                    debug_line = f"`debug=~/.claude/debug/${{session}}.txt`"
                    session_debug_lines = f"{session_line}\n{debug_line}"

                markdown_fallback = (
                    f"📨 **Workflow Completed** (recovered execution)\n\n"
                    f"{status_emoji} **Workflow**: {workflow_name}\n"
                    f"**Workspace**: `{workspace_id}`\n"
                    f"{session_debug_lines}\n"
                    f"**Status**: {status}\n"
                    f"**Duration**: {duration}s\n"
                    f"**Output**: {summary}\n\n"
                    f"ℹ️ _Progress tracking was lost (bot restart or crash). This is a fallback notification._"
                )
                fallback_message = convert_to_telegram_markdown(markdown_fallback)

                # Send new message (not updating existing message)
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=fallback_message,
                    parse_mode="MarkdownV2"
                )
                print(f"   ✅ Fallback notification sent")

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
        return validate_execution_file(execution_file)

    def _format_execution_message(self, execution: Dict[str, Any], emoji: str, workflow_name: str) -> str:
        """Format WorkflowExecution data as Telegram message (no buttons)."""
        return build_execution_message(execution, emoji, workflow_name)



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

            # Extract conversation from transcript for better context
            # Pattern from Claude-Code-Remote adapted to use transcript files
            transcript_path = Path(summary_file.parent.parent.parent / "projects" /
                                   summary_file.name.replace("summary_", "").replace(".json", ".jsonl"))

            print(f"   🔍 DEBUG: Transcript path derived: {transcript_path}")
            print(f"   🔍 DEBUG: Transcript exists: {transcript_path.exists()}")

            conversation = None
            try:
                # Attempt to extract from transcript if available
                if transcript_path.exists():
                    conversation = extract_conversation_from_transcript(transcript_path)
                    user_prompt = conversation['user_prompt']
                    last_response = conversation['assistant_response']

                    # DEBUG: Log raw extraction results
                    print(f"   📝 Extracted conversation from transcript ({conversation['message_count']} messages)")
                    print(f"   🔍 DEBUG RAW user_prompt (len={len(user_prompt)}): {repr(user_prompt[:200])}")
                    print(f"   🔍 DEBUG RAW last_response (len={len(last_response)}): {repr(last_response[:200])}")
                else:
                    # Fallback to summary fields (may be generic)
                    user_prompt = summary.get("last_user_prompt", "")
                    last_response = summary.get("last_response", "Session completed")
                    print(f"   ⚠️  Transcript not found, using summary fields")
                    print(f"   🔍 DEBUG FALLBACK user_prompt: {repr(user_prompt[:200])}")
            except (FileNotFoundError, ValueError, KeyError) as e:
                # Fallback on any extraction error - use summary fields instead
                print(f"   ⚠️  Transcript extraction failed: {e}")
                print(f"   ⏭️  Using summary fallback fields")
                user_prompt = summary.get("last_user_prompt", "")
                last_response = summary.get("last_response", "Session completed")
                print(f"   🔍 DEBUG EXCEPTION FALLBACK user_prompt: {repr(user_prompt[:200])}")
                print(f"   🔍 DEBUG EXCEPTION FALLBACK last_response: {repr(last_response[:200])}")

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

            # Process user prompt with markdown safety (truncate-first pattern from CCR)
            if user_prompt:
                print(f"   🔍 DEBUG BEFORE truncate: {repr(user_prompt[:150])}")
                user_result = truncate_markdown_safe(user_prompt, max_length=100)
                user_prompt = user_result['text']
                print(f"   🔍 DEBUG AFTER truncate: {repr(user_prompt[:150])}")

            # Process last response with markdown safety (truncate-first pattern from CCR)
            # This preserves Claude's original formatting (bold, code, italic)
            response_result = truncate_markdown_safe(last_response, max_length=100)
            last_response = response_result['text']

            # Log if tags were auto-closed (observability SLO)
            if response_result['tags_closed']:
                print(f"   🔧 Auto-closed markdown tags: {response_result['tags_closed']}")

            # Build compact git status line (always show all counters)
            modified = git_status.get('modified_files', 0)
            staged = git_status.get('staged_files', 0)
            untracked = git_status.get('untracked_files', 0)

            # Show all counters even when zero for clarity
            git_compact = format_git_status_compact(modified, staged, untracked)

            # Get lychee details
            lychee_details = lychee_status.get('details', 'Not run')

            # Build message with user prompt as first line if available
            # Use plain text without markdown formatting to avoid MarkdownV2 parsing issues
            # Replace newlines with spaces for single-line display
            print(f"   🔍 DEBUG user_prompt before prompt_line: {repr(user_prompt)}")
            prompt_line = f"❓ {user_prompt.replace(chr(10), ' ').strip()}\n" if user_prompt else ""
            print(f"   🔍 DEBUG prompt_line result: {repr(prompt_line)}")

            # Session + debug log lines (two lines, no emoji)
            # Use separate inline code blocks - single backticks can't contain newlines in MarkdownV2
            session_line = f"`session={session_id}`"
            debug_line = f"`debug=~/.claude/debug/${{session}}.txt`"

            # Display response with preserved formatting
            markdown_message = f"""{prompt_line}{emoji} {last_response}

`{repo_display}` | `{working_dir}`
{session_line}
{debug_line} ({duration}s)
**↯**: `{git_status.get('branch', 'unknown')}` | {git_compact}{git_porcelain_display}

**Lychee**: {lychee_details}

**Available Workflows** ({len(available_workflows)}):
"""
            print(f"   🔍 DEBUG markdown_message (first 300 chars): {repr(markdown_message[:300])}")
            message = convert_to_telegram_markdown(markdown_message)
            print(f"   🔍 DEBUG converted message (first 300 chars): {repr(message[:300])}")

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
            print(f"   📡 Sending to Telegram (chat_id={self.chat_id}, message_len={len(message)} chars)...")
            sent_message = await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="MarkdownV2"
            )
            print(f"   ✅ Telegram API responded: message_id={sent_message.message_id}, chat_id={sent_message.chat_id}")

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
        return validate_summary_file(summary_file)

    def _build_workflow_keyboard(
        self,
        workflows: list[Dict[str, Any]],
        workspace_id: str,
        workspace_path: Path,
        session_id: str,
        correlation_id: str
    ) -> list[list[InlineKeyboardButton]]:
        """Build dynamic workflow keyboard with custom prompt option."""
        return build_workflow_keyboard(workflows, workspace_id, workspace_path, session_id, correlation_id)

