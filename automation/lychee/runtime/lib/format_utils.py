"""
Formatting utilities for Telegram bot messages.

Pure utility functions with no external dependencies (except workspace_helpers).
"""

from pathlib import Path
from typing import Dict, Optional
import json

# Import workspace helpers for config loading
import sys
sys.path.insert(0, str(Path(__file__).parent))
from workspace_helpers import get_workspace_id_from_path, load_registry


def format_git_status_compact(modified: int, staged: int, untracked: int) -> str:
    """
    Format compact git status line.

    Args:
        modified: Count of modified files
        staged: Count of staged files
        untracked: Count of untracked files

    Returns:
        Formatted status string (e.g., "M:2 S:0 U:1")
    """
    return f"M:{modified} S:{staged} U:{untracked}"


def format_repo_display(path: str) -> str:
    """
    Format repository path with home directory as tilde.

    Args:
        path: Absolute path to repository

    Returns:
        Path with home directory replaced by ~
    """
    return str(path).replace(str(Path.home()), "~")


def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram markdown.

    DEPRECATED: Use escape_html() instead. HTML mode is industry best practice.

    Args:
        text: Text to escape

    Returns:
        Text with markdown characters escaped

    Note:
        Square brackets [] are NOT escaped because they only have special meaning
        in Telegram Markdown when used in link syntax [text](url). Standalone
        brackets should be displayed as-is.
    """
    return text.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')


def escape_html(text: str) -> str:
    """
    Escape special characters for Telegram HTML mode.

    HTML mode is the industry-recommended best practice for Telegram bots:
    - Only 3 characters need escaping (vs 40+ in Markdown)
    - More reliable, simpler, less error-prone
    - Prevents common issues with underscores in filenames

    Args:
        text: Text to escape

    Returns:
        Text with HTML entities escaped

    Example:
        >>> escape_html("File: handler_classes.py & utils.py")
        'File: handler_classes.py &amp; utils.py'
    """
    # Order matters: escape & first to avoid double-escaping
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def strip_markdown(text: str) -> str:
    """
    Strip markdown formatting characters from text.

    DEPRECATED: Use strip_html() for HTML-formatted messages.

    Use this when text will be wrapped in markdown formatting to avoid nested/invalid markdown.

    Args:
        text: Text with potential markdown

    Returns:
        Plain text with markdown characters removed
    """
    # Remove common markdown: ** (bold), * (italic), _ (italic), ` (code), [ ] (links)
    import re
    # Remove bold (**text**)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove italic (*text* or _text_)
    text = re.sub(r'[*_](.*?)[*_]', r'\1', text)
    # Remove code (`text`)
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove remaining single * or _
    text = text.replace('*', '').replace('_', '')
    return text


def strip_html(text: str) -> str:
    """
    Strip HTML tags from text for plain-text services (e.g., Pushover).

    Use this when converting HTML-formatted Telegram messages to plain text
    for services that don't support HTML.

    Args:
        text: Text with HTML tags

    Returns:
        Plain text with HTML tags removed

    Example:
        >>> strip_html("File: <code>handler_classes.py</code> & <b>utils.py</b>")
        'File: handler_classes.py & utils.py'
    """
    import re
    # Remove all HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Decode HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text


def truncate_markdown_safe(text: str, max_length: int = 300) -> dict:
    """
    Truncate text preserving markdown validity by closing open tags.

    Pattern adapted from Claude-Code-Remote (MIT License):
    Source: https://github.com/JessyTsui/Claude-Code-Remote
    Reference: src/channels/telegram/telegram.js:186-197

    SLO:
    - Correctness: 100% (all markdown tags closed after truncation)
    - Observability: Returns metadata about truncation and tag closure
    - Maintainability: Single responsibility, < 20 lines logic

    Args:
        text: Text containing markdown to truncate
        max_length: Maximum character length (default: 300)

    Returns:
        dict with keys:
            - text: Truncated text with closed markdown tags
            - original_length: Length before truncation
            - truncated_length: Length after truncation (excluding ellipsis)
            - tags_closed: List of markdown tags that were auto-closed

    Raises:
        ValueError: If max_length < 1
        TypeError: If text is not string

    Example:
        >>> result = truncate_markdown_safe("Hello **world", 10)
        >>> result['text']
        'Hello **wo**...'
        >>> result['tags_closed']
        ['**']
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be str, got {type(text).__name__}")
    if max_length < 1:
        raise ValueError(f"max_length must be >= 1, got {max_length}")

    original_length = len(text)

    # Return as-is if within limit
    if original_length <= max_length:
        return {
            "text": text,
            "original_length": original_length,
            "truncated_length": original_length,
            "tags_closed": []
        }

    # Truncate to max_length
    truncated = text[:max_length]
    tags_closed = []

    # Close unclosed markdown tags
    # Pattern: Count occurrences; if odd, tag is open
    if truncated.count('**') % 2 == 1:
        truncated += '**'
        tags_closed.append('**')

    if truncated.count('`') % 2 == 1:
        truncated += '`'
        tags_closed.append('`')

    if truncated.count('_') % 2 == 1:
        truncated += '_'
        tags_closed.append('_')

    # Add ellipsis to indicate truncation
    result_text = truncated + '...'

    return {
        "text": result_text,
        "original_length": original_length,
        "truncated_length": len(truncated),
        "tags_closed": tags_closed
    }


def extract_conversation_from_transcript(transcript_path: Path) -> dict:
    """
    Extract user prompt and Claude response from transcript JSONL file.

    Pattern inspired by Claude-Code-Remote tmux monitoring, adapted for transcript files:
    Source: https://github.com/JessyTsui/Claude-Code-Remote
    Reference: src/utils/tmux-monitor.js (concept adapted)

    SLO:
    - Correctness: 100% (extracts last complete Q&A pair)
    - Observability: Returns metadata about extraction success
    - Maintainability: Single responsibility, uses stdlib json

    Args:
        transcript_path: Absolute path to Claude transcript JSONL file

    Returns:
        dict with keys:
            - user_prompt: Last user message (truncated to 200 chars with markdown safety)
            - assistant_response: Last Claude response (truncated to 300 chars with markdown safety)
            - truncated: Boolean indicating if either field was truncated
            - message_count: Total messages in transcript

    Raises:
        FileNotFoundError: If transcript file doesn't exist
        json.JSONDecodeError: If transcript contains invalid JSON
        ValueError: If transcript is empty or malformed

    Example:
        >>> result = extract_conversation_from_transcript(Path('/path/to/transcript.jsonl'))
        >>> result['user_prompt']
        'How do I fix this bug?'
        >>> result['assistant_response']
        'You can fix it by...'
    """
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    # Parse JSONL file (one JSON object per line)
    messages = []
    with transcript_path.open('r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                # Claude transcript format: {message: {role, content, ...}}
                wrapper = json.loads(line)
                if 'message' in wrapper:
                    messages.append(wrapper['message'])
                else:
                    raise ValueError(f"Line {line_num}: Missing 'message' key")
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Line {line_num}: {e.msg}",
                    e.doc,
                    e.pos
                )

    if not messages:
        raise ValueError(f"Transcript is empty: {transcript_path}")

    # Extract last user TEXT message (skip tool-result-only messages)
    user_messages = [m for m in messages if m.get('role') == 'user']
    last_user_raw = ""
    if user_messages:
        print(f"   🔍 EXTRACT DEBUG: Found {len(user_messages)} user messages")

        # Search backwards for last message with actual text content
        for user_msg in reversed(user_messages):
            content = user_msg.get('content', '')
            print(f"   🔍 EXTRACT DEBUG: Checking message, content type: {type(content)}")

            if isinstance(content, str):
                # Simple text message
                if content.strip():
                    last_user_raw = content
                    print(f"   🔍 EXTRACT DEBUG: Found string content: {repr(content[:100])}")
                    break
            elif isinstance(content, list):
                # Array format - extract only text blocks, skip tool_result
                text_blocks = [
                    block.get('text', '')
                    for block in content
                    if isinstance(block, dict) and block.get('type') == 'text'
                ]
                if text_blocks:
                    last_user_raw = ' '.join(text_blocks)
                    print(f"   🔍 EXTRACT DEBUG: Found {len(text_blocks)} text blocks")
                    break
                else:
                    print(f"   🔍 EXTRACT DEBUG: Message contains only tool results, skipping")
            else:
                # Fallback
                last_user_raw = str(content)
                if last_user_raw.strip():
                    break

        print(f"   🔍 EXTRACT DEBUG: Final user raw content: {repr(last_user_raw[:300])}")

    # Extract last assistant message
    assistant_messages = [m for m in messages if m.get('role') == 'assistant']
    last_assistant_raw = ""
    if assistant_messages:
        # Assistant content is array of content blocks
        content_blocks = assistant_messages[-1].get('content', [])
        print(f"   🔍 EXTRACT DEBUG: Found {len(assistant_messages)} assistant messages")
        print(f"   🔍 EXTRACT DEBUG: Content blocks type: {type(content_blocks)}, is_list: {isinstance(content_blocks, list)}")
        if isinstance(content_blocks, list):
            text_blocks = [
                block.get('text', '')
                for block in content_blocks
                if block.get('type') == 'text'
            ]
            last_assistant_raw = ' '.join(text_blocks)
            print(f"   🔍 EXTRACT DEBUG: Extracted {len(text_blocks)} text blocks, total len: {len(last_assistant_raw)}")
        else:
            # Fallback if content is string (shouldn't happen but defensive)
            last_assistant_raw = str(content_blocks)
            print(f"   🔍 EXTRACT DEBUG: Fallback - content is string: {repr(content_blocks[:200])}")

    # Truncate with markdown safety
    user_result = truncate_markdown_safe(last_user_raw, max_length=200)
    assistant_result = truncate_markdown_safe(last_assistant_raw, max_length=300)

    truncated = (
        user_result['original_length'] > 200 or
        assistant_result['original_length'] > 300
    )

    return {
        "user_prompt": user_result['text'],
        "assistant_response": assistant_result['text'],
        "truncated": truncated,
        "message_count": len(messages)
    }


def get_workspace_config(
    workspace_id: Optional[str] = None,
    workspace_path: Optional[Path] = None,
    include_name: bool = False,
    verbose: bool = False
) -> Dict[str, str]:
    """
    Load workspace configuration with fallback for unregistered workspaces.

    Args:
        workspace_id: Workspace identifier (registry name or hash)
        workspace_path: Workspace path (used to derive ID if workspace_id not provided)
        include_name: Whether to include workspace name in result
        verbose: Whether to print debug logging

    Returns:
        Dictionary with 'emoji' (and optionally 'name' if include_name=True)

    Raises:
        ValueError: If neither workspace_id nor workspace_path provided
    """
    if verbose:
        print(f"   📋 Loading workspace registry...")

    # Default fallback values
    emoji = "📁"
    ws_name = workspace_path.name if workspace_path else "unknown"

    try:
        # Get workspace_id if not provided
        if workspace_id is None:
            if workspace_path is None:
                raise ValueError("Either workspace_id or workspace_path must be provided")
            workspace_id = get_workspace_id_from_path(workspace_path)

        # Load registry
        registry = load_registry()
        workspace = registry["workspaces"][workspace_id]
        emoji = workspace["emoji"]

        if include_name:
            ws_name = workspace["name"]

        if verbose:
            print(f"   ✓ Workspace config loaded: emoji={emoji}")

    except (ValueError, FileNotFoundError, KeyError):
        # Unregistered workspace - use defaults
        if verbose:
            print(f"   ⚠️  Workspace not in registry, using defaults: emoji={emoji}, path={ws_name}")

    result = {"emoji": emoji}
    if include_name:
        result["name"] = ws_name

    return result
