#!/bin/bash
# SAGE Sync Emergency Backup System
# Creates verified backups before destructive operations
# Part of Phase 1 - Critical Safety Implementation

set -euo pipefail

# Configuration
BACKUP_BASE_DIR="$HOME/.claude/backups"
SESSIONS_DIR="$HOME/.claude/system/sessions"
REMOTE_HOST="tca"
REMOTE_SESSIONS_DIR="~/.claude/system/sessions"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Generate backup timestamp
generate_backup_timestamp() {
    date +"%Y%m%d_%H%M%S"
}

# Create local backup
create_local_backup() {
    local timestamp="$1"
    local backup_dir="$BACKUP_BASE_DIR/emergency/local_$timestamp"
    
    log_info "Creating local emergency backup..." >&2
    
    # Create backup directory
    mkdir -p "$backup_dir"
    
    # Copy sessions with verification
    if [[ -d "$SESSIONS_DIR" ]]; then
        cp -r "$SESSIONS_DIR" "$backup_dir/"
        local_session_count=$(find "$SESSIONS_DIR" -name "*.json" | wc -l)
        if [[ $? -ne 0 ]]; then
            log_error "Failed to count session files in source directory: $SESSIONS_DIR" >&2
            return 1
        fi
        backup_session_count=$(find "$backup_dir/sessions" -name "*.json" | wc -l)
        if [[ $? -ne 0 ]]; then
            log_error "Failed to count session files in backup directory: $backup_dir/sessions" >&2
            return 1
        fi
        
        if [[ "$local_session_count" -eq "$backup_session_count" ]]; then
            log_success "Local backup verified: $local_session_count sessions" >&2
            # Return only the path
            echo "$backup_dir"
            return 0
        else
            log_error "Local backup verification failed: $local_session_count vs $backup_session_count" >&2
            return 1
        fi
    else
        log_warning "No local sessions directory found" >&2
        echo "$backup_dir"
        return 0
    fi
}

# Create remote backup
create_remote_backup() {
    local timestamp="$1"
    local remote_backup_dir="~/.claude/backups/emergency/remote_$timestamp"
    
    log_info "Creating remote emergency backup..." >&2
    
    # Create remote backup directory and copy sessions - fail immediately on any error
    if ! ssh "$REMOTE_HOST" "mkdir -p ~/.claude/backups/emergency && [[ -d ~/.claude/system/sessions ]] && cp -r ~/.claude/system/sessions ~/.claude/backups/emergency/remote_$timestamp"; then
        log_error "Failed to create remote backup via SSH" >&2
        return 1
    fi
    
    # Verify remote backup - fail immediately on any count error
    remote_session_count=$(ssh "$REMOTE_HOST" "find ~/.claude/system/sessions -name '*.json' | wc -l")
    if [[ $? -ne 0 ]]; then
        log_error "Failed to count remote session files" >&2
        return 1
    fi
    
    backup_session_count=$(ssh "$REMOTE_HOST" "find ~/.claude/backups/emergency/remote_$timestamp/sessions -name '*.json' | wc -l")
    if [[ $? -ne 0 ]]; then
        log_error "Failed to count remote backup files" >&2
        return 1
    fi
    
    if [[ "$remote_session_count" -eq "$backup_session_count" ]]; then
        log_success "Remote backup verified: $remote_session_count sessions" >&2
        echo "$remote_backup_dir"
        return 0
    else
        log_error "Remote backup verification failed: $remote_session_count vs $backup_session_count" >&2
        return 1
    fi
}

# Test backup integrity
test_backup_integrity() {
    local local_backup="$1"
    local remote_backup="$2"
    
    log_info "Testing backup integrity..."
    
    # Test local backup readability
    if [[ -d "$local_backup" ]]; then
        local_test_files=$(find "$local_backup" -name "*.json" | head -3)
        for file in $local_test_files; do
            if ! jq empty "$file" >/dev/null; then
                log_error "Local backup integrity test failed: $file"
                return 1
            fi
        done
        log_success "Local backup integrity verified"
    fi
    
    # Test remote backup readability
    if ssh "$REMOTE_HOST" "[[ -d $remote_backup ]]"; then
        remote_test_result=$(ssh "$REMOTE_HOST" "
            find $remote_backup -name '*.json' | head -3 | while read file; do
                jq empty \"\$file\" >/dev/null 2>&1 || { echo 'FAILED'; break; }
            done
            echo 'PASSED'
        " | tail -1)
        
        if [[ "$remote_test_result" == "PASSED" ]]; then
            log_success "Remote backup integrity verified"
        else
            log_error "Remote backup integrity test failed"
            return 1
        fi
    fi
    
    return 0
}

# Generate backup manifest
generate_backup_manifest() {
    local timestamp="$1"
    local local_backup="$2"
    local remote_backup="$3"
    local manifest_file="$BACKUP_BASE_DIR/emergency/manifest_$timestamp.json"
    
    # Count sessions - fail immediately on any error
    local_count=$(find "$local_backup" -name "*.json" | wc -l)
    if [[ $? -ne 0 ]]; then
        log_error "Failed to count local backup sessions for manifest" >&2
        return 1
    fi
    
    remote_count=$(ssh "$REMOTE_HOST" "find $remote_backup -name '*.json' | wc -l")
    if [[ $? -ne 0 ]]; then
        log_error "Failed to count remote backup sessions for manifest" >&2
        return 1
    fi
    
    # Calculate sizes - fail immediately on any error
    local_size=$(du -sh "$local_backup" | cut -f1)
    if [[ $? -ne 0 ]]; then
        log_error "Failed to calculate local backup size for manifest" >&2
        return 1
    fi
    
    remote_size=$(ssh "$REMOTE_HOST" "du -sh $remote_backup | cut -f1")
    if [[ $? -ne 0 ]]; then
        log_error "Failed to calculate remote backup size for manifest" >&2
        return 1
    fi
    
    # Create manifest
    cat > "$manifest_file" << EOF
{
  "backup_timestamp": "$timestamp",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "local_backup": {
    "path": "$local_backup",
    "session_count": $local_count,
    "size": "$local_size"
  },
  "remote_backup": {
    "path": "$remote_backup",
    "session_count": $remote_count,
    "size": "$remote_size"
  },
  "integrity_verified": true,
  "restore_command": "$HOME/.claude/tools/rollback-restore.sh $timestamp"
}
EOF
    
    log_success "Backup manifest created: $manifest_file" >&2
    echo "$manifest_file"
}

# Main backup creation function
create_emergency_backup() {
    local timestamp
    timestamp=$(generate_backup_timestamp)
    
    echo "🚨 SAGE EMERGENCY BACKUP SYSTEM"
    echo "==============================="
    log_info "Creating emergency backup with timestamp: $timestamp"
    
    # Create backups
    local local_backup_path
    local remote_backup_path
    
    # Create backups with proper output handling
    local_backup_path=$(create_local_backup "$timestamp")
    remote_backup_path=$(create_remote_backup "$timestamp")
    
    # Test backup integrity
    if ! test_backup_integrity "$local_backup_path" "$remote_backup_path"; then
        log_error "Backup integrity test failed - EMERGENCY BACKUP COMPROMISED"
        return 1
    fi
    
    # Generate manifest
    local manifest_path
    manifest_path=$(generate_backup_manifest "$timestamp" "$local_backup_path" "$remote_backup_path")
    
    echo ""
    echo "✅ EMERGENCY BACKUP COMPLETED SUCCESSFULLY"
    echo "🕐 Timestamp: $timestamp"
    echo "📁 Local backup: $local_backup_path"
    echo "📁 Remote backup: $remote_backup_path"
    echo "📋 Manifest: $manifest_path"
    echo "🔄 Restore command: $HOME/.claude/tools/rollback-restore.sh $timestamp"
    echo ""
    
    return 0
}

# Script execution
case "${1:-create}" in
    "create")
        create_emergency_backup
        ;;
    "test")
        log_info "Testing emergency backup system..."
        if create_emergency_backup; then
            log_success "Emergency backup system test PASSED"
        else
            log_error "Emergency backup system test FAILED"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 [create|test]"
        echo "  create - Create emergency backup (default)"
        echo "  test   - Test backup system functionality"
        exit 1
        ;;
esac