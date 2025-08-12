#!/bin/bash
# sage-canonical-sessions.sh
# Universal Canonical Session Management for Cross-Platform Claude Code Sync
# Part of SAGE (Smart Automation GPU Environment) system

# Core canonicalization functions for platform-agnostic session handling

set -euo pipefail

# Constants for canonical session management
readonly CANONICAL_PREFIX="~"
readonly LEGACY_SESSION_BACKUP_DIR="legacy"
readonly SESSION_UUID_PATTERN="[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

# Logging function (inherit from main sage-sync system)
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] [CANONICAL] $message" | tee -a "${LOG_FILE:-/tmp/sage-canonical.log}"
}

# Platform detection and home directory pattern identification
detect_platform_info() {
    local platform
    local user_prefix
    local user_name
    
    case "$(uname -s)" in
        Darwin)
            platform="macos"
            user_prefix="Users"
            ;;
        Linux)
            platform="linux"
            user_prefix="home"
            ;;
        MINGW*|CYGWIN*|MSYS*)
            platform="windows"
            user_prefix="c/Users"
            ;;
        *)
            platform="unknown"
            user_prefix="home"
            log "WARNING" "Unknown platform $(uname -s), defaulting to home prefix"
            ;;
    esac
    
    user_name="$(whoami)"
    
    echo "$platform:$user_prefix:$user_name"
}

# Convert platform-specific session directory to canonical format
# Examples:
#   -Users-terryli-eon-nt       -> ~eon-nt
#   -home-tca-eon-nt           -> ~eon-nt  
#   -Users-terryli--claude     -> ~-claude
#   -home-tca--claude          -> ~-claude
canonicalize_session_directory() {
    local session_dir="$1"
    
    # Validate input is a session directory name (starts with -)
    if [[ ! "$session_dir" =~ ^- ]]; then
        log "ERROR" "Invalid session directory format: $session_dir"
        return 1
    fi
    
    # Extract relative path from platform-specific encoding
    # Pattern: -[platform_prefix]-[username]-[relative_path]
    local canonical_path
    
    # Handle different platform patterns
    if [[ "$session_dir" =~ ^-Users-[^-]+-(.*)$ ]]; then
        # macOS pattern: -Users-username-relative-path
        canonical_path="${BASH_REMATCH[1]}"
    elif [[ "$session_dir" =~ ^-home-[^-]+-(.*)$ ]]; then
        # Linux pattern: -home-username-relative-path  
        canonical_path="${BASH_REMATCH[1]}"
    elif [[ "$session_dir" =~ ^-c-Users-[^-]+-(.*)$ ]]; then
        # Windows pattern: -c-Users-username-relative-path
        canonical_path="${BASH_REMATCH[1]}"
    else
        log "WARNING" "Unknown session directory pattern: $session_dir"
        # Fallback: assume it's already canonical or use as-is
        canonical_path="${session_dir#-}"
    fi
    
    # Convert to canonical format with ~ prefix
    local canonical_name="${CANONICAL_PREFIX}${canonical_path}"
    
    log "DEBUG" "Canonicalized: $session_dir -> $canonical_name"
    echo "$canonical_name"
}

# Convert current working directory to canonical session directory name
# Used for session lookup based on current workspace
workspace_to_canonical_session() {
    local workspace_path="${1:-$PWD}"
    local home_path="${2:-$HOME}"
    
    # Extract relative path from workspace
    if [[ "$workspace_path" == "$home_path"* ]]; then
        local relative_path="${workspace_path#$home_path}"
        # Remove leading slash
        relative_path="${relative_path#/}"
        
        # Convert path separators to hyphens for session directory naming
        local canonical_session="${CANONICAL_PREFIX}${relative_path//\//-}"
        
        # Special case for home directory itself (.claude)
        if [[ -z "$relative_path" ]]; then
            canonical_session="${CANONICAL_PREFIX}-home"
        elif [[ "$relative_path" == ".claude" ]]; then
            canonical_session="${CANONICAL_PREFIX}-claude"
        fi
        
        log "DEBUG" "Workspace $workspace_path -> canonical session $canonical_session"
        echo "$canonical_session"
    else
        log "ERROR" "Workspace path $workspace_path is not under home directory $home_path"
        return 1
    fi
}

# Get all platform-specific session directories that map to the same canonical directory
find_equivalent_session_directories() {
    local canonical_session="$1"
    local sessions_base_dir="$2"
    
    # Extract relative path from canonical name
    local relative_path="${canonical_session#$CANONICAL_PREFIX}"
    
    # Find all platform-specific directories that encode this relative path
    local equivalent_dirs=()
    
    # Pattern matching for different platforms
    for session_dir in "$sessions_base_dir"/-*; do
        if [[ -d "$session_dir" ]]; then
            local dir_name=$(basename "$session_dir")
            local canonical_equivalent=$(canonicalize_session_directory "$dir_name")
            
            if [[ "$canonical_equivalent" == "$canonical_session" ]]; then
                equivalent_dirs+=("$dir_name")
                log "DEBUG" "Found equivalent directory: $dir_name -> $canonical_session"
            fi
        fi
    done
    
    printf '%s\n' "${equivalent_dirs[@]}"
}

# Extract all session UUIDs from a session directory
get_session_uuids() {
    local session_dir="$1"
    
    if [[ ! -d "$session_dir" ]]; then
        return 0
    fi
    
    find "$session_dir" -name "*.jsonl" -type f | while read -r session_file; do
        local filename=$(basename "$session_file" .jsonl)
        if [[ "$filename" =~ $SESSION_UUID_PATTERN ]]; then
            echo "$filename"
        fi
    done
}

# Check if two session files have the same UUID (duplicate detection)
sessions_have_same_uuid() {
    local session_file1="$1"
    local session_file2="$2"
    
    local uuid1=$(basename "$session_file1" .jsonl)
    local uuid2=$(basename "$session_file2" .jsonl)
    
    [[ "$uuid1" == "$uuid2" ]]
}

# Merge session files with the same UUID, keeping the most recent content
merge_duplicate_sessions() {
    local session_file1="$1"
    local session_file2="$2"
    local output_file="$3"
    
    log "INFO" "Merging duplicate session files: $(basename "$session_file1") and $(basename "$session_file2")"
    
    # Get file modification times to determine which is more recent
    local time1=$(stat -f "%m" "$session_file1" 2>/dev/null || stat -c "%Y" "$session_file1" 2>/dev/null || echo "0")
    local time2=$(stat -f "%m" "$session_file2" 2>/dev/null || stat -c "%Y" "$session_file2" 2>/dev/null || echo "0")
    
    # Use the more recent file as the base
    local base_file recent_file
    if [[ "$time1" -gt "$time2" ]]; then
        base_file="$session_file1"
        recent_file="$session_file1"
    else
        base_file="$session_file2"  
        recent_file="$session_file2"
    fi
    
    # For now, use the more recent file as the merged result
    # TODO: Implement more sophisticated content merging based on JSONL timestamps
    cp "$recent_file" "$output_file"
    
    log "DEBUG" "Merged session saved to: $output_file (used more recent: $(basename "$recent_file"))"
}

# Create backup of existing session directory structure
backup_legacy_sessions() {
    local sessions_dir="$1"
    local backup_subdir="${sessions_dir}/${LEGACY_SESSION_BACKUP_DIR}"
    
    # Only backup if we haven't already created a backup
    if [[ -d "$backup_subdir" ]]; then
        log "INFO" "Legacy backup already exists at: $backup_subdir"
        return 0
    fi
    
    log "INFO" "Creating backup of legacy session directories"
    mkdir -p "$backup_subdir"
    
    # Move all platform-specific directories to backup
    for session_dir in "$sessions_dir"/-*; do
        if [[ -d "$session_dir" ]]; then
            local dir_name=$(basename "$session_dir")
            # Only backup directories that look like platform-specific encoding
            if [[ "$dir_name" =~ ^-[A-Za-z]+-[^-]+-.*$ ]]; then
                log "DEBUG" "Backing up legacy directory: $dir_name"
                mv "$session_dir" "$backup_subdir/"
            fi
        fi
    done
    
    log "INFO" "Legacy session backup completed"
}

# Migrate all platform-specific session directories to canonical format
migrate_to_canonical_sessions() {
    local sessions_dir="$1"
    local dry_run="${2:-false}"
    
    log "INFO" "Starting migration to canonical session format (dry_run=$dry_run)"
    
    if [[ "$dry_run" == "true" ]]; then
        log "INFO" "DRY RUN: No actual changes will be made"
    fi
    
    # Create backup first (unless dry run)
    if [[ "$dry_run" != "true" ]]; then
        backup_legacy_sessions "$sessions_dir"
        sessions_dir="${sessions_dir}/${LEGACY_SESSION_BACKUP_DIR}"
    fi
    
    # Collect all canonical sessions and their equivalent directories (bash 3.2 compatible)
    local canonical_sessions_file=$(mktemp)
    local equivalent_dirs_file=$(mktemp)
    
    # Build list of canonical sessions and their equivalent directories
    for session_dir in "$sessions_dir"/-*; do
        if [[ -d "$session_dir" ]]; then
            local dir_name=$(basename "$session_dir")
            local canonical_name=$(canonicalize_session_directory "$dir_name")
            
            # Store mapping: canonical_name:dir_name
            echo "$canonical_name:$dir_name" >> "$canonical_sessions_file"
        fi
    done
    
    # Get unique canonical sessions
    local unique_canonicals=$(cut -d: -f1 "$canonical_sessions_file" | sort -u)
    
    # Process each canonical session
    local migration_count=0
    local parent_sessions_dir=$(dirname "$sessions_dir")
    
    for canonical_name in $unique_canonicals; do
        # Get all equivalent directories for this canonical session
        local equivalent_dirs=$(grep "^$canonical_name:" "$canonical_sessions_file" | cut -d: -f2 | tr '\n' ' ')
        
        log "INFO" "Processing canonical session: $canonical_name"
        log "DEBUG" "  Equivalent directories: $equivalent_dirs"
        
        if [[ "$dry_run" == "true" ]]; then
            log "INFO" "  DRY RUN: Would create canonical directory: $canonical_name"
            for dir_name in $equivalent_dirs; do
                log "INFO" "    DRY RUN: Would merge sessions from: $dir_name"
            done
        else
            # Create canonical session directory
            local canonical_dir="$parent_sessions_dir/$canonical_name"
            mkdir -p "$canonical_dir"
            
            # Merge sessions from all equivalent directories (bash 3.2 compatible)
            local seen_uuids_file=$(mktemp)
            
            for dir_name in $equivalent_dirs; do
                local source_dir="$sessions_dir/$dir_name"
                log "DEBUG" "  Merging sessions from: $source_dir"
                
                # Copy all session files, handling duplicates
                for session_file in "$source_dir"/*.jsonl; do
                    if [[ -f "$session_file" ]]; then
                        local session_uuid=$(basename "$session_file" .jsonl)
                        local canonical_file="$canonical_dir/$session_uuid.jsonl"
                        
                        if ! grep -q "^$session_uuid:" "$seen_uuids_file" 2>/dev/null; then
                            # First occurrence of this UUID
                            cp "$session_file" "$canonical_file"
                            echo "$session_uuid:$canonical_file" >> "$seen_uuids_file"
                            log "DEBUG" "    Copied session: $session_uuid"
                        else
                            # Duplicate UUID - merge with existing
                            local existing_file=$(grep "^$session_uuid:" "$seen_uuids_file" | cut -d: -f2-)
                            local temp_merged=$(mktemp)
                            merge_duplicate_sessions "$existing_file" "$session_file" "$temp_merged"
                            mv "$temp_merged" "$canonical_file"
                            log "DEBUG" "    Merged duplicate session: $session_uuid"
                        fi
                    fi
                done
            done
            
            # Cleanup temporary file
            rm -f "$seen_uuids_file"
            
            ((migration_count++))
            log "INFO" "  Created canonical session: $canonical_name"
        fi
    done
    
    # Cleanup temporary files
    rm -f "$canonical_sessions_file" "$equivalent_dirs_file"
    
    log "INFO" "Migration completed. Processed $migration_count canonical sessions"
    
    if [[ "$dry_run" != "true" ]]; then
        log "INFO" "Legacy sessions backed up to: $sessions_dir"
        log "INFO" "Canonical sessions available in: $(dirname "$sessions_dir")"
    fi
}

# Find canonical session directory for current workspace
resolve_current_canonical_session() {
    local sessions_dir="${1:-$HOME/.claude/system/sessions}"
    local current_workspace="${2:-$PWD}"
    
    local canonical_session=$(workspace_to_canonical_session "$current_workspace")
    local canonical_dir="$sessions_dir/$canonical_session"
    
    if [[ -d "$canonical_dir" ]]; then
        echo "$canonical_dir"
        log "DEBUG" "Resolved current workspace to canonical session: $canonical_session"
    else
        log "DEBUG" "No canonical session found for current workspace: $canonical_session"
        return 1
    fi
}

# List all available canonical sessions with their workspace paths
list_canonical_sessions() {
    local sessions_dir="${1:-$HOME/.claude/system/sessions}"
    
    log "INFO" "Available canonical sessions:"
    
    for canonical_dir in "$sessions_dir"/${CANONICAL_PREFIX}*; do
        if [[ -d "$canonical_dir" ]]; then
            local canonical_name=$(basename "$canonical_dir")
            local relative_path="${canonical_name#$CANONICAL_PREFIX}"
            local workspace_path="$HOME/${relative_path//-/\/}"
            local session_count=$(find "$canonical_dir" -name "*.jsonl" -type f | wc -l)
            
            printf "  %-30s -> %-40s (%d sessions)\n" "$canonical_name" "$workspace_path" "$session_count"
        fi
    done
}

# Validate canonical session directory structure
validate_canonical_sessions() {
    local sessions_dir="${1:-$HOME/.claude/system/sessions}"
    local errors=0
    
    log "INFO" "Validating canonical session structure"
    
    # Check for proper canonical naming
    for session_dir in "$sessions_dir"/*; do
        if [[ -d "$session_dir" ]]; then
            local dir_name=$(basename "$session_dir")
            
            if [[ "$dir_name" == "$LEGACY_SESSION_BACKUP_DIR" ]]; then
                continue # Skip backup directory
            fi
            
            if [[ ! "$dir_name" =~ ^${CANONICAL_PREFIX} ]]; then
                log "ERROR" "Non-canonical session directory found: $dir_name"
                ((errors++))
            fi
        fi
    done
    
    # Check for valid session files
    for canonical_dir in "$sessions_dir"/${CANONICAL_PREFIX}*; do
        if [[ -d "$canonical_dir" ]]; then
            local canonical_name=$(basename "$canonical_dir")
            local session_files=$(find "$canonical_dir" -name "*.jsonl" -type f | wc -l)
            
            if [[ "$session_files" -eq 0 ]]; then
                log "WARNING" "Empty canonical session directory: $canonical_name"
            else
                log "DEBUG" "Canonical session $canonical_name contains $session_files session files"
            fi
        fi
    done
    
    if [[ "$errors" -eq 0 ]]; then
        log "INFO" "Canonical session structure validation passed"
    else
        log "ERROR" "Canonical session structure validation failed with $errors errors"
    fi
    
    return "$errors"
}

# Main function to execute canonical session management operations
main_canonical_session_management() {
    local operation="${1:-help}"
    local sessions_dir="${2:-$HOME/.claude/system/sessions}"
    
    case "$operation" in
        "migrate")
            migrate_to_canonical_sessions "$sessions_dir" "${3:-false}"
            ;;
        "migrate-dry-run")
            migrate_to_canonical_sessions "$sessions_dir" "true"
            ;;
        "resolve")
            resolve_current_canonical_session "$sessions_dir" "${3:-$PWD}"
            ;;
        "list")
            list_canonical_sessions "$sessions_dir"
            ;;
        "validate")
            validate_canonical_sessions "$sessions_dir"
            ;;
        "canonicalize")
            canonicalize_session_directory "${2:-}"
            ;;
        *)
            echo "Usage: $0 {migrate|migrate-dry-run|resolve|list|validate|canonicalize} [sessions_dir] [args...]"
            echo "  migrate [sessions_dir] [dry_run]     - Migrate platform-specific sessions to canonical format"
            echo "  migrate-dry-run [sessions_dir]       - Show what migration would do without making changes"
            echo "  resolve [sessions_dir] [workspace]   - Find canonical session for current/specified workspace"
            echo "  list [sessions_dir]                  - List all canonical sessions with workspace mappings"
            echo "  validate [sessions_dir]              - Validate canonical session directory structure"
            echo "  canonicalize [session_dir_name]      - Convert platform-specific name to canonical format"
            ;;
    esac
}

# If script is run directly (not sourced), execute main function
if [[ "${BASH_SOURCE[0]:-}" == "${0}" ]]; then
    main_canonical_session_management "$@"
fi