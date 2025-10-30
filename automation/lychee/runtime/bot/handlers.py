"""
Telegram callback handlers for bot workflows.

Action handlers for button clicks and workflow selections.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from telegram.ext import ContextTypes

import bot_state
from workspace_helpers import compute_workspace_hash
from format_utils import get_workspace_config, convert_to_telegram_markdown
from bot_utils import log_event
from message_builders import build_workflow_start_message


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
        markdown_msg = (
            "❌ Detailed results not available\n\n"
            "The lychee JSON output file was not found. This may happen if:\n"
            "• Validation was run before progressive disclosure was implemented\n"
            "• Results file was manually deleted\n"
            "• Workspace path changed"
        )
        await query.message.reply_text(
            convert_to_telegram_markdown(markdown_msg),
            parse_mode="MarkdownV2"
        )
        return

    try:
        with open(json_results, 'r') as f:
            lychee_data = json.load(f)
    except json.JSONDecodeError as e:
        markdown_msg = (
            f"❌ Failed to parse lychee JSON output\n\n"
            f"Error: {e}\n\n"
            f"File: `{json_results}`"
        )
        await query.message.reply_text(
            convert_to_telegram_markdown(markdown_msg),
            parse_mode="MarkdownV2"
        )
        raise  # Fail-fast

    # Format error_map as readable text
    error_map = lychee_data.get("error_map", {})

    if not error_map:
        markdown_msg = (
            "✅ No detailed errors found\n\n"
            "The error_map is empty. All links may have been fixed."
        )
        await query.message.reply_text(
            convert_to_telegram_markdown(markdown_msg),
            parse_mode="MarkdownV2"
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

    markdown_msg = f"📋 **Detailed Error Breakdown**\n{details_text}"
    await query.message.reply_text(
        convert_to_telegram_markdown(markdown_msg),
        parse_mode='MarkdownV2'
    )

    print(f"📋 Sent detailed breakdown for session {session_id}")


async def handle_workflow_selection(
    query,
    workspace_id: str,
    workspace_path: str,
    session_id: str,
    action: str,
    correlation_id: str,
    context: ContextTypes.DEFAULT_TYPE,
    selections_dir: Path,
    tracking_dir: Path
) -> None:
    """
    Handle workflow selection button click.

    Creates WorkflowSelection file for orchestrator to process.

    Args:
        query: Telegram CallbackQuery object
        workspace_id: Workspace identifier
        workspace_path: Absolute path to workspace
        session_id: Session identifier
        action: Selected action (workflow_<id> or custom_prompt)
        correlation_id: Correlation ID for tracing
        context: Bot context for accessing bot instance
        selections_dir: Selections directory path
        tracking_dir: Tracking directory path

    Raises:
        All errors propagate (fail-fast)
    """
    workspace_hash = compute_workspace_hash(Path(workspace_path))

    # Extract workflow ID from action
    if action == "custom_prompt":
        # TODO Phase 4: Implement custom prompt handler
        # For now, acknowledge and return
        markdown_msg = (
            "✏️ Custom Prompt\n\n"
            "Custom workflow prompts will be available in Phase 4.\n"
            "For now, please select a preset workflow."
        )
        await query.edit_message_text(
            text=convert_to_telegram_markdown(markdown_msg),
            parse_mode="MarkdownV2"
        )
        return

    workflow_id = action.replace("workflow_", "")

    # Create selection file
    selection_file = selections_dir / f"selection_{session_id}_{workspace_hash}.json"

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

    selections_dir.mkdir(parents=True, exist_ok=True)
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
        parse_mode="MarkdownV2"
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

    # Extract user prompt and last response for message context preservation
    user_prompt = summary_data.get("last_user_prompt", "")
    last_response = summary_data.get("last_response", "")

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
        "session_id": session_id,
        "user_prompt": user_prompt,  # Preserve for completion message
        "last_response": last_response  # Preserve for completion message
    }

    bot_state.active_progress_updates[progress_key] = tracking_data

    # Persist tracking data to survive bot restarts (watchexec)
    tracking_dir.mkdir(parents=True, exist_ok=True)
    tracking_file = tracking_dir / f"{workspace_hash}_{session_id}_{workflow_id}_tracking.json"  # Use hash in filename
    tracking_file.write_text(json.dumps(tracking_data, indent=2))
    print(f"   📌 Tracking progress updates (message_id={message_id}, branch={git_branch})")
