# Automation Directory
**Purpose**: Automated workflows, hooks, and integration scripts

## Contents
- `tts/` - **Clipboard & Glass Sound System** (TTS functionality removed 2025-07-28)
  - `config/` - Simplified configuration system
    - `tts_config.json` - Clipboard and glass sound settings (simplified)
  - **Active files**:
    - `claude_response_speaker.sh` - Main clipboard + glass sound script (168 lines)
    - `tts_hook_entry.sh` - Hook entry point
    - `glass_sound_wrapper.sh` - Audio completion notification
  - **Removed/Deprecated**:
    - `lib/` - Modular library components (no longer needed)
    - `tests/` - TTS-specific test suites (obsolete)
    - `scripts/` - TTS utility scripts (obsolete)
    - `bin/` - Speech synthesis executables (removed)
- `hooks/` - Hook system utilities
  - `hook_debug_wrapper.sh` - Hook debugging and logging utilities
  - `followup-trigger.py` - Automated follow-up system
  - `export_hook.sh` - Automated conversation export system
  - `emergency-controls.py` - Emergency safety controls
- `logs/` - System logs and debugging information  
  - `followup.log` - Follow-up system activity logs

## Claude Code Official Status
❌ **USER DIRECTORY** - Safe to customize and modify

This directory contains user automation scripts and is not part of Claude Code's core functionality.