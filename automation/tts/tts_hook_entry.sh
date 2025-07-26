#!/bin/bash
echo "$(date): TTS hook entry started" >> /tmp/claude_tts_debug.log

# Auto-enable clipboard debugging for TTS examination
# This ensures the feature is always available for debugging
export CLAUDE_TTS_TO_CLIPBOARD=1

# Pass the JSON input to the Claude response speaker script in background
# First capture the input, then process it in background
input_data=$(cat)
echo "$input_data" | /Users/terryli/.claude/automation/tts/claude_response_speaker.sh > /dev/null 2>&1 &