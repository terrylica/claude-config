# Multi-Workspace Telegram Bot

Workflow orchestration bot for Claude CLI sessions with progress streaming.

## Features

- **Single-Message Progress Streaming**: One evolving Telegram message from workflow start to completion
- **Persistent Context**: Git branch, workspace, and file status visible throughout execution
- **Auto-Reload (Development)**: Bot automatically restarts when code changes

## Running the Bot

### Development Mode (Auto-Reload) ⭐ **RECOMMENDED**

```bash
cd /Users/terryli/.claude/automation/lychee/runtime/bot
./run-bot-dev.sh
```

**What it does**:

- Watches `bot/`, `lib/`, and `orchestrator/` directories for `.py` file changes
- Automatically restarts bot when you save code changes
- Shows startup logs and errors in terminal
- **No more forgetting to restart!**

### Production Mode (Manual Restart)

```bash
cd /Users/terryli/.claude/automation/lychee/runtime/bot
./run-bot-prod.sh
```

**What it does**:

- Runs bot without auto-reload
- For production/stable environments
- Requires manual restart after code changes

### Background Mode (Old Method)

```bash
nohup doppler run --project claude-config --config dev -- \
  /Users/terryli/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py \
  > /tmp/telegram-bot.log 2>&1 &
```

**Drawbacks**:

- No auto-reload
- Must manually kill and restart
- Logs hidden in `/tmp/telegram-bot.log`

## Industry Best Practices

### Development vs Production

| Environment     | Auto-Reload | Tool                   | When to Use                        |
| --------------- | ----------- | ---------------------- | ---------------------------------- |
| **Development** | ✅ Enabled  | `nodemon`              | Your local machine, active coding  |
| **Production**  | ❌ Disabled | `systemd`/`supervisor` | Server deployment, stable releases |

### Why Auto-Reload in Development?

**Standard practice** used by:

- Flask (`flask run --debug`)
- FastAPI (`uvicorn --reload`)
- Django (`python manage.py runserver`)
- Next.js (`next dev`)

**Benefits**:

- Instant feedback on code changes
- No manual restart needed
- Faster development iteration
- Prevents forgetting to restart

### Why NO Auto-Reload in Production?

**Industry consensus**:

- Controlled deployments only
- No surprise restarts
- Rollback capability
- Monitoring and alerting

## Message Format Example

```
⏳ Workflow: 💾 Commit Changes

Workspace: lychee
Branch: main
Git: 3 modified, 2 staged

Stage: executing
Progress: 40%
Status: Running git diff...
```

All context persists throughout workflow lifecycle—no more losing branch/file info on progress updates!

## Auto-Reload Architecture

```
┌─────────────┐
│  nodemon    │ ← Watches *.py files
└──────┬──────┘
       │ Detects change
       ↓
┌─────────────┐
│ Kill bot    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Restart bot │ ← New code loaded
└─────────────┘
```

**Files watched**:

- `/Users/terryli/.claude/automation/lychee/runtime/bot/*.py`
- `/Users/terryli/.claude/automation/lychee/runtime/lib/*.py`
- `/Users/terryli/.claude/automation/lychee/runtime/orchestrator/*.py`

## Troubleshooting

### Auto-Reload Not Working

1. **Check nodemon installed**:

   ```bash
   which nodemon
   ```

2. **Install if missing**:

   ```bash
   npm install -g nodemon
   ```

3. **Test manually**:
   ```bash
   nodemon --version
   ```

### Bot Not Restarting

- Kill old instances:

  ```bash
  pkill -f multi-workspace-bot.py
  ```

- Check for errors:
  ```bash
  ./run-bot-dev.sh
  # Watch terminal output
  ```

### Want to Use watchfiles Instead?

Alternative Python-native tool (no Node.js dependency):

```bash
# Install
pip install watchfiles  # or: pipx install watchfiles

# Run
watchfiles --filter python \
  'doppler run --project claude-config --config dev -- python multi-workspace-bot.py' \
  .
```

## Related Files

- `/Users/terryli/.claude/specifications/telegram-single-message-progress-streaming.yaml` - SSoT plan
- `/Users/terryli/.claude/automation/lychee/runtime/orchestrator/multi-workspace-orchestrator.py` - Workflow executor
- `/Users/terryli/.claude/automation/lychee/state/workflows.json` - Workflow registry

## Version

Current: v4.0.0 (single-message streaming + persistent context)
