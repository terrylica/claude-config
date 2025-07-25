#!/bin/bash

# Advanced hook debugging wrapper
LOG_FILE="/tmp/claude_tts_debug.log"
HOOK_NAME="$1"
ACTUAL_COMMAND="$2"

echo "$(date): [HOOK-DEBUG] $HOOK_NAME hook execution STARTED" >> "$LOG_FILE"
echo "$(date): [HOOK-DEBUG] Working directory: $(pwd)" >> "$LOG_FILE"
echo "$(date): [HOOK-DEBUG] User: $USER" >> "$LOG_FILE"
echo "$(date): [HOOK-DEBUG] Process PID: $$" >> "$LOG_FILE"
echo "$(date): [HOOK-DEBUG] Parent PID: $PPID" >> "$LOG_FILE"
echo "$(date): [HOOK-DEBUG] Environment PATH: $PATH" >> "$LOG_FILE"
echo "$(date): [HOOK-DEBUG] Command to execute: $ACTUAL_COMMAND" >> "$LOG_FILE"

# Read and log input data
input_data=$(cat)
echo "$(date): [HOOK-DEBUG] Input data: $input_data" >> "$LOG_FILE"

# Execute the actual command
echo "$(date): [HOOK-DEBUG] Executing $HOOK_NAME command..." >> "$LOG_FILE"
echo "$input_data" | eval "$ACTUAL_COMMAND" 2>&1 | while IFS= read -r line; do
    echo "$(date): [HOOK-DEBUG] $HOOK_NAME output: $line" >> "$LOG_FILE"
done

# Capture exit code
exit_code=${PIPESTATUS[1]}
echo "$(date): [HOOK-DEBUG] $HOOK_NAME hook execution COMPLETED with exit code: $exit_code" >> "$LOG_FILE"

exit $exit_code