#!/bin/bash
echo "$(date): Mac IIx sound hook triggered" >> /tmp/claude_tts_debug.log
afplay /Users/terryli/Documents/sounds/mac-iix-16-bit-45958.mp3
sound_exit_code=$?
echo "$(date): Mac IIx sound exit code: $sound_exit_code" >> /tmp/claude_tts_debug.log