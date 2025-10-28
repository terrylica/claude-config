#!/usr/bin/env bash
#
# Development runner for multi-workspace Telegram bot with auto-reload
#
# Usage: ./run-bot-dev.sh
#
# Features:
# - Auto-restarts on Python file changes in bot/, lib/, orchestrator/ directories
# - Graceful shutdown on Ctrl+C
# - Logs to stdout

set -euo pipefail

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_SCRIPT="$BOT_DIR/multi-workspace-bot.py"

# Check if nodemon is installed
if ! command -v nodemon &> /dev/null; then
    echo "❌ nodemon not found. Installing..."
    npm install -g nodemon
fi

echo "=========================================="
echo "🤖 Telegram Bot Development Server"
echo "=========================================="
echo "Bot: $BOT_SCRIPT"
echo "Auto-reload: ENABLED (nodemon)"
echo ""
echo "Watching directories:"
echo "  - $BOT_DIR/*.py"
echo "  - $BOT_DIR/../lib/*.py"
echo "  - $BOT_DIR/../orchestrator/*.py"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Run bot with nodemon
# --watch: directories to watch for changes
# --ext: file extensions to monitor
# --exec: command to run
nodemon \
    --watch "$BOT_DIR" \
    --watch "$BOT_DIR/../lib" \
    --watch "$BOT_DIR/../orchestrator" \
    --ext py \
    --exec "doppler run --project claude-config --config dev -- python" \
    "$BOT_SCRIPT"
