# OSC 52 SSH Clipboard Integration - Implementation Summary

## What We Built

A transparent clipboard bridge enabling Claude Code CLI `/export` command to copy data from a remote Linux box (via SSH, through tmux) to macOS system clipboard using OSC 52 escape sequences.

## The Key Insight

**Problem**: Claude Code `/export` hardcoded to call `xclip -selection clipboard`

**Solution**: Create fake `xclip` at `~/.local/bin/xclip` that:

1. Accepts same CLI arguments as real xclip
1. Reads stdin (the data to copy)
1. Base64 encodes it
1. Wraps in OSC 52 escape sequence
1. Double-wraps if inside tmux (detected via `$TMUX` env var)
1. **Outputs to stderr (`>&2`)** not `/dev/tty`

## Critical Discovery: `>&2` vs `/dev/tty`

### First Attempt (Failed)

```bash
printf '\033]52;c;%s\007' "$encoded" > /dev/tty
# Error: /dev/tty: No such device or address
```

### Why It Failed

- Claude Code executes tools in **non-interactive subprocesses**
- Non-interactive processes lack a **controlling terminal**
- `/dev/tty` doesn't exist in this context

### Working Solution

```bash
printf '\033]52;c;%s\007' "$encoded" >&2
```

### Why It Works

1. **stderr (fd 2) always available** - even in non-interactive contexts
1. **Terminal emulators read both stdout and stderr** for control sequences
1. **Escape sequences are invisible** - terminal interprets them, doesn't display
1. **Claude Code doesn't suppress stderr** - it displays tool output streams
1. **Ghostty receives sequence** regardless of which stream carries it

## Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. User Action                                                    │
│    Claude Code session > /export                                  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 2. Claude Code Execution                                          │
│    echo "<conversation_data>" | xclip -selection clipboard       │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 3. System Resolves Binary                                         │
│    PATH search: /usr/bin/xclip → not found                       │
│                 ~/.local/bin/xclip → FOUND (our wrapper)         │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 4. Wrapper Execution (in subprocess)                              │
│    • Read stdin: conversation data                                │
│    • Base64 encode: SGVsbG8gd29ybGQ=                              │
│    • Detect tmux: check $TMUX env var                             │
│    • Format OSC 52: \033]52;c;SGVsbG8gd29ybGQ=\007               │
│    • If tmux: wrap → \033Ptmux;\033\033]52;c;...\007\033\\      │
│    • Write to stderr: printf '...' >&2                            │
│      (Critical: NOT >/dev/tty because no controlling terminal)   │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 5. tmux Layer (if present)                                        │
│    • Receive on stderr: \033Ptmux;\033\033]52;c;...\007\033\\   │
│    • Recognize DCS passthrough: \033Ptmux;                        │
│    • Unwrap double escape: \033\033 → \033                       │
│    • Pass through: \033]52;c;...\007                             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 6. SSH Transport                                                  │
│    • Escape sequence travels over SSH connection                  │
│    • Transparent to SSH protocol (just byte stream)               │
│    • No special SSH config needed                                 │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 7. Ghostty Terminal (macOS)                                       │
│    • Config: clipboard-write = allow                              │
│    • Receives: \033]52;c;SGVsbG8gd29ybGQ=\007                    │
│    • Parses OSC 52 sequence                                       │
│    • Extracts: SGVsbG8gd29ybGQ=                                   │
│    • Base64 decodes: Hello world                                  │
│    • Writes to: NSPasteboard (macOS system clipboard)            │
└──────────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 8. User Can Paste                                                 │
│    ⌘V anywhere on macOS → "Hello world"                          │
└──────────────────────────────────────────────────────────────────┘
```

## Files Created/Modified

### New Files

1. **`~/.local/bin/xclip`** (remote Linux)

   - xclip-compatible wrapper
   - Emits OSC 52 to stderr
   - Handles tmux detection and wrapping

1. **`~/.claude/docs/setup/ssh-clipboard-osc52.md`**

   - Complete setup guide
   - Testing procedures
   - Troubleshooting tips

1. **`~/.claude/docs/setup/osc52-deep-dive.md`**

   - Technical deep dive
   - Protocol details
   - Architecture diagrams
   - Security considerations

### Modified Files

1. **`~/.zshrc`** (remote Linux)

   - Added `osc52-copy()` function
   - Added `pbcopy` alias for interactive use

1. **`~/.claude/CLAUDE.md`**

   - Added "SSH Clipboard Integration (OSC 52)" section
   - Concise reference with links to detailed docs
   - Emphasized critical `>&2` vs `/dev/tty` detail

1. **`~/.claude/docs/setup/terminal-setup.md`**

   - Added reference to OSC 52 setup
   - Quick setup instructions

## Testing & Verification

### What Works ✅

```bash
# Claude Code
> /export
  ⎿  Conversation copied to clipboard

# Command line (interactive)
echo "test" | xclip -selection clipboard
echo "test" | pbcopy
osc52-copy "direct text"

# All work from:
- Direct SSH session
- Inside tmux
- Via Claude Code tool execution
```

### Terminal Support Verified

- ✅ Ghostty (with clipboard-write = allow)
- ✅ Through tmux 3.x
- ✅ Over SSH (any distance, any latency)

## Why This Architecture is Correct

### 1. Wrapper Pattern

**Advantage**: Transparent to Claude Code

- No source code changes needed
- Works with any tool expecting `xclip`
- Drop-in replacement

### 2. OSC 52 Protocol

**Advantage**: Terminal-native clipboard

- No X11 forwarding (security risk, complexity)
- No reverse SSH (firewall issues)
- No cloud clipboard (privacy concerns)
- Works through SSH transparently

### 3. stderr Output

**Advantage**: Works in non-interactive contexts

- No TTY requirement
- subprocess-safe
- Terminal emulators monitor both stdout/stderr
- Invisible to user (control sequences don't display)

### 4. tmux Detection

**Advantage**: Automatic adaptation

- Checks `$TMUX` environment variable
- Applies correct wrapping automatically
- No user configuration needed
- Works both inside and outside tmux

### 5. Base64 Encoding

**Advantage**: Binary-safe transport

- Handles any character encoding
- No shell escaping issues
- No line-ending problems
- Standard format (RFC 4648)

## Documentation Architecture

Following `~/.claude/` hub-and-spoke pattern:

```
~/.claude/
├── CLAUDE.md                         # Link farm, essentials only
│   └── → SSH Clipboard Integration   # Added: concise summary + links
│
├── docs/
│   └── setup/
│       ├── terminal-setup.md         # Updated: added OSC 52 reference
│       ├── ssh-clipboard-osc52.md    # New: complete setup guide
│       └── osc52-deep-dive.md        # New: technical deep dive
│
└── (actual implementation on remote Linux)
    ~/.local/bin/xclip                # New: wrapper script
    ~/.zshrc                           # Updated: shell integration
```

### Design Principles Applied

1. **Link Farm**: CLAUDE.md contains only essentials + links
1. **Single Source of Truth**: Detailed docs in proper locations
1. **Hub-and-Spoke**: Central index points to module-specific docs
1. **Machine-Readable**: OpenAPI specs for integrations (not needed here)
1. **Separation**: Config (`~/.local/bin/`) separate from docs (`~/.claude/docs/`)

## Key Learnings for Future Reference

### 1. Non-Interactive Subprocess Execution

When tools run in contexts like:

- Claude Code tool execution
- CI/CD pipelines
- Cron jobs
- systemd services

**Assumption that fails**: `/dev/tty` exists
**Safe alternative**: stderr (`>&2`) or stdout

### 2. Terminal Control Sequences

Control sequences work via **any output stream**:

- stdout: `printf '...' >&1`
- stderr: `printf '...' >&2`
- /dev/tty: `printf '...' >/dev/tty` (if exists)

Terminal emulators **scan all streams** for escape sequences. Choose the stream that's guaranteed available in your execution context.

### 3. Protocol Layering

When working through multiplexers (tmux, screen):

1. Check if inside multiplexer (env var)
1. Apply appropriate wrapping
1. Let multiplexer pass through to terminal

Don't try to bypass the multiplexer—work with it.

### 4. Binary Shimming Pattern

To intercept system commands:

1. Create wrapper in `~/.local/bin/`
1. Ensure `~/.local/bin/` early in PATH
1. Preserve CLI compatibility (parse arguments)
1. Implement alternate backend (OSC 52 vs X11)
1. Make transparent to caller

This pattern works for:

- Clipboard: xclip, wl-copy, pbcopy
- Editors: $EDITOR wrapper
- Build tools: make, cargo, npm wrappers
- Notification: notify-send wrapper

### 5. Documentation as Link Farm

For user memory systems (like CLAUDE.md):

- **Keep it concise**: Only irreducible essentials
- **Link liberally**: Point to detailed docs
- **Emphasize critical details**: The `>&2` vs `/dev/tty` gotcha
- **Show requirements clearly**: What's needed where
- **Maintain separation**: Reference docs elsewhere, link to them

## What Makes This "Irreducible"

The solution cannot be simplified further:

**Cannot remove**:

- ❌ Base64 encoding (binary safety)
- ❌ OSC 52 format (terminal protocol)
- ❌ stderr output (non-interactive requirement)
- ❌ tmux detection (correct wrapping)
- ❌ xclip wrapper (Claude Code expects it)

**Cannot substitute**:

- ❌ X11 forwarding (requires admin, security risk)
- ❌ Cloud clipboard (privacy, latency)
- ❌ netcat bridge (firewall, security)
- ❌ pbcopy SSH reverse (connectivity, complexity)

**Each component essential**:

1. **xclip wrapper** → intercepts Claude Code call
1. **OSC 52** → terminal-native clipboard protocol
1. **Base64** → encoding for binary safety
1. **tmux wrapping** → passthrough for multiplexer
1. **stderr** → guaranteed stream in subprocess
1. **Ghostty config** → enables clipboard acceptance

Remove any one → solution breaks.

## Success Metrics

✅ **Functional**:

- Claude Code `/export` works
- Command-line clipboard works
- Works through tmux
- Works over SSH (any distance)

✅ **Transparent**:

- No Claude Code modifications
- No SSH config changes
- No sudo/admin access needed
- Automatic tmux detection

✅ **Documented**:

- CLAUDE.md updated (essentials + links)
- Setup guide created (step-by-step)
- Deep dive written (technical details)
- Terminal setup doc updated (cross-reference)

✅ **Maintainable**:

- Single wrapper script
- Clear documentation path
- Hub-and-spoke architecture
- Links prevent doc drift

## Future Extensions

### For other use cases:

1. **Paste support**: Add OSC 52 read capability (if terminal supports)
1. **Selection targets**: Support primary selection (`-selection primary`)
1. **Clipboard history**: Log copies to file for recovery
1. **Notification**: Pushover alert on large clipboard operations

### For other tools:

- `wl-copy` wrapper (same pattern, different binary name)
- `pbcopy` wrapper (for scripts that hardcode macOS command)
- `xsel` wrapper (alternative to xclip)

Same architecture applies to all clipboard tools—just need to match CLI interface.

______________________________________________________________________

## Bottom Line

**What we did right**:
Using `>&2` instead of `/dev/tty` in the xclip wrapper, because Claude Code (and similar non-interactive tool execution contexts) doesn't allocate a controlling terminal, but stderr is always available and terminal emulators read from it for escape sequences.

**Why it works**:
OSC 52 escape sequences travel over SSH transparently, tmux passes them through when properly wrapped, Ghostty interprets them to update macOS clipboard, and Claude Code remains oblivious—it just thinks xclip worked normally.

**Documentation strategy**:
CLAUDE.md as link farm with irreducible essentials (the `>&2` detail), detailed docs in proper locations (`docs/setup/`), hub-and-spoke architecture maintained, single source of truth preserved.
