#!/bin/bash
# Claude Session Sync Tool
# Synchronizes recent sessions across all directory contexts to ensure
# sessions are accessible from any working directory

set -euo pipefail

# Configuration
CLAUDE_DIR="/home/tca/.claude"
SESSIONS_DIR="$CLAUDE_DIR/system/sessions"
MAX_AGE_DAYS=7
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

show_help() {
    cat << EOF
Claude Session Sync Tool

USAGE:
    claude-session-sync [OPTIONS] [COMMAND]

COMMANDS:
    sync        Synchronize recent sessions (default)
    list        List recent sessions by directory
    clean       Clean old duplicate sessions
    status      Show sync status

OPTIONS:
    -v, --verbose       Enable verbose output
    -d, --days DAYS     Max age of sessions to sync (default: 7)
    -h, --help          Show this help

EXAMPLES:
    claude-session-sync                    # Sync recent sessions
    claude-session-sync -v sync            # Sync with verbose output
    claude-session-sync list               # List recent sessions
    claude-session-sync -d 3 sync          # Sync sessions from last 3 days

DESCRIPTION:
    This tool ensures that recent Claude Code sessions are accessible from
    any working directory by synchronizing session files across all
    directory-specific session folders.

EOF
}

find_recent_sessions() {
    local days=$1
    find "$SESSIONS_DIR" -name "*.jsonl" -type f -mtime -"$days" -printf '%T@ %p\n' | sort -nr
}

get_session_directories() {
    find "$SESSIONS_DIR" -mindepth 1 -maxdepth 1 -type d | grep -E '^.*/(~|-|[A-Za-z])' | sort
}

sync_sessions() {
    local days=$1
    log "Starting session sync for sessions modified in last $days days"
    
    # Get all session directories
    local session_dirs
    mapfile -t session_dirs < <(get_session_directories)
    
    if [[ ${#session_dirs[@]} -eq 0 ]]; then
        warning "No session directories found"
        return 1
    fi
    
    log "Found ${#session_dirs[@]} session directories"
    
    # Find recent sessions
    local recent_sessions
    mapfile -t recent_sessions < <(find_recent_sessions "$days")
    
    if [[ ${#recent_sessions[@]} -eq 0 ]]; then
        warning "No recent sessions found in last $days days"
        return 0
    fi
    
    log "Found ${#recent_sessions[@]} recent sessions"
    
    local synced_count=0
    local total_size=0
    
    # For each recent session, ensure it exists in all relevant directories
    while IFS=' ' read -r timestamp session_path; do
        [[ -z "$session_path" ]] && continue
        
        local session_file
        session_file=$(basename "$session_path")
        local session_size
        session_size=$(stat -c%s "$session_path" 2>/dev/null || echo 0)
        
        log "Processing session: $session_file ($(numfmt --to=iec "$session_size"))"
        
        # Copy to key directories where users commonly work (NO SYMLINKS!)
        local key_dirs=(
            "$SESSIONS_DIR/--home-tca-.claude"
            "$SESSIONS_DIR/--home-tca-eon-nt"
        )
        
        # Also copy to the actual working directories
        local source_dir
        source_dir=$(dirname "$session_path")
        local source_name
        source_name=$(basename "$source_dir")
        
        # Add the source directory's corresponding target
        case "$source_name" in
            "-home-tca-eon-nt")
                key_dirs+=("$SESSIONS_DIR/--home-tca-eon-nt")
                ;;
            "~eon-nt")
                key_dirs+=("$SESSIONS_DIR/--home-tca-eon-nt")
                ;;
            "~-claude")
                key_dirs+=("$SESSIONS_DIR/--home-tca-.claude")
                ;;
        esac
        
        for target_dir in "${key_dirs[@]}"; do
            if [[ -d "$target_dir" ]]; then
                local target_file="$target_dir/$session_file"
                
                # Only copy if target doesn't exist or is older
                if [[ ! -f "$target_file" ]] || [[ "$session_path" -nt "$target_file" ]]; then
                    if cp "$session_path" "$target_file" 2>/dev/null; then
                        # Preserve timestamp
                        touch -r "$session_path" "$target_file"
                        log "Synced to $(basename "$target_dir")"
                        ((synced_count++))
                        ((total_size += session_size))
                    else
                        error "Failed to sync to $target_dir"
                    fi
                fi
            fi
        done
        
    done <<< "$(printf '%s\n' "${recent_sessions[@]}")"
    
    if [[ $synced_count -gt 0 ]]; then
        success "Synced $synced_count sessions ($(numfmt --to=iec "$total_size") total)"
    else
        log "All sessions already synchronized"
    fi
}

list_sessions() {
    local days=$1
    echo "Recent sessions (last $days days):"
    echo
    
    local session_dirs
    mapfile -t session_dirs < <(get_session_directories)
    
    for dir in "${session_dirs[@]}"; do
        local dir_name
        dir_name=$(basename "$dir")
        local session_count
        session_count=$(find "$dir" -name "*.jsonl" -type f -mtime -"$days" | wc -l)
        
        if [[ $session_count -gt 0 ]]; then
            echo -e "${BLUE}$dir_name${NC}: $session_count sessions"
            
            if [[ "$VERBOSE" == "true" ]]; then
                find "$dir" -name "*.jsonl" -type f -mtime -"$days" -printf '  %TY-%Tm-%Td %TH:%TM %f (%s bytes)\n' | sort -r | head -3
                if [[ $session_count -gt 3 ]]; then
                    echo "  ... and $((session_count - 3)) more"
                fi
                echo
            fi
        fi
    done
}

show_status() {
    echo "Claude Session Sync Status"
    echo "=========================="
    echo
    
    local total_sessions
    total_sessions=$(find "$SESSIONS_DIR" -name "*.jsonl" -type f | wc -l)
    local total_size
    total_size=$(find "$SESSIONS_DIR" -name "*.jsonl" -type f -exec stat -c%s {} + | awk '{sum+=$1} END {print sum}')
    
    echo "Total sessions: $total_sessions"
    echo "Total size: $(numfmt --to=iec "$total_size")"
    echo
    
    echo "Session directories:"
    get_session_directories | while read -r dir; do
        local dir_name
        dir_name=$(basename "$dir")
        local count
        count=$(find "$dir" -name "*.jsonl" -type f | wc -l)
        local size
        size=$(find "$dir" -name "*.jsonl" -type f -exec stat -c%s {} + 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        
        printf "  %-30s %6s sessions  %10s\n" "$dir_name" "$count" "$(numfmt --to=iec "$size")"
    done
}

clean_duplicates() {
    log "Cleaning duplicate sessions..."
    
    # Find duplicate sessions across directories
    local temp_file
    temp_file=$(mktemp)
    
    find "$SESSIONS_DIR" -name "*.jsonl" -type f -printf '%f %p %s\n' | sort > "$temp_file"
    
    local cleaned_count=0
    local current_file=""
    local smallest_size=999999999
    local keep_file=""
    
    while read -r filename filepath size; do
        if [[ "$filename" != "$current_file" ]]; then
            # Process previous group
            if [[ -n "$current_file" && $cleaned_count -gt 0 ]]; then
                log "Kept smallest version: $keep_file"
            fi
            
            # Start new group
            current_file="$filename"
            smallest_size="$size"
            keep_file="$filepath"
            cleaned_count=0
        else
            # Same filename, check if duplicate
            if [[ "$size" -lt "$smallest_size" ]]; then
                # Remove the larger file, keep smaller
                if [[ -f "$keep_file" ]]; then
                    rm "$keep_file" && log "Removed larger duplicate: $keep_file"
                fi
                smallest_size="$size"
                keep_file="$filepath"
            else
                # Remove this larger file
                rm "$filepath" && log "Removed larger duplicate: $filepath"
            fi
            ((cleaned_count++))
        fi
    done < "$temp_file"
    
    rm "$temp_file"
    
    if [[ $cleaned_count -gt 0 ]]; then
        success "Cleaned $cleaned_count duplicate sessions"
    else
        log "No duplicates found"
    fi
}

# Parse arguments
COMMAND="sync"
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--days)
            MAX_AGE_DAYS="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        sync|list|clean|status)
            COMMAND="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate sessions directory
if [[ ! -d "$SESSIONS_DIR" ]]; then
    error "Sessions directory not found: $SESSIONS_DIR"
    exit 1
fi

# Execute command
case "$COMMAND" in
    sync)
        sync_sessions "$MAX_AGE_DAYS"
        ;;
    list)
        list_sessions "$MAX_AGE_DAYS"
        ;;
    clean)
        clean_duplicates
        ;;
    status)
        show_status
        ;;
    *)
        error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
