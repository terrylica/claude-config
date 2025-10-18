# MQL5 to Python Indicator Migration - Minimal Workflow

**Version**: 1.0.0
**Status**: ⚠️ Tested with 1 indicator (Laguerre RSI)
**Date**: 2025-10-17

---

## Service Level Objectives

| Metric | Target | Method |
|--------|--------|--------|
| **Availability** | 100% | All commands executable |
| **Correctness** | ≥ 0.999 correlation | scipy.stats.pearsonr validation |
| **Observability** | 100% | Verification step per phase |
| **Maintainability** | ≥ 90% | Commands use absolute paths |

---

## Core Loop

```
1. Get MQL5 indicator values → CSV
2. Implement same logic in Python
3. Compare outputs (correlation ≥ 0.999)
```

**Everything below supports this loop.**

---

## Prerequisites Verification

```bash
BOTTLE="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5"

# 1. Wine Python 3.12
test -f "$BOTTLE/drive_c/Program Files/Python312/python.exe" && echo "✓ Wine Python" || echo "✗ Missing"

# 2. MetaTrader5 package v5.0.5328
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$BOTTLE" \
wine "C:\\Program Files\\Python312\\python.exe" -c "import MetaTrader5; print('✓ MT5 package:', MetaTrader5.__version__)" 2>/dev/null || echo "✗ Missing"

# 3. MT5 terminal
test -f "$BOTTLE/drive_c/Program Files/MetaTrader 5/terminal64.exe" && echo "✓ MT5 terminal" || echo "✗ Missing"
```

**If any check fails**: Stop. Fix prerequisites first.

---

## Phase 1: Find Indicator

```bash
BOTTLE="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5"

# Find by name
find "$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Indicators" -name "*YourIndicator*"

# List all custom
find "$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom" -name "*.mq5"
```

**Output**: Absolute path to indicator .mq5 file

---

## Phase 2: Analyze Algorithm

Read the MQL5 source:

```python
from pathlib import Path
import chardet

mq5_file = Path("/path/from/phase1/indicator.mq5")
with mq5_file.open('rb') as f:
    encoding = chardet.detect(f.read(10_000))['encoding']
content = mq5_file.read_text(encoding=encoding)
print(content)
```

**Document**:
1. Indicator buffers (what values it calculates)
2. Input parameters
3. Dependencies (`#include` directives)
4. Algorithm logic

**Create**: `docs/guides/YOUR_INDICATOR_ANALYSIS.md`

---

## Phase 3: Expose Hidden Buffers

Copy indicator to PythonInterop folder:

```bash
BOTTLE="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5"
SRC="/path/from/phase1/indicator.mq5"
DST="$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/PythonInterop/YourIndicator_Export.mq5"

cp "$SRC" "$DST"
```

Modify `YourIndicator_Export.mq5`:

```mql5
// Original
#property indicator_buffers 2
#property indicator_plots   2

// Modified - expose ALL buffers
#property indicator_buffers 4  // Increase to total buffer count
#property indicator_plots   2  // Plots stay same

// Declare hidden buffers as calculations
double hiddenBuffer1[];
double hiddenBuffer2[];

// In SetupBuffers():
SetIndexBuffer(2, hiddenBuffer1, INDICATOR_CALCULATIONS);
SetIndexBuffer(3, hiddenBuffer2, INDICATOR_CALCULATIONS);
```

**Intent**: Make internal buffers accessible via `CopyBuffer()` for validation.

---

## Phase 4: Compile

```bash
BOTTLE="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5"
CX="$HOME/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine"
FILE="$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/PythonInterop/YourIndicator_Export.mq5"

# Convert to Windows path
WIN_PATH="C:/Program Files/MetaTrader 5/MQL5/Indicators/Custom/PythonInterop/YourIndicator_Export.mq5"

# Compile (NO /inc flag for standard indicators)
"$CX" --bottle "MetaTrader 5" \
  --cx-app "C:/Program Files/MetaTrader 5/MetaEditor64.exe" \
  /log /compile:"$WIN_PATH"
```

**Verify**:

```python
from pathlib import Path
log = Path.home() / "Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/logs/metaeditor.log"
lines = log.read_text(encoding='utf-16-le').strip().split('\n')
print(lines[-1])  # Should show "0 errors"
```

**Check .ex5 exists**:

```bash
ls -lh "$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/PythonInterop/YourIndicator_Export.ex5"
```

---

## Phase 5: Fetch Historical Data

**Requirement**: 5000+ bars for stable warmup

```bash
BOTTLE="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5"

# Ensure MT5 is running and logged in (manual step)
# Open MT5 GUI, login to account

# Fetch 5000 bars
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$BOTTLE" \
wine "C:\\Program Files\\Python312\\python.exe" -c '
import MetaTrader5 as mt5
import pandas as pd

if not mt5.initialize():
    raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

symbol = "EURUSD"
if not mt5.symbol_select(symbol, True):
    raise RuntimeError(f"Failed to select {symbol}")

rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 5000)
if rates is None or len(rates) == 0:
    raise RuntimeError(f"Failed to fetch rates: {mt5.last_error()}")

df = pd.DataFrame(rates)
df["time"] = pd.to_datetime(df["time"], unit="s")
df[["time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]].to_csv("C:\\users\\crossover\\EURUSD_M1_5000bars.csv", index=False)
print(f"Fetched {len(rates)} bars")
mt5.shutdown()
'
```

**Verify**:

```bash
ls -lh "$BOTTLE/drive_c/users/crossover/EURUSD_M1_5000bars.csv"
# Should be ~300KB, 5000 rows
```

---

## Phase 6: Export MQL5 Indicator Values

**Method 1**: ExportAligned.mq5 script (if available)
- Attach indicator to chart
- Run ExportAligned.mq5 script
- Output: `/MQL5/Files/Export_EURUSD_PERIOD_M1.csv`

**Method 2**: Manual export from chart
- Open MT5, attach indicator to EURUSD M1 chart
- Right-click chart → Data Window
- Copy last 100 bars to CSV manually

**Verify**:

```bash
ls -lh "$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Files/Export_EURUSD_PERIOD_M1.csv"
```

---

## Phase 7: Implement Python Indicator

Create `users/crossover/indicators/your_indicator.py`:

```python
"""Your Indicator - Python implementation"""
import pandas as pd
import numpy as np


def calculate_your_indicator(
    df: pd.DataFrame,
    param1: int = 14,
    param2: str = 'ema'
) -> pd.DataFrame:
    """
    Calculate indicator matching MQL5 implementation.

    Args:
        df: DataFrame with columns: time, open, high, low, close
        param1: Parameter 1 (match MQL5 default)
        param2: Parameter 2 (match MQL5 default)

    Returns:
        DataFrame with indicator buffers as columns
    """
    # Implement algorithm from Phase 2 analysis
    # Return DataFrame with all buffers
    result = pd.DataFrame(index=df.index)
    result['buffer1'] = ...  # Your calculation
    result['buffer2'] = ...  # Your calculation
    return result
```

**Critical**: Match MQL5 behavior exactly:
- Expanding windows: `sum(all_bars) / period` not `sum(available_bars) / available_bars`
- Initialization: First bar values often need special handling
- Loop direction: MQL5 series are reversed (newest=0)

---

## Phase 8: Validate

```python
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from indicators.your_indicator import calculate_your_indicator

# 1. Load 5000-bar dataset
df_5000 = pd.read_csv("users/crossover/EURUSD_M1_5000bars.csv")
df_5000["time"] = pd.to_datetime(df_5000["time"])

# 2. Calculate on ALL 5000 bars (provides warmup)
result_5000 = calculate_your_indicator(df_5000, param1=14, param2='ema')

# 3. Extract last 100 bars
result_last100 = result_5000.iloc[-100:].reset_index(drop=True)

# 4. Load MQL5 export (last 100 bars)
df_mql5 = pd.read_csv("MT5/MQL5/Files/Export_EURUSD_PERIOD_M1.csv")

# 5. Compare each buffer
for buffer_name in ['buffer1', 'buffer2']:
    py_values = result_last100[buffer_name].values
    mql_values = df_mql5[f'YourIndicator_{buffer_name}'].values

    # Remove NaN
    mask = ~(np.isnan(py_values) | np.isnan(mql_values))
    py_clean = py_values[mask]
    mql_clean = mql_values[mask]

    # Calculate correlation
    if len(py_clean) < 2:
        raise ValueError(f"{buffer_name}: Insufficient data after NaN removal")

    corr, pval = pearsonr(py_clean, mql_clean)
    mae = np.mean(np.abs(py_clean - mql_clean))
    rmse = np.sqrt(np.mean((py_clean - mql_clean)**2))

    print(f"{buffer_name}:")
    print(f"  Correlation: {corr:.6f} (p={pval:.6f})")
    print(f"  MAE: {mae:.6f}, RMSE: {rmse:.6f}")

    # Check threshold
    if corr < 0.999:
        raise ValueError(f"{buffer_name}: Correlation {corr:.6f} < 0.999 threshold")

print("\n✅ VALIDATION PASSED - All buffers ≥ 0.999 correlation")
```

**Success**: All buffers ≥ 0.999 correlation

**Failure**: See debugging section below

---

## Debugging Common Issues

### Issue 1: Correlation ~0.95

**Cause**: Historical warmup mismatch

**Fix**: Ensure Python calculates on FULL 5000 bars, compare LAST 100 only

### Issue 2: NaN Values

**Cause**: Pandas `rolling().mean()` returns NaN until full window available

**Fix**: Use manual loops with expanding windows:

```python
for i in range(len(data)):
    if i < period:
        result[i] = data[:i+1].sum() / period  # Expanding
    else:
        result[i] = data[i-period+1:i+1].mean()  # Sliding
```

### Issue 3: Small Differences (correlation ~0.9999)

**Cause**: Floating-point precision differences

**Fix**: Acceptable if MAE < 0.001

### Issue 4: Large Differences

**Cause**: Algorithm mismatch (EMA vs SMA, SMMA differences, etc.)

**Fix**: Re-read MQL5 code, check MA method implementation

---

## Time Estimates

| Phase | Time |
|-------|------|
| 0. Prerequisites | 5 min |
| 1. Find Indicator | 2 min |
| 2. Analyze Algorithm | 15-60 min |
| 3. Expose Buffers | 10 min |
| 4. Compile | 5 min |
| 5. Fetch Data | 5 min |
| 6. Export MQL5 Values | 10 min |
| 7. Implement Python | 30-120 min |
| 8. Validate | 10 min |
| **Total** | **1.5-3.5 hours** |

**Note**: Times based on Laguerre RSI (complex indicator). Simple indicators (SMA, EMA) should be faster.

---

## What's Different From Other Guides

This workflow documents:
- What we ACTUALLY did for Laguerre RSI validation
- One method per phase (no alternatives)
- Copy-pastable commands with absolute paths
- CX_BOTTLE environment variable (required, often missing)
- Buffer exposure method (not inline export)
- 5000-bar warmup requirement (critical for correlation)

**Tested with**: 1 indicator (Laguerre RSI, 1.000000 correlation)

**Not yet validated**: Simple indicators (SMA, RSI, EMA)

---

## Version History

- **v1.0.0** (2025-10-17): Initial extraction from Laguerre RSI experience

---

**Next**: Test this workflow with SMA to validate it scales to simple indicators
