#!/usr/bin/env bash
# Bot Wrapper with Restart Notifications
# Monitors bot process and sends notifications on startup/restart
# Usage: bot-wrapper.sh

set -euo pipefail

BOT_SCRIPT="/Users/terryli/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py"
NOTIFY_SCRIPT="/Users/terryli/.claude/automation/lychee/runtime/bot/notify-restart.sh"

# Determine restart reason from environment
# watchexec sets WATCHEXEC_COMMON_PATH when files change
if [[ -n "${WATCHEXEC_COMMON_PATH:-}" ]]; then
    REASON="code_change"
elif [[ -f "/tmp/bot_first_run_$$" ]]; then
    REASON="crash"
else
    REASON="startup"
    touch "/tmp/bot_first_run_$$"
fi

# Send startup notification (fire-and-forget, non-blocking)
if [[ -x "$NOTIFY_SCRIPT" ]]; then
    echo "🔔 Sending $REASON notification..."
    "$NOTIFY_SCRIPT" "$REASON" 0 &
fi

# Run the bot and capture exit code
EXIT_CODE=0
uv run "$BOT_SCRIPT" || EXIT_CODE=$?

# Send restart notification if bot exited abnormally
if [[ $EXIT_CODE -ne 0 ]]; then
    if [[ -x "$NOTIFY_SCRIPT" ]]; then
        echo "🔔 Sending crash notification (exit code: $EXIT_CODE)..."
        "$NOTIFY_SCRIPT" "crash" "$EXIT_CODE" &
    fi
fi

exit $EXIT_CODE
