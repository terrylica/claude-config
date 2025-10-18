# Rust Migration Guide: v4.0.0 → v5.0.0

**Audience**: Rust library users upgrading from v4.0.0 monolithic structure to v5.0.0 modular workspace

**Migration Path**: Automatic (backward compatibility) or Manual (recommended for new code)

**Breaking Changes**: None (full backward compatibility maintained via meta-crate)

---

## Overview

Version 5.0.0 introduces a modular workspace architecture while maintaining 100% backward compatibility with v4.0.0. You have two migration options:

1. **Automatic (Zero Changes)**: Use the `rangebar` meta-crate with legacy imports
2. **Manual (Recommended)**: Migrate to direct crate imports for better modularity

---

## Quick Start: Zero-Change Migration

If you're currently using:

```toml
[dependencies]
rangebar = "4.0.0"
```

Simply update the version:

```toml
[dependencies]
rangebar = { version = "5.0.0", features = ["full"] }
```

**All your v4.0.0 code continues to work without any changes.**

---

## Architecture Changes

### v4.0.0 (Monolithic)

```
rangebar/
├── src/
│   ├── core/
│   ├── providers/
│   ├── infrastructure/
│   ├── engines/
│   └── bin/
└── Cargo.toml (single package)
```

### v5.0.0 (Modular Workspace)

```
rangebar/
├── crates/
│   ├── rangebar-core/        # Core algorithm (4 deps)
│   ├── rangebar-providers/    # Data providers
│   ├── rangebar-config/       # Configuration
│   ├── rangebar-io/           # I/O + Polars
│   ├── rangebar-streaming/    # Real-time streaming
│   ├── rangebar-batch/        # Batch analytics
│   ├── rangebar-cli/          # CLI tools
│   └── rangebar/              # Meta-crate (backward compat)
└── Cargo.toml (workspace root)
```

---

## Migration Paths

### Path 1: Automatic (No Changes Required)

Use the `rangebar` meta-crate with legacy module paths:

```rust
// v4.0.0 code - still works in v5.0.0!
use rangebar::fixed_point::FixedPoint;
use rangebar::range_bars::ExportRangeBarProcessor;
use rangebar::types::{AggTrade, RangeBar};
use rangebar::tier1::{get_tier1_symbols, get_tier1_usdt_pairs};
use rangebar::data::HistoricalDataLoader;
```

**Cargo.toml**:
```toml
[dependencies]
rangebar = { version = "5.0.0", features = ["full"] }
```

**Pros**:
- Zero code changes
- Instant upgrade
- All features enabled

**Cons**:
- Larger binary size (includes all crates)
- Slower compilation (compiles everything)
- Less modular dependency tree

---

### Path 2: Manual (Recommended for New Code)

Migrate to direct crate imports for better modularity:

#### Step 1: Update Dependencies

**Before (v4.0.0)**:
```toml
[dependencies]
rangebar = "4.0.0"
```

**After (v5.0.0)** - Choose what you need:
```toml
[dependencies]
# Minimal: Core algorithm only
rangebar-core = "5.0.0"

# + Data providers
rangebar-providers = { version = "5.0.0", features = ["binance"] }

# + Export formats (Polars integration)
rangebar-io = { version = "5.0.0", features = ["polars-io"] }

# + Streaming processor
rangebar-streaming = "5.0.0"

# + Batch analytics
rangebar-batch = "5.0.0"
```

#### Step 2: Update Imports

**Core Types** (fixed_point, types):

```rust
// Before (v4.0.0)
use rangebar::fixed_point::FixedPoint;
use rangebar::types::{AggTrade, RangeBar, DataSource};
use rangebar::core::processor::RangeBarProcessor;

// After (v5.0.0)
use rangebar_core::{FixedPoint, AggTrade, RangeBar, DataSource};
use rangebar_core::RangeBarProcessor;
```

**Data Providers**:

```rust
// Before (v4.0.0)
use rangebar::data::HistoricalDataLoader;
use rangebar::tier1::{get_tier1_symbols, get_tier1_usdt_pairs};
use rangebar::providers::exness::{ExnessFetcher, ExnessRangeBarBuilder};

// After (v5.0.0)
use rangebar_providers::binance::{
    HistoricalDataLoader,
    get_tier1_symbols,
    get_tier1_usdt_pairs,
};
use rangebar_providers::exness::{ExnessFetcher, ExnessRangeBarBuilder};
```

**I/O & Export**:

```rust
// Before (v4.0.0)
use rangebar::infrastructure::io::{PolarsExporter, ParquetExporter};

// After (v5.0.0)
use rangebar_io::{PolarsExporter, ParquetExporter, ArrowExporter};
```

**Streaming & Batch**:

```rust
// Before (v4.0.0)
use rangebar::engines::streaming::StreamingProcessor;
use rangebar::engines::batch::BatchAnalysisEngine;

// After (v5.0.0)
use rangebar_streaming::StreamingProcessor;
use rangebar_batch::BatchAnalysisEngine;
```

**Configuration**:

```rust
// Before (v4.0.0)
use rangebar::infrastructure::config::Settings;

// After (v5.0.0)
use rangebar_config::Settings;
```

---

## Migration Examples

### Example 1: Basic Range Bar Processing

**Before (v4.0.0)**:
```rust
use rangebar::fixed_point::FixedPoint;
use rangebar::core::processor::RangeBarProcessor;
use rangebar::types::AggTrade;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut processor = RangeBarProcessor::new(250)?; // 25 BPS
    let bars = processor.process_agg_trade_records(&trades)?;
    Ok(())
}
```

**After (v5.0.0 - Automatic)**:
```rust
// No changes needed! Use meta-crate with legacy paths
use rangebar::fixed_point::FixedPoint;
use rangebar::core::processor::RangeBarProcessor;
use rangebar::types::AggTrade;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut processor = RangeBarProcessor::new(250)?;
    let bars = processor.process_agg_trade_records(&trades)?;
    Ok(())
}
```

**After (v5.0.0 - Manual)**:
```rust
// Direct crate imports (recommended)
use rangebar_core::{FixedPoint, RangeBarProcessor, AggTrade};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut processor = RangeBarProcessor::new(250)?;
    let bars = processor.process_agg_trade_records(&trades)?;
    Ok(())
}
```

**Cargo.toml**:
```toml
# Minimal dependency for basic processing
[dependencies]
rangebar-core = "5.0.0"
```

---

### Example 2: Historical Data Loading

**Before (v4.0.0)**:
```rust
use rangebar::data::HistoricalDataLoader;
use rangebar::tier1::get_tier1_symbols;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let symbols = get_tier1_symbols();
    let loader = HistoricalDataLoader::new("BTCUSDT");
    let trades = loader.load_recent_day().await?;
    Ok(())
}
```

**After (v5.0.0 - Manual)**:
```rust
use rangebar_providers::binance::{HistoricalDataLoader, get_tier1_symbols};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let symbols = get_tier1_symbols();
    let loader = HistoricalDataLoader::new("BTCUSDT");
    let trades = loader.load_recent_day().await?;
    Ok(())
}
```

**Cargo.toml**:
```toml
[dependencies]
rangebar-core = "5.0.0"
rangebar-providers = { version = "5.0.0", features = ["binance"] }
tokio = { version = "1.0", features = ["full"] }
```

---

### Example 3: Export to Parquet

**Before (v4.0.0)**:
```rust
use rangebar::infrastructure::io::ParquetExporter;

fn export_bars(bars: &[RangeBar]) -> Result<(), Box<dyn std::error::Error>> {
    let exporter = ParquetExporter::new();
    exporter.export(bars, "output.parquet")?;
    Ok(())
}
```

**After (v5.0.0 - Manual)**:
```rust
use rangebar_io::ParquetExporter;
use rangebar_core::RangeBar;

fn export_bars(bars: &[RangeBar]) -> Result<(), Box<dyn std::error::Error>> {
    let exporter = ParquetExporter::new();
    exporter.export(bars, "output.parquet")?;
    Ok(())
}
```

**Cargo.toml**:
```toml
[dependencies]
rangebar-core = "5.0.0"
rangebar-io = { version = "5.0.0", features = ["polars-io"] }
```

---

### Example 4: Complete Pipeline

**Before (v4.0.0)**:
```rust
use rangebar::data::HistoricalDataLoader;
use rangebar::core::processor::RangeBarProcessor;
use rangebar::infrastructure::io::PolarsExporter;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load data
    let loader = HistoricalDataLoader::new("BTCUSDT");
    let trades = loader.load_historical_range(7).await?;

    // Process
    let mut processor = RangeBarProcessor::new(250)?;
    let bars = processor.process_agg_trade_records(&trades)?;

    // Export
    let exporter = PolarsExporter::new();
    exporter.export_parquet(&bars, "output.parquet")?;

    Ok(())
}
```

**After (v5.0.0 - Manual)**:
```rust
use rangebar_providers::binance::HistoricalDataLoader;
use rangebar_core::RangeBarProcessor;
use rangebar_io::PolarsExporter;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load data
    let loader = HistoricalDataLoader::new("BTCUSDT");
    let trades = loader.load_historical_range(7).await?;

    // Process
    let mut processor = RangeBarProcessor::new(250)?;
    let bars = processor.process_agg_trade_records(&trades)?;

    // Export
    let exporter = PolarsExporter::new();
    exporter.export_parquet(&bars, "output.parquet")?;

    Ok(())
}
```

**Cargo.toml**:
```toml
[dependencies]
rangebar-core = "5.0.0"
rangebar-providers = { version = "5.0.0", features = ["binance"] }
rangebar-io = { version = "5.0.0", features = ["polars-io"] }
tokio = { version = "1.0", features = ["full"] }
```

---

## Feature Flags

v5.0.0 introduces granular feature flags for selective compilation:

### rangebar-providers

```toml
# Default: binance only
rangebar-providers = "5.0.0"

# Enable specific providers
rangebar-providers = { version = "5.0.0", features = ["exness"] }
rangebar-providers = { version = "5.0.0", features = ["dukascopy"] }

# Enable all providers
rangebar-providers = { version = "5.0.0", features = ["all-providers"] }
```

### rangebar-io

```toml
# Default: basic I/O only
rangebar-io = "5.0.0"

# Enable Polars integration
rangebar-io = { version = "5.0.0", features = ["polars-io"] }
```

### rangebar (meta-crate)

```toml
# Minimal: core only
rangebar = "5.0.0"

# Core + providers
rangebar = { version = "5.0.0", features = ["providers"] }

# Core + providers + streaming
rangebar = { version = "5.0.0", features = ["streaming"] }

# Everything
rangebar = { version = "5.0.0", features = ["full"] }
```

---

## CLI Tools

All CLI binaries have been consolidated into the `rangebar-cli` crate but remain accessible via the same commands:

```bash
# Build CLI tools
cargo install --path crates/rangebar-cli --features full

# Or build specific binaries
cargo build --release --bin tier1-symbol-discovery
cargo build --release --bin rangebar-export
cargo build --release --bin data-structure-validator
```

**No changes to command-line usage** - all binaries work identically to v4.0.0.

---

## Testing Your Migration

### Validation Checklist

- [ ] Code compiles without errors: `cargo build --release`
- [ ] All tests pass: `cargo test`
- [ ] No clippy warnings: `cargo clippy -- -D warnings`
- [ ] Binary size is acceptable (check with `ls -lh target/release/your-binary`)
- [ ] Functionality unchanged (run integration tests)

### Quick Test

```rust
use rangebar_core::{RangeBarProcessor, FixedPoint};

#[test]
fn test_migration_compatibility() {
    let mut processor = RangeBarProcessor::new(250).unwrap();
    // Your test code here
}
```

---

## Troubleshooting

### Issue: Import not found

**Error**:
```
error[E0432]: unresolved import `rangebar::core`
```

**Solution**: Update imports to direct crate paths or enable `full` feature:
```toml
rangebar = { version = "5.0.0", features = ["full"] }
```

### Issue: Missing feature

**Error**:
```
error: feature `polars-io` not found in package `rangebar-core`
```

**Solution**: Features are now on specific crates:
```toml
# Wrong
rangebar-core = { version = "5.0.0", features = ["polars-io"] }

# Correct
rangebar-io = { version = "5.0.0", features = ["polars-io"] }
```

### Issue: Circular dependency

**Error**:
```
error: cyclic package dependency
```

**Solution**: Use correct dependency hierarchy:
- `rangebar-core` (no dependencies)
- `rangebar-providers` → `rangebar-core`
- `rangebar-io` → `rangebar-core`
- `rangebar-streaming` → `rangebar-core` + `rangebar-providers`
- `rangebar-batch` → `rangebar-core` + `rangebar-io`

---

## Benefits of v5.0.0 Migration

### Compile Time

- **Selective compilation**: Only compile what you need
- **Parallel builds**: Workspace members build in parallel
- **Smaller binaries**: Exclude unused crates

### Modularity

- **Clear dependencies**: Explicit crate boundaries
- **Better testing**: Test crates in isolation
- **Easier maintenance**: Changes localized to specific crates

### Discoverability

- **Crate-level README**: Each crate has comprehensive documentation
- **Feature flags**: Enable only needed functionality
- **API clarity**: Public APIs explicitly exported

---

## Recommended Migration Strategy

1. **Start with automatic migration** (meta-crate with `full` features)
2. **Verify all tests pass**
3. **Gradually migrate to direct imports** (one module at a time)
4. **Remove unused features** to reduce binary size
5. **Update documentation** to reflect new imports

---

## Version History

| Version | Release Date | Key Changes |
|---------|-------------|-------------|
| v4.0.0 | 2025-10-01 | Monolithic structure |
| v5.0.0 | 2025-10-11 | Modular workspace with backward compatibility |

---

## Support

- **Documentation**: See individual crate README files in `crates/*/README.md `
- **Architecture**: See `/Users/terryli/eon/rangebar/docs/ARCHITECTURE.md `
- **Issues**: Report at https://github.com/Eon-Labs/rangebar/issues
- **Examples**: See `/Users/terryli/eon/rangebar/examples/ `

---

## Summary

**v5.0.0 maintains 100% backward compatibility** while introducing a cleaner modular architecture. Choose your migration path based on your needs:

- **Need instant upgrade?** Use the meta-crate with `features = ["full"]`
- **Want better modularity?** Migrate to direct crate imports
- **Building new projects?** Use direct imports from the start

Both paths are fully supported and will receive updates.
