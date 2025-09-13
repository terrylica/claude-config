#!/bin/bash
# Deploy CNS Remote Integration
# Safely replaces CNS hook with remote-aware version

set -e

echo "🚀 Deploying CNS Remote Integration"
echo "=================================="

# Backup original hook
ORIGINAL_HOOK="$HOME/.claude/automation/cns/cns_hook_entry.sh"
BACKUP_HOOK="$HOME/.claude/automation/cns/cns_hook_entry.sh.backup"
REMOTE_HOOK="$HOME/.claude/tools/cns_hook_entry_remote.sh"

if [[ -f "$ORIGINAL_HOOK" && ! -f "$BACKUP_HOOK" ]]; then
    echo "📋 Backing up original hook..."
    cp "$ORIGINAL_HOOK" "$BACKUP_HOOK"
    echo "   Backup created: $BACKUP_HOOK"
fi

# Install remote-aware hook
if [[ -f "$REMOTE_HOOK" ]]; then
    echo "🔄 Installing remote-aware hook..."
    cp "$REMOTE_HOOK" "$ORIGINAL_HOOK"
    chmod +x "$ORIGINAL_HOOK"
    echo "   ✅ Remote-aware hook installed"
else
    echo "❌ Remote-aware hook not found: $REMOTE_HOOK"
    exit 1
fi

# Test remote client
echo "🧪 Testing remote client..."
if "$HOME/.claude/tools/cns-remote-client.sh" --test; then
    echo "   ✅ Remote client test successful"
else
    echo "   ⚠️  Remote client test failed (expected if tunnel not active)"
fi

echo ""
echo "✅ CNS Remote Integration deployed!"
echo ""
echo "Next steps:"
echo "1. On macOS: Run ~/.claude/tools/macos-setup.sh"
echo "2. On macOS: Start SSH tunnel with 'ssh -f -N kab'"  
echo "3. On macOS: Start hub with ~/.claude/tools/start-cns-hub.sh"
echo "4. Test: Use Claude Code and check for notifications on macOS"
echo ""
echo "To rollback: cp $BACKUP_HOOK $ORIGINAL_HOOK"