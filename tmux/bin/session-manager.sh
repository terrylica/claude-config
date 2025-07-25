#!/bin/bash

# Claude Session Manager
# Explicit session management utilities for advanced users

set -euo pipefail

# Configuration
CLAUDE_TMUX_DIR="$HOME/.claude/tmux"
SESSION_DATA_DIR="$CLAUDE_TMUX_DIR/data/workspace-sessions"
SESSION_LOG="$CLAUDE_TMUX_DIR/data/session-history.log"
WORKSPACE_CONFIG_DIR="$SESSION_DATA_DIR"

# Ensure directories exist
mkdir -p "$SESSION_DATA_DIR"
mkdir -p "$WORKSPACE_CONFIG_DIR"
mkdir -p "$(dirname "$SESSION_LOG")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================================================
# UTILITY FUNCTIONS
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

get_workspace_name() {
    basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g'
}

get_path_hash() {
    echo "$(pwd)" | sha256sum | cut -c1-6
}

get_workspace_config_file() {
    local workspace_name=$(get_workspace_name)
    local path_hash=$(get_path_hash)
    echo "$WORKSPACE_CONFIG_DIR/${workspace_name}-${path_hash}.json"
}

log_session_activity() {
    local session_name="$1"
    local workspace_path="$2"
    local action="${3:-created}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "${timestamp} | ${action} | ${session_name} | ${workspace_path}" >> "$SESSION_LOG"
}

# ============================================================================
# SESSION UTILITIES
# ============================================================================

find_workspace_sessions() {
    local workspace_name="$1"
    local path_hash="$2"
    local session_pattern="claude-.*-${workspace_name}-${path_hash}"
    
    tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "$session_pattern" || true
}

get_session_details() {
    local session_name="$1"
    
    if ! tmux has-session -t "$session_name" 2>/dev/null; then
        echo "notfound|||"
        return
    fi
    
    local last_activity=$(tmux display-message -t "$session_name" -p "#{session_last_attached_string}" 2>/dev/null || echo "unknown")
    local window_count=$(tmux list-windows -t "$session_name" 2>/dev/null | wc -l)
    local status=$(tmux list-sessions -F "#{session_name}:#{?session_attached,🟢 active,⚫ detached}" 2>/dev/null | grep "^$session_name:" | cut -d: -f2 || echo "⚫ detached")
    local created=$(tmux display-message -t "$session_name" -p "#{session_created_string}" 2>/dev/null || echo "unknown")
    
    echo "$last_activity|$window_count|$status|$created"
}

extract_session_type() {
    local session_name="$1"
    # Extract type from claude-{type}-{workspace}-{hash}
    local type=$(echo "$session_name" | sed 's/claude-\([^-]*\)-.*/\1/')
    echo "$type"
}

ensure_unique_session_name() {
    local base_name="$1"
    local counter=0
    local session_name="$base_name"
    
    while tmux has-session -t "$session_name" 2>/dev/null; do
        ((counter++))
        session_name="${base_name}-$(printf "%03d" $counter)"
    done
    
    echo "$session_name"
}

# ============================================================================
# WORKSPACE CONFIGURATION
# ============================================================================

save_workspace_config() {
    local config_file=$(get_workspace_config_file)
    local workspace_name=$(get_workspace_name)
    local path_hash=$(get_path_hash)
    local workspace_path="$(pwd)"
    
    cat > "$config_file" <<EOF
{
  "workspace_name": "$workspace_name",
  "workspace_path": "$workspace_path",
  "path_hash": "$path_hash",
  "last_updated": "$(date -Iseconds)",
  "default_session": "",
  "created_sessions": []
}
EOF
}

get_workspace_config() {
    local config_file=$(get_workspace_config_file)
    
    if [[ ! -f "$config_file" ]]; then
        save_workspace_config
    fi
    
    cat "$config_file"
}

update_workspace_config() {
    local key="$1"
    local value="$2"
    local config_file=$(get_workspace_config_file)
    
    if [[ ! -f "$config_file" ]]; then
        save_workspace_config
    fi
    
    # Simple JSON update (requires jq for complex operations)
    if command -v jq &> /dev/null; then
        jq ".$key = \"$value\" | .last_updated = \"$(date -Iseconds)\"" "$config_file" > "${config_file}.tmp" && mv "${config_file}.tmp" "$config_file"
    fi
}

# ============================================================================
# SESSION COMMANDS
# ============================================================================

cmd_start() {
    local session_type="$1"
    local workspace_name=$(get_workspace_name)
    local path_hash=$(get_path_hash)
    local workspace_path="$(pwd)"
    
    if [[ -z "$session_type" ]]; then
        log_error "Session name required. Usage: claude-session start <name>"
        return 1
    fi
    
    # Create session name
    local base_session="claude-${session_type}-${workspace_name}-${path_hash}"
    local session_name=$(ensure_unique_session_name "$base_session")
    
    log_info "Creating session: $session_name"
    
    # Create tmux session
    tmux new-session -d -s "$session_name" -c "$workspace_path"
    
    # Start claude in the session
    tmux send-keys -t "$session_name" "claude" Enter
    
    # Log activity
    log_session_activity "$session_name" "$workspace_path" "created"
    
    log_success "Session created: $session_name"
    
    # Attach to session
    tmux attach-session -t "$session_name"
}

cmd_list() {
    local workspace_name=$(get_workspace_name)
    local path_hash=$(get_path_hash)
    local show_all=false
    
    # Check for --all flag
    if [[ "${1:-}" == "--all" ]]; then
        show_all=true
    fi
    
    echo ""
    echo -e "${BLUE}🎯 Claude Sessions for $(get_workspace_name):${NC}"
    echo "============================================="
    echo ""
    
    if [[ "$show_all" == true ]]; then
        # Show all Claude sessions across all workspaces
        local all_sessions=$(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "claude-" || true)
        
        if [[ -z "$all_sessions" ]]; then
            echo "No Claude sessions found."
            return
        fi
        
        printf "%-30s | %-12s | %-8s | %-15s | %s\n" "SESSION" "TYPE" "WINDOWS" "LAST ACTIVITY" "STATUS"
        printf "%-30s-+-%-12s-+-%-8s-+-%-15s-+-%s\n" "------------------------------" "------------" "--------" "---------------" "--------"
        
        while IFS= read -r session; do
            [[ -z "$session" ]] && continue
            local session_type=$(extract_session_type "$session")
            local details=$(get_session_details "$session")
            local last_activity=$(echo "$details" | cut -d'|' -f1)
            local window_count=$(echo "$details" | cut -d'|' -f2)
            local status=$(echo "$details" | cut -d'|' -f3)
            
            printf "%-30s | %-12s | %-8s | %-15s | %s\n" \
                "$session" "$session_type" "${window_count}w" "$last_activity" "$status"
        done <<< "$all_sessions"
    else
        # Show only workspace sessions
        local sessions_raw=$(find_workspace_sessions "$workspace_name" "$path_hash")
        
        if [[ -z "$sessions_raw" ]]; then
            echo "No Claude sessions found for this workspace."
            echo ""
            echo "💡 Create a session with: claude-session start <name>"
            echo "💡 Or just run: claude \"your question\""
            return
        fi
        
        printf "%-12s | %-8s | %-15s | %s\n" "TYPE" "WINDOWS" "LAST ACTIVITY" "STATUS" 
        printf "%-12s-+-%-8s-+-%-15s-+-%s\n" "------------" "--------" "---------------" "--------"
        
        while IFS= read -r session; do
            [[ -z "$session" ]] && continue
            local session_type=$(extract_session_type "$session")
            local details=$(get_session_details "$session")
            local last_activity=$(echo "$details" | cut -d'|' -f1)
            local window_count=$(echo "$details" | cut -d'|' -f2)
            local status=$(echo "$details" | cut -d'|' -f3)
            
            printf "%-12s | %-8s | %-15s | %s\n" \
                "$session_type" "${window_count}w" "$last_activity" "$status"
        done <<< "$sessions_raw"
    fi
    
    echo ""
}

cmd_attach() {
    local session_type="$1"
    local workspace_name=$(get_workspace_name)
    local path_hash=$(get_path_hash)
    
    if [[ -z "$session_type" ]]; then
        log_error "Session name required. Usage: claude-session attach <name>"
        return 1
    fi
    
    # Find the session
    local session_name="claude-${session_type}-${workspace_name}-${path_hash}"
    
    if ! tmux has-session -t "$session_name" 2>/dev/null; then
        log_error "Session not found: $session_name"
        echo ""
        echo "Available sessions:"
        cmd_list
        return 1
    fi
    
    log_info "Attaching to session: $session_name"
    log_session_activity "$session_name" "$(pwd)" "attached"
    
    tmux attach-session -t "$session_name"
}

cmd_kill() {
    local session_type="$1"
    local workspace_name=$(get_workspace_name)
    local path_hash=$(get_path_hash)
    
    if [[ -z "$session_type" ]]; then
        log_error "Session name required. Usage: claude-session kill <name>"
        return 1
    fi
    
    # Handle special case for killing all workspace sessions
    if [[ "$session_type" == "--all" ]]; then
        local sessions_raw=$(find_workspace_sessions "$workspace_name" "$path_hash")
        local count=0
        
        while IFS= read -r session; do
            [[ -z "$session" ]] && continue
            if tmux has-session -t "$session" 2>/dev/null; then
                tmux kill-session -t "$session"
                log_session_activity "$session" "$(pwd)" "killed"
                ((count++))
            fi
        done <<< "$sessions_raw"
        
        log_success "Killed $count session(s)"
        return
    fi
    
    # Kill specific session
    local session_name="claude-${session_type}-${workspace_name}-${path_hash}"
    
    if ! tmux has-session -t "$session_name" 2>/dev/null; then
        log_error "Session not found: $session_name"
        return 1
    fi
    
    tmux kill-session -t "$session_name"
    log_session_activity "$session_name" "$(pwd)" "killed"
    log_success "Session killed: $session_name"
}

cmd_clean() {
    local days_old="${1:-7}"
    local workspace_name=$(get_workspace_name)
    local path_hash=$(get_path_hash)
    
    log_info "Cleaning sessions older than $days_old days..."
    
    # Get cutoff date
    local cutoff_date
    if date -d "$days_old days ago" '+%Y-%m-%d' &>/dev/null; then
        # GNU date (Linux)
        cutoff_date=$(date -d "$days_old days ago" '+%Y-%m-%d')
    else
        # BSD date (macOS)
        cutoff_date=$(date -v-"${days_old}d" '+%Y-%m-%d')
    fi
    
    local sessions_raw=$(find_workspace_sessions "$workspace_name" "$path_hash")
    local cleaned_count=0
    
    while IFS= read -r session; do
        [[ -z "$session" ]] && continue
        
        # Extract date from session name (YYYYMMDD format in hash or timestamp)
        local session_date=$(echo "$session" | grep -o '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]' | head -1)
        
        if [[ -n "$session_date" ]]; then
            # Convert to YYYY-MM-DD format for comparison
            local formatted_date="${session_date:0:4}-${session_date:4:2}-${session_date:6:2}"
            
            if [[ "$formatted_date" < "$cutoff_date" ]]; then
                if tmux has-session -t "$session" 2>/dev/null; then
                    log_info "Removing old session: $session"
                    tmux kill-session -t "$session"
                    log_session_activity "$session" "$(pwd)" "cleaned"
                    ((cleaned_count++))
                fi
            fi
        fi
    done <<< "$sessions_raw"
    
    log_success "Cleaned $cleaned_count old session(s)"
}

cmd_config() {
    local action="${1:-show}"
    local key="$2"
    local value="$3"
    
    case "$action" in
        show|get)
            echo ""
            echo -e "${BLUE}🔧 Workspace Configuration:${NC}"
            echo "============================"
            
            local config=$(get_workspace_config)
            if command -v jq &> /dev/null; then
                echo "$config" | jq .
            else
                echo "$config"
            fi
            ;;
        set)
            if [[ -z "$key" || -z "$value" ]]; then
                log_error "Usage: claude-session config set <key> <value>"
                return 1
            fi
            
            update_workspace_config "$key" "$value"
            log_success "Configuration updated: $key = $value"
            ;;
        reset)
            local config_file=$(get_workspace_config_file)
            rm -f "$config_file"
            save_workspace_config
            log_success "Configuration reset to defaults"
            ;;
        *)
            log_error "Unknown config action: $action"
            echo "Usage: claude-session config {show|set|reset} [key] [value]"
            return 1
            ;;
    esac
}

cmd_status() {
    echo ""
    echo -e "${BLUE}🔍 Claude Session System Status${NC}"
    echo "================================="
    echo ""
    
    # System info
    echo "📊 System Information:"
    echo "  Installation: $CLAUDE_TMUX_DIR"
    echo "  Current workspace: $(get_workspace_name)"
    echo "  Workspace hash: $(get_path_hash)"
    echo "  tmux version: $(tmux -V 2>/dev/null || echo 'Not available')"
    echo ""
    
    # Session statistics
    local all_claude_sessions=$(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep -c "claude-" || echo "0")
    local workspace_sessions=$(find_workspace_sessions "$(get_workspace_name)" "$(get_path_hash)" | wc -l)
    
    echo "📈 Session Statistics:"
    echo "  Total Claude sessions: $all_claude_sessions"
    echo "  Workspace sessions: $workspace_sessions"
    echo ""
    
    # Recent activity
    if [[ -f "$SESSION_LOG" ]]; then
        echo "📜 Recent Activity:"
        tail -5 "$SESSION_LOG" | while IFS='|' read -r timestamp action session_name workspace_path; do
            printf "  %-20s | %-8s | %s\n" "$(echo $timestamp | xargs)" "$(echo $action | xargs)" "$(echo $session_name | xargs)"
        done
    fi
    
    echo ""
}

# ============================================================================
# HELP SYSTEM
# ============================================================================

cmd_help() {
    local command="${1:-}"
    
    case "$command" in
        start)
            echo "Usage: claude-session start <name>"
            echo ""
            echo "Create a new named Claude session in the current workspace."
            echo ""
            echo "Examples:"
            echo "  claude-session start auth      # Create session for authentication work"
            echo "  claude-session start bugfix    # Create session for bug fixing"
            ;;
        list)
            echo "Usage: claude-session list [--all]"
            echo ""
            echo "List Claude sessions for the current workspace."
            echo ""
            echo "Options:"
            echo "  --all    Show sessions from all workspaces"
            ;;
        attach)
            echo "Usage: claude-session attach <name>"
            echo ""
            echo "Attach to a specific named session."
            echo ""
            echo "Example:"
            echo "  claude-session attach auth     # Attach to the 'auth' session"
            ;;
        kill)
            echo "Usage: claude-session kill <name|--all>"
            echo ""
            echo "Kill a specific session or all workspace sessions."
            echo ""
            echo "Examples:"
            echo "  claude-session kill auth       # Kill the 'auth' session"
            echo "  claude-session kill --all      # Kill all workspace sessions"
            ;;
        clean)
            echo "Usage: claude-session clean [days]"
            echo ""
            echo "Remove old sessions (default: 7 days)."
            echo ""
            echo "Example:"
            echo "  claude-session clean 3         # Remove sessions older than 3 days"
            ;;
        config)
            echo "Usage: claude-session config {show|set|reset} [key] [value]"
            echo ""
            echo "Manage workspace configuration."
            echo ""
            echo "Examples:"
            echo "  claude-session config show                    # Show current config"
            echo "  claude-session config set default_session auth   # Set default session"
            echo "  claude-session config reset                   # Reset to defaults"
            ;;
        *)
            echo "Claude Session Manager"
            echo "======================"
            echo ""
            echo "Usage: claude-session <command> [options]"
            echo ""
            echo "Commands:"
            echo "  start <name>        Create named session"
            echo "  list [--all]        List workspace sessions"
            echo "  attach <name>       Attach to specific session"
            echo "  kill <name|--all>   Kill session(s)"
            echo "  clean [days]        Remove old sessions"
            echo "  config <action>     Manage configuration"
            echo "  status              Show system status"
            echo "  help [command]      Show help"
            echo ""
            echo "Examples:"
            echo "  claude-session start auth      # Create 'auth' session"
            echo "  claude-session list           # Show workspace sessions"
            echo "  claude-session attach auth    # Attach to 'auth' session"
            echo ""
            echo "💡 For automatic session management, just use: claude \"your question\""
            ;;
    esac
}

# ============================================================================
# MAIN COMMAND DISPATCHER
# ============================================================================

main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        start)
            cmd_start "$@"
            ;;
        list|ls)
            cmd_list "$@"
            ;;
        attach|resume)
            cmd_attach "$@"
            ;;
        kill|rm)
            cmd_kill "$@"
            ;;
        clean|cleanup)
            cmd_clean "$@"
            ;;
        config|cfg)
            cmd_config "$@"
            ;;
        status)
            cmd_status
            ;;
        help|-h|--help)
            cmd_help "$@"
            ;;
        *)
            log_error "Unknown command: $command"
            cmd_help
            exit 1
            ;;
    esac
}

# ============================================================================
# ENTRY POINT
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Being executed directly
    main "$@"
fi