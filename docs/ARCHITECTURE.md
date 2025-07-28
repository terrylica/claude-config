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
│   ├── cns/                   # CNS (Conversation Notification System) (Renamed from tts 2025-07-28)
│   │   ├── config/            # Simplified JSON configuration
│   │   └── *.sh               # Clipboard + glass sound scripts (168 lines)
│   └── logs/                  # Hook logs and debug files
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
**Purpose**: Hook system, modular TTS integration, automation scripts
**Components**:
- `hooks/`: Python hook scripts (followup-trigger, emergency-controls)
- `cns/`: **CNS (Conversation Notification System)** (Renamed from TTS 2025-07-28)
  - `config/`: Simplified JSON configuration (clipboard and sound settings)
  - `conversation_handler.sh`: Main clipboard + glass sound script (168 lines)
  - `cns_hook_entry.sh`: Hook system integration
  - `glass_sound_wrapper.sh`: Audio completion notification
- `logs/`: Debug logs, hook execution logs

**Integration**: Referenced by `settings.json` hooks configuration

### 🔊 Audio Notifications
**Location**: `automation/cns/`
**Purpose**: Glass sound completion notification
**Components**:
- `glass_sound_wrapper.sh`: System sound notification when Claude finishes

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
├── glass_sound_wrapper.sh (audio notification)
├── cns_hook_entry.sh (clipboard tracking)
└── followup-trigger.py (automation)
```

### CNS Processing Chain
**Current (Simplified)**:
```
Hook Event → cns_hook_entry.sh → conversation_handler.sh → 
├── Extract transcript content (JSON parsing)
├── Process user prompt + response (content extraction)
├── Command detection (hash/slash patterns)
├── Combined clipboard copy (USER: + CLAUDE: format)
└── Glass sound notification (separate hook)
```

**Removed (Former TTS)**:
```
❌ All speech synthesis functionality
❌ Complex paragraph aggregation for audio  
❌ macOS `say` command execution
❌ Speech rate/voice/volume processing
❌ Modular library architecture (lib/)
```

### File Path References
All configuration files use absolute paths to maintain reliability:
- **Settings**: `/Users/terryli/.claude/automation/cns/` (current hook references)
- **Configuration**: `/Users/terryli/.claude/automation/cns/config/` (JSON config files)
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
3. **Command Detection**: Modify hash/slash pattern recognition in main script
4. **Path Updates**: Maintain absolute paths for hook system integration
5. **Testing**: Verify clipboard functionality and glass sound notification

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

**Last Updated**: July 28, 2025  
**Architecture Version**: 2.1 - CNS (Conversation Notification System) Complete Rename  
**Compatible with**: Claude Code official constraints as of July 2025