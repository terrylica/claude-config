//! Data provider integrations
//!
//! Source-specific adapters for fetching and processing tick/trade data.
//!
//! ## Supported Providers
//!
//! - `binance` - Binance spot and futures markets (primary - crypto)
//! - `exness` - Exness Raw_Spread tick data (primary - forex)
//! - `dukascopy` - ⚠️ DEPRECATED (rate limiting issues, use `exness`)
//!
//! ## Provider Selection
//!
//! | Asset Class | Provider | Rationale |
//! |-------------|----------|-----------|
//! | Crypto | Binance | Official data, high volume, REST + WebSocket |
//! | Forex | Exness | Zero rate limiting, 100% reliability, simple format |
//! | ~~Forex~~ | ~~Dukascopy~~ | DEPRECATED (77.5% success rate, see `dukascopy/README.md`) |
//!
//! ## Adding New Providers
//!
//! Follow the established pattern:
//!
//! ```text
//! providers/
//! └── [provider_name]/
//!     ├── mod.rs          # Public API and documentation
//!     ├── client.rs       # HTTP client or WebSocket
//!     ├── types.rs        # Provider-specific data structures
//!     ├── builder.rs      # Range bar builder (if custom logic needed)
//!     └── conversion.rs   # Convert to AggTrade format
//! ```
//!
//! ## Design Principles
//!
//! 1. **Adapter pattern**: Convert provider format → AggTrade (core format)
//! 2. **Error propagation**: Raise immediately, no silent failures
//! 3. **Stateless where possible**: Cache externally, not in provider
//! 4. **Documented edge cases**: Timezone handling, decimal factors, etc.
//! 5. **Out-of-box dependencies**: Use standard crates (zip, csv, chrono)

#[cfg(feature = "binance")]
pub mod binance;

#[cfg(feature = "exness")]
pub mod exness;

#[cfg(feature = "dukascopy")]
#[deprecated(
    since = "2.3.0",
    note = "Use `exness` provider instead (zero rate limiting, 100% reliability). See src/providers/dukascopy/README.md"
)]
pub mod dukascopy;
