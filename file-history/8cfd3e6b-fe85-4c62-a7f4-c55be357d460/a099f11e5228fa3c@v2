# Wine Python MT5 Data Export - v3.0.0 True Headless

**Status**: ✅ PRODUCTION READY (2025-10-13 19:45)
**Approach**: Wine Python + MetaTrader5 API (bypasses all GUI requirements)
**Validation**: 0.999920 RSI correlation (USDJPY M1 cold start)

## Executive Summary

v3.0.0 achieves **true headless execution** using Wine Python with the MetaTrader5 package. This approach:

- ✅ Works for ANY symbol/timeframe without GUI initialization
- ✅ Uses programmatic API calls (`mt5.symbol_select()`, `mt5.copy_rates_from_pos()`)
- ✅ No startup.ini dependency - direct MT5 connection
- ✅ Cold start validated (USDJPY never opened in GUI)

## Critical Environment Requirements

### 1. CX_BOTTLE Environment Variable (MANDATORY)

**Discovery**: CrossOver's Perl wine wrapper requires `CX_BOTTLE` environment variable. `WINEPREFIX` alone is insufficient.

**Symptom without CX_BOTTLE**:

```
cxmessage: Unable to find the 'default' bottle:
bottle 'default' not found in '/Users/terryli/Library/Application Support/CrossOver/Bottles'
```

**Solution**:

```bash
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\export_aligned.py" \
  --symbol USDJPY --period M1 --bars 5000
```

**Key Insight**: CrossOver's wine is a Perl wrapper at `/Users/terryli/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine` that reads `CX_BOTTLE` to locate the bottle. Setting only `WINEPREFIX` causes it to fall back to looking for a "default" bottle.

### 2. Path Navigation Complexities

**Three Path Contexts**:

1. **macOS Native Paths**:

   ```bash
   /Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/export_aligned.py
   ```

2. **Wine Windows Paths** (from Wine Python's perspective):

   ```bash
   C:\users\crossover\export_aligned.py
   C:\Program Files\Python312\python.exe
   C:\Program Files\MetaTrader 5\terminal64.exe
   ```

3. **Bottle Export Paths** (output location):
   - **Wine writes to**: `C:\users\crossover\exports\Export_SYMBOL_PERIOD.csv`
   - **macOS reads from**: `~/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/exports/Export_SYMBOL_PERIOD.csv`

**Operations Requiring Each Context**:

| Operation                    | Path Type    | Example                                                       |
| ---------------------------- | ------------ | ------------------------------------------------------------- |
| Execute wine command         | macOS Native | `wine "C:\\Program Files\\Python312\\python.exe" ...`         |
| Python script argument       | Wine Windows | `"C:\\users\\crossover\\export_aligned.py"`                   |
| Edit script on macOS         | macOS Native | `vim ~/Library/.../drive_c/users/crossover/export_aligned.py` |
| Copy CSV to repo             | macOS Native | `cp ~/Library/.../exports/*.csv ./exports/`                   |
| Output directory (in Python) | Wine Windows | `OUTPUT_DIR = "C:\\Users\\crossover\\exports"`                |

**Critical Gotcha**: When passing paths to Wine executables, use Windows-style paths with backslashes. When accessing files from macOS, use macOS paths with forward slashes.

## RSI Calculation Formula Fix

**Problem**: Initial export showed correlation of 0.944 (FAILED validation threshold of 0.999).

**Root Cause**: Incorrect EWM smoothing parameter.

**Wrong Formula** (initial implementation):

```python
# ❌ WRONG - uses span=period
avg_gain = gain.ewm(span=period, adjust=False).mean()
avg_loss = loss.ewm(span=period, adjust=False).mean()

# This computes: alpha = 2/(period+1) = 2/15 = 0.1333 for period=14
```

**Correct Formula** (Wilder's smoothing):

```python
# ✅ CORRECT - uses alpha=1/period
avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

# This computes: alpha = 1/14 = 0.0714 for period=14
```

**Impact**: After fix, correlation improved to 0.999920 (PASSED validation).

**Location**: `/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/export_aligned.py:41-43 `

**Validation**: Mean absolute error dropped from 5.20 to 0.010, max error from 22.07 to 4.96.

## Column Name Normalization

**Problem**: Validator failed with "Missing required columns: ['open', 'high', 'low', 'close']" despite CSV containing data.

**Root Cause**: v3.0.0 Wine Python script outputs **capitalized** column names (`Time, Open, High, Low, Close, Volume, RSI`), but validator expected **lowercase** names.

**Solution**: Added column name normalization in validator:

```python
# In validate_export.py:38
df.columns = df.columns.str.lower()
```

**Impact**:

- v2.0.0 (MQL5): lowercase column names (time, open, high...)
- v3.0.0 (Python API): capitalized column names (Time, Open, High...)
- Validator now handles both formats transparently

**Location**: `/Users/terryli/eon/mql5-crossover/python/validate_export.py:38 `

**Additional Fix**: RSI column detection also updated from `col.startswith("RSI")` to `col.startswith("rsi")` at line 193.

## Complete Working Command

**Execution from macOS Terminal**:

```bash
# Full command with all required environment variables
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\export_aligned.py" \
  --symbol USDJPY \
  --period M1 \
  --bars 5000

# Output appears at (Wine path):
# C:\Users\crossover\exports\Export_USDJPY_PERIOD_M1.csv

# Copy to repo for validation (macOS path):
cp "$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/exports/Export_USDJPY_PERIOD_M1.csv" \
   ./exports/

# Validate
python python/validate_export.py ./exports/Export_USDJPY_PERIOD_M1.csv
```

**Expected Output**:

```
======================================================================
MT5 Data Export - USDJPY M1
======================================================================

[1/6] Initializing MT5 connection...
[OK] MT5 initialized

[2/6] Selecting symbol USDJPY...
[OK] USDJPY selected and added to Market Watch

[3/6] Parsing timeframe M1...
[OK] Timeframe: M1

[4/6] Fetching 5000 bars of USDJPY M1 data...
[OK] Fetched 5050 bars
  Date range: 2025-10-08 10:11:00 to 2025-10-13 22:45:00

[5/6] Calculating RSI (14-period)...
[OK] RSI calculated for 5000 bars
  RSI stats: min=5.87, max=91.66, mean=50.20

[6/6] Exporting to CSV...
[OK] Exported to: C:\Users\crossover\exports\Export_USDJPY_PERIOD_M1.csv
  Rows: 5000
  Columns: Time, Open, High, Low, Close, Volume, RSI

[OK] MT5 shutdown cleanly
```

## Wrapper Script Pattern

**For convenience, create a wrapper script**:

```bash
#!/bin/bash
# scripts/wine-mt5-export

BOTTLE_NAME="MetaTrader 5"
BOTTLE_PATH="$HOME/Library/Application Support/CrossOver/Bottles/$BOTTLE_NAME"
WINE_BIN="/Users/terryli/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine"

# Parse arguments
SYMBOL="${1:-EURUSD}"
PERIOD="${2:-M1}"
BARS="${3:-5000}"

echo "=== Wine MT5 Export (v3.0.0) ==="
echo "Symbol: $SYMBOL"
echo "Period: $PERIOD"
echo "Bars: $BARS"
echo ""

# Execute with proper environment
CX_BOTTLE="$BOTTLE_NAME" \
WINEPREFIX="$BOTTLE_PATH" \
"$WINE_BIN" \
  "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\export_aligned.py" \
  --symbol "$SYMBOL" \
  --period "$PERIOD" \
  --bars "$BARS"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=== Export Successful ==="

    # Copy to repo
    CSV_NAME="Export_${SYMBOL}_PERIOD_${PERIOD}.csv"
    BOTTLE_CSV="$BOTTLE_PATH/drive_c/users/crossover/exports/$CSV_NAME"
    REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)/exports"

    if [ -f "$BOTTLE_CSV" ]; then
        cp "$BOTTLE_CSV" "$REPO_DIR/"
        echo "Copied to: $REPO_DIR/$CSV_NAME"
        echo ""
        echo "Validate with:"
        echo "  python python/validate_export.py exports/$CSV_NAME"
    else
        echo "Warning: CSV not found at $BOTTLE_CSV"
    fi
else
    echo ""
    echo "=== Export Failed (Exit Code: $EXIT_CODE) ==="
fi

exit $EXIT_CODE
```

**Usage**:

```bash
chmod +x scripts/wine-mt5-export
./scripts/wine-mt5-export USDJPY M1 5000
```

## Diagnostic Commands

### Verify Bottle Configuration

```bash
# Check if MT5 is running
ps aux | grep -i "terminal64\|metatrader" | grep -v grep

# List CrossOver bottles
ls -la "$HOME/Library/Application Support/CrossOver/Bottles/"

# Check Wine Python installation
CX_BOTTLE="MetaTrader 5" wine "C:\\Program Files\\Python312\\python.exe" --version

# Test MetaTrader5 package import
CX_BOTTLE="MetaTrader 5" wine "C:\\Program Files\\Python312\\python.exe" -c "import MetaTrader5 as mt5; print(f'MetaTrader5 version: {mt5.__version__}')"
```

### Verify MT5 Connection

```bash
# Test MT5 initialization
CX_BOTTLE="MetaTrader 5" wine "C:\\Program Files\\Python312\\python.exe" -c "
import MetaTrader5 as mt5
if mt5.initialize():
    info = mt5.terminal_info()
    print(f'MT5 Build: {info.build}')
    print(f'Connected: {info.connected}')
    mt5.shutdown()
else:
    print('Failed to initialize MT5')
"
```

### Debug Path Issues

```bash
# Check bottle filesystem from Wine
CX_BOTTLE="MetaTrader 5" wine cmd /c "dir C:\\users\\crossover"

# Check exports directory
CX_BOTTLE="MetaTrader 5" wine cmd /c "dir C:\\users\\crossover\\exports"

# Verify Python script exists
ls -la "$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/export_aligned.py"
```

## Error Handling Patterns

### Error 1: "Unable to find the 'default' bottle"

**Symptom**: `cxmessage: Unable to find the 'default' bottle`

**Cause**: Missing `CX_BOTTLE` environment variable.

**Solution**: Add `CX_BOTTLE="MetaTrader 5"` before wine command.

### Error 2: "Cannot open file" or "FileNotFoundError"

**Symptom**: Wine Python can't find script file.

**Cause**: Incorrect path format (using macOS path instead of Wine path).

**Solution**: Use Wine Windows path: `"C:\\users\\crossover\\export_aligned.py"`

### Error 3: "MT5 initialization failed"

**Symptom**: `mt5.initialize()` returns False.

**Cause**: MT5 terminal not running or not logged in.

**Solution**:

```bash
# Launch MT5 terminal
open "/Users/terryli/Applications/CrossOver/MetaTrader 5/MetaTrader 5.app"
# Log in with credentials, then retry export
```

### Error 4: RSI correlation below 0.999

**Symptom**: Validator shows correlation like 0.944.

**Cause**: Incorrect RSI formula (using `span=period` instead of `alpha=1/period`).

**Solution**: Verify export_aligned.py uses correct formula at lines 41-43.

### Error 5: "Missing required columns"

**Symptom**: Validator fails despite CSV having data.

**Cause**: Column name case mismatch.

**Solution**: Validator should normalize column names with `df.columns = df.columns.str.lower()`.

## Performance Characteristics

**USDJPY M1 Test (5000 bars)**:

- Initialization: <1 second
- Symbol selection: <1 second
- Data fetch: 2-3 seconds
- RSI calculation: 1-2 seconds
- CSV write: <1 second
- **Total time**: ~6-8 seconds

**Scalability**:

- 5,000 bars: ~7 seconds ✓
- 10,000 bars: ~12 seconds (estimated)
- 50,000 bars: ~45 seconds (estimated)
- Timeout recommendation: 120 seconds (2 minutes) for 10,000 bars

## Comparison: v3.0.0 vs v2.0.0

| Aspect              | v2.0.0 (startup.ini)             | v3.0.0 (Python API) |
| ------------------- | -------------------------------- | ------------------- |
| **GUI Requirement** | ❌ Required per symbol/timeframe | ✅ None             |
| **Cold Start**      | ❌ Fails                         | ✅ Works            |
| **Complexity**      | Medium (config generation)       | Low (direct API)    |
| **Reliability**     | Conditional                      | High                |
| **Execution Time**  | 8-10 seconds                     | 6-8 seconds         |
| **Debugging**       | MT5 logs + config issues         | Python exceptions   |
| **Correlation**     | 0.999902 (EURUSD)                | 0.999920 (USDJPY)   |
| **Column Names**    | lowercase                        | Capitalized         |

**Recommendation**: Use v3.0.0 for all new development. v2.0.0 is legacy only.

## Production Checklist

Before deploying v3.0.0 in production:

- [x] ✅ Wine Python 3.12+ installed in bottle
- [x] ✅ MetaTrader5 package 5.0.5328+ installed
- [x] ✅ NumPy 1.26.4 (not 2.x) pinned
- [x] ✅ pandas 2.3.3+ installed
- [x] ✅ MT5 terminal running and logged in
- [x] ✅ CX_BOTTLE environment variable set
- [x] ✅ export_aligned.py uses correct RSI formula
- [x] ✅ Validator normalizes column names
- [x] ✅ Cold start test passed (USDJPY)
- [x] ✅ Validation correlation ≥ 0.999
- [ ] Create wrapper script for convenience
- [ ] Document symbol-specific quirks (if any)
- [ ] Set up monitoring/alerting for export failures

## References

- **Implementation Plan**: `../plans/HEADLESS_EXECUTION_PLAN.md ` - Complete v3.0.0 development history
- **Validation Report**: `../reports/VALIDATION_STATUS.md ` - Test results and SLO metrics
- **CrossOver Essentials**: `CROSSOVER_MQ5.md ` - MT5/Wine environment fundamentals
- **Python Script Location**: `~/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/export_aligned.py `
- **Validator Location**: `python/validate_export.py `

## Update History

- **2025-10-13 19:45**: Initial documentation after USDJPY M1 cold start validation
- **2025-10-13 19:42**: RSI formula fix applied (span → alpha)
- **2025-10-13 19:38**: Column name normalization fix
- **2025-10-13 19:30**: CX_BOTTLE environment variable discovery
- **2025-10-13 17:48**: v3.0.0 Phase 5 cold start validation complete

---

**Navigation Tip**: All paths use absolute format for Ghostty Cmd+click compatibility.
