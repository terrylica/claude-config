# Rangebar API Reference (v5.0.0)

**Target Audience**: AI coding agents (Claude Code, Cursor, etc.) and developers
**Format**: Structured, machine-readable API documentation
**Last Updated**: 2025-10-17
**Status**: Complete (covers all 8 workspace crates)

---

## Quick Navigation

- [Core Types](#core-types) - `AggTrade`, `RangeBar`, `FixedPoint`
- [Processors](#processors) - Range bar computation
- [Data Providers](#data-providers) - Binance, Exness data sources
- [Export Formats](#export-formats) - CSV, Parquet, Arrow
- [Streaming](#streaming) - Real-time processing
- [Batch Analytics](#batch-analytics) - Historical analysis
- [Common Patterns](#common-patterns) - Typical workflows
- [Error Handling](#error-handling) - Error types and patterns

---

## Core Types

### AggTrade (rangebar-core)

**Purpose**: Represents aggregated trade data (unified format across all providers)

**Location**: `crates/rangebar-core/src/types.rs`

**Type Signature**:
```rust
pub struct AggTrade {
    pub agg_trade_id: i64,           // Unique trade identifier
    pub price: FixedPoint,            // Trade price (8-decimal precision)
    pub volume: FixedPoint,           // Trade volume (8-decimal precision)
    pub timestamp: i64,               // Microseconds since epoch (16-digit)
    pub first_trade_id: i64,          // First trade in aggregation
    pub last_trade_id: i64,           // Last trade in aggregation
    pub is_buyer_maker: bool,         // Market maker side
    pub data_source: DataSource,      // Origin (Binance/Exness/etc)
}
```

**Critical Invariants**:
- `timestamp` MUST be in microseconds (16-digit, not milliseconds)
- `price` and `volume` MUST be positive
- Trades MUST be sorted by `(timestamp, agg_trade_id)`

**Construction**:
```rust
use rangebar_core::{AggTrade, FixedPoint, DataSource};

let trade = AggTrade {
    agg_trade_id: 1,
    price: FixedPoint::from_str("50000.12345678")?,
    volume: FixedPoint::from_str("1.5")?,
    timestamp: 1609459200000000,  // μs (16-digit)
    first_trade_id: 1,
    last_trade_id: 1,
    is_buyer_maker: false,
    data_source: DataSource::BinanceSpot,
};
```

---

### RangeBar (rangebar-core)

**Purpose**: Represents completed range bar with OHLCV data

**Location**: `crates/rangebar-core/src/types.rs`

**Type Signature**:
```rust
pub struct RangeBar {
    // OHLCV fields
    pub open: FixedPoint,
    pub high: FixedPoint,
    pub low: FixedPoint,
    pub close: FixedPoint,
    pub volume: FixedPoint,

    // Temporal fields
    pub open_time: i64,               // Microseconds
    pub close_time: i64,              // Microseconds

    // Metadata
    pub turnover: i128,
    pub individual_trade_count: u32,
    pub agg_record_count: u32,
    pub first_trade_id: i64,
    pub last_trade_id: i64,
    pub data_source: DataSource,

    // Enhanced metrics
    pub buy_volume: FixedPoint,
    pub sell_volume: FixedPoint,
    pub buy_trade_count: u32,
    pub sell_trade_count: u32,
    pub vwap: FixedPoint,
    pub buy_turnover: i128,
    pub sell_turnover: i128,
}
```

**Critical Invariants**:
- `high >= low` ALWAYS
- `open_time < close_time` ALWAYS
- `(close == high) OR (close == low)` ALWAYS (breach tick closes bar)
- Threshold breach: `(high - open >= threshold) OR (open - low >= threshold)`

---

### FixedPoint (rangebar-core)

**Purpose**: 8-decimal fixed-point arithmetic (eliminates floating-point errors)

**Location**: `crates/rangebar-core/src/fixed_point.rs`

**Type Signature**:
```rust
pub struct FixedPoint(i64);  // Internal: value × 100,000,000

impl FixedPoint {
    pub const SCALE: i64 = 100_000_000;  // 8 decimals

    pub fn from_str(s: &str) -> Result<Self, ParseError>;
    pub fn to_f64(&self) -> f64;
    pub fn to_i64_scaled(&self) -> i64;
}

// Arithmetic traits: Add, Sub, Mul, Div, Neg
```

**Pattern - String Parsing** (RECOMMENDED):
```rust
use rangebar_core::FixedPoint;

// ✅ Correct: Parse from string (exact decimal)
let price = FixedPoint::from_str("50000.12345678")?;

// ❌ Wrong: Direct f64 (introduces rounding errors)
// let price = FixedPoint::from_f64(50000.12345678);  // NO from_f64 method
```

**Pattern - Arithmetic**:
```rust
let a = FixedPoint::from_str("100.5")?;
let b = FixedPoint::from_str("2.5")?;

let sum = a + b;           // 103.0
let diff = a - b;          // 98.0
let product = a * b;       // 251.25
let quotient = a / b;      // 40.2
```

---

## Processors

### RangeBarProcessor (rangebar-core)

**Purpose**: Core algorithm for generating range bars from trades

**Location**: `crates/rangebar-core/src/processor.rs`

**Type Signature**:
```rust
pub struct RangeBarProcessor {
    threshold_bps: u32,  // In 0.1 BPS units (v3.0.0+)
    // ... internal state
}

impl RangeBarProcessor {
    pub fn new(threshold_bps: u32) -> Result<Self, ProcessingError>;

    pub fn process_agg_trade_records(
        &mut self,
        trades: &[AggTrade]
    ) -> Result<Vec<RangeBar>, ProcessingError>;
}
```

**Critical - Threshold Units** (v3.0.0 breaking change):
```rust
// v3.0.0+: Threshold in 0.1 BPS units
let processor = RangeBarProcessor::new(250)?;  // 250 × 0.1 = 25 BPS = 0.25%

// v2.x (OLD): Threshold in 1 BPS units
// let processor = RangeBarProcessor::new(25)?;  // 25 BPS (DEPRECATED)
```

**Pattern - Basic Processing**:
```rust
use rangebar_core::{RangeBarProcessor, AggTrade};

let mut processor = RangeBarProcessor::new(250)?;  // 25 BPS threshold
let bars = processor.process_agg_trade_records(&trades)?;

println!("Generated {} bars from {} trades", bars.len(), trades.len());
```

**Algorithm Guarantee**: Non-lookahead bias (uses only current and past data)

---

## Data Providers

### Binance Historical Data (rangebar-providers)

**Location**: `crates/rangebar-providers/src/binance/mod.rs`

**Type Signature**:
```rust
pub struct HistoricalDataLoader {
    symbol: String,
    market_type: String,  // "spot", "um", "cm"
}

impl HistoricalDataLoader {
    pub fn new(symbol: &str) -> Self;  // Defaults to spot
    pub fn new_with_market(symbol: &str, market_type: &str) -> Self;

    pub async fn load_recent_day(&self) -> Result<Vec<AggTrade>>;
    pub async fn load_historical_range(&self, days: usize) -> Result<Vec<AggTrade>>;
}

// Tier-1 symbol discovery
pub fn get_tier1_symbols() -> Vec<String>;  // ["BTC", "ETH", "SOL", ...]
pub fn get_tier1_usdt_pairs() -> Vec<String>;  // ["BTCUSDT", "ETHUSDT", ...]
```

**Pattern - Load Spot Data**:
```rust
use rangebar_providers::binance::HistoricalDataLoader;

let loader = HistoricalDataLoader::new("BTCUSDT");  // Defaults to spot
let trades = loader.load_recent_day().await?;
```

**Pattern - Load Futures Data**:
```rust
use rangebar_providers::binance::HistoricalDataLoader;

let loader = HistoricalDataLoader::new_with_market("BTCUSDT", "um");  // UM futures
let trades = loader.load_historical_range(7).await?;  // Last 7 days
```

**Pattern - Tier-1 Symbol Discovery**:
```rust
use rangebar_providers::binance::get_tier1_symbols;

let symbols = get_tier1_symbols();  // Returns 18 Tier-1 symbols
for symbol in symbols {
    println!("Processing {}", symbol);
}
```

**Critical - Market Types**:
- `"spot"` - Spot market (default, 16-digit μs timestamps)
- `"um"` - USD-M futures (13-digit ms → normalized to 16-digit μs)
- `"cm"` - Coin-M futures (13-digit ms → normalized to 16-digit μs)

---

### Exness Forex Data (rangebar-providers)

**Location**: `crates/rangebar-providers/src/exness/mod.rs`

**Type Signature**:
```rust
pub struct ExnessFetcher {
    variant: String,  // "EURUSD", "EURUSD_Plus", etc.
}

impl ExnessFetcher {
    pub fn new(variant: &str) -> Self;

    pub async fn fetch_month(
        &self,
        year: u32,
        month: u32
    ) -> Result<Vec<ExnessTick>>;
}

pub struct ExnessRangeBarBuilder {
    threshold_units: u32,
    // ... internal state
}

impl ExnessRangeBarBuilder {
    pub fn new(
        threshold_units: u32,
        variant: &str,
        strictness: ValidationStrictness
    ) -> Result<Self, ProcessingError>;

    pub fn process_tick(
        &mut self,
        tick: &ExnessTick
    ) -> Result<Option<ExnessRangeBar>, ProcessingError>;
}
```

**Pattern - Fetch Exness Data**:
```rust
use rangebar_providers::exness::{ExnessFetcher, ExnessRangeBarBuilder, ValidationStrictness};

// Fetch tick data
let fetcher = ExnessFetcher::new("EURUSD");
let ticks = fetcher.fetch_month(2024, 10).await?;

// Build range bars
let mut builder = ExnessRangeBarBuilder::new(
    5,  // 0.5 BPS threshold (5 × 0.1 BPS)
    "EURUSD",
    ValidationStrictness::Standard
)?;

for tick in ticks {
    if let Some(bar) = builder.process_tick(&tick)? {
        // Process completed bar
        println!("Bar: {:?}", bar);
    }
}
```

**Critical - Exness Variant**: Use `"EURUSD"` Standard (best SNR=1.90, 1.26M ticks/month)

---

## Export Formats

### Polars Exporter (rangebar-io)

**Location**: `crates/rangebar-io/src/formats/polars.rs`

**Type Signature**:
```rust
pub struct PolarsExporter;

impl PolarsExporter {
    pub fn new() -> Self;

    pub fn export_parquet(
        &self,
        bars: &[RangeBar],
        path: &str
    ) -> Result<()>;

    pub fn export_arrow_ipc(
        &self,
        bars: &[RangeBar],
        path: &str
    ) -> Result<()>;

    pub fn export_streaming_csv(
        &self,
        bars: &[RangeBar],
        path: &str
    ) -> Result<()>;
}
```

**Pattern - Export to Parquet** (70%+ compression):
```rust
use rangebar_io::PolarsExporter;

let exporter = PolarsExporter::new();
exporter.export_parquet(&bars, "output.parquet")?;
```

**Pattern - Export to Arrow IPC** (zero-copy Python):
```rust
use rangebar_io::ArrowExporter;

let exporter = ArrowExporter::new();
exporter.export(&bars, "output.arrow")?;
```

**Python Integration** (Arrow zero-copy):
```python
import pyarrow as pa

with pa.ipc.open_file("output.arrow") as f:
    table = f.read_all()
    df = table.to_pandas()  # Zero-copy transfer
```

---

## Streaming

### StreamingProcessor (rangebar-streaming)

**Purpose**: Real-time range bar generation with bounded memory

**Location**: `crates/rangebar-streaming/src/lib.rs`

**Type Signature**:
```rust
pub struct StreamingProcessor;

impl StreamingProcessor {
    pub fn new(threshold_bps: u32) -> Result<Self, StreamingError>;

    pub fn with_config(
        threshold_bps: u32,
        config: StreamingProcessorConfig
    ) -> Result<Self, StreamingError>;

    pub async fn process_stream<S>(
        &mut self,
        stream: S
    ) -> Result<StreamingMetrics, StreamingError>
    where
        S: Stream<Item = AggTrade>;
}

pub struct StreamingMetrics {
    pub trades_processed: u64,
    pub bars_generated: u64,
    pub processing_duration: Duration,
    pub throughput_trades_per_sec: f64,
    pub circuit_breaker_active: bool,
}
```

**Pattern - Stream Processing**:
```rust
use rangebar_streaming::StreamingProcessor;
use futures::stream::StreamExt;

let mut processor = StreamingProcessor::new(250)?;
let metrics = processor.process_stream(websocket_stream).await?;

println!("Processed {} trades → {} bars",
    metrics.trades_processed,
    metrics.bars_generated
);
```

**Critical - Memory**: Bounded by `max_buffer_size` config (default: 10,000 trades)

---

## Batch Analytics

### BatchAnalysisEngine (rangebar-batch)

**Purpose**: Parallel multi-symbol analysis with comprehensive statistics

**Location**: `crates/rangebar-batch/src/lib.rs`

**Type Signature**:
```rust
pub struct BatchAnalysisEngine;

impl BatchAnalysisEngine {
    pub fn new() -> Self;

    pub fn analyze_single_symbol(
        &self,
        bars: &[RangeBar],
        symbol: &str
    ) -> Result<AnalysisReport>;

    pub fn analyze_multiple_symbols(
        &self,
        data: HashMap<String, Vec<RangeBar>>
    ) -> Result<Vec<AnalysisReport>>;
}

pub struct AnalysisReport {
    pub symbol: String,
    pub total_bars: usize,
    pub price_statistics: PriceStats,
    pub volume_statistics: VolumeStats,
    pub time_statistics: TimeStats,
}
```

**Pattern - Multi-Symbol Analysis**:
```rust
use rangebar_batch::BatchAnalysisEngine;
use std::collections::HashMap;

let engine = BatchAnalysisEngine::new();

let mut data: HashMap<String, Vec<RangeBar>> = HashMap::new();
data.insert("BTCUSDT".to_string(), btc_bars);
data.insert("ETHUSDT".to_string(), eth_bars);

let reports = engine.analyze_multiple_symbols(data)?;  // Parallel via Rayon

for report in reports {
    println!("{}: {} bars, mean price ${:.2}",
        report.symbol,
        report.total_bars,
        report.price_statistics.mean
    );
}
```

---

## Common Patterns

### Pattern 1: Complete Pipeline (Load → Process → Export)

```rust
use rangebar_providers::binance::HistoricalDataLoader;
use rangebar_core::RangeBarProcessor;
use rangebar_io::PolarsExporter;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. Load data
    let loader = HistoricalDataLoader::new("BTCUSDT");
    let trades = loader.load_historical_range(7).await?;

    // 2. Generate range bars
    let mut processor = RangeBarProcessor::new(250)?;  // 25 BPS
    let bars = processor.process_agg_trade_records(&trades)?;

    // 3. Export to Parquet
    let exporter = PolarsExporter::new();
    exporter.export_parquet(&bars, "btcusdt_bars.parquet")?;

    Ok(())
}
```

**Dependencies**:
```toml
rangebar-core = "5.0.0"
rangebar-providers = { version = "5.0.0", features = ["binance"] }
rangebar-io = { version = "5.0.0", features = ["polars-io"] }
tokio = { version = "1.0", features = ["full"] }
```

---

### Pattern 2: Multi-Symbol Parallel Processing

```rust
use rangebar_providers::binance::{get_tier1_symbols, HistoricalDataLoader};
use rangebar_core::RangeBarProcessor;
use rayon::prelude::*;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let symbols = get_tier1_symbols();  // 18 Tier-1 symbols

    // Parallel processing using Rayon
    let results: Vec<_> = symbols.par_iter()
        .map(|symbol| {
            // Each symbol processed in parallel
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(async {
                let loader = HistoricalDataLoader::new(symbol);
                let trades = loader.load_recent_day().await?;

                let mut processor = RangeBarProcessor::new(250)?;
                let bars = processor.process_agg_trade_records(&trades)?;

                Ok::<_, Box<dyn std::error::Error>>((symbol.clone(), bars.len()))
            })
        })
        .collect();

    for result in results {
        let (symbol, bar_count) = result?;
        println!("{}: {} bars", symbol, bar_count);
    }

    Ok(())
}
```

---

### Pattern 3: Streaming with Circuit Breaker

```rust
use rangebar_streaming::{StreamingProcessor, StreamingProcessorConfig};

let config = StreamingProcessorConfig {
    max_buffer_size: 50_000,
    circuit_breaker_threshold: 100,  // Open after 100 errors
    metrics_interval_secs: 60,
    ..Default::default()
};

let mut processor = StreamingProcessor::with_config(250, config)?;
let metrics = processor.process_stream(websocket_stream).await?;

if metrics.circuit_breaker_active {
    eprintln!("⚠️  Circuit breaker activated - too many errors");
}
```

---

## Error Handling

### Error Types

**rangebar-core**:
```rust
pub enum ProcessingError {
    InvalidThreshold(String),
    ParseError(String),
    InvalidPrice(String),
    TimestampError(String),
}
```

**rangebar-providers**:
```rust
pub enum ProviderError {
    NetworkError(String),
    DataNotFound(String),
    ParseError(String),
    ValidationError(String),
}
```

**rangebar-io**:
```rust
pub enum IoError {
    FileWriteError(String),
    SerializationError(String),
    PolarsError(String),
}
```

### Pattern - Error Propagation

```rust
use rangebar_core::{RangeBarProcessor, ProcessingError};

fn process_data(trades: &[AggTrade]) -> Result<Vec<RangeBar>, ProcessingError> {
    let mut processor = RangeBarProcessor::new(250)?;  // Propagate error
    let bars = processor.process_agg_trade_records(trades)?;  // Propagate error
    Ok(bars)
}
```

### Pattern - Error Context

```rust
use rangebar_providers::binance::HistoricalDataLoader;

async fn load_data(symbol: &str) -> Result<Vec<AggTrade>, Box<dyn std::error::Error>> {
    let loader = HistoricalDataLoader::new(symbol);

    let trades = loader.load_recent_day().await
        .map_err(|e| format!("Failed to load {} data: {}", symbol, e))?;

    Ok(trades)
}
```

---

## CLI Tools Reference

**Location**: `crates/rangebar-cli/src/bin/`

| Tool | Purpose | Example |
|------|---------|---------|
| `tier1-symbol-discovery` | Discover Tier-1 symbols | `--format comprehensive` |
| `data-structure-validator` | Validate aggTrades schema | `--markets spot,um` |
| `rangebar-export` | Export range bars to CSV | `BTCUSDT 2024-01-01 2024-01-31 250 ./output` |
| `spot-tier1-processor` | Batch process all Tier-1 | `--threshold-bps 25 --workers 16` |
| `polars-benchmark` | Benchmark Polars performance | `--input data.csv --output-dir ./bench` |
| `temporal-integrity-test-only` | Validate temporal ordering | `--input data.csv` |

---

## Cross-References

**Architecture**: [`ARCHITECTURE.md`](ARCHITECTURE.md)
**Migration Guide**: [`development/MIGRATION-v4-to-v5.md`](development/MIGRATION-v4-to-v5.md)
**Planning Docs**: [`planning/INDEX.md`](planning/INDEX.md)
**Crate READMEs**: `../../crates/*/README.md`
**Examples**: `../../examples/`

---

## AI Agent Optimization Notes

**For Claude Code / AI Coding Agents**:

1. **All type signatures are fully explicit** - no implicit generics or type inference needed
2. **Patterns section provides copy-paste templates** - minimal adaptation required
3. **Critical invariants documented** - understand constraints before code generation
4. **Error handling is explicit** - all Result types documented with error variants
5. **Cross-references use absolute paths** - no ambiguous relative paths
6. **v3.0.0 threshold breaking change** - explicitly called out in multiple places
7. **Dependencies listed for each pattern** - immediate Cargo.toml generation

**Recommended AI Agent Workflow**:
1. Start with "Common Patterns" section for typical use cases
2. Reference "Core Types" for type signatures and invariants
3. Check "Error Handling" for proper Result propagation
4. Verify threshold values (250 = 25 BPS in v3.0.0+)
5. Use cross-references for deeper implementation details

---

**Document Status**: ✅ Complete
**Coverage**: 8/8 workspace crates
**Last Validation**: 2025-10-17
**Format Version**: 1.0 (AI-agent-optimized)
