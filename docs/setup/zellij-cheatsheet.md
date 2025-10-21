# Zellij Command Cheatsheet

**Print this page as PDF for quick reference (Cmd+P or File → Print)**

---

## Session Management

| Command | Description |
|---------|-------------|
| `zellij` | Start Zellij or show session manager |
| `zellij ls` | List all running sessions |
| `zellij ls --exited` | List crashed/exited sessions (resurrectable) |
| `zellij attach <name>` | Attach to existing session |
| `zellij --session <name>` | Create new named session |
| `zellij kill-session <name>` | Kill a running session |
| `zellij kill-all-sessions` | Kill all sessions |

---

## Pane Controls (Inside Zellij)

### Navigation
| Key | Action |
|-----|--------|
| `Ctrl+G` | Enter normal mode (from any mode) |
| `H` / `←` | Move focus left |
| `J` / `↓` | Move focus down |
| `K` / `↑` | Move focus up |
| `L` / `→` | Move focus right |
| `P` | Cycle through panes |

### Pane Management
| Key | Action |
|-----|--------|
| `D` | Split new pane down |
| `R` | Split new pane right |
| `N` | Split new pane (stacked) |
| `C` | Rename pane |
| `F` | Toggle pane fullscreen |
| `W` | Toggle floating panes |
| `Z` | Toggle pane frames |
| `E` | Embed/float pane |
| `I` | Toggle pane pinned |

---

## Tab Controls

| Key | Action |
|-----|--------|
| `1-9` | Jump to tab 1-9 |
| `H` / `←` | Previous tab |
| `J` / `↓` | Next tab |
| `K` / `↑` | Previous tab |
| `L` / `→` | Next tab |
| `N` | New tab |
| `R` | Rename tab |
| `S` | Toggle sync mode (all panes) |
| `[` | Break pane left |
| `]` | Break pane right |
| `B` | Break pane to new tab |

---

## Session Recovery

### After Crash or Reboot

**Automatic (if configured correctly):**
1. Open new Ghostty terminal
2. Zellij auto-resumes previous session
3. Commands show "Press ENTER to run..." banner
4. Review and execute commands

**Manual Recovery:**
```bash
# List resurrectable sessions
zellij ls --exited

# Resume specific session
zellij attach <session-name>

# Resume with session manager
zellij
# Select session from EXITED section
```

---

## Configuration

### Enable/Disable Autostart

**Modify ~/.zshrc:**
```zsh
# To enable autostart in Ghostty:
export ZELLIJ_AUTO_ATTACH=true

# To disable autostart:
# export ZELLIJ_AUTO_ATTACH=true    # ← comment out
```

### Session Persistence Settings

**Location:** `~/.config/zellij/config.kdl`

```kdl
# BALANCED POWER-USER SETUP (recommended for feature engineering)

# Scrollback buffer size (in memory) - 5x default for logs/debugging
scroll_buffer_size 50000

# Save session state every 60 seconds
session_serialization true

# Save visible viewport when serializing
serialize_pane_viewport true

# Crash recovery: save 10K lines to disk (doubled for better recovery)
scrollback_lines_to_serialize 10000

# Serialization frequency (60 seconds = balanced)
serialization_interval 60

# Edit scrollback with Helix
scrollback_editor "hx"

# Auto-exit shell when Zellij closes
auto_exit_zellij_on_quit true
```

**See**: [`docs/setup/zellij-configuration.md`](zellij-configuration.md) for alternative profiles (maximum protection, conservative, etc.)

---

## Quick Reference

### Common Workflows

#### Resume After Crash
```bash
zellij attach <session-name>
```

#### List Everything
```bash
zellij ls              # Show all sessions
zellij ls --exited    # Show crashed sessions
```

#### Create and Name Session
```bash
zellij --session work
zellij --session dev
zellij --session email
```

#### Switch Between Sessions
```bash
zellij                # Show session manager
# Select session from list
```

---

## Important Notes

✓ **Auto-recovery is enabled** - Sessions save state every 1 second
✓ **Safety banner on resume** - Destructive commands require confirmation
✓ **Ghostty-only autostart** - Zellij only auto-starts inside Ghostty
✓ **Scroll up for history** - Previous command output is preserved in scrollback
✓ **Mouse support enabled** - Full scrolling, tab clicking, and pane selection via mouse

⚠️ **Before executing recovered commands** - Always review them in case they're stale
⚠️ **Session naming** - Use descriptive names like `work`, `dev`, `admin`
⚠️ **URLs require Shift+Click** - Use `Shift+Click` to open links (standard multiplexer behavior)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Session not recovering | Check: `zellij ls --exited` to see available sessions |
| Commands won't run on recovery | Normal! Press ENTER to execute, press ESC to skip |
| Duplicate sessions created | Ensure `ZELLIJ_AUTO_ATTACH=true` is set in .zshrc |
| Too much disk usage | Lower `scrollback_lines_to_serialize` value in config.kdl |
| Autostart not working in terminal | Verify you're using Ghostty (`echo $GHOSTTY_RESOURCES_DIR`) |
| Links not clickable in Ghostty | Use `Shift+Click` on URLs (standard workaround for multiplexers) |

---

**Last Updated:** October 2025
**Zellij Version:** 0.43.1+
**Documentation:** See `docs/setup/zellij-session-recovery.md`
