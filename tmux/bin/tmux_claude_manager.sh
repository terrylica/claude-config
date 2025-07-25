#!/bin/bash

# Claude Code tmux Session Manager
# Advanced session management with intelligent naming and selection

set -euo pipefail

# Configuration
CLAUDE_SESSIONS_DIR="$HOME/.claude/tmux/data"
SESSION_LOG="$CLAUDE_SESSIONS_DIR/session_history.log"

# Ensure directory exists
mkdir -p "$CLAUDE_SESSIONS_DIR"

# Generate intelligent session name
generate_session_name() {
    local workspace_name
    local clean_name
    local timestamp
    local session_name
    
    # Get current directory name, handle special cases
    workspace_name=$(basename "$(pwd)")
    
    # Clean workspace name: replace special chars with hyphens, lowercase
    clean_name=$(echo "$workspace_name" | sed 's/[^a-zA-Z0-9]/-/g' | tr '[:upper:]' '[:lower:]' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
    
    # Generate timestamp: YYYY-MM-DD-HHMM
    timestamp=$(date '+%Y-%m-%d-%H%M')
    
    # Construct session name
    session_name="claude-${clean_name}-${timestamp}"
    
    echo "$session_name"
}

# Log session creation
log_session() {
    local session_name="$1"
    local workspace_path="$2"
    local timestamp
    
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "${timestamp} | ${session_name} | ${workspace_path}" >> "$SESSION_LOG"
}

# Start new Claude Code session
start_claude_session() {
    local session_name
    local current_path
    
    session_name=$(generate_session_name)
    current_path=$(pwd)
    
    echo "🚀 Starting Claude Code session: $session_name"
    echo "📁 Workspace: $current_path"
    
    # Check if session already exists (edge case)
    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo "⚠️  Session $session_name already exists. Attaching instead."
        tmux attach-session -t "$session_name"
        return
    fi
    
    # Create new session
    tmux new-session -d -s "$session_name" -c "$current_path"
    
    # Configure session
    tmux send-keys -t "$session_name" "echo 'Claude Code Session: $session_name'" Enter
    tmux send-keys -t "$session_name" "echo 'Workspace: $current_path'" Enter
    tmux send-keys -t "$session_name" "echo 'Started: $(date)'" Enter
    tmux send-keys -t "$session_name" "clear" Enter
    
    # Log session
    log_session "$session_name" "$current_path"
    
    # Start Claude Code
    tmux send-keys -t "$session_name" "claude" Enter
    
    # Attach to session
    tmux attach-session -t "$session_name"
}

# List all Claude sessions with enhanced info
list_claude_sessions() {
    echo "🔍 Active Claude Code Sessions:"
    echo "================================"
    
    if ! tmux list-sessions 2>/dev/null | grep -q "claude-"; then
        echo "No active Claude Code sessions found."
        echo ""
        show_recent_sessions
        return
    fi
    
    # Format: Name | Windows | Created | Status
    tmux list-sessions -F "#{session_name} | #{session_windows}w | #{session_created_string} | #{?session_attached,🟢 Active,⚫ Detached}" 2>/dev/null | \
    grep "claude-" | \
    while IFS='|' read -r name windows created status; do
        # Extract workspace from session name
        workspace=$(echo "$name" | sed 's/claude-\(.*\)-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]/\1/')
        printf "%-30s | %-8s | %-20s | %s\n" "$(echo $name | xargs)" "$(echo $windows | xargs)" "$(echo $created | xargs)" "$(echo $status | xargs)"
        printf "   📁 Workspace: %s\n" "$workspace"
        echo ""
    done
    
    echo ""
    show_recent_sessions
}

# Show recent sessions from log
show_recent_sessions() {
    if [[ -f "$SESSION_LOG" ]]; then
        echo "📜 Recent Session History (last 10):"
        echo "====================================="
        tail -10 "$SESSION_LOG" | while IFS='|' read -r timestamp session_name workspace_path; do
            printf "%-20s | %-30s | %s\n" "$(echo $timestamp | xargs)" "$(echo $session_name | xargs)" "$(echo $workspace_path | xargs)"
        done
        echo ""
    fi
}

# Interactive session selector
select_claude_session() {
    local sessions
    local session_array
    local choice
    
    echo "🎯 Select Claude Code Session:"
    echo "=============================="
    
    # Get Claude sessions
    sessions=$(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "claude-" || true)
    
    if [[ -z "$sessions" ]]; then
        echo "No active Claude Code sessions found."
        echo "Use 'claude-start' to create a new session."
        return 1
    fi
    
    # Convert to array for numbering
    mapfile -t session_array <<< "$sessions"
    
    # Display options
    for i in "${!session_array[@]}"; do
        local session_name="${session_array[$i]}"
        local workspace=$(echo "$session_name" | sed 's/claude-\(.*\)-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]/\1/')
        local status=$(tmux list-sessions -F "#{session_name}:#{?session_attached,🟢 Active,⚫ Detached}" | grep "^$session_name:" | cut -d: -f2)
        
        printf "%2d) %-30s | 📁 %-15s | %s\n" $((i+1)) "$session_name" "$workspace" "$status"
    done
    
    echo ""
    read -p "Enter session number (1-${#session_array[@]}): " choice
    
    # Validate choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le "${#session_array[@]}" ]]; then
        local selected_session="${session_array[$((choice-1))]}"
        echo "🔗 Connecting to: $selected_session"
        tmux attach-session -t "$selected_session"
    else
        echo "❌ Invalid selection. Please try again."
        return 1
    fi
}

# Clean up old sessions
cleanup_old_sessions() {
    local days_old=${1:-7}  # Default 7 days
    local cutoff_date
    
    cutoff_date=$(date -d "$days_old days ago" '+%Y-%m-%d' 2>/dev/null || date -v-"${days_old}d" '+%Y-%m-%d')
    
    echo "🧹 Cleaning up Claude sessions older than $days_old days..."
    
    tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "claude-" | while read -r session_name; do
        # Extract date from session name
        session_date=$(echo "$session_name" | grep -o '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' | head -1)
        
        if [[ "$session_date" < "$cutoff_date" ]]; then
            echo "  Removing old session: $session_name"
            tmux kill-session -t "$session_name" 2>/dev/null || true
        fi
    done
    
    echo "✅ Cleanup complete."
}

# Kill specific Claude session
kill_claude_session() {
    local session_name="$1"
    
    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo "🔥 Killing session: $session_name"
        tmux kill-session -t "$session_name"
        echo "✅ Session terminated."
    else
        echo "❌ Session '$session_name' not found."
    fi
}

# Main command dispatcher
main() {
    case "${1:-help}" in
        "start"|"new")
            start_claude_session
            ;;
        "list"|"ls")
            list_claude_sessions
            ;;
        "select"|"attach"|"resume")
            select_claude_session
            ;;
        "cleanup")
            cleanup_old_sessions "${2:-7}"
            ;;
        "kill")
            kill_claude_session "${2:-}"
            ;;
        "help"|*)
            echo "Claude Code tmux Session Manager"
            echo "================================"
            echo "Usage: $0 {command} [options]"
            echo ""
            echo "Commands:"
            echo "  start, new           Start new Claude session in current workspace"
            echo "  list, ls             List all active Claude sessions"
            echo "  select, attach       Interactive session selector"
            echo "  cleanup [days]       Remove sessions older than N days (default: 7)"
            echo "  kill {session}       Kill specific session"
            echo "  help                 Show this help"
            echo ""
            echo "Session naming: claude-{workspace}-{YYYY-MM-DD-HHMM}"
            echo "Example: claude-my-project-2025-01-15-1430"
            ;;
    esac
}

# Run main function with all arguments
main "$@"