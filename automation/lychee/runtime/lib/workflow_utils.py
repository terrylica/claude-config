"""
Workflow registry utilities for Telegram bot.

Business logic for loading and filtering workflows based on trigger conditions.
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_workflow_registry(registry_path: Path) -> Dict[str, Any]:
    """
    Load workflow registry from workflows.json.

    Args:
        registry_path: Path to workflows.json file

    Returns:
        Workflow registry dictionary

    Raises:
        FileNotFoundError: Registry file not found
        json.JSONDecodeError: Invalid JSON
        ValueError: Invalid registry schema
    """
    if not registry_path.exists():
        raise FileNotFoundError(f"Workflow registry not found: {registry_path}")

    with open(registry_path) as f:
        registry = json.load(f)

    # Validate required fields
    if "version" not in registry or "workflows" not in registry:
        raise ValueError("Invalid registry: missing 'version' or 'workflows'")

    print(f"✅ Loaded workflow registry v{registry['version']} ({len(registry['workflows'])} workflows)")
    return registry


def filter_workflows_by_triggers(
    workflow_registry: Dict[str, Any],
    summary: Dict[str, Any]
) -> list[Dict[str, Any]]:
    """
    Filter workflows based on trigger conditions from session summary.

    Args:
        workflow_registry: Workflow registry dictionary
        summary: SessionSummary data

    Returns:
        List of workflow manifests that match trigger conditions

    Trigger Logic:
        - lychee_errors: true → Only if lychee_status.error_count > 0
        - git_modified: true → Only if git_status.modified_files > 0
        - always: true → Always available
    """
    if workflow_registry is None:
        raise RuntimeError("Workflow registry not loaded")

    available = []
    lychee_errors = summary.get("lychee_status", {}).get("error_count", 0)
    modified_files = summary.get("git_status", {}).get("modified_files", 0)

    for wf_id, workflow in workflow_registry["workflows"].items():
        triggers = workflow.get("triggers", {})

        # Check lychee_errors trigger
        if triggers.get("lychee_errors"):
            if lychee_errors > 0:
                available.append(workflow)
            continue  # Skip other checks if this trigger exists

        # Check git_modified trigger
        if triggers.get("git_modified"):
            if modified_files > 0:
                available.append(workflow)
            continue

        # Check always trigger
        if triggers.get("always"):
            available.append(workflow)

    return available
