# Range Bar Construction from Dukascopy Tick Data
**Design Document** | Ultra-concise implementation strategy

---

## Executive Summary

**Core Challenge:** Dukascopy provides market maker **quotes** (bid/ask with volumes), not actual **trades** like Binance aggTrades. This fundamental semantic difference requires careful adaptation while preserving the existing range bar algorithm.

**Solution:** Adapter pattern with mid-price conversion. Use `(bid+ask)/2` as synthetic trade price, feed into existing `RangeBarProcessor` with zero core changes. Wrapper struct `DukascopyRangeBar { base: RangeBar, spread_stats: SpreadStats }` preserves all Forex-specific information that quotes provide (spread dynamics, liquidity asymmetry) while maintaining compatibility with standard range bar consumers.

**Key Design Decisions:**
- **Volume:** Total liquidity (`bid_vol + ask_vol`), no buy/sell segregation (direction unknown)
- **Direction:** `is_buyer_maker = false` (arbitrary default, not used for segregation)
- **Validation:** Configurable strictness with type-specific price ranges (Forex: 0.01-10k)
- **SpreadStats:** Per-bar SMA for averages (reset on bar close), not rolling EMA
- **Config:** Instrument config embedded in binary (1,607 instruments via `include_str!`)
- **Error Handling:** Module-level `DukascopyError` with automatic conversion via `From` traits

**Implementation Effort:** Estimated 4-8 hours for core conversion, 2-4 hours for validation/testing.

---

## Core Challenge: Data Structure Mismatch

### Binance aggTrades (Current)
```rust
struct AggTrade {
    price: FixedPoint,         // Single price per trade
    volume: FixedPoint,        // Actual quantity traded
    is_buyer_maker: bool,      // Direction indicator
    timestamp: i64,            // Microseconds
}
```
**Semantic:** Actual executed trades with real volume

### Dukascopy Ticks (New)
```rust
struct DukascopyTick {
    ask: f64,                  // TWO prices (not one!)
    bid: f64,                  
    ask_volume: f32,           // Available liquidity (not traded)
    bid_volume: f32,
    timestamp: i64,            // Milliseconds
}
```
**Semantic:** Market maker quotes with available liquidity

---

## Solution: Mid-Price Synthetic Trade

### Conversion Strategy

**Transform Dukascopy tick → Synthetic aggTrade with validation:**

```rust
fn tick_to_synthetic_trade(
    tick: &DukascopyTick,
    instrument: &str,
    id: i64,
    strictness: ValidationStrictness,
) -> Result<AggTrade, DukascopyError> {
    // 1. Validate tick (bid > 0, ask > 0, bid < ask, spread reasonable)
    validate_tick(tick, strictness)?;

    // 2. Get decimal factor from embedded config
    let decimal_factor = get_decimal_factor(instrument)?;
    let instrument_type = get_instrument_type(instrument)?;

    // 3. Calculate mid-price (market consensus price)
    let mid_price = (tick.ask + tick.bid) / 2.0;
    let converted_price = mid_price * decimal_factor as f64;

    // 4. Validate converted price is reasonable for instrument type
    validate_converted_price(converted_price, instrument_type)?;

    // 5. Aggregate liquidity (NOT traded volume)
    let total_liquidity = tick.ask_volume + tick.bid_volume;

    // 6. Direction UNKNOWN for quote data (no buy/sell inference)
    let is_buyer_maker = false;  // Arbitrary default (not used)

    Ok(AggTrade {
        agg_trade_id: id,
        price: FixedPoint::from_f64(converted_price),
        volume: FixedPoint::from_f64(total_liquidity),  // Could be 0.0
        first_trade_id: id,
        last_trade_id: id,
        timestamp: normalize_timestamp(tick.timestamp),  // ms → μs
        is_buyer_maker,
        is_best_match: None,  // N/A for Dukascopy
    })
}
```

**Why mid-price?**
- Standard in academic finance (bid-ask midpoint)
- Represents true market equilibrium
- Used in all major indices (S&P 500, NASDAQ, etc.)
- Avoids bias toward bid or ask side

**Validation Levels** (Configurable):
- **Permissive:** Basic checks (bid > 0, ask > 0, bid < ask)
- **Strict:** + spread < 10% (catches obvious errors) [DEFAULT]
- **Paranoid:** + spread < 1% (flags suspicious data)

---

## Algorithm Preservation

### Current Rangebar Logic (Unchanged!)
```rust
// From processor.rs
if bar_state.bar.is_breach(
    trade.price,                    // ← Was aggTrade.price
    bar_state.upper_threshold,      //    Now: mid-price from tick
    bar_state.lower_threshold,
) {
    // Close bar, start new one
}
```

**No changes needed to core algorithm!**

The rangebar algorithm is price-movement based:
- Compare each "trade" price to bar's OPEN
- Close when price moves ±threshold from OPEN
- Works identically with synthetic mid-price trades

---

## Volume Semantics: Critical Distinction

### aggTrades Volume
```
volume = sum(actual_quantity_traded)
Example: 1.5 BTC actually changed hands
```
**Interpretation:** Executed transaction volume

### Dukascopy Volume
```
volume = bid_volume + ask_volume (available liquidity)
Example: 2.3 lots available at bid + 1.8 lots at ask = 4.1
```
**Interpretation:** Order book depth snapshot

### Handling Strategy

**Decision: Dual tracking with no buy/sell segregation**

```rust
pub struct DukascopyRangeBar {
    pub base: RangeBar {
        // Standard OHLCV
        volume: FixedPoint,              // = total_bid_liquidity + total_ask_liquidity

        // NO buy/sell segregation (direction unknown)
        buy_volume: FixedPoint(0),       // Not tracked
        sell_volume: FixedPoint(0),      // Not tracked
        buy_trade_count: 0,              // Not tracked
        sell_trade_count: 0,             // Not tracked
        individual_trade_count: u32,     // = tick_count
        // ... other fields
    },

    // Dukascopy-specific microstructure
    pub spread_stats: SpreadStats {
        // Accumulators (per-bar, reset on close)
        avg_spread: FixedPoint,          // SMA (spread_sum / tick_count)
        avg_bid_liquidity: FixedPoint,   // SMA (bid_sum / tick_count)
        avg_ask_liquidity: FixedPoint,   // SMA (ask_sum / tick_count)

        min_spread: FixedPoint,
        max_spread: FixedPoint,

        tick_count: u32,
        zero_volume_tick_count: u32,     // Track frequency

        total_bid_liquidity: FixedPoint,
        total_ask_liquidity: FixedPoint,
    }
}
```

**Zero-Volume Handling:**
- **All ticks processed** (including zero-volume)
- Zero-volume ticks update price (OHLC) but contribute 0 to volume
- Tracked separately in `zero_volume_tick_count` for diagnostics
- Tick arrival = market activity regardless of volume

---

## Streaming Implementation

### Adapter Pattern with Error Handling

```rust
pub struct DukascopyRangeBarBuilder {
    processor: RangeBarProcessor,
    tick_counter: i64,
    instrument: String,
    validation_strictness: ValidationStrictness,
    current_spread_stats: SpreadStats,
}

impl DukascopyRangeBarBuilder {
    pub fn new(
        threshold_bps: u32,
        instrument: impl Into<String>,
        validation_strictness: ValidationStrictness,
    ) -> Self {
        Self {
            processor: RangeBarProcessor::new(threshold_bps),
            tick_counter: 0,
            instrument: instrument.into(),
            validation_strictness,
            current_spread_stats: SpreadStats::new(),
        }
    }

    pub fn process_tick(
        &mut self,
        tick: &DukascopyTick
    ) -> Result<Option<DukascopyRangeBar>, DukascopyError> {
        // 1. Validate tick
        validate_tick(tick, self.validation_strictness)?;

        // 2. Update spread stats (accumulates within current bar)
        self.current_spread_stats.update(tick);

        // 3. Convert to synthetic trade
        let synthetic_trade = tick_to_synthetic_trade(
            tick,
            &self.instrument,
            self.tick_counter,
            self.validation_strictness,
        )?;
        self.tick_counter += 1;

        // 4. Process through core processor (ZERO changes to algorithm!)
        let maybe_bar = self.processor.process_single_trade(synthetic_trade)?;

        // 5. If bar closed, wrap with spread stats
        if let Some(base) = maybe_bar {
            let completed_bar = DukascopyRangeBar {
                base,
                spread_stats: self.current_spread_stats.clone(),
            };

            // Reset for next bar (per-bar semantics)
            self.current_spread_stats = SpreadStats::new();

            Ok(Some(completed_bar))
        } else {
            Ok(None)
        }
    }

    pub fn get_incomplete_bar(&self) -> Option<DukascopyRangeBar> {
        self.processor.get_incomplete_bar().map(|base| {
            DukascopyRangeBar {
                base,
                spread_stats: self.current_spread_stats.clone(),
            }
        })
    }
}
```

**Key insights:**
- Adapter pattern preserves 100% of existing rangebar logic
- Result-based error handling (no panics)
- Per-bar SpreadStats (reset on close)
- Automatic conversion via `From` traits

---

## Spread Dynamics Tracking

### Additional Microstructure (Beyond aggTrades)

Dukascopy data enables spread analysis with per-bar SMA:

```rust
pub struct SpreadStats {
    // Accumulators (for SMA calculation)
    spread_sum: FixedPoint,
    bid_liquidity_sum: FixedPoint,
    ask_liquidity_sum: FixedPoint,

    // Min/Max (per bar)
    min_spread: FixedPoint,
    max_spread: FixedPoint,

    // Counters (per bar)
    tick_count: u32,
    zero_volume_tick_count: u32,

    // Totals (per bar)
    total_bid_liquidity: FixedPoint,
    total_ask_liquidity: FixedPoint,
}

impl SpreadStats {
    pub fn new() -> Self {
        Self {
            spread_sum: FixedPoint::ZERO,
            bid_liquidity_sum: FixedPoint::ZERO,
            ask_liquidity_sum: FixedPoint::ZERO,
            min_spread: FixedPoint::MAX,
            max_spread: FixedPoint::MIN,
            tick_count: 0,
            zero_volume_tick_count: 0,
            total_bid_liquidity: FixedPoint::ZERO,
            total_ask_liquidity: FixedPoint::ZERO,
        }
    }

    pub fn update(&mut self, tick: &DukascopyTick) {
        let spread = FixedPoint::from_f64(tick.ask - tick.bid);
        let bid_vol = FixedPoint::from_f64(tick.bid_volume);
        let ask_vol = FixedPoint::from_f64(tick.ask_volume);

        // Accumulate for SMA (O(1))
        self.spread_sum += spread;
        self.bid_liquidity_sum += bid_vol;
        self.ask_liquidity_sum += ask_vol;

        // Track min/max
        self.min_spread = self.min_spread.min(spread);
        self.max_spread = self.max_spread.max(spread);

        // Count ticks
        self.tick_count += 1;
        if tick.bid_volume == 0.0 && tick.ask_volume == 0.0 {
            self.zero_volume_tick_count += 1;
        }

        // Track totals
        self.total_bid_liquidity += bid_vol;
        self.total_ask_liquidity += ask_vol;
    }

    // Calculate averages on demand (O(1))
    pub fn avg_spread(&self) -> FixedPoint {
        if self.tick_count > 0 {
            FixedPoint(self.spread_sum.0 / self.tick_count as i64)
        } else {
            FixedPoint::ZERO
        }
    }

    pub fn avg_bid_liquidity(&self) -> FixedPoint {
        if self.tick_count > 0 {
            FixedPoint(self.bid_liquidity_sum.0 / self.tick_count as i64)
        } else {
            FixedPoint::ZERO
        }
    }

    pub fn avg_ask_liquidity(&self) -> FixedPoint {
        if self.tick_count > 0 {
            FixedPoint(self.ask_liquidity_sum.0 / self.tick_count as i64)
        } else {
            FixedPoint::ZERO
        }
    }
}
```

**Advantage over aggTrades:**
- Capture bid-ask spread information unavailable in trade data
- Track liquidity asymmetry (bid vs ask volume)
- Per-bar SMA for spread/liquidity (simple, correct, O(1))

---

## Quick Reference

**Conversion:**
```rust
mid_price = (bid + ask) / 2.0
price_fixed = FixedPoint::from_f64(mid_price * decimal_factor)
volume = bid_volume + ask_volume  // Could be 0.0
```

**Volume & Direction:**
- `RangeBar.volume` = total liquidity (`bid_vol + ask_vol`)
- `buy_volume` = 0, `sell_volume` = 0 (direction unknown)
- `individual_trade_count` = tick_count

**Structure:**
```rust
DukascopyRangeBar {
    base: RangeBar,           // Standard OHLCV
    spread_stats: SpreadStats // Dukascopy-specific metrics
}
```

**Error Types:**
```rust
DukascopyError {
    Conversion(ConversionError),  // Invalid tick, unknown instrument
    Processing(ProcessingError),  // Core processor errors
}
```

**Config:**
- Instrument config: Embedded via `include_str!("dukascopy-instrument-config.toml")`
- Decimal factors: 100000 (Forex majors), 1000 (JPY pairs), 10 (Crypto)
- Validation: Configurable strictness (Permissive/Strict/Paranoid)

**Timestamp:**
- Input: Milliseconds (GMT)
- Output: Microseconds (via `normalize_timestamp()`)
- Validation: 2000-2035 range

---

## Implementation Roadmap

### Phase 1: Core Conversion (Minimal)
```
src/data/dukascopy/
├── mod.rs
├── tick.rs              # DukascopyTick struct
├── conversion.rs        # tick_to_synthetic_trade()
└── builder.rs           # DukascopyRangeBarBuilder adapter
```

**Dependencies:**
- Use existing `RangeBarProcessor` (zero changes)
- Convert tick → AggTrade → existing pipeline

### Phase 2: Enhanced Microstructure (Optional)
```
src/data/dukascopy/
└── enhanced_bar.rs      # Spread tracking, liquidity metrics
```

**Extends RangeBar with:**
- Spread statistics (avg, min, max)
- Liquidity asymmetry metrics
- Order book dynamics

### Phase 3: Performance Optimization (Future)
```
src/data/dukascopy/
└── direct_processor.rs  # Skip AggTrade conversion overhead
```

**Optimization:**
- Process mid-price directly (avoid struct conversion)
- Zero-copy tick parsing
- SIMD for bulk operations

---

## Validation Strategy

### Cross-Verification Tests

**Test 1: Price Movement Consistency**
```rust
// Given same price movements, should produce same bars
let dukascopy_bars = process_dukascopy_ticks(ticks);
let synthetic_aggTrades = ticks_to_synthetic_trades(ticks);
let aggtrade_bars = process_agg_trades(synthetic_aggTrades);

// Range bar boundaries should match (OHLC times)
assert_eq!(dukascopy_bars.len(), aggtrade_bars.len());
for (d_bar, a_bar) in dukascopy_bars.iter().zip(aggtrade_bars) {
    assert_eq!(d_bar.open_time, a_bar.open_time);
    assert_eq!(d_bar.close_time, a_bar.close_time);
    assert_approx_eq!(d_bar.open, a_bar.open);  // Mid-price
}
```

**Test 2: Threshold Breach Logic**
```rust
// Ensure breach detection works correctly with mid-price
let threshold_bps = 25;
let builder = DukascopyRangeBarBuilder::new(threshold_bps);

// Create ticks that breach +25 bps from open
let mut bars = vec![];
for tick in synthetic_breach_sequence() {
    if let Some(bar) = builder.process_tick(tick) {
        bars.push(bar);
    }
}

assert_eq!(bars.len(), 1);  // Should close exactly one bar
assert!(bars[0].is_breach_valid(threshold_bps));
```

**Test 3: Volume Semantics**
```rust
// Verify volume aggregation matches semantic expectation
let forex_ticks = load_forex_eurusd();
let crypto_ticks = load_crypto_btcusd();

let forex_bars = process_forex(forex_ticks);
let crypto_bars = process_crypto(crypto_ticks);

// Forex should sum liquidity
assert!(forex_bars[0].volume > FixedPoint(0));

// Crypto should use tick count
assert_eq!(crypto_bars[0].tick_count, expected_tick_count);
```

---

## Key Decisions Summary

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Price** | Mid-price `(bid+ask)/2` with decimal factor | Academic standard, unbiased, instrument-aware |
| **Volume** | Total liquidity (`bid_vol + ask_vol`) | Represents available liquidity snapshot |
| **Direction** | `is_buyer_maker = false` (not used) | Direction unknown for quote data |
| **Buy/Sell Segregation** | No segregation (all zeros) | Honest semantics (quote data ≠ trade data) |
| **Zero-Volume Ticks** | Process all (track frequency) | Tick arrival = activity regardless of volume |
| **Validation** | Configurable strictness | Type-specific price ranges (Forex: 0.01-10k) |
| **SpreadStats** | Per-bar SMA (reset on close) | Simple, correct, O(1) updates and queries |
| **Error Handling** | Module-level `DukascopyError` | Clean boundaries, `From` trait auto-conversion |
| **Config Source** | Embedded TOML (`include_str!`) | Zero runtime deps, self-contained binary |
| **Timestamp** | Expand validation (2000-2035) | Covers historical Forex + future data |
| **Algorithm** | **Zero core changes** | Adapter pattern preserves 100% of logic |
| **Structure** | `DukascopyRangeBar { base, spread_stats }` | Wrapper pattern, maximal info retention |

---

## Performance Expectations

### Throughput Estimates

**Per-hour processing (single-threaded):**
```
Download:        ~50ms  (20KB compressed)
Decompress:      ~10ms  (LZMA to 100KB)
Parse ticks:     ~1ms   (5,000 ticks × 20 bytes)
Convert to mid:  ~0.5ms (arithmetic only)
Rangebar proc:   ~1ms   (existing algorithm)
────────────────────────
Total:           ~63ms per hour
```

**Parallelization (10 hours):**
```
Sequential:  10 hours × 63ms = 630ms
Parallel:    max(downloads) ≈ 100ms  (10x speedup)
```

**Memory footprint:**
```
Input:  100KB/hour (decompressed ticks)
Output: ~32 bytes/bar × ~10 bars = 320 bytes
Ratio:  312:1 compression via range bars
```

---

## Implementation Checklist

**Core Types & Config:**
- [ ] `DukascopyTick` struct (bid, ask, volumes, timestamp_ms)
- [ ] `DukascopyRangeBar { base: RangeBar, spread_stats: SpreadStats }`
- [ ] `SpreadStats` struct with SMA accumulators
- [ ] Embed `dukascopy-instrument-config.toml` via `include_str!()`
- [ ] `get_decimal_factor(instrument)` from embedded config
- [ ] `get_instrument_type(instrument)` for validation

**Error Handling:**
- [ ] `DukascopyError` enum (Conversion, Processing)
- [ ] `ConversionError` enum (InvalidTick, UnsupportedInstrument, InvalidPriceRange)
- [ ] `From<ProcessingError>` and `From<ConversionError>` traits
- [ ] `ValidationStrictness` enum (Permissive, Strict, Paranoid)

**Conversion Layer:**
- [ ] `tick_to_synthetic_trade()` with Result return type
- [ ] `validate_tick()` - bid/ask checks, crossed market, spread limits
- [ ] `validate_converted_price()` - type-specific ranges (Forex: 0.01-10k)
- [ ] Mid-price calculation with decimal factor
- [ ] Timestamp normalization (ms → μs via `normalize_timestamp()`)
- [ ] Zero-volume handling (use actual volume, could be 0.0)

**Builder Implementation:**
- [ ] `DukascopyRangeBarBuilder` with `current_spread_stats` field
- [ ] Constructor: `new(threshold_bps, instrument, validation_strictness)`
- [ ] `process_tick()` → `Result<Option<DukascopyRangeBar>, DukascopyError>`
- [ ] `get_incomplete_bar()` → `Option<DukascopyRangeBar>`
- [ ] SpreadStats reset on bar close (per-bar semantics)

**SpreadStats Implementation:**
- [ ] Per-bar SMA accumulators (spread_sum, bid_sum, ask_sum)
- [ ] `update(tick)` - O(1) accumulation
- [ ] `avg_spread()`, `avg_bid_liquidity()`, `avg_ask_liquidity()` - O(1) calculation
- [ ] Min/max tracking, tick_count, zero_volume_tick_count
- [ ] `Clone` trait implementation for snapshot on bar close

**Core Changes:**
- [ ] Expand `timestamp.rs` validation range: 2000-2035
- [ ] Implement `RangeBarProcessor::get_incomplete_bar()` (currently stubbed)

**Validation & Testing:**
- [ ] Unit tests: mid-price calculation with decimal factors
- [ ] Unit tests: tick validation (crossed markets, zero prices, excessive spread)
- [ ] Unit tests: price range validation by instrument type
- [ ] Integration tests: threshold breach detection with Dukascopy ticks
- [ ] End-to-end: EURUSD ticks → `DukascopyRangeBar` with spread stats
- [ ] Zero-volume tick handling (verify OHLC updates, volume = 0)
- [ ] SpreadStats SMA correctness (verify per-bar averages)
- [ ] Performance benchmark: 10 hours in <200ms

---

## Example Usage

```rust
use rangebar::data::dukascopy::{
    DukascopyTick,
    DukascopyRangeBarBuilder,
    DukascopyError,
    ValidationStrictness,
};

fn main() -> Result<(), DukascopyError> {
    // Initialize builder with validation strictness
    let threshold_bps = 25;  // 0.25% range bars
    let mut builder = DukascopyRangeBarBuilder::new(
        threshold_bps,
        "EURUSD",
        ValidationStrictness::Strict,  // Default: catches obvious errors
    );

    // Stream processing with error handling
    for tick in tick_stream {
        match builder.process_tick(&tick) {
            Ok(Some(completed_bar)) => {
                // Bar closed successfully
                println!("Bar: O={} H={} L={} C={} V={}",
                    completed_bar.base.open,
                    completed_bar.base.high,
                    completed_bar.base.low,
                    completed_bar.base.close,
                    completed_bar.base.volume,
                );

                // Access Dukascopy-specific metrics
                println!("  Spread: avg={} min={} max={}",
                    completed_bar.spread_stats.avg_spread(),
                    completed_bar.spread_stats.min_spread,
                    completed_bar.spread_stats.max_spread,
                );
                println!("  Ticks: {} (zero-volume: {})",
                    completed_bar.spread_stats.tick_count,
                    completed_bar.spread_stats.zero_volume_tick_count,
                );
            },
            Ok(None) => {
                // Tick processed, bar still accumulating
            },
            Err(e) => {
                // Validation or processing error
                eprintln!("Error processing tick: {:?}", e);
                // Decide: skip tick, abort, or retry with different strictness
            }
        }
    }

    // Get incomplete bar at stream end
    if let Some(partial_bar) = builder.get_incomplete_bar() {
        println!("Partial bar: {:?}", partial_bar);
    }

    Ok(())
}
```

---

## Conclusion

**Core Insight:** Dukascopy ticks are fundamentally different from aggTrades (quotes vs trades), but the **rangebar algorithm is price-movement based** and works identically with mid-price as synthetic trade price.

**Implementation Strategy:** Adapter pattern with wrapper struct (`DukascopyRangeBar { base, spread_stats }`) preserves 100% of existing rangebar logic while handling data structure conversion and validation at the boundary.

**Key Achievements:**
- **Zero core changes:** Existing `RangeBarProcessor` untouched except `get_incomplete_bar()` implementation
- **Semantic honesty:** No buy/sell segregation (direction unknown), no invented volume for zero-volume ticks
- **Robust validation:** Configurable strictness with type-specific price ranges catches config errors early
- **Information retention:** SpreadStats captures Forex-specific metrics unavailable in aggTrades
- **Per-bar semantics:** SMA calculations reset on bar close for clean bar-local statistics

**Result:**
- Same range bar semantics (±threshold price movement)
- Different volume semantics (liquidity snapshots vs executed trades)
- Enhanced microstructure (spread tracking, liquidity asymmetry)
- Production-ready error handling (Result-based, no panics)

**Estimated Effort:**
- Core implementation: 4-8 hours
- Validation/testing: 2-4 hours
- **Total: 6-12 hours** for complete, production-ready Dukascopy integration
