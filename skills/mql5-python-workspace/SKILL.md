# MQL5→Python Translation Workspace Skill

**Version**: 1.0.0
**Project**: mql5-crossover (CrossOver Bottle MT5 + Python Validation)
**Purpose**: Seamless MQL5 indicator translation to Python with autonomous validation and self-correction

---

## When to Use This Skill

Use this skill when the user wants to:

- Export market data or indicator values from MetaTrader 5
- Translate MQL5 indicators to Python implementations
- Validate Python indicator accuracy against MQL5 reference
- Understand MQL5→Python workflow capabilities and limitations
- Troubleshoot common translation issues

**Activation Phrases**: "MQL5", "MetaTrader", "indicator translation", "Python validation", "export data", "mql5-crossover workspace"

---

## Core Mission

**Main Theme**: Make MQL5→Python translation **as seamless as possible** through:

1. **Autonomous workflows** (headless export, CLI compilation, automated validation)
2. **Validation-driven iteration** (≥0.999 correlation gates all work)
3. **Self-correction** (documented failures prevent future mistakes)
4. **Clear boundaries** (what works vs what doesn't, with alternatives)

**Project Root**: `/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c`

---

## Workspace Capabilities Matrix

### ✅ WHAT THIS WORKSPACE **CAN DO**

#### 1. Automated Headless Market Data Export (v3.0.0)

**Status**: ✅ PRODUCTION (0.999920 correlation validated)

**What It Does**:

- Fetches OHLCV data + built-in indicators (RSI, SMA) from any symbol/timeframe
- True headless via Wine Python + MetaTrader5 API
- No GUI initialization required (cold start supported)
- Execution time: 6-8 seconds for 5000 bars

**Command Example**:

```bash
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\export_aligned.py" \
  --symbol EURUSD --period M1 --bars 5000
```

**Use When**: User needs automated market data exports without GUI interaction

**Limitations**: Cannot access custom indicator buffers (API restriction)

**Reference**: `/docs/guides/WINE_PYTHON_EXECUTION.md`

---

#### 2. GUI-Based Custom Indicator Export (v4.0.0)

**Status**: ✅ PRODUCTION (file-based config system complete)

**What It Does**:

- Exports custom indicator values via file-based configuration
- 13 configurable parameters (symbol, timeframe, bars, indicator flags)
- Flexible parameter changes without code editing
- Execution time: 20-30 seconds (manual drag-and-drop required)

**Workflow**:

```bash
# Step 1: Generate config
python generate_export_config.py \
  --symbol EURUSD --timeframe M1 --bars 5000 \
  --laguerre-rsi --output custom_export.txt

# Step 2: Drag ExportAligned.ex5 to chart in MT5 GUI, click OK
# Step 3: CSV exported to MQL5/Files/
```

**Use When**: User needs custom indicator values (Laguerre RSI, proprietary indicators)

**Limitations**: Requires GUI interaction (not fully headless)

**Reference**: `/docs/guides/V4_FILE_BASED_CONFIG_WORKFLOW.md`

---

#### 3. Rigorous Validation Framework

**Status**: ✅ PRODUCTION (1.000000 correlation achieved for Laguerre RSI)

**What It Does**:

- Validates Python implementations against MQL5 reference exports
- Calculates 4 metrics: Pearson correlation, MAE, RMSE, max difference
- Stores historical validation runs in DuckDB for regression detection
- 32-test comprehensive suite (P0-P3 priorities)

**Quality Gates**:

- **Correlation**: MUST be ≥0.999 (not 0.95 "good enough")
- **MAE**: MUST be <0.001
- **NaN Count**: MUST be 0 (after warmup period)
- **Historical Warmup**: MUST use 5000+ bars for adaptive indicators

**Command Example**:

```bash
python validate_indicator.py \
  --csv Export_EURUSD_PERIOD_M1.csv \
  --indicator laguerre_rsi \
  --threshold 0.999
```

**Use When**: User needs to verify Python indicator accuracy

**Critical Requirement**: 5000-bar warmup (NOT 100 or 500 bars)

**Reference**: `/docs/guides/INDICATOR_VALIDATION_METHODOLOGY.md`

---

#### 4. Complete MQL5→Python Migration Workflow (7 Phases)

**Status**: ✅ PRODUCTION (2-4 hours first time, 1-2 hours subsequently)

**What It Does**:

- Phase 1: Locate & analyze MQL5 indicator (40% automated)
- Phase 2: Modify MQL5 to expose buffers (30% automated)
- Phase 3: CLI compile (~1 second, 90% automated)
- Phase 4: Fetch historical data (95% automated)
- Phase 5: Implement Python indicator (20% automated)
- Phase 6: Validate with warmup (95% automated)
- Phase 7: Document lessons (40% automated)

**Overall Automation**: 60-70% (strategic automation at integration points)

**Self-Correction Mechanisms**:

1. Validation-driven re-implementation loop (correlation threshold)
2. Multi-level compilation verification (4 checks)
3. Wine Python MT5 API error handling (actionable messages)
4. DuckDB historical tracking (regression detection)
5. Comprehensive test suite (32 automated tests)

**Use When**: User wants to migrate a complete indicator from MQL5 to Python

**Time Investment**: 2-4 hours first indicator, faster for subsequent indicators

**Reference**: `/docs/guides/MQL5_TO_PYTHON_MIGRATION_GUIDE.md`

---

#### 5. Lessons Learned Knowledge Base (185+ Hours Captured)

**Status**: ✅ COMPREHENSIVE (8 critical gotchas, 6 validation pitfalls)

**What It Contains**:

- **8 Critical Gotchas**: /inc parameter trap, path spaces, warmup requirement, pandas mismatches, array indexing, shared state, parameter passing, temporal assumptions
- **6 Validation Pitfalls**: Cold start comparison, pandas rolling windows, off-by-one errors, series vs iloc, NaN handling, correlation thresholds
- **70+ Legacy Items**: Documented as NOT VIABLE to prevent retesting
- **Time Savings**: 30-50 hours per developer by reading first

**Use When**: User encounters a bug or wants to avoid common mistakes

**Critical Reading**: `/docs/guides/LESSONS_LEARNED_PLAYBOOK.md` (read BEFORE starting work)

**Reference**: `/docs/guides/LESSONS_LEARNED_PLAYBOOK.md`

---

### ❌ WHAT THIS WORKSPACE **CANNOT DO**

#### 1. Custom Indicator Headless Automation

**Limitation**: Python MetaTrader5 API cannot access custom indicator buffers

**Why**: API design limitation - no `copy_buffer()` function for custom indicators

**Evidence**:

- `/archive/experiments/spike_1_mt5_indicator_access.py` (confirmed via testing)
- Official MetaQuotes statement: "Python API unable to access indicators"

**Alternative**:

- Use v4.0.0 GUI mode for custom indicator exports
- OR reimplement indicator logic in Python directly

**Time Saved by Knowing**: 2+ hours (don't waste time trying API approach)

**Reference**: `/docs/guides/EXTERNAL_RESEARCH_BREAKTHROUGHS.md` (Research B)

---

#### 2. Reliable Startup.ini Parameter Passing

**Limitation**: MT5 does NOT support named sections or ScriptParameters reliably

**Why**: Fundamental MT5 bugs documented in 30+ community sources (2015-2025)

**Failed Approaches** (v2.1.0 - ALL NOT VIABLE):

1. Named sections `[ScriptName]` - ignored by MT5
2. ScriptParameters directive - blocks execution silently
3. .set preset files - strict requirements + silent failures

**Evidence**:

- `/archive/plans/HEADLESS_MQL5_SCRIPT_SOLUTION_A.NOT_VIABLE.md` (22 KB research)
- Full day of testing, comprehensive community research

**Alternative**:

- Use v3.0.0 Python API (no startup.ini needed)
- OR use v4.0.0 file-based config (MQL5/Files/export_config.txt)

**Time Saved by Knowing**: 6-8 hours (approach is research-confirmed broken)

**Reference**: `/docs/guides/SCRIPT_PARAMETER_PASSING_RESEARCH.md`

---

#### 3. Pandas Rolling Windows for MQL5 ATR

**Limitation**: Pandas `rolling().mean()` does NOT match MQL5 expanding window behavior

**Why**: Different denominator logic

- MQL5: `sum(bars 0-5) / 32` (divide by period, even if partial)
- Pandas: `sum(bars 0-5) / 6` (divide by available bars)

**Impact**: 0.95 correlation (FAILED validation) instead of 1.000000

**Required Fix**: Manual loops (10x slower, but correct)

```python
for i in range(len(tr)):
    if i < period:
        atr.iloc[i] = tr.iloc[:i+1].sum() / period  # NOT pandas rolling
    else:
        atr.iloc[i] = tr.iloc[i-period+1:i+1].mean()
```

**Project Philosophy**: "Correctness > Speed for validation"

**Time Saved by Knowing**: 30-45 minutes debugging NaN values

**Reference**: `/docs/guides/LESSONS_LEARNED_PLAYBOOK.md` (Gotcha #4)

---

#### 4. Cold Start Validation (<5000 Bars)

**Limitation**: Cannot validate adaptive indicators without sufficient historical warmup

**Why**: ATR requires 32-bar lookback, Adaptive Period requires 64-bar warmup

**Evidence**:

- 100 bars → 0.951 correlation (FAILED)
- 5000 bars → 1.000000 correlation (PASSED)

**Mental Model**:

```
MQL5: [....4900 bars warmup....][100 bars exported]
Python: [100 bars CSV] ← ZERO context (WRONG!)

Correct: Fetch 5000, calculate on ALL, compare last N
```

**Required Workflow**: Two-stage validation (fetch 5000, calculate all, compare subset)

**Time Saved by Knowing**: 2-3 hours debugging correlation failures

**Reference**: `/docs/guides/PYTHON_INDICATOR_VALIDATION_FAILURES.md` (Failure #5)

---

#### 5. Accept 0.95 Correlation as "Good Enough"

**Limitation**: 0.95 correlation indicates systematic bias, NOT "95% accurate"

**Why**: Small errors compound in live trading

**Production Requirement**: ≥0.999 (99.9% minimum)

**Diagnostic Pattern**:

- 0.95-0.97: Missing historical warmup
- 0.85-0.95: NaN handling mismatch
- 0.70-0.85: Algorithm mismatch
- <0.70: Fundamental implementation error

**Time Saved by Knowing**: Don't waste time on "good enough" - fix the root cause

**Reference**: `/docs/guides/LESSONS_LEARNED_PLAYBOOK.md` (Bug Pattern #1)

---

#### 6. Wine/CrossOver Compilation with Spaces in Paths

**Limitation**: Paths with spaces break Wine compilation SILENTLY

**Symptom**: Exit code 0 (success!) but NO .ex5 file created

**Required Workflow**: Copy-Compile-Verify-Move (4 steps)

```bash
# Step 1: Copy to simple path
cp "Complex (Name).mq5" "C:/Temp.mq5"

# Step 2: Compile
metaeditor64.exe /compile:"C:/Temp.mq5"

# Step 3: Verify (.ex5 exists AND log shows 0 errors)
ls -lh "C:/Temp.ex5"

# Step 4: Move to destination
cp "C:/Temp.ex5" "C:/Program Files/.../Script.ex5"
```

**Time Saved by Knowing**: 3+ hours debugging silent failures

**Reference**: `/docs/guides/LESSONS_LEARNED_PLAYBOOK.md` (Gotcha #2)

---

#### 7. Use `/inc` Parameter for Standard Compilation

**Limitation**: `/inc` parameter OVERRIDES (not augments) default include paths

**Common Mistake**:

```bash
# WRONG (causes 102 errors):
metaeditor64.exe /compile:"C:/Program Files/MT5/MQL5/Scripts/Script.mq5" \
  /inc:"C:/Program Files/MT5/MQL5"  # Redundant + breaks

# RIGHT (no /inc needed):
metaeditor64.exe /compile:"C:/Program Files/MT5/MQL5/Scripts/Script.mq5"
```

**When to Actually Use `/inc`**: ONLY when compiling from EXTERNAL directory

**Time Saved by Knowing**: 4+ hours debugging compilation errors

**Reference**: `/docs/guides/EXTERNAL_RESEARCH_BREAKTHROUGHS.md` (Research A)

---

## Critical Requirements & Assumptions

### User MUST Assume:

1. ✅ **MT5 Terminal Running**: API approaches require logged-in terminal
2. ✅ **Wine/CrossOver Installed**: No native macOS MT5 support
3. ✅ **Python 3.12+ in Wine**: Required for MetaTrader5 package
4. ✅ **NumPy 1.26.4**: MUST use this version (not 2.x - Wine incompatible)
5. ✅ **5000+ Bar Warmup**: Required for validation (not 100 or 500 bars)
6. ✅ **Manual Loops for ATR**: Cannot use pandas rolling windows
7. ✅ **≥0.999 Correlation**: Strict threshold (not 0.95 "good enough")
8. ✅ **Copy-Compile-Move**: Required for paths with spaces in Wine

### User Must NOT Assume:

1. ❌ startup.ini parameter passing works reliably
2. ❌ Python API can access custom indicator buffers
3. ❌ Pandas operations match MQL5 behavior automatically
4. ❌ 0.95 correlation is "good enough"
5. ❌ 100 bars is sufficient for validation
6. ❌ `/inc` parameter helps with standard compilation
7. ❌ Paths with spaces work in Wine compilation
8. ❌ NumPy 2.x works with MetaTrader5 package

---

## Common User Workflows

### 1. Quick Market Data Export (Beginner - 10-15 seconds)

**Use Case**: User wants EURUSD M1 data with RSI

**Workflow**:

```bash
# One-liner (v3.0.0 headless)
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\export_aligned.py" \
  --symbol EURUSD --period M1 --bars 5000
```

**Output**: CSV with OHLCV + RSI_14 at `users/crossover/exports/`

**Reference**: `/docs/guides/V4_FILE_BASED_CONFIG_WORKFLOW.md` (Quick Start)

---

### 2. Custom Laguerre RSI Export (Intermediate - 20-30 seconds)

**Use Case**: User wants Laguerre RSI indicator values

**Workflow**:

```bash
# Step 1: Generate config
python generate_export_config.py --symbol XAUUSD --timeframe M1 \
  --bars 5000 --laguerre-rsi --output laguerre_export.txt

# Step 2: Open MT5 GUI, drag ExportAligned.ex5 to XAUUSD M1 chart, click OK

# Step 3: CSV at MQL5/Files/Export_XAUUSD_M1_Laguerre.csv
```

**Output**: CSV with OHLCV + Laguerre_RSI + ATR + Adaptive_Period

**Reference**: `/docs/guides/V4_FILE_BASED_CONFIG_WORKFLOW.md` (Example 3)

---

### 3. Validate Python Indicator (Intermediate - 5-10 minutes)

**Use Case**: User wrote Python Laguerre RSI, needs to verify accuracy

**Workflow**:

```bash
# Step 1: Fetch 5000 bars from MT5 (v3.0.0 OR v4.0.0)

# Step 2: Calculate Python indicator on ALL 5000 bars

# Step 3: Validate
python validate_indicator.py \
  --csv Export_EURUSD_PERIOD_M1.csv \
  --indicator laguerre_rsi \
  --threshold 0.999

# Output:
# [PASS] Laguerre_RSI: correlation=1.000000
# [PASS] ATR: correlation=0.999987
# Status: PASS - All buffers meet threshold
```

**Success Criteria**: All buffers ≥0.999 correlation

**Reference**: `/docs/guides/INDICATOR_VALIDATION_METHODOLOGY.md`

---

### 4. Complete Indicator Migration (Advanced - 2-4 hours)

**Use Case**: User wants to translate new MQL5 indicator to Python

**Workflow**: 7-phase checklist-driven process

**Checklist**: `/docs/templates/INDICATOR_MIGRATION_CHECKLIST.md` (copy-paste ready)

**Key Phases**:

1. Locate & analyze (bash commands + manual review)
2. Modify MQL5 (expose hidden buffers)
3. CLI compile (~1 second)
4. Fetch 5000 bars (automated)
5. Implement Python (manual + pandas patterns)
6. Validate ≥0.999 (automated)
7. Document lessons (manual + git)

**Time Investment**: 2-4 hours first time, 1-2 hours subsequently

**Reference**: `/docs/guides/MQL5_TO_PYTHON_MIGRATION_GUIDE.md`

---

## Documentation Hub (Single Source of Truth)

### Quick Start (35-45 minutes)

- **New Users**: `/docs/guides/MQL5_TO_PYTHON_MIGRATION_GUIDE.md` (7-phase workflow)
- **Critical Gotchas**: `/docs/guides/LESSONS_LEARNED_PLAYBOOK.md` (read FIRST)
- **Copy-Paste Checklist**: `/docs/templates/INDICATOR_MIGRATION_CHECKLIST.md`

### Execution Workflows

- **Headless Export**: `/docs/guides/WINE_PYTHON_EXECUTION.md` (v3.0.0)
- **GUI Export**: `/docs/guides/V4_FILE_BASED_CONFIG_WORKFLOW.md` (v4.0.0)
- **Validation**: `/docs/guides/INDICATOR_VALIDATION_METHODOLOGY.md`

### Critical References

- **Lessons Learned**: `/docs/guides/LESSONS_LEARNED_PLAYBOOK.md` (8 gotchas)
- **Validation Failures**: `/docs/guides/PYTHON_INDICATOR_VALIDATION_FAILURES.md` (3-hour journey)
- **External Research**: `/docs/guides/EXTERNAL_RESEARCH_BREAKTHROUGHS.md` (game-changers)
- **Legacy Assessment**: `/docs/reports/LEGACY_CODE_ASSESSMENT.md` (what NOT to retry)

### Architecture & Tools

- **Environment Setup**: `/docs/guides/CROSSOVER_MQ5.md` (Wine/CrossOver)
- **File Locations**: `/docs/guides/MT5_FILE_LOCATIONS.md` (paths reference)
- **CLI Compilation**: `/docs/guides/MQL5_CLI_COMPILATION_SUCCESS.md` (~1s compile)

### Navigation

- **Task Navigator**: `/docs/MT5_REFERENCE_HUB.md` (decision trees, canonical map)
- **Project Memory**: `/CLAUDE.md` (hub-and-spoke architecture)
- **Documentation Index**: `/docs/README.md` (complete guide catalog)

---

## Skill Activation Guidelines

### When to Activate This Skill

Activate when user mentions:

- "MQL5" or "MetaTrader 5" or "MT5"
- "indicator translation" or "export data"
- "Python validation" or "correlation check"
- "CrossOver bottle" or "Wine Python"
- "Laguerre RSI", "ATR", "technical indicators"
- File paths containing `MetaTrader 5/drive_c`

### How to Guide Users

**1. Understand Intent First**

- What do they want to export? (market data vs custom indicator)
- What's their experience level? (beginner vs advanced)
- What's their time constraint? (quick export vs full migration)

**2. Recommend Appropriate Workflow**

- Headless automation → v3.0.0 (built-in indicators only)
- Custom indicators → v4.0.0 (GUI mode)
- Validation → Universal framework (≥0.999 threshold)
- Full migration → 7-phase workflow (2-4 hours)

**3. Set Clear Expectations**

- What CAN be done (with confidence)
- What CANNOT be done (with alternatives)
- Time investment (realistic estimates)
- Quality gates (≥0.999 correlation non-negotiable)

**4. Prevent Common Mistakes**

- Read Lessons Learned Playbook FIRST (saves 8-12 hours)
- Use 5000 bars for validation (not 100 or 500)
- Don't retry NOT VIABLE approaches (30-50 hours saved)
- Respect "Correctness > Speed" philosophy

**5. Reference Documentation Frequently**

- This workspace has 95/100 documentation readiness score
- Every failure documented with solutions
- Hub-and-spoke architecture (single source of truth per topic)

---

## Error Handling Patterns

### Common Errors & Solutions

**Error**: `correlation=0.951 (threshold 0.999) - FAILED`
**Diagnosis**: Missing historical warmup
**Solution**: Fetch 5000 bars, calculate on ALL, compare last N
**Time**: 2-3 hours if not known upfront

**Error**: `No module named 'MetaTrader5'`
**Diagnosis**: Running in macOS Python (not Wine Python)
**Solution**: Use Wine Python: `wine "C:\\...\\python.exe"`
**Time**: 5-10 minutes

**Error**: `Exit code 0 but no .ex5 file created`
**Diagnosis**: Path has spaces, Wine compilation silent failure
**Solution**: Copy-Compile-Verify-Move (4-step pattern)
**Time**: 3+ hours if not known upfront

**Error**: `102 compilation errors`
**Diagnosis**: `/inc` parameter overrides defaults
**Solution**: Remove `/inc` parameter entirely
**Time**: 4+ hours if not known upfront

**Error**: `99 NaN values in indicator output`
**Diagnosis**: Using pandas rolling windows (returns NaN until full window)
**Solution**: Use manual loops for expanding window logic
**Time**: 30-45 minutes

---

## Time Investment ROI

### Documentation Time Savings

| Knowledge Area           | Documentation   | Time Saved per Use |
| ------------------------ | --------------- | ------------------ |
| Lessons Learned Playbook | 8 gotchas       | 8-12 hours         |
| Legacy Assessment        | 70+ items       | 30-50 hours        |
| Validation Methodology   | 6 pitfalls      | 2-3 hours          |
| External Research        | 3 breakthroughs | 10-15 hours        |
| Migration Guide          | 7 phases        | 4-6 hours          |

**Total Time Invested**: 185+ hours (captured in documentation)
**Total Time Saved**: 50-100 hours per developer
**Break-Even Point**: After 2-3 indicators

---

## Success Metrics

### Validated Indicators (Production-Ready)

**Laguerre RSI v1.0.0**:

- ✅ Correlation: 1.000000 (all 3 buffers)
- ✅ Temporal leakage audit: CLEAN
- ✅ Documentation: Complete (analysis + validation + audit)
- ✅ Test coverage: Comprehensive validation suite
- **Status**: PRODUCTION READY

### Quality Standards

- **Correlation**: ≥0.999 (not 0.95)
- **MAE**: <0.001
- **NaN Count**: 0 (after warmup)
- **Historical Warmup**: 5000+ bars
- **Documentation**: Algorithm analysis + validation report + temporal audit

### Validation Runs

- **DuckDB Tracking**: All validation runs stored permanently
- **Regression Detection**: Historical comparison enabled
- **Bar-Level Debugging**: Top 100 largest differences stored
- **Reproducibility**: All parameters stored

---

## Version History

**v1.0.0** (2025-10-27)

- Initial skill creation based on 5-agent parallel research
- Comprehensive boundary definition (CAN vs CANNOT)
- 7-phase workflow documentation
- 185+ hours of debugging captured
- Production-ready validation framework (1.000000 correlation)

---

## Skill Maintenance

### When to Update This Skill

- New indicator validated (add to production-ready list)
- New NOT VIABLE approach discovered (add to limitations)
- New gotcha documented (add to lessons learned reference)
- Workflow optimization (update automation percentages)

### Health Check

Run comprehensive validation suite:

```bash
python comprehensive_validation.py --priority ALL --verbose
```

**Target**: 30/32 PASS (2 expected failures: duckdb/numpy missing in macOS Python)

---

**Skill Status**: ✅ PRODUCTION READY
**Last Updated**: 2025-10-27
**Maintenance**: Update when new indicators validated or limitations discovered
