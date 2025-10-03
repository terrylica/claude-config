//! Data provider integrations
//!
//! Source-specific adapters for fetching and processing tick/trade data.
//!
//! ## Supported Providers
//!
//! - `binance` - Binance spot and futures markets (primary - crypto)
//! - `dukascopy` - Dukascopy tick data (secondary - forex/multi-asset)
//!
//! ## Adding New Providers
//!
//! Follow the established pattern:
//!
//! ```
//! providers/
//! └── [provider_name]/
//!     ├── mod.rs          # Public API and documentation
//!     ├── client.rs       # HTTP client or WebSocket
//!     ├── types.rs        # Provider-specific data structures
//!     └── conversion.rs   # Convert to AggTrade format
//! ```
//!
//! ## Design Principles
//!
//! 1. **Adapter pattern**: Convert provider format → AggTrade (core format)
//! 2. **Error propagation**: Raise immediately, no silent failures
//! 3. **Stateless where possible**: Cache externally, not in provider
//! 4. **Documented edge cases**: Timezone handling, decimal factors, etc.

pub mod binance;

// Dukascopy will be added in Phase 4
// pub mod dukascopy;
