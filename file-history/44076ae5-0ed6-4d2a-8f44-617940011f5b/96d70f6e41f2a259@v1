# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Non-lookahead bias range bar construction from Binance UM Futures aggTrades data.

**Core Algorithm**: Range bars close when price moves ±threshold basis points from the bar's OPEN price (not from high/low range).

**Architecture**: Pure Rust implementation for performance and reliability (processes 1B+ ticks). All components native Rust: symbol discovery, data processing, and analysis.

## Key Commands

**Dev**: `cargo build --release`, `cargo test`, `cargo clippy`, `./scripts/update-deps.sh`

**Deploy**: `doppler run -- shuttle deploy`

**Data Ops**: `tier1-symbol-discovery --format comprehensive`, `rangebar-analyze`, `rangebar-export [SYMBOL] [dates] [threshold] [output] [um]`, `data-structure-validator --features data-integrity`

## Data Structure Validation

**Tool**: `data-structure-validator` validates Binance aggTrades across spot/futures markets

**Key Differences**:
- **Spot**: No headers, short columns (`a,p,q,f,l,T,m`), 16-digit μs timestamps
- **UM Futures**: Headers, descriptive columns, 13-digit ms timestamps
- **Parser**: Auto-detects format, normalizes timestamps to microseconds
- **Critical**: Use `aggTrades` nomenclature (not `trades`) - affects all naming


## Architecture

### Data Pipeline
1. **Symbol Discovery**: `tier1-symbol-discovery` → Multi-market symbol analysis
2. **Data Structure Validation**: `data-structure-validator` → Cross-market format verification
3. **Data Fetching**: `binance_historical_data` → Raw CSV/ZIP files with validated schemas
4. **Preprocessing**: CSV → Parquet with schema validation
5. **Computation**: Pure Rust processes Parquet → Range bars
6. **Analysis**: `rangebar-analyze` → Parallel Tier-1 analysis
7. **Output**: Structured bar data (OHLCV format)

**Performance**: Pure Rust, Rayon parallelism, fixed-point arithmetic

## Critical Algorithm Invariants

**Algorithm**: Fixed thresholds from bar OPEN (`±threshold_bps`), breach tick closes bar
**Validation**: `(high_breach → close_breach) AND (low_breach → close_breach)`

### Data Source Requirements
- **Source**: https://github.com/stas-prokopiev/binance_historical_data
- **Primary Asset Class**: `"spot"` (Default) for standard spot trading pairs
- **Optional Markets**: `"um"` (USD-M Futures) for USDT/USDC perpetuals, `"cm"` (Coin-M Futures)
- **Data Type**: `"aggTrades"` **ONLY**
- **Usage**: Specify market type via command line arguments or use spot by default

### Tier-1 Instruments Definition
**Tier-1 instruments** are crypto assets that Binance respects highly enough to list across **ALL THREE** futures markets:
1. **UM Futures (USDT-margined)**: e.g., BTCUSDT, ETHUSDT
2. **UM Futures (USDC-margined)**: e.g., BTCUSDC, ETHUSDC
3. **CM Futures (Coin-margined)**: e.g., BTCUSD_PERP, ETHUSD_PERP

**Current Count**: 18 Tier-1 instruments (BTC, ETH, SOL, ADA, AVAX, etc.)
**Key Characteristic**: Multi-market availability indicates Binance's highest confidence
**Use Cases**: Cross-market extrapolative reliability analysis, settlement currency arbitrage

**Structure**: `src/bin/` (tools), `tests/` (validation), `scripts/` (automation), `output/` (results)

## Common Issues

**Fixes**: `rustup update`, `cargo clean`, sort by `(timestamp, aggTradeId)`, thresholds from OPEN only

## Rust Binaries

**Tools**: `tier1-symbol-discovery --format [comprehensive|minimal]`, `rangebar-analyze`, `rangebar-export`

**Testing**: `cargo test`, `cargo bench` - validates non-lookahead, performance <100ms/1M ticks

**Publishing**: GitHub Actions OIDC on git tags, manual: `cargo publish --all-features`

## Dependency Management

**Auto-Updates**: Dependabot weekly PRs (`.github/dependabot.yml`), caret requirements (`^0.51.0`), manual validation (`scripts/update-deps.sh`)
