# Bot Restart Notification System

## Overview

Automated dual-channel notification system that sends alerts via **Telegram** and **Pushover** whenever the Telegram bot restarts.

**Monitoring**: watchexec detects file changes and restarts the bot
**Notifications**: Both Telegram and Pushover receive restart alerts
**Logging**: Dedicated log at `/Users/terryli/.claude/automation/lychee/logs/bot-notifications.log`

## Architecture

```
watchexec (file watcher)
    ↓
bot-wrapper.sh (detects restart reason)
    ↓
notify-restart.sh (dual notification)
    ├─→ Telegram API (instant mobile push)
    └─→ Pushover API (persistent notifications)
```

## Components

### 1. `bot-wrapper.sh`

Wraps the bot execution and detects restart events.

**Restart Detection**:

- `startup` - First run (creates `/tmp/bot_first_run_$$` marker)
- `code_change` - File modification detected by watchexec (`WATCHEXEC_COMMON_PATH` set)
- `crash` - Bot exited with non-zero exit code

**Location**: `/Users/terryli/.claude/automation/lychee/runtime/bot/bot-wrapper.sh`

### 2. `notify-restart.sh`

Sends notifications to both Telegram and Pushover.

**Notification Types**:

| Reason | Emoji | Priority | Description |
| --- | --- | --- | --- |
| `startup` | 🚀 | normal | Initial bot start |
| `code_change` | 🔄 | normal | Automatic reload (watchexec) |
| `crash` | 💥 | high | Unexpected termination |

**Location**: `/Users/terryli/.claude/automation/lychee/runtime/bot/notify-restart.sh`

## Configuration

### Telegram Credentials

Loaded from Doppler secrets (via `doppler run`):

- `TELEGRAM_BOT_TOKEN` - Bot authentication token
- `TELEGRAM_CHAT_ID` - Target chat ID for notifications

### Pushover Credentials

Multi-source fallback (priority order):

1. **Git-based config** (preferred): `~/.claude/automation/cns/config/cns_config.json`
1. **macOS Keychain** (fallback): `security find-generic-password`

See `/Users/terryli/.claude/specifications/pushover-integration.yaml` for details.

## Logs

### Bot Logs

Main bot operational logs:

```bash
/Users/terryli/.claude/automation/lychee/logs/telegram-handler.log
```

### Notification Logs

Dedicated notification activity logs:

```bash
/Users/terryli/.claude/automation/lychee/logs/bot-notifications.log
```

**View recent notifications**:

```bash
tail -50 /Users/terryli/.claude/automation/lychee/logs/bot-notifications.log
```

## Testing

### Manual Notification Test

```bash
# Export credentials
export TELEGRAM_BOT_TOKEN=$(doppler run --project claude-config --config dev -- printenv TELEGRAM_BOT_TOKEN)
export TELEGRAM_CHAT_ID=$(doppler run --project claude-config --config dev -- printenv TELEGRAM_CHAT_ID)

# Send test notification
/Users/terryli/.claude/automation/lychee/runtime/bot/notify-restart.sh "startup" 0
```

### Trigger Automatic Restart

```bash
# Touch a Python file to trigger watchexec
touch /Users/terryli/.claude/automation/lychee/runtime/bot/bot_services.py

# Wait 5 seconds and check notifications
sleep 5 && tail -20 /Users/terryli/.claude/automation/lychee/logs/bot-notifications.log
```

## Watchexec Command

Current watchexec configuration:

```bash
watchexec \
  --watch /Users/terryli/.claude/automation/lychee/runtime/bot \
  --watch /Users/terryli/.claude/automation/lychee/runtime/lib \
  --watch /Users/terryli/.claude/automation/lychee/runtime/orchestrator \
  --exts py \
  --restart \
  --debounce 100ms \
  --stop-signal SIGTERM \
  --stop-timeout 5s \
  -- doppler run --project claude-config --config dev -- \
     /Users/terryli/.claude/automation/lychee/runtime/bot/bot-wrapper.sh \
  >> /Users/terryli/.claude/automation/lychee/logs/telegram-handler.log 2>&1 &
```

**PID File**: `/Users/terryli/.claude/automation/lychee/state/bot.pid`

## Message Format

### Telegram Message

```markdown
🚀 **Telegram Bot Started**

**Host**: `terrylis-mac`
**Time**: 2025-10-29 22:30:15 PDT
**PID**: 12345
**Exit Code**: 0

_Monitoring active via watchexec_
```

### Pushover Message

```
Title: Bot Started
Message:
Host: terrylis-mac
Time: 2025-10-29 22:30:15 PDT
Exit: 0
```

**Sound**: cosmic
**Device**: iphone_13_mini

## Troubleshooting

### No notifications received

1. **Check notification log**:

   ```bash
   tail -50 /Users/terryli/.claude/automation/lychee/logs/bot-notifications.log
   ```

1. **Verify credentials**:

   ```bash
   doppler run --project claude-config --config dev -- printenv | grep TELEGRAM
   jq '.pushover' ~/.claude/automation/cns/config/cns_config.json
   ```

1. **Test manually**:

   ```bash
   /Users/terryli/.claude/automation/lychee/runtime/bot/notify-restart.sh startup 0
   ```

### Bot not restarting

1. **Check watchexec process**:

   ```bash
   ps aux | grep watchexec | grep -v grep
   ```

1. **Check bot wrapper process**:

   ```bash
   ps aux | grep bot-wrapper | grep -v grep
   ```

### Duplicate notifications

This is expected behavior - watchexec may restart the bot multiple times during rapid file changes. Notifications are fire-and-forget to avoid blocking bot startup.

## Security

- **Telegram credentials**: Stored in Doppler (encrypted secrets management)
- **Pushover credentials**: Git-based config (private company repo) with keychain fallback
- **Logs**: Local filesystem only, not exposed externally
- **Notification content**: Does not include sensitive data (workspace paths, API keys, etc.)

## Related Documentation

- **Pushover Integration**: `/Users/terryli/.claude/specifications/pushover-integration.yaml`
- **Bot Architecture**: `/Users/terryli/.claude/automation/lychee/runtime/bot/README.md`
- **CNS System**: `/Users/terryli/.claude/automation/cns/README.md`

## Future Enhancements

- [ ] Add notification throttling (max 1 per minute) to prevent spam
- [ ] Include last 5 lines of bot log in crash notifications
- [ ] Add webhook endpoint for external monitoring systems
- [ ] Track restart frequency metrics (SQLite database)
