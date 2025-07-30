# Universal GFM Link Checker Access

## Zero-Impact Global Usage

Since every user has the standardized `$HOME/.claude/` directory structure, the GFM link checker is universally accessible without any system modifications.

## Usage from Any Workspace

Use the standard path from any directory:

```bash
# Check current directory
$HOME/.claude/tools/gfm-link-checker/bin/gfm-check

# Check specific directory  
$HOME/.claude/tools/gfm-link-checker/bin/gfm-check /path/to/other/workspace

# Check with options
$HOME/.claude/tools/gfm-link-checker/bin/gfm-check --no-completeness --verbose
```

## Benefits

- **Zero Configuration**: Works immediately on any system with `$HOME/.claude/` structure
- **Universal**: Same command works for all users across all computers
- **No Impact**: Requires no shell profile modifications or system changes
- **Portable**: Part of the Claude Code global configuration template

## Verification

Test from any directory:
```bash
cd /tmp
$HOME/.claude/tools/gfm-link-checker/bin/gfm-check --help
```

The tool preserves your current working directory and can validate any workspace.