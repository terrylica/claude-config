#!/usr/bin/env bash
# Cleanup Stale Hook Processes
# Run this at the start of Stop hooks to prevent cached file issues

set -euo pipefail

# Kill processes older than 1 hour that might have cached old hook files
cleanup_stale_hooks() {
    local max_age_seconds=3600  # 1 hour

    # Find and kill stale hook processes
    for pattern in "check-links-hybrid.sh" "cns_hook_entry.sh" "format-markdown.sh"; do
        # Get PIDs and their start times
        pgrep -f "$pattern" 2>/dev/null | while read -r pid; do
            # Get process start time in seconds since epoch
            if [[ "$(uname)" == "Darwin" ]]; then
                # macOS
                start_time=$(ps -p "$pid" -o lstart= 2>/dev/null | xargs -I {} date -j -f "%a %b %d %H:%M:%S %Y" "{}" +%s 2>/dev/null || echo "0")
            else
                # Linux
                start_time=$(ps -p "$pid" -o lstart= 2>/dev/null | xargs -I {} date -d "{}" +%s 2>/dev/null || echo "0")
            fi

            current_time=$(date +%s)
            age=$((current_time - start_time))

            if [[ $age -gt $max_age_seconds ]]; then
                echo "[cleanup] Killing stale process $pid (age: ${age}s, pattern: $pattern)" >> /tmp/hook-cleanup.log
                kill -9 "$pid" 2>/dev/null || true
            fi
        done
    done
}

# Only run if called directly (not sourced)
if [[ "${BASH_SOURCE[0]:-}" == "${0}" ]] || [[ -z "${BASH_SOURCE[0]:-}" ]]; then
    cleanup_stale_hooks 2>/dev/null || true
fi
