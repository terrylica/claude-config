# Claude Code tmux Integration Setup

## Quick Installation

1. **Add to your shell configuration:**
   ```bash
   echo 'source ~/.claude/tmux_aliases.sh' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Test the installation:**
   ```bash
   claude-start    # Start new session
   claude-list     # View active sessions
   claude-resume   # Interactive session selector
   ```

## Command Reference

### Primary Commands
- `claude-start` / `claude-new` - Start new session in current workspace
- `claude-resume` / `claude-select` - Interactive session selector
- `claude-list` / `claude-ls` - List all active Claude sessions
- `claude-quick` - Resume latest session or start new one
- `claude-here` - Start session specifically in current directory

### Maintenance
- `claude-cleanup [days]` - Remove sessions older than N days (default: 7)
- `claude-kill {session}` - Terminate specific session
- `tmux-kill-all` - Kill all Claude sessions

### Utilities
- `claude-keys` - Show tmux key binding reference
- `claude-status` - Quick status of active sessions

## Session Naming Convention

**Format:** `claude-{workspace}-{YYYY-MM-DD-HHMM}`

**Examples:**
- `claude-my-project-2025-01-15-1430`
- `claude-scripts-2025-01-15-0900`
- `claude-api-server-2025-01-15-1630`

## Workflow Examples

### Daily Development
```bash
cd ~/my-project
claude-start          # Creates: claude-my-project-2025-01-15-1430
# Work happens...
# Terminal closes/crashes
claude-resume         # Interactive selector shows all sessions
```

### Multiple Projects
```bash
# Morning: Start work on API
cd ~/api-server
claude-start          # claude-api-server-2025-01-15-0900

# Afternoon: Switch to frontend
cd ~/frontend-app  
claude-start          # claude-frontend-app-2025-01-15-1400

# View all active sessions
claude-list
```

### Session Recovery
```bash
# After system restart, see what sessions exist
claude-list

# Resume specific session
claude-resume         # Interactive picker

# Or quick resume latest
claude-quick          # Attaches to most recent session
```

## Advanced Features

### Session History
- All sessions logged to `~/.claude/tmux_sessions/session_history.log`
- View recent sessions with `claude-list`
- Automatic workspace detection and tagging

### Automatic Cleanup
```bash
# Remove sessions older than 3 days
claude-cleanup 3

# Weekly cleanup (add to crontab)
0 2 * * 0 ~/.claude/tmux_claude_manager.sh cleanup 7
```

### tmux Key Bindings
- `Ctrl+b d` - Detach (session keeps running)
- `Ctrl+b s` - tmux session selector
- `Ctrl+b c` - New window in current session
- See `claude-keys` for complete reference

## Integration with Claude.md

The system respects your CLAUDE.md preferences:
- Workspace detection works with your `/Users/terryli/scripts` setup
- Session logging for audit trails
- Compatible with your existing tool preferences

## Troubleshooting

### Session Not Found
```bash
# List actual tmux sessions
tmux list-sessions

# Check if tmux is running
pgrep tmux
```

### Permission Issues
```bash
# Ensure script is executable
chmod +x ~/.claude/tmux_claude_manager.sh
```

### Cleanup Logs
```bash
# View session history
cat ~/.claude/tmux_sessions/session_history.log

# Clear old logs
> ~/.claude/tmux_sessions/session_history.log
```