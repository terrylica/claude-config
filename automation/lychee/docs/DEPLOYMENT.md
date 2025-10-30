# Lychee Link Autofix Bot - Deployment Guide

Version: 1.0.0

## Architecture

The system consists of two background services:

1. **telegram-approval-handler.py** - Polls Telegram for button clicks, updates approval state
1. **auto-fix-orchestrator.py** - Watches approval state, triggers Claude CLI auto-fix

## Deployment Options

### Option 1: Development Mode (Zellij Layout) ✨ Recommended for Testing

**When to use:** Development, testing, manual control

**Pros:**

- Visible logs in terminal
- Easy to restart/debug
- No system integration required
- Can attach/detach

**Start:**

```bash
zellij --layout ~/.claude/automation/lychee/lychee-bot.kdl
```

**Monitor:**

- Tab 1: Both services running in split panes
- Tab 2: Live Lychee log tail

**Stop:**

- Close Zellij session or kill panes individually

---

### Option 2: Production Mode (macOS Launchd) ✨ Recommended for Daily Use

**When to use:** Stable daily usage, auto-start on login

**Pros:**

- Auto-start on login
- Auto-restart on crash
- System-managed logs
- Runs truly in background

**Install:**

```bash
# Create log directory
mkdir -p ~/.claude/logs

# Copy plist files to LaunchAgents
cp ~/.claude/automation/lychee/com.user.lychee.*.plist ~/Library/LaunchAgents/

# Load services
launchctl load ~/Library/LaunchAgents/com.user.lychee.telegram-handler.plist
launchctl load ~/Library/LaunchAgents/com.user.lychee.orchestrator.plist
```

**Check Status:**

```bash
# List running services
launchctl list | grep lychee

# Check specific service
launchctl list com.user.lychee.telegram-handler
```

**View Logs:**

```bash
# Live logs
tail -f ~/.claude/logs/telegram-handler.log
tail -f ~/.claude/logs/orchestrator.log

# Errors
tail -f ~/.claude/logs/telegram-handler.error.log
tail -f ~/.claude/logs/orchestrator.error.log
```

**Stop Services:**

```bash
launchctl unload ~/Library/LaunchAgents/com.user.lychee.telegram-handler.plist
launchctl unload ~/Library/LaunchAgents/com.user.lychee.orchestrator.plist
```

**Restart Services:**

```bash
launchctl kickstart -k gui/$(id -u)/com.user.lychee.telegram-handler
launchctl kickstart -k gui/$(id -u)/com.user.lychee.orchestrator
```

---

### Option 3: Manual Background Processes (Current)

**When to use:** Quick one-off testing only

**Not recommended because:**

- Manual start required
- No auto-restart
- No log management
- Process dies when terminal closes

**Start:**

```bash
cd ~/.claude/automation/lychee
doppler run -p claude-config -c dev -- uv run telegram-approval-handler.py &
doppler run -p claude-config -c dev -- uv run auto-fix-orchestrator.py &
```

---

## Recommended Setup

### For Daily Use:

1. **Install Launchd agents** (Option 2)
1. **Keep Zellij layout** (Option 1) for debugging when needed

### For Development:

1. **Use Zellij layout exclusively** (Option 1)

---

## Troubleshooting

### Services Not Starting

**Check Doppler credentials:**

```bash
doppler setup --project claude-config --config dev
doppler run -p claude-config -c dev -- echo "OK"
```

**Check paths in plist files:**

- Verify `/opt/homebrew/bin/doppler` exists (or use `/usr/local/bin/doppler`)
- Verify `/Users/terryli/.local/bin/uv` exists
- Verify script paths are correct

### Services Crash Loop

**Check logs:**

```bash
tail -50 ~/.claude/logs/*.error.log
```

**Common issues:**

- Missing Doppler credentials
- Missing Telegram bot token/chat ID
- Python dependency issues

**Force restart:**

```bash
launchctl kickstart -k gui/$(id -u)/com.user.lychee.telegram-handler
```

### Not Receiving Telegram Notifications

**Check approval handler is running:**

```bash
launchctl list com.user.lychee.telegram-handler
# OR
ps aux | grep telegram-approval-handler
```

**Check orchestrator is running:**

```bash
launchctl list com.user.lychee.orchestrator
# OR
ps aux | grep auto-fix-orchestrator
```

**Test notification manually:**

```bash
doppler run -p claude-config -c dev -- uv run send-hook-notification.py
```

---

## Configuration

### Environment Variables (via Doppler)

Required secrets in `claude-config/dev`:

- `TELEGRAM_BOT_TOKEN` - Bot API token from @BotFather
- `TELEGRAM_CHAT_ID` - Your Telegram user ID

### File Locations

- **Approval state:** `/tmp/lychee_approval_state.json`
- **Lychee results:** `/tmp/claude_lychee_full.txt`
- **Logs:** `~/.claude/logs/`
- **Scripts:** `~/.claude/automation/lychee/`

---

## Monitoring

### Quick Health Check

```bash
# All services healthy if both show PID
launchctl list | grep lychee

# Check recent activity
tail -20 ~/.claude/logs/telegram-handler.log
tail -20 ~/.claude/logs/orchestrator.log
```

### Detailed Status

```bash
# Service details
launchctl list com.user.lychee.telegram-handler
launchctl list com.user.lychee.orchestrator

# Process info
ps aux | grep -E "(telegram-approval|auto-fix-orchestrator)" | grep -v grep
```

---

## Uninstall

```bash
# Stop and unload services
launchctl unload ~/Library/LaunchAgents/com.user.lychee.*.plist

# Remove plist files
rm ~/Library/LaunchAgents/com.user.lychee.*.plist

# Optional: Remove logs
rm -rf ~/.claude/logs/telegram-handler*
rm -rf ~/.claude/logs/orchestrator*
```
