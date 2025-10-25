# Claude Code Configuration Architecture

## Overview

This document describes the refactored architecture of the Claude Code workspace configuration, designed for development workflows while maintaining full compatibility with Claude Code constraints and Unix system portability.

## Directory Structure

```
~/.claude/
├── settings.json              # [FIXED] Main Claude Code configuration
├── CLAUDE.md                  # [FIXED] User memory & APCF methodology
├── agents/                    # [FIXED] Agent configurations
├── bin/                       # [NEW] Utility scripts
│   └── cns-notify             # Manual CNS notification trigger
├── automation/                # [NEW] Automation subsystem
│   ├── cns/                   # CNS (Conversation Notification System)
│   │   ├── config/            # JSON configuration (clipboard + sound)
│   │   ├── lib/               # Simplified common utilities
│   │   ├── scripts/           # Test and validation scripts
│   │   ├── tests/             # Unit and integration tests
│   │   └── *.sh               # Core CNS scripts (async hook architecture)
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
- `agents/`: Agent definitions
- `commands/`: Slash command definitions

**Constraints**: Cannot be moved or renamed per Claude Code documentation

### 🤖 Automation Subsystem

**Location**: `automation/`
**Purpose**: Hook system, CNS integration, automation scripts
**Components**:

- `cns/`: **CNS (Conversation Notification System)** (Clipboard + Toy Story notification + TTS)
  - `config/`: JSON configuration (cns_config.json - clipboard and sound settings)
  - `lib/common/`: Simplified config loader (58 lines, CNS-only variables)
  - `scripts/`: Test and validation utilities
  - `tests/`: Unit and integration test suites
  - `conversation_handler.sh`: Main clipboard processing script (188 lines)
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
**Purpose**: Cross-platform audio notification with configurable volume
**Components**:

- `cns_notification_hook.sh`: Platform-aware audio playback + folder name TTS when Claude finishes
- Platform detection for `afplay` (macOS) / `paplay`/`aplay` (Linux)
- Volume control via JSON configuration (0.0-1.0 range)
- Text-to-speech: `say` (macOS) / `espeak`/`festival` (Linux)

**Integration**: Async hook system for cross-platform audio feedback

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
- `~/.claude/statsig` → `system/statsig`
- `~/.claude/todos` → `system/todos`

Session storage is canonical at `~/.claude/projects/`.

### 📖 Documentation

**Location**: `docs/`
**Purpose**: Architecture documentation and usage guides
**Files**:

- `README.md`: Main configuration documentation
- `ARCHITECTURE.md`: This architecture document
- `architecture/workflow-orchestration-comparison.md`: Event-driven workflow orchestration research and recommendations

## Integration Patterns

### Modern Hook System Flow (CNS Architecture)

```
Claude Code Event → settings.json hooks →
└── cns_hook_entry.sh (async entry point) →
    └── conversation_handler.sh (clipboard processing) →
        └── cns_notification_hook.sh (cross-platform audio + TTS)
```

### Platform Compatibility

**Supported Systems**: Unix-like systems (macOS, Linux)
**Dependencies**: Automatic platform detection for:

- Audio: `afplay` / `paplay` / `aplay`
- Clipboard: `pbcopy` / `xclip` / `xsel`
- Text-to-Speech: `say` / `espeak` / `festival`

**Repository**: https://github.com/terrylica/claude-config

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
✅ Simplified 58-line config loader (CNS-only variables)
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
find ~/.claude/projects/ -name "*.jsonl" -mtime +90 -exec mv {} history/sessions/ \;
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
- **Development Context**: Session transcripts in `~/.claude/projects/`
- **Research Documentation**: Structured in `docs/`

### Development Tools

- **Agents**: Specialized agents for compliance, testing, research
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

## Workspace Reorganization Plan

### Status: Proposed (Documentation Phase Complete)

As of October 2025, a comprehensive workspace reorganization has been planned to address organizational debt and improve maintainability.

### Current Issues

- **Artifact Accumulation**: 210 MB of unmanaged runtime data
- **Organizational Debt**: Root-level scripts, backup files, unclear taxonomy
- **Current Score**: 7.2/10 organization quality
- **Target Score**: 9.0/10 with clear standards and automation

### Reorganization Documentation

Complete reorganization specifications and guides available:

- **[Workspace Reorganization Specification](/specifications/workspace-reorganization.yaml)** - Target architecture, migration rules, retention policies
- **[Complete Move Map](/specifications/reorg-move-map.yaml)** - 28 file operations with dependencies and validation
- **[Tool Organization Standards](/docs/standards/TOOL_ORGANIZATION.md)** - Taxonomy, decision tree, development workflow
- **[Tool Manifest](/tools/tool-manifest.yaml)** - Machine-readable registry of 19 tools
- **[Cleanup Targets](/specifications/reorg-cleanup-targets.yaml)** - 12 cleanup operations with safety protocols
- **[Artifact Retention Policy](/docs/maintenance/ARTIFACT_RETENTION.md)** - 30-day retention with automated archival
- **[Health Check Specification](/specifications/workspace-health-check.yaml)** - 42 validation checks across 8 categories
- **[Rollback Procedures](/docs/maintenance/REORGANIZATION_ROLLBACK.md)** - Phase-by-phase safety procedures
- **[Migration Guide](/docs/maintenance/WORKSPACE_REORGANIZATION_GUIDE.md)** - Step-by-step execution instructions
- **[Execution Checklists](/specifications/reorg-execution-checklists.yaml)** - Pre/phase/post migration checklists

### Target Directory Structure

The proposed reorganization enhances the existing structure:

```
~/.claude/
├── [Existing Core - Unchanged]
├── tools/                        # Enhanced tool organization
│   ├── bin/                      # [NEW] Executable wrappers
│   ├── config/                   # [NEW] Configuration utilities
│   ├── lib/                      # [NEW] Shared libraries
│   └── {tool-name}/              # Individual tool directories
├── system/                       # Enhanced system organization
│   ├── todos/                    # [MOVED FROM ROOT]
│   ├── file-history/             # [MOVED FROM ROOT]
│   ├── debug/                    # [MOVED FROM ROOT]
│   ├── history/                  # [CONSOLIDATED]
│   │   ├── session-history.jsonl # [MOVED FROM ROOT]
│   │   └── archive/              # [MOVED FROM ROOT]
│   └── [existing system files]
├── archive/                      # [NEW] Compressed old artifacts
│   ├── shell-snapshots-YYYY-MM.tar.gz
│   ├── debug-logs-YYYY-MM.tar.gz
│   └── file-history-YYYY-MM.tar.gz
└── specifications/               # [ENHANCED] Machine-readable specs
    └── [reorganization specs]
```

### Reorganization Phases

1. **Phase 1: Documentation** ✅ Complete (October 2025)
   - All specifications and guides created
   - Tool manifest documented
   - Target architecture defined

2. **Phase 2: Safe Cleanup** - Remove backup files, fix anomalies
3. **Phase 3: Root Cleanup** - Move root scripts to tools/
4. **Phase 4: System Consolidation** ⚠️ High Risk - Move runtime artifacts
5. **Phase 5: Archival** - Compress old artifacts (30-day policy)
6. **Phase 6: Advanced** - Optional uv migration

### Conservative Approach

- **Documentation-first**: Complete blueprint before execution
- **Phased execution**: Independent, reversible phases
- **Validation gates**: Health checks after each phase
- **Rollback procedures**: Documented for every operation
- **Risk assessment**: Clear marking of high-risk operations

### Tool Organization Taxonomy

New decision tree for script placement:

- **Automation hooks** → `/automation/{system-name}/`
- **Configuration utilities** → `/tools/config/`
- **Standalone tools** → `/tools/{tool-name}/`
- **Executable wrappers** → `/tools/bin/`
- **System integration** → `/bin/` (minimize new scripts)

See `/docs/standards/TOOL_ORGANIZATION.md` for complete taxonomy.

### Artifact Retention

Automated 30-day retention policy:

- **Shell snapshots**: Archive after 30 days, ~80% compression
- **Debug logs**: Archive after 30 days, selective by severity
- **File history**: Archive after 30 days, test Claude Code compatibility
- **Automation**: Monthly LaunchAgent or cron job

Expected space savings: ~150-200 MB initially, ongoing management

### Health Monitoring

42 validation checks across 8 categories:

1. File organization (8 checks)
2. Tool validation (6 checks)
3. Symlink integrity (4 checks)
4. Hook validation (5 checks)
5. Documentation links (3 checks)
6. Permission validation (4 checks)
7. Artifact management (6 checks)
8. Git health (6 checks)

Automation target: `/tools/bin/workspace-health-check.sh`

### Execution Status

- **Current**: Documentation phase complete
- **Next**: Review and approval
- **Timeline**: Phased execution over 2-4 weeks
- **Risk mitigation**: Conservative approach, extensive validation

For detailed execution instructions, see `/docs/maintenance/WORKSPACE_REORGANIZATION_GUIDE.md`.

---

**Last Updated**: October 23, 2025 (Architecture version 2.2, Reorganization plan v1.0.0)
**Architecture Version**: 2.2 - CNS Purification & Async Architecture Complete
**Reorganization Status**: Documentation phase complete, awaiting execution approval
**Compatible with**: Claude Code official constraints as of October 2025
