//! Batch processing and analysis using Polars
//!
//! This module provides batch analytics capabilities powered by Polars
//! for research, backtesting, and advanced statistical analysis.

#[cfg(feature = "polars-analytics")]
pub mod engine;

// Re-export commonly used types when polars-analytics feature is enabled
#[cfg(feature = "polars-analytics")]
pub use engine::{AnalysisReport, BatchAnalysisEngine, BatchConfig, BatchError, BatchResult};
