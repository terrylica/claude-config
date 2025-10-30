# Workspace Reorganization Execution Guide

**Version**: 1.0.0
**Status**: Proposed
**Created**: 2025-10-23
**Approach**: Conservative, documentation-first, phased execution

______________________________________________________________________

## Executive Summary

This guide provides **step-by-step instructions** for executing the workspace reorganization documented in `/specifications/workspace-reorganization.yaml`.

### Current State vs. Target

**Current Issues** (Score: 7.2/10):

- 210 MB runtime artifact accumulation
- Root-level scripts (4 files)
- Backup files in production (3 files)
- Inconsistent tool organization
- No artifact retention policy

**Target State** (Score: 9.0/10):

- Managed artifact retention (30-day policy)
- Clear tool taxonomy (tools/bin/, tools/config/)
- No backup files (use git history)
- Automated health checks
- Comprehensive documentation

______________________________________________________________________

## Quick Reference

| Phase                             | Risk    | Duration | Deliverable                   |
| --------------------------------- | ------- | -------- | ----------------------------- |
| **Phase 1: Documentation**        | Minimal | 8h       | Complete specs & docs         |
| **Phase 2: Safe Cleanup**         | Low     | 2h       | Remove backups, fix anomalies |
| **Phase 3: Root Cleanup**         | Medium  | 3h       | Move root scripts             |
| **Phase 4: System Consolidation** | Medium  | 4h       | Organize system artifacts     |
| **Phase 5: Archival**             | Low     | 2h       | Archive old artifacts         |
| **Phase 6: Advanced (Optional)**  | Medium  | 3h       | uv migration, etc.            |

**Total Duration**: 22 hours (can be done incrementally)

______________________________________________________________________

## Phase 1: Documentation & Specification (COMPLETED)

**Status**: ✅ Completed 2025-10-23
**Risk**: Minimal (documentation only)
**Duration**: 8 hours

### Deliverables Created

1. ✅ `/specifications/workspace-reorganization.yaml` - Target architecture
1. ✅ `/specifications/reorg-move-map.yaml` - Complete file move mapping
1. ✅ `/specifications/reorg-cleanup-targets.yaml` - Cleanup targets
1. ✅ `/specifications/workspace-health-check.yaml` - Validation spec
1. ✅ `/docs/standards/TOOL_ORGANIZATION.md` - Tool taxonomy
1. ✅ `/docs/maintenance/ARTIFACT_RETENTION.md` - Retention policies
1. ✅ `/docs/maintenance/REORGANIZATION_ROLLBACK.md` - Rollback procedures
1. ✅ `/docs/maintenance/WORKSPACE_REORGANIZATION_GUIDE.md` - This guide
1. ✅ `/tools/tool-manifest.yaml` - Tool registry
1. ✅ Execution checklists (pre/phase/post)

### Next Steps

Review all documentation before proceeding to Phase 2.

______________________________________________________________________

## Phase 2: Safe Cleanup

**Risk**: Low
**Duration**: 2 hours
**Recoverable**: Yes (git restore)

### Pre-Flight Checklist

Execute `/specifications/reorg-execution-checklists.yaml` → `pre_migration_checklist`

###Operations

1. **Delete backup files** (after git verification):

   - `/statusline.sh.backup`
   - `/archive/sage-sync-legacy/sage-sync.original`
   - `/automation/cns/cns_hook_entry.sh.backup`

1. **Fix nested directory**:

   - Move `/.claude/settings.local.json` → `/system/settings.local.json`
   - Remove empty `/.claude/` directory

### Execution Steps

```bash
# Step 1: Backup
/tools/emergency-backup.sh

# Step 2: Git commit
git add -A
git commit -m "pre-cleanup snapshot"

# Step 3: Verify backups exist in git history
git log -- statusline.sh.backup
git log -- automation/cns/cns_hook_entry.sh

# Step 4: Delete backup files
rm statusline.sh.backup
rm archive/sage-sync-legacy/sage-sync.original
rm automation/cns/cns_hook_entry.sh.backup

# Step 5: Fix nested directory
mkdir -p system/
mv .claude/settings.local.json system/settings.local.json
rmdir .claude/

# Step 6: Commit
git add -A
git commit -m "refactor(workspace): phase-2 safe cleanup - remove backups, fix nesting"

# Step 7: Validate
/tools/bin/workspace-health-check.sh
```

### Rollback

```bash
# If issues occur
git reset --hard HEAD~1
```

______________________________________________________________________

## Phase 3: Root Cleanup

**Risk**: Medium
**Duration**: 3 hours
**Requires**: Documentation updates

### Operations

1. **Create tool subdirectories**:

   - `/tools/bin/`
   - `/tools/config/`

1. **Move root scripts**:

   - `/install-all-tools` → `/tools/bin/install-all-tools.sh`
   - `/disable-pyright.sh` → `/tools/config/disable-pyright.sh`
   - `/instant-sync-option.sh` → `/archive/legacy/instant-sync-option.sh`

### Execution Steps

```bash
# Step 1: Create directories
mkdir -p tools/bin tools/config archive/legacy

# Step 2: Create README files
cat > tools/bin/README.md << 'EOF'
# Executable Tool Wrappers

Entry point scripts that delegate to implementations.
See /docs/standards/TOOL_ORGANIZATION.md for details.
EOF

cat > tools/config/README.md << 'EOF'
# Tool Configuration Utilities

Configuration and setup scripts.
See /docs/standards/TOOL_ORGANIZATION.md for details.
EOF

# Step 3: Move scripts
mv install-all-tools tools/bin/install-all-tools.sh
mv disable-pyright.sh tools/config/disable-pyright.sh
mv instant-sync-option.sh archive/legacy/instant-sync-option.sh

# Step 4: Update symlinks if needed
ln -sf /Users/terryli/.claude/tools/bin/install-all-tools.sh ~/.local/bin/install-all-tools

# Step 5: Test
tools/bin/install-all-tools.sh --help

# Step 6: Update documentation references
# (manually update docs that reference old paths)

# Step 7: Commit
git add -A
git commit -m "refactor(workspace): phase-3 root cleanup - move scripts to tools/"

# Step 8: Validate
/tools/bin/workspace-health-check.sh
```

### Rollback

See `/docs/maintenance/REORGANIZATION_ROLLBACK.md` → Phase 3

______________________________________________________________________

## Phase 4: System Consolidation ⚠️ HIGH RISK

**Risk**: Medium-High
**Duration**: 4 hours
**Critical**: Claude Code may reference these paths

### ⚠️ WARNING

This phase moves directories that Claude Code may actively use:

- `todos/` → `system/todos/`
- `file-history/` → `system/file-history/`
- `debug/` → `system/debug/`

**Recommendation**: Skip this phase unless you understand Claude Code internals.

### If Proceeding

1. **Full workspace backup** (not just git)
1. **Test in isolated environment first**
1. **Have rollback procedure ready**
1. **Monitor Claude Code behavior closely**

### Execution (CAUTIOUS)

```bash
# Step 1: FULL backup (not just git)
tar -czf ~/claude-workspace-backup-$(date +%Y%m%d).tar.gz ~/.claude/

# Step 2: Create system directory
mkdir -p system/

# Step 3: Move directories ONE AT A TIME
mv todos system/todos

# Step 4: TEST IMMEDIATELY
# Start Claude Code, verify task tracking works
# If broken, rollback immediately

# If successful, continue:
mv file-history system/file-history
# TEST: Verify file history works

mv debug system/debug
# TEST: Verify debugging works

# Step 5: Consolidate history
mkdir -p system/history
mv history.jsonl system/history/session-history.jsonl
mv history system/history/archive

# Step 6: Commit
git add -A
git commit -m "refactor(workspace): phase-4 system consolidation - organize runtime artifacts"
```

### Rollback

See `/docs/maintenance/REORGANIZATION_ROLLBACK.md` → Phase 4 (CRITICAL section)

______________________________________________________________________

## Phase 5: Artifact Archival

**Risk**: Low
**Duration**: 2 hours
**Benefit**: ~150 MB space recovery

### Operations

Archive artifacts older than 30 days:

- Shell snapshots (69 MB)
- Debug logs (57 MB)
- File history (63 MB)

### Execution

```bash
# Step 1: Identify old artifacts
find shell-snapshots/ -type f -mtime +30 | head -10

# Step 2: Archive shell snapshots
tar -czf archive/shell-snapshots-$(date +%Y-%m).tar.gz \
    $(find shell-snapshots/ -type f -mtime +30)

# Step 3: Verify archive
tar -tzf archive/shell-snapshots-$(date +%Y-%m).tar.gz | wc -l
tar -tzf archive/shell-snapshots-$(date +%Y-%m).tar.gz > /dev/null && echo "Valid"

# Step 4: Only delete if verification passed
find shell-snapshots/ -type f -mtime +30 -delete

# Step 5: Repeat for debug and file-history
# (same process)

# Step 6: Commit
git add archive/
git commit -m "chore(workspace): phase-5 archival - compress old artifacts"

# Step 7: Verify space savings
du -sh shell-snapshots/ debug/ file-history/ archive/
```

______________________________________________________________________

## Phase 6: Advanced (Optional)

**Risk**: Medium
**Duration**: 3 hours
**Optional**: Can be deferred

### Operations

1. Migrate gfm-link-checker from .venv to uv
1. Archive old CHANGELOG entries (optional)
1. Document statusline.sh usage (optional)

### Recommendation

**Skip this phase initially**. Focus on Phases 1-5 first. Revisit Phase 6 after validating reorganization success.

______________________________________________________________________

## Post-Reorganization

### Validation

```bash
# Run full health check
/tools/bin/workspace-health-check.sh

# Verify all tools work
tools/bin/install-all-tools.sh --help
gfm-check --help

# Test automation
# (trigger CNS, test prettier)

# Check documentation links
gfm-check docs/
```

### Monitoring

**First Week**:

- Daily health checks
- Watch for issues
- Monitor artifact growth
- Verify automation works

**First Month**:

- Weekly health checks
- Adjust retention policies if needed
- Document any issues

**Ongoing**:

- Monthly health checks
- Monthly artifact archival
- Update documentation as needed

______________________________________________________________________

## Maintenance

### Monthly Tasks

1. **Artifact Archival**:

   ```bash
   /tools/maintenance/archive-artifacts.sh  # Create this script
   ```

1. **Health Check**:

   ```bash
   /tools/bin/workspace-health-check.sh
   ```

1. **Tool Manifest Update**:

   - Review `/tools/tool-manifest.yaml`
   - Update for any new/removed tools

### Automation Setup

**LaunchAgent** (macOS) or **cron** for:

- Monthly artifact archival
- Weekly health checks
- Space monitoring

See `/docs/maintenance/ARTIFACT_RETENTION.md` for automation details.

______________________________________________________________________

## Troubleshooting

### Common Issues

1. **Claude Code won't start**: Rollback Phase 4
1. **Tools not found**: Check symlinks and PATH
1. **Documentation links broken**: Run gfm-check and fix
1. **Artifact archival failed**: Check compression, disk space

See `/docs/maintenance/REORGANIZATION_ROLLBACK.md` for detailed troubleshooting.

______________________________________________________________________

## Success Criteria

After reorganization, verify:

- [ ] Overall score improves from 7.2 to 9.0+
- [ ] No root-level scripts (except planned exceptions)
- [ ] No backup files in production
- [ ] Artifact retention policy active
- [ ] Tool taxonomy clear and documented
- [ ] Health check passes (40+/42 checks)
- [ ] All automation functional
- [ ] Documentation complete and linked
- [ ] Space recovery achieved (~150-200 MB)
- [ ] Monitoring and maintenance automated

______________________________________________________________________

## Reference

### Key Documents

- **[Reorganization Spec](/specifications/workspace-reorganization.yaml)** - What should be
- **[Move Map](/specifications/reorg-move-map.yaml)** - How to get there
- **[Tool Taxonomy](/docs/standards/TOOL_ORGANIZATION.md)** - Organization rules
- **[Artifact Retention](/docs/maintenance/ARTIFACT_RETENTION.md)** - Lifecycle management
- **[Health Check Spec](/specifications/workspace-health-check.yaml)** - Validation
- **[Rollback Procedures](/docs/maintenance/REORGANIZATION_ROLLBACK.md)** - Safety
- **[Execution Checklists](/specifications/reorg-execution-checklists.yaml)** - Step-by-step

### Commands

```bash
# Backup
/tools/emergency-backup.sh

# Health check
/tools/bin/workspace-health-check.sh

# Rollback (immediate)
git reset --hard HEAD~1

# Rollback (backup-based)
/tools/rollback-restore.sh --backup=/path/to/backup.tar.gz
```

______________________________________________________________________

**Status**: Ready for phased execution
**Next Step**: Review all documentation, then execute Phase 2
**Questions**: Create issues in `/docs/maintenance/REORGANIZATION_ISSUES.md`
