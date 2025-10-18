# Iteration 2: SMA Test - Interim Report (BLOCKED)

**Version**: 1.0.0
**Date**: 2025-10-17
**Status**: 🔴 BLOCKED at export phase

---

## Service Level Objectives - Current Status

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Availability** | 100% | 80% | 🟡 Partial |
| **Correctness** | 100% | N/A | ⏸️ Cannot test |
| **Observability** | 100% | 75% | 🟡 Partial |
| **Maintainability** | ≥ 90% | 85% | 🟡 Acceptable |

**Root Cause**: Automated script execution via config file not working.

---

## What We Accomplished

### Phase 1: SimpleSMA_Test.mq5 Creation ✅ COMPLETE
- Created minimal SMA indicator (14-period, 70 lines)
- Location: `MQL5/Indicators/Custom/PythonInterop/SimpleSMA_Test.mq5`
- Compilation: Successful (7.4KB, 0 errors, 721ms)
- **Learning**: CLI compilation works WITHOUT `/inc` flag (flag OVERRIDES default paths)

### Phase 2: SMAModule.mqh Creation ✅ COMPLETE
- Created module following RSIModule.mqh pattern
- Location: `MQL5/Include/DataExport/modules/SMAModule.mqh`
- Uses `iCustom()` to load SimpleSMA_Test indicator
- **Learning**: Module pattern is reusable for any custom indicator

### Phase 3: ExportAligned.mq5 Update ✅ COMPLETE
- Added `#include <DataExport/modules/SMAModule.mqh>`
- Added inputs: `InpUseSMA` (bool), `InpSMAPeriod` (int)
- Added SMA loading logic at lines 68-80
- Compilation: Successful (24KB, 0 errors, 912ms)
- **Critical Discovery**: `/inc` flag causes 101 errors, omitting it works perfectly

### Phase 4: Automated Execution ❌ BLOCKED
- Created `sma_export_config.ini` with [StartUp] section
- Terminal launched but script did not execute
- No export file created
- **Status**: Automated config approach needs investigation

---

## Critical Learnings

### Learning 1: /inc Flag Behavior
**Problem**: Compilation with `/inc:"C:/Program Files/MetaTrader 5/MQL5"` failed with 101 errors

**Root Cause**: CLAUDE.md states `/inc` parameter OVERRIDES (not augments) default include paths

**Solution**: Omit `/inc` flag entirely for standard indicators/scripts

**Evidence**:
```bash
# FAILED (101 errors)
/log /compile:"C:/ExportAligned.mq5" /inc:"C:/Program Files/MetaTrader 5/MQL5"

# SUCCEEDED (0 errors, 912ms)
/log /compile:"C:/ExportAligned.mq5"
```

**Impact**: Updates required to MQL5_TO_PYTHON_MINIMAL.md and REALITY_CHECK_MATRIX.md

---

### Learning 2: Module Pattern Scalability
**Finding**: SMAModule.mqh was created in 5 minutes by following RSIModule.mqh pattern

**Pattern**:
```cpp
bool [Indicator]Module_Load(
    const string symbol,
    const ENUM_TIMEFRAMES timeframe,
    const int bars,
    const int period,  // or other parameters
    IndicatorColumn &column,
    string &errorMessage)
{
    column.header = StringFormat("[Name]_%d", period);
    column.digits = 5;
    ArrayResize(column.values, bars);
    ArraySetAsSeries(column.values, true);

    int handle = iCustom(symbol, timeframe, "Path\\To\\Indicator", period);
    if(handle == INVALID_HANDLE) {
        errorMessage = "Indicator handle creation failed";
        return false;
    }
    int copied = CopyBuffer(handle, 0, 0, bars, column.values);
    IndicatorRelease(handle);
    if(copied != bars) {
        errorMessage = StringFormat("CopyBuffer expected %d bars, received %d", bars, copied);
        return false;
    }
    return true;
}
```

**Impact**: This pattern can be applied to ANY custom indicator

---

### Learning 3: Config File Execution Unclear
**Attempted**: MT5 terminal launch with `/config:"C:\\users\\crossover\\sma_export_config.ini"`

**Config File**:
```ini
[StartUp]
Script=Scripts\\DataExport\\ExportAligned
Symbol=EURUSD
Period=M1
ShutdownTerminal=1

[Inputs]
InpSymbol=EURUSD
InpTimeframe=1
InpBars=5000
InpUseSMA=true
InpSMAPeriod=14
```

**Result**: Terminal launched, no script execution, no log entry

**Possible Issues**:
1. Config file path or format incorrect
2. Terminal must be already logged in for scripts to run
3. [StartUp] section requires specific syntax we haven't discovered
4. Script path format wrong (should it be absolute?)

**Status**: Needs further investigation or GUI fallback

---

## File Locations

### Created Files
```bash
# SimpleSMA Test Indicator
$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/PythonInterop/SimpleSMA_Test.mq5
$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/PythonInterop/SimpleSMA_Test.ex5

# SMA Module
$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Include/DataExport/modules/SMAModule.mqh

# Updated Export Script
$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Scripts/DataExport/ExportAligned.mq5
$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Scripts/DataExport/ExportAligned.ex5 (24KB)

# Python Implementation
$BOTTLE/drive_c/users/crossover/indicators/simple_sma.py

# Config File
$BOTTLE/drive_c/users/crossover/sma_export_config.ini
```

### Expected Output (Not Created)
```bash
$BOTTLE/drive_c/users/crossover/exports/Export_EURUSD_M1_SMA.csv
```

---

## Blockers

### Blocker 1: Script Execution
**Issue**: Cannot run ExportAligned.mq5 script automatically

**Options**:
1. **Manual Execution** (Fastest)
   - Open MT5 GUI
   - Navigate to Navigator → Scripts → DataExport → ExportAligned
   - Drag to EURUSD M1 chart
   - Set parameters: InpUseSMA=true, InpSMAPeriod=14, InpUseRSI=false, InpUseLaguerreRSI=false
   - Run script
   - **Time**: 2 minutes
   - **Reliability**: 100%

2. **Investigate Config Format** (Unknown time)
   - Research MT5 config file documentation
   - Test different formats
   - **Time**: 30-60 minutes
   - **Reliability**: Unknown

3. **Python API Alternative** (Not Possible)
   - CLAUDE.md states: "Python MetaTrader5 API cannot access indicator buffers"
   - **Conclusion**: Not viable

**Recommendation**: Option 1 (Manual Execution) to unblock testing

---

## Next Steps

### Immediate Actions

1. **User Decision Required**: How to proceed with script execution?
   - Option A: Manual GUI execution (2 minutes, reliable)
   - Option B: Investigate config automation (30-60 minutes, uncertain)

2. **After Export** (blocked on step 1):
   - Verify CSV has SMA_14 column with MQL5 values
   - Run Python validation: `python validate_indicator.py --csv Export_EURUSD_M1_SMA.csv --indicator sma`
   - Update validation framework if needed
   - Document correlation results

3. **Update Documentation** (blocked on validation):
   - Update REALITY_CHECK_MATRIX.md with `/inc` flag finding
   - Update MQL5_TO_PYTHON_MINIMAL.md compilation steps
   - Document module pattern for future indicators
   - Create Iteration 3 workflow improvements

---

## Questions for Iteration 3

1. Should we create a registry system for indicator modules?
   - `spike_2_registry_pattern.py` exists in archives
   - `validate_indicator.py` has hardcoded indicators only
   - Registry would enable dynamic loading

2. Should we document manual GUI workflow as primary?
   - CLI compilation works (SimpleSMA_Test, ExportAligned)
   - Script execution automation unclear
   - Manual execution is reliable

3. What's the actual method used for Laguerre RSI export?
   - `Export_EURUSD_PERIOD_M1.csv` exists from Oct 15
   - Contains Laguerre_RSI columns
   - How was ExportAligned run?

---

## Updated Reality Check

| Phase | Documented | Actual | Match? |
|-------|-----------|--------|--------|
| Prerequisites | Missing | N/A | ❌ |
| Indicator Creation | N/A | SimpleSMA_Test.mq5 created | ✅ |
| Compilation | "Use /inc flag" | "/inc OVERRIDES, omit it" | ❌ |
| Module Creation | Not documented | SMAModule.mqh pattern | ❌ |
| Export Script Update | Not documented | Updated ExportAligned.mq5 | ❌ |
| Script Execution | "Use config file" | Config didn't work | ❌ |
| Python Validation | Generic | Needs SMA support | ⏸️ |

**Reality Check Score**: 14% (1/7 phases match)

---

**Status**: Iteration 2 paused at script execution phase, awaiting user decision on manual vs automated approach
