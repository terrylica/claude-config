#!/bin/bash
# CNS Remote Alert Setup - macOS Local Machine
# Run this script on your LOCAL macOS machine

set -e

echo "🚀 CNS Remote Alert Setup - macOS Local Machine"
echo "=============================================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script must be run on macOS"
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p ~/.claude/tools
mkdir -p ~/.ssh/controlmasters

# Copy hub script from remote (you'll need to scp this from your Linux box)
echo "📋 Hub script location: ~/.claude/tools/cns-local-hub.py"
echo "   Copy from Linux: scp kab:~/.claude/tools/cns-local-hub.py ~/.claude/tools/"

# Install notification tools
echo "🔧 Checking notification tools..."
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew required. Install from: https://brew.sh"
    exit 1
fi

echo "Installing terminal-notifier and alerter..."
brew install terminal-notifier alerter

# Test SSH tunnel
echo "🔗 Testing SSH tunnel setup..."
echo "   Your SSH config should have the reverse tunnel configured for 'kab'"
echo "   To activate: ssh -f -N kab"
echo "   To check: ssh -O check kab"

# Create launch script
cat > ~/.claude/tools/start-cns-hub.sh << 'EOF'
#!/bin/bash
# Start CNS Local Hub
cd ~/.claude/tools
python3 cns-local-hub.py
EOF

chmod +x ~/.claude/tools/start-cns-hub.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy hub script: scp kab:~/.claude/tools/cns-local-hub.py ~/.claude/tools/"
echo "2. Start SSH tunnel: ssh -f -N kab"
echo "3. Start hub: ~/.claude/tools/start-cns-hub.sh"
echo "4. Test from remote: echo 'test' | nc localhost 4000"
echo ""
echo "🎯 The hub will listen on 127.0.0.1:5050 and display notifications!"