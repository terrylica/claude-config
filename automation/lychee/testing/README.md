# Testing Tools

**Purpose**: Development and debugging scripts for lychee automation system

**⚠️ DEVELOPMENT ONLY** - Do not run in production environments

______________________________________________________________________

## Scripts

### inject-results.sh

**Purpose**: Simulate broken link detection scenarios

**Usage**:

```bash
cd /Users/terryli/.claude/automation/lychee/testing
./inject-results.sh
```

**What it does**:

1. Creates fake lychee results with broken links
1. Writes to `../.lychee-results.txt`
1. Triggers notification workflow when session stops

**Expected outcome**: Telegram notification appears with broken link count

______________________________________________________________________

### test-notification-emit.py

**Purpose**: Manually emit notification files to test bot consumption

**Usage**:

```bash
cd /Users/terryli/.claude/automation/lychee/testing
uv run test-notification-emit.py
```

**What it does**:

1. Generates notification JSON with test data
1. Writes to `state/notifications/notify_test_*.json`
1. Bot detects file and sends Telegram message

**Expected outcome**: Telegram notification with test workspace data

______________________________________________________________________

### test-headless-invocation.py

**Purpose**: Test bot logic without Telegram API connection

**Usage**:

```bash
cd /Users/terryli/.claude/automation/lychee/testing
uv run test-headless-invocation.py
```

**What it does**:

1. Mocks Telegram bot initialization
1. Tests file watching and processing logic
1. Validates JSON parsing and error handling

**Expected outcome**: Console output showing bot logic execution

______________________________________________________________________

## Testing Workflow

### End-to-End Test

1. **Inject Results**:

   ```bash
   ./inject-results.sh
   ```

1. **Stop Session**: End Claude Code session to trigger hook

1. **Verify Notification**: Check Telegram for notification message

1. **Click Button**: Click "Auto-Fix All" in Telegram

1. **Monitor Orchestrator**:

   ```bash
   tail -f ~/.claude/logs/orchestrator.log
   ```

1. **Verify Completion**: Check Telegram for completion message

1. **Query Events**:

   ```bash
   sqlite3 ../state/events.db "SELECT event_type, timestamp FROM session_events WHERE correlation_id = '...' ORDER BY timestamp;"
   ```

### Component Tests

#### Test Bot File Watching

```bash
# Start bot in foreground
cd ../runtime/bot
uv run multi-workspace-bot.py

# In another terminal
cd ../../testing
uv run test-notification-emit.py

# Expected: Bot logs show file detected and processed
```

#### Test Orchestrator Invocation

```bash
# Manually create approval file
cat > ../state/approvals/approval_test_$(date +%s).json <<EOF
{
  "workspace_path": "/Users/terryli/.claude",
  "session_id": "test-session",
  "decision": "auto_fix_all",
  "correlation_id": "01K8TEST00000000000000000",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S)+00:00",
  "metadata": {
    "workspace_hash": "test1234",
    "workspace_id": "test-workspace"
  }
}
EOF

# Expected: Orchestrator spawns, invokes Claude CLI
```

______________________________________________________________________

## State Cleanup

After testing, clean state directories:

```bash
# Remove test notifications
rm ../state/notifications/notify_test_*.json

# Remove test approvals
rm ../state/approvals/approval_test_*.json

# Remove test completions
rm ../state/completions/completion_test_*.json

# Remove old callbacks (>30 days)
find ../state/callbacks -name "*.json" -mtime +30 -delete
```

______________________________________________________________________

## Debugging

### Bot Not Processing Files

```bash
# Check bot is running
ps aux | grep multi-workspace-bot

# Check file permissions
ls -la ../state/notifications/

# Check bot logs
tail -50 ~/.claude/logs/telegram-handler.log
```

### Orchestrator Not Spawning

```bash
# Check approval file format
cat ../state/approvals/*.json | jq .

# Check orchestrator logs
tail -50 ~/.claude/logs/orchestrator.log

# Verify Claude CLI available
which claude
```

### Event Store Issues

```bash
# Check database exists
ls -la ../state/events.db

# Verify schema
sqlite3 ../state/events.db ".schema session_events"

# Check recent events
sqlite3 ../state/events.db "SELECT * FROM session_events ORDER BY timestamp DESC LIMIT 10;"
```

______________________________________________________________________

## SLOs for Testing

### Correctness

- **Target**: 100% - Test scripts produce expected output
- **Validation**: Run all 3 scripts, verify no errors

### Observability

- **Target**: 100% - Test events logged to event store
- **Validation**: Query events.db after running tests

______________________________________________________________________

## Adding New Tests

When adding test scripts:

1. Add `# /// script` PEP 723 header for uv dependencies
1. Include `# DEVELOPMENT ONLY` comment at top
1. Use emoji-prefixed logging for consistency
1. Clean up generated state files
1. Document in this README

Example template:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema>=4.0.0"]
# ///
"""
Test Script Name

DEVELOPMENT ONLY - Do not run in production
"""

import json
from pathlib import Path

def main():
    print("🧪 Starting test...")
    # Test logic here
    print("   ✓ Test completed")

if __name__ == "__main__":
    main()
```

______________________________________________________________________

## References

- **Main README**: `../README.md`
- **Contributing**: `../CONTRIBUTING.md`
- **Event Store Schema**: `../migrations/001_create_event_store.sql`
