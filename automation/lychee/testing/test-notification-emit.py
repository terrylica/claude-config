#!/usr/bin/env python3
"""
Test Notification Emission Script

Simulates a broken link notification from the stop hook without waiting for
actual broken links to be detected. Useful for testing the notification flow.

Usage:
  ./test-notification-emit.py                # Use default workspace
  ./test-notification-emit.py /path/to/ws    # Specify workspace
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone

def emit_notification(workspace_path: str, error_count: int = 3):
    """
    Emit a test notification to the notifications directory.

    Args:
        workspace_path: Absolute path to workspace
        error_count: Number of fake broken links
    """
    workspace_path = Path(workspace_path).resolve()

    # Generate session ID (use test prefix)
    session_id = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Compute workspace hash (same as hook does)
    workspace_hash = hashlib.sha256(str(workspace_path).encode()).hexdigest()[:8]

    # Create notification payload
    notification = {
        "workspace_path": str(workspace_path),
        "session_id": session_id,
        "error_count": error_count,
        "details": f"TEST: Simulated {error_count} broken link(s) for testing",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Write notification file
    notification_dir = Path("/tmp/lychee_state/notifications")
    notification_dir.mkdir(parents=True, exist_ok=True)

    notification_file = notification_dir / f"notify_{session_id}_{workspace_hash}.json"
    notification_file.write_text(json.dumps(notification, indent=2))

    print(f"✅ Created notification:")
    print(f"   File: {notification_file}")
    print(f"   Workspace: {workspace_path}")
    print(f"   Session: {session_id}")
    print(f"   Hash: {workspace_hash}")
    print(f"   Errors: {error_count}")
    print()
    print("📬 Bot should detect this notification and send Telegram message")


if __name__ == "__main__":
    # Get workspace path from args or use default
    if len(sys.argv) > 1:
        workspace = sys.argv[1]
    else:
        workspace = "/Users/terryli/.claude"

    # Validate workspace exists
    if not Path(workspace).exists():
        print(f"❌ Workspace does not exist: {workspace}", file=sys.stderr)
        sys.exit(1)

    emit_notification(workspace)
