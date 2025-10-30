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

Session state serialization is fully enabled with balanced power-user settings:

```kdl
// Buffer: 50K lines per pane (5x default for logs/debugging)
scroll_buffer_size 50000

// Saves session layout, panes, tabs every 60 seconds
session_serialization true

// Also saves visible viewport when serializing
serialize_pane_viewport true

// Save last 10000 lines of scrollback for crash recovery
// (doubled from 5000 for better recovery capability)
scrollback_lines_to_serialize 10000

// Serialization frequency (60 seconds = balanced, explicit default)
serialization_interval 60

// Edit scrollback in Helix
scrollback_editor "hx"

// Prevents nested shells when reattaching
auto_exit_zellij_on_quit true
```

**Configuration Profile**: Balanced Power-User

- **Memory**: ~8 MB per pane (suitable for feature engineering workloads)
- **Disk**: ~100-250 KB per session
- **Recovery**: Up to 10,000 lines of scrollback preserved
- **Performance**: Negligible overhead, minimal disk I/O

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
1. Session moves to "EXITED" status in session manager
1. Can be resumed anytime with `zellij attach <session-name>`

### After Crash or System Restart

1. Previous session stored in cache (~/.cache/zellij)
1. Next time terminal opens in Ghostty:
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

### Current Settings

**Buffer Size**: 50,000 lines (in memory)

- Immediately available when scrolling up with `Ctrl+S`
- Lost when pane closes or session exits
- Provides extensive history for logs/debugging

**Serialization**: 10,000 lines (to disk)

- Restored automatically after crashes/restarts
- Survives system shutdown
- Doubled from previous 5000 for better recovery

### Adjusting Scrollback

Edit `~/.config/zellij/config.kdl`:

```kdl
# BUFFER SIZE (in-memory, immediate scrollback)
scroll_buffer_size 10000        # Conservative (default)
scroll_buffer_size 50000        # Current: Power-user (logs/debugging)
scroll_buffer_size 100000       # Maximum (high memory use)

# SERIALIZATION (disk, crash recovery)
scrollback_lines_to_serialize 0         # Unlimited (uses more disk)
scrollback_lines_to_serialize 1000      # Minimal (minimal disk)
scrollback_lines_to_serialize 10000     # Current: Balanced power-user
scrollback_lines_to_serialize 50000     # Maximum recovery
```

### Why Two Settings?

- **`scroll_buffer_size`**: How much Zellij keeps in RAM - determines immediate scrollback when you press `Ctrl+S`
- **`scrollback_lines_to_serialize`**: How much gets saved to disk for crash recovery - survives system restarts

Both matter for comprehensive history tracking.

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

- [Ghostty Shell Integration](terminal-setup.md)
- [Terminal Setup Guide](terminal-setup.md)
