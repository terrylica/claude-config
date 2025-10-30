# Workflow Orchestration Quick Reference

**For**: Telegram bot → file watching → Claude CLI → notifications workflows
**Full Research**: [`workflow-orchestration-comparison.md`](/Users/terryli/.claude/docs/architecture/workflow-orchestration-comparison.md)
**Specification**: [`lightweight-workflow-orchestration-research.yaml`](/Users/terryli/.claude/specifications/lightweight-workflow-orchestration-research.yaml)

______________________________________________________________________

## TL;DR - Use SQLite + Huey

```bash
# Install
uv pip install 'huey[sqlite]' watchdog

# Create queue database
mkdir -p ~/.claude/workflows
```

**Why**: Zero deployment complexity, scales from 2 to 10+ workflows, easy debugging

______________________________________________________________________

## 5-Approach Comparison

| Approach               | Deploy     | Extend     | Simple   | Score | Use When                       |
| ---------------------- | ---------- | ---------- | -------- | ----- | ------------------------------ |
| **SQLite + Huey**      | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐⭐ | **5** | **Starting simple, growing**   |
| Asyncio Event Bus      | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | ⭐⭐⭐⭐ | 4     | Embedded, single-process       |
| State Machine + SQLite | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | ⭐⭐⭐   | 4     | Complex multi-step workflows   |
| Redis Streams          | ⭐⭐       | ⭐⭐⭐⭐⭐ | ⭐⭐⭐   | 3     | Already have Redis, need scale |
| MCP Server             | ⭐⭐       | ⭐⭐⭐⭐   | ⭐⭐     | 2     | **Wait until 2026**            |

______________________________________________________________________

## Minimal Implementation (SQLite + Huey)

```python
# /// script
# dependencies = ["huey[sqlite]", "watchdog"]
# ///

from huey import SqliteHuey
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

# Configure queue
huey = SqliteHuey(filename='~/.claude/workflows/queue.db')

# Define tasks
@huey.task()
def analyze_file(filepath):
    result = subprocess.run(['claude', 'analyze', filepath], capture_output=True)
    if result.returncode == 0:
        send_notification(f"Analysis complete: {filepath}")
    return result.stdout

@huey.task()
def send_notification(message):
    # Telegram/Pushover implementation
    pass

# File watcher
class WorkflowHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            analyze_file(event.src_path)

# Start observer
observer = Observer()
observer.schedule(WorkflowHandler(), '~/.claude/docs', recursive=True)
observer.start()

# Run worker in separate process:
# huey_consumer module.huey
```

______________________________________________________________________

## Architecture Diagram

```
┌─────────────┐
│ File Watcher│
│  (watchdog) │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  Producer   │────▶│ SQLite Queue │
│(Telegram bot)│     │    (Huey)    │
└─────────────┘     └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │Worker Process│
                    │(Huey consumer)│
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Claude CLI   │
                    │  Invocation  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │Notification  │
                    │(Telegram)    │
                    └──────────────┘
```

______________________________________________________________________

## Decision Tree

```
Need distributed processing? → YES → Redis Streams
                             → NO  → Continue

Complex state-dependent flows? → YES → State Machine + Huey
                                → NO  → Continue

Need persistence across restarts? → YES → SQLite + Huey ⭐
                                   → NO  → Asyncio Event Bus

Already have Redis? → YES → Redis Streams viable
                    → NO  → SQLite + Huey ⭐
```

______________________________________________________________________

## Growth Strategy

### Phase 1: Start (2 workflows)

- Single SQLite file
- Single worker process
- 2 `@huey.task()` functions

### Phase 2: Expand (3-5 workflows)

- More task decorators
- Task chaining
- Separate queue names

### Phase 3: Scale (6-10 workflows)

- Multiple worker processes
- State machine for complex flows
- Consider Redis backend if needed

### Phase 4: Advanced (>10 workflows)

- Evaluate Prefect/Temporal
- Or continue with Huey + Redis (proven)

______________________________________________________________________

## Key Commands

```bash
# Install dependencies
uv pip install 'huey[sqlite]' watchdog pyrogram

# Start worker
huey_consumer workflow_module.huey

# Inspect queue (debugging)
sqlite3 ~/.claude/workflows/queue.db "SELECT * FROM task_queue;"

# Monitor logs
tail -f /tmp/huey.log
```

______________________________________________________________________

## Python Libraries

### Recommended (SQLite + Huey)

- `huey[sqlite]` - Task queue with SQLite backend
- `watchdog` - File system monitoring
- `pyrogram` - Telegram bot integration

### Alternative (Asyncio)

- `asyncio` (stdlib) - Pure Python event loop
- `aiofiles` - Async file I/O

### Alternative (State Machine)

- `transitions` - State machine library
- `huey[sqlite]` - For task execution

### Not Recommended Now

- `redis` - Requires Redis server (unless already have)
- `mcp` - Too immature (check 2026)

______________________________________________________________________

## Common Patterns

### Task Chaining

```python
@huey.task()
def step1():
    result = do_work()
    step2.schedule(args=(result,), delay=5)  # Chain next task

@huey.task()
def step2(data):
    process(data)
```

### Error Handling

```python
@huey.task(retries=3, retry_delay=60)
def flaky_task():
    try:
        external_api_call()
    except APIError:
        raise  # Will retry
```

### Scheduling

```python
from huey import crontab

@huey.periodic_task(crontab(hour='*/6'))
def periodic_workflow():
    # Runs every 6 hours
    pass
```

______________________________________________________________________

## Debugging Tips

### Inspect Queue

```bash
sqlite3 ~/.claude/workflows/queue.db
sqlite> .tables
sqlite> SELECT * FROM task_queue WHERE status='pending';
```

### Test Single Task

```python
# Run task immediately (blocking)
result = analyze_file.call_local('/path/to/file.md')
```

### View Worker Logs

```bash
# Run worker with verbose logging
huey_consumer module.huey --verbose --logfile=/tmp/huey.log
```

______________________________________________________________________

## When NOT to Use These Approaches

### Use Existing Solutions If:

- Already have Airflow/Prefect/Temporal running
- Need distributed execution across machines (use Redis Streams or existing orchestrator)
- Workflows require complex DAG visualization (use Airflow)
- Need enterprise workflow engine features (SLA monitoring, complex scheduling)

### These approaches are for:

- Starting simple with 2-10 workflows
- Single-machine orchestration
- File watching + CLI invocation patterns
- Lightweight, embedded workflows

______________________________________________________________________

## Additional Resources

- **Full Research**: [`workflow-orchestration-comparison.md`](/Users/terryli/.claude/docs/architecture/workflow-orchestration-comparison.md)
- **Specification**: [`lightweight-workflow-orchestration-research.yaml`](/Users/terryli/.claude/specifications/lightweight-workflow-orchestration-research.yaml)
- Huey Docs: https://huey.readthedocs.io/
- Transitions Docs: https://github.com/pytransitions/transitions
- Watchdog Docs: https://python-watchdog.readthedocs.io/

______________________________________________________________________

**Updated**: 2025-10-24
**Recommendation**: Start with SQLite + Huey, add state machine layer if workflows become complex
