//! Core range bar processing algorithms
//!
//! Non-lookahead bias range bar construction with temporal integrity guarantees.
//!
//! ## Features
//!
//! - Non-lookahead bias: Thresholds computed only from bar open price
//! - Breach inclusion: Breaching trade included in closing bar
//! - Fixed thresholds: Never recalculated during bar lifetime
//! - Temporal integrity: Guaranteed correct historical simulation

pub mod fixed_point;
pub mod processor;
pub mod timestamp;
pub mod types;

// Test utilities (only available in test builds or with test-utils feature)
#[cfg(any(test, feature = "test-utils"))]
pub mod test_utils;

// Re-export commonly used types
pub use fixed_point::FixedPoint;
pub use processor::{ExportRangeBarProcessor, ProcessingError, RangeBarProcessor};
pub use timestamp::{
    create_aggtrade_with_normalized_timestamp, normalize_timestamp, validate_timestamp,
};
pub use types::{AggTrade, DataSource, RangeBar};
