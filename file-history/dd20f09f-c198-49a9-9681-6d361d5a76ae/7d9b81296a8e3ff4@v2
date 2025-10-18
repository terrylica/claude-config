# rangebar-cli

Command-line tools for range bar processing, analysis, and validation.

## Overview

`rangebar-cli` consolidates all command-line binaries for the rangebar workspace. Provides tools for symbol discovery, data validation, range bar export, benchmarking, and analysis.

## Available Tools

### tier1-symbol-discovery

Discover Tier-1 cryptocurrency symbols across Binance markets:

```bash
# Comprehensive output with market matrix
cargo run --bin tier1-symbol-discovery -- --format comprehensive

# Minimal output (symbols only)
cargo run --bin tier1-symbol-discovery -- --format minimal
```

**Output**: 18 Tier-1 symbols available across spot, UM futures, and CM futures markets.

### data-structure-validator

Validate Binance aggTrades data structure across markets:

```bash
# Validate all Tier-1 symbols across spot/um/cm markets
cargo run --bin data-structure-validator --release

# Validate specific markets
cargo run --bin data-structure-validator -- --markets spot,um

# Custom date range
cargo run --bin data-structure-validator -- \
  --start-date 2024-01-01 --end-date 2024-12-31
```

**Features**:
- Cross-market schema detection (spot vs futures differences)
- Timestamp precision validation (16-digit μs vs 13-digit ms)
- SHA256 checksum verification (optional)
- Parallel processing with configurable workers

### rangebar-export

Export range bars from aggTrades data:

```bash
# Export BTCUSDT spot market (default)
cargo run --bin rangebar-export --release -- \
  BTCUSDT 2024-01-01 2024-01-31 250 ./output

# Export UM futures market
cargo run --bin rangebar-export --release -- \
  BTCUSDT 2024-01-01 2024-01-31 250 ./output um

# Threshold: 250 units × 0.1 BPS = 25 BPS = 0.25%
```

**Output**: CSV files with OHLCV data and enhanced metrics (trade counts, turnover, etc.).

### spot-tier1-processor

Batch processor for all Tier-1 spot symbols:

```bash
# Process all 18 Tier-1 symbols in parallel
cargo run --bin spot-tier1-processor --release -- \
  --start-date 2024-07-01 --end-date 2024-10-31 --threshold-bps 25

# Custom parallelism
cargo run --bin spot-tier1-processor -- --workers 16
```

**Features**:
- Parallel execution using Rayon (default: 8 workers)
- Comprehensive execution statistics
- JSON metadata with symbol performance rankings
- Automatic output file naming

### polars-benchmark

Benchmark Polars integration performance:

```bash
cargo run --bin polars-benchmark --features polars-io -- \
  --input ./data/BTCUSDT_bars.csv \
  --output-dir ./benchmark_output
```

**Tests**:
- Parquet export (70%+ compression target)
- Arrow IPC export (zero-copy Python)
- Streaming CSV export (2x-5x speedup target)
- General Polars performance

### temporal-integrity-test-only

Validate temporal integrity of Polars conversions:

```bash
cargo run --bin temporal-integrity-test-only --features polars-io -- \
  --input ./data/BTCUSDT_bars.csv
```

**Validates**:
- Monotonic timestamp ordering
- DataFrame operation safety
- Export readiness without round-trip conversion

### rangebar-api

RESTful API server for range bar processing (future):

```bash
cargo run --bin rangebar-api --release
```

## Tool Categories

### Discovery & Validation
- `tier1-symbol-discovery` - Symbol discovery
- `data-structure-validator` - Data validation

### Processing & Export
- `rangebar-export` - Single symbol export
- `spot-tier1-processor` - Batch Tier-1 processing

### Testing & Benchmarking
- `polars-benchmark` - Performance benchmarks
- `temporal-integrity-test-only` - Temporal validation

### Services
- `rangebar-api` - REST API server

## Common Flags

All tools support standard flags:

```bash
--help              # Show comprehensive help
--version           # Show version
--verbose, -v       # Verbose output
```

## Dependencies

`rangebar-cli` uses all workspace crates:

- **rangebar-core** - Core algorithm
- **rangebar-providers** - Data providers
- **rangebar-config** - Configuration
- **rangebar-io** - Export formats
- **rangebar-streaming** - Streaming processing
- **rangebar-batch** - Batch processing

## Version

Current version: **5.0.0** (modular crate architecture)

## Documentation

- Architecture: `/Users/terryli/eon/rangebar/docs/ARCHITECTURE.md `
- Examples: `/Users/terryli/eon/rangebar/examples/ `
- Each tool has comprehensive `--help` documentation

## License

See LICENSE file in the repository root.
