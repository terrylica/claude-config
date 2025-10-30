#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-telegram-bot[rate-limiter]>=21.0",
#     "jsonschema>=4.0.0",
#     "psutil>=7.0.0",
# ]
# ///
"""
Multi-Workspace Telegram Bot - Workflow Orchestration

Processes session summaries, notifications, and completion files.
Presents dynamic workflow menu based on trigger conditions.
Polls Telegram API for button clicks with idle timeout.
Auto-shuts down after 10 minutes of inactivity.

Version: 5.2.0
Specification: ~/.claude/specifications/telegram-workflows-orchestration-v4.yaml

Changes from v5.0.0:
- Migrate to psutil for PID management (industry-standard approach)
- Add cmdline verification to prevent PID reuse false positives
- Better process detection (handles zombie processes, access denied errors)

Changes from v4.9.0:
- Extract async services to bot_services.py (-183 lines)
- Total reduction: 183 lines (28%, 662 -> 479)

Changes from v4.5.1:
- Phase 1: Extract file validators, message formatters, keyboard builder (-222 lines)
- Phase 2: Extract file processors, progress tracking (-72 lines)
- Phase 3: Extract handler functions (-259 lines)
- Phase 4: Extract handler classes (-636 lines)
- Phase 5: Extract async services (-183 lines)
- Total reduction: 1372 lines (74%, 1851 -> 479)

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
    strip_markdown,
    truncate_markdown_safe,
    extract_conversation_from_transcript,
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
    build_workflow_start_message,
    build_completion_message,
    build_execution_message
)
from file_validators import (
    validate_notification_file,
    validate_completion_file,
    validate_execution_file,
    validate_summary_file
)
from keyboard_builders import (
    build_workflow_keyboard
)
from file_processors import (
    process_pending_files,
    scan_and_process
)
from handlers import (
    handle_view_details,
    handle_workflow_selection
)
from handler_classes import (
    NotificationHandler,
    CompletionHandler,
    WorkflowExecutionHandler,
    SummaryHandler
)
from bot_services import (
    periodic_file_scanner,
    progress_poller,
    idle_timeout_monitor
)
import bot_state
from bot_state import (
    update_activity,
    get_idle_time,
    restore_progress_tracking
)


def signal_handler(signum: int, frame) -> None:
    """Handle termination signals."""
    sig_name = signal.Signals(signum).name
    print(f"\n🛑 Received {sig_name}, shutting down...")
    bot_state.shutdown_requested = True



# Handler classes moved to handler_classes.py

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
        await query.edit_message_text(text=f"❌ {e}", parse_mode="HTML")
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
        await handle_workflow_selection(query, workspace_id, workspace_path, session_id, action, correlation_id, context, SELECTIONS_DIR, TRACKING_DIR)
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
        text=f"{emoji} <b>Action Received</b>: {action}\n\n"
             f"Workspace: <code>{workspace_id}</code>\n"
             f"Session: <code>{session_id}</code>\n\n"
             f"Processing...",
        parse_mode="HTML"
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
    """Generic processor for pending files on startup."""
    await process_pending_files(directory, file_pattern, handler_class, handler_method, file_type, app, int(CHAT_ID))


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


# Async service functions moved to bot_services.py


def _restore_progress_tracking() -> None:
    """Restore progress tracking state from disk (survives watchexec restarts)."""
    restore_progress_tracking(TRACKING_DIR)


async def main() -> int:
    """Main entry point - on-demand polling with auto-shutdown."""
    print("=" * 70)
    print("Multi-Workspace Telegram Bot - Workflow Orchestration Mode")
    print("=" * 70)
    print(f"Version: 5.2.0")
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
        monitor_task = asyncio.create_task(idle_timeout_monitor(IDLE_TIMEOUT_SECONDS))
        scanner_task = asyncio.create_task(periodic_file_scanner(
            app, NOTIFICATION_DIR, COMPLETION_DIR, SUMMARIES_DIR, EXECUTIONS_DIR, int(CHAT_ID)
        ))
        progress_task = asyncio.create_task(progress_poller(app, PROGRESS_DIR, int(CHAT_ID), PROGRESS_POLL_INTERVAL))

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
