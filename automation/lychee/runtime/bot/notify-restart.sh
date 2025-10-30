#!/usr/bin/env bash
# Bot Restart Notification System
# Sends notifications to both Telegram and Pushover when bot restarts
# Usage: notify-restart.sh <reason> [exit_code] [watchexec_info_file] [crash_context_file]

set -euo pipefail

# Log to dedicated notification log
NOTIFICATION_LOG="/Users/terryli/.claude/automation/lychee/logs/bot-notifications.log"
exec >> "$NOTIFICATION_LOG" 2>&1

# Arguments
REASON="${1:-unknown}"
EXIT_CODE="${2:-0}"
WATCHEXEC_INFO_FILE="${3:-}"
CRASH_CONTEXT_FILE="${4:-}"

# Metadata
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

# Log notification start
echo "========================================================================"
echo "🔔 Bot Restart Notification - $TIMESTAMP"
echo "========================================================================"
HOSTNAME_SHORT="$(hostname -s 2>/dev/null || hostname 2>/dev/null || echo 'unknown')"
PID="$$"

# Get Claude Code session ID (from environment or recent session)
CLAUDE_SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"
if [[ -z "$CLAUDE_SESSION_ID" ]]; then
    # Try to get most recent session from Claude Code debug dir
    LATEST_SESSION_FILE=$(ls -t ~/.claude/debug/*.txt 2>/dev/null | head -1)
    if [[ -n "$LATEST_SESSION_FILE" ]]; then
        CLAUDE_SESSION_ID=$(basename "$LATEST_SESSION_FILE" .txt)
    else
        CLAUDE_SESSION_ID="unknown"
    fi
fi

# Get git branch and working directory
BOT_DIR="/Users/terryli/.claude/automation/lychee/runtime/bot"
cd "$BOT_DIR" 2>/dev/null || true
GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
WORKING_DIR=$(pwd | sed "s|^$HOME|~|")  # Replace home with tilde

# Parse watchexec diagnostic info if available
WATCHEXEC_DETAILS=""
CHANGED_FILES=""
if [[ -f "$WATCHEXEC_INFO_FILE" ]]; then
    echo "📊 Watchexec diagnostic info available"

    # Extract file change information
    if command -v jq >/dev/null 2>&1; then
        COMMON_PATH=$(jq -r '.watchexec.common_path // ""' "$WATCHEXEC_INFO_FILE" 2>/dev/null || echo "")
        WRITTEN_PATH=$(jq -r '.watchexec.written_path // ""' "$WATCHEXEC_INFO_FILE" 2>/dev/null || echo "")
        CREATED_PATH=$(jq -r '.watchexec.created_path // ""' "$WATCHEXEC_INFO_FILE" 2>/dev/null || echo "")
        REMOVED_PATH=$(jq -r '.watchexec.removed_path // ""' "$WATCHEXEC_INFO_FILE" 2>/dev/null || echo "")

        # Build file change summary (Markdown format)
        if [[ -n "$WRITTEN_PATH" ]]; then
            FILENAME=$(basename "$WRITTEN_PATH")
            CHANGED_FILES="Modified: \`$FILENAME\`"
            TRIGGER_PATH="$WRITTEN_PATH"
        elif [[ -n "$CREATED_PATH" ]]; then
            FILENAME=$(basename "$CREATED_PATH")
            CHANGED_FILES="Created: \`$FILENAME\`"
            TRIGGER_PATH="$CREATED_PATH"
        elif [[ -n "$REMOVED_PATH" ]]; then
            FILENAME=$(basename "$REMOVED_PATH")
            CHANGED_FILES="Deleted: \`$FILENAME\`"
            TRIGGER_PATH="$REMOVED_PATH"
        elif [[ -n "$COMMON_PATH" ]]; then
            FILENAME=$(basename "$COMMON_PATH")
            CHANGED_FILES="Changed: \`$FILENAME\`"
            TRIGGER_PATH="$COMMON_PATH"
        else
            # No file detected - show generic watchexec restart
            CHANGED_FILES="Watchexec detected change (file not identified)"
            TRIGGER_PATH="(file detection failed - check within 30s window)"
        fi

        WATCHEXEC_DETAILS="
**Trigger**: \`$TRIGGER_PATH\`
**Action**: $CHANGED_FILES"
    else
        WATCHEXEC_DETAILS="
_Watchexec info available (jq not installed)_"
    fi
fi

# Extract crash context if available
CRASH_INFO=""
if [[ -f "$CRASH_CONTEXT_FILE" ]]; then
    echo "💥 Crash context available"

    # Read last error lines
    CRASH_PREVIEW=$(tail -5 "$CRASH_CONTEXT_FILE" 2>/dev/null || echo "(no context)")

    CRASH_INFO="

**Last Log Lines**:
\`\`\`
$CRASH_PREVIEW
\`\`\`"
fi

# Determine restart type and emoji
if [[ "$REASON" == "startup" ]]; then
    EMOJI="🚀"
    STATUS="Started"
    PRIORITY="normal"
    PUSHOVER_SOUND="cosmic"
elif [[ "$REASON" == "code_change" ]]; then
    EMOJI="🔄"
    STATUS="Restarted"
    PRIORITY="normal"
    PUSHOVER_SOUND="bike"
elif [[ "$REASON" == "crash" ]]; then
    EMOJI="💥"
    STATUS="Crashed"
    PRIORITY="high"
    PUSHOVER_SOUND="siren"
else
    EMOJI="⚠️"
    STATUS="Restarted"
    PRIORITY="normal"
    PUSHOVER_SOUND="cosmic"
fi

# Build session debug line (matches format from message_builders.py)
SESSION_DEBUG_LINE="session=$CLAUDE_SESSION_ID | 🐛 debug=~/.claude/debug/\${session}.txt"

# Build message (Markdown format, simplified like other Telegram messages)
if [[ "$REASON" == "crash" ]]; then
    # For crashes, show exit code and crash details
    MESSAGE="$EMOJI **Bot $STATUS**

**Directory**: \`$WORKING_DIR\`
**Branch**: \`$GIT_BRANCH\`
\`$SESSION_DEBUG_LINE\`

**Exit Code**: $EXIT_CODE$WATCHEXEC_DETAILS$CRASH_INFO"
else
    # For normal restarts, simplified format (no exit code, no host, no monitoring)
    if [[ -n "$WATCHEXEC_DETAILS" ]]; then
        # Code change restart - show trigger and action
        MESSAGE="$EMOJI **Bot $STATUS**

**Directory**: \`$WORKING_DIR\`
**Branch**: \`$GIT_BRANCH\`
\`$SESSION_DEBUG_LINE\`
$WATCHEXEC_DETAILS"
    else
        # Startup or other reason
        MESSAGE="$EMOJI **Bot $STATUS**

**Directory**: \`$WORKING_DIR\`
**Branch**: \`$GIT_BRANCH\`
\`$SESSION_DEBUG_LINE\`"
    fi
fi

# Save message to persistent file for debugging
MESSAGE_ARCHIVE_DIR="/Users/terryli/.claude/automation/lychee/logs/notification-archive"
mkdir -p "$MESSAGE_ARCHIVE_DIR"
MESSAGE_ARCHIVE_FILE="$MESSAGE_ARCHIVE_DIR/$(date '+%Y%m%d-%H%M%S')-$REASON-$PID.txt"

cat > "$MESSAGE_ARCHIVE_FILE" <<ARCHIVE_EOF
========================================================================
Notification Archive
========================================================================
Timestamp: $TIMESTAMP
Reason: $REASON
Exit Code: $EXIT_CODE
Host: $HOSTNAME_SHORT
PID: $PID

--- TELEGRAM MESSAGE ---
$MESSAGE

--- VARIABLES ---
WATCHEXEC_DETAILS: ${WATCHEXEC_DETAILS:-<empty>}
CRASH_INFO: ${CRASH_INFO:-<empty>}
CHANGED_FILES: ${CHANGED_FILES:-<empty>}

--- WATCHEXEC INFO FILE ---
$(cat "$WATCHEXEC_INFO_FILE" 2>/dev/null || echo "Not available")

--- CRASH CONTEXT FILE ---
$(cat "$CRASH_CONTEXT_FILE" 2>/dev/null || echo "Not available")
========================================================================
ARCHIVE_EOF

echo "📝 Message archived: $MESSAGE_ARCHIVE_FILE"

# Send to Telegram
if [[ -n "${TELEGRAM_BOT_TOKEN:-}" ]] && [[ -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    echo "📱 Sending Telegram notification..."

    # Use Python for reliable Telegram API call
    # Create temp file for message to avoid escaping issues
    MESSAGE_FILE="/tmp/telegram_message_$$.txt"
    cat > "$MESSAGE_FILE" <<MSGEOF
$MESSAGE
MSGEOF

    python3 - "$MESSAGE_FILE" <<'EOF'
import os
import urllib.request
import urllib.parse
import json
import sys

bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

# Read message from file to avoid shell escaping issues
with open(sys.argv[1], 'r') as f:
    markdown_message = f.read()

# Convert Markdown to Telegram MarkdownV2
try:
    import telegramify_markdown
    message = telegramify_markdown.markdownify(markdown_message)
except ImportError:
    print('   ⚠️  telegramify-markdown not installed, using raw markdown (may cause errors)')
    message = markdown_message

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
data = {
    'chat_id': chat_id,
    'text': message,
    'parse_mode': 'MarkdownV2'
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
            print(f'   Message preview: {message[:200]}...')
except Exception as e:
    print(f'   ❌ Failed to send Telegram notification: {e}')
    print(f'   Message preview: {message[:200]}...')
EOF

    rm -f "$MESSAGE_FILE"
else
    echo "   ⏭️  Skipping Telegram (missing credentials)"
fi

# Send to Pushover
if command -v pushover-notify >/dev/null 2>&1; then
    echo "📲 Sending Pushover notification..."

    PUSHOVER_TITLE="Bot $STATUS"

    # Build detailed Pushover message (plain text, no markdown)
    PUSHOVER_MESSAGE="Host: $HOSTNAME_SHORT
Time: $TIMESTAMP
PID: $PID
Exit: $EXIT_CODE"

    # Add file change info if available (strip HTML tags for plain text)
    if [[ -n "$CHANGED_FILES" ]]; then
        # Strip HTML tags: <code>text</code> → text
        CHANGED_FILES_PLAIN=$(echo "$CHANGED_FILES" | sed 's/<[^>]*>//g')
        PUSHOVER_MESSAGE="$PUSHOVER_MESSAGE

File Change: $CHANGED_FILES_PLAIN"
    fi

    # Add crash preview if available (first 2 lines only for Pushover)
    if [[ -f "$CRASH_CONTEXT_FILE" ]]; then
        CRASH_SHORT=$(tail -2 "$CRASH_CONTEXT_FILE" 2>/dev/null | tr '\n' ' ' || echo "")
        if [[ -n "$CRASH_SHORT" ]]; then
            PUSHOVER_MESSAGE="$PUSHOVER_MESSAGE

Error: ${CRASH_SHORT:0:200}"
        fi
    fi

    # Use priority 1 for crashes (high priority, bypasses quiet hours)
    if [[ "$PRIORITY" == "high" ]]; then
        PUSHOVER_PRIORITY=1
    else
        PUSHOVER_PRIORITY=0
    fi

    # Send with appropriate priority and sound
    curl -s \
        --form-string "token=$(security find-generic-password -s 'pushover-app-token' -a 'terryli' -w 2>/dev/null || jq -r '.pushover.app_token // ""' ~/.claude/automation/cns/config/cns_config.json 2>/dev/null)" \
        --form-string "user=$(security find-generic-password -s 'pushover-user-key' -a 'terryli' -w 2>/dev/null || jq -r '.pushover.user_key // ""' ~/.claude/automation/cns/config/cns_config.json 2>/dev/null)" \
        --form-string "device=iphone_13_mini" \
        --form-string "title=$PUSHOVER_TITLE" \
        --form-string "message=$PUSHOVER_MESSAGE" \
        --form-string "sound=$PUSHOVER_SOUND" \
        --form-string "priority=$PUSHOVER_PRIORITY" \
        https://api.pushover.net/1/messages.json >/dev/null 2>&1

    if [[ $? -eq 0 ]]; then
        echo "   ✅ Pushover notification sent (priority: $PUSHOVER_PRIORITY, sound: $PUSHOVER_SOUND)"
    else
        echo "   ⏭️  Pushover notification skipped (credentials not configured)"
    fi
else
    echo "   ⏭️  Skipping Pushover (pushover-notify not found)"
fi

echo "✅ Notification completed"
