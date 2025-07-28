#!/bin/bash
# Async sound hook - spawn and exit immediately
{
    afplay /Users/terryli/Documents/sounds/toy-story-short-happy-audio-logo-short-cartoony-intro-outro-music-125627-clipped.mp3 > /dev/null 2>&1
    sleep 0.01
    folder_name="$(basename "$(pwd)")"
    if [[ "$folder_name" == .* ]]; then
        say "dot ${folder_name#.}"
    else
        say "$folder_name"
    fi
} &
# Exit immediately, don't wait for sound to finish