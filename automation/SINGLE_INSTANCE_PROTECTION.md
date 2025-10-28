# Single-Instance Protection System

**Version**: 1.0.0
**Created**: 2025-10-27
**Purpose**: Prevent multiple process instances and file caching issues

---

## The Problem

We encountered critical production issues:

1. **Multiple bot instances** - 3 Telegram bots running simultaneously, wasting resources
2. **Cached hook files** - Bash processes kept old file versions open for 24+ hours
3. **Stale processes** - Process from Oct 26 still running on Oct 27, using inode 86071856 (old file) instead of 86304987 (current file)

This caused the "Stop hook error" to persist despite all fixes being in place.

---

## The Solution

### 1. Single-Instance Library

**File**: `/Users/terryli/.claude/automation/lib/single-instance.sh`

**Features**:

- PID file management with automatic stale cleanup
- File locking (`flock`) for atomic operations
- Process verification (not just PID check)
- Automatic cleanup on exit via `trap`
- Optional `--kill-existing` to terminate running instances

**Usage**:

```bash
#!/usr/bin/env bash
source "$HOME/.claude/automation/lib/single-instance.sh"

# Ensure only one instance (fail if already running)
ensure_single_instance "my-script"

# OR: Kill existing instance and start fresh
ensure_single_instance "my-script" --kill-existing

# Rest of your script...
```

**How it works**:

1. **Check PID file** - Look for `/Users/terryli/.claude/automation/run/my-script.pid`
2. **Verify process** - Don't just check PID existence, verify it's actually our script (handles PID reuse)
3. **Clean stale PIDs** - If process not running or is different script, remove PID file
4. **Atomic write** - Use `flock` to ensure no race conditions
5. **Register cleanup** - Set `trap` to remove PID file on exit

### 2. Stale Hook Cleanup

**File**: `/Users/terryli/.claude/automation/lib/cleanup-stale-hooks.sh`

**Purpose**: Kill hook processes older than 1 hour (prevents file caching)

**Usage** (automatically called by hooks):

```bash
source "$HOME/.claude/automation/lib/cleanup-stale-hooks.sh"
cleanup_stale_hooks
```

**How it works**:

1. Find all processes matching hook patterns
2. Calculate process age from start time
3. Kill processes older than 1 hour (3600 seconds)
4. Log actions to `/tmp/hook-cleanup.log`

### 3. Telegram Bot Launcher

**File**: `/Users/terryli/.local/bin/start-telegram-bot`

**Purpose**: Safe bot startup with single-instance protection

**Usage**:

```bash
# Start bot (kills existing instance if running)
start-telegram-bot
```

**Features**:

- Automatically kills existing bot instances
- Uses PID file: `/Users/terryli/.claude/automation/run/telegram-bot.pid`
- Ensures clean startup every time

---

## Integration Status

### ✅ Implemented

1. **Single-instance library** - Core functionality complete
2. **Bot launcher** - `/Users/terryli/.local/bin/start-telegram-bot`
3. **Stale hook cleanup** - Integrated into `check-links-hybrid.sh`
4. **PID directory** - Auto-created at `/Users/terryli/.claude/automation/run/`

### 🔄 In Progress

- Hook cleanup integration testing

### 📋 Recommended (Optional)

1. **System service** - Run bot as macOS LaunchAgent for auto-restart
2. **Monitoring** - Alert if PID file cleanup happens frequently
3. **Metrics** - Track process age distribution

---

## File Caching Explanation

### Why Bash Caches Files

When bash executes a script with `bash /path/to/script.sh`, it:

1. **Opens the file** (gets file descriptor, e.g., FD 255)
2. **Stores inode reference** (e.g., inode 86071856)
3. **Reads from inode** - NOT from the path

If you edit the file:

- Old process keeps reading from **old inode** 86071856
- New processes read from **new inode** 86304987
- Result: Old and new processes run different code!

### Example from Our System

```
PID 62324: Started Oct 26 18:06
  - File descriptor 255r → inode 86071856 (25,550 bytes)
  - This is the OLD version of check-links-hybrid.sh

Current file: Oct 27 14:43
  - inode 86304987 (26,157 bytes)
  - This is the NEW version with our fixes
```

### Why 1 Hour Timeout?

- Claude Code sessions typically last < 1 hour
- Hooks run on Stop events (end of session)
- If a hook process lives > 1 hour, it's definitely stale
- Balance between safety (don't kill active hooks) and freshness

---

## Testing

### Test Single-Instance Protection

```bash
# Terminal 1: Start bot
start-telegram-bot
# [single-instance] Started telegram-bot with PID 12345

# Terminal 2: Try to start again (should fail)
start-telegram-bot
# [single-instance] ERROR: telegram-bot is already running (PID 12345)

# Terminal 2: Force kill and start
source ~/.claude/automation/lib/single-instance.sh
ensure_single_instance "telegram-bot" --kill-existing
# [single-instance] Killing existing instance (PID 12345)
# [single-instance] Started telegram-bot with PID 67890
```

### Test Stale Hook Cleanup

```bash
# Create a fake stale process
sleep 10000 &
pid=$!

# Wait 1 hour (or manually set age in cleanup script for testing)
# Then run cleanup
/Users/terryli/.claude/automation/lib/cleanup-stale-hooks.sh

# Check log
tail /tmp/hook-cleanup.log
```

### Verify No Cached Hooks

```bash
# Check for open file handles to hooks
lsof | grep "check-links-hybrid.sh"

# Should show only recent processes or none
```

---

## Troubleshooting

### Multiple Instances Still Running

**Symptom**: `ps aux | grep telegram-bot` shows multiple processes

**Cause**: Old instances not properly killed

**Fix**:

```bash
source ~/.claude/automation/lib/single-instance.sh
kill_all_instances "telegram-bot"
```

### PID File Stale

**Symptom**: Bot won't start, says "already running" but `ps` shows nothing

**Cause**: PID file left behind after crash

**Fix**:

```bash
rm /Users/terryli/.claude/automation/run/telegram-bot.pid
```

(The library should auto-clean this, but manual removal works)

### Hook Still Using Old File

**Symptom**: Fixes applied but error persists

**Debugging**:

```bash
# Find processes with old file open
lsof | grep check-links-hybrid

# Check process age
ps -p <PID> -o pid,lstart,command

# Force kill all hook processes
pkill -9 -f "check-links-hybrid"
```

---

## Future Enhancements

### 1. macOS LaunchAgent

Create `/Users/terryli/Library/LaunchAgents/com.terryli.telegram-bot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.terryli.telegram-bot</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/terryli/.local/bin/start-telegram-bot</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/terryli/.claude/automation/lychee/logs/bot-stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/terryli/.claude/automation/lychee/logs/bot-stderr.log</string>
</dict>
</plist>
```

Load:

```bash
launchctl load ~/Library/LaunchAgents/com.terryli.telegram-bot.plist
```

### 2. Monitoring Script

```bash
#!/usr/bin/env bash
# Monitor for frequent PID cleanup (indicates issues)

pidfile_dir="/Users/terryli/.claude/automation/run"
watch_duration=3600  # 1 hour

initial_count=$(ls "$pidfile_dir"/*.pid 2>/dev/null | wc -l)
sleep $watch_duration
final_count=$(ls "$pidfile_dir"/*.pid 2>/dev/null | wc -l)

if [[ $final_count -gt $((initial_count + 10)) ]]; then
    echo "WARNING: Excessive PID file creation detected" | \
        mail -s "Hook Protection Alert" user@example.com
fi
```

### 3. Systemd Integration (Linux)

For Linux systems, create `/etc/systemd/user/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Bot for Claude Code
After=network.target

[Service]
Type=simple
ExecStart=/Users/terryli/.local/bin/start-telegram-bot
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

---

## References

- **PID files**: https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch05s13.html
- **flock**: `man flock` - File locking for atomic operations
- **Bash traps**: https://tldp.org/LDP/Bash-Beginners-Guide/html/sect_12_02.html
- **Process verification**: Prevents PID reuse issues (PID wraps at 99999 on macOS)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-27
**Maintainer**: Terry Li
