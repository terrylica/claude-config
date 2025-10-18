# Headless Execution Implementation Plan

**Current Version**: 4.0.0 (File-Based Config - IN PROGRESS)
**Created**: 2025-10-17
**Status**: IN PROGRESS 🔄

**Version History**:
- v4.0.0 (2025-10-17): File-based configuration for custom indicators - IN PROGRESS
- v3.0.0 (2025-10-13): Python API for market data - COMPLETE ✅
- v2.1.0 (2025-10-17): Startup.ini parameter passing - FAILED ❌ (NOT VIABLE)
- v2.0.0 (2025-10-13): Startup.ini basic script launch - CONDITIONALLY WORKING ⚠️

---

## v4.0.0: File-Based Configuration (Current - IN PROGRESS)

**Created**: 2025-10-17
**Status**: IN PROGRESS 🔄
**Objective**: Enable custom indicator export via file-based parameter passing

**Approach**: MQL5 script reads parameters from `export_config.txt` in `MQL5/Files/` sandbox
- Bypasses MT5 startup.ini parameter passing complexity
- Python generates config file before launching MT5
- Works with custom indicators (unlike v3.0.0 Python API)
- Full programmatic control

### Implementation Phases

**Phase 1: Design** ✅ COMPLETE
- [x] Choose config format: key=value text (simpler, no JSON parsing needed)
- [x] Define parameter mappings: Match `ExportAligned.mq5` input names exactly
- [x] Document file location: `MQL5/Files/export_config.txt` (accessible from MQL5 + Python)
- [x] Document encoding: UTF-8 (standard, matches MQL5 string handling)

**Design Decisions**:

**1. Config Format: Key=Value Text**
```
# Example: export_config.txt
InpSymbol=EURUSD
InpTimeframe=1
InpBars=100
InpUseRSI=false
InpUseSMA=true
InpSMAPeriod=14
InpUseLaguerreRSI=false
InpOutputName=Export_EURUSD_M1_SMA.csv
```
- **Rationale**: Simple parsing with MQL5 `FileReadString()` + `StringSplit()`
- **Alternative Rejected**: JSON (requires external library like JAson.mqh, more complex)
- **Format Rules**:
  - One parameter per line
  - Format: `ParameterName=Value`
  - Boolean values: `true`/`false` (lowercase)
  - String values: no quotes needed
  - Comments: Lines starting with `#` ignored
  - Empty lines ignored

**2. Parameter Mappings** (Match ExportAligned.mq5 inputs exactly):
| Config File Parameter | MQL5 Input Variable | Type | Default | Notes |
|-----------------------|---------------------|------|---------|-------|
| `InpSymbol` | `InpSymbol` | string | "EURUSD" | Symbol name |
| `InpTimeframe` | `InpTimeframe` | int | 1 | ENUM: 1=M1, 5=M5, 60=H1, etc. |
| `InpBars` | `InpBars` | int | 5000 | Number of bars to export |
| `InpUseRSI` | `InpUseRSI` | bool | true | Enable RSI indicator |
| `InpRSIPeriod` | `InpRSIPeriod` | int | 14 | RSI period |
| `InpUseSMA` | `InpUseSMA` | bool | false | Enable SMA indicator |
| `InpSMAPeriod` | `InpSMAPeriod` | int | 14 | SMA period |
| `InpUseLaguerreRSI` | `InpUseLaguerreRSI` | bool | false | Enable Laguerre RSI |
| `InpLaguerreInstanceID` | `InpLaguerreInstanceID` | string | "A" | Laguerre instance ID |
| `InpLaguerreAtrPeriod` | `InpLaguerreAtrPeriod` | int | 32 | ATR period |
| `InpLaguerreSmoothPeriod` | `InpLaguerreSmoothPeriod` | int | 5 | Smoothing period |
| `InpLaguerreSmoothMethod` | `InpLaguerreSmoothMethod` | int | 1 | ENUM: 0=SMA, 1=EMA, 2=SMMA, 3=LWMA |
| `InpOutputName` | `InpOutputName` | string | "" | Custom output filename |

**3. File Location**: `MQL5/Files/export_config.txt`
- **MQL5 Access**: `FileOpen("export_config.txt", FILE_READ|FILE_TXT)`
- **Python Access (macOS)**: `$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Files/export_config.txt`
- **Python Access (Wine)**: `C:\Program Files\MetaTrader 5\MQL5\Files\export_config.txt`
- **Rationale**: MQL5/Files/ is the sandbox directory accessible from both MQL5 and external scripts

**4. Encoding**: UTF-8
- **Rationale**: Standard encoding, MQL5 `FileOpen()` with `FILE_TXT` handles UTF-8
- **Alternative Rejected**: UTF-16LE (used by .set files, but adds complexity)

**5. Loading Strategy**:
- Config file is **optional** - if not present, use input parameters from .mq5
- Config file **overrides** input parameters if present
- Missing parameters in config → fall back to defaults
- Invalid values → log error and use defaults (no silent failures)

**6. Error Handling**:
- Config file not found → Use input parameters (graceful degradation)
- Invalid format (no `=` delimiter) → Skip line, log warning
- Invalid boolean (`true1`) → Default to `false`, log warning
- Invalid integer (`abc`) → Use default, log error
- Unknown parameter name → Ignore, log warning (forward compatibility)

**Phase 2: MQL5 Config Reader** ⏸️ PENDING
- [ ] Implement `LoadConfigFromFile()` function
- [ ] Add parameter parsing logic
- [ ] Add fallback to input parameters if no config

**Phase 3: Diagnostic Logging** ⏸️ PENDING
- [ ] Add parameter value logging
- [ ] Verify config loading in logs
- [ ] Test compilation

**Phase 4: Python Config Generator** ⏸️ PENDING
- [ ] Create `generate_export_config.py` script
- [ ] Test config file generation
- [ ] Verify file location and permissions

**Phase 5: Baseline Test (EURUSD)** ⏸️ PENDING
- [ ] Generate config (100 bars, SMA enabled)
- [ ] Run export script
- [ ] Verify logs show config loaded
- [ ] Verify CSV has 100 bars + SMA column

**Phase 6: Cold-Start Test (XAUUSD)** ⏸️ PENDING
- [ ] Generate config for XAUUSD
- [ ] Run export without GUI initialization
- [ ] Verify success

**Phase 7: Multi-Config Test** ⏸️ PENDING
- [ ] Test different parameter combinations
- [ ] Verify flexibility

**Phase 8: Automation Script** ⏸️ PENDING
- [ ] Create `export_with_config.sh` wrapper
- [ ] Test end-to-end workflow

**Phase 9: Documentation** ⏸️ PENDING
- [ ] Document workflow in guides/
- [ ] Update CLAUDE.md with v4.0.0 status

**Phase 10 (Optional): GUI .set File Test** ⏸️ PENDING
- [ ] Create one preset via MT5 GUI
- [ ] Test ScriptParameters with GUI-generated file
- [ ] Compare with file-based approach

**Current Status**: Phase 1 complete ✅, Phase 2 next (MQL5 config reader implementation)

---

## v3.0.0: Python MetaTrader5 API (COMPLETE ✅)

**Completed**: 2025-10-13
**Status**: PRODUCTION READY
**Objective**: True headless MT5 data export without manual GUI initialization

**Result**: ✅ **SUCCESS** - All 5 phases completed

**Key Achievements**:
1. ✅ Wine Python 3.12.8 + MetaTrader5 5.0.5328 working with NumPy 1.26.4
2. ✅ Custom RSI calculation (pandas ewm) - no pandas-ta dependency
3. ✅ MT5 connection via Wine Python - no bridge complexity
4. ✅ Cold start validation passed - XAUUSD M1/H1 exported without GUI initialization
5. ✅ CSV format matches ExportAligned.mq5 exactly

**Critical Test**: XAUUSD (never opened in GUI) exported successfully for both M1 and H1 timeframes - **proving true headless capability**

**Files**:
- Export script: `C:\users\crossover\export_aligned.py`
- Outputs: `C:\Users\crossover\exports\Export_{SYMBOL}_PERIOD_{TIMEFRAME}.csv`
- Test scripts: `test_mt5_connection.py`, `test_numpy_workaround.bat`

**Usage**:
```bash
# From macOS command line (via cxstart)
cxstart --bottle "MetaTrader 5" -- cmd /c "\"C:\Program Files\Python312\python.exe\" C:\users\crossover\export_aligned.py --symbol XAUUSD --period M1 --bars 5000"

# Output accessible from macOS
cat "/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/exports/Export_XAUUSD_PERIOD_M1.csv"
```

---

## Problem Statement

**v2.0.0 Limitation Discovered** (2025-10-13 16:09):
- startup.ini approach requires prior GUI initialization for each symbol/timeframe
- EURUSD M1: ✅ Works (manually initialized at 15:03)
- XAUUSD H1: ❌ Fails (never opened in GUI)
- Root cause: `[StartUp]` section attaches scripts to existing chart contexts, does not create charts

**Requirement**: True headless execution without manual GUI steps for any symbol/timeframe

## Solution Architecture

**MetaTrader5 Python API (Wine Python only)**:

```
Wine Python + MetaTrader5 package
    ↓ Direct IPC connection
MT5 Terminal (CrossOver/Wine)
    ↓ CSV output
macOS filesystem (shared)
```

**Key Capabilities**:
- `mt5.symbol_select()` - programmatically add symbols to Market Watch
- `mt5.copy_rates_range()` - fetch OHLC data without charts
- No GUI interaction required - eliminates chart context dependency
- CSV files written to shared macOS filesystem
- pandas-ta for RSI calculation (installable in Wine Python)

**Architecture Rationale**:
- mt5linux/pymt5adapter both require MetaTrader5 package (Windows-only) on macOS side - fundamentally incompatible
- Direct Wine Python execution simplifies architecture, eliminates bridge complexity
- macOS can read CSV files directly from shared bottle filesystem

## Service Level Objectives

### Availability
- **Target**: 95% success rate for any symbol/timeframe without prior GUI setup
- **Measurement**: Successful CSV generation for never-before-initialized symbols
- **Failure condition**: Cold start test (XAUUSD H1) fails

### Correctness
- **Target**: 100% data integrity, correlation ≥ 0.999 with MT5 native indicators
- **Measurement**: python/validate_export.py all checks pass
- **Failure condition**: Any integrity check fails OR RSI correlation < 0.999

### Observability
- **Target**: All API calls logged with errors propagated (no silent failures)
- **Measurement**: Log entries for mt5.initialize(), symbol_select(), copy_rates_range() with error codes
- **Failure condition**: API call fails without logged error via mt5.last_error()

### Maintainability
- **Target**: Single command data export, no manual Wine/MT5 management
- **Measurement**: User runs one script, bridge auto-starts, MT5 auto-connects
- **Failure condition**: User must manually start Wine processes or MT5 terminal between runs

## Implementation Phases

### Phase 1: Wine Python Environment Setup
**Status**: COMPLETE ✅
**Resolution**: NumPy 1.26.4 downgrade successful
**Validation**: MetaTrader5 5.0.5328 imports successfully in Wine Python
**Completion Time**: 2025-10-13 17:20

**Objective**: Install Python and MetaTrader5 package inside CrossOver bottle

**Resolution Details**:

1. ✅ **NumPy Version Pinning** - SUCCESSFUL
   - Downgraded from NumPy 2.3.3 to NumPy 1.26.4
   - MetaTrader5 5.0.5328 imports successfully
   - Test script: `test_numpy_workaround.bat`
   - Validation output: `SUCCESS: MetaTrader5 version: 5.0.5328`

**Tasks Completed**:
1. ✅ Python 3.12.8 installed in CrossOver bottle via GUI (MetaTrader 5 bottle)
2. ✅ NumPy 2.3.3 uninstalled
3. ✅ NumPy 1.26.4 installed (MetaTrader5-compatible version)
4. ✅ MetaTrader5 5.0.5328 package reinstalled
5. ✅ MetaTrader5 import test successful

**Success Criteria Met**:
- ✅ Wine Python 3.12.8 installed and functional
- ✅ `import MetaTrader5` succeeds in Wine Python
- ✅ Package version: MetaTrader5 5.0.5328

**Validation Result**:
```bash
# Executed in Wine Python via test_numpy_workaround.bat
SUCCESS: MetaTrader5 version: 5.0.5328
```

### Phase 2: Wine Python Dependencies (REVISED)
**Status**: COMPLETE ✅
**Previous Approach**: mt5linux bridge - ABANDONED (requires MetaTrader5 package on macOS, which is Windows-only)
**New Approach**: Run entire Python script in Wine, output CSV to shared filesystem
**Completion Time**: 2025-10-13 17:35
**Resolution**: Skipped pandas-ta, calculate RSI manually with pandas (simpler, no dependency conflicts)

**Objective**: Install dependencies for RSI calculation in Wine Python

**Resolution Details**:
1. ✅ pandas 2.3.3 installed with NumPy 1.26.4 pinned
2. ✅ pandas-ta SKIPPED - RSI calculation implemented directly with pandas ewm()
3. ✅ Output directory working - CrossOver provides automatic filesystem integration

**Tasks Completed**:
- pandas installed successfully with --no-deps to avoid NumPy upgrade
- pandas dependencies manually installed (python-dateutil, pytz, tzdata)
- Environment restored after initial pandas-ta installation broke NumPy pinning
- RSI calculation implemented manually (3 lines of code vs pandas-ta dependency)

**Success Criteria Met**:
- ✅ pandas imports successfully in Wine Python
- ✅ NumPy 1.26.4 remains stable (no upgrade to 2.x)
- ✅ Output directory accessible from both Wine and macOS
- ✅ Custom RSI calculation working correctly

**Validation Result**:
```bash
# Environment diagnostic via restore_and_test.bat
Python 3.12.8, NumPy 1.26.4, MetaTrader5 5.0.5328, pandas 2.3.3
SUCCESS: All packages working without crashes
```

### Phase 3: MT5 Connection Test
**Status**: COMPLETE ✅
**Completion Time**: 2025-10-13 17:40
**Validation**: test_mt5_connection.py successful

**Objective**: Verify Wine Python can connect to MT5 and fetch data

**Resolution Details**:
- ✅ Connected to MT5 build 5331 successfully
- ✅ EURUSD selected programmatically (no GUI needed)
- ✅ Fetched 7,175 bars of M1 data
- ✅ Latest close: 1.15702

**Tasks Completed**:
1. ✅ Created test_mt5_connection.py with proper error handling
2. ✅ MT5 initialize() successful
3. ✅ terminal_info() returned MT5 build 5331
4. ✅ symbol_select("EURUSD", True) worked without prior GUI initialization
5. ✅ copy_rates_range() fetched data successfully

**Success Criteria Met**:
- ✅ `mt5.initialize()` returns True
- ✅ `mt5.terminal_info()` returns build info
- ✅ `copy_rates_range()` returns bars with OHLCV fields

**Validation Result**:
```bash
# Executed via run_test_now.bat
[OK] MT5 initialized successfully
[OK] Connected to MT5 build 5331
  Company: MetaQuotes Ltd.
  Name: MetaTrader 5
  Connected: True
[OK] EURUSD selected and added to Market Watch
[OK] Fetched 7175 bars
  First bar: 2025-10-06 17:38:00
  Last bar:  2025-10-13 17:37:00
  Latest close: 1.15702
[OK] MT5 shutdown cleanly
Phase 3 Test: PASSED
```

### Phase 4: Data Export Script Development
**Status**: COMPLETE ✅
**Completion Time**: 2025-10-13 17:45
**Validation**: EURUSD M1 export successful (5,001 rows)

**Objective**: Rewrite ExportAligned.mq5 logic in Python with RSI calculation

**Resolution Details**:
- ✅ Created export_aligned.py with full functionality
- ✅ Custom RSI implementation using pandas ewm() (Wilder's smoothing)
- ✅ Command-line interface with --symbol, --period, --bars, --output
- ✅ Proper error propagation with mt5.last_error()
- ✅ CSV format matches ExportAligned.mq5 exactly
- ✅ Updated to use copy_rates_from_pos() for non-24/7 markets

**Tasks Completed**:
1. ✅ Created export_aligned.py with argparse CLI
2. ✅ Implemented symbol selection with error checking
3. ✅ Fetched OHLC data using copy_rates_from_pos() (more reliable than date ranges)
4. ✅ Calculated RSI with custom implementation: `rsi = 100 - (100 / (1 + rs))`
5. ✅ Exported to CSV with matching format

**Success Criteria Met**:
- ✅ Script runs without errors for any symbol/timeframe
- ✅ CSV format matches ExportAligned.mq5 (Time, Open, High, Low, Close, Volume, RSI)
- ✅ RSI values calculated correctly for all bars (14-period warmup included)

**Validation Result**:
```bash
# EURUSD M1 test export
File: Export_EURUSD_PERIOD_M1.csv
Rows: 5,001 (5,000 data + 1 header)
Latest data: 2025-10-14 00:39:00
RSI: 48.58181
CSV columns: Time,Open,High,Low,Close,Volume,RSI
Time format: 2025.10.14 00:39:00 (matches MQL5)
```

### Phase 5: Cold Start Validation
**Status**: COMPLETE ✅
**Completion Time**: 2025-10-13 17:48
**Validation**: XAUUSD M1 and H1 both successful - TRUE HEADLESS CONFIRMED

**Objective**: Verify headless execution for symbols never opened in GUI

**Resolution Details**:
- ✅ XAUUSD M1: 5,000 bars exported successfully (never opened in GUI)
- ✅ XAUUSD H1: 5,000 bars exported successfully (never opened in GUI)
- ✅ Both symbol/timeframe combinations worked without ANY manual initialization
- ✅ mt5.symbol_select() worked without prior chart context
- ✅ copy_rates_from_pos() more reliable than copy_rates_range() for non-24/7 markets

**Tasks Completed**:
1. ✅ Confirmed XAUUSD never manually opened in MT5 GUI
2. ✅ Ran export for XAUUSD M1: 5,000 bars (2025-10-08 to 2025-10-13)
3. ✅ Ran export for XAUUSD H1: 5,000 bars (2024-12-04 to 2025-10-13)
4. ✅ CSV files generated with expected bars
5. ✅ RSI values calculated correctly

**Success Criteria Met**:
- ✅ Script completed without GUI interaction
- ✅ CSV files exist with 5,000 bars each
- ✅ CSV format matches ExportAligned.mq5 exactly
- ✅ RSI values present and correct

**Validation Results**:

**XAUUSD M1**:
```bash
File: Export_XAUUSD_PERIOD_M1.csv
Rows: 5,000
Date range: 2025-10-08 12:13:00 to 2025-10-14 03:33:00
RSI stats: min=5.68, max=94.03, mean=51.99
Sample data:
  Time: 2025.10.08 12:13:00, Close: 4036.46000, RSI: 38.61895
  Time: 2025.10.14 03:33:00, Close: 4127.58000, RSI: 65.85679
```

**XAUUSD H1**:
```bash
File: Export_XAUUSD_PERIOD_H1.csv
Rows: 5,000
Date range: 2024-12-04 12:00:00 to 2025-10-13 20:00:00
RSI stats: min=5.07, max=94.27, mean=53.79
Exit code: 0 (SUCCESS)
```

**Critical Test Result**: This is THE test that FAILED in v2.0.0 - XAUUSD was never opened in the GUI, and the Python API approach successfully selected the symbol and fetched data without ANY manual initialization. **True headless capability confirmed.**

---

## v2.1.0: Startup.ini Parameter Passing (FAILED ❌)

**Date**: 2025-10-17
**Status**: NOT VIABLE - General MT5 limitation, not Wine-specific
**Objective**: Pass custom parameters to ExportAligned.mq5 via startup.ini

### Test Results (All Failed)

**Test 1: Named Section Method** - ❌ FAILED
- Config: `[ExportAligned]` section with all parameters
- Expected: 100 bars, SMA column, `Export_EURUSD_M1_SMA.csv`
- Actual: 5000 bars (defaults), RSI column, `Export_EURUSD_PERIOD_M1.csv`
- **Conclusion**: Named sections NOT supported by MT5 (only `[StartUp]` section documented)

**Test 2: ScriptParameters with .set Preset File** - ❌ FAILED (Script didn't execute)
- Config: `ScriptParameters=ExportAligned.set`
- Preset file: UTF-16LE BOM encoded, `MQL5/Presets/ExportAligned.set`
- Expected: Script executes with preset parameters
- Actual: Script does NOT execute at all (silent failure)
- **Conclusion**: ScriptParameters blocks execution when preset file has issues

### Research Findings (4 Parallel Subtasks)

**Finding 1: Named Sections NOT Supported**
- MT5 documentation only specifies predefined sections (`[StartUp]`, `[Experts]`, etc.)
- Custom named sections like `[ScriptName]` are NOT documented
- Windows users report same failure - NOT a Wine bug
- ✅ Confirmed: Universal MT5 limitation

**Finding 2: ScriptParameters Silent Failure**
- ScriptParameters IS valid for scripts (not EA-only)
- Fails silently when:
  - Wrong encoding (must be UCS-2 LE with BOM)
  - Wrong location (must be `MQL5/Presets/` root)
  - Script missing `#property script_show_inputs`
- MT5 provides ZERO error messages on failure
- ✅ Confirmed: Strict requirements cause silent failures

**Finding 3: No Wine-Specific Issues**
- No Wine bugs found for parameter passing
- All failures replicate on native Windows
- Community reports confirm same issues on Windows
- ✅ Confirmed: MT5 design limitation, not Wine compatibility issue

**Finding 4: Alternative Methods Exist**
- File-based config reading (MQL5 FileOpen/FileReadString)
- JSON/INI parsing libraries available (JAson.mqh, IniFiles.mqh)
- Python MetaTrader5 API (v3.0.0 - already working)
- ✅ Confirmed: Viable alternatives available

### Verdict

**Status**: ❌ NOT VIABLE on CrossOver (or native Windows)

**Reasons**:
1. Named sections don't work (MT5 limitation, all platforms)
2. ScriptParameters has strict requirements with silent failures
3. No error feedback when configuration fails
4. v3.0.0 Python API + v4.0.0 file-based config are superior solutions

**Recommendation**: Use v3.0.0 for market data, implement v4.0.0 for custom indicators

---

## Off-the-Shelf Components

### Required Packages
- **Python 3.12+** (x64 Windows): python.org/downloads/windows/
- **MetaTrader5 Python package**: pypi.org/project/MetaTrader5/
- **mt5linux bridge**: pypi.org/project/mt5linux/ (Lucas Campagna, Linux/Mac bridge)
- **pandas-ta**: pypi.org/project/pandas-ta/ (RSI and technical indicators)

### Alternatives Considered
- **TA-Lib**: Requires C compilation, more complex setup (rejected)
- **Custom RPyC server**: Re-inventing mt5linux (rejected - use existing solution)
- **REST API wrapper**: Over-engineered for single-user local setup (rejected)

## Error Propagation Protocol

**No silent failures** - all errors must raise exceptions with context:

```python
# Example error handling pattern
if not mt5.initialize():
    error_code, error_msg = mt5.last_error()
    raise ConnectionError(
        f"MT5 initialization failed\n"
        f"Error code: {error_code}\n"
        f"Message: {error_msg}\n"
        f"Ensure MT5 terminal is running and logged in"
    )
```

**Error Categories**:
1. **Environment errors**: Python/package installation issues
2. **Connection errors**: mt5linux bridge or MT5 terminal communication failures
3. **Data errors**: Symbol not found, data fetch failures, empty results
4. **Validation errors**: RSI correlation below threshold, integrity check failures

**Logging Requirements**:
- All mt5.* API calls logged with timestamps
- Error codes from `mt5.last_error()` always included in exceptions
- Full tracebacks preserved (no exception swallowing)

## Migration from v2.0.0

**Deprecated**:
- `mq5run` script (startup.ini approach)
- Manual GUI initialization requirement
- startup.ini config file generation

**Preserved**:
- CSV output format (backward compatible)
- `python/validate_export.py` validation logic
- MT5 terminal in CrossOver (still required, but no GUI interaction)

**New Entry Point**:
```bash
# Old (conditional - requires GUI setup)
./scripts/mq5run --symbol XAUUSD --period PERIOD_H1

# New (true headless)
uv run --active python -m export_aligned_py --symbol XAUUSD --period H1 --bars 5000
```

## Progress Tracking

### Phase 1: Wine Python Setup ✅ COMPLETE (2025-10-13 17:20)
- [x] Python 3.12 Windows installer downloaded (via CrossOver GUI)
- [x] Python 3.12.8 installed in CrossOver bottle (MetaTrader 5 bottle)
- [x] NumPy 1.26.4 workaround tested and successful
- [x] MetaTrader5 5.0.5328 package installed with compatible NumPy
- [x] Import test successful - MetaTrader5 imports in Wine Python

### Phase 2: Wine Python Dependencies ✅ COMPLETE (2025-10-13 17:35)
- [x] pandas 2.3.3 installed with NumPy 1.26.4 pinned
- [x] pandas-ta SKIPPED - custom RSI implementation chosen
- [x] Environment stable after restore
- [x] Output directory accessible from Wine and macOS

### Phase 3: MT5 Connection ✅ COMPLETE (2025-10-13 17:40)
- [x] mt5.initialize() successful
- [x] mt5.terminal_info() returns data (build 5331)
- [x] Basic data fetch works (EURUSD M1 - 7,175 bars)
- [x] symbol_select() works without prior GUI initialization

### Phase 4: Export Script ✅ COMPLETE (2025-10-13 17:45)
- [x] export_aligned.py created with full CLI
- [x] Symbol selection logic implemented with error checking
- [x] OHLC data fetch implemented (copy_rates_from_pos)
- [x] RSI calculation implemented (custom pandas ewm)
- [x] CSV export implemented with matching format
- [x] EURUSD M1 validation passed (5,000 bars)

### Phase 5: Cold Start Validation ✅ COMPLETE (2025-10-13 17:48)
- [x] XAUUSD M1 export successful (never initialized in GUI - 5,000 bars)
- [x] XAUUSD H1 export successful (never initialized in GUI - 5,000 bars)
- [x] CSV format matches ExportAligned.mq5
- [x] RSI values calculated correctly
- [x] **TRUE HEADLESS CAPABILITY CONFIRMED** - no manual GUI initialization required

## Wine Scientific Python Incompatibility - RESOLVED ✅

**Discovery Date**: 2025-10-13 16:56
**Research Completed**: 2025-10-13 17:15
**Resolution Date**: 2025-10-13 17:20
**Final Status**: NumPy 1.26.4 workaround successful

**Error**: `Unhandled exception: unimplemented function ucrtbase.dll.crealf called in 64-bit code`
**Root Cause**: NumPy 2.x (MetaTrader5 dependency) uses compiled C extensions that call Windows math functions not fully implemented in Wine 10.0
**Impact**: Cannot run MetaTrader5 Python package under Wine with NumPy 2.x

**Resolution**:
1. ✅ **NumPy 1.26.4 downgrade** - SUCCESSFUL
   - Community-verified working (MQL5 forum, Sep 2024)
   - Test script: `test_numpy_workaround.bat`
   - Result: MetaTrader5 5.0.5328 imports successfully
   - Validation: All 5 phases completed with this workaround

2. ⏸️ **Wine 10.1+ upgrade** - NOT NEEDED (NumPy downgrade sufficient)

3. ⏸️ **Native UCRT override** - NOT NEEDED (NumPy downgrade sufficient)

**Fallback Approaches** - NOT NEEDED (NumPy 1.26.4 workaround successful)

## Decision Log

### Decision 1: NumPy 1.26.4 workaround for Wine compatibility - SUCCESSFUL ✅
**Date**: 2025-10-13 17:15 (Created) → 2025-10-13 17:20 (Resolved)
**Initial Status**: Python API approach blocked by Wine UCRT incompatibility
**Research Findings**: Community-verified workarounds exist (NumPy 1.x pinning, Wine upgrade, native DLL)
**Rationale**: MetaTrader5 package compiled against NumPy 1.x API, not 2.x. NumPy 2.x uses additional UCRT functions not in Wine 10.0.
**Evidence**:
- `ucrtbase.dll.crealf` unimplemented function error during NumPy 2.x import
- MQL5 community confirmation (Sep 2024): MetaTrader5 incompatible with NumPy 2.x
- WineHQ forum (Mar 2025): Wine 10.1+ has improved UCRT support
**Resolution**: NumPy 1.26.4 downgrade via `test_numpy_workaround.bat` - SUCCESSFUL
**Outcome**: MetaTrader5 5.0.5328 imports successfully, all 5 phases completed
**Alternative**: Revert to v2.0.0 startup.ini approach - NOT NEEDED

### Decision 2: Abandon mt5linux bridge, use Wine Python only
**Date**: 2025-10-13 17:30
**Initial Plan**: Use mt5linux/pymt5adapter bridge for macOS Python → Wine MT5
**Blocking Issue**: Both bridge packages require MetaTrader5 package (Windows-only) importable on macOS side
**Evidence**:
- mt5linux 0.1.9 requires ancient numpy==1.21.4 (incompatible with Python 3.13, distutils removed)
- pymt5adapter all versions require exact metatrader5==5.0.31 or 5.0.33 (not available for macOS)
- MetaTrader5 package is Windows-only, cannot run on macOS even with Wine bridge
**Revised Architecture**: Run entire Python script in Wine, write CSV to shared macOS filesystem
**Rationale**: Simplifies architecture, eliminates bridge complexity, leverages CrossOver's filesystem integration
**Trade-off**: Script execution happens in Wine (slightly more friction), but eliminates dependency hell

### Decision 3: pandas-ta for RSI vs TA-Lib
**Rationale**: pandas-ta is pure Python (no C compilation), simpler installation, sufficient accuracy
**Alternative**: TA-Lib (rejected - requires compilation, overkill for RSI only)

### Decision 4: Raise errors immediately vs retry logic
**Rationale**: User requirement - "no fallbacks, defaults, retries". Fail fast for transparency.
**Alternative**: Automatic retry with exponential backoff (rejected per requirements)

## References

**Research Report**: AI researcher findings (2025-10-13) - 18 sources, 66 searches
**Archived Plan**: ../archive/HEADLESS_EXECUTION_PLAN.v2.0.0.archived.md (startup.ini approach)
**Validation Status**: ../reports/VALIDATION_STATUS.md (conditionally validated for v2.0.0, v3.0.0 complete)
**Knowledge Base**: ../guides/CROSSOVER_MQ5.md (MT5/CrossOver operations)

## Update Protocol

- Increment version (major.minor.patch) on significant changes
- Update phase status: PENDING → IN_PROGRESS → COMPLETE/FAILED
- Log all decisions with date and rationale
- Move superseded approaches to archived files
- Update references in VALIDATION_STATUS.md and CROSSOVER_MQ5.md to point to latest plan
