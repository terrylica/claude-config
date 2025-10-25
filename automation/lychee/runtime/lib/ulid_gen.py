#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-ulid>=2.7.0",
#     "typing-extensions>=4.0.0",
# ]
# ///
"""
ULID Generator

Generates ULID (Universally Unique Lexicographically Sortable Identifier).
Used for correlation IDs in event tracking.

SLO: Correctness 100% (collision-resistant, sortable by time)
"""

import sys
from ulid import ULID


def generate() -> str:
    """
    Generate ULID.

    Returns:
        26-character ULID string (e.g., 01JEGQXV8KHTNF3YD8G7ZC9XYK)

    Raises:
        Never - ULID() cannot fail
    """
    return str(ULID())


def main() -> int:
    """CLI entry point."""
    print(generate())
    return 0


if __name__ == "__main__":
    sys.exit(main())
