# Range Bar Algorithm Specification

**Version**: 5.0.0
**Status**: authoritative
**Created**: 2025-10-17
**Supersedes**: `docs/planning/architecture/algorithm-spec.md` (v1.0.0, archived)

---

## Purpose

This specification defines the **canonical range bar construction algorithm** implemented in the rangebar workspace. All implementations, documentation, and tests must conform to this specification.

**Single Source of Truth**: This document is the authoritative reference for algorithm behavior, replacing all duplicated descriptions in README files, code comments, and planning documents.

---

## Core Algorithm Definition

### Mathematical Formulation

**Threshold Units** (v3.0.0+): Thresholds specified in **tenths of basis points (0.1bps units)**

Given:
- `threshold_bps` = threshold in 0.1bps units (e.g., `250` = 25bps = 0.25%)
- Bar opens at price `P_open`

For each bar:
```
threshold_ratio = threshold_bps / 100_000  # Convert 0.1bps units to decimal
upper_breach = P_open + (P_open * threshold_ratio)
lower_breach = P_open - (P_open * threshold_ratio)
```

**Examples**:
```
threshold_bps = 250 (25bps = 0.25%)
  P_open = 50000.00
  upper_breach = 50125.00  (50000 × 1.0025)
  lower_breach = 49875.00  (50000 × 0.9975)

threshold_bps = 10 (1bps = 0.01%)
  P_open = 1.09450
  upper_breach = 1.09461  (1.09450 × 1.0001)
  lower_breach = 1.09439  (1.09450 × 0.9999)
```

**Bar closes when**: `tick_price >= upper_breach OR tick_price <= lower_breach`

### Critical Invariants

1. **Thresholds are FIXED**: Computed once when bar opens, never recalculated
2. **Based on OPEN only**: Not based on evolving high/low or current range
3. **Breach tick included**: The tick causing the breach belongs to the closing bar
4. **Non-lookahead**: Current tick cannot influence its own breach decision
5. **Next bar opens at breach tick**: The tick that closes bar N opens bar N+1

### Breaking Change History

**v3.0.0 (2025-09-24)**: Threshold units changed from 1bps to 0.1bps for precision
- **Migration**: Multiply all threshold values by 10
- **Before**: `threshold_bps = 25` (25bps = 0.25%)
- **After**: `threshold_bps = 250` (250 × 0.1bps = 25bps = 0.25%)
- **Rationale**: Enable precise thresholds like 0.5bps (5 units) for forex markets

---

## Implementation Pseudocode

### Core Processing Loop

```python
def process_agg_trade_records(trades, threshold_bps):
    """
    Convert sorted AggTrade records to range bars.

    Args:
        trades: List[AggTrade] sorted by (timestamp, agg_trade_id)
        threshold_bps: u32 in 0.1bps units (250 = 25bps = 0.25%)

    Returns:
        List[RangeBar] completed bars only (no partial bars)
    """
    threshold_ratio = threshold_bps / 100_000
    bars = []
    current_bar = None
    defer_open = False

    for trade in trades:
        if defer_open:
            # Previous bar closed, this trade opens new bar
            current_bar = initialize_bar(trade, threshold_ratio)
            defer_open = False
            continue

        if current_bar is None:
            # First bar initialization
            current_bar = initialize_bar(trade, threshold_ratio)
            continue

        # Update bar with current trade
        current_bar.update(trade)

        # Check breach using FIXED thresholds (computed from open)
        if is_breach(trade.price, current_bar.upper_threshold, current_bar.lower_threshold):
            bars.append(current_bar.finalize())
            current_bar = None
            defer_open = True  # Next trade opens new bar

    # Omit final partial bar (strict algorithm compliance)
    return bars


def initialize_bar(trade, threshold_ratio):
    """Create new bar state with fixed thresholds."""
    bar = RangeBarState()
    bar.open = trade.price
    bar.high = trade.price
    bar.low = trade.price
    bar.close = trade.price
    bar.volume = trade.volume
    bar.open_time = trade.timestamp
    bar.close_time = trade.timestamp

    # Compute FIXED thresholds from opening price
    bar.upper_threshold = bar.open + (bar.open * threshold_ratio)
    bar.lower_threshold = bar.open - (bar.open * threshold_ratio)

    return bar


def is_breach(price, upper, lower):
    """Check if price breaches fixed thresholds."""
    return price >= upper or price <= lower
```

### Data Structures

```rust
pub struct AggTrade {
    pub agg_trade_id: i64,
    pub price: FixedPoint,        // 8-decimal precision (SCALE = 100_000_000)
    pub volume: FixedPoint,
    pub timestamp: i64,            // Microseconds (16-digit)
    pub first_trade_id: i64,
    pub last_trade_id: i64,
    pub is_buyer_maker: bool,
    pub is_best_match: Option<bool>,
}

pub struct RangeBar {
    pub open_time: i64,           // Microseconds
    pub close_time: i64,          // Microseconds
    pub open: FixedPoint,
    pub high: FixedPoint,
    pub low: FixedPoint,
    pub close: FixedPoint,
    pub volume: FixedPoint,
    pub turnover: i128,
    pub individual_trade_count: u32,
    pub agg_record_count: u32,
    pub first_trade_id: i64,
    pub last_trade_id: i64,
    pub buy_volume: FixedPoint,
    pub sell_volume: FixedPoint,
    pub buy_trade_count: u32,
    pub sell_trade_count: u32,
    pub vwap: FixedPoint,
    pub buy_turnover: i128,
    pub sell_turnover: i128,
}
```

---

## Data Source Specifications

### Binance (Crypto)

**Primary Asset Class**: Spot (default)
**Optional Markets**: UM Futures (USDT/USDC), CM Futures (Coin-margined)
**Source**: https://github.com/stas-prokopiev/binance_historical_data

**Data Type**: `aggTrades` (aggregate trades) ONLY

**Schema Differences**:

| Aspect | Spot | UM Futures | CM Futures |
|--------|------|------------|------------|
| Headers | No | Yes (descriptive) | Yes (descriptive) |
| Columns | `a,p,q,f,l,T,m` | `agg_trade_id,price,quantity,...` | Same as UM |
| Timestamp | 16-digit μs | 13-digit ms | 13-digit ms |
| Normalization | None (native) | ×1000 → 16-digit μs | ×1000 → 16-digit μs |

**Critical**: Use `aggTrades` nomenclature (not `trades`) in all naming and documentation.

**Temporal Integrity**: All timestamps normalized to **microseconds (16-digit)** for consistent ordering.

### Exness (Forex)

**Variant**: EURUSD Standard (default)
**API**: `https://ticks.ex2archive.com/ticks/EURUSD/{year}/{month}/Exness_EURUSD_{year}_{month}.zip`

**Data Format**: ZIP → CSV (Bid/Ask/Timestamp)

**Schema**:
```csv
"Exness","Symbol","Timestamp","Bid","Ask"
"exness","EURUSD_Standard","2024-01-15 00:00:00.032Z",1.0945,1.09456
```

**Characteristics**:
- Monthly granularity (~1.26M ticks/month for EURUSD 2019-2025)
- No volume data (Bid/Ask prices only)
- ISO 8601 UTC timestamps with millisecond precision
- ZIP compression (~10:1 ratio, ~9MB/month)

**Volume Semantics**:
- `RangeBar.volume` = 0 (no volume data available)
- `buy_volume` = 0 (direction unknown - market maker quotes)
- `sell_volume` = 0
- Use `SpreadStats` for market stress signals instead

**Threshold Recommendations**:
- HFT: 0.2bps (2 units) = 0.002%
- Intraday: 0.5bps (5 units) = 0.005%
- Swing: 1.0bps (10 units) = 0.01%

---

## Non-Lookahead Validation

### Breach Consistency Invariant

**Every completed bar must satisfy**:
```
IF (high - open) >= threshold THEN (close == high)
IF (open - low) >= threshold THEN (close == low)
```

**Explanation**: If high/low breached threshold, bar must close at that extreme.

**Validation Example**:
```rust
#[test]
fn test_breach_consistency() {
    let bar = completed_bar;
    let threshold = bar.open * 0.0025;  // 25bps for example

    let high_breach = (bar.high - bar.open) >= threshold;
    let low_breach = (bar.open - bar.low) >= threshold;

    if high_breach {
        assert_eq!(bar.close, bar.high, "High breach must close at high");
    }
    if low_breach {
        assert_eq!(bar.close, bar.low, "Low breach must close at low");
    }
}
```

### What Makes It Non-Lookahead

✅ **Correct (No Lookahead)**:
1. Compute thresholds from bar's open price (fixed)
2. Update bar statistics with current tick (high, low, close, volume)
3. Check if current tick breaches pre-computed thresholds
4. If breach: close bar, next tick opens new bar

❌ **Incorrect (Has Lookahead)**:
1. Update bar statistics with current tick
2. Recompute thresholds using updated high/low (dynamic)
3. Check if current tick breaches updated thresholds
4. This allows future information (updated high/low) to influence decision

---

## Edge Cases

### 1. Exact Threshold Breach

```
Open: 50000.00
Threshold: 250 (25bps = 0.25%)
Upper: 50125.00
Tick: 50125.00 (exact match)
Result: Bar closes (>= operator), breach tick included
```

### 2. Large Price Gap

```
Open: 50000.00
Threshold: 250 (25bps = 0.25%)
Range: [49875.00, 50125.00]
Tick: 51000.00 (+2% gap)
Result: Single bar closes at 51000.00 (NOT multiple bars to fill gap)
```

### 3. Oscillation Without Breach

```
Open: 50000.00
Threshold: 250 (25bps = 0.25%)
Ticks: 50100 (+0.2%), 49900 (-0.2%), 50120 (+0.24%)
Result: No bar closes (all within ±0.25%), continues building
```

### 4. Empty Input

```
trades = []
Result: Return empty list (no bars)
```

### 5. Unsorted Trades

```
trades = [trade2, trade1]  # Wrong order
Result: Raise UnsortedTrades error with index and timestamps
```

---

## Implementation Requirements

### Fixed-Point Arithmetic

**Rationale**: Avoid floating-point rounding errors, ensure deterministic results.

```rust
pub struct FixedPoint(i64);

impl FixedPoint {
    pub const SCALE: i64 = 100_000_000;  // 8-decimal precision

    pub fn from_str(s: &str) -> Result<Self, ParseError> {
        // Parse "50000.12345678" → 5000012345678_i64
    }

    pub fn to_f64(&self) -> f64 {
        self.0 as f64 / Self::SCALE as f64
    }
}

// Threshold calculation (v3.0.0: 0.1bps units)
pub fn compute_range_thresholds(open: FixedPoint, threshold_bps: u32) -> (FixedPoint, FixedPoint) {
    let open_val = open.0;
    let threshold = threshold_bps as i64;
    let upper = open_val + (open_val * threshold) / 100_000;  // BASIS_POINTS_SCALE
    let lower = open_val - (open_val * threshold) / 100_000;
    (FixedPoint(upper), FixedPoint(lower))
}
```

### Error Handling

**Policy**: Raise and propagate - no fallbacks, no silent failures.

```rust
#[derive(Error, Debug)]
pub enum ProcessingError {
    #[error("Trades not sorted at index {index}: prev=({prev_time}, {prev_id}), curr=({curr_time}, {curr_id})")]
    UnsortedTrades {
        index: usize,
        prev_time: i64,
        prev_id: i64,
        curr_time: i64,
        curr_id: i64,
    },

    #[error("Invalid threshold: {threshold_bps} (0.1bps units). Valid range: 1-100,000 (0.001%-100%)")]
    InvalidThreshold { threshold_bps: u32 },

    #[error("Empty trade data")]
    EmptyData,
}
```

### Performance Targets

| Dataset Size | Target Time | Memory Usage |
|--------------|-------------|--------------|
| 1M ticks | < 100ms | O(1) per bar (streaming) |
| 100M ticks | < 10s | O(N) for N bars (batch) |
| 1B ticks | < 100s | Parallel processing (Rayon) |

---

## References

**Source Code**:
- Core Algorithm: [`../../crates/rangebar-core/src/processor.rs`](../../crates/rangebar-core/src/processor.rs)
- Fixed-Point: [`../../crates/rangebar-core/src/fixed_point.rs`](../../crates/rangebar-core/src/fixed_point.rs)
- Types: [`../../crates/rangebar-core/src/types.rs`](../../crates/rangebar-core/src/types.rs)
- Binance Provider: [`../../crates/rangebar-providers/src/binance/mod.rs`](../../crates/rangebar-providers/src/binance/mod.rs)
- Exness Provider: [`../../crates/rangebar-providers/src/exness/mod.rs`](../../crates/rangebar-providers/src/exness/mod.rs)

**Migration Guides**:
- v4→v5 Workspace: [`../development/MIGRATION-v4-to-v5.md`](../development/MIGRATION-v4-to-v5.md)
- v3.0.0 Precision: [`../planning/v3.0.0-precision-migration-plan.md`](../planning/v3.0.0-precision-migration-plan.md)

**Architecture**:
- Overview: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)

**Superseded Documents**:
- [`../planning/architecture/algorithm-spec.md`](../planning/architecture/algorithm-spec.md) (v1.0.0, archived)

---

**END OF ALGORITHM SPECIFICATION**
