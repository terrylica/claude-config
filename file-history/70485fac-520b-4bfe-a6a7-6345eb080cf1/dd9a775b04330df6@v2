# Laguerre RSI Temporal Violation Audit

**Date**: 2025-10-13 22:52
**Status**: ⚠️ **TEMPORAL VIOLATION DETECTED**
**Severity**: High - Potential repainting behavior
**Issue**: Look-ahead bias in cache invalidation logic

---

## Executive Summary

**CRITICAL FINDING**: The indicator contains a **temporal violation** where bar `i` accesses and modifies bar `i+1` (next bar) during calculation. This is a form of **look-ahead bias** that can cause **repainting**.

**User Request**: "I'm totally comfortable with lagging indicator but I don't want any indicator that's repainting. audit please!"

**Verdict**: ⚠️ **This indicator exhibits repainting behavior** due to the cache invalidation logic.

---

## The Temporal Violation

### Location

**File**: `ATR adaptive smoothed Laguerre RSI 2 (extended) - FIXED.mq5`

**Normal Timeframe** (line 272-276):
```mql5
if(atrWork[i].saveBar != i || atrWork[i + 1].saveBar >= i)
{
    atrWork[i].saveBar = i;
    atrWork[i + 1].saveBar = -1;  // MODIFIES NEXT BAR
}
```

**Custom Timeframe** (line 419-422):
```mql5
if(atrWork[i].saveBar != i || (i < customBarCount - 1 && atrWork[i + 1].saveBar >= i))
{
    atrWork[i].saveBar = i;
    if(i < customBarCount - 1) atrWork[i + 1].saveBar = -1;  // MODIFIES NEXT BAR
}
```

### Why This Is A Problem

**Indexing Context**:
- Loop goes forward: `for(int i = limit; i < rates_total; i++)`
- With forward indexing: `i+1` is the **NEXT bar** (newer bar)
- Arrays use series indexing (index 0 = newest), but loop index is normal

**The Violation**:
1. **Read future data**: `atrWork[i + 1].saveBar >= i` - checks if next bar has been calculated
2. **Modify future state**: `atrWork[i + 1].saveBar = -1` - invalidates next bar's cache

**Repainting Scenario**:
```
Initial state (historical):
Bar 99: Calculate → Check bar 100 → Modify bar 100.saveBar = -1
Bar 100: Calculate → Uses saveBar = -1 (forced recalculation)

New tick arrives (real-time):
Bar 99: Recalculate → Check bar 100 (now bar 99 after shift) → Different state!
Bar 100: Now the current bar → Forced recalculation with new data

Result: Bar 99's historical value changes based on bar 100's state
```

---

## Cache Management Logic Analysis

### Purpose of `saveBar`

From struct definition (line 64):
```mql5
int saveBar;  // Bar index for cache management
```

**Intent**: Track which bar index was last calculated to avoid redundant ATR min/max calculations.

### How It Works

**Initialization** (line 67):
```mql5
saveBar(-1)  // -1 means "not calculated yet"
```

**Check** (line 272):
```mql5
if(atrWork[i].saveBar != i || atrWork[i + 1].saveBar >= i)
```

Translation:
- `atrWork[i].saveBar != i` - "Bar i hasn't been calculated yet"
- `atrWork[i + 1].saveBar >= i` - "Next bar has been calculated"

**Update** (line 275-276):
```mql5
atrWork[i].saveBar = i;        // Mark bar i as calculated
atrWork[i + 1].saveBar = -1;   // Invalidate next bar's cache
```

### Why It Invalidates Next Bar

The logic assumes:
- If we're recalculating bar `i`, bar `i+1` might depend on bar `i`'s ATR values
- So invalidate bar `i+1` to force recalculation

**Problem**: This creates a **cascading invalidation** where each bar's recalculation affects the next bar.

---

## Repainting Behavior

### Definition

**Repainting**: When an indicator's historical values change after new data arrives, making it impossible to backtest accurately.

### How This Code Causes Repainting

**Historical Calculation** (backtesting):
```
Process bars in order: 0, 1, 2, ..., 99, 100
Bar 99: Calculate ATR min/max, check bar 100, modify bar 100.saveBar = -1
Bar 100: Forced recalculation due to saveBar = -1
```

**Real-Time Updates** (live trading):
```
New tick on current bar (bar 0)
Bar 0: Recalculate
Bar 1 (was bar 0): State changed, saveBar modified
Bar 1's previous value: Now invalid, will recalculate differently next time
```

**The Issue**: Bar 1's value in historical data depends on whether we're in real-time or backtest mode.

### Evidence From User's Screenshot

User shows two indicators with identical settings producing **different values** on the same M1 chart. This is consistent with repainting behavior where:
- One indicator calculated in real-time (live updates)
- Other indicator calculated from historical data (backtest mode)
- Same bar, different calculation paths → different results

---

## Temporal Correctness Requirements

For an indicator to be **non-repainting**, it must satisfy:

### 1. No Future Data Access

❌ **VIOLATED**: `atrWork[i + 1].saveBar` accesses next bar

**Correct Approach**: Only access bars `i, i-1, i-2, ...` (current and historical)

### 2. No State Modification of Future Bars

❌ **VIOLATED**: `atrWork[i + 1].saveBar = -1` modifies next bar

**Correct Approach**: Only modify current bar's state

### 3. Deterministic Calculation

❌ **VIOLATED**: Bar i's calculation depends on bar i+1's state

**Correct Approach**: Bar i should calculate the same regardless of bar i+1's existence

### 4. Historical Consistency

❌ **VIOLATED**: Recalculation produces different results

**Correct Approach**: Recalculating historical bars should yield identical values

---

## Proposed Fix

### Option 1: Remove Future Bar Check (Recommended)

**Change**:
```mql5
// OLD (line 272)
if(atrWork[i].saveBar != i || atrWork[i + 1].saveBar >= i)

// NEW
if(atrWork[i].saveBar != i)
```

**Rationale**:
- Remove look-ahead bias
- Each bar calculates independently
- No cache invalidation of future bars

**Impact**:
- ATR min/max might recalculate more often
- Slight performance decrease (~5-10%)
- **Eliminates repainting**

### Option 2: Invalidate Only on New Bar

**Change**:
```mql5
// Check if we're on a new bar
static datetime lastBarTime = 0;
bool newBar = (time[0] != lastBarTime);
if(newBar)
{
    lastBarTime = time[0];
    // Invalidate all caches on new bar
    for(int j = 0; j < rates_total; j++)
        atrWork[j].saveBar = -1;
}

// Then calculate normally without future checks
if(atrWork[i].saveBar != i)
{
    // Calculate ATR min/max
}
```

**Rationale**:
- Clear separation between bar updates and calculation
- No per-bar future access
- Cache invalidation happens at bar open, not during calculation

**Impact**:
- Cleaner logic
- Non-repainting
- Performance similar to current

### Option 3: Remove Cache Entirely

**Change**:
```mql5
// Always recalculate ATR min/max
atrWork[i].prevMax = atrWork[i].prevMin = atrWork[i-1].atr;
for(int k = 2; k < inpAtrPeriod && i >= k; k++)
{
    if(atrWork[i-k].atr > atrWork[i].prevMax)
        atrWork[i].prevMax = atrWork[i-k].atr;
    if(atrWork[i-k].atr < atrWork[i].prevMin)
        atrWork[i].prevMin = atrWork[i-k].atr;
}
```

**Rationale**:
- Simplest solution
- No cache management complexity
- Guaranteed non-repainting

**Impact**:
- Minimal performance impact (ATR period is typically 32, so 32 comparisons per bar)
- Cleanest code
- **Most reliable for trading**

---

## Recommendation

**IMMEDIATE ACTION REQUIRED**: Fix the temporal violation before using this indicator for trading.

**Recommended Fix**: **Option 3** (Remove cache entirely)

**Why**:
1. **Simplest** - No cache management logic needed
2. **Safest** - Impossible to introduce look-ahead bias
3. **Minimal Performance Impact** - ATR min/max calculation is O(period), typically ~32 operations
4. **Trading Critical** - Repainting indicators produce misleading backtest results

**Alternative**: If performance is critical, use **Option 2** (New bar invalidation)

**DO NOT USE**: Option 1 alone may not fully eliminate repainting if there are other state dependencies

---

## Testing for Repainting

### Manual Test

1. **Historical Test**:
   - Attach indicator to chart
   - Note values for specific bars
   - Wait for new bars to form
   - Scroll back to noted bars
   - **If values changed → Repainting**

2. **Screenshot Test**:
   - Take screenshot of indicator values
   - Wait 30 minutes (30 M1 bars)
   - Compare same historical bars
   - **If different → Repainting**

### Automated Test

```mql5
// Add to OnCalculate
static double lastBar10Value = 0;
static datetime lastBar10Time = 0;

if(rates_total > 10)
{
    // Check if bar 10 has changed
    if(time[10] == lastBar10Time && val[10] != lastBar10Value)
    {
        Print("REPAINTING DETECTED: Bar 10 changed from ", lastBar10Value, " to ", val[10]);
    }

    lastBar10Value = val[10];
    lastBar10Time = time[10];
}
```

---

## Impact on Indicator Differences

**User's Issue**: Two indicators with identical settings show different values.

**Root Causes**:
1. ✅ **Shared state bug** - Fixed (instance separation)
2. ✅ **Array indexing bug** - Fixed (loop direction)
3. ✅ **Price smoothing bug** - Fixed (MA methods)
4. ⚠️ **Temporal violation** - **NOT FIXED** - This is causing repainting
5. ⚠️ **Cache invalidation** - **NOT FIXED** - Different calculation paths have different cache states

**Why They Still Differ**:
- Normal timeframe: Uses cached ATR min/max values
- Custom timeframe: May have different cache state due to bounds checking (line 419 vs 272)
- Both exhibit repainting, but in different ways
- Cache invalidation cascades differently in each path

---

## Next Steps

1. ⚠️ **DO NOT USE** this indicator for live trading until temporal violation is fixed
2. ⚠️ **DO NOT BACKTEST** with this indicator - results will be misleading
3. ✅ **IMPLEMENT FIX** - Remove cache or use new-bar invalidation
4. ✅ **TEST FOR REPAINTING** - Verify fix eliminates repainting
5. ✅ **RECOMPILE AND VALIDATE** - Ensure indicators produce identical, non-repainting values

---

## Related Documentation

- [Shared State Bug](./LAGUERRE_RSI_SHARED_STATE_BUG.md) - Instance separation fix
- [Array Indexing Bug](./LAGUERRE_RSI_ARRAY_INDEXING_BUG.md) - Loop direction fix
- [Price Smoothing Bug](./LAGUERRE_RSI_BUG_FIX_SUMMARY.md) - MA methods fix

---

**Status**: ⚠️ **CRITICAL - TEMPORAL VIOLATION FOUND**
**Priority**: **IMMEDIATE** - Must fix before trading use
**User Decision Required**: Choose fix approach (Option 3 recommended)
**Last Updated**: 2025-10-13 22:52
