#!/bin/bash
echo "$(date): CNS hook entry started" >> /tmp/claude_cns_debug.log

# Auto-enable clipboard debugging for CNS examination
# This ensures the feature is always available for debugging
export CLAUDE_CNS_CLIPBOARD=1

# Pass the JSON input to the conversation handler script in background
# First capture the input, then process it in background
input_data=$(cat)
echo "$input_data" | /Users/terryli/.claude/automation/cns/conversation_handler.sh > /dev/null 2>&1 &