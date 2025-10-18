# Python Indicator Validation Methodology

**Version**: 1.0.0
**Status**: Production
**Validated**: Laguerre RSI (1.000000 correlation)
**Last Updated**: 2025-10-17

---

## Overview

Single source of truth for validating Python indicator implementations against MQL5 reference implementations. Consolidates 3+ hours of debugging and 185+ hours of cumulative development.

---

## Critical Requirements

### 5000-Bar Historical Warmup (NON-OPTIONAL)

**Why Required**:
- MQL5 indicators on live charts have full historical context (4900+ bars)
- Python calculations from CSV exports have ZERO historical context
- Indicators with memory (ATR, EMA, adaptive periods) produce different values with different starting conditions
- Different starting conditions = systematic bias = ~0.95 correlation (FAILURE)

**Mental Model**:
```
MQL5 Chart Timeline:
[......4900 bars of history.......][100 bars exported]
                                    ^
                                    ATR has 4900 bars context

Python Calculation (WRONG):
[100 bars from CSV]
^
ATR starts from ZERO ← MISMATCH
```

**Specific Requirements**:
- Bars 0-31: ATR uses expanding window
- Bars 32-63: Adaptive coefficient stabilizes
- Bar 64+: All components warmed up
- **Production minimum: 5000 bars**

### MQL5 Expanding Window Behavior

MQL5 divides by `period` even for partial windows, NOT by available bar count.

**MQL5**:
```mql5
for(int i=0; i<period && i<rates_total; i++)
{
    sum += tr[i];
    atr[i] = sum / period;  // Divide by period, not (i+1)
}

for(int i=period; i<rates_total; i++)
{
    atr[i] = mean(tr[i-period+1 : i+1]);
}
```

**Python** (manual loops required):
```python
atr = pd.Series(index=tr.index, dtype=float)

for i in range(len(tr)):
    if i < period:
        atr.iloc[i] = tr.iloc[:i+1].sum() / period  # NOT / (i+1)
    else:
        atr.iloc[i] = tr.iloc[i-period+1:i+1].mean()
```

**Example**:
```python
# Bar 5 (6 bars available, period=32):
# MQL5:    sum(0-5) / 32 = 0.000123 / 32 = 0.00000384
# Pandas:  sum(0-5) / 6  = 0.000123 / 6  = 0.0000205 (WRONG)
```

---

## Two-Stage Validation

### Stage 1: Fetch Historical Dataset (AUTOMATED)

```bash
CX="~/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine"
"$CX" --bottle "MetaTrader 5" "C:\\Program Files\\Python312\\python.exe" -c '
import MetaTrader5 as mt5
import pandas as pd

mt5.initialize()
mt5.symbol_select("EURUSD", True)
rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M1, 0, 5000)

df = pd.DataFrame(rates)
df["time"] = pd.to_datetime(df["time"], unit="s")
df[["time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]].to_csv(
    "C:\\users\\crossover\\EURUSD_M1_5000bars.csv", index=False)
mt5.shutdown()
'
```

### Stage 2: Calculate and Compare (AUTOMATED)

```python
import pandas as pd
import numpy as np
from indicators.your_indicator import calculate_your_indicator
from scipy.stats import pearsonr

# Load 5000 bars
df_5000 = pd.read_csv("EURUSD_M1_5000bars.csv")
df_5000["time"] = pd.to_datetime(df_5000["time"])

# Calculate on ALL 5000 bars
result_5000 = calculate_your_indicator(df_5000, param1=32, param2='ema')

# Extract last 100 for comparison
result_last100 = result_5000.iloc[-100:].copy()

# Load MQL5 export
df_mql5 = pd.read_csv("Export_EURUSD_PERIOD_M1.csv")

# Compare
for buffer_name, py_col in [('Buffer1', 'buffer1')]:
    mql_col = next(c for c in df_mql5.columns if c.lower().startswith(buffer_name.lower()))

    py_values = result_last100[py_col].values
    mql_values = df_mql5[mql_col].values
    mask = ~(np.isnan(py_values) | np.isnan(mql_values))

    corr, _ = pearsonr(py_values[mask], mql_values[mask])
    mae = np.mean(np.abs(py_values[mask] - mql_values[mask]))

    status = "PASS" if corr >= 0.999 else "FAIL"
    print(f"[{status}] {buffer_name}: corr={corr:.6f}, MAE={mae:.6f}")
```

---

## Correlation Thresholds

### Production: ≥0.999

```python
# WRONG
if correlation > 0.90:
    print("Good enough")

# RIGHT
if correlation >= 0.999:
    print("Production ready")
else:
    print("FAIL - systematic bias")
```

**Why 0.999 not 0.95**:
- 0.95 = systematic bias (usually missing warmup)
- Production trading requires 99.9%+ accuracy
- Small errors compound in live trading

| Criterion | Target |
|-----------|--------|
| Correlation (per buffer) | ≥ 0.999 |
| MAE | < 0.001 |
| NaN count (after warmup) | 0 |

### Troubleshooting

| Correlation | Likely Cause | Solution |
|-------------|--------------|----------|
| ~0.95 | Missing warmup | Fetch 5000 bars, calculate on all |
| ~0.85-0.95 | NaN values | Check pandas behavior, use manual loops |
| ~0.70-0.85 | Algorithm mismatch | Verify EMA/SMA/SMMA formulas |
| < 0.70 | Major error | Restart with algorithm analysis |

**Debug Steps**:
1. Check NaN counts
2. Compare first 10 bars (initialization)
3. Compare last 10 bars (steady-state)
4. Plot differences
5. Verify warmup (5000 bars fetched?)

---

## Common Pitfalls

### 1. Pandas Rolling Windows Return NaN

**Problem**:
```python
# WRONG - First 31 bars are NaN
atr = tr.rolling(window=32).mean()
```

**Solution**: See MQL5 Expanding Window Behavior section

### 2. Pandas Expanding Mean Wrong Denominator

**Problem**: `expanding().mean()` divides by actual window size, not period.

**Solution**: Manual loops (see above)

### 3. Comparing MQL5 With Warmup vs Python Cold Start

**Solution**: Fetch 5000 bars, calculate on all, compare last N

### 4. Accepting 0.95 Correlation

**Reality**: 0.95 = systematic bias. Production requires 0.999+

### 5. Off-by-One Errors

**Problem**:
```python
# WRONG - Misses last bar
for i in range(len(df) - 1):
    atr.iloc[i] = calculate(...)
```

**Solution**:
```python
# RIGHT
for i in range(len(df)):
    atr.iloc[i] = calculate(...)

# Verify
assert result['atr'].notna().sum() == len(df)
```

### 6. Series vs iloc Indexing

**Problem**:
```python
# WRONG - May fail if index != [0,1,2,...]
for i in range(len(df)):
    value = df['close'][i]
```

**Solution**:
```python
# RIGHT - Position-based
for i in range(len(df)):
    value = df['close'].iloc[i]
```

---

## Success Criteria Checklist

**Compilation (MANUAL)**:
- [ ] MQL5: 0 errors, .ex5 created (~25KB)
- [ ] All buffers exposed

**Data (AUTOMATED)**:
- [ ] 5000+ bars fetched
- [ ] CSV verified (~305KB for M1)

**Visual (MANUAL)**:
- [ ] Indicator on MT5 chart
- [ ] Data Window shows values
- [ ] Warmed up (10+ seconds)

**Python (MANUAL)**:
- [ ] All functions implemented
- [ ] No pandas NaN traps
- [ ] Proper `.iloc` indexing

**Validation (AUTOMATED)**:
- [ ] Calculated on 5000 bars
- [ ] Last 100 extracted
- [ ] Correlation ≥ 0.999 ALL buffers
- [ ] MAE < 0.001
- [ ] Zero NaN in comparison

**Algorithm (MANUAL)**:
- [ ] No look-ahead (`buffer[i+1]`)
- [ ] All MA methods verified
- [ ] Consistent behavior

**Documentation (MANUAL)**:
- [ ] Algorithm analysis created
- [ ] Validation report created
- [ ] CLAUDE.md updated

---

## Debugging Tools

### NaN Count
```python
print(f"NaN: {result['buffer'].isna().sum()} / {len(result)}")
```

### First/Last Comparison
```python
print("Python first 10:", result['buffer'].head(10).values)
print("MQL5 first 10:", df_mql5['Buffer'].head(10).values)
```

### Statistics
```python
print(f"Min: {result['buffer'].min():.6f}")
print(f"Max: {result['buffer'].max():.6f}")
print(f"Mean: {result['buffer'].mean():.6f}")
```

### Visual Diff
```python
import matplotlib.pyplot as plt
diff = mql5_values - python_values
plt.plot(diff)
plt.title("MQL5 - Python Difference")
plt.show()
```

---

## Time Estimates

| Phase | First Time | Subsequent |
|-------|------------|------------|
| Fetch data | 5-10 min | 2-3 min |
| Implement | 1-2 hours | 30-60 min |
| Validate | 15-30 min | 5-10 min |
| Debug | 1-3 hours | 15-30 min |
| **Total** | **2-5 hours** | **1-2 hours** |

---

## References

- `PYTHON_INDICATOR_VALIDATION_FAILURES.md` - 3-hour debugging timeline
- `LESSONS_LEARNED_PLAYBOOK.md` - 185+ hours lessons
- `LAGUERRE_RSI_VALIDATION_SUCCESS.md` - Perfect correlation achieved
- `MQL5_TO_PYTHON_MIGRATION_GUIDE.md` - Complete workflow
- `WINE_PYTHON_EXECUTION.md` - v3.0.0 Wine Python
