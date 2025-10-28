#!/usr/bin/env bash
#
# Production runner for multi-workspace Telegram bot (NO auto-reload)
#
# Usage: ./run-bot-prod.sh
#
# Features:
# - No auto-reload (production mode)
# - Runs in foreground (managed by systemd/supervisor)
# - Proper signal handling
# - Logs to stdout/stderr for process manager capture

set -euo pipefail

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_SCRIPT="$BOT_DIR/multi-workspace-bot.py"

echo "=========================================="
echo "🤖 Telegram Bot Production Server"
echo "=========================================="
echo "Bot: $BOT_SCRIPT"
echo "Auto-reload: DISABLED (production mode)"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Run bot without auto-reload
exec doppler run --project claude-config --config dev -- "$BOT_SCRIPT"
