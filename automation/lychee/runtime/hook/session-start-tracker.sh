#!/usr/bin/env bash
# Session Start Time Tracker
# Version: 1.0.0
#
# Purpose: Track session start time for duration calculation in Stop hook
# Execution: On SessionStart event
# Output: Writes timestamp to state file

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

TIMESTAMP_DIR="$HOME/.claude/automation/lychee/state/session_timestamps"
mkdir -p "$TIMESTAMP_DIR"

# =============================================================================
# Read Hook Input
# =============================================================================

# Read JSON input from stdin
hook_input=$(cat) || hook_input=""

# Extract session_id
if [[ -n "$hook_input" ]]; then
    session_id=$(echo "$hook_input" | jq -r '.session_id // ""' 2>/dev/null) || session_id=""
else
    session_id=""
fi

# Generate fallback session_id if not provided
if [[ -z "$session_id" ]]; then
    session_id="session-$(date +%Y%m%d-%H%M%S)-$$"
fi

# =============================================================================
# Write Start Timestamp
# =============================================================================

# Write current Unix timestamp (seconds since epoch)
timestamp_file="$TIMESTAMP_DIR/${session_id}.timestamp"
date +%s > "$timestamp_file"

# Log for debugging
{
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Session started: $session_id"
    echo "  → Timestamp file: $timestamp_file"
    echo "  → Start time: $(date +%s)"
} >> "$HOME/.claude/logs/session-tracker.log" 2>&1

# =============================================================================
# Cleanup Old Timestamps (>7 days)
# =============================================================================

# Clean up timestamp files older than 7 days to prevent accumulation
find "$TIMESTAMP_DIR" -name "*.timestamp" -type f -mtime +7 -delete 2>/dev/null || true

exit 0
