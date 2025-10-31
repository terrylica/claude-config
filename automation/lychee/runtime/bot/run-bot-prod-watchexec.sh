#!/usr/bin/env bash
#
# Production Bot Runner with Watchexec
#
# Runs bot under watchexec supervision for auto-reload capability
# Designed to be supervised by launchd (top-level supervisor)
#
# Architecture:
#   launchd (auto-start, crash recovery, health monitoring)
#     └─> THIS SCRIPT
#         └─> watchexec (file watching, auto-reload)
#             └─> bot-wrapper-prod.sh (crash alerts)
#                 └─> doppler + uv + bot (execution)

set -euo pipefail

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_WRAPPER="$BOT_DIR/bot-wrapper-prod.sh"
STATE_DIR="$HOME/.claude/automation/lychee/state"
WATCH_DIRS=(
    "$BOT_DIR"
    "$BOT_DIR/../lib"
    "$BOT_DIR/../orchestrator"
)

# Ensure state directory exists
mkdir -p "$STATE_DIR"

# Log startup
echo "=========================================="
echo "🤖 Telegram Bot Production Server"
echo "=========================================="
echo "Mode: Production (launchd supervised)"
echo "Auto-reload: ENABLED (watchexec)"
echo "Health monitoring: ENABLED"
echo ""
echo "Watching directories:"
for dir in "${WATCH_DIRS[@]}"; do
    echo "  - $dir/*.py"
done
echo ""
echo "Supervision chain:"
echo "  launchd → watchexec → bot-wrapper → bot"
echo "=========================================="
echo ""

# Check if watchexec is installed
if ! command -v watchexec &> /dev/null; then
    echo "❌ watchexec not found. Installing via Homebrew..."
    brew install watchexec
fi

# Build watch paths for watchexec
WATCH_ARGS=()
for dir in "${WATCH_DIRS[@]}"; do
    WATCH_ARGS+=("--watch" "$dir")
done

# Send launchd startup notification
if [[ -x "$BOT_DIR/notify-launchd-event.sh" ]]; then
    "$BOT_DIR/notify-launchd-event.sh" "startup" &
fi

# Run watchexec with production wrapper
# launchd will supervise THIS process
# watchexec will supervise the bot
exec watchexec \
    "${WATCH_ARGS[@]}" \
    --exts py \
    --restart \
    --debounce 100ms \
    --stop-signal SIGTERM \
    --stop-timeout 5s \
    -- "$BOT_WRAPPER"
