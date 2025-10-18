# rangebar-core

Core algorithm and types for non-lookahead range bar construction from tick data.

## Overview

`rangebar-core` provides the fundamental algorithm for constructing range bars - a time-independent charting technique where bars close when price moves ±threshold basis points from the bar's open price. This implementation guarantees no lookahead bias, making it suitable for backtesting and live trading systems.

## Key Features

- **Fixed-Point Arithmetic**: 8-decimal precision (SCALE = 100,000,000) eliminates floating-point errors
- **Non-Lookahead Algorithm**: Threshold breach detection uses only current and past data
- **Minimal Dependencies**: Only 4 essential dependencies (chrono, serde, serde_json, thiserror)
- **Type Safety**: Strongly-typed `AggTrade`, `RangeBar`, and `FixedPoint` structures
- **Serialization Support**: Full serde support for all core types

## Core Types

### AggTrade

Represents aggregated trade data with microsecond-precision timestamps:

```rust
pub struct AggTrade {
    pub agg_trade_id: i64,
    pub price: FixedPoint,
    pub volume: FixedPoint,
    pub timestamp: i64,  // microseconds
    // ... other fields
}
```

### RangeBar

Represents a completed range bar with OHLCV data:

```rust
pub struct RangeBar {
    pub open: FixedPoint,
    pub high: FixedPoint,
    pub low: FixedPoint,
    pub close: FixedPoint,
    pub volume: FixedPoint,
    pub open_time: i64,
    pub close_time: i64,
    // ... other fields
}
```

### FixedPoint

8-decimal fixed-point arithmetic for exact decimal representation:

```rust
pub struct FixedPoint(i64);  // Value × 100,000,000

impl FixedPoint {
    pub const SCALE: i64 = 100_000_000;
    pub fn from_str(s: &str) -> Result<Self>;
    pub fn to_f64(&self) -> f64;
}
```

## Usage

### Basic Range Bar Processing

```rust
use rangebar_core::{RangeBarProcessor, AggTrade};

// Create processor with 25 BPS (0.25%) threshold
// v3.0.0+ uses 0.1 BPS units: 250 = 25 BPS
let mut processor = RangeBarProcessor::new(250)?;

// Process trades
let bars = processor.process_agg_trade_records(&trades)?;
```

### Algorithm Invariants

Range bars close when price moves ±threshold BPS from the bar's OPEN price:

```rust
// Every bar satisfies:
assert!(high_breach → close_breach);
assert!(low_breach → close_breach);

// Where:
// high_breach = (high - open) ≥ threshold
// low_breach = (open - low) ≥ threshold
// close_breach = (close == high) || (close == low)
```

## Dependencies

- **chrono** `0.4` - Timestamp handling and conversions
- **serde** `1.0` - Serialization framework
- **serde_json** `1.0` - JSON serialization
- **thiserror** `2.0` - Ergonomic error handling

## Version

Current version: **5.0.0** (modular crate architecture)

## Critical Notes

### Threshold Units (v3.0.0 Breaking Change)

v3.0.0 changed threshold units from 1 BPS to 0.1 BPS:

- **Old API (v2.x)**: `new(25)` = 25 BPS = 0.25%
- **New API (v3.0.0+)**: `new(250)` = 250 × 0.1 BPS = 25 BPS = 0.25%

**Migration**: Multiply all threshold values by 10.

### Timestamp Precision

All timestamps are in microseconds (16-digit). Different data sources require normalization:

- **Binance Spot**: Native 16-digit μs (no conversion)
- **Binance UM Futures**: 13-digit ms → multiply by 1000
- **Exness**: Converted during tick processing

## Documentation

- Comprehensive architecture: `/Users/terryli/eon/rangebar/docs/ARCHITECTURE.md `
- Migration guides: `/Users/terryli/eon/rangebar/docs/planning/ `
- API examples: `/Users/terryli/eon/rangebar/examples/ `

## License

See LICENSE file in the repository root.
