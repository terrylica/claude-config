# Error Recovery Guide for Long-Running Jobs

Practical strategies for resuming failed data processing jobs without restarting from scratch.

## Table of Contents

- [Overview](#overview)
- [Common Failure Modes](#common-failure-modes)
- [Recovery Strategies](#recovery-strategies)
- [Checkpointing Patterns](#checkpointing-patterns)
- [Data Validation](#data-validation)
- [Best Practices](#best-practices)

## Overview

Long-running jobs (multi-symbol analysis, historical backtests, large datasets) can fail for various reasons. This guide provides **practical recovery patterns** to resume work efficiently.

**Key Principle**: Design jobs to be **idempotent** and **resumable** - running the same operation multiple times produces the same result.

## Common Failure Modes

### 1. Network Timeouts (Binance/Exness API)

**Symptoms**:
```
Error: reqwest::Error: operation timed out
Failed to fetch BTCUSDT 2024-01-15
```

**Impact**: Partial data loss for specific symbols/dates

**Recovery**: Resume from failed symbol/date (see [Checkpointing Patterns](#checkpointing-patterns))

### 2. Disk Space Exhaustion

**Symptoms**:
```
Error: No space left on device (os error 28)
Failed to write output/ETHUSDT_25bps.parquet
```

**Impact**: Completed bars in memory are lost, partial file may be corrupted

**Recovery**:
1. Free disk space (`df -h` to check)
2. Remove corrupted partial files
3. Resume from last complete checkpoint
4. Consider streaming export instead of batch

### 3. Out of Memory (OOM)

**Symptoms**:
```
signal: 9, SIGKILL
Killed: 9
```

**Impact**: All in-memory state lost, no partial results saved

**Recovery**:
1. Reduce batch size (process fewer symbols/dates per run)
2. Use streaming mode instead of batch mode
3. Resume with smaller chunks

### 4. Invalid Data / Parse Errors

**Symptoms**:
```
Error: CSV parse error at line 45123
Error: FixedPoint parse error: invalid decimal "1.234e-5"
Error: Timestamp parse error
```

**Impact**: Single symbol/date may fail, others may succeed

**Recovery**:
1. Identify failed symbol/date from error message
2. Skip corrupted data (log for manual review)
3. Resume processing remaining symbols
4. Investigate root cause separately

### 5. Algorithm Invariant Violations

**Symptoms**:
```
Assertion failed: high >= open
Breach consistency invariant violated
```

**Impact**: Bug in algorithm or data corruption, partial results may be invalid

**Recovery**:
1. Save input data that triggered violation
2. File bug report with reproducible test case
3. DO NOT resume - results may be invalid
4. Wait for fix or use different threshold

## Recovery Strategies

### Strategy 1: File-Based Checkpointing (Recommended)

**When to Use**: Multi-symbol processing, large date ranges

**Pattern**:
```rust
use std::path::Path;
use std::collections::HashSet;

fn process_symbols_with_checkpointing(
    symbols: Vec<String>,
    output_dir: &Path,
) -> Result<(), Error> {
    // Scan output directory for completed symbols
    let completed: HashSet<String> = std::fs::read_dir(output_dir)?
        .filter_map(|entry| entry.ok())
        .filter_map(|entry| {
            let name = entry.file_name();
            let name_str = name.to_string_lossy();
            if name_str.ends_with("_25bps.parquet") {
                // Extract symbol from filename (e.g., "BTCUSDT_25bps.parquet" → "BTCUSDT")
                Some(name_str.trim_end_matches("_25bps.parquet").to_string())
            } else {
                None
            }
        })
        .collect();

    println!("Found {} completed symbols, {} remaining",
        completed.len(),
        symbols.len() - completed.len()
    );

    for symbol in symbols {
        // Skip already-processed symbols
        if completed.contains(&symbol) {
            println!("✓ Skipping {} (already complete)", symbol);
            continue;
        }

        println!("Processing {}...", symbol);

        // Process symbol (may fail - that's OK)
        match process_single_symbol(&symbol, output_dir) {
            Ok(_) => println!("✓ Completed {}", symbol),
            Err(e) => {
                eprintln!("✗ Failed {}: {}", symbol, e);
                // Continue to next symbol instead of aborting
                continue;
            }
        }
    }

    Ok(())
}
```

**Benefits**:
- Zero memory overhead (filesystem is the state)
- Automatically resumes from failures
- Works across process restarts
- Easy to inspect progress (`ls output/`)

### Strategy 2: Progress Log File

**When to Use**: Need detailed audit trail, debugging failures

**Pattern**:
```rust
use std::fs::OpenOptions;
use std::io::Write;

struct ProgressLogger {
    log_file: std::fs::File,
}

impl ProgressLogger {
    fn new(path: &Path) -> Result<Self, Error> {
        let log_file = OpenOptions::new()
            .create(true)
            .append(true)  // Append mode - survives crashes
            .open(path)?;
        Ok(Self { log_file })
    }

    fn log_start(&mut self, symbol: &str, date: &str) {
        writeln!(
            self.log_file,
            "{} START {} {}",
            chrono::Utc::now().to_rfc3339(),
            symbol,
            date
        ).ok();
    }

    fn log_complete(&mut self, symbol: &str, date: &str, bar_count: usize) {
        writeln!(
            self.log_file,
            "{} COMPLETE {} {} bars={}",
            chrono::Utc::now().to_rfc3339(),
            symbol,
            date,
            bar_count
        ).ok();
    }

    fn log_error(&mut self, symbol: &str, date: &str, error: &str) {
        writeln!(
            self.log_file,
            "{} ERROR {} {} error={}",
            chrono::Utc::now().to_rfc3339(),
            symbol,
            date,
            error
        ).ok();
    }
}

// Usage:
let mut logger = ProgressLogger::new(Path::new("progress.log"))?;

for symbol in symbols {
    logger.log_start(&symbol, &date);

    match process_symbol(&symbol, &date) {
        Ok(bars) => logger.log_complete(&symbol, &date, bars.len()),
        Err(e) => {
            logger.log_error(&symbol, &date, &e.to_string());
            continue;  // Resume next symbol
        }
    }
}
```

**Analyzing Progress**:
```bash
# Check completion rate
grep "COMPLETE" progress.log | wc -l

# Find failed symbols
grep "ERROR" progress.log

# Find symbols that started but didn't complete (crashed)
comm -23 <(grep "START" progress.log | awk '{print $3}' | sort) \
         <(grep "COMPLETE\|ERROR" progress.log | awk '{print $3}' | sort)
```

### Strategy 3: Atomic File Writes

**When to Use**: Prevent partial/corrupted files

**Pattern**:
```rust
use std::fs;
use std::path::Path;

fn write_bars_atomically(bars: &[RangeBar], output_path: &Path) -> Result<(), Error> {
    // Write to temporary file first
    let temp_path = output_path.with_extension("tmp");

    // Export to temp file
    let exporter = PolarsExporter::new();
    exporter.export_to_parquet(bars, &temp_path)?;

    // Atomically rename (only if write succeeded)
    fs::rename(&temp_path, output_path)?;

    Ok(())
}
```

**Benefits**:
- File either exists completely or doesn't exist
- Never leaves partial/corrupted files
- Safe to retry on same filename

### Strategy 4: Batch Size Tuning

**When to Use**: Memory constraints, progress visibility

**Pattern**:
```rust
const BATCH_SIZE: usize = 10;  // Process 10 symbols at a time

for batch in symbols.chunks(BATCH_SIZE) {
    println!("Processing batch {}/{}", batch_idx + 1, num_batches);

    for symbol in batch {
        process_symbol(symbol)?;
    }

    // Checkpoint after each batch
    println!("✓ Batch complete - progress saved");
}
```

**Tuning Guidelines**:
- **Memory-constrained**: 5-10 symbols per batch
- **I/O-bound**: 50-100 symbols per batch
- **Network-bound**: Reduce batch size on timeouts

## Checkpointing Patterns

### Pattern 1: Date-Based Checkpointing

**Use Case**: Processing multi-year historical data

```rust
use chrono::{NaiveDate, Duration};

fn process_date_range_with_checkpoints(
    symbol: &str,
    start: NaiveDate,
    end: NaiveDate,
    output_dir: &Path,
) -> Result<(), Error> {
    let mut current = start;

    while current <= end {
        let output_file = output_dir.join(format!(
            "{}_{}.parquet",
            symbol,
            current.format("%Y-%m-%d")
        ));

        // Skip already-processed dates
        if output_file.exists() {
            println!("✓ Skipping {} (exists)", current);
            current = current + Duration::days(1);
            continue;
        }

        // Fetch and process single day
        match fetch_and_process_day(symbol, current) {
            Ok(bars) => {
                write_bars_atomically(&bars, &output_file)?;
                println!("✓ Completed {}", current);
            }
            Err(e) => {
                eprintln!("✗ Failed {}: {}", current, e);
                // Continue to next day instead of aborting
            }
        }

        current = current + Duration::days(1);
    }

    Ok(())
}
```

### Pattern 2: Symbol Manifest File

**Use Case**: Track completion across multiple runs

```rust
use std::collections::HashSet;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct Manifest {
    completed_symbols: HashSet<String>,
    failed_symbols: Vec<(String, String)>,  // (symbol, error)
}

impl Manifest {
    fn load_or_create(path: &Path) -> Result<Self, Error> {
        if path.exists() {
            let json = std::fs::read_to_string(path)?;
            Ok(serde_json::from_str(&json)?)
        } else {
            Ok(Self {
                completed_symbols: HashSet::new(),
                failed_symbols: Vec::new(),
            })
        }
    }

    fn save(&self, path: &Path) -> Result<(), Error> {
        let json = serde_json::to_string_pretty(self)?;
        let temp = path.with_extension("tmp");
        std::fs::write(&temp, json)?;
        std::fs::rename(&temp, path)?;  // Atomic
        Ok(())
    }

    fn mark_complete(&mut self, symbol: String) {
        self.completed_symbols.insert(symbol);
    }

    fn mark_failed(&mut self, symbol: String, error: String) {
        self.failed_symbols.push((symbol, error));
    }
}

// Usage:
let manifest_path = Path::new("manifest.json");
let mut manifest = Manifest::load_or_create(&manifest_path)?;

for symbol in symbols {
    if manifest.completed_symbols.contains(&symbol) {
        println!("✓ Skipping {} (completed)", symbol);
        continue;
    }

    match process_symbol(&symbol) {
        Ok(_) => {
            manifest.mark_complete(symbol.clone());
            manifest.save(&manifest_path)?;  // Save after each success
        }
        Err(e) => {
            manifest.mark_failed(symbol.clone(), e.to_string());
            manifest.save(&manifest_path)?;
        }
    }
}
```

## Data Validation

### Validate Partial Results Before Resuming

**Critical**: Verify completed data is valid before resuming processing

```rust
use rangebar_io::PolarsExporter;

fn validate_existing_output(path: &Path) -> Result<bool, Error> {
    if !path.exists() {
        return Ok(false);  // Doesn't exist - needs processing
    }

    // Attempt to read existing file
    let df = match polars::prelude::ParquetReader::new(std::fs::File::open(path)?)
        .finish()
    {
        Ok(df) => df,
        Err(e) => {
            eprintln!("✗ Corrupted file {}: {}", path.display(), e);
            // Delete corrupted file
            std::fs::remove_file(path)?;
            return Ok(false);  // Needs reprocessing
        }
    };

    // Validate schema
    let required_columns = ["open", "high", "low", "close", "volume", "open_time", "close_time"];
    for col in required_columns {
        if !df.get_column_names().contains(&col) {
            eprintln!("✗ Missing column {} in {}", col, path.display());
            std::fs::remove_file(path)?;
            return Ok(false);
        }
    }

    // Validate row count (catch truncated files)
    if df.height() == 0 {
        eprintln!("✗ Empty file {}", path.display());
        std::fs::remove_file(path)?;
        return Ok(false);
    }

    // File is valid
    Ok(true)
}

// Usage:
for symbol in symbols {
    let output_path = output_dir.join(format!("{}_25bps.parquet", symbol));

    if validate_existing_output(&output_path)? {
        println!("✓ Skipping {} (valid output exists)", symbol);
        continue;
    }

    // Process symbol
    process_symbol(&symbol, &output_path)?;
}
```

## Best Practices

### 1. Fail Fast on Unrecoverable Errors

```rust
// ✅ Good: Propagate fatal errors immediately
if threshold_bps < 1 {
    return Err(ProcessingError::InvalidThreshold { threshold_bps });
}

// ✅ Good: Continue on recoverable errors (network timeout)
for symbol in symbols {
    match fetch_data(&symbol) {
        Ok(data) => process(data)?,
        Err(NetworkError::Timeout) => {
            eprintln!("Timeout fetching {}, skipping", symbol);
            continue;  // Try next symbol
        }
        Err(e) => return Err(e.into()),  // Fatal error
    }
}
```

### 2. Log Errors to File (Not Just stderr)

```rust
use std::fs::OpenOptions;

fn log_error(symbol: &str, error: &Error) {
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open("errors.log")
        .unwrap();

    writeln!(
        file,
        "{} {} {}",
        chrono::Utc::now().to_rfc3339(),
        symbol,
        error
    ).ok();
}
```

**Benefits**: Errors survive terminal closure, easier post-mortem analysis

### 3. Use Descriptive Output Filenames

```rust
// ✅ Good: Includes all parameters
format!("{}_{}bps_{}_to_{}.parquet", symbol, threshold_bps / 10, start_date, end_date)

// ❌ Bad: Ambiguous
format!("{}_output.parquet", symbol)
```

### 4. Test Recovery Logic

```rust
#[test]
fn test_resume_from_partial_completion() {
    let temp_dir = tempdir().unwrap();

    // Simulate partial completion (3 out of 5 symbols)
    let symbols = vec!["BTC", "ETH", "SOL", "ADA", "AVAX"];
    for symbol in &symbols[0..3] {
        let path = temp_dir.path().join(format!("{}_25bps.parquet", symbol));
        std::fs::write(&path, b"fake data").unwrap();
    }

    // Run processor
    let completed = find_completed_symbols(temp_dir.path()).unwrap();

    // Verify only remaining symbols processed
    assert_eq!(completed.len(), 3);
    assert!(completed.contains("BTC"));
    assert!(completed.contains("ETH"));
    assert!(completed.contains("SOL"));
}
```

### 5. Monitor Disk Space Proactively

```rust
use nix::sys::statvfs::statvfs;

fn check_disk_space(path: &Path, required_gb: u64) -> Result<(), Error> {
    let stat = statvfs(path)?;
    let available_gb = (stat.blocks_available() * stat.block_size()) / 1_000_000_000;

    if available_gb < required_gb {
        return Err(Error::InsufficientDiskSpace {
            available_gb,
            required_gb,
        });
    }

    Ok(())
}

// Usage: Check before processing
check_disk_space(output_dir, 100)?;  // Require 100GB free
```

### 6. Streaming Export for Memory Safety

**When to Use**: Processing datasets larger than RAM

```rust
use rangebar_io::StreamingCsvExporter;

fn process_large_dataset_streaming(
    trades: impl Iterator<Item = AggTrade>,
    output_path: &Path,
) -> Result<(), Error> {
    let mut processor = RangeBarProcessor::new(250)?;
    let mut exporter = StreamingCsvExporter::new(output_path.to_path_buf())?;

    for trade in trades {
        // Process one trade at a time
        if let Some(bar) = processor.process_single_trade(trade)? {
            // Write immediately (no buffering)
            exporter.write_bar(&bar)?;
        }
    }

    Ok(())
}
```

**Benefits**:
- Constant memory usage (O(1) bars in memory)
- Partial results saved if crash occurs
- Works with unlimited data sizes

## Real-World Example: Tier-1 Multi-Symbol Analysis

```rust
use rangebar_providers::binance::get_tier1_usdt_pairs;

fn process_tier1_with_recovery(
    threshold_bps: u32,
    output_dir: &Path,
) -> Result<(), Error> {
    let symbols = get_tier1_usdt_pairs();  // 18 symbols
    let manifest_path = output_dir.join("manifest.json");
    let mut manifest = Manifest::load_or_create(&manifest_path)?;

    println!("Processing {} Tier-1 symbols", symbols.len());
    println!("Already completed: {}", manifest.completed_symbols.len());

    for (i, symbol) in symbols.iter().enumerate() {
        println!("\n[{}/{}] {}", i + 1, symbols.len(), symbol);

        // Skip completed
        if manifest.completed_symbols.contains(symbol) {
            println!("✓ Skipped (already complete)");
            continue;
        }

        let output_file = output_dir.join(format!("{}_{}bps.parquet", symbol, threshold_bps / 10));

        // Validate existing partial output
        if output_file.exists() && !validate_existing_output(&output_file)? {
            println!("! Removing corrupted output");
            std::fs::remove_file(&output_file)?;
        }

        // Process symbol with retries
        let result = retry_with_backoff(3, || {
            fetch_and_process_symbol(symbol, threshold_bps, &output_file)
        });

        match result {
            Ok(_) => {
                manifest.mark_complete(symbol.clone());
                manifest.save(&manifest_path)?;
                println!("✓ Complete");
            }
            Err(e) => {
                manifest.mark_failed(symbol.clone(), e.to_string());
                manifest.save(&manifest_path)?;
                eprintln!("✗ Failed: {}", e);
                // Continue to next symbol
            }
        }
    }

    // Summary
    println!("\n=== Summary ===");
    println!("Completed: {}", manifest.completed_symbols.len());
    println!("Failed: {}", manifest.failed_symbols.len());

    if !manifest.failed_symbols.is_empty() {
        println!("\nFailed symbols:");
        for (symbol, error) in &manifest.failed_symbols {
            println!("  {} - {}", symbol, error);
        }
    }

    Ok(())
}

fn retry_with_backoff<F, T>(max_attempts: usize, mut f: F) -> Result<T, Error>
where
    F: FnMut() -> Result<T, Error>,
{
    let mut attempts = 0;
    loop {
        attempts += 1;
        match f() {
            Ok(result) => return Ok(result),
            Err(e) if attempts >= max_attempts => return Err(e),
            Err(e) => {
                eprintln!("Attempt {}/{} failed: {}", attempts, max_attempts, e);
                std::thread::sleep(std::time::Duration::from_secs(2u64.pow(attempts as u32)));
            }
        }
    }
}
```

## Quick Reference

| Failure Mode | Recovery Strategy | Tools |
|--------------|-------------------|-------|
| Network timeout | Skip failed symbol, retry with backoff | `retry_with_backoff()` |
| Disk full | Free space, resume from checkpoints | `df -h`, file-based checkpointing |
| OOM | Reduce batch size, use streaming | `StreamingCsvExporter` |
| Invalid data | Log error, skip symbol | Progress log, `log_error()` |
| Partial corruption | Validate on resume, delete if invalid | `validate_existing_output()` |
| Process crash | File-based checkpoints auto-resume | Manifest pattern, atomic writes |

## Further Reading

- **Streaming Processing**: `/Users/terryli/eon/rangebar/crates/rangebar-streaming/README.md `
- **Parallel Analysis**: `/Users/terryli/eon/rangebar/crates/rangebar-batch/README.md `
- **Data Providers**: `/Users/terryli/eon/rangebar/crates/rangebar-providers/README.md `
- **Example Scripts**: `/Users/terryli/eon/rangebar/examples/ ` (needs v5.0.0 migration)
