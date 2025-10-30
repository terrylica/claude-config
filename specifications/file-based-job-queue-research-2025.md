# File-Based Job Queue and Task Coordination Research (2025)

**Research Date:** 2025-10-25
**Python Version:** 3.12+
**Target Platforms:** macOS, Linux (Unix-like)

## Executive Summary

This research evaluates modern file-based job queue and task coordination systems for Python to solve race conditions, feedback loops, and duplicate processing in a multi-process notification and approval workflow system.

**Key Finding:** SQLite-based solutions (Huey, persist-queue, litequeue) combined with proper file locking libraries (filelock, portalocker) offer the best balance of atomicity, crash recovery, and offline capability for the specific use case.

---

## Library Comparison

### Job Queue Systems

| Library | GitHub Stars | Last Update | Python Support | Maintenance Status | License |
| --- | --- | --- | --- | --- | --- |
| **huey** | 5.7k | 2025-03-19 (v2.5.3) | 3.x | Active | MIT |
| **diskcache** | 2.7k | 2024-08 | 3.6-3.10+ | Active | Apache-2.0 |
| **persist-queue** | 365 | 2024-11 (v1.0.0) | 3.5+ | Active | BSD-3-Clause |
| **litequeue** | 213 | 2025-02-10 (v0.6) | 3.x | Active | MIT |

### File Locking Libraries

| Library | GitHub Stars | Last Update | Python Support | Cross-Platform | License |
| --- | --- | --- | --- | --- | --- |
| **filelock** | 901 | 2025-10-08 (v3.20.0) | 3.x | Yes | Unlicense |
| **portalocker** | 310 | 2025-06-14 (v3.2.0) | 3.x | Yes (Windows/Unix) | BSD-3-Clause |

### File System Monitoring

| Library | Type | Best For | Notes |
| --- | --- | --- | --- |
| **watchdog** | Cross-platform | Production | Uses inotify (Linux), FSEvents (macOS), polling |
| **os.replace()** | Built-in (3.3+) | Atomic writes | Atomic on same filesystem |

---

## Detailed Analysis

### 1. Huey

**Best For:** Full-featured task queue with minimal setup

**Pros:**

- Multiple storage backends (SQLite, Redis, file-system, in-memory)
- Built-in scheduling, retries, priorities
- Multi-process/thread/greenlet support
- Well-documented, widely adopted

**Cons:**

- More features than needed for simple coordination
- Requires running consumer process
- Heavier than pure file-based solutions

**SQLite Backend:**

```python
from huey import SqliteHuey

huey = SqliteHuey(filename='/path/to/huey.db')

@huey.task()
def process_approval(approval_id):
    # Process approval
    pass

# Enqueue task
process_approval('approval-123')
```

**Migration Complexity:** Medium - Requires refactoring current file-based workflow to task-based model

---

### 2. DiskCache

**Best For:** High-performance caching with queue capabilities

**Pros:**

- Pure Python, no compilation needed
- Thread-safe and process-safe
- Deque implementation for queues
- Excellent performance (25µs reads, 198µs writes)
- 100% test coverage

**Cons:**

- Primarily a cache, not purpose-built queue
- Queue features less documented than caching
- May be overkill for simple coordination

**Deque Usage:**

```python
from diskcache import Deque

# Create persistent deque
queue = Deque(directory='/path/to/cache')

# Producer
queue.append({'type': 'link_broken', 'file': '/path/to/file.md'})

# Consumer
try:
    item = queue.popleft()
    process_item(item)
except IndexError:
    pass  # Queue empty
```

**Migration Complexity:** Easy - Can wrap existing file operations with minimal changes

---

### 3. persist-queue

**Best For:** Thread-safe persistent queues with acknowledgment patterns

**Pros:**

- Built-in crash recovery (disk-based persistence)
- Acknowledgment queue (ack/nack/ack_failed)
- File-based and SQLite options
- Simple API similar to stdlib Queue
- Thread-safe out of the box

**Cons:**

- Smaller community (365 stars)
- Less documentation than huey/diskcache
- v1.0.0 dropped Python 2 support (recent major change)

**Acknowledgment Pattern (Ideal for Your Use Case):**

```python
from persistqueue import SQLiteAckQueue

# Create ack queue
queue = SQLiteAckQueue(path='/path/to/queue', auto_commit=True)

# Producer (bash hook)
queue.put({
    'type': 'link_broken',
    'file': '/path/to/broken-link.md',
    'timestamp': '2025-10-25T10:30:00'
})

# Consumer (Telegram bot)
item = queue.get()  # Blocks until item available
try:
    # Send notification
    send_telegram_notification(item)
    queue.ack(item)  # Mark successful
except Exception as e:
    queue.nack(item)  # Return to queue for retry
```

**Migration Complexity:** Easy - Minimal refactoring, direct queue API

---

### 4. litequeue

**Best For:** Lightweight SQLite-based queues with timing metrics

**Pros:**

- Single-file implementation (simple)
- Built-in timing metrics (in_time, lock_time, done_time)
- UUIDv7 message IDs (time-sortable)
- No external dependencies
- Recent updates (Feb 2025)

**Cons:**

- Smallest community (213 stars)
- Less mature than alternatives
- Limited documentation
- String-only messages (requires JSON serialization)

**Basic Usage:**

```python
from litequeue import LiteQueue
import json

# Create queue
queue = LiteQueue(db_path='/path/to/queue.db')

# Producer
queue.put(json.dumps({
    'type': 'approval',
    'user_id': 12345,
    'file': '/path/to/file.md'
}))

# Consumer
message = queue.pop()
if message:
    data = json.loads(message['message'])
    process_approval(data)
    queue.done(message['message_id'])
```

**Migration Complexity:** Easy - Simple API, direct replacement for file operations

---

## File Locking Solutions

### 1. filelock (Recommended)

**Best For:** Platform-independent file locking

**Pros:**

- Most popular (901 stars)
- Actively maintained (Oct 2025 release)
- Clean context manager API
- Part of tox-dev ecosystem (well-tested)
- 686k dependent projects

**Cons:**

- Advisory locking only (not mandatory)

**Usage:**

```python
from filelock import FileLock
import json
from pathlib import Path

def atomic_write_notification(data, filepath):
    """Atomically write notification file with lock"""
    lock_path = filepath.with_suffix('.lock')

    with FileLock(lock_path, timeout=10):
        # Write to temp file
        temp_path = filepath.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(data, f)

        # Atomic replace
        temp_path.replace(filepath)

    # Lock released, safe to read

def atomic_read_and_delete(filepath):
    """Atomically read and delete notification file"""
    lock_path = filepath.with_suffix('.lock')

    with FileLock(lock_path, timeout=10):
        if not filepath.exists():
            return None

        # Read data
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Delete file
        filepath.unlink()

        return data
```

---

### 2. portalocker

**Best For:** Advanced locking with distributed support

**Pros:**

- Cross-platform (Windows/Linux/BSD/Unix)
- Distributed locking via Redis
- BoundedSemaphore for process coordination
- Advisory and mandatory locking support

**Cons:**

- Smaller community (310 stars)
- More complex for basic use cases
- Redis dependency for distributed features

**Usage:**

```python
import portalocker
import json

def atomic_write_with_lock(data, filepath):
    """Write with exclusive lock"""
    with portalocker.Lock(filepath, 'w', timeout=10) as f:
        json.dump(data, f)

def atomic_read_with_lock(filepath):
    """Read with shared lock"""
    try:
        with portalocker.Lock(filepath, 'r', timeout=10) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
```

---

## Atomic File Operations (Built-in)

### os.replace() Pattern (Python 3.3+)

**Best For:** Simple atomic writes without external dependencies

```python
import os
import json
import tempfile
from pathlib import Path

def atomic_write(data, filepath):
    """
    Atomic write using temp file + os.replace()

    Atomic on same filesystem (macOS, Linux)
    Works correctly on Windows (overwrites destination)
    """
    filepath = Path(filepath)

    # Create temp file in same directory (ensures same filesystem)
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=filepath.parent,
        delete=False,
        prefix=f'.{filepath.name}.',
        suffix='.tmp'
    ) as tf:
        json.dump(data, tf)
        temp_path = Path(tf.name)

    # Atomic replace (overwrites if exists)
    os.replace(temp_path, filepath)

def atomic_read_and_delete(filepath):
    """
    Read and delete in one operation

    Note: Not atomic without external locking!
    Use filelock wrapper for true atomicity.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        return None

    # Read
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Delete
    filepath.unlink()

    return data
```

**Limitations:**

- Read-then-delete is NOT atomic without locking
- Atomic only on same filesystem
- No built-in retry/timeout mechanism

---

## Process Coordination Patterns

### 1. File System Watching (Debounced)

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import defaultdict

class DebouncedHandler(FileSystemEventHandler):
    """
    Debounces file events to avoid processing incomplete writes
    """
    def __init__(self, callback, debounce_seconds=1.0):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.pending = defaultdict(lambda: None)

    def on_created(self, event):
        if event.is_directory:
            return

        # Cancel existing timer
        if self.pending[event.src_path]:
            self.pending[event.src_path].cancel()

        # Schedule new timer
        timer = threading.Timer(
            self.debounce_seconds,
            self._process_file,
            args=[event.src_path]
        )
        timer.start()
        self.pending[event.src_path] = timer

    def _process_file(self, filepath):
        self.callback(filepath)
        del self.pending[filepath]

# Usage
def process_notification(filepath):
    data = atomic_read_and_delete(filepath)
    if data:
        send_telegram_notification(data)

handler = DebouncedHandler(process_notification, debounce_seconds=1.0)
observer = Observer()
observer.schedule(handler, path='/path/to/notifications', recursive=False)
observer.start()
```

---

### 2. SQLite-Based Coordination (Recommended)

```python
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

class JobQueue:
    """
    SQLite-based job queue with deduplication and crash recovery

    Prevents:
    - Race conditions (IMMEDIATE transaction)
    - Feedback loops (idempotent job IDs)
    - Duplicate processing (status tracking)
    """

    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with self._connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    claimed_at TEXT,
                    claimed_by TEXT,
                    completed_at TEXT,
                    error TEXT,
                    retry_count INTEGER DEFAULT 0
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_status_created
                ON jobs(status, created_at)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_type_status
                ON jobs(type, status)
            ''')

    @contextmanager
    def _connect(self):
        """Context manager for WAL-mode connections"""
        conn = sqlite3.connect(
            self.db_path,
            isolation_level='IMMEDIATE',  # Lock immediately
            timeout=30.0  # Wait up to 30s for locks
        )
        conn.execute('PRAGMA journal_mode=WAL')  # Enable WAL mode
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def enqueue(self, job_id, job_type, data):
        """
        Enqueue job (idempotent - duplicate IDs ignored)

        Returns: True if inserted, False if duplicate
        """
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT INTO jobs (id, type, data, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    job_id,
                    job_type,
                    json.dumps(data),
                    datetime.utcnow().isoformat()
                ))
                return True
            except sqlite3.IntegrityError:
                # Duplicate job_id - already processed/processing
                return False

    def claim_next(self, worker_id, job_type=None):
        """
        Atomically claim next pending job

        Returns: Job dict or None if queue empty
        """
        with self._connect() as conn:
            # Find oldest pending job
            query = '''
                SELECT * FROM jobs
                WHERE status = 'pending'
            '''
            params = []

            if job_type:
                query += ' AND type = ?'
                params.append(job_type)

            query += ' ORDER BY created_at LIMIT 1'

            row = conn.execute(query, params).fetchone()

            if not row:
                return None

            # Claim job
            conn.execute('''
                UPDATE jobs
                SET status = 'processing',
                    claimed_at = ?,
                    claimed_by = ?
                WHERE id = ? AND status = 'pending'
            ''', (
                datetime.utcnow().isoformat(),
                worker_id,
                row['id']
            ))

            # Verify we claimed it (another worker might have)
            if conn.total_changes == 0:
                return None  # Someone else claimed it

            return dict(row)

    def complete(self, job_id):
        """Mark job as completed"""
        with self._connect() as conn:
            conn.execute('''
                UPDATE jobs
                SET status = 'completed',
                    completed_at = ?
                WHERE id = ?
            ''', (datetime.utcnow().isoformat(), job_id))

    def fail(self, job_id, error, max_retries=3):
        """
        Mark job as failed

        Retries job if under max_retries, else marks as failed
        """
        with self._connect() as conn:
            row = conn.execute(
                'SELECT retry_count FROM jobs WHERE id = ?',
                (job_id,)
            ).fetchone()

            if row and row['retry_count'] < max_retries:
                # Retry
                conn.execute('''
                    UPDATE jobs
                    SET status = 'pending',
                        retry_count = retry_count + 1,
                        error = ?
                    WHERE id = ?
                ''', (error, job_id))
            else:
                # Max retries exceeded
                conn.execute('''
                    UPDATE jobs
                    SET status = 'failed',
                        completed_at = ?,
                        error = ?
                    WHERE id = ?
                ''', (datetime.utcnow().isoformat(), error, job_id))

    def cleanup_old_jobs(self, days=7):
        """Delete completed/failed jobs older than N days"""
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        with self._connect() as conn:
            conn.execute('''
                DELETE FROM jobs
                WHERE status IN ('completed', 'failed')
                AND datetime(completed_at) < datetime(?, 'unixepoch')
            ''', (cutoff,))

# Usage Example
queue = JobQueue('/path/to/jobs.db')

# Producer (bash hook)
job_id = f"link-broken-{filepath}-{timestamp}"
queue.enqueue(job_id, 'link_broken', {
    'file': filepath,
    'link': broken_link,
    'line': line_number
})

# Consumer (Telegram bot)
worker_id = f"telegram-bot-{os.getpid()}"
while True:
    job = queue.claim_next(worker_id, job_type='link_broken')
    if job:
        try:
            send_notification(json.loads(job['data']))
            queue.complete(job['id'])
        except Exception as e:
            queue.fail(job['id'], str(e), max_retries=3)
    else:
        time.sleep(5)  # No jobs, wait
```

---

## Preventing Feedback Loops

### Strategy 1: Job ID Based on Content Hash

```python
import hashlib

def create_job_id(filepath, link, line):
    """
    Create deterministic job ID based on content

    Same broken link = same ID = deduplication
    """
    content = f"{filepath}:{link}:{line}"
    hash_part = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"link-broken-{hash_part}"

# Enqueue (idempotent)
job_id = create_job_id('/path/file.md', 'https://dead.link', 42)
queue.enqueue(job_id, 'link_broken', {...})  # Duplicate = ignored
```

---

### Strategy 2: Exclude Hook from Claude Sessions

```bash
#!/bin/bash
# Git hook that skips execution during Claude sessions

# Check if running in Claude session
if [ -n "$CLAUDE_SESSION_ID" ]; then
    exit 0  # Skip hook
fi

# Check for marker file
if [ -f "/tmp/claude-orchestrator-active" ]; then
    exit 0  # Skip hook
fi

# Normal hook execution
python3 detect_broken_links.py
```

```python
# Orchestrator creates marker file
def run_claude_session(command):
    marker_file = Path('/tmp/claude-orchestrator-active')

    try:
        marker_file.touch()
        os.environ['CLAUDE_SESSION_ID'] = str(uuid.uuid4())

        # Run Claude CLI
        subprocess.run(['claude', *command])
    finally:
        marker_file.unlink(missing_ok=True)
        os.environ.pop('CLAUDE_SESSION_ID', None)
```

---

## Recommendation for Your Use Case

### Primary Solution: SQLite Queue (persist-queue or custom)

**Why:**

1. **Atomic Operations:** SQLite IMMEDIATE transactions prevent race conditions
1. **Deduplication:** Primary key job IDs prevent duplicate processing
1. **Crash Recovery:** All state persisted to disk automatically
1. **No Servers:** Pure file-based, works offline
1. **Multi-Process Safe:** WAL mode allows concurrent readers + single writer
1. **Acknowledgment Pattern:** Track pending/processing/completed states

**Implementation:**

```python
# Option 1: Use persist-queue (easiest)
from persistqueue import SQLiteAckQueue

notification_queue = SQLiteAckQueue('/data/notifications.db')
approval_queue = SQLiteAckQueue('/data/approvals.db')
completion_queue = SQLiteAckQueue('/data/completions.db')

# Option 2: Custom SQLite queue (more control)
from job_queue import JobQueue  # See implementation above

queue = JobQueue('/data/jobs.db')
```

---

### Secondary: File Locking for Legacy Compatibility

If maintaining current file-based approach, wrap with filelock:

```python
from filelock import FileLock
from pathlib import Path
import json

NOTIFICATION_DIR = Path('/data/notifications')

def write_notification(data):
    """Write notification with lock"""
    notification_id = data['id']
    filepath = NOTIFICATION_DIR / f"{notification_id}.json"
    lock_path = NOTIFICATION_DIR / f"{notification_id}.lock"

    with FileLock(lock_path, timeout=10):
        atomic_write(data, filepath)

def read_and_delete_notification(notification_id):
    """Read and delete notification atomically"""
    filepath = NOTIFICATION_DIR / f"{notification_id}.json"
    lock_path = NOTIFICATION_DIR / f"{notification_id}.lock"

    with FileLock(lock_path, timeout=10):
        if not filepath.exists():
            return None

        with open(filepath) as f:
            data = json.load(f)

        filepath.unlink()
        return data
```

---

## Migration Complexity Assessment

| Solution | Complexity | Effort | Benefits |
| --- | --- | --- | --- |
| **SQLite Queue (custom)** | Medium | 2-3 days | Maximum control, perfect fit |
| **persist-queue** | Easy | 1 day | Drop-in replacement, ack pattern |
| **filelock wrapper** | Easy | 1 day | Minimal changes, keeps current design |
| **huey** | Medium | 3-5 days | Full task queue, overkill for needs |
| **diskcache** | Easy | 1-2 days | Good performance, cache-focused |
| **litequeue** | Easy | 1-2 days | Lightweight, less mature |

---

## Production Examples

### Example 1: File Processing Pipeline (persist-queue)

```python
from persistqueue import SQLiteAckQueue
import logging

# Initialize queues
input_queue = SQLiteAckQueue('/data/input.db', auto_commit=True)
output_queue = SQLiteAckQueue('/data/output.db', auto_commit=True)

# Worker process
logger = logging.getLogger(__name__)

while True:
    item = input_queue.get(block=True, timeout=5)

    try:
        # Process
        result = process_file(item)

        # Forward to next stage
        output_queue.put(result)

        # Acknowledge success
        input_queue.ack(item)
        logger.info(f"Processed {item['id']}")

    except Exception as e:
        # Return to queue for retry
        input_queue.nack(item)
        logger.error(f"Failed {item['id']}: {e}")
```

---

### Example 2: Approval Workflow (Custom SQLite)

```python
# Complete workflow implementation
from job_queue import JobQueue
import os

# Initialize queues
notifications = JobQueue('/data/notifications.db')
approvals = JobQueue('/data/approvals.db')
completions = JobQueue('/data/completions.db')

# Bash hook (producer)
def on_broken_link(filepath, link, line):
    job_id = create_job_id(filepath, link, line)
    notifications.enqueue(job_id, 'link_broken', {
        'file': filepath,
        'link': link,
        'line': line
    })

# Telegram bot (consumer + producer)
def poll_notifications():
    worker_id = f"telegram-{os.getpid()}"

    while True:
        job = notifications.claim_next(worker_id)

        if job:
            try:
                # Send Telegram notification
                message_id = send_telegram(json.loads(job['data']))
                notifications.complete(job['id'])

                # Wait for approval (creates approval job on button click)
                # (handled by Telegram callback handler)

            except Exception as e:
                notifications.fail(job['id'], str(e))
        else:
            time.sleep(5)

# Telegram callback handler
def on_approval_button(callback_query):
    approval_id = callback_query.data
    approvals.enqueue(approval_id, 'user_approval', {
        'user_id': callback_query.from_user.id,
        'original_job_id': approval_id,
        'approved_at': datetime.utcnow().isoformat()
    })

# Orchestrator (consumer + producer)
def poll_approvals():
    worker_id = f"orchestrator-{os.getpid()}"

    while True:
        job = approvals.claim_next(worker_id)

        if job:
            try:
                # Launch Claude CLI session
                data = json.loads(job['data'])
                run_claude_session(data)

                # Create completion job
                completions.enqueue(
                    f"completion-{job['id']}",
                    'session_complete',
                    {'approval_id': job['id']}
                )

                approvals.complete(job['id'])

            except Exception as e:
                approvals.fail(job['id'], str(e))
        else:
            time.sleep(5)

# Bot completion handler (consumer)
def poll_completions():
    worker_id = f"telegram-completion-{os.getpid()}"

    while True:
        job = completions.claim_next(worker_id)

        if job:
            try:
                # Notify user of completion
                send_telegram_completion(json.loads(job['data']))
                completions.complete(job['id'])
            except Exception as e:
                completions.fail(job['id'], str(e))
        else:
            time.sleep(5)
```

---

## Key Takeaways

1. **SQLite + WAL mode** is the sweet spot for file-based job coordination in 2025
1. **filelock** (901 stars) is the most widely adopted file locking library
1. **persist-queue** offers best balance of simplicity and features for acknowledgment workflows
1. **Custom SQLite implementation** provides maximum control for specific requirements
1. **Avoid atomicwrites** (unmaintained) - use `os.replace()` instead
1. **watchdog** for file monitoring, but prefer polling SQLite queue for reliability
1. **Deduplication via deterministic job IDs** prevents duplicate processing
1. **Environment markers** (CLAUDE_SESSION_ID) prevent feedback loops

---

## References

### GitHub Repositories

- huey: `/github.com/coleifer/huey`
- diskcache: `/github.com/grantjenks/python-diskcache`
- persist-queue: `/github.com/peter-wangxu/persist-queue`
- litequeue: `/github.com/litements/litequeue`
- filelock: `/github.com/tox-dev/filelock`
- portalocker: `/github.com/wolph/portalocker`
- watchdog: `/github.com/gorakhargosh/watchdog`

### Documentation

- Python os.replace(): `/docs.python.org/3/library/os.html#os.replace`
- SQLite WAL Mode: `/sqlite.org/wal.html`
- PEP 723 (Inline Dependencies): `/peps.python.org/pep-0723/`

### Production Use Cases

- File-based queues for data processing: Prakritidev Verma (Medium, 2024)
- SQLite background job system: Jason Gorman (2024)
- Distributed SQLite queue: DEV Community (2024)
