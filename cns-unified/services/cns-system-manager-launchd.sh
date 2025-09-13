#!/bin/bash
# CNS System Manager (LaunchAgent Compatible) - Service supervisor for CNS Remote Alert System
# Simplified version that works with macOS LaunchAgent process management
# Part of the CNS unified service architecture

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CNS_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$CNS_ROOT/logs/cns-system.log"
ERROR_LOG="$CNS_ROOT/logs/cns-system.error.log"

# Service configuration
HUB_SCRIPT="$CNS_ROOT/bin/cns-local-hub.py"
TUNNEL_HOST="yca"

# Logging functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $*" | tee -a "$LOG_FILE"
}

error_log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" | tee -a "$ERROR_LOG"
}

# Signal handling for graceful shutdown
cleanup() {
    log "CNS LaunchAgent Manager: Shutdown signal received"
    
    # Close SSH tunnel
    if ssh -O check "$TUNNEL_HOST" &>/dev/null; then
        log "Closing SSH tunnel to $TUNNEL_HOST"
        ssh -O exit "$TUNNEL_HOST" &>/dev/null || true
    fi
    
    log "CNS LaunchAgent Manager: Shutdown complete"
    exit 0
}

trap cleanup SIGTERM SIGINT SIGQUIT

# Helper functions
is_ssh_tunnel_active() {
    ssh -O check "$TUNNEL_HOST" &>/dev/null
}

ensure_ssh_tunnel() {
    if is_ssh_tunnel_active; then
        log "SSH tunnel to $TUNNEL_HOST is active"
        return 0
    fi
    
    log "Establishing SSH tunnel to $TUNNEL_HOST"
    
    # Clean up any stale connections
    ssh -O exit "$TUNNEL_HOST" &>/dev/null || true
    sleep 2
    
    # Establish new tunnel (non-background for LaunchAgent)
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

# LaunchAgent-compatible main function
main() {
    log "CNS LaunchAgent Manager started (PID: $$)"
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Ensure SSH tunnel is active
    ensure_ssh_tunnel
    
    # Change to the bin directory
    cd "$CNS_ROOT/bin"
    
    # Start CNS hub as the main process (LaunchAgent manages this)
    log "Starting CNS hub as main process"
    exec python3 cns-local-hub.py
}

# Status check function for external use
status_check() {
    echo "CNS LaunchAgent Manager Status"
    echo "=============================="
    
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
case "${1:-main}" in
    "main"|"monitor"|"start")
        main
        ;;
    "status")
        status_check
        ;;
    *)
        echo "Usage: $0 {main|monitor|start|status}"
        exit 1
        ;;
esac