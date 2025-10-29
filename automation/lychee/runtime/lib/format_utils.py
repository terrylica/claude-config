"""
Formatting utilities for Telegram bot messages.

Pure utility functions with no external dependencies (except workspace_helpers).
"""

from pathlib import Path
from typing import Dict, Optional

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

    Args:
        text: Text to escape

    Returns:
        Text with markdown characters escaped
    """
    return text.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')


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
