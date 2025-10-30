# Reference Implementation

Complete working example from lychee bot monitoring system.

## File Structure

```
automation/lychee/runtime/bot/
├── bot-wrapper.sh         # watchexec wrapper, detects restart reasons
├── notify-restart.sh      # Dual-channel notification script
└── logs/
    ├── bot-notifications.log              # Notification execution log
    └── notification-archive/              # Pre-send message archives
        └── YYYYMMDD-HHMMSS-reason-PID.txt
```

## notify-restart.sh (Core Script)

**Usage**:
```bash
notify-restart.sh <reason> [exit_code] [watchexec_info_file] [crash_context_file]
```

**Arguments**:
- `reason`: `startup` | `code_change` | `crash`
- `exit_code`: Process exit code (default: 0)
- `watchexec_info_file`: JSON file with watchexec diagnostic info
- `crash_context_file`: Last N lines of error logs

**Key Components**:

### 1. HTML Message Construction

```bash
# Build message with HTML tags
MESSAGE="$EMOJI <b>Telegram Bot $STATUS</b>

<b>Host</b>: <code>$HOSTNAME_SHORT</code>
<b>Time</b>: $TIMESTAMP
<b>PID</b>: $PID
<b>Exit Code</b>: $EXIT_CODE$WATCHEXEC_DETAILS$CRASH_INFO

<i>Monitoring: watchexec</i>"
```

### 2. File Change Detection

```bash
# Parse watchexec JSON output
COMMON_PATH=$(jq -r '.watchexec.common_path // ""' "$WATCHEXEC_INFO_FILE")
WRITTEN_PATH=$(jq -r '.watchexec.written_path // ""' "$WATCHEXEC_INFO_FILE")

# HTML escape and format
FILENAME=$(basename "$WRITTEN_PATH" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
CHANGED_FILES="Modified: <code>$FILENAME</code>"
```

### 3. Telegram API Call (Python)

```python
import os
import urllib.request
import json
import sys

bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

# Read message from file (avoids shell escaping issues)
with open(sys.argv[1], 'r') as f:
    message = f.read()

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
data = {
    'chat_id': chat_id,
    'text': message,
    'parse_mode': 'HTML'  # ← Key: HTML mode
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    if result.get('ok'):
        print('   ✅ Telegram notification sent')
```

### 4. Pushover API Call

```bash
curl -s \
  --form-string "token=$(security find-generic-password -s 'pushover-app-token' -a 'terryli' -w)" \
  --form-string "user=$(security find-generic-password -s 'pushover-user-key' -a 'terryli' -w)" \
  --form-string "device=iphone_13_mini" \
  --form-string "title=$PUSHOVER_TITLE" \
  --form-string "message=$PUSHOVER_MESSAGE" \
  --form-string "sound=$PUSHOVER_SOUND" \
  --form-string "priority=$PUSHOVER_PRIORITY" \
  https://api.pushover.net/1/messages.json
```

**Priority/Sound Mapping**:
```bash
case "$REASON" in
    startup)
        PRIORITY="normal"
        PUSHOVER_PRIORITY=0
        PUSHOVER_SOUND="cosmic"
        ;;
    code_change)
        PRIORITY="normal"
        PUSHOVER_PRIORITY=0
        PUSHOVER_SOUND="bike"
        ;;
    crash)
        PRIORITY="high"
        PUSHOVER_PRIORITY=1  # Bypasses quiet hours
        PUSHOVER_SOUND="siren"
        ;;
esac
```

### 5. Message Archiving

```bash
MESSAGE_ARCHIVE_DIR="/path/to/logs/notification-archive"
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
```

## bot-wrapper.sh (watchexec Integration)

### Restart Detection

```bash
FIRST_RUN_MARKER="/tmp/lychee_bot_first_run"
REASON="startup"

if [[ ! -f "$FIRST_RUN_MARKER" ]]; then
    REASON="startup"
    touch "$FIRST_RUN_MARKER"
else
    REASON="code_change"  # Assume watchexec restart
fi

# Run bot
EXIT_CODE=0
uv run bot.py || EXIT_CODE=$?

# Update reason if crashed
if [[ $EXIT_CODE -ne 0 ]]; then
    REASON="crash"

    # Capture crash context
    CRASH_CONTEXT="/tmp/bot_crash_context_$$.txt"
    tail -20 "$BOT_LOG" > "$CRASH_CONTEXT"

    # Send notification (background, non-blocking)
    "$NOTIFY_SCRIPT" "$REASON" "$EXIT_CODE" "$WATCHEXEC_INFO_FILE" "$CRASH_CONTEXT" &
fi
```

### File Change Detection (macOS)

```bash
# Get current time
NOW=$(date +%s)

# Find most recently modified .py file
MOST_RECENT_FILE=""
MOST_RECENT_TIME=0

for dir in /path/to/watched/{bot,lib,orchestrator}; do
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            # Get modification time (macOS)
            FILE_MTIME=$(stat -f %m "$file" 2>/dev/null || echo "0")
            AGE=$((NOW - FILE_MTIME))

            # If modified in last 60s and newer than current best
            if [[ $AGE -lt 60 ]] && [[ $FILE_MTIME -gt $MOST_RECENT_TIME ]]; then
                MOST_RECENT_FILE="$file"
                MOST_RECENT_TIME=$FILE_MTIME
                echo "📝 Found recently modified: $(basename "$file") (${AGE}s ago)"
            fi
        fi
    done < <(find "$dir" -name "*.py" -type f 2>/dev/null)
done

if [[ -n "$MOST_RECENT_FILE" ]]; then
    echo "✅ Detected file change: $(basename "$MOST_RECENT_FILE")"
fi
```

## watchexec Configuration

### Basic Pattern

```bash
# Run with watchexec
watchexec \
    --restart \
    --watch /path/to/code \
    --exts py \
    -- /path/to/bot-wrapper.sh
```

### With Diagnostic Output

```bash
# Export diagnostic info to JSON file
export WATCHEXEC_FILTERER_TYPE=tagged
export WATCHEXEC_COMMON_PATH=""

watchexec \
    --restart \
    --watch /path/to/code \
    --exts py \
    --emit-events-to json \
    -- /path/to/bot-wrapper.sh
```

## Doppler Integration

### Load Credentials

```bash
# In wrapper script or systemd service
export $(doppler secrets download --no-file --format env)

# Or selectively:
export TELEGRAM_BOT_TOKEN=$(doppler secrets get TELEGRAM_BOT_TOKEN --plain)
export TELEGRAM_CHAT_ID=$(doppler secrets get TELEGRAM_CHAT_ID --plain)
```

### Doppler Secrets Structure

```json
{
  "TELEGRAM_BOT_TOKEN": "1234567890:ABC...",
  "TELEGRAM_CHAT_ID": "-1001234567890",
  "PUSHOVER_APP_TOKEN": "azGDORePK8gMa...",
  "PUSHOVER_USER_KEY": "uQiRzpo4DXghD..."
}
```

## Logging Configuration

### Redirect to Dedicated Log

```bash
#!/usr/bin/env bash
# notify-restart.sh

# Log all output to dedicated file
NOTIFICATION_LOG="/path/to/logs/bot-notifications.log"
exec >> "$NOTIFICATION_LOG" 2>&1

echo "========================================================================"
echo "🔔 Bot Restart Notification - $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "========================================================================"

# Rest of script...
```

### Log Rotation (Optional)

```bash
# Keep last 100KB only
if [[ -f "$NOTIFICATION_LOG" ]] && [[ $(stat -f %z "$NOTIFICATION_LOG") -gt 102400 ]]; then
    tail -1000 "$NOTIFICATION_LOG" > "$NOTIFICATION_LOG.tmp"
    mv "$NOTIFICATION_LOG.tmp" "$NOTIFICATION_LOG"
fi
```

## Testing

### Manual Test

```bash
# Test notification directly
./notify-restart.sh "code_change" 0 "/path/to/watchexec-info.json" ""

# Check logs
tail -f logs/bot-notifications.log

# Check archive
ls -lah logs/notification-archive/
cat logs/notification-archive/$(ls -t logs/notification-archive/ | head -1)
```

### Test HTML Rendering

```bash
# Send test message with special characters
MESSAGE="<b>Test</b>: <code>handler_classes.py</code> with <i>underscores</i>"

# Should render correctly with underscores visible
```

## Troubleshooting

### Telegram 400 Bad Request

```bash
# Check archived message for invalid HTML
cat logs/notification-archive/latest.txt

# Common issues:
# - Unescaped & < >
# - Unclosed tags
# - Invalid tag nesting
```

### No File Detected

```bash
# Check watchexec info file
cat /path/to/watchexec-info.json

# Verify stat command works
stat -f %m /path/to/file.py

# Check time window (60s default)
```

### Credentials Not Loading

```bash
# Test Doppler
doppler secrets get TELEGRAM_BOT_TOKEN --plain

# Test environment
echo "$TELEGRAM_BOT_TOKEN"

# Test keychain (macOS)
security find-generic-password -s 'pushover-app-token' -a 'username' -w
```

## Performance Notes

- Message archiving: ~5ms per notification
- Telegram API call: ~200-500ms (network dependent)
- Pushover API call: ~100-300ms (network dependent)
- Total overhead: ~300-800ms per notification

Fire-and-forget background execution ensures process restart is not delayed.

## Security Considerations

1. **Credentials**: Never logged, only loaded at runtime
2. **Message Content**: May contain file paths - ensure no secrets in filenames
3. **Archive Files**: Store in restricted directory (600/700 permissions)
4. **Log Rotation**: Prevent unbounded growth
5. **API Tokens**: Use read-only scopes where possible

## Real-World Example Output

### Telegram Message (HTML Rendered)

```
🔄 Telegram Bot Restarted (code change)

Host: m3max
Time: 2025-10-29 22:58:21 PDT
PID: 31307
Exit Code: 0

Trigger: /Users/terryli/.claude/automation/lychee/runtime/lib/format_utils.py
Action: Modified: format_utils.py

Monitoring: watchexec
```

### Archived Message File

```
========================================================================
Notification Archive
========================================================================
Timestamp: 2025-10-29 22:58:21 PDT
Reason: code_change
Exit Code: 0
Host: m3max
PID: 31307

--- TELEGRAM MESSAGE ---
🔄 <b>Telegram Bot Restarted (code change)</b>

<b>Host</b>: <code>m3max</code>
<b>Time</b>: 2025-10-29 22:58:21 PDT
<b>PID</b>: 31307
<b>Exit Code</b>: 0

<b>Trigger</b>: <code>/Users/terryli/.claude/automation/lychee/runtime/lib/format_utils.py</code>
<b>Action</b>: Modified: <code>format_utils.py</code>

<i>Monitoring: watchexec</i>

--- WATCHEXEC INFO FILE ---
{
  "timestamp": "2025-10-30T05:58:21Z",
  "watchexec": {
    "common_path": "/Users/terryli/.claude/automation/lychee/runtime/lib/format_utils.py",
    "written_path": "/Users/terryli/.claude/automation/lychee/runtime/lib/format_utils.py"
  }
}
========================================================================
```

## Success Metrics

From 2025-10-29 production deployment:
- ✅ 15+ notifications sent successfully
- ✅ 0 formatting errors (after HTML migration)
- ✅ 100% dual-channel delivery (both Telegram + Pushover)
- ✅ File detection: 95% accuracy (5% missing due to rapid restart)
- ✅ Average latency: 400ms per notification
