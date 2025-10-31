#!/usr/bin/env bash
#
# Telegram Bot Service Manager (launchd)
#
# Usage:
#   ./bot-service.sh install   - Install and start the service
#   ./bot-service.sh uninstall - Stop and uninstall the service
#   ./bot-service.sh start     - Start the service
#   ./bot-service.sh stop      - Stop the service
#   ./bot-service.sh restart   - Restart the service
#   ./bot-service.sh status    - Show service status
#   ./bot-service.sh logs      - Tail service logs

set -euo pipefail

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$BOT_DIR/com.terryli.telegram-bot.plist"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCHD_DIR/com.terryli.telegram-bot.plist"
SERVICE_NAME="com.terryli.telegram-bot"

install_service() {
    echo "📦 Installing Telegram Bot service..."

    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$LAUNCHD_DIR"

    # Copy plist to LaunchAgents
    cp "$PLIST_FILE" "$INSTALLED_PLIST"
    echo "✓ Copied plist to $INSTALLED_PLIST"

    # Load service
    launchctl load "$INSTALLED_PLIST"
    echo "✓ Service loaded"

    # Bootstrap service
    launchctl enable "gui/$(id -u)/$SERVICE_NAME"
    echo "✓ Service enabled"

    echo ""
    echo "✅ Service installed successfully!"
    echo ""
    echo "Service will:"
    echo "  • Auto-start on login"
    echo "  • Auto-restart on crashes (10s throttle)"
    echo "  • Log to /tmp/telegram-bot.log"
    echo ""
    echo "Check status: ./bot-service.sh status"
    echo "View logs:    ./bot-service.sh logs"
}

uninstall_service() {
    echo "🗑️  Uninstalling Telegram Bot service..."

    # Stop service if running
    launchctl bootout "gui/$(id -u)/$SERVICE_NAME" 2>/dev/null || true

    # Disable service
    launchctl disable "gui/$(id -u)/$SERVICE_NAME" 2>/dev/null || true

    # Remove plist
    rm -f "$INSTALLED_PLIST"
    echo "✓ Service uninstalled"

    echo ""
    echo "✅ Service uninstalled successfully!"
}

start_service() {
    echo "▶️  Starting Telegram Bot service..."
    launchctl kickstart -k "gui/$(id -u)/$SERVICE_NAME"
    echo "✓ Service started"
    sleep 2
    status_service
}

stop_service() {
    echo "⏸️  Stopping Telegram Bot service..."
    launchctl kill SIGTERM "gui/$(id -u)/$SERVICE_NAME" 2>/dev/null || true
    echo "✓ Service stopped"
}

restart_service() {
    echo "🔄 Restarting Telegram Bot service..."
    stop_service
    sleep 1
    start_service
}

status_service() {
    echo "📊 Service Status:"
    echo ""

    if launchctl print "gui/$(id -u)/$SERVICE_NAME" &>/dev/null; then
        launchctl print "gui/$(id -u)/$SERVICE_NAME" | grep -E "state|pid|last exit"
        echo ""

        # Check if watchexec process is running (launchd supervises watchexec now)
        WATCHEXEC_PID=$(launchctl print "gui/$(id -u)/$SERVICE_NAME" | grep -o 'pid = [0-9]*' | awk '{print $3}')
        if [[ -n "$WATCHEXEC_PID" ]]; then
            echo "✅ Service is RUNNING"
            echo ""
            echo "Architecture: launchd → watchexec → bot"
            echo ""
            echo "Watchexec Process (supervised by launchd):"
            ps -p "$WATCHEXEC_PID" -o pid,ppid,state,etime,rss,command | head -2
            echo ""

            # Try to find bot process (child of watchexec tree)
            BOT_PID=$(pgrep -f "multi-workspace-bot.py" 2>/dev/null || echo "")
            if [[ -n "$BOT_PID" ]]; then
                echo "Bot Process (supervised by watchexec):"
                ps -p "$BOT_PID" -o pid,ppid,state,etime,rss,command | head -2
                echo ""
                echo "Full Process Tree:"
                ps -o pid,ppid,state,etime,rss,command | grep -E "(watchexec|multi-workspace-bot|doppler.*bot|uv.*bot)" | grep -v grep | head -10
            else
                echo "⚠️  Bot process not found (watchexec may be restarting it)"
            fi
        else
            echo "⚠️  Service is LOADED but NOT RUNNING"
        fi
    else
        echo "❌ Service is NOT INSTALLED"
        echo ""
        echo "Install with: ./bot-service.sh install"
    fi
}

tail_logs() {
    echo "📜 Tailing logs (Ctrl+C to stop)..."
    echo ""
    echo "Logs:"
    echo "  - Launchd: ~/.claude/automation/lychee/logs/telegram-bot-launchd.log"
    echo "  - Bot: ~/.claude/automation/lychee/logs/telegram-handler.log"
    echo ""
    tail -f "$HOME/.claude/automation/lychee/logs/telegram-bot-launchd.log" \
            "$HOME/.claude/automation/lychee/logs/telegram-bot-launchd-error.log" \
            "$HOME/.claude/automation/lychee/logs/telegram-handler.log" 2>/dev/null
}

show_help() {
    cat <<EOF
Telegram Bot Service Manager (launchd)

Production mode with full supervision and auto-reload.

Architecture:
    launchd (top supervisor)
      └─> watchexec (file watcher, auto-reload)
          └─> bot-wrapper (crash detection, alerts)
              └─> bot (actual process)

Features:
    ✅ Auto-start on login
    ✅ Auto-restart on crashes (10s throttle)
    ✅ Auto-reload on .py file changes (watchexec)
    ✅ Crash alerts via Telegram
    ✅ Full supervision chain

Usage: $0 <command>

Commands:
    install     Install and start the service
    uninstall   Stop and uninstall the service
    start       Start the service
    stop        Stop the service
    restart     Restart the service
    status      Show service status (full process tree)
    logs        Tail service logs
    help        Show this help message

Examples:
    # Install service (auto-starts on login, runs continuously)
    $0 install

    # Check if service is running (shows launchd + watchexec + bot)
    $0 status

    # View logs in real-time
    $0 logs

    # Restart after major changes (code changes auto-reload via watchexec)
    $0 restart

    # Uninstall service
    $0 uninstall

Note: Code changes (.py files) trigger automatic reload via watchexec.
      No need to restart manually for code updates!
EOF
}

# Main command router
case "${1:-}" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    logs)
        tail_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
