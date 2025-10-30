# Task Queue Architecture Diagrams

## Current File-Based Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Bash Stop Hook                          │
│  automation/prettier/stop-prettier-markdown.sh              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Writes JSON file
                  │ notify_{session}_{hash}.json
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              File System (state/notifications/)             │
│                                                              │
│  notify_abc123_xyz789.json                                  │
│  notify_def456_uvw012.json                                  │
│  notify_ghi789_rst345.json                                  │
│                                                              │
│  ❌ Race conditions on file deletion                        │
│  ❌ Manual deduplication via hash                           │
│  ❌ No crash recovery (orphaned files)                      │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ Polls directory every 5 seconds
              │ (5s latency, continuous I/O overhead)
              ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Telegram Bot (async)                    │
│                                                              │
│  while True:                                                │
│      files = glob("notify_*.json")                          │
│      for f in files:                                        │
│          data = json.load(f)                                │
│          await send_notification(data)                      │
│          f.unlink()  # ⚠️ Race condition!                  │
│      await asyncio.sleep(5)  # ⏱️ 5s latency               │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ User clicks button
                  │ Writes approval JSON file
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              File System (state/approvals/)                 │
│                                                              │
│  approval_session123_hash456.json                           │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ Polls directory OR explicit trigger
              ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Orchestrator (async)                    │
│                                                              │
│  files = glob("approval_*.json")                            │
│  for f in files:                                            │
│      await invoke_claude_cli(f)                             │
│      f.unlink()  # ❌ Lost if process crashes!             │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Spawns subprocess
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   Claude CLI Subprocess                     │
│                  (up to 5 minutes)                          │
│                                                              │
│  ❌ No retry on orchestrator crash                         │
│  ❌ No visibility into queue depth                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Writes completion JSON file
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              File System (state/completions/)               │
│                                                              │
│  completion_session123_hash456.json                         │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ Polls directory every 5 seconds
              ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Telegram Bot (async)                    │
│                                                              │
│  while True:                                                │
│      files = glob("completion_*.json")                      │
│      for f in files:                                        │
│          await send_completion(f)                           │
│          f.unlink()                                         │
│      await asyncio.sleep(5)                                 │
└─────────────────────────────────────────────────────────────┘
```

### Issues with Current Approach

1. **Race Conditions**: Multiple processes can read same file before deletion
1. **5-Second Latency**: Polling introduces 0-5s delay (avg 2.5s)
1. **No Crash Recovery**: Tasks lost if process crashes during execution
1. **Manual Deduplication**: Hash-based checking prone to edge cases
1. **File System Clutter**: JSON files accumulate, require manual cleanup
1. **No Visibility**: Can't query queue depth, task status, or history

---

## Proposed SQLite Queue Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Bash Stop Hook                          │
│  automation/prettier/stop-prettier-markdown.sh              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Option A: Python wrapper (enqueue_task)
                  │ Option B: Direct SQLite CLI (fast!)
                  │
                  │ INSERT INTO notifications (data) VALUES (...)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   SQLite Queue Database                      │
│              ~/.claude/automation/lychee/                    │
│                    state/tasks.db                            │
│                                                               │
│  Tables:                                                      │
│  - notifications (link validation requests)                  │
│  - approvals (user decisions)                                │
│  - completions (Claude CLI results)                          │
│                                                               │
│  Features:                                                    │
│  ✅ WAL mode (concurrent reads during writes)               │
│  ✅ ACID transactions (no race conditions)                  │
│  ✅ UNIQUE constraints (automatic deduplication)            │
│  ✅ Crash-resistant (AckQueue for long tasks)               │
│  ✅ Query-able (SELECT for monitoring)                      │
└─────────────┬───────────────────┬───────────────────────────┘
              │                   │
              │                   │ Both consume same queue
              │                   │ (SQLite handles locking)
              ▼                   ▼
┌──────────────────────┐   ┌──────────────────────────────────┐
│  Telegram Bot        │   │  Background Scanner              │
│  (async consumer)    │   │  (async consumer)                │
│                      │   │                                  │
│  queue = get_queue() │   │  Optional: watchdog triggers     │
│  while True:         │   │  on WAL file modification        │
│    task = dequeue()  │   │  (event-driven, zero latency)    │
│    if task:          │   │                                  │
│      process(task)   │   │                                  │
│    else:             │   │                                  │
│      sleep(1)        │   │                                  │
│                      │   │                                  │
│  ✅ 1s latency      │   │  ✅ <100ms latency (events)     │
│  ✅ No race conds   │   │                                  │
└──────────┬───────────┘   └──────────────────────────────────┘
           │
           │ User clicks button
           │ enqueue_task(APPROVALS, ...)
           ▼
┌─────────────────────────────────────────────────────────────┐
│              SQLite Queue - Approvals Table                 │
│                                                              │
│  Task persists in queue until acknowledged                  │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ Dequeue with acknowledgment
              │ task_id, task = queue.get()
              ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Orchestrator (async)                    │
│                                                              │
│  queue = get_ack_queue(APPROVALS)                           │
│  task_id, task = queue.get()  # Stays in queue!            │
│  try:                                                       │
│      await invoke_claude_cli(task)                          │
│      queue.ack(task_id)  # ✅ Remove from queue            │
│  except:                                                    │
│      queue.nack(task_id)  # 🔄 Return for retry            │
│                                                              │
│  ✅ Automatic crash recovery                               │
│  ✅ Task retry on failure                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Spawns subprocess
                  │ asyncio.create_subprocess_exec(...)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   Claude CLI Subprocess                     │
│                  (up to 5 minutes)                          │
│                                                              │
│  ✅ If orchestrator crashes, task returns to queue         │
│  ✅ If subprocess fails, nack() retries automatically       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ On completion, enqueue result
                  │ enqueue_task(COMPLETIONS, ...)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              SQLite Queue - Completions Table               │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ Dequeue completion
              ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Telegram Bot (async)                    │
│                                                              │
│  queue = get_queue(COMPLETIONS)                             │
│  while True:                                                │
│      task = dequeue()                                       │
│      if task:                                               │
│          await send_telegram_completion(task)               │
│      else:                                                  │
│          await asyncio.sleep(1)                             │
│                                                              │
│  ✅ Clean database (auto-cleanup old completions)          │
│  ✅ Query history (debugging/monitoring)                    │
└─────────────────────────────────────────────────────────────┘
```

### Improvements with SQLite Queue

1. **ACID Guarantees**: Zero race conditions via SQLite transactions
1. **1-Second Latency**: Polling reduced to 1s (or event-driven \<100ms)
1. **Automatic Crash Recovery**: AckQueue ensures tasks survive crashes
1. **Native Deduplication**: UNIQUE constraints prevent duplicate tasks
1. **Clean Storage**: Single database file, automatic WAL management
1. **Full Visibility**: SQL queries for monitoring, debugging, analytics

---

## Event-Driven Architecture (Zero Latency)

For ultra-low latency, combine `persist-queue` with `watchdog` for event-driven dequeue:

```
┌─────────────────────────────────────────────────────────────┐
│                     Bash Stop Hook                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ enqueue_task(...)
                  │ SQLite writes to WAL file
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              SQLite WAL File Modified                       │
│              tasks.db-wal                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ watchdog detects file change
                  │ (inotify on Linux, FSEvents on macOS)
                  │ <10ms latency
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Watchdog File System Observer                  │
│                                                              │
│  observer = Observer()                                      │
│  observer.schedule(                                         │
│      QueueWatcher(QUEUE_DB, on_queue_modified),            │
│      QUEUE_PATH                                             │
│  )                                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Triggers immediate dequeue
                  │ asyncio.create_task(process_queue())
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Async Queue Consumer                           │
│                                                              │
│  async def on_queue_modified():                             │
│      while not queue.empty():                               │
│          task = dequeue()                                   │
│          await process(task)                                │
│                                                              │
│  ⚡ <100ms end-to-end latency                              │
│  ⚡ Zero polling overhead                                   │
└─────────────────────────────────────────────────────────────┘
```

### Event-Driven Implementation

```python
import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class QueueWatcher(FileSystemEventHandler):
    """Watch for SQLite WAL modifications to trigger immediate processing."""

    def __init__(self, queue_db: Path, process_callback):
        self.queue_db = queue_db
        self.process_callback = process_callback
        self.processing = False

    def on_modified(self, event):
        # Trigger on WAL file modification (indicates new data)
        if event.src_path.endswith('.db-wal'):
            if not self.processing:
                asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """Process all pending tasks (debounced)."""
        self.processing = True
        await self.process_callback()
        self.processing = False


# Usage in bot/orchestrator
async def process_all_pending():
    """Process all tasks in queue (triggered by watchdog)."""
    queue = get_queue(TASK_QUEUE_NOTIFICATION)

    while not queue.empty():
        task = queue.get(block=False)
        await process_task(task)


# Start watchdog observer
observer = Observer()
observer.schedule(
    QueueWatcher(QUEUE_DB, process_all_pending),
    str(STATE_DIR),
    recursive=False
)
observer.start()
```

---

## Data Flow Comparison

### File-Based Flow

```
Stop Hook → JSON File (5ms write)
              ↓
          [0-5s polling delay]
              ↓
          Bot scans directory (10-50ms)
              ↓
          Read JSON (5ms)
              ↓
          Process task (100-1000ms)
              ↓
          Delete file (5ms) ⚠️ Race condition

Total latency: 2.5s average (0-5s range)
```

### SQLite Queue Flow (Polling)

```
Stop Hook → SQLite INSERT (2ms)
              ↓
          [0-1s polling delay]
              ↓
          Bot SELECT FROM queue (1ms)
              ↓
          Process task (100-1000ms)
              ↓
          Transaction auto-committed

Total latency: 0.5s average (0-1s range)
```

### SQLite Queue Flow (Event-Driven)

```
Stop Hook → SQLite INSERT (2ms)
              ↓
          WAL file modified
              ↓
          [<10ms inotify/FSEvents]
              ↓
          Bot triggered immediately
              ↓
          SELECT FROM queue (1ms)
              ↓
          Process task (100-1000ms)

Total latency: <100ms (excluding task processing)
```

---

## SQLite Schema Design

### Minimal Schema (persist-queue handles this)

```sql
-- persist-queue creates these automatically
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL
);

-- Enable WAL mode for concurrency
PRAGMA journal_mode=WAL;
```

### Enhanced Schema (with deduplication)

```sql
-- Custom schema for advanced features
CREATE TABLE IF NOT EXISTS task_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,  -- Deduplication
    task_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending/in_progress/completed/failed
    data TEXT NOT NULL,
    enqueued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_task_status ON task_queue(status);
CREATE INDEX IF NOT EXISTS idx_task_type ON task_queue(task_type);
CREATE INDEX IF NOT EXISTS idx_task_enqueued ON task_queue(enqueued_at);

-- Enable WAL mode
PRAGMA journal_mode=WAL;
```

---

## Migration Strategy Visual

```
Phase 1: Parallel Operation (2 weeks)
┌────────────────┐
│   Stop Hook    │
└────┬──────┬────┘
     │      │
     │      └─────> SQLite Queue (new)
     │                    ↓
     │              Bot reads from queue
     │                    ↓
     │              [Monitor for issues]
     │
     └────────────> JSON File (legacy)
                         ↓
                    Bot reads from files (fallback)


Phase 2: Queue Primary (1 week)
┌────────────────┐
│   Stop Hook    │
└────┬───────────┘
     │
     └─────────────> SQLite Queue (primary)
                         ↓
                    Bot reads from queue
                         ↓
                    Falls back to files only if queue fails


Phase 3: Queue Only (cleanup)
┌────────────────┐
│   Stop Hook    │
└────┬───────────┘
     │
     └─────────────> SQLite Queue (only)
                         ↓
                    Bot reads from queue
                         ↓
                    [Delete legacy file-based code]
```

---

## Performance Benchmarks (Estimated)

| Operation | File-Based | SQLite Queue | Improvement |
| --- | --- | --- | --- |
| **Enqueue** | 5ms (write JSON) | 2ms (INSERT) | **2.5x faster** |
| **Dequeue** | 2500ms avg (polling) | 500ms avg (polling) | **5x faster** |
| **Dequeue** | 2500ms avg (polling) | \<100ms (event-driven) | **25x faster** |
| **Concurrent writers** | Conflicts (manual locking) | Safe (SQLite ACID) | **∞ improvement** |
| **Concurrent readers** | N × file reads | 1 × SELECT | **N×/1 improvement** |
| **Crash recovery** | Manual file cleanup | Automatic (AckQueue) | **∞ improvement** |
| **Deduplication** | Hash check (O(n)) | UNIQUE constraint (O(1)) | **N× improvement** |
| **Queue depth query** | len(glob()) = O(n) | SELECT COUNT(\*) = O(1) | **N× improvement** |

---

## Monitoring & Observability

### File-Based (Limited)

```bash
# Count pending tasks
ls ~/.claude/automation/lychee/state/notifications/ | wc -l

# No history, no status, no retry info
```

### SQLite Queue (Rich)

```sql
-- Queue depth by type
SELECT task_type, status, COUNT(*) as count
FROM task_queue
GROUP BY task_type, status;

-- Average processing time
SELECT task_type,
       AVG(JULIANDAY(completed_at) - JULIANDAY(started_at)) * 86400 as avg_seconds
FROM task_queue
WHERE status = 'completed'
GROUP BY task_type;

-- Failed tasks
SELECT task_id, task_type, error_message, retry_count
FROM task_queue
WHERE status = 'failed'
ORDER BY enqueued_at DESC;

-- Tasks in progress > 5 minutes (potential hangs)
SELECT task_id, task_type,
       (JULIANDAY('now') - JULIANDAY(started_at)) * 86400 as seconds_running
FROM task_queue
WHERE status = 'in_progress'
  AND started_at < datetime('now', '-5 minutes');
```

---

## References

- Full research: `/Users/terryli/.claude/docs/architecture/lightweight-async-task-queue-research.md`
- Quick reference: `/Users/terryli/.claude/docs/architecture/task-queue-quick-reference.md`
- persist-queue docs: https://github.com/peter-wangxu/persist-queue
- SQLite WAL mode: https://www.sqlite.org/wal.html
