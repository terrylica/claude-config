#!/bin/bash
# SAGE Sync Core Library - Modularized Functions
# Rollback Reference: c80d866 (pre-MHR modularization snapshot)
# Part of SAGE Sync Infrastructure - Bulletproof Session Preservation

# Import canonical session management functions
source "$HOME/.claude/sage-aliases/lib/sage-canonical-sessions.sh"

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

# Universal Cross-Platform Session Sync with Canonical Format
# Migrates platform-specific sessions to canonical format for cross-platform compatibility
sync_canonical_claude_sessions() {
    section "Universal Cross-Platform Claude Session Sync"
    
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
    
    # Step 1: Migrate local sessions to canonical format
    log "INFO" "Step 1: Migrating local sessions to canonical format"
    if [[ $DRY_RUN == true ]]; then
        log "INFO" "DRY RUN: Would migrate local sessions to canonical format"
        migrate_to_canonical_sessions "$CLAUDE_SESSIONS_DIR" "true"
    else
        # Check if canonical migration is needed
        local needs_migration=false
        local platform_specific_dirs=$(find "$CLAUDE_SESSIONS_DIR" -maxdepth 1 -type d -name "-*-*-*" 2>/dev/null | wc -l)
        local canonical_dirs=$(find "$CLAUDE_SESSIONS_DIR" -maxdepth 1 -type d -name "~*" 2>/dev/null | wc -l)
        
        if [[ $platform_specific_dirs -gt 0 && $canonical_dirs -eq 0 ]]; then
            log "INFO" "Found $platform_specific_dirs platform-specific session directories, migrating to canonical format"
            needs_migration=true
        elif [[ $platform_specific_dirs -gt 0 && $canonical_dirs -gt 0 ]]; then
            log "INFO" "Mixed session format detected, consolidating to canonical format"
            needs_migration=true
        else
            log "INFO" "Sessions already in canonical format ($canonical_dirs canonical directories)"
        fi
        
        if [[ $needs_migration == true ]]; then
            migrate_to_canonical_sessions "$CLAUDE_SESSIONS_DIR" "false"
            log "SUCCESS" "Local session migration to canonical format completed"
        fi
    fi
    
    # Step 2: Count canonical sessions for sync validation
    local local_canonical_sessions=$(find "$CLAUDE_SESSIONS_DIR/~"* -name "*.jsonl" 2>/dev/null | wc -l || echo "0")
    local local_canonical_dirs=$(find "$CLAUDE_SESSIONS_DIR" -maxdepth 1 -type d -name "~*" 2>/dev/null | wc -l || echo "0")
    local local_size=$(du -sk "$CLAUDE_SESSIONS_DIR/" 2>/dev/null | cut -f1 || echo "0")
    
    log "INFO" "Local canonical sessions: $local_canonical_dirs directories, $local_canonical_sessions session files, ${local_size}KB"
    
    if [[ $DRY_RUN == true ]]; then
        log "INFO" "DRY RUN: Would sync canonical sessions to remote"
        log "INFO" "DRY RUN: Rsync would sync ~/canonical directories and exclude legacy platform-specific directories"
        return 0
    fi
    
    # Step 3: Sync canonical directories to remote
    progress "Syncing canonical Claude sessions to remote..."
    
    # Sync only canonical directories (starting with ~) to ensure cross-platform compatibility
    local rsync_cmd="rsync -avz --update --stats --human-readable"
    
    # Include canonical directories and standard session files
    rsync_cmd="$rsync_cmd --include='~*/' --include='~*/**' --include='*.json' --include='*.jsonl' --include='projects/' --exclude='legacy/' --exclude='-*'"
    
    if [[ $VERBOSE == true ]]; then
        rsync_cmd="$rsync_cmd --progress"
    fi
    
    log "DEBUG" "Executing canonical sync: $rsync_cmd \"$CLAUDE_SESSIONS_DIR/\" \"$REMOTE_HOST:$REMOTE_SESSIONS_DIR/\""
    
    if $rsync_cmd "$CLAUDE_SESSIONS_DIR/" "$REMOTE_HOST:$REMOTE_SESSIONS_DIR/" 2>&1 | tee -a "$LOG_FILE"; then
        # Step 4: Post-sync validation
        local remote_canonical_sessions=$(ssh -o ConnectTimeout=10 "$REMOTE_HOST" "find $REMOTE_SESSIONS_DIR/~* -name '*.jsonl' 2>/dev/null | wc -l" 2>/dev/null || echo "0")
        local remote_canonical_dirs=$(ssh -o ConnectTimeout=10 "$REMOTE_HOST" "find $REMOTE_SESSIONS_DIR -maxdepth 1 -type d -name '~*' 2>/dev/null | wc -l" 2>/dev/null || echo "0")
        local remote_size=$(ssh -o ConnectTimeout=10 "$REMOTE_HOST" "du -sk $REMOTE_SESSIONS_DIR/ | cut -f1" 2>/dev/null || echo "0")
        
        log "INFO" "Remote canonical sessions after sync: $remote_canonical_dirs directories, $remote_canonical_sessions session files, ${remote_size}KB"
        
        # Success criteria: At least the canonical directories synced properly
        if [[ $remote_canonical_dirs -gt 0 && $local_canonical_dirs -eq $remote_canonical_dirs ]]; then
            log "SUCCESS" "Canonical Claude sessions sync completed successfully"
            log "INFO" "Cross-platform session compatibility established"
            log "INFO" "Sessions can now be resumed on any platform with matching workspace structure"
        else
            log "WARNING" "Canonical directory count mismatch: local=$local_canonical_dirs, remote=$remote_canonical_dirs"
            log "INFO" "This may indicate sync issues or partial transfer"
        fi
        
        # Additional validation: Check specific cross-platform sessions
        log "INFO" "Validating cross-platform session availability..."
        local cross_platform_sessions=("~eon-nt" "~scripts" "~-claude")
        for canonical_session in "${cross_platform_sessions[@]}"; do
            if ssh -o ConnectTimeout=10 "$REMOTE_HOST" "test -d $REMOTE_SESSIONS_DIR/$canonical_session" 2>/dev/null; then
                local session_count=$(ssh -o ConnectTimeout=10 "$REMOTE_HOST" "find $REMOTE_SESSIONS_DIR/$canonical_session -name '*.jsonl' | wc -l" 2>/dev/null || echo "0")
                log "SUCCESS" "Cross-platform session $canonical_session: Available ($session_count sessions)"
            fi
        done
        
    else
        log "ERROR" "Canonical Claude sessions sync failed"
        return 1
    fi
}

# Defensive Truth: Session sync with path corruption protection is essential
# Claude Code creates mangled session directory names that break remote environments
# DEPRECATED: Use sync_canonical_claude_sessions() for cross-platform compatibility
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