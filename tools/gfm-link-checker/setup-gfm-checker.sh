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

# Install dependencies using uv
echo "📦 Installing dependencies with uv..."
uv sync --directory "$PROJECT_DIR"

# Universal access approach - no system modifications needed
echo "🌍 Universal access configured using standardized Claude Code paths"
echo "   No system modifications required - works across all users"

echo "✅ Setup complete!"
echo ""
echo "Usage examples:"
echo "  # Global command access (available after copying to ~/.local/bin):"
echo "  gfm-check"
echo "  gfm-check /path/to/workspace --no-external"
echo "  gfm-check --format json --output report.json"
echo ""
echo "  # Direct uv execution:"
echo "  uv run --directory $PROJECT_DIR $PROJECT_DIR/gfm_link_checker.py"