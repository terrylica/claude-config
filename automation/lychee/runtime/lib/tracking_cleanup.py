"""
Tracking File TTL Cleanup

Removes orphaned tracking files to prevent disk bloat.

Orphaned files occur when:
- Execution completion handler crashes
- File deletion fails
- Bot killed during cleanup
"""

import sys
import time
from pathlib import Path


def cleanup_orphaned_tracking(tracking_dir: Path, ttl_minutes: int = 30) -> int:
    """
    Remove orphaned tracking files older than TTL.

    Args:
        tracking_dir: Directory containing tracking JSON files
        ttl_minutes: Age threshold in minutes

    Returns:
        Number of files removed

    Raises:
        OSError: If directory access fails (critical error)
    """
    if not tracking_dir.exists():
        return 0

    cutoff = time.time() - (ttl_minutes * 60)
    removed_count = 0

    try:
        for tracking_file in tracking_dir.glob("*_tracking.json"):
            try:
                # Check age
                mtime = tracking_file.stat().st_mtime
                if mtime < cutoff:
                    age = time.time() - mtime
                    tracking_file.unlink()
                    print(f"   🗑️  Tracking: Removed orphaned {tracking_file.name} (age={age/60:.1f}m)")
                    removed_count += 1
            except FileNotFoundError:
                # File deleted between glob and stat (race condition, non-critical)
                pass
            except OSError as e:
                # File access error - log and continue
                print(f"   ⚠️  Tracking: Failed to clean {tracking_file.name}: {e}", file=sys.stderr)

        if removed_count > 0:
            print(f"   ✅ Tracking: Cleaned up {removed_count} orphaned file(s)")

        return removed_count

    except OSError as e:
        # Directory access failure - critical error
        print(f"❌ Failed to access tracking directory: {e}", file=sys.stderr)
        raise
