# Contributing to Lychee Automation

## Directory Structure

### Production Runtime (`runtime/`)

Active system components executed during normal operation:

- **`bot/`** - Telegram bot (polling, button handlers, file watchers)
- **`orchestrator/`** - Claude CLI invocation manager
- **`hook/`** - Session stop hook (link validation trigger)
- **`lib/`** - Shared libraries (event logging, workspace helpers, ULID generation)

**Do not modify unless:**

- Fixing bugs
- Adding observability
- Improving error handling

### One-Time Setup (`setup/`)

Scripts executed once during initial configuration:

- **`auth/`** - Telegram session authentication (interactive + non-interactive)
- **`bot/`** - Bot creation via BotFather API
- **`registry/`** - Workspace registration

**When to re-run:**

- New machine setup
- Telegram token rotation
- Adding new workspaces

### Development Tools (`testing/`)

Scripts for development, debugging, and validation:

- `inject-results.sh` - Simulate broken link scenarios
- `test-notification-emit.py` - Emit test notifications
- `test-headless-invocation.py` - Test bot without Telegram

**Usage**: Run locally only, never in production

### Configuration (`config/`)

System integration and deployment configs:

- **`launchd/`** - macOS background service plists

### Documentation (`docs/`)

System documentation and deployment guides:

- `COMPLETE_WORKFLOW.md` - End-to-end workflow documentation
- `DEPLOYMENT.md` - Deployment procedures
- `QUICK_START.md` - Setup quickstart
- `DOPPLER_SECRETS.md` - Credential management

### State (`state/`)

Runtime state files (managed by system):

- **`events.db`** - SQLite event store (correlation tracking)
- **`callbacks/`** - Telegram button callback mapping
- **`notifications/`** - Hook → Bot notification files
- **`approvals/`** - Bot → Orchestrator approval files
- **`completions/`** - Orchestrator → Bot completion files
- **`registry.json`** - Workspace configuration

**Manual intervention**: Only for debugging, never modify during runtime

### Archive (`archive/`)

Historical artifacts and deprecated code:

- **`planning/`** - Legacy planning documents
- **`reports/`** - Analysis reports
- **`migrations/`** - Version migration documentation
- **`deprecated-code/`** - Removed code (e.g., webhook infrastructure)

---

## Development Workflow

### Testing Changes

1. **Unit Tests**: None currently (file-based integration testing)
1. **Integration Tests**: Use `testing/` scripts to simulate workflows
1. **Manual Testing**: Monitor logs during session stop/approval flows

### Testing with inject-results.sh

```bash
# Simulate broken links
cd automation/lychee/testing
./inject-results.sh

# Expected: Telegram notification appears
# Action: Click button, verify orchestrator invocation
```

### State Cleanup

After testing, clean state files:

```bash
rm -rf state/notifications/*.json
rm -rf state/approvals/*.json
rm -rf state/completions/*.json

# Callbacks accumulate, cleanup old ones:
find state/callbacks -name "*.json" -mtime +30 -delete
```

---

## Code Standards

### Error Handling

**Fail-fast policy**: Raise and propagate errors, no silent failures

```python
# ✅ Good
def process_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return json.loads(path.read_text())

# ❌ Bad
def process_file(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}  # Silent failure
```

### Logging

Use emoji-prefixed structured logging for observability:

```python
print(f"🔄 Processing notification: {filename}")
print(f"   ✓ Workspace loaded: {workspace_id}")
print(f"   📤 Telegram message sent")
```

**Standard Emoji**:

- 🔄 = Processing started
- ✓ = Step completed
- 📊 = Metrics/statistics
- 📤 = Output emitted
- ❌ = Error occurred
- ⚠️ = Warning

### File Operations

**Atomic writes**: Use temporary file + rename pattern

```python
# ✅ Good - atomic write
temp_file = state_dir / f"{filename}.tmp"
temp_file.write_text(json.dumps(data))
temp_file.rename(state_dir / filename)

# ❌ Bad - non-atomic write
(state_dir / filename).write_text(json.dumps(data))
```

---

## Event Store (SQLite)

### Schema

```sql
CREATE TABLE session_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    component TEXT NOT NULL CHECK (component IN ('hook', 'bot', 'orchestrator', 'claude-cli')),
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata JSON,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
);
```

### Querying Events

```bash
# View events for a correlation ID
sqlite3 state/events.db "SELECT event_type, timestamp FROM session_events WHERE correlation_id = '01K8...' ORDER BY timestamp;"

# View recent bot events
sqlite3 state/events.db "SELECT event_type, metadata FROM session_events WHERE component = 'bot' ORDER BY timestamp DESC LIMIT 10;"
```

---

## SLOs

### Availability

- **Target**: 99% - Bot and orchestrator running during active hours
- **Measurement**: launchd service uptime
- **Validation**: `ps aux | grep multi-workspace`

### Correctness

- **Target**: 100% - All events logged to event store
- **Measurement**: Correlation ID coverage across hook → bot → orchestrator
- **Validation**: Query events.db for complete workflows

### Observability

- **Target**: 100% - All workflows traceable via correlation ID
- **Measurement**: Event store completeness
- **Validation**: End-to-end correlation ID propagation

### Maintainability

- **Target**: Single source of truth for state
- **Measurement**: No duplicated configuration
- **Validation**: Registry.json as canonical workspace source

---

## Common Tasks

### Adding a New Workspace

```bash
# Register workspace
cd setup/registry
python register-workspace.py --workspace-id my-project --emoji 📝 --path /path/to/project

# Verify registration
cat ../../state/registry.json
```

### Debugging Correlation Failures

```bash
# Find correlation ID from Telegram notification
CORRELATION_ID="01K8E91BQ8ZHVG4QZAPB3B4Q8W"

# Trace full workflow
sqlite3 state/events.db "SELECT component, event_type, timestamp FROM session_events WHERE correlation_id = '$CORRELATION_ID' ORDER BY timestamp;"
```

### Bot Not Responding

```bash
# Check if bot is running
ps aux | grep multi-workspace-bot

# Check last activity
tail -50 ~/.claude/logs/telegram-handler.log

# Restart bot
launchctl unload ~/Library/LaunchAgents/com.user.lychee.telegram-handler.plist
launchctl load ~/Library/LaunchAgents/com.user.lychee.telegram-handler.plist
```

---

## Architecture Decisions

### Why Polling Instead of Webhooks?

**v3.0.0 Migration**: Simplified deployment, no server infrastructure required

**Tradeoffs**:

- Latency: 1-2 second button response (vs instant with webhooks)
- Complexity: Reduced (no server, SSL, domain management)
- Idle Handling: Bot shuts down after 10 minutes idle (auto-restarts on next session)

### Why File-Based State Instead of Database?

**File-based workflow state**:

- Simplicity: No database migrations for state files
- Atomicity: Filesystem rename is atomic
- Debugging: State files human-readable JSON

**Database for events only**:

- Observability: SQLite for correlation tracking
- Queryability: Complex event analysis requires SQL

---

## Safety Guidelines

### Never Modify

- **State files during runtime** - Race conditions with bot/orchestrator
- **Event store schema** - Breaking change for existing data
- **Correlation ID format** - ULID standard required for distributed tracing

### Safe to Modify

- Documentation
- Testing scripts
- Log format (emoji, structure)
- SLO thresholds

### Requires Testing

- Bot polling logic
- Orchestrator Claude CLI invocation
- Hook lychee validation
- Error propagation

---

## Getting Help

- **Logs**: `~/.claude/logs/telegram-handler.log`, `~/.claude/logs/orchestrator.log`
- **State**: `automation/lychee/state/events.db`
- **Documentation**: `automation/lychee/docs/`
