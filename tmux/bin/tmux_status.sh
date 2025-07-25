#!/bin/bash

# Claude Code tmux Status Reporter
# Quick system status and health check

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CLAUDE_TMUX_DIR="$HOME/.claude/tmux"
SESSION_LOG="$CLAUDE_TMUX_DIR/data/session_history.log"

echo -e "${BLUE}🔍 Claude Code tmux System Status${NC}"
echo "=================================="
echo ""

# System Information
echo "📊 System Information:"
echo "  tmux version: $(tmux -V 2>/dev/null || echo 'Not installed')"
echo "  Installation: $CLAUDE_TMUX_DIR"
echo "  Shell config: $([[ -f ~/.zshrc ]] && echo '~/.zshrc exists' || echo '~/.zshrc missing')"
echo ""

# Active Sessions
echo "🖥️  Active Sessions:"
active_count=$(tmux list-sessions 2>/dev/null | grep -c "claude-" || echo "0")
if [[ "$active_count" -gt 0 ]]; then
    echo -e "  ${GREEN}$active_count Claude sessions active${NC}"
    tmux list-sessions -F "  - #{session_name} (#{?session_attached,🟢 attached,⚫ detached})" 2>/dev/null | grep "claude-" | head -5
    if [[ "$active_count" -gt 5 ]]; then
        echo "  ... and $((active_count - 5)) more"
    fi
else
    echo -e "  ${YELLOW}No active Claude sessions${NC}"
fi
echo ""

# Session History
echo "📜 Session History:"
if [[ -f "$SESSION_LOG" ]]; then
    total_sessions=$(wc -l < "$SESSION_LOG" 2>/dev/null || echo "0")
    echo "  Total sessions created: $total_sessions"
    
    if [[ "$total_sessions" -gt 0 ]]; then
        echo "  Recent sessions:"
        tail -3 "$SESSION_LOG" | while IFS='|' read -r timestamp session_name workspace; do
            printf "    %-20s | %s\n" "$(echo $timestamp | xargs)" "$(echo $session_name | xargs)"
        done
    fi
else
    echo -e "  ${YELLOW}No session history found${NC}"
fi
echo ""

# Configuration Status
echo "⚙️  Configuration:"
echo "  Manager script: $([[ -x "$CLAUDE_TMUX_DIR/bin/tmux_claude_manager.sh" ]] && echo '✅ executable' || echo '❌ missing/not executable')"
echo "  Aliases config: $([[ -f "$CLAUDE_TMUX_DIR/config/aliases.sh" ]] && echo '✅ present' || echo '❌ missing')"
echo "  Data directory: $([[ -d "$CLAUDE_TMUX_DIR/data" ]] && echo '✅ present' || echo '❌ missing')"

# Check if aliases are loaded
if command -v claude-start &> /dev/null; then
    echo -e "  Shell aliases: ${GREEN}✅ loaded${NC}"
else
    echo -e "  Shell aliases: ${YELLOW}⚠️  not loaded (restart terminal or source ~/.zshrc)${NC}"
fi
echo ""

# Disk Usage
echo "💾 Storage:"
if [[ -d "$CLAUDE_TMUX_DIR" ]]; then
    size=$(du -sh "$CLAUDE_TMUX_DIR" 2>/dev/null | cut -f1 || echo "unknown")
    echo "  Directory size: $size"
fi

# Log file size
if [[ -f "$SESSION_LOG" ]]; then
    log_size=$(du -sh "$SESSION_LOG" 2>/dev/null | cut -f1 || echo "unknown")
    echo "  Session log: $log_size"
fi
echo ""

# Health Check
echo "🏥 Health Check:"
issues=0

# Check tmux installation
if ! command -v tmux &> /dev/null; then
    echo "  ❌ tmux not installed"
    ((issues++))
fi

# Check directory structure
for dir in bin config data docs; do
    if [[ ! -d "$CLAUDE_TMUX_DIR/$dir" ]]; then
        echo "  ❌ Missing directory: $dir"
        ((issues++))
    fi
done

# Check essential files
essential_files=(
    "bin/tmux_claude_manager.sh"
    "config/aliases.sh"
)

for file in "${essential_files[@]}"; do
    if [[ ! -f "$CLAUDE_TMUX_DIR/$file" ]]; then
        echo "  ❌ Missing file: $file"
        ((issues++))
    fi
done

if [[ "$issues" -eq 0 ]]; then
    echo -e "  ${GREEN}✅ All systems operational${NC}"
else
    echo -e "  ${YELLOW}⚠️  $issues issue(s) detected${NC}"
    echo "  Run: ~/.claude/tmux/bin/tmux_installer.sh to repair"
fi

echo ""
echo "💡 Quick Commands:"
echo "  claude-start     Start new session"
echo "  claude-resume    Select existing session"
echo "  claude-list      View all sessions"