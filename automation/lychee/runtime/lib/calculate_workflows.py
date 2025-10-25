#!/usr/bin/env python3
# /// script
# dependencies = []
# ///

"""Calculate available workflows based on session context.

This helper filters workflows from the registry based on trigger conditions.
Used by the Stop hook to determine which workflows should be presented to the user.

Usage:
    calculate_workflows.py --error-count N --modified-files M [--registry PATH]

Returns:
    JSON array of workflow IDs that match the trigger conditions
"""

import json
import sys
from pathlib import Path
from typing import Any


def filter_workflows(
    error_count: int,
    modified_files: int,
    registry_path: Path
) -> list[str]:
    """Filter workflows by trigger conditions.

    Args:
        error_count: Number of lychee validation errors
        modified_files: Number of git modified files
        registry_path: Path to workflows.json registry

    Returns:
        List of workflow IDs that match trigger conditions

    Trigger Logic:
        - lychee_errors: true → Only if error_count > 0
        - git_modified: true → Only if modified_files > 0
        - always: true → Always available
        - No triggers set → Never available
    """
    if not registry_path.exists():
        print(
            f"Error: Registry not found at {registry_path}",
            file=sys.stderr
        )
        return []

    try:
        with open(registry_path) as f:
            registry = json.load(f)
    except json.JSONDecodeError as e:
        print(
            f"Error: Invalid JSON in registry: {e}",
            file=sys.stderr
        )
        return []

    workflows = registry.get('workflows', {})
    available = []

    for wf_id, workflow in workflows.items():
        triggers = workflow.get('triggers', {})

        # Check lychee_errors trigger
        if triggers.get('lychee_errors'):
            if error_count > 0:
                available.append(wf_id)
            continue  # Skip other checks if this trigger exists

        # Check git_modified trigger
        if triggers.get('git_modified'):
            if modified_files > 0:
                available.append(wf_id)
            continue

        # Check always trigger
        if triggers.get('always'):
            available.append(wf_id)

    return available


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Calculate available workflows based on session context'
    )
    parser.add_argument(
        '--error-count',
        type=int,
        required=True,
        help='Number of lychee validation errors'
    )
    parser.add_argument(
        '--modified-files',
        type=int,
        required=True,
        help='Number of git modified files'
    )
    parser.add_argument(
        '--registry',
        type=Path,
        default=Path(__file__).parent.parent / 'state' / 'workflows.json',
        help='Path to workflows.json registry'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )

    args = parser.parse_args()

    if args.debug:
        print(
            f"Debug: error_count={args.error_count}, "
            f"modified_files={args.modified_files}, "
            f"registry={args.registry}",
            file=sys.stderr
        )

    workflows = filter_workflows(
        args.error_count,
        args.modified_files,
        args.registry
    )

    # Output as JSON array
    print(json.dumps(workflows))
    return 0


if __name__ == '__main__':
    sys.exit(main())
