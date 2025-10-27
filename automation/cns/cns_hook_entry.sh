#!/bin/bash
# CNS hook - supports both local and remote SSH environments
# Maintains fire-and-forget async pattern for <10ms execution

# Capture input immediately
input_data=$(cat)

# Note: Terminal display removed - Claude Code suppresses hook output
# Session ID is visible in status line instead

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

        # If both are empty, create directory context message matching local behavior
        if [[ -z "$user_prompt" && -z "$claude_response" ]]; then
            working_dir=$(pwd 2>/dev/null || echo "unknown")
            working_dir_name=$(basename "$working_dir" 2>/dev/null || echo "directory")

            # Format directory name for proper TTS pronunciation (match local behavior)
            if [[ "$working_dir_name" == .* ]]; then
                claude_response="dot ${working_dir_name:1}"
            else
                claude_response="$working_dir_name"
            fi
        fi

        # Export metadata for remote client
        export CNS_SESSION_ID=$(echo "$input_data" | jq -r '.session_id // "unknown"' 2>/dev/null)
        export CNS_HOOK_EVENT=$(echo "$input_data" | jq -r '.hook_event_name // "unknown"' 2>/dev/null)

        # Send to remote client with hook integration
        "$HOME/.claude/tools/cns-remote-client.sh" --hook "$user_prompt" "$claude_response"
        
    else
        # Local environment - use existing CNS system
        echo "$(date): Local environment detected, using existing CNS" >> /tmp/claude_cns_debug.log
        export CLAUDE_CNS_CLIPBOARD=1

        # Extract metadata for potential Pushover fallback
        export CNS_SESSION_ID=$(echo "$input_data" | jq -r '.session_id // "unknown"' 2>/dev/null)
        export CNS_HOOK_EVENT=$(echo "$input_data" | jq -r '.hook_event_name // "unknown"' 2>/dev/null)
        export CNS_CWD=$(echo "$input_data" | jq -r '.cwd // ""' 2>/dev/null)

        echo "$input_data" | "$HOME/.claude/automation/cns/conversation_handler.sh" > /dev/null 2>&1
    fi
} &

# Exit immediately for async performance - don't wait for background process
exit 0