# Lychee Multi-Workspace Link Validation - Complete Workflow

**Version**: 3.0.1
**Status**: Fully Operational
**Last Updated**: 2025-10-25
**Architecture**: Polling-based with on-demand bot lifecycle

## Overview

Complete end-to-end workflow documentation showing all 4 phases of the multi-workspace link validation system with completion notifications.

**Key Design Decisions**:

- **On-Demand Bot**: Bot only starts when errors detected, auto-shuts down after 10 minutes idle
- **SQLite Correlation**: All events tracked in `events.db` with ULID correlation IDs
- **Fail-Fast**: No silent failures, all errors propagate and are logged

______________________________________________________________________

## Bot Lifecycle (v3.0.0 Polling Architecture)

**Design**: On-demand activation with idle timeout

### Lifecycle States

```
┌─────────────────────────────────────────────────────┐
│ State 1: Bot Stopped                                │
│ - No process running                                │
│ - Hook detects errors → Starts bot                 │
│ - Hook detects no errors → Bot remains stopped     │
└─────────────────────────────────────────────────────┘
                    ↓ (errors > 0)
┌─────────────────────────────────────────────────────┐
│ State 2: Bot Active                                 │
│ - Processing notifications/approvals/completions    │
│ - Polling Telegram for button clicks               │
│ - SQLite event logging                             │
│ - Idle timer: 10 minutes                           │
└─────────────────────────────────────────────────────┘
                    ↓ (idle timeout)
┌─────────────────────────────────────────────────────┐
│ State 3: Bot Shutdown                               │
│ - Logs `bot.shutdown` event to SQLite              │
│ - Returns to State 1                               │
└─────────────────────────────────────────────────────┘
```

**Rationale**: Polling architecture (v3.0.0) eliminates webhook infrastructure complexity. Bot runs only when needed, reducing resource usage.

**Observability**: Check SQLite for bot lifecycle events:

```bash
sqlite3 state/events.db "SELECT event_type, timestamp FROM session_events WHERE component='bot' ORDER BY timestamp DESC LIMIT 10;"
```

______________________________________________________________________

## Phase 1: Detection & Initial Notification ✅

**Status**: Operational
**Components**: Stop Hook → Notification File → Bot → Telegram

### Flow

```
[User stops Claude Code session]
         ↓
┌─────────────────────────┐
│  Stop Hook              │
│  check-links-hybrid.sh  │
└─────────────────────────┘
         ↓
[Run lychee on all .md files (background process)]
[Check results: Found 3 broken links]
         ↓
[IF errors > 0: Start bot if not running]  ← NEW in v3.0.0
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  IF errors > 0:                                                 │
│  Write notification file:                                       │
│  /tmp/lychee_state/notifications/notify_{session}_{hash}.json  │
│                                                                 │
│  Content:                                                       │
│  {                                                              │
│    "workspace_path": "/Users/terryli/.claude",                 │
│    "session_id": "abc-123",                                    │
│    "error_count": 3,                                           │
│    "details": "Found 3 broken links",                          │
│    "timestamp": "2025-10-24T19:00:00Z"                         │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
         ↓
[File appears in filesystem]
         ↓
┌─────────────────────────┐
│  Bot Process            │
│  (watchfiles library)   │
│  Watching:              │
│  /tmp/lychee_state/     │
│    notifications/       │
└─────────────────────────┘
         ↓
[Detects: notify_abc-123_81e622b5.json]
[Reads file content]
[Loads workspace registry: emoji=🔗, name=.claude]
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Bot sends Telegram message:                                │
│                                                             │
│  🔗 **Link Validation** - .claude                           │
│                                                             │
│  **Workspace**: `/Users/terryli/.claude`                    │
│  **Session**: `abc-123`                                     │
│                                                             │
│  Found 3 broken link(s) in workspace                        │
│                                                             │
│  Choose action:                                             │
│  [✅ Auto-Fix All]  [❌ Reject]                             │
│                                                             │
│  (Buttons have callback_data: cb_a1b2c3d4)                  │
└─────────────────────────────────────────────────────────────┘
         ↓
[Deletes consumed notification file]
```

______________________________________________________________________

## Phase 2: User Decision & Approval ✅

**Status**: Operational
**Components**: User → Telegram → Bot → Approval File

### Flow

```
[User opens Telegram, sees message]
         ↓
[User clicks: ✅ Auto-Fix All]
         ↓
┌─────────────────────────┐
│  Telegram Server        │
│  Sends callback to Bot  │
└─────────────────────────┘
         ↓
[callback_query with data: "cb_a1b2c3d4"]
         ↓
┌─────────────────────────┐
│  Bot Process            │
│  handle_callback()      │
└─────────────────────────┘
         ↓
[Acknowledges callback immediately]
[Resolves callback_data:]
[Reads: /tmp/lychee_state/callbacks/cb_a1b2c3d4.json]
[Gets: workspace_path, session_id, action="auto_fix_all"]
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  Bot writes approval file:                                      │
│  /tmp/lychee_state/approvals/approval_abc-123_81e622b5.json    │
│                                                                 │
│  Content:                                                       │
│  {                                                              │
│    "workspace_path": "/Users/terryli/.claude",                 │
│    "session_id": "abc-123",                                    │
│    "decision": "auto_fix_all",                                 │
│    "timestamp": "2025-10-24T19:01:00Z",                        │
│    "metadata": {                                               │
│      "workspace_hash": "81e622b5",                             │
│      "workspace_id": "lychee-autofix"                          │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Bot updates Telegram message:                              │
│                                                             │
│  🔗 **Action Received**: auto_fix_all                       │
│                                                             │
│  Workspace: `lychee-autofix`                                │
│  Session: `abc-123`                                         │
│                                                             │
│  Processing...                                              │
└─────────────────────────────────────────────────────────────┘
```

______________________________________________________________________

## Phase 3: Claude CLI Execution ✅

**Status**: Operational
**Components**: Orchestrator → Claude CLI → Output Capture

### Flow

```
┌─────────────────────────┐
│  Orchestrator Process   │
│  (watchfiles library)   │
│  Watching:              │
│  /tmp/lychee_state/     │
│    approvals/           │
└─────────────────────────┘
         ↓
[Detects: approval_abc-123_81e622b5.json]
[Reads file content]
[Validates workspace path (security check)]
[Checks decision: "auto_fix_all"]
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Orchestrator invokes Claude CLI:                          │
│                                                             │
│  Process:                                                   │
│    /opt/homebrew/bin/claude                                │
│    -p "Fix broken links detected by Lychee..."             │
│    --output-format json                                    │
│                                                             │
│  Working directory: /Users/terryli/.claude                 │
│  Timeout: 300 seconds (5 minutes)                          │
│                                                             │
│  Logging:                                                   │
│    🔧 Starting subprocess...                                │
│    ✓ Process started (PID: 21441)                          │
│    ⏳ Waiting for completion...                             │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────┐
│  Claude CLI Process     │
│  (Running in bg)        │
└─────────────────────────┘
         ↓
[Reads: /tmp/claude_lychee_full.txt (lychee results)]
[Analyzes broken links]
[Uses Edit tool to fix:]
  - CLAUDE.md:45 #setup → #installation
  - CLAUDE.md:67 #usage → #getting-started
  - README.md:12 #contributing → #development
         ↓
[Writes to stdout: "✅ Fixed 3 broken fragment links..."]
[Exits with code: 0 (success)]
         ↓
┌──────────────────────────┐
│  Orchestrator receives:  │
├──────────────────────────┤
│  stdout: "✅ Fixed..."   │
│  stderr: ""              │
│  exit_code: 0            │
│  duration: 21.7s         │
│                          │
│  Logging:                │
│    ✓ Process completed   │
│    📊 Exit code: 0       │
│    📊 Stdout length: 1256│
│    📊 Stderr length: 0   │
│    ⏱️  Duration: 21.7s   │
└──────────────────────────┘
         ↓
[Deletes consumed approval file]
[Proceeds to Phase 4...]
```

______________________________________________________________________

## Phase 4: Completion Notification ✅

**Status**: Operational (NEW in v2.1.0)
**Components**: Orchestrator → Completion File → Bot → Telegram

### Flow

````
┌──────────────────────────┐
│  Orchestrator            │
│  (after Claude finishes) │
└──────────────────────────┘
         ↓
[Captured Claude CLI result:]
  - exit_code: 0
  - stdout: "✅ Fixed 3 broken fragment links..."
  - stderr: ""
  - duration: 21.7 seconds
         ↓
[Logging:]
  📝 Emitting completion notification...
  🔄 Preparing completion notification...
  ✓ Workspace: lychee-autofix (hash: 81e622b5)
  📝 Extracting summary from success output...
  ✓ Summary: Fixed 3 broken fragment links...
  ✓ Completion object created (1641 bytes)
  💾 Writing to: completion_abc-123_81e622b5.json
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  Orchestrator writes completion file:                          │
│  /tmp/lychee_state/completions/completion_abc-123_81e622b5.json│
│                                                                 │
│  Content:                                                       │
│  {                                                              │
│    "workspace_path": "/Users/terryli/.claude",                 │
│    "workspace_id": "lychee-autofix",                           │
│    "session_id": "abc-123",                                    │
│    "status": "success",                                        │
│    "exit_code": 0,                                             │
│    "duration_seconds": 21.7,                                   │
│    "summary": "Fixed 3 broken fragment links in CLAUDE.md",    │
│    "stdout": "✅ Fixed 3 broken fragment links...",            │
│    "stderr": "",                                               │
│    "timestamp": "2025-10-24T19:02:00Z"                         │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
         ↓
[File appears in filesystem]
         ↓
┌─────────────────────────┐
│  Bot Process            │
│  (NEW watcher)          │
│  Watching:              │
│  /tmp/lychee_state/     │
│    completions/         │
└─────────────────────────┘
         ↓
[Detects: completion_abc-123_81e622b5.json]
         ↓
[Logging:]
  📬 New completion: completion_abc-123_81e622b5.json
  🔄 Processing completion...
  📖 Reading completion file...
  ✓ Loaded: workspace=lychee-autofix, session=abc-123, status=success
  📋 Loading workspace registry...
  ✓ Workspace config loaded: emoji=🔗
  ✍️  Formatting completion message...
  ✓ Message formatted (678 chars)
  📡 Sending to Telegram...
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Bot sends NEW Telegram message:                            │
│                                                             │
│  🔗 ✅ **Auto-Fix Completed** - .claude                     │
│                                                             │
│  **Session**: `abc-123`                                     │
│  **Duration**: 21.7s                                        │
│                                                             │
│  **Summary**:                                               │
│  Fixed 3 broken fragment links in CLAUDE.md                │
│                                                             │
│  **Details**:                                               │
│  ```                                                        │
│  ✅ Fixed 3 broken fragment links:                          │
│    - CLAUDE.md:45 #setup → #installation                   │
│    - CLAUDE.md:67 #usage → #getting-started                │
│    - README.md:12 #contributing → #development             │
│  ```                                                        │
└─────────────────────────────────────────────────────────────┘
         ↓
[Logging:]
  📤 ✅ Sent completion for lychee-autofix (abc-123)
  🗑️  Consumed: completion_abc-123_81e622b5.json
         ↓
[User sees completion notification in Telegram] ✅
````

______________________________________________________________________

## Summary of Data Flow

### State Files Created Throughout Process

1. **Notifications** (`/tmp/lychee_state/notifications/notify_{session}_{hash}.json`)

   - Created by: Stop Hook
   - Consumed by: Bot
   - Triggers: Initial Telegram notification

1. **Callbacks** (`/tmp/lychee_state/callbacks/cb_{hash}.json`)

   - Created by: Bot (when sending Telegram message)
   - Consumed by: Bot (when user clicks button)
   - Purpose: Map short callback_data to full context

1. **Approvals** (`/tmp/lychee_state/approvals/approval_{session}_{hash}.json`)

   - Created by: Bot (after user clicks button)
   - Consumed by: Orchestrator
   - Triggers: Claude CLI execution

1. **Completions** (`/tmp/lychee_state/completions/completion_{session}_{hash}.json`) ✨ NEW

   - Created by: Orchestrator (after Claude CLI finishes)
   - Consumed by: Bot
   - Triggers: Completion Telegram notification

______________________________________________________________________

## Processes Involved

### 1. Stop Hook

**Location**: `~/.claude/automation/lychee/runtime/hook/check-links-hybrid.sh`
**Type**: Synchronous shell script
**Role**: Detect broken links, emit notification
**Trigger**: User stops Claude Code session

### 2. Telegram Bot

**Location**: `~/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py`
**Type**: Python async process (python-telegram-bot)
**Watchers**:

- `notifications/` → Send Telegram notification
- `completions/` → Send completion message ✨ NEW
  **Handlers**:
- CallbackQueryHandler → Write approval file

### 3. Orchestrator

**Location**: `~/.claude/automation/lychee/runtime/orchestrator/multi-workspace-orchestrator.py`
**Type**: Python async process (watchfiles)
**Watchers**:

- `approvals/` → Invoke Claude CLI
  **Actions**:
- Execute Claude CLI (5 min timeout)
- Capture stdout/stderr/exit_code
- Emit completion file ✨ NEW

### 4. Claude CLI

**Location**: `/opt/homebrew/bin/claude`
**Type**: Node.js CLI tool
**Role**: Fix broken links based on lychee results
**Output**: stdout (changes made), stderr (errors)

______________________________________________________________________

## Completion Notification Scenarios

### Success Scenario

**Conditions**: exit_code=0, no errors
**Message Format**:

```
🔗 ✅ Auto-Fix Completed
Workspace: lychee-autofix
Session: abc-123
Duration: 21.7s

Summary:
Fixed 3 broken fragment links in CLAUDE.md

Details:
[Full stdout]
```

### Error Scenario

**Conditions**: exit_code≠0 or exception
**Message Format**:

```
🔗 ❌ Auto-Fix Failed
Workspace: lychee-autofix
Session: abc-123
Duration: 12.3s | Exit Code: 1

Summary:
Error: Could not read /tmp/claude_lychee_full.txt

Error:
[Full stderr]
```

### Timeout Scenario

**Conditions**: Execution exceeds 300 seconds
**Message Format**:

```
🔗 ⏱️ Auto-Fix Timeout
Workspace: lychee-autofix
Session: abc-123
Duration: 300.0s (limit reached)

Summary:
Claude CLI exceeded 5-minute timeout
```

______________________________________________________________________

## Observability Commands

### View Active State Files

```bash
# All pending notifications
ls -lt /tmp/lychee_state/notifications/

# All pending approvals
ls -lt /tmp/lychee_state/approvals/

# All completions
ls -lt /tmp/lychee_state/completions/

# Watch all state directories
watch -n 1 'ls -lt /tmp/lychee_state/*/*.json | head -20'
```

### Monitor Logs

```bash
# Bot activity (real-time)
tail -f ~/.claude/logs/telegram-handler.log

# Orchestrator activity (real-time)
tail -f ~/.claude/logs/orchestrator.log

# Both logs side-by-side
tail -f ~/.claude/logs/telegram-handler.log ~/.claude/logs/orchestrator.log
```

### Check Service Status

```bash
# Verify services running
launchctl list | grep lychee

# Expected output:
# XXXXX  0  com.user.lychee.telegram-handler
# XXXXX  0  com.user.lychee.orchestrator
```

______________________________________________________________________

## Testing

### Manual End-to-End Test

```bash
# 1. Emit test notification
/Users/terryli/.claude/automation/lychee/testing/test-notification-emit.py

# 2. Check Telegram for notification

# 3. Click "✅ Auto-Fix All" button

# 4. Monitor orchestrator log
tail -f ~/.claude/logs/orchestrator.log

# 5. Wait for completion message in Telegram (15-30 seconds typical)
```

### POC Validation

```bash
# Run POC test (all 3 scenarios)
/tmp/lychee_poc/test_all_scenarios.sh

# Shows message formatting for:
# - Success
# - Error
# - Timeout
```

______________________________________________________________________

## Version History

**v3.0.1** (2025-10-25):

- Documentation updates to reflect v3.0.0 polling architecture
- Clarified on-demand bot lifecycle behavior
- No code changes (documentation only)

**v3.0.0** (2025-10-24):

- Migrated from webhook to polling architecture
- On-demand bot lifecycle (10-minute idle timeout)
- Eliminated server infrastructure requirements
- SQLite event store for correlation tracking

**v2.1.0** (2025-10-24):

- Added Phase 4: Completion notifications
- Enhanced logging throughout
- Full end-to-end tested and operational

**v2.0.0** (2025-10-24):

- Multi-workspace architecture
- Phases 1-3 operational

**v0.1.1**:

- Detection-only (deprecated)
