#!/usr/bin/env bash
# Setup script for MQL5 Article Extraction System
# Creates persistent virtual environment with uv

set -e

echo "🚀 Setting up MQL5 Article Extraction System..."
echo

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ Found uv $(uv --version)"
echo

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo

# Install dependencies
echo "📦 Installing dependencies..."
uv pip install --python .venv/bin/python -r requirements.txt
echo "✅ Dependencies installed"
echo

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
.venv/bin/python -m playwright install chromium
echo "✅ Playwright browsers installed"
echo

# Verify installation
echo "🔍 Verifying installation..."
if .venv/bin/python mql5_extract.py --help > /dev/null 2>&1; then
    echo "✅ Installation verified successfully"
else
    echo "❌ Verification failed"
    exit 1
fi
echo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "📚 Usage:"
echo
echo "   # Activate virtual environment"
echo "   source .venv/bin/activate"
echo
echo "   # Or run directly with full path"
echo "   .venv/bin/python mql5_extract.py discover-and-extract"
echo
echo "   # Extract single article"
echo "   .venv/bin/python mql5_extract.py single <URL>"
echo
echo "   # Batch extraction"
echo "   .venv/bin/python mql5_extract.py batch urls.txt"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
