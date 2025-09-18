#!/usr/bin/env python3
"""
Workspace Cleanup Tool - Frees up disk space by archiving old data
@path-export: workspace-cleanup
"""

import shutil
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta


class WorkspaceCleanup:
    def __init__(self, dry_run=False):
        self.workspace = Path.home() / ".claude"
        self.archive = Path.home() / ".claude-archive"
        self.freed_space = 0
        self.dry_run = dry_run
        self.operations = []

    def archive_legacy_sessions(self):
        """Archive legacy session directories"""
        legacy_dirs = [
            "system/sessions/legacy",
            "system/sessions.backup.165519"
        ]

        for legacy_dir in legacy_dirs:
            path = self.workspace / legacy_dir
            if path.exists():
                timestamp = datetime.now().strftime("%Y%m%d")
                archive_name = f"{path.name}-{timestamp}"
                self._archive_directory(path, "sessions-legacy", archive_name)

    def archive_old_sessions(self, days=30):
        """Archive sessions older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        sessions_dir = self.workspace / "system" / "sessions"

        if not sessions_dir.exists():
            return

        archived_count = 0
        for session_file in sessions_dir.rglob("*"):
            if session_file.is_file():
                try:
                    mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
                    if mtime < cutoff:
                        self._archive_file(session_file, "old-sessions")
                        archived_count += 1
                except OSError:
                    continue

        print(f"Archived {archived_count} old session files")

    def remove_duplicate_projects(self):
        """Remove identified duplicate project directories"""
        duplicates = [
            "projects/-home-tca-eon-nt",
            "projects/-home-tca--claude",
            "projects/~-claude",
            "projects/~eon-nt",
            "projects/legacy"
        ]

        for dup in duplicates:
            path = self.workspace / dup
            if path.exists():
                self._archive_directory(path, "duplicate-projects")

    def clean_empty_todos(self):
        """Remove empty or tiny todo files"""
        todos_dir = self.workspace / "todos"

        if not todos_dir.exists():
            return

        cleaned_count = 0
        for todo_file in todos_dir.glob("*.json"):
            try:
                file_size = todo_file.stat().st_size
                if file_size < 100:
                    if not self.dry_run:
                        self.freed_space += file_size
                        todo_file.unlink()
                    else:
                        self.freed_space += file_size
                        self.operations.append(f"DELETE: {todo_file}")
                    cleaned_count += 1
            except OSError:
                continue

        print(f"Cleaned {cleaned_count} empty todo files")

    def archive_old_logs(self, days=30):
        """Archive log files older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        logs_dir = self.workspace / "logs"

        if not logs_dir.exists():
            return

        archived_count = 0
        for log_file in logs_dir.glob("*.log"):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff:
                    self._archive_file(log_file, "logs")
                    archived_count += 1
            except OSError:
                continue

        print(f"Archived {archived_count} old log files")

    def _archive_file(self, source, archive_subdir):
        """Move file to archive"""
        dest_dir = self.archive / archive_subdir / source.parent.name

        if not self.dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / source.name

            self.freed_space += source.stat().st_size
            shutil.move(str(source), str(dest))
        else:
            self.freed_space += source.stat().st_size
            self.operations.append(f"ARCHIVE: {source} -> {dest_dir}")

    def _archive_directory(self, source, archive_subdir, custom_name=None):
        """Move directory to archive"""
        dest_name = custom_name or source.name
        dest = self.archive / archive_subdir / dest_name

        if not self.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Calculate size before move
            try:
                self.freed_space += sum(f.stat().st_size for f in source.rglob("*") if f.is_file())
            except OSError:
                pass

            shutil.move(str(source), str(dest))
        else:
            try:
                self.freed_space += sum(f.stat().st_size for f in source.rglob("*") if f.is_file())
            except OSError:
                pass
            self.operations.append(f"ARCHIVE: {source} -> {dest}")

    def run(self, skip_sessions=False):
        """Execute cleanup operations"""
        print(f"Starting workspace cleanup{'(DRY RUN)' if self.dry_run else ''}...")

        self.archive_legacy_sessions()

        if not skip_sessions:
            self.archive_old_sessions()

        self.remove_duplicate_projects()
        self.clean_empty_todos()
        self.archive_old_logs()

        freed_gb = self.freed_space / (1024**3)

        if self.dry_run:
            print(f"\nDRY RUN RESULTS:")
            print(f"Would free: {freed_gb:.2f}GB")
            print(f"Operations to perform: {len(self.operations)}")
            if self.operations:
                print("\nFirst 10 operations:")
                for op in self.operations[:10]:
                    print(f"  {op}")
        else:
            print(f"Cleanup complete! Freed: {freed_gb:.2f}GB")

        return freed_gb


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Claude workspace cleanup tool")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    parser.add_argument("--skip-sessions", action="store_true",
                       help="Skip archiving old session files")

    args = parser.parse_args()

    cleanup = WorkspaceCleanup(dry_run=args.dry_run)
    freed_gb = cleanup.run(skip_sessions=args.skip_sessions)

    if freed_gb > 0:
        sys.exit(0)
    else:
        print("No space could be freed")
        sys.exit(1)


if __name__ == "__main__":
    main()