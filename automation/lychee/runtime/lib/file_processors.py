"""
File processing utilities for Telegram bot.

Generic file scanning and processing functions for startup and periodic scans.
"""

import sys
from pathlib import Path
from typing import Type

from telegram.ext import Application


async def process_pending_files(
    directory: Path,
    file_pattern: str,
    handler_class: Type,
    handler_method: str,
    file_type: str,
    app: Application,
    chat_id: int
) -> None:
    """
    Process pending files on startup.

    Scans directory for files matching pattern and processes with handler.

    Args:
        directory: Directory to scan
        file_pattern: Glob pattern (e.g., "notify_*.json")
        handler_class: Handler class to instantiate
        handler_method: Method name to call on handler
        file_type: Human-readable file type for logging
        app: Telegram Application instance
        chat_id: Telegram chat ID

    Raises:
        Exceptions from handler methods propagate (logged but not raised)
    """
    handler = handler_class(app.bot, chat_id)

    # Check if directory exists
    if not directory.exists():
        print(f"📂 No {file_type} directory found")
        return

    # Scan for files
    files = sorted(directory.glob(file_pattern))
    if not files:
        print(f"📂 No pending {file_type}s")
        return

    print(f"📬 Found {len(files)} pending {file_type}(s)")
    for file in files:
        try:
            print(f"   Processing: {file.name}")
            # Call handler method dynamically
            await getattr(handler, handler_method)(file)
        except Exception as e:
            print(f"   ❌ Failed to process {file.name}: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)


async def scan_and_process(
    directory: Path,
    file_pattern: str,
    handler,
    handler_method: str,
    file_type: str
) -> None:
    """
    Scan directory for files and process with handler.

    Used by periodic file scanner for ongoing file processing.

    Args:
        directory: Directory to scan
        file_pattern: Glob pattern for files
        handler: Handler instance (already instantiated)
        handler_method: Method name to call
        file_type: File type name for logging

    Raises:
        Exceptions from handler methods propagate (logged but not raised)
    """
    if not directory.exists():
        return

    files = sorted(directory.glob(file_pattern))
    for file in files:
        try:
            print(f"📬 Found {file_type}: {file.name}")
            await getattr(handler, handler_method)(file)
        except Exception as e:
            print(f"❌ Failed to process {file.name}: {type(e).__name__}: {e}", file=sys.stderr)
