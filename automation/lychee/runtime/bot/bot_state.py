"""
Global bot state management.

This module maintains shared state across bot components.
"""
from typing import Dict, Tuple

# Shutdown flag
shutdown_requested: bool = False

# Last activity timestamp for idle timeout
last_activity_time: float = 0.0

# Workflow registry (loaded at startup)
workflow_registry: Dict = {}

# Active progress updates: (workspace_id, session_id, workflow_id) ’ tracking context
active_progress_updates: Dict[Tuple[str, str, str], Dict] = {}

# Summary cache: (workspace_id, session_id) ’ summary data
summary_cache: Dict[Tuple[str, str], Dict] = {}

# Content deduplication: (workspace_id, session_id, workflow_id) ’ last sent text
# Prevents redundant API calls when progress content hasn't changed
last_sent_content: Dict[Tuple[str, str, str], str] = {}
