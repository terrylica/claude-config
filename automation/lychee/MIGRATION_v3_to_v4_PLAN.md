# Migration Plan: v3.0.1 → v4.0.0

**Date**: 2025-10-25
**Status**: Planning Phase
**Type**: Major Breaking Changes (Directory Rename + Architecture Refactor)
**SSoT Specification**: `/Users/terryli/.claude/specifications/telegram-workflows-orchestration-v4.yaml`

---

## Executive Summary

**Goal**: Elevate Telegram notifications to primary orchestration layer, with lychee as one of many workflows.

**Key Changes**:
1. **Directory Rename**: `automation/lychee/` → `automation/telegram-workflows/`
2. **Session Summaries**: Always send (even 0 errors), provide workflow menu
3. **Workflow Registry**: Dynamically loaded plugins (lychee, housekeeping, docs, etc.)
4. **Hybrid UI**: Preset buttons + custom prompt option
5. **Smart Orchestration**: Dependency resolution for multi-workflow execution

**Migration Complexity**: High (directory rename, schema changes, UI overhaul)
**Estimated Duration**: 4-6 hours
**Rollback Strategy**: Git tag + revert

---

## Breaking Changes

### 1. Directory Structure

**Before (v3.0.1)**:
```
automation/lychee/
├── runtime/{bot,hook,orchestrator,lib}
├── state/{callbacks,notifications,approvals,completions,events.db}
├── docs/
└── README.md
```

**After (v4.0.0)**:
```
automation/telegram-workflows/
├── core/
│   ├── bot.py (workflow-agnostic)
│   ├── orchestrator.py (workflow-agnostic)
│   ├── hook.sh (emits session summaries)
│   └── lib/ (shared utilities)
├── workflows/
│   ├── workflows.json (registry)
│   ├── lychee/ (migrated from v3)
│   ├── housekeeping/
│   ├── documentation/
│   └── templates/
├── state/
│   ├── summaries/ (replaces notifications/)
│   ├── selections/ (replaces approvals/)
│   ├── executions/ (replaces completions/)
│   ├── callbacks/
│   └── events.db (unchanged)
├── docs/
└── README.md
```

### 2. State File Schema Changes

**Notifications → Summaries**:
- Old: `notify_{session}_{hash}.json` with lychee-specific fields
- New: `summary_{session}_{hash}.json` with generic session data + available workflows

**Approvals → Selections**:
- Old: `approval_{session}_{hash}.json` with single action
- New: `selection_{execution_id}.json` with workflow_ids array + orchestration mode

**Completions → Executions**:
- Old: `completion_{session}_{hash}.json` with Claude output
- New: `execution_{execution_id}.json` with workflow_id + execution metadata

### 3. Hook Output Format

**Old Behavior**:
```bash
if [[ $broken_links_count -gt 0 ]]; then
    # Write notification file
    # Start bot
fi
```

**New Behavior**:
```bash
# Always write session summary (even 0 errors)
write_session_summary \
    --duration "$session_duration" \
    --git-modified "$modified_files" \
    --lychee-errors "$broken_links_count"

# Start bot (if not running)
start_bot_if_needed
```

### 4. Bot UI Changes

**Old UI**:
```
🔗 Link Validation - .claude

Found 3 broken link(s)

[✅ Auto-Fix All]  [❌ Reject]
```

**New UI**:
```
📊 Session Summary - 🔗 .claude

Duration: 847s | Branch: main
Modified: 5 files | Untracked: 12 files
Lychee: 3 broken links

Choose workflows:

[🔗 Fix Broken Links]  [🧹 Prune Legacy]
[📝 Fix Docstrings]    [🔤 Rename Variables]
[✍️ Custom Prompt]
```

---

## Migration Phases

### Phase 0: Preparation ✅

**Status**: Completed

- [x] Audit v3.0.1 system (BOT_LIFECYCLE_ANALYSIS.md)
- [x] Update docs to v3.0.1 (COMPLETE_WORKFLOW.md)
- [x] Commit baseline (commit f344ae9)
- [x] Create v4.0.0 specification (telegram-workflows-orchestration-v4.yaml)

**Git Tag**: `v3.0.1-baseline` (create before Phase 1)

---

### Phase 1: Create Workflow Registry

**Goal**: Define initial workflows in registry format

**Tasks**:
1. Create `workflows.json` with schema from spec
2. Migrate lychee workflow definition from hardcoded logic
3. Add housekeeping workflows:
   - `prune-legacy` (remove unused code)
   - `fix-docstrings` (standardize docs)
   - `rename-variables` (improve naming)
   - `custom-prompt` (free-form user input)
4. Validate registry against JSON schema

**Artifacts**:
- `state/workflows.json` (100-200 lines)

**Testing**:
```bash
# Validate JSON structure
jq . state/workflows.json

# Verify all workflows have required fields
jq '.workflows | to_entries[] | .value | {id, name, category, triggers}' state/workflows.json
```

**Success Criteria**:
- [ ] Registry file valid JSON
- [ ] 5 workflows defined (lychee + 4 new)
- [ ] All workflows have prompt_template
- [ ] Trigger conditions specified

---

### Phase 2: Directory Rename

**Goal**: Rename `automation/lychee/` → `automation/telegram-workflows/` with git history

**Tasks**:
1. Create git tag: `v3.0.1-before-rename`
2. Use `git mv` to preserve history:
   ```bash
   git mv automation/lychee automation/telegram-workflows
   ```
3. Update all absolute paths in code:
   - Hook script
   - Bot script
   - Orchestrator script
   - Launchd plists
   - Documentation references
4. Commit rename

**Search & Replace**:
```bash
# Find all hardcoded paths
grep -r "automation/lychee" automation/telegram-workflows/

# Update to automation/telegram-workflows
```

**Testing**:
```bash
# Verify git history preserved
git log --follow automation/telegram-workflows/core/bot.py

# Check no broken symlinks
find automation/telegram-workflows/ -type l -exec test ! -e {} \; -print
```

**Success Criteria**:
- [ ] Directory renamed with `git mv`
- [ ] Git history accessible
- [ ] No hardcoded `/lychee/` paths remain
- [ ] All absolute paths updated

---

### Phase 3: Refactor Hook (Session Summaries)

**Goal**: Update hook to emit generic session summaries (always, not just on errors)

**Tasks**:
1. Extract git status:
   ```bash
   git_branch=$(git rev-parse --abbrev-ref HEAD)
   modified_files=$(git status --porcelain | grep "^ M" | wc -l)
   untracked_files=$(git status --porcelain | grep "^??" | wc -l)
   ```
2. Calculate session duration (track start time)
3. Create `SessionSummary` schema writer
4. Update hook logic:
   - **Old**: `if [[ $broken_links_count -gt 0 ]]; then emit notification`
   - **New**: Always emit summary + start bot
5. Update state directory: `notifications/` → `summaries/`

**File**: `core/hook.sh`

**Testing**:
```bash
# Trigger hook manually
./core/hook.sh

# Verify summary file created
ls state/summaries/

# Check summary format
jq . state/summaries/summary_*.json
```

**Success Criteria**:
- [ ] Hook always emits summary (even 0 errors)
- [ ] Summary includes git_status, lychee_status
- [ ] Bot starts on every session stop
- [ ] SQLite logs `summary.created` event

---

### Phase 4: Refactor Bot (Workflow Menu UI)

**Goal**: Bot displays workflow menu based on registry, handles multi-selection

**Tasks**:
1. **Startup**: Load `workflows.json` into memory
2. **Summary Handler**:
   - Read `SessionSummary` from `state/summaries/`
   - Filter workflows by trigger conditions:
     - `lychee_errors: true` → show if `lychee_status.error_count > 0`
     - `git_modified: true` → show if `git_status.modified_files > 0`
     - `always: true` → always show
   - Generate Telegram inline keyboard:
     - 2-column layout
     - Category headers
     - Workflow buttons with icons
     - "Custom Prompt" button
3. **Selection Handler**:
   - Handle button clicks
   - Support multi-select (checkboxes)
   - Emit `WorkflowSelection` to `state/selections/`
   - Show confirmation message

**File**: `core/bot.py`

**Key Changes**:
```python
# Load registry on startup
with open('state/workflows.json') as f:
    workflow_registry = json.load(f)

# Generate UI dynamically
def generate_workflow_menu(summary: SessionSummary) -> InlineKeyboard:
    available = filter_workflows_by_triggers(summary)
    return build_inline_keyboard(available, columns=2)
```

**Testing**:
```bash
# Test with test summary
./testing/test-summary-emit.py

# Verify Telegram message shows:
# - Session summary
# - Workflow buttons (based on triggers)
# - Custom prompt option
```

**Success Criteria**:
- [ ] Bot loads workflow registry on startup
- [ ] Workflow menu dynamically generated
- [ ] Trigger filtering works (lychee only shows if errors > 0)
- [ ] Custom prompt option available
- [ ] SQLite logs `selection.received` event

---

### Phase 5: Refactor Orchestrator (Workflow Execution)

**Goal**: Orchestrator loads workflows from registry, executes with smart orchestration

**Tasks**:
1. **Startup**: Load `workflows.json` into memory
2. **Selection Handler**:
   - Read `WorkflowSelection` from `state/selections/`
   - Resolve workflow definitions from registry
   - If `orchestration_mode == "smart"`:
     - Build dependency graph
     - Topological sort
     - Execute in order
   - If `orchestration_mode == "sequential"`:
     - Execute in user-selected order
3. **Execution**:
   - For each workflow:
     - Render Jinja2 prompt template with context
     - Invoke Claude CLI with rendered prompt
     - Capture stdout/stderr/exit_code
     - Emit `WorkflowExecution` to `state/executions/`
4. **Correlation**:
   - Preserve correlation_id throughout
   - Log all events to SQLite

**File**: `core/orchestrator.py`

**Key Changes**:
```python
# Load registry on startup
with open('state/workflows.json') as f:
    workflow_registry = json.load(f)

# Render prompt template
from jinja2 import Template
template = Template(workflow.prompt_template)
rendered_prompt = template.render(
    workspace_path=summary.workspace_path,
    session_id=summary.session_id,
    lychee_status=summary.lychee_status,
    git_status=summary.git_status,
    correlation_id=summary.correlation_id
)

# Execute with smart orchestration
if selection.orchestration_mode == "smart":
    execution_order = resolve_dependencies(selection.workflow_ids)
else:
    execution_order = selection.workflow_ids
```

**Testing**:
```bash
# Test single workflow
./testing/test-workflow-execute.py --workflow lychee-autofix

# Test multi-workflow with dependencies
./testing/test-workflow-execute.py --workflows format-code,fix-docstrings

# Verify smart orchestration order
```

**Success Criteria**:
- [ ] Orchestrator loads workflow registry
- [ ] Prompt templates rendered with context
- [ ] Smart orchestration resolves dependencies
- [ ] Multiple workflows execute correctly
- [ ] SQLite logs `execution.started`, `execution.completed` events

---

### Phase 6: Testing & Documentation

**Goal**: End-to-end testing, update all documentation to v4.0.0

**Tasks**:

**Testing**:
1. **Test 1**: Session stop with 0 errors
   - Expected: Summary sent, workflow menu shown, no lychee option
2. **Test 2**: Session stop with lychee errors
   - Expected: Summary sent, workflow menu includes lychee option
3. **Test 3**: Single workflow selection
   - Expected: Workflow executes, completion notification sent
4. **Test 4**: Multi-workflow selection (smart orchestration)
   - Expected: Workflows execute in dependency order
5. **Test 5**: Custom prompt
   - Expected: User-provided prompt executed
6. **Test 6**: Bot idle timeout
   - Expected: Bot shuts down after 10 minutes

**Documentation Updates**:
1. `README.md`: Update to v4.0.0, new directory structure
2. `COMPLETE_WORKFLOW.md`: Add session summary phase, workflow menu
3. `CONTRIBUTING.md`: Update file paths, workflow plugin guide
4. `testing/README.md`: Update test scripts for v4.0.0

**New Documentation**:
1. `WORKFLOW_PLUGIN_GUIDE.md`: How to create new workflows
2. `MIGRATION_v3_to_v4.md`: Detailed migration guide
3. `docs/WORKFLOW_REGISTRY.md`: Registry schema documentation

**Success Criteria**:
- [ ] All 6 test scenarios pass
- [ ] End-to-end correlation ID tracing works
- [ ] All docs updated to v4.0.0
- [ ] New plugin guide created

---

### Phase 7: Cleanup & Release

**Goal**: Archive legacy code, finalize v4.0.0 release

**Tasks**:
1. Move v3-specific code to `archive/v3.0.1/`:
   - Old notification handler
   - Hardcoded lychee logic
   - v3 migration docs
2. Update `.gitignore` (if needed)
3. Create git tag: `v4.0.0`
4. Update CHANGELOG.md
5. Create release summary document

**Git Commit Sequence**:
```bash
# Commit Phase 1-5 changes
git add .
git commit -m "refactor(telegram-workflows): migrate to v4.0.0 workflow registry system"

# Tag release
git tag -a v4.0.0 -m "Release v4.0.0: Telegram Workflows Orchestration"
```

**Success Criteria**:
- [ ] All legacy code archived
- [ ] Git tag created
- [ ] CHANGELOG.md updated
- [ ] Release summary created

---

## Rollback Plan

### If Issues Found During Migration

**Option A: Revert to v3.0.1**
```bash
# Revert all changes
git reset --hard v3.0.1-baseline

# Restart services
launchctl stop com.user.lychee.telegram-handler
launchctl start com.user.lychee.telegram-handler
```

**Option B: Pause Migration**
```bash
# Create branch for current work
git checkout -b migration-v4-paused

# Return to v3.0.1
git checkout main
git reset --hard v3.0.1-baseline
```

### If Issues Found After Deployment

**Option A: Emergency Rollback**
```bash
# Revert directory rename
git mv automation/telegram-workflows automation/lychee

# Revert state schema changes
mv state/summaries state/notifications
mv state/selections state/approvals
mv state/executions state/completions

# Commit
git commit -m "ROLLBACK: Emergency revert to v3.0.1"
```

**Option B: Forward Fix**
- Use v4 architecture but disable new workflows
- Keep only lychee workflow active
- Fix bugs incrementally

---

## Risk Assessment

### High Risk Items

1. **Directory Rename**
   - Risk: Breaks launchd services, hardcoded paths
   - Mitigation: Comprehensive grep for all paths, test services after rename
   - Rollback: `git mv` back to original name

2. **State Schema Changes**
   - Risk: Bot/orchestrator expect old format, crashes
   - Mitigation: Gradual migration, keep old handlers as fallback
   - Rollback: Revert state file patterns

3. **Hook Always Emits Summary**
   - Risk: Bot overwhelmed with notifications
   - Mitigation: Idle timeout still applies, bot shuts down after 10 min
   - Rollback: Add conditional check back

### Medium Risk Items

1. **Workflow Registry Loading**
   - Risk: Invalid JSON crashes bot
   - Mitigation: JSON schema validation on startup, fail-fast
   - Rollback: Use hardcoded workflows as fallback

2. **Smart Orchestration**
   - Risk: Circular dependencies crash orchestrator
   - Mitigation: Detect cycles, fallback to sequential
   - Rollback: Disable smart mode, use sequential only

### Low Risk Items

1. **Telegram UI Changes**
   - Risk: Users confused by new menu
   - Mitigation: Clear button labels, help text
   - Rollback: Not needed (UI-only change)

2. **Documentation Updates**
   - Risk: Outdated docs
   - Mitigation: Update all docs in single phase
   - Rollback: Not applicable

---

## Success Metrics

### Phase Completion

- [ ] Phase 0: Preparation ✅
- [ ] Phase 1: Workflow Registry
- [ ] Phase 2: Directory Rename
- [ ] Phase 3: Refactor Hook
- [ ] Phase 4: Refactor Bot
- [ ] Phase 5: Refactor Orchestrator
- [ ] Phase 6: Testing & Docs
- [ ] Phase 7: Cleanup & Release

### System Health

**Post-Migration Checks**:
```bash
# Verify services running
launchctl list | grep telegram-workflows

# Check recent events
sqlite3 state/events.db "SELECT event_type, COUNT(*) FROM session_events GROUP BY event_type;"

# Test end-to-end
./testing/test-e2e-workflow.sh
```

**Expected Event Types** (v4.0.0):
- `summary.created` (replaces `notification.created`)
- `summary.received` (replaces `notification.received`)
- `selection.received` (replaces `approval.created`)
- `execution.started` (replaces `orchestrator.started`)
- `execution.completed` (replaces `orchestrator.completed`)

### SLO Compliance

- **Availability**: 99% (same as v3)
- **Correctness**: 100% (all events logged)
- **Observability**: 100% (correlation ID tracking)
- **Maintainability**: Single source of truth (workflows.json)

---

## Timeline Estimate

| Phase                | Duration | Dependencies                   |
| -------------------- | -------- | ------------------------------ |
| Phase 0: Preparation | 2h       | None (✅ Complete)             |
| Phase 1: Registry    | 1h       | Phase 0                        |
| Phase 2: Rename      | 30min    | Phase 1                        |
| Phase 3: Hook        | 1h       | Phase 2                        |
| Phase 4: Bot         | 2h       | Phase 3                        |
| Phase 5: Orchestrator| 2h       | Phase 4                        |
| Phase 6: Testing     | 1.5h     | Phase 5                        |
| Phase 7: Cleanup     | 30min    | Phase 6                        |
| **Total**            | **10.5h**| Sequential execution           |

**Recommended Approach**: Execute phases 1-7 in single session to avoid partial states.

---

## Next Steps

1. **Review This Plan**: User approval required
2. **Create Git Tag**: `v3.0.1-baseline` before starting Phase 1
3. **Execute Phases Sequentially**: No skipping, verify each phase
4. **Update This Document**: Track progress, capture findings in `x-implementation-findings`

**Status**: ⏸️ Awaiting user approval to proceed with Phase 1

---

**Migration Plan Complete** - Ready for execution pending user confirmation.
