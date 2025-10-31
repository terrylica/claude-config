#!/usr/bin/env bash
#
# Telegram Rate Limit Alert via Pushover
#
# Sends high-priority Pushover notification when Telegram API rate limit is hit.
# Called by bot when HTTP 429 (Too Many Requests) is encountered.
#
# Usage: notify-rate-limit.sh <workspace_id> <session_id> <retry_after_seconds> <error_message>
#
# Example:
#   notify-rate-limit.sh "81e622b5" "906b0590-fba9-4b39-ab69-cbf11f8f1b9c" "4900" "RetryAfter: 4900"

set -euo pipefail

# Parse arguments
WORKSPACE_ID="${1:-unknown}"
SESSION_ID="${2:-unknown}"
RETRY_AFTER="${3:-unknown}"
ERROR_MESSAGE="${4:-Rate limit exceeded}"

# Timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
HOSTNAME_SHORT=$(hostname -s)

# Calculate retry time if numeric
if [[ "$RETRY_AFTER" =~ ^[0-9]+$ ]]; then
    RETRY_MINUTES=$(( RETRY_AFTER / 60 ))
    RETRY_TIME=$(date -v+${RETRY_AFTER}S "+%H:%M:%S" 2>/dev/null || date -d "+${RETRY_AFTER} seconds" "+%H:%M:%S" 2>/dev/null || echo "unknown")
    RETRY_DISPLAY="~${RETRY_MINUTES}min (until $RETRY_TIME)"
else
    RETRY_DISPLAY="$RETRY_AFTER"
fi

# Build Pushover message (plain text, no markdown)
PUSHOVER_TITLE="⚠️ Telegram Rate Limit"

PUSHOVER_MESSAGE="Host: $HOSTNAME_SHORT
Time: $TIMESTAMP
Workspace: ${WORKSPACE_ID:0:8}
Session: ${SESSION_ID:0:8}

Retry After: $RETRY_DISPLAY

Error: ${ERROR_MESSAGE:0:300}

The bot has exceeded Telegram's API rate limits and is temporarily blocked from sending messages. Pushover notifications will continue to work normally."

# Send to Pushover with HIGH priority (bypasses quiet hours)
if command -v pushover-notify >/dev/null 2>&1; then
    echo "📲 Sending Pushover rate limit alert..."

    curl -s \
        --form-string "token=$(security find-generic-password -s 'pushover-app-token' -a 'terryli' -w 2>/dev/null || jq -r '.pushover.app_token // ""' ~/.claude/automation/cns/config/cns_config.json 2>/dev/null)" \
        --form-string "user=$(security find-generic-password -s 'pushover-user-key' -a 'terryli' -w 2>/dev/null || jq -r '.pushover.user_key // ""' ~/.claude/automation/cns/config/cns_config.json 2>/dev/null)" \
        --form-string "device=iphone_13_mini" \
        --form-string "title=$PUSHOVER_TITLE" \
        --form-string "message=$PUSHOVER_MESSAGE" \
        --form-string "sound=siren" \
        --form-string "priority=1" \
        https://api.pushover.net/1/messages.json >/dev/null 2>&1

    if [[ $? -eq 0 ]]; then
        echo "   ✅ Pushover alert sent (priority: high, sound: siren)"
        exit 0
    else
        echo "   ⚠️  Pushover alert failed (check credentials)" >&2
        exit 1
    fi
else
    echo "   ⏭️  Pushover not available (pushover-notify not found)" >&2
    exit 1
fi
