#!/bin/bash
# CNS notification hook - plays audio and speaks folder name
{
    afplay /Users/terryli/.claude/media/toy-story-notification.mp3 > /dev/null 2>&1
    sleep 0.01
    folder_name="$(basename "$(pwd)")"
    if [[ "$folder_name" == .* ]]; then
        say "dot ${folder_name#.}"
    else
        say "$folder_name"
    fi
} &
# Exit immediately, don't wait for sound to finish