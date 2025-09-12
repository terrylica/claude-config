#!/bin/bash
# CNS Remote Client - Send notifications from Linux SSH to macOS
# Fixed version that uses curl instead of netcat for HTTP compatibility

# Configuration
TIMEOUT="5"
SSH_TUNNEL_HOST="127.0.0.1"
SSH_TUNNEL_PORT="4000"
LOG_FILE="/tmp/cns-remote-client.log"

# Logging function
log() {
    echo "$(date "+%Y-%m-%d %H:%M:%S") - $1" >> "$LOG_FILE"
}

# Environment detection
detect_environment() {
    cat << EOF
{
    "hostname": "$(hostname)",
    "user": "$(whoami)",
    "cwd": "$(pwd)",
    "ssh_client": "${SSH_CLIENT:-}",
    "ssh_connection": "${SSH_CONNECTION:-}"
}
