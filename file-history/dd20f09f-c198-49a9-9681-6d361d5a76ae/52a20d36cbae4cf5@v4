# Workspace Migration Plan v5.0.0

**Status**: ✅ Complete
**Start Date**: 2025-10-04
**Completion Date**: 2025-10-11 (7 days actual)
**Version**: rangebar v4.0.0 → v5.0.0

## SLOs

### Availability
- Zero downtime for library users (backward compatibility via meta-crate)
- All 7 CLI binaries remain functional throughout migration
- CI/CD pipeline passes at each phase completion

### Correctness
- All 16 existing test suites pass without modification
- No behavioral changes to core algorithm
- Identical output for identical inputs (verified via golden tests)

### Observability
- Each phase creates git commit with structured message
- Migration tracking via `docs/planning/workspace-migration-v5.0.0.md`
- Dependency graph documented in each crate's README

### Maintainability
- Maximum 3 levels of dependency depth (core → provider → engine)
- Each crate compiles independently
- Clear separation of concerns (no circular dependencies)

---

## Dependency Graph (Surveyed 2025-10-04)

```
Level 0: core/fixed_point.rs (447 LOC) ← NO dependencies
Level 1: core/types.rs (405 LOC) ← fixed_point
Level 2: core/processor.rs, core/timestamp.rs (1,023 LOC) ← types, fixed_point
Level 3: providers/* (3,700 LOC) ← core ONLY
Level 3: infrastructure/config (1,009 LOC) ← core/fixed_point ONLY
Level 3: infrastructure/io (977 LOC) ← core
Level 4: engines/streaming (2,130 LOC) ← core, providers/binance
Level 4: engines/batch (798 LOC) ← core, infrastructure/io
Level 5: infrastructure/api (147 LOC) ← everything
Level 5: binaries (2,000+ LOC) ← everything
```

**Total**: ~10,160 LOC in src/ (excluding binaries)

---

## Workspace Structure

```
rangebar/
├── Cargo.toml (workspace root)
├── crates/
│   ├── rangebar-core/        # Core algorithm (Level 0-2)
│   ├── rangebar-providers/    # Data providers (Level 3)
│   ├── rangebar-config/       # Configuration (Level 3)
│   ├── rangebar-io/           # I/O operations (Level 3)
│   ├── rangebar-streaming/    # Streaming engine (Level 4)
│   ├── rangebar-batch/        # Batch engine (Level 4)
│   ├── rangebar-cli/          # CLI binaries (Level 5)
│   └── rangebar/              # Meta-crate (facade)
```

---

## Phase 1: Workspace Setup

**Duration**: 2 hours
**Risk**: Low
**Status**: ✅ Completed (2025-10-04)

### Tasks
- [x] Create workspace root `Cargo.toml`
- [x] Create crate directories: `crates/{rangebar-core,rangebar-providers,rangebar-config,rangebar-io,rangebar-streaming,rangebar-batch,rangebar-cli,rangebar}`
- [x] Define `[workspace.package]` common metadata
- [x] Define `[workspace.dependencies]` shared dependencies
- [x] Create stub manifests for all 8 crates

### Validation
```bash
cargo build -p rangebar-core  # ✅ Success (4.95s)
cargo build -p rangebar        # ✅ Success (0.13s)
```

### Files Created
- `Cargo.toml` (workspace root)
- `Cargo.toml.v4-backup` (backup of v4.0.0 manifest)
- `crates/*/Cargo.toml` (8 stub manifests)
- `crates/*/src/lib.rs` (8 empty libraries)

### Observations
- Workspace resolver 2 handles dependency resolution correctly
- Empty crates compile without errors
- Build time for empty crates: <5 seconds total

---

## Phase 2: Extract rangebar-core

**Duration**: 6 hours
**Risk**: Low
**Status**: ✅ Completed (2025-10-10)

### Rationale
- Core has ZERO dependencies on other modules (validated via import analysis)
- If core tests pass → guaranteed no breaking changes
- Easiest phase to validate (builds confidence)

### Tasks
- [x] Create `crates/rangebar-core/Cargo.toml`
  - Dependencies: serde, chrono, thiserror, pyo3 (optional), utoipa (optional)
  - Features: test-utils, python, api (all optional)
- [x] Copy `src/core/*` → `crates/rangebar-core/src/`
- [x] Create `crates/rangebar-core/src/lib.rs`
- [x] Fix internal imports (`crate::core::` → `crate::`)
- [x] Run tests: `cargo test -p rangebar-core` (24/24 passed)

### Validation
```bash
cd crates/rangebar-core
cargo test --all-features
cargo clippy -- -D warnings
cargo build --release
```

### Files Modified
- Created: `crates/rangebar-core/Cargo.toml`
- Created: `crates/rangebar-core/src/lib.rs`
- Copied: `src/core/*.rs` → `crates/rangebar-core/src/`

### Success Criteria
- ✅ All core tests pass (24/24 - 23 unit tests + 1 doctest)
- ✅ Zero clippy warnings (with `-D warnings`)
- ✅ Compiles in <5 seconds (dev mode: 4.95s)

### Implementation Notes
- Fixed import paths: `crate::core::` → `crate::`
- Updated doctest: `rangebar::core::timestamp` → `rangebar_core::timestamp`
- Added optional features: `python = ["pyo3"]`, `api = ["utoipa"]`
- All data source references updated: `crate::types::DataSource`

---

## Phase 3: Extract rangebar-providers

**Duration**: 8 hours
**Risk**: Medium
**Status**: ✅ Completed (2025-10-10)

### Dependencies
- `rangebar-core` (from Phase 2)

### Tasks
- [x] Create `crates/rangebar-providers/Cargo.toml`
  - Dependencies: rangebar-core, reqwest, tokio, csv, zip, lzma-rs, tokio-tungstenite, tokio-stream, futures-util, byteorder, once_cell, toml
  - Features: binance (default), exness, dukascopy, all-providers
- [x] Copy `src/providers/*` → `crates/rangebar-providers/src/`
- [x] Update imports:
  - `use crate::core::FixedPoint;` → `use rangebar_core::FixedPoint;`
  - `use crate::core::types::AggTrade;` → `use rangebar_core::AggTrade;`
  - `use crate::providers::exness::` → `use crate::exness::`
- [x] Feature-gate providers in `lib.rs`
- [x] Fix doctests with correct module paths
- [x] Fix include_str! path for Dukascopy instrument config

### Import Changes
```rust
// Before
use crate::core::fixed_point::FixedPoint;
use crate::core::types::{AggTrade, RangeBar};
use crate::core::timestamp::normalize_timestamp;
use crate::providers::exness::types::ExnessTick;

// After
use rangebar_core::{FixedPoint, AggTrade, RangeBar, normalize_timestamp};
use crate::exness::types::ExnessTick;
```

### Validation
```bash
cargo test -p rangebar-providers --features binance       # 7 unit + 3 doctests ✅
cargo test -p rangebar-providers --features exness        # 23 unit + 3 doctests ✅
cargo test -p rangebar-providers --features dukascopy     # 22 unit + 4 doctests ✅
cargo test -p rangebar-providers --all-features           # 38 unit + 10 doctests ✅
cargo clippy -p rangebar-providers --all-features -- -D warnings  # ✅ Clean
```

### Success Criteria
- ✅ All 38 unit tests pass (binance: 7, exness: 23, dukascopy: 22)
- ✅ All 10 doctests pass (binance: 3, exness: 3, dukascopy: 4)
- ✅ Feature-isolated compilation works (each provider compiles independently)
- ✅ Zero clippy warnings (with `-D warnings`)

### Implementation Notes
- Added provider-specific optional dependencies:
  - **Binance**: tokio-tungstenite 0.23, tokio-stream 0.1, futures-util 0.3 (WebSocket support)
  - **Exness/Dukascopy**: lzma-rs 0.3 (LZMA compression)
  - **Dukascopy only**: byteorder 1.5, once_cell 1.20, toml 0.8 (binary parsing + config)
- Fixed include_str! path: `../../../docs/` → `../../../../docs/` (workspace depth adjustment)
- Updated all doctests from `use rangebar::providers::` to `use rangebar_providers::`
- Fixed exness mod.rs doctest error handling to avoid returning Result in unit function

---

## Phase 4: Extract rangebar-config + rangebar-io

**Duration**: 8 hours
**Risk**: Medium
**Status**: Pending

### 4A: rangebar-config

**Tasks**:
- [ ] Create `crates/rangebar-config/Cargo.toml`
- [ ] Copy `src/infrastructure/config/*` → `crates/rangebar-config/src/`
- [ ] Update imports to use `rangebar_core`

### 4B: rangebar-io

**Tasks**:
- [ ] Create `crates/rangebar-io/Cargo.toml`
- [ ] Copy `src/infrastructure/io/*` → `crates/rangebar-io/src/`
- [ ] Feature-gate polars: `parquet = ["polars"]`
- [ ] Update imports to use `rangebar_core`

### Validation
```bash
cargo test -p rangebar-config
cargo test -p rangebar-io --features parquet
```

---

## Phase 5: Extract rangebar-streaming + rangebar-batch

**Duration**: 10 hours
**Risk**: High (circular dependency with providers)
**Status**: Pending

### Critical Issue: engines/streaming/universal.rs

**Problem**:
```rust
use crate::providers::binance::BinanceWebSocketStream;
```

**Solution**: Feature-gate binance integration
```toml
[features]
binance-integration = ["rangebar-providers/binance"]
```

```rust
#[cfg(feature = "binance-integration")]
use rangebar_providers::binance::BinanceWebSocketStream;
```

### 5A: rangebar-streaming

**Tasks**:
- [ ] Create `crates/rangebar-streaming/Cargo.toml`
- [ ] Copy `src/engines/streaming/*` → `crates/rangebar-streaming/src/`
- [ ] Feature-gate binance dependency in `universal.rs`
- [ ] Update imports

### 5B: rangebar-batch

**Tasks**:
- [ ] Create `crates/rangebar-batch/Cargo.toml`
- [ ] Copy `src/engines/batch/*` → `crates/rangebar-batch/src/`
- [ ] Depend on `rangebar-io` for DataFrameConverter
- [ ] Update imports

### Validation
```bash
cargo test -p rangebar-streaming --all-features
cargo test -p rangebar-batch
```

---

## Phase 6: Extract rangebar-cli

**Duration**: 6 hours
**Risk**: Medium
**Status**: Pending

### Tasks
- [ ] Create `crates/rangebar-cli/Cargo.toml`
  - Depends on: all previous crates with full features
- [ ] Copy `src/bin/*` → `crates/rangebar-cli/src/bin/`
- [ ] Update imports in all 7 binaries:
  - `use rangebar::infrastructure::config::Settings;` → `use rangebar_config::Settings;`
  - `use rangebar::get_tier1_symbols;` → `use rangebar_providers::binance::get_tier1_symbols;`
  - etc.
- [ ] Define `[[bin]]` entries for all 7 executables

### Validation
```bash
cargo build -p rangebar-cli --release
cargo run --bin tier1-symbol-discovery -- --help
cargo run --bin rangebar-analyze -- --help
```

---

## Phase 7: Create rangebar Meta-Crate

**Duration**: 4 hours
**Risk**: Low
**Status**: Pending

### Purpose
Backward compatibility for users upgrading from v4.0.0

### Tasks
- [ ] Create `crates/rangebar/Cargo.toml`
  - Optional dependencies on all sub-crates
  - Features: core, providers, io, streaming, batch, full
- [ ] Create `crates/rangebar/src/lib.rs`
  - Re-export all crates
  - Maintain legacy module paths (`pub mod fixed_point`, `pub mod core`, etc.)

### Validation
```bash
# Test backward compatibility
cargo test -p rangebar --features full

# Test that old code still works
cargo build --example basic-usage
```

---

## Phase 8: Update Root Workspace

**Duration**: 2 hours
**Risk**: Low
**Status**: Pending

### Tasks
- [ ] Move current `src/` → `src-archived/` (backup)
- [ ] Update root `Cargo.toml` to be workspace-only
- [ ] Remove `[lib]` and `[[bin]]` from root
- [ ] Update `.gitignore` if needed
- [ ] Update `CLAUDE.md` with new structure
- [ ] Update `README.md` (if exists)

### Validation
```bash
cargo build --workspace --all-features
cargo test --workspace --all-features
cargo clippy --workspace --all-features -- -D warnings
```

---

## Regression Testing Protocol

**Run after EACH phase**:

```bash
# 1. Workspace builds
cargo build --workspace --all-features

# 2. All tests pass
cargo test --workspace --all-features

# 3. No circular dependencies
cargo tree -p rangebar-core | grep -E "(rangebar-providers|rangebar-io)"
# Expected: No matches

# 4. Clippy clean
cargo clippy --workspace --all-features -- -D warnings

# 5. Format check
cargo fmt --all -- --check

# 6. Build all binaries
for bin in tier1-symbol-discovery rangebar-analyze data-structure-validator \
           spot-tier1-processor polars-benchmark temporal-integrity-validator; do
    cargo build --release --bin $bin
done
```

---

## Error Handling Policy

**Zero Tolerance**:
- Tests fail → STOP, fix before proceeding
- Clippy warnings → STOP, fix before proceeding
- Circular dependency detected → STOP, redesign
- Import resolution fails → STOP, fix paths

**No Fallbacks**:
- No `unwrap_or_default()`
- No silent `Result` ignoring
- No optional dependencies to hide errors
- Propagate all errors via `?` operator

---

## Git Commit Strategy

**One commit per phase**:
```bash
# Phase 1
git commit -m "refactor: create workspace structure (Phase 1/8)

- Add workspace root Cargo.toml
- Create crate directory structure
- Define workspace.package metadata
- Define workspace.dependencies

SLO: Correctness ✓ (empty workspace builds)"

# Phase 2
git commit -m "refactor: extract rangebar-core crate (Phase 2/8)

- Copy src/core/* to crates/rangebar-core/
- Add rangebar-core/Cargo.toml
- Create rangebar-core/src/lib.rs
- All core tests pass (0 modifications)

SLO: Correctness ✓ (tests pass), Maintainability ✓ (zero external deps)"
```

---

## Rollback Strategy

**If any phase fails**:
1. `git reset --hard HEAD~1` (undo last commit)
2. Restore from `src-archived/` if needed
3. Document failure in this plan
4. Redesign phase before retry

---

## Documentation Updates

**After migration completes**:
- [ ] Update `README.md` with new crate structure
- [ ] Update `CLAUDE.md` with workspace conventions
- [ ] Create `crates/*/README.md` for each crate
- [ ] Update `docs/planning/README.md` to deprecate old plans
- [ ] Add workspace diagram to `docs/architecture/`

---

## Timeline

| Phase | Duration | Commit | Date | Status |
|-------|----------|--------|------|--------|
| 1. Workspace setup | 2h | 44c9515 | 2025-10-04 | ✅ Complete |
| 2. Extract core | 6h | 44c9515 | 2025-10-04 | ✅ Complete |
| 3. Extract providers | 8h | 44c9515 | 2025-10-04 | ✅ Complete |
| 4. Extract config+io | 8h | 44c9515 | 2025-10-04 | ✅ Complete |
| 5. Extract engines | 10h | 44c9515 | 2025-10-04 | ✅ Complete |
| 6. Extract CLI | 6h | 44c9515 | 2025-10-04 | ✅ Complete |
| 7. Meta-crate | 4h | 44c9515 | 2025-10-04 | ✅ Complete |
| 8. Root cleanup | 2h | dd8f971 | 2025-10-11 | ✅ Complete |

**Total**: 46 hours (~6 days at 8h/day)

---

## Success Metrics

- [x] All 16 test suites pass
- [x] All 7 binaries build successfully
- [x] Compilation time unchanged (±10%)
- [x] Zero clippy warnings
- [x] CI/CD pipeline green
- [ ] Crates.io publication succeeds (pending release)

---

## References

- Initial analysis: Session 2025-10-03 (3yrs rangebar construction)
- Import dependency analysis: `grep -r "^use crate::" src/`
- LOC counts: `wc -l src/**/*.rs`
- External deps: `cargo tree --depth 1`

---

**Next Action**: Migration complete. Archive to `docs/planning/legacy/` if needed.
