# Next Steps - Post-Restructuring v5.0.0

**Status**: Workspace migration complete
**Date**: 2025-10-11

---

## Completed ✅

1. **Workspace Restructuring (v5.0.0)**
   - 8-crate modular architecture
   - Provider pattern (Binance, Exness)
   - Data management (data/, cache/, output/ with READMEs)
   - 108+ tests passing
   - All clippy warnings fixed
   - Backward compatibility via meta-crate

2. **Documentation**
   - Updated CLAUDE.md with v5.0.0 structure
   - Migration plan complete
   - Documentation audit (3 rounds)

---

## Immediate Action Items

### 1. Investigate 4 Pre-Existing Test Failures (Unrelated to EURUSD Audit)

**Failing Tests**:
1. `engines::batch::engine::tests::test_single_symbol_analysis`
2. `engines::batch::engine::tests::test_multiple_symbols_analysis`
3. `infrastructure::io::formats::tests::test_dataframe_to_rangebar_conversion`
4. `infrastructure::io::formats::tests::test_rangebar_to_rangebar_conversion`

**Error Pattern**:
```
called `Result::unwrap()` on an `Err` value: ValueExtractionFailed {
    operation: "extract_f64_at_index_3",
    source: "Unexpected type: Null"
}
```

**Root Cause**: Likely test data has NULL values in Polars DataFrame columns

**Investigation**:
```bash
# Run single test with backtrace:
RUST_BACKTRACE=1 cargo test --lib engines::batch::engine::tests::test_single_symbol_analysis -- --nocapture

# Check test data generation:
rg "test_single_symbol_analysis" src/engines/batch/engine.rs -A 30
```

**Likely Fix**: Update test data to avoid NULL values or handle them gracefully

---

### 4. Validate No Regressions

**Full Test Suite**:
```bash
# All features enabled
cargo test --all-features

# No default features (minimal)
cargo test --no-default-features

# Specific feature combinations
cargo test --features polars-io
cargo test --features polars-analytics
cargo test --features streaming-stats
```

**Clippy (strict)**:
```bash
cargo clippy --all-features -- -D warnings
```

**Build (release)**:
```bash
cargo build --release --all-features
```

---

## Suggested Improvements

### Short-term (This Week)

1. **Fix 4 failing tests** - batch/io test failures (NULL values in DataFrame)
2. **Add regression detection CI** (optional) - Template for GitHub Actions
3. **Multi-instrument validation** - Test across crypto and forex pairs

### Medium-term (This Month)

1. **Cross-validation with Binance** - Compare range bars across different markets
2. **Property-based testing** - Add proptest for core algorithm
3. **Chaos engineering** - Inject faults (missing ticks, crossed markets, duplicates)

### Long-term (This Quarter)

1. **Differential testing** - Reference implementation for comparison
2. **Production monitoring** - Daily validation in CI/CD
3. **Performance profiling** - Benchmark provider throughput

---

## Risk Assessment

### Critical (P0) - Must Fix Before Production

- ✅ **Clippy warnings** - FIXED
- ⚠️ **4 failing tests** - Need investigation (batch/io tests)

### High (P1) - Fix Soon

- **Limited edge case coverage** - Need fuzzing/property tests
- **Cross-validation needed** - Compare providers across markets

### Medium (P2) - Nice to Have

- **No performance benchmarks** - Provider throughput comparison
- **Manual test execution** - Need CI automation
- **Limited multi-instrument testing** - Expand coverage

---

## Questions for User

1. **Next Priority**: Investigate 4 pre-existing test failures or other focus area?
2. **CI/CD Integration**: Implement GitHub Actions workflow for automated validation?
3. **Additional Instruments**: Which symbols/pairs should be validated next?

---

## References

- **Migration Doc**: `docs/planning/workspace-migration-v5.0.0.md`
- **Architecture**: CLAUDE.md - Module Structure section
