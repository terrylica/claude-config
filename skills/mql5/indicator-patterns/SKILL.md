______________________________________________________________________

## name: mql5-indicator-patterns description: MQL5 visual indicator construction patterns and debugging. Use when developing custom MQL5 indicators with visual plots, handling bar recalculation, debugging blank/invisible indicator displays, working with indicator buffers, or fixing display scale issues. Covers IndicatorSetDouble, INDICATOR_MINIMUM, INDICATOR_MAXIMUM, DRAW_LINE, INDICATOR_DATA, INDICATOR_CALCULATIONS, rolling window state management, and bar recalculation patterns. allowed-tools: Read, Grep, Edit, Write

# MQL5 Visual Indicator Patterns

Battle-tested patterns for creating custom MQL5 indicators with proper display, buffer management, and real-time updates.

## Part 1: Display Scale Management

### Problem: Blank Indicator Window

**Symptom**: Indicator compiles successfully but shows blank/empty window on chart

**Root Cause**: MT5 auto-scaling fails for very small values (e.g., 0.00-0.05 range)

### Solution: Explicit Scale Setting

```mql5
int OnInit()
{
   // ... other initialization ...

   // FIX: Explicitly set scale range for small values
   IndicatorSetDouble(INDICATOR_MINIMUM, 0.0);
   IndicatorSetDouble(INDICATOR_MAXIMUM, 0.1);

   return INIT_SUCCEEDED;
}
```

**When to use**:

- Score/probability indicators (0.0-1.0 range)
- Normalized metrics with small variations
- Any values where range < 1.0

**Reference**: MQL5 forum threads 135340, 137233, 154523 document this limitation

______________________________________________________________________

## Part 2: Buffer Architecture Patterns

### Two-Buffer Pattern (Visible + Hidden)

Use when you need to track previous values for recalculation:

```mql5
#property indicator_buffers 2  // Total buffers
#property indicator_plots   1  // Visible plots

double BufVisible[];  // Plot buffer
double BufHidden[];   // Tracking buffer

int OnInit()
{
   SetIndexBuffer(0, BufVisible, INDICATOR_DATA);        // Visible
   SetIndexBuffer(1, BufHidden, INDICATOR_CALCULATIONS); // Hidden

   return INIT_SUCCEEDED;
}
```

**Buffer Types**:

- `INDICATOR_DATA`: Visible plot (appears on chart)
- `INDICATOR_CALCULATIONS`: Hidden buffer (for internal calculations)

**Why use hidden buffers**:

- Store previous bar values for recalculation
- Track intermediate calculation steps
- Maintain rolling window state

______________________________________________________________________

## Part 3: Bar Recalculation Pattern

### Problem: Rolling Window Drift

Current bar updates with each tick. Naive implementations double-count values, causing drift in rolling statistics.

### Solution: New Bar Detection + Value Replacement

```mql5
// Static variables preserve state between OnCalculate calls
static double sum = 0.0;
static int last_processed_bar = -1;

int OnCalculate(const int rates_total, const int prev_calculated, ...)
{
   for(int i = start; i < rates_total; i++)
   {
      // Detect if this is a NEW bar (not recalculation)
      bool is_new_bar = (i > last_processed_bar);

      double current_value = GetValue(i);

      if(is_new_bar)
      {
         // NEW BAR: Add to window, slide if needed
         if(i >= window_size)
         {
            int idx_out = i - window_size;
            sum -= BufHidden[idx_out];  // Remove oldest
         }
         sum += current_value;  // Add newest
      }
      else
      {
         // RECALCULATION: Replace old value with new value
         if(i == last_processed_bar && BufHidden[i] != EMPTY_VALUE)
         {
            sum -= BufHidden[i];        // Remove old contribution
         }
         sum += current_value;          // Add new value
      }

      // Store for next recalculation
      BufHidden[i] = current_value;
      last_processed_bar = i;

      // Calculate indicator using sum
      BufVisible[i] = sum / window_size;
   }

   return rates_total;
}
```

**Key points**:

- `is_new_bar` differentiates new bars from recalculation
- Hidden buffer stores old values for subtraction
- Static `last_processed_bar` tracks position
- Only slide window on NEW bars

______________________________________________________________________

## Part 4: Rolling Window State Management

### Pattern: Static Sum Variables

```mql5
static double sum = 0.0;
static double sum_squared = 0.0;
static int last_processed_bar = -1;

// Initialize sums on first run
if(prev_calculated == 0 || start == StartCalcPosition)
{
   sum = 0.0;
   sum_squared = 0.0;
   last_processed_bar = StartCalcPosition - 1;

   // Prime the window with initial values
   for(int j = start - window_size + 1; j <= start; j++)
   {
      double x = GetValue(j);
      sum += x;
      sum_squared += x * x;
   }
}
```

**Why static variables**:

- Preserve state between `OnCalculate()` calls
- Avoid recalculating entire window each tick
- Enable O(1) sliding window updates

**Initialization pattern**:

- Reset on first run (`prev_calculated == 0`)
- Prime window with initial N values
- Update incrementally thereafter

______________________________________________________________________

## Part 5: PLOT_DRAW_BEGIN Calculation

### Warmup Requirement Pattern

```mql5
int OnInit()
{
   // Calculate total warmup needed
   int cci_warmup = InpCCILength;        // Underlying indicator
   int window_warmup = InpWindow - 1;    // Rolling window
   int StartCalcPosition = cci_warmup + window_warmup;

   // Tell MT5 when valid values start
   PlotIndexSetInteger(0, PLOT_DRAW_BEGIN, StartCalcPosition);

   // Initialize early bars as EMPTY_VALUE
   for(int i = 0; i < StartCalcPosition; i++)
   {
      BufVisible[i] = EMPTY_VALUE;
   }

   return INIT_SUCCEEDED;
}
```

**Formula**: `PLOT_DRAW_BEGIN = underlying_warmup + own_warmup - 1`

**Why**:

- Prevents plotting garbage values during warmup
- Matches bars to ensure alignment with base indicator
- Required for composite indicators

______________________________________________________________________

## Part 6: Common Pitfalls & Solutions

### Pitfall 1: Blank Display with Valid Data

**Symptom**: CSV shows valid values but chart is blank

**Fix**: Set explicit scale (see Part 1)

### Pitfall 2: Rolling Window Drift

**Symptom**: Values slowly drift away from expected range

**Fix**: Use bar recalculation pattern with hidden buffer (Part 3)

### Pitfall 3: Misaligned Plots

**Symptom**: Indicator values don't match underlying indicator timing

**Fix**: Calculate correct `PLOT_DRAW_BEGIN` (Part 5)

### Pitfall 4: Forward-Indexed Arrays

**Symptom**: Values appear backwards or misaligned

**Fix**: Always set arrays as forward-indexed:

```mql5
ArraySetAsSeries(BufVisible, false);
ArraySetAsSeries(BufHidden, false);
```

MQL5 defaults to reverse indexing (series) - override for clarity.

______________________________________________________________________

## Part 7: Complete Example Template

```mql5
#property indicator_separate_window
#property indicator_buffers 2
#property indicator_plots   1

#property indicator_label1    "My Indicator"
#property indicator_type1     DRAW_LINE
#property indicator_color1    clrOrange
#property indicator_width1    2

input int InpPeriod = 20;
input int InpWindow = 30;

double BufVisible[];
double BufHidden[];
int hBase = INVALID_HANDLE;

int OnInit()
{
   // Buffers
   SetIndexBuffer(0, BufVisible, INDICATOR_DATA);
   SetIndexBuffer(1, BufHidden, INDICATOR_CALCULATIONS);

   // Warmup
   int StartCalcPosition = InpPeriod + InpWindow - 1;
   PlotIndexSetInteger(0, PLOT_DRAW_BEGIN, StartCalcPosition);
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);

   // Explicit scale for small values
   IndicatorSetDouble(INDICATOR_MINIMUM, 0.0);
   IndicatorSetDouble(INDICATOR_MAXIMUM, 1.0);

   // Base indicator
   hBase = iSomeIndicator(_Symbol, _Period, InpPeriod);
   if(hBase == INVALID_HANDLE) return INIT_FAILED;

   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(hBase != INVALID_HANDLE) IndicatorRelease(hBase);
}

int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                ...)
{
   int StartCalcPosition = InpPeriod + InpWindow - 1;
   if(rates_total <= StartCalcPosition) return 0;

   // Get base data
   static double base[];
   ArrayResize(base, rates_total);
   ArraySetAsSeries(base, false);
   if(CopyBuffer(hBase, 0, 0, rates_total, base) < rates_total)
      return prev_calculated;

   // Set forward indexing
   ArraySetAsSeries(BufVisible, false);
   ArraySetAsSeries(BufHidden, false);

   // Start position
   int start = (prev_calculated == 0) ? StartCalcPosition : prev_calculated - 1;
   if(start < StartCalcPosition) start = StartCalcPosition;

   // Initialize early bars
   if(prev_calculated == 0)
   {
      for(int i = 0; i < start; i++)
      {
         BufVisible[i] = EMPTY_VALUE;
         BufHidden[i] = EMPTY_VALUE;
      }
   }

   // Rolling window state
   static double sum = 0.0;
   static int last_processed_bar = -1;

   // Prime window on first run
   if(prev_calculated == 0 || start == StartCalcPosition)
   {
      sum = 0.0;
      last_processed_bar = StartCalcPosition - 1;

      for(int j = start - InpWindow + 1; j <= start; j++)
         sum += base[j];
   }

   // Main loop
   for(int i = start; i < rates_total && !IsStopped(); i++)
   {
      bool is_new_bar = (i > last_processed_bar);

      // Slide window on new bar
      if(is_new_bar && i >= InpWindow)
      {
         int idx_out = i - InpWindow;
         sum -= base[idx_out];
      }

      double current = base[i];

      // Update sum
      if(is_new_bar)
      {
         sum += current;
      }
      else
      {
         if(i == last_processed_bar && BufHidden[i] != EMPTY_VALUE)
            sum -= BufHidden[i];
         sum += current;
      }

      last_processed_bar = i;

      // Calculate & store
      BufHidden[i] = current;
      BufVisible[i] = sum / InpWindow;
   }

   return rates_total;
}
```

______________________________________________________________________

## Part 8: Debugging Checklist

When indicator not displaying correctly:

1. **Check scale**:

   - [ ] Added `IndicatorSetDouble(INDICATOR_MINIMUM/MAXIMUM)`?
   - [ ] Range appropriate for data values?

1. **Check buffers**:

   - [ ] `indicator_buffers` >= `indicator_plots`?
   - [ ] Hidden buffers for tracking old values?
   - [ ] `ArraySetAsSeries(buffer, false)` for all buffers?

1. **Check warmup**:

   - [ ] `PLOT_DRAW_BEGIN` calculated correctly?
   - [ ] Early bars initialized to `EMPTY_VALUE`?

1. **Check recalculation**:

   - [ ] Bar detection logic (`is_new_bar`)?
   - [ ] Old value subtraction before adding new?
   - [ ] `last_processed_bar` tracking working?

1. **Check data flow**:

   - [ ] Base indicator handle valid?
   - [ ] `CopyBuffer` returning expected count?
   - [ ] No `EMPTY_VALUE` in calculated range?

______________________________________________________________________

## Summary

**Key patterns for production MQL5 indicators**:

1. **Explicit scale** for small values (< 1.0 range)
1. **Hidden buffers** for recalculation tracking
1. **New bar detection** prevents rolling window drift
1. **Static variables** maintain state efficiently
1. **Proper warmup** calculation prevents misalignment
1. **Forward indexing** for code clarity

These patterns solve the most common indicator development issues encountered in real-world MT5 development.
