"""
Production PID File Manager

Atomic PID file management with fcntl locking and stale detection.
Eliminates TOCTOU race conditions in concurrent startup scenarios.

This module replaces bot_utils.py PID management to fix the race condition
discovered during session 906b0590 investigation.
"""

import os
import sys
import fcntl
import errno
import atexit
import psutil
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class LockResult:
    """Result of PID file lock operation."""
    success: bool
    message: str
    pid: Optional[int] = None
    cmdline: Optional[str] = None


class PIDFileManager:
    """
    Production-grade PID file manager with file locking and stale detection.

    Combines fcntl file locking (atomicity) with psutil verification (diagnostics).

    Key Features:
    - Atomic lock acquisition (no race conditions)
    - Stale PID detection (handles crashes, power failures)
    - Auto-cleanup on process exit (normal or abnormal)
    - Diagnostic verification (actionable error messages)
    - Network filesystem detection (identifies stale locks)

    Example:
        >>> pid_mgr = PIDFileManager(Path("/var/run/myapp.pid"), "myapp.py")
        >>> if not pid_mgr.acquire():
        ...     sys.exit(1)
        >>> # ... application code ...
        >>> pid_mgr.release()  # Optional (auto-cleanup on exit)
    """

    def __init__(self, pid_file: Path, script_name: str = ""):
        """
        Initialize PID file manager.

        Args:
            pid_file: Path to PID file
            script_name: Script name for verification (prevents PID reuse false positives)
        """
        self.pid_file = pid_file
        self.script_name = script_name
        self.fd: Optional[int] = None

    def acquire(self) -> bool:
        """
        Acquire exclusive lock on PID file.

        Atomically:
        1. Opens PID file (creates if needed)
        2. Attempts to acquire exclusive fcntl lock
        3. Writes current process PID to file
        4. Registers cleanup handler

        Returns:
            True if lock acquired successfully, False otherwise.
            Detailed error messages printed to stderr on failure.

        Raises:
            No exceptions raised - all errors handled internally.
        """
        try:
            # Open file for read/write, create if needed
            # Mode 0o644: Owner can read/write, group/others can read
            self.fd = os.open(
                str(self.pid_file),
                os.O_RDWR | os.O_CREAT,
                0o644
            )

            # Try to acquire exclusive lock (non-blocking)
            try:
                fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError as e:
                if e.errno in (errno.EACCES, errno.EAGAIN):
                    # Lock is held by another process
                    result = self._diagnose_lock_holder()
                    print(f"❌ {result.message}", file=sys.stderr)
                    if result.pid:
                        print(f"   PID: {result.pid}", file=sys.stderr)
                    if result.cmdline:
                        print(f"   Command: {result.cmdline}", file=sys.stderr)
                    return False
                else:
                    # Other IO error
                    print(f"❌ Failed to lock PID file: {e}", file=sys.stderr)
                    return False

            # We have the lock! Write our PID
            self._write_pid()

            # Register cleanup handler for normal exit
            atexit.register(self.release)

            print(f"✅ Acquired PID file lock: {self.pid_file} (PID: {os.getpid()})")
            return True

        except Exception as e:
            # Unexpected error
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
            print(f"❌ Failed to acquire PID file lock: {type(e).__name__}: {e}", file=sys.stderr)
            return False

    def _write_pid(self) -> None:
        """Write current process PID to locked file."""
        # Clear any existing content
        os.ftruncate(self.fd, 0)

        # Write PID
        os.write(self.fd, f"{os.getpid()}\n".encode())

        # Force write to disk
        os.fsync(self.fd)

    def _diagnose_lock_holder(self) -> LockResult:
        """
        Diagnose why lock acquisition failed using psutil.

        Distinguishes between:
        - Real conflict (another instance running)
        - Stale lock (process dead, network FS issue)
        - Initialization race (process starting up)

        Returns:
            LockResult with diagnostic information
        """
        try:
            # Read PID from locked file
            os.lseek(self.fd, 0, os.SEEK_SET)
            pid_data = os.read(self.fd, 32).decode().strip()

            if not pid_data:
                # PID file is locked but empty (initialization race)
                os.close(self.fd)
                self.fd = None
                return LockResult(
                    success=False,
                    message="PID file locked but empty (another process initializing)"
                )

            # Parse PID
            try:
                stored_pid = int(pid_data)
            except ValueError:
                # Corrupted PID file
                os.close(self.fd)
                self.fd = None
                return LockResult(
                    success=False,
                    message=f"PID file locked but contains invalid data: {pid_data!r}"
                )

            # Verify process with psutil
            is_running, cmdline = self._is_process_running(stored_pid)

            os.close(self.fd)
            self.fd = None

            if is_running:
                # Real conflict - another instance is running
                return LockResult(
                    success=False,
                    message=f"Another instance is already running",
                    pid=stored_pid,
                    cmdline=cmdline
                )
            else:
                # Stale lock - network filesystem or kernel bug
                return LockResult(
                    success=False,
                    message=(
                        f"Stale lock detected (PID {stored_pid} not running). "
                        "This indicates a network filesystem or kernel issue. "
                        f"Manual intervention required: rm {self.pid_file}"
                    ),
                    pid=stored_pid
                )

        except Exception as e:
            # Diagnostic failure
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
            return LockResult(
                success=False,
                message=f"Failed to diagnose lock holder: {type(e).__name__}: {e}"
            )

    def _is_process_running(self, pid: int) -> Tuple[bool, Optional[str]]:
        """
        Check if process is running using psutil with cmdline verification.

        Prevents PID reuse false positives.

        Args:
            pid: Process ID to check

        Returns:
            Tuple of (is_running, cmdline)
        """
        if not psutil.pid_exists(pid):
            return False, None

        try:
            p = psutil.Process(pid)
            cmdline = p.cmdline()
            cmdline_str = ' '.join(cmdline)

            # If script_name specified, verify it matches
            if self.script_name:
                is_our_script = self.script_name in cmdline_str
                return is_our_script, cmdline_str
            else:
                # No script_name verification
                return True, cmdline_str

        except psutil.NoSuchProcess:
            # Process died between check and Process() call
            return False, None
        except psutil.AccessDenied:
            # Cannot access process info
            return False, None

    def release(self) -> None:
        """
        Release lock and cleanup PID file.

        Safe to call multiple times (idempotent).
        Automatically called on normal process exit via atexit.

        On abnormal exit (SIGKILL, crash, power failure):
        - Kernel auto-releases lock (next acquire() will succeed)
        - PID file may remain (but lock is released, so harmless)
        """
        if self.fd is not None:
            try:
                # Close file descriptor (auto-releases lock)
                os.close(self.fd)
                self.fd = None

                # Remove PID file
                self.pid_file.unlink(missing_ok=True)

                print(f"🗑️  Released PID file lock: {self.pid_file}")

            except Exception as e:
                # Cleanup failure (rare, but don't crash on exit)
                print(f"⚠️  Failed to cleanup PID file: {type(e).__name__}: {e}", file=sys.stderr)

    def __enter__(self):
        """Context manager entry."""
        if not self.acquire():
            raise RuntimeError("Failed to acquire PID file lock")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False  # Don't suppress exceptions
