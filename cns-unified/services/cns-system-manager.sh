#!/bin/bash
# CNS System Manager - Service supervisor for CNS Remote Alert System
# Monitors and maintains CNS hub + SSH tunnel persistence
# Part of the CNS unified service architecture

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CNS_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$CNS_ROOT/logs/cns-system.log"
ERROR_LOG="$CNS_ROOT/logs/cns-system.error.log"
PID_FILE="/tmp/cns-system-manager.pid"

# Service configuration
HUB_SCRIPT="$CNS_ROOT/bin/cns-local-hub.py"
HUB_PORT="5050"
HUB_HOST="127.0.0.1"
TUNNEL_HOST="yca"
TUNNEL_CHECK_INTERVAL=30
HUB_CHECK_INTERVAL=15
RESTART_DELAY=5
MAX_RESTART_ATTEMPTS=3
RESTART_WINDOW=300  # 5 minutes

# State tracking (simplified for compatibility)
CNS_HUB_RESTART_COUNT=0
SSH_TUNNEL_RESTART_COUNT=0
CNS_HUB_LAST_RESTART=0
SSH_TUNNEL_LAST_RESTART=0
SHUTDOWN_REQUESTED=false

# Logging functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $*" | tee -a "$LOG_FILE"
}

error_log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" | tee -a "$ERROR_LOG"
}

debug_log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [DEBUG] $*" >> "$LOG_FILE"
}

# Signal handling for graceful shutdown
cleanup() {
    log "CNS System Manager: Shutdown signal received"
    SHUTDOWN_REQUESTED=true
    
    # Stop CNS hub
    if pgrep -f "$HUB_SCRIPT" >/dev/null; then
        log "Stopping CNS hub processes"
        pkill -f "$HUB_SCRIPT" || true
        sleep 2
        pkill -9 -f "$HUB_SCRIPT" 2>/dev/null || true
    fi
    
    # Close SSH tunnel
    if ssh -O check "$TUNNEL_HOST" &>/dev/null; then
        log "Closing SSH tunnel to $TUNNEL_HOST"
        ssh -O exit "$TUNNEL_HOST" &>/dev/null || true
    fi
    
    rm -f "$PID_FILE"
    log "CNS System Manager: Shutdown complete"
    exit 0
}

trap cleanup SIGTERM SIGINT SIGQUIT

# Helper functions
is_port_listening() {
    local port="$1"
    lsof -i ":$port" >/dev/null 2>&1
}

is_ssh_tunnel_active() {
    ssh -O check "$TUNNEL_HOST" &>/dev/null
}

get_hub_pid() {
    pgrep -f "$HUB_SCRIPT" | head -1
}

should_restart_service() {
    local service="$1"
    local current_time=$(date +%s)
    local last_restart=0
    local restart_count=0
    
    # Get service-specific variables
    case "$service" in
        "cns_hub")
            last_restart=$CNS_HUB_LAST_RESTART
            restart_count=$CNS_HUB_RESTART_COUNT
            ;;
        "ssh_tunnel")
            last_restart=$SSH_TUNNEL_LAST_RESTART
            restart_count=$SSH_TUNNEL_RESTART_COUNT
            ;;
    esac
    
    # Reset count if outside restart window
    if (( current_time - last_restart > RESTART_WINDOW )); then
        case "$service" in
            "cns_hub")
                CNS_HUB_RESTART_COUNT=0
                restart_count=0
                ;;
            "ssh_tunnel")
                SSH_TUNNEL_RESTART_COUNT=0
                restart_count=0
                ;;
        esac
    fi
    
    if (( restart_count >= MAX_RESTART_ATTEMPTS )); then
        error_log "Service $service exceeded max restart attempts ($MAX_RESTART_ATTEMPTS) in window"
        return 1
    fi
    
    return 0
}

record_restart() {
    local service="$1"
    local current_time=$(date +%s)
    
    case "$service" in
        "cns_hub")
            CNS_HUB_LAST_RESTART=$current_time
            CNS_HUB_RESTART_COUNT=$((CNS_HUB_RESTART_COUNT + 1))
            ;;
        "ssh_tunnel")
            SSH_TUNNEL_LAST_RESTART=$current_time
            SSH_TUNNEL_RESTART_COUNT=$((SSH_TUNNEL_RESTART_COUNT + 1))
            ;;
    esac
}

# Service management functions
start_cns_hub() {
    if is_port_listening "$HUB_PORT"; then
        debug_log "CNS hub already running on port $HUB_PORT"
        return 0
    fi
    
    log "Starting CNS hub"
    cd "$CNS_ROOT/bin"
    python3 cns-local-hub.py &
    sleep 2
    
    if is_port_listening "$HUB_PORT"; then
        log "CNS hub started successfully (PID: $(get_hub_pid))"
        return 0
    else
        error_log "Failed to start CNS hub"
        return 1
    fi
}

restart_cns_hub() {
    if ! should_restart_service "cns_hub"; then
        return 1
    fi
    
    log "Restarting CNS hub"
    record_restart "cns_hub"
    
    # Stop existing processes
    pkill -f "$HUB_SCRIPT" 2>/dev/null || true
    sleep 2
    pkill -9 -f "$HUB_SCRIPT" 2>/dev/null || true
    
    sleep "$RESTART_DELAY"
    start_cns_hub
}

ensure_ssh_tunnel() {
    if is_ssh_tunnel_active; then
        debug_log "SSH tunnel to $TUNNEL_HOST is active"
        return 0
    fi
    
    if ! should_restart_service "ssh_tunnel"; then
        return 1
    fi
    
    log "Establishing SSH tunnel to $TUNNEL_HOST"
    record_restart "ssh_tunnel"
    
    # Clean up any stale connections
    ssh -O exit "$TUNNEL_HOST" &>/dev/null || true
    sleep 2
    
    # Establish new tunnel
    if ssh -f -N "$TUNNEL_HOST" &>/dev/null; then
        sleep 2
        if is_ssh_tunnel_active; then
            log "SSH tunnel established successfully"
            return 0
        fi
    fi
    
    error_log "Failed to establish SSH tunnel to $TUNNEL_HOST"
    return 1
}

# Health monitoring
check_cns_hub_health() {
    if ! is_port_listening "$HUB_PORT"; then
        error_log "CNS hub not listening on port $HUB_PORT"
        restart_cns_hub
        return $?
    fi
    
    # Test hub responsiveness
    if ! curl -s --connect-timeout 3 "http://$HUB_HOST:$HUB_PORT/health" >/dev/null 2>&1; then
        error_log "CNS hub not responding to health check"
        restart_cns_hub
        return $?
    fi
    
    return 0
}

check_ssh_tunnel_health() {
    if ! is_ssh_tunnel_active; then
        error_log "SSH tunnel to $TUNNEL_HOST is down"
        ensure_ssh_tunnel
        return $?
    fi
    
    return 0
}

# Main monitoring loop
monitor_services() {
    log "CNS System Manager started (PID: $$)"
    echo $$ > "$PID_FILE"
    
    # Initial startup
    log "Performing initial service startup"
    ensure_ssh_tunnel
    start_cns_hub
    
    # Monitoring loop
    local hub_check_counter=0
    local tunnel_check_counter=0
    
    while ! $SHUTDOWN_REQUESTED; do
        # Check CNS hub health
        if (( hub_check_counter >= HUB_CHECK_INTERVAL )); then
            check_cns_hub_health
            hub_check_counter=0
        fi
        
        # Check SSH tunnel health
        if (( tunnel_check_counter >= TUNNEL_CHECK_INTERVAL )); then
            check_ssh_tunnel_health
            tunnel_check_counter=0
        fi
        
        # Increment counters and sleep
        ((hub_check_counter++))
        ((tunnel_check_counter++))
        sleep 1
    done
}

# Status reporting
status_report() {
    echo "CNS System Manager Status"
    echo "========================="
    
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Manager: Running (PID: $(cat "$PID_FILE"))"
    else
        echo "Manager: Not running"
    fi
    
    if is_port_listening "$HUB_PORT"; then
        echo "CNS Hub: Running (PID: $(get_hub_pid), Port: $HUB_PORT)"
    else
        echo "CNS Hub: Not running"
    fi
    
    if is_ssh_tunnel_active; then
        echo "SSH Tunnel: Active ($TUNNEL_HOST)"
    else
        echo "SSH Tunnel: Inactive"
    fi
    
    echo ""
    echo "Recent logs:"
    tail -10 "$LOG_FILE" 2>/dev/null || echo "No logs available"
}

# Main execution
case "${1:-monitor}" in
    "monitor"|"start")
        # Check if already running
        if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "CNS System Manager already running (PID: $(cat "$PID_FILE"))"
            exit 1
        fi
        
        # Create log directory
        mkdir -p "$(dirname "$LOG_FILE")"
        
        # Start monitoring
        monitor_services
        ;;
    "stop")
        if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "Stopping CNS System Manager (PID: $(cat "$PID_FILE"))"
            kill -TERM "$(cat "$PID_FILE")"
            sleep 3
            if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
                kill -KILL "$(cat "$PID_FILE")"
            fi
            rm -f "$PID_FILE"
            echo "CNS System Manager stopped"
        else
            echo "CNS System Manager not running"
        fi
        ;;
    "status")
        status_report
        ;;
    "restart")
        $0 stop
        sleep 2
        $0 start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart|monitor}"
        echo ""
        echo "Commands:"
        echo "  start/monitor - Start the CNS system manager"
        echo "  stop          - Stop the CNS system manager"
        echo "  status        - Show system status"
        echo "  restart       - Restart the CNS system manager"
        exit 1
        ;;
esac