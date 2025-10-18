# mql5-crossover Project Memory

**Architecture**: Link Farm + Hub-and-Spoke with Progressive Disclosure

## 🚀 Quick Start (New to This Project?)

**First Time Here? Start with these 3 documents in order:**

1. **[MQL5_TO_PYTHON_MIGRATION_GUIDE.md](docs/guides/MQL5_TO_PYTHON_MIGRATION_GUIDE.md)** ⭐ - Complete 7-phase workflow (2-4 hours per indicator)
2. **[LESSONS_LEARNED_PLAYBOOK.md](docs/guides/LESSONS_LEARNED_PLAYBOOK.md)** 🔥 - 8 critical gotchas (prevents 50+ hours of debugging)
3. **[INDICATOR_MIGRATION_CHECKLIST.md](docs/templates/INDICATOR_MIGRATION_CHECKLIST.md)** ✨ - Copy-paste checklist with all commands

**Ready to Export Data?**
- Headless (automated): **[WINE_PYTHON_EXECUTION.md](docs/guides/WINE_PYTHON_EXECUTION.md)** (v3.0.0)
- GUI (manual): **[V4_FILE_BASED_CONFIG_WORKFLOW.md](docs/guides/V4_FILE_BASED_CONFIG_WORKFLOW.md)** (v4.0.0)

---

## Navigation Index

**Current Workspace**: `/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c ` (CrossOver bottle root)
**Project Documentation**: `docs/README.md ` - Project overview and documentation index

## Core Guides

### Master Workflow
- **[MQL5_TO_PYTHON_MIGRATION_GUIDE.md](docs/guides/MQL5_TO_PYTHON_MIGRATION_GUIDE.md)** - **⭐ START HERE** - Complete MQL5→Python indicator migration workflow (7 phases, battle-tested, 2-4 hours first time)
- **[LESSONS_LEARNED_PLAYBOOK.md](docs/guides/LESSONS_LEARNED_PLAYBOOK.md)** - **🔥 CRITICAL GOTCHAS** - Hard-won lessons from 185+ hours of debugging (READ BEFORE STARTING NEW WORK)

### Quick References
- **[WINE_PYTHON_EXECUTION.md](docs/guides/WINE_PYTHON_EXECUTION.md)** - v3.0.0 Wine Python execution (production) - CX_BOTTLE, path navigation, RSI formula, diagnostics
- **[V4_FILE_BASED_CONFIG_WORKFLOW.md](docs/guides/V4_FILE_BASED_CONFIG_WORKFLOW.md)** - **✨ NEW** - v4.0.0 File-based config workflow (production) - GUI-based exports with flexible parameters
- **[MT5_FILE_LOCATIONS.md](docs/guides/MT5_FILE_LOCATIONS.md)** - Complete MT5 file paths and indicator translation workflow
- **[MQL5_ENCODING_SOLUTIONS.md](docs/guides/MQL5_ENCODING_SOLUTIONS.md)** - MQL5 encoding guide - UTF-8/UTF-16LE both work, chardet, Git integration, Python patterns
- **[LAGUERRE_RSI_ANALYSIS.md](docs/guides/LAGUERRE_RSI_ANALYSIS.md)** - ATR Adaptive Smoothed Laguerre RSI - Complete algorithm breakdown and Python translation guide
- **[PYTHON_INDICATOR_VALIDATION_FAILURES.md](docs/guides/PYTHON_INDICATOR_VALIDATION_FAILURES.md)** - Hard-learned lessons from validation failures - NaN traps, warmup requirements, pandas pitfalls (3 hours of debugging)
- **[EXTERNAL_RESEARCH_BREAKTHROUGHS.md](docs/guides/EXTERNAL_RESEARCH_BREAKTHROUGHS.md)** - Critical lessons from external AI research - /inc parameter trap, script automation via config files, Python API limitations, path handling in CrossOver
- **[SCRIPT_PARAMETER_PASSING_RESEARCH.md](docs/guides/SCRIPT_PARAMETER_PASSING_RESEARCH.md)** - MQL5 Script Parameter Passing - Community research on startup.ini + ScriptParameters + .set files (30+ sources, 7 working examples, known bugs documented)
- **[LAGUERRE_RSI_TEMPORAL_AUDIT.md](docs/guides/LAGUERRE_RSI_TEMPORAL_AUDIT.md)** - Temporal leakage audit - No look-ahead bias detected, approved for production use
- **[LAGUERRE_RSI_SHARED_STATE_BUG.md](docs/guides/LAGUERRE_RSI_SHARED_STATE_BUG.md)** - Fixed: Shared laguerreWork array - Separate instances for normal/custom timeframe (root cause)
- **[LAGUERRE_RSI_ARRAY_INDEXING_BUG.md](docs/guides/LAGUERRE_RSI_ARRAY_INDEXING_BUG.md)** - Fixed: Series indexing direction - Loop backwards for proper EMA calculation
- **[LAGUERRE_RSI_BUG_FIX_SUMMARY.md](docs/guides/LAGUERRE_RSI_BUG_FIX_SUMMARY.md)** - Fixed: Price smoothing bug - All MA methods now work in custom timeframe mode
- **[LAGUERRE_RSI_BUG_REPORT.md](docs/guides/LAGUERRE_RSI_BUG_REPORT.md)** - Original bug report (EMA vs SMA inconsistency) - RESOLVED
- **[MQL5_CLI_COMPILATION_SUCCESS.md](docs/guides/MQL5_CLI_COMPILATION_SUCCESS.md)** - CLI compilation via CrossOver --cx-app flag (~1s compile time, production-ready)
- **[CROSSOVER_MQ5.md](docs/guides/CROSSOVER_MQ5.md)** - MT5/CrossOver technical reference and shell setup (v2.0.0 legacy)
- **[BOTTLE_TRACKING.md](docs/guides/BOTTLE_TRACKING.md)** - CrossOver bottle file tracking via X: drive mapping

### Templates & Tools
- **[INDICATOR_MIGRATION_CHECKLIST.md](docs/templates/INDICATOR_MIGRATION_CHECKLIST.md)** - **✨ NEW** - Copy-paste ready checklist for 7-phase workflow (2-4 hours per indicator)
- **[generate_export_config.py](users/crossover/generate_export_config.py)** - **✨ NEW** - Python script to generate v4.0.0 config files
- **[Config Examples](Program Files/MetaTrader 5/MQL5/Files/configs/)** - **✨ NEW** - 5 example configs (RSI, SMA, Laguerre RSI, multi-indicator, validation)

## Implementation Plans

- **[HEADLESS_EXECUTION_PLAN.md](docs/plans/HEADLESS_EXECUTION_PLAN.md)** - v4.0.0 File-based config COMPLETE + v3.0.0 Python API
  - **v4.0.0**: File-based configuration for GUI exports - COMPLETE ✅ (GUI mode)
  - **v3.0.0**: Python API for market data - COMPLETE ✅ (true headless)
  - **v2.1.0**: Startup.ini parameter passing - FAILED ❌ (NOT VIABLE)
  - **v2.0.0**: Basic startup.ini script launch - CONDITIONALLY WORKING ⚠️
  - **Key Achievement**: Two complementary production-ready approaches
  - **Status**: v3.0.0 (headless) + v4.0.0 (GUI) production-ready, all tooling complete

## Validation Reports

- **[DOCUMENTATION_READINESS_ASSESSMENT.md](docs/reports/DOCUMENTATION_READINESS_ASSESSMENT.md)** - **⭐ READINESS AUDIT** - Comprehensive assessment of documentation completeness, workspace structure, and migration readiness (95/100 score)
- **[VALIDATION_STATUS.md](docs/reports/VALIDATION_STATUS.md)** - Current SLO metrics and test results
- **[SUCCESS_REPORT.md](docs/reports/SUCCESS_REPORT.md)** - Manual and headless validation (0.999902 correlation)
- **[LAGUERRE_RSI_VALIDATION_SUCCESS.md](docs/reports/LAGUERRE_RSI_VALIDATION_SUCCESS.md)** - Python Laguerre RSI validation (1.000000 correlation, 5000-bar warmup methodology)

## Architecture

### Directory Structure

```
Program Files/MetaTrader 5/MQL5/          # MT5 idiomatic structure
├── Scripts/DataExport/                    # Export scripts (modular design)
│   ├── ExportAligned.mq5 + .ex5          # Main export script
│   └── ExportEURUSD.mq5                  # Legacy EURUSD exporter
├── Include/DataExport/                    # Custom include libraries
│   ├── DataExportCore.mqh                # Core export functionality
│   ├── ExportAlignedCommon.mqh           # Common utilities
│   └── modules/                          # Modular components
│       └── RSIModule.mqh                 # RSI calculation module
└── Indicators/Custom/                     # Project-based organization
    ├── ProductionIndicators/              # Production-ready indicators
    ├── PythonInterop/                     # Python export workflow indicators
    ├── Libraries/                         # Shared library files (.mqh)
    └── Development/                       # Active development
        └── ConsecutivePattern/            # cc indicator project
            ├── cc.mq5                     # Main version
            ├── cc_backup.mq5              # Standalone fallback
            └── lib/                       # Local dependencies

users/crossover/                           # Python workspace (utilities)
├── export_aligned.py                      # Wine Python v3.0.0 export script
├── validate_export.py                     # CSV validation tool
├── test_mt5_connection.py                 # MT5 connection diagnostics
├── test_xauusd_info.py                    # Symbol info testing
├── indicators/                            # Python indicator implementations
│   ├── __init__.py
│   └── laguerre_rsi.py
└── exports/                               # CSV outputs

.claude/                                   # Local settings
└── settings.local.json                    # Project-specific settings

docs/                                      # Documentation hub
├── guides/                                # Step-by-step workflows (15+ guides)
├── plans/                                 # Implementation plans
├── reports/                               # Validation results
└── archive/                               # Historical/deprecated

archive/                                   # Legacy code preserved
├── experiments/                           # Spike tests and prototypes (5 files)
├── plans/                                 # Completed plan documents (8 files)
├── docs/                                  # Outdated guides with version markers
│   ├── QUICKSTART.v2.0.0.md              # v2.0.0 startup.ini approach
│   ├── AI_AGENT_WORKFLOW.v2.0.0.md       # v2.0.0 development patterns
│   ├── CROSSOVER_MQ5.v2.0.0.md           # v2.0.0 CrossOver setup
│   └── MQL5_CLI_COMPILATION_INVESTIGATION.md  # 11+ failed attempts (historical)
├── indicators/                            # Archived indicator versions (organized by project)
│   ├── laguerre_rsi/                     # Laguerre RSI development history
│   │   ├── compiled/                     # Compiled .ex5 files (3)
│   │   ├── development/                  # Development versions
│   │   ├── original/                     # Original source files
│   │   └── test_files/                   # Test/experiment files
│   ├── cc/                                # Consecutive Pattern (cc) indicator
│   │   ├── compiled/                     # Compiled .ex5 files (4)
│   │   ├── development/                  # Development versions (10 files)
│   │   └── source/                       # Source files and docs
│   └── vwap/                              # VWAP indicator
│       └── vwap-multi.ex5                # Compiled file
├── mt5work_legacy/                       # Old development workspace
└── scripts/v2.0.0/                       # v2.0.0 legacy wrappers

exports/                                   # CSV exports (gitignored)
```

**Structural Patterns** (v2.0.0):
- MT5 idiomatic layout (Scripts/DataExport, Include/DataExport)
- Project-based indicator folders (ProductionIndicators, PythonInterop, Libraries, Development)
- Centralized Python utilities (users/crossover/)
- Documentation hub (docs/ with 4 subdirectories)
- Legacy preservation (archive/ - no deletion policy)

### Single Source of Truth

| Topic                       | Authoritative Document                  |
| --------------------------- | --------------------------------------- |
| **🚀 WORKFLOWS & PROCESSES** | |
| **MQL5→Python Migration Workflow (MASTER)** | **`docs/guides/MQL5_TO_PYTHON_MIGRATION_GUIDE.md`** ⭐ |
| **Lessons Learned Playbook (CRITICAL GOTCHAS)** | **`docs/guides/LESSONS_LEARNED_PLAYBOOK.md`** 🔥 |
| **Indicator Migration Checklist (COPY-PASTE READY)** | **`docs/templates/INDICATOR_MIGRATION_CHECKLIST.md`** ✨ |
| Wine Python Execution (v3.0.0 Headless) | `docs/guides/WINE_PYTHON_EXECUTION.md` |
| v4.0.0 File-Based Config Workflow (GUI) | `docs/guides/V4_FILE_BASED_CONFIG_WORKFLOW.md` ✨ |
| Headless Execution Architecture (v2/v3/v4 Complete) | `docs/plans/HEADLESS_EXECUTION_PLAN.md` |
| **🔧 TECHNICAL REFERENCES** | |
| MT5 File Paths & Translation | `docs/guides/MT5_FILE_LOCATIONS.md` |
| MQL5 Encoding (UTF-8/UTF-16LE) | `docs/guides/MQL5_ENCODING_SOLUTIONS.md` |
| MQL5 CLI Compilation (Production) | `docs/guides/MQL5_CLI_COMPILATION_SUCCESS.md` |
| MT5/CrossOver Setup (v2.0.0) | `docs/guides/CROSSOVER_MQ5.md` |
| Bottle File Tracking | `docs/guides/BOTTLE_TRACKING.md` |
| **📊 VALIDATION & TESTING** | |
| Python Indicator Validation Methodology (1.000000 correlation) | `docs/reports/LAGUERRE_RSI_VALIDATION_SUCCESS.md` |
| Python Indicator Validation Failures & Debugging (3 hours lessons) | `docs/guides/PYTHON_INDICATOR_VALIDATION_FAILURES.md` |
| Validation Status (Current SLOs) | `docs/reports/VALIDATION_STATUS.md` |
| **🔬 LAGUERRE RSI CASE STUDY** | |
| Laguerre RSI Algorithm & Translation | `docs/guides/LAGUERRE_RSI_ANALYSIS.md` |
| Laguerre RSI Temporal Audit (No look-ahead bias) | `docs/guides/LAGUERRE_RSI_TEMPORAL_AUDIT.md` |
| Laguerre RSI Shared State Bug (ROOT CAUSE) | `docs/guides/LAGUERRE_RSI_SHARED_STATE_BUG.md` |
| Laguerre RSI Array Indexing Bug | `docs/guides/LAGUERRE_RSI_ARRAY_INDEXING_BUG.md` |
| Laguerre RSI Price Smoothing Bug | `docs/guides/LAGUERRE_RSI_BUG_FIX_SUMMARY.md` |
| Laguerre RSI Original Bug Report | `docs/guides/LAGUERRE_RSI_BUG_REPORT.md` |
| **🔍 RESEARCH & DISCOVERIES** | |
| External Research Breakthroughs (MQL5 CLI, Script Automation, Python API) | `docs/guides/EXTERNAL_RESEARCH_BREAKTHROUGHS.md` |
| MQL5 Script Parameter Passing (startup.ini, ScriptParameters, .set files) | `docs/guides/SCRIPT_PARAMETER_PASSING_RESEARCH.md` |
| **📋 ASSESSMENTS & STATUS** | |
| Documentation Readiness Assessment (95/100 score) | `docs/reports/DOCUMENTATION_READINESS_ASSESSMENT.md` |
| Pruning Assessment | `docs/reports/PRUNING_ASSESSMENT.md` |
| Historical Context (2022-2025 research) | `docs/archive/historical.txt` |

## Python Workspace Utilities

### users/crossover/ (Persistent Tools)

**Core Scripts**:
- `export_aligned.py` - Wine Python v3.0.0 data export (headless, production)
- **`validate_indicator.py`** - ⭐ Universal indicator validation framework (v1.0.0, production, ≥0.999 correlation)
- `validate_export.py` - ⚠️ DEPRECATED - Use validate_indicator.py instead (RSI-only legacy tool)
- **`generate_export_config.py`** - ✨ v4.0.0 config file generator (command-line tool)
- `test_mt5_connection.py` - MT5 connection diagnostics
- `test_xauusd_info.py` - Symbol information testing

**Python Indicators**:
- `indicators/laguerre_rsi.py` - Laguerre RSI implementation (v1.0.0, validated 1.000000 correlation)
- `indicators/__init__.py` - Package initialization

**Config Files** (v4.0.0):
- `../Program Files/MetaTrader 5/MQL5/Files/export_config.txt` - Active config (read by ExportAligned.mq5)
- `../Program Files/MetaTrader 5/MQL5/Files/configs/` - 5 example configs + README

**Output**:
- `exports/` - CSV export destination

**Usage Patterns**:
```bash
# Export data (v3.0.0 headless)
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\export_aligned.py" \
  --symbol EURUSD --period M1 --bars 5000

# Validate correlation (simple)
python validate_export.py ../../exports/Export_EURUSD_PERIOD_M1.csv

# Validate indicator (comprehensive)
python validate_indicator.py \
  --csv /path/to/Export_EURUSD_PERIOD_M1.csv \
  --indicator laguerre_rsi \
  --threshold 0.999
```

## Indicator Organization

### Project-Based Hierarchy (v2.0.0)

**MT5 Navigator Path**: `Indicators → Custom → [Project Folders]`

**Folder Structure**:
- `ProductionIndicators/` - Production-ready indicators
- `PythonInterop/` - Python export workflow indicators
- `Libraries/` - Shared library files (`.mqh`)
- `Development/` - Active development projects
  - `ConsecutivePattern/` - cc indicator with local dependencies
    - `cc.mq5` - Main version
    - `cc_backup.mq5` - Standalone fallback
    - `lib/` - Local project libraries

**Design Principles**:
- Functional separation (Production/Python/Libraries/Development)
- Project self-containment (local dependencies in project folders)
- Scalability (add new project folders as needed)
- MT5 Navigator visibility (organized hierarchy)

## Key Commands

```bash
# Compile MQL5 (CLI - production method)
CX="~/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine"
BOTTLE="MetaTrader 5"
ME="C:/Program Files/MetaTrader 5/MetaEditor64.exe"
"$CX" --bottle "$BOTTLE" --cx-app "$ME" /log /compile:"C:/YourIndicator.mq5" /inc:"C:/Program Files/MetaTrader 5/MQL5"

# Compile MQL5 (GUI fallback - open in MetaEditor, press F7)
# File → Open → Program Files/MetaTrader 5/MQL5/Scripts/DataExport/ExportAligned.mq5

# Export data (v3.0.0 - true headless, PRODUCTION)
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\export_aligned.py" \
  --symbol EURUSD --period M1 --bars 5000

# Copy CSV to repo
cp "$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/exports/Export_EURUSD_PERIOD_M1.csv" exports/

# Export data (v4.0.0 - file-based config, GUI mode)
# Step 1: Create config file at: MQL5/Files/export_config.txt
cat > "$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Files/export_config.txt" << 'EOF'
InpSymbol=EURUSD
InpTimeframe=1
InpBars=100
InpUseRSI=false
InpUseSMA=true
InpSMAPeriod=14
InpUseLaguerreRSI=false
InpOutputName=Export_EURUSD_M1_Test.csv
EOF

# Step 2: Open MT5 GUI, drag ExportAligned onto EURUSD M1 chart, click OK
# Script reads config file and exports with those parameters
# Output: MQL5/Files/Export_EURUSD_M1_Test.csv

# Export data (v2.0.0 - LEGACY, ARCHIVED - use v3.0.0 or v4.0.0 instead)
# DEPRECATED: ./scripts/mq5run (archived in archive/scripts/v2.0.0/)
# Use v3.0.0 for headless or v4.0.0 for GUI with flexible parameters

# Validate
cd users/crossover && python validate_export.py ../../exports/Export_EURUSD_PERIOD_M1.csv

# Kill MT5 Processes (reliable 3-step method)
# Step 1: Identify processes with PIDs
ps aux | grep -E "terminal64|wineserver" | grep -v grep

# Step 2: Kill by specific PID (not by name)
kill -9 <PID_terminal64>
kill -9 <PID_wineserver>

# Step 3: Verify termination (wait 2-3 seconds)
sleep 3
ps aux | grep -E "terminal64|wineserver" | grep -v grep || echo "✅ All killed"

# Run MQL5 Script Headless (v2.1.0 Solution A - via startup.ini)
CROSSOVER_BIN="$HOME/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/cxstart"
BOTTLE_NAME="MetaTrader 5"
TERMINAL_EXE="C:\\Program Files\\MetaTrader 5\\terminal64.exe"

timeout 120 "$CROSSOVER_BIN" \
  --bottle "$BOTTLE_NAME" \
  --wait-children \
  -- \
  "$TERMINAL_EXE" \
  /portable \
  /skipupdate \
  /config:"Config\\startup_sma_test.ini"
```

## Service Level Objectives

- **Availability**: 100% ✓ (20 files accessible)
- **Correctness**: 100% ✓ (0.999902 correlation, all references resolved)
- **Observability**: 100% ✓ (14 reorg commits)
- **Maintainability**: 100% ✓ (organized hierarchy, language conventions)

## MT5 File Locations (CrossOver Bottle)

**Bottle Root**: `/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5 `

**Critical Paths**:
```bash
# MT5 executables
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/terminal64.exe
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MetaEditor64.exe

# MQL5 source tree
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/

# Indicators (user + examples)
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Examples/

# Include files (libraries)
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Include/

# Scripts
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Scripts/

# Wine Python environment
$BOTTLE_ROOT/drive_c/Program Files/Python312/python.exe
$BOTTLE_ROOT/drive_c/users/crossover/export_aligned.py
$BOTTLE_ROOT/drive_c/users/crossover/exports/

# MT5 logs (diagnostics)
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/logs/
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Logs/
```

**Target Indicator Example**:
```bash
# ATR adaptive smoothed Laguerre RSI 2 (extended)
/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/ATR adaptive smoothed Laguerre RSI 2 (extended).mq5
```

**Search Commands**:
```bash
# Find indicator by name
find "$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Indicators" -name "*Laguerre*"

# List all custom indicators
find "$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom" -name "*.mq5"

# Find include dependencies
grep "#include" indicator.mq5
```

See `docs/guides/MT5_FILE_LOCATIONS.md ` for complete path reference and indicator translation workflow.

## Critical Requirements & Limitations

### v3.0.0 (Python API) - PRODUCTION ✅

**Status**: Fully validated (2025-10-13 19:45)

**Requirements**:
- Wine Python 3.12+ with MetaTrader5 5.0.5328 and NumPy 1.26.4 (not 2.x)
- CX_BOTTLE environment variable (mandatory for CrossOver wine wrapper)
- MT5 terminal running and logged in
- Correct RSI formula: `alpha=1/period` (not `span=period`)
- Validator with column name normalization

**Capabilities**:
- True headless - works for any symbol/timeframe without GUI initialization
- Cold start validated: USDJPY M1 (0.999920 correlation)
- Programmatic symbol selection via `mt5.symbol_select()`
- Direct data fetch via `mt5.copy_rates_from_pos()`

**Critical Path Operations**:
- macOS → Wine execution: Use `CX_BOTTLE` + `WINEPREFIX` + wine command
- Python script paths: Windows-style `C:\users\crossover\...`
- CSV copy: macOS native paths `~/Library/.../drive_c/users/...`
- See `docs/guides/WINE_PYTHON_EXECUTION.md ` for complete path navigation guide

**Python Indicator Validation Requirements**:
- **Historical Warmup Requirement**: Python implementations need identical historical context as MQL5
- Cannot compare MQL5 indicator with full history to Python cold start (will produce ~0.95 correlation)
- Solution: Fetch 5000+ bars using Wine Python MT5 API, calculate on all bars, compare last N bars
- ATR requires 32-bar lookback, Adaptive Period requires 64-bar warmup for stable values
- MQL5 ATR uses expanding window for first N bars (sum/period), not pandas rolling().mean()
- See `docs/reports/LAGUERRE_RSI_VALIDATION_SUCCESS.md ` for complete methodology

### v2.0.0 (startup.ini) - LEGACY ⚠️

**Status**: Deprecated (use v3.0.0 instead)

**Limitations**:
- ⚠️ **Conditional** - requires manual GUI initialization per symbol/timeframe
- Each new symbol must be opened in MT5 GUI once before headless works
- startup.ini `[StartUp]` section attaches to existing charts only (cannot create new charts)

**Recommendation**: Migrate to v3.0.0 for production use

## Research Context

**Historical Findings**: `docs/archive/historical.txt ` (2022-2025 community research)
**Archived Plans**: `docs/archive/HEADLESS_EXECUTION_PLAN.v2.0.0.archived.md ` (startup.ini approach)

## Project Status

- **Version**: 4.0.0 (File-based config COMPLETE 2025-10-17)
- **Headless Execution**: v3.0.0 (Python API PRODUCTION) + v4.0.0 (File-based config COMPLETE - GUI mode) + v2.1.0 (startup.ini parameter passing NOT VIABLE)
- **Workflow Matrix**:
  - **Manual GUI Exports**: v4.0.0 file-based config (no code editing, flexible parameters)
  - **Automated Headless**: v3.0.0 Python API (true headless, any symbol/timeframe)
  - **Custom Indicators**: v4.0.0 GUI mode only (Python API can't access indicator buffers)
- **Latest Validation**: Laguerre RSI - 1.000000 correlation, 5000-bar warmup (2025-10-17)
- **Python Indicators**: Laguerre RSI v1.0.0 (validated, production-ready)
- **Structure**: MT5 idiomatic hierarchy with project-based organization
- **Pruning Status** (2025-10-17 Phases 1-2 COMPLETE):
  - **Phase 1** (2025-10-17 08:00):
    - ✅ Archived 5 spike test files → `archive/experiments/`
    - ✅ Archived 8 completed plan documents → `archive/plans/`
    - ✅ Archived 3 outdated guides with version markers → `archive/docs/`
    - ✅ Added deprecation warning to `validate_export.py`
    - ✅ Updated CLAUDE.md (removed 3 guides, cleaned Single Source of Truth table)
  - **Phase 2** (2025-10-17 08:30):
    - ✅ Reorganized archive/indicators/ structure
    - ✅ Created separate subdirectories: laguerre_rsi/compiled, cc/compiled, cc/source, vwap/
    - ✅ Moved 3 Laguerre RSI .ex5 files to laguerre_rsi/compiled/
    - ✅ Moved 4 cc .ex5 files to cc/compiled/
    - ✅ Moved cc source files (.mq5, .md) to cc/source/
    - ✅ Moved vwap-multi.ex5 to vwap/
    - ✅ Removed empty compiled_orphans/ directory
  - **Impact**: 16 files archived (Phase 1), clean indicator organization (Phase 2)
  - **Next**: Phase 3-5 pruning available in `docs/reports/PRUNING_ASSESSMENT.md`
  - **Note**: Minor cleanup needed - 10 cc files remain in laguerre_rsi/development/ (can be addressed later)
- **Key Changes (2025-10-15)**:
  - MT5 idiomatic structure (Scripts/DataExport, Include/DataExport)
  - Project-based indicator folders (ProductionIndicators, PythonInterop, Libraries, Development)
  - Centralized Python workspace (users/crossover/)
  - ConsecutivePattern (cc) indicator with local dependencies
  - Single Custom/ folder structure
  - Legacy code archived (archive/)
- **Critical Discoveries**:
  - **2025-10-17**: v4.0.0 File-Based Config (COMPLETE - GUI mode)
    - Config reader working: 8 parameters successfully override defaults
    - Working copies pattern: Handles MQL5 const input limitation (create mutable copies in OnStart)
    - Config file location: `MQL5/Files/export_config.txt` (key=value format)
    - Baseline test validated: 101 lines (100 bars + header), SMA_14 column present
    - Headless limitation confirmed: startup.ini doesn't execute scripts reliably (same as v2.0.0)
    - Scope: GUI-based manual exports (complements v3.0.0 Python API for headless)
  - **2025-10-17**: v2.1.0 Startup.ini Parameter Passing (NOT VIABLE)
    - Named sections `[ScriptName]` NOT supported by MT5 (Windows + Wine)
    - ScriptParameters directive blocks execution with silent failure
    - .set preset files require: UTF-16LE BOM, MQL5/Presets/ location, `#property script_show_inputs`
    - File-based config reading is viable alternative (v4.0.0)
    - startup.ini config location: `C:\users\crossover\Config\` (not `Program Files/.../Config/`)
    - Script path resolution: MT5 adds "Scripts\" prefix automatically
    - Process management: Kill by PID (not name), verify termination, check both terminal64 and wineserver
  - **2025-10-17**: External Research Breakthroughs
    - MQL5 `/inc` parameter OVERRIDES (not augments) default include paths - omit unless using external includes
    - Script automation via `[StartUp]` config section with `ShutdownTerminal=1` for headless operation
    - Python MetaTrader5 API cannot access indicator buffers (no `copy_buffer()` or `create_indicator()`)
    - CrossOver path handling: spaces in paths break Wine compilation silently
  - **2025-10-17**: Python indicator validation methodology (historical warmup requirement)
  - **2025-10-17**: MQL5 ATR expanding window behavior (sum/period for first N bars)
  - **2025-10-17**: Perfect correlation (1.000000) achieved with 5000-bar warmup
  - **2025-10-13**: CX_BOTTLE environment variable requirement
  - **2025-10-13**: RSI formula fix (span → alpha)
  - **2025-10-13**: Column name normalization
  - **2025-10-13**: Path navigation patterns (macOS ↔ Wine)
  - **2025-10-13**: MT5 file locations fully documented
  - **2025-10-13**: CLI compilation via `--cx-app` and `--bottle` flags
  - **2025-10-13**: CrossOver path: `~/Applications/` not `/Applications/`
- **Documentation**: Complete empirical workflow guides
  - Production: `WINE_PYTHON_EXECUTION.md ` (v3.0.0 workflow)
  - File Paths: `MT5_FILE_LOCATIONS.md ` (indicator translation)
  - Refactoring: `MT5_IDIOMATIC_REFACTORING.md ` (project structure)

## Workflow Robustness Status

**Expansion Ready**: ✅ Partially Ready (for additional indicators)

**Strengths**:
- File location discovery (documented with absolute paths)
- Wine Python execution (v3.0.0 validated, CX_BOTTLE + WINEPREFIX)
- CLI compilation (CrossOver --cx-app, ~1s compile time)
- Validation pipeline (0.999+ correlation requirement, 5000-bar warmup methodology)
- Python indicator library (Laguerre RSI v1.0.0 validated at 1.000000 correlation)
- CSV export workflow (column normalization)
- Git tracking (organized structure)
- Path navigation (macOS ↔ Wine documented)

**Needs Improvement**:
- Dependency resolution (manual `#include` tracking)
- State management patterns (class-based indicator templates)
- Performance benchmarking (validation criteria)

**Resolved (2025-10-17)**:
- Python Indicator Validation Methodology - 5000-bar warmup requirement documented
- Laguerre RSI Python Implementation - v1.0.0 validated (1.000000 correlation)
- ATR Expanding Window Behavior - MQL5 behavior documented and replicated in Python
- Historical Data Fetching - Wine Python MT5 API method documented

**Resolved (2025-10-16)**:
- Temporal Leakage Audit - ATR Adaptive Laguerre RSI verified clean (no look-ahead bias)
- Indicator Renaming - ProductionIndicators (6) and PythonInterop (6) renamed with descriptive names

**Resolved (2025-10-15)**:
- Indicator Organization - Project-based hierarchy
- Python Workspace - Consolidated at users/crossover/
- ConsecutivePattern - Local dependencies preserved

**Resolved (2025-10-13)**:
- UTF-8 Encoding - MQL5 compiler accepts UTF-8 and UTF-16LE
- Laguerre RSI Bugs - Temporal violations, shared state, array indexing, price smoothing fixed
- CLI Compilation - CrossOver --cx-app flag method (~1s compile time)

**Next Steps**:
1. ✅ Validate Laguerre RSI Python implementation (COMPLETE: 1.000000 correlation)
2. ✅ Document historical warmup validation methodology (COMPLETE: see LAGUERRE_RSI_VALIDATION_SUCCESS.md)
3. Expand Python indicators library (additional indicators beyond Laguerre RSI)
4. Integrate Laguerre RSI with export_aligned.py
5. Test Laguerre RSI with multiple instance IDs on chart
6. Create class-based indicator API for real-time incremental updates

**Encoding Quick Reference**:
```python
# MQL5 compiler accepts BOTH UTF-8 and UTF-16LE (no conversion needed!)
# Prefer UTF-8 for easier editing and git diffs

# Read MQL5 file with automatic detection (recommended)
from pathlib import Path
import chardet
with Path(mq5_file).open('rb') as f:
    raw = f.read(10_000)
    encoding = chardet.detect(raw)['encoding']
content = Path(mq5_file).read_text(encoding=encoding)

# Or read with known encoding (UTF-16LE for original files)
content = Path(mq5_file).read_text(encoding='utf-16-le')

# Edit and save as UTF-8 (works perfectly for compilation)
Path(mq5_file).write_text(content, encoding='utf-8')
```

**CLI Compilation Quick Reference**:

**Critical Requirements**:
1. CrossOver path: `~/Applications/CrossOver.app` (NOT `/Applications/`)
2. File paths: Use simple names without spaces/parentheses (copy to C:/ root first)
3. Encoding: UTF-8 and UTF-16LE both work
4. Workflow: Copy → Compile → Verify log → Move .ex5 back (4-step process)

**Common Failure Modes**:
- Exit code 0 but no .ex5 file → Path has spaces/special chars
- Silent failure, no log entry → Wrong CrossOver path
- "invalid syntax" error → Unimplemented function prototypes
- "undefined function" error → Missing function implementations

**Working Workflow** (~1s compile time):
```bash
# Step 1: Copy to simple location (CRITICAL - paths with spaces FAIL)
BOTTLE="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5"
cp "ATR adaptive (extended) - FIXED.mq5" "$BOTTLE/drive_c/Indicator.mq5"

# Step 2: Compile (verify CrossOver path is ~/Applications NOT /Applications)
CX="$HOME/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine"
"$CX" --bottle "MetaTrader 5" --cx-app "C:/Program Files/MetaTrader 5/MetaEditor64.exe" \
  /log /compile:"C:/Indicator.mq5" /inc:"C:/Program Files/MetaTrader 5/MQL5"

# Step 3: Verify compilation (MUST check log AND .ex5 existence)
python3 << 'EOF'
from pathlib import Path
log = Path.home() / "Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/logs/metaeditor.log"
lines = log.read_text(encoding='utf-16-le').strip().split('\n')
print(lines[-1])  # Shows: "0 errors, 1 warnings, 1080 msec elapsed" on success
EOF
ls -lh "$BOTTLE/drive_c/Indicator.ex5"  # Verify .ex5 created (~25KB)

# Step 4: Move back to Custom Indicators
cp "$BOTTLE/drive_c/Indicator.ex5" \
   "$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/Your Indicator.ex5"
```

**Key Flags**:
- `--bottle "MetaTrader 5"` - CrossOver bottle-aware flag
- `--cx-app "C:/..."` - CrossOver app launcher
- `/log` - Enable compilation logging
- `/compile:"C:/file.mq5"` - Source file (forward slashes, simple path)
- `/inc:"C:/..."` - Include directory for MQL5 headers

See `docs/guides/MQL5_CLI_COMPILATION_SUCCESS.md ` for complete guide and automation script.

---

**Navigation Tip**: All paths are relative from project root. Use Cmd+click in Ghostty terminal for direct file access.
