# Correlation ID Patterns and Distributed Request Tracing Research

**Research Date**: 2025-10-25
**Context**: Multi-process Python systems with bash hooks, async Python bots, orchestrators, and CLI subprocesses
**Goal**: Trace requests across process boundaries, detect circular dependencies, enable lightweight loop prevention

---

## Executive Summary

This research evaluates correlation ID standards, propagation mechanisms, and circular dependency detection for tracing requests through multi-process systems. Key findings:

- **W3C Trace Context** is the industry standard (128-bit trace ID + 64-bit span ID)
- **Environment variables** are the most Unix-native propagation mechanism
- **ULID** provides best balance of sortability, size, and collision resistance
- **Topological sort with cycle detection** is the standard algorithm for dependency graphs
- **Python's graphlib** provides built-in cycle detection
- **Idempotency tokens** prevent loops better than circuit breakers alone

---

## 1. Correlation ID Standards Comparison

### 1.1 W3C Trace Context (Industry Standard)

**Format**: `traceparent: 00-{trace-id}-{parent-id}-{flags}`

**Components**:

- **Version**: 2 hex digits (currently `00`)
- **Trace ID**: 32 hex digits (128 bits) - globally unique for entire trace
- **Parent ID / Span ID**: 16 hex digits (64 bits) - identifies specific call
- **Trace Flags**: 2 hex digits - sampling flags

**Example**:

```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
```

**Advantages**:

- Standardized by W3C (interoperability across vendors)
- Supported by OpenTelemetry, Datadog, Elastic, Dynatrace
- Built-in parent-child relationship tracking
- HTTP header propagation for distributed systems

**Disadvantages**:

- Designed for HTTP/web services (requires adaptation for bash/subprocess)
- Fixed format (less flexible than custom IDs)

**Use Case**: Best for systems that integrate with APM tools or distributed tracing platforms

---

### 1.2 OpenTelemetry Format

**Format**: Compatible with W3C Trace Context

**Components**:

- **Trace ID**: 128-bit integer (formatted as 32-char hex string)
- **Span ID**: 64-bit integer (formatted as 16-char hex string)

**Python Format**:

```python
trace_id_hex = f'{trace_id:032x}'  # 32 characters
span_id_hex = f'{span_id:016x}'    # 16 characters
```

**Advantages**:

- Native Python support (opentelemetry-api)
- Automatic log injection
- SQLite exporter available
- Built-in parent-child span tracking

**Disadvantages**:

- Requires OpenTelemetry SDK dependency
- More complex than simple UUID

**Use Case**: Python-heavy systems with telemetry requirements

---

### 1.3 UUID v4 (Random)

**Format**: 128-bit identifier, 36 characters with hyphens

**Example**: `550e8400-e29b-41d4-a716-446655440000`

**Generation in Bash**:

```bash
# Method 1: uuidgen command
uuid=$(uuidgen)

# Method 2: Kernel interface
uuid=$(cat /proc/sys/kernel/random/uuid)

# Method 3: Python
uuid=$(python3 -c 'import uuid; print(uuid.uuid4())')
```

**Generation in Python**:

```python
import uuid
correlation_id = str(uuid.uuid4())
```

**Advantages**:

- Simple to generate (built-in tools)
- Universally unique (collision resistance: ~2^122)
- No coordination required
- Widely supported

**Disadvantages**:

- Not sortable by time
- No embedded timestamp
- Larger string representation (36 chars)
- Random ordering (poor database index performance)

**Use Case**: Simple correlation without time-ordering requirements

---

### 1.4 ULID (Universally Unique Lexicographically Sortable Identifier)

**Format**: 128-bit identifier, 26 characters (Base32)

**Structure**:

- **Timestamp**: 48 bits (milliseconds since Unix epoch)
- **Randomness**: 80 bits

**Example**: `01ARZ3NDEKTSV4RRFFQ69G5FAV`

**Generation in Bash**:

```bash
# Basic ULID implementation
timestamp_ms=$(( $(date +%s%3N) ))
timestamp_hex=$(printf '%012x' $timestamp_ms)
random_hex=$(openssl rand -hex 10)
ulid="${timestamp_hex}${random_hex}"
```

**Generation in Python**:

```python
# Using python-ulid library
import ulid
correlation_id = str(ulid.create())

# Or manual implementation
import time
import random
timestamp_ms = int(time.time() * 1000)
random_bits = random.getrandbits(80)
ulid_value = (timestamp_ms << 80) | random_bits
```

**Advantages**:

- **Sortable by time** (critical for request tracing)
- Shorter than UUID (26 vs 36 characters)
- Case-insensitive Base32 encoding
- Embedded timestamp (first 10 chars)
- URL-safe
- 4096 IDs per millisecond (80-bit randomness)

**Disadvantages**:

- Less universal support than UUID
- Requires library or custom implementation

**Use Case**: **RECOMMENDED** for request tracing with temporal ordering

---

### 1.5 Snowflake ID (Twitter's Design)

**Format**: 64-bit integer

**Structure** (customizable):

- **Timestamp**: 41 bits (milliseconds)
- **Machine ID**: 10 bits (datacenter + worker)
- **Sequence**: 12 bits (counter per millisecond)

**Example**: `1234567890123456789` (19 digits)

**Advantages**:

- Most efficient storage (8 bytes)
- Sortable by time
- High throughput (4096 IDs/ms/machine)
- Integer format (efficient indexing)
- Embeds machine ID (origin tracking)

**Disadvantages**:

- Requires machine ID coordination
- Not suitable for bash scripts (no built-in generation)
- 64-bit limit (overflow in ~69 years)
- Collision risk without proper coordination

**Use Case**: High-throughput distributed systems with coordinated machines

---

### 1.6 Comparison Matrix

| Feature | W3C Trace Context | UUID v4 | ULID | Snowflake |
| --- | --- | --- | --- | --- |
| **Size** | 128-bit (32 hex) | 128-bit (36 chars) | 128-bit (26 chars) | 64-bit (19 digits) |
| **Sortable** | No | No | **Yes** | **Yes** |
| **Timestamp** | No | No | **Yes** (48-bit) | **Yes** (41-bit) |
| **Collision Resistance** | High (2^128) | High (2^122) | High (2^80/ms) | Medium (requires coordination) |
| **Bash Generation** | Complex | **Easy** (uuidgen) | Medium | Hard |
| **Python Generation** | Easy (OTel SDK) | **Easy** (stdlib) | Easy (library) | Medium |
| **String Length** | 55 chars (full) | 36 chars | **26 chars** | 19 digits |
| **Parent-Child Tracking** | **Built-in** | No | No | No |
| **Machine ID** | No | No | No | **Yes** (10-bit) |
| **URL-Safe** | No (hyphens) | No (hyphens) | **Yes** | **Yes** |

**Recommendation**: **ULID** for correlation IDs (sortable, compact, easy generation) + **W3C Trace Context format** for parent-child tracking

---

## 2. Cross-Process ID Propagation Mechanisms

### 2.1 Environment Variables (RECOMMENDED)

**Mechanism**: Set environment variable in parent process, inherited by children

**Bash to Python Example**:

```bash
#!/bin/bash
# Generate correlation ID in bash
export CORRELATION_ID=$(uuidgen)
export TRACE_PARENT="00-$(uuidgen | tr -d '-')00000000-$(uuidgen | tr -d '-' | head -c 16)-01"

# Launch Python script (inherits env vars)
python3 orchestrator.py
```

**Python subprocess propagation**:

```python
import os
import subprocess

# Read correlation ID from environment
correlation_id = os.environ.get('CORRELATION_ID')

# Propagate to subprocess (automatic inheritance)
subprocess.run(['claude', 'code'], env=os.environ)

# Or explicit propagation with new child ID
child_env = os.environ.copy()
child_env['PARENT_CORRELATION_ID'] = correlation_id
child_env['CORRELATION_ID'] = generate_new_ulid()
subprocess.run(['some_command'], env=child_env)
```

**Advantages**:

- Native Unix mechanism (POSIX standard)
- Automatic inheritance by default
- No file I/O overhead
- Works across any language (bash, Python, Rust, Go)
- No protocol required

**Disadvantages**:

- Environment space limits (typically 128KB total)
- Can't propagate back to parent
- Global scope (visible to all child processes)

**Best Practices**:

- Use consistent naming: `CORRELATION_ID`, `TRACE_ID`, `SPAN_ID`
- Create new span ID per process: `PARENT_SPAN_ID` + new `SPAN_ID`
- Clean namespace: `TRACE_*` prefix for all tracing variables

---

### 2.2 Command-Line Arguments

**Mechanism**: Pass IDs as CLI flags

**Example**:

```bash
#!/bin/bash
CORRELATION_ID=$(uuidgen)
python3 orchestrator.py --correlation-id "$CORRELATION_ID" --trace-id "$TRACE_ID"
```

**Python**:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--correlation-id', required=True)
parser.add_argument('--trace-id', required=False)
args = parser.parse_args()

# Propagate to subprocess
subprocess.run([
    'claude', 'code',
    '--correlation-id', args.correlation_id
])
```

**Advantages**:

- Explicit (visible in `ps` output)
- Easy to debug (can see IDs in process list)
- Language-agnostic

**Disadvantages**:

- Visible in process list (security risk for sensitive IDs)
- Requires command-line parsing in every process
- Verbose for multiple IDs
- Not suitable for daemons/long-running processes

**Use Case**: One-shot scripts, debugging scenarios

---

### 2.3 File-Based Passing (JSON Metadata)

**Mechanism**: Write correlation context to temporary JSON file

**Bash**:

```bash
#!/bin/bash
CORRELATION_ID=$(uuidgen)
TRACE_FILE=$(mktemp)

cat > "$TRACE_FILE" <<EOF
{
  "correlation_id": "$CORRELATION_ID",
  "trace_id": "$(uuidgen | tr -d '-')",
  "timestamp": "$(date -Iseconds)",
  "process": "bash-hook"
}
EOF

python3 orchestrator.py --trace-file "$TRACE_FILE"
rm -f "$TRACE_FILE"
```

**Python**:

```python
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--trace-file', required=True)
args = parser.parse_args()

with open(args.trace_file) as f:
    trace_context = json.load(f)

correlation_id = trace_context['correlation_id']
```

**Advantages**:

- Can pass complex structured data
- Supports nested contexts
- Atomic writes (rename for safety)
- Can be inspected for debugging

**Disadvantages**:

- File I/O overhead
- Race conditions (requires proper locking)
- Cleanup required (tmpfiles)
- Not suitable for high-frequency tracing

**Use Case**: Complex trace context with metadata

---

### 2.4 stdin/stdout Protocols

**Mechanism**: Pass correlation ID via pipe/stdin

**Bash to Python**:

```bash
#!/bin/bash
echo '{"correlation_id": "'$(uuidgen)'"}' | python3 orchestrator.py
```

**Python**:

```python
import sys
import json

trace_context = json.loads(sys.stdin.read())
correlation_id = trace_context['correlation_id']
```

**Advantages**:

- No file I/O
- Natural for pipeline architectures
- Can stream context updates

**Disadvantages**:

- Requires stdin to be available
- Doesn't work for daemons
- Complex error handling

**Use Case**: Pipeline-style architectures (Unix philosophy)

---

### 2.5 Unix Domain Sockets

**Mechanism**: Pass file descriptors and data via Unix sockets

**Python Example**:

```python
import socket
import os

# Server (parent process)
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind('/tmp/trace.sock')
server.listen(1)

# Client (child process)
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect('/tmp/trace.sock')
client.send(b'{"correlation_id": "..."}')
```

**Advantages**:

- Bidirectional communication
- Can pass file descriptors (SCM_RIGHTS)
- Persistent connection

**Disadvantages**:

- Complex setup
- Requires socket management
- Overkill for simple ID propagation

**Use Case**: Long-running daemon coordination

---

### 2.6 Propagation Mechanism Comparison

| Mechanism | Overhead | Bash Support | Bidirectional | Complexity | Recommended |
| --- | --- | --- | --- | --- | --- |
| **Environment Variables** | **Minimal** | **Excellent** | No | **Low** | **YES** |
| Command-Line Args | Minimal | Excellent | No | Low | For debugging |
| File-Based (JSON) | Medium | Good | Yes | Medium | For complex context |
| stdin/stdout | Low | Good | No | Medium | For pipelines |
| Unix Sockets | Low | Poor | **Yes** | **High** | For daemons |

**Recommendation**: **Environment Variables** for simplicity + **File-Based JSON** for complex trace graphs

---

## 3. Bash-to-Python Integration Patterns

### 3.1 Basic Environment Variable Propagation

**Bash Hook (Stop Hook)**:

```bash
#!/bin/bash
# /path/to/stop-hook.sh

# Generate correlation ID if not already set (prevent loops)
if [ -z "$CORRELATION_ID" ]; then
    export CORRELATION_ID=$(uuidgen)
    export TRACE_ID=$(uuidgen | tr -d '-')00000000
    export SPAN_ID=$(uuidgen | tr -d '-' | head -c 16)
    export PARENT_SPAN_ID=""
else
    # Loop detected - use existing ID but don't propagate further
    echo "WARNING: CORRELATION_ID already set, potential loop detected" >&2
    export LOOP_DETECTED="true"
fi

# Create notification with correlation context
cat > /tmp/notification.json <<EOF
{
    "correlation_id": "$CORRELATION_ID",
    "trace_id": "$TRACE_ID",
    "span_id": "$SPAN_ID",
    "parent_span_id": "$PARENT_SPAN_ID",
    "timestamp": "$(date -Iseconds)",
    "source": "bash-stop-hook"
}
EOF

# Log with correlation ID
echo "[TRACE $CORRELATION_ID] Stop hook triggered" >&2
```

**Python Bot (Async Notification Processor)**:

```python
#!/usr/bin/env python3
import os
import json
import asyncio
import ulid
from pathlib import Path

async def process_notification(notification_file: Path):
    """Process notification from stop hook"""
    with open(notification_file) as f:
        notification = json.load(f)

    # Extract correlation context
    correlation_id = notification['correlation_id']
    trace_id = notification['trace_id']
    parent_span_id = notification['span_id']

    # Create new span for bot processing
    span_id = str(ulid.create())[:16]

    # Log with correlation context
    log_with_trace(
        correlation_id, trace_id, span_id,
        "Bot processing notification",
        parent_span_id=parent_span_id
    )

    # Create approval with propagated context
    approval = {
        "correlation_id": correlation_id,
        "trace_id": trace_id,
        "span_id": str(ulid.create())[:16],  # New span for approval
        "parent_span_id": span_id,
        "timestamp": datetime.now().isoformat(),
        "source": "python-bot",
        "action": "approval_created"
    }

    with open('/tmp/approval.json', 'w') as f:
        json.dump(approval, f)

    log_with_trace(
        correlation_id, trace_id, span_id,
        "Approval created",
        parent_span_id=parent_span_id
    )

def log_with_trace(correlation_id, trace_id, span_id, message, **kwargs):
    """Structured logging with trace context"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "correlation_id": correlation_id,
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": kwargs.get('parent_span_id'),
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry))
```

**Python Orchestrator (Approval Processor)**:

```python
#!/usr/bin/env python3
import os
import json
import subprocess
from pathlib import Path

def process_approval(approval_file: Path):
    """Process approval and launch Claude CLI"""
    with open(approval_file) as f:
        approval = json.load(f)

    # Extract correlation context
    correlation_id = approval['correlation_id']
    trace_id = approval['trace_id']
    parent_span_id = approval['span_id']

    # Create new span for orchestrator
    span_id = str(ulid.create())[:16]

    log_with_trace(
        correlation_id, trace_id, span_id,
        "Orchestrator launching Claude CLI",
        parent_span_id=parent_span_id
    )

    # Propagate correlation context to subprocess
    env = os.environ.copy()
    env['CORRELATION_ID'] = correlation_id
    env['TRACE_ID'] = trace_id
    env['SPAN_ID'] = str(ulid.create())[:16]  # New span for CLI
    env['PARENT_SPAN_ID'] = span_id

    # Check for circular dependency BEFORE launching
    if is_circular_dependency(correlation_id, trace_id):
        log_with_trace(
            correlation_id, trace_id, span_id,
            "ERROR: Circular dependency detected, aborting",
            parent_span_id=parent_span_id,
            level="ERROR"
        )
        return

    # Launch Claude CLI with propagated context
    subprocess.run(['claude', 'code'], env=env)

    log_with_trace(
        correlation_id, trace_id, span_id,
        "Claude CLI completed",
        parent_span_id=parent_span_id
    )

def is_circular_dependency(correlation_id: str, trace_id: str) -> bool:
    """Check if this request would create a circular dependency"""
    # Load request graph from SQLite
    # Check for cycles using topological sort
    # Return True if cycle detected
    pass  # Implementation in section 4
```

---

### 3.2 Extracting IDs from JSON Input

**Python Pattern**:

```python
import json
import os
import sys
from typing import Optional, Dict

def extract_trace_context(
    json_file: Optional[str] = None,
    json_stdin: bool = False
) -> Dict[str, str]:
    """
    Extract correlation context from multiple sources
    Priority: JSON file > stdin > environment variables
    """
    context = {}

    # Priority 1: JSON file
    if json_file:
        with open(json_file) as f:
            data = json.load(f)
            context = {
                'correlation_id': data.get('correlation_id'),
                'trace_id': data.get('trace_id'),
                'span_id': data.get('span_id'),
                'parent_span_id': data.get('parent_span_id')
            }

    # Priority 2: stdin
    elif json_stdin and not sys.stdin.isatty():
        data = json.load(sys.stdin)
        context = {
            'correlation_id': data.get('correlation_id'),
            'trace_id': data.get('trace_id'),
            'span_id': data.get('span_id'),
            'parent_span_id': data.get('parent_span_id')
        }

    # Priority 3: Environment variables
    else:
        context = {
            'correlation_id': os.environ.get('CORRELATION_ID'),
            'trace_id': os.environ.get('TRACE_ID'),
            'span_id': os.environ.get('SPAN_ID'),
            'parent_span_id': os.environ.get('PARENT_SPAN_ID')
        }

    # Generate missing IDs
    if not context['correlation_id']:
        context['correlation_id'] = str(ulid.create())
    if not context['trace_id']:
        context['trace_id'] = str(ulid.create())
    if not context['span_id']:
        context['span_id'] = str(ulid.create())[:16]

    return context
```

---

### 3.3 Propagating to Subprocesses

**Pattern for Creating Child Spans**:

```python
import subprocess
import ulid

def spawn_subprocess_with_trace(
    command: list,
    correlation_id: str,
    trace_id: str,
    parent_span_id: str
) -> subprocess.CompletedProcess:
    """
    Spawn subprocess with proper trace context propagation
    Creates new span ID for child process
    """
    # Create new span for subprocess
    child_span_id = str(ulid.create())[:16]

    # Prepare environment with trace context
    env = os.environ.copy()
    env['CORRELATION_ID'] = correlation_id
    env['TRACE_ID'] = trace_id
    env['SPAN_ID'] = child_span_id
    env['PARENT_SPAN_ID'] = parent_span_id

    # Log span creation
    log_span_start(
        correlation_id=correlation_id,
        trace_id=trace_id,
        span_id=child_span_id,
        parent_span_id=parent_span_id,
        operation=f"subprocess: {' '.join(command)}"
    )

    # Execute subprocess
    result = subprocess.run(command, env=env, capture_output=True)

    # Log span completion
    log_span_end(
        correlation_id=correlation_id,
        trace_id=trace_id,
        span_id=child_span_id,
        return_code=result.returncode
    )

    return result
```

---

## 4. Circular Dependency Detection Algorithms

### 4.1 Request Graph Construction

**SQLite Schema for Tracing**:

```sql
-- Correlation ID table (one per request flow)
CREATE TABLE correlation_contexts (
    correlation_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    root_span_id TEXT,
    completed BOOLEAN DEFAULT FALSE
);

-- Span table (one per process/operation)
CREATE TABLE spans (
    span_id TEXT PRIMARY KEY,
    correlation_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    parent_span_id TEXT,  -- NULL for root spans
    operation TEXT NOT NULL,
    source TEXT NOT NULL,  -- 'bash-hook', 'python-bot', 'orchestrator', 'claude-cli'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT CHECK(status IN ('running', 'completed', 'failed')),
    metadata JSON,
    FOREIGN KEY (correlation_id) REFERENCES correlation_contexts(correlation_id),
    FOREIGN KEY (parent_span_id) REFERENCES spans(span_id)
);

-- Dependency edges (for graph analysis)
CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_span_id TEXT NOT NULL,
    to_span_id TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_span_id) REFERENCES spans(span_id),
    FOREIGN KEY (to_span_id) REFERENCES spans(span_id),
    FOREIGN KEY (correlation_id) REFERENCES correlation_contexts(correlation_id),
    UNIQUE(from_span_id, to_span_id)
);

-- Indexes for fast graph traversal
CREATE INDEX idx_spans_correlation ON spans(correlation_id);
CREATE INDEX idx_spans_parent ON spans(parent_span_id);
CREATE INDEX idx_spans_source ON spans(source);
CREATE INDEX idx_dependencies_correlation ON dependencies(correlation_id);
CREATE INDEX idx_dependencies_from ON dependencies(from_span_id);
CREATE INDEX idx_dependencies_to ON dependencies(to_span_id);
```

---

### 4.2 Topological Sort with Cycle Detection (Kahn's Algorithm)

**Python Implementation**:

```python
from collections import defaultdict, deque
from typing import List, Dict, Set, Optional

def detect_circular_dependency(
    correlation_id: str,
    db_path: str = "~/.claude/traces.db"
) -> tuple[bool, Optional[List[str]]]:
    """
    Detect circular dependencies using Kahn's algorithm (topological sort)

    Returns:
        (has_cycle, cycle_path)
        - has_cycle: True if cycle detected
        - cycle_path: List of span IDs forming the cycle (if detected)
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build dependency graph for this correlation ID
    cursor.execute("""
        SELECT from_span_id, to_span_id
        FROM dependencies
        WHERE correlation_id = ?
    """, (correlation_id,))

    edges = cursor.fetchall()
    conn.close()

    # Build adjacency list and in-degree count
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()

    for from_span, to_span in edges:
        graph[from_span].append(to_span)
        in_degree[to_span] += 1
        all_nodes.add(from_span)
        all_nodes.add(to_span)

    # Initialize queue with nodes that have no dependencies
    queue = deque([node for node in all_nodes if in_degree[node] == 0])
    sorted_order = []

    # Kahn's algorithm
    while queue:
        node = queue.popleft()
        sorted_order.append(node)

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If sorted_order doesn't contain all nodes, there's a cycle
    has_cycle = len(sorted_order) != len(all_nodes)

    if has_cycle:
        # Find the cycle path using DFS
        cycle_path = find_cycle_path(graph, all_nodes, sorted_order)
        return True, cycle_path

    return False, None


def find_cycle_path(
    graph: Dict[str, List[str]],
    all_nodes: Set[str],
    processed_nodes: List[str]
) -> List[str]:
    """
    Find a cycle path using DFS with white-grey-black states

    States:
        - WHITE (0): Not visited
        - GREY (1): Being processed (in current DFS path)
        - BLACK (2): Fully processed
    """
    WHITE, GREY, BLACK = 0, 1, 2
    state = {node: WHITE for node in all_nodes}
    parent = {}
    cycle = []

    def dfs(node: str) -> bool:
        """Returns True if cycle found"""
        state[node] = GREY

        for neighbor in graph.get(node, []):
            if state[neighbor] == GREY:
                # Cycle detected! Reconstruct path
                cycle.append(neighbor)
                current = node
                while current != neighbor:
                    cycle.append(current)
                    current = parent.get(current)
                cycle.append(neighbor)  # Complete the cycle
                cycle.reverse()
                return True

            if state[neighbor] == WHITE:
                parent[neighbor] = node
                if dfs(neighbor):
                    return True

        state[node] = BLACK
        return False

    # Find cycle starting from unprocessed nodes
    unprocessed = all_nodes - set(processed_nodes)
    for node in unprocessed:
        if state[node] == WHITE:
            if dfs(node):
                return cycle

    return []
```

---

### 4.3 DFS-Based Cycle Detection (Alternative)

**Python Implementation Using graphlib (Python 3.9+)**:

```python
from graphlib import TopologicalSorter, CycleError
import sqlite3

def detect_cycle_graphlib(
    correlation_id: str,
    db_path: str = "~/.claude/traces.db"
) -> tuple[bool, Optional[str]]:
    """
    Detect cycles using Python's built-in graphlib
    Simpler but less detailed than manual implementation

    Returns:
        (has_cycle, error_message)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build dependency graph
    cursor.execute("""
        SELECT from_span_id, to_span_id
        FROM dependencies
        WHERE correlation_id = ?
    """, (correlation_id,))

    edges = cursor.fetchall()
    conn.close()

    # Build dependency dict (predecessors for each node)
    graph = defaultdict(set)
    for from_span, to_span in edges:
        graph[to_span].add(from_span)

    # TopologicalSorter automatically detects cycles
    ts = TopologicalSorter(graph)

    try:
        # This will raise CycleError if cycle exists
        sorted_nodes = list(ts.static_order())
        return False, None
    except CycleError as e:
        return True, str(e)
```

---

### 4.4 Loop Prevention Strategies

#### 4.4.1 Idempotency Tokens

**Concept**: Each operation gets a unique idempotency key that prevents duplicate execution

**Implementation**:

```python
import hashlib
import json
import sqlite3

def generate_idempotency_key(
    correlation_id: str,
    operation: str,
    parameters: dict
) -> str:
    """
    Generate deterministic idempotency key for operation
    Same inputs = same key = prevents duplicate execution
    """
    payload = {
        'correlation_id': correlation_id,
        'operation': operation,
        'parameters': parameters
    }
    payload_json = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(payload_json.encode()).hexdigest()


def execute_with_idempotency(
    correlation_id: str,
    operation: str,
    parameters: dict,
    execute_func: callable,
    db_path: str = "~/.claude/traces.db"
):
    """
    Execute operation only if idempotency key hasn't been seen
    """
    idempotency_key = generate_idempotency_key(
        correlation_id, operation, parameters
    )

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if operation already executed
    cursor.execute("""
        SELECT executed_at, result
        FROM idempotent_operations
        WHERE idempotency_key = ?
    """, (idempotency_key,))

    existing = cursor.fetchone()

    if existing:
        # Operation already executed, return cached result
        executed_at, result = existing
        conn.close()
        return json.loads(result) if result else None

    # Execute operation
    result = execute_func()

    # Store execution record
    cursor.execute("""
        INSERT INTO idempotent_operations
            (idempotency_key, correlation_id, operation, parameters, result)
        VALUES (?, ?, ?, ?, ?)
    """, (
        idempotency_key,
        correlation_id,
        operation,
        json.dumps(parameters),
        json.dumps(result)
    ))

    conn.commit()
    conn.close()

    return result

# Schema addition:
"""
CREATE TABLE idempotent_operations (
    idempotency_key TEXT PRIMARY KEY,
    correlation_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    parameters JSON NOT NULL,
    result JSON,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
```

---

#### 4.4.2 Circuit Breaker Pattern

**Concept**: Prevent cascading failures by breaking the circuit after N failures

**Implementation**:

```python
import time
from enum import Enum
from typing import Optional

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failures detected, stop trying
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,  # seconds
        db_path: str = "~/.claude/traces.db"
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.db_path = db_path

    def get_state(self, circuit_name: str) -> CircuitState:
        """Get current circuit state from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT state, failure_count, last_failure_time
            FROM circuit_breakers
            WHERE name = ?
        """, (circuit_name,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return CircuitState.CLOSED

        state, failure_count, last_failure_time = row

        # Check if timeout expired (transition OPEN -> HALF_OPEN)
        if state == CircuitState.OPEN.value:
            if time.time() - last_failure_time > self.timeout:
                return CircuitState.HALF_OPEN

        return CircuitState(state)

    def record_success(self, circuit_name: str):
        """Record successful operation, reset circuit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO circuit_breakers (name, state, failure_count)
            VALUES (?, ?, 0)
            ON CONFLICT(name) DO UPDATE SET
                state = ?,
                failure_count = 0
        """, (circuit_name, CircuitState.CLOSED.value, CircuitState.CLOSED.value))

        conn.commit()
        conn.close()

    def record_failure(self, circuit_name: str):
        """Record failure, potentially open circuit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO circuit_breakers
                (name, state, failure_count, last_failure_time)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(name) DO UPDATE SET
                failure_count = failure_count + 1,
                last_failure_time = ?,
                state = CASE
                    WHEN failure_count + 1 >= ?
                    THEN ?
                    ELSE state
                END
        """, (
            circuit_name,
            CircuitState.CLOSED.value,
            time.time(),
            time.time(),
            self.failure_threshold,
            CircuitState.OPEN.value
        ))

        conn.commit()
        conn.close()

    def call(self, circuit_name: str, func: callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        state = self.get_state(circuit_name)

        if state == CircuitState.OPEN:
            raise Exception(f"Circuit breaker OPEN for {circuit_name}")

        try:
            result = func(*args, **kwargs)
            self.record_success(circuit_name)
            return result
        except Exception as e:
            self.record_failure(circuit_name)
            raise

# Schema addition:
"""
CREATE TABLE circuit_breakers (
    name TEXT PRIMARY KEY,
    state TEXT CHECK(state IN ('closed', 'open', 'half_open')),
    failure_count INTEGER DEFAULT 0,
    last_failure_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
```

---

#### 4.4.3 Request Depth Limiting

**Simple Loop Prevention**:

```python
def check_request_depth(
    correlation_id: str,
    max_depth: int = 10,
    db_path: str = "~/.claude/traces.db"
) -> tuple[bool, int]:
    """
    Check if request has exceeded maximum depth (simple cycle prevention)

    Returns:
        (is_valid, current_depth)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count spans in this correlation chain
    cursor.execute("""
        SELECT COUNT(*) FROM spans
        WHERE correlation_id = ?
    """, (correlation_id,))

    depth = cursor.fetchone()[0]
    conn.close()

    return depth < max_depth, depth
```

---

## 5. Lightweight Tracing Libraries

### 5.1 OpenTelemetry with SQLite Exporter

**Installation**:

```bash
pip install opentelemetry-api opentelemetry-sdk
```

**Configuration for Offline Tracing**:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
import sqlite3
import json

class SQLiteSpanExporter:
    """Custom SQLite exporter for OpenTelemetry"""

    def __init__(self, db_path: str = "~/.claude/traces.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otel_spans (
                trace_id TEXT NOT NULL,
                span_id TEXT NOT NULL,
                parent_span_id TEXT,
                name TEXT NOT NULL,
                start_time INTEGER NOT NULL,
                end_time INTEGER,
                attributes JSON,
                status_code TEXT,
                PRIMARY KEY (trace_id, span_id)
            )
        """)

        conn.commit()
        conn.close()

    def export(self, spans):
        """Export spans to SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for span in spans:
            cursor.execute("""
                INSERT OR REPLACE INTO otel_spans
                    (trace_id, span_id, parent_span_id, name,
                     start_time, end_time, attributes, status_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                format(span.context.trace_id, '032x'),
                format(span.context.span_id, '016x'),
                format(span.parent.span_id, '016x') if span.parent else None,
                span.name,
                span.start_time,
                span.end_time,
                json.dumps(dict(span.attributes)),
                span.status.status_code.name
            ))

        conn.commit()
        conn.close()

        return True  # Success

    def shutdown(self):
        """Cleanup resources"""
        pass

# Setup tracer
resource = Resource.create({"service.name": "claude-orchestrator"})
provider = TracerProvider(resource=resource)
exporter = SQLiteSpanExporter()
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Usage
with tracer.start_as_current_span("process_notification") as span:
    span.set_attribute("correlation_id", correlation_id)
    span.set_attribute("notification_type", "stop_hook")
    # ... do work ...
```

**Advantages**:

- Industry standard API
- Automatic context propagation
- Rich instrumentation
- SQLite for offline storage

**Disadvantages**:

- Heavier dependency
- Requires SDK setup
- Overkill for simple tracing

---

### 5.2 Custom Lightweight Tracer

**Minimal Implementation**:

```python
import json
import sqlite3
import time
import ulid
from contextlib import contextmanager
from typing import Optional

class LightweightTracer:
    """Minimal tracer for correlation ID tracking"""

    def __init__(self, db_path: str = "~/.claude/traces.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite schema (same as section 4.1)"""
        # Use schema from section 4.1
        pass

    @contextmanager
    def span(
        self,
        operation: str,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None
    ):
        """
        Context manager for span tracking

        Usage:
            with tracer.span("process_notification", correlation_id=cid):
                # ... do work ...
        """
        # Generate IDs if not provided
        if not correlation_id:
            correlation_id = str(ulid.create())
        if not trace_id:
            trace_id = str(ulid.create())

        span_id = str(ulid.create())[:16]
        start_time = time.time()

        # Log span start
        self._log_span_start(
            correlation_id, trace_id, span_id,
            parent_span_id, operation
        )

        span_context = {
            'correlation_id': correlation_id,
            'trace_id': trace_id,
            'span_id': span_id,
            'parent_span_id': parent_span_id
        }

        try:
            yield span_context
            status = 'completed'
        except Exception as e:
            status = 'failed'
            span_context['error'] = str(e)
            raise
        finally:
            # Log span end
            self._log_span_end(
                span_id, status, time.time() - start_time
            )

    def _log_span_start(
        self, correlation_id, trace_id, span_id,
        parent_span_id, operation
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO spans
                (span_id, correlation_id, trace_id, parent_span_id,
                 operation, status, started_at)
            VALUES (?, ?, ?, ?, ?, 'running', CURRENT_TIMESTAMP)
        """, (span_id, correlation_id, trace_id, parent_span_id, operation))

        if parent_span_id:
            cursor.execute("""
                INSERT OR IGNORE INTO dependencies
                    (from_span_id, to_span_id, correlation_id)
                VALUES (?, ?, ?)
            """, (parent_span_id, span_id, correlation_id))

        conn.commit()
        conn.close()

    def _log_span_end(self, span_id, status, duration):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE spans
            SET status = ?, completed_at = CURRENT_TIMESTAMP,
                metadata = json_set(COALESCE(metadata, '{}'), '$.duration', ?)
            WHERE span_id = ?
        """, (status, duration, span_id))

        conn.commit()
        conn.close()

# Usage
tracer = LightweightTracer()

with tracer.span("orchestrator.launch_cli", correlation_id=cid) as span:
    subprocess.run(['claude', 'code'])
```

---

## 6. Reference Patterns from Production Systems

### 6.1 systemd Dependency Tracking

**Key Concepts**:

- **Requirement Dependencies**: `Requires=`, `Wants=`, `Requisite=`
- **Ordering Dependencies**: `After=`, `Before=`
- **Cycle Handling**: systemd breaks cycles arbitrarily (not auto-resolved)

**Analysis Tools**:

```bash
# View dependency tree
systemctl list-dependencies SERVICE_NAME

# Generate GraphViz dot file
systemd-analyze dot | dot -Tpng -o deps.png

# Show critical chain (time-ordered)
systemd-analyze critical-chain
```

**Lessons**:

- Separate ordering from requirements
- Provide tools for visualization
- Document that cycles are invalid (must be manually resolved)

---

### 6.2 Make Build System

**Algorithm**: Depth-First Search with timestamp checking

**Key Concepts**:

- **Targets**: Nodes in dependency graph
- **Prerequisites**: Edges in graph
- **Timestamps**: Determine if rebuild needed

**Cycle Handling**: Make doesn't allow circular dependencies (results in error)

**Visualization**:

```bash
# Using makefile2graph
make -Bnd | make2graph | dot -Tpng -o makefile.png
```

**Lessons**:

- DFS traversal for dependency resolution
- Timestamp-based change detection
- Explicit error on circular dependencies

---

### 6.3 CI/CD Job Dependency Graphs

**GitLab CI `needs` Keyword**:

```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script: make build

test:
  stage: test
  needs: [build] # Explicit dependency
  script: make test

deploy:
  stage: deploy
  needs: [test]
  script: make deploy
```

**GitHub Actions `needs` Keyword**:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: make build

  test:
    needs: build # Wait for build to complete
    runs-on: ubuntu-latest
    steps:
      - run: make test
```

**Lessons**:

- Explicit `needs` keyword for dependencies
- Visual pipeline graphs for debugging
- Parallel execution where possible
- Fail-fast on circular dependencies

---

## 7. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     CORRELATION ID FLOW                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   Bash Hook      │  Generate: CORRELATION_ID, TRACE_ID, SPAN_ID
│   (Stop Hook)    │  Export: Environment variables
└────────┬─────────┘
         │ ENV: CORRELATION_ID=<ulid>
         │      TRACE_ID=<ulid>
         │      SPAN_ID=<ulid-16>
         │      PARENT_SPAN_ID=""
         │
         │ Creates: /tmp/notification.json
         │
         ▼
┌──────────────────┐
│   Python Bot     │  Read: notification.json
│   (Async)        │  Extract: correlation context
└────────┬─────────┘  Create: New SPAN_ID (child)
         │ ENV: CORRELATION_ID=<same>
         │      TRACE_ID=<same>
         │      SPAN_ID=<new-ulid-16>
         │      PARENT_SPAN_ID=<hook-span-id>
         │
         │ Creates: /tmp/approval.json
         │
         ▼
┌──────────────────┐
│  Orchestrator    │  Read: approval.json
│   (Python)       │  Extract: correlation context
└────────┬─────────┘  Check: Circular dependency?
         │            Create: New SPAN_ID (child)
         │
         │ ┌──────────────────────────────┐
         │ │  CYCLE CHECK (BEFORE SPAWN)  │
         │ │  1. Load dependency graph    │
         │ │  2. Run topological sort     │
         │ │  3. If cycle: ABORT          │
         │ └──────────────────────────────┘
         │
         │ ENV: CORRELATION_ID=<same>
         │      TRACE_ID=<same>
         │      SPAN_ID=<new-ulid-16>
         │      PARENT_SPAN_ID=<bot-span-id>
         │
         ▼
┌──────────────────┐
│   Claude CLI     │  Inherit: Environment variables
│   (Subprocess)   │  Check: CORRELATION_ID already set?
└────────┬─────────┘  If set: LOOP DETECTED → log warning
         │
         │ Triggers stop hook again...
         │
         ▼
┌──────────────────┐
│   Bash Hook      │  Check: CORRELATION_ID env var
│   (Loop!)        │  If exists: ABORT (loop detected)
└──────────────────┘  Log: "Loop prevented"


┌─────────────────────────────────────────────────────────────────┐
│                     SQLITE TRACE DATABASE                       │
└─────────────────────────────────────────────────────────────────┘

correlation_contexts          spans                    dependencies
┌─────────────────┐          ┌──────────────┐         ┌──────────────┐
│ correlation_id  │◄─────────│ span_id      │         │ from_span_id │
│ trace_id        │          │ correlation  │─────────│ to_span_id   │
│ root_span_id    │          │ trace_id     │         │ correlation  │
│ created_at      │          │ parent_span  │         └──────────────┘
│ completed       │          │ operation    │
└─────────────────┘          │ source       │
                             │ started_at   │
                             │ completed_at │
                             │ status       │
                             └──────────────┘

Query for cycle detection:
  SELECT from_span_id, to_span_id
  FROM dependencies
  WHERE correlation_id = ?

  → Build graph → Topological sort → Detect cycle
```

---

## 8. Complete SQLite Schema

```sql
-- Drop existing tables (for clean setup)
DROP TABLE IF EXISTS dependencies;
DROP TABLE IF EXISTS spans;
DROP TABLE IF EXISTS correlation_contexts;
DROP TABLE IF EXISTS idempotent_operations;
DROP TABLE IF EXISTS circuit_breakers;
DROP TABLE IF EXISTS otel_spans;

-- Correlation contexts (one per request flow)
CREATE TABLE correlation_contexts (
    correlation_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL UNIQUE,
    root_span_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE,
    metadata JSON
);

-- Spans (one per process/operation)
CREATE TABLE spans (
    span_id TEXT PRIMARY KEY,
    correlation_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    parent_span_id TEXT,  -- NULL for root spans
    operation TEXT NOT NULL,
    source TEXT NOT NULL,  -- 'bash-hook', 'python-bot', 'orchestrator', 'claude-cli'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds REAL,
    status TEXT CHECK(status IN ('running', 'completed', 'failed', 'aborted')) DEFAULT 'running',
    error_message TEXT,
    metadata JSON,

    FOREIGN KEY (correlation_id) REFERENCES correlation_contexts(correlation_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_span_id) REFERENCES spans(span_id) ON DELETE SET NULL
);

-- Dependency edges (for graph analysis)
CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_span_id TEXT NOT NULL,  -- Parent span
    to_span_id TEXT NOT NULL,    -- Child span
    correlation_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (from_span_id) REFERENCES spans(span_id) ON DELETE CASCADE,
    FOREIGN KEY (to_span_id) REFERENCES spans(span_id) ON DELETE CASCADE,
    FOREIGN KEY (correlation_id) REFERENCES correlation_contexts(correlation_id) ON DELETE CASCADE,

    UNIQUE(from_span_id, to_span_id)
);

-- Idempotent operations (loop prevention)
CREATE TABLE idempotent_operations (
    idempotency_key TEXT PRIMARY KEY,
    correlation_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    parameters JSON NOT NULL,
    result JSON,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (correlation_id) REFERENCES correlation_contexts(correlation_id) ON DELETE CASCADE
);

-- Circuit breakers (failure protection)
CREATE TABLE circuit_breakers (
    name TEXT PRIMARY KEY,
    state TEXT CHECK(state IN ('closed', 'open', 'half_open')) DEFAULT 'closed',
    failure_count INTEGER DEFAULT 0,
    last_failure_time REAL,
    last_success_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OpenTelemetry spans (if using OTel SDK)
CREATE TABLE otel_spans (
    trace_id TEXT NOT NULL,
    span_id TEXT NOT NULL,
    parent_span_id TEXT,
    name TEXT NOT NULL,
    start_time INTEGER NOT NULL,  -- nanoseconds since epoch
    end_time INTEGER,
    attributes JSON,
    status_code TEXT CHECK(status_code IN ('UNSET', 'OK', 'ERROR')),

    PRIMARY KEY (trace_id, span_id)
);

-- Indexes for fast graph traversal
CREATE INDEX idx_spans_correlation ON spans(correlation_id);
CREATE INDEX idx_spans_parent ON spans(parent_span_id);
CREATE INDEX idx_spans_source ON spans(source);
CREATE INDEX idx_spans_status ON spans(status);
CREATE INDEX idx_spans_started ON spans(started_at);

CREATE INDEX idx_dependencies_correlation ON dependencies(correlation_id);
CREATE INDEX idx_dependencies_from ON dependencies(from_span_id);
CREATE INDEX idx_dependencies_to ON dependencies(to_span_id);

CREATE INDEX idx_idempotent_correlation ON idempotent_operations(correlation_id);
CREATE INDEX idx_idempotent_executed ON idempotent_operations(executed_at);

CREATE INDEX idx_otel_trace ON otel_spans(trace_id);
CREATE INDEX idx_otel_parent ON otel_spans(parent_span_id);

-- Views for common queries

-- View: Active spans (currently running)
CREATE VIEW active_spans AS
SELECT
    s.span_id,
    s.correlation_id,
    s.operation,
    s.source,
    s.started_at,
    ROUND((julianday('now') - julianday(s.started_at)) * 86400, 2) AS running_seconds
FROM spans s
WHERE s.status = 'running'
ORDER BY s.started_at;

-- View: Request traces (full correlation chain)
CREATE VIEW request_traces AS
SELECT
    cc.correlation_id,
    cc.trace_id,
    COUNT(s.span_id) AS span_count,
    MIN(s.started_at) AS first_span_started,
    MAX(s.completed_at) AS last_span_completed,
    SUM(CASE WHEN s.status = 'failed' THEN 1 ELSE 0 END) AS failed_spans,
    SUM(CASE WHEN s.status = 'running' THEN 1 ELSE 0 END) AS running_spans
FROM correlation_contexts cc
LEFT JOIN spans s ON cc.correlation_id = s.correlation_id
GROUP BY cc.correlation_id, cc.trace_id;

-- View: Dependency graph edges
CREATE VIEW dependency_graph AS
SELECT
    d.correlation_id,
    s1.operation AS from_operation,
    s1.source AS from_source,
    s2.operation AS to_operation,
    s2.source AS to_source,
    d.from_span_id,
    d.to_span_id
FROM dependencies d
JOIN spans s1 ON d.from_span_id = s1.span_id
JOIN spans s2 ON d.to_span_id = s2.span_id;
```

---

## 9. Code Examples

### 9.1 Bash: Generate and Propagate Correlation ID

```bash
#!/bin/bash
# /path/to/bash-hook.sh

set -euo pipefail

# Configuration
TRACE_DB="$HOME/.claude/traces.db"
LOG_FILE="$HOME/.claude/trace.log"

# Functions
generate_ulid() {
    # Simple ULID: timestamp (10 chars) + random (16 chars)
    timestamp_ms=$(( $(date +%s) * 1000 ))
    timestamp_b32=$(printf '%010s' $(echo "obase=32; $timestamp_ms" | bc))
    random_b32=$(openssl rand -base64 12 | tr -d '/+=' | head -c 16)
    echo "${timestamp_b32}${random_b32}" | tr '[:lower:]' '[:upper:]'
}

generate_span_id() {
    # 16-character hex span ID
    openssl rand -hex 8
}

log_with_trace() {
    local level="$1"
    shift
    local message="$*"

    local log_entry
    log_entry=$(cat <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "level": "$level",
  "correlation_id": "${CORRELATION_ID:-}",
  "trace_id": "${TRACE_ID:-}",
  "span_id": "${SPAN_ID:-}",
  "parent_span_id": "${PARENT_SPAN_ID:-}",
  "source": "bash-hook",
  "message": "$message"
}
EOF
)
    echo "$log_entry" >> "$LOG_FILE"
    echo "[$level] $message" >&2
}

# Main logic

# Check for loop: if CORRELATION_ID already set, we're in a loop
if [ -n "${CORRELATION_ID:-}" ]; then
    log_with_trace "ERROR" "Loop detected: CORRELATION_ID already set ($CORRELATION_ID)"

    # Record loop event in database
    sqlite3 "$TRACE_DB" <<SQL
INSERT INTO spans (span_id, correlation_id, trace_id, operation, source, status, error_message)
VALUES (
    '$(generate_span_id)',
    '$CORRELATION_ID',
    '${TRACE_ID:-}',
    'loop-detected',
    'bash-hook',
    'aborted',
    'Circular dependency detected'
);
SQL

    exit 1
fi

# Generate correlation context
export CORRELATION_ID=$(generate_ulid)
export TRACE_ID=$(generate_ulid)
export SPAN_ID=$(generate_span_id)
export PARENT_SPAN_ID=""

log_with_trace "INFO" "Generated new correlation context"

# Record span in database
sqlite3 "$TRACE_DB" <<SQL
INSERT INTO correlation_contexts (correlation_id, trace_id, root_span_id)
VALUES ('$CORRELATION_ID', '$TRACE_ID', '$SPAN_ID');

INSERT INTO spans (span_id, correlation_id, trace_id, operation, source, status)
VALUES ('$SPAN_ID', '$CORRELATION_ID', '$TRACE_ID', 'stop-hook-triggered', 'bash-hook', 'running');
SQL

# Create notification with trace context
NOTIFICATION_FILE="/tmp/notification-${CORRELATION_ID}.json"
cat > "$NOTIFICATION_FILE" <<EOF
{
  "correlation_id": "$CORRELATION_ID",
  "trace_id": "$TRACE_ID",
  "span_id": "$SPAN_ID",
  "parent_span_id": "$PARENT_SPAN_ID",
  "timestamp": "$(date -Iseconds)",
  "source": "bash-hook",
  "event": "stop-hook-triggered"
}
EOF

log_with_trace "INFO" "Created notification: $NOTIFICATION_FILE"

# Mark span as completed
sqlite3 "$TRACE_DB" <<SQL
UPDATE spans
SET status = 'completed', completed_at = CURRENT_TIMESTAMP
WHERE span_id = '$SPAN_ID';
SQL

log_with_trace "INFO" "Stop hook completed successfully"
```

---

### 9.2 Python: Extract and Propagate Correlation IDs

```python
#!/usr/bin/env python3
"""
Orchestrator: Process approvals and launch Claude CLI with trace propagation
"""

import os
import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Configuration
TRACE_DB = Path.home() / ".claude" / "traces.db"
LOG_FILE = Path.home() / ".claude" / "trace.log"

def generate_ulid() -> str:
    """Generate ULID (simplified implementation)"""
    import time
    import random
    timestamp = int(time.time() * 1000)
    random_bits = random.getrandbits(80)
    # Base32 encoding simplified
    return f"{timestamp:013x}{random_bits:020x}".upper()[:26]

def generate_span_id() -> str:
    """Generate 16-character hex span ID"""
    import random
    return f"{random.getrandbits(64):016x}"

def log_with_trace(
    correlation_id: str,
    trace_id: str,
    span_id: str,
    level: str,
    message: str,
    parent_span_id: Optional[str] = None,
    **kwargs
):
    """Structured logging with trace context"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "correlation_id": correlation_id,
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "source": "orchestrator",
        "message": message,
        **kwargs
    }

    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    print(f"[{level}] {message}", file=sys.stderr)

def extract_trace_context(notification_file: Path) -> Dict[str, str]:
    """Extract correlation context from notification JSON"""
    with open(notification_file) as f:
        notification = json.load(f)

    return {
        'correlation_id': notification['correlation_id'],
        'trace_id': notification['trace_id'],
        'span_id': notification['span_id'],
        'parent_span_id': notification.get('parent_span_id')
    }

def detect_circular_dependency(
    correlation_id: str,
    db_path: Path = TRACE_DB
) -> tuple[bool, Optional[list]]:
    """
    Detect circular dependencies using Kahn's algorithm
    Returns (has_cycle, cycle_path)
    """
    from collections import defaultdict, deque

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build dependency graph
    cursor.execute("""
        SELECT from_span_id, to_span_id
        FROM dependencies
        WHERE correlation_id = ?
    """, (correlation_id,))

    edges = cursor.fetchall()
    conn.close()

    if not edges:
        return False, None

    # Build adjacency list and in-degree
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()

    for from_span, to_span in edges:
        graph[from_span].append(to_span)
        in_degree[to_span] += 1
        all_nodes.add(from_span)
        all_nodes.add(to_span)

    # Kahn's algorithm
    queue = deque([node for node in all_nodes if in_degree[node] == 0])
    sorted_order = []

    while queue:
        node = queue.popleft()
        sorted_order.append(node)

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Cycle detected if not all nodes processed
    has_cycle = len(sorted_order) != len(all_nodes)

    if has_cycle:
        # Find cycle path (simplified)
        cycle = list(all_nodes - set(sorted_order))
        return True, cycle

    return False, None

def record_span_start(
    span_id: str,
    correlation_id: str,
    trace_id: str,
    parent_span_id: Optional[str],
    operation: str,
    db_path: Path = TRACE_DB
):
    """Record span start in database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO spans
            (span_id, correlation_id, trace_id, parent_span_id,
             operation, source, status)
        VALUES (?, ?, ?, ?, ?, 'orchestrator', 'running')
    """, (span_id, correlation_id, trace_id, parent_span_id, operation))

    # Record dependency edge
    if parent_span_id:
        cursor.execute("""
            INSERT OR IGNORE INTO dependencies
                (from_span_id, to_span_id, correlation_id)
            VALUES (?, ?, ?)
        """, (parent_span_id, span_id, correlation_id))

    conn.commit()
    conn.close()

def record_span_end(
    span_id: str,
    status: str,
    error_message: Optional[str] = None,
    db_path: Path = TRACE_DB
):
    """Record span completion in database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE spans
        SET status = ?,
            completed_at = CURRENT_TIMESTAMP,
            error_message = ?
        WHERE span_id = ?
    """, (status, error_message, span_id))

    conn.commit()
    conn.close()

def launch_claude_cli_with_trace(
    correlation_id: str,
    trace_id: str,
    parent_span_id: str
) -> int:
    """
    Launch Claude CLI subprocess with trace context propagation
    Returns exit code
    """
    # Create new span for CLI subprocess
    cli_span_id = generate_span_id()

    log_with_trace(
        correlation_id, trace_id, cli_span_id,
        "INFO", "Launching Claude CLI subprocess",
        parent_span_id=parent_span_id
    )

    # Record span start
    record_span_start(
        cli_span_id, correlation_id, trace_id,
        parent_span_id, "claude-cli-execution"
    )

    # Prepare environment with trace context
    env = os.environ.copy()
    env['CORRELATION_ID'] = correlation_id
    env['TRACE_ID'] = trace_id
    env['SPAN_ID'] = cli_span_id
    env['PARENT_SPAN_ID'] = parent_span_id

    # Launch subprocess
    try:
        result = subprocess.run(
            ['claude', 'code'],
            env=env,
            capture_output=True,
            text=True
        )

        status = 'completed' if result.returncode == 0 else 'failed'
        error_msg = result.stderr if result.returncode != 0 else None

        record_span_end(cli_span_id, status, error_msg)

        log_with_trace(
            correlation_id, trace_id, cli_span_id,
            "INFO" if result.returncode == 0 else "ERROR",
            f"Claude CLI completed with exit code {result.returncode}",
            parent_span_id=parent_span_id,
            exit_code=result.returncode
        )

        return result.returncode

    except Exception as e:
        record_span_end(cli_span_id, 'failed', str(e))

        log_with_trace(
            correlation_id, trace_id, cli_span_id,
            "ERROR", f"Failed to launch Claude CLI: {e}",
            parent_span_id=parent_span_id
        )

        return 1

def main():
    """Main orchestrator logic"""
    if len(sys.argv) < 2:
        print("Usage: orchestrator.py <notification-file>", file=sys.stderr)
        sys.exit(1)

    notification_file = Path(sys.argv[1])

    if not notification_file.exists():
        print(f"Notification file not found: {notification_file}", file=sys.stderr)
        sys.exit(1)

    # Extract trace context from notification
    context = extract_trace_context(notification_file)
    correlation_id = context['correlation_id']
    trace_id = context['trace_id']
    parent_span_id = context['span_id']

    # Create new span for orchestrator
    span_id = generate_span_id()

    log_with_trace(
        correlation_id, trace_id, span_id,
        "INFO", "Orchestrator processing approval",
        parent_span_id=parent_span_id
    )

    # Record span start
    record_span_start(
        span_id, correlation_id, trace_id,
        parent_span_id, "approval-processing"
    )

    # CHECK FOR CIRCULAR DEPENDENCY BEFORE LAUNCHING
    has_cycle, cycle_path = detect_circular_dependency(correlation_id)

    if has_cycle:
        error_msg = f"Circular dependency detected: {cycle_path}"

        log_with_trace(
            correlation_id, trace_id, span_id,
            "ERROR", error_msg,
            parent_span_id=parent_span_id,
            cycle_path=cycle_path
        )

        record_span_end(span_id, 'aborted', error_msg)
        sys.exit(1)

    # Launch Claude CLI
    exit_code = launch_claude_cli_with_trace(
        correlation_id, trace_id, span_id
    )

    # Mark orchestrator span as completed
    record_span_end(
        span_id,
        'completed' if exit_code == 0 else 'failed'
    )

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
```

---

### 9.3 Python: Build Request Graph from Logs

```python
#!/usr/bin/env python3
"""
Analyze request traces and build dependency graphs
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

TRACE_DB = Path.home() / ".claude" / "traces.db"

def build_request_graph(
    correlation_id: str,
    db_path: Path = TRACE_DB
) -> Dict:
    """
    Build complete request graph for visualization
    Returns graph structure with nodes and edges
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all spans for this correlation
    cursor.execute("""
        SELECT
            span_id, operation, source,
            started_at, completed_at,
            status, parent_span_id,
            metadata
        FROM spans
        WHERE correlation_id = ?
        ORDER BY started_at
    """, (correlation_id,))

    spans = cursor.fetchall()

    # Get all dependencies
    cursor.execute("""
        SELECT from_span_id, to_span_id
        FROM dependencies
        WHERE correlation_id = ?
    """, (correlation_id,))

    edges = cursor.fetchall()
    conn.close()

    # Build graph structure
    nodes = []
    for span in spans:
        (span_id, operation, source, started, completed,
         status, parent, metadata) = span

        nodes.append({
            'id': span_id,
            'operation': operation,
            'source': source,
            'started': started,
            'completed': completed,
            'status': status,
            'parent': parent,
            'metadata': json.loads(metadata) if metadata else {}
        })

    graph = {
        'correlation_id': correlation_id,
        'nodes': nodes,
        'edges': [
            {'from': from_span, 'to': to_span}
            for from_span, to_span in edges
        ]
    }

    return graph

def visualize_graph_ascii(graph: Dict) -> str:
    """
    Generate ASCII art visualization of request graph
    """
    nodes = {n['id']: n for n in graph['nodes']}
    edges = defaultdict(list)

    for edge in graph['edges']:
        edges[edge['from']].append(edge['to'])

    # Find root nodes (no parent)
    roots = [n['id'] for n in graph['nodes'] if not n['parent']]

    def render_tree(node_id: str, prefix: str = "", is_last: bool = True) -> List[str]:
        """Recursively render tree structure"""
        node = nodes[node_id]
        lines = []

        # Current node
        connector = "└── " if is_last else "├── "
        status_symbol = {
            'completed': '✓',
            'failed': '✗',
            'running': '⟳',
            'aborted': '⊗'
        }.get(node['status'], '?')

        lines.append(
            f"{prefix}{connector}{status_symbol} {node['source']}: {node['operation']} "
            f"[{node['id'][:8]}]"
        )

        # Children
        children = edges.get(node_id, [])
        for i, child_id in enumerate(children):
            is_child_last = (i == len(children) - 1)
            child_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(render_tree(child_id, child_prefix, is_child_last))

        return lines

    output = [f"Request Trace: {graph['correlation_id']}", ""]

    for root in roots:
        output.extend(render_tree(root))

    return '\n'.join(output)

def export_graphviz_dot(graph: Dict, output_file: Path):
    """
    Export graph to GraphViz DOT format for visualization
    """
    dot_lines = [
        "digraph request_trace {",
        "  rankdir=TB;",
        "  node [shape=box, style=rounded];",
        ""
    ]

    # Add nodes
    for node in graph['nodes']:
        color = {
            'completed': 'green',
            'failed': 'red',
            'running': 'yellow',
            'aborted': 'orange'
        }.get(node['status'], 'gray')

        label = f"{node['source']}\\n{node['operation']}"
        dot_lines.append(
            f'  "{node["id"]}" [label="{label}", color={color}];'
        )

    dot_lines.append("")

    # Add edges
    for edge in graph['edges']:
        dot_lines.append(f'  "{edge["from"]}" -> "{edge["to"]}";')

    dot_lines.append("}")

    with open(output_file, 'w') as f:
        f.write('\n'.join(dot_lines))

    print(f"GraphViz DOT file written to: {output_file}")
    print(f"Generate PNG with: dot -Tpng {output_file} -o graph.png")

# Example usage
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: analyze_trace.py <correlation-id>")
        sys.exit(1)

    correlation_id = sys.argv[1]

    # Build graph
    graph = build_request_graph(correlation_id)

    # ASCII visualization
    print(visualize_graph_ascii(graph))
    print()

    # Export GraphViz
    dot_file = Path(f"trace-{correlation_id}.dot")
    export_graphviz_dot(graph, dot_file)
```

---

## 10. Recommendations Summary

### For Your Multi-Process System

1. **Correlation ID Format**: Use **ULID** (sortable, compact, timestamp-embedded)
   - Bash: `uuidgen` for simplicity (fallback to UUID v4)
   - Python: `ulid.create()` library

2. **Propagation Mechanism**: **Environment Variables** (primary) + **JSON files** (complex context)
   - Simple and Unix-native
   - Automatic inheritance across bash → Python → subprocess
   - Check `CORRELATION_ID` presence to detect loops

3. **Parent-Child Tracking**: W3C Trace Context format
   - `TRACE_ID` (constant across request)
   - `SPAN_ID` (unique per process)
   - `PARENT_SPAN_ID` (link to parent)

4. **Loop Detection**: **Three-layer approach**
   - **Layer 1**: Environment variable check (fast, immediate)
   - **Layer 2**: Topological sort before subprocess spawn (medium, comprehensive)
   - **Layer 3**: Idempotency tokens (slow, robust)

5. **Storage**: **SQLite database** at `~/.claude/traces.db`
   - Lightweight (no external services)
   - Fast graph queries (indexed joins)
   - Schema provided in section 8

6. **Tracing Library**: **Custom lightweight tracer** (section 5.2)
   - Avoid heavy OpenTelemetry SDK
   - Simple context manager API
   - Direct SQLite writes

7. **Visualization**: **GraphViz export** + **ASCII tree**
   - Debug with `dot -Tpng trace.dot -o trace.png`
   - Quick inspection with ASCII tree in logs

---

## References

- W3C Trace Context: https://www.w3.org/TR/trace-context/
- OpenTelemetry Specification: https://opentelemetry.io/docs/specs/otel/
- ULID Spec: https://github.com/ulid/spec
- Kahn's Algorithm: https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm
- Python graphlib: https://docs.python.org/3/library/graphlib.html
- systemd Dependencies: https://www.freedesktop.org/software/systemd/man/systemd.unit.html

---

**End of Research Report**
