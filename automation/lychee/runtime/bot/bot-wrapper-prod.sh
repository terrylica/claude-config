#!/usr/bin/env bash
#
# Production Bot Wrapper with Health Monitoring
#
# Monitors bot process and sends alerts on startup/crash/health issues
# Runs under watchexec supervision (which is supervised by launchd)

set -euo pipefail

BOT_SCRIPT="/Users/terryli/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py"
NOTIFY_SCRIPT="/Users/terryli/.claude/automation/lychee/runtime/bot/notify-restart.sh"
BOT_LOG="/Users/terryli/.claude/automation/lychee/logs/telegram-handler.log"
CRASH_LOG="/tmp/bot_crash_prod_$$.log"

# Production mode markers
RESTART_COUNT_FILE="/tmp/bot_restart_count"
LAST_RESTART_FILE="/tmp/bot_last_restart"

# Get or initialize restart counter
get_restart_count() {
    if [[ -f "$RESTART_COUNT_FILE" ]]; then
        cat "$RESTART_COUNT_FILE"
    else
        echo "0"
    fi
}

increment_restart_count() {
    local count=$(get_restart_count)
    local new_count=$((count + 1))
    echo "$new_count" > "$RESTART_COUNT_FILE"
    echo "$(date +%s)" > "$LAST_RESTART_FILE"
    echo "$new_count"
}

reset_restart_count() {
    echo "0" > "$RESTART_COUNT_FILE"
}

check_restart_rate() {
    local count=$(get_restart_count)
    if [[ $count -eq 0 ]]; then
        return 0
    fi

    local last_restart=$(cat "$LAST_RESTART_FILE" 2>/dev/null || echo "0")
    local now=$(date +%s)
    local elapsed=$((now - last_restart))

    # If 5+ restarts in last 60 seconds, alert critically
    if [[ $count -ge 5 ]] && [[ $elapsed -lt 60 ]]; then
        echo "CRITICAL: $count restarts in ${elapsed}s"
        return 1
    fi

    # Reset counter if last restart was > 5 minutes ago (stable)
    if [[ $elapsed -gt 300 ]]; then
        reset_restart_count
    fi

    return 0
}

# Detect restart reason
if [[ ! -f "/tmp/bot_first_run_prod" ]]; then
    REASON="startup"
    touch "/tmp/bot_first_run_prod"
    reset_restart_count
else
    REASON="code_change"
    restart_count=$(increment_restart_count)

    # Check if restart rate is too high
    if ! check_restart_rate; then
        REASON="crash_loop"
        echo "⚠️  HIGH RESTART RATE DETECTED - Potential crash loop!"
    fi
fi

echo "=========================================="
echo "🤖 Bot Starting (Production Mode)"
echo "=========================================="
echo "Reason: $REASON"
echo "Restart count: $(get_restart_count)"
echo "Supervisor: launchd → watchexec → THIS WRAPPER"
echo "=========================================="
echo ""

# Send startup notification (fire-and-forget, non-blocking)
if [[ -x "$NOTIFY_SCRIPT" ]]; then
    echo "🔔 Sending $REASON notification..."
    doppler run --project claude-config --config dev -- "$NOTIFY_SCRIPT" "$REASON" 0 "/tmp/watchexec_info_prod.json" &
fi

# Run the bot with doppler and capture exit code and stderr
EXIT_CODE=0
doppler run --project claude-config --config dev -- uv run "$BOT_SCRIPT" 2> >(tee -a "$CRASH_LOG" >&2) || EXIT_CODE=$?

# Handle bot exit
if [[ $EXIT_CODE -ne 0 ]]; then
    echo "=========================================="
    echo "❌ Bot Exited Abnormally"
    echo "=========================================="
    echo "Exit code: $EXIT_CODE"
    echo "Restart count: $(get_restart_count)"
    echo "=========================================="

    # Capture crash context
    CRASH_CONTEXT="/tmp/bot_crash_context_prod_$$.txt"
    echo "Exit code: $EXIT_CODE" > "$CRASH_CONTEXT"
    echo "Restart count: $(get_restart_count)" >> "$CRASH_CONTEXT"
    echo "" >> "$CRASH_CONTEXT"

    if [[ -f "$BOT_LOG" ]]; then
        echo "=== Last 20 lines of bot log ===" >> "$CRASH_CONTEXT"
        tail -20 "$BOT_LOG" >> "$CRASH_CONTEXT" 2>/dev/null || true
    fi

    if [[ -f "$CRASH_LOG" && -s "$CRASH_LOG" ]]; then
        echo "" >> "$CRASH_CONTEXT"
        echo "=== STDERR ===" >> "$CRASH_CONTEXT"
        tail -10 "$CRASH_LOG" >> "$CRASH_CONTEXT" 2>/dev/null || true
    fi

    # Send crash notification
    if [[ -x "$NOTIFY_SCRIPT" ]]; then
        echo "🔔 Sending crash notification..."
        doppler run --project claude-config --config dev -- "$NOTIFY_SCRIPT" "crash" "$EXIT_CODE" "/tmp/watchexec_info_prod.json" "$CRASH_CONTEXT" &
    fi

    # Cleanup
    rm -f "$CRASH_LOG" "$CRASH_CONTEXT" 2>/dev/null || true
else
    echo "✅ Bot exited cleanly (exit code: 0)"
fi

exit $EXIT_CODE
