//! Real-time streaming engine for range bar processing
//!
//! This module provides real-time streaming capabilities for processing
//! range bars from live data sources with support for replay, statistics,
//! and indicators.

pub mod replay_buffer;
pub mod processor;

#[cfg(feature = "stats")]
pub mod stats;

#[cfg(feature = "indicators")]
pub mod indicators;

#[cfg(feature = "binance-integration")]
pub mod universal;

// Re-export commonly used types
pub use replay_buffer::{ReplayBuffer, ReplayBufferStats};
pub use processor::StreamingProcessor;

#[cfg(feature = "stats")]
pub use stats::{StreamingStatsEngine, StreamingConfig, StatisticsSnapshot};

#[cfg(feature = "indicators")]
pub use indicators::{
    ExponentialMovingAverage, IndicatorError, MACD, MACDValue, RSI, SimpleMovingAverage, CCI,
};

#[cfg(feature = "binance-integration")]
pub use universal::{StreamError, StreamMode, TradeStream, UniversalStream};
