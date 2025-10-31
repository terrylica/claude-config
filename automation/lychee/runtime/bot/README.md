# Multi-Workspace Telegram Bot

Workflow orchestration bot for Claude CLI sessions with progress streaming and full supervision.

## Features

- **Single-Message Progress Streaming**: One evolving Telegram message from workflow start to completion
- **Persistent Context**: Git branch, workspace, and file status visible throughout execution
- **Full Supervision Chain**: launchd → watchexec → bot (every layer monitored)
- **Auto-Reload**: Bot automatically restarts when code changes using **watchexec** 🦀
- **Auto-Start**: System-level daemon management via **launchd** (survives reboots)
- **Health Monitoring**: Crash detection, restart rate tracking, Telegram alerts

## Quick Start (Production Mode - Only Mode)

### Installation (One-Time Setup)

```bash
cd /Users/terryli/.claude/automation/lychee/runtime/bot
./bot-service.sh install
```

This installs the bot as a launchd service that:

- Starts automatically on login
- Runs continuously (survives reboots)
- Auto-restarts on crashes
- Auto-reloads on code changes

### Service Management

```bash
# Check status (shows full supervision chain)
./bot-service.sh status

# View logs (launchd + bot)
./bot-service.sh logs

# Restart (rarely needed, code changes auto-reload)
./bot-service.sh restart

# Temporarily stop
./bot-service.sh stop

# Resume after stop
./bot-service.sh start

# Remove completely
./bot-service.sh uninstall
```

### Shell Aliases (Recommended)

After sourcing `~/.claude/sage-aliases/aliases/bot-management.sh`:

```bash
bot status      # Show status
bot logs        # Tail logs
bot restart     # Restart service
bot stop        # Stop service
bot start       # Start service
bot-pids        # Show PIDs
bot-state-count # State directory stats
```

## Architecture

### Supervision Chain

```
launchd (macOS top supervisor)
  └─> run-bot-prod-watchexec.sh
      └─> watchexec (file watcher, auto-reload)
          └─> bot-wrapper-prod.sh (crash detection, alerts)
              └─> doppler run
                  └─> uv run
                      └─> python3 multi-workspace-bot.py
```

**Every layer is monitored and supervised.**

### Health Monitoring Layers

| Layer | Monitors | Alert Trigger | Action |
| --- | --- | --- | --- |
| **launchd** | watchexec crashes | 3+ crashes in 10s | Auto-restart watchexec |
| **watchexec** | Bot crashes | Process exits | Auto-restart bot |
| **bot-wrapper** | Crash loops | 5+ restarts in 60s | Telegram alert (critical) |
| **bot** | Internal errors | API failures, queue backlogs | Telegram alert (errors) |

## Key Features

### ✅ Auto-Reload on Code Changes

**No manual restart needed!**

1. Edit any `.py` file in `bot/`, `lib/`, or `orchestrator/`
2. Save the file
3. watchexec detects change (100ms debounce)
4. Bot automatically restarts (~2-3 seconds)
5. New code is loaded

**Watched Directories**:

- `/Users/terryli/.claude/automation/lychee/runtime/bot/*.py`
- `/Users/terryli/.claude/automation/lychee/runtime/lib/*.py`
- `/Users/terryli/.claude/automation/lychee/runtime/orchestrator/*.py`

### ✅ Full Supervision

**Survives Everything**:

- ✅ Reboots (launchd auto-start on login)
- ✅ Crashes (launchd auto-restart watchexec)
- ✅ Code changes (watchexec auto-reload bot)
- ✅ Hangs/freezes (process monitoring)

**Process Monitoring**:

- launchd ensures watchexec always runs
- watchexec ensures bot always runs
- bot-wrapper detects crash loops
- All failures generate Telegram alerts

### ✅ Health Monitoring

**Crash Detection**:

- Captures exit code
- Records last 20 lines of logs
- Includes stderr output
- Sends full context to Telegram

**Restart Rate Tracking**:

- Monitors restart frequency
- Alerts if 5+ restarts in 60 seconds
- Resets counter after 5 minutes of stability
- Prevents runaway restart loops

**Multi-Channel Alerts**:

- Telegram (primary): Crash/loop/error alerts
- System logs: launchd events
- Bot logs: Internal diagnostics

## Why watchexec? (Rust-based File Watcher)

### Comparison with Alternatives

| Tool | Language | .gitignore | Debouncing | Cross-Platform | Speed |
| --- | --- | --- | --- | --- | --- |
| **watchexec** | Rust | ✅ Auto | ✅ 50ms | ✅ Yes | ⚡ Very Fast |
| watchfiles | Rust+Py | ❌ Manual | ✅ Yes | ✅ Yes | ⚡ Fast |
| nodemon | Node.js | ❌ Manual | ✅ Yes | ✅ Yes | 🐌 Slower |
| entr | C | ❌ None | ❌ No | ⚠️ Unix only | ⚡ Fast |

### Why watchexec Won (2025 State-of-the-Art)

**Research findings** (via WebSearch):

- Built on Rust `notify` library (same foundation as `cargo-watch`)
- **Smart defaults**: No need to configure ignore patterns
- **Modern replacement** for `entr` (traditional Unix tool)
- Used by major Rust projects (Tauri, cargo-watch)
- Cross-platform (macOS, Linux, Windows)

**Source**: [TIL: Watchexec - Modern File Watching (2025)](https://tech.stonecharioteer.com/posts/2025/til-watchexec/)

## Why launchd? (macOS Native Supervisor)

**Native macOS system manager** (equivalent to Linux `systemd`):

- ✅ Process supervision (auto-restart on crashes)
- ✅ Resource limits (memory, CPU)
- ✅ Auto-start on login
- ✅ Environment variables
- ✅ Logging (stdout/stderr redirection)
- ✅ Crash throttling (prevents restart loops)

**vs. alternatives**:

- ❌ `cron`: No process supervision
- ❌ Manual scripts: No auto-restart
- ❌ Docker: Overkill for single service
- ✅ launchd: Native, lightweight, battle-tested

## Important Notes

### Code Changes Auto-Reload

No need to run `bot restart` after editing code. watchexec handles this automatically.

The only time you need manual restart:

- Changing environment variables
- Updating launchd plist
- Major architecture changes

### Always Running

The bot runs continuously. To stop it completely:

- Temporary: `bot stop` (launchd won't restart until you run `bot start`)
- Permanent: `bot uninstall` (removes launchd service)

### No Development Mode

As of v5.8.0, there is only production mode. It provides all features needed for both development and production use:

- Auto-reload for rapid iteration (development need)
- Full supervision for reliability (production need)
- Crash detection for debugging (development need)
- Always-on operation for workflows (production need)

**Archived**: Development mode files moved to `archive/v5.8.0-development-mode/`

### Process Tree is Normal

When you run `bot status`, you'll see multiple PIDs:

```
launchd (PID 1)
  └─> run-bot-prod-watchexec.sh (PID from launchctl)
      └─> watchexec (PID XXXXX)
          └─> bot-wrapper-prod.sh (PID XXXXX)
              └─> doppler (PID XXXXX)
                  └─> uv (PID XXXXX)
                      └─> python3 (PID XXXXX)
```

**This is normal!** It's a parent→child process chain, not multiple instances.

### Logs

**Launchd logs**:

- `~/.claude/automation/lychee/logs/telegram-bot-launchd.log`
- `~/.claude/automation/lychee/logs/telegram-bot-launchd-error.log`

**Bot logs**:

- `~/.claude/automation/lychee/logs/telegram-handler.log`

**View all logs**: `bot logs` (tails all log files)

## Troubleshooting

### Bot Not Starting

```bash
# Check service status
bot status

# Check launchd logs
tail -50 ~/.claude/automation/lychee/logs/telegram-bot-launchd.log

# Check bot logs
tail -50 ~/.claude/automation/lychee/logs/telegram-handler.log

# Reinstall
bot uninstall
bot install
```

### Crash Loop Detected

If you receive "CRITICAL: Crash Loop Detected" alert:

1. Check Telegram alert for error context
2. Review logs: `bot logs`
3. Fix the issue in code
4. Save file (watchexec auto-reloads)
5. Restart counter resets after 5 min stability

### Code Changes Not Reloading

```bash
# Verify watchexec is running
bot status  # Should show watchexec process

# Check which files are watched
ps aux | grep watchexec  # Should show --watch paths

# Manual restart
bot restart
```

## Version History

- **v5.8.0** (2025-10-30): Remove development mode, production-only
- **v5.7.0** (2025-10-30): Add launchd + watchexec full supervision
- **v5.6.0** (2025-10-30): Add bot-dev.sh lifecycle management (archived)
- **v5.5.3** (2025-10-30): Disable idle timeout for dev mode
- **v5.5.0** (2025-10-30): Remove hook-based bot starting
- **v4.0.0** (2024): Add SessionSummary + workflow menu (replaced v3 error-only)

See [CHANGELOG.md](../../CHANGELOG.md) for full history.
