# Simple tmux Session Manager

Clean, minimal tmux session management with smart naming.

## 🎯 Philosophy

**Simple. Clean. Transparent.**
- Pure tmux commands under the hood
- Smart folder-based naming
- No plugins, no persistence, no complexity
- Sessions exist while you use them

## 🚀 Quick Start

### One-Command Setup
```bash
setup-simple-tmux
```

That's it! You now have:
- ✅ Smart session management  
- ✅ Simple commands (ts/tl/tk)
- ✅ Zero configuration needed
- ✅ Clean, fast operation

### Basic Usage
```bash
# Create/attach session using current folder name
ts                    # or: tmux-session

# Create/attach session with custom name  
ts auth               # or: tmux-session auth

# List all sessions
tl                    # or: tmux-list

# Kill a session
tk auth               # or: tmux-kill auth

# Detach from session (keeps it running)
Ctrl+b, then d
```

## 🧠 Smart Naming

The session manager automatically creates intelligent session names:

| Directory | Session Name | Reason |
|-----------|--------------|--------|
| `~/my-project` | `my-project` | Standard naming |
| `~/.config` | `dotconfig` | Dot folder awareness |
| `~/.git` | `dotgit` | Preserves dot nature |
| `/tmp/Test_App` | `test-app` | Normalized to lowercase |
| `~/My-Cool-App` | `my-cool-app` | Spaces/symbols → hyphens |

## 📋 Commands

### Core Commands
- `tmux-session [name]` - Create/attach session (uses folder name if no name provided)
- `tmux-list` - List all sessions with status
- `tmux-kill <name>` - Kill specific session

### Quick Aliases
- `ts [name]` - Short for `tmux-session`
- `tl` - Short for `tmux-list`
- `tk <name>` - Short for `tmux-kill`
- `tmux-here` - Same as `ts` (create/attach using folder name)

### Help
- `tmux-help` - Show complete usage guide (shell function)

## 🎪 Example Workflow

```bash
# Working on a project
cd ~/my-awesome-project
ts                           # Creates 'my-awesome-project' session

# In the tmux session - work normally
# Press Ctrl+b then d to detach (session keeps running)

# Later, return to work
cd ~/my-awesome-project  
ts                           # Attaches to existing 'my-awesome-project' session

# Multiple contexts in same project
ts frontend                  # Create dedicated frontend session
ts backend                   # Create dedicated backend session
ts testing                   # Create dedicated testing session

# List all sessions
tl
# ==================
# SESSION              | WINDOWS  | CREATED                   | STATUS
# ---------------------+----------+---------------------------+--------
# my-awesome-project   | 1w       | Jul 29 10:30              | 🟢 active
# frontend             | 2w       | Jul 29 11:15              | ⚫ detached
# backend              | 1w       | Jul 29 11:16              | ⚫ detached

# Kill finished sessions
tk frontend
tk backend
```

## 🔧 Features

### ✅ What It Does
- **Smart naming**: Converts folder names to valid session names
- **Dot folder awareness**: `.config` → `dotconfig`
- **Session management**: Create if new, attach if exists
- **Standard tmux**: Uses native tmux commands only
- **Clean operation**: No background processes or plugins

### ❌ What It Doesn't Do
- No session persistence across reboots
- No complex automation or send-keys
- No Claude Code integration
- No configuration files or JSON
- No multi-file architecture
- No session restoration/saving

## 🏗️ File Structure

```
~/.claude/tmux/
├── bin/
│   ├── tmux-session          # Main session manager
│   ├── tmux-list            # Session listing utility  
│   └── tmux-kill            # Session killer utility
├── config/
│   ├── simple-shell-integration.sh  # Shell aliases & functions
│   └── tmux.conf            # Clean tmux configuration
└── SIMPLE-USAGE.md         # This documentation
```

## 💡 Design Principles

1. **Transparency**: You can see exactly what tmux commands are run
2. **Simplicity**: Each script does one thing well
3. **Unix-First**: Built for Unix-like systems (macOS, Linux) using standard conventions
4. **Maintainability**: Easy to modify and extend
5. **Predictability**: Same input always gives same output
6. **Clean**: No plugins, no persistence, no complexity

> **Platform Note**: Designed for Unix environments with standard `$HOME` and shell conventions. Not Windows-compatible.

## 🔧 Customization

The scripts are simple bash files - feel free to modify them:

- `tmux-session`: Modify naming logic or session creation
- `tmux-list`: Customize output format
- `tmux-kill`: Add confirmation prompts
- `simple-shell-integration.sh`: Add your own aliases

## ⚡ Session Management

### Detaching vs Exiting
- **Detach** (`Ctrl+b, d`): Session keeps running in background
- **Exit** (`exit` or `Ctrl+d`): Terminates session completely

### Session Lifecycle
- Sessions exist only while tmux is running
- Detached sessions persist until system reboot or manual kill
- No automatic restoration after reboot (by design)

## ✨ Benefits of Simple Approach

| Aspect | Simple Approach | Complex Systems |
|--------|----------------|-----------------|
| **Learning** | Standard tmux knowledge | Custom commands |
| **Debugging** | Visible commands | Hidden automation |
| **Portability** | Works everywhere | Requires setup |
| **Maintenance** | Minimal | High overhead |
| **Reliability** | Predictable | Race conditions |
| **Performance** | Fast | Complex logic |
| **Resources** | Minimal | Background processes |

---

*Simple tools for simple needs. Tmux does session management perfectly - no plugins required.*