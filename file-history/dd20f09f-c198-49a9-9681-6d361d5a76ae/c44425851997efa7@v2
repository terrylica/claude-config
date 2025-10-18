# Dukascopy → Exness Migration Plan

**Version**: 1.0.0
**Date**: 2025-10-03
**Status**: completed
**Context**: Replace Dukascopy provider with Exness Raw_Spread due to rate limiting issues

---

## Executive Summary

### User's Proposal

> "We do have the privilege of simply by copying the Dukascopy folder to a new folder called Exness and then we can modify the Exness folder from there. But of course these are two brokers and their data source are completely different."

### Assessment

**Your proposal is SENSIBLE with modifications.**

**Why copy-and-modify works:**
- ✅ Both provide Forex tick data (Bid/Ask quotes)
- ✅ Both use mid-price for range bars
- ✅ Both require validation and error handling
- ✅ Builder pattern and spread stats logic is reusable
- ✅ Test structure is identical (synthetic, real-world, edge cases)

**Critical differences requiring modification:**
- ⚠️ **Data format**: LZMA binary (.bi5) → ZIP CSV
- ⚠️ **Volume data**: 4 fields (bid/ask/volumes) → 2 fields (bid/ask only)
- ⚠️ **Granularity**: Hourly files → Monthly files
- ⚠️ **Instrument config**: Embedded TOML → Simple symbol validation
- ⚠️ **Decimal factors**: Binary integer → Float64 direct

### Recommendation

**✅ APPROVE copy-and-modify strategy** with systematic refactoring:

1. Copy `src/providers/dukascopy/` → `src/providers/exness/`
2. Gut `client.rs` (LZMA → ZIP/CSV)
3. Simplify `types.rs` (remove volumes)
4. Keep `builder.rs` structure (mid-price logic reusable)
5. Deprecate Dukascopy with README notice

---

## Current Dukascopy Implementation Survey

### File Structure

```
src/providers/dukascopy/
├── mod.rs          (3.6 KB)  - Public API, documentation
├── types.rs        (12.5 KB) - DukascopyTick, SpreadStats, Errors
├── client.rs       (10.9 KB) - HTTP fetcher, .bi5 parser, instrument config
├── builder.rs      (9.8 KB)  - DukascopyRangeBarBuilder, mid-price processor
└── conversion.rs   (9.9 KB)  - Tick validation, synthetic trade conversion
```

### Data Flow

```
HTTP GET (.bi5)
  → LZMA decompress
  → Binary parsing (20 bytes/tick)
  → DukascopyTick { bid, ask, bid_vol, ask_vol, timestamp_ms }
  → Validation (CrossedMarket, ExcessiveSpread, PriceRange)
  → Mid-price calculation: (bid + ask) / 2
  → RangeBarProcessor → DukascopyRangeBar { base, spread_stats }
```

### Key Dependencies

- `lzma-rs` - LZMA decompression
- `byteorder` - Big-endian binary parsing
- `reqwest` - HTTP client (120s timeout)
- `once_cell` - Lazy static instrument config
- `toml` - Instrument config parsing (1,607 instruments)

### Critical Features

1. **Instrument Config** (`client.rs`):
   - Embedded TOML with 1,607 instruments
   - Decimal factors for binary→float conversion
   - Type inference (Forex/Crypto/Commodity/Equity)

2. **Spread Stats** (`types.rs`):
   - Per-bar SMA: avg spread, min/max spread
   - Bid/Ask liquidity tracking
   - Tick count

3. **Validation Strictness** (`types.rs`):
   - Permissive: Basic checks only
   - Strict: Spread < 10% (default)
   - Paranoid: Spread < 1%

4. **Error Handling** (`types.rs`):
   - Fatal: UnsupportedInstrument, InvalidDecimalFactor
   - Skip: CrossedMarket, ExcessiveSpread
   - Abort: >10% error rate (SystemicDataQualityIssue)

### Test Coverage

```
tests/dukascopy_*.rs (6 files)
├── dukascopy_integration_test.rs   - Basic fetcher + builder smoke test
├── dukascopy_real_data_test.rs     - Live EURUSD 1-hour test
├── dukascopy_comprehensive_test.rs - Multi-day EURUSD validation
├── dukascopy_volatile_test.rs      - High volatility scenarios
├── dukascopy_audit_test.rs         - Algorithm integrity checks
└── dukascopy_eurusd_adversarial_audit.rs - Ultra-low threshold (0.1bps) validation
```

---

## Exness Data Characteristics

### Data Format

```csv
"Exness","Symbol","Timestamp","Bid","Ask"
"exness","EURUSD_Raw_Spread","2024-01-15 00:00:00.032Z",1.0945,1.09456
```

**Key Differences from Dukascopy**:

| Aspect | Dukascopy | Exness |
|--------|-----------|--------|
| **Container** | LZMA (.bi5) | ZIP (.zip) |
| **Format** | Binary (20 bytes/tick) | CSV (text) |
| **Fields** | Bid, Ask, BidVol, AskVol, Time | Bid, Ask, Timestamp |
| **Volumes** | ✅ Available | ❌ Missing |
| **Timestamp** | ms offset from hour start | ISO 8601 UTC string |
| **Decimal Encoding** | Integer × decimal_factor | Float64 direct |
| **Granularity** | Hourly files | Monthly files |
| **File Size** | ~50KB/hour compressed | ~9MB/month compressed |
| **Download** | 120 requests/5 days | 1 request/month |

### API Pattern

```
https://ticks.ex2archive.com/ticks/{SYMBOL}_Raw_Spread/{year}/{month}/Exness_{SYMBOL}_Raw_Spread_{year}_{month}.zip

Example:
https://ticks.ex2archive.com/ticks/EURUSD_Raw_Spread/2024/01/Exness_EURUSD_Raw_Spread_2024_01.zip
```

### No Rate Limiting

- ✅ 100% reliability (vs 77.5% Dukascopy Phase 1)
- ✅ 3 seconds/month download (vs 250s/5days Dukascopy)
- ✅ No complex timeout/retry logic needed

---

## Migration Strategy: Copy-and-Modify Analysis

### What Can Be Reused Directly (80% of code)

#### ✅ `builder.rs` - ALMOST UNCHANGED

**Reusable logic**:
- DukascopyRangeBarBuilder → ExnessRangeBarBuilder (rename only)
- Mid-price calculation: `(bid + ask) / 2`
- SpreadStats accumulation (sum, min, max, count)
- process_tick() → process_tick() (identical logic)
- get_incomplete_bar() → get_incomplete_bar()

**Changes needed**:
- Remove volume handling (ExnessTick has no volumes)
- Update struct names (Dukascopy → Exness)
- Update documentation references

**Estimated effort**: 15 minutes (find-replace + volume removal)

#### ✅ `types.rs` - SIMPLIFY

**Reusable structures**:
- SpreadStats (avg, min, max, count)
- ValidationStrictness (Permissive/Strict/Paranoid)
- ConversionError variants (most of them)
- ExnessRangeBar { base: RangeBar, spread_stats: SpreadStats }

**Remove entirely**:
- InstrumentType enum (no complex instrument config needed)
- UnsupportedInstrument error (symbol validation simpler)
- InvalidDecimalFactor error (no binary encoding)
- bid_liquidity_sum, ask_liquidity_sum fields (no volumes)

**Add**:
- Simple symbol validation (EURUSD_Raw_Spread pattern)

**Estimated effort**: 30 minutes (deletion + simplification)

#### ✅ `conversion.rs` - SIMPLIFY

**Reusable validation logic**:
- validate_tick() structure
- validate_price() checks
- CrossedMarket detection
- ExcessiveSpread calculation

**Remove entirely**:
- Decimal factor conversion (binary → float)
- Instrument config lookups
- Price range validation (InstrumentType-specific)

**Change**:
- tick_to_synthetic_trade() → simpler (no volume fields)

**Estimated effort**: 20 minutes (deletion + simplification)

### What Must Be Completely Rewritten (20% of code)

#### ❌ `client.rs` - COMPLETE REWRITE

**Dukascopy version** (10.9 KB):
```rust
- Embedded TOML config (1,607 instruments)
- get_instrument_info() → (decimal_factor, InstrumentType)
- HTTP GET → LZMA decompress → Binary parsing
- 20-byte tick structure (big-endian)
- Timeout: 120s request, 30s connect
```

**Exness version** (estimated 5 KB):
```rust
- Simple symbol validation (EURUSD_Raw_Spread pattern)
- HTTP GET → ZIP extract → CSV parse
- CSV parsing: serde_csv with deserialize
- Timestamp: ISO 8601 → chrono::DateTime
- Timeout: 30s (Exness is fast, no complex retry)
```

**Key simplifications**:
- ✅ No LZMA decompression (use `zip` crate)
- ✅ No binary parsing (use `csv` crate)
- ✅ No decimal factors (float64 direct)
- ✅ No instrument config (simple symbol string)
- ✅ No complex timeout logic (Exness reliable)

**Dependencies change**:
```toml
# Remove:
lzma-rs = "0.3"
byteorder = "1.5"
toml = "0.8"

# Add:
zip = "0.6"
csv = "1.3"
chrono = "0.4"
```

**Estimated effort**: 2 hours (new HTTP → ZIP → CSV pipeline)

---

## Detailed Migration Plan

### Phase 1: Setup (5 minutes)

```bash
# 1. Copy provider directory
cp -r src/providers/dukascopy src/providers/exness

# 2. Rename files (none needed, structure identical)

# 3. Global find-replace in exness/
cd src/providers/exness
sed -i '' 's/Dukascopy/Exness/g' *.rs
sed -i '' 's/dukascopy/exness/g' *.rs
```

### Phase 2: Update `types.rs` (30 minutes)

**Changes**:

1. Remove volume fields from SpreadStats:
```rust
// DELETE:
bid_liquidity_sum: FixedPoint,
ask_liquidity_sum: FixedPoint,

// KEEP:
spread_sum: FixedPoint,
min_spread: FixedPoint,
max_spread: FixedPoint,
tick_count: u32,
```

2. Update ExnessTick structure:
```rust
pub struct ExnessTick {
    pub bid: f64,
    pub ask: f64,
    pub timestamp_ms: i64,  // Parsed from ISO 8601
    // NO volumes
}
```

3. Remove InstrumentType enum (entire section)

4. Remove instrument-specific errors:
```rust
// DELETE:
UnsupportedInstrument { instrument: String },
InvalidDecimalFactor { ... },
InvalidPriceRange { ... },
```

5. Simplify ExnessError:
```rust
pub enum ExnessError {
    Conversion(#[from] ConversionError),
    Processing(#[from] ProcessingError),
    Http(#[from] reqwest::Error),      // NEW
    Csv(#[from] csv::Error),           // NEW
    Zip(#[from] zip::ZipError),        // NEW
    Timestamp(#[from] chrono::ParseError), // NEW
}
```

### Phase 3: Rewrite `client.rs` (2 hours)

**New structure**:

```rust
//! Exness HTTP client and CSV fetcher
//!
//! Fetches monthly ZIP archives containing CSV tick data.

use super::types::{ConversionError, ExnessTick};
use chrono::{DateTime, Utc};
use csv::ReaderBuilder;
use reqwest::Client;
use std::io::Read;
use std::time::Duration;
use zip::ZipArchive;

/// Exness HTTP data fetcher
pub struct ExnessFetcher {
    client: Client,
    symbol: String,  // e.g., "EURUSD_Raw_Spread"
}

impl ExnessFetcher {
    pub fn new(symbol: &str) -> Self {
        Self {
            client: Client::builder()
                .timeout(Duration::from_secs(30))  // Exness is fast
                .build()
                .expect("Failed to build HTTP client"),
            symbol: symbol.to_string(),
        }
    }

    /// Fetch monthly data
    ///
    /// URL: https://ticks.ex2archive.com/ticks/{symbol}/{year}/{month}/Exness_{symbol}_{year}_{month}.zip
    pub async fn fetch_month(&self, year: u16, month: u8) -> Result<Vec<ExnessTick>, ExnessError> {
        let url = format!(
            "https://ticks.ex2archive.com/ticks/{}/{:04}/{:02}/Exness_{}_{:04}_{:02}.zip",
            self.symbol, year, month, self.symbol, year, month
        );

        // 1. HTTP GET
        let response = self.client.get(&url).send().await?;
        let bytes = response.bytes().await?;

        // 2. Extract ZIP
        let reader = std::io::Cursor::new(bytes);
        let mut archive = ZipArchive::new(reader)?;
        let mut csv_file = archive.by_index(0)?;  // First file

        // 3. Read CSV content
        let mut csv_content = String::new();
        csv_file.read_to_string(&mut csv_content)?;

        // 4. Parse CSV
        let mut reader = ReaderBuilder::new()
            .has_headers(true)
            .from_reader(csv_content.as_bytes());

        let mut ticks = Vec::new();
        for result in reader.deserialize() {
            let record: ExnessCsvRecord = result?;
            ticks.push(ExnessTick::from_csv(record)?);
        }

        Ok(ticks)
    }
}

/// CSV record structure (matches Exness format)
#[derive(serde::Deserialize)]
struct ExnessCsvRecord {
    #[serde(rename = "Exness")]
    _provider: String,  // Ignore

    #[serde(rename = "Symbol")]
    _symbol: String,  // Ignore (already in fetcher)

    #[serde(rename = "Timestamp")]
    timestamp: String,  // ISO 8601

    #[serde(rename = "Bid")]
    bid: f64,

    #[serde(rename = "Ask")]
    ask: f64,
}

impl ExnessTick {
    fn from_csv(record: ExnessCsvRecord) -> Result<Self, ConversionError> {
        // Parse timestamp: "2024-01-15 00:00:00.032Z"
        let dt = DateTime::parse_from_rfc3339(&record.timestamp)
            .or_else(|_| {
                // Handle alternative format without 'Z'
                let with_z = format!("{}Z", record.timestamp);
                DateTime::parse_from_rfc3339(&with_z)
            })?;

        let timestamp_ms = dt.timestamp_millis();

        Ok(Self {
            bid: record.bid,
            ask: record.ask,
            timestamp_ms,
        })
    }
}
```

**Key simplifications**:
- No LZMA decompression
- No binary parsing
- No decimal factors
- No instrument config
- Standard Rust crates (`zip`, `csv`, `chrono`)

### Phase 4: Update `builder.rs` (15 minutes)

**Changes**:

1. Rename struct:
```rust
pub struct ExnessRangeBarBuilder {
    processor: RangeBarProcessor,
    spread_stats: SpreadStats,
    threshold: i64,
    symbol: String,
}
```

2. Remove volume handling in process_tick():
```rust
// DELETE volume accumulation:
self.spread_stats.bid_liquidity_sum += ...;
self.spread_stats.ask_liquidity_sum += ...;

// KEEP spread tracking:
let spread = tick.ask - tick.bid;
self.spread_stats.spread_sum += FixedPoint::from_f64(spread)?;
self.spread_stats.min_spread = self.spread_stats.min_spread.min(spread_fp);
self.spread_stats.max_spread = self.spread_stats.max_spread.max(spread_fp);
self.spread_stats.tick_count += 1;
```

3. Update documentation references (Dukascopy → Exness)

### Phase 5: Update `conversion.rs` (20 minutes)

**Changes**:

1. Remove decimal factor conversion

2. Simplify validate_tick():
```rust
pub fn validate_tick(
    tick: &ExnessTick,
    strictness: ValidationStrictness,
) -> Result<(), ConversionError> {
    // Basic checks
    if tick.bid <= 0.0 {
        return Err(ConversionError::InvalidBid { bid: tick.bid });
    }
    if tick.ask <= 0.0 {
        return Err(ConversionError::InvalidAsk { ask: tick.ask });
    }

    // Crossed market
    if tick.bid > tick.ask {
        return Err(ConversionError::CrossedMarket {
            bid: tick.bid,
            ask: tick.ask,
        });
    }

    // Spread validation (strictness-dependent)
    let spread_pct = ((tick.ask - tick.bid) / tick.bid) * 100.0;
    let threshold = match strictness {
        ValidationStrictness::Permissive => return Ok(()),
        ValidationStrictness::Strict => 10.0,
        ValidationStrictness::Paranoid => 1.0,
    };

    if spread_pct > threshold {
        return Err(ConversionError::ExcessiveSpread {
            spread_pct,
            threshold_pct: threshold,
        });
    }

    Ok(())
}
```

3. Remove price range validation (no InstrumentType)

### Phase 6: Update `mod.rs` (5 minutes)

```rust
//! Exness range bar construction from tick data (Raw_Spread variant)
//!
//! Converts Exness market maker quotes (bid/ask only) to range bars
//! using mid-price as synthetic trade price.
//!
//! ## Key Differences from Dukascopy
//!
//! - No tick volumes (Bid/Ask prices only)
//! - Monthly ZIP/CSV format (vs hourly .bi5 binary)
//! - Direct float64 prices (vs integer × decimal_factor)
//! - Zero rate limiting (100% reliability)
//!
//! ## Data Source
//!
//! URL: `https://ticks.ex2archive.com/ticks/{SYMBOL}_Raw_Spread/{year}/{month}/...`
//! Variant: `{SYMBOL}_Raw_Spread` (e.g., `EURUSD_Raw_Spread`)
//! Rationale: CV=8.17 (8× higher spread variability than Standard)

pub mod builder;
pub mod client;
pub mod conversion;
pub mod types;

pub use builder::ExnessRangeBarBuilder;
pub use client::ExnessFetcher;
pub use types::{
    ConversionError, ExnessError, ExnessRangeBar, ExnessTick,
    SpreadStats, ValidationStrictness,
};
```

### Phase 7: Update Tests (1 hour)

**Strategy**: Copy test structure, update data sources

```bash
# Copy test files
cp tests/dukascopy_integration_test.rs tests/exness_integration_test.rs
cp tests/dukascopy_eurusd_adversarial_audit.rs tests/exness_eurusd_ultra_low_threshold.rs
```

**Update test data**:

1. `exness_integration_test.rs`:
   - Change fetcher: `ExnessFetcher::new("EURUSD_Raw_Spread")`
   - Change method: `fetch_month(2024, 1)` (vs fetch_hour)
   - Update expected tick count: ~60K/day (vs ~84K/day)

2. `exness_eurusd_ultra_low_threshold.rs`:
   - Same Jan 15-19, 2024 period
   - Expected: 300,425 ticks (validated empirically)
   - Threshold: 1 (0.1bps in v3.0.0 units)
   - Target: ~480 bars/day

### Phase 8: Deprecate Dukascopy (5 minutes)

**Create deprecation README**:

```bash
cat > src/providers/dukascopy/README.md << 'EOF'
# Dukascopy Provider (DEPRECATED)

**Status**: ⚠️ DEPRECATED as of 2025-10-03
**Replacement**: `exness` provider

## Deprecation Reason

Dukascopy data source exhibits severe rate limiting issues:
- HTTP 503 errors on 27/120 requests (77.5% reliability)
- Complex timeout/retry logic required (120s timeouts)
- IP-based rate limiting with long windows
- 250 seconds to download 5 days of data

**Reference**: `docs/planning/dukascopy-timeout-retry-strategy.md`

## Migration Path

Use Exness Raw_Spread variant instead:
- ✅ 100% reliability (zero rate limiting)
- ✅ 3 seconds/month download (80× faster)
- ✅ Simpler implementation (ZIP/CSV vs LZMA/binary)
- ⚠️ 28% fewer ticks (60K/day vs 84K/day) - acceptable for range bars
- ⚠️ No tick volumes (Bid/Ask only)

**See**: `src/providers/exness/` and `docs/planning/exness-migration-plan.md`

## Code Preservation

This module is preserved for:
- Historical reference
- Volume-weighted feature research (future)
- Binary format parsing patterns

Do NOT use for new implementations.
EOF
```

### Phase 9: Update Module Registration (5 minutes)

**Update** `src/providers/mod.rs`:

```rust
//! Data provider integrations
//!
//! ## Supported Providers
//!
//! - `binance` - Binance spot and futures markets (primary - crypto)
//! - `exness` - Exness Raw_Spread tick data (primary - forex)
//! - `dukascopy` - ⚠️ DEPRECATED (rate limiting issues, use `exness`)

pub mod binance;
pub mod exness;

#[deprecated(
    since = "2.3.0",
    note = "Use `exness` provider instead (zero rate limiting, 100% reliability)"
)]
pub mod dukascopy;
```

**Update** `src/lib.rs` documentation (if needed)

### Phase 10: Update Documentation (15 minutes)

1. **Update CLAUDE.md**: ✅ Already done

2. **Create migration guide**:
   - This file (`docs/planning/exness-migration-plan.md`)

3. **Update docs/planning/architecture/**:
   - Add Exness to provider comparison matrix
   - Mark Dukascopy as deprecated

4. **Archive Dukascopy docs**:
```bash
mv docs/planning/dukascopy-* docs/planning/archive/dukascopy/
```

---

## Dependency Changes

### Remove (from Cargo.toml)

```toml
lzma-rs = "0.3"        # LZMA decompression
byteorder = "1.5"      # Binary parsing
toml = "0.8"           # Instrument config
once_cell = "1.19"     # Lazy static config
```

### Add

```toml
zip = "0.6"            # ZIP extraction
csv = "1.3"            # CSV parsing
chrono = "0.4"         # Timestamp parsing (may already exist)
```

**Net change**: -4 deps, +3 deps (likely +2 if chrono exists)

---

## Risk Assessment

### Low Risk ✅

1. **Data format change**: Well-documented, straightforward ZIP/CSV
2. **Code isolation**: Dukascopy/Exness providers are independent modules
3. **Test coverage**: Can validate Exness against same test cases
4. **Reusable logic**: 80% of builder/validation code unchanged

### Medium Risk ⚠️

1. **Timestamp parsing**: ISO 8601 with potential format variations
   - **Mitigation**: Handle both `2024-01-15 00:00:00.032Z` and without `Z`
   - **Fallback**: Use chrono's flexible parsing

2. **Missing volumes**: SpreadStats no longer tracks liquidity
   - **Impact**: Loss of bid/ask liquidity metadata
   - **Mitigation**: Document in ExnessRangeBar as known limitation
   - **Future**: Could add volume estimation from price volatility

3. **Monthly granularity**: Cannot fetch single day
   - **Impact**: Must download ~9MB for single-day test
   - **Mitigation**: Cache monthly files locally, filter in memory

### Zero Risk ✅

1. **Core algorithm unchanged**: RangeBarProcessor stays identical
2. **Binance provider unaffected**: Completely separate module
3. **Backward compatibility**: Dukascopy deprecated, not removed
4. **Rollback**: Keep Dukascopy code, can revert if needed

---

## Timeline Estimate

| Phase | Task | Effort | Dependencies |
|-------|------|--------|--------------|
| 1 | Copy directory, find-replace | 5 min | None |
| 2 | Update types.rs (remove volumes) | 30 min | Phase 1 |
| 3 | Rewrite client.rs (ZIP/CSV) | 2 hours | Phase 1 |
| 4 | Update builder.rs (no volumes) | 15 min | Phase 2 |
| 5 | Update conversion.rs (simplify) | 20 min | Phase 2 |
| 6 | Update mod.rs (docs) | 5 min | Phases 2-5 |
| 7 | Copy/update tests | 1 hour | Phases 2-6 |
| 8 | Deprecate Dukascopy (README) | 5 min | None |
| 9 | Update module registration | 5 min | Phase 6 |
| 10 | Update documentation | 15 min | All |

**Total effort**: ~4.5 hours (single developer, uninterrupted)

**Recommended**: Execute phases 1-6 in single session (3 hours), then test/docs separately.

---

## Validation Criteria

### Phase 3 Complete: Client Functional

```bash
# Test: Fetch January 2024 EURUSD_Raw_Spread
cargo test --package rangebar --test exness_integration_test -- fetch_month --exact
```

**Expected**:
- Download completes in <5 seconds
- Returns ~1.35M ticks for full month
- No HTTP errors, no timeout errors

### Phase 7 Complete: All Tests Pass

```bash
# Run Exness test suite
cargo test --package rangebar exness_
```

**Expected**:
- `exness_integration_test` ✅ (basic fetcher)
- `exness_eurusd_ultra_low_threshold` ✅ (Jan 15-19 validation)
- 300,425 ticks fetched
- 0.1bps produces ~480 bars/day

### Phase 10 Complete: Documentation Audit

**Checklist**:
- [ ] CLAUDE.md references Exness (not Dukascopy) ✅ Already done
- [ ] `src/providers/mod.rs` marks Dukascopy deprecated
- [ ] Dukascopy README.md explains deprecation
- [ ] Migration plan exists (`docs/planning/exness-migration-plan.md`)
- [ ] Cargo.toml updated (removed lzma-rs, byteorder, toml)

---

## Alternative Strategies Considered

### Alternative 1: Adapter Pattern (Rejected)

**Idea**: Create `ExnessAdapter` that wraps `DukascopyRangeBarBuilder`

**Pros**:
- Maximum code reuse
- Dukascopy stays canonical

**Cons**:
- Artificial dependency (Exness depends on Dukascopy types)
- Confusing to maintain (volume fields always zero)
- Performance overhead (extra conversion layer)

**Verdict**: ❌ Rejected - Tight coupling bad, minimal code savings

### Alternative 2: Shared Traits (Rejected)

**Idea**: Create `ForexTickProvider` trait, both implement

**Pros**:
- Clean abstraction
- Polymorphic provider switching

**Cons**:
- Over-engineering for 2 providers
- Volume field mismatch breaks abstraction
- More boilerplate than copy-and-modify

**Verdict**: ❌ Rejected - YAGNI (You Ain't Gonna Need It)

### Alternative 3: Keep Both (Rejected)

**Idea**: Maintain both Dukascopy and Exness indefinitely

**Pros**:
- User choice
- Fallback if Exness fails

**Cons**:
- Dukascopy unusable (77.5% reliability)
- Maintenance burden (2× providers)
- Confusing to users ("which should I use?")

**Verdict**: ❌ Rejected - Dukascopy proven unreliable

### Alternative 4: Delete Dukascopy Immediately (Rejected)

**Idea**: Remove Dukascopy code entirely

**Pros**:
- Clean slate
- No deprecated code

**Cons**:
- Loss of volume-tracking implementation
- Loss of binary parsing patterns
- Harder to rollback if Exness fails

**Verdict**: ❌ Rejected - Preserve for reference/research

---

## Recommendation Summary

### ✅ APPROVED: Copy-and-Modify with Deprecation

**Execution order**:

1. **Immediate** (Phases 1-6): Core migration (3 hours)
   - Copy directory, gut client.rs, simplify types
   - Faster than from-scratch (no design decisions)
   - Lower risk than abstraction layers

2. **Next session** (Phases 7-10): Tests + docs (1.5 hours)
   - Validate against same Jan 15-19 data
   - Document deprecation clearly

3. **Long term**: Deprecation → eventual removal
   - Keep Dukascopy code for 1 release cycle
   - Remove in v3.1.0 or later (after Exness proven)

**Why this is sensible**:
- ✅ Reuses 80% of logic (builder, spread stats, validation)
- ✅ Simplifies maintenance (removes LZMA, binary, config complexity)
- ✅ Preserves history (Dukascopy deprecated, not deleted)
- ✅ Fast execution (4.5 hours vs weeks of design)
- ✅ Low risk (isolated modules, comprehensive tests)

**You were correct**: Copy-and-modify is the pragmatic choice here.

---

## Next Steps

**DO NOT EXECUTE YET** - This is a planning document.

When ready to proceed:

```bash
# 1. Review this plan with user
# 2. Get explicit approval for Phase 1-6 execution
# 3. Create feature branch
git checkout -b feature/exness-provider-migration

# 4. Execute phases sequentially
# 5. Validate after each phase
# 6. Open PR when all tests pass
```

**User confirmation needed** before proceeding.
