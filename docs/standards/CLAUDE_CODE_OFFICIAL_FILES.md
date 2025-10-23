# Claude Code Official Files - DO NOT MOVE OR DELETE

This document catalogues critical files and directories that are integral to Claude Code functionality. **Moving, deleting, or improperly modifying these files will break Claude Code.**

## 🚨 CRITICAL CLAUDE CODE SYSTEM FILES

### Core Configuration Files

- `CLAUDE.md` - ✅ **CLAUDE CODE OFFICIAL** - User memory and global instructions
- `settings.json` - ✅ **CLAUDE CODE OFFICIAL** - Claude Code configuration and settings
- `.gitignore` - ⚠️ **SYSTEM CRITICAL** - Version control exclusions (customizable but essential)

### System Directories

- `system/` - ✅ **CLAUDE CODE OFFICIAL** - Session management and runtime data
  - `~/.claude/projects/` - Auto-generated session files (canonical)
  - `system/todos/` - Todo tracking system files
  - **WARNING**: Do not move or delete the `system/` directory

### Automation Integration

- `automation/cns/` - ⚠️ **CLAUDE CODE INTEGRATION** - CNS hook system
  - CNS configuration and execution files via `settings.json`
  - Integration with Claude Code's event system
  - **CAUTION**: Modifications may break automation features

### Auto-Generated Runtime Data

- `shell-snapshots/` - 🔄 **AUTO-GENERATED** - Temporary shell command snapshots
  - Auto-created during Claude Code sessions
  - Excluded from version control
  - Safe to delete (will be regenerated)

## ✅ USER-SAFE DIRECTORIES

These directories are user-created and safe to modify:

- `agents/` - Custom agent configurations
- `automation/` - User automation scripts
- `commands/` - Custom slash commands
- `docs/` - User documentation
- `history/` - Historical data archive
- `tmux/` - Tmux configurations
- `tools/` - Standalone utilities

## 📋 DIRECTORY STATUS LEGEND

- ✅ **CLAUDE CODE OFFICIAL** - Core system file, do not move/delete
- ⚠️ **CLAUDE CODE INTEGRATION** - Integrates with Claude Code, modify with caution
- 🔄 **AUTO-GENERATED** - Automatically created, safe to delete
- ❌ **USER DIRECTORY** - User-created, safe to customize

## 🔧 SAFE MODIFICATIONS

You can safely:

- Add custom files to user directories
- Modify user automation scripts
- Create new tools and utilities
- Customize tmux and agent configurations
- Update documentation in `docs/`

## ⛔ DANGEROUS OPERATIONS

**Never do these:**

- Move or rename the `system/` directory
- Delete `CLAUDE.md` or `settings.json`
- Modify auto-generated session files
- Break the Claude Code directory structure

---

**Remember**: When in doubt, check this document before making structural changes to the `.claude` directory.
