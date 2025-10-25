# Workspace Reorganization Rollback Procedures

**Version**: 1.0.0
**Status**: Proposed
**Created**: 2025-10-23
**Purpose**: Safety procedures for rolling back failed reorganization operations

---

## Overview

This document provides **step-by-step rollback procedures** for each phase of workspace reorganization. Every reorganization operation must have a defined, tested rollback strategy before execution.

---

## Rollback Principles

### 1. Immediate Rollback

**When to use**: Operation failed immediately, no dependent operations completed

**Method**: Direct file operations (mv, rm, restore)

```bash
# Example: Failed move operation
mv /target/location/file.sh /original/location/file.sh
```

### 2. Git-Based Rollback

**When to use**: Operation succeeded but caused issues discovered later

**Method**: Git reset to pre-operation commit

```bash
# Rollback to last known good state
git reset --hard HEAD~1

# Or rollback to specific commit
git reset --hard <commit-hash>
```

### 3. Backup-Based Rollback

**When to use**: Git history insufficient or files were outside git

**Method**: Restore from emergency backup

```bash
# Restore from backup
/tools/rollback-restore.sh --backup=/path/to/backup.tar.gz
```

---

## Phase-by-Phase Rollback

### Phase 2: Safe Cleanup (Backups & Anomalies)

**Operations**: Delete backup files, fix nested directories

#### Rollback Procedure

1. **For deleted backup files**:

   ```bash
   # Restore from git
   git restore statusline.sh.backup
   git restore archive/sage-sync-legacy/sage-sync.original
   git restore automation/cns/cns_hook_entry.sh.backup
   ```

2. **For nested directory fix**:
   ```bash
   # Recreate nested structure if needed
   mkdir -p .claude/
   mv system/settings.local.json .claude/settings.local.json
   ```

**Validation**: Verify all backup files restored

---

### Phase 3: Root Cleanup (Move Scripts)

**Operations**: Move root-level scripts to tools/

#### Rollback Procedure

1. **Move scripts back**:

   ```bash
   # From move map: MOVE-001, MOVE-002, MOVE-003
   mv tools/bin/install-all-tools.sh ./install-all-tools
   mv tools/config/disable-pyright.sh ./disable-pyright.sh
   mv archive/legacy/instant-sync-option.sh ./instant-sync-option.sh
   ```

2. **Verify executability**:

   ```bash
   chmod +x install-all-tools disable-pyright.sh instant-sync-option.sh
   ```

3. **Test functionality**:
   ```bash
   ./install-all-tools --help
   ```

**Validation**: All scripts work from original locations

---

### Phase 4: System Consolidation (HIGH RISK)

**Operations**: Move todos/, file-history/, debug/ to system/

#### Rollback Procedure (CRITICAL)

1. **STOP Claude Code immediately**

2. **Move directories back**:

   ```bash
   # MOVE-008, MOVE-009, MOVE-010
   mv system/todos ./todos
   mv system/file-history ./file-history
   mv system/debug ./debug
   mv system/history/session-history.jsonl ./history.jsonl
   mv system/history/archive ./history
   ```

3. **Verify Claude Code configuration**:
   - Check if Claude Code can find todos/
   - Verify file history works
   - Test session functionality

4. **If configuration changes were made**:
   ```bash
   # Restore settings.json from git
   git restore settings.json
   ```

**Validation**:

- [ ] Claude Code starts successfully
- [ ] Task tracking works
- [ ] File history accessible
- [ ] Sessions restore properly

---

### Phase 5: Artifact Archival

**Operations**: Compress and archive old artifacts

#### Rollback Procedure

1. **Extract archived files**:

   ```bash
   # ARCHIVE-001: shell-snapshots
   tar -xzf archive/shell-snapshots-2025-10.tar.gz -C shell-snapshots/

   # ARCHIVE-002: debug logs
   tar -xzf archive/debug-logs-2025-10.tar.gz -C debug/

   # ARCHIVE-003: file-history
   tar -xzf archive/file-history-2025-10.tar.gz -C file-history/
   ```

2. **Verify extraction**:

   ```bash
   # Count files
   find shell-snapshots/ -type f | wc -l
   find debug/ -type f | wc -l
   find file-history/ -type d -mindepth 1 | wc -l
   ```

3. **Test systems**:
   - Claude Code file history
   - Debug logging
   - Session recovery

**Validation**: All extracted files accessible and functional

---

### Phase 6: Advanced (uv migration)

**Operations**: Remove .venv, migrate to uv

#### Rollback Procedure

1. **Restore .venv from backup**:

   ```bash
   # Restore from emergency backup
   tar -xzf backup/gfm-link-checker-venv.tar.gz -C gfm-link-checker/
   ```

2. **Remove uv configuration if added**:

   ```bash
   rm gfm-link-checker/pyproject.toml # if newly created
   git restore gfm-link-checker/pyproject.toml # if modified
   ```

3. **Test functionality**:
   ```bash
   cd gfm-link-checker
   .venv/bin/python -m pytest  # or whatever test command works
   ```

**Validation**: gfm-link-checker works with .venv

---

## Emergency Procedures

### Complete Workspace Rollback

**When to use**: Multiple phases failed, workspace unstable

1. **Stop all processes**:

   ```bash
   # Stop Claude Code, any running scripts
   pkill -f "claude"
   ```

2. **Identify last known good commit**:

   ```bash
   git log --oneline | head -20
   # Find commit before reorganization started
   ```

3. **Hard reset**:

   ```bash
   git reset --hard <last-good-commit>
   ```

4. **Restore from backup if needed**:

   ```bash
   /tools/emergency-backup.sh --restore /path/to/backup.tar.gz
   ```

5. **Verify workspace**:
   ```bash
   /tools/bin/workspace-health-check.sh
   ```

---

### Backup-Based Recovery

**When git rollback insufficient**

1. **List available backups**:

   ```bash
   ls -lh /path/to/backups/
   ```

2. **Choose backup**:

   ```bash
   # Most recent before reorganization
   BACKUP="/path/to/backup-2025-10-23-pre-reorg.tar.gz"
   ```

3. **Extract to temporary location**:

   ```bash
   mkdir /tmp/workspace-restore
   tar -xzf "$BACKUP" -C /tmp/workspace-restore
   ```

4. **Compare and restore selectively**:

   ```bash
   # Restore specific directories
   rsync -av /tmp/workspace-restore/todos/ ~/claude/todos/
   rsync -av /tmp/workspace-restore/file-history/ ~/.claude/file-history/
   ```

5. **Verify**:
   ```bash
   /tools/bin/workspace-health-check.sh
   ```

---

## Validation Checklist

After any rollback, verify:

- [ ] Git status clean or expected
- [ ] All tools executable and functional
- [ ] Claude Code starts successfully
- [ ] Task tracking works
- [ ] File history accessible
- [ ] Automation hooks work
- [ ] Documentation links valid
- [ ] No broken symlinks
- [ ] Workspace health check passes

---

## Prevention

### Pre-Operation Checklist

Before **any** reorganization operation:

1. [ ] **Full backup**: Run `/tools/emergency-backup.sh`
2. [ ] **Git commit**: Commit current state with descriptive message
3. [ ] **Test health**: Run workspace health check
4. [ ] **Document state**: Note current configuration
5. [ ] **Prepare rollback**: Know exact rollback steps

### During Operation

1. **One operation at a time**: Don't batch risky operations
2. **Test immediately**: Verify each operation before proceeding
3. **Commit frequently**: Git commit after each successful operation
4. **Monitor logs**: Watch for errors or warnings

### After Operation

1. **Immediate validation**: Test affected systems
2. **Health check**: Run full workspace health check
3. **Document issues**: Note any problems encountered
4. **Wait before cleanup**: Keep backups for 30 days

---

## Troubleshooting

### Issue: Claude Code won't start after reorganization

**Cause**: Likely related to Phase 4 (system consolidation)

**Fix**:

1. Rollback Phase 4 operations (see above)
2. Check settings.json for path references
3. Restore from backup if needed

### Issue: Tools not found after Phase 3

**Cause**: Symlinks or PATH issues

**Fix**:

1. Verify symlinks: `ls -l ~/.local/bin/`
2. Recreate symlinks if needed
3. Check PATH includes `~/.local/bin`

### Issue: File history missing after Phase 5

**Cause**: Archival deleted files prematurely

**Fix**:

1. Extract from archive (see Phase 5 rollback)
2. Verify archive integrity
3. Test Claude Code file history

### Issue: Git rollback doesn't restore files

**Cause**: Files were outside git or in .gitignore

**Fix**:

1. Use backup-based recovery
2. Check what files were in .gitignore
3. Extract selectively from emergency backup

---

## Related Documentation

- [Workspace Reorganization Specification](/specifications/workspace-reorganization.yaml)
- [Move Map](/specifications/reorg-move-map.yaml)
- [Cleanup Targets](/specifications/reorg-cleanup-targets.yaml)
- [Health Check Specification](/specifications/workspace-health-check.yaml)
- [Migration Guide](/docs/maintenance/WORKSPACE_REORGANIZATION_GUIDE.md)

---

**Remember**: Conservative approach. When in doubt, don't proceed. A slow, careful reorganization is better than a fast, broken one.
