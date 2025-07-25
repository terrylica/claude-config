#!/bin/bash

# Enhanced TTS script - Intelligently speaks Claude responses with paragraph aggregation
#
# KNOWN LIMITATION: Interactive plan approval dialogs do NOT trigger any hook events
# - Plan presentation works (triggers Stop hook)
# - Normal responses work (triggers Stop hook) 
# - Interactive prompts ("Would you like to proceed? 1/2/3") bypass hook system entirely
# - This is a confirmed Claude Code limitation (GitHub issues #1460, #2223)
# - No UserPromptSubmit, Notification, or other hooks fire during interactive prompts
# - Users must rely on manual TTS commands for interactive prompt feedback
#
# Configurable TTS parameters
SPEECH_RATE=198                    # Words per minute (10% slower than 220)
CHARS_PER_SECOND=16.50            # Estimated characters per second (198 WPM / 60 * 5 chars/word)
MAX_FULL_RESPONSE_SECONDS=10      # If entire response ≤ this, read it all
MIN_PARAGRAPH_CHARS=50            # Minimum characters for a paragraph to be considered adequate
TARGET_MIN_SECONDS=5              # Target minimum speech duration 
TARGET_MAX_SECONDS=25             # Target maximum speech duration before stopping aggregation
TARGET_MIN_CHARS=$(echo "$TARGET_MIN_SECONDS * $CHARS_PER_SECOND" | bc -l | awk '{printf "%.0f", $0}')
TARGET_MAX_CHARS=$(echo "$TARGET_MAX_SECONDS * $CHARS_PER_SECOND" | bc -l | awk '{printf "%.0f", $0}')
# Rotate log if it gets too large (>50KB)
if [[ -f /tmp/claude_tts_debug.log ]] && [[ $(stat -f%z /tmp/claude_tts_debug.log 2>/dev/null || echo 0) -gt 51200 ]]; then
    mv /tmp/claude_tts_debug.log /tmp/claude_tts_debug.log.old
fi
echo "$(date): Enhanced TTS hook triggered" >> /tmp/claude_tts_debug.log
echo "$(date): Glass sound should have played before this entry" >> /tmp/claude_tts_debug.log

# Read JSON input from stdin
input=$(cat)
echo "Input received: $input" >> /tmp/claude_tts_debug.log

# Extract all available fields from JSON input for debugging
session_id=$(echo "$input" | jq -r '.session_id // empty')
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty')
hook_event_name=$(echo "$input" | jq -r '.hook_event_name // empty')
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active // empty')
cwd=$(echo "$input" | jq -r '.cwd // empty')

echo "=== HOOK EVENT DETAILS ===" >> /tmp/claude_tts_debug.log
echo "Session ID: $session_id" >> /tmp/claude_tts_debug.log
echo "Transcript path: $transcript_path" >> /tmp/claude_tts_debug.log
echo "Hook event name: $hook_event_name" >> /tmp/claude_tts_debug.log
echo "Stop hook active: $stop_hook_active" >> /tmp/claude_tts_debug.log
echo "Working directory: $cwd" >> /tmp/claude_tts_debug.log
echo "=========================" >> /tmp/claude_tts_debug.log

if [[ -n "$transcript_path" && -f "$transcript_path" ]]; then
    echo "File exists and is readable" >> /tmp/claude_tts_debug.log
    
    # Wait for transcript to be fully written by polling for a complete entry
    # We'll wait up to 5 seconds, checking every 0.5 seconds
    max_attempts=10
    attempt=0
    last_response=""
    
    while [[ $attempt -lt $max_attempts ]]; do
        # Get more lines to ensure we capture user prompts in long sessions
        last_lines=$(tail -50 "$transcript_path" 2>/dev/null)
        
        # Look for assistant response with our session ID
        temp_response=$(echo "$last_lines" | tail -r | while read -r line; do
            if [[ -n "$line" ]]; then
                # Check if this is an assistant message with matching session
                role=$(echo "$line" | jq -r '.message.role // empty' 2>/dev/null)
                type=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
                line_session=$(echo "$line" | jq -r '.sessionId // empty' 2>/dev/null)
                
                if [[ "$role" == "assistant" && "$type" == "assistant" && "$line_session" == "$session_id" ]]; then
                    # Try to extract text content
                    text_content=$(echo "$line" | jq -r '.message.content[]? | select(.type == "text") | .text // empty' 2>/dev/null)
                    
                    if [[ -n "$text_content" && ${#text_content} -gt 20 ]]; then
                        echo "$text_content"
                        exit 0
                    fi
                fi
            fi
        done 2>/dev/null)
        
        if [[ -n "$temp_response" && ${#temp_response} -gt 20 ]]; then
            last_response="$temp_response"
            echo "Found complete response on attempt $((attempt + 1)): ${#last_response} chars" >> /tmp/claude_tts_debug.log
            break
        fi
        
        echo "Attempt $((attempt + 1)): Waiting for complete transcript entry..." >> /tmp/claude_tts_debug.log
        sleep 0.5
        ((attempt++))
    done
    
    if [[ -z "$last_response" ]]; then
        echo "Timeout: Falling back to any available response" >> /tmp/claude_tts_debug.log
        # Fallback: try to get any recent assistant response
        last_response=$(echo "$last_lines" | tail -r | while read -r line; do
            if [[ -n "$line" ]]; then
                role=$(echo "$line" | jq -r '.message.role // empty' 2>/dev/null)
                type=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
                
                if [[ "$role" == "assistant" && "$type" == "assistant" ]]; then
                    text_content=$(echo "$line" | jq -r '.message.content[]? | select(.type == "text") | .text // empty' 2>/dev/null)
                    if [[ -n "$text_content" && ${#text_content} -gt 10 ]]; then
                        echo "$text_content"
                        exit 0
                    fi
                fi
            fi
        done 2>/dev/null)
    fi
    
    # Also look for user prompt with specific pattern
    user_prompt=""
    echo "Searching for user prompt with specific pattern..." >> /tmp/claude_tts_debug.log
    
    # Look for the most recent user message in this session
    echo "Searching for user message in session: $session_id" >> /tmp/claude_tts_debug.log
    echo "Available lines to search: $(echo "$last_lines" | wc -l)" >> /tmp/claude_tts_debug.log
    
    user_content=$(echo "$last_lines" | tail -r | while read -r line; do
        if [[ -n "$line" ]]; then
            role=$(echo "$line" | jq -r '.message.role // empty' 2>/dev/null)
            type=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
            line_session=$(echo "$line" | jq -r '.sessionId // empty' 2>/dev/null)
            
            echo "Checking line: role=$role, type=$type, session=$line_session" >> /tmp/claude_tts_debug.log
            
            if [[ "$role" == "user" && "$type" == "user" && "$line_session" == "$session_id" ]]; then
                # Skip tool result messages - look for actual text messages only
                has_tool_result=$(echo "$line" | jq -r '.message.content[]? | select(.type == "tool_result") | .type // empty' 2>/dev/null)
                
                if [[ -z "$has_tool_result" ]]; then
                    # Try to extract text content from real user messages
                    text_content=$(echo "$line" | jq -r '.message.content[]? | select(.type == "text") | .text // empty' 2>/dev/null)
                    
                    # If that fails, try alternative extraction methods
                    if [[ -z "$text_content" ]]; then
                        text_content=$(echo "$line" | jq -r '.message.content[0].text // empty' 2>/dev/null)
                    fi
                    
                    # Check if content is a string (not object/array)
                    if [[ -z "$text_content" ]]; then
                        content_type=$(echo "$line" | jq -r '.message.content | type' 2>/dev/null)
                        if [[ "$content_type" == "string" ]]; then
                            text_content=$(echo "$line" | jq -r '.message.content // empty' 2>/dev/null)
                        fi
                    fi
                    
                    echo "Found user text message with content: ${text_content:0:50}..." >> /tmp/claude_tts_debug.log
                    
                    if [[ -n "$text_content" && "$text_content" != "null" && ${#text_content} -gt 2 ]]; then
                        echo "$text_content"
                        exit 0
                    fi
                else
                    echo "Skipping tool result message" >> /tmp/claude_tts_debug.log
                fi
            fi
        fi
    done 2>/dev/null)
    
    # If no exact session match, search more aggressively in longer transcript
    if [[ -z "$user_content" ]]; then
        echo "No session-specific user message found, searching more extensively" >> /tmp/claude_tts_debug.log
        # Search the last 100 lines for user prompts in long sessions
        extended_lines=$(tail -100 "$transcript_path" 2>/dev/null)
        user_content=$(echo "$extended_lines" | tail -r | while read -r line; do
            if [[ -n "$line" ]]; then
                role=$(echo "$line" | jq -r '.message.role // empty' 2>/dev/null)
                type=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
                
                if [[ "$role" == "user" && "$type" == "user" ]]; then
                    # CRITICAL: Skip tool result messages completely in fallback too!
                    has_tool_result=$(echo "$line" | jq -r '.message.content[]? | select(.type == "tool_result") | .type // empty' 2>/dev/null)
                    
                    if [[ -z "$has_tool_result" ]]; then
                        # Try multiple extraction methods for user text content
                        text_content=$(echo "$line" | jq -r '.message.content[]? | select(.type == "text") | .text // empty' 2>/dev/null)
                        
                        # If that fails, try alternative extraction methods
                        if [[ -z "$text_content" ]]; then
                            text_content=$(echo "$line" | jq -r '.message.content[0].text // empty' 2>/dev/null)
                        fi
                        
                        # Check if content is a string (not object/array) and not a tool result
                        if [[ -z "$text_content" ]]; then
                            content_type=$(echo "$line" | jq -r '.message.content | type' 2>/dev/null)
                            if [[ "$content_type" == "string" ]]; then
                                candidate_content=$(echo "$line" | jq -r '.message.content // empty' 2>/dev/null)
                                # Reject content that looks like tool results (contains tool_use_id)
                                if [[ "$candidate_content" != *"tool_use_id"* ]]; then
                                    text_content="$candidate_content"
                                fi
                            fi
                        fi
                        
                        if [[ -n "$text_content" && "$text_content" != "null" && ${#text_content} -gt 2 && "$text_content" != *"tool_use_id"* ]]; then
                            echo "Found fallback user message: ${text_content:0:50}..." >> /tmp/claude_tts_debug.log
                            echo "$text_content"
                            exit 0
                        else
                            echo "Skipping potential tool result in fallback: ${text_content:0:30}..." >> /tmp/claude_tts_debug.log
                        fi
                    else
                        echo "Skipping tool result message in fallback" >> /tmp/claude_tts_debug.log
                    fi
                fi
            fi
        done 2>/dev/null)
    fi
    
    # Always use the user prompt if found (no pattern matching)
    if [[ -n "$user_content" ]]; then
        user_prompt="$user_content"
        echo "Found user prompt: ${#user_prompt} chars" >> /tmp/claude_tts_debug.log
        echo "User prompt first 100 chars: ${user_prompt:0:100}..." >> /tmp/claude_tts_debug.log
    else
        # Final fallback: search entire transcript for most recent user message in this session
        echo "No user prompt found in recent lines, searching entire transcript" >> /tmp/claude_tts_debug.log
        full_transcript_user=$(grep "\"sessionId\":\"$session_id\"" "$transcript_path" 2>/dev/null | tail -r | while read -r line; do
            role=$(echo "$line" | jq -r '.message.role // empty' 2>/dev/null)
            type=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
            
            if [[ "$role" == "user" && "$type" == "user" ]]; then
                # Skip tool result messages
                has_tool_result=$(echo "$line" | jq -r '.message.content[]? | select(.type == "tool_result") | .type // empty' 2>/dev/null)
                
                if [[ -z "$has_tool_result" ]]; then
                    text_content=$(echo "$line" | jq -r '.message.content[]? | select(.type == "text") | .text // empty' 2>/dev/null)
                    
                    if [[ -z "$text_content" ]]; then
                        content_type=$(echo "$line" | jq -r '.message.content | type' 2>/dev/null)
                        if [[ "$content_type" == "string" ]]; then
                            text_content=$(echo "$line" | jq -r '.message.content // empty' 2>/dev/null)
                        fi
                    fi
                    
                    if [[ -n "$text_content" && "$text_content" != "null" && ${#text_content} -gt 2 ]]; then
                        echo "$text_content"
                        exit 0
                    fi
                fi
            fi
        done 2>/dev/null)
        
        if [[ -n "$full_transcript_user" ]]; then
            user_prompt="$full_transcript_user"
            echo "Found user prompt from full transcript search: ${#user_prompt} chars" >> /tmp/claude_tts_debug.log
        else
            # Ultimate fallback: generic prompt announcement
            user_prompt="Your previous request"
            echo "Using generic user prompt fallback" >> /tmp/claude_tts_debug.log
        fi
    fi
    
    echo "Final extracted response length: ${#last_response}" >> /tmp/claude_tts_debug.log
    echo "First 150 chars: ${last_response:0:150}..." >> /tmp/claude_tts_debug.log
    
    if [[ -n "$last_response" && ${#last_response} -gt 10 ]]; then
        # Prepare content for TTS - combine user prompt and assistant response if both exist
        combined_content=""
        
        # Define reusable function for creating user-prefixed content
        create_user_prefixed_content() {
            local user_text="$1"
            local assistant_text="$2"
            echo "Yourhighness the Great, Destroyer of Catastrophically Underwhelming Flesh-Based Social Protocols prompted. $user_text... Claude Code responded as follows. $assistant_text"
        }
        
        if [[ -n "$user_prompt" ]]; then
            # Clean user prompt
            clean_user_prompt=$(echo "$user_prompt" | \
                sed 's/\\n/ /g' | \
                sed 's/\*\*\([^*]*\)\*\*/\1/g' | \
                sed 's/`\([^`]*\)`/\1/g' | \
                sed 's/<[^>]*>//g')
            
            echo "Added user prompt to TTS content: ${#clean_user_prompt} chars" >> /tmp/claude_tts_debug.log
        fi
        
        # Clean up assistant response markdown
        clean_text=$(echo "$last_response" | \
            sed 's/\\n/ /g' | \
            sed 's/\*\*\([^*]*\)\*\*/\1/g' | \
            sed 's/`\([^`]*\)`/\1/g' | \
            sed 's/<[^>]*>//g')
        
        # Combine user prompt and assistant response using DRY function
        if [[ -n "$user_prompt" ]]; then
            combined_content=$(create_user_prefixed_content "$clean_user_prompt" "$clean_text")
        else
            combined_content="$clean_text"
        fi
        
        echo "Combined content length: ${#combined_content}" >> /tmp/claude_tts_debug.log
        echo "Using combined content for TTS processing" >> /tmp/claude_tts_debug.log
        
        # Calculate estimated speech time using combined content
        estimated_seconds=$(echo "${#combined_content} / $CHARS_PER_SECOND" | bc -l | awk '{printf "%.1f", $0}')
        echo "Estimated speech time: ${estimated_seconds} seconds for ${#combined_content} characters" >> /tmp/claude_tts_debug.log
        
        # If combined content is short enough, read the entire thing
        if (( $(echo "$estimated_seconds <= $MAX_FULL_RESPONSE_SECONDS" | bc -l) )); then
            final_sentence="$combined_content"
            echo "Reading entire combined content (${estimated_seconds}s ≤ 10s)" >> /tmp/claude_tts_debug.log
        else
            # For longer content, use intelligent paragraph aggregation on the assistant response part only
            echo "Combined content too long (${estimated_seconds}s > ${MAX_FULL_RESPONSE_SECONDS}s), using paragraph aggregation" >> /tmp/claude_tts_debug.log
            
            # Split assistant response text into paragraphs using a more compatible approach
            # First convert escaped newlines to real newlines
            normalized_text=$(echo "$clean_text" | sed 's/\\n/\n/g')
            
            # Split into paragraphs - first try double newlines, then single
            if echo "$normalized_text" | grep -q $'\n\n'; then
                # Split on double newlines and filter non-empty paragraphs
                paragraph_list=$(echo "$normalized_text" | awk 'BEGIN{RS="\n\n"} {gsub(/^[[:space:]]+|[[:space:]]+$/, ""); if(length > 5) print $0}')
                echo "Using double-newline paragraph separation" >> /tmp/claude_tts_debug.log
            else
                # Split on single newlines and filter substantial content
                paragraph_list=$(echo "$normalized_text" | awk 'BEGIN{RS="\n"} {gsub(/^[[:space:]]+|[[:space:]]+$/, ""); if(length > 15) print $0}')
                echo "Using single-newline paragraph separation" >> /tmp/claude_tts_debug.log
            fi
            
            # Convert to array using a simple approach
            paragraph_array=()
            while IFS= read -r line; do
                if [[ -n "$line" ]]; then
                    paragraph_array+=("$line")
                fi
            done <<< "$paragraph_list"
            
            echo "Found ${#paragraph_array[@]} paragraphs" >> /tmp/claude_tts_debug.log
            
            if [[ ${#paragraph_array[@]} -eq 0 ]]; then
                # Fallback if no paragraphs found
                fallback_text=$(echo "$clean_text" | tail -c 150 | sed 's/^[[:space:]]*//')
                if [[ -n "$user_prompt" ]]; then
                    final_sentence=$(create_user_prefixed_content "$clean_user_prompt" "$fallback_text")
                else
                    final_sentence="$fallback_text"
                fi
                echo "No paragraphs found, using last 150 characters with user prompt if available" >> /tmp/claude_tts_debug.log
            else
                # Start with the last paragraph and work backwards
                aggregated_text=""
                paragraph_count=0
                
                # Work backwards through paragraphs
                for (( i=${#paragraph_array[@]}-1; i>=0; i-- )); do
                    # Get current paragraph content
                    current_paragraph="${paragraph_array[i]}"
                    
                    # Try adding this paragraph to our aggregated text with pause markers
                    if [[ -z "$aggregated_text" ]]; then
                        potential_text="$current_paragraph"
                    else
                        # Add paragraph break with pause marker for TTS
                        potential_text="$current_paragraph... $aggregated_text"
                    fi
                    
                    potential_length=${#potential_text}
                    potential_seconds=$(echo "$potential_length / $CHARS_PER_SECOND" | bc -l)
                    
                    echo "Considering paragraph $((i+1)): ${#current_paragraph} chars, total would be ${potential_length} chars (${potential_seconds}s)" >> /tmp/claude_tts_debug.log
                    
                    # If adding this paragraph would exceed our target max, stop (unless we have nothing yet)
                    if [[ -n "$aggregated_text" ]] && (( $(echo "$potential_length > $TARGET_MAX_CHARS" | bc -l) )); then
                        echo "Adding paragraph would exceed target max (${TARGET_MAX_CHARS} chars), stopping aggregation" >> /tmp/claude_tts_debug.log
                        break
                    fi
                    
                    # Add this paragraph
                    aggregated_text="$potential_text"
                    ((paragraph_count++))
                    
                    # Only stop if we've reached close to the maximum target (95% threshold)
                    # Keep aggregating to provide comprehensive content coverage
                    if (( potential_length >= TARGET_MIN_CHARS )) && (( potential_length >= (TARGET_MAX_CHARS * 95 / 100) )); then
                        echo "Reached comprehensive content (${potential_length} chars ≥ 95% of target max), stopping aggregation" >> /tmp/claude_tts_debug.log
                        break
                    fi
                done
                
                # If we still don't have enough content, use what we have
                if [[ -z "$aggregated_text" ]]; then
                    aggregated_text="${paragraph_array[-1]}"  # Last paragraph
                    echo "Fallback: using last paragraph only" >> /tmp/claude_tts_debug.log
                fi
                
                # Prepend user prompt if available using DRY function
                if [[ -n "$user_prompt" ]]; then
                    final_sentence=$(create_user_prefixed_content "$clean_user_prompt" "$aggregated_text")
                else
                    final_sentence="$aggregated_text"
                fi
                
                final_length=${#final_sentence}
                final_seconds=$(echo "$final_length / $CHARS_PER_SECOND" | bc -l | awk '{printf "%.1f", $0}')
                echo "Final aggregation: $paragraph_count paragraph(s), ${final_length} chars, ${final_seconds}s" >> /tmp/claude_tts_debug.log
            fi
        fi
        
        echo "Final text for TTS (${#final_sentence} chars): ${final_sentence:0:100}..." >> /tmp/claude_tts_debug.log
        
        # === CLIPBOARD DEBUGGING FEATURE ===
        # Copy TTS content to clipboard for user examination
        # Enable with: export CLAUDE_TTS_TO_CLIPBOARD=1
        echo "$(date): Checking clipboard debug flag: CLAUDE_TTS_TO_CLIPBOARD='${CLAUDE_TTS_TO_CLIPBOARD:-UNSET}'" >> /tmp/claude_tts_debug.log
        if [[ "${CLAUDE_TTS_TO_CLIPBOARD:-0}" == "1" ]]; then
            # Create comprehensive clipboard content with metadata
            clipboard_content="=== Claude TTS Content Debug $(date) ===
Session: $session_id
Length: ${#final_sentence} chars
Estimated Duration: $(echo "${#final_sentence} / $CHARS_PER_SECOND" | bc -l | awk '{printf "%.1f", $0}')s
Speech Rate: ${SPEECH_RATE} WPM

=== ORIGINAL TEXT ===
$final_sentence

=== SANITIZED TEXT (what actually gets spoken) ===
[Will be shown after sanitization]

=== END DEBUG INFO ===
"
            
            # Copy to clipboard with error handling
            if echo "$clipboard_content" | pbcopy 2>/dev/null; then
                echo "$(date): TTS content copied to clipboard for debugging" >> /tmp/claude_tts_debug.log
            else
                echo "$(date): Failed to copy TTS content to clipboard" >> /tmp/claude_tts_debug.log
            fi
            
            # Also save to persistent debug file for examination
            debug_file="/tmp/claude_tts_content_$(date +%Y%m%d_%H%M%S).txt"
            echo "$clipboard_content" > "$debug_file" 2>/dev/null && \
                echo "$(date): TTS content saved to $debug_file" >> /tmp/claude_tts_debug.log
        fi
        
        # Speak the final sentence using configured speech rate
        if [[ -n "$final_sentence" && ${#final_sentence} -gt 3 ]]; then
            # BULLETPROOF TTS Sanitization (Multi-Layer Defense)
            sanitized_text="$final_sentence"
            
            # Layer 1: Basic character normalization
            sanitized_text=$(echo "$sanitized_text" | sed 's/[""''`]/'"'"'/g')  # Replace all quote types with single quotes
            sanitized_text=$(echo "$sanitized_text" | sed 's/[—–—]/—/g')  # Normalize em-dashes
            sanitized_text=$(echo "$sanitized_text" | sed 's/[✅❌🔍🎯🔧📝⚡🎉]//g')  # Remove common emojis
            sanitized_text=$(echo "$sanitized_text" | sed 's/\*\*\?//g')  # Remove markdown stars
            sanitized_text=$(echo "$sanitized_text" | sed 's/##\?//g')  # Remove markdown headers
            sanitized_text=$(echo "$sanitized_text" | tr '\n\r' ' ')  # Convert line breaks to spaces
            
            # Layer 2: Fix leading dash problem (critical fix)
            sanitized_text=$(echo "$sanitized_text" | sed 's/^[[:space:]]*-/The/')  # Replace leading dash with "The"
            sanitized_text=$(echo "$sanitized_text" | sed 's/\.\.\. -/. The/g')  # Replace "... -" with ". The"
            
            # Layer 3: Advanced shell-safe cleaning
            sanitized_text=$(echo "$sanitized_text" | sed 's/  \+/ /g')  # Collapse multiple spaces
            sanitized_text=$(echo "$sanitized_text" | sed 's/^ *//; s/ *$//')  # Trim whitespace
            sanitized_text=$(echo "$sanitized_text" | tr -d '\0-\31\127')  # Remove control characters
            
            # Layer 4: Final validation and fallback
            if [[ ${#sanitized_text} -lt 3 ]]; then
                sanitized_text="Claude response complete"
                echo "Sanitization resulted in too-short text, using fallback" >> /tmp/claude_tts_debug.log
            fi
            
            # === UPDATE CLIPBOARD WITH SANITIZED TEXT ===
            if [[ "${CLAUDE_TTS_TO_CLIPBOARD:-0}" == "1" ]]; then
                # Update clipboard with both original and sanitized versions
                updated_clipboard_content="=== Claude TTS Content Debug $(date) ===
Session: $session_id
Length: ${#final_sentence} chars (original) → ${#sanitized_text} chars (sanitized)
Estimated Duration: $(echo "${#sanitized_text} / $CHARS_PER_SECOND" | bc -l | awk '{printf "%.1f", $0}')s
Speech Rate: ${SPEECH_RATE} WPM

=== ORIGINAL TEXT ===
$final_sentence

=== SANITIZED TEXT (what actually gets spoken) ===
$sanitized_text

=== SANITIZATION CHANGES ===
Original length: ${#final_sentence} chars
Sanitized length: ${#sanitized_text} chars
Character difference: $((${#final_sentence} - ${#sanitized_text}))

=== END DEBUG INFO ===
"
                
                # Update clipboard and debug file with complete info
                if echo "$updated_clipboard_content" | pbcopy 2>/dev/null; then
                    echo "$(date): Updated clipboard with sanitized TTS content" >> /tmp/claude_tts_debug.log
                fi
                
                # Update the debug file with complete content
                debug_file="/tmp/claude_tts_content_$(date +%Y%m%d_%H%M%S).txt"
                echo "$updated_clipboard_content" > "$debug_file" 2>/dev/null && \
                    echo "$(date): Updated debug file with sanitized content: $debug_file" >> /tmp/claude_tts_debug.log
            fi
            
            # Layer 5: Safe file-based execution with robust error handling
            temp_speech_file=""
            cleanup_temp_file() {
                if [[ -n "$temp_speech_file" && -f "$temp_speech_file" ]]; then
                    rm -f "$temp_speech_file" 2>/dev/null
                    echo "$(date): Cleaned up temp file: $temp_speech_file" >> /tmp/claude_tts_debug.log
                fi
            }
            
            # Set cleanup trap for any exit scenario
            trap cleanup_temp_file EXIT INT TERM
            
            # Create temp file with proper randomization (no .txt suffix for mktemp)
            if temp_speech_file=$(mktemp /tmp/claude_speech_XXXXXX 2>/dev/null); then
                echo "$(date): Created temp file: $temp_speech_file" >> /tmp/claude_tts_debug.log
                
                # Write sanitized text to temp file with error checking
                if echo "$sanitized_text" > "$temp_speech_file" 2>/dev/null; then
                    echo "Original text length: ${#final_sentence}, Sanitized length: ${#sanitized_text}" >> /tmp/claude_tts_debug.log
                    echo "First 100 chars of sanitized text: ${sanitized_text:0:100}" >> /tmp/claude_tts_debug.log
                    echo "Using temp file for TTS: $temp_speech_file" >> /tmp/claude_tts_debug.log
                    
                    # Add a small delay to let notification sound finish
                    sleep 0.5
                    
                    # Execute TTS with file input (completely avoids shell escaping issues)
                    say_output=$(say -r "$SPEECH_RATE" -f "$temp_speech_file" 2>&1)
                    say_exit_code=$?
                else
                    echo "$(date): Failed to write to temp file, falling back to direct TTS" >> /tmp/claude_tts_debug.log
                    say_output=$(echo "$sanitized_text" | say -r "$SPEECH_RATE" -f - 2>&1)
                    say_exit_code=$?
                fi
            else
                echo "$(date): mktemp failed, using fallback approach" >> /tmp/claude_tts_debug.log
                # Fallback: use stdin pipe method
                say_output=$(echo "$sanitized_text" | say -r "$SPEECH_RATE" -f - 2>&1)
                say_exit_code=$?
            fi
            
            # Manual cleanup (trap will also ensure cleanup)
            cleanup_temp_file
            
            echo "TTS exit code: $say_exit_code" >> /tmp/claude_tts_debug.log
            if [[ $say_exit_code -ne 0 ]]; then
                echo "TTS error output: $say_output" >> /tmp/claude_tts_debug.log
                # Ultimate fallback
                echo "TTS failed, executing fallback notification" >> /tmp/claude_tts_debug.log
                say -r "$SPEECH_RATE" "Claude response ready" 2>/dev/null || true
            else
                echo "TTS executed successfully at ${SPEECH_RATE} WPM using file input" >> /tmp/claude_tts_debug.log
            fi
        else
            nohup say -r "$SPEECH_RATE" "Claude response complete" > /dev/null 2>&1 &
            echo "Fallback TTS executed - final sentence too short" >> /tmp/claude_tts_debug.log
        fi
    else
        # Fallback message
        nohup say -r "$SPEECH_RATE" "Claude response complete" > /dev/null 2>&1 &
        echo "Fallback TTS executed - no response found after delay" >> /tmp/claude_tts_debug.log
    fi
else
    # Fallback if no transcript available
    nohup say -r "$SPEECH_RATE" "Claude response complete" > /dev/null 2>&1 &
    echo "Fallback TTS executed - no transcript available" >> /tmp/claude_tts_debug.log
fi