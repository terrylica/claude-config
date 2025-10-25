#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Event Logger

Logs events to SQLite event store.
Fail-fast: raises on error, no silent failures.

SLO:
- Availability: 99.9% (must not block main workflow)
- Correctness: 100% (all events captured, raise on error)
- Observability: Full (all events queryable)
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# Database path from environment or default
DEFAULT_DB_PATH = Path.home() / ".claude" / "automation" / "lychee" / "state" / "events.db"
DB_PATH = Path(os.getenv("LYCHEE_EVENTS_DB", str(DEFAULT_DB_PATH)))


class EventLoggingError(Exception):
    """Base exception for event logging failures."""
    pass


class DatabaseConnectionError(EventLoggingError):
    """Cannot connect to SQLite database."""
    pass


class CorrelationIDMissing(EventLoggingError):
    """Required CORRELATION_ID not found."""
    pass


def log_event(
    correlation_id: str,
    workspace_id: str,
    session_id: str,
    component: str,
    event_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log event to SQLite event store.

    Args:
        correlation_id: ULID for request tracing
        workspace_id: Workspace hash or ULID
        session_id: Claude Code session UUID
        component: Component name (hook, bot, orchestrator, claude-cli)
        event_type: Hierarchical event type (e.g., hook.started)
        metadata: Event-specific data (will be JSON-encoded)

    Raises:
        DatabaseConnectionError: Cannot connect to database
        CorrelationIDMissing: correlation_id is empty
        EventLoggingError: Any other database error
    """
    # Validate required fields
    if not correlation_id:
        raise CorrelationIDMissing("correlation_id is required")

    # Validate component
    valid_components = {'hook', 'bot', 'orchestrator', 'claude-cli'}
    if component not in valid_components:
        raise EventLoggingError(
            f"Invalid component '{component}', must be one of {valid_components}"
        )

    # Current timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # Encode metadata as JSON
    metadata_json = json.dumps(metadata) if metadata else None

    # Connect to database
    try:
        conn = sqlite3.connect(str(DB_PATH))
    except sqlite3.Error as e:
        raise DatabaseConnectionError(f"Cannot connect to {DB_PATH}: {e}") from e

    try:
        # Insert event
        conn.execute(
            """
            INSERT INTO session_events
            (correlation_id, workspace_id, session_id, component, event_type, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (correlation_id, workspace_id, session_id, component, event_type, timestamp, metadata_json)
        )
        conn.commit()
    except sqlite3.Error as e:
        raise EventLoggingError(f"Failed to insert event: {e}") from e
    finally:
        conn.close()


def main() -> int:
    """
    CLI entry point for testing.

    Usage: event_logger.py CORRELATION_ID WORKSPACE_ID SESSION_ID COMPONENT EVENT_TYPE [METADATA_JSON]
    """
    if len(sys.argv) < 6:
        print("Usage: event_logger.py CORRELATION_ID WORKSPACE_ID SESSION_ID COMPONENT EVENT_TYPE [METADATA_JSON]", file=sys.stderr)
        return 1

    correlation_id = sys.argv[1]
    workspace_id = sys.argv[2]
    session_id = sys.argv[3]
    component = sys.argv[4]
    event_type = sys.argv[5]
    metadata = json.loads(sys.argv[6]) if len(sys.argv) > 6 else None

    try:
        log_event(correlation_id, workspace_id, session_id, component, event_type, metadata)
        print(f"✅ Event logged: {component}.{event_type}")
        return 0
    except EventLoggingError as e:
        print(f"❌ Event logging failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
