#!/bin/bash

# Claude Code tmux Setup Installer
# Automated installation and configuration script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLAUDE_TMUX_DIR="$HOME/.claude/tmux"
SHELL_CONFIG="$HOME/.zshrc"

# Logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v tmux &> /dev/null; then
        log_error "tmux is not installed. Please install tmux first:"
        echo "  macOS: brew install tmux"
        echo "  Ubuntu: sudo apt install tmux"
        exit 1
    fi
    
    if [[ ! -f "$SHELL_CONFIG" ]]; then
        log_warning "Shell configuration file not found: $SHELL_CONFIG"
        log_info "Creating $SHELL_CONFIG..."
        touch "$SHELL_CONFIG"
    fi
    
    log_success "Prerequisites check completed"
}

# Install aliases
install_aliases() {
    log_info "Installing shell aliases..."
    
    local alias_line="source $CLAUDE_TMUX_DIR/config/aliases.sh"
    
    if grep -q "source.*claude.*tmux.*aliases" "$SHELL_CONFIG"; then
        log_warning "Claude tmux aliases already configured in $SHELL_CONFIG"
    else
        echo "" >> "$SHELL_CONFIG"
        echo "# Claude Code tmux Integration" >> "$SHELL_CONFIG"
        echo "$alias_line" >> "$SHELL_CONFIG"
        log_success "Aliases added to $SHELL_CONFIG"
    fi
}

# Setup tmux configuration (optional)
setup_tmux_config() {
    log_info "Setting up tmux configuration..."
    
    local tmux_config="$HOME/.tmux.conf"
    local claude_tmux_config="$CLAUDE_TMUX_DIR/config/tmux.conf"
    
    if [[ -f "$tmux_config" ]]; then
        log_warning "Existing .tmux.conf found. Backing up to .tmux.conf.backup"
        cp "$tmux_config" "$tmux_config.backup"
    fi
    
    read -p "Do you want to use the Claude-optimized tmux configuration? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$claude_tmux_config" "$tmux_config"
        log_success "Claude tmux configuration installed"
    else
        log_info "Skipping tmux configuration setup"
    fi
}

# Test installation
test_installation() {
    log_info "Testing installation..."
    
    # Source the aliases to test
    if source "$CLAUDE_TMUX_DIR/config/aliases.sh" 2>/dev/null; then
        log_success "Aliases sourced successfully"
    else
        log_error "Failed to source aliases"
        return 1
    fi
    
    # Test script execution
    if "$CLAUDE_TMUX_DIR/bin/tmux_claude_manager.sh" help >/dev/null 2>&1; then
        log_success "Claude tmux manager script working"
    else
        log_error "Claude tmux manager script failed"
        return 1
    fi
    
    log_success "Installation test completed successfully"
}

# Show completion message
show_completion() {
    echo ""
    echo "🎉 Claude Code tmux Integration Setup Complete!"
    echo "=============================================="
    echo ""
    echo "📁 Installation Directory: $CLAUDE_TMUX_DIR"
    echo ""
    echo "🚀 Getting Started:"
    echo "   1. Restart your terminal or run: source $SHELL_CONFIG"
    echo "   2. Navigate to any project directory"
    echo "   3. Run: claude-start"
    echo ""
    echo "📚 Available Commands:"
    echo "   claude-start     Start new session in current workspace"
    echo "   claude-resume    Interactive session selector"
    echo "   claude-list      View all active sessions"
    echo "   claude-quick     Resume latest or start new"
    echo "   claude-keys      Show tmux key bindings"
    echo ""
    echo "📖 Documentation: $CLAUDE_TMUX_DIR/docs/"
    echo ""
    echo "Happy coding with persistent Claude sessions! 🎯"
}

# Main installation flow
main() {
    echo "🔧 Claude Code tmux Integration Installer"
    echo "========================================="
    echo ""
    
    check_prerequisites
    install_aliases
    setup_tmux_config
    test_installation
    show_completion
}

# Run installer
main "$@"