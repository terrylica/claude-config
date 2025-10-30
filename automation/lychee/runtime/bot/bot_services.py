"""
Telegram bot async background services.

Provides periodic file scanning, progress polling, and idle timeout monitoring.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram.ext import Application

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from format_utils import format_git_status_compact, format_repo_display
from file_processors import scan_and_process
from handler_classes import (
    NotificationHandler,
    CompletionHandler,
    WorkflowExecutionHandler,
    SummaryHandler
)
import bot_state


async def periodic_file_scanner(
    app: "Application",
    notification_dir: Path,
    completion_dir: Path,
    summaries_dir: Path,
    executions_dir: Path,
    chat_id: int
) -> None:
    """Periodically scan for new notification, completion, summary, and execution files (dual-mode)."""
    print(f"📂 Periodic file scanner started (every 5s)")

    notification_handler = NotificationHandler(app.bot, chat_id)
    completion_handler = CompletionHandler(app.bot, chat_id)
    summary_handler = SummaryHandler(app.bot, chat_id)  # Phase 3 - v4.0.0
    execution_handler = WorkflowExecutionHandler(app.bot, chat_id)  # Phase 4 - WorkflowExecution completion

    while not bot_state.shutdown_requested:
        await asyncio.sleep(5)  # Scan every 5 seconds

        # Phase 3 - v4.0.0: Scan for new summaries (prioritize over notifications)
        await scan_and_process(summaries_dir, "summary_*.json", summary_handler, "send_workflow_menu", "summary")

        # v3 backward compat: Scan for new notifications
        await scan_and_process(notification_dir, "notify_*.json", notification_handler, "send_notification", "notification")

        # Scan for new completions (v3 backward compat)
        await scan_and_process(completion_dir, "completion_*.json", completion_handler, "send_completion", "completion")

        # Phase 4 - v4.0.0: Scan for workflow execution completions
        await scan_and_process(executions_dir, "execution_*.json", execution_handler, "send_execution_completion", "execution")


async def progress_poller(
    app: "Application",
    progress_dir: Path,
    chat_id: int,
    poll_interval: float = 2.0
) -> None:
    """Poll progress files and update Telegram messages with streaming progress."""
    print(f"📊 Progress poller started (every {poll_interval}s)")
    print(f"   Progress directory: {progress_dir}")
    print(f"   Active tracking: {len(bot_state.active_progress_updates)} workflows")

    while not bot_state.shutdown_requested:
        await asyncio.sleep(poll_interval)

        if not progress_dir.exists():
            continue

        # Get all JSON files in progress directory
        all_json_files = list(progress_dir.glob("*.json"))

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
                try:
                    await app.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=progress_text,
                        parse_mode="HTML"
                    )
                    print(f"   ✅ Message updated successfully")
                except Exception as edit_error:
                    # Handle Telegram API errors gracefully (e.g., duplicate content)
                    error_type = type(edit_error).__name__
                    if "BadRequest" in error_type and "not modified" in str(edit_error).lower():
                        print(f"   ⏭️  Skipped update (content unchanged)")
                    else:
                        # Re-raise unexpected errors
                        raise

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


async def idle_timeout_monitor(idle_timeout_seconds: int) -> None:
    """Monitor idle time and request shutdown if timeout exceeded."""
    print(f"⏱️  Idle timeout monitor started ({idle_timeout_seconds}s)")

    while not bot_state.shutdown_requested:
        await asyncio.sleep(30)  # Check every 30 seconds

        idle_time = bot_state.get_idle_time()
        if idle_time >= idle_timeout_seconds:
            print(f"\n⏱️  Idle timeout reached ({idle_time:.0f}s >= {idle_timeout_seconds}s)")
            print("   Shutting down...")
            bot_state.shutdown_requested = True
            break

        # Log progress every 5 minutes
        if int(idle_time) % 300 == 0 and idle_time > 0:
            remaining = idle_timeout_seconds - idle_time
            print(f"⏱️  Idle: {idle_time:.0f}s, auto-shutdown in {remaining:.0f}s")
