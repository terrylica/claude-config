# MT5 Reference Hub

**Purpose**: Single navigation point for AI agent task discovery
**Version**: 1.0.0
**Last Updated**: 2025-10-17

---

## Decision Tree

### Export Market Data

```
Need custom indicators?
├─ NO → WINE_PYTHON_EXECUTION.md (v3.0.0, FULLY AUTOMATED)
└─ YES → V4_FILE_BASED_CONFIG_WORKFLOW.md (v4.0.0, SEMI-AUTOMATED, GUI required)

Symbol/timeframe never opened in GUI?
├─ YES → v3.0.0 only (cold start supported)
└─ NO → v3.0.0 or v4.0.0 both work
```

### Compile MQL5 File

```
Source file in terminal's MQL5/ directory?
├─ YES → MQL5_CLI_COMPILATION_SUCCESS.md (omit /inc parameter)
└─ NO → MQL5_CLI_COMPILATION_SUCCESS.md (use /inc parameter)

Path has spaces?
├─ YES → Copy to simple path first (EXTERNAL_RESEARCH_BREAKTHROUGHS.md, line 118-165)
└─ NO → Compile directly
```

### Read MQL5 File

```
Know encoding?
├─ YES → read_text(encoding='utf-16-le' or 'utf-8')
└─ NO → MQL5_ENCODING_SOLUTIONS.md (auto-detect with chardet)
```

### Validate Python Indicator

```
Correlation ≥0.999?
├─ YES → SUCCESS
└─ NO → Check:
    ├─ Warmup: 5000+ bars? → LAGUERRE_RSI_VALIDATION_SUCCESS.md
    ├─ NaN values? → LESSONS_LEARNED_PLAYBOOK.md (Gotcha #4)
    └─ Pandas behavior? → PYTHON_INDICATOR_VALIDATION_FAILURES.md
```

### Pass Parameters to MQL5 Script

```
Which version?
├─ v3.0.0 → CLI args (no config file needed)
├─ v4.0.0 → export_config.txt (V4_FILE_BASED_CONFIG_WORKFLOW.md)
└─ v2.0.0 → NOT VIABLE (SCRIPT_PARAMETER_PASSING_RESEARCH.md)
```

---

## Canonical Source Map

**See**: `CLAUDE.md` - Single Source of Truth table

Quick index by concern:
- 🚀 **Workflows**: MQL5_TO_PYTHON_MIGRATION_GUIDE, LESSONS_LEARNED_PLAYBOOK
- 🗺️ **Paths**: MT5_FILE_LOCATIONS (BOTTLE_ROOT, directory structure)
- 🔤 **Encoding**: MQL5_ENCODING_SOLUTIONS (UTF-8/UTF-16LE detection)
- ⚙️ **Compilation**: MQL5_CLI_COMPILATION_SUCCESS, EXTERNAL_RESEARCH_BREAKTHROUGHS (/inc trap)
- 🍷 **Wine**: CROSSOVER_MQ5 (environment, mq5c tool)
- 📋 **Configuration**: SCRIPT_PARAMETER_PASSING_RESEARCH (startup.ini), MQL5_PRESET_FILES_RESEARCH (.set format)
- 📊 **Validation**: LAGUERRE_RSI_VALIDATION_SUCCESS (5000-bar warmup), PYTHON_INDICATOR_VALIDATION_FAILURES

---

## Automation Matrix

| Task | Document | Automation Level | Manual Steps |
|------|----------|------------------|--------------|
| Export OHLCV | WINE_PYTHON_EXECUTION | FULLY AUTOMATED | None |
| Export with indicators | V4_FILE_BASED_CONFIG_WORKFLOW | SEMI-AUTOMATED | Open symbol in GUI once |
| Compile MQL5 | MQL5_CLI_COMPILATION_SUCCESS | FULLY AUTOMATED | None |
| Validate indicator | LAGUERRE_RSI_VALIDATION_SUCCESS | FULLY AUTOMATED | None |
| Find file paths | MT5_FILE_LOCATIONS | N/A (reference) | None |
| Read MQL5 encoding | MQL5_ENCODING_SOLUTIONS | FULLY AUTOMATED | None (chardet) |
| Kill MT5 processes | CROSSOVER_MQ5, LESSONS_LEARNED_PLAYBOOK | MANUAL | 3-step process |
| Create .set file | MQL5_PRESET_FILES_RESEARCH | MANUAL GUI | Generate via MT5 GUI |
| Migrate indicator | MQL5_TO_PYTHON_MIGRATION_GUIDE | SEMI-AUTOMATED | Manual algorithm analysis |

---

## Consolidated Paths

**BOTTLE_ROOT** (canonical): `/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5`
(See: MT5_FILE_LOCATIONS.md for complete reference)

**Common Paths**:
```bash
# MT5 executables
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/terminal64.exe
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MetaEditor64.exe

# MQL5 source tree
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/

# Indicators
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/

# Wine Python
$BOTTLE_ROOT/drive_c/Program Files/Python312/python.exe
$BOTTLE_ROOT/drive_c/users/crossover/export_aligned.py

# Logs
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/logs/
$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Logs/

# CrossOver wine
~/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine
```

---

## Hard-Learned Gotchas (Quick Reference)

**See**: LESSONS_LEARNED_PLAYBOOK.md for complete details

### Critical (Read First)
1. `/inc` parameter OVERRIDES (not augments) → EXTERNAL_RESEARCH_BREAKTHROUGHS.md
2. Spaces in paths = silent failure → MQL5_CLI_COMPILATION_SUCCESS.md
3. 5000-bar warmup required for validation → LAGUERRE_RSI_VALIDATION_SUCCESS.md
4. Pandas `rolling()` ≠ MQL5 behavior → PYTHON_INDICATOR_VALIDATION_FAILURES.md

### Compilation
- Exit code 0 but no .ex5 → Path has spaces/parentheses
- 102 errors → `/inc` parameter used incorrectly
- UTF-16LE log encoding → Use metaeditor.log reader in MQL5_CLI_COMPILATION_SUCCESS.md

### Validation
- Correlation ~0.95 → Missing historical warmup
- NaN in first N bars → Expected (warmup period)
- Different values per timeframe → Shared state bug (separate instances required)

### Wine Environment
- CX_BOTTLE required → WINE_PYTHON_EXECUTION.md
- CrossOver path: `~/Applications/` NOT `/Applications/`
- Kill by PID, not name → LESSONS_LEARNED_PLAYBOOK.md Gotcha #8

---

## Common Task Workflows

### Export Data (Most Common)
1. v3.0.0: WINE_PYTHON_EXECUTION.md → ~7s, no GUI
2. v4.0.0: V4_FILE_BASED_CONFIG_WORKFLOW.md → ~8s, GUI required

### Compile MQL5 (Second Most Common)
1. MQL5_CLI_COMPILATION_SUCCESS.md → ~1s
2. Check: Path simple? `/inc` omitted?

### Validate Indicator (Third Most Common)
1. Fetch 5000+ bars → WINE_PYTHON_EXECUTION.md
2. Calculate Python indicator on all bars
3. Compare with MQL5 export → LAGUERRE_RSI_VALIDATION_SUCCESS.md
4. Check correlation ≥0.999

### Migrate Indicator (Complete Workflow)
1. MQL5_TO_PYTHON_MIGRATION_GUIDE.md (7 phases, 2-4 hours)
2. Pre-read: LESSONS_LEARNED_PLAYBOOK.md (5 min, saves 50+ hours)
3. Template: INDICATOR_MIGRATION_CHECKLIST.md

---

## Time Estimates

| Task | First Time | Subsequent |
|------|------------|------------|
| Migrate indicator | 2-4 hours | 1-2 hours |
| Export data (v3.0.0) | 6-8 seconds | 6-8 seconds |
| Export data (v4.0.0) | 8 seconds | 8 seconds |
| Compile MQL5 | ~1 second | ~1 second |
| Validate indicator | 5-10 min | 5-10 min |
| Find file paths | <1 min | <1 min |
| Read gotchas | 5 min (critical) | - |

---

## Critical Reading Order (New Agent Onboarding)

**35 minutes to avoid 50+ hours of debugging**:

1. LESSONS_LEARNED_PLAYBOOK.md (Gotchas 1-8) - 10 min
2. MQL5_TO_PYTHON_MIGRATION_GUIDE.md (Overview + Common Pitfalls) - 15 min
3. WINE_PYTHON_EXECUTION.md (Path Navigation) - 5 min
4. MT5_FILE_LOCATIONS.md (Critical Paths) - 5 min

---

## Version History

**v1.0.0** (2025-10-17):
- Initial hub creation
- 100+ scenarios extracted from 12 guides
- Decision trees for 5 common workflows
- Canonical source map aligned with CLAUDE.md
- Automation matrix for all documented tasks
- Consolidated paths (zero duplication)
- Hard-learned gotchas quick reference

**Next Review**: After 5 indicator migrations
