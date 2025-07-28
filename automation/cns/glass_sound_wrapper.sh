#!/bin/bash
# Async sound hook - spawn and exit immediately
afplay /Users/terryli/Documents/sounds/mac-iix-16-bit-45958.mp3 > /dev/null 2>&1 &
# Exit immediately, don't wait for sound to finish