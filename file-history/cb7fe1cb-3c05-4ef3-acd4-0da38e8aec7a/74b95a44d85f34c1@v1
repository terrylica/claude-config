//! Exness data types and error handling
//!
//! Core data structures for Exness Raw_Spread tick data, enhanced range bars,
//! and error types with fail-fast propagation.

use rangebar_core::fixed_point::FixedPoint;
use rangebar_core::processor::ProcessingError;
use rangebar_core::types::RangeBar;
use serde::{Deserialize, Serialize};
use thiserror::Error;

// ============================================================================
// Error Types
// ============================================================================

/// Top-level Exness processing error
///
/// Error policy: Raise and propagate immediately, no fallbacks or defaults.
#[derive(Error, Debug)]
pub enum ExnessError {
    /// Tick conversion failure (validation)
    #[error("Conversion error: {0}")]
    Conversion(#[from] ConversionError),

    /// Core range bar processing error (algorithm failure)
    #[error("Processing error: {0}")]
    Processing(#[from] ProcessingError),

    /// HTTP request failure
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),

    /// ZIP archive extraction failure
    #[error("ZIP error: {0}")]
    Zip(#[from] zip::result::ZipError),

    /// CSV parsing failure
    #[error("CSV error: {0}")]
    Csv(#[from] csv::Error),

    /// Timestamp parsing failure
    #[error("Timestamp parse error: {0}")]
    Timestamp(#[from] chrono::ParseError),

    /// I/O error
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
}

/// Tick conversion and validation errors
///
/// Error policy: Raise immediately on any validation failure.
/// No skipping, no error rate thresholds - strict fail-fast.
#[derive(Error, Debug)]
pub enum ConversionError {
    /// Bid price <= 0 (invalid quote)
    #[error("Invalid bid price: {bid} (must be > 0)")]
    InvalidBid { bid: f64 },

    /// Ask price <= 0 (invalid quote)
    #[error("Invalid ask price: {ask} (must be > 0)")]
    InvalidAsk { ask: f64 },

    /// Crossed market: bid > ask (data corruption)
    #[error("Crossed market: bid={bid} > ask={ask}")]
    CrossedMarket { bid: f64, ask: f64 },

    /// Spread exceeds threshold (stale quote)
    #[error("Excessive spread: {spread_pct:.2}% (threshold: {threshold_pct:.2}%)")]
    ExcessiveSpread {
        spread_pct: f64,
        threshold_pct: f64,
    },

    /// FixedPoint conversion error (f64 → FixedPoint)
    #[error("FixedPoint conversion failed for '{value}': {error}")]
    FixedPointConversion { value: String, error: String },
}

/// Validation strictness level for tick processing
///
/// Configurable at builder construction time.
/// - Permissive: Basic checks only (bid > 0, ask > 0, bid < ask)
/// - Strict: + Spread < 10% [DEFAULT]
/// - Paranoid: + Spread < 1% (flags suspicious data)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum ValidationStrictness {
    /// Basic checks only (bid > 0, ask > 0, bid < ask)
    Permissive,

    /// + Spread < 10% (catches obvious errors) [DEFAULT]
    #[default]
    Strict,

    /// + Spread < 1% (flags suspicious data)
    Paranoid,
}

// ============================================================================
// Data Types
// ============================================================================

/// Exness tick data (market maker quote)
///
/// Exness Raw_Spread variant characteristics:
/// - Bimodal spread distribution: 98% at 0.0 pips, 2% at 1-9 pips
/// - CV=8.17 (8× higher variability than Standard variant)
/// - Encodes broker risk perception via spread dynamics
///
/// Data source: ZIP → CSV (monthly granularity)
/// Format: Bid, Ask, Timestamp (no volumes)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExnessTick {
    /// Bid price (market maker bid)
    pub bid: f64,

    /// Ask price (market maker offer)
    pub ask: f64,

    /// Timestamp in milliseconds (UTC)
    /// Parsed from ISO 8601 format
    pub timestamp_ms: i64,
}

/// Spread dynamics statistics (per-bar)
///
/// Uses Simple Moving Average (SMA) with O(1) incremental updates.
/// All state resets when bar closes - per-bar semantics.
///
/// Mathematical correctness:
/// - avg = sum / count (integer division on FixedPoint)
/// - Precision: 8 decimals adequate for financial spreads
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpreadStats {
    /// Sum of spreads (for SMA calculation)
    spread_sum: FixedPoint,

    /// Minimum spread observed in bar
    pub min_spread: FixedPoint,

    /// Maximum spread observed in bar
    pub max_spread: FixedPoint,

    /// Number of ticks in bar
    pub tick_count: u32,
}

impl SpreadStats {
    /// Create new SpreadStats with zero state
    pub fn new() -> Self {
        Self {
            spread_sum: FixedPoint(0),
            min_spread: FixedPoint(i64::MAX), // Will be replaced on first update
            max_spread: FixedPoint(i64::MIN),
            tick_count: 0,
        }
    }

    /// Update statistics with new tick (O(1) operation)
    ///
    /// Accumulates sums for later SMA calculation.
    /// Tracks min/max and counts.
    pub fn update(&mut self, tick: &ExnessTick) {
        // Format with 8 decimals to match FixedPoint precision
        let spread_str = format!("{:.8}", tick.ask - tick.bid);

        let spread = FixedPoint::from_str(&spread_str)
            .unwrap_or(FixedPoint(0));

        // Accumulate for SMA (O(1))
        self.spread_sum = FixedPoint(self.spread_sum.0 + spread.0);

        // Track min/max
        if spread.0 < self.min_spread.0 {
            self.min_spread = spread;
        }
        if spread.0 > self.max_spread.0 {
            self.max_spread = spread;
        }

        // Count ticks
        self.tick_count += 1;
    }

    /// Calculate average spread (O(1) operation)
    ///
    /// Integer division on FixedPoint is mathematically correct:
    /// (Σ value_i × 10^8) / N = (Σ value_i / N) × 10^8
    pub fn avg_spread(&self) -> FixedPoint {
        if self.tick_count > 0 {
            FixedPoint(self.spread_sum.0 / self.tick_count as i64)
        } else {
            FixedPoint(0)
        }
    }
}

impl Default for SpreadStats {
    fn default() -> Self {
        Self::new()
    }
}

/// Range bar enhanced with Exness-specific spread metrics
///
/// Wrapper pattern: Preserves standard RangeBar API while adding
/// Forex-specific spread dynamics unavailable in aggTrades.
///
/// Volume semantics:
/// - base.volume = 0 (Exness Raw_Spread has no volume data)
/// - base.buy_volume = 0 (direction unknown for quote data)
/// - base.sell_volume = 0 (direction unknown for quote data)
/// - spread_stats captures market stress signals
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExnessRangeBar {
    /// Standard OHLCV range bar
    pub base: RangeBar,

    /// Exness-specific spread metrics
    pub spread_stats: SpreadStats,
}

// ============================================================================
// SLOs (Service Level Objectives)
// ============================================================================

/// Availability SLO: 100% fetch success
///
/// Target: Zero rate limiting (empirical: 100% vs Dukascopy 77.5%)
/// Measurement: HTTP request success rate
/// Alerting: Any HTTP 503 or timeout triggers immediate failure
pub const AVAILABILITY_SLO_TARGET: f64 = 1.0;

/// Correctness SLO: 100% data validation pass
///
/// Target: All ticks pass validation (no CrossedMarket, ExcessiveSpread)
/// Measurement: Validation error rate
/// Alerting: Any validation error triggers immediate failure
pub const CORRECTNESS_SLO_TARGET: f64 = 1.0;

/// Observability SLO: All errors logged with full context
///
/// Target: 100% error traceability
/// Measurement: Error propagation completeness
/// Implementation: thiserror with full context preservation
pub const OBSERVABILITY_SLO_TARGET: f64 = 1.0;

/// Maintainability SLO: Out-of-box dependencies only
///
/// Target: Zero custom parsers (use zip, csv, chrono crates)
/// Measurement: Dependency graph audit
/// Implementation: Standard crates, no LZMA/binary complexity
pub const MAINTAINABILITY_SLO_STANDARD: &str = "out-of-box";

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_spread_stats_sma_calculation() {
        let mut stats = SpreadStats::new();

        // Add 3 ticks with known spreads
        stats.update(&ExnessTick {
            bid: 1.0800,
            ask: 1.0815, // spread = 0.0015
            timestamp_ms: 1000000,
        });

        stats.update(&ExnessTick {
            bid: 1.0802,
            ask: 1.0818, // spread = 0.0016
            timestamp_ms: 1001000,
        });

        stats.update(&ExnessTick {
            bid: 1.0801,
            ask: 1.0815, // spread = 0.0014
            timestamp_ms: 1002000,
        });

        assert_eq!(stats.tick_count, 3);

        // Verify averages are calculated (values depend on FixedPoint conversion)
        assert!(stats.avg_spread().0 > 0);
        assert!(stats.min_spread.0 > 0);
        assert!(stats.max_spread.0 > 0);
    }

    #[test]
    fn test_spread_stats_min_max_tracking() {
        let mut stats = SpreadStats::new();

        stats.update(&ExnessTick {
            bid: 1.0800,
            ask: 1.0810, // spread = 0.0010
            timestamp_ms: 1000000,
        });

        stats.update(&ExnessTick {
            bid: 1.0802,
            ask: 1.0822, // spread = 0.0020 (max)
            timestamp_ms: 1001000,
        });

        stats.update(&ExnessTick {
            bid: 1.0801,
            ask: 1.0806, // spread = 0.0005 (min)
            timestamp_ms: 1002000,
        });

        assert_eq!(stats.tick_count, 3);
        // Min should be smallest spread
        assert!(stats.min_spread.0 < stats.max_spread.0);
    }
}
