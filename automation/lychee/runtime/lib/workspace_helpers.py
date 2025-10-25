"""
Multi-Workspace Helpers
Shared utilities for workspace routing and callback mapping.
"""

import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# State directories
STATE_DIR = Path.home() / ".claude" / "automation" / "lychee" / "state"
CALLBACK_DIR = STATE_DIR / "callbacks"
REGISTRY_FILE = STATE_DIR / "registry.json"

# TTL for state files
STATE_TTL_MINUTES = 5


def load_registry() -> Dict[str, Any]:
    """Load workspace registry."""
    if not REGISTRY_FILE.exists():
        raise FileNotFoundError(f"Registry not found: {REGISTRY_FILE}")

    with REGISTRY_FILE.open() as f:
        registry = json.load(f)

    # Validate schema
    if "version" not in registry or "workspaces" not in registry:
        raise ValueError("Invalid registry schema")

    return registry


def get_workspace_id_from_path(workspace_path: Path) -> str:
    """
    Find workspace ID from path in registry.

    Args:
        workspace_path: Absolute workspace path

    Returns:
        workspace_id from registry

    Raises:
        ValueError: Workspace not found in registry
    """
    workspace_path = workspace_path.resolve()
    registry = load_registry()

    for ws_id, ws_config in registry["workspaces"].items():
        if Path(ws_config["path"]).resolve() == workspace_path:
            return ws_id

    raise ValueError(f"Workspace not registered: {workspace_path}")


def compute_workspace_hash(workspace_path: Path) -> str:
    """
    Compute 8-character hash of workspace path.

    Args:
        workspace_path: Absolute workspace path

    Returns:
        8-character hex hash
    """
    workspace_path = workspace_path.resolve()
    return hashlib.sha256(str(workspace_path).encode()).hexdigest()[:8]


def create_callback_data(
    workspace_id: str,
    workspace_path: str,
    session_id: str,
    action: str,
    correlation_id: Optional[str] = None
) -> str:
    """
    Create short callback_data with hash mapping.

    Stores full context in callback file, returns 11-byte identifier.

    Args:
        workspace_id: Workspace identifier
        workspace_path: Absolute workspace path
        session_id: Session UUID
        action: Action name (auto_fix_all, review, reject)
        correlation_id: Optional ULID for request tracing

    Returns:
        Callback identifier (format: "cb_{hash8}")
    """
    context = {
        "workspace_id": workspace_id,
        "workspace_path": str(Path(workspace_path).resolve()),
        "session_id": session_id,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    if correlation_id:
        context["correlation_id"] = correlation_id

    # Generate hash
    context_json = json.dumps(context, sort_keys=True)
    hash_val = hashlib.sha256(context_json.encode()).hexdigest()[:8]
    callback_id = f"cb_{hash_val}"

    # Store mapping
    CALLBACK_DIR.mkdir(parents=True, exist_ok=True)
    callback_file = CALLBACK_DIR / f"{callback_id}.json"
    callback_file.write_text(json.dumps(context, indent=2))

    return callback_id


def resolve_callback_data(callback_id: str) -> Dict[str, Any]:
    """
    Resolve callback_data to full context.

    Args:
        callback_id: Callback identifier (format: "cb_{hash8}")

    Returns:
        Full context dictionary

    Raises:
        ValueError: Callback not found or expired
    """
    callback_file = CALLBACK_DIR / f"{callback_id}.json"

    if not callback_file.exists():
        raise ValueError(f"Callback not found: {callback_id}")

    # Check TTL
    age = datetime.now(timezone.utc).timestamp() - callback_file.stat().st_mtime
    if age > STATE_TTL_MINUTES * 60:
        callback_file.unlink()
        raise ValueError(f"Callback expired: {callback_id}")

    return json.loads(callback_file.read_text())


def validate_workspace_path(workspace_path: Path) -> Path:
    """
    Validate workspace path with security checks.

    Args:
        workspace_path: Workspace path to validate

    Returns:
        Canonical workspace path

    Raises:
        ValueError: Invalid workspace path
    """
    workspace_path = workspace_path.resolve()

    # Must be under user home
    home = Path.home().resolve()
    try:
        workspace_path.relative_to(home)
    except ValueError:
        raise ValueError(f"Workspace outside home directory: {workspace_path}")

    # Must exist and be directory
    if not workspace_path.exists():
        raise ValueError(f"Workspace does not exist: {workspace_path}")

    if not workspace_path.is_dir():
        raise ValueError(f"Workspace is not a directory: {workspace_path}")

    return workspace_path


def cleanup_expired_files(
    directory: Path,
    ttl_minutes: int = STATE_TTL_MINUTES,
    max_files: int = 100
) -> int:
    """
    Remove expired and excess state files.

    Args:
        directory: Directory to clean
        ttl_minutes: Time-to-live in minutes
        max_files: Maximum files to keep (oldest deleted first)

    Returns:
        Number of files deleted
    """
    if not directory.exists():
        return 0

    files = sorted(
        directory.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True  # Newest first
    )

    deleted = 0
    ttl_seconds = ttl_minutes * 60
    now = datetime.now(timezone.utc).timestamp()

    for idx, file_path in enumerate(files):
        # Delete if expired
        age = now - file_path.stat().st_mtime
        if age > ttl_seconds:
            file_path.unlink()
            deleted += 1
            continue

        # Delete if exceeds max
        if idx >= max_files:
            file_path.unlink()
            deleted += 1

    return deleted
