---
name: telegram-bot-management
description: Telegram bot development workflow, startup procedures, and watchexec auto-reload. Use when user mentions telegram bot, lychee automation, bot startup, bot restart, watchexec, or bot development.
---

# Telegram Bot Management

Multi-workspace Telegram bot workflow orchestration with auto-reload development mode.

## Critical Rules

**⚠️ NEVER start bot without watchexec in development**

## Startup Procedure

### Development Mode (RECOMMENDED)

```bash
# Correct way - with auto-reload
/Users/terryli/.claude/automation/lychee/runtime/bot/run-bot-dev-watchexec.sh
```

**Features:**
- ✅ Auto-restarts on `.py` file changes (100ms debounce)
- ✅ Monitors: `bot/`, `lib/`, `orchestrator/` directories
- ✅ Graceful shutdown (SIGTERM → 5s timeout → SIGKILL)
- ✅ Respects `.gitignore` automatically

### Verification

Check if running correctly:

```bash
# Should show watchexec process
ps aux | grep watchexec | grep bot

# Should show bot process under watchexec
ps aux | grep multi-workspace-bot
```

### Common Mistakes

❌ **WRONG**: `doppler run --project claude-config --config dev -- uv run multi-workspace-bot.py`
- No auto-reload
- Manual restart required for code changes
- Easy to forget to restart

✅ **CORRECT**: Use `run-bot-dev-watchexec.sh` wrapper script

## Stopping the Bot

```bash
# Kill watchexec (will stop bot gracefully)
pkill watchexec

# Or kill bot directly (watchexec will restart it)
pkill -f multi-workspace-bot.py
```

## Production Mode

For production deployment (auto-start on login):

```bash
cd /Users/terryli/.claude/automation/lychee/runtime/bot

# Install launchd service
./bot-service.sh install

# Check status
./bot-service.sh status

# View logs
./bot-service.sh logs
```

## Troubleshooting

### Bot not auto-restarting on code changes

**Cause**: Not running under watchexec
**Fix**: Kill bot, restart with `run-bot-dev-watchexec.sh`

### PID file lock error

**Cause**: Previous bot process still running
**Fix**:
```bash
pkill -9 -f multi-workspace-bot.py
rm -f ~/.claude/automation/lychee/state/bot.pid
# Then restart with watchexec script
```

### Multiple bot instances

**Cause**: Started bot multiple times without watchexec
**Fix**:
```bash
# Kill all instances
pkill -9 watchexec
pkill -9 -f multi-workspace-bot.py
rm -f ~/.claude/automation/lychee/state/bot.pid

# Start fresh
/Users/terryli/.claude/automation/lychee/runtime/bot/run-bot-dev-watchexec.sh
```

## File Locations

- **Bot script**: `/Users/terryli/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py`
- **Dev wrapper**: `/Users/terryli/.claude/automation/lychee/runtime/bot/run-bot-dev-watchexec.sh`
- **Service manager**: `/Users/terryli/.claude/automation/lychee/runtime/bot/bot-service.sh`
- **PID file**: `/Users/terryli/.claude/automation/lychee/state/bot.pid`
- **Logs**: Check `ps` output or `/tmp/bot-watchexec*.log`

## References

- **Bot README**: `/Users/terryli/.claude/automation/lychee/runtime/bot/README.md`
- **CLAUDE.md Automation section**: Always start with watchexec wrapper
