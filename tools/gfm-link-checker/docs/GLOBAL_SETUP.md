# Universal GFM Link Checker Access

## Global Command Access

The GFM link checker is installed to `~/.local/bin` for universal, robust access across all shells and environments.

## Usage from Any Workspace

Use the global command from any directory:

```bash
# Check current directory
gfm-check

# Check specific directory  
gfm-check /path/to/other/workspace

# Check with options
gfm-check --no-completeness --verbose
```

## Benefits

- **Industry Standard**: Uses standard `~/.local/bin` location
- **Universal Access**: Works in any shell (bash, zsh, fish)
- **Script-Ready**: Works in automation, cron jobs, SSH sessions
- **No Sudo Required**: User-owned installation
- **Cross-Platform**: Same pattern on macOS and Linux

## Verification

Test from any directory:
```bash
cd /tmp
gfm-check --help
```

The tool preserves your current working directory and can validate any workspace.