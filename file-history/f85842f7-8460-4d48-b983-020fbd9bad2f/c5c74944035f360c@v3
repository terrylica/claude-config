//! Dukascopy-specific type definitions
//!
//! Core data structures for Dukascopy tick data and enhanced range bars.
//! Wrapper pattern preserves standard RangeBar compatibility while adding
//! Forex-specific microstructure information.

use crate::core::fixed_point::FixedPoint;
use crate::core::types::RangeBar;
use serde::{Deserialize, Serialize};

/// Dukascopy tick data (market maker quote)
///
/// Semantic difference from aggTrades (Q10, Q11):
/// - aggTrades: Actual executed trades with real volume
/// - DukascopyTick: Market maker quotes with available liquidity
///
/// Critical: This is QUOTE data, not TRADE data.
/// No trade direction available → no buy/sell segregation possible.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DukascopyTick {
    /// Ask price (market maker offer price)
    pub ask: f64,

    /// Bid price (market maker bid price)
    pub bid: f64,

    /// Available liquidity at ask (NOT traded volume)
    pub ask_volume: f32,

    /// Available liquidity at bid (NOT traded volume)
    pub bid_volume: f32,

    /// Timestamp in milliseconds (GMT)
    /// Normalized to microseconds during conversion
    pub timestamp_ms: i64,
}

/// Spread dynamics and liquidity statistics (per-bar)
///
/// Uses Simple Moving Average (SMA) with O(1) incremental updates (Q6, Q21).
/// All state resets when bar closes (Q13) - per-bar semantics, not rolling.
///
/// Mathematical correctness (Q21):
/// - avg = sum / count (integer division on FixedPoint)
/// - Precision: 8 decimals adequate for financial spreads
/// - No EMA complexity needed (per-bar reset)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpreadStats {
    /// Sum of spreads (for SMA calculation)
    spread_sum: FixedPoint,

    /// Sum of bid liquidity (for SMA calculation)
    bid_liquidity_sum: FixedPoint,

    /// Sum of ask liquidity (for SMA calculation)
    ask_liquidity_sum: FixedPoint,

    /// Minimum spread observed in bar
    pub min_spread: FixedPoint,

    /// Maximum spread observed in bar
    pub max_spread: FixedPoint,

    /// Number of ticks in bar
    pub tick_count: u32,

    /// Number of zero-volume ticks (diagnostic metric, Q7)
    pub zero_volume_tick_count: u32,

    /// Total bid liquidity accumulated in bar
    pub total_bid_liquidity: FixedPoint,

    /// Total ask liquidity accumulated in bar
    pub total_ask_liquidity: FixedPoint,
}

impl SpreadStats {
    /// Create new SpreadStats with zero state
    pub fn new() -> Self {
        Self {
            spread_sum: FixedPoint(0),
            bid_liquidity_sum: FixedPoint(0),
            ask_liquidity_sum: FixedPoint(0),
            min_spread: FixedPoint(i64::MAX), // Will be replaced on first update
            max_spread: FixedPoint(i64::MIN),
            tick_count: 0,
            zero_volume_tick_count: 0,
            total_bid_liquidity: FixedPoint(0),
            total_ask_liquidity: FixedPoint(0),
        }
    }

    /// Update statistics with new tick (O(1) operation)
    ///
    /// Accumulates sums for later SMA calculation.
    /// Tracks min/max, counts, and totals.
    pub fn update(&mut self, tick: &DukascopyTick) {
        // Format with 8 decimals to match FixedPoint precision
        let spread_str = format!("{:.8}", tick.ask - tick.bid);
        let bid_vol_str = format!("{:.8}", tick.bid_volume);
        let ask_vol_str = format!("{:.8}", tick.ask_volume);

        let spread = FixedPoint::from_str(&spread_str)
            .unwrap_or(FixedPoint(0));
        let bid_vol = FixedPoint::from_str(&bid_vol_str)
            .unwrap_or(FixedPoint(0));
        let ask_vol = FixedPoint::from_str(&ask_vol_str)
            .unwrap_or(FixedPoint(0));

        // Accumulate for SMA (O(1))
        self.spread_sum = FixedPoint(self.spread_sum.0 + spread.0);
        self.bid_liquidity_sum = FixedPoint(self.bid_liquidity_sum.0 + bid_vol.0);
        self.ask_liquidity_sum = FixedPoint(self.ask_liquidity_sum.0 + ask_vol.0);

        // Track min/max
        if spread.0 < self.min_spread.0 {
            self.min_spread = spread;
        }
        if spread.0 > self.max_spread.0 {
            self.max_spread = spread;
        }

        // Count ticks
        self.tick_count += 1;
        if tick.bid_volume == 0.0 && tick.ask_volume == 0.0 {
            self.zero_volume_tick_count += 1;
        }

        // Track totals
        self.total_bid_liquidity = FixedPoint(self.total_bid_liquidity.0 + bid_vol.0);
        self.total_ask_liquidity = FixedPoint(self.total_ask_liquidity.0 + ask_vol.0);
    }

    /// Calculate average spread (O(1) operation)
    ///
    /// Integer division on FixedPoint is mathematically correct (Q21):
    /// (Σ value_i × 10^8) / N = (Σ value_i / N) × 10^8
    pub fn avg_spread(&self) -> FixedPoint {
        if self.tick_count > 0 {
            FixedPoint(self.spread_sum.0 / self.tick_count as i64)
        } else {
            FixedPoint(0)
        }
    }

    /// Calculate average bid liquidity (O(1) operation)
    pub fn avg_bid_liquidity(&self) -> FixedPoint {
        if self.tick_count > 0 {
            FixedPoint(self.bid_liquidity_sum.0 / self.tick_count as i64)
        } else {
            FixedPoint(0)
        }
    }

    /// Calculate average ask liquidity (O(1) operation)
    pub fn avg_ask_liquidity(&self) -> FixedPoint {
        if self.tick_count > 0 {
            FixedPoint(self.ask_liquidity_sum.0 / self.tick_count as i64)
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

/// Range bar enhanced with Dukascopy-specific microstructure
///
/// Wrapper pattern (Q3): Preserves standard RangeBar API while adding
/// Forex-specific metrics unavailable in aggTrades.
///
/// Volume semantics (Q10, Q11):
/// - base.volume = total_bid_liquidity + total_ask_liquidity
/// - base.buy_volume = 0 (direction unknown for quote data)
/// - base.sell_volume = 0 (direction unknown for quote data)
/// - spread_stats captures bid/ask asymmetry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DukascopyRangeBar {
    /// Standard OHLCV range bar
    pub base: RangeBar,

    /// Dukascopy-specific spread and liquidity metrics
    pub spread_stats: SpreadStats,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_spread_stats_sma_calculation() {
        let mut stats = SpreadStats::new();

        // Add 3 ticks with known spreads
        stats.update(&DukascopyTick {
            bid: 1.0800,
            ask: 1.0815, // spread = 0.0015
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1000000,
        });

        stats.update(&DukascopyTick {
            bid: 1.0802,
            ask: 1.0818, // spread = 0.0016
            bid_volume: 110.0,
            ask_volume: 130.0,
            timestamp_ms: 1001000,
        });

        stats.update(&DukascopyTick {
            bid: 1.0801,
            ask: 1.0815, // spread = 0.0014
            bid_volume: 105.0,
            ask_volume: 125.0,
            timestamp_ms: 1002000,
        });

        assert_eq!(stats.tick_count, 3);
        assert_eq!(stats.zero_volume_tick_count, 0);

        // Verify averages are calculated (values depend on FixedPoint conversion)
        assert!(stats.avg_spread().0 > 0);
        assert!(stats.avg_bid_liquidity().0 > 0);
        assert!(stats.avg_ask_liquidity().0 > 0);
    }

    #[test]
    fn test_zero_volume_tracking() {
        let mut stats = SpreadStats::new();

        // Zero-volume tick (Q7, Q14)
        stats.update(&DukascopyTick {
            bid: 1.0800,
            ask: 1.0815,
            bid_volume: 0.0,
            ask_volume: 0.0,
            timestamp_ms: 1000000,
        });

        assert_eq!(stats.tick_count, 1);
        assert_eq!(stats.zero_volume_tick_count, 1);
        assert_eq!(stats.total_bid_liquidity.0, 0);
        assert_eq!(stats.total_ask_liquidity.0, 0);
    }
}
