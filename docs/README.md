# Claude Code Global Configuration

This directory contains the global configuration for Claude Code, organized into specialized subsystems for enhanced workflow integration.

## System Architecture

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **[APCF System](../CLAUDE.md#apcf-audit-proof-commit-format-for-sred-evidence-generation)** | Audit-proof commit formatting for SR&ED evidence | `CLAUDE.md` |
| **[TTS Integration](../automation/tts/claude_response_speaker.sh)** | Text-to-speech for Claude responses | `automation/tts/claude_response_speaker.sh`, `automation/tts/tts_hook_entry.sh` |
| **[Command Hub](../commands/)** | Slash command system for workflow automation | `commands/hub/` directory |
| **[Automation Hooks](../hooks/)** | Event-driven automation and integrations | `hooks/` directory, `automation/hooks/hook_debug_wrapper.sh` |
| **[Development Tools](../tools/)** | Standalone utilities and development aids | `tools/gfm-link-checker/` |
| **[System Runtime](../system/)** | Session management and todo tracking | `system/sessions/`, `system/todos/` |
| **[Development Context](../settings.json)** | Core configuration and system preferences | `settings.json` |
| **[Agent Configurations](../agents/)** | Custom agent definitions and behaviors | `agents/` directory |
| **[Tmux Integration](../tmux/)** | Terminal multiplexer and workspace management | `tmux/` directory |
| **[Historical Data](../history/)** | Archived sessions and development history | `history/` directory |

## Core Configuration Files

- **`settings.json`**: Main Claude Code configuration with model settings and hook definitions
- **`CLAUDE.md`**: User memory system with APCF methodology and workflow preferences  
- **`.gitignore`**: Version control exclusions for temporary and system files
- **`CLAUDE_CODE_OFFICIAL_FILES.md`**: Safety documentation for critical system files

⚠️ **Claude Code Official Files (DO NOT MOVE):**
- `CLAUDE.md` - User memory file
- `settings.json` - Configuration
- `system/` directory - Session and runtime data

⚠️ **Integration Files (Modify with caution):**
- `hooks/` directory - Event system integration

## Audio Integration

The TTS system uses:
- **System sounds**: Audio notifications from macOS system library
- **Hook Integration**: Automated audio feedback on Claude Code events via `automation/tts/`
- **Debug Logging**: Comprehensive TTS operation tracking for troubleshooting

## Usage

This configuration enables:
1. **APCF Workflow**: Type "APCF" to generate audit-proof commit messages with SR&ED evidence
2. **Audio Feedback**: Automatic text-to-speech for Claude responses via hook system
3. **Slash Commands**: Custom workflow automation through `/command` syntax
4. **Memory Persistence**: Cross-session project context and preference retention
5. **Development Integration**: Seamless workflow with git, debugging, and productivity tools

For detailed APCF usage and commit formatting guidelines, see the [APCF section in CLAUDE.md](../CLAUDE.md#apcf-audit-proof-commit-format-for-sred-evidence-generation).