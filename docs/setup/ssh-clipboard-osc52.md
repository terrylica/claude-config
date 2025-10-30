# SSH Clipboard Integration via OSC 52

## Overview

Enable Claude Code CLI `/export` command to copy to macOS clipboard when SSH'd into remote Linux box, even inside tmux.

## Architecture

```
macOS (Ghostty) → SSH → Linux (tmux) → Claude Code → xclip wrapper → OSC 52 → macOS clipboard
```

## Prerequisites

- **Local**: Ghostty terminal with OSC 52 enabled
- **Remote**: Linux box with `~/.local/bin` in PATH

## Setup

### 1. Local: Enable Ghostty Clipboard Support

**File**: `~/.config/ghostty/config` (on macOS)

```
clipboard-read = allow
clipboard-write = allow
```

### 2. Remote: Install xclip Wrapper

**File**: `~/.local/bin/xclip`

```bash
#!/bin/bash
# xclip wrapper for Claude Code that uses OSC 52 over SSH

osc52_copy() {
  local input
  if [ -t 0 ]; then
    input="$*"
  else
    input=$(cat)
  fi

  local encoded=$(printf %s "$input" | base64 | tr -d '\n')

  if [ -n "$TMUX" ]; then
    printf "\033Ptmux;\033\033]52;c;%s\007\033\\" "$encoded" >&2
  else
    printf "\033]52;c;%s\007" "$encoded" >&2
  fi
}

# Parse xclip arguments (basic compatibility)
selection="clipboard"
in_mode=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -selection|-sel)
      selection="$2"
      shift 2
      ;;
    -i|-in)
      in_mode=true
      shift
      ;;
    -o|-out)
      echo "xclip -o (paste) not supported via OSC 52" >&2
      exit 1
      ;;
    *)
      shift
      ;;
  esac
done

osc52_copy
```

Make executable:

```bash
chmod +x ~/.local/bin/xclip
```

### 3. Remote: Optional Shell Integration

Add to `~/.zshrc` for direct use outside Claude Code:

```zsh
# OSC 52 clipboard support for SSH (works with Ghostty on macOS)
osc52-copy() {
  local input
  if [ -t 0 ]; then
    input="$*"
  else
    input=$(cat)
  fi

  local encoded=$(printf %s "$input" | base64 | tr -d '\n')

  if [ -n "$TMUX" ]; then
    printf "\033Ptmux;\033\033]52;c;%s\007\033\\" "$encoded" >&2
  else
    printf "\033]52;c;%s\007" "$encoded" >&2
  fi
}

# Create pbcopy alias for macOS-style usage
alias pbcopy='osc52-copy'
```

Reload: `exec zsh` or `source ~/.zshrc`

## Usage

### In Claude Code

```
> /export
  ⎿  Conversation copied to clipboard
```

Now paste on macOS: `⌘V`

### Command Line

```bash
# Via xclip
echo "test" | xclip -selection clipboard

# Via pbcopy alias
echo "test" | pbcopy

# Via function
osc52-copy "direct text"
```

## Testing

### Test 1: Basic OSC 52 (outside tmux)

```bash
printf '\033]52;c;%s\a' "$(echo -n 'OSC52 works!' | base64)"
# Paste on macOS to verify
```

### Test 2: Inside tmux

```bash
tmux new -s test
printf '\033Ptmux;\033\033]52;c;%s\a\033\\' "$(echo -n 'tmux OSC52 works!' | base64)"
# Paste on macOS to verify
```

### Test 3: Via wrapper

```bash
echo "xclip wrapper works!" | xclip -selection clipboard
# Paste on macOS to verify
```

### Test 4: Claude Code

```bash
claude
> /export
# Paste to verify entire conversation copied
```

## Troubleshooting

### `/export` still fails

1. Check xclip is in PATH: `which xclip` (should show `~/.local/bin/xclip`)
2. Verify wrapper is executable: `ls -la ~/.local/bin/xclip`
3. Test manually: `echo "test" | xclip -selection clipboard`

### Nothing appears in clipboard

1. Verify Ghostty config has `clipboard-write = allow`
2. Test raw OSC 52 outside Claude Code
3. Check terminal supports OSC 52: [Terminal.Sexy](https://terminal.sexy/)

### Works outside tmux, fails inside

1. Verify `$TMUX` environment variable is set: `echo $TMUX`
2. Test tmux-wrapped sequence manually
3. Check tmux version: `tmux -V` (≥3.2 recommended)

### "No such device or address" error

Wrapper is trying to write to `/dev/tty` instead of `>&2`. Verify wrapper uses `>&2`.

## Technical Details

### Why `>&2` not `/dev/tty`?

**Problem**: `/dev/tty` doesn't exist in non-interactive contexts (like Claude Code tool execution)

**Solution**: Write to stderr (`>&2`), which:

- Always available in subprocesses
- Terminal emulators read from both stdout/stderr for control sequences
- Escape sequences are invisible to user (don't appear in output)

### OSC 52 Format

```
\033]52;c;<base64_data>\007
```

- `\033]52` = OSC 52 sequence start
- `c` = clipboard target (vs `p` for primary selection)
- Base64-encoded payload (no newlines)
- `\007` = BEL terminator (or `\033\\` for ST)

### tmux Passthrough Format

```
\033Ptmux;\033\033]52;c;<base64_data>\007\033\\
```

- `\033Ptmux;` = DCS start for tmux
- `\033\033` = Doubled escape so tmux passes through
- `\033\\` = ST terminator for DCS

### Security Considerations

**Safe**:

- OSC 52 only transfers clipboard data
- No display server access (unlike X11 forwarding)
- Terminal config controls acceptance (`clipboard-write = allow`)

**Risks**:

- Malicious script could exfiltrate data to clipboard
- User might unknowingly paste compromised content
- **Mitigation**: Only use on trusted servers

## Terminal Compatibility

| Terminal | Support | Notes |
| --- | --- | --- |
| Ghostty | ✅ Native | Requires config |
| iTerm2 | ✅ Native | v3.4.0+ |
| WezTerm | ✅ Native | Default enabled |
| Kitty | ✅ Native | Default enabled |
| Alacritty | ⚠️ Partial | Requires `osc52` feature |
| tmux | ✅ Passthrough | Requires wrapping |
| Terminal.app | ❌ None | No OSC 52 support |

## References

### Internal Documentation

- [OSC 52 Deep Dive](osc52-deep-dive.md) - Complete technical analysis, protocol details, architecture
- [Implementation Summary](osc52-implementation-summary.md) - What we built, why it works, key discoveries
- [Implementation Checklist](osc52-implementation-checklist.md) - Verification, testing, quick reference

### External Resources

- [OSC 52 Specification](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h3-Operating-System-Commands)
- [Ghostty Config Reference](https://ghostty.org/docs/config/reference)
- [tmux Control Mode](https://github.com/tmux/tmux/wiki/Control-Mode)
