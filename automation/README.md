# Automation Directory
**Purpose**: Automated workflows, hooks, and integration scripts

## Contents
- `cns/` - **CNS (Conversation Notification System)** (Formerly TTS, renamed 2025-07-28)
  - `config/` - Configuration system
    - `cns_config.json` - Clipboard and glass sound settings
    - `debug_config.json` - Debug logging configuration
    - `speech_profiles.json` - Speech profile settings
    - `text_processing_rules.json` - Text processing rules
  - **Active files**:
    - `conversation_handler.sh` - Main clipboard + glass sound script
    - `cns_hook_entry.sh` - Hook entry point
    - `glass_sound_wrapper.sh` - Audio completion notification
  - `lib/common/` - Common utility libraries
    - `config_loader.sh` - Configuration loading utilities
    - `error_handler.sh` - Error handling functions
    - `logger.sh` - Logging utilities
  - `tests/` - Test suites
    - `unit/test_config_loader.sh` - Unit tests for config loader
    - `integration/test_foundation_integration.sh` - Integration tests
  - `scripts/test_foundation.sh` - Test foundation script
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