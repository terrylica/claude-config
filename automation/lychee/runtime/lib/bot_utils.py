"""
Bot utility functions for event logging and PID file management.

Pure utility functions with minimal dependencies.
"""

import json
import os
import psutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


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


def is_bot_running(pid: int, script_name: str = "multi-workspace-bot.py") -> Tuple[bool, Optional[str]]:
    """
    Check if bot process is actually running using psutil (industry-standard approach).

    This function prevents false positives from:
    - PID reuse (new unrelated process with same PID)
    - Zombie processes (os.kill returns True for zombies)
    - Access denied errors

    Args:
        pid: Process ID to check
        script_name: Script name to verify (prevents PID reuse false positives)

    Returns:
        Tuple of (is_running, cmdline_str):
        - is_running: True if bot is actually running, False otherwise
        - cmdline_str: Full command line if process exists, None otherwise

    References:
        - Research: /Users/terryli/.claude/docs/architecture/process-management-tools-research.md
        - psutil documentation: https://psutil.readthedocs.io/
    """
    if not psutil.pid_exists(pid):
        return False, None

    try:
        p = psutil.Process(pid)
        cmdline = p.cmdline()
        cmdline_str = ' '.join(cmdline)

        # Verify it's actually our bot (prevents PID reuse)
        is_bot = script_name in cmdline_str

        return is_bot, cmdline_str

    except psutil.NoSuchProcess:
        # Process died between pid_exists check and Process() call
        return False, None
    except psutil.AccessDenied:
        # Cannot access process info - assume it's not our bot
        return False, None


def create_pid_file(pid_file_path: Path) -> None:
    """
    Create PID file atomically with stale PID cleanup.

    Handles watchexec restart race condition by checking if existing PID is actually running.
    If the process is dead (stale PID file), removes it and creates a new one.

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
        # PID file exists - check if process is actually running using psutil
        try:
            stored_pid = int(pid_file_path.read_text().strip())

            # Use psutil for robust process detection (prevents PID reuse, zombie false positives)
            is_running, cmdline = is_bot_running(stored_pid)

            if is_running:
                # Process is running - this is a real conflict
                print(f"❌ PID file already exists: {pid_file_path}", file=sys.stderr)
                print(f"   Another bot instance is running (PID: {stored_pid})", file=sys.stderr)
                print(f"   Command line: {cmdline}", file=sys.stderr)
                raise
            else:
                # Process is NOT running - stale PID file from previous crash/restart
                if cmdline:
                    print(f"⚠️  Found stale PID file (PID {stored_pid} is not our bot)")
                    print(f"   Process command line: {cmdline}")
                else:
                    print(f"⚠️  Found stale PID file (PID {stored_pid} is not running)")
                print(f"   Removing stale PID file and retrying...")
                pid_file_path.unlink()

                # Retry creating PID file (recursive call, but only once)
                fd = os.open(str(pid_file_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
                try:
                    os.write(fd, f"{os.getpid()}\n".encode())
                    print(f"✅ Created PID file after cleanup: {pid_file_path} (PID: {os.getpid()})")
                finally:
                    os.close(fd)

        except FileExistsError:
            # Re-raise FileExistsError from real bot conflict (don't treat as corrupted file)
            raise
        except (ValueError, IOError) as e:
            # Corrupted PID file - remove and retry
            print(f"⚠️  Corrupted PID file: {e}")
            print(f"   Removing corrupted PID file and retrying...")
            pid_file_path.unlink()

            # Retry creating PID file
            fd = os.open(str(pid_file_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            try:
                os.write(fd, f"{os.getpid()}\n".encode())
                print(f"✅ Created PID file after cleanup: {pid_file_path} (PID: {os.getpid()})")
            finally:
                os.close(fd)

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
