# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Non-lookahead bias range bar construction from tick data (crypto: Binance aggTrades, forex: Exness EURUSD Raw_Spread).

**Core Algorithm**: See authoritative specification → [`docs/specifications/algorithm-spec.md`](/Users/terryli/eon/rangebar/docs/specifications/algorithm-spec.md)

**Architecture**: Pure Rust implementation for performance and reliability (processes 1B+ ticks). All components native Rust: symbol discovery, data processing, and analysis.

## Workspace Structure (v5.0.0)

**Modular Crate Architecture**: 8 specialized crates organized as Cargo workspace

**Core Crates**:
- `crates/rangebar-core/` - Core algorithm, fixed-point arithmetic, types
- `crates/rangebar-providers/` - Data providers (Binance, Exness)
- `crates/rangebar-config/` - Configuration management
- `crates/rangebar-io/` - I/O operations and Polars integration

**Engine Crates**:
- `crates/rangebar-streaming/` - Real-time streaming processor
- `crates/rangebar-batch/` - Batch analytics engine

**Tools & Compatibility**:
- `crates/rangebar-cli/` - Command-line tools (all binaries)
- `crates/rangebar/` - Meta-crate for v4.0.0 backward compatibility

**Legacy**:
- `src-archived/` - v4.0.0 monolithic structure (archived, git tracked)

## Key Commands

**Dev**: `cargo build --release`, `cargo test`, `cargo clippy`, `./scripts/update-deps.sh`

**Release**: `./scripts/release.sh` - Automated versioning, changelog, and GitHub release

**Deploy**: `doppler run -- shuttle deploy`

**Data Ops**: `tier1-symbol-discovery --format comprehensive`, `parallel-tier1-analysis`, `spot-tier1-processor`, `data-structure-validator --features data-integrity`

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
6. **Analysis**: `parallel-tier1-analysis` → Parallel multi-symbol batch analysis
7. **Output**: Structured bar data (OHLCV format)

**Performance**: Pure Rust, Rayon parallelism, fixed-point arithmetic

## Critical Algorithm Invariants

**Specification**: [`docs/specifications/algorithm-spec.md`](/Users/terryli/eon/rangebar/docs/specifications/algorithm-spec.md) (authoritative)
**Breach Consistency**: `(high_breach → close_breach) AND (low_breach → close_breach)`

### Data Source Requirements

#### Binance (Primary - Crypto)
- **Source**: https://github.com/stas-prokopiev/binance_historical_data
- **Primary Asset Class**: `"spot"` (Default) for standard spot trading pairs
- **Optional Markets**: `"um"` (USD-M Futures) for USDT/USDC perpetuals, `"cm"` (Coin-M Futures)
- **Data Type**: `"aggTrades"` **ONLY**
- **Usage**: Specify market type via command line arguments or use spot by default

#### Exness (Primary - Forex)
- **Variant**: `EURUSD_Raw_Spread` - **CHOSEN** for 8× higher spread variability (CV=8.17) encoding broker risk perception
- **Why Raw_Spread**: Bimodal distribution (98% at 0.0 pips + 2% stress events 1-9 pips) = maximum signal-to-noise for market stress forecasting
- **Rejected Alternatives**: Standard (CV=0.46, too constant), Standard_Plus (higher cost, lower CV), Cent/Mini (unnecessary contract sizes)
- **API**: `https://ticks.ex2archive.com/ticks/EURUSD_Raw_Spread/{year}/{month}/Exness_EURUSD_Raw_Spread_{year}_{month}.zip`
- **Format**: ZIP→CSV (Bid/Ask/Timestamp), ~925K-1.18M ticks/month, validated 2019-2025
- **Data Characteristics**: No volume data (mid-price used for range bars), commission-based pricing model
- **Thresholds**: 0.1bps (minimum), 0.2bps (HFT), 0.5bps (intraday), 1.0bps (swing)

### Tier-1 Instruments Definition
**Tier-1 instruments** are crypto assets that Binance respects highly enough to list across **ALL THREE** futures markets:
1. **UM Futures (USDT-margined)**: e.g., BTCUSDT, ETHUSDT
2. **UM Futures (USDC-margined)**: e.g., BTCUSDC, ETHUSDC
3. **CM Futures (Coin-margined)**: e.g., BTCUSD_PERP, ETHUSD_PERP

**Current Count**: 18 Tier-1 instruments (BTC, ETH, SOL, ADA, AVAX, etc.)
**Key Characteristic**: Multi-market availability indicates Binance's highest confidence
**Use Cases**: Cross-market extrapolative reliability analysis, settlement currency arbitrage

**Directory Structure**: `crates/` (workspace crates), `tests/` (integration tests), `scripts/` (automation), `output/` (results), `src-archived/` (v4.0.0 legacy code)

## Common Issues

**Fixes**: `rustup update`, `cargo clean`, sort by `(timestamp, aggTradeId)`, thresholds from OPEN only

## Rust Binaries

**Location**: All command-line tools consolidated in `crates/rangebar-cli/src/bin/` (6 binaries)

**Tools**: `tier1-symbol-discovery --format [comprehensive|minimal]`, `parallel-tier1-analysis`, `spot-tier1-processor`, `data-structure-validator`, `polars-benchmark`, `temporal-integrity-test-only`

**Testing**: `cargo test`, `cargo bench` - validates non-lookahead, performance <100ms/1M ticks

**Publishing**: GitHub Actions OIDC on git tags, manual: `cargo publish -p <crate-name>`

## Dependency Management

**Auto-Updates**: Dependabot weekly PRs (`.github/dependabot.yml`), caret requirements (`^0.51.0`), manual validation (`scripts/update-deps.sh`)

## Release Workflow

**Automation**: git-cliff + Commitizen for automated release management

**Process**: `./scripts/release.sh` executes:
1. Version bump (Commitizen with SemVer)
2. CHANGELOG.md generation (git-cliff with detailed commit history)
3. RELEASE_NOTES.md generation (git-cliff with user-friendly format)
4. Git push with tags
5. GitHub release creation

**Configuration**:
- `.cz.toml` - Commitizen config (version tracking, conventional commits)
- `cliff.toml` - Detailed changelog template (developer-focused)
- `cliff-release-notes.toml` - Release notes template (user-focused)

**Manual Commands**:
- `uvx --from commitizen cz bump --yes` - Version bump only
- `git-cliff --config cliff.toml --output CHANGELOG.md` - Generate changelog
- `git-cliff --config cliff-release-notes.toml --latest --output RELEASE_NOTES.md` - Generate release notes
