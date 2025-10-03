# Workspace Restructuring Migration Plan

**Version**: v2.3.0
**Date Started**: 2025-10-02
**Status**: IN PROGRESS

---

## Objectives

1. **Code Organization**: Layered architecture (Core → Providers → Engines → Infrastructure)
2. **Data Management**: Explicit input/output/cache separation with documented taxonomy
3. **Provider Pattern**: Clear pattern for adding future data sources (Kraken, Alpaca, etc.)
4. **Zero Duplication**: Single source of truth (tier1/symbols, statistics)

---

## Architecture Design

### 4-Layer Model

```
Layer 1: Core         → Provider-agnostic algorithm (RangeBar, FixedPoint, timestamp)
Layer 2: Providers    → Source-specific integrations (Binance, Dukascopy, future providers)
Layer 3: Engines      → Processing modes (streaming, batch)
Layer 4: Infrastructure → Supporting systems (I/O, config, API)
```

### Target Structure

```
src/
├── core/                        # Layer 1 (NO CHANGES)
├── providers/                   # Layer 2 (NEW)
│   ├── binance/
│   │   ├── mod.rs
│   │   ├── historical.rs        ← data/historical.rs
│   │   ├── symbols.rs           ← MERGE tier1.rs + market/symbols.rs
│   │   └── websocket.rs         ← streaming/websocket.rs
│   └── dukascopy/
│       ├── mod.rs               ← Consolidate from 7 files
│       ├── client.rs            ← fetcher.rs + config.rs
│       ├── builder.rs
│       ├── types.rs             ← types.rs + error.rs
│       └── conversion.rs
├── engines/                     # Layer 3 (NEW)
│   ├── streaming/
│   │   ├── processor.rs         ← streaming_processor.rs (root)
│   │   ├── stats.rs             ← MERGE statistics.rs + streaming/stats.rs
│   │   ├── indicators.rs
│   │   ├── universal.rs
│   │   └── replay_buffer.rs
│   └── batch/
│       └── engine.rs
└── infrastructure/              # Layer 4 (NEW)
    ├── io/
    ├── config/
    └── api/
```

---

## Migration Phases

### Phase 1: Data Management ✅ COMPLETE
- [x] Create data/, cache/ directories
- [x] Create output/ subdirectories (benchmarks, validation, production, experiments)
- [x] Write README.md for data/, cache/, output/, test_data/
- [x] Update .gitignore with selective tracking

**Validation**: Directories exist, READMEs readable
**Commit**: Data management structure

---

### Phase 2: Core Verification ✅ COMPLETE
- [x] Verify src/core/ compiles standalone
- [x] Move src/core/ → src/core/ (no changes, just validation)
- [x] Run: cargo check --lib
- [x] Run: cargo test --lib (core tests only)

**Success Gate**: ✅ PASSED - cargo check + 88 tests passed in 0.15s

**Validation SLOs**:
- Correctness: ✅ All core algorithm tests pass (88/88)
- Observability: ✅ No warnings from clippy
- Maintainability: ✅ Module structure unchanged

**Result**: Core module stable, no changes needed

---

### Phase 3: Providers - Binance ✅ COMPLETE
- [x] Create src/providers/binance/mod.rs
- [x] Move src/data/historical.rs → src/providers/binance/historical.rs
- [x] MERGE src/tier1.rs + src/market/symbols.rs → src/providers/binance/symbols.rs
  - ✅ Verified identical content (diff showed FILES ARE IDENTICAL)
  - ✅ Used tier1.rs as source
- [x] Move src/streaming/websocket.rs → src/providers/binance/websocket.rs
- [x] Update imports within moved files
- [x] Run: cargo check --lib
- [x] Run: cargo test (binance provider tests)

**Success Gate**: ✅ PASSED - cargo check + 7 tests passed in 0.00s

**Validation SLOs**:
- Correctness: ✅ Symbol discovery returns 18 Tier-1 symbols (test passed)
- Observability: ✅ No clippy warnings on new module
- Maintainability: ✅ Single source of truth (providers/binance/symbols.rs)

**Result**: Binance provider operational at src/providers/binance/
**Note**: Old files (tier1.rs, market/symbols.rs, data/historical.rs, streaming/websocket.rs) remain temporarily for backward compatibility. Will be deleted in Phase 11.

---

### Phase 4: Providers - Dukascopy 🔜 PENDING
- [ ] Create src/providers/dukascopy/mod.rs
- [ ] CONSOLIDATE: fetcher.rs + config.rs → client.rs
  - Move DukascopyFetcher + INSTRUMENT_CONFIG to client.rs
  - Keep lazy static config loading
- [ ] CONSOLIDATE: types.rs + error.rs → types.rs
  - Move all error enums to types.rs
  - Rationale: Tightly coupled, 388 lines total
- [ ] Keep: builder.rs, conversion.rs (no changes)
- [ ] Update internal imports
- [ ] Run: cargo check --lib
- [ ] Run: cargo test (dukascopy tests)

**Success Gate**: cargo check pass, dukascopy module compiles

**Validation SLOs**:
- Correctness: DukascopyFetcher can fetch EURUSD hour
- Observability: Module structure clear (5 files not 7)
- Maintainability: Related code colocated

**Commit**: Dukascopy provider consolidated

---

### Phase 5: Engines - Streaming 🔜 PENDING
- [ ] Create src/engines/streaming/mod.rs
- [ ] Move src/streaming_processor.rs → src/engines/streaming/processor.rs
- [ ] MERGE src/statistics.rs + src/streaming/stats.rs → src/engines/streaming/stats.rs
  - Compare files first (diff analysis)
  - Keep most complete version
  - Preserve all public APIs
- [ ] Move src/streaming/{indicators,universal,replay_buffer}.rs → src/engines/streaming/
- [ ] Update imports
- [ ] Run: cargo check --lib
- [ ] Run: cargo test (streaming tests)

**Success Gate**: cargo check pass, streaming engine compiles

**Validation SLOs**:
- Correctness: StreamingStatsEngine API unchanged
- Observability: Single stats module, no duplication
- Maintainability: Clear engine separation

**Commit**: Streaming engine migrated

---

### Phase 6: Engines - Batch 🔜 PENDING
- [ ] Create src/engines/batch/mod.rs
- [ ] Move src/batch/engine.rs → src/engines/batch/engine.rs
- [ ] Update imports
- [ ] Run: cargo check --lib (polars-analytics feature)

**Success Gate**: cargo check pass with feature flag

**Commit**: Batch engine migrated

---

### Phase 7: Infrastructure 🔜 PENDING
- [ ] Move src/io/ → src/infrastructure/io/
- [ ] Move src/config/ → src/infrastructure/config/
- [ ] Move src/api/ → src/infrastructure/api/
- [ ] Update imports
- [ ] Run: cargo check --lib --all-features

**Success Gate**: cargo check pass with all features

**Commit**: Infrastructure modules migrated

---

### Phase 8: Update lib.rs 🔜 PENDING
- [ ] Rewrite pub mod declarations
- [ ] Add legacy compatibility exports
- [ ] Update re-exports
- [ ] Run: cargo check --lib --all-features
- [ ] Run: cargo test --lib

**Success Gate**: Library compiles with all features

**Validation SLOs**:
- Correctness: Public API unchanged (backward compatible)
- Observability: Clear module hierarchy
- Maintainability: Legacy exports documented

**Commit**: lib.rs updated with new structure

---

### Phase 9: Update Binaries 🔜 PENDING
- [ ] Update imports in src/bin/*.rs (7 files)
- [ ] Run: cargo check --bins
- [ ] Test key binaries:
  - tier1-symbol-discovery
  - spot-tier1-processor
  - data-structure-validator

**Success Gate**: All binaries compile and run

**Commit**: Binaries updated

---

### Phase 10: Update Tests 🔜 PENDING
- [ ] Update imports in tests/*.rs (13 files)
- [ ] Run: cargo test --all-features
- [ ] Verify all 143+ tests pass

**Success Gate**: Full test suite passes

**Commit**: Tests updated

---

### Phase 11: Cleanup 🔜 PENDING
- [ ] Delete old directories:
  - src/data/
  - src/market/
  - src/streaming/
  - src/config/
  - src/io/
  - src/api/
  - src/batch/
- [ ] Delete duplicate root files:
  - src/tier1.rs
  - src/statistics.rs
  - src/streaming_processor.rs
- [ ] Delete empty directories (archived/, bin/disabled/)
- [ ] Run: cargo check --all-features
- [ ] Run: cargo test --all-features
- [ ] Run: cargo clippy -- -D warnings

**Success Gate**: Clean compilation, all tests pass, zero clippy warnings

**Commit**: Old structure removed

---

### Phase 12: Documentation 🔜 PENDING
- [ ] Update CLAUDE.md with new architecture
- [ ] Update README.md if needed
- [ ] Create architecture diagram (optional)
- [ ] This migration doc marked COMPLETE

**Commit**: Documentation updated

---

## Rollback Procedures

### Per-Phase Rollback
```bash
# If phase fails validation
git reset --hard HEAD
git clean -fd
```

### Full Rollback (if catastrophic)
```bash
git log --oneline -20  # Find commit before migration
git reset --hard <commit-before-restructure>
```

---

## Validation Criteria

### Per-Phase
- `cargo check` passes for affected modules
- `cargo test` passes for affected tests
- `cargo clippy` shows no new warnings
- Binary execution test (if applicable)

### Final Validation
- `cargo check --all-features` passes
- `cargo test --all-features` passes (all 143+ tests)
- `cargo clippy --all-features -- -D warnings` passes
- Key binaries execute successfully:
  - `tier1-symbol-discovery --format minimal`
  - `cargo run --bin data-structure-validator -- --help`

---

## SLO Compliance

### Correctness
- Algorithm integrity: RangeBarProcessor behavior unchanged
- Public API: Backward compatibility via legacy exports
- Test coverage: All existing tests pass

### Observability
- Module hierarchy: Clear 4-layer structure
- Import paths: Semantic (providers, engines, infrastructure)
- Error propagation: Unchanged (raise immediately)

### Maintainability
- Code duplication: Eliminated (symbols, statistics)
- Provider pattern: Clear template for future sources
- Documentation: Every directory has README.md

---

## Current Status

**Phase**: 2 (Core Verification)
**Last Updated**: 2025-10-02
**Blockers**: None
**Next Step**: Verify core/ module compiles standalone

---

## Lessons Learned

(To be populated during migration)

---

## References

- Initial plan discussion: 2025-10-02 conversation
- Dukascopy implementation: docs/planning/research/dukascopy-implementation-complete.md
- Architecture requirements: CLAUDE.md
