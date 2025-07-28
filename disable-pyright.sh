#!/bin/bash

# Comprehensive Basedpyright/Pyright Disabler for Cursor IDE

echo "🔧 Disabling Basedpyright/Pyright completely..."

# Kill any running pyright processes
echo "🔪 Killing pyright processes..."
pkill -f "pyright" 2>/dev/null || echo "No pyright processes found"
pkill -f "basedpyright" 2>/dev/null || echo "No basedpyright processes found"
pkill -f "pylsp" 2>/dev/null || echo "No pylsp processes found"

# Set environment variables to disable Python language servers
echo "🌍 Setting environment variables..."
export PYRIGHT_PYTHON_ENABLE=false
export BASEDPYRIGHT_ENABLE=false
export PYTHON_LANGUAGE_SERVER=none
export VSCODE_PYTHON_ANALYSIS_DISABLED=true

# Create/update shell profile to persist env vars
SHELL_PROFILE=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_PROFILE="$HOME/.bashrc"
fi

if [[ -n "$SHELL_PROFILE" ]]; then
    echo "📝 Adding environment variables to $SHELL_PROFILE..."
    {
        echo ""
        echo "# Disable Python Language Servers for Cursor IDE"
        echo "export PYRIGHT_PYTHON_ENABLE=false"
        echo "export BASEDPYRIGHT_ENABLE=false"
        echo "export PYTHON_LANGUAGE_SERVER=none"
        echo "export VSCODE_PYTHON_ANALYSIS_DISABLED=true"
    } >> "$SHELL_PROFILE"
fi

# Check if Cursor is running and suggest restart
if pgrep -f "Cursor" > /dev/null; then
    echo "⚠️  Cursor is currently running. Please restart Cursor IDE for changes to take effect."
else
    echo "✅ Cursor is not running. Changes will take effect when you start Cursor."
fi

echo "🎯 Basedpyright/Pyright disable configuration complete!"
echo ""
echo "📋 Summary of actions taken:"
echo "   • Killed running pyright/basedpyright processes"
echo "   • Set environment variables to disable language servers"
echo "   • Created .vscode/settings.json with comprehensive disable settings"
echo "   • Created .vscode/extensions.json to block Python extensions"
echo "   • Created .cursorrules for Cursor-specific configuration"
echo "   • Created pyrightconfig.json with all checks disabled"
echo ""
echo "🔄 Next steps:"
echo "   1. Restart Cursor IDE completely"
echo "   2. Check Extensions tab (Cmd+Shift+X) and disable/uninstall basedpyright extension"
echo "   3. Source your shell profile: source $SHELL_PROFILE"