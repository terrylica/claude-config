"""
Telegram message builders for bot workflows.

Pure message formatting functions for consistent Telegram display.
"""

import json
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

    # Compact session + debug log line
    session_debug_line = f"session={session_id} | 🐛 debug=~/.claude/debug/${{session}}.txt"

    return (
        f"{prompt_line}{emoji} **{last_response}**\n\n"
        f"`{repo_display}` | `{working_dir}`\n"
        f"`{session_debug_line}` ({duration}s)\n"
        f"**↯**: `{git_branch}` | {git_compact}{git_porcelain_display}\n\n"
        f"**Lychee**: {lychee_details}\n\n"
        f"⏳ **Workflow: {workflow_name}**\n"
        f"**Stage**: starting | **Progress**: 0%\n"
        f"**Status**: Starting..."
    )


def build_completion_message(completion: Dict[str, Any], emoji: str) -> str:
    """
    Format completion data as Telegram message.

    Args:
        completion: Completion data dictionary
        emoji: Workspace emoji

    Returns:
        Formatted Telegram message with markdown
    """
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

    # Compact session + debug log line
    session_debug_line = f"session={session_id} | 🐛 debug=~/.claude/debug/${{session}}.txt"

    message = f"""{emoji} {status_emoji} **{title}**

**Workspace**: `{workspace_id}`
`{session_debug_line}`
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


def build_execution_message(execution: Dict[str, Any], emoji: str, workflow_name: str) -> str:
    """
    Format WorkflowExecution data as Telegram message.

    Args:
        execution: Execution data dictionary
        emoji: Workspace emoji
        workflow_name: Workflow display name

    Returns:
        Formatted Telegram message with markdown
    """
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

    # Debug log path
    debug_log = f"~/.claude/debug/{session_id}.txt"

    message = f"""{emoji} {status_emoji} **{title}**

**Workflow**: {full_workflow_name}
**Workspace**: `{workspace_id}`
**Session**: `{session_id}`
**Debug Log**: `{debug_log}`
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
