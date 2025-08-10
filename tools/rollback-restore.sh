#!/bin/bash
# SAGE Sync Emergency Rollback & Restore System
# Restores sessions from emergency backups
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

# List available backups
list_available_backups() {
    echo "📋 Available Emergency Backups:"
    echo "==============================="
    
    local backup_count=0
    for manifest in "$BACKUP_BASE_DIR"/emergency/manifest_*.json; do
        if [[ -f "$manifest" ]]; then
            local timestamp=$(jq -r '.backup_timestamp' "$manifest")
            local created_at=$(jq -r '.created_at' "$manifest")
            local local_count=$(jq -r '.local_backup.session_count' "$manifest")
            local remote_count=$(jq -r '.remote_backup.session_count' "$manifest")
            local local_size=$(jq -r '.local_backup.size' "$manifest")
            
            echo "🕐 Backup: $timestamp"
            echo "   📅 Created: $created_at"
            echo "   📊 Sessions: Local=$local_count, Remote=$remote_count"
            echo "   💾 Size: $local_size"
            echo "   🔄 Restore: $0 $timestamp"
            echo ""
            
            ((backup_count++))
        fi
    done
    
    if [[ $backup_count -eq 0 ]]; then
        log_warning "No emergency backups found in $BACKUP_BASE_DIR/emergency/"
        return 1
    fi
    
    return 0
}

# Validate backup exists and is intact
validate_backup() {
    local timestamp="$1"
    local manifest_file="$BACKUP_BASE_DIR/emergency/manifest_$timestamp.json"
    
    if [[ ! -f "$manifest_file" ]]; then
        log_error "Backup manifest not found: $manifest_file"
        return 1
    fi
    
    # Read backup paths from manifest
    local local_backup_path=$(jq -r '.local_backup.path' "$manifest_file")
    local remote_backup_path=$(jq -r '.remote_backup.path' "$manifest_file")
    
    # Validate local backup
    if [[ ! -d "$local_backup_path" ]]; then
        log_error "Local backup directory not found: $local_backup_path"
        return 1
    fi
    
    # Validate remote backup
    if ! ssh "$REMOTE_HOST" "[[ -d $remote_backup_path ]]"; then
        log_error "Remote backup directory not found: $remote_backup_path"
        return 1
    fi
    
    log_success "Backup validation passed for timestamp: $timestamp"
    return 0
}

# Create safety backup of current state before restore
create_pre_restore_backup() {
    local timestamp="$1"
    local pre_restore_timestamp="pre_restore_${timestamp}_$(date +%H%M%S)"
    
    log_info "Creating pre-restore safety backup: $pre_restore_timestamp"
    
    # Use the emergency backup system to backup current state
    if "$HOME/.claude/tools/emergency-backup.sh" create >/dev/null 2>&1; then
        log_success "Pre-restore safety backup created"
        return 0
    else
        log_error "Failed to create pre-restore safety backup"
        return 1
    fi
}

# Restore local sessions
restore_local_sessions() {
    local timestamp="$1"
    local manifest_file="$BACKUP_BASE_DIR/emergency/manifest_$timestamp.json"
    local backup_path=$(jq -r '.local_backup.path' "$manifest_file")
    
    log_info "Restoring local sessions from: $backup_path"
    
    # Backup current sessions first
    if [[ -d "$SESSIONS_DIR" ]]; then
        local current_backup="$SESSIONS_DIR.backup.$(date +%H%M%S)"
        mv "$SESSIONS_DIR" "$current_backup"
        log_info "Current sessions backed up to: $current_backup"
    fi
    
    # Restore from backup
    if [[ -d "$backup_path/sessions" ]]; then
        cp -r "$backup_path/sessions" "$SESSIONS_DIR"
        
        # Verify restore
        local restored_count=$(find "$SESSIONS_DIR" -name "*.json" 2>/dev/null | wc -l)
        local expected_count=$(jq -r '.local_backup.session_count' "$manifest_file")
        
        if [[ "$restored_count" -eq "$expected_count" ]]; then
            log_success "Local sessions restored: $restored_count files"
            return 0
        else
            log_error "Local restore verification failed: $restored_count vs $expected_count"
            return 1
        fi
    else
        log_error "Backup sessions directory not found: $backup_path/sessions"
        return 1
    fi
}

# Restore remote sessions
restore_remote_sessions() {
    local timestamp="$1"
    local manifest_file="$BACKUP_BASE_DIR/emergency/manifest_$timestamp.json"
    local backup_path=$(jq -r '.remote_backup.path' "$manifest_file")
    
    log_info "Restoring remote sessions from: $backup_path"
    
    # Create remote restore script
    local remote_script=$(cat << 'EOF'
# Backup current sessions
if [[ -d ~/.claude/system/sessions ]]; then
    mv ~/.claude/system/sessions ~/.claude/system/sessions.backup.$(date +%H%M%S)
fi

# Restore from backup
if [[ -d BACKUP_PATH/sessions ]]; then
    cp -r BACKUP_PATH/sessions ~/.claude/system/sessions
    echo "Remote sessions restored successfully"
else
    echo "ERROR: Backup sessions directory not found"
    exit 1
fi
EOF
)
    
    # Replace BACKUP_PATH placeholder and execute on remote
    if ssh "$REMOTE_HOST" "${remote_script//BACKUP_PATH/$backup_path}"; then
        # Verify remote restore
        local restored_count=$(ssh "$REMOTE_HOST" "find ~/.claude/system/sessions -name '*.json' 2>/dev/null | wc -l")
        local expected_count=$(jq -r '.remote_backup.session_count' "$manifest_file")
        
        if [[ "$restored_count" -eq "$expected_count" ]]; then
            log_success "Remote sessions restored: $restored_count files"
            return 0
        else
            log_error "Remote restore verification failed: $restored_count vs $expected_count"
            return 1
        fi
    else
        log_error "Failed to execute remote restore"
        return 1
    fi
}

# Main restore function
restore_from_backup() {
    local timestamp="$1"
    local restore_local="${2:-true}"
    local restore_remote="${3:-true}"
    
    echo "🔄 SAGE EMERGENCY RESTORE SYSTEM"
    echo "================================="
    log_info "Restoring from backup timestamp: $timestamp"
    
    # Validate backup exists
    if ! validate_backup "$timestamp"; then
        return 1
    fi
    
    # Create pre-restore safety backup
    if ! create_pre_restore_backup "$timestamp"; then
        log_warning "Pre-restore backup failed, but continuing with restore"
    fi
    
    # Restore local sessions
    if [[ "$restore_local" == "true" ]]; then
        if ! restore_local_sessions "$timestamp"; then
            log_error "Local session restore failed"
            return 1
        fi
    fi
    
    # Restore remote sessions
    if [[ "$restore_remote" == "true" ]]; then
        if ! restore_remote_sessions "$timestamp"; then
            log_error "Remote session restore failed"
            return 1
        fi
    fi
    
    echo ""
    echo "✅ EMERGENCY RESTORE COMPLETED SUCCESSFULLY"
    echo "🕐 Restored from backup: $timestamp"
    echo "📁 Local sessions: $(find "$SESSIONS_DIR" -name "*.json" 2>/dev/null | wc -l) files"
    echo "📁 Remote sessions: $(ssh "$REMOTE_HOST" "find ~/.claude/system/sessions -name '*.json' 2>/dev/null | wc -l" 2>/dev/null || echo "unknown") files"
    echo ""
    
    return 0
}

# Interactive restore with confirmation
interactive_restore() {
    local timestamp="$1"
    
    echo "🚨 EMERGENCY RESTORE CONFIRMATION"
    echo "=================================="
    echo "⚠️  This will REPLACE current sessions with backup data"
    echo "🕐 Backup timestamp: $timestamp"
    echo "💾 Current sessions will be backed up before restore"
    echo ""
    
    # Show backup details
    local manifest_file="$BACKUP_BASE_DIR/emergency/manifest_$timestamp.json"
    if [[ -f "$manifest_file" ]]; then
        local created_at=$(jq -r '.created_at' "$manifest_file")
        local local_count=$(jq -r '.local_backup.session_count' "$manifest_file")
        local remote_count=$(jq -r '.remote_backup.session_count' "$manifest_file")
        
        echo "📊 Backup contains:"
        echo "   Local sessions: $local_count files"
        echo "   Remote sessions: $remote_count files"
        echo "   Created: $created_at"
        echo ""
    fi
    
    echo "🛑 To proceed, type: 'I UNDERSTAND RESTORE WILL REPLACE CURRENT SESSIONS'"
    read -p "Confirmation: " user_input
    
    if [[ "$user_input" != "I UNDERSTAND RESTORE WILL REPLACE CURRENT SESSIONS" ]]; then
        echo "❌ Restore cancelled - current sessions preserved"
        return 1
    fi
    
    restore_from_backup "$timestamp"
}

# Script execution
case "${1:-list}" in
    "list")
        list_available_backups
        ;;
    "test")
        log_info "Testing restore system..."
        if list_available_backups >/dev/null; then
            log_success "Restore system test PASSED - backups available"
        else
            log_warning "No backups available for testing"
        fi
        ;;
    *)
        if [[ $# -eq 0 ]]; then
            echo "Usage: $0 [list|test|TIMESTAMP]"
            echo "  list      - List available backups"
            echo "  test      - Test restore system"
            echo "  TIMESTAMP - Restore from specific backup (requires confirmation)"
            exit 1
        else
            # Restore from specific timestamp
            timestamp="$1"
            interactive_restore "$timestamp"
        fi
        ;;
esac