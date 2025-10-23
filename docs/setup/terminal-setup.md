# Terminal Setup Guide

## Ghostty Terminal Emulator

### Session Management & Window Restoration

**Config**: `~/.config/ghostty/config`

```toml
# Session management (macOS only)
window-save-state = always
window-inherit-working-directory = true

# Tab bar style - native macOS tabs for drag-to-merge support
macos-titlebar-style = native

# Disable shell integration title to allow custom emoji titles
shell-integration-features = no-title
```

**Features**:

- `window-save-state = always` - Restores window position, size, tabs, and splits on restart
- `window-inherit-working-directory = true` - New tabs/splits inherit current directory
- `macos-titlebar-style = native` - Enables native macOS tab drag-to-merge (drag window onto another window)

**Merging Windows**: With native titlebar, drag a Ghostty window onto another window's titlebar to merge as tabs.

### Custom Emoji Tab Titles by Directory

**Zsh Config**: Add to `~/.zshrc`:

```zsh
# Disable Oh-My-Zsh auto-title to allow custom emoji titles
DISABLE_AUTO_TITLE="true"

# Dynamic tab title based on ~/eon/ subdirectory
eon_set_tab_title() {
  if [[ -n "$GHOSTTY_RESOURCES_DIR" ]]; then
    local title_prefix=""
    local dir_name=$(basename "$PWD")

    case "$PWD" in
      */eon/ml-feature-*)           title_prefix="🤖 ML" ;;
      */eon/evolutionary-forest*)   title_prefix="🧬 Research" ;;
      */eon/backtesting.py*)        title_prefix="📊 Backtest" ;;
      */eon/funding-rate-arbitrage*) title_prefix="💹 Arb" ;;
      */eon/AlphaForge*)            title_prefix="⚡ Alpha" ;;
      */eon/data-source-manager*)   title_prefix="💾 Data" ;;
      */eon/gapless-crypto-data*)   title_prefix="₿ Crypto" ;;
      */eon/experiment_*)           title_prefix="🧪 Exp" ;;
      */eon/helpers-worktree*)      title_prefix="🔧 Tools" ;;
      */eon/custom-logger*)         title_prefix="📝 Logger" ;;
      */eon/_Archived*)             title_prefix="📦 Archive" ;;
      */eon/*)                      title_prefix="⚙️" ;;
      */dental-career-opportunities*) title_prefix="🦷 Dental" ;;
      *)                            title_prefix="" ;;
    esac

    if [[ -n "$title_prefix" ]]; then
      printf '\033]0;%s %s\007' "$title_prefix" "$dir_name"
    else
      printf '\033]0;%s\007' "$dir_name"
    fi
  fi
}

# Hook to update tab title on directory change
add-zsh-hook precmd eon_set_tab_title
```

**Result**: Tab titles show emoji prefixes based on directory (e.g., "🧪 Exp experiment_01", "🦷 Dental dental-career-opportunities").

### Claude Code Terminal Title Integration

**Problem**: Claude Code CLI continuously updates terminal title during streaming, overwriting custom emoji titles.

**Solution**: Disable Claude Code title updates via environment variables.

**Config**: `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_DISABLE_TERMINAL_TITLE": "1",
    "CLAUDE_DISABLE_TITLE_UPDATES": "1"
  }
}
```

**Result**: Claude Code respects custom emoji titles and doesn't override them during operation.

### Remote SSH Focus Tracking Issue

**Problem**: `[O[I[O[I` escape sequences appearing in input when clicking outside terminal during SSH sessions.

**Root Cause**: Terminal focus event tracking mode (DECSET 1004) enabled by shell configuration (Oh My Zsh, zsh-autosuggestions, or tmux).

**Solution**: Disable focus events in shell initialization.

#### Fix for zsh (with Powerlevel10k)

Add to `~/.zshrc` after instant prompt section:

```zsh
# Disable focus tracking (prevents [O[I escape sequences in Ghostty)
printf '\033[?1004l' >/dev/null 2>&1
```

**Placement**: Must be after Powerlevel10k instant prompt block (after line ~6) to avoid console output warnings.

#### Fix for tmux

Add to `~/.tmux.conf`:

```tmux
# Disable focus events
set -g focus-events off
```

Apply: `tmux source-file ~/.tmux.conf`

### Terminfo Installation for Remote Systems

Ghostty uses `TERM=xterm-ghostty`. Install terminfo on remote servers:

```bash
# On local machine (with Ghostty)
infocmp xterm-ghostty > /tmp/xterm-ghostty.ti
scp /tmp/xterm-ghostty.ti remote-host:/tmp/

# On remote machine
tic -x /tmp/xterm-ghostty.ti  # Installs to ~/.terminfo/
rm /tmp/xterm-ghostty.ti
```

#### Enable TERM Forwarding

**Local** `~/.ssh/config`:

```ssh
Host remote-host
    SendEnv TERM
```

**Remote** `/etc/ssh/sshd_config` (requires sudo):

```
AcceptEnv TERM
```

Restart sshd: `sudo systemctl restart sshd`

### Dark Theme Syntax Highlighting

For zsh-syntax-highlighting on dark backgrounds, add to `~/.zshrc`:

```zsh
# Fix comment visibility on dark backgrounds
ZSH_HIGHLIGHT_STYLES[comment]='fg=244,italic'  # Gray
ZSH_HIGHLIGHT_STYLES[alias]='fg=cyan,bold'
ZSH_HIGHLIGHT_STYLES[builtin]='fg=cyan'
ZSH_HIGHLIGHT_STYLES[command]='fg=green'
```

### SSH Clipboard Integration (OSC 52)

Enable Claude Code `/export` to copy to macOS clipboard over SSH:

**See**: [ssh-clipboard-osc52.md](ssh-clipboard-osc52.md) for complete setup

**Quick setup**:

1. Local Ghostty: Add `clipboard-write = allow` to `~/.config/ghostty/config`
2. Remote Linux: Install xclip wrapper to `~/.local/bin/xclip`

The wrapper emits OSC 52 escape sequences that travel over SSH and are interpreted by Ghostty to update the macOS system clipboard.

## Kitty Terminal Emulator

### Helix Markdown Formatter (Prettier) PATH Issue

**Problem**: Prettier formatter fails in Helix when Kitty is launched from Finder/GUI (markdown files opened by double-click). Error: `A formatter isn't available` or `env: node: No such file or directory`.

**Root Cause**: macOS GUI apps inherit limited PATH (`/usr/bin:/bin:/usr/sbin:/sbin`), excluding Homebrew and user-installed tools. Prettier requires `node` in PATH.

**Solution**: Export PATH in Kitty's configuration.

#### Required Setup

**1. Install Prettier globally**:

```bash
npm install -g prettier@latest
```

**2. Create system symlinks** (ensures tools available regardless of shell config):

```bash
sudo ln -sf ~/.nvm/versions/node/v22.17.0/bin/node /usr/local/bin/node
sudo ln -sf ~/.nvm/versions/node/v22.17.0/bin/prettier /usr/local/bin/prettier
```

**3. Configure Kitty PATH** (`~/.config/kitty/kitty.conf`):

Add in the `env` section (~line 1658):

```toml
# Add /usr/local/bin to PATH for tools like prettier and node
env PATH=/usr/local/bin:/opt/homebrew/bin:${PATH}
```

**4. Configure Helix formatter** (`~/.config/helix/languages.toml`):

```toml
[[language]]
name = "markdown"
formatter = { command = 'prettier', args = ["--parser", "markdown"] }
auto-format = true
```

**5. Restart Kitty** (Cmd+Q, reopen) - config changes only apply to new instances.

#### What DOESN'T Work

❌ **Kitty as file handler for `public.data` files** - Kitty's Info.plist claims `public.data` but cannot handle `file://` URLs from macOS Launch Services
❌ **Absolute paths in Helix config** - Helix caches config; symlinks + PATH export more reliable
❌ **Shell rc file PATH exports** - Not loaded for GUI-launched apps

#### Verification

```bash
# In Helix opened via Kitty
:fmt

# Should format markdown tables without errors
```

```bash
# Check Helix health
hx --health markdown
# Should show: ✓ prettier
```

### File Associations

For markdown files opened via double-click to use Kitty+Helix:

```bash
# Set Kitty as default for markdown
duti -s net.kovidgoyal.kitty .md all
duti -s net.kovidgoyal.kitty net.daringfireball.markdown all

# For .txt files
duti -s net.kovidgoyal.kitty .txt all
```

**Note**: Requires Kitty configured to open Helix by default. Set `$EDITOR` environment variable in shell config.

## Troubleshooting

### Check Current Focus Tracking State

```bash
# This command should produce no output if disabled
printf '\033[?1004l'
```

### Reset Terminal State

```bash
reset  # Full terminal reset
```

### Verify No Console Output During Shell Init

Exit and reconnect - you should see no Powerlevel10k warnings about console output.
