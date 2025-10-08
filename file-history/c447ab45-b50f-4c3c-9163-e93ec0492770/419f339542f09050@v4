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
    
    if command -v nc-disabled >/dev/null 2>&1; then
        # Use netcat for fast transmission
        echo "$json_payload" | nc -w "$TIMEOUT" "$SSH_TUNNEL_HOST" "$SSH_TUNNEL_PORT" 2>/dev/null
        return $?
    elif command -v curl >/dev/null 2>&1; then
        # Fallback to curl
        curl -s --connect-timeout "$TIMEOUT" \
             -X POST \
             -H "Content-Type: application/json" \
             -d "$json_payload" \
             "http://$SSH_TUNNEL_HOST:$SSH_TUNNEL_PORT/" >/dev/null 2>&1
        return $?
    else
        # No tools available
        return 1
    fi
}

# Send notification via external service fallback
send_via_fallback() {
    local message="$1"

    # Gather context information (portable across Linux/macOS)
    local username="${USER:-$(whoami 2>/dev/null || echo 'unknown')}"
    local current_dir="$(pwd 2>/dev/null || echo '/unknown')"
    local folder_name="$(basename "$current_dir" 2>/dev/null || echo 'unknown')"
    local hostname_short="$(hostname -s 2>/dev/null || hostname 2>/dev/null || echo 'unknown')"

    # Create rich notification title with context
    local notification_title="CNS: ${username}@${hostname_short}"

    # Create rich message with folder context
    local notification_message="📁 ${folder_name}
${message}"

    # Load Pushover credentials (priority order):
    # 1. CNS config (shared in git) - preferred
    # 2. ~/.pushover_config (local override)
    # 3. macOS Keychain (fallback)

    local PUSHOVER_USER=""
    local PUSHOVER_TOKEN=""
    local PUSHOVER_SOUND="toy_story"  # Default sound

    # Try CNS config first (works everywhere after git pull)
    CNS_CONFIG="$HOME/.claude/automation/cns/config/cns_config.json"
    if [[ -f "$CNS_CONFIG" ]]; then
        PUSHOVER_USER=$(jq -r '.pushover.user_key // empty' "$CNS_CONFIG" 2>/dev/null)
        PUSHOVER_TOKEN=$(jq -r '.pushover.app_token // empty' "$CNS_CONFIG" 2>/dev/null)
        PUSHOVER_SOUND=$(jq -r '.pushover.default_sound // "toy_story"' "$CNS_CONFIG" 2>/dev/null)
    fi

    # Fallback to local config if CNS config didn't have credentials
    if [[ -z "$PUSHOVER_USER" || -z "$PUSHOVER_TOKEN" ]] && [[ -f ~/.pushover_config ]]; then
        source ~/.pushover_config
    fi

    # Send via Pushover if we have credentials
    if [[ -n "${PUSHOVER_TOKEN:-}" && -n "${PUSHOVER_USER:-}" ]]; then
        curl -s --connect-timeout "$TIMEOUT" \
             -F "token=$PUSHOVER_TOKEN" \
             -F "user=$PUSHOVER_USER" \
             -F "message=$notification_message" \
             -F "title=$notification_title" \
             -F "sound=$PUSHOVER_SOUND" \
             https://api.pushover.net/1/messages.json >/dev/null 2>&1
        return $?
    fi

    # Check if ntfy is configured
    if [[ -f ~/.ntfy_config ]]; then
        source ~/.ntfy_config
        if [[ -n "${NTFY_TOPIC:-}" ]]; then
            curl -s --connect-timeout "$TIMEOUT" \
                 -H "Title: $notification_title" \
                 -d "$notification_message" \
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

    # Dual notification architecture: SSH tunnel + Pushover
    local tunnel_success=false
    local pushover_success=false

    # Send via SSH tunnel (for local macOS audio)
    if send_via_tunnel "$message" "$json_payload"; then
        log "✅ Notification sent via SSH tunnel"
        tunnel_success=true
    else
        log "⚠️  SSH tunnel failed"
    fi

    # Send via Pushover (always, for mobile notifications)
    if send_via_fallback "$message"; then
        log "✅ Notification sent via Pushover"
        pushover_success=true
    else
        log "⚠️  Pushover failed"
    fi

    # Success if either method worked
    if [[ "$tunnel_success" == "true" || "$pushover_success" == "true" ]]; then
        return 0
    fi

    log "❌ All notification methods failed"
    return 1
}

# CNS hook integration - matches existing CNS pattern
cns_hook_entry() {
    local user_prompt="${1:-}"
    local claude_response="${2:-}"
    local hook_json="${3:-}"

    # Extract Claude Code metadata if available (from stdin or environment)
    local session_id="${CNS_SESSION_ID:-unknown}"
    local hook_event="${CNS_HOOK_EVENT:-unknown}"
    local session_short=""

    # If we have hook JSON data, parse it
    if [[ -n "$hook_json" ]]; then
        session_id=$(echo "$hook_json" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")
        hook_event=$(echo "$hook_json" | jq -r '.hook_event_name // "unknown"' 2>/dev/null || echo "unknown")
    fi

    # Create short session ID (first 8 chars)
    if [[ "$session_id" != "unknown" ]]; then
        session_short=$(echo "$session_id" | cut -d'-' -f1)
    fi

    # Use Claude response as primary message, fallback to prompt
    local message="$claude_response"
    if [[ -z "$message" && -n "$user_prompt" ]]; then
        message="$user_prompt"
    elif [[ -z "$message" ]]; then
        # Generate consistent folder announcement matching local macOS behavior
        local working_dir=$(pwd 2>/dev/null || echo "unknown")
        local folder_name=$(basename "$working_dir" 2>/dev/null || echo "directory")

        # Format directory name for proper TTS pronunciation (match local behavior)
        if [[ "$folder_name" == .* ]]; then
            message="dot ${folder_name:1}"
        else
            message="$folder_name"
        fi
    fi

    # Add session metadata to message if available
    if [[ -n "$session_short" ]]; then
        message="${message}

🆔 ${session_short} | ${hook_event}"
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