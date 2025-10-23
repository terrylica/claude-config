#!/usr/bin/env bash
# Prettier Markdown Formatting Stop Hook
# Formats all .md files in workspace when Claude stops responding
# Uses fire-and-forget pattern for async execution (< 10ms exit)

set -euo pipefail

# Get workspace directory from Claude Code environment
workspace_dir="${CLAUDE_WORKSPACE_DIR:-$(pwd)}"

# Fire-and-forget async formatting - exit immediately
{
    # Find all .md files, excluding common ignore patterns
    find "$workspace_dir" -type f -name "*.md" \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -not -path "*/file-history/*" \
        -not -path "*/plugins/*" \
        -exec /Users/terryli/.nvm/versions/node/v22.17.0/bin/prettier \
            --write \
            --prose-wrap preserve \
            --config "$HOME/.claude/.prettierrc" \
            {} + > /dev/null 2>&1
} &

# Exit immediately - don't wait for background process
exit 0
