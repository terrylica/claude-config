# Zellij Session Recovery & Crash Resilience

Complete guide to Zellij session persistence, crash recovery, and session management in Ghostty.

## Overview

Zellij is configured to automatically save your session state every 1 second and restore it after crashes or computer reboots. This ensures you never lose your work environment.

## Configuration Files

### 1. **~/.zshrc** - Shell Integration
Zellij is configured to:
- Auto-start only when running inside Ghostty (via `GHOSTTY_RESOURCES_DIR` detection)
- Auto-attach to existing sessions (reuse instead of creating duplicates)
- Auto-exit shell when Zellij closes (prevents nested shells)

**Key Settings:**
```zsh
if [[ -n "$GHOSTTY_RESOURCES_DIR" ]]; then
  export ZELLIJ_AUTO_ATTACH=true
  export ZELLIJ_AUTO_EXIT=true
  eval "$(zellij setup --generate-auto-start zsh)"
fi
```

### 2. **~/.config/zellij/config.kdl** - Session Recovery
Session state serialization is fully enabled:

```kdl
// Saves session layout, panes, tabs every 1 second
session_serialization true

// Also saves visible viewport when serializing
serialize_pane_viewport true

// Save last 5000 lines of scrollback (adjust as needed)
scrollback_lines_to_serialize 5000

// Prevents nested shells when reattaching
auto_exit_zellij_on_quit true
```

## What Gets Saved

✓ **Always Saved:**
- Session layout (panes, tabs, splits)
- Running commands in each pane

✓ **Optional (Currently Enabled):**
- Pane viewport (what was visible on screen)
- Scrollback buffer (command history, last 5000 lines)

✗ **Not Saved (By Design):**
- Environment variables (can be problematic on recovery)
- Command output/results (can be huge)

## How Recovery Works

### After Normal Shutdown
1. Zellij saves final session state
2. Session moves to "EXITED" status in session manager
3. Can be resumed anytime with `zellij attach <session-name>`

### After Crash or System Restart
1. Previous session stored in cache (~/.cache/zellij)
2. Next time terminal opens in Ghostty:
   - Zellij autostart activates
   - `ZELLIJ_AUTO_ATTACH=true` reuses session
   - Session layout and panes are restored
   - Commands show "Press ENTER to run..." safety banner

### Safety Measures
- Destructive commands (like `rm -rf`) require confirmation before running
- Prevents accidental data loss from stale commands
- You can review and edit commands before execution

## Command Reference

See **[Zellij Command Cheatsheet](zellij-cheatsheet.md)** for a printable reference of all Zellij commands.

The cheatsheet includes:
- Session management commands
- Pane and tab controls
- Keyboard shortcuts
- Session recovery procedures
- Common workflows
- Troubleshooting guide

**Print the cheatsheet as PDF** for quick reference at your terminal.

## Common Usage Examples

**See the cheatsheet for complete command reference!**

### Resume from Crash
```bash
# Open new Ghostty terminal
# Session auto-resumes automatically

# Or manually list and attach:
zellij ls --exited              # List resurrectable sessions
zellij attach <session-name>    # Attach to specific session
```

### Switch Between Sessions
```bash
zellij                          # Show session manager
zellij ls                       # List all sessions
zellij attach work              # Attach to "work" session
```

### Create Named Session
```bash
zellij --session main           # Create "main" session
zellij --session dev            # Create "dev" session
```

## Scrollback Configuration

### Current Setting: 5000 Lines

Balances:
- **Recovery capability**: Can restore up to 5000 lines of history
- **Disk usage**: Reasonable size without excessive storage

### Adjusting Scrollback

Edit `~/.config/zellij/config.kdl`:

```kdl
# Save all scrollback (maximum recovery, uses more disk)
scrollback_lines_to_serialize 0

# Save limited scrollback (minimal disk usage)
scrollback_lines_to_serialize 1000

# Current default (good balance)
scrollback_lines_to_serialize 5000
```

## Troubleshooting

### Session Not Recovering
- Check if session is in "EXITED" status: `zlr`
- Verify `session_serialization true` in config.kdl
- Check cache directory: `ls ~/.cache/zellij/`
- Try manual attach: `zla <session-name>`

### Duplicate Sessions Created
- Ensure `ZELLIJ_AUTO_ATTACH=true` is set in .zshrc
- Disable auto-attach if you prefer manual control (remove the env var)

### Commands Not Running on Recovery
- This is intentional! Commands show "Press ENTER to run..." banner
- Allows review before execution
- Edit or skip problematic commands

### Excessive Disk Usage
- Reduce `scrollback_lines_to_serialize` value
- Or set to 0 if unlimited scrollback causes issues

## Performance Impact

- **Serialization overhead**: Minimal (runs every 1 second in background)
- **Memory usage**: Negligible
- **Disk space**: 5-50KB per session (depending on pane count and scrollback)

Zellij session serialization has minimal performance impact while providing comprehensive crash recovery.

## References

- [Zellij Session Resurrection](https://zellij.dev/documentation/session-resurrection.html)
- [Zellij Configuration Options](https://zellij.dev/documentation/options)
- [Zellij Integration Guide](https://zellij.dev/documentation/integration.html)

## See Also

- [Ghostty Shell Integration](../terminal-setup.md)
- [Terminal Setup Guide](terminal-setup.md)
