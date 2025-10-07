# API Breaking Change: Threshold Granularity 1bps → 0.1bps

**Version**: 1.0.0
**Created**: 2025-10-03
**Status**: PLANNING
**Type**: BREAKING CHANGE (Major version bump required)

---

## Problem Statement

**Current API Constraint**: `threshold_bps: u32` with 1bps granularity (minimum 0.01%)

**User Requirement**: 480 bars/day from EURUSD data

**Math Analysis**:
```
EURUSD typical daily volatility: 0.5-1.0% (50-100 pips)
Target bars/day: 480
Required threshold: 0.5% ÷ 480 = 0.00104% ≈ 0.01bps

Current minimum threshold: 1bps = 0.01% → gives 50-100 bars/day
Gap: Need 10x finer granularity
```

**Root Cause**: Forex instruments (EURUSD) use 5 decimal places (pipettes), requiring sub-1bps thresholds for high-frequency bar generation.

---

## Proposed Solution

### Change Threshold Unit Definition

**Current Interpretation**:
- `threshold_bps: u32` where 1 unit = 1bps = 0.01%
- Example: `new(25, ...)` → 25bps = 0.25%

**New Interpretation**:
- `threshold_bps: u32` where 1 unit = 0.1bps = 0.001%
- Example: `new(250, ...)` → 250 × 0.1bps = 25bps = 0.25%

### Calculation Change

**Current Formula**:
```rust
let threshold_fraction = threshold_bps as f64 / 10_000.0;
// Example: 25 / 10000 = 0.0025 = 0.25%
```

**New Formula**:
```rust
let threshold_fraction = threshold_bps as f64 / 100_000.0;
// Example: 250 / 100000 = 0.0025 = 0.25%
```

**Alternative (clearer)**:
```rust
let threshold_fraction = (threshold_bps as f64 * 0.1) / 10_000.0;
// Example: (250 * 0.1) / 10000 = 25 / 10000 = 0.0025 = 0.25%
```

---

## Impact Analysis

### Breaking Changes

**1. API Signature** (no change, but semantics change):
```rust
// Before: threshold_bps in 1bps units
pub fn new(threshold_bps: u32, ...) -> Self

// After: threshold_bps in 0.1bps units (same signature, different meaning)
pub fn new(threshold_bps: u32, ...) -> Self
```

**2. User Code Migration**:
```rust
// Before (v2.x):
RangeBarProcessor::new(25)  // 25bps = 0.25%

// After (v3.x):
RangeBarProcessor::new(250) // 250 × 0.1bps = 25bps = 0.25%
```

**Migration multiplier**: All threshold values × 10

### Files Requiring Changes

**Core Library** (`src/`):
1. `src/core/processor.rs` - RangeBarProcessor threshold calculation
2. `src/providers/dukascopy/builder.rs` - DukascopyRangeBarBuilder (pass-through)
3. `src/providers/dukascopy/types.rs` - Documentation updates
4. `src/lib.rs` - Public API documentation

**Tests** (`tests/`):
1. `tests/dukascopy_eurusd_adversarial_audit.rs` - All threshold values × 10
2. `tests/integration_tests.rs` - If exists, update thresholds
3. Unit tests in `src/core/processor.rs` - Update threshold values

**Documentation** (`docs/`, root):
1. `CLAUDE.md` - Update examples with new threshold values
2. `CHANGELOG.md` - Breaking change entry
3. `docs/planning/` - Update all referenced threshold values

**Examples/Binaries** (`src/bin/`):
1. Any CLI tools using thresholds - Update default values

---

## Validation Criteria

### Backward Compatibility Verification

**Test Suite**:
```rust
// Old behavior (v2.x): new(25) → 25bps
// New behavior (v3.x): new(250) → 25bps
// Verify: new(250) produces identical results to old new(25)
```

**Approach**:
1. Run current test suite, capture bar counts
2. Apply changes (multiply thresholds by 10)
3. Run new test suite, verify identical bar counts
4. Any mismatch → calculation error, must fix

### New Capability Verification

**Ultra-Low Threshold Tests**:
```rust
// v3.x only: 0.1bps = 1 unit
DukascopyRangeBarBuilder::new(1, "EURUSD", ...)  // 0.1bps
DukascopyRangeBarBuilder::new(5, "EURUSD", ...)  // 0.5bps
DukascopyRangeBarBuilder::new(10, "EURUSD", ...) // 1bps (old minimum)
```

**Expected Results** (from previous analysis):
- 1 unit (0.1bps): ~500 bars/day (EURUSD moderate volatility)
- 5 units (0.5bps): ~100 bars/day
- 10 units (1bps): ~50 bars/day (current minimum)

---

## Implementation Plan

### Phase 1: Core Calculation Change

**File**: `src/core/processor.rs`

**Change**:
```rust
// BEFORE:
impl RangeBarProcessor {
    pub fn new(threshold_bps: u32) -> Self {
        let threshold_fraction = threshold_bps as f64 / 10_000.0;
        // ...
    }
}

// AFTER:
impl RangeBarProcessor {
    pub fn new(threshold_bps: u32) -> Self {
        // threshold_bps now in 0.1bps units (e.g., 250 = 25bps)
        let threshold_fraction = threshold_bps as f64 / 100_000.0;
        // ...
    }
}
```

**Documentation Change**:
```rust
/// Creates a new range bar processor
///
/// # Arguments
///
/// * `threshold_bps` - Threshold in **tenths of basis points** (0.1bps units)
///   - Example: `25` → 2.5bps = 0.025%
///   - Example: `250` → 25bps = 0.25%
///   - Minimum: `1` → 0.1bps = 0.001%
///
/// # Breaking Change (v3.0.0)
///
/// Prior to v3.0.0, `threshold_bps` was in 1bps units.
/// **Migration**: Multiply all threshold values by 10.
```

### Phase 2: Update All Tests

**Strategy**: Global search-replace with validation

**Pattern**:
```bash
# Find all RangeBarProcessor::new and DukascopyRangeBarBuilder::new calls
rg "::new\(\s*(\d+)\s*," --type rust

# For each match:
# - If value is threshold parameter
# - Multiply by 10
# - Update comment if present
```

**Example Migrations**:
```rust
// Before:
RangeBarProcessor::new(3)   → RangeBarProcessor::new(30)   // 3bps → 3bps
DukascopyRangeBarBuilder::new(5, ...) → DukascopyRangeBarBuilder::new(50, ...) // 5bps → 5bps
builder = Builder::new(25, ...) → builder = Builder::new(250, ...) // 25bps → 25bps
```

**Files to Update**:
- `tests/dukascopy_eurusd_adversarial_audit.rs`
- `src/core/processor.rs` (unit tests)
- `src/providers/dukascopy/builder.rs` (unit tests)
- Any integration tests

### Phase 3: Add Ultra-Low Threshold Tests

**File**: `tests/dukascopy_eurusd_adversarial_audit.rs`

**New Test Cases**:
```rust
// Test ultra-low thresholds (0.1bps - 1bps)
let mut builder_01bps = DukascopyRangeBarBuilder::new(1, "EURUSD", ...);   // 0.1bps
let mut builder_05bps = DukascopyRangeBarBuilder::new(5, "EURUSD", ...);   // 0.5bps
let mut builder_1bps = DukascopyRangeBarBuilder::new(10, "EURUSD", ...);   // 1bps (old minimum)

// Expected bar counts (from 38K ticks, ~1 day):
// 0.1bps: ~500 bars
// 0.5bps: ~100 bars
// 1bps: ~50 bars
```

### Phase 4: Update Documentation

**Files**:
1. `CLAUDE.md` - Update all threshold examples
2. `CHANGELOG.md` - Add breaking change entry
3. `docs/planning/dukascopy-eurusd-audit-plan.md` - Update threshold values
4. `README.md` (if exists) - Update examples

**CHANGELOG Entry**:
```markdown
## [3.0.0] - 2025-10-03

### Breaking Changes

- **Threshold Granularity**: Changed `threshold_bps` parameter interpretation from 1bps units to 0.1bps units
  - **Migration Required**: Multiply all threshold values by 10
  - Example: `new(25, ...)` (v2.x) → `new(250, ...)` (v3.x) for same 25bps threshold
  - **Rationale**: Enable ultra-low thresholds (0.1-0.9bps) for forex instruments with 5 decimal precision
  - **Minimum threshold**: Now 0.1bps (1 unit) vs 1bps (1 unit) previously
  - **Impact**: All RangeBarProcessor and DukascopyRangeBarBuilder usage

### Added

- Support for ultra-low thresholds: 0.1bps minimum (enables 400-600 bars/day for EURUSD)
- New test coverage for 0.1bps - 1bps range

### Migration Guide

```rust
// v2.x code:
let processor = RangeBarProcessor::new(25);  // 25bps
let builder = DukascopyRangeBarBuilder::new(10, "EURUSD", Strict); // 10bps

// v3.x code (multiply thresholds by 10):
let processor = RangeBarProcessor::new(250);  // 25bps (same behavior)
let builder = DukascopyRangeBarBuilder::new(100, "EURUSD", Strict); // 10bps (same behavior)

// v3.x new capability:
let builder = DukascopyRangeBarBuilder::new(1, "EURUSD", Strict);  // 0.1bps (NEW)
let builder = DukascopyRangeBarBuilder::new(5, "EURUSD", Strict);  // 0.5bps (NEW)
```
```

### Phase 5: Version Bump

**Files**:
- `Cargo.toml` - Update version: `2.2.0` → `3.0.0`
- `.cz.toml` - Update version if using Commitizen

---

## Risk Assessment

### Risk 1: Silent Behavioral Change
**Scenario**: User updates to v3.0.0 without migration, gets 10x more bars than expected
**Likelihood**: High (breaking change)
**Mitigation**:
- Major version bump (v3.0.0) signals breaking change
- Clear CHANGELOG entry with migration guide
- Update CLAUDE.md prominently

### Risk 2: Floating-Point Precision Issues
**Scenario**: Ultra-low thresholds (0.1bps) cause precision errors in calculations
**Likelihood**: Low (f64 has sufficient precision for 5 decimal places)
**Mitigation**:
- Test with real data at 0.1bps threshold
- Verify bar counts match expectations
- Monitor for precision drift in long-running tests

### Risk 3: Test Suite Failures After Migration
**Scenario**: Missed threshold updates cause test failures
**Likelihood**: Medium (manual search-replace error-prone)
**Mitigation**:
- Automated search with `rg` for all `::new` calls
- Run full test suite after each file update
- Verify bar counts match pre-migration baseline

### Risk 4: Documentation Inconsistency
**Scenario**: Some docs updated, others missed, causing confusion
**Likelihood**: Medium (many doc files)
**Mitigation**:
- Comprehensive file list in this plan
- Search for "bps" in all markdown files
- Update all references consistently

---

## Success Criteria

### Must Have (P0)

- ✅ Core calculation changed: `threshold_bps / 100_000.0`
- ✅ All existing tests pass with updated threshold values (× 10)
- ✅ Bar counts identical pre/post migration (for same effective threshold)
- ✅ Ultra-low threshold tests (0.1bps - 1bps) added and passing
- ✅ CHANGELOG entry documenting breaking change
- ✅ Version bumped to 3.0.0

### Should Have (P1)

- ✅ All documentation updated (CLAUDE.md, planning docs)
- ✅ Migration guide in CHANGELOG
- ✅ API documentation updated (/// comments)
- ✅ EURUSD 480 bars/day target achieved with 0.1bps threshold

### Nice to Have (P2)

- ✅ Automated migration script for users
- ✅ Deprecation warning in v2.3.0 (if pre-release window)
- ✅ Blog post or detailed migration guide

---

## Execution Checklist

**Pre-Implementation**:
- [ ] Review this plan for completeness
- [ ] User approval on breaking change approach
- [ ] Baseline current test results (bar counts at each threshold)

**Implementation**:
- [ ] Phase 1: Update `src/core/processor.rs` calculation
- [ ] Phase 1: Update `src/providers/dukascopy/builder.rs` docs
- [ ] Phase 2: Update all test threshold values (× 10)
- [ ] Phase 3: Add ultra-low threshold tests (0.1bps - 1bps)
- [ ] Phase 4: Update CHANGELOG.md with breaking change entry
- [ ] Phase 4: Update CLAUDE.md examples
- [ ] Phase 4: Update planning docs
- [ ] Phase 5: Bump version to 3.0.0

**Validation**:
- [ ] Run full test suite: `cargo test --all-features`
- [ ] Verify bar counts match baseline (for equivalent thresholds)
- [ ] Run EURUSD audit test with 0.1bps threshold
- [ ] Verify 400-600 bars/day achieved @ 0.1bps
- [ ] Clippy clean: `cargo clippy -- -D warnings`
- [ ] Documentation builds: `cargo doc --no-deps`

**Post-Implementation**:
- [ ] Commit with conventional commit: `feat!: change threshold granularity to 0.1bps`
- [ ] Tag release: `git tag v3.0.0`
- [ ] Update tracker document with results
- [ ] Update NEXT_STEPS.md with completion status

---

## Alternative Approaches Considered

### Alternative 1: Add New Parameter (Rejected)
```rust
pub fn new(threshold_bps: u32, granularity: BpsGranularity) -> Self
// where BpsGranularity = OneBps | TenthBps
```
**Rejected**: API clutter, confusing for users

### Alternative 2: Use f64 for threshold_bps (Rejected)
```rust
pub fn new(threshold_bps: f64, ...) -> Self
```
**Rejected**: Breaking change anyway, f64 less clear than scaled u32

### Alternative 3: New Threshold Type (Rejected)
```rust
pub struct Threshold { tenths_of_bps: u32 }
impl Threshold {
    pub fn from_bps(bps: f64) -> Self { ... }
}
```
**Rejected**: Over-engineered for simple use case

### Selected Approach: Reinterpret u32 Units
**Rationale**:
- Minimal API surface change
- Clear migration path (× 10)
- Enables ultra-low thresholds without type complexity
- Consistent with integer-based precision (avoids f64 ambiguity)

---

## References

- **Parent Plan**: `docs/planning/dukascopy-eurusd-ultra-low-threshold.md`
- **Audit Plan**: `docs/planning/dukascopy-eurusd-audit-plan.md`
- **Implementation Tracker**: `docs/planning/dukascopy-eurusd-audit-implementation.md`
- **Core Processor**: `src/core/processor.rs`
- **Dukascopy Builder**: `src/providers/dukascopy/builder.rs`
- **Test File**: `tests/dukascopy_eurusd_adversarial_audit.rs`
- **Current Version**: 2.2.0
- **Target Version**: 3.0.0 (breaking change)
