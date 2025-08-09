#!/bin/bash

# Simplified Claude Response Hook - Clipboard Processing Only
# CNS (Conversation Notification System) - clipboard copying with notification support

# Configuration
CONFIG_DIR="$HOME/.claude/automation/cns/config"
CNS_CONFIG_FILE="$CONFIG_DIR/cns_config.json"

echo "$(date): CNS clipboard hook triggered" >> /tmp/claude_cns_debug.log

# Load configuration
clipboard_enabled="1"  # default enabled
if [[ -f "$CNS_CONFIG_FILE" ]]; then
    clipboard_enabled=$(jq -r '.command_detection.clipboard_enabled // true' "$CNS_CONFIG_FILE" 2>/dev/null)
    if [[ "$clipboard_enabled" == "false" ]]; then
        clipboard_enabled="0"
    else
        clipboard_enabled="1"
    fi
    echo "$(date): Clipboard enabled from config: $clipboard_enabled" >> /tmp/claude_cns_debug.log
else
    echo "$(date): Config file not found, using default clipboard enabled" >> /tmp/claude_cns_debug.log
fi

# Read input from Claude Code hook
input_data=$(cat)
echo "Input received: $input_data" >> /tmp/claude_cns_debug.log

# Parse hook data
session_id=$(echo "$input_data" | jq -r '.session_id // ""')
transcript_path=$(echo "$input_data" | jq -r '.transcript_path // ""')
hook_event=$(echo "$input_data" | jq -r '.hook_event_name // ""')
cwd=$(echo "$input_data" | jq -r '.cwd // ""')

echo "=== HOOK EVENT DETAILS ===" >> /tmp/claude_cns_debug.log
echo "Session ID: $session_id" >> /tmp/claude_cns_debug.log
echo "Transcript path: $transcript_path" >> /tmp/claude_cns_debug.log
echo "Hook event name: $hook_event" >> /tmp/claude_cns_debug.log
echo "Working directory: $cwd" >> /tmp/claude_cns_debug.log
echo "=========================" >> /tmp/claude_cns_debug.log

# Simplified Command Detection Function
detect_user_content_type() {
    local user_text="$1"
    
    # Remove leading/trailing whitespace for analysis
    local trimmed_text=$(echo "$user_text" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
    
    echo "$(date): [CLIPBOARD] Analyzing user input: '${trimmed_text:0:50}...'" >> /tmp/claude_cns_debug.log
    
    # Command detection - starts with # or /
    if [[ "$trimmed_text" =~ ^# ]] || [[ "$trimmed_text" =~ ^/[a-zA-Z] ]]; then
        echo "$(date): [CLIPBOARD] Detected HASH/SLASH COMMAND: ${trimmed_text:0:50}" >> /tmp/claude_cns_debug.log
        echo "command_hash_slash"
        return 0
    fi
    
    # Default to natural language
    echo "$(date): [CLIPBOARD] Classified as NATURAL LANGUAGE: ${trimmed_text:0:30}" >> /tmp/claude_cns_debug.log
    echo "natural_language"
    return 0
}

# Process user content for clipboard only
process_user_clipboard() {
    local user_text="$1"
    
    if [[ -z "$user_text" || ${#user_text} -lt 3 ]]; then
        echo "$(date): User content too short, skipping clipboard" >> /tmp/claude_cns_debug.log
        return 1
    fi
    
    # Detect content type
    local content_type=$(detect_user_content_type "$user_text")
    echo "$(date): [CLIPBOARD] User content type: $content_type" >> /tmp/claude_cns_debug.log
    
    # Note: Clipboard handling moved to combined function after finding both user and Claude content
    echo "$(date): User content processed, clipboard will be handled after finding Claude response" >> /tmp/claude_cns_debug.log
}

if [[ -n "$transcript_path" && -f "$transcript_path" ]]; then
    echo "File exists and is readable" >> /tmp/claude_cns_debug.log
    
    # Wait for transcript to be fully written
    max_attempts=10
    attempt=0
    last_response=""
    
    while [[ $attempt -lt $max_attempts ]]; do
        # Get recent lines to find the latest response
        last_lines=$(tail -50 "$transcript_path" 2>/dev/null)
        
        # Look for assistant response with our session ID
        temp_response=$(echo "$last_lines" | tail -r | while read -r line; do
            if [[ -n "$line" ]]; then
                # Check if this is an assistant message with matching session
                if echo "$line" | jq -e --arg session "$session_id" 'select(.type == "assistant" and .sessionId == $session)' >/dev/null 2>&1; then
                    # Extract message content from the new format
                    content=$(echo "$line" | jq -r '.message.content[0].text // empty' 2>/dev/null)
                    if [[ -n "$content" ]]; then
                        echo "$content"
                        break
                    fi
                fi
            fi
        done)
        
        if [[ -n "$temp_response" && ${#temp_response} -gt 50 ]]; then
            last_response="$temp_response"
            echo "Found complete response on attempt $((attempt + 1)): ${#last_response} chars" >> /tmp/claude_cns_debug.log
            break
        else
            attempt=$((attempt + 1))
            sleep 0.5
        fi
    done
    
    # Extract user prompt for clipboard
    echo "Searching for user prompt with specific pattern..." >> /tmp/claude_cns_debug.log
    
    user_prompt=$(echo "$last_lines" | tac | while read -r line; do
        if [[ -n "$line" ]]; then
            echo "Checking line: $(echo "$line" | jq -r 'select(.type != null) | "type=\(.type), sessionId=\(.sessionId // "none")"' 2>/dev/null || echo "Invalid JSON")" >> /tmp/claude_cns_debug.log
            
            # Check if this is a user message with matching session
            if echo "$line" | jq -e --arg session "$session_id" 'select(.type == "user" and .sessionId == $session)' >/dev/null 2>&1; then
                # Skip tool result messages - check if message.content is an array with tool_result
                if echo "$line" | jq -e '.message.content[0].type == "tool_result"' >/dev/null 2>&1; then
                    echo "Skipping tool result message" >> /tmp/claude_cns_debug.log
                    continue
                fi
                
                # Extract message content - handle both string and array formats
                content=$(echo "$line" | jq -r '.message.content // empty' 2>/dev/null)
                if [[ -n "$content" && ${#content} -gt 10 ]]; then
                    echo "Found user text message with content: ${content:0:50}..." >> /tmp/claude_cns_debug.log
                    echo "$content"
                    break
                fi
            fi
        fi
    done)
    
    if [[ -n "$user_prompt" ]]; then
        echo "Found user prompt: ${#user_prompt} chars" >> /tmp/claude_cns_debug.log
        echo "User prompt first 100 chars: ${user_prompt:0:100}" >> /tmp/claude_cns_debug.log
        
        # Process user content for clipboard
        process_user_clipboard "$user_prompt"
    else
        echo "No user prompt found in transcript" >> /tmp/claude_cns_debug.log
    fi
    
    if [[ -n "$last_response" ]]; then
        echo "Final extracted response length: ${#last_response}" >> /tmp/claude_cns_debug.log
        echo "First 150 chars: ${last_response:0:150}" >> /tmp/claude_cns_debug.log
        echo "$(date): Content extracted - User: ${#user_prompt} chars, Claude: ${#last_response} chars" >> /tmp/claude_cns_debug.log
        
        # Copy both user prompt and Claude response to clipboard
        # Check both environment variable and config file setting
        local should_copy_clipboard="${CLAUDE_CNS_CLIPBOARD:-$clipboard_enabled}"
        if [[ "$should_copy_clipboard" == "1" && -n "$user_prompt" ]]; then
            # Create combined content with proper formatting
            local combined_content
            combined_content=$(printf "USER: %s\n\nCLAUDE: %s" "$user_prompt" "$last_response")
            
            # Platform-specific clipboard copy
            if command -v pbcopy >/dev/null 2>&1; then
                # macOS
                if printf "%s" "$combined_content" | pbcopy 2>/dev/null; then
                    echo "$(date): Combined content copied to clipboard: User(${#user_prompt}) + Claude(${#last_response}) chars" >> /tmp/claude_cns_debug.log
                else
                    echo "$(date): Failed to copy combined content to clipboard (pbcopy)" >> /tmp/claude_cns_debug.log
                fi
            elif command -v xclip >/dev/null 2>&1; then
                # Linux with xclip
                if printf "%s" "$combined_content" | xclip -selection clipboard 2>/dev/null; then
                    echo "$(date): Combined content copied to clipboard: User(${#user_prompt}) + Claude(${#last_response}) chars" >> /tmp/claude_cns_debug.log
                else
                    echo "$(date): Failed to copy combined content to clipboard (xclip)" >> /tmp/claude_cns_debug.log
                fi
            elif command -v xsel >/dev/null 2>&1; then
                # Linux with xsel
                if printf "%s" "$combined_content" | xsel --clipboard --input 2>/dev/null; then
                    echo "$(date): Combined content copied to clipboard: User(${#user_prompt}) + Claude(${#last_response}) chars" >> /tmp/claude_cns_debug.log
                else
                    echo "$(date): Failed to copy combined content to clipboard (xsel)" >> /tmp/claude_cns_debug.log
                fi
            else
                echo "$(date): No supported clipboard tool found (pbcopy/xclip/xsel)" >> /tmp/claude_cns_debug.log
            fi
        else
            echo "$(date): Clipboard copying disabled (config: $clipboard_enabled, env: ${CLAUDE_CNS_CLIPBOARD:-unset})" >> /tmp/claude_cns_debug.log
        fi
        
        # Trigger audio notification with working directory context
        echo "$(date): Triggering notification hook with cwd: $cwd" >> /tmp/claude_cns_debug.log
        echo "$input_data" | "$HOME/.claude/automation/cns/cns_notification_hook.sh" &
    else
        echo "No valid response found after $max_attempts attempts" >> /tmp/claude_cns_debug.log
    fi
else
    echo "Transcript file not found or not readable: $transcript_path" >> /tmp/claude_cns_debug.log
fi

echo "$(date): CNS clipboard hook completed" >> /tmp/claude_cns_debug.log