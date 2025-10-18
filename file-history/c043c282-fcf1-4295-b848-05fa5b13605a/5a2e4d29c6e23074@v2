# Iteration 2: SMA Test Plan

**Version**: 1.0.0
**Date**: 2025-10-17
**Purpose**: Validate minimal workflow with simplest possible indicator

---

## Test Objective

Validate that MQL5_TO_PYTHON_MINIMAL.md workflow works for a SIMPLE indicator.

**Why SMA**:
- Algorithm: `SMA[i] = sum(close[i-period+1 .. i]) / period`
- No dependencies (no #include needed)
- No complex state
- Should complete in < 1 hour

---

## Approach

Create minimal SMA indicator from scratch (not use existing complex indicators).

**Intent**: Test the WORKFLOW, not validate an already-working indicator.

---

## Test Indicator Specification

### Name
`SimpleSMA_Test.mq5`

### Algorithm
```cpp
// Simple Moving Average - Test Implementation
#property indicator_chart_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "SMA"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrBlue
#property indicator_width1  2

input int InpPeriod = 14;  // SMA Period

double SMABuffer[];

int OnInit()
{
    SetIndexBuffer(0, SMABuffer, INDICATOR_DATA);
    IndicatorSetString(INDICATOR_SHORTNAME, StringFormat("SMA(%d)", InpPeriod));
    return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
    int start = InpPeriod - 1;
    if(prev_calculated == 0)
    {
        // Initialize
        ArrayInitialize(SMABuffer, 0.0);
    }
    else
    {
        start = prev_calculated - 1;
    }

    for(int i = start; i < rates_total; i++)
    {
        double sum = 0.0;
        for(int j = 0; j < InpPeriod; j++)
        {
            sum += close[i - j];
        }
        SMABuffer[i] = sum / InpPeriod;
    }

    return(rates_total);
}
```

---

## Test Execution Plan

### Phase 0: Setup (5 min)
- [ ] Create SimpleSMA_Test.mq5 in PythonInterop folder
- [ ] Verify prerequisites (Wine Python, MT5 package, terminal)

### Phase 1: Compile (5 min)
- [ ] Compile SimpleSMA_Test.mq5 using CLI method
- [ ] Verify .ex5 created
- [ ] Record compilation time

### Phase 2: Fetch Data (5 min)
- [ ] Use existing EURUSD_M1_5000bars.csv (already have from Laguerre RSI)
- [ ] Or fetch fresh if needed

### Phase 3: Export MQL5 Values (10 min)
- [ ] Attach SimpleSMA_Test to EURUSD M1 chart
- [ ] Wait for calculation
- [ ] Export last 100 bars to CSV
- [ ] Record method used (ExportAligned vs manual)

### Phase 4: Implement Python SMA (15 min)
- [ ] Create users/crossover/indicators/simple_sma.py
- [ ] Implement SMA function (should be ~10 lines)
- [ ] Match MQL5 initialization behavior

### Phase 5: Validate (10 min)
- [ ] Run correlation test
- [ ] Expect correlation >= 0.999
- [ ] Record actual correlation value

### Phase 6: Document (15 min)
- [ ] Record actual time for each phase
- [ ] Note any deviations from minimal workflow
- [ ] Identify gaps in documentation
- [ ] Create ITERATION_2_SMA_TEST_REPORT.md

---

## Success Criteria

- [ ] SMA Python correlation >= 0.999
- [ ] Total time <= 1 hour
- [ ] No undocumented steps required
- [ ] All commands from minimal workflow worked

---

## Deviations to Track

| Step | Expected (from guide) | Actual | Deviation? |
|------|----------------------|--------|------------|
| Prerequisites | 5 min | | |
| Find indicator | N/A (creating new) | | |
| Analyze | 5 min (simple) | | |
| Modify/Create | 10 min | | |
| Compile | 5 min | | |
| Fetch Data | 5 min | | |
| Export MQL5 | 10 min | | |
| Implement Python | 15 min | | |
| Validate | 10 min | | |
| **Total** | **1 hour** | | |

---

## Next Steps

1. Execute test following minimal workflow EXACTLY
2. Fill in "Actual" times
3. Note all deviations
4. Create test report
5. Update minimal workflow if needed (Iteration 3)

---

**Status**: Plan created, ready to execute
