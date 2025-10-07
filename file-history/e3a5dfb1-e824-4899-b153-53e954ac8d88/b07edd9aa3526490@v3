#!/bin/bash
# CNS SSH Tunnel Listener - Receives notifications from remote SSH sessions
# Runs as background service on macOS to receive JSON payloads from remote CNS

set -euo pipefail

PORT="${1:-4000}"
LOG_FILE="$HOME/.claude/logs/cns-tunnel-listener.log"
PID_FILE="$HOME/.claude/logs/cns-tunnel-listener.pid"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Check if already running
if [[ -f "$PID_FILE" ]]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        log "❌ Listener already running (PID: $OLD_PID)"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

# Save PID
echo $$ > "$PID_FILE"

log "🚀 CNS Tunnel Listener starting on port $PORT"

# Process incoming notifications
process_notification() {
    local json_data="$1"

    log "📥 Received notification"

    # Extract message and environment
    local message=$(echo "$json_data" | jq -r '.message // .content.claude_response // "Remote notification"' 2>/dev/null)
    local title=$(echo "$json_data" | jq -r '.title // "CNS Remote"' 2>/dev/null)
    local hostname=$(echo "$json_data" | jq -r '.environment.hostname // "remote"' 2>/dev/null)
    local volume=$(echo "$json_data" | jq -r '.audio_config.volume // 0.3' 2>/dev/null)

    log "  Title: $title"
    log "  From: $hostname"
    log "  Message: ${message:0:50}..."

    # Play notification audio
    AUDIO_FILE="$HOME/.claude/media/toy-story-notification.mp3"
    if [[ -f "$AUDIO_FILE" ]] && command -v afplay >/dev/null 2>&1; then
        afplay "$AUDIO_FILE" --volume "$volume" &>/dev/null &
    fi

    # Voice announcement
    if command -v say >/dev/null 2>&1; then
        # Announce hostname and first few words
        local announce="Remote from $hostname"
        say "$announce" &>/dev/null &
    fi

    # Optional: Send to Pushover for persistence
    if command -v pushover-notify >/dev/null 2>&1; then
        pushover-notify "$title" "$message" "iphone_13_mini" "silent" &>/dev/null &
    fi

    log "✅ Notification processed"
}

# Cleanup handler
cleanup() {
    log "🛑 Stopping CNS Tunnel Listener"
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start netcat listener
log "👂 Listening on port $PORT (Press Ctrl+C to stop)"
while true; do
    # Use nc to receive JSON payloads
    JSON_DATA=$(nc -l "$PORT" 2>/dev/null || true)

    if [[ -n "$JSON_DATA" ]]; then
        # Process in background to handle next request quickly
        process_notification "$JSON_DATA" &
    fi

    # Small delay to prevent CPU spinning
    sleep 0.1
done
