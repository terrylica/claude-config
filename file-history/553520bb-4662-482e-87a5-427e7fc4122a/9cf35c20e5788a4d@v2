# Strategic Plan Corrections

**Version**: 1.1.0
**Date**: 2025-10-16
**Status**: Active corrections to STRATEGIC_PLAN.md v1.0.0

---

## Correction 1: CSV I/O Priority (Section 2.1)

**Original claim** (STRATEGIC_PLAN.md lines 136-173):
> ### 2.1 CSV I/O Consolidation (HIGH PRIORITY)
> **SOTA Alternative**: Polars native CSV codec
> **Estimated Impact**: Performance: 5-10x faster CSV loading

**Correction** (2025-10-16):
- ❌ **INCORRECT PRIORITY**: CSV consolidation is NOT high priority
- ❌ **SPECULATIVE CLAIM**: "5-10x improvement" has no profiling evidence
- ❌ **WRONG CONTEXT**: CSV is testing-only, not production format

**Corrected understanding**:
- ✅ **Production formats**: Parquet, Arrow (already implemented via polars)
- ✅ **CSV role**: Testing/debugging only (human-readable inspection)
- ✅ **Current state**: Adequate for testing needs (polars_benchmark.rs:84 uses `csv` crate)
- ✅ **Priority**: LOW or SKIP (not on critical path)

**Impact**:
- Hybrid Plan Phase 1 Action 4 **rejected** (2-3 days saved)
- Focus redirected to valuable work (Action 5: ADR documentation)

**Rationale**:
1. **No evidence of bottleneck**: No profiling data showing CSV is slow
2. **Not on critical path**: CSV is not used for production output
3. **Premature optimization**: Classic "measure first, optimize later" violation
4. **Weak ROI**: 2-3 days investment for unknown benefit on non-critical code

---

## Optimization Validation Checklist

**Before adding optimization work to plans**, verify:

1. ✅ **Evidence**: Profiling data showing actual bottleneck (not theoretical)
2. ✅ **Impact**: On critical path for production use cases
3. ✅ **ROI**: Clear benefit justifies time investment
4. ✅ **User need**: Solves real user pain point (not developer curiosity)

**Red flags** (skip the optimization):
- ❌ Claims like "5-10x improvement" without measurements
- ❌ "HIGH PRIORITY" based on library capabilities, not user needs
- ❌ Optimizing testing utilities instead of production code
- ❌ "Should be faster" without profiling current performance

---

## CSV Usage Guideline

**Production use cases** (performance-critical):
- ❌ DO NOT use CSV for production output
- ✅ USE Parquet (70% compression, columnar storage)
- ✅ USE Arrow IPC (zero-copy Python transfer)

**Testing/debugging use cases** (human inspection):
- ✅ CSV is appropriate (human-readable, easy to inspect)
- ✅ Current `csv` crate is adequate (not a bottleneck)
- ✅ polars_benchmark.rs already uses `csv` crate for loading test data

---

## References

- Original plan: `/Users/terryli/eon/rangebar/STRATEGIC_PLAN.md`
- Corrected implementation: `/Users/terryli/eon/rangebar/docs/planning/current/hybrid-plan-phase1.md`
- Action 4 rejection: hybrid-plan-phase1.md lines 209-223
- Learnings: hybrid-plan-phase1.md lines 351-370
