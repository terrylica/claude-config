# Architecture

Comprehensive architectural overview of the rangebar workspace.

## Table of Contents

- [Overview](#overview)
- [Workspace Structure](#workspace-structure)
- [Crate Dependency Graph](#crate-dependency-graph)
- [Data Flow](#data-flow)
- [Public APIs](#public-apis)
- [Design Patterns](#design-patterns)
- [Processing Modes](#processing-modes)

## Overview

Rangebar is a modular Rust workspace implementing non-lookahead range bar construction from tick data. The architecture prioritizes:

- **Minimal-dependency core**: Algorithm isolation with only 4 essential dependencies (chrono, serde, serde_json, thiserror)
- **Provider pattern**: Unified interface for multiple data sources (Binance, Exness)
- **Dual-mode processing**: Streaming (bounded memory) vs. Batch (high throughput)
- **Feature-gated compilation**: Selective compilation via Cargo features

**Version**: 5.0.0 (modular crate architecture)

## Workspace Structure

The workspace consists of 8 specialized crates:

### Core Crates

**rangebar-core** - Core algorithm and types
- Minimal dependencies: chrono (timestamps), serde/serde_json (serialization), thiserror (errors)
- Fixed-point arithmetic (8-decimal precision)
- Non-lookahead threshold breach detection
- Public types: `AggTrade`, `RangeBar`, `FixedPoint`, `RangeBarProcessor`

**rangebar-providers** - Data providers
- Binance: `HistoricalDataLoader`, aggTrades CSV/Parquet, Tier-1 symbol discovery
- Exness: `ExnessFetcher`, EURUSD Standard (forex)
- Unified `AggTrade` interface for all providers

**rangebar-config** - Configuration management
- Settings management via `config` crate
- Environment-aware configuration
- Public API: `Settings::load()`, `Settings::default()`

**rangebar-io** - I/O operations
- Polars integration for DataFrame operations
- Multiple export formats: CSV, Parquet, Arrow, IPC
- Streaming CSV export with bounded memory

### Engine Crates

**rangebar-streaming** - Real-time streaming processor
- Bounded memory processing (configurable buffer size)
- Circuit breaker pattern for error handling
- Real-time metrics collection
- Public API: `StreamingProcessor`, `StreamingConfig`, `StreamingMetrics`

**rangebar-batch** - Batch analytics engine
- High-throughput batch processing
- Multi-symbol parallel analysis
- Comprehensive statistics generation
- Public API: `BatchAnalysisEngine`, `BatchConfig`, `AnalysisReport`

### Tools & Compatibility

**rangebar-cli** - Command-line tools
- All binaries consolidated in `src/bin/` (6 total)
- Tools: `tier1-symbol-discovery`, `parallel-tier1-analysis`, `spot-tier1-processor`, `data-structure-validator`, `polars-benchmark`, `temporal-integrity-test-only`

**rangebar** - Meta-crate
- Backward compatibility with v4.0.0 API
- Re-exports all sub-crates
- Legacy module paths: `fixed_point`, `range_bars`, `types`, `tier1`, `data`

## Crate Dependency Graph

```
rangebar (meta-crate)
├── rangebar-core (4 deps: chrono, serde, serde_json, thiserror)
├── rangebar-providers
│   └── rangebar-core
├── rangebar-config
│   └── rangebar-core
├── rangebar-io
│   └── rangebar-core
├── rangebar-streaming
│   ├── rangebar-core
│   └── rangebar-providers
└── rangebar-batch
    ├── rangebar-core
    └── rangebar-io

rangebar-cli (standalone)
├── rangebar-core
├── rangebar-providers
├── rangebar-config
├── rangebar-io
├── rangebar-streaming
└── rangebar-batch
```

**Key Characteristics**:
- `rangebar-core` has minimal external dependencies (4 essential libs: chrono for timestamps, serde/serde_json for serialization, thiserror for error handling)
- All other crates depend on `rangebar-core`
- `rangebar-streaming` depends on `rangebar-providers` (data fetching)
- `rangebar-batch` depends on `rangebar-io` (Polars integration)
- `rangebar-cli` uses all crates

## Data Flow

High-level data processing pipeline:

```
1. Symbol Discovery
   ├── tier1-symbol-discovery → Multi-market symbol analysis
   └── Output: Symbol lists, market availability matrix

2. Data Structure Validation
   ├── data-structure-validator → Cross-market format verification
   └── Output: Schema validation reports

3. Data Fetching
   ├── HistoricalDataLoader (Binance) → Raw CSV/ZIP files
   ├── ExnessFetcher (Exness) → Tick data
   └── Output: Normalized AggTrade records

4. Preprocessing
   ├── CSV → Parquet conversion
   ├── Schema validation
   └── Output: Validated Parquet files

5. Range Bar Computation
   ├── RangeBarProcessor (core algorithm)
   ├── Fixed-point arithmetic (no float errors)
   └── Output: RangeBar sequences

6. Analysis (optional)
   ├── rangebar-analyze → Parallel Tier-1 analysis
   ├── Statistics generation
   └── Output: Analysis reports

7. Export
   ├── CSV, Parquet, Arrow, IPC formats
   ├── PolarsExporter → DataFrame operations
   └── Output: Structured bar data (OHLCV format)
```

**Data Types Flow**:
```
Raw CSV/JSON → AggTrade → RangeBar → DataFrame → File
             (providers) (core)     (io)      (exporters)
```

## Public APIs

### rangebar-core

**Core Types**:
```rust
pub struct AggTrade {
    pub agg_trade_id: i64,
    pub price: FixedPoint,
    pub volume: FixedPoint,
    pub timestamp: i64,  // microseconds
    // ... other fields
}

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

pub struct FixedPoint(i64);  // 8-decimal precision (SCALE = 100,000,000)
```

**Processor**:
```rust
impl RangeBarProcessor {
    pub fn new(threshold_bps: u32) -> Result<Self, ProcessingError>;
    pub fn process_agg_trade_records(&mut self, trades: &[AggTrade])
        -> Result<Vec<RangeBar>, ProcessingError>;
}
```

### rangebar-providers

**Binance**:
```rust
impl HistoricalDataLoader {
    pub fn new(symbol: &str) -> Self;
    pub fn new_with_market(symbol: &str, market_type: &str) -> Self;
    pub async fn load_historical_range(days: usize) -> Result<Vec<AggTrade>>;
}

pub fn get_tier1_symbols() -> Vec<String>;
pub fn get_tier1_usdt_pairs() -> Vec<String>;
```

**Exness**:
```rust
impl ExnessFetcher {
    pub fn new(variant: &str) -> Self;
    pub async fn fetch_month(year: u32, month: u32)
        -> Result<Vec<ExnessTick>>;
}

impl ExnessRangeBarBuilder {
    pub fn new(threshold_units: u32, variant: &str, strictness: ValidationStrictness)
        -> Result<Self, ProcessingError>;
    pub fn process_tick(&mut self, tick: &ExnessTick)
        -> Result<Option<ExnessRangeBar>, ProcessingError>;
}
```

### rangebar-config

```rust
impl Settings {
    pub fn load() -> Result<Self, ConfigError>;
    pub fn default() -> Self;
}

pub struct Settings {
    pub app: AppSettings,
    pub binance: BinanceSettings,
    // ... other fields
}
```

### rangebar-io

```rust
impl PolarsExporter {
    pub fn new() -> Self;
    pub fn export_to_parquet(&self, bars: &[RangeBar], path: &Path)
        -> Result<()>;
    pub fn export_to_csv(&self, bars: &[RangeBar], path: &Path)
        -> Result<()>;
}

impl StreamingCsvExporter {
    pub fn new(path: PathBuf) -> Result<Self>;
    pub fn write_bar(&mut self, bar: &RangeBar) -> Result<()>;
}
```

### rangebar-streaming

```rust
impl StreamingProcessor {
    pub fn new(threshold_bps: u32) -> Result<Self, StreamingError>;
    pub fn with_config(threshold_bps: u32, config: StreamingProcessorConfig)
        -> Result<Self, StreamingError>;
    pub async fn process_stream<S>(&mut self, stream: S)
        -> Result<StreamingMetrics, StreamingError>
    where
        S: Stream<Item = AggTrade>;
}

pub struct StreamingMetrics {
    pub trades_processed: u64,
    pub bars_generated: u64,
    pub processing_duration: Duration,
    // ... other metrics
}
```

### rangebar-batch

```rust
impl BatchAnalysisEngine {
    pub fn new() -> Self;
    pub fn analyze_single_symbol(&self, bars: &[RangeBar], symbol: &str)
        -> Result<AnalysisReport>;
    pub fn analyze_multiple_symbols(&self, data: HashMap<String, Vec<RangeBar>>)
        -> Result<Vec<AnalysisReport>>;
}

pub struct AnalysisReport {
    pub symbol: String,
    pub total_bars: usize,
    pub price_statistics: PriceStats,
    pub volume_statistics: VolumeStats,
    // ... other stats
}
```

## Design Patterns

### 1. Minimal-Dependency Core

**Pattern**: Algorithm isolation with minimal essential dependencies

**Implementation**:
```toml
# rangebar-core/Cargo.toml
[dependencies]
chrono = "0.4"           # Timestamp handling
serde = "1.0"            # Serialization support
serde_json = "1.0"       # JSON serialization
thiserror = "2.0"        # Ergonomic error handling
```

**Rationale**:
- **chrono**: Required for timestamp operations and conversions
- **serde/serde_json**: Enables serialization of core types (AggTrade, RangeBar)
- **thiserror**: Provides ergonomic error handling without boilerplate

**Benefits**:
- Minimal transitive dependency surface area (4 well-audited crates)
- Stable core algorithm with battle-tested dependencies
- Easy to audit and verify (all deps are Rust ecosystem standards)

### 2. Provider Pattern

**Pattern**: Unified interface for multiple data sources

**Implementation**:
```rust
// Common trait: AggTrade
pub struct AggTrade {
    pub timestamp: i64,  // microseconds (normalized)
    pub price: FixedPoint,
    pub volume: FixedPoint,
    // ... other fields
}

// Providers convert to AggTrade:
// Binance: CSV → AggTrade
// Exness: ExnessTick → AggTrade (via ExnessRangeBarBuilder)
```

**Benefits**:
- Unified processing pipeline
- Easy to add new data sources
- Temporal integrity via timestamp normalization (13-digit ms ↔ 16-digit μs)

### 3. Feature-Gated Compilation

**Pattern**: Selective compilation via Cargo features

**Implementation**:
```toml
# rangebar/Cargo.toml
[features]
default = ["core"]
providers = ["rangebar-providers"]
streaming = ["rangebar-streaming", "providers"]
batch = ["rangebar-batch", "io"]
full = ["providers", "config", "io", "streaming", "batch"]
```

**Benefits**:
- Smaller binary sizes
- Faster compilation
- Optional dependencies (e.g., Polars only when needed)

### 4. Fixed-Point Arithmetic

**Pattern**: Integer-based decimal arithmetic to avoid floating-point errors

**Implementation**:
```rust
pub struct FixedPoint(i64);  // Value × 100,000,000 (8 decimals)

impl FixedPoint {
    pub const SCALE: i64 = 100_000_000;

    pub fn from_str(s: &str) -> Result<Self> {
        // Parse decimal string to fixed-point integer
    }

    pub fn to_f64(&self) -> f64 {
        self.0 as f64 / Self::SCALE as f64
    }
}
```

**Benefits**:
- No floating-point rounding errors
- Exact decimal representation
- Deterministic results across platforms

### 5. Circuit Breaker Pattern

**Pattern**: Fault tolerance in streaming processing

**Implementation**:
```rust
pub struct StreamingProcessorConfig {
    pub max_buffer_size: usize,
    pub circuit_breaker_threshold: usize,
    // ... other fields
}

// Circuit breaker activates when error rate exceeds threshold
// Prevents cascade failures in real-time processing
```

**Benefits**:
- Graceful degradation under load
- Prevents memory exhaustion
- Real-time monitoring via metrics

## Processing Modes

### Streaming Mode (Real-time)

**Characteristics**:
- Bounded memory (configurable buffer size)
- Suitable for real-time tick processing
- Circuit breaker for error handling
- Metrics collection for monitoring

**Use Cases**:
- Live trading systems
- Real-time analytics
- WebSocket data ingestion

**Example**:
```rust
use rangebar::streaming::StreamingProcessor;

let threshold_bps = 25;  // 0.25% range bars
let mut processor = StreamingProcessor::new(threshold_bps)?;

// Process stream with bounded memory
let metrics = processor.process_stream(agg_trade_stream).await?;
println!("Processed {} trades", metrics.trades_processed);
```

### Batch Mode (Analytics)

**Characteristics**:
- High-throughput batch processing
- Multi-symbol parallel analysis (Rayon)
- Comprehensive statistics generation
- In-memory data structures

**Use Cases**:
- Historical backtesting
- Multi-symbol analysis
- Research and development

**Example**:
```rust
use rangebar::batch::BatchAnalysisEngine;

let engine = BatchAnalysisEngine::new();
let report = engine.analyze_single_symbol(&range_bars, "BTCUSDT")?;

println!("Total bars: {}", report.total_bars);
println!("Mean price: {}", report.price_statistics.mean);
```

### Comparison

| Feature | Streaming | Batch |
|---------|-----------|-------|
| Memory Usage | Bounded | Unbounded |
| Throughput | Moderate | High |
| Parallelism | Single-threaded | Multi-threaded (Rayon) |
| Real-time | Yes | No |
| Use Case | Live trading | Historical analysis |

## Critical Invariants

### Algorithm Correctness

**Threshold Breach Detection**:
- Range bars close when price moves ±threshold basis points from bar's **OPEN** price
- Breach tick becomes bar's close
- Next bar opens at breach tick's price

**Validation**:
```rust
// Every bar must satisfy:
assert!(high_breach → close_breach);
assert!(low_breach → close_breach);

// Where:
// high_breach = (high - open) ≥ threshold
// low_breach = (open - low) ≥ threshold
// close_breach = (close == high) || (close == low)
```

### Temporal Integrity

**Timestamp Normalization**:
- All timestamps normalized to microseconds (16-digit)
- Binance Spot: 16-digit μs (native)
- Binance UM Futures: 13-digit ms → 16-digit μs (×1000)
- Exness: Converted to μs during tick processing

**Validation**:
```rust
// Monotonic timestamp ordering
assert!(bar.open_time < bar.close_time);
assert!(bar[i].close_time ≤ bar[i+1].open_time);
```

### Data Integrity

**AggTrade Requirements**:
- Sorted by `(timestamp, agg_trade_id)`
- No duplicate `agg_trade_id` values
- All prices and volumes > 0

**Validation Tools**:
- `data-structure-validator`: Cross-market schema verification
- `temporal-integrity-validator`: Timestamp continuity checks

## Performance Characteristics

### Core Algorithm

- **Throughput**: <100ms per 1M ticks (single-threaded)
- **Memory**: O(1) per bar (streaming mode)
- **Precision**: 8-decimal fixed-point (no float errors)

### Batch Processing

- **Parallelism**: Rayon thread pool (N-1 CPUs)
- **Throughput**: Scales linearly with CPU cores
- **Memory**: O(N) for N bars (in-memory)

### Streaming Processing

- **Buffer Size**: Configurable (default: 10,000 trades)
- **Circuit Breaker**: Activates at error threshold
- **Metrics**: Real-time processing statistics

## Future Enhancements

### Planned Features

1. **Additional Providers**: Support for more data sources (Deribit, Kraken)
2. **WebSocket Streaming**: Real-time WebSocket ingestion
3. **Distributed Processing**: Kafka/Redis integration for horizontal scaling
4. **Enhanced Analytics**: Advanced statistics (autocorrelation, entropy)

### Known Limitations

1. **Examples**: 11/14 examples disabled (require feature flags in Cargo.toml)
2. **Documentation**: API docs incomplete for some modules
3. **Migration Docs**: Multiple migration docs need consolidation

## References

- **Algorithm Details**: `/Users/terryli/eon/rangebar/docs/planning/v3.0.0-precision-migration-plan.md`
- **Provider Specifications**: `/Users/terryli/eon/rangebar/docs/planning/exness-eurusd-standard-final-decision.md`
- **Migration Guides**: `/Users/terryli/eon/rangebar/docs/planning/` (multiple files)
- **Development Setup**: `/Users/terryli/eon/rangebar/.editorconfig`, `/Users/terryli/eon/rangebar/.rust-analyzer.toml`
