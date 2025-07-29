# Claude Code Configuration Architecture

## Overview
This document describes the refactored architecture of the Claude Code workspace configuration, optimized for development workflows while maintaining full compatibility with Claude Code constraints and Unix system portability.

## Directory Structure

```
~/.claude/
├── settings.json              # [FIXED] Main Claude Code configuration
├── CLAUDE.md                  # [FIXED] User memory & APCF methodology
├── agents/                    # [FIXED] Sub-agent configurations
├── commands/                  # [FIXED] Slash commands (/ruff-fix, /apcf, /gfm-check)
├── bin/                       # [NEW] Utility scripts
│   └── cns-notify             # Manual CNS notification trigger
├── automation/                # [NEW] Automation subsystem  
│   ├── hooks/                 # Hook system files (Python scripts)
│   ├── cns/                   # CNS (Conversation Notification System)
│   │   ├── config/            # JSON configuration (clipboard + sound)
│   │   ├── lib/               # Simplified common utilities
│   │   ├── scripts/           # Test and validation scripts
│   │   ├── tests/             # Unit and integration tests
│   │   └── *.sh               # Core CNS scripts (async hook architecture)
│   └── logs/                  # Hook execution logs
├── history/                   # [NEW] Historical data
│   └── shell-snapshots/       # Shell command history snapshots
├── shell-snapshots/           # [FIXED] Current shell snapshots (Claude Code required)
├── system/                    # [NEW] System-managed files
│   ├── ide/                   # IDE integration locks (gitignored)
│   ├── sessions/              # Current project sessions
│   ├── statsig/               # Telemetry cache
│   └── todos/                 # Active todo tracking (JSON files)
├── tmux/                      # [NEW] Tmux integration system
│   ├── bin/                   # Tmux management scripts
│   ├── config/                # Shell integration and aliases
│   ├── docs/                  # Tmux setup documentation
│   └── data/                  # Tmux session data
├── tools/                     # [NEW] Development tools
│   └── gfm-link-checker/      # GitHub Flavored Markdown link validator
└── docs/                      # [NEW] Documentation
    ├── README.md              # Main workspace documentation
    └── ARCHITECTURE.md        # This architecture document
```

## Subsystem Architecture

### 🔒 Core Configuration (Constrained)
**Location**: Root level (`~/.claude/`)
**Purpose**: Claude Code required files
**Files**: 
- `settings.json`: Hook configurations, model settings
- `CLAUDE.md`: User memory, APCF methodology
- `agents/`: Sub-agent definitions
- `commands/`: Slash command definitions

**Constraints**: Cannot be moved or renamed per Claude Code documentation

### 🤖 Automation Subsystem
**Location**: `automation/`
**Purpose**: Hook system, CNS integration, automation scripts
**Components**:
- `cns/`: **CNS (Conversation Notification System)** (Clipboard + Toy Story notification + TTS)
  - `config/`: JSON configuration (cns_config.json - clipboard and sound settings)
  - `lib/common/`: Simplified config loader (59 lines, CNS-only variables)
  - `scripts/`: Test and validation utilities
  - `tests/`: Unit and integration test suites  
  - `conversation_handler.sh`: Main clipboard processing script (168 lines)
  - `cns_hook_entry.sh`: Async hook entry point (fire-and-forget pattern)
  - `cns_notification_hook.sh`: Toy Story audio notification with configurable volume and folder name TTS (async)
- `logs/`: Hook execution logs and debug files

**Integration**: Referenced by `settings.json` hooks configuration with async architecture

### 🔧 Utility Scripts
**Location**: `bin/`
**Purpose**: Manual utility scripts and tools
**Components**:
- `cns-notify`: Manual CNS notification trigger for testing functionality

**Usage**: Independent testing and manual operation of CNS features

### 🖥️ Tmux Integration
**Location**: `tmux/`
**Purpose**: Simple tmux session management with smart naming
**Components**:
- `bin/`: Core session management scripts (`tmux-session`, `tmux-list`, `tmux-kill`)
- `config/`: Clean tmux configuration and shell integration
- `SIMPLE-USAGE.md`: Complete documentation

**Philosophy**: Clean, transparent tmux wrapper without plugins or persistence. Pure tmux commands with intelligent folder-based session naming.

### 🔗 Development Tools
**Location**: `tools/`
**Purpose**: Standalone development utilities
**Components**:
- `gfm-link-checker/`: GitHub Flavored Markdown link validation tool with workspace integration

**Features**: Local README.md validation with GitHub-specific behavior awareness

### 🔊 Audio Notifications
**Location**: `$HOME/.claude/automation/cns/`
**Purpose**: Toy Story notification with folder name TTS
**Components**:
- `cns_notification_hook.sh`: Toy Story sound + folder name TTS when Claude finishes

**Integration**: Separate hook system for audio feedback (no TTS)

### 📚 History Management
**Location**: `history/`
**Purpose**: Long-term data retention and archival
**Components**:
- `shell-snapshots/`: Shell command history files
- `sessions/`: Archived project session transcripts
- `todos-archive/`: Completed todo items (>30 days)

**Maintenance**: Automated cleanup of old system files

### ⚙️ System Management
**Location**: `system/` (symlinked to root)
**Purpose**: System-managed files requiring specific locations
**Components**:
- `ide/`: IDE integration lock files
- `sessions/`: Active project session data  
- `statsig/`: Telemetry and analytics cache
- `todos/`: Active todo tracking files

**Symlinks**: Maintains compatibility through symlinks:
- `~/.claude/ide` → `system/ide`
- `~/.claude/projects` → `system/sessions`
- `~/.claude/statsig` → `system/statsig`
- `~/.claude/todos` → `system/todos`

### 📖 Documentation
**Location**: `docs/`
**Purpose**: Architecture documentation and usage guides
**Files**:
- `README.md`: Main configuration documentation
- `ARCHITECTURE.md`: This architecture document

## Integration Patterns

### Hook System Flow
```
Claude Code Event → settings.json hooks →
├── cns_notification_hook.sh (Toy Story notification + TTS)
├── cns_hook_entry.sh (clipboard tracking)
```

### CNS Processing Chain
**Current (Async Architecture)**:
```
Claude Code Stop Hook → settings.json →
├── cns_hook_entry.sh (captures stdin, spawns background)
│   └── conversation_handler.sh (async processing)
│       ├── JSON parsing & content extraction
│       ├── Command detection (hash/slash patterns)  
│       ├── Clipboard copy (USER: + CLAUDE: format)
│       └── Debug logging (/tmp/claude_cns_debug.log)
└── cns_notification_hook.sh (async Toy Story sound + TTS)
    └── afplay background process
```

**Key Architectural Principles**:
```
✅ Fire-and-forget async pattern - hooks exit immediately
✅ Background processing - no session delays
✅ Simplified 59-line config loader (CNS-only variables)
✅ Clipboard + Toy Story notification + folder name TTS functionality
✅ No timeout constraints in settings.json
```

**Removed (Former TTS System)**:
```
❌ All speech synthesis functionality
❌ Complex paragraph aggregation for audio  
❌ macOS `say` command execution
❌ Speech rate/voice/volume processing
❌ 196-line TTS-contaminated config loader
❌ Synchronous hook execution patterns
```

### File Path References
All configuration files use $HOME-based paths for portability:
- **Settings**: `$HOME/.claude/automation/cns/` (current hook references)
- **Configuration**: `$HOME/.claude/automation/cns/config/` (JSON config files)
- **Scripts**: Reference other components via absolute paths and module loading
- **Logs**: Use centralized `/tmp/claude_cns_debug.log` with structured logging

## Maintenance Guidelines

### Regular Cleanup
```bash
# Clean old IDE locks (daily)
find system/ide/ -name "*.lock" -mtime +1 -delete

# Clean old statsig cache (weekly)  
find system/statsig/ -name "*.cached.*" -mtime +7 -delete

# Archive old sessions (quarterly)
find system/sessions/ -name "*.jsonl" -mtime +90 -exec mv {} history/sessions/ \;
```

### Backup Strategy
```bash
# Full configuration backup
tar -czf claude-config-$(date +%Y%m%d).tar.gz \
  ~/.claude/{settings.json,CLAUDE.md,agents,commands,automation,audio,docs}

# Exclude system-managed and temporary files
# Include: user configurations, custom scripts, documentation
```

### Update Procedures
1. **CNS System Updates**: Modify `automation/cns/conversation_handler.sh` (168 lines)
2. **Configuration Changes**: Update `automation/cns/config/cns_config.json` 
3. **Hook Architecture**: Maintain async fire-and-forget pattern in all hooks
4. **Command System**: Add new slash commands to `commands/` directory
5. **Utility Scripts**: Add tools to `bin/` for manual operations
6. **Development Tools**: Extend `tools/` for new workspace utilities
7. **Testing**: Use `bin/cns-notify` for manual CNS functionality verification

## SR&ED Integration

### APCF Workflow Support
- **Evidence Generation**: APCF methodology in `CLAUDE.md`
- **Audit Trail**: Git repository with commit history
- **Development Context**: Session transcripts in `system/sessions/`
- **Research Documentation**: Structured in `docs/`

### Development Tools
- **Slash Commands**: `/ruff-fix`, `/apcf`, `/gfm-check` for workflow automation
- **Sub-agents**: Specialized agents for compliance, testing, research
- **Hook Automation**: Async logging and session management (no delays)
- **Manual Utilities**: `bin/cns-notify` for independent testing
- **Link Validation**: `tools/gfm-link-checker/` for documentation integrity

## Security Considerations

### File Permissions
- Scripts: `755` (executable by owner)
- Configs: `644` (readable by owner/group)
- Logs: Restricted to `/tmp/` with automatic rotation

### Data Isolation
- System files: Isolated in `system/` with symlinks
- User data: Separated in dedicated subsystems
- Temporary data: Automatic cleanup and rotation

## Future Extensibility

### Plugin Architecture
- New subsystems can be added parallel to existing ones
- Hook system supports additional automation scripts
- Command system supports new workflow commands

### Version Control
- Git repository tracks all user-customizable files
- System-managed files excluded via `.gitignore`
- Architecture documentation versioned with changes

---

**Last Updated**: July 28, 2025  
**Architecture Version**: 2.2 - CNS Purification & Async Architecture Complete  
**Compatible with**: Claude Code official constraints as of July 2025