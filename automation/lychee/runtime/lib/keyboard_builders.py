"""
Telegram inline keyboard builders for bot workflows.

Constructs interactive button layouts for workflow selection and actions.
"""

from pathlib import Path
from typing import Dict, Any, List

from telegram import InlineKeyboardButton

from workspace_helpers import create_callback_data


def build_workflow_keyboard(
    workflows: List[Dict[str, Any]],
    workspace_id: str,
    workspace_path: Path,
    session_id: str,
    correlation_id: str
) -> List[List[InlineKeyboardButton]]:
    """
    Build dynamic workflow keyboard with custom prompt option.

    Args:
        workflows: List of available workflow dictionaries
        workspace_id: Workspace identifier
        workspace_path: Workspace path
        session_id: Session identifier
        correlation_id: Correlation ID for tracing

    Returns:
        Telegram keyboard layout (list of button rows)
    """
    keyboard = []

    # Add workflow buttons (2 per row for compact layout)
    for i in range(0, len(workflows), 2):
        row = []
        for workflow in workflows[i:i+2]:
            row.append(
                InlineKeyboardButton(
                    f"{workflow['icon']} {workflow['name']}",
                    callback_data=create_callback_data(
                        workspace_id=workspace_id,
                        workspace_path=str(workspace_path),
                        session_id=session_id,
                        action=f"workflow_{workflow['id']}",
                        correlation_id=correlation_id
                    )
                )
            )
        keyboard.append(row)

    # Add custom prompt option (always available)
    keyboard.append([
        InlineKeyboardButton(
            "✏️ Custom Prompt",
            callback_data=create_callback_data(
                workspace_id=workspace_id,
                workspace_path=str(workspace_path),
                session_id=session_id,
                action="custom_prompt",
                correlation_id=correlation_id
            )
        )
    ])

    return keyboard
