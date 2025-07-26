# Automation Directory
**Purpose**: Automated workflows, hooks, and integration scripts

## Contents
- `tts/` - **Modular text-to-speech system** (Phase 1 foundation complete)
  - `config/` - JSON-based configuration system
    - `tts_config.json` - Core TTS settings and timing parameters
    - `speech_profiles.json` - Voice and speech profiles
    - `text_processing_rules.json` - Text sanitization and processing rules
    - `debug_config.json` - Debugging and logging configuration
  - `lib/` - Modular library components
    - `common/` - Foundation infrastructure (config, logging, error handling)
    - `input/` - Input processing modules (JSON parser, transcript monitor)
    - `processing/` - Text processing pipeline (sanitizer, aggregator)
    - `output/` - Output systems (speech synthesizer, debug exporter)
    - `testing/` - Test framework for unit and integration testing
  - `tests/` - Comprehensive test suite
    - `unit/` - Unit tests for individual modules
    - `integration/` - End-to-end integration tests
    - `fixtures/` - Test data and mock responses
  - `scripts/` - Utility and maintenance scripts
  - `bin/` - Executable entry points (future orchestrator location)
  - **Legacy files** (maintained for compatibility):
    - `claude_response_speaker.sh` - Original monolithic TTS engine
    - `tts_hook_entry.sh` - Hook entry point (updated for modular system)
    - `glass_sound_wrapper.sh` - Audio notification wrapper
- `hooks/` - Hook system utilities
  - `hook_debug_wrapper.sh` - Hook debugging and logging utilities
  - `followup-trigger.py` - Automated follow-up system
  - `emergency-controls.py` - Emergency safety controls
- `logs/` - System logs and debugging information  
  - `followup.log` - Follow-up system activity logs

## Claude Code Official Status
❌ **USER DIRECTORY** - Safe to customize and modify

This directory contains user automation scripts and is not part of Claude Code's core functionality.