"""
Bot utility functions for event logging and PID file management.

Pure utility functions with minimal dependencies.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def log_event(
    correlation_id: str,
    workspace_id: str,
    session_id: str,
    component: str,
    event_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log event to SQLite event store via event_logger.py.

    Args:
        correlation_id: ULID for request tracing
        workspace_id: Workspace hash or ULID
        session_id: Claude Code session UUID
        component: Component name (bot)
        event_type: Event type (e.g., notification.received)
        metadata: Event-specific data

    Raises:
        subprocess.CalledProcessError: Event logging failed
    """
    event_logger = Path.home() / ".claude" / "automation" / "lychee" / "runtime" / "lib" / "event_logger.py"
    metadata_json = json.dumps(metadata) if metadata else "{}"

    try:
        subprocess.run(
            [str(event_logger), correlation_id, workspace_id, session_id, component, event_type, metadata_json],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to log event {event_type}: {e.stderr}", file=sys.stderr)
        raise


def create_pid_file(pid_file_path: Path) -> None:
    """
    Create PID file atomically.

    Args:
        pid_file_path: Path to PID file

    Raises:
        FileExistsError: Another bot instance is already running
        OSError: File system error
    """
    try:
        # Atomic create with O_EXCL (fails if file exists)
        fd = os.open(str(pid_file_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        try:
            os.write(fd, f"{os.getpid()}\n".encode())
            print(f"✅ Created PID file: {pid_file_path} (PID: {os.getpid()})")
        finally:
            os.close(fd)
    except FileExistsError:
        print(f"❌ PID file already exists: {pid_file_path}", file=sys.stderr)
        print(f"   Another bot instance is likely running", file=sys.stderr)
        raise
    except Exception as e:
        print(f"❌ Failed to create PID file: {type(e).__name__}: {e}", file=sys.stderr)
        raise


def cleanup_pid_file(pid_file_path: Path) -> None:
    """
    Remove PID file if it exists and belongs to this process.

    Args:
        pid_file_path: Path to PID file
    """
    try:
        if pid_file_path.exists():
            # Verify PID file contains our PID before removing
            try:
                stored_pid = int(pid_file_path.read_text().strip())
                if stored_pid == os.getpid():
                    pid_file_path.unlink()
                    print(f"🗑️  Removed PID file: {pid_file_path}")
                else:
                    print(f"⚠️  PID file belongs to different process ({stored_pid}), not removing", file=sys.stderr)
            except (ValueError, OSError) as e:
                # Corrupted PID file, remove it anyway
                pid_file_path.unlink()
                print(f"🗑️  Removed corrupted PID file: {e}")
    except Exception as e:
        print(f"⚠️  Failed to cleanup PID file: {type(e).__name__}: {e}", file=sys.stderr)
