#!/usr/bin/env bash
# Bot Wrapper with Restart Notifications
# Monitors bot process and sends notifications on startup/restart
# Usage: bot-wrapper.sh

set -euo pipefail

BOT_SCRIPT="/Users/terryli/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py"
NOTIFY_SCRIPT="/Users/terryli/.claude/automation/lychee/runtime/bot/notify-restart.sh"
BOT_LOG="/Users/terryli/.claude/automation/lychee/logs/telegram-handler.log"
CRASH_LOG="/tmp/bot_crash_$$.log"
FIRST_RUN_MARKER="/tmp/bot_first_run"

# Capture all watchexec environment variables for diagnostic info
WATCHEXEC_INFO_FILE="/tmp/watchexec_info_$$.json"

# Detect changed file first (before creating JSON)
# Find most recently modified Python file (within last minute)
CHANGED_FILE=""
RECENT_CHANGE_FULL=""

# Get current time in seconds since epoch
NOW=$(date +%s)

# Find most recently modified .py file in watched directories
MOST_RECENT_FILE=""
MOST_RECENT_TIME=0

for dir in /Users/terryli/.claude/automation/lychee/runtime/{bot,lib,orchestrator}; do
    if [[ -d "$dir" ]]; then
        while IFS= read -r file; do
            if [[ -f "$file" ]]; then
                # Get file modification time
                FILE_MTIME=$(stat -f %m "$file" 2>/dev/null || echo "0")
                AGE=$((NOW - FILE_MTIME))

                # If file was modified in last 60 seconds and is newer than current best
                if [[ $AGE -lt 60 ]] && [[ $FILE_MTIME -gt $MOST_RECENT_TIME ]]; then
                    MOST_RECENT_FILE="$file"
                    MOST_RECENT_TIME=$FILE_MTIME
                    echo "📝 Found recently modified file: $(basename "$file") (${AGE}s ago)"
                fi
            fi
        done < <(find "$dir" -name "*.py" -type f 2>/dev/null)
    fi
done

if [[ -n "$MOST_RECENT_FILE" ]]; then
    CHANGED_FILE=$(basename "$MOST_RECENT_FILE")
    RECENT_CHANGE_FULL="$MOST_RECENT_FILE"
    AGE=$((NOW - MOST_RECENT_TIME))
    echo "✅ Detected file change: $CHANGED_FILE (${AGE}s ago, path: $RECENT_CHANGE_FULL)"
else
    echo "⚠️  No recently modified files detected (checked last 60s)"
fi

# Create diagnostic info JSON
cat > "$WATCHEXEC_INFO_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "watchexec": {
    "common_path": "${RECENT_CHANGE_FULL}",
    "created_path": "",
    "removed_path": "",
    "renamed_path": "",
    "written_path": "${RECENT_CHANGE_FULL}",
    "meta_changed_path": "",
    "otherwise_changed_path": ""
  },
  "environment": {
    "user": "${USER:-unknown}",
    "shell": "${SHELL:-unknown}",
    "pwd": "$(pwd)"
  }
}
EOF

# Determine restart reason
# First run: create marker and set reason to "startup"
# Subsequent runs: check if this is a watchexec restart or a crash
if [[ ! -f "$FIRST_RUN_MARKER" ]]; then
    REASON="startup"
    touch "$FIRST_RUN_MARKER"
else
    # After first run, assume code_change (watchexec restart)
    # Will be updated to "crash" if exit code != 0
    REASON="code_change"
fi

# Send startup notification (fire-and-forget, non-blocking)
# Use doppler to load credentials for Telegram notification
if [[ -x "$NOTIFY_SCRIPT" ]]; then
    echo "🔔 Sending $REASON notification..."
    doppler run --project claude-config --config dev -- "$NOTIFY_SCRIPT" "$REASON" 0 "$WATCHEXEC_INFO_FILE" &
fi

# Run the bot with doppler and capture exit code and stderr
EXIT_CODE=0
doppler run --project claude-config --config dev -- uv run "$BOT_SCRIPT" 2> >(tee -a "$CRASH_LOG" >&2) || EXIT_CODE=$?

# Send restart notification if bot exited abnormally
if [[ $EXIT_CODE -ne 0 ]]; then
    # Capture last 20 lines of bot log for crash context
    CRASH_CONTEXT="/tmp/bot_crash_context_$$.txt"
    if [[ -f "$BOT_LOG" ]]; then
        tail -20 "$BOT_LOG" > "$CRASH_CONTEXT" 2>/dev/null || true
    fi

    # Capture stderr from crash
    if [[ -f "$CRASH_LOG" && -s "$CRASH_LOG" ]]; then
        echo "--- STDERR ---" >> "$CRASH_CONTEXT"
        tail -10 "$CRASH_LOG" >> "$CRASH_CONTEXT" 2>/dev/null || true
    fi

    if [[ -x "$NOTIFY_SCRIPT" ]]; then
        echo "🔔 Sending crash notification (exit code: $EXIT_CODE)..."
        doppler run --project claude-config --config dev -- "$NOTIFY_SCRIPT" "crash" "$EXIT_CODE" "$WATCHEXEC_INFO_FILE" "$CRASH_CONTEXT" &
    fi
fi

# Cleanup temporary files
rm -f "$WATCHEXEC_INFO_FILE" "$CRASH_LOG" "$CRASH_CONTEXT" 2>/dev/null || true

exit $EXIT_CODE
