# Reality Check Matrix - Laguerre RSI Experience

**Version**: 1.0.0
**Date**: 2025-10-17
**Purpose**: Compare documented workflow vs actual Laguerre RSI implementation

---

## Service Level Objectives

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 100% | All documented steps executable |
| **Correctness** | 100% | Steps produce expected outcomes |
| **Observability** | 100% | Verification step per phase |
| **Maintainability** | ≥ 90% | Steps remain valid across updates |

**Current SLO Status**: 🔴 42% (5/12 phases match reality)

---

## Matrix: Guide vs Reality

| Phase | Current Guide Says | What We Actually Did | Match? | Gap Type |
|-------|-------------------|---------------------|--------|----------|
| **Prerequisites** | Assumes Wine Python + MT5 package installed | No verification step documented | ❌ | Missing verification |
| **Find Indicator** | `find ... -name "*.mq5"` | Used this exact command | ✅ | - |
| **Analyze Algorithm** | "Read and understand", document in guide | Created LAGUERRE_RSI_ANALYSIS.md (37KB doc) | ✅ | - |
| **Modify MQL5** | "Add inline export code to OnCalculate()" | Modified existing indicator, added buffer exposure (buffers 3-4) | ❌ | Wrong approach |
| **CLI Compile** | Shows command WITH `/inc` flag | Used CLI WITHOUT `/inc` flag | ❌ | Wrong flag usage |
| **Copy to Simple Path** | Copy to C:/Indicator.mq5 | Did NOT copy - compiled directly | ⚠️ | Workflow deviation |
| **Verify Compilation** | Check log + .ex5 existence | Did this exactly | ✅ | - |
| **Start MT5** | `wine ... terminal64.exe &` + `sleep 5` | MT5 was already running, no verification | ⚠️ | Incomplete |
| **Fetch Historical Data** | Inline Wine Python `-c` script (30 lines) | Used inline script (exact from validation report) | ✅ | - |
| **Python Implementation** | Generic template shown | Created 11 functions, 400+ lines in laguerre_rsi.py | ⚠️ | Complexity gap |
| **Export MQL5 Values** | "Add export code to OnCalculate()" | Used ExportAligned.mq5 script separately | ❌ | Wrong approach |
| **Validate** | Use validate_indicator.py | Used inline Python script with scipy | ⚠️ | Tool difference |

**Legend**:
- ✅ Match: Guide accurately represents reality
- ❌ Gap: Guide shows wrong approach
- ⚠️ Deviation: Reality differs but both work

---

## Critical Gaps Identified

### Gap 1: MQL5 Modification Approach

**Guide Says**:
```mql5
// In indicator OnCalculate(), add export code
if(rates_total > 5000)
{
    string filename = "Export_" + Symbol() + "_" + EnumToString(Period()) + ".csv";
    int handle = FileOpen(filename, FILE_WRITE|FILE_CSV);
    // ... export code ...
}
```

**Reality**:
- Modified `/MQL5/Indicators/Custom/PythonInterop/ATR_Adaptive_Laguerre_RSI.mq5`
- Added buffer exposure: `#property indicator_buffers 5` (was 3)
- Added buffers 3-4 as INDICATOR_CALCULATIONS type
- Did NOT add inline export code
- Used separate ExportAligned.mq5 script for export

**Root Cause**: Guide documents theoretical approach, not actual workflow

**Impact**: User wastes time adding export code to indicator, may break indicator logic

---

### Gap 2: CLI Compilation Flags

**Guide Shows**:
```bash
"$CX" --bottle "MetaTrader 5" --cx-app "C:/Program Files/MetaTrader 5/MetaEditor64.exe" \
  /log /compile:"C:/Indicator.mq5" /inc:"C:/Program Files/MetaTrader 5/MQL5"
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**Reality**:
- Used CLI compilation WITHOUT `/inc` flag
- File: `docs/guides/MQL5_CLI_COMPILATION_SUCCESS.md` states "/inc OVERRIDES default paths"
- For standard indicators using `#include <MovingAverages.mqh>`, omit `/inc`

**Actual Command**:
```bash
"$CX" --bottle "MetaTrader 5" --cx-app "C:/Program Files/MetaTrader 5/MetaEditor64.exe" \
  /log /compile:"C:/Indicator.mq5"
```

**Root Cause**: Guide shows example with `/inc` but text says "don't use it"

**Impact**: Compilation failures due to include path override

---

### Gap 3: Data Export Method

**Guide Says**: Add inline export code to indicator OnCalculate()

**Reality**:
- Used ExportAligned.mq5 script from `/MQL5/Scripts/DataExport/`
- Script runs separately from indicator
- Reads indicator buffers via `CopyBuffer()`
- Exports to CSV in `/MQL5/Files/` directory

**Tool Used**: `export_aligned.py` + `ExportAligned.mq5` (modular approach)

**Root Cause**: Guide documents one-off export approach, not repeatable system

**Impact**: User modifies indicator unnecessarily, breaks modularity

---

### Gap 4: Prerequisites Verification

**Guide Says**: "Required Tools" section lists tools, no verification

**Reality**: No documented way to check:
- Is Wine Python 3.12 installed?
- Is MetaTrader5 package version 5.0.5328 (not 2.x)?
- Is MT5 terminal installed and accessible?
- Are validation tools present?

**Missing Commands**:
```bash
# Check Wine Python
ls "Program Files/Python312/python.exe"

# Check MetaTrader5 package version
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" -c \
  "import MetaTrader5; print(MetaTrader5.__version__)"

# Check MT5 connection
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\test_mt5_connection.py"
```

**Root Cause**: Guide assumes prerequisites, doesn't verify

**Impact**: User encounters "MT5 initialize failed" in Phase 4, wastes 30+ minutes debugging

---

### Gap 5: Simple Path Copy Step

**Guide Says**: Copy indicator to `C:/Indicator.mq5` (simple path, no spaces)

**Reality**: Compiled directly from original location with spaces in path

**Actual File Path**:
```
/Program Files/MetaTrader 5/MQL5/Indicators/Custom/PythonInterop/ATR_Adaptive_Laguerre_RSI.mq5
                                                                  ^^^^^ Has spaces ^^^^^
```

**Question**: Is the "simple path" step necessary or can CrossOver handle spaces?

**Test Required**: Compile indicator with spaces in path vs without

**Impact**: Unknown - may be unnecessary step or critical workaround

---

## Workflow Complexity Reality

### What Guide Suggests

"Time Estimate: 2-4 hours for first indicator"

### What Actually Happened (Laguerre RSI)

**Indicator Complexity**:
- 11 Python functions
- 400+ lines of code
- 4 buffers to validate
- ATR calculation requiring expanding window replication
- Laguerre filter with 4-stage recursive calculation
- Adaptive gamma coefficient calculation

**Actual Time Investment** (estimated from git commits):
- Oct 13-17: 4 days of work
- Multiple bug fixes: shared state, array indexing, price smoothing
- 3+ hours of validation debugging (NaN traps, warmup issues)
- Multiple documents created (ANALYSIS, BUG REPORTS, VALIDATION)

**Reality**: Laguerre RSI is a COMPLEX indicator, not representative of typical workflow

---

## Missing: Environment Variable

**Guide Missing**: CX_BOTTLE environment variable requirement

**Reality** (from WINE_PYTHON_EXECUTION.md):
```bash
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" script.py
```

**Without CX_BOTTLE**: Wine commands may fail silently

**Impact**: Phase 4 (data fetch) fails with cryptic errors

---

## Tools Actually Used

### MQL5 Side

1. **MetaEditor CLI**: CrossOver --cx-app method
2. **ExportAligned.mq5**: Modular export script
3. **Buffer exposure**: Modified indicator to expose internal buffers

### Python Side

1. **Wine Python 3.12**: MT5 API access
2. **MetaTrader5 package**: v5.0.5328
3. **indicators/laguerre_rsi.py**: Custom implementation
4. **Inline validation script**: scipy.stats.pearsonr for correlation

### Files Created

- `LAGUERRE_RSI_ANALYSIS.md` (37KB algorithm breakdown)
- `LAGUERRE_RSI_TEMPORAL_AUDIT.md` (temporal violation check)
- `LAGUERRE_RSI_SHARED_STATE_BUG.md` (root cause analysis)
- `LAGUERRE_RSI_ARRAY_INDEXING_BUG.md` (series direction fix)
- `LAGUERRE_RSI_BUG_FIX_SUMMARY.md` (price smoothing fix)
- `LAGUERRE_RSI_VALIDATION_SUCCESS.md` (this report)
- `PYTHON_INDICATOR_VALIDATION_FAILURES.md` (debugging journey)
- `indicators/laguerre_rsi.py` (400+ line implementation)

---

## Correct Minimal Workflow (What We Actually Did)

### Phase 1: Prerequisites Verification
```bash
# Check Wine Python exists
ls "$BOTTLE/drive_c/Program Files/Python312/python.exe"

# Check MetaTrader5 package
ls "$BOTTLE/drive_c/Program Files/Python312/Lib/site-packages/MetaTrader5"

# Check MT5 connection
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$BOTTLE" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\test_mt5_connection.py"
```

### Phase 2: Find Indicator
```bash
find "$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Indicators" \
  -name "*Laguerre*"
```

### Phase 3: Analyze Algorithm
- Read MQL5 source with chardet encoding detection
- Document algorithm in ANALYSIS.md
- Identify buffers, parameters, dependencies

### Phase 4: Modify MQL5 for Export
- Copy to PythonInterop/ folder
- Add buffer exposure (increase buffer count)
- Set hidden buffers as INDICATOR_CALCULATIONS type
- Do NOT add inline export code

### Phase 5: Compile
```bash
CX="$HOME/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine"

# Compile WITHOUT /inc flag for standard indicators
"$CX" --bottle "MetaTrader 5" \
  --cx-app "C:/Program Files/MetaTrader 5/MetaEditor64.exe" \
  /log /compile:"C:/Full/Path/To/Indicator.mq5"
```

### Phase 6: Verify Compilation
```python
from pathlib import Path
log = Path.home() / "Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/logs/metaeditor.log"
lines = log.read_text(encoding='utf-16-le').strip().split('\n')
print(lines[-1])  # Should show "0 errors, X warnings, Y msec elapsed"
```

### Phase 7: Fetch Historical Data (5000+ bars)
```bash
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$BOTTLE" \
wine "C:\\Program Files\\Python312\\python.exe" -c '
import MetaTrader5 as mt5
import pandas as pd

mt5.initialize()
mt5.symbol_select("EURUSD", True)
rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M1, 0, 5000)
df = pd.DataFrame(rates)
df["time"] = pd.to_datetime(df["time"], unit="s")
df.to_csv("C:\\users\\crossover\\EURUSD_M1_5000bars.csv", index=False)
mt5.shutdown()
'
```

### Phase 8: Attach Indicator to MT5 Chart
- Open MT5 GUI
- Open EURUSD M1 chart
- Drag indicator from Navigator to chart
- Wait for warmup (10 seconds)

### Phase 9: Export Indicator Values
```bash
# Use ExportAligned.mq5 script
# Attach to chart and run, or use mt5.ini config method
# Output: /MQL5/Files/Export_EURUSD_PERIOD_M1.csv
```

### Phase 10: Implement Python Indicator
- Create indicators/your_indicator.py
- Implement all functions matching MQL5 algorithm
- Handle expanding windows for ATR calculations
- Match MQL5 initialization behavior exactly

### Phase 11: Validate
```python
# Load 5000-bar dataset
df_5000 = pd.read_csv("EURUSD_M1_5000bars.csv")

# Calculate on ALL 5000 bars
result_5000 = calculate_indicator(df_5000, params...)

# Extract last 100 bars
result_last100 = result_5000.iloc[-100:].copy()

# Load MQL5 export (last 100 bars)
df_mql5 = pd.read_csv("Export_EURUSD_PERIOD_M1.csv")

# Calculate correlation
from scipy.stats import pearsonr
corr, _ = pearsonr(py_values, mql5_values)
print(f"Correlation: {corr:.6f}")
```

---

## Recommendations

### Immediate Actions

1. **Create Prerequisites Verification Script**
   - Check Wine Python installation
   - Check MetaTrader5 package version
   - Test MT5 connection
   - **Time**: 30 minutes

2. **Document Modular Export Workflow**
   - ExportAligned.mq5 approach
   - Buffer exposure method
   - Remove inline export code examples
   - **Time**: 30 minutes

3. **Fix CLI Compilation Examples**
   - Remove `/inc` from standard indicator example
   - Add note: "Only use /inc for external includes"
   - **Time**: 10 minutes

4. **Add CX_BOTTLE Environment Variable**
   - Document in all Wine Python examples
   - Explain why it's required
   - **Time**: 15 minutes

### Test with Simple Indicator

**Before updating guide**: Test workflow with SMA (Simple Moving Average)

**Why SMA**:
- 5-10 lines of code
- No dependencies
- No complex state management
- Can complete in 30-45 minutes

**Purpose**: Validate if workflow scales to SIMPLE indicators (Laguerre RSI was too complex for first test)

---

## Version History

- **v1.0.0** (2025-10-17): Initial reality check based on Laguerre RSI validation success report

---

## Next Steps

1. ✅ Complete reality check (this document)
2. ⏳ Extract minimal workflow based on actual experience
3. ⏳ Test minimal workflow with SMA
4. ⏳ Update workflow based on SMA learnings
5. ⏳ Test with RSI to validate consistency
6. ⏳ Check convergence (if SMA and RSI match, workflow is stable)

---

**Status**: Iteration 0 complete - Reality documented, ready for Iteration 1 (minimal workflow extraction)
