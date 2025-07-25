#!/bin/bash

# Claude Code tmux Integration Installer
# Automated setup and configuration script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
CLAUDE_TMUX_DIR="$HOME/.claude/tmux"
SHELL_CONFIG="$HOME/.zshrc"
BACKUP_DIR="$HOME/.claude/tmux/backup"

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

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

log_header() {
    echo ""
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BLUE}$(echo "$1" | sed 's/./=/g')${NC}"
}

# ============================================================================
# PREREQUISITE CHECKS
# ============================================================================

check_prerequisites() {
    log_header "Checking Prerequisites"
    
    local issues=0
    
    # Check for Claude Code
    if command -v claude &> /dev/null; then
        log_success "Claude Code found: $(command -v claude)"
    else
        log_error "Claude Code not found"
        echo "  Please install Claude Code first:"
        echo "  Visit: https://claude.ai/claude-code"
        ((issues++))
    fi
    
    # Check for tmux
    if command -v tmux &> /dev/null; then
        log_success "tmux found: $(tmux -V)"
    else
        log_error "tmux not found"
        echo "  Install tmux:"
        echo "    macOS: brew install tmux"
        echo "    Ubuntu: sudo apt install tmux"
        echo "    CentOS: sudo yum install tmux"
        ((issues++))
    fi
    
    # Check shell
    if [[ "$SHELL" == *"zsh"* ]]; then
        log_success "Shell: zsh detected"
        SHELL_CONFIG="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        log_success "Shell: bash detected"
        SHELL_CONFIG="$HOME/.bashrc"
    else
        log_warning "Shell: $SHELL (may need manual configuration)"
    fi
    
    # Check shell config file
    if [[ -f "$SHELL_CONFIG" ]]; then
        log_success "Shell config: $SHELL_CONFIG exists"
    else
        log_warning "Shell config: $SHELL_CONFIG not found (will create)"
        touch "$SHELL_CONFIG"
    fi
    
    if [[ $issues -gt 0 ]]; then
        log_error "Please resolve $issues issue(s) before continuing"
        exit 1
    fi
    
    log_success "All prerequisites satisfied"
}

# ============================================================================
# BACKUP AND MIGRATION
# ============================================================================

backup_existing_config() {
    log_header "Backing Up Existing Configuration"
    
    mkdir -p "$BACKUP_DIR"
    local backup_made=false
    
    # Backup old files if they exist
    local old_files=(
        "$HOME/.claude/tmux_claude_manager.sh"
        "$HOME/.claude/tmux_aliases.sh"
        "$HOME/.claude/TMUX_SETUP.md"
    )
    
    for file in "${old_files[@]}"; do
        if [[ -f "$file" ]]; then
            local backup_name="$(basename "$file").$(date +%Y%m%d-%H%M%S)"
            cp "$file" "$BACKUP_DIR/$backup_name"
            log_info "Backed up: $(basename "$file") → backup/$backup_name"
            backup_made=true
        fi
    done
    
    # Backup shell config lines
    if grep -q "tmux.*claude\|claude.*tmux" "$SHELL_CONFIG" 2>/dev/null; then
        local shell_backup="$BACKUP_DIR/shell-config-backup.$(date +%Y%m%d-%H%M%S)"
        grep "tmux.*claude\|claude.*tmux" "$SHELL_CONFIG" > "$shell_backup" 2>/dev/null || true
        log_info "Backed up shell config lines → backup/$(basename "$shell_backup")"
        backup_made=true
    fi
    
    if [[ "$backup_made" == true ]]; then
        log_success "Backups created in: $BACKUP_DIR"
    else
        log_info "No existing configuration found to backup"
    fi
}

remove_old_config() {
    log_header "Removing Old Configuration"
    
    # Remove old files
    local old_files=(
        "$HOME/.claude/tmux_claude_manager.sh"
        "$HOME/.claude/tmux_aliases.sh"
        "$HOME/.claude/TMUX_SETUP.md"
    )
    
    local removed_count=0
    for file in "${old_files[@]}"; do
        if [[ -f "$file" ]]; then
            rm -f "$file"
            log_info "Removed: $(basename "$file")"
            ((removed_count++))
        fi
    done
    
    # Remove old shell config lines
    if [[ -f "$SHELL_CONFIG" ]]; then
        # Create temporary file without old claude tmux lines
        grep -v "tmux.*claude\|claude.*tmux\|tmux_aliases\|tmux_claude_manager" "$SHELL_CONFIG" > "${SHELL_CONFIG}.tmp" 2>/dev/null || cp "$SHELL_CONFIG" "${SHELL_CONFIG}.tmp"
        
        if ! diff -q "$SHELL_CONFIG" "${SHELL_CONFIG}.tmp" &>/dev/null; then
            mv "${SHELL_CONFIG}.tmp" "$SHELL_CONFIG"
            log_info "Cleaned shell config: $SHELL_CONFIG"
            ((removed_count++))
        else
            rm -f "${SHELL_CONFIG}.tmp"
        fi
    fi
    
    if [[ $removed_count -gt 0 ]]; then
        log_success "Removed $removed_count old configuration item(s)"
    else
        log_info "No old configuration found to remove"
    fi
}

# ============================================================================
# INSTALLATION
# ============================================================================

verify_installation() {
    log_header "Verifying Installation"
    
    local issues=0
    
    # Check directory structure
    local required_dirs=(
        "$CLAUDE_TMUX_DIR/bin"
        "$CLAUDE_TMUX_DIR/config"
        "$CLAUDE_TMUX_DIR/data"
        "$CLAUDE_TMUX_DIR/docs"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            log_success "Directory exists: $(basename "$dir")/"
        else
            log_error "Missing directory: $dir"
            ((issues++))
        fi
    done
    
    # Check required files
    local required_files=(
        "$CLAUDE_TMUX_DIR/bin/claude-router.sh"
        "$CLAUDE_TMUX_DIR/bin/session-manager.sh"
        "$CLAUDE_TMUX_DIR/config/shell-integration.sh"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" && -x "$file" ]]; then
            log_success "File ready: $(basename "$file")"
        elif [[ -f "$file" ]]; then
            log_warning "File exists but not executable: $(basename "$file")"
            chmod +x "$file"
            log_success "Made executable: $(basename "$file")"
        else
            log_error "Missing file: $file"
            ((issues++))
        fi
    done
    
    if [[ $issues -gt 0 ]]; then
        log_error "Installation verification failed with $issues issue(s)"
        return 1
    fi
    
    log_success "Installation verified successfully"
}

install_shell_integration() {
    log_header "Installing Shell Integration"
    
    local integration_line="source $CLAUDE_TMUX_DIR/config/shell-integration.sh"
    
    # Check if already configured
    if grep -F "$integration_line" "$SHELL_CONFIG" &>/dev/null; then
        log_warning "Shell integration already configured"
        return
    fi
    
    # Add integration to shell config
    echo "" >> "$SHELL_CONFIG"
    echo "# Claude Code tmux Integration" >> "$SHELL_CONFIG"
    echo "$integration_line" >> "$SHELL_CONFIG"
    
    log_success "Added integration to: $SHELL_CONFIG"
}

setup_tmux_config() {
    log_header "Setting Up tmux Configuration"
    
    local tmux_config="$HOME/.tmux.conf"
    local claude_tmux_config="$CLAUDE_TMUX_DIR/config/tmux.conf"
    
    if [[ ! -f "$claude_tmux_config" ]]; then
        log_info "No Claude tmux config found, skipping"
        return
    fi
    
    echo ""
    echo "An optimized tmux configuration is available that enhances the Claude session experience."
    echo ""
    
    if [[ -f "$tmux_config" ]]; then
        echo "⚠️  You already have a tmux configuration: $tmux_config"
        echo ""
        echo "Options:"
        echo "  1) Keep current config (no changes)"
        echo "  2) Backup current and use Claude config"  
        echo "  3) Append Claude config to current config"
        echo ""
        read -p "Choose option [1]: " choice
        choice=${choice:-1}
        
        case "$choice" in
            1)
                log_info "Keeping existing tmux configuration"
                ;;
            2)
                local backup_name=".tmux.conf.backup.$(date +%Y%m%d-%H%M%S)"
                cp "$tmux_config" "$HOME/$backup_name"
                cp "$claude_tmux_config" "$tmux_config"
                log_success "Backed up to: ~/$backup_name"
                log_success "Installed Claude tmux configuration"
                ;;
            3)
                echo "" >> "$tmux_config"
                echo "# Claude Code tmux Integration" >> "$tmux_config"
                cat "$claude_tmux_config" >> "$tmux_config"
                log_success "Appended Claude config to existing tmux config"
                ;;
        esac
    else
        read -p "Install Claude-optimized tmux configuration? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp "$claude_tmux_config" "$tmux_config"
            log_success "Installed Claude tmux configuration"
        else
            log_info "Skipped tmux configuration"
        fi
    fi
}

# ============================================================================
# TESTING
# ============================================================================

test_installation() {
    log_header "Testing Installation"
    
    # Test sourcing the integration
    if source "$CLAUDE_TMUX_DIR/config/shell-integration.sh" 2>/dev/null; then
        log_success "Shell integration loads successfully"
    else
        log_error "Failed to load shell integration"
        return 1
    fi
    
    # Test claude function availability
    if declare -F claude &>/dev/null; then
        log_success "claude function available"
    else
        log_error "claude function not available"
        return 1
    fi
    
    # Test session manager
    if "$CLAUDE_TMUX_DIR/bin/session-manager.sh" help &>/dev/null; then
        log_success "Session manager working"
    else
        log_error "Session manager failed"
        return 1
    fi
    
    # Test router
    if "$CLAUDE_TMUX_DIR/bin/claude-router.sh" 2>/dev/null | grep -q "Claude Code not found"; then
        log_success "Router working (Claude Code check)"
    else
        log_warning "Router test inconclusive (may need Claude Code installed)"
    fi
    
    log_success "Installation tests completed"
}

# ============================================================================
# COMPLETION MESSAGE
# ============================================================================

show_completion() {
    log_header "Installation Complete!"
    
    echo ""
    echo -e "${GREEN}🎉 Claude Code tmux Integration is now installed!${NC}"
    echo ""
    echo -e "${BOLD}📁 Installation Details:${NC}"
    echo "  Directory: $CLAUDE_TMUX_DIR"
    echo "  Shell integration: $SHELL_CONFIG"
    echo "  Backup location: $BACKUP_DIR"
    echo ""
    echo -e "${BOLD}🚀 Getting Started:${NC}"
    echo "  1. Restart your terminal or run: source $SHELL_CONFIG"
    echo "  2. Navigate to any project directory"
    echo "  3. Run: claude \"help me get started\""
    echo ""
    echo -e "${BOLD}📚 Available Commands:${NC}"
    echo "  claude [args...]              # Smart session management + Claude execution"
    echo "  claude-session start <name>   # Create named session"
    echo "  claude-session list          # List workspace sessions"
    echo "  claude-session status        # Show system status"
    echo "  claude-help                  # Show detailed help"
    echo ""
    echo -e "${BOLD}💡 Key Features:${NC}"
    echo "  • Zero-config persistence: Just use 'claude' normally"
    echo "  • All Claude flags work: --model, --debug, --print, etc."
    echo "  • Workspace-aware sessions: Each project gets its own context"
    echo "  • Smart routing: Interactive queries use tmux, utilities run directly"
    echo ""
    echo -e "${BOLD}🔧 Maintenance:${NC}"
    echo "  claude-debug                 # Troubleshoot issues"
    echo "  claude-migrate               # Check for old configurations"
    echo "  claude-session clean         # Remove old sessions"
    echo ""
    echo -e "${GREEN}Happy coding with persistent Claude sessions! 🎯${NC}"
}

# ============================================================================
# MAIN INSTALLATION FLOW
# ============================================================================

main() {
    echo -e "${BOLD}${BLUE}🔧 Claude Code tmux Integration Installer${NC}"
    echo -e "${BLUE}===========================================${NC}"
    
    # Parse arguments
    local force=false
    local skip_tmux=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                force=true
                shift
                ;;
            --skip-tmux)
                skip_tmux=true
                shift
                ;;
            --help|-h)
                echo ""
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --force       Force installation even if already installed"
                echo "  --skip-tmux   Skip tmux configuration setup"
                echo "  --help        Show this help message"
                echo ""
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Check if already installed
    if [[ -f "$CLAUDE_TMUX_DIR/config/shell-integration.sh" && "$force" != true ]]; then
        log_warning "Installation already exists"
        echo ""
        echo "The Claude tmux integration appears to be already installed."
        echo "Use --force to reinstall or run individual setup steps:"
        echo ""
        echo "  claude-debug     # Check current installation"
        echo "  claude-migrate   # Check for old configurations"
        echo ""
        read -p "Continue with reinstallation? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled"
            exit 0
        fi
    fi
    
    # Run installation steps
    check_prerequisites
    backup_existing_config
    remove_old_config
    verify_installation
    install_shell_integration
    
    if [[ "$skip_tmux" != true ]]; then
        setup_tmux_config
    fi
    
    test_installation
    show_completion
    
    echo ""
    log_info "Installation log available at: $CLAUDE_TMUX_DIR/data/install.log"
}

# ============================================================================
# ERROR HANDLING
# ============================================================================

# Trap errors and provide helpful information
trap 'echo ""; log_error "Installation failed on line $LINENO. Check the error above."; exit 1' ERR

# Create log file
mkdir -p "$CLAUDE_TMUX_DIR/data" 2>/dev/null || true
exec > >(tee -a "$CLAUDE_TMUX_DIR/data/install.log")
exec 2>&1

# ============================================================================
# ENTRY POINT
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi