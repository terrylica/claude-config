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
CHANGED_FILE=""
RECENT_CHANGE=$(find /Users/terryli/.claude/automation/lychee/runtime/{bot,lib,orchestrator} \
    -name "*.py" -type f -mtime -10s 2>/dev/null | head -1)
if [[ -n "$RECENT_CHANGE" ]]; then
    CHANGED_FILE=$(basename "$RECENT_CHANGE")
    RECENT_CHANGE_FULL="$RECENT_CHANGE"
    echo "📝 Detected file change: $CHANGED_FILE"
else
    RECENT_CHANGE_FULL=""
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
if [[ -x "$NOTIFY_SCRIPT" ]]; then
    echo "🔔 Sending $REASON notification..."
    "$NOTIFY_SCRIPT" "$REASON" 0 "$WATCHEXEC_INFO_FILE" &
fi

# Run the bot and capture exit code and stderr
EXIT_CODE=0
uv run "$BOT_SCRIPT" 2> >(tee -a "$CRASH_LOG" >&2) || EXIT_CODE=$?

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
        "$NOTIFY_SCRIPT" "crash" "$EXIT_CODE" "$WATCHEXEC_INFO_FILE" "$CRASH_CONTEXT" &
    fi
fi

# Cleanup temporary files
rm -f "$WATCHEXEC_INFO_FILE" "$CRASH_LOG" "$CRASH_CONTEXT" 2>/dev/null || true

exit $EXIT_CODE
