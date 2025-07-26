# Text-to-Speech Hook System

Intelligent audio feedback for Claude Code responses with modular architecture.

## Architecture

- **Configuration**: `config/` - JSON-based settings and profiles
- **Foundation**: `lib/common/` - Config loading, logging, error handling
- **Entry Point**: `tts_hook_entry.sh` - Main hook script
- **Legacy**: `claude_response_speaker.sh` - Monolithic compatibility script

## Files

- `tts_hook_entry.sh` - Primary entry point for modular system
- `claude_response_speaker.sh` - Legacy monolithic script
- `config/` - JSON configuration files
- `lib/` - Modular library components
- `scripts/` - Development and testing scripts
- `tests/` - Unit and integration tests

## Debug Logging

Debug logs are written to `/tmp/claude_tts_debug.log` with structured logging.