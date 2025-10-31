# Terminal Setup Guide

## iTerm2 Terminal Emulator

### Session Management & Window Restoration

**Preferences**: iTerm2 → Preferences → General → Startup

```
✓ Use System Window Restoration Setting
✓ Restore only hotkey window after restart
```

**Features**:

- Native macOS window state restoration - Restores window position, size, tabs, and splits
- "Restore only hotkey window after restart" - Only restores specific windows you've configured
- Full session restoration via iTerm2 sessions (saved manually or automatically)

**Saving Sessions**:

- Window → Save Window Arrangement (Cmd+Shift+S)
- Window → Restore Window Arrangement

### Custom Emoji Tab Titles by Directory

**Zsh Config**: Already configured in `~/.zshrc`:

```zsh
# Disable Oh-My-Zsh auto-title to allow custom emoji titles
DISABLE_AUTO_TITLE="true"

# Dynamic tab title based on ~/eon/ subdirectory
eon_set_tab_title() {
  if [[ "$TERM_PROGRAM" == "iTerm.app" ]]; then
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

### Split Panes

**Native Split Commands**:

- Cmd+D - Split vertically
- Cmd+Shift+D - Split horizontally
- Cmd+Option+Arrow - Navigate between splits
- Cmd+W - Close current split/pane

**Advanced Split Configuration**:

- Preferences → Keys → Key Bindings
- Customize split navigation and creation keybindings

### Remote SSH Focus Tracking Issue

**Problem**: `[O[I[O[I` escape sequences appearing in input when clicking outside terminal during SSH sessions.

**Root Cause**: Terminal focus event tracking mode (DECSET 1004) enabled by shell configuration (Oh My Zsh, zsh-autosuggestions).

**Solution**: Disable focus events in shell initialization.

#### Fix for zsh (with Powerlevel10k)

Add to `~/.zshrc` after instant prompt section:

```zsh
# Disable focus tracking (prevents [O[I escape sequences)
printf '\033[?1004l' >/dev/null 2>&1
```

**Placement**: Must be after Powerlevel10k instant prompt block (after line ~6) to avoid console output warnings.

### SSH Clipboard Integration (OSC 52)

Enable Claude Code `/export` to copy to macOS clipboard over SSH:

**See**: [ssh-clipboard-osc52.md](ssh-clipboard-osc52.md) for complete setup

**Quick setup**:

1. **iTerm2**: Preferences → General → Selection → ✓ Applications in terminal may access clipboard
2. **Remote Linux**: Install xclip wrapper to `~/.local/bin/xclip`

The wrapper emits OSC 52 escape sequences that travel over SSH and are interpreted by iTerm2 to update the macOS system clipboard.

### Theme & Appearance

**Recommended Settings**:

- Preferences → Profiles → Colors → Color Presets → Import → Choose a theme
- Popular themes: Dracula, Nord, Tokyo Night, Solarized Dark
- Preferences → Appearance → Theme → Minimal (for clean UI)

**Font Configuration**:

- Preferences → Profiles → Text → Font
- Recommended: JetBrains Mono, Fira Code, SF Mono
- Enable ligatures if using Fira Code

### iTerm2-Specific Features

**Smart Selection**:

- Cmd+Click to open URLs
- Double-click to select words
- Triple-click to select lines

**Instant Replay**:

- Cmd+Option+B - View terminal scrollback history with timeline

**Shell Integration**:

- iTerm2 → Install Shell Integration
- Provides command history navigation, status indicators, and more

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
