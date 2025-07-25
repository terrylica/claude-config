# Claude Code Configuration Architecture

## Overview
This document describes the refactored architecture of Terry Li's Claude Code configuration, optimized for SR&ED development workflows while maintaining full compatibility with Claude Code constraints.

## Directory Structure

```
~/.claude/
├── settings.json              # [FIXED] Main Claude Code configuration
├── CLAUDE.md                  # [FIXED] User memory & APCF methodology
├── agents/                    # [FIXED] Sub-agent configurations
├── commands/                  # [FIXED] Slash commands
│   └── hub/                   # Command hub system commands
├── automation/                # [NEW] Automation subsystem
│   ├── hooks/                 # Hook system files
│   ├── scripts/               # Shell scripts (TTS, wrappers)
│   └── logs/                  # Hook logs and debug files
├── audio/                     # [NEW] TTS/Audio subsystem
│   ├── sounds/                # Audio files
│   └── configs/               # Audio-related configurations
├── history/                   # [NEW] Historical data
│   ├── shell-snapshots/       # Shell command history
│   ├── sessions/              # Archived project sessions
│   └── todos-archive/         # Completed todos
├── system/                    # [NEW] System-managed files
│   ├── ide/                   # IDE integration locks
│   ├── sessions/              # Current project sessions
│   ├── statsig/               # Telemetry cache
│   └── todos/                 # Active todo tracking
└── docs/                      # [NEW] Documentation
    ├── README.md              # Main documentation
    └── ARCHITECTURE.md        # This file
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
**Purpose**: Hook system, TTS integration, automation scripts
**Components**:
- `hooks/`: Python hook scripts (followup-trigger, emergency-controls)
- `scripts/`: Shell scripts (TTS entry, debug wrappers, audio)
- `logs/`: Debug logs, hook execution logs

**Integration**: Referenced by `settings.json` hooks configuration

### 🔊 Audio Subsystem  
**Location**: `audio/`
**Purpose**: TTS and audio feedback system
**Components**:
- `sounds/`: Audio files for notifications
- `configs/`: Audio-specific configuration files

**Integration**: Used by automation scripts for audio feedback

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
├── glass_sound_wrapper.sh (notification)
├── tts_hook_entry.sh (text-to-speech)
└── followup-trigger.py (automation)
```

### TTS Processing Chain
```
Hook Event → tts_hook_entry.sh → claude_response_speaker.sh → 
├── Extract transcript content
├── Process user prompt + response
├── Generate optimized TTS content
└── Execute macOS `say` command
```

### File Path References
All configuration files use absolute paths to maintain reliability:
- Settings: `/Users/terryli/.claude/automation/scripts/`
- Scripts: Reference other scripts via absolute paths
- Logs: Use centralized `/tmp/claude_tts_debug.log`

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
1. **Script Updates**: Modify files in `automation/`
2. **Configuration Changes**: Update `settings.json`, `CLAUDE.md`
3. **Path Updates**: Maintain absolute paths in all references
4. **Testing**: Validate functionality after changes

## SR&ED Integration

### APCF Workflow Support
- **Evidence Generation**: APCF methodology in `CLAUDE.md`
- **Audit Trail**: Git repository with commit history
- **Development Context**: Session transcripts in `system/sessions/`
- **Research Documentation**: Structured in `docs/`

### Development Tools
- **Command Hub**: `/hub:*` commands for workflow automation
- **Sub-agents**: Specialized agents for compliance, testing
- **Hook Automation**: Automatic logging and session management

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

**Last Updated**: July 25, 2025  
**Architecture Version**: 1.0  
**Compatible with**: Claude Code official constraints as of July 2025