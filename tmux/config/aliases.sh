# Claude Code tmux Integration Aliases
# Source this file in your ~/.zshrc: source ~/.claude/tmux/config/aliases.sh

# Path to tmux manager script
CLAUDE_TMUX_MANAGER="$HOME/.claude/tmux/bin/tmux_claude_manager.sh"

# Core Claude session management
alias claude-start="$CLAUDE_TMUX_MANAGER start"
alias claude-new="$CLAUDE_TMUX_MANAGER start"
alias claude-list="$CLAUDE_TMUX_MANAGER list"
alias claude-ls="$CLAUDE_TMUX_MANAGER list"
alias claude-resume="$CLAUDE_TMUX_MANAGER select"
alias claude-select="$CLAUDE_TMUX_MANAGER select"
alias claude-attach="$CLAUDE_TMUX_MANAGER select"

# Session maintenance
alias claude-cleanup="$CLAUDE_TMUX_MANAGER cleanup"
alias claude-kill="$CLAUDE_TMUX_MANAGER kill"

# Quick tmux operations
alias tmux-kill-all='tmux list-sessions | grep claude- | cut -d: -f1 | xargs -I {} tmux kill-session -t {}'
alias tmux-detach='tmux detach'

# Enhanced session info
alias claude-sessions="$CLAUDE_TMUX_MANAGER list"
alias claude-status="$HOME/.claude/tmux/bin/tmux_status.sh"

# Workspace-aware shortcuts
claude-here() {
    echo "🚀 Starting Claude in $(pwd)"
    "$CLAUDE_TMUX_MANAGER" start
}

claude-quick() {
    # Quick resume of most recent session or create new
    local latest_session
    latest_session=$(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "claude-" | tail -1)
    
    if [[ -n "$latest_session" ]]; then
        echo "🔗 Resuming latest session: $latest_session"
        tmux attach-session -t "$latest_session"
    else
        echo "🚀 No sessions found, starting new one"
        "$CLAUDE_TMUX_MANAGER" start
    fi
}

# tmux key bindings helper
claude-keys() {
    echo "🔑 Essential tmux Key Bindings:"
    echo "==============================="
    echo "Ctrl+b d     Detach from session"
    echo "Ctrl+b c     Create new window"
    echo "Ctrl+b n     Next window"
    echo "Ctrl+b p     Previous window"
    echo "Ctrl+b %     Split pane vertically"
    echo "Ctrl+b \"     Split pane horizontally"
    echo "Ctrl+b arrow Navigate panes"
    echo "Ctrl+b x     Kill current pane"
    echo "Ctrl+b &     Kill current window"
    echo "Ctrl+b s     Session selector"
    echo "Ctrl+b w     Window selector"
    echo ""
    echo "💡 Use 'claude-resume' for smart session selection"
}

# Export functions for use in subshells
export -f claude-here claude-quick claude-keys