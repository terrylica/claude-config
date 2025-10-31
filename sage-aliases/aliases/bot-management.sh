#!/bin/bash
# Telegram Bot Management Aliases
# Part of SAGE Aliases Tool - ~/.claude/tools/sage-aliases/

# =============================================================================
# BOT LIFECYCLE MANAGEMENT (Production Mode Only)
# =============================================================================

# Production mode (launchd + watchexec supervision)
alias bot='~/.claude/automation/lychee/runtime/bot/bot-service.sh'
alias bot-start='~/.claude/automation/lychee/runtime/bot/bot-service.sh start'
alias bot-stop='~/.claude/automation/lychee/runtime/bot/bot-service.sh stop'
alias bot-restart='~/.claude/automation/lychee/runtime/bot/bot-service.sh restart'
alias bot-status='~/.claude/automation/lychee/runtime/bot/bot-service.sh status'
alias bot-install='~/.claude/automation/lychee/runtime/bot/bot-service.sh install'
alias bot-uninstall='~/.claude/automation/lychee/runtime/bot/bot-service.sh uninstall'

# =============================================================================
# BOT MONITORING & DEBUGGING
# =============================================================================

# Logs
alias bot-logs='tail -f ~/.claude/automation/lychee/logs/telegram-handler.log'
alias bot-logs-last='tail -50 ~/.claude/automation/lychee/logs/telegram-handler.log'
alias bot-logs-errors='grep -i error ~/.claude/automation/lychee/logs/telegram-handler.log | tail -20'

# Process inspection
alias bot-ps='ps aux | grep -E "(watchexec.*bot|multi-workspace-bot)" | grep -v grep'
alias bot-tree='pstree -p $(cat ~/.claude/automation/lychee/state/watchexec.pid 2>/dev/null || echo "1") 2>/dev/null || echo "Bot not running"'

# PID files
alias bot-pids='echo "Watchexec: $(cat ~/.claude/automation/lychee/state/watchexec.pid 2>/dev/null || echo "N/A")" && echo "Bot: $(cat ~/.claude/automation/lychee/state/bot.pid 2>/dev/null || echo "N/A")"'

# =============================================================================
# STATE DIRECTORIES
# =============================================================================

# Quick navigation
alias bot-state='cd ~/.claude/automation/lychee/state'
alias bot-summaries='cd ~/.claude/automation/lychee/state/summaries && ls -lh'
alias bot-callbacks='cd ~/.claude/automation/lychee/state/callbacks && ls -lh | head -20'
alias bot-progress='cd ~/.claude/automation/lychee/state/progress && ls -lh'

# State inspection
alias bot-state-count='echo "Summaries: $(ls ~/.claude/automation/lychee/state/summaries 2>/dev/null | wc -l)" && echo "Callbacks: $(ls ~/.claude/automation/lychee/state/callbacks 2>/dev/null | wc -l)" && echo "Progress: $(ls ~/.claude/automation/lychee/state/progress 2>/dev/null | wc -l)"'

# =============================================================================
# DEVELOPMENT SHORTCUTS
# =============================================================================

# Code navigation
alias bot-code='cd ~/.claude/automation/lychee/runtime/bot'
alias bot-edit='code ~/.claude/automation/lychee/runtime/bot'
alias bot-lib='cd ~/.claude/automation/lychee/runtime/lib'

# Quick edits
alias bot-config='${EDITOR:-nano} ~/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py'
alias bot-workflows='${EDITOR:-nano} ~/.claude/automation/lychee/state/workflows.json'

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Quick restart with log tail
bot-reload() {
    bot-restart && echo "" && echo "Following logs (Ctrl+C to exit):" && sleep 2 && bot-logs
}

# Clean restart (stop, clean state, start)
bot-clean-restart() {
    echo "🧹 Cleaning bot state..."
    bot-stop
    rm -f ~/.claude/automation/lychee/state/watchexec.pid
    rm -f ~/.claude/automation/lychee/state/bot.pid
    echo "✓ Cleaned PID files"
    sleep 1
    bot-start
}

# Show full bot status with logs
bot-full-status() {
    bot-status
    echo ""
    echo "===== Recent Activity (last 10 lines) ====="
    bot-logs-last | tail -10
}
