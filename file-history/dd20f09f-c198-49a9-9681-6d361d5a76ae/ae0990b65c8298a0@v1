# Rangebar Codebase Survey - Complete Index

## Navigation Guide

This folder contains a comprehensive survey of the rangebar codebase completed October 16, 2025.

### Documents

**Full Technical Survey**
- 📄 **`CODEBASE_SURVEY.md`** - Complete 16KB technical analysis
  - 13 major sections covering architecture, algorithms, testing, dependencies
  - Detailed findings on temporal logic, potential issues, SOTA recommendations
  - Read this for: Deep technical understanding, decision-making context

**Quick Reference** 
- 📄 **`SURVEY_QUICK_REFERENCE.md`** - Executive summary (2-3 min read)
  - Essential facts, metrics, file locations
  - All 6 binaries with purposes
  - Known issues and recommendations
  - Read this for: Quick lookup, onboarding, decision reminders

---

## Key Findings Summary

### Workspace Structure
```
✓ 8 specialized crates (modular, clean separation)
✓ 6 focused CLI binaries (each with single purpose)
✓ 4,091 LOC of integration tests (excellent coverage)
✓ 30 markdown documentation files (well-organized)
ℹ 59 archived files from v4.0.0 (preserved for reference)
```

### Core Algorithm
```
- Threshold breach detection using fixed-point arithmetic
- Thresholds calculated from bar OPEN only (non-lookahead bias)
- Invariant: (high_breach → close_breach) AND (low_breach → close_breach)
- Implementation: RangeBarProcessor (primary), ExportRangeBarProcessor (legacy)
```

### Code Quality
```
✓ Zero unsafe blocks (pure Rust)
✓ Fixed-point precision (no floating-point precision loss)
✓ Comprehensive validation (sorting, temporal, format)
✓ Excellent test coverage (real + synthetic data)
⚠ 183 unwrap() instances (mostly in test code)
⚠ 1 TODO comment (volume conservation re-enable)
```

### Temporal Logic
```
✓ Explicit timestamp normalization (13-digit ms → 16-digit μs)
✓ Cross-year boundary testing (DST, leap seconds)
✓ Zero-duration bars validated (intentional, tested)
✓ Timestamp ordering validation (pre-condition check)
⚠ Floating-point turnover calc (mitigated: cast to i128)
```

### Data Integrity
```
✓ Non-lookahead bias enforced
✓ Market microstructure tracked (buy/sell segregation)
✓ Volume tracking enabled
✓ Trade ID range preservation
⚠ Volume conservation check currently disabled
```

---

## Critical File Locations

| What | Where | LOC |
|------|-------|-----|
| **Core Algorithm** | `crates/rangebar-core/src/processor.rs` | 841 |
| **Fixed-Point Arithmetic** | `crates/rangebar-core/src/fixed_point.rs` | 259 |
| **Type Definitions** | `crates/rangebar-core/src/types.rs` | 406 |
| **Timestamp Handling** | `crates/rangebar-core/src/timestamp.rs` | 152 |
| **Binance Provider** | `crates/rangebar-providers/src/binance/` | ~400 |
| **Exness Provider** | `crates/rangebar-providers/src/exness/` | ~300 |
| **6 CLI Tools** | `crates/rangebar-cli/src/bin/` | 98K |
| **Integration Tests** | `crates/rangebar/tests/` | 4,091 |
| **Archived v4.0.0** | `src-archived/` | 59 files |
| **Documentation** | `docs/` | 30 files |

---

## Critical Algorithms to Understand

### 1. Threshold Breach Detection
Location: `processor.rs::process_agg_trade_records()`
```
for each trade:
  if trade.price breaches (upper_threshold OR lower_threshold):
    close current bar
    start new bar with this trade
  else:
    update current bar OHLCV
```

### 2. Fixed-Point Thresholds
Location: `fixed_point.rs::compute_range_thresholds()`
```
delta = (price * threshold_bps) / 100_000
upper = price + delta
lower = price - delta
// v3.0.0: threshold_bps now in 0.1bps units (multiply by 10 from v2)
```

### 3. Timestamp Normalization
Location: `timestamp.rs::normalize_timestamp()`
```
if timestamp < 10_000_000_000_000:  // 13-digit boundary
  return timestamp * 1_000         // 13-digit ms → 16-digit μs
else:
  return timestamp                 // Already 16-digit μs
```

---

## Temporal Logic Patterns

### Safe Patterns ✓
- Zero-duration bars (open_time == close_time)
- Explicit timestamp ordering validation
- Cross-year boundary handling
- Timezone/DST via chrono

### Mitigated Risks ⚠
- Floating-point intermediate (cast to i128 prevents loss)
- 13-digit vs 16-digit detection (threshold: 10^13)
- CSV format variations (detected by validator)
- Unsorted trades (pre-condition validated)

---

## All 6 Binaries

1. **tier1-symbol-discovery** (22K)
   - Identifies Tier-1 crypto instruments (18 total)
   - Validates across Spot + 2 Futures markets
   - Output: comprehensive or minimal format

2. **data-structure-validator** (25K)
   - Cross-market data format validation
   - Quarterly sampling across 2022-2025
   - SHA256 checksum verification
   - Parallel workers (default 8)

3. **spot-tier1-processor** (14K)
   - Spot-specific processing pipeline
   - Real data integration

4. **parallel-tier1-analysis** (21K)
   - Parallel analytics across Tier-1
   - Comprehensive reporting

5. **polars-benchmark** (8.7K)
   - DataFrame performance analysis
   - Parquet operations testing

6. **temporal-integrity-validator** (8.4K)
   - Timestamp format detection
   - Boolean format consistency
   - Multi-year validation

---

## Dependency Overview

**Core (Minimal)**:
- serde/json (serialization)
- chrono (time handling)
- thiserror (error types)

**Async/Concurrency**:
- tokio 1.0 (runtime)
- rayon 1.11 (parallelism)

**Data Processing**:
- polars 0.51 (DataFrame, Parquet, lazy)
- csv 1.3 (parsing)
- zip 2.2 (archives)

**Validation**:
- md5 0.7 (checksums)
- sha2 0.10 (verification)

**Web (Optional)**:
- axum 0.7 (framework)
- utoipa 4.2 (OpenAPI)

**NO Python dependencies** - Pure Rust

---

## Recent Development (Last 20 Commits)

- feat: add focused real data tests (Phase 4)
- fix: relocate workspace tests/ to crates/rangebar/tests/
- refactor: replace synthetic data with real CSV data (Phase 3)
- refactor: centralize test helpers to generators.rs (Phase 1.5)
- feat: add CSV loader for real test data (Phase 1)

---

## Known Technical Debt

### High Priority
1. **Volume Conservation** (Disabled)
   - Currently disabled in `integration_test.rs`
   - Re-enable when processor complete

2. **StatisticalEngine** (Refactored)
   - Legacy statistics module restructured
   - Tests disabled pending documentation

### Medium Priority
3. **Duplicate Code**
   - ExportRangeBarProcessor duplicates algorithm
   - Consolidate into single implementation

4. **CSV Consolidation**
   - Use polars native codec for all CSV I/O
   - Reduce dependency count

### Low Priority
5. **Archived Code**
   - 59 files in src-archived/
   - Could be Git-archived as tagged reference

---

## Documentation Resources

### In This Repository
- **Full Survey**: `CODEBASE_SURVEY.md`
- **Quick Ref**: `SURVEY_QUICK_REFERENCE.md`
- **Planning**: `/docs/planning/` (architecture, research)
- **Development**: `/docs/development/` (guides, migration)
- **Archive**: `/docs/archive/` (historical audits)

### Algorithm References
- Algorithm Spec: `/docs/planning/architecture/algorithm-spec.md`
- Breaking Changes: `/docs/development/MIGRATION.md`
- Test Cleanup Plan: `/docs/planning/test-cleanup-plan-v2-llm-friendly.md`

---

## Version History

- **v5.0.0** (Current) - Modular workspace, 8 crates
- **v4.0.0** - Monolithic structure (archived in src-archived/)
- **v3.0.0** - Basis points granularity change (0.1bps units)

---

## Recommended Next Steps

### Immediate
1. Re-enable volume conservation validation
2. Document statistical engine refactoring
3. Consolidate duplicate algorithm code

### Short-term
1. Migrate CSV I/O to polars native
2. Update chrono → time migration
3. Archive src-archived/ as Git tag

### Long-term
1. Unified statistics pipeline via polars
2. Production hardening
3. Additional forex support (if needed)

---

**Survey Completed**: October 16, 2025
**Codebase Version**: 5.0.0 (Rust 1.90)
**Total Analysis**: 17,075 LOC crates + 4,091 LOC tests
**Quality Assessment**: HIGH - Well-structured, comprehensive testing, excellent documentation

For questions, refer to the full survey at `/Users/terryli/eon/rangebar/CODEBASE_SURVEY.md`
