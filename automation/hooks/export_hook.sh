#!/bin/bash

# Auto-Export Hook for Claude Code
# Uses claude-code-exporter to automatically export conversations

LOG_FILE="/tmp/claude_export_debug.log"
EXPORT_DIR="$HOME/.claude/exports"

echo "$(date): Auto-export hook triggered" >> "$LOG_FILE"

# Read hook data from stdin
hook_data=$(cat)

# Extract project directory from hook data
cwd=$(echo "$hook_data" | jq -r '.cwd // ""')
session_id=$(echo "$hook_data" | jq -r '.session_id // ""')

if [[ -n "$cwd" && "$cwd" != "null" ]]; then
    # Create export directory if it doesn't exist
    mkdir -p "$EXPORT_DIR"
    
    # Generate timestamp for export file
    timestamp=$(date +%Y%m%d_%H%M%S)
    
    # Export conversation using claude-code-exporter
    export_file="$EXPORT_DIR/conversation_${timestamp}.md"
    
    echo "$(date): Exporting conversation from $cwd to $export_file" >> "$LOG_FILE"
    
    # Export the conversation (prompts only, markdown format)
    if claude-prompts "$cwd" --output="$export_file" 2>>"$LOG_FILE"; then
        echo "$(date): Successfully exported conversation to $export_file" >> "$LOG_FILE"
        
        # Optional: Copy to clipboard for immediate use
        if [[ -f "$export_file" ]]; then
            cat "$export_file" | pbcopy 2>/dev/null && \
                echo "$(date): Exported conversation copied to clipboard" >> "$LOG_FILE"
        fi
    else
        echo "$(date): Failed to export conversation from $cwd" >> "$LOG_FILE"
    fi
else
    echo "$(date): No valid project directory found in hook data" >> "$LOG_FILE"
fi

echo "$(date): Auto-export hook completed" >> "$LOG_FILE"