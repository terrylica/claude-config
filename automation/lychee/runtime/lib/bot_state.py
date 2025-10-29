"""
Bot shared state management.

Global state shared between bot main file and handler modules.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Global state for bot lifecycle
shutdown_requested: bool = False
last_activity_time: Optional[float] = None

# Phase 4 - v4.1.0: Progress tracking persistence (survives watchexec restarts)
# Keyed by (workspace_id, session_id, workflow_id) -> tracking data
active_progress_updates: Dict[tuple, Dict[str, Any]] = {}

# Phase 3 - v4.0.0: Summary caching for instant workflow menu rendering
# Keyed by (workspace_id, session_id) -> summary data
summary_cache: Dict[tuple, Dict[str, Any]] = {}

# Phase 3 - v4.0.0: Workflow registry
workflow_registry: Optional[Dict[str, Any]] = None


def update_activity() -> None:
    """Update last activity timestamp."""
    global last_activity_time
    last_activity_time = asyncio.get_event_loop().time()


def get_idle_time() -> float:
    """Get seconds since last activity."""
    if last_activity_time is None:
        return 0.0
    return asyncio.get_event_loop().time() - last_activity_time


def restore_progress_tracking(tracking_dir: Path) -> None:
    """
    Restore progress tracking state from disk.

    Reads tracking JSON files and populates active_progress_updates dictionary.
    Survives watchexec restarts.

    Args:
        tracking_dir: Directory containing tracking JSON files

    Raises:
        json.JSONDecodeError: If tracking file contains invalid JSON (logged, not raised)
        KeyError: If required fields missing (logged, not raised)
    """
    print("\n🔄 Restoring progress tracking state...")

    if not tracking_dir.exists():
        print(f"   ℹ️  No tracking state to restore")
        return

    restored_count = 0
    for tracking_file in tracking_dir.glob("*_tracking.json"):
        try:
            tracking_data = json.loads(tracking_file.read_text())
            # Get IDs from tracking data (more reliable than filename parsing)
            workspace_id = tracking_data["workspace_id"]
            session_id = tracking_data["session_id"]
            # Extract workflow_id from filename: {workspace}_{session}_{workflow}_tracking.json
            # UUIDs use dashes (not underscores), so split is simple:
            # Example: 81e622b5_fb77a731-3922-4da4-bc54-4b2db9de6e40_commit-changes_tracking.json
            filename_parts = tracking_file.stem.replace("_tracking", "").split("_")
            # parts[0] = workspace_id (8 chars hash)
            # parts[1] = session_id (UUID with dashes)
            # parts[2:] = workflow_id (might contain underscores)
            workflow_id = "_".join(filename_parts[2:])

            progress_key = (workspace_id, session_id, workflow_id)
            active_progress_updates[progress_key] = tracking_data
            restored_count += 1
            print(f"   ✓ Restored: {workspace_id}/{workflow_id} (msg {tracking_data['message_id']})")
        except Exception as e:
            print(f"   ⚠️  Failed to restore {tracking_file.name}: {e}")

    print(f"   ✅ Restored {restored_count} tracked workflow(s)")
