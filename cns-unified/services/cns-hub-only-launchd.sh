#!/bin/bash
# CNS Hub Only (LaunchAgent Compatible) - Pure CNS hub for LaunchAgent
# Assumes SSH tunnel is already established and managed separately
# Part of the CNS unified service architecture

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CNS_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$CNS_ROOT/logs/cns-hub-launchd.log"

# Logging functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $*" | tee -a "$LOG_FILE"
}

# Signal handling for graceful shutdown
cleanup() {
    log "CNS Hub LaunchAgent: Shutdown signal received"
    log "CNS Hub LaunchAgent: Shutdown complete"
    exit 0
}

trap cleanup SIGTERM SIGINT SIGQUIT

# LaunchAgent-compatible main function
main() {
    log "CNS Hub LaunchAgent started (PID: $$)"
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Change to the bin directory
    cd "$CNS_ROOT/bin"
    
    # Start CNS hub as the main process (LaunchAgent manages this)
    log "Starting CNS hub as main process"
    exec python3 cns-local-hub.py
}

# Main execution
main