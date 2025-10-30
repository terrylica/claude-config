# Task Queue Quick Reference

**TL;DR**: Use `persist-queue` with SQLite backend for lightweight, crash-resistant task coordination between bash, Python asyncio, and subprocesses.

______________________________________________________________________

## Installation

```python
# PEP 723 inline dependency
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "persist-queue>=1.1.0",
# ]
# ///
```

______________________________________________________________________

## Quick Start

### 1. Enqueue Task (Bash Stop Hook)

**Option A: Python wrapper** (recommended for complex data)

```python
#!/usr/bin/env -S uv run
from pathlib import Path
import sys
sys.path.insert(0, str(Path.home() / ".claude/automation/lychee/runtime/lib"))
from queue_helpers import enqueue_task, TASK_QUEUE_NOTIFICATION

enqueue_task(
    TASK_QUEUE_NOTIFICATION,
    "link_validation",
    {"workspace_path": str(Path.cwd())}
)
```

**Option B: Direct SQLite CLI** (fastest, no Python overhead)

```bash
sqlite3 "$HOME/.claude/automation/lychee/state/tasks.db" <<EOF
PRAGMA journal_mode=WAL;
INSERT INTO notifications (data) VALUES ('{"workspace": "$(pwd)"}');
EOF
```

### 2. Dequeue Task (Async Python)

```python
from queue_helpers import get_queue, TASK_QUEUE_NOTIFICATION
import asyncio
import json

queue = get_queue(TASK_QUEUE_NOTIFICATION)

while True:
    loop = asyncio.get_event_loop()
    task = await loop.run_in_executor(
        None,
        lambda: queue.get(block=False) if not queue.empty() else None
    )

    if task:
        data = json.loads(task)
        await process_task(data)
    else:
        await asyncio.sleep(1)
```

### 3. Long-Running Tasks with Crash Recovery

```python
from queue_helpers import get_ack_queue, TASK_QUEUE_APPROVAL

queue = get_ack_queue(TASK_QUEUE_APPROVAL)

while True:
    task_id, task_json = queue.get(block=True, timeout=5)

    try:
        await long_running_subprocess(task_json)
        queue.ack(task_id)  # Success - remove from queue
    except Exception:
        queue.nack(task_id)  # Failure - return to queue for retry
```

______________________________________________________________________

## Key Patterns

### Deduplication

```python
# Use deterministic task_id for automatic deduplication
task_id = f"{workspace_hash}_{session_id}"

enqueue_task(
    queue_name=TASK_QUEUE_NOTIFICATION,
    task_type="link_validation",
    data=data,
    task_id=task_id  # Prevents duplicate tasks
)
```

### Event-Driven (Zero Latency)

```python
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class QueueWatcher(FileSystemEventHandler):
    def __init__(self, queue_path, callback):
        self.queue_path = queue_path
        self.callback = callback

    def on_modified(self, event):
        if event.src_path == str(self.queue_path / "notifications"):
            asyncio.create_task(self.callback())

# Trigger immediate dequeue when queue file changes (WAL writes)
observer = Observer()
observer.schedule(QueueWatcher(QUEUE_PATH, process_queue), QUEUE_PATH)
observer.start()
```

______________________________________________________________________

## Comparison Cheat Sheet

| Feature           | File-Based        | persist-queue        |
| ----------------- | ----------------- | -------------------- |
| Latency           | 0-5s (avg 2.5s)   | 0-1s (avg 0.5s)      |
| Race conditions   | Yes               | No (ACID)            |
| Crash recovery    | Manual            | Automatic (AckQueue) |
| Deduplication     | Manual hashing    | Native (UNIQUE)      |
| Bash integration  | Easy (JSON files) | Easy (SQLite CLI)    |
| Concurrent access | Risky             | Safe (WAL mode)      |

______________________________________________________________________

## Common Issues & Solutions

### "database is locked"

```python
queue = SQLiteQueue(
    path="./state",
    name="tasks",
    multithreading=True,  # Enables WAL mode
    timeout=30.0  # Increase timeout
)
```

### Queue grows unbounded

```python
# Add periodic cleanup
async def cleanup_old_tasks():
    while True:
        conn = sqlite3.connect(QUEUE_DB)
        conn.execute(
            "DELETE FROM task_history WHERE completed_at < datetime('now', '-24 hours')"
        )
        await asyncio.sleep(3600)  # Cleanup every hour
```

### Tasks lost on crash

```python
# Use AckQueue instead of SQLiteQueue
queue = get_ack_queue("approvals")  # Tasks persist until ack'd
```

______________________________________________________________________

## Full Research

See `/Users/terryli/.claude/docs/architecture/lightweight-async-task-queue-research.md` for comprehensive analysis, benchmarks, and migration guide.
