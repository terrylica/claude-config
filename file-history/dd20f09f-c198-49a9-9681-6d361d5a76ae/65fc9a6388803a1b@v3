# rangebar

[![Crates.io](https://img.shields.io/crates/v/rangebar)](https://crates.io/crates/rangebar)
[![Documentation](https://docs.rs/rangebar/badge.svg)](https://docs.rs/rangebar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Non-lookahead range bar construction for cryptocurrency trading with temporal integrity guarantees.

## Quick Start

Add this to your `Cargo.toml`:

```toml
[dependencies]
rangebar = "5.0"
```

## Usage

```rust
use rangebar::{RangeBarProcessor, AggTrade, FixedPoint};

// Create processor with 25 basis points (0.25%) threshold
let mut processor = RangeBarProcessor::new(250);

// Create sample aggTrade
let trade = AggTrade {
    agg_trade_id: 1,
    price: FixedPoint::from_str("50000.0").unwrap(),
    volume: FixedPoint::from_str("1.0").unwrap(),
    first_trade_id: 1,
    last_trade_id: 1,
    timestamp: 1609459200000,
    is_buyer_maker: false,
};

// Process aggTrade records into range bars
let agg_trade_records = vec![trade];
let bars = processor.process_agg_trade_records(&agg_trade_records).unwrap();

for bar in bars {
    println!("Bar: O={} H={} L={} C={} V={}",
             bar.open, bar.high, bar.low, bar.close, bar.volume);
}
```

## Algorithm

See authoritative specification: [`docs/specifications/algorithm-spec.md`](docs/specifications/algorithm-spec.md)

Key properties: non-lookahead bias, fixed thresholds from bar open, breach inclusion.

## Features

- Non-lookahead bias range bar construction
- Fixed-point arithmetic for precision
- Streaming and batch processing modes
- Tier-1 cryptocurrency symbol discovery

## License

MIT license. See [LICENSE](LICENSE) for details.
