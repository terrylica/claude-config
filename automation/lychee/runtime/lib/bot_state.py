"""
Bot shared state management.

Global state shared between bot main file and handler modules.
"""

import asyncio
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
