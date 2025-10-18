# Performance Profiling and Optimization Guide

Practical techniques for profiling and optimizing range bar processing workflows.

## Table of Contents

- [Quick Start](#quick-start)
- [Profiling Tools](#profiling-tools)
- [Common Bottlenecks](#common-bottlenecks)
- [Optimization Strategies](#optimization-strategies)
- [Benchmarking](#benchmarking)
- [Memory Profiling](#memory-profiling)

## Quick Start

### Basic Throughput Measurement

```rust
use rangebar_core::RangeBarProcessor;
use std::time::Instant;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let threshold_bps = 250;
    let trades = load_your_data()?;  // Your data loading logic

    let start = Instant::now();
    let mut processor = RangeBarProcessor::new(threshold_bps)?;
    let bars = processor.process_agg_trade_records(&trades)?;
    let duration = start.elapsed();

    println!("Processed {} trades → {} bars in {:.2}s",
        trades.len(),
        bars.len(),
        duration.as_secs_f64()
    );

    println!("Throughput: {:.0} trades/sec",
        trades.len() as f64 / duration.as_secs_f64()
    );

    Ok(())
}
```

**Expected Performance** (Apple M1 Pro, Ryzen 9 5950X):
- **1M trades**: 50-100ms (~10-20M trades/sec)
- **10M trades**: 200-400ms (~25-50M trades/sec)
- **100M trades**: 2-4s (~25-50M trades/sec)

**Performance Targets**:
- ✅ **Good**: >5M trades/sec
- ⚠️  **Acceptable**: 1-5M trades/sec
- ❌ **Slow**: <1M trades/sec (investigate bottlenecks)

## Profiling Tools

### 1. cargo-flamegraph (CPU Profiling)

**Installation**:
```bash
cargo install flamegraph
```

**Usage**:
```bash
# Profile your binary (example: tier1-symbol-discovery)
cargo flamegraph --bin tier1_symbol_discovery -- --format comprehensive

# Opens flamegraph.svg in browser
open flamegraph.svg
```

**Interpreting Flamegraphs**:
- **Wide bars**: Time-consuming functions (hot paths)
- **Tall stacks**: Deep call chains (potential optimization targets)
- **Look for**:
  - Heavy I/O operations (file reads, network)
  - Fixed-point arithmetic (should be fast)
  - Unnecessary allocations (clones, Vec growth)

### 2. cargo-criterion (Microbenchmarking)

**Setup** (`Cargo.toml`):
```toml
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "processor_bench"
harness = false
```

**Benchmark File** (`benches/processor_bench.rs`):
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion, Throughput};
use rangebar_core::{RangeBarProcessor, test_utils::generators};

fn bench_processor(c: &mut Criterion) {
    let mut group = c.benchmark_group("processor");

    for size in [10_000, 100_000, 1_000_000] {
        group.throughput(Throughput::Elements(size as u64));

        let trades = generators::create_massive_realistic_dataset(size);
        let threshold_bps = 250;

        group.bench_function(format!("{}_trades", size), |b| {
            b.iter(|| {
                let mut processor = RangeBarProcessor::new(threshold_bps).unwrap();
                processor.process_agg_trade_records(black_box(&trades)).unwrap()
            });
        });
    }

    group.finish();
}

criterion_group!(benches, bench_processor);
criterion_main!(benches);
```

**Run Benchmarks**:
```bash
cargo bench

# Output:
# processor/10000_trades   time: [1.234 ms 1.245 ms 1.256 ms]
#                          thrpt: [7.96M elem/s 8.04M elem/s 8.12M elem/s]
```

**Benefits**:
- Statistical analysis (mean, stddev, outliers)
- Regression detection (compares to baseline)
- Throughput reporting (elements/sec)

### 3. perf (Linux-only, Deep CPU Analysis)

**Installation**:
```bash
sudo apt-get install linux-tools-common linux-tools-generic
```

**Record Profile**:
```bash
# Build with debug symbols
cargo build --release --bin tier1_symbol_discovery

# Record CPU profile
perf record --call-graph=dwarf ./target/release/tier1_symbol_discovery --format comprehensive

# Analyze
perf report
```

**Key Metrics**:
- **Cycles**: Total CPU cycles
- **Instructions**: Total instructions executed
- **Cache misses**: L1/L2/L3 cache inefficiencies
- **Branch mispredictions**: Control flow inefficiencies

### 4. Instruments (macOS-only, Comprehensive Profiling)

**Launch**:
```bash
# Open Xcode Instruments
open -a Instruments

# Or from command line (replace with your binary and args)
xcrun xctrace record --template "Time Profiler" --launch target/release/YOUR_BINARY [ARGS]
```

**Templates**:
- **Time Profiler**: CPU usage over time
- **Allocations**: Memory allocation tracking
- **System Trace**: I/O, network, system calls

## Common Bottlenecks

### Bottleneck 1: Data Loading (I/O Bound)

**Symptoms**:
- Flamegraph dominated by `std::fs::read`, `csv::Reader`
- CPU usage <50% during processing
- Long wait times before processing starts

**Diagnosis**:
```bash
# Time data loading separately (example with hypothetical --load-only flag)
time cargo run --release --bin YOUR_BINARY -- [YOUR_ARGS]
```

**Solutions**:

**Option A: Parallel Data Loading** (Best for multi-symbol)
```rust
use rayon::prelude::*;

let data: Vec<_> = symbols.par_iter()
    .map(|symbol| {
        let loader = HistoricalDataLoader::new(symbol);
        loader.load_historical_range(days).await
    })
    .collect();
```

**Option B: Memory-Mapped Files** (Best for single large file)
```rust
use memmap2::Mmap;

let file = File::open("data.csv")?;
let mmap = unsafe { Mmap::map(&file)? };
let cursor = std::io::Cursor::new(&mmap[..]);

// Parse directly from memory-mapped region
let reader = csv::Reader::from_reader(cursor);
```

**Option C: Streaming** (Best for memory constraints)
```rust
// Don't load all data upfront
for chunk in data_loader.iter_chunks(chunk_size) {
    process_chunk(chunk)?;
}
```

### Bottleneck 2: Memory Allocations

**Symptoms**:
- Flamegraph shows time in `alloc`, `realloc`
- High memory usage
- Frequent garbage collection pauses

**Diagnosis**:
```bash
# macOS: Allocations instrument
xcrun xctrace record --template Allocations --launch target/release/YOUR_BINARY ...

# Linux: Valgrind massif
valgrind --tool=massif --massif-out-file=massif.out ./target/release/YOUR_BINARY ...
ms_print massif.out
```

**Solutions**:

**Pre-allocate Vectors**:
```rust
// ❌ Bad: Grows incrementally
let mut bars = Vec::new();
for trade in trades {
    bars.push(process(trade));
}

// ✅ Good: Pre-allocate capacity
let mut bars = Vec::with_capacity(trades.len() / 100);  // Estimate
for trade in trades {
    bars.push(process(trade));
}
```

**Use Streaming**:
```rust
// ❌ Bad: Loads everything in memory
let all_trades = loader.load_all().await?;
let bars = processor.process_agg_trade_records(&all_trades)?;

// ✅ Good: Constant memory
for trade in loader.iter_trades().await? {
    if let Some(bar) = processor.process_single_trade(trade)? {
        exporter.write_bar(&bar)?;
    }
}
```

### Bottleneck 3: Unnecessary Cloning

**Symptoms**:
- Flamegraph shows time in `clone`
- High memory bandwidth usage

**Diagnosis**:
```rust
// Add #[derive(Clone)] only where needed
// Use cargo-clippy to detect unnecessary clones
cargo clippy -- -W clippy::clone_on_copy -W clippy::redundant_clone
```

**Solutions**:
```rust
// ❌ Bad: Unnecessary clone
let bar_copy = bar.clone();
process(bar_copy);

// ✅ Good: Borrow
process(&bar);

// ❌ Bad: Clone in loop
for _ in 0..n {
    let data = expensive_data.clone();
    process(data);
}

// ✅ Good: Borrow in loop
for _ in 0..n {
    process(&expensive_data);
}
```

### Bottleneck 4: Fixed-Point Arithmetic

**Symptoms**:
- Flamegraph shows time in `FixedPoint::from_str`, arithmetic ops
- Should be <5% of total time

**Diagnosis**:
```rust
// Benchmark fixed-point operations
#[bench]
fn bench_fixed_point_ops(b: &mut Bencher) {
    let x = FixedPoint::from_str("50000.12345678").unwrap();
    let y = FixedPoint::from_str("1.0025").unwrap();

    b.iter(|| {
        black_box(x.compute_range_thresholds(250))
    });
}
```

**Expected**: 5-10ns per operation (no optimization needed)
**Slow**: >100ns per operation (investigate)

### Bottleneck 5: String Parsing

**Symptoms**:
- Flamegraph dominated by `from_str`, `parse`
- Slow CSV parsing

**Solutions**:

**Use serde deserialize directly** (fastest):
```rust
#[derive(Deserialize)]
struct AggTradeRecord {
    price: String,  // Parse to FixedPoint later
    volume: String,
    timestamp: i64,
    // ...
}

// Batch parse after deserialization
let trades: Vec<AggTrade> = records.into_iter()
    .map(|r| AggTrade {
        price: FixedPoint::from_str(&r.price).unwrap(),
        volume: FixedPoint::from_str(&r.volume).unwrap(),
        timestamp: r.timestamp,
        // ...
    })
    .collect();
```

**Cache parsed values**:
```rust
// ❌ Bad: Parse same value repeatedly
for _ in 0..n {
    let price = FixedPoint::from_str("50000.12345678").unwrap();
}

// ✅ Good: Parse once
let price = FixedPoint::from_str("50000.12345678").unwrap();
for _ in 0..n {
    use_price(price);
}
```

## Optimization Strategies

### Strategy 1: Parallel Processing (Rayon)

**When**: Multi-symbol processing, independent operations

```rust
use rayon::prelude::*;

// Process symbols in parallel
let results: Vec<_> = symbols.par_iter()
    .map(|symbol| {
        let mut processor = RangeBarProcessor::new(threshold_bps)?;
        let trades = load_symbol_data(symbol)?;
        processor.process_agg_trade_records(&trades)
    })
    .collect();
```

**Speedup**: Near-linear with CPU cores (8 cores → 7-8x faster)

### Strategy 2: SIMD (Manual Optimization)

**When**: Large datasets, tight loops (advanced)

**Note**: Current fixed-point implementation is already highly optimized (pure integer arithmetic). SIMD likely not needed unless profiling shows CPU bottleneck.

### Strategy 3: Reduce Allocations

**Reuse Buffers**:
```rust
struct ProcessorState {
    processor: RangeBarProcessor,
    bar_buffer: Vec<RangeBar>,
}

impl ProcessorState {
    fn process_reusing_buffer(&mut self, trades: &[AggTrade]) -> &[RangeBar] {
        self.bar_buffer.clear();  // Reuse capacity

        for trade in trades {
            if let Some(bar) = self.processor.process_single_trade(trade.clone()).unwrap() {
                self.bar_buffer.push(bar);
            }
        }

        &self.bar_buffer
    }
}
```

### Strategy 4: Profile-Guided Optimization (PGO)

**Enable PGO** (`Cargo.toml`):
```toml
[profile.release]
lto = "fat"           # Link-time optimization
codegen-units = 1     # Single codegen unit for better optimization
```

**Benchmark Impact**:
```bash
# Before
cargo bench --bench processor_bench

# After
cargo build --release
cargo bench --bench processor_bench

# Compare results
```

**Expected Improvement**: 5-15% faster

## Benchmarking

### Built-in Benchmark Suite

```bash
# Run all benchmarks
cargo bench

# Run specific benchmark
cargo bench --bench processor_bench

# Save baseline for comparison
cargo bench --bench processor_bench -- --save-baseline main

# Compare to baseline
git checkout feature-branch
cargo bench --bench processor_bench -- --baseline main
```

### Custom Benchmark Script

```bash
#!/bin/bash
# benchmark.sh - Compare performance across thresholds

SYMBOL="BTCUSDT"
DAYS=30

echo "Threshold,Trades,Bars,Time(ms),Throughput(trades/s)"

for THRESHOLD in 10 25 50 100 250 500 1000; do
    OUTPUT=$(cargo run --release --bin YOUR_BINARY -- \
        --benchmark \
        --symbol $SYMBOL \
        --days $DAYS \
        --threshold $THRESHOLD \
        --output /dev/null)

    echo "$THRESHOLD,$OUTPUT"
done
```

**Run**:
```bash
chmod +x benchmark.sh
./benchmark.sh > benchmark_results.csv

# Analyze in spreadsheet or:
python3 -c "import pandas as pd; df = pd.read_csv('benchmark_results.csv'); print(df)"
```

## Memory Profiling

### Heap Usage (Valgrind Massif, Linux)

```bash
# Build with debug symbols
cargo build --release

# Profile memory
valgrind --tool=massif \
    --massif-out-file=massif.out \
    ./target/release/YOUR_BINARY [YOUR_ARGS]

# Visualize
ms_print massif.out | less

# Or graphically
massif-visualizer massif.out
```

### Memory Growth (macOS Instruments)

```bash
# Record Allocations profile
xcrun xctrace record \
    --template Allocations \
    --output allocations.trace \
    --launch ./target/release/YOUR_BINARY [YOUR_ARGS]

# Open in Instruments
open allocations.trace
```

**Look For**:
- **Memory leaks**: Allocations never freed
- **Growth**: Linear growth suggests batching needed
- **Spikes**: Large temporary allocations (optimize or stream)

### Stack Usage (cargo-stack-sizes)

```bash
cargo install cargo-stack-sizes

# Analyze stack usage
cargo stack-sizes --release --bin YOUR_BINARY | head -20
```

**Watch For**:
- Functions using >100KB stack (risk of overflow)
- Large stack arrays (move to heap)

## Performance Checklist

Before deploying to production, verify:

- [ ] **Throughput**: >5M trades/sec on target hardware
- [ ] **Memory**: <2GB for typical workload (100M trades)
- [ ] **Latency**: <100ms for 1M trades
- [ ] **Streaming**: Constant O(1) memory for unbounded data
- [ ] **Parallel**: Scales linearly with CPU cores
- [ ] **Regression**: No performance degradation vs baseline
- [ ] **Profiled**: Flamegraph shows balanced CPU usage (no single hotspot >30%)

## Quick Reference

| Tool | Platform | Use Case | Output |
|------|----------|----------|--------|
| `cargo bench` | All | Microbenchmarks | Statistical analysis |
| `flamegraph` | Linux, macOS | CPU profiling | SVG flamegraph |
| `perf` | Linux | Deep CPU analysis | CLI report |
| `Instruments` | macOS | Comprehensive | GUI traces |
| `Valgrind massif` | Linux | Memory profiling | Heap snapshots |
| `cargo-stack-sizes` | All | Stack usage | Function sizes |

## Further Reading

- **Rust Performance Book**: https://nnethercote.github.io/perf-book/
- **Criterion Documentation**: https://bheisler.github.io/criterion.rs/book/
- **Flamegraph Tutorial**: https://www.brendangregg.com/flamegraphs.html
- **Common Workflows**: `/Users/terryli/eon/rangebar/docs/guides/common-workflows.md `
