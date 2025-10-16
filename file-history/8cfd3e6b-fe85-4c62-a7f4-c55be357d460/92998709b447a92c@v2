# Headless Execution Implementation Plan

**Version**: 2.0.0
**Created**: 2025-10-13
**Updated**: 2025-10-13
**Status**: RESOLVED
**Parent**: AI_AGENT_WORKFLOW.md

## Service Level Objectives

### Availability
- Target: 95% success rate for headless script execution
- Measurement: Successful CSV generation within timeout period
- Failure condition: No CSV generated OR MT5 process hangs

### Correctness
- Target: 100% data integrity (no missing/corrupted bars)
- Measurement: validate_export.py integrity checks pass
- Failure condition: Any integrity check fails OR indicator correlation < 0.999

### Observability
- Target: All execution attempts logged with exit codes
- Measurement: Log file exists with timestamp, command, output, exit code
- Failure condition: Execution occurs without log entry

### Maintainability
- Target: Single executable entry point (mq5run)
- Measurement: No manual config file editing required
- Failure condition: User must modify config files between runs

## Implementation Strategy

### Phase 1: Diagnostic (5 min) - COMPLETE ✅

**Objective**: Locate MT5 logs to determine why script didn't execute

**Tasks**:
1. ✅ Find all .log files modified in last 24h in bottle
2. ✅ Search logs for keywords: "script", "export", "startup", "error", "fail"
3. ✅ Identify actual MT5 log location in portable mode
4. ✅ Extract relevant error messages

**Success Criteria**:
- Log file located: YES ✅
- Error message found: YES ✅
- Root cause identified: YES ✅

**Results**:
- **Log location**: `/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/logs/20251013.log`
- **Error found**: `QM	2	14:57:22.303	Terminal	cannot load config "C:\Program Files\MetaTrader 5\config\startup_20251013_145717.ini"" at start`
- **Root cause**: Config file path had double quotes due to shell quoting + absolute path with spaces
- **Solution**: Use relative path `config\startup_${TIMESTAMP}.ini` without quotes

### Phase 2: Research (conditional) - SKIPPED ✅

**Trigger**: Phase 1 fails to identify root cause (DID NOT OCCUR)

**Research Queries**:
1. "CrossOver cxstart MetaTrader 5 portable mode macOS headless script execution 2023-2025"
2. "MT5 startup.ini Script parameter Wine CrossOver portable installation"
3. "MetaTrader 5 MQL5/Logs location portable mode Wine bottle"

**Off-the-shelf Solutions to Evaluate**:
1. MetaTrader5 Python package (pypi.org/project/MetaTrader5/)
2. mt5linux project (github.com/lucas-campagna/mt5linux)
3. Docker mt5 images with VNC

**Success Criteria**:
- Working example found: YES/NO
- Solution applicable to CrossOver/macOS: YES/NO
- Complexity assessment: LOW/MEDIUM/HIGH

**Failure Escalation**: If no solution → Phase 3

**Outcome**: Not executed - Phase 1 diagnostic successfully identified and resolved root cause

### Phase 3: Python API Implementation (alternative approach) - SKIPPED ✅

**Trigger**: Phases 1-2 fail OR Python API identified as superior

**Objective**: Replace startup.ini approach with MetaTrader5 Python package

**Architecture**:
```
MT5 (running 24/7) ← Python API → mq5run wrapper → CSV export
```

**Requirements**:
1. MetaTrader5 Python package installed in Wine bottle
2. MT5 running with API enabled
3. RPyC or similar for cross-process communication

**Implementation Steps**:
1. Install MetaTrader5 package in Wine Python
2. Test mt5.initialize() from host Python
3. Replace mq5run script execution with mt5.copy_rates_from()
4. Export to CSV directly from Python

**Success Criteria**:
- mt5.initialize() succeeds
- mt5.copy_rates_from() returns data
- No MQL5 script execution required

**Outcome**: Not executed - startup.ini approach working as intended after Phase 1 fix

## Current Status

### Completed
- ✅ Manual script execution validated
- ✅ CSV export format verified
- ✅ Python validator working
- ✅ mq5run wrapper created
- ✅ Startup.ini format correct per research
- ✅ MT5 log location identified
- ✅ Root cause diagnosed (config path quoting)
- ✅ Config path fix implemented
- ✅ Headless execution validated (2 CSV files generated)
- ✅ Data integrity confirmed (correlation 0.999902)

### Blocked
None - all blockers resolved

### Next Action
None - implementation complete and validated

## Decision Log

### Decision 1: Try diagnostic before research
**Date**: 2025-10-13
**Rationale**: Research already covered generic Wine patterns. Need CrossOver/macOS-specific info which logs will reveal.
**Alternative**: Research first (rejected - wastes time if issue is simple)

### Decision 2: Python API as fallback
**Rationale**: Multiple 2022+ sources suggest Python API is preferred over startup configs for automation
**Risk**: Requires Wine Python setup, may have own complexity
**Mitigation**: Only pursue if diagnostic fails

### Decision 3: Phase 1 sufficient - Phases 2-3 skipped
**Date**: 2025-10-13
**Rationale**: Log analysis immediately revealed exact error (config path quoting). Single-line fix resolved issue completely.
**Outcome**: Startup.ini approach validated working. Python API and additional research unnecessary.
**SLOs Met**: Availability (100% success), Correctness (0.999902 correlation), Observability (full logs), Maintainability (single mq5run entry point)

## References

**Research Findings**: /Users/terryli/eon/mql5-crossover/historical.txt (lines 5000-5073)
**Implementation**: /Users/terryli/eon/mql5-crossover/mq5run
**Validation**: /Users/terryli/eon/mql5-crossover/SUCCESS_REPORT.md

## Superseded Plans

### Phase 2: Research (Web search for CrossOver-specific patterns)
**Status**: Skipped - not required
**Reason**: Phase 1 diagnostic immediately identified root cause through log analysis

### Phase 3: Python API Implementation
**Status**: Skipped - not required
**Reason**: Startup.ini approach working as designed after config path fix
**Note**: Python API remains valid future alternative for direct data access without MQL5 scripts

---

**Update Protocol**:
- Increment version on major changes
- Mark phases COMPLETE/FAILED/SKIPPED
- Move failed approaches to "Superseded Plans" section
- Update references to point to latest implementations
