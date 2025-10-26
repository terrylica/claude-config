# Phase 4 Orchestrator Implementation Handoff

**Date**: 2025-10-26
**Version**: v4.0.0
**Status**: SCAFFOLDING COMPLETE / CORE IMPLEMENTATION PENDING
**Commits**: c406b72 (Phase 2), 1d11055 (Phase 3), e094550 (Phase 4 scaffolding)

---

## Current Implementation Status

### ✅ Complete (Phases 0-3)

**Phase 0: Pre-Migration Validation**
- OpenAPI 3.1.1 specification: `specifications/telegram-workflows-orchestration-v4.yaml`
- Git baseline established
- Pre-migration validation script

**Phase 1: Workflow Registry**
- `automation/lychee/state/workflows.json` created
- 4 workflows defined: lychee-autofix, prune-legacy, fix-docstrings, rename-variables
- JSON schema validated
- Jinja2 templates validated

**Phase 2: Hook Refactor**
- File: `automation/lychee/runtime/hook/check-links-hybrid.sh`
- SessionSummary emitted on EVERY stop
- Git status extraction (branch, modified/untracked/staged, ahead/behind)
- Session duration tracking
- Dual-mode: SessionSummary (v4) + Notification (v3)
- Bot always starts (not just on errors)
- SQLite logging: hook.started, hook.completed, summary.created

**Phase 3: Bot Refactor**
- File: `automation/lychee/runtime/bot/multi-workspace-bot.py`
- Workflow registry loading
- Trigger-based filtering (lychee_errors, git_modified, always)
- SummaryHandler class (~180 lines)
- Dynamic workflow keyboard (2 per row)
- Workflow selection handler
- Selection files created in `state/selections/`
- Dual-mode: summaries (v4) + notifications (v3)
- SQLite logging: summary.received, summary.processed, selection.created

**Phase 4: Scaffolding**
- File: `automation/lychee/runtime/orchestrator/multi-workspace-orchestrator.py`
- Jinja2 dependency added
- Registry loading function: `load_workflow_registry()`
- Template rendering function: `render_workflow_prompt()`
- Dependency resolver placeholder: `resolve_workflow_dependencies()`
- Constants: SELECTIONS_DIR, EXECUTIONS_DIR, WORKFLOWS_REGISTRY

### ⏹️ Pending (Phase 4 Core)

1. **WorkflowOrchestrator Class**
   - Process WorkflowSelection files
   - Multi-workflow execution loop
   - Template context building (from SessionSummary)
   - Claude CLI invocation per workflow
   - Execution results emission

2. **Main Function Updates**
   - Dual-mode CLI argument handling: `--selection-file` (v4) or approval file (v3)
   - Registry loading on startup
   - Route to WorkflowOrchestrator or ApprovalOrchestrator

3. **Testing**
   - Inject test selection file
   - Verify Jinja2 rendering
   - Verify Claude CLI invocation
   - Verify execution results emission
   - Verify SQLite event logging

---

## Architecture Overview

### Data Flow (v4.0.0)

```
User Session Ends
    ↓
Hook: SessionSummary created → state/summaries/
    ↓
Bot: Loads registry, filters workflows, shows menu
    ↓
User: Selects workflow(s)
    ↓
Bot: WorkflowSelection created → state/selections/
    ↓
Orchestrator: Processes selection
    ├─ Loads registry
    ├─ Resolves dependencies (Phase 4: no-op, returns input order)
    ├─ For each workflow:
    │   ├─ Renders Jinja2 template with context
    │   ├─ Invokes Claude CLI
    │   └─ Emits WorkflowExecution → state/executions/
    └─ Bot: Sends completion to Telegram
```

### State Files Structure

```
automation/lychee/state/
├── workflows.json           # Registry (v4 SSoT)
├── summaries/               # SessionSummary files (Phase 2)
│   └── summary_{session_id}_{workspace_hash}.json
├── selections/              # WorkflowSelection files (Phase 3)
│   └── selection_{session_id}_{workspace_hash}.json
├── executions/              # WorkflowExecution results (Phase 4 TODO)
│   └── execution_{session_id}_{workspace_hash}_{workflow_id}.json
├── notifications/           # v3 backward compat (dual-mode)
├── approvals/               # v3 backward compat (dual-mode)
├── completions/             # Unchanged (used by both v3 and v4)
└── events.db                # SQLite event log (ULID correlation)
```

---

## Implementation Guide

### Step 1: Create WorkflowOrchestrator Class

**Location**: After `ApprovalOrchestrator` class in `multi-workspace-orchestrator.py`

**Required Methods**:

```python
class WorkflowOrchestrator:
    """Processes workflow selections and executes multi-workflow pipelines (v4.0.0)."""

    def __init__(self):
        self.correlation_id = None
        self.workspace_hash = None
        self.session_id = None
        self.registry = None

    async def process_selection(self, selection_file: Path) -> None:
        """
        Process WorkflowSelection file and execute workflows.

        Args:
            selection_file: Path to WorkflowSelection JSON

        Raises:
            All errors propagate (fail-fast)
        """
        # 1. Read and validate selection
        # 2. Load registry if not loaded
        # 3. Validate workspace path
        # 4. Load SessionSummary for template context
        # 5. Resolve workflow dependencies
        # 6. Execute workflows sequentially
        # 7. Emit execution results
        # 8. Cleanup selection file

    async def _execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute single workflow.

        Args:
            workflow_id: Workflow identifier
            context: Template rendering context

        Returns:
            Execution result metadata
        """
        # 1. Get workflow from registry
        # 2. Render Jinja2 template
        # 3. Invoke Claude CLI
        # 4. Emit WorkflowExecution result
        # 5. Return execution metadata

    def _build_template_context(
        self,
        summary: Dict[str, Any],
        workspace_path: Path
    ) -> Dict[str, Any]:
        """Build Jinja2 template context from SessionSummary."""
        # Extract: workspace_path, session_id, git_status, lychee_status, correlation_id
        pass
```

### Step 2: Template Context Structure

**Required Context Fields** (from SessionSummary):

```python
context = {
    "workspace_path": "/path/to/workspace",  # str
    "session_id": "uuid",                    # str
    "correlation_id": "ulid",                # str
    "git_status": {                          # dict
        "branch": "main",
        "modified_files": 4,
        "untracked_files": 3,
        "staged_files": 0,
        "ahead_commits": 0,
        "behind_commits": 0
    },
    "lychee_status": {                       # dict
        "ran": True,                         # bool
        "error_count": 0,                    # int
        "details": "No broken links found",  # str
        "results_file": "/path/.lychee-results.txt"  # str
    }
}
```

**Template Rendering Example**:

```python
workflow = registry["workflows"]["lychee-autofix"]
template = Template(workflow["prompt_template"])
prompt = template.render(**context)
# Result: "Fix broken links detected by Lychee in /path/to/workspace.\n\n..."
```

### Step 3: WorkflowExecution Result Schema

**File**: `state/executions/execution_{session_id}_{workspace_hash}_{workflow_id}.json`

```json
{
  "correlation_id": "01K8...",
  "workspace_path": "/path/to/workspace",
  "workspace_id": "81e622b5",
  "session_id": "uuid",
  "workflow_id": "lychee-autofix",
  "workflow_name": "Fix Broken Links",
  "status": "success",
  "exit_code": 0,
  "duration_seconds": 45.2,
  "stdout": "...",
  "stderr": "",
  "timestamp": "2025-10-26T22:35:00Z",
  "metadata": {
    "estimated_duration": 30,
    "risk_level": "low",
    "category": "validation"
  }
}
```

### Step 4: Update main() Function

**Required Changes**:

```python
async def main() -> int:
    """Main entry point - dual-mode (selections or approvals)."""
    global workflow_registry

    # Phase 4: Load registry
    print("📋 Loading workflow registry...")
    workflow_registry = load_workflow_registry()

    # Parse CLI arguments
    if len(sys.argv) < 2:
        print("Usage: orchestrator.py <selection-file-or-approval-file>", file=sys.stderr)
        return 1

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"❌ File not found: {input_file}", file=sys.stderr)
        return 1

    # Route based on file type
    if "selection_" in input_file.name:
        # v4: Process WorkflowSelection
        orchestrator = WorkflowOrchestrator()
        await orchestrator.process_selection(input_file)
    elif "approval_" in input_file.name:
        # v3: Process Approval (backward compat)
        orchestrator = ApprovalOrchestrator()
        await orchestrator.process_approval(input_file)
    else:
        print(f"❌ Unknown file type: {input_file.name}", file=sys.stderr)
        return 1

    return 0
```

### Step 5: Load SessionSummary for Context

**Required**: Read summary file to get template context

```python
def _read_session_summary(self, session_id: str, workspace_hash: str) -> Dict[str, Any]:
    """Read SessionSummary file for template context."""
    summary_file = SUMMARIES_DIR / f"summary_{session_id}_{workspace_hash}.json"

    if not summary_file.exists():
        # Summary may have been consumed by bot
        # Fallback: Use minimal context from selection file
        raise FileNotFoundError(f"SessionSummary not found: {summary_file}")

    with open(summary_file) as f:
        return json.load(f)
```

**Alternative Approach**: Store summary data in selection file (bot could include it)

---

## Testing Strategy

### Manual Testing (Phase 4)

**Test 1: Inject Selection File**

```bash
# 1. Create test selection
cat > /Users/terryli/.claude/automation/lychee/state/selections/selection_test_12345678.json <<EOF
{
  "workspace_path": "/Users/terryli/.claude",
  "workspace_id": "12345678",
  "session_id": "test-phase4",
  "workflows": ["prune-legacy"],
  "correlation_id": "01K8TEST",
  "timestamp": "2025-10-26T22:00:00Z",
  "metadata": {}
}
EOF

# 2. Create corresponding summary (for context)
cat > /Users/terryli/.claude/automation/lychee/state/summaries/summary_test-phase4_12345678.json <<EOF
{
  "correlation_id": "01K8TEST",
  "workspace_path": "/Users/terryli/.claude",
  "workspace_id": "12345678",
  "session_id": "test-phase4",
  "timestamp": "2025-10-26T22:00:00Z",
  "duration_seconds": 60,
  "git_status": {
    "branch": "main",
    "modified_files": 2,
    "untracked_files": 0,
    "staged_files": 1,
    "ahead_commits": 0,
    "behind_commits": 0
  },
  "lychee_status": {
    "ran": true,
    "error_count": 0,
    "details": "No broken links found",
    "results_file": "/Users/terryli/.claude/.lychee-results.txt"
  },
  "available_workflows": ["prune-legacy", "fix-docstrings"]
}
EOF

# 3. Run orchestrator
cd /Users/terryli/.claude/automation/lychee
./runtime/orchestrator/multi-workspace-orchestrator.py state/selections/selection_test_12345678.json
```

**Expected Output**:
- Registry loaded
- Template rendered with session context
- Claude CLI invoked
- WorkflowExecution result created in `state/executions/`
- SQLite events logged: orchestrator.started, claude_cli.started, claude_cli.completed, workflow.executed

**Test 2: Verify Jinja2 Rendering**

```python
# Quick test in Python REPL
from jinja2 import Template
import json

with open("state/workflows.json") as f:
    registry = json.load(f)

workflow = registry["workflows"]["prune-legacy"]
template = Template(workflow["prompt_template"])

context = {
    "workspace_path": "/Users/terryli/.claude",
    "session_id": "test",
    "git_status": {"modified_files": 2},
    "correlation_id": "01K8TEST"
}

prompt = template.render(**context)
print(prompt)
# Should output: "Identify and remove legacy code in /Users/terryli/.claude: ..."
```

---

## Key Implementation Decisions

### 1. Dependency Resolution (Phase 4 Limitation)

**Decision**: Return workflows in provided order (no topological sort)

**Rationale**:
- Workflows in v4.0.0 have no dependencies (all `dependencies: []`)
- Proper dependency resolution requires topological sort algorithm
- Can be added in Phase 5+ without breaking changes

**Code**:
```python
def resolve_workflow_dependencies(workflow_ids, registry):
    # Phase 4: No-op, return input order
    print("⚠️  Dependency resolution not implemented")
    return workflow_ids
```

### 2. SessionSummary Availability

**Challenge**: Bot consumes (deletes) summary files after processing

**Options**:
- A. Store summary data in selection file (bot includes it)
- B. Don't delete summary files (bot marks as processed instead)
- C. Orchestrator fails if summary missing (require re-run from hook)

**Recommendation**: Option A (store in selection file)

**Changes Required** (bot):
```python
# In handle_workflow_selection()
selection_state = {
    "workspace_path": workspace_path,
    "workspace_id": workspace_hash,
    "session_id": session_id,
    "workflows": [workflow_id],
    "correlation_id": correlation_id,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "summary_data": summary,  # ADD THIS
    "metadata": {...}
}
```

### 3. Multi-Workflow Execution

**Approach**: Sequential execution (for loop)

```python
for workflow_id in ordered_workflow_ids:
    result = await self._execute_workflow(workflow_id, context)
    # Emit result immediately (don't wait for all to complete)
```

**Future Enhancement**: Parallel execution for independent workflows

---

## SQLite Event Tracking

**New Events for Phase 4**:

| Event Type | Component | Metadata |
|------------|-----------|----------|
| `selection.received` | orchestrator | selection_file, workflow_ids |
| `workflow.started` | orchestrator | workflow_id, workflow_name |
| `workflow.template_rendered` | orchestrator | workflow_id, template_length |
| `workflow.completed` | orchestrator | workflow_id, status, duration |
| `execution.created` | orchestrator | execution_file, workflow_id |

**Query for End-to-End Trace**:

```sql
SELECT event_type, component, timestamp, metadata
FROM session_events
WHERE correlation_id = '01K8...'
ORDER BY timestamp;
```

**Expected Trace**:
1. hook.started
2. hook.completed
3. summary.created
4. summary.received (bot)
5. summary.processed (bot)
6. selection.created (bot)
7. selection.received (orchestrator)
8. workflow.started (orchestrator)
9. claude_cli.started (orchestrator)
10. claude_cli.completed (orchestrator)
11. workflow.completed (orchestrator)
12. execution.created (orchestrator)

---

## SLO Validation

**Phase 4 SLOs**:

| SLO | Target | Validation Method |
|-----|--------|-------------------|
| Correctness | 100% | All workflows execute, results emitted |
| Observability | 100% | All events logged with correlation_id |
| Maintainability | Single source | workflows.json is canonical |

---

## Next Session Resumption

**Commands to Resume**:

```bash
# 1. Check current state
cd /Users/terryli/.claude
git status
git log --oneline -5

# 2. Review handoff
cat automation/lychee/PHASE_4_HANDOFF.md

# 3. Check todos
cat todos/*agent*.json | jq '.todos[] | select(.status != "completed")'

# 4. Review SSoT
less specifications/telegram-workflows-orchestration-v4.yaml

# 5. Start implementation
# Edit: automation/lychee/runtime/orchestrator/multi-workspace-orchestrator.py
# Add WorkflowOrchestrator class after line 189
```

**Key Files**:
- SSoT: `specifications/telegram-workflows-orchestration-v4.yaml`
- Migration Plan: `automation/lychee/MIGRATION_v3_to_v4_PLAN_v2.md`
- Orchestrator: `automation/lychee/runtime/orchestrator/multi-workspace-orchestrator.py`
- Handoff: `automation/lychee/PHASE_4_HANDOFF.md` (this file)

---

## Estimated Remaining Effort

**Phase 4 Core**: 2-3 hours
- WorkflowOrchestrator class: 1 hour
- Template context building: 30 min
- Execution loop: 1 hour
- Testing: 30 min

**Phase 5 (Integration Testing)**: 2-3 hours
- 5 test scenarios
- SQLite validation
- Documentation

**Phase 6 (Rename)**: 1-1.5 hours
- Stop services, git mv, update paths

**Phase 7 (Cleanup)**: 1-2 hours
- Remove dual-mode code

**Phase 8 (Docs)**: 2-3 hours
- README, CHANGELOG, release notes

**Total Remaining**: ~10-15 hours

---

## Success Criteria

**Phase 4 Complete When**:
- ✅ WorkflowOrchestrator processes selection files
- ✅ Jinja2 templates render with session context
- ✅ Claude CLI invoked for each workflow
- ✅ WorkflowExecution results emitted to executions/
- ✅ Dual-mode maintained (selections + approvals)
- ✅ SQLite events logged with correlation tracking
- ✅ Manual test passes (inject selection file)
- ✅ SSoT updated with findings
- ✅ Committed and pushed

**v4.0.0 Release Ready When**:
- All Phases 0-8 complete
- Integration tests pass (5 scenarios)
- Documentation updated
- Git tag created: v4.0.0
- Migration plan marked complete
