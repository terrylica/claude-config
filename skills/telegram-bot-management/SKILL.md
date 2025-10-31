---
name: telegram-bot-management
description: Telegram bot production management, monitoring, and troubleshooting. Use when user mentions telegram bot, lychee automation, bot status, bot restart, or bot monitoring.
---

# Telegram Bot Management

Multi-workspace Telegram bot workflow orchestration with full supervision (launchd + watchexec).

## Critical Rules

**Production Mode Only** - As of v5.8.0, there is only one way to run the bot.

## Bot Management Commands

### Check Status

```bash
bot-service.sh status
# Or use alias
bot status
```

Shows:
- launchd supervision status
- watchexec process (PID, uptime, memory)
- Bot process (PID, uptime, memory)
- Full process tree
- Recent log activity

### View Logs

```bash
bot-service.sh logs
# Or use alias
bot logs
```

Tails all logs:
- Launchd logs (supervision layer)
- Bot logs (application layer)

### Restart Bot

```bash
bot-service.sh restart
# Or use alias
bot restart
```

**Rarely needed** - Code changes auto-reload via watchexec!

### Stop Bot

```bash
bot-service.sh stop
# Or use alias
bot stop
```

Temporarily stops the bot. Use `bot start` to resume.

### Start Bot

```bash
bot-service.sh start
# Or use alias
bot start
```

Resumes bot after temporary stop.

## Installation (One-Time)

```bash
cd /Users/terryli/.claude/automation/lychee/runtime/bot
./bot-service.sh install
```

This:
- Installs launchd service
- Auto-starts on login
- Auto-restarts on crashes
- Auto-reloads on code changes

## Architecture

```
launchd (macOS top supervisor)
  └─> run-bot-prod-watchexec.sh
      └─> watchexec (file watcher, auto-reload)
          └─> bot-wrapper-prod.sh (crash detection)
              └─> doppler run
                  └─> uv run
                      └─> python3 multi-workspace-bot.py
```

**Every layer is monitored and supervised.**

## Auto-Reload Feature

**Code changes trigger automatic reload:**

1. Edit `.py` file in `bot/`, `lib/`, or `orchestrator/`
2. Save file
3. watchexec detects change (100ms debounce)
4. Bot restarts automatically (~2-3 seconds)
5. New code is loaded

**No manual restart needed!**

## Health Monitoring

### Layer 1: launchd
- Monitors: watchexec crashes
- Action: Auto-restart watchexec
- Alerts: System logs

### Layer 2: watchexec
- Monitors: Bot crashes
- Action: Auto-restart bot
- Alerts: Automatic (no intervention needed)

### Layer 3: bot-wrapper-prod
- Monitors: Crash loops (5+ restarts/60s)
- Action: Telegram alert with full context
- Alerts: Telegram (critical)

### Layer 4: bot
- Monitors: Internal errors
- Action: Telegram alert
- Alerts: Telegram (errors)

## Troubleshooting

### Bot Not Running

```bash
# Check status
bot status

# If not running, check launchd
launchctl list | grep telegram-bot

# Reinstall if needed
bot uninstall
bot install
```

### Crash Loop Alert

If you receive "CRITICAL: Crash Loop Detected" in Telegram:

1. Check Telegram alert for error context
2. Review logs: `bot logs`
3. Fix the issue in code
4. Save file (auto-reloads)
5. Restart counter resets after 5 min stability

### Code Changes Not Reloading

```bash
# Verify watchexec is running
bot status  # Should show watchexec process

# Check watched directories
ps aux | grep watchexec  # Should show --watch paths

# Manual restart if needed
bot restart
```

### Multiple PIDs Normal

When you run `bot status`, you'll see 6-7 PIDs:

```
launchd (PID 1)
  └─> run-bot-prod-watchexec.sh (PID XXXXX)
      └─> watchexec (PID XXXXX)
          └─> bot-wrapper-prod.sh (PID XXXXX)
              └─> doppler (PID XXXXX)
                  └─> uv (PID XXXXX)
                      └─> python3 (PID XXXXX)
```

**This is NORMAL!** It's a parent→child process chain, not multiple instances.

### PID File Errors

```bash
# Clean stale PID files
rm -f ~/.claude/automation/lychee/state/bot.pid
rm -f ~/.claude/automation/lychee/state/watchexec.pid

# Restart bot
bot restart
```

## File Locations

- **Bot script**: `/Users/terryli/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py`
- **Service manager**: `/Users/terryli/.claude/automation/lychee/runtime/bot/bot-service.sh`
- **Production runner**: `/Users/terryli/.claude/automation/lychee/runtime/bot/run-bot-prod-watchexec.sh`
- **Crash monitor**: `/Users/terryli/.claude/automation/lychee/runtime/bot/bot-wrapper-prod.sh`
- **PID files**: `/Users/terryli/.claude/automation/lychee/state/{watchexec,bot}.pid`
- **Launchd logs**: `~/.claude/automation/lychee/logs/telegram-bot-launchd*.log`
- **Bot logs**: `~/.claude/automation/lychee/logs/telegram-handler.log`

## Shell Aliases

After sourcing `~/.claude/sage-aliases/aliases/bot-management.sh`:

```bash
bot status          # Show status
bot logs            # Tail logs
bot restart         # Restart service
bot stop            # Stop service
bot start           # Start service
bot-pids            # Show PIDs
bot-state-count     # State directory stats
bot-logs-errors     # Show recent errors
```

## References

- **Bot README**: `/Users/terryli/.claude/automation/lychee/runtime/bot/README.md`
- **CHANGELOG**: `/Users/terryli/.claude/automation/lychee/CHANGELOG.md`
- **CLAUDE.md**: Always use production mode (launchd + watchexec)

## Version History

- **v5.8.0** (2025-10-30): Production-only mode
- **v5.7.0** (2025-10-30): Full supervision (launchd + watchexec)
- **v5.6.0** (2025-10-30): Dev lifecycle management (archived)

## Important Notes

**No Development Mode** - As of v5.8.0, production mode provides all features:
- Auto-reload for rapid iteration (dev need)
- Full supervision for reliability (prod need)
- Crash detection for debugging (dev need)
- Always-on operation (prod need)

**Always Running** - The bot runs continuously. To stop completely:
- Temporary: `bot stop`
- Permanent: `bot uninstall`
