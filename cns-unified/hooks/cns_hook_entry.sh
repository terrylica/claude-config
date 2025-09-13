#!/bin/bash
# CNS hook - supports both local and remote SSH environments
# Maintains fire-and-forget async pattern for <10ms execution

# Capture input immediately
input_data=$(cat)

# Environment detection - quick checks only
is_ssh_session() {
    [[ -n "${SSH_CLIENT:-}" || -n "${SSH_CONNECTION:-}" ]]
}

# Quick remote client availability check
has_remote_client() {
    [[ -x "$HOME/.claude/tools/cns-remote-client.sh" ]]
}

# Route to appropriate handler based on environment
{
    if is_ssh_session && has_remote_client; then
        # Remote SSH environment - use remote client
        echo "$(date): Remote SSH session detected, routing to remote client" >> /tmp/claude_cns_debug.log
        
        # Extract user prompt and Claude response for remote client
        user_prompt=$(echo "$input_data" | jq -r '.user_prompt // empty' 2>/dev/null || echo "")
        claude_response=$(echo "$input_data" | jq -r '.claude_response // empty' 2>/dev/null || echo "$input_data")
        
        # Send to remote client with hook integration
        "$HOME/.claude/tools/cns-remote-client.sh" --hook "$user_prompt" "$claude_response"
        
    else
        # Local environment - use existing CNS system
        echo "$(date): Local environment detected, using existing CNS" >> /tmp/claude_cns_debug.log
        export CLAUDE_CNS_CLIPBOARD=1
        echo "$input_data" | "$HOME/.claude/automation/cns/conversation_handler.sh" > /dev/null 2>&1
    fi
} &

# Exit immediately for async performance - don't wait for background process