#!/bin/bash
# Async CNS hook - capture input then spawn background process
export CLAUDE_CNS_CLIPBOARD=1
input_data=$(cat)
{
    echo "$input_data" | "$HOME/.claude/automation/cns/conversation_handler.sh" > /dev/null 2>&1
} &
# Exit immediately, don't wait for background process