#!/bin/bash
# Session ID Display Hook - Appends session ID to Claude Code responses
# Uses systemMessage field with default system color

# Read hook input from stdin
input_data=$(cat)

# Extract session ID from hook input
session_id=$(echo "$input_data" | jq -r '.session_id // "unknown"')

# Output JSON with systemMessage to display to user (no color codes)
jq -n --arg sid "$session_id" '{
  "systemMessage": ("Session ID: " + $sid),
  "continue": true,
  "suppressOutput": false
}'
