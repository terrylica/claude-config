#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-telegram-bot>=21.0",
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
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

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
PID_FILE = STATE_DIR / "bot.pid"
WORKFLOWS_REGISTRY = STATE_DIR / "workflows.json"  # Phase 3 - v4.0.0

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

IDLE_TIMEOUT_SECONDS = 600  # 10 minutes
POLL_INTERVAL = 1.0  # seconds
POLL_TIMEOUT = 10  # API request timeout

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

            # Send message
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

            # Load workspace config
            print(f"   📋 Loading workspace registry...")
            registry = load_registry()
            workspace = registry["workspaces"][workspace_id]
            emoji = workspace["emoji"]
            print(f"   ✓ Workspace config loaded: emoji={emoji}")

            # Format message based on status
            print(f"   ✍️  Formatting completion message...")
            message = self._format_completion_message(completion, emoji)
            print(f"   ✓ Message formatted ({len(message)} chars)")

            # Send message
            print(f"   📡 Sending to Telegram (chat_id={self.chat_id})...")
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown"
            )

            # Send full output as document if > 500 chars (progressive disclosure)
            status = completion["status"]
            if status == "success" and completion.get("stdout"):
                stdout = completion["stdout"].strip()
                if stdout and len(stdout) > 500:
                    print(f"   📄 Sending full output as document ({len(stdout)} chars)...")

                    # Extract readable content from JSON output (if applicable)
                    readable_content = stdout
                    try:
                        result_data = json.loads(stdout)
                        if isinstance(result_data, dict) and 'result' in result_data:
                            # Extract human-readable result from JSON
                            readable_content = result_data['result']
                            print(f"   ✓ Extracted readable content from JSON ({len(readable_content)} chars)")
                        else:
                            print(f"   ⚠️  JSON parsed but no 'result' field, using raw output")
                    except json.JSONDecodeError:
                        # Not JSON - use raw output as-is
                        print(f"   ℹ️  Output is not JSON, using raw content")

                    file_path = f"/tmp/autofix_report_{session_id[:8]}.txt"
                    with open(file_path, 'w') as f:
                        f.write(readable_content)

                    await self.bot.send_document(
                        chat_id=self.chat_id,
                        document=open(file_path, 'rb'),
                        filename=f"autofix-report-{session_id[:8]}.txt",
                        caption="📄 Full auto-fix report\n\nReadable output from Claude CLI."
                    )
                    os.remove(file_path)
                    print(f"   ✓ Document sent and temp file cleaned")

            elif status == "error" and completion.get("stderr"):
                stderr = completion["stderr"].strip()
                if stderr and len(stderr) > 500:
                    print(f"   📄 Sending full error log as document ({len(stderr)} chars)...")
                    file_path = f"/tmp/autofix_error_{session_id[:8]}.txt"
                    with open(file_path, 'w') as f:
                        f.write(stderr)

                    await self.bot.send_document(
                        chat_id=self.chat_id,
                        document=open(file_path, 'rb'),
                        filename=f"autofix-error-{session_id[:8]}.txt",
                        caption="❌ Full error log\n\nComplete stderr from Claude CLI."
                    )
                    os.remove(file_path)
                    print(f"   ✓ Document sent and temp file cleaned")

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

        # Add stdout for success cases (progressive disclosure)
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

                if len(readable_content) > 500:
                    # Indicate full output will be sent as attachment
                    message += f"\n\n**Result**: Auto-fix completed\n\n"
                    message += f"[Full report will be attached below ⬇️]"
                else:
                    # Short output - include inline
                    message += f"\n**Details**:\n```\n{readable_content}\n```"

        # Add stderr for error cases
        if status == "error" and completion.get("stderr"):
            stderr = completion["stderr"].strip()
            if stderr:
                if len(stderr) > 500:
                    # Indicate full error will be sent as attachment
                    message += f"\n\n[Full error log will be attached below ⬇️]"
                else:
                    # Short error - include inline
                    message += f"\n**Error**:\n```\n{stderr}\n```"

        return message

    def _cleanup_completion(self, completion_file: Path) -> None:
        """Delete consumed completion file."""
        try:
            completion_file.unlink()
            print(f"🗑️  Consumed: {completion_file.name}")
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

            # Load workspace config (with fallback for unregistered workspaces)
            try:
                workspace_id = get_workspace_id_from_path(workspace_path)
                registry = load_registry()
                workspace = registry["workspaces"][workspace_id]
                emoji = workspace["emoji"]
                ws_name = workspace["name"]
            except (ValueError, FileNotFoundError, KeyError):
                # Unregistered workspace - use defaults
                workspace_id = summary.get("workspace_id", "unknown")
                emoji = "📁"
                ws_name = workspace_path.name

            # Format message with session context
            lychee_status = summary.get("lychee_status", {})
            git_status = summary.get("git_status", {})
            duration = summary.get("duration_seconds", 0)

            message = f"""{emoji} **Session Summary** - {ws_name}

**Workspace**: `{workspace_path}`
**Session**: `{session_id}`
**Duration**: {duration}s

**Git Status**:
• Branch: `{git_status.get('branch', 'unknown')}`
• Modified: {git_status.get('modified_files', 0)} files
• Untracked: {git_status.get('untracked_files', 0)} files

**Lychee**: {lychee_status.get('details', 'Not run')}

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

            # Send message
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

    # Send as document if > 4000 chars, otherwise inline
    if len(details_text) > 4000:
        file_path = f"/tmp/lychee_details_{session_id[:8]}.txt"

        # Format plain text for file (without markdown)
        plain_lines = []
        for file_path_key, errors in error_map.items():
            short_path = file_path_key.replace(workspace_path, '').lstrip('/')
            plain_lines.append(f"\n{short_path} ({len(errors)} errors):")
            for error in errors:
                url = error.get("url", "unknown")
                status = error.get("status", {})
                error_text = status.get("text", "Unknown error")
                error_details = status.get("details", "")

                plain_lines.append(f"  • {url}")
                plain_lines.append(f"    {error_text}")
                if error_details:
                    plain_lines.append(f"    {error_details}")

        with open(file_path, 'w') as f:
            f.write('\n'.join(plain_lines))

        await query.message.reply_document(
            document=open(file_path, 'rb'),
            filename=f"link-errors-{session_id[:8]}.txt",
            caption="📋 Detailed error breakdown\n\nComplete list of broken links with error messages."
        )
        os.remove(file_path)
    else:
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
    correlation_id: str
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

    Raises:
        All errors propagate (fail-fast)
    """
    workspace_hash = compute_workspace_hash(Path(workspace_path))

    # Extract workflow ID from action
    if action == "custom_prompt":
        # TODO Phase 4: Implement custom prompt handler
        # For now, acknowledge and return
        await query.edit_message_text(
            "✏️ Custom Prompt\n\n"
            "Custom workflow prompts will be available in Phase 4.\n"
            "For now, please select a preset workflow.",
            parse_mode="Markdown"
        )
        return

    workflow_id = action.replace("workflow_", "")

    # Create selection file
    selection_file = SELECTIONS_DIR / f"selection_{session_id}_{workspace_hash}.json"

    selection_state = {
        "workspace_path": workspace_path,
        "workspace_id": workspace_hash,
        "session_id": session_id,
        "workflows": [workflow_id],  # Single workflow for Phase 3 (multi-select in future)
        "correlation_id": correlation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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

    # Confirm to user
    registry = load_registry()
    emoji = registry["workspaces"][workspace_id]["emoji"]

    # Get workflow details
    if workflow_registry and workflow_id in workflow_registry["workflows"]:
        workflow = workflow_registry["workflows"][workflow_id]
        workflow_name = f"{workflow['icon']} {workflow['name']}"
        estimated_duration = workflow.get("estimated_duration", "unknown")

        await query.edit_message_text(
            f"{emoji} **Workflow Selected**: {workflow_name}\n\n"
            f"Workspace: `{workspace_id}`\n"
            f"Session: `{session_id}`\n"
            f"Estimated duration: ~{estimated_duration}s\n\n"
            f"Orchestrator will process this workflow...",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            f"{emoji} **Workflow Selected**: {workflow_id}\n\n"
            f"Workspace: `{workspace_id}`\n"
            f"Session: `{session_id}`\n\n"
            f"Processing...",
            parse_mode="Markdown"
        )

    print(f"✅ Workflow selected: {workflow_id} for workspace: {workspace_id}")


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
        await query.edit_message_text(f"❌ {e}")
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
        await handle_workflow_selection(query, workspace_id, workspace_path, session_id, action, correlation_id)
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

    # Confirm to user
    registry = load_registry()
    emoji = registry["workspaces"][workspace_id]["emoji"]

    await query.edit_message_text(
        f"{emoji} **Action Received**: {action}\n\n"
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


async def periodic_file_scanner(app: Application) -> None:
    """Periodically scan for new notification, completion, and summary files (dual-mode)."""
    global shutdown_requested

    print(f"📂 Periodic file scanner started (every 5s)")

    notification_handler = NotificationHandler(app.bot, int(CHAT_ID))
    completion_handler = CompletionHandler(app.bot, int(CHAT_ID))
    summary_handler = SummaryHandler(app.bot, int(CHAT_ID))  # Phase 3 - v4.0.0

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

        # Scan for new completions
        if COMPLETION_DIR.exists():
            completion_files = sorted(COMPLETION_DIR.glob("completion_*.json"))
            for completion_file in completion_files:
                try:
                    print(f"📬 Found completion: {completion_file.name}")
                    await completion_handler.send_completion(completion_file)
                except Exception as e:
                    print(f"❌ Failed to process {completion_file.name}: {type(e).__name__}: {e}", file=sys.stderr)


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

    try:
        # Create PID file (fails if another instance running)
        create_pid_file()

        # Initialize activity tracking
        last_activity_time = asyncio.get_event_loop().time()
        print(f"⏱️  Activity timer initialized")

        # Initialize Telegram bot
        print("\n📱 Initializing Telegram bot...")
        app = Application.builder().token(BOT_TOKEN).build()
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
        print("✅ Pending files processed")

        # Start background tasks
        print()
        monitor_task = asyncio.create_task(idle_timeout_monitor())
        scanner_task = asyncio.create_task(periodic_file_scanner(app))

        # Event loop - wait for shutdown
        print("\n✅ Bot running (polling for updates + scanning for files)")
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
