# Output Directory

Generated range bars and analysis results. **Selectively committed to git.**

## Structure

```
output/
├── benchmarks/            # Performance validation (commit summaries only)
│   └── YYYY-MM-DD_name/
│       ├── summary.json   ← COMMIT THIS
│       └── *.parquet      ← DO NOT COMMIT
├── validation/            # Data structure validation (commit reports)
│   └── YYYY-MM-DD_name/
│       ├── report.md      ← COMMIT THIS
│       └── *.csv          ← DO NOT COMMIT
├── production/            # Final exports (DO NOT COMMIT - too large)
│   └── provider_symbol_threshold/
│       └── *.parquet
└── experiments/           # Ad-hoc analysis (git ignore, document separately)
    └── YYYY-MM-DD_name/
```

## Taxonomy

### `benchmarks/`
- **Purpose**: Performance validation, throughput testing
- **Git Policy**: Commit JSON summaries only (< 1MB)
- **Naming**: `YYYY-MM-DD_benchmark-name/`
- **Example**: `2025-10-02_dukascopy-105k-ticks/summary.json`

### `validation/`
- **Purpose**: Data structure validation, integrity checks
- **Git Policy**: Commit markdown reports only
- **Naming**: `YYYY-MM-DD_validation-type/`
- **Example**: `2025-10-02_binance-spot-tier1/report.md`

### `production/`
- **Purpose**: Final range bar exports for downstream ML models
- **Git Policy**: **NEVER** commit (multi-GB files)
- **Naming**: `[provider]_[market]_[SYMBOL]/[threshold]bps/`
- **Example**: `binance_spot_BTCUSDT/0025bps/2024-07-01_2024-07-31.parquet`

### `experiments/`
- **Purpose**: Ad-hoc analysis, parameter exploration
- **Git Policy**: Ignore all (document in lab notebook)
- **Naming**: `YYYY-MM-DD_experiment-name/`
- **Cleanup**: Delete after documenting results

## Naming Convention

**Format**: `[provider]_[market?]_[SYMBOL]_rangebar_[start]_[end]_[threshold].[ext]`

**Examples**:
- `binance_spot_BTCUSDT_rangebar_20240701_20241031_0025bps.parquet`
- `dukascopy_EURUSD_rangebar_20250115_20250115_0025bps.csv`
- `binance_um_ETHUSDT_rangebar_20240801_20240831_0050bps.json`

## File Formats

- **Parquet** (`.parquet`): Production use (best compression, fast queries)
- **CSV** (`.csv`): Human-readable, debugging
- **JSON** (`.json`): Metadata, summaries, validation reports

## Storage Management

### Current State
Many legacy subdirectories exist from previous runs. These will be **migrated** to the new structure:

- `bps_validation_*` → `validation/`
- `spot_tier1_batch` → `production/binance_spot/`
- `symbol_analysis` → `experiments/`

### Cleanup Policy
- Keep `benchmarks/` and `validation/` indefinitely (small, valuable)
- Archive `production/` to external storage monthly
- Delete `experiments/` after documenting results

## Git Policy Summary

```gitignore
# Commit these
!/output/benchmarks/**/*.json
!/output/validation/**/*.md

# Never commit these
/output/production/
/output/experiments/
```

See `.gitignore` for full rules.
