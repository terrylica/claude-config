# Universal Validation Architecture - Implementation Plan

**Version**: 1.3.0
**Created**: 2025-10-16
**Updated**: 2025-10-16 (Script automation discovery, fully automated workflow)
**Status**: In Progress
**SLO Target**: Availability 100%, Correctness 100%, Observability 100%, Maintainability 100%

---

## Objective

Replace indicator-specific validation scripts with universal registry-driven architecture using DuckDB for validation history.

**Success Criteria**:
- Laguerre RSI validation: MQL5 vs Python correlation ≥ 0.999
- Existing export_aligned.py usage unchanged (backward compatibility)
- Single source of truth: registry.yaml for all indicators

---

## Architecture

**UPDATED**: MT5 Python API does not support `create_indicator()` (Spike 1 discovery)

### Components

1. **Configuration**: `indicators/registry.yaml` - Indicator metadata + parameter mappings
2. **MQL5 Export**: `LaguerreRSIModule.mqh` + `ExportAligned.mq5` - Export indicator buffers to CSV
3. **Automation**: `generate_mt5_config.py` - Generate MT5 startup config files
4. **Orchestration**: `run_validation.py` - End-to-end validation orchestration
5. **Validation**: `validate_indicator.py` - Universal validation script
6. **Storage**: `validation.ddb` - DuckDB database for validation history

### Data Flow

```
Python Orchestrator
    ↓
Generate config.ini ([StartUp] Script=..., ShutdownTerminal=1)
    ↓
terminal64.exe /config:config.ini (automated)
    ↓
MT5 Terminal → ExportAligned.mq5 → iCustom() → MQL5 buffer values → CSV export
    ↓
Terminal shuts down
    ↓
validate_indicator.py loads CSV
    ↓
Python recalculates indicator values
    ↓
Compare MQL5 vs Python (correlation, MAE, RMSE)
    ↓
Store metrics in validation.ddb
    ↓
Query results via SQL views
```

---

## Service Level Objectives

| SLO | Target | Measurement |
|-----|--------|-------------|
| **Availability** | 100% | All 20 workspace files accessible |
| **Correctness** | 100% | Correlation ≥ 0.999 between MQL5 and Python |
| **Observability** | 100% | All validation runs tracked in DuckDB |
| **Maintainability** | 100% | Single registry.yaml, no indicator-specific scripts |

---

## Implementation Phases

### Phase 0: Spike Validation (Status: ❌ Spike 1 FAILED - Architecture Revised)

**Spike 1 Result**: ❌ FAILED
- **Assumption**: MT5 Python API supports `mt5.create_indicator()` + `mt5.copy_buffer()`
- **Finding**: MetaTrader5 module has NO such methods
- **Available methods**: Only trading ops, OHLC/tick data (copy_rates, copy_ticks), account management
- **Impact**: Must use MQL5 CSV export approach instead of Python API buffer access
- **Action**: Revised architecture to use `LaguerreRSIModule.mqh` + extend `ExportAligned.mq5`

**Remaining Spikes**: Registry YAML (Spike 2), DuckDB performance (Spike 3), Backward compat (Spike 4)
- Status: Deferred (not critical for MQL5 export approach)

**CLI Compilation Discovery** (2025-10-16 21:46):
- **Finding**: `/inc` parameter BREAKS compilation by overriding default include search
- **Solution**: Omit `/inc` parameter for scripts in MQL5 directory structure
- **Working Command**: `metaeditor64.exe /log /compile:"C:/SimpleName.mq5"`
- **Result**: ExportAligned.mq5 with LaguerreRSIModule compiled successfully (0 errors, 892ms)

**Script Automation Discovery** (2025-10-16 22:00, Research Audit):
- **Previous Assumption**: MQL5 scripts require manual GUI execution
- **Finding**: MT5 supports automated script execution via `[StartUp]` configuration
- **Method**: `terminal64.exe /config:config.ini` with `[StartUp] Script=..., ShutdownTerminal=1`
- **Source**: Official MT5 documentation (metatrader5.com/en/terminal/help/start_advanced/start)
- **Impact**: Enables fully automated validation workflow (no manual steps)
- **Limitation**: Script input parameters cannot be passed via config.ini (must use .set files or defaults)

---

### Phase 1: Core Infrastructure (Status: ✅ COMPLETE)

**Files Created**:
- ✅ `Include/DataExport/modules/LaguerreRSIModule.mqh` - MQL5 module for Laguerre RSI export
- ✅ `Scripts/DataExport/ExportAligned.mq5` - Extended with Laguerre RSI support
- ✅ `Scripts/DataExport/ExportAligned.ex5` - Compiled successfully (23KB)

**Dependencies Installed**:
- ✅ `duckdb==1.4.1` - Analytical database
- ✅ `pyyaml==6.0.3` - YAML parsing

**Files Created**:
- ✅ `validation_schema.sql` - DuckDB schema (4 tables, 3 views)
- ✅ `validate_indicator.py` - Universal validation script

**SLO Impact**: Maintainability +100% (modular indicator export system)

---

### Phase 2: Automation Integration (Status: ⏳ In Progress)

**Files to Create**:
- `generate_mt5_config.py` - Generate MT5 startup config.ini files
- `run_validation.py` - End-to-end validation orchestrator

**Automation Workflow**:
1. Generate config.ini with `[StartUp]` section (Script, Symbol, Period, ShutdownTerminal)
2. Execute `terminal64.exe /config:config.ini` (script runs with default parameters, terminal closes)
3. Load exported CSV and run `validate_indicator.py`
4. Store results in `validation.ddb`

**Parameter Limitation**:
- MT5 config.ini does NOT support passing script input parameters
- Scripts use default values from source code (e.g., InpUseLaguerreRSI=false, InpBars=5000)
- Workaround: Modify defaults and recompile, or use .set preset files (requires additional automation)

**SLO Impact**: Availability 100% (automated with default parameters)

---

### Phase 3: Validation Testing (Status: ⏳ Pending)

**Scenarios**:
- Baseline: EURUSD M1, 5000 bars
- Parameters: SMMA, LWMA variations
- Symbols: XAUUSD H1, GBPUSD H4

**SLO Impact**: Correctness 100% (correlation ≥ 0.999)

---

### Phase 4: Documentation (Status: ⏳ Pending)

**Files to Create**:
- `docs/guides/VALIDATION_WORKFLOW.md`
- `validation_report.py`

**SLO Impact**: Observability 100% (all runs queryable)

---

## Dependencies

**Python Packages** (OSS):
- `duckdb` - Analytical database (columnar storage, SQL analytics)
- `pyyaml` - YAML parsing (configuration)
- `MetaTrader5` - MT5 Python API (already installed)
- `pandas` - DataFrame operations (already installed)
- `numpy` - Numerical computing (already installed)

**Installation**:
```bash
CX_BOTTLE="MetaTrader 5" \
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
wine "C:\\Program Files\\Python312\\python.exe" -m pip install duckdb pyyaml
```

---

## Risks & Mitigations

### CRITICAL: MT5 Python API Compatibility

**Risk**: `mt5.create_indicator()` may fail with custom indicators
**Detection**: Spike 1 test result
**Mitigation**: Error propagates, implementation halts if spike fails
**Fallback**: None (requirement violation)

### HIGH: Python/MQL5 Value Mismatch

**Risk**: Correlation < 0.999
**Detection**: Phase 3 validation tests
**Mitigation**: Error propagates, debug bar-by-bar in DuckDB
**Fallback**: None (correctness SLO violation)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-10-16 | Initial plan | AI Agent |
| 1.1.0 | 2025-10-16 | Spike 1 failure, architecture revised to MQL5 CSV export | AI Agent |
| 1.2.0 | 2025-10-16 | Phase 1 complete, CLI compilation discovery, dependencies installed | AI Agent |
| 1.3.0 | 2025-10-16 | Script automation discovery via research audit, fully automated workflow | AI Agent |

---

## References

- Laguerre RSI Implementation: `indicators/laguerre_rsi.py`
- MQL5 Source: `PythonInterop/ATR_Adaptive_Laguerre_RSI.mq5`
- Existing Validation: `validate_export.py` (RSI-only, to be superseded)
- DuckDB Spike: `duckdb_validation_spike.py` (proof of concept)

---

## Next Actions

1. ✅ Execute Spike 1: MT5 Python API custom indicator access (FAILED - revised architecture)
2. ✅ Create LaguerreRSIModule.mqh and extend ExportAligned.mq5
3. ✅ Install DuckDB and PyYAML dependencies
4. ✅ Create validation.ddb schema (SQL DDL)
5. ✅ Create validate_indicator.py (universal validation script)
6. ⏳ Create generate_mt5_config.py (config.ini generator)
7. ⏳ Create run_validation.py (end-to-end orchestrator)
8. ⏳ Test automated workflow (EURUSD M1, 100 bars baseline)
9. ⏳ Test full validation (EURUSD M1, 5000 bars)
10. ⏳ Document workflow in VALIDATION_WORKFLOW.md
