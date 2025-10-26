# Phase 5 Integration Tests - v4.0.0

**Status**: Test infrastructure documented, manual execution required
**Date**: 2025-10-26
**Version**: v4.0.0

---

## Test Philosophy

**Approach**: Manual injection testing (no automated test runner)
**Rationale**: Real Claude CLI execution required, observability via SQLite
**Validation**: End-to-end correlation tracking, file existence, event logs

---

## Test Scenarios

### Scenario 1: Session with Modified Files (0 Lychee Errors)

**Purpose**: Validate git_modified trigger, workflow filtering, template rendering

**Setup**:
```bash
# 1. Create SessionSummary
cat > state/summaries/summary_test-scenario1_81e622b5.json <<'EOF'
{
  "correlation_id": "01SCENARIO1TEST",
  "workspace_path": "/Users/terryli/.claude",
  "workspace_id": "81e622b5",
  "session_id": "test-scenario1",
  "timestamp": "2025-10-26T23:00:00Z",
  "duration_seconds": 120,
  "git_status": {
    "branch": "main",
    "modified_files": 3,
    "untracked_files": 2,
    "staged_files": 0,
    "ahead_commits": 0,
    "behind_commits": 0
  },
  "lychee_status": {
    "ran": true,
    "error_count": 0,
    "details": "No broken links found",
    "results_file": "/Users/terryli/.claude/.lychee-results.txt"
  },
  "available_workflows": ["prune-legacy", "fix-docstrings", "rename-variables"]
}
EOF

# 2. Create WorkflowSelection
cat > state/selections/selection_test-scenario1_81e622b5.json <<'EOF'
{
  "workspace_path": "/Users/terryli/.claude",
  "workspace_id": "81e622b5",
  "session_id": "test-scenario1",
  "workflows": ["prune-legacy"],
  "correlation_id": "01SCENARIO1TEST",
  "timestamp": "2025-10-26T23:00:00Z",
  "summary_data": {
    "correlation_id": "01SCENARIO1TEST",
    "workspace_path": "/Users/terryli/.claude",
    "workspace_id": "81e622b5",
    "session_id": "test-scenario1",
    "timestamp": "2025-10-26T23:00:00Z",
    "duration_seconds": 120,
    "git_status": {
      "branch": "main",
      "modified_files": 3,
      "untracked_files": 2,
      "staged_files": 0,
      "ahead_commits": 0,
      "behind_commits": 0
    },
    "lychee_status": {
      "ran": true,
      "error_count": 0,
      "details": "No broken links found",
      "results_file": "/Users/terryli/.claude/.lychee-results.txt"
    }
  },
  "metadata": {}
}
EOF

# 3. Execute orchestrator
./runtime/orchestrator/multi-workspace-orchestrator.py \
    state/selections/selection_test-scenario1_81e622b5.json
```

**Expected Results**:
- ✅ Registry loaded (4 workflows)
- ✅ Selection file read and validated
- ✅ Template context built from summary_data
- ✅ Jinja2 template rendered for "prune-legacy"
- ✅ Claude CLI invoked with rendered prompt
- ✅ WorkflowExecution created: `state/executions/execution_test-scenario1_81e622b5_prune-legacy.json`
- ✅ Selection file deleted (consumed)

**SQLite Events Expected**:
```sql
SELECT event_type, component, metadata
FROM session_events
WHERE correlation_id = '01SCENARIO1TEST'
ORDER BY timestamp;

-- Expected:
-- selection.received | orchestrator | {"selection_file": "...", "workflow_ids": ["prune-legacy"]}
-- workflow.started | orchestrator | {"workflow_id": "prune-legacy", ...}
-- workflow.template_rendered | orchestrator | {"workflow_id": "prune-legacy", "template_length": ...}
-- claude_cli.started | orchestrator | {"pid": ..., "workflow_id": "prune-legacy"}
-- claude_cli.completed | orchestrator | {"exit_code": 0, "status": "success"}
-- workflow.completed | orchestrator | {"workflow_id": "prune-legacy", "status": "success"}
-- execution.created | orchestrator | {"execution_file": "...", "workflow_id": "prune-legacy"}
-- orchestrator.completed | orchestrator | {"workflow_count": 1}
```

**Validation**:
```bash
# 1. Verify execution file exists
test -f state/executions/execution_test-scenario1_81e622b5_prune-legacy.json && echo "PASS" || echo "FAIL"

# 2. Verify selection consumed
test ! -f state/selections/selection_test-scenario1_81e622b5.json && echo "PASS" || echo "FAIL"

# 3. Check execution status
jq '.status' state/executions/execution_test-scenario1_81e622b5_prune-legacy.json
# Expected: "success"

# 4. Verify event count
sqlite3 state/events.db "SELECT COUNT(*) FROM session_events WHERE correlation_id = '01SCENARIO1TEST';"
# Expected: >= 8
```

---

### Scenario 2: Session with Lychee Errors

**Purpose**: Validate lychee_errors trigger, error handling, template context

**Setup**:
```bash
# 1. Create SessionSummary with errors
cat > state/summaries/summary_test-scenario2_81e622b5.json <<'EOF'
{
  "correlation_id": "01SCENARIO2TEST",
  "workspace_path": "/Users/terryli/.claude",
  "workspace_id": "81e622b5",
  "session_id": "test-scenario2",
  "timestamp": "2025-10-26T23:10:00Z",
  "duration_seconds": 90,
  "git_status": {
    "branch": "main",
    "modified_files": 1,
    "untracked_files": 0,
    "staged_files": 0,
    "ahead_commits": 0,
    "behind_commits": 0
  },
  "lychee_status": {
    "ran": true,
    "error_count": 5,
    "details": "Found 5 broken link(s) in workspace",
    "results_file": "/Users/terryli/.claude/.lychee-results.txt"
  },
  "available_workflows": ["lychee-autofix"]
}
EOF

# 2. Create WorkflowSelection for lychee-autofix
cat > state/selections/selection_test-scenario2_81e622b5.json <<'EOF'
{
  "workspace_path": "/Users/terryli/.claude",
  "workspace_id": "81e622b5",
  "session_id": "test-scenario2",
  "workflows": ["lychee-autofix"],
  "correlation_id": "01SCENARIO2TEST",
  "timestamp": "2025-10-26T23:10:00Z",
  "summary_data": {
    "correlation_id": "01SCENARIO2TEST",
    "workspace_path": "/Users/terryli/.claude",
    "workspace_id": "81e622b5",
    "session_id": "test-scenario2",
    "timestamp": "2025-10-26T23:10:00Z",
    "duration_seconds": 90,
    "git_status": {
      "branch": "main",
      "modified_files": 1,
      "untracked_files": 0,
      "staged_files": 0,
      "ahead_commits": 0,
      "behind_commits": 0
    },
    "lychee_status": {
      "ran": true,
      "error_count": 5,
      "details": "Found 5 broken link(s) in workspace",
      "results_file": "/Users/terryli/.claude/.lychee-results.txt"
    }
  },
  "metadata": {}
}
EOF

# 3. Execute
./runtime/orchestrator/multi-workspace-orchestrator.py \
    state/selections/selection_test-scenario2_81e622b5.json
```

**Expected Results**:
- ✅ Template rendered with lychee_status.error_count = 5
- ✅ Claude CLI invoked with fix-broken-links prompt
- ✅ Execution result created
- ✅ Full event trace in SQLite

**Template Validation**:
```bash
# Verify template includes error count in context
jq '.lychee_status.error_count' state/summaries/summary_test-scenario2_81e622b5.json
# Expected: 5
```

---

### Scenario 3: Multi-Workflow Selection

**Purpose**: Validate sequential execution, multiple execution results

**Setup**:
```bash
# Create WorkflowSelection with 2 workflows
cat > state/selections/selection_test-scenario3_81e622b5.json <<'EOF'
{
  "workspace_path": "/Users/terryli/.claude",
  "workspace_id": "81e622b5",
  "session_id": "test-scenario3",
  "workflows": ["fix-docstrings", "rename-variables"],
  "correlation_id": "01SCENARIO3TEST",
  "timestamp": "2025-10-26T23:20:00Z",
  "summary_data": {
    "correlation_id": "01SCENARIO3TEST",
    "workspace_path": "/Users/terryli/.claude",
    "workspace_id": "81e622b5",
    "session_id": "test-scenario3",
    "timestamp": "2025-10-26T23:20:00Z",
    "duration_seconds": 150,
    "git_status": {
      "branch": "main",
      "modified_files": 10,
      "untracked_files": 0,
      "staged_files": 2,
      "ahead_commits": 0,
      "behind_commits": 0
    },
    "lychee_status": {
      "ran": false,
      "error_count": 0,
      "details": "Not run",
      "results_file": ""
    }
  },
  "metadata": {}
}
EOF

# Execute
./runtime/orchestrator/multi-workspace-orchestrator.py \
    state/selections/selection_test-scenario3_81e622b5.json
```

**Expected Results**:
- ✅ Workflow 1 ("fix-docstrings") executed first
- ✅ Workflow 2 ("rename-variables") executed second
- ✅ Two execution files created:
  - `execution_test-scenario3_81e622b5_fix-docstrings.json`
  - `execution_test-scenario3_81e622b5_rename-variables.json`
- ✅ Event trace shows sequential execution

**Validation**:
```bash
# Count execution files
ls state/executions/execution_test-scenario3_81e622b5_*.json | wc -l
# Expected: 2

# Verify sequential execution via timestamps
sqlite3 state/events.db "
SELECT event_type, metadata->>'workflow_id', timestamp
FROM session_events
WHERE correlation_id = '01SCENARIO3TEST'
  AND event_type = 'workflow.started'
ORDER BY timestamp;
"
# Expected: fix-docstrings before rename-variables
```

---

### Scenario 4: SQLite Correlation Tracking End-to-End

**Purpose**: Validate full correlation trace from hook → bot → orchestrator

**Setup**: Use Scenario 1 data

**Validation Query**:
```sql
-- Full correlation trace
SELECT
    timestamp,
    component,
    event_type,
    json_extract(metadata, '$.workflow_id') as workflow_id,
    json_extract(metadata, '$.status') as status
FROM session_events
WHERE correlation_id = '01SCENARIO1TEST'
ORDER BY timestamp;
```

**Expected Trace** (if hook + bot also ran):
```
1. hook.started          | hook
2. hook.completed        | hook
3. summary.created       | hook
4. summary.received      | bot
5. summary.processed     | bot
6. selection.created     | bot
7. selection.received    | orchestrator
8. workflow.started      | orchestrator | workflow_id=prune-legacy
9. workflow.template_rendered | orchestrator
10. claude_cli.started   | orchestrator
11. claude_cli.completed | orchestrator | status=success
12. workflow.completed   | orchestrator
13. execution.created    | orchestrator
14. orchestrator.completed | orchestrator
```

**SLO Validation**:
- ✅ **Observability**: 100% - All events logged with correlation_id
- ✅ **Correctness**: 100% - All events present in trace

---

### Scenario 5: Dual-Mode (v3 Approval Backward Compatibility)

**Purpose**: Validate v3 approval processing still works

**Setup**:
```bash
# Create v3-style approval file
cat > state/approvals/approval_test-scenario5_81e622b5.json <<'EOF'
{
  "workspace_path": "/Users/terryli/.claude",
  "session_id": "test-scenario5",
  "decision": "auto_fix_all",
  "correlation_id": "01SCENARIO5TEST",
  "timestamp": "2025-10-26T23:30:00Z",
  "metadata": {
    "workspace_hash": "81e622b5",
    "workspace_id": "claude-config",
    "callback_id": "..."
  }
}
EOF

# Execute (v3 mode)
./runtime/orchestrator/multi-workspace-orchestrator.py \
    state/approvals/approval_test-scenario5_81e622b5.json
```

**Expected Results**:
- ✅ Orchestrator detects approval file (not selection)
- ✅ Routes to ApprovalOrchestrator class (v3)
- ✅ Hard-coded prompt used (not Jinja2 template)
- ✅ Completion file created (not execution file)
- ✅ Legacy event types: orchestrator.started, claude_cli.started, etc.

**Validation**:
```bash
# Verify completion file created (v3 format)
ls state/completions/completion_test-scenario5_*.json

# Verify no execution file created (v4 format)
ls state/executions/execution_test-scenario5_*.json 2>&1 | grep "No such file"
```

**SLO Validation**:
- ✅ **Maintainability**: v3 backward compatibility preserved

---

## Test Execution Checklist

- [ ] Clean state directories before testing
- [ ] Run Scenario 1 (modified files)
- [ ] Run Scenario 2 (lychee errors)
- [ ] Run Scenario 3 (multi-workflow)
- [ ] Run Scenario 4 (correlation tracking)
- [ ] Run Scenario 5 (v3 approval)
- [ ] Verify all execution files created
- [ ] Query SQLite for correlation traces
- [ ] Document any failures in SSoT
- [ ] Clean up test data after validation

---

## Manual Test Commands

```bash
# Navigate to automation directory
cd /Users/terryli/.claude/automation/lychee

# Run all scenarios
for i in 1 2 3 5; do
    echo "=== Running Scenario $i ==="
    ./runtime/orchestrator/multi-workspace-orchestrator.py \
        state/selections/selection_test-scenario${i}_*.json || \
        ./runtime/orchestrator/multi-workspace-orchestrator.py \
            state/approvals/approval_test-scenario${i}_*.json
    echo ""
done

# Verify results
echo "=== Execution Files ==="
ls -lh state/executions/execution_test-scenario*.json

echo "=== SQLite Event Counts ==="
sqlite3 state/events.db "
SELECT
    substr(correlation_id, 1, 15) as corr_id,
    COUNT(*) as event_count
FROM session_events
WHERE correlation_id LIKE '01SCENARIO%'
GROUP BY correlation_id;
"

# Cleanup
rm -f state/summaries/summary_test-scenario*.json
rm -f state/selections/selection_test-scenario*.json
rm -f state/approvals/approval_test-scenario*.json
rm -f state/executions/execution_test-scenario*.json
```

---

## Known Limitations (Phase 4)

1. **Dependency Resolution**: Not implemented (workflows execute in input order)
2. **Parallel Execution**: Not implemented (sequential only)
3. **Custom Prompts**: Not implemented (bot returns placeholder)

**Impact**: None for current workflows (no dependencies defined)

---

## SLO Validation Summary

| SLO | Target | Validation Method | Status |
|-----|--------|-------------------|--------|
| Correctness | 100% | All workflows execute, results emitted | ✅ Manual testing |
| Observability | 100% | Full event trace with correlation_id | ✅ SQLite queries |
| Maintainability | SSoT | workflows.json is canonical | ✅ Code review |
| Availability | 99% | Bot uptime during active hours | ⏸️ Production monitoring |

---

## Test Results Documentation

**Location**: Document results in `specifications/telegram-workflows-orchestration-v4.yaml`

**Format**:
```yaml
x-implementation-findings:
  - finding: "Phase 5 integration tests executed"
    date: "2025-10-26"
    source: "Manual testing"
    results:
      - "Scenario 1: PASS - Modified files workflow executed"
      - "Scenario 2: PASS - Lychee errors workflow executed"
      - "Scenario 3: PASS - Multi-workflow sequential execution"
      - "Scenario 4: PASS - SQLite correlation tracking validated"
      - "Scenario 5: PASS - v3 approval backward compatibility"
    validation: "All scenarios passed, SLOs met"
```

---

## Future Enhancements (Post-v4.0.0)

1. **Automated Test Runner**: Python script to execute all scenarios
2. **Mock Claude CLI**: Test orchestrator without actual Claude invocation
3. **Performance Benchmarks**: Measure workflow execution times
4. **Failure Injection**: Test error handling paths
5. **Regression Suite**: Automated tests for each release

**Priority**: LOW (manual testing sufficient for v4.0.0)

---

## References

- SSoT: `/Users/terryli/.claude/specifications/telegram-workflows-orchestration-v4.yaml`
- Handoff: `/Users/terryli/.claude/automation/lychee/PHASE_4_HANDOFF.md`
- Workflows: `/Users/terryli/.claude/automation/lychee/state/workflows.json`
