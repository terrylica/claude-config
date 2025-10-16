# mql5-crossover Project Memory

**Architecture**: Link Farm + Hub-and-Spoke with Progressive Disclosure

## Navigation Index

**Entry Point**: `/Users/terryli/eon/mql5-crossover/README.md ` - Project overview and quick start

## Core Guides

- **[QUICKSTART.md](docs/guides/QUICKSTART.md)** - 5-minute setup and validation
- **[WINE_PYTHON_EXECUTION.md](docs/guides/WINE_PYTHON_EXECUTION.md)** - v3.0.0 Wine Python execution (production) - CX_BOTTLE, path navigation, RSI formula, diagnostics
- **[MT5_FILE_LOCATIONS.md](docs/guides/MT5_FILE_LOCATIONS.md)** - Complete MT5 file paths and indicator translation workflow
- **[MQL5_ENCODING_SOLUTIONS.md](docs/guides/MQL5_ENCODING_SOLUTIONS.md)** - MQL5 encoding guide - UTF-8/UTF-16LE both work, chardet, Git integration, Python patterns
- **[LAGUERRE_RSI_ANALYSIS.md](docs/guides/LAGUERRE_RSI_ANALYSIS.md)** - ATR Adaptive Smoothed Laguerre RSI - Complete algorithm breakdown and Python translation guide
- **[LAGUERRE_RSI_SHARED_STATE_BUG.md](docs/guides/LAGUERRE_RSI_SHARED_STATE_BUG.md)** - ✅ Fixed: Shared laguerreWork array - Separate instances for normal/custom timeframe (root cause)
- **[LAGUERRE_RSI_ARRAY_INDEXING_BUG.md](docs/guides/LAGUERRE_RSI_ARRAY_INDEXING_BUG.md)** - ✅ Fixed: Series indexing direction - Loop backwards for proper EMA calculation
- **[LAGUERRE_RSI_BUG_FIX_SUMMARY.md](docs/guides/LAGUERRE_RSI_BUG_FIX_SUMMARY.md)** - ✅ Fixed: Price smoothing bug - All MA methods now work in custom timeframe mode
- **[LAGUERRE_RSI_BUG_REPORT.md](docs/guides/LAGUERRE_RSI_BUG_REPORT.md)** - Original bug report (EMA vs SMA inconsistency) - RESOLVED
- **[MQL5_CLI_COMPILATION_SUCCESS.md](docs/guides/MQL5_CLI_COMPILATION_SUCCESS.md)** - CLI compilation via CrossOver --cx-app flag (~1s compile time, production-ready)
- **[AI_AGENT_WORKFLOW.md](docs/guides/AI_AGENT_WORKFLOW.md)** - Complete development workflow for AI agents
- **[CROSSOVER_MQ5.md](docs/guides/CROSSOVER_MQ5.md)** - MT5/CrossOver technical reference and shell setup (v2.0.0 legacy)
- **[BOTTLE_TRACKING.md](docs/guides/BOTTLE_TRACKING.md)** - CrossOver bottle file tracking via X: drive mapping

## Implementation Plans

- **[HEADLESS_EXECUTION_PLAN.md](docs/plans/HEADLESS_EXECUTION_PLAN.md)** - v3.0.0 Python API approach (COMPLETE)
  - **Supersedes**: v2.0.0 startup.ini approach (conditionally working only)
  - **Key Achievement**: True headless execution without GUI initialization
  - **Status**: All 5 phases complete, cold start validated

## Validation Reports

- **[VALIDATION_STATUS.md](docs/reports/VALIDATION_STATUS.md)** - Current SLO metrics and test results
- **[SUCCESS_REPORT.md](docs/reports/SUCCESS_REPORT.md)** - Manual and headless validation (0.999902 correlation)

## Architecture

### Directory Structure

```
mql5/          # MQL5 source (Scripts/, Include/, Samples/)
python/        # Python validation tools
scripts/       # Automation (mq5run wrapper for v2.0.0)
docs/          # Documentation (guides/, plans/, reports/, archive/)
config/        # MT5 configuration files
exports/       # CSV outputs (gitignored)
logs/          # Execution logs (gitignored)
```

### Single Source of Truth

| Topic                       | Authoritative Document                  |
| --------------------------- | --------------------------------------- |
| Quick Start                 | `docs/guides/QUICKSTART.md`             |
| Wine Python Execution (v3.0.0) | `docs/guides/WINE_PYTHON_EXECUTION.md`  |
| MT5 File Paths & Translation | `docs/guides/MT5_FILE_LOCATIONS.md`     |
| MQL5 Encoding (UTF-8/UTF-16LE) | `docs/guides/MQL5_ENCODING_SOLUTIONS.md` |
| Laguerre RSI Algorithm & Translation | `docs/guides/LAGUERRE_RSI_ANALYSIS.md` |
| Laguerre RSI Shared State Bug (ROOT CAUSE) | `docs/guides/LAGUERRE_RSI_SHARED_STATE_BUG.md` |
| Laguerre RSI Array Indexing Bug | `docs/guides/LAGUERRE_RSI_ARRAY_INDEXING_BUG.md` |
| Laguerre RSI Price Smoothing Bug | `docs/guides/LAGUERRE_RSI_BUG_FIX_SUMMARY.md` |
| Laguerre RSI Original Bug Report | `docs/guides/LAGUERRE_RSI_BUG_REPORT.md` |
| MQL5 CLI Compilation (Production) | `docs/guides/MQL5_CLI_COMPILATION_SUCCESS.md` |
| Development Workflow        | `docs/guides/AI_AGENT_WORKFLOW.md`      |
| MT5/CrossOver Setup (v2.0.0) | `docs/guides/CROSSOVER_MQ5.md`          |
| Bottle File Tracking        | `docs/guides/BOTTLE_TRACKING.md`        |
| Headless Execution Plan     | `docs/plans/HEADLESS_EXECUTION_PLAN.md` |
| Validation Status           | `docs/reports/VALIDATION_STATUS.md`     |
| Historical Context          | `docs/archive/historical.txt`           |

## Key Commands

```bash
# Compile MQL5 (CLI - production method)
CX="~/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine"
BOTTLE="MetaTrader 5"
ME="C:/Program Files/MetaTrader 5/MetaEditor64.exe"
"$CX" --bottle "$BOTTLE" --cx-app "$ME" /log /compile:"C:/YourIndicator.mq5" /inc:"C:/Program Files/MetaTrader 5/MQL5"

# Compile MQL5 (GUI fallback)
mq5c mql5/Scripts/ExportAligned.mq5

# Export data (v3.0.0 - true headless, PRODUCTION)
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" \
  "C:\\users\\crossover\\export_aligned.py" \
  --symbol EURUSD --period M1 --bars 5000

# Copy CSV to repo
cp "$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/exports/Export_EURUSD_PERIOD_M1.csv" exports/

# Export data (v2.0.0 - LEGACY, requires GUI initialization)
./scripts/mq5run --symbol EURUSD --period PERIOD_M1

# Validate
python python/validate_export.py exports/Export_EURUSD_PERIOD_M1.csv
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
- **CX_BOTTLE environment variable** (mandatory for CrossOver's wine wrapper)
- MT5 terminal running and logged in
- Correct RSI formula: `alpha=1/period` (not `span=period`)
- Validator with column name normalization

**Capabilities**:
- ✅ **True headless** - works for ANY symbol/timeframe without GUI initialization
- ✅ Cold start validated: USDJPY M1 (0.999920 correlation)
- ✅ Programmatic symbol selection via `mt5.symbol_select()`
- ✅ Direct data fetch via `mt5.copy_rates_from_pos()`

**Critical Path Operations**:
- macOS → Wine execution: Use `CX_BOTTLE` + `WINEPREFIX` + wine command
- Python script paths: Windows-style `C:\users\crossover\...`
- CSV copy: macOS native paths `~/Library/.../drive_c/users/...`
- See `docs/guides/WINE_PYTHON_EXECUTION.md ` for complete path navigation guide

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

- **Version**: 1.0.0 (reorganization complete 2025-10-13)
- **Headless Execution**: v3.0.0 PRODUCTION (Python API, true headless validated)
- **Latest Validation**: USDJPY M1 cold start - 0.999920 RSI correlation (2025-10-13 19:45)
- **Critical Discoveries**:
  - CX_BOTTLE environment variable requirement
  - RSI formula fix (span → alpha)
  - Column name normalization
  - Path navigation patterns (macOS ↔ Wine)
  - MT5 file locations fully documented
  - CLI compilation via `--cx-app` and `--bottle` flags
  - CrossOver path: `~/Applications/` not `/Applications/`
- **Structure**: Clean organized hierarchy with SLO compliance
- **Documentation**: Complete empirical workflow guides
  - Production: `WINE_PYTHON_EXECUTION.md ` (v3.0.0 workflow)
  - File Paths: `MT5_FILE_LOCATIONS.md ` (indicator translation)

## Workflow Robustness Status

**Expansion Ready**: ✅ Partially Ready (for additional indicators)

**Strengths**:
- ✅ File location discovery (fully documented with absolute paths)
- ✅ Wine Python execution (v3.0.0 validated, CX_BOTTLE + WINEPREFIX)
- ✅ CLI compilation (production-ready via CrossOver --cx-app, ~1s compile time)
- ✅ Validation pipeline (0.999+ correlation requirement)
- ✅ CSV export workflow (automated with column normalization)
- ✅ Git tracking (organized repo structure)
- ✅ Path navigation (macOS ↔ Wine contexts documented)

**Needs Improvement**:
- ⚠️ Dependency resolution (manual `#include` tracking)
- ⚠️ Indicator library structure (need `python/indicators/` modules)
- ⚠️ State management patterns (need class-based indicator templates)
- ⚠️ Performance benchmarking (add to validation criteria)

**Recently Resolved**:
- ✅ **UTF-8 Encoding Discovery** (2025-10-13 23:53): UTF-8 works perfectly for MQL5 compilation - no conversion needed! Previous UTF-16LE requirement was incorrect.
- ✅ **Laguerre RSI Temporal Violations** (2025-10-13 23:53): Fixed `atrWork[i+1]` future bar access - removed cache, always recalculate from historical data
- ✅ **Laguerre RSI Instance Isolation** (2025-10-13 23:53): Added `inpInstanceID` parameter to separate static array memory between indicator instances
- ✅ **Laguerre RSI Shared State Bug** (2025-10-13 22:44): Fixed - Separate instances for normal vs custom timeframe. See `LAGUERRE_RSI_SHARED_STATE_BUG.md `
- ✅ **Laguerre RSI Price Smoothing Bug** (2025-10-13 22:29): Fixed - All MA methods (SMA, EMA, SMMA, LWMA) now work in custom timeframe. See `LAGUERRE_RSI_BUG_FIX_SUMMARY.md `
- ✅ **Laguerre RSI Array Indexing Bug** (2025-10-13 22:34): Fixed - Series indexing direction corrected. See `LAGUERRE_RSI_ARRAY_INDEXING_BUG.md `
- ✅ **CLI Compilation** (2025-10-13 22:25): Production-ready method via CrossOver `--cx-app` flag. See `MQL5_CLI_COMPILATION_SUCCESS.md `

**Next Steps for "ATR adaptive smoothed Laguerre RSI 2 (extended) - FIXED_COMPLETE.mq5"**:
1. ✅ UTF-8 encoding (SOLVED: MQL5 compiler accepts UTF-8 directly, no conversion needed)
2. ✅ Extract calculation logic and dependencies (COMPLETE: see `LAGUERRE_RSI_ANALYSIS.md `)
3. ✅ Fix MQL5 price smoothing bug (COMPLETE: see `LAGUERRE_RSI_BUG_FIX_SUMMARY.md `)
4. ✅ Fix MQL5 array indexing bug (COMPLETE: see `LAGUERRE_RSI_ARRAY_INDEXING_BUG.md `)
5. ✅ Fix MQL5 shared state bug (COMPLETE: see `LAGUERRE_RSI_SHARED_STATE_BUG.md `)
6. ✅ Fix temporal violations (COMPLETE: removed `atrWork[i+1]` cache, always recalculate)
7. ✅ Add instance isolation parameter (COMPLETE: `inpInstanceID` prevents shared static arrays)
8. ✅ CLI compilation (COMPLETE: LaguerreRSI_Fixed_Complete.ex5, 25KB, 0 errors, 1 warning, 1.1s)
9. 🔄 Test on M1 chart with different instance IDs (IN PROGRESS: need Instance ID "B" for second indicator)
10. ⏳ Create `python/indicators/laguerre_rsi.py` module (implement all 4 MA methods)
11. ⏳ Integrate with `export_aligned.py`
12. ⏳ Validate correlation ≥ 0.999 between fixed MQL5 and Python implementation

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

**CLI Compilation Quick Reference** (Hard-Learned Truths from Trial & Error):

**Critical Requirements** (11+ failed attempts before success):
1. ❗ CrossOver path: `~/Applications/CrossOver.app` (NOT `/Applications/` - path error causes silent failure)
2. ❗ File paths: MUST use simple names without spaces/parentheses (copy to C:/ root first)
3. ✅ Encoding: UTF-8 works perfectly (UTF-16LE also works, no conversion needed)
4. ❗ Workflow: Copy → Compile → Verify log → Move .ex5 back (4-step mandatory)

**Common Failure Modes & Solutions**:
- ❌ Exit code 0 but no .ex5 file → Path has spaces/special chars, copy to `C:/SimpleName.mq5`
- ❌ Silent failure, no log entry → Wrong CrossOver path, verify `~/Applications/CrossOver.app` exists
- ❌ "invalid syntax" error → Check for unimplemented function prototypes or actual syntax errors
- ❌ "undefined function" error → Missing function implementations (declarations not enough)

**Working Workflow** (production-ready, ~1s compile time):
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

**Key Flags** (after 11+ failed methods, these work):
- `--bottle "MetaTrader 5"` - CrossOver bottle-aware flag (required)
- `--cx-app "C:/..."` - CrossOver app launcher (not plain wine)
- `/log` - Enable compilation logging
- `/compile:"C:/file.mq5"` - Source file (forward slashes, simple path)
- `/inc:"C:/..."` - Include directory for MQL5 headers

See `docs/guides/MQL5_CLI_COMPILATION_SUCCESS.md ` for complete guide, troubleshooting, and automation script.

See `docs/guides/MT5_FILE_LOCATIONS.md ` for complete indicator translation workflow and robustness audit.

---

**Navigation Tip**: All paths are relative from project root. Use Cmd+click in Ghostty terminal for direct file access.
