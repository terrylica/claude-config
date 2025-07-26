#!/bin/bash
echo "$(date): Glass sound hook triggered" >> /tmp/claude_tts_debug.log
afplay /System/Library/Sounds/Glass.aiff
glass_exit_code=$?
echo "$(date): Glass sound exit code: $glass_exit_code" >> /tmp/claude_tts_debug.log