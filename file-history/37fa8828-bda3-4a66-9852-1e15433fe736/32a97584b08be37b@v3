#!/bin/bash
# Setup Pushover on remote SSH server for CNS notifications
# Run this on your LOCAL macOS, it will configure the REMOTE server

set -euo pipefail

REMOTE_HOST="${1:-ssh-yca}"

echo "🔧 Setting up Pushover on remote: $REMOTE_HOST"

# Get credentials from local macOS keychain
echo "📥 Retrieving Pushover credentials from local keychain..."
USER_KEY=$(security find-generic-password -s "pushover-user-key" -a "terryli" -w 2>/dev/null)
APP_TOKEN=$(security find-generic-password -s "pushover-app-token" -a "terryli" -w 2>/dev/null)

if [[ -z "$USER_KEY" ]]; then
    echo "❌ User key not found in keychain"
    echo "Run: pushover-setup first"
    exit 1
fi

if [[ -z "$APP_TOKEN" ]]; then
    echo "❌ Application token not found in keychain"
    echo "Run: pushover-setup <your-app-token>"
    exit 1
fi

# Create config on remote server
echo "📤 Installing Pushover config on $REMOTE_HOST..."
ssh "$REMOTE_HOST" "cat > ~/.pushover_config" << EOF
PUSHOVER_USER="$USER_KEY"
PUSHOVER_TOKEN="$APP_TOKEN"
EOF

ssh "$REMOTE_HOST" "chmod 600 ~/.pushover_config"

# Verify installation
echo "✅ Testing remote Pushover notification..."
ssh "$REMOTE_HOST" "~/.claude/tools/cns-remote-client.sh --test"

echo ""
echo "✅ Setup complete!"
echo "CNS notifications from $REMOTE_HOST will now use Pushover"
echo ""
echo "Test from remote:"
echo "  ssh $REMOTE_HOST '~/.claude/tools/cns-remote-client.sh --test'"
