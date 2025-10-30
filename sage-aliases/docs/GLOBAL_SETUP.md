# SAGE Aliases Tool - Global Setup

**Tool**: SAGE development aliases and productivity commands\
**Location**: `~/.claude/tools/sage-aliases/`\
**Access**: Global commands via `~/.local/bin` (industry standard)

## Installation Status

✅ **Tool Structure**: Complete directory organization\
✅ **Universal Commands**: `gpu`, `sage-dev`, `sage-status` executables\
✅ **Alias Categories**: 4 organized alias files\
✅ **Documentation**: Complete usage guide

## Universal Access Commands

### Available Globally (via ~/.local/bin)

```bash
gpu-ws           # GPU workstation connection and management
sage-dev         # SAGE development environment launcher
sage-status      # Infrastructure health monitoring
sage-sync        # Comprehensive sync tool for dual environments
```

### Command Examples

```bash
# Test GPU workstation connectivity
gpu-ws

# Start SAGE ensemble development
sage-dev ensemble

# Check complete infrastructure health
sage-status

# Sync sessions and workspace
sage-sync --sync-sessions
```

## Shell Integration Options

### Option 1: Universal Commands Only (Recommended)

Use the universal commands without sourcing aliases:

- Minimal shell impact
- Clean command interface
- Preserves working directory

### Option 2: Full Alias Integration

Source specific alias categories as needed:

```bash
# Add to ~/.zshrc or ~/.bashrc if desired
source ~/.claude/tools/sage-aliases/aliases/gpu-workstation.sh
source ~/.claude/tools/sage-aliases/aliases/sage-development.sh
```

## Architecture Benefits

### Universal Access Pattern

- **Industry Standard**: Uses `~/.local/bin` location (same as pipx, uv, etc.)
- **Cross-Platform**: Same pattern on macOS and Linux environments
- **Shell Agnostic**: Works in bash, zsh, fish, and any POSIX shell
- **Automation Ready**: Works in scripts, cron jobs, SSH sessions
- **No Sudo Required**: User-owned installation and updates

### Organized Structure

- **Modular Design**: Separate concerns (GPU, SAGE, sync, network)
- **Universal Commands**: High-level interface via `bin/` executables
- **Detailed Aliases**: Category-specific aliases for power users
- **Complete Documentation**: Usage guides and examples

## Migration from Loose Files

### Files Relocated

- `~/.claude/gpu-workstation-aliases.sh` → `sage-aliases/aliases/gpu-workstation.sh`
- Created organized structure with universal access
- Added comprehensive command interface

### Shell Configuration Update

The old shell configuration referencing loose files can be:

1. **Removed** (use universal commands only)
1. **Updated** to reference new organized structure
1. **Kept minimal** with selective sourcing

## Usage Verification

### Test Universal Commands

```bash
# Should work immediately (via PATH)
gpu help
sage-dev help
sage-status help
```

### Test Infrastructure

```bash
# Complete infrastructure check
sage-status

# GPU connectivity test
gpu check

# SAGE models availability
sage-dev status
```

## Troubleshooting

### If Commands Not Found

Check PATH includes `~/.local/bin`:

```bash
echo $PATH | grep ".local/bin"
```

If not found, add to your shell config:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### If Aliases Not Working

Source specific alias files:

```bash
source ~/.claude/tools/sage-aliases/aliases/gpu-workstation.sh
```

## Next Steps

1. **Test universal commands**: Verify `gpu`, `sage-dev`, `sage-status` work
1. **Clean old references**: Remove loose file sources from shell config
1. **Use in development**: Integrate commands into daily SAGE workflow
1. **Extend as needed**: Add new commands to `bin/` directory

**Status**: Production ready with universal access following `.claude/tools` convention
