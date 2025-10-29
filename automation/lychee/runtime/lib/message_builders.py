"""
Telegram message builders for bot workflows.

Pure message formatting functions for consistent Telegram display.
"""

from typing import Dict, Any

# Import formatting utilities
from format_utils import (
    format_git_status_compact,
    format_repo_display,
    escape_markdown
)


def build_workflow_start_message(
    emoji: str,
    workflow_name: str,
    session_id: str,
    summary_data: Dict[str, Any],
    workspace_path: str
) -> str:
    """
    Build initial workflow start message with full context.

    Args:
        emoji: Workspace emoji
        workflow_name: Workflow display name
        session_id: Session identifier
        summary_data: Cached session summary
        workspace_path: Workspace path

    Returns:
        Formatted Telegram message
    """
    # Extract session context from cached summary
    git_status = summary_data.get("git_status", {})
    lychee_status = summary_data.get("lychee_status", {})

    git_branch = git_status.get("branch", "unknown")
    git_modified = git_status.get("modified_files", 0)
    git_untracked = git_status.get("untracked_files", 0)
    git_staged = git_status.get("staged_files", 0)
    git_porcelain_lines = git_status.get('porcelain', [])

    # Extract repository root and working directory
    repository_root = summary_data.get("repository_root", summary_data.get("workspace_path", workspace_path))
    working_dir = summary_data.get("working_directory", ".")
    repo_display = format_repo_display(repository_root)

    # Extract and truncate user prompt and last response
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
        display_lines = git_porcelain_lines[:10]
        porcelain_text = "\n".join(display_lines)
        if len(git_porcelain_lines) > 10:
            porcelain_text += f"\n... and {len(git_porcelain_lines) - 10} more"
        # Wrap in code block for proper formatting (prevents markdown parsing issues)
        git_porcelain_display = f"\n```\n{porcelain_text}\n```"

    # Compact git status
    git_compact = format_git_status_compact(git_modified, git_staged, git_untracked)

    # Escape markdown in user_prompt and last_response
    if user_prompt:
        user_prompt = escape_markdown(user_prompt)
    if last_response:
        last_response = escape_markdown(last_response)

    # Build message with full context
    prompt_line = f"❓ _{user_prompt}_\n" if user_prompt else ""

    # Escape lychee details
    lychee_details = lychee_status.get('details', 'Not run')
    if lychee_details:
        lychee_details = escape_markdown(lychee_details)

    return (
        f"{prompt_line}{emoji} **{last_response}**\n\n"
        f"`{repo_display}` | `{working_dir}`\n"
        f"`{session_id}` ({duration}s)\n"
        f"**↯**: `{git_branch}` | {git_compact}{git_porcelain_display}\n\n"
        f"**Lychee**: {lychee_details}\n\n"
        f"⏳ **Workflow: {workflow_name}**\n"
        f"**Stage**: starting | **Progress**: 0%\n"
        f"**Status**: Starting..."
    )
