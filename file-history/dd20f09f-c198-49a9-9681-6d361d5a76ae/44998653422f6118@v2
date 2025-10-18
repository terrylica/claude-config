# Rangebar Codebase - Quick Reference

## Essential Facts

**Project**: Non-lookahead bias range bar construction for crypto & forex trading
**Version**: 5.0.0 (Rust 1.90)
**Total Code**: ~17,075 LOC + ~4,091 LOC tests

## Key Metrics

```
Crates:           8 (modular workspace)
Binaries:         6 CLI tools
Tests:            10 integration test files
Documentation:    30 markdown files
Archived Code:    59 files (src-archived/v4.0.0)
Testing Coverage: Excellent (real data + synthetic)
Unsafe Code:      0 instances
Quality Score:    HIGH
```

## Core Algorithm

**Algorithm**: Fixed-point threshold breach detection
- Thresholds calculated from bar OPEN price only (non-lookahead bias)
- Breach when price moves ±threshold_bps from OPEN
- Breaching trade included in closing bar
- Next bar opens with following trade

**Critical Invariant**:
```
(high_breach → close_breach) AND (low_breach → close_breach)
```

## File Locations

| Component | Location | LOC |
|-----------|----------|-----|
| Core Algorithm | `crates/rangebar-core/src/processor.rs` | 841 |
| Fixed-Point Arithmetic | `crates/rangebar-core/src/fixed_point.rs` | 259 |
| Type Definitions | `crates/rangebar-core/src/types.rs` | 406 |
| Timestamp Handling | `crates/rangebar-core/src/timestamp.rs` | 152 |
| Binance Provider | `crates/rangebar-providers/src/binance/` | ~400 |
| Exness Provider | `crates/rangebar-providers/src/exness/` | ~300 |
| CLI Tools | `crates/rangebar-cli/src/bin/` | 98K total |
| Integration Tests | `crates/rangebar/tests/` | 4,091 |

## All 6 Binaries

1. **tier1-symbol-discovery** - Tier-1 crypto symbol identification
2. **data-structure-validator** - Cross-market data format validation
3. **spot-tier1-processor** - Spot market processing
4. **parallel-tier1-analysis** - Parallel analytics engine
5. **polars-benchmark** - DataFrame performance testing
6. **temporal-integrity-validator** - Timestamp format validation

## Temporal Logic Patterns

### Safe Patterns
- ✓ Zero-duration bars (open_time == close_time) allowed
- ✓ Timestamp ordering validation pre-condition check
- ✓ Cross-year boundary handling tested
- ✓ Explicit timezone/DST handling via chrono

### Potential Risks (Mitigated)
- ⚠ Floating-point intermediate in turnover calc (cast to i128 → safe)
- ⚠ 13-digit vs 16-digit timestamp detection (threshold: 10^13, validated)
- ⚠ CSV format variations (detected and handled)

## Data Sources

### Binance (Primary - Crypto)
- Markets: Spot, UM Futures, CM Futures
- Tier-1: 18 instruments across all markets
- Format: 16-digit microsecond timestamps
- Data: aggTrades nomenclature only

### Exness (Primary - Forex)
- Instrument: EURUSD Standard
- Format: ZIP→CSV with Bid/Ask/Timestamp
- Frequency: ~1.26M ticks/month
- Years: 2019-2025+

## Dependencies

**Core (No Python)**:
- `serde/serde_json` - Serialization
- `chrono` - Time handling
- `thiserror` - Error types

**Async**:
- `tokio` - Runtime
- `rayon` - Data parallelism

**Data**:
- `polars` - DataFrame/Parquet
- `csv`, `zip` - Format handling

**No Python dependencies** - Pure Rust

## Breaking Changes

### v3.0.0 (Basis Points)
- `threshold_bps` unit changed: 1bps → 0.1bps
- Migration: multiply all threshold values by 10
- Example: `250` means 25bps (was 250bps)

## Testing

### Test Coverage
✓ Real data (BTCUSDT, ETHUSDT)
✓ Synthetic scenarios
✓ Boundary conditions
✓ Cross-year transitions
✓ Memory stability
✓ Forex validation (Exness EURUSD)

### Key Test Files
- `integration_test.rs` - Primary validation
- `boundary_consistency_tests.rs` - Edge cases
- `cross_year_speed_comparison.rs` - Performance
- `exness_eurusd_integration_test.rs` - Forex

## Documentation Quality

**Hub-and-Spoke Architecture**:
- `/docs/planning/current/` - Active development
- `/docs/planning/architecture/` - Algorithm specs
- `/docs/development/` - Process guides
- `/docs/archive/` - Historical audits

**Recent phases documented**:
- Phase 1: CSV loader implementation
- Phase 2: Test generator centralization
- Phase 3: Real data migration
- Phase 4: Focused real data tests
- Phase 5: In progress

## Known Issues

1. **Volume Conservation** (Disabled)
   - Currently disabled in tests
   - TODO: Re-enable when processor complete

2. **StatisticalEngine** (Refactored)
   - Legacy statistics module restructured
   - Tests disabled pending documentation

3. **ExportRangeBarProcessor** (Duplicate)
   - Legacy implementation still maintained
   - Duplicates core algorithm logic
   - Kept for backward compatibility

## Recommendations

### Immediate
1. Re-enable volume conservation validation
2. Document statistical engine refactoring
3. Consolidate duplicate algorithm code

### Short-term
1. Migrate CSV I/O to `polars` native codec
2. Migrate from `chrono` to `time` crate
3. Archive `src-archived/` as Git tag

### Long-term
1. Unified statistics pipeline via `polars`
2. Production deployment hardening
3. Additional forex pair support (if needed)

---

**Last Updated**: October 16, 2025
**Survey**: `CODEBASE_SURVEY.md` (full report)
