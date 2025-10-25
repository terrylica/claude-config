# Migration Execution Guide: v3.0.1 → v4.0.0

**Single Source of Truth for Migration Execution**

**Status**: ✅ **READY TO PROCEED** - All pre-migration fixes applied and tested
**Date**: 2025-10-25
**Current Version**: v3.0.1
**Target Version**: v4.0.0

---

## Quick Start

**Current Blockers**: 0 - All fixes complete ✅
**Time to Migrate**: 25.5 hours base + 4.5h buffer = 30 hours (4-5 days execution)

---

## Pre-Migration Fixes ✅ COMPLETE (Applied 2025-10-25)

### ✅ Fix 1: Session Duration Tracking (30 min)

**What**: Add SessionStart hook to track session timing

**Action**: Update `~/.claude/settings.json` - add this to `hooks.SessionStart` array:

```json
{
  "type": "command",
  "command": "$HOME/.claude/automation/lychee/runtime/hook/session-start-tracker.sh"
}
```

**Full SessionStart section should look like**:

```json
"SessionStart": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "$HOME/.claude/automation/lychee/runtime/hook/session-start-tracker.sh"
      },
      {
        "type": "command",
        "command": "$HOME/.claude/automation/lychee/testing/inject-results.sh"
      }
    ]
  }
]
```

**Test**: Start/stop a Claude Code session, check `~/.claude/automation/lychee/state/session_timestamps/` for timestamp files

**Files Created**: Already done ✅

- `/Users/terryli/.claude/automation/lychee/runtime/hook/session-start-tracker.sh`

---

### ✅ Fix 2: Workflow Calculator (Complete)

**What**: Helper script to calculate available workflows

**Status**: Already created ✅

- `/Users/terryli/.claude/automation/lychee/runtime/lib/calculate_workflows.py`

**Test**:

```bash
# Test with sample data
uv run ~/.claude/automation/lychee/runtime/lib/calculate_workflows.py \
    --error-count 3 \
    --modified-files 5 \
    --debug

# Should output: ["lychee-autofix", "fix-docstrings", "prune-legacy"]
```

---

### ✅ Fix 3: Update OpenAPI Spec (COMPLETE)

**File**: `~/.claude/specifications/telegram-workflows-orchestration-v4.yaml`

**Change 1** - Add context to WorkflowSelection (after line 386):

```yaml
workspace_path:
  type: string
  format: path
  description: "Workspace path from session summary (for template rendering)"
  example: "/Users/terryli/.claude"

git_status:
  $ref: "#/components/schemas/GitStatus"
  description: "Git status from session summary (for template rendering)"

lychee_status:
  $ref: "#/components/schemas/LycheeStatus"
  description: "Lychee status from session summary (for template rendering)"
```

**Change 2** - Update required fields (line 344):

```yaml
required:
  - selection_type
  - correlation_id
  - session_id
  - timestamp
  - workspace_path # ADD THIS
```

**Change 3** - Fix migration-steps (lines 797-807):

```yaml
migration-steps:
  0: "Run pre-migration validation (no pending files, clean git, services healthy)"
  1: "Create state/workflows.json registry with 4 initial workflows"
  2: "Refactor hook: emit SessionSummary (dual-mode with notifications), add git status, session duration"
  3: "Refactor bot: load registry, watch summaries/, dynamic workflow menu (dual-mode with notifications)"
  4: "Refactor orchestrator: load registry, watch selections/, Jinja2 template rendering, smart dependencies (dual-mode with approvals)"
  5: "Integration testing: 5 comprehensive test scenarios including correlation tracing"
  6: "Service management & directory rename: stop services, git mv lychee→telegram-workflows, update launchd plists, restart"
  7: "Remove dual-mode: delete old handlers, archive v3 state directories, create SQLite compatibility view"
  8: "Documentation: update all docs to v4.0.0, create release notes, git tag v4.0.0"
```

**Change 4** - Populate implementation findings (line 809):

```yaml
x-implementation-findings:
  - finding: "Approval JSON uses 'decision' field, not 'action', includes metadata wrapper"
    date: "2025-10-25"
    source: "Round 1 verification"
    impact: "Documentation corrected"

  - finding: "Orchestrator launched via asyncio.create_subprocess_exec, NOT launchctl"
    date: "2025-10-25"
    source: "Round 1 verification"
    impact: "Launchd services for auto-start only, not IPC"

  - finding: "Hook does NOT collect git status (Phase 2 must ADD)"
    date: "2025-10-25"
    source: "Round 1 verification"
    impact: "Phase 2 complexity +30min, new feature implementation required"

  - finding: "Hook does NOT track session duration (Phase 2 must ADD)"
    date: "2025-10-25"
    source: "Round 1 verification"
    impact: "SessionStart hook created for timestamp tracking"

  - finding: "WorkflowSelection missing context for template rendering"
    date: "2025-10-25"
    source: "Round 2/3 verification"
    impact: "Schema updated with workspace_path, git_status, lychee_status fields"
```

---

### ✅ Fix 4: Update Migration Plan (COMPLETE)

**File**: `MIGRATION_v3_to_v4_PLAN_v2.md`

**Change 1** - Executive summary (line 24):

```markdown
**Timeline Adjusted**: 10.5h → 30h total (25.5h base + 4.5h buffer, 3-day execution recommended)
```

**Change 2** - Phase 2 header (line 315):

```markdown
**Duration**: 3-3.5 hours (git status and duration tracking are NEW features)
```

**Change 3** - Phase 2 code - Add after line 373 in `write_session_summary()`:

```bash
# Calculate available workflows using helper
available_wfs_json=$(uv run "$LIB_DIR/calculate_workflows.py" \
    --error-count "$broken_links_count" \
    --modified-files "$modified_files" \
    --registry "$STATE_DIR/workflows.json")

# Include in summary
available_wfs="$available_wfs_json"
```

**Change 4** - Phase 2 code - Update line 375:

```bash
# OLD:
"available_workflows": []

# NEW:
"available_workflows": $available_wfs
```

**Change 5** - Phase 2 code - Session duration (replace lines 333-342):

```bash
# Calculate Session Duration
TIMESTAMP_DIR="$HOME/.claude/automation/lychee/state/session_timestamps"
timestamp_file="$TIMESTAMP_DIR/${session_id}.timestamp"

if [[ -f "$timestamp_file" ]]; then
    session_start_time=$(cat "$timestamp_file")
    session_end_time=$(date +%s)
    session_duration=$((session_end_time - session_start_time))
    rm -f "$timestamp_file"
else
    # Fallback if timestamp not found
    session_duration=0
    echo "Warning: Session start timestamp not found, duration set to 0" >> "$log_file" 2>&1
fi
```

**Change 6** - Phase 3 code - Update WorkflowSelection (lines 631-642):

```python
selection = {
    "selection_type": "preset",
    "correlation_id": summary['correlation_id'],
    "session_id": summary['session_id'],
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "workflow_ids": [workflow_id],
    "orchestration_mode": "smart",
    # ADD CONTEXT FOR TEMPLATE RENDERING:
    "workspace_path": summary['workspace_path'],
    "git_status": summary['git_status'],
    "lychee_status": summary['lychee_status']
}
```

**Change 7** - Phase 4 header (line 740):

```markdown
**Duration**: 4-5 hours (template rendering and context handling are NEW)
**Risk**: CRITICAL (verify WorkflowSelection context fix applied)
```

**Change 8** - Timeline table (lines 1632-1642):

```markdown
| Phase 2: Hook | 3.5h | 6h |
| Phase 3: Bot | 4h | 10h |
| Phase 4: Orchestrator | 5h | 15h |
| Phase 5: Testing | 3h | 18h |
| Phase 6: Rename + Services | 1.5h | 19.5h |
| Phase 7: Cleanup | 2h | 21.5h |
| Phase 8: Documentation | 3h | 24.5h |
| **Buffer (issues)** | 5.5h | **30h** |
```

---

## Pre-Migration Checklist

After applying all fixes above:

- [ ] settings.json updated with SessionStart hook
- [ ] OpenAPI spec updated (3 changes)
- [ ] Migration plan updated (8 changes)
- [ ] Session tracker tested (start/stop session, check timestamps)
- [ ] Workflow calculator tested (returns correct workflow IDs)
- [ ] All changes committed to git
- [ ] Pre-migration validation script ready

**Once all checked**: Proceed to Phase 0 below

---

## Phase 0: Pre-Migration Validation

**Duration**: 30 minutes
**Must complete before Phase 1**

### Run Validation Script

```bash
cd ~/.claude/automation/lychee

# Check for pending state files
find state/notifications state/approvals state/completions -name "*.json" 2>/dev/null

# Should be empty - if not, let bot/orchestrator consume first

# Check git status
git status

# Should be clean - commit or stash changes

# Check SQLite accessible
sqlite3 state/events.db "SELECT COUNT(*) FROM session_events;"

# Should return a number

# Check services (may not be running, that's OK)
ps aux | grep multi-workspace-bot

# Create git tag for safety
git tag -a v3.0.1-verified -m "Pre-migration state verified"
```

### Success Criteria

- [ ] No pending notification files
- [ ] No pending approval files
- [ ] No pending completion files
- [ ] Git working directory clean
- [ ] SQLite database accessible
- [ ] Git tag v3.0.1-verified created

---

## Phase 1: Create Workflow Registry

**Duration**: 1-1.5 hours
**Risk**: LOW

### Tasks

1. **Create registry file**:

```bash
cd ~/.claude/automation/lychee
touch state/workflows.json
```

2. **Populate with 4 workflows** (copy from spec or plan):
   - lychee-autofix
   - prune-legacy
   - fix-docstrings
   - rename-variables

3. **Validate JSON**:

```bash
jq . state/workflows.json > /dev/null && echo "✅ Valid JSON"
```

4. **Test workflow calculator**:

```bash
uv run runtime/lib/calculate_workflows.py \
    --error-count 3 \
    --modified-files 5 \
    --registry state/workflows.json
```

### Success Criteria

- [ ] state/workflows.json created
- [ ] Valid JSON syntax
- [ ] 4 workflows defined
- [ ] calculate_workflows.py returns correct IDs

### Rollback

```bash
rm state/workflows.json
```

**Commit**: `git commit -m "feat(v4): add workflow registry with 4 workflows"`

---

## Phase 2: Refactor Hook (Dual-Mode)

**Duration**: 3-3.5 hours
**Risk**: MEDIUM

### Tasks

See MIGRATION_v3_to_v4_PLAN_v2.md Phase 2 (with fixes applied)

Key changes:

- Add git status extraction
- Add session duration calculation (using timestamps)
- Add available_workflows calculation (using helper)
- Emit SessionSummary (always)
- Emit Notification (only if errors > 0) - dual mode
- Bot starts always (not just on errors)

### Testing

```bash
# Trigger hook manually
./runtime/hook/check-links-hybrid.sh

# Check both formats emitted
ls -l state/summaries/
ls -l state/notifications/  # Only if errors

# Verify available_workflows populated
jq '.available_workflows' state/summaries/summary_*.json
```

### Success Criteria

- [ ] Git status collected correctly
- [ ] Session duration calculated (check logs)
- [ ] available_workflows populated (not empty array)
- [ ] Summary always emitted
- [ ] Notification only if errors > 0
- [ ] Bot starts on every session stop

### Rollback

```bash
git checkout runtime/hook/check-links-hybrid.sh
rm -rf state/summaries/
```

**Commit**: `git commit -m "feat(v4): hook emits session summaries with dual-mode"`

---

## Phase 3: Refactor Bot (Workflow Menu)

**Duration**: 4 hours
**Risk**: MEDIUM-HIGH

See MIGRATION_v3_to_v4_PLAN_v2.md Phase 3 (with WorkflowSelection context fix applied)

### Success Criteria

- [ ] Bot loads workflow registry
- [ ] Watches summaries/ directory
- [ ] Dynamic workflow menu based on triggers
- [ ] WorkflowSelection includes context (workspace_path, git_status, lychee_status)
- [ ] Dual mode works (watches both notifications/ and summaries/)

### Rollback

```bash
git checkout runtime/bot/multi-workspace-bot.py
rm -rf state/selections/
```

**Commit**: `git commit -m "feat(v4): bot loads registry and displays workflow menu"`

---

## Phase 4: Refactor Orchestrator

**Duration**: 4-5 hours
**Risk**: CRITICAL (verify context fix)

See MIGRATION_v3_to_v4_PLAN_v2.md Phase 4

### Success Criteria

- [ ] Orchestrator loads registry
- [ ] Jinja2 templates render correctly (with context from WorkflowSelection)
- [ ] Smart dependency resolution works
- [ ] Dual mode works (watches both approvals/ and selections/)

### Rollback

```bash
git checkout runtime/orchestrator/multi-workspace-orchestrator.py
rm -rf state/executions/
```

**Commit**: `git commit -m "feat(v4): orchestrator executes workflows from registry"`

---

## Phase 5: Integration Testing

**Duration**: 3 hours
**Risk**: MEDIUM

### Test Scenarios

1. Session with 0 errors → Summary sent, workflows menu shown
2. Session with lychee errors → Lychee workflow available
3. Multi-workflow selection → Dependencies resolved
4. End-to-end correlation tracking → All events logged

See MIGRATION_v3_to_v4_PLAN_v2.md Phase 5 for detailed test procedures

### Success Criteria

- [ ] All 5 test scenarios pass
- [ ] No errors in logs
- [ ] State files cleaned up after workflows
- [ ] SQLite correlation tracking works

**No rollback needed** - fix issues and re-test

---

## Phase 6: Directory Rename & Services

**Duration**: 1-1.5 hours
**Risk**: MEDIUM

### Critical Steps

```bash
# 1. Stop services
launchctl stop com.user.lychee.telegram-handler
launchctl stop com.user.lychee.orchestrator

# 2. Rename with git mv
cd ~/.claude/automation
git mv lychee telegram-workflows

# 3. Update launchd plists
sed -i '' 's|automation/lychee|automation/telegram-workflows|g' \
    ~/Library/LaunchAgents/com.user.lychee.*.plist

# 4. Reload services
launchctl unload ~/Library/LaunchAgents/com.user.lychee.*.plist
launchctl load ~/Library/LaunchAgents/com.user.lychee.*.plist

# 5. Restart
launchctl start com.user.lychee.telegram-handler
```

### Success Criteria

- [ ] Directory renamed atomically
- [ ] Git history preserved
- [ ] Services running from new location
- [ ] End-to-end test passes

### Rollback

```bash
launchctl stop com.user.lychee.telegram-handler
cd ~/.claude/automation
git mv telegram-workflows lychee
# Revert plists, reload services
```

**Commit**: `git commit -m "refactor: rename automation/lychee → automation/telegram-workflows"`

---

## Phase 7: Remove Dual Mode

**Duration**: 2 hours
**Risk**: LOW

See MIGRATION_v3_to_v4_PLAN_v2.md Phase 7

Remove backward compatibility:

- Delete watch_notifications() from bot
- Delete watch_approvals() from orchestrator
- Delete notification emission from hook
- Archive old state directories

**Commit**: `git commit -m "refactor(v4): remove dual-mode backward compatibility"`

---

## Phase 8: Documentation & Release

**Duration**: 3 hours
**Risk**: LOW

- Update all documentation to v4.0.0
- Create CHANGELOG entry
- Create git tag v4.0.0
- Verify all docs reference new directory name

**Commit**: `git commit -m "docs: update all documentation to v4.0.0"`
**Tag**: `git tag -a v4.0.0 -m "Release v4.0.0: Telegram Workflows System"`

---

## Quick Reference

### Timeline Summary

| Phase     | Duration | Cumulative |
| --------- | -------- | ---------- |
| **Fixes** | **3-4h** | **3-4h**   |
| Phase 0   | 0.5h     | 4.5h       |
| Phase 1   | 1.5h     | 6h         |
| Phase 2   | 3.5h     | 9.5h       |
| Phase 3   | 4h       | 13.5h      |
| Phase 4   | 5h       | 18.5h      |
| Phase 5   | 3h       | 21.5h      |
| Phase 6   | 1.5h     | 23h        |
| Phase 7   | 2h       | 25h        |
| Phase 8   | 3h       | 28h        |
| Buffer    | 5h       | **33h**    |

**Total**: 33-34 hours (4-5 days with breaks)

### Critical Files

- **This file**: Single source of truth
- **MIGRATION_v3_to_v4_PLAN_v2.md**: Detailed phase instructions (with fixes applied)
- **BLOCKING_ISSUES_FIXES.md**: Detailed fix explanations and testing
- **telegram-workflows-orchestration-v4.yaml**: Target spec (with fixes applied)

### Emergency Contacts

- Full rollback: See MIGRATION_v3_to_v4_PLAN_v2.md lines 1550-1590
- Verification audit: See archive/verification-2025-10-25/

---

**Status**: ✅ All pre-migration fixes complete and tested (2025-10-25)

**Implementation Summary**:

- ✅ Session duration tracking: SessionStart hook configured in settings.json
- ✅ Workflow calculator: Helper script tested with sample data
- ✅ OpenAPI spec: 4 changes applied (WorkflowSelection context, migration-steps, implementation-findings)
- ✅ Migration Plan v2: 8 changes applied (timelines, durations, code updates)

**Next Action**: Proceed to Phase 0 (Pre-Migration Validation)
