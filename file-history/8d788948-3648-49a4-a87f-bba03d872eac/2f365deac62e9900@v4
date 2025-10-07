//! Non-lookahead range bar construction for cryptocurrency trading.
//!
//! This crate provides algorithms for constructing range bars from aggTrade data
//! with temporal integrity guarantees, ensuring no lookahead bias in financial backtesting.
//!
//! ## Features
//!
//! - Non-lookahead bias range bar construction
//! - Fixed-point arithmetic for precision
//! - Dual-path streaming and batch processing
//! - Polars-powered analytics and I/O
//! - Tier-1 cryptocurrency symbol discovery
//! - Pure Rust implementation
//!
//! ## Basic Usage
//!
//! ```rust
//! use rangebar::{RangeBarProcessor, AggTrade, FixedPoint};
//!
//! // Create processor with 250 basis points threshold
//! let mut processor = RangeBarProcessor::new(250);
//!
//! // Create sample aggTrade
//! let trade = AggTrade {
//!     agg_trade_id: 1,
//!     price: FixedPoint::from_str("50000.0").unwrap(),
//!     volume: FixedPoint::from_str("1.0").unwrap(),
//!     first_trade_id: 1,
//!     last_trade_id: 1,
//!     timestamp: 1609459200000,
//!     is_buyer_maker: false,
//!     is_best_match: None,
//! };
//!
//! // Process aggTrade records into range bars
//! let agg_trade_records = vec![trade];
//! let bars = processor.process_agg_trade_records(&agg_trade_records).unwrap();
//! ```
//!
//! ## Dual-Path Architecture
//!
//! ### Streaming Mode (Real-time)
//! ```rust
//! use rangebar::StreamingProcessor;
//!
//! let threshold_bps = 25; // 0.25% range bars
//! let processor = StreamingProcessor::new(threshold_bps);
//! // Real-time processing with bounded memory
//! ```
//!
//! ### Batch Mode (Analytics)
//! ```rust
//! #[cfg(feature = "polars-analytics")]
//! use rangebar::engines::batch::BatchAnalysisEngine;
//! use rangebar::core::types::RangeBar;
//!
//! #[cfg(feature = "polars-analytics")]
//! {
//!     let range_bars: Vec<RangeBar> = vec![]; // Your range bar data
//!     let engine = BatchAnalysisEngine::new();
//!     // let result = engine.analyze_single_symbol(&range_bars, "BTCUSDT").unwrap(); // Commented out for empty data
//! }
//! ```
//!
//! ## I/O Operations
//! ```rust
//! #[cfg(feature = "polars-io")]
//! use rangebar::infrastructure::io::ParquetExporter;
//! use rangebar::core::types::RangeBar;
//!
//! #[cfg(feature = "polars-io")]
//! {
//!     let range_bars: Vec<RangeBar> = vec![]; // Your range bar data
//!     let exporter = ParquetExporter::new();
//!     // exporter.export(&range_bars, "output.parquet").unwrap(); // Commented out to avoid file I/O in tests
//! }
//! ```
//!
//! ## Algorithm
//!
//! Range bars close when price moves ±threshold% from the bar's **opening price**:
//!
//! 1. **Non-lookahead bias**: Thresholds computed only from bar open price
//! 2. **Breach inclusion**: Breaching aggTrade included in closing bar
//! 3. **Fixed thresholds**: Never recalculated during bar lifetime
//!

// Core modules (always available)
pub mod core;

// New structure (Phases 3-7: Providers + Engines + Infrastructure)
pub mod providers;
pub mod engines;
pub mod infrastructure;

// Test utilities (only available in test builds)
#[cfg(any(test, feature = "test-utils"))]
pub mod test_utils;

// Optional modules based on feature flags (now in infrastructure/engines)

// Legacy modules for backward compatibility

// Production-ready streaming architecture available via crate::streaming module

// Legacy compatibility
pub mod fixed_point {
    pub use crate::core::fixed_point::*;
}

pub mod range_bars {
    pub use crate::core::processor::*;
}

pub mod tier1 {
    pub use crate::providers::binance::symbols::*;
}

pub mod types {
    pub use crate::core::types::*;
}

// Re-export commonly used types for convenience
pub use infrastructure::config::Settings;
pub use core::{
    AggTrade, ExportRangeBarProcessor, FixedPoint, ProcessingError, RangeBar, RangeBarProcessor,
};
pub use providers::binance::symbols::{TIER1_SYMBOLS, get_tier1_symbols, get_tier1_usdt_pairs, is_tier1_symbol};
pub use engines::streaming::processor::{
    StreamingError, StreamingMetrics, StreamingProcessor, StreamingProcessorConfig,
};

// Re-export Polars-powered modules when features are enabled
#[cfg(feature = "polars-io")]
pub use infrastructure::io::{ArrowExporter, ParquetExporter, PolarsExporter, StreamingCsvExporter};

#[cfg(feature = "polars-analytics")]
pub use engines::batch::{AnalysisReport, BatchAnalysisEngine, BatchConfig, BatchResult};

#[cfg(feature = "streaming-stats")]
pub use engines::streaming::stats::{
    BarStats, OhlcStatistics, PriceStatistics, RollingStats, StatisticsSnapshot,
    StreamingStatsEngine, TradeStats, VolumeStatistics,
};

#[cfg(feature = "real-time-indicators")]
pub use engines::streaming::indicators::{
    CCI, ExponentialMovingAverage, IndicatorError, MACD, MACDValue, RSI, SimpleMovingAverage,
};

/// Version information
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const NAME: &str = env!("CARGO_PKG_NAME");
pub const DESCRIPTION: &str = env!("CARGO_PKG_DESCRIPTION");

/// Library initialization and configuration
pub fn init() {
    // Future: Initialize logging, metrics, etc.
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[allow(clippy::const_is_empty)]
    fn test_version() {
        assert!(!VERSION.is_empty());
        assert!(!NAME.is_empty());
        assert!(!DESCRIPTION.is_empty());
    }

    #[test]
    fn test_types_export() {
        // Test that we can create and use exported types
        let fp = FixedPoint::from_str("123.456").unwrap();
        assert_eq!(fp.to_string(), "123.45600000");
    }

    // Legacy statistics test disabled
    // #[cfg(feature = "statistics")]
    // #[test]
    // fn test_statistics_export() {
    //     // Test that statistics module is accessible
    //     let engine = StatisticalEngine::new();
    //     assert!(engine.config().parallel_computation);
    // }
}
