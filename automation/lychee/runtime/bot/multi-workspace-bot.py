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

Version: 4.9.0
Specification: ~/.claude/specifications/telegram-workflows-orchestration-v4.yaml

Changes from v4.8.0:
- Extract handler classes to handler_classes.py (-636 lines)
- Total reduction: 636 lines (49%, 1298 -> 662)

Changes from v4.5.1:
- Phase 1: Extract file validators, message formatters, keyboard builder (-222 lines)
- Phase 2: Extract file processors, progress tracking (-72 lines)
- Phase 3: Extract handler functions (-259 lines)
- Phase 4: Extract handler classes (-636 lines)
- Total reduction: 1189 lines (64%, 1851 -> 662)

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


async def _scan_and_process(
    directory: Path,
    file_pattern: str,
    handler,
    handler_method: str,
    file_type: str
) -> None:
    """Scan directory for files and process with handler."""
    await scan_and_process(directory, file_pattern, handler, handler_method, file_type)


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

                # Compact session + debug log line
                session_debug_line = f"session={session_id} | 🐛 debug=~/.claude/debug/${{session}}.txt"

                progress_text = (
                    f"{emoji} **Workflow: {workflow_name}**\n\n"
                    f"**Repository**: `{repo_display}`\n"
                    f"**Directory**: `{working_dir}`\n"
                    f"**Branch**: `{git_branch}`\n"
                    f"**↯**: {git_status_line}\n\n"
                    f"`{session_debug_line}`\n"
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
    """Restore progress tracking state from disk (survives watchexec restarts)."""
    restore_progress_tracking(TRACKING_DIR)


async def main() -> int:
    """Main entry point - on-demand polling with auto-shutdown."""
    print("=" * 70)
    print("Multi-Workspace Telegram Bot - Workflow Orchestration Mode")
    print("=" * 70)
    print(f"Version: 4.9.0")
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
