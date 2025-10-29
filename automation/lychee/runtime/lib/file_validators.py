"""
JSON file validation for Telegram bot state files.

Validates required fields in notification, completion, execution, and summary files.
Raises ValueError on missing fields or JSON parse errors.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def validate_json_file(
    file_path: Path,
    required_fields: List[str],
    file_type: str = "file"
) -> Dict[str, Any]:
    """
    Read and validate JSON file with required fields.

    Args:
        file_path: Path to JSON file
        required_fields: List of required field names
        file_type: Human-readable file type for error messages

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file isn't valid JSON
        ValueError: If required fields are missing
    """
    if not file_path.exists():
        raise FileNotFoundError(f"{file_type} not found: {file_path}")

    with file_path.open() as f:
        data = json.load(f)

    # Validate required fields
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"Missing required fields in {file_type}: {missing}")

    return data


def validate_notification_file(notification_file: Path) -> Dict[str, Any]:
    """
    Read and validate notification request file.

    Args:
        notification_file: Path to notification JSON

    Returns:
        Validated notification data

    Raises:
        ValueError: If required fields missing
        json.JSONDecodeError: If invalid JSON
    """
    required = ["workspace_path", "session_id", "error_count", "details", "timestamp"]
    return validate_json_file(notification_file, required, "notification")


def validate_completion_file(completion_file: Path) -> Dict[str, Any]:
    """
    Read and validate completion notification file.

    Args:
        completion_file: Path to completion JSON

    Returns:
        Validated completion data

    Raises:
        ValueError: If required fields missing
        json.JSONDecodeError: If invalid JSON
    """
    required = ["workspace_id", "session_id", "status", "exit_code",
                "duration_seconds", "summary", "timestamp"]
    return validate_json_file(completion_file, required, "completion")


def validate_execution_file(execution_file: Path) -> Dict[str, Any]:
    """
    Read and validate workflow execution file.

    Args:
        execution_file: Path to execution JSON

    Returns:
        Validated execution data

    Raises:
        ValueError: If required fields missing
        json.JSONDecodeError: If invalid JSON
    """
    required = ["correlation_id", "workspace_id", "session_id", "workflow_id",
                "workflow_name", "status", "exit_code", "duration_seconds", "timestamp"]
    return validate_json_file(execution_file, required, "execution")


def validate_summary_file(summary_file: Path) -> Dict[str, Any]:
    """
    Read and validate session summary file.

    Args:
        summary_file: Path to summary JSON

    Returns:
        Validated summary data

    Raises:
        ValueError: If required fields missing
        json.JSONDecodeError: If invalid JSON with detailed error reporting
    """
    try:
        with summary_file.open() as f:
            content = f.read()
            data = json.loads(content)
    except json.JSONDecodeError as e:
        # Provide detailed error context for debugging
        print(f"❌ JSON PARSE ERROR in {summary_file.name}:")
        print(f"   Error: {e}")
        print(f"   File content:")
        for i, line in enumerate(content.split('\n'), 1):
            marker = " <-- ERROR" if i == e.lineno else ""
            print(f"   {i:3d}: {line}{marker}")
        raise

    required = ["correlation_id", "workspace_path", "workspace_id", "session_id",
                "timestamp", "duration_seconds", "git_status", "lychee_status"]
    missing = [f for f in required if f not in data]
    if missing:
        raise ValueError(f"Missing required fields in summary: {missing}")

    return data
