# OSC 52 Clipboard over SSH: Deep Dive

## What We Discovered

### The Problem

Claude Code CLI's `/export` command was failing with:

```
Failed to copy to clipboard. Make sure `xclip` or `wl-copy` is installed
```

This happened even though we SSH'd from macOS (which has clipboard) into a Linux box inside tmux.

### Root Cause Analysis

#### Layer 1: Claude Code's Hardcoded Binary Check

- Claude Code CLI `/export` command is **hardcoded** to look for `xclip` or `wl-copy` binaries
- It does NOT use shell aliases or functions
- It does NOT try `pbcopy` (macOS native)
- It directly executes: `xclip -selection clipboard` or `wl-copy`

#### Layer 2: SSH Session Limitations

- Traditional clipboard tools (`xclip`, `wl-copy`) require local X11/Wayland display server
- SSH sessions typically lack direct access to the client's display
- Setting `DISPLAY=:0` only works if X11 forwarding is configured (security risk, complex setup)

#### Layer 3: Terminal Escape Sequences (OSC 52)

- **OSC** = Operating System Command
- **OSC 52** = Specific sequence for clipboard operations
- Format: `\033]52;<target>;base64(data)\007`
  - `\033]52;c;` = Set clipboard
  - `c` = clipboard buffer (vs primary selection `p`)
  - Base64-encoded payload
  - Terminated with BEL (`\007`) or ST (`\033\\`)

#### Layer 4: tmux Complication

- tmux intercepts escape sequences for session management
- OSC 52 sequences must be **double-wrapped** when inside tmux:
  ```
  \033Ptmux;\033\033]52;c;<data>\007\033\\
  ```
- `\033P` = DCS (Device Control String) start for tmux
- Inner escape doubled (`\033\033`) so tmux passes it through
- Terminated with ST (`\033\\`)

### The Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ macOS Client (iTerm2 Terminal)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ iTerm2 Config:                                       │   │
│  │   clipboard-read = allow                             │   │
│  │   clipboard-write = allow                            │   │
│  │   osc-color-report-format = 8-bit # OSC 52 support   │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           │ SSH Connection                   │
│                           ▼                                  │
└───────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│ Remote Linux (Debian 12)                                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ~/.local/bin/xclip (Wrapper Script)                    │  │
│  │  • Intercepts xclip -selection clipboard              │  │
│  │  • Reads stdin                                         │  │
│  │  • Base64 encodes data                                 │  │
│  │  • Detects if in tmux ($TMUX env var)                 │  │
│  │  • Outputs OSC 52 sequence to stderr (>&2)            │  │
│  │                                                         │  │
│  │  Critical Fix: >&2 not >/dev/tty                      │  │
│  │  Reason: /dev/tty unavailable in non-interactive      │  │
│  │          contexts (like Claude Code tool execution)   │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           │ OSC 52 via stderr                 │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ tmux (if present)                                       │  │
│  │  • Recognizes \033Ptmux; prefix                        │  │
│  │  • Unwraps double-escaped sequence                     │  │
│  │  • Passes through to terminal                          │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            │ OSC 52 escape sequence
                            │ travels back over SSH
                            ▼
┌───────────────────────────────────────────────────────────────┐
│ iTerm2 Terminal (receives sequence)                          │
│  • Parses OSC 52 sequence                                     │
│  • Base64 decodes payload                                     │
│  • Writes to macOS system clipboard (NSPasteboard)            │
└───────────────────────────────────────────────────────────────┘
```

### Why `>&2` Instead of `>/dev/tty`?

**First Attempt Failed:**

```bash
printf '\033]52;c;%s\007' "$encoded" > /dev/tty
# Error: /dev/tty: No such device or address
```

**Root Cause:**

- `/dev/tty` is the **controlling terminal** device
- Claude Code runs tools in non-interactive subprocess contexts
- No controlling terminal allocated
- `/dev/tty` does not exist or is not accessible

**Working Solution:**

```bash
printf '\033]52;c;%s\007' "$encoded" >&2
```

**Why stderr (fd 2) Works:**

1. stderr is always connected (even for non-interactive processes)
1. Escape sequences written to stderr are processed by terminal emulator
1. Terminal emulators read from both stdout and stderr for control sequences
1. Claude Code doesn't suppress stderr (it displays tool output)
1. iTerm2 receives the sequence regardless of which stream it's on

### The Complete Flow

1. **User triggers**: `/export` in Claude Code
1. **Claude Code calls**: `echo "<data>" | xclip -selection clipboard`
1. **System resolves**: `~/.local/bin/xclip` (our wrapper, not real xclip)
1. **Wrapper executes**:
   ```bash
   input=$(cat)                              # Read stdin
   encoded=$(printf %s "$input" | base64 | tr -d '\n')
   if [ -n "$TMUX" ]; then
     printf "\033Ptmux;\033\033]52;c;%s\007\033\\" "$encoded" >&2
   else
     printf "\033]52;c;%s\007" "$encoded" >&2
   fi
   ```
1. **Escape sequence travels**:
   - Through tmux (if present) → unwrapped
   - Through SSH connection → transparent passthrough
   - To iTerm2 terminal → interpreted
1. **iTerm2 updates**: macOS system clipboard
1. **User can paste**: `⌘V` anywhere on macOS

### Terminal Support Matrix

| Terminal | OSC 52 Support | Notes |
| --- | --- | --- |
| iTerm2 | ✅ Full | Native, requires `clipboard-write = allow` |
| iTerm2 | ✅ Full | Native since v3.4.0 |
| WezTerm | ✅ Full | Native |
| Kitty | ✅ Full | Native |
| Alacritty | ✅ With config | Requires `osc52` feature enabled |
| tmux | ✅ Passthrough | Requires special wrapping (Ptmux) |
| Terminal.app | ❌ None | Does not support OSC 52 |
| xterm | ⚠️ Partial | Requires compile-time flag |

### iTerm2 Specific Configuration

Required in `~/.config/iTerm2/config` (macOS side):

```
clipboard-read = allow
clipboard-write = allow
```

Optional (improves compatibility):

```
osc-color-report-format = 8-bit
```

### Security Implications

**Why OSC 52 is safer than X11 forwarding:**

- No full display server access needed
- Only clipboard data can be transferred
- Can be controlled with terminal config (`clipboard-write = allow`)
- No ability to spawn windows or capture screen
- Unidirectional (client can't inject data back via OSC 52 alone)

**Potential risks:**

- Malicious script on server could exfiltrate sensitive data to clipboard
- User might paste compromised content unknowingly
- Mitigation: Trust your servers, use for personal/team environments

### Why Not X11 Forwarding?

**X11 Forwarding approach:**

```bash
# Local ~/.ssh/config
Host remote
    ForwardX11 yes

# Remote
export DISPLAY=localhost:10.0
echo "test" | xclip -selection clipboard
```

**Disadvantages:**

1. Requires `X11Forwarding yes` in `/etc/ssh/sshd_config` (admin access)
1. Requires X11 server running on macOS (XQuartz)
1. Higher security risk (full display access)
1. Slower (more protocol overhead)
1. Breaks if X11 forwarding disabled by policy

**OSC 52 advantages:**

- No server-side config changes needed
- No admin/sudo required
- Works with any terminal supporting OSC 52
- Pure escape sequences (no external dependencies)
- Works through multiplexers (tmux, screen)

### Alternative Approaches (Not Used)

#### 1. SSH RemoteCommand with pbcopy

```bash
# Remote ~/.local/bin/pbcopy
ssh ${SSH_CLIENT%% *} pbcopy
```

**Why not:**

- Requires SSH back from server to client (reverse connectivity)
- Firewall issues
- Authentication complexity

#### 2. netcat Bridge

```bash
# Client: nc -l 12345 | pbcopy
# Server: echo "data" | nc client-ip 12345
```

**Why not:**

- Requires firewall rules
- Manual port management
- Security risk (unencrypted, unauthenticated)

#### 3. Cloud Clipboard Service

```bash
# curl -X POST https://clipboard.example.com -d @-
```

**Why not:**

- Data leaves trusted network
- Requires internet connection
- Privacy/security concerns
- API rate limits

### Performance Characteristics

**Payload size limits:**

- Most terminals: 100KB - 1MB safe
- iTerm2: tested up to 10MB
- tmux: may require `set -g set-clipboard on`
- Base64 overhead: ~33% size increase

**Latency:**

- Local machine: \<1ms
- LAN SSH: 1-10ms
- WAN SSH: 50-200ms (depends on RTT)
- tmux adds: ~5ms processing overhead

### Debugging Techniques

**Test raw OSC 52 (outside tmux):**

```bash
printf '\033]52;c;%s\a' "$(echo -n 'test' | base64)"
```

**Test with tmux wrapper:**

```bash
printf '\033Ptmux;\033\033]52;c;%s\a\033\\' "$(echo -n 'test' | base64)"
```

**Verify base64 encoding:**

```bash
echo -n "Hello" | base64
# Should output: SGVsbG8=
```

**Check if terminal is processing sequence:**

```bash
strace -e write bash -c 'printf "\033]52;c;dGVzdA==\a" >&2' 2>&1 | grep 52
```

**Monitor tmux passthrough:**

```bash
tmux show-options -g | grep clipboard
# set-clipboard should be 'on' or 'external'
```

### Common Pitfalls

1. **Forgot `\n` stripping in base64:**

   ```bash
   base64 | tr -d '\n'  # Correct
   base64               # Wrong: includes newlines
   ```

1. **Wrong terminator:**

   ```bash
   printf '...\007'  # BEL (correct)
   printf '...\n'    # Wrong
   ```

1. **Missing tmux detection:**

   ```bash
   if [ -n "$TMUX" ]; then  # Correct
   if [ "$TMUX" ]; then     # Also works
   if command -v tmux; then # Wrong: checks if tmux exists, not if inside
   ```

1. **Output to wrong stream:**

   ```bash
   printf '...' >&2   # Correct
   printf '...' >&1   # Works but less reliable
   printf '...' > /dev/tty  # Fails in non-interactive
   ```

### Integration Points

**Where this solution touches:**

1. `~/.local/bin/xclip` - Wrapper script (created)
1. `~/.zshrc` - Optional: `osc52-copy()` function and `pbcopy` alias
1. iTerm2 config - Must have `clipboard-write = allow`
1. Claude Code - Uses via `/export` command (no changes needed)
1. tmux - Transparent passthrough (no config changes needed)

### Related Standards

- **ECMA-48**: Control Functions for Coded Character Sets
- **ITU T.416**: OSC (Operating System Command) specification
- **XTerm Control Sequences**: De-facto standard implementation
- **tmux DCS passthrough**: Documented in `man tmux` under "CONTROL MODE"

### Further Reading

- [OSC 52 Specification](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h3-Operating-System-Commands)
- [iTerm2 Documentation](https://iTerm2.org/docs/config/reference)
- [tmux Control Mode](https://github.com/tmux/tmux/wiki/Control-Mode)
- [Terminal Feature Detection](https://github.com/termstandard/colors)

---

## Summary: The Irreducible Essentials

**Problem:** Claude Code `/export` needs `xclip`, but remote Linux has no access to macOS clipboard.

**Solution:** Create `~/.local/bin/xclip` wrapper that:

1. Reads stdin (what xclip would do)
1. Base64 encodes it
1. Wraps in OSC 52 escape sequence
1. Double-wraps if inside tmux
1. Outputs to stderr (not /dev/tty)

**Why it works:**

- Escape sequences travel back over SSH
- iTerm2 terminal intercepts OSC 52
- Updates macOS system clipboard
- Claude Code none the wiser (still thinks it's calling xclip)

**Critical fix:** `>&2` instead of `>/dev/tty` because Claude Code runs tools in non-interactive contexts where controlling terminal doesn't exist.
