# Simple tmux Integration for Terminal
# Source this in your ~/.zshrc: source ~/.claude/tmux/config/simple-shell-integration.sh
#
# This provides clean, simple tmux session management completely separate from Claude Code

# Note: Load guard removed to ensure aliases are always available


# Configuration
export CLAUDE_TMUX_DIR="$HOME/.claude/tmux"

# Core tmux session management aliases
alias tmux-session="$CLAUDE_TMUX_DIR/bin/tmux-session"
alias tmux-list="$CLAUDE_TMUX_DIR/bin/tmux-list"
alias tmux-kill="$CLAUDE_TMUX_DIR/bin/tmux-kill"
alias setup-simple-tmux="$CLAUDE_TMUX_DIR/bin/setup-simple-tmux"

# Convenient shortcuts
alias ts="$CLAUDE_TMUX_DIR/bin/tmux-session"    # Quick session creation/attach
alias tl="$CLAUDE_TMUX_DIR/bin/tmux-list"       # List sessions
alias tk="$CLAUDE_TMUX_DIR/bin/tmux-kill"       # Kill session

# Note: Session persistence is automatic - no manual commands needed

# Quick session operations for current directory
alias tmux-here="$CLAUDE_TMUX_DIR/bin/tmux-session"    # Create/attach session using folder name


# Help function
tmux-help() {
    echo "🎯 Simple tmux Session Management"
    echo "=================================="
    echo ""
    echo "Core Commands:"
    echo "  tmux-session [name]     Create/attach session (uses folder name if no name)"
    echo "  tmux-list              List all sessions with status"
    echo "  tmux-kill <name>       Kill specific session"
    echo ""
    echo ""
    echo "Quick Aliases:"
    echo "  ts [name]              Short for tmux-session"
    echo "  tl                     Short for tmux-list"
    echo "  tk <name>              Short for tmux-kill"
    echo "  tmux-here              Same as ts (create/attach using folder name)"
    echo ""
    echo "Smart Naming Examples:"
    echo "  ~/my-project    →  my-project"
    echo "  ~/.config       →  dotconfig"
    echo "  ~/.git          →  dotgit"
    echo "  /tmp/Test_App   →  test-app"
    echo ""
    echo "Usage:"
    echo "  cd ~/my-project && ts          # Creates 'my-project' session"
    echo "  ts auth                        # Creates 'auth' session"
    echo "  tl                             # List all sessions"
    echo "  tk auth                        # Kill 'auth' session"
    echo ""
    echo "✨ Sessions automatically persist across reboots - just use and don't worry!"
    echo ""
    echo "Setup:"
    echo "  setup-simple-tmux      Run initial setup (installs everything)"
}

# Functions available in current shell only (no export to avoid tmux display issues)

# Simple tmux integration loaded silently