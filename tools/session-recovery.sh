#!/bin/bash
# Claude Session Recovery Script
# Migrates sessions from custom system/sessions/ to official ~/.claude/projects/

set -euo pipefail

CLAUDE_DIR="/home/tca/.claude"
SOURCE_DIR="$CLAUDE_DIR/system/sessions"
TARGET_DIR="$CLAUDE_DIR/projects"

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

migrate_sessions() {
    local source_path="$1"
    local target_path="$2"
    
    if [[ ! -d "$source_path" ]]; then
        log "SKIP: $source_path (not a directory)"
        return 0
    fi
    
    local session_count
    session_count=$(find "$source_path" -name "*.jsonl" -type f | wc -l)
    
    if [[ $session_count -eq 0 ]]; then
        log "SKIP: $source_path (no sessions)"
        return 0
    fi
    
    log "MIGRATE: $source_path -> $target_path ($session_count sessions)"
    
    # Create target directory
    mkdir -p "$target_path"
    
    # Copy all .jsonl files with timestamp preservation
    find "$source_path" -name "*.jsonl" -type f -exec cp -p {} "$target_path/" \;
    
    log "✅ Migrated $session_count sessions to $target_path"
}

main() {
    log "🔄 Starting Claude Session Recovery"
    log "Source: $SOURCE_DIR"
    log "Target: $TARGET_DIR"
    
    # Ensure target directory exists
    mkdir -p "$TARGET_DIR"
    
    # Find all session directories in system/sessions/
    while IFS= read -r -d '' session_dir; do
        local dir_name
        dir_name=$(basename "$session_dir")
        
        # Convert directory names to official format
        case "$dir_name" in
            # Ubuntu paths (current machine)
            "-home-tca--claude")
                migrate_sessions "$session_dir" "$TARGET_DIR/-home-tca--claude"
                ;;
            "--home-tca-eon-nt"|"-home-tca-eon-nt")
                migrate_sessions "$session_dir" "$TARGET_DIR/-home-tca-eon-nt"
                ;;
            "-home-tca-scripts")
                migrate_sessions "$session_dir" "$TARGET_DIR/-home-tca-scripts"
                ;;
            
            # macOS paths (synced from remote)
            "-Users-terryli--claude")
                migrate_sessions "$session_dir" "$TARGET_DIR/-Users-terryli--claude"
                ;;
            "-Users-terryli-eon-nt")
                migrate_sessions "$session_dir" "$TARGET_DIR/-Users-terryli-eon-nt"
                ;;
            "-Users-terryli-scripts")
                migrate_sessions "$session_dir" "$TARGET_DIR/-Users-terryli-scripts"
                ;;
            "-Users-terryli-"*)
                # All other macOS project paths
                migrate_sessions "$session_dir" "$TARGET_DIR/$dir_name"
                ;;
            
            # Canonical format (tilde-prefixed)
            "~"*)
                migrate_sessions "$session_dir" "$TARGET_DIR/$dir_name"
                ;;
            
            # Special directories
            "projects")
                # Handle nested projects directory
                find "$session_dir" -mindepth 1 -maxdepth 1 -type d | while IFS= read -r nested_dir; do
                    local nested_name
                    nested_name=$(basename "$nested_dir")
                    migrate_sessions "$nested_dir" "$TARGET_DIR/$nested_name"
                done
                ;;
            
            "legacy")
                # Handle legacy directory
                find "$session_dir" -mindepth 1 -maxdepth 1 -type d | while IFS= read -r legacy_dir; do
                    local legacy_name
                    legacy_name=$(basename "$legacy_dir")
                    migrate_sessions "$legacy_dir" "$TARGET_DIR/$legacy_name"
                done
                ;;
            
            *)
                log "UNKNOWN: $dir_name - migrating as-is"
                migrate_sessions "$session_dir" "$TARGET_DIR/$dir_name"
                ;;
        esac
        
    done < <(find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 -type d -print0)
    
    # Summary
    local total_sessions
    total_sessions=$(find "$TARGET_DIR" -name "*.jsonl" -type f | wc -l)
    local total_dirs
    total_dirs=$(find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
    
    log "✅ RECOVERY COMPLETE"
    log "📊 Total sessions: $total_sessions"
    log "📁 Total directories: $total_dirs"
    log "📂 Location: $TARGET_DIR"
    
    # Show directory structure
    log ""
    log "📋 Directory structure:"
    ls -1 "$TARGET_DIR" | head -20
    if [[ $(ls -1 "$TARGET_DIR" | wc -l) -gt 20 ]]; then
        log "... and $(($(ls -1 "$TARGET_DIR" | wc -l) - 20)) more directories"
    fi
}

main "$@"
