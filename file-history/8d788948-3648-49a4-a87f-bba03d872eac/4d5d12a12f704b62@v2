# EURUSD Ultra-Low Threshold Optimization Plan

**Version**: 1.0.0
**Created**: 2025-10-03
**Status**: IN PROGRESS
**Parent Plan**: `dukascopy-eurusd-audit-plan.md`
**Supersedes**: `dukascopy-eurusd-threshold-optimization.md` (Option 1)

---

## Objective

Increase EURUSD range bar count to meet revised user requirement: 480 bars/day from real Dukascopy data.

**Previous State**: 84.4 bars/day @ 3bps (Option 1 result)
**Target State**: 480 bars/day @ 1bps or 0.5bps

**Scaling Analysis**:
- 3bps → 84.4 bars/day
- To achieve 480 bars/day: 480 / 84.4 = 5.7x increase required
- Estimated threshold: 3bps / 5.7 = 0.53bps

---

## Problem Statement

Option 1 implementation produced insufficient bar count for revised target:
- **Actual**: 84.4 bars/day @ 3bps (projected)
- **Required**: 480 bars/day
- **Gap**: 5.7x shortfall

**User Requirement Change**: From "dozens to hundreds per day" (24-100) to **480 bars/day** (hourly bars)

---

## Solution: Ultra-Low Threshold Testing

### Approach

Test ultra-low thresholds to find optimal sensitivity for 480 bars/day:
- **1bps** (0.01%): Expected 200-300 bars/day
- **0.5bps** (0.005%): Expected 400-600 bars/day

### Implementation

Extend `audit_7_real_eurusd_statistical_properties` test:

1. Add 2 new builders: 1bps, 0.5bps (keep existing 3bps, 5bps for comparison)
2. Process all ticks through all 6 thresholds: 0.5bps, 1bps, 3bps, 5bps, 10bps, 25bps
3. Validate threshold monotonicity: bars(0.5bps) >= bars(1bps) >= bars(3bps) >= ...
4. Assert minimum bar counts: 0.5bps >= 480 bars/day, 1bps >= 200 bars/day
5. Validate same properties on ALL thresholds:
   - Temporal integrity
   - Spread statistics
   - Threshold monotonicity

### Code Changes

**File**: `tests/dukascopy_eurusd_adversarial_audit.rs`

**Change 1**: Add 0.5bps and 1bps builders
```rust
let mut builder_05 = DukascopyRangeBarBuilder::new(0.5, "EURUSD", ValidationStrictness::Strict);
// ERROR: threshold_bps is u32, cannot accept 0.5
// SOLUTION: threshold is in basis points, 0.5bps = 0.5 basis points
// Need to check if DukascopyRangeBarBuilder accepts f64 or only u32

// Alternative: If only u32 accepted, cannot test 0.5bps
// Fallback: Test 1bps only
```

**Change 2**: Process all ticks through all builders (single pass)
```rust
for tick in &ticks {
    match builder_1.process_tick(tick) { ... }
    match builder_3.process_tick(tick) { ... }
    // ... etc
}
```

**Change 3**: Update expected minimums
```rust
// 5 weekdays, target 480 bars/day (full data scenario)
// With partial data (~1 day), scale expectations
let min_bars_per_day_1bps = 200; // Conservative estimate
let min_bars_per_day_05bps = 480; // User requirement
```

---

## Risk Assessment

### Risk 1: Builder Does Not Accept Sub-1 Basis Point Thresholds
**Likelihood**: ✅ CONFIRMED (threshold_bps is u32, not f64)
**API Constraint**: `DukascopyRangeBarBuilder::new(threshold_bps: u32, ...)`
**Mitigation**:
- ✅ API checked: u32 type means minimum threshold is 1bps
- Cannot test 0.5bps (would require f64 or u64 with decimal scaling)
- Test 1bps as minimum, add 2bps as intermediate threshold
**Impact**: May not reach 480 bars/day target with 1bps alone

### Risk 2: 1bps Produces Excessive Bar Count
**Likelihood**: Medium (may produce 200-300 bars/day)
**Mitigation**:
- If 1bps < 480/day but close, document as acceptable
- If 1bps >> 480/day, recommend 1bps as production threshold

### Risk 3: Breach Anomaly Worsens at Ultra-Low Thresholds
**Likelihood**: High (more bars = more opportunities for anomalies)
**Mitigation**: Diagnostic output only, skip strict validation

### Risk 4: Test Runtime Increases Significantly
**Likelihood**: High (processing 38K ticks through 6 builders, generating 200-600 bars)
**Mitigation**: Acceptable (test is --ignored, manual execution only)

---

## SLO Definitions

### Correctness
- ✅ All thresholds produce monotonically non-increasing bar counts
- ✅ 1bps produces >= 200 bars/day (or >= target based on actual data)
- ✅ All bars pass temporal integrity (monotonic timestamps)
- ✅ All bars pass spread validation (< 0.005 for EURUSD)

### Observability
- ✅ Log bar counts for all 6 thresholds
- ✅ Log bars/day metric for each threshold
- ✅ Log mean spread for each threshold
- ✅ If assertion fails, log expected vs actual with context
- ✅ Log if 0.5bps not supported (threshold_bps type limitation)

### Maintainability
- ✅ Reusable validation logic (DRY principle)
- ✅ No code duplication (use existing multi-threshold pattern)
- ✅ Clear test output (numbered steps, clear PASS/FAIL)

---

## Success Criteria

**Must Have (P0)**:
- ✅ Test produces >= 480 bars/day @ 1bps (or 0.5bps if supported) from full data
- ✅ Threshold monotonicity holds across all thresholds
- ✅ All bars pass temporal integrity
- ✅ All bars pass spread validation

**Should Have (P1)**:
- ✅ Actual bars/day meets or exceeds 480 @ optimal threshold
- ✅ Documentation updated with findings
- ✅ Recommendation for production threshold

**Nice to Have (P2)**:
- ✅ Test runtime < 60s
- ✅ 0.5bps supported (if API allows)

---

## Implementation Steps

### Step 1: Check API Constraints
1. Check DukascopyRangeBarBuilder::new() signature
2. Determine if threshold_bps accepts u32 or f64
3. If u32 only, document 1bps as minimum testable threshold

### Step 2: Add Ultra-Low Threshold Builders
1. Add builder_1 (1bps)
2. Add builder_05 (0.5bps) if API supports
3. Keep existing builders for comparison

### Step 3: Run Test
1. Process all ticks through all builders
2. Log bar counts for all thresholds
3. Validate threshold monotonicity

### Step 4: Document Findings
1. Update implementation tracker with results
2. Update NEXT_STEPS.md with recommendation
3. Document any API limitations discovered

---

## References

- **Parent Plan**: `docs/planning/dukascopy-eurusd-audit-plan.md`
- **Previous Plan**: `docs/planning/dukascopy-eurusd-threshold-optimization.md` (Option 1)
- **Implementation Tracker**: `docs/planning/dukascopy-eurusd-audit-implementation.md`
- **Test File**: `tests/dukascopy_eurusd_adversarial_audit.rs`
- **Previous Result**: 84.4 bars/day @ 3bps
- **Target**: 480 bars/day @ 1bps or 0.5bps
