# Team Setup Guide - Claude Code Workspace

## Quick Start (2 minutes)

### 1. Clone the Workspace

```bash
git clone <your-repo-url> ~/.claude
```

### 2. Install ALL Workspace Tools (Automated)

```bash
cd ~/.claude
./install-all-tools
```

**The installer will:**

- ✅ Install SAGE development tools (sage-dev, sage-sync, sage-status, gpu-ws)
- ✅ Install GFM link checker (gfm-check)
- ✅ Install CNS notification system (cns-notify)
- ✅ Configure your PATH automatically if needed
- ✅ **Backup existing files before overwriting (safety feature)**
- ✅ **Automatic rollback on installation failure**
- ✅ **Verify commands actually work (not just file existence)**
- ✅ Provide detailed explanations for each step
- ✅ Handle missing tools gracefully (skips unavailable tools)

### 3. Restart Your Shell (if needed)

```bash
# The installer will tell you if this is needed:
source ~/.zshrc  # for zsh users
source ~/.bashrc # for bash users
```

### 4. Test Installation

```bash
sage-dev --help
gfm-check --help
tmux-session --help
```

## What You Get

### Universal Commands (available from any directory):

#### SAGE Development Suite:

- **`sage-dev`** - SAGE development environment launcher
- **`sage-sync`** - Workspace/session sync tool
- **`sage-status`** - Infrastructure health monitoring
- **`gpu-ws`** - GPU workstation connection and management

#### Documentation & Quality Tools:

- **`gfm-check`** - GitHub Flavored Markdown link integrity checker

#### System & Productivity Tools:

- **`cns-notify`** - Audio notification system for Claude Code

### Example Usage:

```bash
# SAGE Development
sage-status                                    # Check infrastructure health
sage-dev docs                                  # Documentation work (local)
sage-dev tirex                                 # TiRex GPU development (remote)
sage-dev ensemble                              # Full SAGE integration (remote)
sage-sync --push-workspace --sync-sessions     # Sync between environments

# Documentation & Quality
gfm-check                                      # Check markdown links in current directory
gfm-check --fix                                # Auto-fix broken internal links
gfm-check /path/to/docs --no-external         # Check specific directory, skip external URLs

# System Tools
cns-notify                                     # Test audio notification
gpu-ws                                         # Connect to GPU workstation
```

## How It Works

### Hybrid Architecture:

- **Source files**: Organized in `~/.claude/tools/sage-aliases/`
- **Executables**: Globally accessible via `~/.local/bin/`
- **PATH**: Automatically configured by installer

### Benefits:

- ✅ **Universal Access**: Commands work from any directory
- ✅ **Industry Standard**: Uses `~/.local/bin` (same as pipx, uv, cargo)
- ✅ **Shell Agnostic**: Works in bash, zsh, fish
- ✅ **No Admin Rights**: User-owned installation
- ✅ **Team Consistent**: Same setup across all machines
- ✅ **Safe Installation**: Automatic backup/rollback prevents system corruption
- ✅ **Verified Functionality**: Tests commands actually work, not just file existence

## Troubleshooting

The installer handles most issues automatically, but if you encounter problems:

### Commands Not Found After Installation?

**First, try re-running the installer** - it includes diagnostics and safety features:

```bash
~/.claude/install-all-tools
```

The enhanced installer will:

- ✅ Check if files exist and are executable
- ✅ Verify PATH configuration
- ✅ **Test commands actually execute and work properly**
- ✅ **Automatically backup existing files before changes**
- ✅ **Roll back changes if installation fails**
- ✅ Provide specific fix instructions

### Manual Diagnostics (if installer doesn't help):

1. **Check PATH includes `~/.local/bin`:**

   ```bash
   echo $PATH | grep ".local/bin"
   ```

1. **Check files exist and are executable:**

   ```bash
   ls -la ~/.local/bin/sage-*
   ls -la ~/.local/bin/gpu-ws
   ```

1. **Test individual commands:**

   ```bash
   ~/.local/bin/sage-dev --help
   ~/.local/bin/sage-sync --help
   ```

### If All Else Fails

The installer provides a **manual installation section** with step-by-step instructions for cases where the automated process doesn't work.

## Manual Installation (if installer fails)

```bash
# Create directory
mkdir -p ~/.local/bin

# Copy executables
cp ~/.claude/tools/sage-aliases/bin/* ~/.local/bin/

# Make executable
chmod +x ~/.local/bin/sage-*
chmod +x ~/.local/bin/gpu-ws

# Add to PATH (if needed)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Development Notes

- **Source code**: All in `~/.claude/tools/sage-aliases/`
- **Updates**: `git pull` + re-run installer
- **Customization**: Edit files in `~/.claude/tools/sage-aliases/aliases/`
- **Documentation**: See `~/.claude/tools/sage-aliases/docs/README.md`
