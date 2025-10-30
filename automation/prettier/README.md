# Prettier Markdown Formatting Stop Hook

**Purpose**: Automatically format all markdown files in workspace when Claude Code CLI stops responding

**Status**: ✅ Active (October 2025)

______________________________________________________________________

## How It Works

1. **Trigger**: Claude Code invokes Stop hooks after main agent finishes responding
1. **Execution**: Script spawns background Prettier process with `{ work } &` pattern
1. **Exit**: Script exits immediately (< 10ms) - no user-visible delay
1. **Formatting**: Background process formats all .md files in workspace
1. **Result**: Files are formatted and ready for next git commit

______________________________________________________________________

## Architecture

### Fire-and-Forget Pattern

```bash
# Critical: Exit immediately, don't wait for formatting
{
    find "$workspace_dir" -type f -name "*.md" \
        -not -path "*/node_modules/*" \
        -exec prettier --write {} + > /dev/null 2>&1
} &

exit 0  # Immediate exit
```

### Integration with Claude Code

```json
// settings.json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/automation/cns/cns_hook_entry.sh"
          },
          {
            "type": "command",
            "command": "$HOME/.claude/automation/prettier/format-markdown.sh"
          }
        ]
      }
    ]
  }
}
```

**Hook Order**:

1. CNS notification hook (sends notification)
1. Prettier formatting hook (formats markdown)

Both execute asynchronously - neither blocks Claude Code.

______________________________________________________________________

## Configuration

### Prettier Settings (.prettierrc)

```json
{
  "proseWrap": "preserve",
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

**Key Setting**: `proseWrap: "preserve"` - Maintains line breaks for GitHub/BitBucket compatibility

### Excluded Patterns

- `**/node_modules/**` - Dependencies
- `**/.git/**` - Git internals
- `**/file-history/**` - Claude Code history
- `**/plugins/**` - Plugin files

______________________________________________________________________

## Testing

### Manual Test

```bash
# Test hook execution time
time ~/.claude/automation/prettier/format-markdown.sh

# Should show:
# - 0.00s user time (script exits immediately)
# - Background process formats files
```

### Integration Test

```bash
# 1. Create badly formatted test file
echo "# Test\n\nBadly    formatted    text" > /tmp/test.md

# 2. Run Claude Code in workspace
cd /tmp
claude

# 3. After Claude stops, check formatting
cat test.md
# Should show properly formatted markdown
```

______________________________________________________________________

## Troubleshooting

### Hook Not Running

**Symptoms**: Files not formatted after Claude stops

**Checks**:

```bash
# Verify hook in settings
jq '.hooks.Stop' ~/.claude/settings.json

# Check script executable
ls -l ~/.claude/automation/prettier/format-markdown.sh

# Test manually
~/.claude/automation/prettier/format-markdown.sh
```

### Slow Execution

**Symptoms**: Delay after Claude stops

**Checks**:

```bash
# Measure exit time
time ~/.claude/automation/prettier/format-markdown.sh

# Should complete in < 10ms (script exit, not formatting)
```

### Formatting Errors

**Symptoms**: Files not formatted correctly

**Checks**:

```bash
# Verify config exists
cat ~/.claude/.prettierrc

# Test Prettier manually
prettier --write --prose-wrap preserve README.md
```

______________________________________________________________________

## Related Specifications

- [prettier-markdown-formatting.yaml](/Users/terryli/.claude/specifications/prettier-markdown-formatting.yaml) - Complete technical specification
- [cns-conversation-notification-system.yaml](/Users/terryli/.claude/specifications/cns-conversation-notification-system.yaml) - CNS stop hook (same pattern)

______________________________________________________________________

## Version History

- **1.0.0** (2025-10-22): Initial implementation with fire-and-forget async pattern
