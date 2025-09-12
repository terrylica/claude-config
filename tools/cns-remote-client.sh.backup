#!/bin/bash
# CNS Remote Client - Linux SSH Environment
# Sends notifications from remote Linux to local macOS via SSH tunnel
# Fire-and-forget execution for CNS hook integration

set -euo pipefail

# Configuration
SSH_TUNNEL_HOST="127.0.0.1"
SSH_TUNNEL_PORT="4000"
TIMEOUT="2"
LOG_FILE="/tmp/cns-remote-client.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" >> "$LOG_FILE"
}

# Environment detection
detect_environment() {
    local env_info="{\"hostname\":\"$(hostname)\""
    
    # Add current working directory
    env_info+=",\"cwd\":\"$(pwd)\""
    
    # Add tmux session if available
    if [[ -n "${TMUX_PANE:-}" ]]; then
        local tmux_session=$(tmux display-message -p '#S')
        env_info+=",\"tmux_session\":\"$tmux_session\""
    fi
    
    # Add SSH client info if available
    if [[ -n "${SSH_CLIENT:-}" ]]; then
        env_info+=",\"ssh_client\":\"$SSH_CLIENT\""
    fi
    
    env_info+="}"
    echo "$env_info"
}

# Send notification via SSH tunnel
send_via_tunnel() {
    local message="$1"
    local json_payload="$2"
    
    if command -v nc >/dev/null 2>&1; then
        # Use netcat for fast transmission
        echo "$json_payload" | nc -w "$TIMEOUT" "$SSH_TUNNEL_HOST" "$SSH_TUNNEL_PORT" 2>/dev/null
        return $?
    elif command -v curl >/dev/null 2>&1; then
        # Fallback to curl
        curl -s --connect-timeout "$TIMEOUT" \
             -X POST \
             -H "Content-Type: application/json" \
             -d "$json_payload" \
             "http://$SSH_TUNNEL_HOST:$SSH_TUNNEL_PORT/notify" >/dev/null 2>&1
        return $?
    else
        # No tools available
        return 1
    fi
}

# Send notification via external service fallback
send_via_fallback() {
    local message="$1"
    
    # Check if Pushover is configured
    if [[ -f ~/.pushover_config ]]; then
        source ~/.pushover_config
        if [[ -n "${PUSHOVER_TOKEN:-}" && -n "${PUSHOVER_USER:-}" ]]; then
            curl -s --connect-timeout "$TIMEOUT" \
                 -F "token=$PUSHOVER_TOKEN" \
                 -F "user=$PUSHOVER_USER" \
                 -F "message=$message" \
                 -F "title=CNS Remote Alert" \
                 https://api.pushover.net/1/messages.json >/dev/null 2>&1
            return $?
        fi
    fi
    
    # Check if ntfy is configured
    if [[ -f ~/.ntfy_config ]]; then
        source ~/.ntfy_config
        if [[ -n "${NTFY_TOPIC:-}" ]]; then
            curl -s --connect-timeout "$TIMEOUT" \
                 -H "Title: CNS Remote Alert" \
                 -d "$message" \
                 "https://ntfy.sh/$NTFY_TOPIC" >/dev/null 2>&1
            return $?
        fi
    fi
    
    return 1
}

# Main notification function
send_notification() {
    local message="${1:-Remote notification}"
    local title="${2:-CNS Remote Alert}"
    
    # Create JSON payload
    local env_data=$(detect_environment)
    local timestamp=$(date -Iseconds)
    
    local json_payload=$(cat << EOF
{
  "session_id": "$(hostname)-$$",
  "timestamp": "$timestamp",
  "environment": $env_data,
  "title": "$title",
  "message": "$message",
  "content": {
    "claude_response": "$message",
    "clipboard_enabled": false
  },
  "audio_config": {
    "volume": 0.7,
    "announcement_text": "Remote notification from $(hostname)"
  }
}
EOF
)
    
    log "Sending notification: $title - $message"
    
    # Try SSH tunnel first (primary method per agent consensus)
    if send_via_tunnel "$message" "$json_payload"; then
        log "✅ Notification sent via SSH tunnel"
        return 0
    fi
    
    log "⚠️  SSH tunnel failed, trying fallback services"
    
    # Try external service fallback
    if send_via_fallback "$message"; then
        log "✅ Notification sent via fallback service"
        return 0
    fi
    
    log "❌ All notification methods failed"
    return 1
}

# CNS hook integration - matches existing CNS pattern
cns_hook_entry() {
    local user_prompt="${1:-}"
    local claude_response="${2:-}"
    
    # Use Claude response as primary message, fallback to prompt
    local message="$claude_response"
    if [[ -z "$message" && -n "$user_prompt" ]]; then
        message="$user_prompt"
    elif [[ -z "$message" ]]; then
        message="Claude Code session activity"
    fi
    
    # Fire-and-forget execution in background to maintain <10ms hook time
    {
        send_notification "$message" "CNS Remote" 
    } &
    
    # Exit immediately for hook performance
    return 0
}

# Command line interface
main() {
    case "${1:-}" in
        "--hook")
            # CNS hook integration
            cns_hook_entry "${2:-}" "${3:-}"
            ;;
        "--test")
            # Test notification
            send_notification "Test notification from $(hostname)" "CNS Test"
            ;;
        "--setup-pushover")
            # Setup Pushover configuration
            echo "Setting up Pushover integration..."
            echo "Enter your Pushover User Key:"
            read -r user_key
            echo "Enter your Pushover Application Token:"
            read -r app_token
            
            cat > ~/.pushover_config << EOF
PUSHOVER_USER="$user_key"
PUSHOVER_TOKEN="$app_token"
EOF
            chmod 600 ~/.pushover_config
            echo "✅ Pushover configured. Test with: $0 --test"
            ;;
        "--setup-ntfy")
            # Setup ntfy configuration
            echo "Setting up ntfy integration..."
            echo "Enter your ntfy topic name:"
            read -r topic
            
            cat > ~/.ntfy_config << EOF
NTFY_TOPIC="$topic"
EOF
            chmod 600 ~/.ntfy_config
            echo "✅ ntfy configured. Test with: $0 --test"
            ;;
        "--help"|"-h"|"")
            cat << EOF
CNS Remote Client - Send notifications from Linux SSH to macOS

Usage: $0 [OPTION] [MESSAGE]

Options:
  --hook [prompt] [response]  CNS hook integration mode
  --test                      Send test notification  
  --setup-pushover           Configure Pushover fallback
  --setup-ntfy               Configure ntfy fallback
  --help, -h                 Show this help

Examples:
  $0 --test
  $0 --hook "user input" "Claude response"
  echo "Custom message" | $0

Direct message:
  $0 "Build completed successfully"

Environment:
  SSH Tunnel: $SSH_TUNNEL_HOST:$SSH_TUNNEL_PORT
  Log file: $LOG_FILE
EOF
            ;;
        *)
            # Direct message mode
            local message="$*"
            if [[ -z "$message" ]]; then
                # Read from stdin if no args
                message=$(cat)
            fi
            send_notification "$message"
            ;;
    esac
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi