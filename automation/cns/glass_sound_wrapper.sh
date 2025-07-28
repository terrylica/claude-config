#!/bin/bash
# Async sound hook - spawn and exit immediately
afplay /Users/terryli/Documents/sounds/toy-story-short-happy-audio-logo-short-cartoony-intro-outro-music-125627.mp3 > /dev/null 2>&1 &
# Exit immediately, don't wait for sound to finish