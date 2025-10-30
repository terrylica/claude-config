#!/usr/bin/env bash
# Bot Restart Notification System
# Sends notifications to both Telegram and Pushover when bot restarts
# Usage: notify-restart.sh <reason> [exit_code]

set -euo pipefail

# Log to dedicated notification log
NOTIFICATION_LOG="/Users/terryli/.claude/automation/lychee/logs/bot-notifications.log"
exec >> "$NOTIFICATION_LOG" 2>&1

# Arguments
REASON="${1:-unknown}"
EXIT_CODE="${2:-0}"

# Metadata
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

# Log notification start
echo "========================================================================"
echo "🔔 Bot Restart Notification - $TIMESTAMP"
echo "========================================================================"
HOSTNAME_SHORT="$(hostname -s 2>/dev/null || hostname 2>/dev/null || echo 'unknown')"
PID="$$"

# Determine restart type and emoji
if [[ "$REASON" == "startup" ]]; then
    EMOJI="🚀"
    STATUS="Started"
    PRIORITY="normal"
elif [[ "$REASON" == "code_change" ]]; then
    EMOJI="🔄"
    STATUS="Restarted (code change)"
    PRIORITY="normal"
elif [[ "$REASON" == "crash" ]]; then
    EMOJI="💥"
    STATUS="Restarted (crash)"
    PRIORITY="high"
else
    EMOJI="⚠️"
    STATUS="Restarted ($REASON)"
    PRIORITY="normal"
fi

# Build message
MESSAGE="$EMOJI **Telegram Bot $STATUS**

**Host**: \`$HOSTNAME_SHORT\`
**Time**: $TIMESTAMP
**PID**: $PID
**Exit Code**: $EXIT_CODE

_Monitoring active via watchexec_"

# Send to Telegram
if [[ -n "${TELEGRAM_BOT_TOKEN:-}" ]] && [[ -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    echo "📱 Sending Telegram notification..."

    # Use Python for reliable Telegram API call
    python3 - <<EOF
import os
import urllib.request
import urllib.parse
import json

bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

message = """$MESSAGE"""

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
data = {
    'chat_id': chat_id,
    'text': message,
    'parse_mode': 'Markdown'
}

try:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        if result.get('ok'):
            print('   ✅ Telegram notification sent')
        else:
            print(f'   ❌ Telegram API error: {result}')
except Exception as e:
    print(f'   ❌ Failed to send Telegram notification: {e}')
EOF
else
    echo "   ⏭️  Skipping Telegram (missing credentials)"
fi

# Send to Pushover
if command -v pushover-notify >/dev/null 2>&1; then
    echo "📲 Sending Pushover notification..."

    PUSHOVER_TITLE="Bot $STATUS"
    PUSHOVER_MESSAGE="Host: $HOSTNAME_SHORT
Time: $TIMESTAMP
Exit: $EXIT_CODE"

    if pushover-notify "$PUSHOVER_TITLE" "$PUSHOVER_MESSAGE" "iphone_13_mini" "cosmic" 2>/dev/null; then
        echo "   ✅ Pushover notification sent"
    else
        echo "   ⏭️  Pushover notification skipped (credentials not configured)"
    fi
else
    echo "   ⏭️  Skipping Pushover (pushover-notify not found)"
fi

echo "✅ Notification completed"
