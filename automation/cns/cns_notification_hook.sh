#!/bin/bash
# CNS notification hook - plays audio and speaks folder name
# Run audio in current session, then background the rest
(
    # Read volume setting from config (default 0.3 if not found)
    CNS_CONFIG="$HOME/.claude/automation/cns/config/cns_config.json"
    VOLUME=$(jq -r '.audio.notification_volume // 0.3' "$CNS_CONFIG" 2>/dev/null || echo "0.3")
    
    # Play notification at configured volume (platform-aware with user session access)
    AUDIO_FILE="$HOME/.claude/media/toy-story-notification.mp3"
    if [[ -f "$AUDIO_FILE" ]]; then
        if command -v afplay >/dev/null 2>&1; then
            # macOS - Play audio FIRST, wait for completion before voice announcement
            afplay "$AUDIO_FILE" --volume "$VOLUME" &>/dev/null
        elif command -v paplay >/dev/null 2>&1; then
            # Linux with PulseAudio
            paplay "$AUDIO_FILE" > /dev/null 2>&1
        elif command -v aplay >/dev/null 2>&1; then
            # Linux with ALSA
            aplay "$AUDIO_FILE" > /dev/null 2>&1
        fi
    fi
    sleep 0.01
    
    # Read hook data to get the actual working directory
    hook_data=$(cat 2>/dev/null || echo "{}")
    cwd=$(echo "$hook_data" | jq -r '.cwd // ""' 2>/dev/null || echo "")
    current_dir="${cwd:-$(pwd)}"
    
    folder_name="$(basename "$current_dir")"
    
    # Text-to-speech announcement (platform-aware)
    announce_text=""
    if [[ -n "$TMUX" ]]; then
        # In tmux: announce both tmux and the actual folder
        if [[ "$folder_name" == .* ]]; then
            announce_text="tmux dot ${folder_name#.}"
        else
            announce_text="tmux $folder_name"
        fi
    else
        # Not in tmux: just announce the folder
        if [[ "$folder_name" == .* ]]; then
            announce_text="dot ${folder_name#.}"
        else
            announce_text="$folder_name"
        fi
    fi
    
    # Platform-specific text-to-speech with user session access
    if [[ -n "$announce_text" ]]; then
        if command -v say >/dev/null 2>&1; then
            # macOS - Voice announcement AFTER jingle completes
            say "$announce_text" &>/dev/null
        elif command -v espeak >/dev/null 2>&1; then
            # Linux with espeak
            espeak "$announce_text" > /dev/null 2>&1
        elif command -v festival >/dev/null 2>&1; then
            # Linux with festival
            echo "$announce_text" | festival --tts > /dev/null 2>&1
        fi
    fi
) > /dev/null 2>&1 &

# Exit immediately after spawning audio process
exit 0