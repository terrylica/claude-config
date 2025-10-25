#!/bin/bash
# Cleanup Old State Files
#
# Purpose: Remove callback files older than retention period to prevent unbounded growth
# Usage: ./cleanup-old-state.sh [--dry-run]
# Cron: 0 2 * * * /Users/terryli/.claude/automation/lychee/bin/cleanup-old-state.sh

set -euo pipefail

# Configuration
STATE_DIR="$HOME/.claude/automation/lychee/state"
CALLBACK_DIR="$STATE_DIR/callbacks"
RETENTION_DAYS=30

# Parse arguments
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

# Validate directories exist
if [[ ! -d "$CALLBACK_DIR" ]]; then
    echo "❌ Callback directory not found: $CALLBACK_DIR"
    exit 1
fi

echo "🧹 Cleanup Old State Files"
echo "   Retention: ${RETENTION_DAYS} days"
echo "   Directory: $CALLBACK_DIR"
echo ""

# Find old callback files
OLD_FILES=$(find "$CALLBACK_DIR" -name "*.json" -type f -mtime +${RETENTION_DAYS} 2>/dev/null || true)
FILE_COUNT=$(echo "$OLD_FILES" | grep -v "^$" | wc -l | tr -d ' ')

if [[ "$FILE_COUNT" -eq 0 ]]; then
    echo "✓ No files older than ${RETENTION_DAYS} days"
    exit 0
fi

echo "📊 Found $FILE_COUNT files older than ${RETENTION_DAYS} days"
echo ""

# List files to be deleted
echo "Files to delete:"
echo "$OLD_FILES" | while read -r file; do
    if [[ -n "$file" ]]; then
        AGE_DAYS=$(( ($(date +%s) - $(stat -f %m "$file")) / 86400 ))
        SIZE=$(stat -f %z "$file")
        echo "   • $(basename "$file") (${AGE_DAYS}d old, ${SIZE}B)"
    fi
done
echo ""

# Calculate space to be freed
TOTAL_SIZE=$(echo "$OLD_FILES" | xargs stat -f %z 2>/dev/null | awk '{s+=$1} END {print s}')
TOTAL_KB=$((TOTAL_SIZE / 1024))

echo "💾 Space to free: ${TOTAL_KB}KB"
echo ""

if [[ "$DRY_RUN" == true ]]; then
    echo "🔍 DRY RUN - No files deleted"
    echo "   Run without --dry-run to delete files"
    exit 0
fi

# Delete files
DELETED=0
FAILED=0

echo "$OLD_FILES" | while read -r file; do
    if [[ -n "$file" ]]; then
        if rm "$file" 2>/dev/null; then
            ((DELETED++)) || true
        else
            ((FAILED++)) || true
            echo "   ⚠️  Failed to delete: $(basename "$file")"
        fi
    fi
done

echo "✅ Cleanup complete"
echo "   Deleted: $DELETED files"
if [[ "$FAILED" -gt 0 ]]; then
    echo "   Failed: $FAILED files"
fi
echo "   Freed: ${TOTAL_KB}KB"
