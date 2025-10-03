//! Real-time streaming processing engine
//!
//! High-performance streaming capabilities for real-time range bar processing
//! and technical indicator computation.
//!
//! ## Components
//!
//! - `processor` - Production streaming architecture with bounded memory
//! - `stats` - Streaming statistics engine
//! - `indicators` - Technical indicators (SMA, EMA, RSI, MACD, CCI)
//! - `universal` - Universal stream adapter (real-time, replay, speed control)
//! - `replay_buffer` - Time-windowed replay buffer

pub mod indicators;
pub mod processor;
pub mod replay_buffer;
pub mod stats;
pub mod universal;

// Re-export commonly used types
pub use indicators::{
    CCI, ExponentialMovingAverage, IndicatorError, MACD, MACDValue, RSI, SimpleMovingAverage,
};
pub use processor::{StreamingError, StreamingMetrics, StreamingProcessor, StreamingProcessorConfig};
pub use replay_buffer::ReplayBuffer;
pub use stats::{
    BarStats, OhlcStatistics, PriceStatistics, RollingStats, StatisticsSnapshot, StreamingConfig,
    StreamingStatsEngine, TradeStats, VolumeStatistics,
};
pub use universal::{StreamMode, TradeStream, UniversalStream};
