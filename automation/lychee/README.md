# Lychee Link Validation Automation

**Version**: 3.0.1
**Status**: Operational
**Specification (SSoT)**: `/Users/terryli/.claude/specifications/multi-workspace-link-validation-v3.yaml`
**Architecture**: Polling-based (v3.0.0), on-demand with idle timeout

## System Overview

Automated link validation and auto-fixing with Telegram-based approval workflows. Polling architecture replaces webhook infrastructure for simplified deployment.

**Bot Mode**: On-demand polling with 10-minute idle shutdown
**Correlation**: ULID-based distributed tracing across hook → bot → orchestrator
**Storage**: SQLite event store for full workflow observability
**Processes**: 1 bot + N orchestrators (spawned on approval)

## Complete Workflow

### Phase 1: Detection & Notification

1. User stops Claude Code session
1. Stop hook runs lychee link validation
1. If broken links found: hook emits notification file
1. Bot detects notification → sends Telegram message with workspace emoji

### Phase 2: User Approval

1. User receives Telegram notification with action buttons
1. User clicks **"✅ Auto-Fix All"** or **"❌ Reject"**
1. Bot writes approval file to state directory

### Phase 3: Claude CLI Execution

1. Orchestrator detects approval file
1. Validates workspace path (security check)
1. Invokes Claude CLI in background with 5-minute timeout
1. Captures stdout, stderr, exit code, duration

### Phase 4: Completion Notification ✨ NEW in v2.1.0

1. Orchestrator emits completion file with execution results
1. Bot detects completion → sends Telegram message with outcome
1. User receives feedback: **✅ Success** / **❌ Error** / **⏱️ Timeout**

## Directory Structure

```
automation/lychee/
├── runtime/              # Active system components
│   ├── bot/             # multi-workspace-bot.py (Telegram handler)
│   ├── orchestrator/    # multi-workspace-orchestrator.py (Claude CLI invoker)
│   ├── hook/            # check-links-hybrid.sh (session stop hook)
│   └── lib/             # workspace_helpers.py (shared utilities)
├── setup/                # One-time configuration scripts
│   ├── auth/            # auth-telegram*.py (Telegram authentication)
│   ├── bot/             # create-bot-automated.py (bot creation)
│   └── registry/        # register-workspace.py (workspace registration)
├── config/               # Configuration files
│   ├── launchd/         # macOS background service plists
│   └── zellij/          # zellij-session-snapshot.kdl (terminal session)
├── testing/              # Development & testing tools
│   ├── test-notification-emit.py
│   ├── test-notification-consume.py
│   └── test-approval-emit.py
├── docs/                 # Documentation
│   ├── DOPPLER_SECRETS.md
│   ├── DEPLOYMENT.md
│   ├── QUICK_START.md
│   ├── DIAGNOSIS_AND_REDESIGN.md
│   └── COMPLETE_WORKFLOW.md
├── state/                # Runtime state
│   ├── events.db        # SQLite event store (correlation tracking)
│   ├── callbacks/       # Telegram button callback mapping
│   ├── notifications/   # Hook → Bot notification files
│   ├── approvals/       # Bot → Orchestrator approval files
│   ├── completions/     # Orchestrator → Bot completion files
│   └── registry.json    # Workspace configuration
├── archive/              # Historical artifacts
│   ├── planning/        # Legacy planning docs
│   ├── reports/         # Analysis reports
│   ├── migrations/      # Version migration docs
│   └── deprecated-code/ # Removed code (webhook infrastructure)
└── README.md             # This file
```

## State Files

**Location**: `$HOME/.claude/automation/lychee/state/`

| File/Directory   | Purpose                      | Pattern                                         | Retention |
| ---------------- | ---------------------------- | ----------------------------------------------- | --------- |
| `events.db`      | Event correlation store      | SQLite database with session_events table       | ∞         |
| `notifications/` | Hook → Bot requests          | `notify_{session_id}_{workspace_hash}.json`     | Consumed  |
| `approvals/`     | Bot → Orchestrator decisions | `approval_{session_id}_{workspace_hash}.json`   | Consumed  |
| `completions/`   | Orchestrator → Bot results   | `completion_{session_id}_{workspace_hash}.json` | Consumed  |
| `callbacks/`     | Telegram button callbacks    | `cb_{hash8}.json`                               | 30 days   |
| `registry.json`  | Workspace metadata           | JSON with emoji + path mapping                  | ∞         |

## Components

### Stop Hook

**File**: `runtime/hook/check-links-hybrid.sh`
**Trigger**: Claude Code session stop event
**Output**: Notification file if broken links found

### Telegram Bot

**File**: `runtime/bot/multi-workspace-bot.py`
**Process**: Background launchd service
**Watches**:

- `/tmp/lychee_state/notifications/` → Send Telegram notification
- `/tmp/lychee_state/completions/` → Send completion message

**Handles**:

- Button callbacks → Write approval files

### Orchestrator

**File**: `runtime/orchestrator/multi-workspace-orchestrator.py`
**Process**: Background launchd service
**Watches**:

- `/tmp/lychee_state/approvals/` → Invoke Claude CLI

**Captures**:

- stdout, stderr, exit_code, duration
- Emits completion notification

## Observability

### Logs

```bash
# Bot activity
tail -f ~/.claude/logs/telegram-handler.log

# Orchestrator activity
tail -f ~/.claude/logs/orchestrator.log
```

**Log Format**: Emoji-prefixed structured logging

- 🔄 = Processing started
- ✓ = Step completed
- 📊 = Metrics/statistics
- 📤 = Output emitted
- ❌ = Error occurred

### State Inspection

```bash
# View pending notifications
ls /tmp/lychee_state/notifications/

# View pending approvals
ls /tmp/lychee_state/approvals/

# View completions
ls /tmp/lychee_state/completions/

# Show workspace registry
cat /tmp/lychee_state/registry.json | jq

# Watch for new state files
watch -n 1 'ls -lt /tmp/lychee_state/*/*.json | head -20'
```

### Service Status

```bash
# Check if services are running
launchctl list | grep lychee

# Expected output:
# XXXXX  0  com.user.lychee.telegram-handler
# XXXXX  0  com.user.lychee.orchestrator

# Restart services
launchctl stop com.user.lychee.telegram-handler
launchctl stop com.user.lychee.orchestrator
launchctl start com.user.lychee.telegram-handler
launchctl start com.user.lychee.orchestrator
```

## Completion Notification Formats

### Success

```
🔗 ✅ Auto-Fix Completed

Workspace: lychee-autofix
Session: test-20251024-195117
Duration: 21.7s

Summary:
Fixed 3 broken fragment links in CLAUDE.md

Details:
[Full Claude CLI output]
```

### Error

```
🔗 ❌ Auto-Fix Failed

Workspace: lychee-autofix
Session: test-20251024-195117
Duration: 12.3s | Exit Code: 1

Summary:
Error: Could not read /tmp/claude_lychee_full.txt

Error:
[Full error message]
```

### Timeout

```
🔗 ⏱️ Auto-Fix Timeout

Workspace: lychee-autofix
Session: test-20251024-195117
Duration: 300.0s (limit reached)

Summary:
Claude CLI exceeded 5-minute timeout
```

## Workspace Management

### Register New Workspace

```bash
# Add workspace to registry
/Users/terryli/.claude/automation/lychee/setup/registry/register-workspace.py

# Follow prompts to provide:
# - Workspace path
# - Workspace ID (alphanumeric + hyphens)
# - Emoji for visual identification
```

### Workspace Registry Schema

```json
{
  "version": "2.0.0",
  "workspaces": {
    "lychee-autofix": {
      "emoji": "🔗",
      "path": "/Users/terryli/.claude",
      "name": ".claude"
    },
    "project-a": {
      "emoji": "📊",
      "path": "/Users/terryli/projects/project-a",
      "name": "proj-a"
    }
  }
}
```

## Testing

### Manual Test Flow

1. **Emit test notification**:

   ```bash
   /Users/terryli/.claude/automation/lychee/testing/test-notification-emit.py
   ```

1. **Check Telegram** for notification message

1. **Click button** in Telegram

1. **Watch logs** for Claude CLI execution:

   ```bash
   tail -f ~/.claude/logs/orchestrator.log
   ```

1. **Check Telegram** for completion message

### Test Scenarios

**POC Validation** (in `/tmp/lychee_poc/`):

```bash
/tmp/lychee_poc/test_all_scenarios.sh
```

Demonstrates all 3 completion message formats.

## Deployment

### Background Services (launchd)

**Bot**: `config/launchd/com.user.lychee.telegram-handler.plist`
**Orchestrator**: `config/launchd/com.user.lychee.orchestrator.plist`

```bash
# Load services
launchctl load ~/Library/LaunchAgents/com.user.lychee.telegram-handler.plist
launchctl load ~/Library/LaunchAgents/com.user.lychee.orchestrator.plist
```

### Environment Variables (Doppler)

**Project**: `claude-config`
**Config**: `dev`

Required secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

See: `docs/DOPPLER_SECRETS.md`

## Dependencies

**Python** (via uv):

- `python-telegram-bot>=21.0` (Telegram bot API)
- `watchfiles>=1.0.0` (File system monitoring, Rust-backed)
- `jsonschema>=4.0.0` (State file validation)

**System**:

- `lychee` (Homebrew: `brew install lychee`)
- `doppler` (Doppler CLI for secrets)

## Version History

### v2.1.0 (2025-10-24) - Current

**New Features**:

- ✅ Completion notifications after Claude CLI execution
- ✅ Detailed emoji-prefixed logging
- ✅ Line-by-line execution tracing
- ✅ Full stdout/stderr capture

**Files Modified**:

- `runtime/bot/multi-workspace-bot.py` (added CompletionHandler)
- `runtime/orchestrator/multi-workspace-orchestrator.py` (added output capture)

**Backward Compatibility**: Full

### v2.0.0 (2025-10-24)

**Breaking Changes**:

- Multi-workspace architecture (no backward compatibility)
- New file structure (`/tmp/lychee_state/`)
- Removed single-workspace components

### v0.1.1

Detection-only (deprecated), see `specifications/lychee-link-validation.yaml`

## Troubleshooting

### No Telegram Messages

1. Check bot process: `launchctl list | grep telegram-handler`
1. Check bot log: `tail -f ~/.claude/logs/telegram-handler.log`
1. Verify Doppler secrets: `doppler secrets -p claude-config -c dev`

### Claude CLI Not Running

1. Check orchestrator process: `launchctl list | grep orchestrator`
1. Check orchestrator log: `tail -f ~/.claude/logs/orchestrator.log`
1. Check approval files exist: `ls /tmp/lychee_state/approvals/`

### No Completion Messages

1. Check completions directory: `ls /tmp/lychee_state/completions/`
1. Check bot log for completion processing
1. Verify bot is watching completions directory (should see in startup logs)

### State Files Not Cleaning Up

State files have 5-minute TTL and auto-cleanup runs every 60 seconds.
Manual cleanup: `rm /tmp/lychee_state/*/*.json`

## References

- **Specification**: `/Users/terryli/.claude/specifications/multi-workspace-link-validation.yaml`
- **Workflow Diagram**: `docs/COMPLETE_WORKFLOW.md`
- **Migration Notes**: `docs/MIGRATION_v2.0_to_v2.1.md`
- **POC**: `/tmp/lychee_poc/` (reference implementation)
- **Lychee docs**: https://lychee.cli.rs/
- **Claude Code hooks**: https://docs.claude.com/en/docs/claude-code/hooks
