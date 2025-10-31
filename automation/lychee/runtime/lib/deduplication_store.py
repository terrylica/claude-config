"""
Content Deduplication Store

Persists content deduplication state to survive bot restarts.
Prevents redundant Telegram API calls by caching SHA256 hashes of sent content.

This module addresses the root cause discovered in session 906b0590:
- Bot restart loses in-memory last_sent_content dictionary
- Duplicate progress updates trigger Telegram API calls
- Accumulated API calls lead to HTTP 429 rate limiting

Solution: Persist SHA256 hashes to disk with TTL-based cleanup.
"""

import hashlib
import sys
import time
from pathlib import Path
from typing import Dict, Tuple


class DeduplicationStore:
    """
    Persist content deduplication state to survive restarts.

    Uses SHA256 hashing to minimize disk I/O while maintaining correctness.
    Each (workspace_id, session_id, workflow_id) tuple maps to a hash file.
    """

    def __init__(self, dedup_dir: Path, ttl_minutes: int = 30):
        """
        Initialize deduplication store.

        Args:
            dedup_dir: Directory for hash files
            ttl_minutes: Age threshold for hash file expiration

        Raises:
            OSError: If directory creation fails
        """
        self.dedup_dir = dedup_dir
        self.ttl_seconds = ttl_minutes * 60
        self.cache: Dict[Tuple[str, str, str], str] = {}

        # Ensure directory exists
        try:
            self.dedup_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"❌ Failed to create deduplication directory: {e}", file=sys.stderr)
            raise

    def _make_filename(self, workspace_id: str, session_id: str, workflow_id: str) -> Path:
        """
        Generate hash filename for deduplication entry.

        Uses SHA256 to avoid filesystem limits on filename length.

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier
            workflow_id: Workflow identifier

        Returns:
            Path to hash file
        """
        key_str = f"{workspace_id}_{session_id}_{workflow_id}"
        key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]
        return self.dedup_dir / f"{key_hash}.hash"

    def check_duplicate(self, workspace_id: str, session_id: str, workflow_id: str, content: str) -> bool:
        """
        Check if content is duplicate of last sent.

        Returns:
            True if content is duplicate (skip sending)
            False if content is new (send to Telegram)
        """
        progress_key = (workspace_id, session_id, workflow_id)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Check in-memory cache first (fast path)
        if progress_key in self.cache:
            if self.cache[progress_key] == content_hash:
                print(f"   ⏭️  Dedup: Cache HIT (in-memory) - skipping API call")
                return True

        # Check disk cache (restore after restart)
        hash_file = self._make_filename(workspace_id, session_id, workflow_id)
        if hash_file.exists():
            try:
                # Verify TTL
                age = time.time() - hash_file.stat().st_mtime
                if age < self.ttl_seconds:
                    stored_hash = hash_file.read_text().strip()
                    if stored_hash == content_hash:
                        # Restore to memory for fast future lookups
                        self.cache[progress_key] = content_hash
                        print(f"   ⏭️  Dedup: Cache HIT (disk) - skipping API call")
                        return True
                else:
                    # Expired - remove
                    hash_file.unlink()
                    print(f"   🗑️  Dedup: Expired hash file removed (age={age:.0f}s)")
            except Exception as e:
                # Disk read error - treat as cache miss and continue
                print(f"   ⚠️  Dedup: Hash file read error: {e}", file=sys.stderr)

        # Not a duplicate
        print(f"   ✅ Dedup: Cache MISS - sending to Telegram")
        return False

    def record_sent(self, workspace_id: str, session_id: str, workflow_id: str, content: str) -> None:
        """
        Record that content was sent (after successful API call).

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier
            workflow_id: Workflow identifier
            content: Sent message content

        Raises:
            OSError: If hash file write fails (critical error)
        """
        progress_key = (workspace_id, session_id, workflow_id)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Update in-memory cache
        self.cache[progress_key] = content_hash

        # Persist to disk (atomic write-then-rename)
        hash_file = self._make_filename(workspace_id, session_id, workflow_id)
        tmp_file = hash_file.with_suffix(".tmp")

        try:
            tmp_file.write_text(content_hash)
            tmp_file.rename(hash_file)  # Atomic on POSIX
            print(f"   💾 Dedup: Recorded hash (len={len(content)} chars)")
        except OSError as e:
            print(f"❌ Failed to write hash file: {e}", file=sys.stderr)
            raise

    def cleanup(self, workspace_id: str, session_id: str, workflow_id: str) -> None:
        """
        Remove deduplication state when workflow completes.

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier
            workflow_id: Workflow identifier
        """
        progress_key = (workspace_id, session_id, workflow_id)

        # Remove from memory
        self.cache.pop(progress_key, None)

        # Remove from disk
        hash_file = self._make_filename(workspace_id, session_id, workflow_id)
        if hash_file.exists():
            try:
                hash_file.unlink()
                print(f"   🗑️  Dedup: Cleaned up hash file")
            except OSError as e:
                # Non-critical - log and continue
                print(f"   ⚠️  Dedup: Failed to cleanup hash file: {e}", file=sys.stderr)

    def restore_all(self) -> int:
        """
        Restore all valid deduplication state from disk.

        Called on bot startup. Removes expired entries.

        Returns:
            Count of valid hash files found

        Raises:
            OSError: If directory access fails (critical error)
        """
        restored_count = 0
        now = time.time()

        try:
            for hash_file in self.dedup_dir.glob("*.hash"):
                try:
                    # Check TTL
                    age = now - hash_file.stat().st_mtime
                    if age > self.ttl_seconds:
                        hash_file.unlink()
                        print(f"   🗑️  Dedup: Removed expired {hash_file.name} (age={age:.0f}s)")
                        continue

                    # Valid - leave on disk for lazy loading on first check
                    restored_count += 1

                except Exception as e:
                    print(f"   ⚠️  Dedup: Failed to process {hash_file.name}: {e}", file=sys.stderr)

            print(f"   ✅ Dedup: Found {restored_count} valid hash file(s)")
            return restored_count

        except OSError as e:
            print(f"❌ Failed to restore deduplication state: {e}", file=sys.stderr)
            raise
