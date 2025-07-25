#!/bin/bash
# Setup script for GitHub Flavored Markdown Link Integrity Checker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "🔗 Setting up GitHub Flavored Markdown Link Integrity Checker..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is required but not found"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

cd "$PROJECT_DIR"

# Install dependencies using uv
echo "📦 Installing dependencies with uv..."
uv sync

# Create symlink for easier access (optional)
SYMLINK_PATH="/usr/local/bin/gfm-check"
if [[ -w "/usr/local/bin" ]]; then
    ln -sf "$PROJECT_DIR/bin/gfm-check" "$SYMLINK_PATH"
    echo "🔗 Created global command: gfm-check"
else
    echo "⚠️  Cannot create global command (no write access to /usr/local/bin)"
    echo "   You can use: $PROJECT_DIR/bin/gfm-check"
fi

echo "✅ Setup complete!"
echo ""
echo "Usage examples:"
echo "  # Local execution:"
echo "  $PROJECT_DIR/bin/gfm-check"
echo "  $PROJECT_DIR/bin/gfm-check /path/to/workspace --no-external"
echo "  $PROJECT_DIR/bin/gfm-check --format json --output report.json"
echo ""
echo "  # Global command (if symlink created):"
echo "  gfm-check"
echo "  gfm-check /path/to/workspace --no-external"
echo ""
echo "  # Direct uv execution:"
echo "  cd $PROJECT_DIR && uv run gfm_link_checker.py"