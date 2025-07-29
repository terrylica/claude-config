# Automation Directory
**Purpose**: Automated workflows, hooks, and integration scripts

## Contents
- `cns/` - **CNS (Conversation Notification System)** (Formerly TTS, renamed 2025-07-28)
  - `config/` - Configuration system
    - `cns_config.json` - Clipboard and notification settings with volume control
    - `debug_config.json` - **[LEGACY]** Debug logging configuration (testing only)
    - `speech_profiles.json` - **[LEGACY]** Speech profile settings (testing only)
    - `text_processing_rules.json` - **[LEGACY]** Text processing rules (testing only)
  - **Active files**:
    - `conversation_handler.sh` - Main clipboard processing script
    - `cns_hook_entry.sh` - Hook entry point
    - `cns_notification_hook.sh` - Toy Story audio notification with configurable volume and folder name TTS
  - `lib/common/` - Common utility libraries
    - `config_loader.sh` - Configuration loading utilities
    - `error_handler.sh` - Error handling functions
    - `logger.sh` - Logging utilities
  - `tests/` - Test suites
    - `unit/test_config_loader.sh` - Unit tests for config loader
    - `integration/test_foundation_integration.sh` - Integration tests
  - `scripts/test_foundation.sh` - Test foundation script

## Claude Code Official Status
❌ **USER DIRECTORY** - Safe to customize and modify

This directory contains user automation scripts and is not part of Claude Code's core functionality.