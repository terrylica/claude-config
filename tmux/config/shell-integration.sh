# Claude Code tmux Integration
# Source this file in your ~/.zshrc: source ~/.claude/tmux/config/shell-integration.sh

# Configuration
CLAUDE_TMUX_DIR="$HOME/.claude/tmux"

# ============================================================================
# MAIN CLAUDE FUNCTION WITH INTELLIGENT ROUTING
# ============================================================================

claude() {
    # Check if Claude Code is available
    if ! command -v claude &> /dev/null; then
        echo "❌ Claude Code not found. Please install Claude Code first." >&2
        echo "   Visit: https://claude.ai/claude-code" >&2
        return 1
    fi
    
    # Check if tmux is available
    if ! command -v tmux &> /dev/null; then
        echo "⚠️  tmux not found. Running Claude Code directly without persistence." >&2
        command claude "$@"
        return
    fi
    
    # Source the router and run it
    if [[ -f "$CLAUDE_TMUX_DIR/bin/claude-router.sh" ]]; then
        source "$CLAUDE_TMUX_DIR/bin/claude-router.sh"
        claude_router "$@"
    else
        echo "❌ Claude router not found. Running Claude Code directly." >&2
        command claude "$@"
    fi
}

# ============================================================================
# SESSION MANAGEMENT ALIAS
# ============================================================================

alias claude-session="$CLAUDE_TMUX_DIR/bin/session-manager.sh"

# ============================================================================
# UTILITY ALIASES
# ============================================================================

# Quick session operations
alias claude-sessions='claude-session list'
alias claude-status='claude-session status'

# ============================================================================
# COMPLETION AND HELPER FUNCTIONS
# ============================================================================

# Help function for discovering commands
claude-help() {
    echo "🎯 Claude Code tmux Integration"
    echo "==============================="
    echo ""
    echo "Main Usage:"
    echo "  claude [args...]           # Smart session management + Claude execution"
    echo ""
    echo "Session Management:"
    echo "  claude-session start <name>    # Create named session"
    echo "  claude-session list [--all]    # List sessions"
    echo "  claude-session attach <name>   # Attach to session"
    echo "  claude-session kill <name>     # Kill session"
    echo "  claude-session clean [days]    # Remove old sessions"
    echo "  claude-session status          # System status"
    echo ""
    echo "Quick Aliases:"
    echo "  claude-sessions            # List workspace sessions"
    echo "  claude-status              # Show system status"
    echo ""
    echo "Examples:"
    echo "  claude \"help me debug this\"         # Auto-managed session"
    echo "  claude-session start auth           # Create 'auth' session"
    echo "  claude --model gpt-4 \"help me\"     # All Claude flags work"
    echo "  claude --print \"quick question\"    # Non-interactive (no tmux)"
    echo ""
    echo "💡 The claude command intelligently routes based on usage patterns:"
    echo "   • Interactive queries → tmux persistence"
    echo "   • Non-interactive (--print) → direct execution"
    echo "   • Subcommands (config, mcp) → direct execution"
    echo "   • Session conflicts (--continue) → user prompt"
}

# ============================================================================
# WORKSPACE UTILITIES
# ============================================================================

# Quick workspace session info
claude-workspace() {
    local workspace_name=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g')
    local path_hash=$(echo "$(pwd)" | sha256sum | cut -c1-6)
    
    echo "📁 Current Workspace: $workspace_name"
    echo "🔍 Path Hash: $path_hash"
    echo "📂 Full Path: $(pwd)"
    echo ""
    
    # Show workspace sessions
    claude-session list
}

# ============================================================================
# MIGRATION AND COMPATIBILITY
# ============================================================================

# Function to help users migrate from old installations
claude-migrate() {
    echo "🔄 Claude tmux Integration Migration"
    echo "====================================="
    echo ""
    
    # Check for old installation
    if [[ -f "$HOME/.claude/tmux_claude_manager.sh" ]] || [[ -f "$HOME/.claude/tmux_aliases.sh" ]]; then
        echo "⚠️  Old installation detected!"
        echo ""
        echo "Old files found:"
        [[ -f "$HOME/.claude/tmux_claude_manager.sh" ]] && echo "  - $HOME/.claude/tmux_claude_manager.sh"
        [[ -f "$HOME/.claude/tmux_aliases.sh" ]] && echo "  - $HOME/.claude/tmux_aliases.sh"
        echo ""
        echo "These files are no longer used. You can safely remove them:"
        echo "  rm -f ~/.claude/tmux_claude_manager.sh"
        echo "  rm -f ~/.claude/tmux_aliases.sh"
        echo ""
    fi
    
    # Check shell configuration
    if grep -q "tmux_aliases\|tmux_claude_manager" ~/.zshrc 2>/dev/null; then
        echo "⚠️  Old shell configuration detected in ~/.zshrc"
        echo ""
        echo "Please remove old entries and add:"
        echo "  source ~/.claude/tmux/config/shell-integration.sh"
        echo ""
    fi
    
    echo "✅ Migration check complete"
}

# ============================================================================
# DEBUGGING AND DIAGNOSTICS
# ============================================================================

# Debug function for troubleshooting
claude-debug() {
    echo "🔍 Claude tmux Integration Debug Info"
    echo "====================================="
    echo ""
    
    # System info
    echo "📊 System Information:"
    echo "  OS: $(uname -s)"
    echo "  Shell: $SHELL"
    echo "  tmux: $(tmux -V 2>/dev/null || echo 'Not available')" 
    echo "  Claude Code: $(command -v claude &>/dev/null && echo 'Available' || echo 'Not found')"
    echo ""
    
    # Installation info
    echo "📁 Installation:"
    echo "  Base directory: $CLAUDE_TMUX_DIR"
    echo "  Router script: $([[ -f "$CLAUDE_TMUX_DIR/bin/claude-router.sh" ]] && echo '✅ Present' || echo '❌ Missing')"
    echo "  Session manager: $([[ -f "$CLAUDE_TMUX_DIR/bin/session-manager.sh" ]] && echo '✅ Present' || echo '❌ Missing')"
    echo "  Integration loaded: $([[ "$(type -t claude)" == "function" ]] && echo '✅ Yes' || echo '❌ No')"
    echo ""
    
    # Current workspace
    echo "📂 Current Workspace:"
    claude-workspace
    echo ""
    
    # Function definitions
    echo "🔧 Function Status:"
    echo "  claude function: $([[ "$(type -t claude)" == "function" ]] && echo '✅ Defined' || echo '❌ Not defined')"
    echo "  claude-session alias: $([[ -n "$(alias claude-session 2>/dev/null)" ]] && echo '✅ Defined' || echo '❌ Not defined')"
    echo ""
    
    # Test basic functionality
    echo "🧪 Basic Tests:"
    if command -v tmux &>/dev/null; then
        echo "  tmux connectivity: ✅ OK"
    else
        echo "  tmux connectivity: ❌ tmux not available"
    fi
    
    if [[ -f "$CLAUDE_TMUX_DIR/bin/claude-router.sh" ]]; then
        echo "  router script: ✅ OK"
    else
        echo "  router script: ❌ Missing"
    fi
}

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

# Export functions for use in subshells
export -f claude claude-help claude-workspace claude-migrate claude-debug

# ============================================================================
# INITIALIZATION
# ============================================================================

# Check for required components on load
if [[ ! -f "$CLAUDE_TMUX_DIR/bin/claude-router.sh" ]]; then
    echo "⚠️  Claude tmux integration not properly installed." >&2
    echo "   Missing: $CLAUDE_TMUX_DIR/bin/claude-router.sh" >&2
    echo "   Run the installer to fix this issue." >&2
fi

# Create data directories if they don't exist
mkdir -p "$CLAUDE_TMUX_DIR/data/workspace-sessions" 2>/dev/null || true