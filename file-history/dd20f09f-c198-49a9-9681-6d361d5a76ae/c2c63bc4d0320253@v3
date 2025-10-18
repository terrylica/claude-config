# Test Data Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-16

## Overview

This guide explains when to use real CSV data vs synthetic generated data in integration tests, and how to use the test data infrastructure.

## Test Data Types

### Real Market Data (CSV)

**Location**: `../../crates/rangebar-core/src/test_data_loader.rs`

**Purpose**: Validation of range bar construction against real market behavior

**When to Use**:
- Validating algorithm correctness with real market data
- Testing multiple threshold scenarios (25 bps, 50 bps, 100 bps)
- Data integrity validation (temporal ordering, positive prices/volumes)
- Threshold scaling behavior (bar count decreases with wider thresholds)
- Acceptance testing and final validation

**Available Datasets**:
- BTCUSDT: 5,000 trades from 2025-09-01
- ETHUSDT: 10,000 trades from 2025-09-01

**Loading Data**:
```rust
use rangebar_core::test_data_loader::{load_btcusdt_test_data, load_ethusdt_test_data};

#[test]
fn test_with_real_btcusdt_data() {
    let trades = load_btcusdt_test_data().expect("Failed to load BTCUSDT data");
    // trades.len() == 5000
}

#[test]
fn test_with_real_ethusdt_data() {
    let trades = load_ethusdt_test_data().expect("Failed to load ETHUSDT data");
    // trades.len() == 10000
}
```

**Characteristics**:
- Deterministic (same data every run)
- Real market patterns (volatility, trends, gaps)
- Fixed size (5,000 or 10,000 trades)
- Pre-validated (temporal ordering, data integrity)

**Limitations**:
- Fixed datasets (cannot adjust size or characteristics)
- Limited to BTCUSDT and ETHUSDT
- Cannot test edge cases (precision limits, extreme volumes, etc.)

### Synthetic Generated Data

**Location**: `../../crates/rangebar-core/src/test_utils/generators.rs`

**Purpose**: Controlled testing of specific scenarios and edge cases

**When to Use**:
- Testing edge cases (precision limits, extreme volumes, timestamp boundaries)
- Large-scale testing (1M+ trades for performance and memory tests)
- Multi-day boundary scenarios (session transitions, year boundaries)
- Frequency variation testing (HFT, low-frequency, mixed)
- Stress testing (rapid threshold hits, floating point edge cases)
- Parametric testing (custom dataset sizes, patterns, characteristics)

**Available Generators**:

#### Basic Trade Creation
```rust
use rangebar_core::test_utils::generators::create_test_trade;

let trade = create_test_trade(
    1,           // Trade ID
    50000.0,     // Price
    1659312000000 // Timestamp (ms)
);
```

#### Large-Scale Datasets
```rust
use rangebar_core::test_utils::generators::create_massive_realistic_dataset;

// Generate 1M trades with realistic market patterns
let trades = create_massive_realistic_dataset(1_000_000);
```

#### Multi-Day Boundaries
```rust
use rangebar_core::test_utils::generators::create_multi_day_boundary_dataset;

// Generate 7 days of data with varying patterns
let trades = create_multi_day_boundary_dataset(7);
```

#### Market Session Data
```rust
use rangebar_core::test_utils::generators::{
    create_asian_session_data,
    create_european_session_data,
    create_us_session_data,
    create_weekend_gap_data,
};

let asian = create_asian_session_data();      // Low volatility
let european = create_european_session_data(); // Medium volatility
let us = create_us_session_data();            // High volatility
let weekend = create_weekend_gap_data();      // Very low activity
```

#### Frequency Variations
```rust
use rangebar_core::test_utils::generators::{
    create_high_frequency_data,
    create_medium_frequency_data,
    create_low_frequency_data,
    create_mixed_frequency_data,
};

let hft = create_high_frequency_data(10);    // 10ms intervals
let medium = create_medium_frequency_data(500); // 500ms intervals
let low = create_low_frequency_data(5000);   // 5s intervals
let mixed = create_mixed_frequency_data();   // Variable intervals
```

#### Stress Testing
```rust
use rangebar_core::test_utils::generators::{
    create_rapid_threshold_hit_data,
    create_precision_limit_data,
    create_volume_extreme_data,
    create_timestamp_edge_data,
    create_floating_point_stress_data,
};

let rapid = create_rapid_threshold_hit_data();      // Rapid threshold crossings
let precision = create_precision_limit_data();      // 8 decimal place edge cases
let volume = create_volume_extreme_data();          // Volume extremes
let timestamps = create_timestamp_edge_data();      // Timestamp boundaries
let floating = create_floating_point_stress_data(); // Float precision edge cases
```

**Characteristics**:
- Deterministic (pure functions, no randomness)
- Parameterized (adjustable size, patterns, characteristics)
- Mathematical patterns (sine waves, trends, oscillations)
- No external dependencies or I/O

## Processing Styles

### Batch Processing
```rust
use rangebar_core::test_utils::generators::process_batch_style;

let trades = load_btcusdt_test_data().unwrap();
let range_bars = process_batch_style(&trades, 25); // 25 bps threshold
```

### Streaming Processing
```rust
use rangebar_core::test_utils::generators::process_streaming_style;

let trades = load_btcusdt_test_data().unwrap();
let range_bars = process_streaming_style(&trades, 25).await; // 25 bps threshold
```

## Decision Matrix

| Test Scenario | Data Type | Rationale |
|--------------|-----------|-----------|
| Algorithm correctness validation | Real CSV | Validates against actual market behavior |
| Threshold scaling (25/50/100 bps) | Real CSV | Real market patterns for threshold comparison |
| Data integrity (temporal ordering, positive values) | Real CSV | Pre-validated real data |
| Edge cases (precision, extremes) | Synthetic | Controlled edge case generation |
| Large-scale (1M+ trades) | Synthetic | Real datasets too small |
| Multi-day boundaries | Synthetic | Controlled day-to-day pattern variations |
| Session transitions (Asian/EU/US) | Synthetic | Controlled session characteristics |
| Frequency variations (HFT/mixed) | Synthetic | Controlled interval patterns |
| Stress testing | Synthetic | Controlled extreme conditions |
| Performance benchmarks | Synthetic | Parametric dataset sizes |
| Memory efficiency tests | Synthetic | Large parametric datasets |

## Examples

### Example 1: Real Data Test (BTCUSDT)
```rust
use rangebar::{FixedPoint, RangeBar, RangeBarProcessor};
use rangebar_core::test_data_loader::load_btcusdt_test_data;

#[test]
fn test_btcusdt_standard_threshold() {
    let mut processor = RangeBarProcessor::new(25); // 25 bps
    let trades = load_btcusdt_test_data().expect("Failed to load data");

    let range_bars = processor
        .process_agg_trade_records(&trades)
        .expect("Failed to process trades");

    assert!(!range_bars.is_empty());

    // Validate OHLCV integrity
    for bar in &range_bars {
        assert!(bar.high >= bar.open);
        assert!(bar.high >= bar.close);
        assert!(bar.low <= bar.open);
        assert!(bar.low <= bar.close);
        assert!(bar.volume > FixedPoint(0));
    }
}
```

### Example 2: Synthetic Data Test (Large Scale)
```rust
use rangebar_core::test_utils::generators::{
    create_massive_realistic_dataset,
    process_batch_style,
};

#[tokio::test]
async fn test_massive_dataset_performance() {
    let trades = create_massive_realistic_dataset(1_000_000);
    let range_bars = process_batch_style(&trades, 25);

    assert!(!range_bars.is_empty());
    assert!(range_bars.len() < trades.len()); // Bars compress trades
}
```

### Example 3: Multi-Scenario Test (Both Types)
```rust
use rangebar_core::test_data_loader::load_btcusdt_test_data;
use rangebar_core::test_utils::generators::create_massive_realistic_dataset;

#[test]
fn test_real_vs_synthetic_consistency() {
    // Real data
    let real_trades = load_btcusdt_test_data().unwrap();
    let real_bars = process_batch_style(&real_trades, 25);

    // Synthetic data (same scale)
    let synthetic_trades = create_massive_realistic_dataset(5000);
    let synthetic_bars = process_batch_style(&synthetic_trades, 25);

    // Both should produce valid bars
    assert!(!real_bars.is_empty());
    assert!(!synthetic_bars.is_empty());
}
```

## Best Practices

### 1. Use Real Data for Acceptance Tests
Real CSV data validates that the algorithm works correctly with actual market behavior.

### 2. Use Synthetic Data for Edge Cases
Synthetic generators allow controlled testing of boundary conditions and edge cases that may not appear in real data.

### 3. Combine Both for Comprehensive Coverage
Use real data for correctness validation and synthetic data for edge cases, performance, and parametric testing.

### 4. Fail Fast
Both real and synthetic data loaders use fail-fast error handling. If data loading fails, the test fails immediately with a clear error message.

### 5. Document Data Characteristics
When using synthetic data, document the pattern characteristics (volatility, frequency, session type) in test comments.

## Service Level Objectives (SLOs)

### Real Data Loader SLOs
- **Availability**: 100% (fail-fast on missing files)
- **Correctness**: 100% (strict schema validation, no data loss)
- **Observability**: 100% (all errors include file path and line context)
- **Maintainability**: 100% (csv crate + serde, no custom parsing)

### Synthetic Generator SLOs
- **Availability**: 100% (deterministic, no external dependencies)
- **Correctness**: 100% (monotonic timestamps, valid prices, no corruption)
- **Observability**: 100% (predictable patterns, documented parameters)
- **Maintainability**: 100% (single source of truth, no duplication)

## File Locations

```
crates/rangebar-core/src/
├── test_data_loader.rs          # Real CSV data loader (245 lines)
└── test_utils/
    └── generators.rs             # Synthetic data generators (513 lines)

test_data/
├── BTCUSDT/
│   └── BTCUSDT_aggTrades_20250901.csv  # 5,000 trades
└── ETHUSDT/
    └── ETHUSDT_aggTrades_20250901.csv  # 10,000 trades

crates/rangebar/tests/
├── binance_btcusdt_real_data_test.rs   # Real data tests (218 lines)
├── binance_ethusdt_real_data_test.rs   # Real data tests (218 lines)
├── large_boundary_tests.rs             # Synthetic data tests
├── multi_month_memory_tests.rs         # Synthetic data tests
└── cross_year_speed_comparison.rs      # Synthetic data tests
```

## Running Tests

### Run Real Data Tests Only
```bash
cargo nextest run --package rangebar --features test-utils \
  --test binance_btcusdt_real_data_test \
  --test binance_ethusdt_real_data_test
```

### Run Synthetic Data Tests Only
```bash
cargo nextest run --package rangebar --features test-utils \
  --test large_boundary_tests \
  --test multi_month_memory_tests \
  --test cross_year_speed_comparison
```

### Run All Integration Tests
```bash
cargo nextest run --workspace --features rangebar/test-utils,rangebar/providers,rangebar/exness,rangebar/streaming
```

## References

- Real data loader: `../../crates/rangebar-core/src/test_data_loader.rs`
- Synthetic generators: `../../crates/rangebar-core/src/test_utils/generators.rs`
- Real data tests: `../../crates/rangebar/tests/binance_btcusdt_real_data_test.rs`
- Test cleanup plan: `../planning/test-cleanup-plan-v2-llm-friendly.md`
