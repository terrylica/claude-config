# Claude Code Global Configuration

This directory contains the global configuration for Claude Code, organized into specialized subsystems for workflow integration.

## System Requirements

**Supported Platforms**: Unix-like systems only (macOS, Linux)  
**Shell Requirements**: POSIX-compliant shells (zsh, bash)  
**Dependencies**: 
- Common: `jq`, `curl`
- Audio (macOS): `afplay` OR Audio (Linux): `paplay`/`aplay`
- Clipboard (macOS): `pbcopy` OR Clipboard (Linux): `xclip`/`xsel`
- Text-to-Speech (macOS): `say` OR TTS (Linux): `espeak`/`festival`

> **Note**: This workspace is **not designed for Windows compatibility**. All paths and scripts assume Unix conventions (`$HOME`, `/tmp/`, etc.)

## System Architecture

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **[APCF System](../CLAUDE.md#apcf-audit-proof-commit-format-for-sred-evidence-generation)** | Audit-proof commit formatting for SR&ED evidence | `CLAUDE.md` |
| **[CNS (Conversation Notification System)](../automation/cns/)** | Conversation tracking and audio notification system | `automation/cns/conversation_handler.sh`, `automation/cns/config/` |
| **[Command Hub](../commands/)** | Slash command system for workflow automation | `commands/` directory |
| **[Automation System](../automation/)** | Event-driven automation and CNS integration | `automation/cns/`, `automation/logs/` |
| **[Development Tools](../tools/)** | Standalone utilities and development aids | `tools/gfm-link-checker/` |
| **[Migration Documentation](REPOSITORY_MIGRATION.md)** | Repository migration guide and verification | `docs/REPOSITORY_MIGRATION.md` |
| **[System Runtime](../system/)** | Session management and todo tracking | `system/sessions/`, `system/todos/`, `system/ide/`, `system/statsig/` |
| **[Development Context](../settings.json)** | Core configuration and system preferences | `settings.json` |
| **[Agent Configurations](../agents/)** | Custom agent definitions and behaviors | `agents/` directory |
| **[Tmux Integration](../tmux/)** | Simple session management with smart naming | `tmux/` directory |
| **[Historical Data](../history/)** | Archived sessions and development history | `history/` directory |
| **[Shell Snapshots](../shell-snapshots/)** | Terminal session state captures | `shell-snapshots/` directory |

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
- `automation/cns/` directory - CNS hook system integration

## Audio & Clipboard Integration

The CNS (Conversation Notification System) provides:
- **Clipboard Tracking**: Automatic copying of conversation exchanges (USER: + CLAUDE: format)
- **Cross-Platform Audio**: Configurable volume notification with platform detection (`afplay`/`paplay`/`aplay`)
- **Cross-Platform Clipboard**: Platform detection for clipboard operations (`pbcopy`/`xclip`/`xsel`)
- **Cross-Platform TTS**: Folder name text-to-speech with platform alternatives (`say`/`espeak`/`festival`)
- **Command Detection**: Smart handling of hash (`#`) and slash (`/`) commands for clipboard optimization
- **Debug Logging**: Comprehensive operation tracking at `/tmp/claude_cns_debug.log`
- **Volume Control**: JSON-configurable notification volume (0.0-1.0 range)

## Usage

This configuration enables:
1. **APCF Workflow**: Type "APCF" to generate audit-proof commit messages with SR&ED evidence
2. **Cross-Platform Portability**: Supports both macOS and Linux with automatic platform detection
3. **Clipboard Tracking**: Automatic conversation capture for easy sharing and reference
4. **Configurable Audio**: Volume-controlled notification system with platform-specific audio players
5. **Slash Commands**: Custom workflow automation through `/command` syntax including `/apcf`
6. **Memory Persistence**: Cross-session project context and preference retention
7. **Development Integration**: Seamless workflow with git, debugging, and productivity tools
8. **Organizational Repository**: Hosted at https://github.com/Eon-Labs/claude-config

For detailed APCF usage and commit formatting guidelines, see the [APCF section in CLAUDE.md](../CLAUDE.md#apcf-audit-proof-commit-format-for-sred-evidence-generation).