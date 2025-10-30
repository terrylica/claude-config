______________________________________________________________________

## name: dual-channel-watchexec-notifications description: Send dual-channel notifications (Telegram + Pushover) on watchexec events with proper formatting and credentials. Use when monitoring file changes, process restarts, or setting up watchexec-triggered alerts. Covers HTML mode, credential management, and common pitfalls. allowed-tools: Read, Write, Edit, Bash

# Dual-Channel Watchexec Notifications

Send reliable notifications to both Telegram and Pushover when watchexec detects file changes or process crashes.

## Core Pattern

**watchexec wrapper script** → **detect event** → **notify-script** → **Telegram + Pushover**

```bash
# wrapper.sh - Monitors process and detects restart reasons
watchexec --restart -- python bot.py

# On event, call:
notify-script.sh <reason> <exit_code> <watchexec_info_file> <crash_context>
```

## Telegram: Use HTML Mode (NOT Markdown)

### Why HTML Mode

**Industry Best Practice**:

- Markdown/MarkdownV2 requires escaping 40+ special characters (`.`, `-`, `_`, etc.)
- HTML only requires escaping 3 characters: `&`, `<`, `>`
- More reliable, simpler, less error-prone

### HTML Formatting

```python
# Python API call
data = {
    'chat_id': chat_id,
    'text': message,
    'parse_mode': 'HTML'  # NOT 'Markdown' or 'MarkdownV2'
}
```

**HTML Tags**:

- Bold: `<b>text</b>`
- Code: `<code>text</code>`
- Italic: `<i>text</i>`
- Code blocks: `<pre>text</pre>`

**HTML Escaping** (Bash):

```bash
# Escape special chars before sending
ESCAPED=$(echo "$text" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
MESSAGE="<b>Alert</b>: <code>$ESCAPED</code>"
```

### Message Template

**Simplified format** (matches other Telegram messages in the system):

```bash
# Build session debug line
SESSION_DEBUG_LINE="session=$CLAUDE_SESSION_ID | 🐛 debug=~/.claude/debug/\${session}.txt"

# Normal restart (code change or startup)
MESSAGE="$EMOJI <b>Bot $STATUS</b>

<b>Directory</b>: <code>$WORKING_DIR</code>
<b>Branch</b>: <code>$GIT_BRANCH</code>
<code>$SESSION_DEBUG_LINE</code>
$WATCHEXEC_DETAILS"

# Crash (includes exit code and error details)
MESSAGE="$EMOJI <b>Bot Crashed</b>

<b>Directory</b>: <code>$WORKING_DIR</code>
<b>Branch</b>: <code>$GIT_BRANCH</code>
<code>$SESSION_DEBUG_LINE</code>

<b>Exit Code</b>: $EXIT_CODE
$CRASH_INFO"
```

**Why this format**:
- Consistent with other Telegram messages (workflow completions, notifications)
- Removes unnecessary info (host, monitoring system, timestamp)
- Adds context (session ID, branch, directory)
- Exit code only shown for crashes (not for normal restarts with exit code 0)

## Pushover Integration

### API Call Pattern

```bash
curl -s \
  --form-string "token=$PUSHOVER_APP_TOKEN" \
  --form-string "user=$PUSHOVER_USER_KEY" \
  --form-string "device=device_name" \
  --form-string "title=$TITLE" \
  --form-string "message=$MESSAGE" \
  --form-string "sound=$SOUND" \
  --form-string "priority=$PRIORITY" \
  https://api.pushover.net/1/messages.json
```

**Priority Levels**:

- `0`: Normal (default sound, respects quiet hours)
- `1`: High (bypasses quiet hours, alert sound)

**Sounds**: `cosmic`, `bike`, `siren`, etc.

### ⚠️ CRITICAL: Pushover Does NOT Support HTML

**Pushover uses plain text only** - you MUST strip HTML tags before sending:

```bash
# ❌ WRONG - Pushover will display literal HTML tags
PUSHOVER_MESSAGE="<b>Alert</b>: <code>file.py</code>"
# User sees: <b>Alert</b>: <code>file.py</code>

# ✅ CORRECT - Strip HTML tags for plain text
CHANGED_FILES_PLAIN=$(echo "$CHANGED_FILES" | sed 's/<[^>]*>//g')
PUSHOVER_MESSAGE="Alert: $CHANGED_FILES_PLAIN"
# User sees: Alert: file.py
```

**Why This Matters**:

- Telegram uses HTML mode for formatting
- Pushover does NOT interpret HTML
- Sending HTML to Pushover shows ugly `<code>`, `<b>` tags in notification
- Always strip tags: `sed 's/<[^>]*>//g'`

**Pattern**: Build message in HTML for Telegram, then strip tags for Pushover:

```bash
# 1. Build HTML message for Telegram
MESSAGE_HTML="<b>File</b>: <code>handler_classes.py</code>"

# 2. Strip HTML for Pushover
MESSAGE_PLAIN=$(echo "$MESSAGE_HTML" | sed 's/<[^>]*>//g')
# Result: "File: handler_classes.py"
```

## Credential Management

### Pattern 1: Doppler (Recommended)

```bash
# Load from Doppler project
export TELEGRAM_BOT_TOKEN=$(doppler secrets get TELEGRAM_BOT_TOKEN --plain)
export TELEGRAM_CHAT_ID=$(doppler secrets get TELEGRAM_CHAT_ID --plain)
```

### Pattern 2: Environment Variables

```bash
# From shell environment
if [[ -n "${TELEGRAM_BOT_TOKEN:-}" ]] && [[ -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    # Send notification
fi
```

### Pattern 3: Keychain (macOS)

```bash
PUSHOVER_TOKEN=$(security find-generic-password -s 'pushover-app-token' -a 'username' -w 2>/dev/null)
```

**Security**: Never hardcode credentials in scripts or skill files!

## watchexec Integration

### File Change Detection (macOS Compatible)

**DO** (works on macOS):

```bash
# Use stat to check modification time
NOW=$(date +%s)
FILE_MTIME=$(stat -f %m "$file" 2>/dev/null || echo "0")
AGE=$((NOW - FILE_MTIME))

if [[ $AGE -lt 60 ]]; then
    echo "File modified ${AGE}s ago"
fi
```

**DON'T** (broken on macOS):

```bash
# find -newermt has different syntax on BSD/macOS
find . -newermt "60 seconds ago"  # ❌ Fails on macOS
```

### Restart Reason Detection

```bash
# Determine why process restarted
if [[ ! -f "$FIRST_RUN_MARKER" ]]; then
    REASON="startup"
    touch "$FIRST_RUN_MARKER"
elif [[ $EXIT_CODE -ne 0 ]]; then
    REASON="crash"
else
    REASON="code_change"
fi
```

## Message Archiving (Debugging)

Always save messages before sending for post-mortem debugging:

```bash
MESSAGE_ARCHIVE_DIR="/path/to/logs/notification-archive"
mkdir -p "$MESSAGE_ARCHIVE_DIR"
MESSAGE_FILE="$MESSAGE_ARCHIVE_DIR/$(date '+%Y%m%d-%H%M%S')-$REASON-$PID.txt"

cat > "$MESSAGE_FILE" <<ARCHIVE_EOF
========================================================================
Timestamp: $TIMESTAMP
Reason: $REASON
Exit Code: $EXIT_CODE

--- TELEGRAM MESSAGE ---
$MESSAGE

--- CONTEXT ---
$(cat "$WATCHEXEC_INFO_FILE" 2>/dev/null || echo "Not available")
========================================================================
ARCHIVE_EOF
```

## Common Pitfalls

### Pitfall 1: Pushover Shows HTML Tags (CRITICAL)

**Problem**: Pushover displays literal `<code>`, `<b>`, `</code>` in notifications

**Cause**: Pushover uses **plain text only** - does NOT interpret HTML

**Solution**: Strip HTML tags before sending to Pushover

```bash
# ❌ WRONG - Sends HTML to Pushover
PUSHOVER_MESSAGE="Modified: <code>handler_classes.py</code>"
# User sees: Modified: <code>handler_classes.py</code>

# ✅ CORRECT - Strip HTML tags
CHANGED_FILES_PLAIN=$(echo "$CHANGED_FILES" | sed 's/<[^>]*>//g')
PUSHOVER_MESSAGE="Modified: $CHANGED_FILES_PLAIN"
# User sees: Modified: handler_classes.py
```

**Remember**: Telegram = HTML, Pushover = Plain Text

### Pitfall 2: Markdown Escaping Hell

**Problem**: Files with underscores (`handler_classes.py`) display as `handlerclasses.py`

**Cause**: Markdown treats `_` as italic marker

**Solution**: Use HTML mode, wrap in `<code>` tags

```bash
# ❌ WRONG (Markdown)
MESSAGE="Modified: handler_classes.py"  # Renders: handlerclasses.py

# ✅ CORRECT (HTML)
FILENAME=$(basename "$file" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
MESSAGE="Modified: <code>$FILENAME</code>"  # Renders: handler_classes.py
```

### Pitfall 3: Literal Variable Names Sent

**Problem**: Telegram receives literal text `"$MESSAGE"` instead of content

**Cause**: Heredoc with quotes prevents variable expansion

**Solution**: Use heredoc WITHOUT quotes

```bash
# ❌ WRONG
cat > "$FILE" <<'MSGEOF'
$MESSAGE
MSGEOF

# ✅ CORRECT
cat > "$FILE" <<MSGEOF
$MESSAGE
MSGEOF
```

### Pitfall 3: macOS File Detection Failures

**Problem**: Empty Trigger/Action fields, no file detected

**Cause**: `find -newermt` syntax differs on BSD (macOS) vs GNU (Linux)

**Solution**: Use `stat` instead of `find -newermt`

```bash
# ✅ CORRECT (portable)
FILE_MTIME=$(stat -f %m "$file" 2>/dev/null || echo "0")  # macOS
# For Linux: stat -c %Y "$file"
```

### Pitfall 4: Telegram 400 Bad Request

**Problem**: HTTP 400 errors with "Bad Request"

**Causes**:

1. Missing HTML escaping (`&`, `<`, `>`)
1. Unclosed HTML tags
1. Invalid HTML structure

**Solution**: Always escape special chars, validate HTML structure

```bash
# Test message before sending
echo "$MESSAGE" | grep -E '<[^>]*$'  # Check for unclosed tags
```

### Pitfall 5: Hardcoded Credentials

**Problem**: Secrets leaked in git, exposed in logs

**Solution**: Use env vars, Doppler, or keychain

```bash
# ❌ WRONG
TELEGRAM_BOT_TOKEN="1234567890:ABC..."

# ✅ CORRECT
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
    echo "Error: TELEGRAM_BOT_TOKEN not set"
    exit 1
fi
```

## Execution Pattern

### Fire-and-Forget Background Notifications

Don't block process restart on notification delivery:

```bash
# Run notification in background (non-blocking)
"$NOTIFY_SCRIPT" "crash" "$EXIT_CODE" "$INFO_FILE" "$CONTEXT_FILE" &

# Process continues/restarts immediately
```

## Validation Checklist

Before deploying:

- [ ] Using HTML parse mode for Telegram (not Markdown)
- [ ] HTML escaping applied to all dynamic content (`&`, `<`, `>`)
- [ ] Credentials loaded from env vars/Doppler (not hardcoded)
- [ ] Message archiving enabled for debugging
- [ ] File detection uses `stat` (not `find -newermt`)
- [ ] Heredocs use unquoted delimiters for variable expansion
- [ ] Notifications run in background (fire-and-forget)
- [ ] Tested with files containing special chars (`_`, `.`, `-`)
- [ ] Both Telegram and Pushover successfully receiving

## Example Scripts

Self-contained examples in `examples/` directory:

- **`notify-restart.sh`**: Complete dual-channel notification script
- **`bot-wrapper.sh`**: watchexec wrapper with restart detection
- **`setup-example.sh`**: Full setup guide and systemd service

All examples include:

- HTML mode formatting
- Dual-channel delivery (Telegram + Pushover)
- Message archiving
- watchexec integration
- Crash context capture
- Multiple credential loading patterns

See `reference.md` for detailed implementation notes.

## Summary

**Key Lessons**:

1. **Always use HTML mode** for Telegram (simpler escaping)
1. **Escape only 3 chars** in HTML: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`
1. **Archive messages** before sending for debugging
1. **Use `stat`** for file detection on macOS (not `find -newermt`)
1. **Load credentials** from env vars/Doppler (never hardcode)
1. **Fire-and-forget** background notifications (don't block restarts)

**Token cost**: ~50 tokens until activated, ~1500 when loaded
