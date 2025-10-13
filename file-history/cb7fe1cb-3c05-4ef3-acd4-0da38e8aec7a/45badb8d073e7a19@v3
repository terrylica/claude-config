//! Data provider integrations
//!
//! Source-specific adapters for fetching and processing tick/trade data.
//!
//! ## Supported Providers
//!
//! - `binance` - Binance spot and futures markets (primary - crypto)
//! - `exness` - Exness EURUSD Standard tick data (primary - forex)
//!
//! ## Provider Selection
//!
//! | Asset Class | Provider | Rationale |
//! |-------------|----------|-----------|
//! | Crypto | Binance | Official data, high volume, REST + WebSocket |
//! | Forex | Exness | Zero rate limiting, 100% reliability, simple format |
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
