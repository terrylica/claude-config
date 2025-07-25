# Claude Code Global Configuration

This directory contains the global configuration for Claude Code, organized into specialized subsystems for enhanced workflow integration.

## System Architecture

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **[APCF System](CLAUDE.md#apcf-audit-proof-commit-format-for-sred-evidence-generation)** | Audit-proof commit formatting for SR&ED evidence | `CLAUDE.md` |
| **[TTS Integration](claude_response_speaker.sh)** | Text-to-speech for Claude responses | `claude_response_speaker.sh`, `tts_hook_entry.sh` |
| **[Command Hub](commands/)** | Slash command system for workflow automation | `commands/` directory |
| **[Automation Hooks](hooks/)** | Event-driven automation and integrations | `hooks/` directory, `hook_debug_wrapper.sh` |
| **[Project Memory](projects/)** | Cross-session context and state persistence | `projects/` directory |
| **[Development Context](settings.json)** | Core configuration and system preferences | `settings.json` |

## Core Configuration Files

- **`settings.json`**: Main Claude Code configuration with model settings and hook definitions
- **`CLAUDE.md`**: User memory system with APCF methodology and workflow preferences  
- **Glass.aiff**: System notification sound (from macOS system sounds)
- **`.gitignore`**: Version control exclusions for temporary and system files

## Audio Integration

The TTS system uses:
- **Glass.aiff**: System notification sound (from macOS)
- **Hook Integration**: Automated audio feedback on Claude Code events
- **Debug Logging**: Comprehensive TTS operation tracking for troubleshooting

## Usage

This configuration enables:
1. **APCF Workflow**: Type "APCF" to generate audit-proof commit messages with SR&ED evidence
2. **Audio Feedback**: Automatic text-to-speech for Claude responses via hook system
3. **Slash Commands**: Custom workflow automation through `/command` syntax
4. **Memory Persistence**: Cross-session project context and preference retention
5. **Development Integration**: Seamless workflow with git, debugging, and productivity tools

For detailed APCF usage and commit formatting guidelines, see the [APCF section in CLAUDE.md](CLAUDE.md#apcf-audit-proof-commit-format-for-sred-evidence-generation).