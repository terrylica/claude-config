# ATR Adaptive Laguerre RSI - Complete Validation Plan

**Date**: 2025-10-16
**Status**: Planning Phase
**Objective**: Validate Python translation achieves correlation ≥ 0.999 with MQL5 implementation

---

## Executive Summary

This document outlines a comprehensive validation strategy for verifying that the Python implementation of ATR Adaptive Laguerre RSI (`users/crossover/indicators/laguerre_rsi.py`) produces numerically equivalent results to the MQL5 indicator (`PythonInterop/ATR_Adaptive_Laguerre_RSI.mq5`).

**Current State**:
- ✅ Python implementation complete (456 lines, 9 functions)
- ✅ Export integration complete (`export_aligned.py`)
- ⏳ Validation pending - NO comparison with MQL5 indicator yet
- ❌ MQL5 export script does NOT yet export indicator buffer values

**Validation Gap**: Current workflow calculates Laguerre RSI only in Python. MQL5 indicator values are never compared.

**Solution**: Dual-export validation workflow with statistical analysis.

---

## Current State Analysis

### Python Implementation

**File**: `users/crossover/indicators/laguerre_rsi.py`

**Modular Structure** (9 functions):
1. `calculate_true_range()` - True Range calculation
2. `calculate_atr()` - Simple MA of TR over period
3. `calculate_atr_min_max()` - Rolling min/max ATR
4. `calculate_adaptive_coefficient()` - ATR-based coefficient (0.0-1.0)
5. `calculate_adaptive_period()` - Adaptive period = atr_period * (coeff + 0.75)
6. `get_price_series()` - Price extraction with 4 MA methods (SMA/EMA/SMMA/LWMA)
7. `calculate_laguerre_filter()` - Four-stage recursive filter
8. `calculate_laguerre_rsi()` - RSI from filter stages
9. `classify_signal()` - Signal classification (bullish/bearish/neutral)

**Main Function**: `calculate_laguerre_rsi_indicator()` - End-to-end calculation

**Parameters**:
- `atr_period=32` - ATR period
- `price_type='close'` - Price to use
- `price_smooth_period=5` - Price smoothing period
- `price_smooth_method='ema'` - Price smoothing method
- `level_up=0.85` - Upper threshold
- `level_down=0.15` - Lower threshold

### MQL5 Implementation

**File**: `PythonInterop/ATR_Adaptive_Laguerre_RSI.mq5`

**Parameters** (lines 18-24):
```mql5
input string             inpInstanceID  = "A";            // Instance ID
input int                inpAtrPeriod   = 32;             // ATR period ✓ matches Python
input ENUM_APPLIED_PRICE inpRsiPrice    = PRICE_CLOSE;    // Price ✓ matches Python
input int                inpRsiMaPeriod = 5;              // Price smoothing period ✓ matches Python
input ENUM_MA_METHOD     inpRsiMaType   = MODE_EMA;       // Price smoothing method ✓ matches Python
input double             inpLevelUp     = 0.85;           // Level up ✓ matches Python
input double             inpLevelDown   = 0.15;           // Level down ✓ matches Python
```

**Buffers**:
- `val[]` - Main indicator values (Laguerre RSI)
- `valc[]` - Color index (signal classification)
- `prices[]` - Smoothed price values

**Algorithm Flow**:
1. Calculate True Range (lines 240-243)
2. Calculate ATR via sliding window (lines 246-260)
3. Calculate ATR min/max over lookback period (lines 263-283)
4. Calculate adaptive coefficient (lines 286-288)
5. Calculate Laguerre RSI with adaptive period (line 291)
6. Set color based on thresholds (line 294)

**Temporal Status**: Clean - No look-ahead bias (validated 2025-10-16)

### Current Export Workflow

**Python Script**: `users/crossover/export_aligned.py`

**Current Behavior**:
1. Fetches OHLC data from MT5 via Python API (`mt5.copy_rates_from_pos()`)
2. Calculates RSI in Python (14-period, standard formula)
3. Calculates Laguerre RSI in Python (`calculate_laguerre_rsi_indicator()`)
4. Exports to CSV: Time, OHLC, Volume, RSI, Laguerre_RSI, Laguerre_Signal, Adaptive_Period, ATR

**Problem**: All calculations are Python-only. No comparison with MQL5 indicator.

**MQL5 Script**: `Scripts/DataExport/ExportAligned.mq5`

**Current Behavior**:
1. Exports OHLC data
2. Exports RSI via `RSIModule.mqh`
3. **Does NOT export Laguerre RSI from indicator**

**Gap**: Need MQL5 script to export indicator buffer values for comparison.

---

## Validation Architecture

### Dual-Export Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Validation Workflow                          │
└─────────────────────────────────────────────────────────────────┘

1. MQL5 Export Path:
   ┌──────────────┐    ┌────────────────┐    ┌─────────────────┐
   │ MT5 Terminal │───>│ MQL5 Script    │───>│ CSV (MQL5)      │
   │  (OHLC data) │    │ + iCustom()    │    │ - OHLC          │
   │              │    │   indicator    │    │ - Laguerre_MQL5 │
   └──────────────┘    └────────────────┘    └─────────────────┘
                                                      │
                                                      v
2. Python Validation:                     ┌─────────────────────┐
   ┌──────────────┐    ┌────────────────┐ │ Validation Script   │
   │ Read CSV     │───>│ Calculate      │>│ - Load both values  │
   │ (MQL5)       │    │ Laguerre_Python│ │ - Statistical tests │
   │              │    │ using same OHLC│ │ - Visual plots      │
   └──────────────┘    └────────────────┘ │ - Generate report   │
                                           └─────────────────────┘
                                                      │
                                                      v
3. Output:                                ┌─────────────────────┐
                                          │ Validation Report   │
                                          │ - Correlation       │
                                          │ - RMSE, MAE         │
                                          │ - Max error         │
                                          │ - Visual plots      │
                                          │ - Pass/Fail verdict │
                                          └─────────────────────┘
```

### Key Components

**Component 1: MQL5 Indicator Export Script**
- **Purpose**: Load ATR_Adaptive_Laguerre_RSI indicator and export buffer values
- **Method**: Use `iCustom()` to access indicator
- **Output**: CSV with Time, OHLC, Volume, Laguerre_RSI_MQL5, Signal_MQL5, Adaptive_Period_MQL5, ATR_MQL5
- **File**: `Scripts/DataExport/ExportLaguerreRSI.mq5` (NEW)

**Component 2: Python Validation Script**
- **Purpose**: Read MQL5 export, calculate Python Laguerre RSI, compare results
- **Method**: Statistical analysis + visual validation
- **Output**: Validation report with metrics and plots
- **File**: `users/crossover/validate_laguerre_rsi.py` (NEW)

**Component 3: Validation Report Generator**
- **Purpose**: Generate comprehensive validation report
- **Format**: Markdown with embedded plots
- **Output**: `docs/reports/LAGUERRE_RSI_VALIDATION_REPORT.md`

---

## Validation Metrics

### Statistical Metrics

**1. Pearson Correlation Coefficient (r)**
- **Definition**: Measures linear correlation between two variables
- **Range**: -1.0 to +1.0
- **Target**: r ≥ 0.9999 (requirement: ≥ 0.999)
- **Formula**: r = cov(X,Y) / (σ_X * σ_Y)
- **Interpretation**:
  - 0.999 < r ≤ 1.000: Extremely strong correlation ✓
  - 0.990 < r ≤ 0.999: Very strong correlation (acceptable with justification)
  - r ≤ 0.990: Weak correlation ❌

**2. Spearman Rank Correlation (ρ)**
- **Definition**: Measures monotonic relationship (non-parametric)
- **Range**: -1.0 to +1.0
- **Target**: ρ ≥ 0.9999
- **Use Case**: Validates consistent ordering of values

**3. Root Mean Square Error (RMSE)**
- **Definition**: Square root of average squared differences
- **Range**: 0.0 to ∞
- **Target**: RMSE < 0.0001 (0.01% of typical RSI range 0-1)
- **Formula**: RMSE = √(Σ(y_mql5 - y_python)² / n)
- **Interpretation**:
  - RMSE < 0.0001: Excellent match ✓
  - 0.0001 ≤ RMSE < 0.001: Good match (acceptable)
  - RMSE ≥ 0.001: Poor match ❌

**4. Mean Absolute Error (MAE)**
- **Definition**: Average absolute difference
- **Range**: 0.0 to ∞
- **Target**: MAE < 0.0001
- **Formula**: MAE = Σ|y_mql5 - y_python| / n
- **Interpretation**:
  - MAE < 0.0001: Excellent ✓
  - 0.0001 ≤ MAE < 0.001: Good (acceptable)
  - MAE ≥ 0.001: Poor ❌

**5. Maximum Absolute Error (Max Error)**
- **Definition**: Largest single difference
- **Range**: 0.0 to ∞
- **Target**: Max Error < 0.001 (0.1% of RSI range)
- **Formula**: Max Error = max(|y_mql5 - y_python|)
- **Interpretation**:
  - Max Error < 0.001: Excellent ✓
  - 0.001 ≤ Max Error < 0.01: Good (acceptable)
  - Max Error ≥ 0.01: Poor ❌

**6. R² (Coefficient of Determination)**
- **Definition**: Proportion of variance explained
- **Range**: 0.0 to 1.0
- **Target**: R² ≥ 0.9998
- **Formula**: R² = 1 - (SS_res / SS_tot)
- **Interpretation**:
  - R² ≥ 0.9998: Excellent ✓
  - 0.9990 ≤ R² < 0.9998: Good (acceptable)
  - R² < 0.9990: Poor ❌

### Warmup Period Analysis

**Challenge**: First N bars may differ due to initialization

**Solution**: Analyze error distribution vs bar index

**Metrics**:
- Correlation excluding first 50 bars
- Correlation excluding first 100 bars
- Identify optimal warmup period

**Expected Behavior**: Error should decrease after warmup period

### Edge Case Validation

**Test Cases**:
1. **First Bar**: TR = high - low (no previous close)
2. **Early Bars** (i < atr_period): Partial ATR calculation
3. **Zero Volatility**: ATR min == ATR max (coefficient = 0.5)
4. **Extreme Volatility**: ATR at maximum (coefficient = 0.0)
5. **Division by Zero**: totalMovement == 0 (return 0.5 or 0.0)

---

## Implementation Plan

### Phase 1: MQL5 Export Script (2-3 hours)

**Task 1.1**: Create LaguerreRSIModule.mqh
- Location: `Include/DataExport/modules/LaguerreRSIModule.mqh`
- Function: `LaguerreRSIModule_Load()`
- Uses: `iCustom()` to load indicator
- Reads: Buffer 0 (main RSI values)
- Returns: `IndicatorColumn` with Laguerre RSI values

**Task 1.2**: Create ExportLaguerreRSI.mq5
- Location: `Scripts/DataExport/ExportLaguerreRSI.mq5`
- Inputs: Symbol, Timeframe, Bars, ATR Period, Price Smooth Period, Price Smooth Method
- Process: Load OHLC + call LaguerreRSIModule_Load() + export CSV
- Output: `Export_{Symbol}_{Timeframe}_LaguerreRSI_MQL5.csv`

**Task 1.3**: Compile and Test
- Compile via CLI or GUI
- Test on EURUSD M1 100 bars
- Verify CSV output contains expected columns

### Phase 2: Python Validation Script (3-4 hours)

**Task 2.1**: Create validate_laguerre_rsi.py
- Location: `users/crossover/validate_laguerre_rsi.py`
- Functions:
  - `load_mql5_export(csv_path)` - Load MQL5 CSV
  - `calculate_python_laguerre(df, params)` - Calculate Python version
  - `calculate_correlation(mql5, python)` - Pearson + Spearman
  - `calculate_errors(mql5, python)` - RMSE, MAE, Max Error
  - `plot_comparison(mql5, python, output_path)` - Visual plots
  - `plot_residuals(mql5, python, output_path)` - Error analysis
  - `generate_report(metrics, output_path)` - Markdown report

**Task 2.2**: Statistical Analysis Module
- Warmup period detection (auto-detect optimal cutoff)
- Edge case identification (first bar, zero volatility, etc.)
- Parameter sensitivity analysis (optional)

**Task 2.3**: Visualization Module
- Overlay plot (MQL5 vs Python)
- Difference plot (residuals over time)
- Scatter plot (correlation)
- Histogram (error distribution)
- Q-Q plot (normality check of residuals)

### Phase 3: Validation Execution (1-2 hours)

**Test Scenario 1: Baseline Validation**
- Symbol: EURUSD
- Timeframe: M1
- Bars: 1000
- Parameters: Default (atr_period=32, smooth_period=5, smooth_method=EMA)

**Test Scenario 2: High Volatility**
- Symbol: XAUUSD (Gold)
- Timeframe: M1
- Bars: 1000
- Parameters: Default

**Test Scenario 3: Low Volatility**
- Symbol: EURUSD
- Timeframe: D1 (daily)
- Bars: 500
- Parameters: Default

**Test Scenario 4: Parameter Sensitivity**
- Symbol: EURUSD
- Timeframe: M1
- Bars: 1000
- Test ATR periods: 14, 32, 50, 100
- Test smooth methods: SMA, EMA, SMMA, LWMA

### Phase 4: Report Generation (1 hour)

**Deliverables**:
1. `LAGUERRE_RSI_VALIDATION_REPORT.md` - Main validation report
2. `validation_plots/` - Directory with all plots
3. `validation_data/` - Raw CSV files and intermediate results
4. Update `CLAUDE.md` with validation status

---

## Test Scenarios

### Scenario 1: Baseline Validation (EURUSD M1)

**Purpose**: Establish baseline correlation

**Parameters**:
- Symbol: EURUSD
- Timeframe: M1
- Bars: 1000
- ATR Period: 32
- Price Smooth Period: 5
- Price Smooth Method: EMA

**Expected Results**:
- Correlation: r ≥ 0.9999
- RMSE: < 0.0001
- MAE: < 0.0001
- Max Error: < 0.001

**Pass Criteria**: All metrics within target thresholds

### Scenario 2: High Volatility (XAUUSD M1)

**Purpose**: Test behavior in volatile markets

**Parameters**:
- Symbol: XAUUSD (Gold)
- Timeframe: M1
- Bars: 1000
- ATR Period: 32
- Price Smooth Period: 5
- Price Smooth Method: EMA

**Expected Results**:
- Correlation: r ≥ 0.9999
- RMSE: < 0.0001
- Max Error: < 0.001
- Adaptive Period: Wide range (24-56)

**Pass Criteria**: Metrics maintained despite high volatility

### Scenario 3: Low Volatility (EURUSD D1)

**Purpose**: Test behavior in quiet markets

**Parameters**:
- Symbol: EURUSD
- Timeframe: D1 (daily)
- Bars: 500
- ATR Period: 32
- Price Smooth Period: 5
- Price Smooth Method: EMA

**Expected Results**:
- Correlation: r ≥ 0.9999
- RMSE: < 0.0001
- Adaptive Period: Narrow range (near maximum)

**Pass Criteria**: Metrics maintained in low volatility

### Scenario 4: Parameter Sweep

**Purpose**: Validate across parameter space

**Test Matrix**:
```
ATR Periods: [14, 32, 50, 100]
Smooth Methods: [SMA, EMA, SMMA, LWMA]
Smooth Periods: [1, 5, 10]
Total: 4 × 4 × 3 = 48 combinations
```

**Subset for Initial Validation** (reduce to 8 combinations):
- ATR=32, Methods=[SMA, EMA, SMMA, LWMA], Period=5 (4 tests)
- ATR=[14, 50, 100], Method=EMA, Period=5 (3 tests)
- ATR=32, Method=EMA, Period=[1, 10] (2 tests - 1 already tested above)

**Expected Results**:
- All combinations: r ≥ 0.999
- Majority: r ≥ 0.9999

**Pass Criteria**: 100% of combinations pass correlation threshold

### Scenario 5: Edge Cases

**Test 5.1: Zero Volatility**
- Construct synthetic data with constant price
- Expected: coefficient = 0.5, RSI stable

**Test 5.2: First Bar**
- Validate TR calculation without previous close
- Expected: TR = high - low

**Test 5.3: Short Data**
- Test with bars < atr_period
- Expected: Graceful handling, partial calculations

---

## Acceptance Criteria

### Primary Criteria (MUST PASS)

**PC-1: Baseline Correlation**
- ✓ Pearson correlation r ≥ 0.999 on EURUSD M1 1000 bars
- ✓ Default parameters (atr=32, smooth=EMA(5))

**PC-2: Statistical Significance**
- ✓ RMSE < 0.0001
- ✓ MAE < 0.0001
- ✓ Max Error < 0.001

**PC-3: Multi-Symbol Validation**
- ✓ Pass on at least 2 different symbols (EURUSD + XAUUSD)

**PC-4: Multi-Timeframe Validation**
- ✓ Pass on at least 2 different timeframes (M1 + D1)

### Secondary Criteria (SHOULD PASS)

**SC-1: Enhanced Correlation**
- ✓ Pearson correlation r ≥ 0.9999 (exceeding requirement)

**SC-2: Parameter Robustness**
- ✓ Pass all 4 smoothing methods (SMA/EMA/SMMA/LWMA)
- ✓ Pass at least 3 ATR periods (14/32/50)

**SC-3: Warmup Period**
- ✓ Identify optimal warmup period (expected: 50-100 bars)
- ✓ Correlation improves after warmup

**SC-4: Visual Validation**
- ✓ Overlay plots show indistinguishable lines
- ✓ Residual plots show random noise (no systematic bias)

### Failure Criteria (AUTO-FAIL)

**FC-1: Low Correlation**
- ❌ r < 0.999 on baseline validation

**FC-2: High Error**
- ❌ RMSE ≥ 0.001 (10x threshold)

**FC-3: Systematic Bias**
- ❌ Residual plots show trend or pattern

**FC-4: Edge Case Failure**
- ❌ Crashes or NaN values on valid input

---

## Timeline and Deliverables

### Estimated Timeline: 8-10 hours total

**Phase 1: MQL5 Export Script (2-3 hours)**
- Create LaguerreRSIModule.mqh
- Create ExportLaguerreRSI.mq5
- Compile and test

**Phase 2: Python Validation Script (3-4 hours)**
- Create validate_laguerre_rsi.py
- Implement statistical analysis
- Implement visualization

**Phase 3: Validation Execution (1-2 hours)**
- Run 4 test scenarios
- Collect results
- Analyze edge cases

**Phase 4: Report Generation (1 hour)**
- Generate plots
- Write validation report
- Update project documentation

**Contingency Buffer (1 hour)**
- Debug issues
- Rerun failed tests
- Additional analysis if needed

### Deliverables

**Code Deliverables**:
1. `Include/DataExport/modules/LaguerreRSIModule.mqh` - MQL5 indicator loading module
2. `Scripts/DataExport/ExportLaguerreRSI.mq5` - MQL5 export script
3. `users/crossover/validate_laguerre_rsi.py` - Python validation script

**Data Deliverables**:
4. `validation_data/Export_EURUSD_M1_LaguerreRSI_MQL5.csv` - MQL5 export
5. `validation_data/Export_XAUUSD_M1_LaguerreRSI_MQL5.csv` - High volatility test
6. `validation_data/Export_EURUSD_D1_LaguerreRSI_MQL5.csv` - Low volatility test

**Visualization Deliverables**:
7. `validation_plots/overlay_plot.png` - MQL5 vs Python overlay
8. `validation_plots/residuals_plot.png` - Error over time
9. `validation_plots/scatter_plot.png` - Correlation scatter
10. `validation_plots/histogram_plot.png` - Error distribution
11. `validation_plots/qq_plot.png` - Normality check

**Documentation Deliverables**:
12. `docs/reports/LAGUERRE_RSI_VALIDATION_REPORT.md` - Main report
13. Update `CLAUDE.md` with validation status
14. Update `docs/guides/LAGUERRE_RSI_ANALYSIS.md` with validation reference

---

## Risk Assessment

### Technical Risks

**Risk 1: Floating Point Precision**
- **Probability**: High
- **Impact**: Low
- **Mitigation**: Use `np.isclose()` with appropriate tolerances (rtol=1e-5, atol=1e-8)

**Risk 2: Array Indexing Direction**
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Carefully verify MQL5 series indexing (oldest=0) vs Python (oldest=0)

**Risk 3: Initial Bar Differences**
- **Probability**: High
- **Impact**: Low
- **Mitigation**: Exclude warmup period from correlation calculation

**Risk 4: MA Method Implementation**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Test each MA method independently (SMA/EMA/SMMA/LWMA)

**Risk 5: iCustom() Parameter Mismatch**
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Explicitly verify indicator parameters match Python implementation

### Schedule Risks

**Risk 6: Compilation Failures**
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Use proven CLI compilation workflow, simple file paths

**Risk 7: Data Export Issues**
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Reuse existing DataExport infrastructure

**Risk 8: Visualization Complexity**
- **Probability**: Low
- **Impact**: Low
- **Mitigation**: Use matplotlib with simple plot types

---

## Success Criteria Summary

**Validation PASSES if**:
- ✅ Pearson correlation r ≥ 0.999 on baseline test
- ✅ RMSE < 0.0001 on baseline test
- ✅ Max Error < 0.001 on baseline test
- ✅ Multi-symbol validation passes (2+ symbols)
- ✅ Multi-timeframe validation passes (2+ timeframes)
- ✅ All edge cases handled gracefully (no crashes, no NaN)

**Validation is EXCEPTIONAL if**:
- ⭐ Pearson correlation r ≥ 0.9999 (exceeds requirement)
- ⭐ RMSE < 0.00001 (10x better than threshold)
- ⭐ All smoothing methods pass (SMA/EMA/SMMA/LWMA)
- ⭐ Residuals show pure random noise (visual inspection)

**Validation FAILS if**:
- ❌ Correlation r < 0.999 on any primary test
- ❌ RMSE ≥ 0.001 on baseline test
- ❌ Systematic bias detected in residuals
- ❌ Edge cases produce NaN or crash

---

## Next Steps

**Immediate** (Start validation implementation):
1. Create `Include/DataExport/modules/LaguerreRSIModule.mqh`
2. Create `Scripts/DataExport/ExportLaguerreRSI.mq5`
3. Compile and test MQL5 export on EURUSD M1 100 bars

**Short-term** (Within 1 day):
4. Create `users/crossover/validate_laguerre_rsi.py`
5. Run baseline validation (EURUSD M1 1000 bars)
6. Generate initial validation report

**Medium-term** (Within 2 days):
7. Run full test suite (4 scenarios)
8. Generate comprehensive validation report
9. Update project documentation

---

## References

- **MQL5 Indicator**: `PythonInterop/ATR_Adaptive_Laguerre_RSI.mq5`
- **Python Implementation**: `users/crossover/indicators/laguerre_rsi.py`
- **Export Script**: `users/crossover/export_aligned.py`
- **Algorithm Analysis**: `docs/guides/LAGUERRE_RSI_ANALYSIS.md`
- **Temporal Audit**: `docs/guides/LAGUERRE_RSI_TEMPORAL_AUDIT.md`
- **Bug Fix Summary**: `docs/guides/LAGUERRE_RSI_BUG_FIX_SUMMARY.md`
