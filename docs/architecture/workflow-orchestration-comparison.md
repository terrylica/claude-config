# Lightweight Workflow Orchestration for Claude Code CLI

**Research Date**: 2025-10-24
**Purpose**: Compare event-driven architecture solutions for orchestrating Claude Code CLI workflows without heavy engines
**Full Specification**: [`/Users/terryli/.claude/specifications/lightweight-workflow-orchestration-research.yaml`](/Users/terryli/.claude/specifications/lightweight-workflow-orchestration-research.yaml)

## Executive Summary

For orchestrating Telegram bot → file watching → Claude CLI invocation → notifications workflows, **SQLite + Huey + watchdog** is the recommended approach for starting simple and growing to 10+ workflows.

### Quick Comparison Matrix

| Approach               | Deploy | Extend | Simple | Score | Best For                       |
| ---------------------- | ------ | ------ | ------ | ----- | ------------------------------ |
| **SQLite + Huey**      | 1      | 4      | 2      | 5     | **Starting simple, growing**   |
| Asyncio Event Bus      | 1      | 3      | 2      | 4     | Embedded, single-process       |
| Redis Streams          | 3      | 5      | 3      | 3     | Already have Redis, need scale |
| State Machine + SQLite | 2      | 4      | 3      | 4     | Complex multi-step workflows   |
| MCP Server             | 3      | 4      | 4      | 2     | Future, wait for maturity      |

**Scoring**: 1 = simplest/best, 5 = most complex/worst (except Extend and Score where higher is better)

## Approach 1: SQLite + Huey (RECOMMENDED)

### Overview

Use Huey task queue with SQLite backend for persistent, durable workflow orchestration.

### Architecture

```
┌─────────────────┐
│  File Watcher   │
│   (watchdog)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│  Event Producer │────▶│  SQLite Queue    │
│  (Telegram bot) │     │  (Huey/LiteQueue)│
└─────────────────┘     └────────┬─────────┘
                                 │
                                 ▼
┌─────────────────┐     ┌──────────────────┐
│ Background      │◀────│  Worker Process  │
│ Claude CLI      │     │  (Huey consumer) │
│ Invocation      │     └──────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Notification   │
│  (Telegram/Push)│
└─────────────────┘
```

### Pros & Cons

**Pros**:

- Zero external dependencies - just SQLite file
- Huey supports SQLite, Redis, or in-memory backends
- Built-in retry logic and task scheduling
- Atomic operations and ACID guarantees
- Easy debugging - inspect queue with sqlite3 CLI
- Works with existing file watching (watchdog)

**Cons**:

- SQLite not ideal for high-concurrency writes
- Polling overhead if not using triggers
- Worker process management needed
- No distributed processing without additional work

### Minimal Implementation

```python
# /// script
# dependencies = ["huey[sqlite]", "watchdog"]
# ///

from huey import SqliteHuey
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

# Configure Huey
huey = SqliteHuey(filename='~/.claude/workflow_queue.db')

@huey.task()
def analyze_file(filepath):
    """Task: Analyze file with Claude CLI"""
    result = subprocess.run(['claude', 'analyze', filepath], capture_output=True)
    return result.stdout

@huey.task()
def send_notification(message):
    """Task: Send notification"""
    # Implementation
    pass

# File watcher
class WorkflowHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            analyze_file(event.src_path)

# Start worker: huey_consumer module.huey
```

### Growth Path

1. **Start (2 workflows)**: Single SQLite file, single worker
2. **Add workflows (3-5)**: New `@huey.task()` functions
3. **Scale workers**: Multiple worker processes
4. **Upgrade backend**: Switch to Redis if concurrency needed
5. **Task pipelines**: Chain tasks with `.then()` or manual orchestration

### Deployment Complexity: 1/5

- Single SQLite file
- No external services
- Worker runs as background process

### Extensibility: 4/5

- Easy to add new task types
- Task chaining supported
- Can switch backends transparently
- Integrates well with other tools

### Code Simplicity: 2/5

- Simple decorator-based API
- Familiar task queue patterns
- Minimal boilerplate

---

## Approach 2: Asyncio-Native Event Bus

### Overview

Pure Python asyncio with event bus pattern using `asyncio.Queue` - no external dependencies.

### Architecture

```
┌─────────────────────────────────────────┐
│      Main Async Event Loop              │
│                                          │
│  ┌────────────┐      ┌───────────────┐ │
│  │ Event Bus  │      │  Event Queue  │ │
│  │ (asyncio)  │◀────▶│ (asyncio.Queue)│ │
│  └─────┬──────┘      └───────────────┘ │
│        │                                │
│        ├──────────┬──────────┬─────────┤
│        ▼          ▼          ▼         │
│  ┌─────────┐ ┌────────┐ ┌──────────┐  │
│  │Handler 1│ │Handler2│ │ Handler3 │  │
│  │ (File)  │ │(Telegram)│ (Claude) │  │
│  └─────────┘ └────────┘ └──────────┘  │
└─────────────────────────────────────────┘
```

### Pros & Cons

**Pros**:

- Zero dependencies - pure Python stdlib
- Fully embedded, no external processes
- Native async/await patterns
- Fine-grained control over execution
- Easy to debug and test
- No polling overhead

**Cons**:

- No built-in persistence across restarts
- Manual event routing and handler registration
- Requires asyncio knowledge
- No distributed processing
- State management is manual

### Minimal Implementation

```python
import asyncio
from typing import Callable, Dict, List

class EventBus:
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.queue = asyncio.Queue()

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def publish(self, event_type: str, data: dict):
        await self.queue.put((event_type, data))

    async def process_events(self):
        while True:
            event_type, data = await self.queue.get()
            handlers = self.handlers.get(event_type, [])
            await asyncio.gather(*[h(data) for h in handlers])

# Usage
bus = EventBus()

async def handle_file_change(data):
    proc = await asyncio.create_subprocess_exec('claude', 'analyze', data['path'])
    await proc.wait()
    await bus.publish('analysis.complete', {'result': 'success'})

bus.handlers['file.changed'] = [handle_file_change]
```

### Growth Path

1. **Start**: Single event bus, few handlers
2. **Add workflows**: Register new event types and handlers
3. **Complex flows**: Chain events (handler emits new events)
4. **State tracking**: Add JSON/SQLite persistence layer
5. **Concurrency**: Use semaphores to limit parallel execution

### Deployment: 1/5 | Extensibility: 3/5 | Simplicity: 2/5

---

## Approach 3: Redis Streams

### Overview

Redis Streams with consumer groups for distributed workflow orchestration.

### Architecture

```
┌─────────────────┐
│  File Watcher   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│   Producer      │────▶│  Redis Streams   │
│ (XADD commands) │     │  (file:events)   │
└─────────────────┘     └────────┬─────────┘
                                 │
         ┌───────────────────────┴────────────┐
         ▼                                    ▼
┌──────────────────┐              ┌──────────────────┐
│ Consumer Group 1 │              │ Consumer Group 2 │
│  (claude-workers)│              │ (notifiers)      │
└────────┬─────────┘              └────────┬─────────┘
         │                                 │
         ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│  Worker 1, 2, 3  │              │  Notifier 1, 2   │
└──────────────────┘              └──────────────────┘
```

### Pros & Cons

**Pros**:

- Built-in consumer groups for parallel processing
- Automatic message acknowledgment and retry
- Stream persistence and replay capability
- Distributed workers out of the box
- High throughput and low latency
- Mature Python client (redis-py)

**Cons**:

- Requires Redis server (external dependency)
- Memory-based, need persistence configuration
- Additional deployment complexity vs SQLite
- Learning curve for Streams concepts
- Overkill for simple 2-workflow use case

### Minimal Implementation

```python
# /// script
# dependencies = ["redis"]
# ///

import redis
import json

r = redis.Redis(host='localhost', port=6379)

# Producer
def publish_file_event(filepath):
    event = {'type': 'file.changed', 'path': filepath}
    r.xadd('workflow:events', {'data': json.dumps(event)})

# Consumer
def process_events():
    r.xgroup_create('workflow:events', 'claude-workers', id='0', mkstream=True)

    while True:
        messages = r.xreadgroup(
            'claude-workers', 'worker-1',
            {'workflow:events': '>'},
            count=1, block=5000
        )

        for stream, msgs in messages:
            for msg_id, fields in msgs:
                data = json.loads(fields['data'])
                # Process event
                r.xack('workflow:events', 'claude-workers', msg_id)
```

### Growth Path

1. **Start**: Single Redis instance, single stream
2. **Add workflows**: Create new streams per workflow type
3. **Scale workers**: Add consumers to existing groups
4. **Parallel stages**: Multiple consumer groups on same stream

### Deployment: 3/5 | Extensibility: 5/5 | Simplicity: 3/5

**Recommendation**: Only if you already have Redis infrastructure.

---

## Approach 4: State Machine + SQLite Hybrid

### Overview

Combine Python state machine library (transitions) with SQLite persistence for structured workflow states.

### Architecture

```
┌─────────────────────────────────────────────┐
│         Workflow State Machine              │
│                                              │
│  ┌─────────┐    trigger   ┌──────────────┐ │
│  │  IDLE   │─────────────▶│  PROCESSING  │ │
│  └─────────┘              └──────┬───────┘ │
│       ▲                          │         │
│       │                          ▼         │
│  ┌─────────┐              ┌──────────────┐ │
│  │  DONE   │◀─────────────│   WAITING    │ │
│  └─────────┘   complete   └──────────────┘ │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         SQLite State Storage                 │
│  - Current state per workflow instance       │
│  - Transition history                        │
│  - Workflow metadata and context             │
└─────────────────────────────────────────────┘
```

### Pros & Cons

**Pros**:

- Clear workflow state modeling
- Transitions library very mature
- Built-in state persistence to SQLite
- Visual state diagrams (mermaid/graphviz)
- Callback hooks at each transition
- Easy to validate state transitions
- Async support with AsyncMachine

**Cons**:

- Need to design state machines upfront
- Less flexible than pure event-driven
- State machine abstraction has learning curve
- Still need separate task queue for async work

### Minimal Implementation

```python
# /// script
# dependencies = ["transitions", "huey[sqlite]"]
# ///

from transitions import Machine
import sqlite3

class WorkflowModel:
    states = ['idle', 'processing', 'waiting', 'done', 'failed']

    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.machine = Machine(
            model=self,
            states=WorkflowModel.states,
            initial='idle'
        )

        # Define transitions
        self.machine.add_transition('start', 'idle', 'processing',
                                  before='enqueue_task')
        self.machine.add_transition('complete', 'processing', 'waiting',
                                  after='send_notification')
        self.machine.add_transition('finish', 'waiting', 'done')

    def enqueue_task(self):
        # Enqueue Claude CLI task
        pass

    def persist_state(self):
        conn = sqlite3.connect('workflows.db')
        conn.execute('UPDATE workflows SET state = ? WHERE id = ?',
                    (self.state, self.workflow_id))
        conn.commit()
```

### Growth Path

1. **Start**: Define 2 state machines for current workflows
2. **Add workflows**: Create new state machine classes
3. **Shared states**: Use hierarchical state machines
4. **Complex flows**: Nested states and parallel machines
5. **Visualization**: Generate state diagrams for documentation

### Deployment: 2/5 | Extensibility: 4/5 | Simplicity: 3/5

**Best combined with**: Huey for async task execution + watchdog for file events

---

## Approach 5: Model Context Protocol (MCP) Server

### Overview

Use MCP server architecture for workflow state and notifications - emerging standard for AI agent orchestration.

### Pros & Cons

**Pros**:

- Purpose-built for AI agent workflows
- Built-in notification system
- Maintains state across interactions
- Standard protocol for Claude integration
- Future-proof as Claude Code adopts MCP

**Cons**:

- Very new protocol (2024-2025)
- Limited Python implementations
- Documentation still evolving
- Overkill for simple workflows
- Ecosystem not yet mature

### Recommendation

**DO NOT USE YET**. Monitor for maturity in Q2-Q3 2026. Better to start with Huey/asyncio and migrate later if MCP becomes standard.

### Deployment: 3/5 | Extensibility: 4/5 | Simplicity: 4/5 | Score: 2/5

---

## Decision Tree

```
Q1: Need distributed processing across machines?
  YES → Redis Streams or wait for distributed solution
  NO  → Continue

Q2: Complex workflows with many states and branches?
  YES → State Machine + Huey hybrid
  NO  → Continue

Q3: Need state to persist across restarts?
  YES → SQLite + Huey ⭐ RECOMMENDED
  NO  → Continue

Q4: Single-process embedded workflow?
  YES → Asyncio Event Bus
  NO  → SQLite + Huey ⭐ RECOMMENDED

Q5: Already have Redis infrastructure?
  YES → Redis Streams is viable
  NO  → SQLite + Huey ⭐ RECOMMENDED
```

---

## Implementation Roadmap

### Phase 1: Initial Setup (1-2 days)

- Install Huey: `uv pip install 'huey[sqlite]'`
- Install watchdog: `uv pip install watchdog`
- Create SQLite database: `~/.claude/workflow_queue.db`
- Define initial 2 workflows as `@huey.task()` functions
- Set up file watcher event handler
- Test single workflow: file change → task execution
- Start Huey consumer: `huey_consumer module.huey`

### Phase 2: Integration (3-5 days)

- Integrate Telegram bot event producer
- Add task chaining for multi-step workflows
- Implement notification tasks (Telegram/Pushover)
- Add error handling and retry logic
- Create systemd/launchd service for worker
- Set up logging and monitoring

### Phase 3: Expansion (as needed)

- Add workflows 3-5 as new task functions
- Implement task scheduling (periodic tasks)
- Add workflow state tracking table
- Create CLI tool for queue inspection
- Document workflow definitions

### Phase 4: Scale (if needed)

- Add state machine layer for complex workflows
- Implement workflow analytics/metrics
- Consider Redis backend if concurrency issues
- Evaluate Prefect/Temporal if >10 workflows

---

## Detailed Comparison

### Deployment Complexity

| Approach      | Requirements                      | Setup Time |
| ------------- | --------------------------------- | ---------- |
| SQLite + Huey | Single file, no services          | 30 min     |
| Asyncio       | Pure Python, no dependencies      | 1 hour     |
| Redis Streams | Redis server (local or remote)    | 2 hours    |
| State Machine | SQLite + library                  | 1 hour     |
| MCP           | MCP server process, documentation | 4+ hours   |

### Persistence

| Approach      | Method                       | Durability |
| ------------- | ---------------------------- | ---------- |
| SQLite + Huey | SQLite ACID guarantees       | Excellent  |
| Asyncio       | Manual (JSON/YAML)           | Fair       |
| Redis Streams | Redis AOF/RDB (memory-based) | Good       |
| State Machine | SQLite state tables          | Excellent  |
| MCP           | Backend-dependent            | Unknown    |

### Distribution

| Approach      | Capability              |
| ------------- | ----------------------- |
| SQLite + Huey | Single machine\*        |
| Asyncio       | Single process only     |
| Redis Streams | Multi-worker native     |
| State Machine | Single machine          |
| MCP           | Implementation-specific |

\*Can switch Huey to Redis backend for distribution

### Learning Curve

| Approach      | Difficulty | Prerequisites                  |
| ------------- | ---------- | ------------------------------ |
| SQLite + Huey | Low        | Task queue patterns            |
| Asyncio       | Medium     | async/await knowledge          |
| Redis Streams | Medium     | Redis concepts                 |
| State Machine | Medium     | State machine design           |
| MCP           | High       | New protocol, limited examples |

### Debugging & Monitoring

| Approach      | Tools                          | Quality   |
| ------------- | ------------------------------ | --------- |
| SQLite + Huey | sqlite3 CLI, inspect queue     | Excellent |
| Asyncio       | Python debugger, print/logging | Good      |
| Redis Streams | Redis CLI, XINFO commands      | Good      |
| State Machine | Visual diagrams + SQL queries  | Excellent |
| MCP           | TBD - tooling immature         | Unknown   |

---

## Recommended Python Libraries

### SQLite + Huey Approach

- **huey** (`uv pip install 'huey[sqlite]'`) - Task queue with multiple backends
- **watchdog** (`uv pip install watchdog`) - File system event monitoring
- **litequeue** (alternative) - Simple SQLite queue
- **persist-queue** (alternative) - Persistent queue with crash recovery

### Asyncio Approach

- **asyncio** (stdlib) - Native async event loop
- **aiofiles** (`uv pip install aiofiles`) - Async file I/O
- **watchdog** - File system monitoring

### Redis Streams Approach

- **redis** (`uv pip install redis`) - Official Redis Python client
- **walrus** (`uv pip install walrus`) - High-level Redis abstractions

### State Machine Approach

- **transitions** (`uv pip install transitions`) - Lightweight state machine (recommended)
- **python-statemachine** (`uv pip install python-statemachine`) - Alternative implementation

---

## Key Findings from Research

### NATS.io

- Lightweight messaging system with Python client (nats-py)
- **Cannot run embedded** in Python - requires NATS server
- More complex than needed for 2-10 workflows
- Better suited for microservices architectures

### Redis Streams

- Excellent for distributed workflows
- Consumer groups provide robust message delivery
- **Requires Redis server** - adds deployment complexity
- Overkill unless you already have Redis infrastructure

### SQLite Queue Pattern

- **Huey** is most mature with multi-backend support (SQLite, Redis, in-memory)
- **LiteQueue** provides simple queue primitives
- **persist-queue** survives process crashes
- SQLite limitations: Not ideal for high-concurrency writes, but fine for 2-10 workflows

### State Machines

- **transitions** library very mature and well-documented
- Excellent for complex workflows with many states
- Can generate visual diagrams (GraphViz, Mermaid)
- Best combined with task queue (Huey) for async execution

### MCP Servers

- Protocol specification published (2024-2025)
- **Too immature** for production use
- Limited Python implementations
- Revisit in Q2-Q3 2026

### Asyncio Patterns

- Producer-consumer queues are standard pattern
- Event bus implementation is straightforward
- No persistence without additional work
- Perfect for embedded, single-process workflows

---

## Final Recommendation

### Primary: SQLite + Huey + watchdog

**Why:**

- Lowest deployment complexity (single file)
- Mature, battle-tested libraries
- Easy to understand and debug
- Scales from 2 to 10+ workflows smoothly
- Can upgrade to Redis backend later if needed

**Architecture:**

```
File watcher (watchdog) → Huey task queue (SQLite) → Workers → Notifications
```

**Implementation time**: 1-2 days for initial setup

### Alternative 1: State Machine + Huey Hybrid

**Use when:**

- Workflows have complex state dependencies
- Need clear state visualization
- Workflows require approval steps or rollback

### Alternative 2: Pure Asyncio Event Bus

**Use when:**

- Single process, no persistence needed
- Rapid prototyping
- Embedded workflows in larger application
- Zero external dependencies required

### Avoid

- **Redis Streams**: Unless you already have Redis infrastructure
- **MCP Server**: Too immature, revisit Q2-Q3 2026
- **NATS.io**: Requires external server, overkill for this use case

---

## Additional Resources

- Huey Documentation: https://huey.readthedocs.io/en/latest/
- Transitions Documentation: https://github.com/pytransitions/transitions
- Redis Streams Tutorial: https://redis.io/docs/manual/data-types/streams/
- Asyncio Patterns: https://medium.com/data-science-collective/mastering-event-driven-architecture-in-python-with-asyncio-and-pub-sub-patterns-2b26db3f11c9
- Watchdog Documentation: https://python-watchdog.readthedocs.io/
- MCP Specification: https://modelcontextprotocol.io/docs/concepts/architecture

---

**Next Steps**: Review the full OpenAPI specification at [`/Users/terryli/.claude/specifications/lightweight-workflow-orchestration-research.yaml`](/Users/terryli/.claude/specifications/lightweight-workflow-orchestration-research.yaml) for complete implementation examples and detailed analysis.
