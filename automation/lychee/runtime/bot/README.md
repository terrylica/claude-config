# Multi-Workspace Telegram Bot

Workflow orchestration bot for Claude CLI sessions with progress streaming.

## Features

- **Single-Message Progress Streaming**: One evolving Telegram message from workflow start to completion
- **Persistent Context**: Git branch, workspace, and file status visible throughout execution
- **Auto-Reload (Development)**: Bot automatically restarts when code changes using **watchexec** 🦀
- **Auto-Start (Production)**: System-level daemon management via **launchd**

## Quick Start

### Development Mode ⭐ **RECOMMENDED**

```bash
cd /Users/terryli/.claude/automation/lychee/runtime/bot
./run-bot-dev-watchexec.sh
```

**Features**:

- ✅ Auto-restarts on `.py` file changes
- ✅ Rust-based watchexec (faster than nodemon)
- ✅ Respects `.gitignore` automatically
- ✅ Built-in debouncing (100ms)
- ✅ Graceful restarts (SIGTERM → SIGKILL)

### Production Mode (launchd Service)

Install as system service:

```bash
cd /Users/terryli/.claude/automation/lychee/runtime/bot
./bot-service.sh install
```

**Features**:

- ✅ Auto-starts on login
- ✅ Auto-restarts on crashes (10s throttle)
- ✅ Native macOS daemon manager
- ✅ Logs to `/tmp/telegram-bot.log`

**Service Management**:

```bash
# Check status
./bot-service.sh status

# View logs
./bot-service.sh logs

# Restart after code changes
./bot-service.sh restart

# Stop service
./bot-service.sh stop

# Uninstall service
./bot-service.sh uninstall
```

## Why watchexec? (Rust-based File Watcher)

### Comparison with Alternatives

| Tool          | Language | .gitignore | Debouncing | Cross-Platform | Speed        |
| ------------- | -------- | ---------- | ---------- | -------------- | ------------ |
| **watchexec** | Rust     | ✅ Auto    | ✅ 50ms    | ✅ Yes         | ⚡ Very Fast |
| watchfiles    | Rust+Py  | ❌ Manual  | ✅ Yes     | ✅ Yes         | ⚡ Fast      |
| nodemon       | Node.js  | ❌ Manual  | ✅ Yes     | ✅ Yes         | 🐌 Slower    |
| entr          | C        | ❌ None    | ❌ No      | ⚠️ Unix only   | ⚡ Fast      |

### Why watchexec Won (2025 State-of-the-Art)

**Research findings** (via WebSearch):

- Built on Rust `notify` library (same foundation as `cargo-watch`)
- **Smart defaults**: No need to configure ignore patterns
- **Modern replacement** for `entr` (traditional Unix tool)
- Used by major Rust projects (Tauri, cargo-watch)
- Cross-platform (macOS, Linux, Windows)

**Source**: [TIL: Watchexec - Modern File Watching (2025)](https://tech.stonecharioteer.com/posts/2025/til-watchexec/)

## Auto-Reload Architecture

```
┌─────────────┐
│  watchexec  │ ← Watches bot/, lib/, orchestrator/ for *.py
└──────┬──────┘
       │ File change detected (100ms debounce)
       ↓
┌─────────────┐
│ SIGTERM     │ → Graceful shutdown (5s timeout)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Restart bot │ ← New code loaded instantly
└─────────────┘
```

**Watched directories**:

- `/Users/terryli/.claude/automation/lychee/runtime/bot/*.py`
- `/Users/terryli/.claude/automation/lychee/runtime/lib/*.py`
- `/Users/terryli/.claude/automation/lychee/runtime/orchestrator/*.py`

## Production Deployment (launchd)

### Why launchd?

**Native macOS system manager** (equivalent to Linux `systemd`):

- ✅ Process supervision (auto-restart on crashes)
- ✅ Resource limits (memory, CPU)
- ✅ Logging (stdout/stderr)
- ✅ Environment variables
- ✅ Boot-time startup
- ✅ Crash throttling (prevents restart loops)

### Service Configuration

Location: `com.terryli.telegram-bot.plist`

**Key features**:

- **KeepAlive**: Restarts on crashes
- **ThrottleInterval**: 10s between restarts (prevents loops)
- **SoftResourceLimits**: Max 1GB memory
- **ExitTimeOut**: 5s graceful shutdown

### Manual Control (without service)

```bash
# Background with logs
nohup doppler run --project claude-config --config dev -- \
  uv run multi-workspace-bot.py \
  > /tmp/telegram-bot.log 2>&1 &

# Stop
pkill -f multi-workspace-bot.py
```

## Message Format Example

```
⏳ Workflow: 💾 Commit Changes

Repository: ~/.claude
Directory: automation/lychee/runtime/bot
Branch: main
Git: M:3 S:2

Stage: executing
Progress: 40%
Status: Running git diff...
```

**Git Status Format** (compact):

- `M:3` - 3 modified files
- `S:2` - 2 staged files
- `U:1` - 1 untracked file
- `clean` - No changes

All context persists throughout workflow lifecycle!

## Troubleshooting

### Auto-Reload Not Working

1. **Check watchexec installed**:

   ```bash
   which watchexec  # Should be /opt/homebrew/bin/watchexec
   ```

1. **Install if missing**:

   ```bash
   brew install watchexec
   ```

1. **Test version**:

   ```bash
   watchexec --version  # Should be 2.3.2+
   ```

### Service Not Starting

1. **Check service status**:

   ```bash
   ./bot-service.sh status
   ```

1. **View error logs**:

   ```bash
   cat /tmp/telegram-bot-error.log
   ```

1. **Verify doppler config**:

   ```bash
   doppler run --project claude-config --config dev -- env | grep TOKEN
   ```

### Bot Process Stuck

Kill all instances:

```bash
pkill -f "watchexec.*multi-workspace-bot"
pkill -f "multi-workspace-bot.py"
```

Restart clean:

```bash
./run-bot-dev-watchexec.sh
```

## Development Workflow

### Making Code Changes

1. **Edit files** in `bot/`, `lib/`, or `orchestrator/`
1. **Save** - watchexec detects change automatically
1. **Wait 100ms** - debouncing period
1. **Bot restarts** - new code loaded (takes ~2-3s)
1. **Test** - send Telegram message to verify

**No manual restart needed!** ⚡

### Testing Changes

```bash
# Start dev server
./run-bot-dev-watchexec.sh

# In another terminal, watch logs
tail -f /tmp/telegram-bot-dev-watchexec.log

# Make changes, save, watch auto-reload happen
```

## Installation

### Prerequisites

```bash
# Install watchexec (Rust-based file watcher)
brew install watchexec

# Install doppler (secrets management)
brew install dopplerhq/cli/doppler

# Install uv (Python package manager)
brew install uv

# Configure doppler
doppler login
doppler setup --project claude-config --config dev
```

### First Run

```bash
# Development (recommended for local testing)
./run-bot-dev-watchexec.sh

# Production (install as service)
./bot-service.sh install
./bot-service.sh status
```

## File Structure

```
bot/
├── multi-workspace-bot.py           # Main bot implementation
├── run-bot-dev-watchexec.sh         # Development runner (watchexec)
├── run-bot-dev.sh                   # Legacy dev runner (nodemon)
├── run-bot-prod.sh                  # Simple production runner
├── bot-service.sh                   # launchd service manager
├── com.terryli.telegram-bot.plist   # launchd configuration
└── README.md                        # This file

../lib/
├── calculate_workflows.py           # Workflow computation
├── ulid_gen.py                      # ULID generation
└── ...

../orchestrator/
└── multi-workspace-orchestrator.py  # Workflow execution engine
```

## Related Files

- `/Users/terryli/.claude/specifications/telegram-single-message-progress-streaming.yaml` - SSoT plan
- `/Users/terryli/.claude/automation/lychee/state/workflows.json` - Workflow registry
- `/Users/terryli/.claude/automation/lychee/runtime/hook/check-links-hybrid.sh` - SessionSummary generator

## Version

Current: v4.1.0 (watchexec auto-reload + launchd production setup)

## Industry Best Practices

### Development vs Production

| Environment     | Auto-Reload | Tool      | When to Use                        |
| --------------- | ----------- | --------- | ---------------------------------- |
| **Development** | ✅ Enabled  | watchexec | Your local machine, active coding  |
| **Production**  | ❌ Disabled | launchd   | Always-on service, stable releases |

### Why Auto-Reload in Development?

**Standard practice** used by:

- FastAPI: `uvicorn --reload`
- Flask: `flask run --debug`
- Django: `python manage.py runserver`
- Next.js: `next dev`
- Rust: `cargo-watch`

**Benefits**:

- ⚡ Instant feedback on code changes
- 🔄 No manual restart needed
- 🚀 Faster development iteration
- 🧠 Prevents forgetting to restart

### Why NO Auto-Reload in Production?

**Industry consensus**:

- 🎯 Controlled deployments only
- ⚠️ No surprise restarts
- ↩️ Rollback capability
- 📊 Monitoring and alerting
- 🔒 Stability over convenience
