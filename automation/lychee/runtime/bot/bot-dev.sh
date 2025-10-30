#!/usr/bin/env bash
#
# Telegram Bot Development Mode Manager
#
# Manages the watchexec-based auto-reload development server with proper
# singleton enforcement and lifecycle management.
#
# Usage:
#   ./bot-dev.sh start   - Start development server (refuses if already running)
#   ./bot-dev.sh stop    - Stop development server (clean shutdown)
#   ./bot-dev.sh restart - Restart development server
#   ./bot-dev.sh status  - Show development server status
#
# Features:
#   • Singleton enforcement (prevents multiple watchexec instances)
#   • PID file management for watchexec process
#   • Clean start/stop/restart operations
#   • Status checks with health validation
#   • Process tree visibility

set -euo pipefail

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$HOME/.claude/automation/lychee/state"
WATCHEXEC_PID_FILE="$STATE_DIR/watchexec.pid"
BOT_PID_FILE="$STATE_DIR/bot.pid"
STARTUP_SCRIPT="$BOT_DIR/run-bot-dev-watchexec.sh"
LOG_FILE="$HOME/.claude/automation/lychee/logs/telegram-handler.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure state directory exists
mkdir -p "$STATE_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

#
# Helper Functions
#

is_process_running() {
    local pid=$1
    if ps -p "$pid" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

get_process_tree() {
    local pid=$1
    # Show process tree starting from watchexec
    ps -o pid,ppid,stat,etime,rss,command | head -1
    ps -o pid,ppid,stat,etime,rss,command | grep -E "(^[[:space:]]*$pid |watchexec|multi-workspace-bot|doppler.*bot|uv.*bot)" | grep -v grep || true
}

cleanup_stale_pid_file() {
    local pid_file=$1
    local process_name=$2

    if [[ ! -f "$pid_file" ]]; then
        return 0
    fi

    local stored_pid
    stored_pid=$(cat "$pid_file" 2>/dev/null || echo "")

    if [[ -z "$stored_pid" ]]; then
        echo -e "${YELLOW}⚠️  Empty PID file found, removing${NC}"
        rm -f "$pid_file"
        return 0
    fi

    if ! is_process_running "$stored_pid"; then
        echo -e "${YELLOW}⚠️  Stale $process_name PID file found (PID $stored_pid not running)${NC}"
        rm -f "$pid_file"
        return 0
    fi

    # Check if it's actually our process
    local cmdline
    cmdline=$(ps -p "$stored_pid" -o command= 2>/dev/null || echo "")
    if [[ ! "$cmdline" =~ $process_name ]]; then
        echo -e "${YELLOW}⚠️  PID $stored_pid is not $process_name: $cmdline${NC}"
        rm -f "$pid_file"
        return 0
    fi

    return 1  # Process is running
}

#
# Command Implementations
#

start_dev_server() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}🤖 Starting Telegram Bot (Development)${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # Check for stale watchexec PID file
    if ! cleanup_stale_pid_file "$WATCHEXEC_PID_FILE" "watchexec"; then
        local stored_pid
        stored_pid=$(cat "$WATCHEXEC_PID_FILE")
        echo -e "${RED}❌ Development server already running!${NC}"
        echo ""
        echo "Watchexec PID: $stored_pid"
        echo ""
        echo "Process tree:"
        get_process_tree "$stored_pid"
        echo ""
        echo -e "${YELLOW}To stop: ./bot-dev.sh stop${NC}"
        echo -e "${YELLOW}To restart: ./bot-dev.sh restart${NC}"
        exit 1
    fi

    # Start watchexec in background and capture its PID
    echo -e "${GREEN}▶️  Starting watchexec with auto-reload...${NC}"
    nohup "$STARTUP_SCRIPT" >> "$LOG_FILE" 2>&1 &
    local watchexec_pid=$!

    # Save watchexec PID
    echo "$watchexec_pid" > "$WATCHEXEC_PID_FILE"

    # Wait a moment for startup
    sleep 2

    # Verify it started
    if ! is_process_running "$watchexec_pid"; then
        echo -e "${RED}❌ Failed to start watchexec${NC}"
        rm -f "$WATCHEXEC_PID_FILE"
        echo ""
        echo "Check logs: tail -f $LOG_FILE"
        exit 1
    fi

    # Wait for bot to start (bot creates its own PID file)
    echo -e "${GREEN}⏳ Waiting for bot to initialize...${NC}"
    local max_wait=10
    local waited=0
    while [[ $waited -lt $max_wait ]]; do
        if [[ -f "$BOT_PID_FILE" ]]; then
            local bot_pid
            bot_pid=$(cat "$BOT_PID_FILE" 2>/dev/null || echo "")
            if [[ -n "$bot_pid" ]] && is_process_running "$bot_pid"; then
                echo ""
                echo -e "${GREEN}✅ Development server started successfully!${NC}"
                echo ""
                echo "Watchexec PID: $watchexec_pid"
                echo "Bot PID: $bot_pid"
                echo ""
                echo "Features:"
                echo "  ✓ Auto-reload on .py file changes"
                echo "  ✓ Watches: bot/, lib/, orchestrator/"
                echo "  ✓ Debouncing: 100ms"
                echo ""
                echo "Commands:"
                echo "  Status:  ./bot-dev.sh status"
                echo "  Stop:    ./bot-dev.sh stop"
                echo "  Restart: ./bot-dev.sh restart"
                echo "  Logs:    tail -f $LOG_FILE"
                echo ""
                return 0
            fi
        fi
        sleep 1
        ((waited++))
    done

    echo -e "${YELLOW}⚠️  Bot initialization taking longer than expected${NC}"
    echo ""
    echo "Watchexec is running, but bot hasn't started yet."
    echo "Check logs: tail -f $LOG_FILE"
}

stop_dev_server() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}⏹️  Stopping Telegram Bot (Development)${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    if [[ ! -f "$WATCHEXEC_PID_FILE" ]]; then
        echo -e "${YELLOW}⚠️  Development server is not running (no PID file)${NC}"

        # Check for orphaned processes
        local orphaned_watchexec
        orphaned_watchexec=$(pgrep -f "watchexec.*multi-workspace-bot" || echo "")
        if [[ -n "$orphaned_watchexec" ]]; then
            echo ""
            echo -e "${YELLOW}Found orphaned watchexec processes:${NC}"
            ps -p "$orphaned_watchexec" -o pid,etime,command
            echo ""
            read -p "Kill these processes? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kill "$orphaned_watchexec" 2>/dev/null || true
                echo -e "${GREEN}✓ Killed orphaned processes${NC}"
            fi
        fi
        exit 0
    fi

    local watchexec_pid
    watchexec_pid=$(cat "$WATCHEXEC_PID_FILE")

    if ! is_process_running "$watchexec_pid"; then
        echo -e "${YELLOW}⚠️  Watchexec process (PID $watchexec_pid) is not running${NC}"
        rm -f "$WATCHEXEC_PID_FILE"
        exit 0
    fi

    echo -e "${GREEN}🛑 Sending SIGTERM to watchexec (PID $watchexec_pid)${NC}"

    # Get all child processes before killing
    local child_pids
    child_pids=$(pgrep -P "$watchexec_pid" || echo "")

    # Send SIGTERM to watchexec (it will cascade to children)
    kill -TERM "$watchexec_pid" 2>/dev/null || true

    # Wait for graceful shutdown (max 10 seconds)
    local max_wait=10
    local waited=0
    while [[ $waited -lt $max_wait ]]; do
        if ! is_process_running "$watchexec_pid"; then
            echo -e "${GREEN}✓ Watchexec stopped gracefully${NC}"
            rm -f "$WATCHEXEC_PID_FILE"

            # Verify bot also stopped
            if [[ -f "$BOT_PID_FILE" ]]; then
                local bot_pid
                bot_pid=$(cat "$BOT_PID_FILE" 2>/dev/null || echo "")
                if [[ -n "$bot_pid" ]] && is_process_running "$bot_pid"; then
                    echo -e "${YELLOW}⚠️  Bot process still running, sending SIGTERM${NC}"
                    kill -TERM "$bot_pid" 2>/dev/null || true
                    sleep 2
                fi
            fi

            echo ""
            echo -e "${GREEN}✅ Development server stopped successfully${NC}"
            return 0
        fi
        sleep 1
        ((waited++))
    done

    # Force kill if graceful shutdown failed
    echo -e "${YELLOW}⚠️  Graceful shutdown timed out, forcing kill${NC}"
    kill -9 "$watchexec_pid" 2>/dev/null || true

    # Kill any remaining child processes
    if [[ -n "$child_pids" ]]; then
        echo "$child_pids" | xargs kill -9 2>/dev/null || true
    fi

    rm -f "$WATCHEXEC_PID_FILE"
    echo -e "${GREEN}✓ Development server force-stopped${NC}"
}

restart_dev_server() {
    echo -e "${BLUE}🔄 Restarting development server...${NC}"
    echo ""

    stop_dev_server
    echo ""
    sleep 1
    start_dev_server
}

status_dev_server() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}📊 Development Server Status${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # Check watchexec
    if [[ ! -f "$WATCHEXEC_PID_FILE" ]]; then
        echo -e "${YELLOW}⚠️  Development server is NOT RUNNING${NC}"
        echo ""
        echo "PID file not found: $WATCHEXEC_PID_FILE"
        echo ""
        echo -e "${GREEN}Start with: ./bot-dev.sh start${NC}"
        exit 1
    fi

    local watchexec_pid
    watchexec_pid=$(cat "$WATCHEXEC_PID_FILE")

    if ! is_process_running "$watchexec_pid"; then
        echo -e "${RED}❌ Watchexec process is DEAD (PID $watchexec_pid)${NC}"
        echo ""
        echo "Stale PID file found. Run './bot-dev.sh stop' to clean up."
        exit 1
    fi

    echo -e "${GREEN}✅ Development server is RUNNING${NC}"
    echo ""

    # Show watchexec info
    echo -e "${BLUE}Watchexec Process:${NC}"
    echo "  PID: $watchexec_pid"
    ps -p "$watchexec_pid" -o etime,rss,command | tail -1 | awk '{printf "  Uptime: %s\n  Memory: %s KB\n  Command: %s\n", $1, $2, substr($0, index($0,$3))}'
    echo ""

    # Check bot
    if [[ ! -f "$BOT_PID_FILE" ]]; then
        echo -e "${YELLOW}⚠️  Bot PID file not found (still starting?)${NC}"
        echo ""
    else
        local bot_pid
        bot_pid=$(cat "$BOT_PID_FILE" 2>/dev/null || echo "")

        if [[ -z "$bot_pid" ]]; then
            echo -e "${YELLOW}⚠️  Bot PID file is empty${NC}"
            echo ""
        elif ! is_process_running "$bot_pid"; then
            echo -e "${RED}❌ Bot process is DEAD (PID $bot_pid)${NC}"
            echo "  Watchexec should restart it shortly..."
            echo ""
        else
            echo -e "${BLUE}Bot Process:${NC}"
            echo "  PID: $bot_pid"
            ps -p "$bot_pid" -o etime,rss,command | tail -1 | awk '{printf "  Uptime: %s\n  Memory: %s KB\n  Command: %s\n", $1, $2, substr($0, index($0,$3))}'
            echo ""
        fi
    fi

    # Show full process tree
    echo -e "${BLUE}Process Tree:${NC}"
    get_process_tree "$watchexec_pid"
    echo ""

    # Show recent log activity
    if [[ -f "$LOG_FILE" ]]; then
        echo -e "${BLUE}Recent Logs (last 5 lines):${NC}"
        tail -5 "$LOG_FILE" | sed 's/^/  /'
        echo ""
        echo -e "${YELLOW}Full logs: tail -f $LOG_FILE${NC}"
    fi
}

show_help() {
    cat <<EOF
${BLUE}Telegram Bot Development Mode Manager${NC}

Manages the watchexec-based auto-reload development server with proper
singleton enforcement and lifecycle management.

${GREEN}Usage:${NC} $0 <command>

${GREEN}Commands:${NC}
    ${YELLOW}start${NC}     Start development server (refuses if already running)
    ${YELLOW}stop${NC}      Stop development server (clean shutdown)
    ${YELLOW}restart${NC}   Restart development server
    ${YELLOW}status${NC}    Show development server status and process tree
    ${YELLOW}help${NC}      Show this help message

${GREEN}Features:${NC}
    ✓ Singleton enforcement (prevents multiple watchexec instances)
    ✓ PID file management for watchexec and bot processes
    ✓ Clean start/stop/restart operations
    ✓ Auto-reload on Python file changes (100ms debounce)
    ✓ Process tree visibility and health checks

${GREEN}Examples:${NC}
    # Start development server
    $0 start

    # Check if server is running
    $0 status

    # Restart after major changes
    $0 restart

    # Stop development server
    $0 stop

${GREEN}Logs:${NC}
    tail -f $LOG_FILE

${GREEN}Production Mode:${NC}
    For production deployment with launchd:
    ./bot-service.sh install
EOF
}

# Main command router
case "${1:-}" in
    start)
        start_dev_server
        ;;
    stop)
        stop_dev_server
        ;;
    restart)
        restart_dev_server
        ;;
    status)
        status_dev_server
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: ${1:-}${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
