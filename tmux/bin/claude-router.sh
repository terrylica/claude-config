#!/bin/bash

# Claude Code Intelligent Router
# Routes Claude commands to appropriate execution context (direct vs tmux session)

set -euo pipefail

# Configuration
CLAUDE_TMUX_DIR="$HOME/.claude/tmux"
SESSION_DATA_DIR="$CLAUDE_TMUX_DIR/data/workspace-sessions"
SESSION_LOG="$CLAUDE_TMUX_DIR/data/session-history.log"

# Ensure directories exist
mkdir -p "$SESSION_DATA_DIR"
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
    echo -e "${BLUE}ℹ️  $1${NC}" >&2
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" >&2
}

log_error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

get_workspace_name() {
    basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g'
}

get_path_hash() {
    echo "$(pwd)" | sha256sum | cut -c1-6
}

get_current_timestamp() {
    date '+%Y%m%d-%H%M%S'
}

log_session_activity() {
    local session_name="$1"
    local workspace_path="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "${timestamp} | ${session_name} | ${workspace_path}" >> "$SESSION_LOG"
}

# ============================================================================
# MODE DETECTION
# ============================================================================

detect_execution_mode() {
    local args=("$@")
    
    # Check for non-interactive modes
    for arg in "${args[@]}"; do
        case "$arg" in
            --print|--output-format|--input-format)
                echo "direct"
                return
                ;;
            config|mcp|doctor|update|install|migrate-installer|setup-token)
                echo "direct"
                return
                ;;
            --continue|--resume)
                echo "conflict"
                return
                ;;
        esac
    done
    
    # Check for explicit session-id (special case)
    for arg in "${args[@]}"; do
        if [[ "$arg" == "--session-id" ]]; then
            echo "conflict"
            return
        fi
    done
    
    # Default to interactive mode (tmux compatible)
    echo "interactive"
}

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

find_workspace_sessions() {
    local workspace_name="$1"
    local path_hash="$2"
    local session_pattern="claude-.*-${workspace_name}-${path_hash}"
    
    tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "$session_pattern" || true
}

create_session() {
    local session_name="$1"
    local workspace_path="$(pwd)"
    
    log_info "Creating session: $session_name"
    
    # Create tmux session
    tmux new-session -d -s "$session_name" -c "$workspace_path"
    
    # Log session creation
    log_session_activity "$session_name" "$workspace_path"
    
    echo "$session_name"
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

get_session_info() {
    local session_name="$1"
    local last_activity=""
    local window_count=""
    local status=""
    
    if tmux has-session -t "$session_name" 2>/dev/null; then
        last_activity=$(tmux display-message -t "$session_name" -p "#{session_last_attached_string}" 2>/dev/null || echo "unknown")
        window_count=$(tmux list-windows -t "$session_name" 2>/dev/null | wc -l)
        status=$(tmux list-sessions -F "#{session_name}:#{?session_attached,🟢 active,⚫ detached}" 2>/dev/null | grep "^$session_name:" | cut -d: -f2)
    fi
    
    echo "$last_activity|$window_count|$status"
}

extract_session_type() {
    local session_name="$1"
    # Extract type from claude-{type}-{workspace}-{hash}
    echo "$session_name" | sed 's/claude-\([^-]*\)-.*/\1/'
}

# ============================================================================
# SESSION SELECTION
# ============================================================================

prompt_session_choice() {
    local sessions=("$@")
    local workspace_name=$(get_workspace_name)
    
    echo ""
    echo -e "${BLUE}🎯 Multiple Claude sessions found for ${workspace_name}:${NC}"
    echo "================================================"
    echo ""
    
    for i in "${!sessions[@]}"; do
        local session="${sessions[$i]}"
        local session_type=$(extract_session_type "$session")
        local info=$(get_session_info "$session")
        local last_activity=$(echo "$info" | cut -d'|' -f1)
        local window_count=$(echo "$info" | cut -d'|' -f2)
        local status=$(echo "$info" | cut -d'|' -f3)
        
        printf "%2d) %-12s (%s, %sw, %s)\n" \
            $((i+1)) \
            "$session_type" \
            "$last_activity" \
            "$window_count" \
            "$status"
    done
    
    echo ""
    read -p "Select session [1]: " choice
    choice=${choice:-1}
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le "${#sessions[@]}" ]]; then
        echo "${sessions[$((choice-1))]}"
    else
        log_error "Invalid selection. Using first session."
        echo "${sessions[0]}"
    fi
}

# ============================================================================
# ARGUMENT PRESERVATION & EXECUTION
# ============================================================================

preserve_arguments() {
    local args=("$@")
    local preserved_cmd="claude"
    
    for arg in "${args[@]}"; do
        preserved_cmd+=" $(printf '%q' "$arg")"
    done
    
    echo "$preserved_cmd"
}

execute_in_session() {
    local session_name="$1"
    shift
    local args=("$@")
    
    # Ensure session exists
    if ! tmux has-session -t "$session_name" 2>/dev/null; then
        create_session "$session_name"
    fi
    
    if [[ ${#args[@]} -eq 0 ]]; then
        # No arguments - just attach to session
        log_info "Attaching to session: $session_name"
        tmux attach-session -t "$session_name"
    else
        # Arguments provided - send command and attach
        local cmd=$(preserve_arguments "${args[@]}")
        log_info "Executing in session $session_name: claude [${#args[@]} args]"
        
        tmux send-keys -t "$session_name" "$cmd" Enter
        tmux attach-session -t "$session_name"
    fi
}

# ============================================================================
# SESSION CONFLICT HANDLING
# ============================================================================

handle_session_conflict() {
    local args=("$@")
    
    echo ""
    log_warning "Session Management Conflict Detected"
    echo ""
    echo "You're using Claude's built-in session management (--continue, --resume, or --session-id)"
    echo "which conflicts with tmux persistence."
    echo ""
    echo "Options:"
    echo "  1) Use Claude's session management (run directly, no tmux)"
    echo "  2) Use tmux persistence (ignore Claude's session flags)"
    echo ""
    read -p "Choose option [1]: " choice
    choice=${choice:-1}
    
    case "$choice" in
        1)
            log_info "Running Claude directly with session management flags"
            command claude "${args[@]}"
            ;;
        2)
            log_info "Using tmux persistence (ignoring Claude's session flags)"
            route_to_tmux_session "${args[@]}"
            ;;
        *)
            log_error "Invalid choice. Running Claude directly."
            command claude "${args[@]}"
            ;;
    esac
}

# ============================================================================
# CORE ROUTING LOGIC
# ============================================================================

route_to_tmux_session() {
    local args=("$@")
    local workspace_name=$(get_workspace_name)
    local path_hash=$(get_path_hash)
    
    # Find existing workspace sessions
    local sessions_raw=$(find_workspace_sessions "$workspace_name" "$path_hash")
    local sessions=()
    
    # Convert to array
    if [[ -n "$sessions_raw" ]]; then
        while IFS= read -r session; do
            [[ -n "$session" ]] && sessions+=("$session")
        done <<< "$sessions_raw"
    fi
    
    local target_session=""
    
    case ${#sessions[@]} in
        0)
            # No sessions - create default
            local base_session="claude-default-${workspace_name}-${path_hash}"
            target_session=$(ensure_unique_session_name "$base_session")
            ;;
        1)
            # One session - use it
            target_session="${sessions[0]}"
            ;;
        *)
            # Multiple sessions - prompt user
            target_session=$(prompt_session_choice "${sessions[@]}")
            ;;
    esac
    
    execute_in_session "$target_session" "${args[@]}"
}

# ============================================================================
# MAIN ROUTER FUNCTION
# ============================================================================

claude_router() {
    local args=("$@")
    
    # Detect execution mode
    local mode=$(detect_execution_mode "${args[@]}")
    
    case "$mode" in
        "direct")
            # Non-interactive modes, subcommands - run directly
            command claude "${args[@]}"
            ;;
        "conflict")
            # Session conflicts - handle with user prompt
            handle_session_conflict "${args[@]}"
            ;;
        "interactive")
            # Safe for tmux persistence
            route_to_tmux_session "${args[@]}"
            ;;
        *)
            log_error "Unknown execution mode: $mode"
            command claude "${args[@]}"
            ;;
    esac
}

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

# If script is being sourced, export the function
if [[ "${BASH_SOURCE[0]:-}" != "${0:-}" ]]; then
    # Being sourced - make function available
    export -f claude_router
else
    # Being executed directly - run the router
    claude_router "$@"
fi