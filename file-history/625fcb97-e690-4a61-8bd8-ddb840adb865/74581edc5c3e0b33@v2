# Workflow Validation Audit & Testing Plan

**Date**: 2025-10-17
**Purpose**: Audit documented workflows against reality before presenting to coworkers
**Status**: 🔴 CRITICAL GAPS FOUND - DO NOT SHARE YET

---

## Executive Summary

**Finding**: The documented workflow has **7 critical gaps** that could cause a new user to fail. We've only validated ONE indicator (Laguerre RSI) and haven't tested if someone new can follow the guide from scratch.

**Risk**: Presenting this workflow to coworkers without end-to-end validation could damage credibility.

**Recommendation**: Complete the validation test plan below before sharing with team.

---

## Critical Gaps Found

### Gap 1: Missing CX_BOTTLE Environment Variable ⚠️ BLOCKER

**Location**: Phase 4.2 - Fetch Historical Data

**Issue**: The guide shows Wine Python execution but OMITS the critical `CX_BOTTLE` environment variable that we discovered is mandatory for CrossOver wine wrapper.

**Current Documentation** (WRONG):
```bash
"$CX" --bottle "MetaTrader 5" "C:\\Program Files\\Python312\\python.exe" -c '
import MetaTrader5 as mt5
# ... Python code ...
'
```

**Reality** (CORRECT - from WINE_PYTHON_EXECUTION.md):
```bash
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\script.py"
```

**Impact**: New user will get silent failures or "MT5 initialize failed" errors.

**Fix Required**: Update Phase 4.2 with correct environment variables and explain why they're needed.

---

### Gap 2: Conflicting /inc Guidance ⚠️ CONFUSING

**Location**: Phase 3.2 - CLI Compile

**Issue**: Text says "do NOT add `/inc` unless using external includes" but the example immediately shows `/inc` in the command.

**Current Documentation**:
```bash
# Text: "Do NOT add /inc unless using external includes"
# But then shows:
"$CX" --bottle "MetaTrader 5" --cx-app "C:/Program Files/MetaTrader 5/MetaEditor64.exe" \
  /log /compile:"C:/Indicator.mq5" /inc:"C:/Program Files/MetaTrader 5/MQL5"
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                    This contradicts the advice above!
```

**Reality**: We should show TWO examples:
1. Standard indicators (NO /inc)
2. External includes (WITH /inc)

**Impact**: User confusion about when to use /inc, potential compilation failures.

**Fix Required**: Split into two clear examples with explanations.

---

### Gap 3: Phase 6.2 Export Method Doesn't Match Reality ⚠️ MISLEADING

**Location**: Phase 6.2 - Export MQL5 Indicator Values

**Issue**: Guide shows adding export code to `OnCalculate()` function, but our actual workflow uses `ExportAligned.mq5` script separately.

**Current Documentation**:
```mql5
// In indicator OnCalculate(), add export code
if(rates_total > 5000)
{
    // ... export code ...
}
```

**Reality**: We use `ExportAligned.mq5` script with indicator modules, NOT inline export code.

**Impact**: User tries to modify indicator with export code, breaks indicator logic, wastes time.

**Fix Required**: Update Phase 6.2 to reference ExportAligned.mq5 script or document both approaches.

---

### Gap 4: No Prerequisites Verification ⚠️ ASSUMPTION

**Location**: Prerequisites section

**Issue**: Guide ASSUMES Wine Python 3.12 + MetaTrader5 package are installed but provides no verification or installation steps.

**Current Documentation**:
```markdown
### Required Tools
- **Wine Python 3.12**: Installed in CrossOver bottle at `C:\Program Files\Python312\`
- **MetaTrader5 Package**: Installed in Wine Python (`pip install MetaTrader5`)
```

**Reality**: New users need:
1. How to verify Wine Python is installed
2. How to install if missing
3. How to verify MetaTrader5 package is installed
4. How to check package version (we're using 5.0.5328, not 2.x)

**Verification Commands** (MISSING from guide):
```bash
# Check Wine Python
ls "Program Files/Python312/python.exe"

# Check MetaTrader5 package
ls "Program Files/Python312/Lib/site-packages/MetaTrader5"

# Check version
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" -c "import MetaTrader5; print(MetaTrader5.__version__)"
```

**Impact**: New user fails at Phase 4 with cryptic import errors.

**Fix Required**: Add Prerequisites Verification section with step-by-step checks.

---

### Gap 5: Only ONE Indicator Validated ⚠️ UNPROVEN

**Issue**: We've only tested the workflow with Laguerre RSI. No evidence a NEW person can follow this guide for a DIFFERENT indicator.

**Validated**: Laguerre RSI (1.000000 correlation) ✅

**Not Validated**:
- A second indicator migration following the guide
- A new person (not us) following the guide
- The guide's time estimates (are they realistic?)
- The guide's troubleshooting steps (do they work?)

**Impact**: Hidden edge cases, missing steps, or outdated information may only surface when coworkers try to use this.

**Fix Required**: Complete end-to-end validation test (see Test Plan below).

---

### Gap 6: Missing MT5 Connection Verification ⚠️ SILENT FAILURE

**Location**: Phase 4.1 - Ensure MT5 is Running

**Issue**: Guide says "Start MT5 if not running" but doesn't verify:
1. MT5 actually started successfully
2. MT5 is logged in to an account
3. Symbol data is available

**Current Documentation**:
```bash
# Start MT5 if not running
CX="$HOME/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine"
"$CX" --bottle "MetaTrader 5" "C:/Program Files/MetaTrader 5/terminal64.exe" &
sleep 5
```

**Reality**: Wine MT5 startup can fail silently. User needs to verify:
```bash
# Check if MT5 process is running
ps aux | grep terminal64

# Test MT5 connection
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\test_mt5_connection.py"
```

**Impact**: User proceeds to Phase 4.2, gets "MT5 initialize failed", wastes 30 minutes debugging.

**Fix Required**: Add MT5 connection verification steps.

---

### Gap 7: Inline Python Script May Not Work ⚠️ UNTESTED

**Location**: Phase 4.2 - Fetch Historical Data

**Issue**: The guide shows a complex multi-line Python script passed via `-c` flag. This approach is UNTESTED in our workflow.

**Current Documentation**:
```bash
"$CX" --bottle "MetaTrader 5" "C:\\Program Files\\Python312\\python.exe" -c '
import MetaTrader5 as mt5
import pandas as pd
# ... 30 lines of Python code ...
'
```

**Reality**: Our actual workflow uses separate `.py` files (export_aligned.py), not inline scripts.

**Risk**: Shell quoting issues, line break handling, or path escaping could cause silent failures.

**Fix Required**: Use file-based approach or TEST the inline approach first.

---

## Validation Test Plan

### Phase 1: Prerequisites Verification Script

**Goal**: Create a script that verifies ALL prerequisites before starting workflow.

**Script**: `users/crossover/verify_prerequisites.py`

```python
#!/usr/bin/env python3
"""
Verify all prerequisites for MQL5→Python migration workflow
"""
from pathlib import Path
import subprocess
import sys

def check_wine_python():
    """Check Wine Python 3.12 is installed"""
    bottle = Path.home() / "Library/Application Support/CrossOver/Bottles/MetaTrader 5"
    python_exe = bottle / "drive_c/Program Files/Python312/python.exe"

    if not python_exe.exists():
        return False, f"Wine Python not found at {python_exe}"

    return True, f"✓ Wine Python found: {python_exe}"


def check_metatrader5_package():
    """Check MetaTrader5 package is installed"""
    bottle = Path.home() / "Library/Application Support/CrossOver/Bottles/MetaTrader 5"
    mt5_package = bottle / "drive_c/Program Files/Python312/Lib/site-packages/MetaTrader5"

    if not mt5_package.exists():
        return False, f"MetaTrader5 package not found at {mt5_package}"

    # Check version
    try:
        result = subprocess.run([
            "wine",
            "C:\\Program Files\\Python312\\python.exe",
            "-c", "import MetaTrader5; print(MetaTrader5.__version__)"
        ], capture_output=True, text=True, timeout=10,
        env={
            "CX_BOTTLE": "MetaTrader 5",
            "WINEPREFIX": str(bottle)
        })

        version = result.stdout.strip()
        return True, f"✓ MetaTrader5 {version} installed"
    except Exception as e:
        return False, f"MetaTrader5 package check failed: {e}"


def check_mt5_terminal():
    """Check MT5 terminal is installed"""
    bottle = Path.home() / "Library/Application Support/CrossOver/Bottles/MetaTrader 5"
    terminal_exe = bottle / "drive_c/Program Files/MetaTrader 5/terminal64.exe"

    if not terminal_exe.exists():
        return False, f"MT5 terminal not found at {terminal_exe}"

    return True, f"✓ MT5 terminal found: {terminal_exe}"


def check_validation_tools():
    """Check validation tools exist"""
    bottle = Path.home() / "Library/Application Support/CrossOver/Bottles/MetaTrader 5"
    validate_indicator = bottle / "drive_c/users/crossover/validate_indicator.py"

    if not validate_indicator.exists():
        return False, f"validate_indicator.py not found at {validate_indicator}"

    return True, f"✓ validate_indicator.py found"


def main():
    print("=== MQL5→Python Workflow Prerequisites Check ===\n")

    checks = [
        ("Wine Python 3.12", check_wine_python),
        ("MetaTrader5 Package", check_metatrader5_package),
        ("MT5 Terminal", check_mt5_terminal),
        ("Validation Tools", check_validation_tools),
    ]

    all_passed = True

    for name, check_func in checks:
        print(f"Checking {name}...")
        passed, message = check_func()
        print(f"  {message}")

        if not passed:
            all_passed = False
        print()

    if all_passed:
        print("✅ ALL PREREQUISITES MET - Ready to start workflow")
        return 0
    else:
        print("❌ PREREQUISITES MISSING - Fix issues above before starting")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Action**: Create this script and add to Phase 0 of the guide.

---

### Phase 2: End-to-End Test with Different Indicator

**Goal**: Validate the workflow works for a SECOND indicator (not Laguerre RSI).

**Test Indicator**: RSI (Relative Strength Index) - Simple, well-understood, fast to validate

**Steps**:
1. Follow MQL5_TO_PYTHON_MIGRATION_GUIDE.md from Phase 1-7
2. Document every step taken (actual commands, not just guide commands)
3. Note any deviations from guide
4. Time each phase
5. Document all errors encountered and solutions

**Success Criteria**:
- RSI Python implementation achieves ≥ 0.999 correlation
- All 7 phases complete without manual intervention
- Actual time ≤ 150% of documented estimate
- No undocumented steps required

**Deliverable**: RSI_VALIDATION_TEST_REPORT.md

---

### Phase 3: Fresh User Simulation

**Goal**: Test if someone NEW can follow the guide.

**Approach**: Pretend we've never done this before:
1. Start with ONLY the guide (no prior knowledge)
2. Follow guide EXACTLY as written
3. Don't fill in implicit steps
4. Document every point of confusion

**Questions to Answer**:
- Is every command copy-pastable?
- Are paths absolute or require substitution?
- Are prerequisites clearly verified?
- Are error messages explained?
- Are troubleshooting steps sufficient?

**Deliverable**: FRESH_USER_TEST_REPORT.md

---

### Phase 4: Fix All Gaps

**Goal**: Update MQL5_TO_PYTHON_MIGRATION_GUIDE.md to address all 7 gaps found.

**Changes Required**:
1. Add Phase 0: Prerequisites Verification
2. Fix Phase 3.2: Split /inc examples
3. Fix Phase 4.1: Add MT5 connection verification
4. Fix Phase 4.2: Add CX_BOTTLE environment variables
5. Fix Phase 6.2: Reference ExportAligned.mq5 approach
6. Add troubleshooting section for each phase
7. Add "Actually Validated" section listing tested indicators

**Deliverable**: MQL5_TO_PYTHON_MIGRATION_GUIDE.md v2.0.0

---

### Phase 5: Peer Review

**Goal**: Have teammate follow guide and provide feedback.

**Process**:
1. Share updated guide with one coworker
2. Ask them to migrate a simple indicator (RSI or MACD)
3. Observe without helping (unless blocked > 10 minutes)
4. Collect feedback on clarity, accuracy, completeness

**Success Criteria**:
- Coworker completes workflow in < 3 hours
- Coworker achieves ≥ 0.999 correlation
- No more than 2 clarifying questions needed

**Deliverable**: PEER_REVIEW_FEEDBACK.md

---

## Current Status

### Tools Verified ✅
- [x] Wine Python 3.12: EXISTS at `C:\Program Files\Python312\python.exe`
- [x] MetaTrader5 Package: v5.0.5328 INSTALLED
- [x] validate_indicator.py: EXISTS
- [x] export_aligned.py: EXISTS
- [x] MT5 Terminal: EXISTS

### Workflow Validated ✅
- [x] Laguerre RSI: 1.000000 correlation (5000-bar warmup)

### Workflow NOT Validated ❌
- [ ] Second indicator migration (RSI planned)
- [ ] Fresh user test (no prior knowledge)
- [ ] Prerequisites verification script
- [ ] CX_BOTTLE environment variable testing
- [ ] Inline Python script approach
- [ ] MT5 connection verification steps
- [ ] ExportAligned.mq5 workflow documentation

---

## Recommendations

### Before Sharing with Coworkers:

1. **IMMEDIATELY**: Create verify_prerequisites.py script (30 min)
2. **PRIORITY 1**: Test RSI indicator migration end-to-end (2 hours)
3. **PRIORITY 2**: Fix all 7 gaps in guide (1 hour)
4. **PRIORITY 3**: Fresh user simulation test (2 hours)
5. **PRIORITY 4**: Peer review with one coworker (3 hours)

**Total Time**: ~8.5 hours

### After Validation Complete:

1. Create WORKFLOW_VALIDATION_COMPLETE.md certification
2. Add "Validated with 2 indicators" badge to guide
3. Share with team via presentation + live demo
4. Collect feedback for 2 weeks before declaring "production-ready"

---

## Risk Assessment

**If we share now** (WITHOUT validation):
- ❌ Coworker hits Gap 1 (CX_BOTTLE) → fails at Phase 4 → wastes 1 hour
- ❌ Coworker follows Gap 3 (inline export) → breaks indicator → wastes 2 hours
- ❌ Team loses confidence in our documentation
- ❌ We look unprofessional

**If we validate first** (8.5 hours investment):
- ✅ Coworkers succeed on first try
- ✅ We catch hidden edge cases
- ✅ Documentation is truly "battle-tested"
- ✅ Team has confidence in the workflow

---

## Conclusion

**You were absolutely right to question this.** The documented workflow has **7 critical gaps** that would cause new users to fail. We need to complete the 5-phase validation test plan (8.5 hours) before sharing with coworkers.

**Next Action**: Choose one:
1. **Fix immediately**: Complete Phase 1-5 validation (8.5 hours, HIGH confidence after)
2. **Partial fix**: Complete Phase 1-2 only (3 hours, MEDIUM confidence)
3. **Share with caveat**: "This worked for Laguerre RSI but needs more testing"

**Recommendation**: Option 1 - Complete validation. 8.5 hours investment now saves 10+ hours of coworker frustration later.
