#!/bin/bash
# SAGE Sync Workspace Operations - Modularized Functions
# Rollback Reference: c80d866 (pre-MHR modularization snapshot)
# Part of SAGE Sync Infrastructure - Bulletproof Session Preservation

# Defensive Truth: Workspace sync with git backup prevents local changes loss
# Never overwrite local changes without creating recoverable backup branches
push_workspace() {
    section "Pushing Workspace to Remote"
    
    if [[ $DRY_RUN == true ]]; then
        log "INFO" "DRY RUN: Would push $LOCAL_WORKSPACE/ to $REMOTE_HOST:$REMOTE_WORKSPACE/"
        rsync -avzn --delete --stats "$LOCAL_WORKSPACE/" "$REMOTE_HOST:$REMOTE_WORKSPACE/" | tee -a "$LOG_FILE"
        return 0
    fi
    
    progress "Starting workspace push..."
    
    # Pre-sync validation
    local local_files=$(find "$LOCAL_WORKSPACE" -type f | wc -l)
    local local_size=$(du -sk "$LOCAL_WORKSPACE" | cut -f1)
    
    log "INFO" "Local workspace: $local_files files, ${local_size}KB"
    
    # Execute rsync with comprehensive logging
    local rsync_cmd="rsync -avz --delete --stats --human-readable --progress"
    
    if [[ $VERBOSE == true ]]; then
        rsync_cmd="$rsync_cmd --verbose"
    fi
    
    log "DEBUG" "Executing: $rsync_cmd \"$LOCAL_WORKSPACE/\" \"$REMOTE_HOST:$REMOTE_WORKSPACE/\""
    
    if $rsync_cmd "$LOCAL_WORKSPACE/" "$REMOTE_HOST:$REMOTE_WORKSPACE/" 2>&1 | tee -a "$LOG_FILE"; then
        # Post-sync validation
        local remote_files=$(ssh "$REMOTE_HOST" "find $REMOTE_WORKSPACE -type f | wc -l" 2>/dev/null || echo "0")
        local remote_size=$(ssh "$REMOTE_HOST" "du -sk $REMOTE_WORKSPACE | cut -f1" 2>/dev/null || echo "0")
        
        log "INFO" "Remote workspace after sync: $remote_files files, ${remote_size}KB"
        
        if [[ $local_files -eq $remote_files ]]; then
            log "SUCCESS" "Workspace push completed successfully"
            log "INFO" "File count matches: $local_files files"
        else
            log "WARNING" "File count mismatch: local=$local_files, remote=$remote_files"
            log "INFO" "This may be normal if .gitignore patterns differ"
        fi
    else
        log "ERROR" "Workspace push failed"
        return 1
    fi
}

# Defensive Truth: Pull workspace requires backup of local changes first
# Git backup branches prevent loss of uncommitted work during sync operations
pull_workspace() {
    section "Pulling Workspace from Remote"
    
    if [[ $DRY_RUN == true ]]; then
        log "INFO" "DRY RUN: Would pull $REMOTE_HOST:$REMOTE_WORKSPACE/ to $LOCAL_WORKSPACE/"
        rsync -avzn --delete --stats "$REMOTE_HOST:$REMOTE_WORKSPACE/" "$LOCAL_WORKSPACE/" | tee -a "$LOG_FILE"
        return 0
    fi
    
    progress "Starting workspace pull..."
    
    # Backup local changes if they exist - CRITICAL for data preservation
    if [[ -d "$LOCAL_WORKSPACE/.git" ]]; then
        progress "Checking for local changes..."
        cd "$LOCAL_WORKSPACE"
        if ! git diff --quiet || ! git diff --cached --quiet; then
            local backup_branch="backup-before-pull-$(date +%Y%m%d-%H%M%S)"
            log "WARNING" "Local changes detected, creating backup branch: $backup_branch"
            git checkout -b "$backup_branch" && git add -A && git commit -m "Backup before pull sync" || {
                log "ERROR" "Failed to create backup branch"
                return 1
            }
            git checkout master
        fi
    fi
    
    # Pre-sync validation
    local remote_files=$(ssh "$REMOTE_HOST" "find $REMOTE_WORKSPACE -type f | wc -l" 2>/dev/null || echo "0")
    local remote_size=$(ssh "$REMOTE_HOST" "du -sk $REMOTE_WORKSPACE | cut -f1" 2>/dev/null || echo "0")
    
    log "INFO" "Remote workspace: $remote_files files, ${remote_size}KB"
    
    # Execute rsync
    local rsync_cmd="rsync -avz --delete --stats --human-readable --progress"
    
    if [[ $VERBOSE == true ]]; then
        rsync_cmd="$rsync_cmd --verbose"
    fi
    
    log "DEBUG" "Executing: $rsync_cmd \"$REMOTE_HOST:$REMOTE_WORKSPACE/\" \"$LOCAL_WORKSPACE/\""
    
    if $rsync_cmd "$REMOTE_HOST:$REMOTE_WORKSPACE/" "$LOCAL_WORKSPACE/" 2>&1 | tee -a "$LOG_FILE"; then
        # Post-sync validation
        local local_files=$(find "$LOCAL_WORKSPACE" -type f | wc -l)
        local local_size=$(du -sk "$LOCAL_WORKSPACE" | cut -f1)
        
        log "INFO" "Local workspace after sync: $local_files files, ${local_size}KB"
        log "SUCCESS" "Workspace pull completed successfully"
    else
        log "ERROR" "Workspace pull failed"
        return 1
    fi
}