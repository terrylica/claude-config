#!/usr/bin/env bash
#
# Development runner for multi-workspace Telegram bot with auto-reload
#
# Usage: ./run-bot-dev-watchexec.sh
#
# Features:
# - Auto-restarts on Python file changes using watchexec (Rust-based)
# - Respects .gitignore automatically
# - Built-in debouncing (50ms)
# - Graceful shutdown on Ctrl+C
# - Logs to stdout

set -euo pipefail

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_SCRIPT="$BOT_DIR/multi-workspace-bot.py"
WATCH_DIRS=(
    "$BOT_DIR"
    "$BOT_DIR/../lib"
    "$BOT_DIR/../orchestrator"
)

# Check if watchexec is installed
if ! command -v watchexec &> /dev/null; then
    echo "❌ watchexec not found. Installing via Homebrew..."
    brew install watchexec
fi

echo "=========================================="
echo "🤖 Telegram Bot Development Server"
echo "=========================================="
echo "Bot: $BOT_SCRIPT"
echo "Auto-reload: ENABLED (watchexec 🦀)"
echo ""
echo "Watching directories:"
for dir in "${WATCH_DIRS[@]}"; do
    echo "  - $dir/*.py"
done
echo ""
echo "Features:"
echo "  ✓ Respects .gitignore"
echo "  ✓ Debouncing (50ms)"
echo "  ✓ Graceful restarts"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Build watch paths for watchexec
WATCH_ARGS=()
for dir in "${WATCH_DIRS[@]}"; do
    WATCH_ARGS+=("--watch" "$dir")
done

# Run bot with watchexec
# --restart: Kill and restart the process on changes
# --exts: Only watch .py files
# --debounce: Wait 100ms before restarting (accounts for multi-file saves)
# --stop-signal: Send SIGTERM for graceful shutdown
# --stop-timeout: Wait 5s for graceful shutdown before SIGKILL
exec watchexec \
    "${WATCH_ARGS[@]}" \
    --exts py \
    --restart \
    --debounce 100ms \
    --stop-signal SIGTERM \
    --stop-timeout 5s \
    -- doppler run --project claude-config --config dev -- uv run "$BOT_SCRIPT"
