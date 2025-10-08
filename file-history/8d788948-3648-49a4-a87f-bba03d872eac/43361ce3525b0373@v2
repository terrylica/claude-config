//! Processing engines
//!
//! Different modes of range bar processing optimized for specific use cases.
//!
//! ## Engine Types
//!
//! - `streaming` - Real-time streaming with bounded memory and backpressure
//! - `batch` - Large-scale batch analytics with Polars integration
//!
//! ## Architecture
//!
//! Both engines consume the same core algorithm (RangeBarProcessor) but differ
//! in memory management and I/O strategies:
//!
//! - Streaming: Constant memory, reactive, suitable for live trading
//! - Batch: Bulk processing, parallel analytics, suitable for backtesting

pub mod streaming;

#[cfg(feature = "polars-analytics")]
pub mod batch;
