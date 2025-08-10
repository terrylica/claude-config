#!/bin/bash
# SAGE Sync Core Library - Modularized Functions
# Rollback Reference: c80d866 (pre-MHR modularization snapshot)
# Part of SAGE Sync Infrastructure - Bulletproof Session Preservation

# Defensive Truth: Always validate environment before destructive operations
# This prevents silent failures that could lead to data loss or sync corruption
validate_environment() {
    section "Environment Validation"
    
    local errors=0
    
    # Check local workspace
    if [[ ! -d "$LOCAL_WORKSPACE" ]]; then
        log "ERROR" "Local workspace not found: $LOCAL_WORKSPACE"
        ((errors++))
    else
        log "SUCCESS" "Local workspace found: $LOCAL_WORKSPACE"
    fi
    
    # Check Claude directory
    if [[ ! -d "$CLAUDE_DIR" ]]; then
        log "ERROR" "Claude directory not found: $CLAUDE_DIR"
        ((errors++))
    else
        log "SUCCESS" "Claude directory found: $CLAUDE_DIR"
    fi
    
    # Check required commands
    local required_commands=("rsync" "ssh")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log "ERROR" "Required command not found: $cmd"
            ((errors++))
        else
            log "DEBUG" "Command available: $cmd"
        fi
    done
    
    # Check git availability for workspace backup (optional)
    if command -v "git" &> /dev/null; then
        log "DEBUG" "Command available: git (for workspace backup)"
    else
        log "DEBUG" "Git not available (workspace backup disabled)"
    fi
    
    # Test SSH connection
    log "DEBUG" "REMOTE_HOST variable is: $REMOTE_HOST"
    progress "Testing SSH connection to $REMOTE_HOST..."
    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$REMOTE_HOST" "echo 'SSH connection successful'" &>/dev/null; then
        log "SUCCESS" "SSH connection to $REMOTE_HOST successful"
    else
        log "ERROR" "SSH connection to $REMOTE_HOST failed"
        log "INFO" "Troubleshooting: Check ZeroTier connection with 'sudo zerotier-cli peers'"
        ((errors++))
    fi
    
    # Check remote workspace
    if ssh -o ConnectTimeout=10 "$REMOTE_HOST" "test -d $REMOTE_WORKSPACE" &>/dev/null; then
        log "SUCCESS" "Remote workspace found: $REMOTE_WORKSPACE"
    else
        log "WARNING" "Remote workspace not found, will create: $REMOTE_WORKSPACE"
        if [[ $DRY_RUN == false ]]; then
            ssh "$REMOTE_HOST" "mkdir -p $REMOTE_WORKSPACE" || {
                log "ERROR" "Failed to create remote workspace"
                ((errors++))
            }
        fi
    fi
    
    # Check disk space
    local local_space=$(df "$HOME" | awk 'NR==2 {print $4}')
    local remote_space=$(ssh "$REMOTE_HOST" "df ~ | awk 'NR==2 {print \$4}'" 2>/dev/null || echo "0")
    
    log "INFO" "Local disk space available: ${local_space}KB"
    log "INFO" "Remote disk space available: ${remote_space}KB"
    
    if [[ $local_space -lt 1000000 ]]; then  # Less than 1GB
        log "WARNING" "Low local disk space: ${local_space}KB"
    fi
    
    if [[ $remote_space -lt 1000000 ]]; then  # Less than 1GB
        log "WARNING" "Low remote disk space: ${remote_space}KB"
    fi
    
    if [[ $errors -gt 0 ]]; then
        log "ERROR" "Environment validation failed with $errors errors"
        return 1
    fi
    
    log "SUCCESS" "Environment validation passed"
    return 0
}

# Defensive Truth: Session sync with path corruption protection is essential
# Claude Code creates mangled session directory names that break remote environments
sync_claude_sessions() {
    section "Syncing Claude Sessions"
    
    # Check if Claude sessions directory exists
    if [[ ! -d "$CLAUDE_SESSIONS_DIR" ]]; then
        log "WARNING" "No Claude sessions directory found at $CLAUDE_SESSIONS_DIR"
        log "INFO" "Creating empty sessions directory"
        if [[ $DRY_RUN == false ]]; then
            mkdir -p "$CLAUDE_SESSIONS_DIR" || {
                log "ERROR" "Failed to create Claude sessions directory"
                return 1
            }
        fi
    fi
    
    # Count local sessions
    local local_sessions=$(find "$CLAUDE_SESSIONS_DIR/" -name "*.jsonl" -o -name "*.json" 2>/dev/null | wc -l)
    local local_size=$(du -sk "$CLAUDE_SESSIONS_DIR/" 2>/dev/null | cut -f1 || echo "0")
    
    log "INFO" "Local Claude sessions: $local_sessions files, ${local_size}KB"
    
    if [[ $DRY_RUN == true ]]; then
        log "INFO" "DRY RUN: Would sync Claude sessions to remote"
        rsync -avzn --delete --exclude='-*' --include='*.json' --include='*.jsonl' --include='projects/' "$CLAUDE_SESSIONS_DIR/" "$REMOTE_HOST:$REMOTE_SESSIONS_DIR/" | tee -a "$LOG_FILE"
        return 0
    fi
    
    # Execute rsync session sync with path corruption protection
    progress "Syncing Claude sessions to remote..."
    
    # Use merge strategy instead of --delete to preserve remote sessions  
    # --update only transfers files that are newer or don't exist on remote
    # This prevents accidental deletion of remote-only sessions
    local rsync_cmd="rsync -avz --update --stats --human-readable"
    
    # Exclude problematic directory-named sessions that cause path conflicts
    # This prevents GPU workstation errors from malformed directory names
    rsync_cmd="$rsync_cmd --exclude='-*' --include='*.json' --include='*.jsonl' --include='projects/'"
    
    if [[ $VERBOSE == true ]]; then
        rsync_cmd="$rsync_cmd --progress"
    fi
    
    log "DEBUG" "Executing: $rsync_cmd \"$CLAUDE_SESSIONS_DIR/\" \"$REMOTE_HOST:$REMOTE_SESSIONS_DIR/\""
    
    if $rsync_cmd "$CLAUDE_SESSIONS_DIR/" "$REMOTE_HOST:$REMOTE_SESSIONS_DIR/" 2>&1 | tee -a "$LOG_FILE"; then
        # Post-sync validation
        local remote_sessions=$(ssh -o ConnectTimeout=10 "$REMOTE_HOST" "find $REMOTE_SESSIONS_DIR/ -name '*.jsonl' -o -name '*.json' | wc -l" 2>/dev/null || echo "0")
        local remote_size=$(ssh -o ConnectTimeout=10 "$REMOTE_HOST" "du -sk $REMOTE_SESSIONS_DIR/ | cut -f1" 2>/dev/null || echo "0")
        
        log "INFO" "Remote Claude sessions after sync: $remote_sessions files, ${remote_size}KB"
        
        if [[ $local_sessions -eq $remote_sessions ]]; then
            log "SUCCESS" "Claude sessions sync completed successfully"
            log "INFO" "Session count matches: $local_sessions files"
        else
            log "WARNING" "Session count mismatch: local=$local_sessions, remote=$remote_sessions"
            log "INFO" "This may indicate sync issues or network problems"
        fi
    else
        log "ERROR" "Claude sessions sync failed"
        return 1
    fi
}

# Defensive Truth: SAGE model status checks prevent deployment failures
# Always verify model availability before assuming sync success
check_sage_status() {
    section "SAGE Models Status Check"
    
    # Local models
    log "INFO" "Checking local models..."
    
    local models=("alphaforge" "catch22" "tsfresh" "nautilus_trader" "data-source-manager" "finplot")
    for model in "${models[@]}"; do
        if [[ -d "$LOCAL_WORKSPACE/repos/$model" ]]; then
            log "SUCCESS" "Local $model: Available"
        else
            log "WARNING" "Local $model: Missing"
        fi
    done
    
    # Python packages
    cd "$LOCAL_WORKSPACE"
    for pkg in "pycatch22" "tsfresh"; do
        if uv run python -c "import $pkg; print('$pkg available')" &>/dev/null; then
            log "SUCCESS" "Local $pkg: Available"
        else
            log "WARNING" "Local $pkg: Not installed"
        fi
    done
    
    # Remote models (if accessible)
    log "INFO" "Checking remote models..."
    
    if ssh -o ConnectTimeout=5 "$REMOTE_HOST" "test -d $REMOTE_WORKSPACE" &>/dev/null; then
        for model in "${models[@]}"; do
            if ssh "$REMOTE_HOST" "test -d $REMOTE_WORKSPACE/repos/$model" &>/dev/null; then
                log "SUCCESS" "Remote $model: Available"
            else
                log "WARNING" "Remote $model: Missing"
            fi
        done
        
        # Remote Python packages
        if ssh "$REMOTE_HOST" "cd $REMOTE_WORKSPACE && source .venv/bin/activate && python3 -c 'import torch; print(f\"PyTorch CUDA: {torch.cuda.is_available()}\")'" &>/dev/null; then
            log "SUCCESS" "Remote TiRex GPU: Available"
        else
            log "WARNING" "Remote TiRex GPU: Not available"
        fi
    else
        log "WARNING" "Remote environment not accessible for status check"
    fi
}