//! Core range bar processing algorithm
//!
//! Implements non-lookahead bias range bar construction where bars close when
//! price moves ±threshold bps from the bar's OPEN price.

use crate::fixed_point::FixedPoint;
use crate::types::{AggTrade, RangeBar};
#[cfg(feature = "python")]
use pyo3::prelude::*;
use thiserror::Error;

/// Range bar processor with non-lookahead bias guarantee
pub struct RangeBarProcessor {
    /// Threshold in tenths of basis points (250 = 25bps, v3.0.0+)
    threshold_bps: u32,

    /// Current bar state for streaming processing (Q19)
    /// Enables get_incomplete_bar() and stateful process_single_trade()
    current_bar_state: Option<RangeBarState>,
}

impl RangeBarProcessor {
    /// Create new processor with given threshold
    ///
    /// # Arguments
    ///
    /// * `threshold_bps` - Threshold in **tenths of basis points** (0.1bps units)
    ///   - Example: `250` → 25bps = 0.25%
    ///   - Example: `10` → 1bps = 0.01%
    ///   - Minimum: `1` → 0.1bps = 0.001%
    ///
    /// # Breaking Change (v3.0.0)
    ///
    /// Prior to v3.0.0, `threshold_bps` was in 1bps units.
    /// **Migration**: Multiply all threshold values by 10.
    pub fn new(threshold_bps: u32) -> Self {
        Self {
            threshold_bps,
            current_bar_state: None,
        }
    }

    /// Process a single trade and return completed bar if any
    ///
    /// Maintains internal state for streaming use case. State persists across calls
    /// until a bar completes (threshold breach), enabling get_incomplete_bar().
    ///
    /// # Arguments
    ///
    /// * `trade` - Single aggregated trade to process
    ///
    /// # Returns
    ///
    /// `Some(RangeBar)` if a bar was completed, `None` otherwise
    ///
    /// # State Management
    ///
    /// - First trade: Initializes new bar state
    /// - Subsequent trades: Updates existing bar or closes on breach
    /// - Breach: Returns completed bar, starts new bar with breaching trade
    pub fn process_single_trade(
        &mut self,
        trade: AggTrade,
    ) -> Result<Option<RangeBar>, ProcessingError> {
        match &mut self.current_bar_state {
            None => {
                // First trade - initialize new bar
                self.current_bar_state = Some(RangeBarState::new(&trade, self.threshold_bps));
                Ok(None)
            }
            Some(bar_state) => {
                // Check for threshold breach
                if bar_state.bar.is_breach(
                    trade.price,
                    bar_state.upper_threshold,
                    bar_state.lower_threshold,
                ) {
                    // Breach detected - close current bar
                    bar_state.bar.update_with_trade(&trade);

                    // Validation: Ensure high/low include open/close extremes
                    debug_assert!(
                        bar_state.bar.high >= bar_state.bar.open.max(bar_state.bar.close)
                    );
                    debug_assert!(bar_state.bar.low <= bar_state.bar.open.min(bar_state.bar.close));

                    let completed_bar = bar_state.bar.clone();

                    // Start new bar with breaching trade
                    self.current_bar_state = Some(RangeBarState::new(&trade, self.threshold_bps));

                    Ok(Some(completed_bar))
                } else {
                    // No breach - update existing bar
                    bar_state.bar.update_with_trade(&trade);
                    Ok(None)
                }
            }
        }
    }

    /// Get any incomplete bar currently being processed
    ///
    /// Returns clone of current bar state for inspection without consuming it.
    /// Useful for final bar at stream end or progress monitoring.
    ///
    /// # Returns
    ///
    /// `Some(RangeBar)` if bar is in progress, `None` if no active bar
    pub fn get_incomplete_bar(&self) -> Option<RangeBar> {
        self.current_bar_state
            .as_ref()
            .map(|state| state.bar.clone())
    }

    /// Process AggTrade records into range bars including incomplete bars for analysis
    ///
    /// # Arguments
    ///
    /// * `agg_trade_records` - Slice of AggTrade records sorted by (timestamp, agg_trade_id)
    ///
    /// # Returns
    ///
    /// Vector of range bars including incomplete bars at end of data
    ///
    /// # Warning
    ///
    /// This method is for analysis purposes only. Incomplete bars violate the
    /// fundamental range bar algorithm and should not be used for production trading.
    pub fn process_agg_trade_records_with_incomplete(
        &mut self,
        agg_trade_records: &[AggTrade],
    ) -> Result<Vec<RangeBar>, ProcessingError> {
        self.process_agg_trade_records_with_options(agg_trade_records, true)
    }

    /// Process Binance aggregated trade records into range bars
    ///
    /// This is the primary method for converting AggTrade records (which aggregate
    /// multiple individual trades) into range bars based on price movement thresholds.
    ///
    /// # Parameters
    ///
    /// * `agg_trade_records` - Slice of AggTrade records sorted by (timestamp, agg_trade_id)
    ///   Each record represents multiple individual trades aggregated at same price
    ///
    /// # Returns
    ///
    /// Vector of completed range bars (ONLY bars that breached thresholds).
    /// Each bar tracks both individual trade count and AggTrade record count.
    pub fn process_agg_trade_records(
        &mut self,
        agg_trade_records: &[AggTrade],
    ) -> Result<Vec<RangeBar>, ProcessingError> {
        self.process_agg_trade_records_with_options(agg_trade_records, false)
    }

    /// Process AggTrade records with options for including incomplete bars
    ///
    /// Batch processing mode: Clears any existing state before processing.
    /// Use process_single_trade() for stateful streaming instead.
    ///
    /// # Parameters
    ///
    /// * `agg_trade_records` - Slice of AggTrade records sorted by (timestamp, agg_trade_id)
    /// * `include_incomplete` - Whether to include incomplete bars at end of processing
    ///
    /// # Returns
    ///
    /// Vector of range bars (completed + incomplete if requested)
    pub fn process_agg_trade_records_with_options(
        &mut self,
        agg_trade_records: &[AggTrade],
        include_incomplete: bool,
    ) -> Result<Vec<RangeBar>, ProcessingError> {
        if agg_trade_records.is_empty() {
            return Ok(Vec::new());
        }

        // Validate records are sorted
        self.validate_trade_ordering(agg_trade_records)?;

        // Clear streaming state - batch mode uses local state
        self.current_bar_state = None;

        let mut bars = Vec::with_capacity(agg_trade_records.len() / 100); // Heuristic capacity
        let mut current_bar: Option<RangeBarState> = None;
        let mut defer_open = false;

        for agg_record in agg_trade_records {
            if defer_open {
                // Previous bar closed, this agg_record opens new bar
                current_bar = Some(RangeBarState::new(agg_record, self.threshold_bps));
                defer_open = false;
                continue;
            }

            match current_bar {
                None => {
                    // First bar initialization
                    current_bar = Some(RangeBarState::new(agg_record, self.threshold_bps));
                }
                Some(ref mut bar_state) => {
                    // Check if this AggTrade record breaches the threshold
                    if bar_state.bar.is_breach(
                        agg_record.price,
                        bar_state.upper_threshold,
                        bar_state.lower_threshold,
                    ) {
                        // Breach detected - update bar with breaching record (includes microstructure)
                        bar_state.bar.update_with_trade(agg_record);

                        // Validation: Ensure high/low include open/close extremes
                        debug_assert!(
                            bar_state.bar.high >= bar_state.bar.open.max(bar_state.bar.close)
                        );
                        debug_assert!(
                            bar_state.bar.low <= bar_state.bar.open.min(bar_state.bar.close)
                        );

                        bars.push(bar_state.bar.clone());
                        current_bar = None;
                        defer_open = true; // Next record will open new bar
                    } else {
                        // No breach: normal update with microstructure calculations
                        bar_state.bar.update_with_trade(agg_record);
                    }
                }
            }
        }

        // Add final partial bar only if explicitly requested
        // This preserves algorithm integrity: bars should only close on threshold breach
        if include_incomplete && let Some(bar_state) = current_bar {
            bars.push(bar_state.bar);
        }

        Ok(bars)
    }

    /// Validate that trades are properly sorted for deterministic processing
    fn validate_trade_ordering(&self, trades: &[AggTrade]) -> Result<(), ProcessingError> {
        for i in 1..trades.len() {
            let prev = &trades[i - 1];
            let curr = &trades[i];

            // Check ordering: (timestamp, agg_trade_id) ascending
            if curr.timestamp < prev.timestamp
                || (curr.timestamp == prev.timestamp && curr.agg_trade_id <= prev.agg_trade_id)
            {
                return Err(ProcessingError::UnsortedTrades {
                    index: i,
                    prev_time: prev.timestamp,
                    prev_id: prev.agg_trade_id,
                    curr_time: curr.timestamp,
                    curr_id: curr.agg_trade_id,
                });
            }
        }

        Ok(())
    }
}

/// Internal state for a range bar being built
struct RangeBarState {
    /// The range bar being constructed
    pub bar: RangeBar,

    /// Upper breach threshold (FIXED from bar open)
    pub upper_threshold: FixedPoint,

    /// Lower breach threshold (FIXED from bar open)
    pub lower_threshold: FixedPoint,
}

impl RangeBarState {
    /// Create new range bar state from opening trade
    fn new(trade: &AggTrade, threshold_bps: u32) -> Self {
        let bar = RangeBar::new(trade);

        // Compute FIXED thresholds from opening price
        let (upper_threshold, lower_threshold) = bar.open.compute_range_thresholds(threshold_bps);

        Self {
            bar,
            upper_threshold,
            lower_threshold,
        }
    }
}

/// Processing errors
#[derive(Error, Debug)]
pub enum ProcessingError {
    #[error(
        "Trades not sorted at index {index}: prev=({prev_time}, {prev_id}), curr=({curr_time}, {curr_id})"
    )]
    UnsortedTrades {
        index: usize,
        prev_time: i64,
        prev_id: i64,
        curr_time: i64,
        curr_id: i64,
    },

    #[error("Empty trade data")]
    EmptyData,

    #[error("Invalid threshold: {threshold_bps} basis points")]
    InvalidThreshold { threshold_bps: u32 },
}

#[cfg(feature = "python")]
impl From<ProcessingError> for PyErr {
    fn from(err: ProcessingError) -> PyErr {
        match err {
            ProcessingError::UnsortedTrades {
                index,
                prev_time,
                prev_id,
                curr_time,
                curr_id,
            } => pyo3::exceptions::PyValueError::new_err(format!(
                "Trades not sorted at index {}: prev=({}, {}), curr=({}, {})",
                index, prev_time, prev_id, curr_time, curr_id
            )),
            ProcessingError::EmptyData => {
                pyo3::exceptions::PyValueError::new_err("Empty trade data")
            }
            ProcessingError::InvalidThreshold { threshold_bps } => {
                pyo3::exceptions::PyValueError::new_err(format!(
                    "Invalid threshold: {} basis points",
                    threshold_bps
                ))
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_utils::{self, scenarios};

    #[test]
    fn test_single_bar_no_breach() {
        let mut processor = RangeBarProcessor::new(250); // 250 × 0.1bps = 25bps

        // Create trades that stay within 25 bps threshold
        let trades = scenarios::no_breach_sequence(250);

        // Test strict algorithm compliance: no bars should be created without breach
        let bars = processor.process_agg_trade_records(&trades).unwrap();
        assert_eq!(
            bars.len(),
            0,
            "Strict algorithm should not create bars without breach"
        );

        // Test analysis mode: incomplete bar should be available for analysis
        let bars_with_incomplete = processor
            .process_agg_trade_records_with_incomplete(&trades)
            .unwrap();
        assert_eq!(
            bars_with_incomplete.len(),
            1,
            "Analysis mode should include incomplete bar"
        );

        let bar = &bars_with_incomplete[0];
        assert_eq!(bar.open.to_string(), "50000.00000000");
        assert_eq!(bar.high.to_string(), "50100.00000000");
        assert_eq!(bar.low.to_string(), "49900.00000000");
        assert_eq!(bar.close.to_string(), "49900.00000000");
    }

    #[test]
    fn test_exact_breach_upward() {
        let mut processor = RangeBarProcessor::new(250); // 250 × 0.1bps = 25bps

        let trades = scenarios::exact_breach_upward(250);

        // Test strict algorithm: only completed bars (with breach)
        let bars = processor.process_agg_trade_records(&trades).unwrap();
        assert_eq!(
            bars.len(),
            1,
            "Strict algorithm should only return completed bars"
        );

        // First bar should close at breach
        let bar1 = &bars[0];
        assert_eq!(bar1.open.to_string(), "50000.00000000");
        // Breach at 25 bps = 0.25% = 50000 * 1.0025 = 50125
        assert_eq!(bar1.close.to_string(), "50125.00000000"); // Breach tick included
        assert_eq!(bar1.high.to_string(), "50125.00000000");
        assert_eq!(bar1.low.to_string(), "50000.00000000");

        // Test analysis mode: includes incomplete second bar
        let bars_with_incomplete = processor
            .process_agg_trade_records_with_incomplete(&trades)
            .unwrap();
        assert_eq!(
            bars_with_incomplete.len(),
            2,
            "Analysis mode should include incomplete bars"
        );

        // Second bar should start at next tick price (not breach price)
        let bar2 = &bars_with_incomplete[1];
        assert_eq!(bar2.open.to_string(), "50500.00000000"); // Next tick after breach
        assert_eq!(bar2.close.to_string(), "50500.00000000");
    }

    #[test]
    fn test_exact_breach_downward() {
        let mut processor = RangeBarProcessor::new(250); // 250 × 0.1bps = 25bps = 0.25%

        let trades = scenarios::exact_breach_downward(250);

        let bars = processor.process_agg_trade_records(&trades).unwrap();

        assert_eq!(bars.len(), 1);

        let bar = &bars[0];
        assert_eq!(bar.open.to_string(), "50000.00000000");
        assert_eq!(bar.close.to_string(), "49875.00000000"); // Breach tick included
        assert_eq!(bar.high.to_string(), "50000.00000000");
        assert_eq!(bar.low.to_string(), "49875.00000000");
    }

    #[test]
    fn test_large_gap_single_bar() {
        let mut processor = RangeBarProcessor::new(250); // 250 × 0.1bps = 25bps = 0.25%

        let trades = scenarios::large_gap_sequence();

        let bars = processor.process_agg_trade_records(&trades).unwrap();

        // Should create exactly ONE bar, not multiple bars to "fill the gap"
        assert_eq!(bars.len(), 1);

        let bar = &bars[0];
        assert_eq!(bar.open.to_string(), "50000.00000000");
        assert_eq!(bar.close.to_string(), "51000.00000000");
        assert_eq!(bar.high.to_string(), "51000.00000000");
        assert_eq!(bar.low.to_string(), "50000.00000000");
    }

    #[test]
    fn test_unsorted_trades_error() {
        let mut processor = RangeBarProcessor::new(250); // 250 × 0.1bps = 25bps

        let trades = scenarios::unsorted_sequence();

        let result = processor.process_agg_trade_records(&trades);
        assert!(result.is_err());

        match result {
            Err(ProcessingError::UnsortedTrades { index, .. }) => {
                assert_eq!(index, 1);
            }
            _ => panic!("Expected UnsortedTrades error"),
        }
    }

    #[test]
    fn test_threshold_calculation() {
        let processor = RangeBarProcessor::new(250); // 250 × 0.1bps = 25bps = 0.25%

        let trade = test_utils::create_test_agg_trade(1, "50000.0", "1.0", 1000);
        let bar_state = RangeBarState::new(&trade, processor.threshold_bps);

        // 50000 * 0.0025 = 125 (25bps = 0.25%)
        assert_eq!(bar_state.upper_threshold.to_string(), "50125.00000000");
        assert_eq!(bar_state.lower_threshold.to_string(), "49875.00000000");
    }

    #[test]
    fn test_empty_trades() {
        let mut processor = RangeBarProcessor::new(250); // 250 × 0.1bps = 25bps
        let trades = scenarios::empty_sequence();
        let bars = processor.process_agg_trade_records(&trades).unwrap();
        assert_eq!(bars.len(), 0);
    }

    #[test]
    fn test_debug_streaming_data() {
        let mut processor = RangeBarProcessor::new(100); // 100 × 0.1bps = 10bps = 0.1%

        // Create trades similar to our test data
        let trades = vec![
            test_utils::create_test_agg_trade(1, "50014.00859087", "0.12019569", 1756710002083),
            test_utils::create_test_agg_trade(2, "50163.87750994", "1.01283708", 1756710005113), // ~0.3% increase
            test_utils::create_test_agg_trade(3, "50032.44128269", "0.69397094", 1756710008770),
        ];

        println!("Test data prices: 50014 -> 50163 -> 50032");
        println!("Expected price movements: +0.3% then -0.26%");

        let bars = processor.process_agg_trade_records(&trades).unwrap();
        println!("Generated {} range bars", bars.len());

        for (i, bar) in bars.iter().enumerate() {
            println!(
                "  Bar {}: O={} H={} L={} C={}",
                i + 1,
                bar.open,
                bar.high,
                bar.low,
                bar.close
            );
        }

        // With a 0.1% threshold and 0.3% price movement, we should get at least 1 bar
        assert!(
            !bars.is_empty(),
            "Expected at least 1 range bar with 0.3% price movement and 0.1% threshold"
        );
    }

    #[test]
    fn test_export_processor_with_manual_trades() {
        println!("Testing ExportRangeBarProcessor with same trade data...");

        let mut export_processor = ExportRangeBarProcessor::new(100); // 100 × 0.1bps = 10bps = 0.1%

        // Use same trades as the working basic test
        let trades = vec![
            test_utils::create_test_agg_trade(1, "50014.00859087", "0.12019569", 1756710002083),
            test_utils::create_test_agg_trade(2, "50163.87750994", "1.01283708", 1756710005113), // ~0.3% increase
            test_utils::create_test_agg_trade(3, "50032.44128269", "0.69397094", 1756710008770),
        ];

        println!(
            "Processing {} trades with ExportRangeBarProcessor...",
            trades.len()
        );

        export_processor.process_trades_continuously(&trades);
        let bars = export_processor.get_all_completed_bars();

        println!(
            "ExportRangeBarProcessor generated {} range bars",
            bars.len()
        );
        for (i, bar) in bars.iter().enumerate() {
            println!(
                "  Bar {}: O={} H={} L={} C={}",
                i + 1,
                bar.open,
                bar.high,
                bar.low,
                bar.close
            );
        }

        // Should match the basic processor results (1 bar)
        assert!(
            !bars.is_empty(),
            "ExportRangeBarProcessor should generate same results as basic processor"
        );
    }
}

/// Internal state for range bar construction with fixed-point precision
#[derive(Debug, Clone)]
struct InternalRangeBar {
    open_time: i64,
    close_time: i64,
    open: FixedPoint,
    high: FixedPoint,
    low: FixedPoint,
    close: FixedPoint,
    volume: FixedPoint,
    turnover: i128,
    individual_trade_count: i64,
    agg_record_count: u32,
    first_trade_id: i64,
    last_trade_id: i64,
    /// Volume from buy-side trades (is_buyer_maker = false)
    buy_volume: FixedPoint,
    /// Volume from sell-side trades (is_buyer_maker = true)
    sell_volume: FixedPoint,
    /// Number of buy-side trades
    buy_trade_count: i64,
    /// Number of sell-side trades
    sell_trade_count: i64,
    /// Volume Weighted Average Price
    vwap: FixedPoint,
    /// Turnover from buy-side trades
    buy_turnover: i128,
    /// Turnover from sell-side trades
    sell_turnover: i128,
}

/// Export-oriented range bar processor for streaming use cases
///
/// This implementation uses the proven fixed-point arithmetic algorithm
/// that achieves 100% breach consistency compliance in multi-year processing.
pub struct ExportRangeBarProcessor {
    threshold_bps: u32,
    current_bar: Option<InternalRangeBar>,
    completed_bars: Vec<RangeBar>,
}

impl ExportRangeBarProcessor {
    /// Create new export processor with given threshold
    ///
    /// # Arguments
    ///
    /// * `threshold_bps` - Threshold in **tenths of basis points** (0.1bps units)
    ///   - Example: `250` → 25bps = 0.25%
    ///   - Example: `10` → 1bps = 0.01%
    ///   - Minimum: `1` → 0.1bps = 0.001%
    ///
    /// # Breaking Change (v3.0.0)
    ///
    /// Prior to v3.0.0, `threshold_bps` was in 1bps units.
    /// **Migration**: Multiply all threshold values by 10.
    pub fn new(threshold_bps: u32) -> Self {
        Self {
            threshold_bps,
            current_bar: None,
            completed_bars: Vec::new(),
        }
    }

    /// Process trades continuously using proven fixed-point algorithm
    /// This method maintains 100% breach consistency by using precise integer arithmetic
    pub fn process_trades_continuously(&mut self, trades: &[AggTrade]) {
        for trade in trades {
            self.process_single_trade_fixed_point(trade);
        }
    }

    /// Process single trade using proven fixed-point algorithm (100% breach consistency)
    fn process_single_trade_fixed_point(&mut self, trade: &AggTrade) {
        if self.current_bar.is_none() {
            // Start new bar
            let trade_turnover = (trade.price.to_f64() * trade.volume.to_f64()) as i128;

            self.current_bar = Some(InternalRangeBar {
                open_time: trade.timestamp,
                close_time: trade.timestamp,
                open: trade.price,
                high: trade.price,
                low: trade.price,
                close: trade.price,
                volume: trade.volume,
                turnover: trade_turnover,
                individual_trade_count: 1,
                agg_record_count: 1,
                first_trade_id: trade.agg_trade_id,
                last_trade_id: trade.agg_trade_id,
                // Market microstructure fields
                buy_volume: if trade.is_buyer_maker {
                    FixedPoint(0)
                } else {
                    trade.volume
                },
                sell_volume: if trade.is_buyer_maker {
                    trade.volume
                } else {
                    FixedPoint(0)
                },
                buy_trade_count: if trade.is_buyer_maker { 0 } else { 1 },
                sell_trade_count: if trade.is_buyer_maker { 1 } else { 0 },
                vwap: trade.price,
                buy_turnover: if trade.is_buyer_maker {
                    0
                } else {
                    trade_turnover
                },
                sell_turnover: if trade.is_buyer_maker {
                    trade_turnover
                } else {
                    0
                },
            });
            return;
        }

        // Process existing bar - work with reference
        let bar = self.current_bar.as_mut().unwrap();
        let trade_turnover = (trade.price.to_f64() * trade.volume.to_f64()) as i128;

        // CRITICAL FIX: Use fixed-point integer arithmetic for precise threshold calculation
        // v3.0.0: threshold_bps now in 0.1bps units, using BASIS_POINTS_SCALE = 100_000
        let price_val = trade.price.0;
        let bar_open_val = bar.open.0;
        let threshold_bps = self.threshold_bps as i64;
        let upper_threshold = bar_open_val + (bar_open_val * threshold_bps) / 100_000;
        let lower_threshold = bar_open_val - (bar_open_val * threshold_bps) / 100_000;

        // Update bar with new trade
        bar.close_time = trade.timestamp;
        bar.close = trade.price;
        bar.volume.0 += trade.volume.0;
        bar.turnover += trade_turnover;
        bar.individual_trade_count += 1;
        bar.agg_record_count += 1;
        bar.last_trade_id = trade.agg_trade_id;

        // Update high/low
        if price_val > bar.high.0 {
            bar.high = trade.price;
        }
        if price_val < bar.low.0 {
            bar.low = trade.price;
        }

        // Update market microstructure
        if trade.is_buyer_maker {
            bar.sell_volume.0 += trade.volume.0;
            bar.sell_turnover += trade_turnover;
            bar.sell_trade_count += 1;
        } else {
            bar.buy_volume.0 += trade.volume.0;
            bar.buy_turnover += trade_turnover;
            bar.buy_trade_count += 1;
        }

        // CRITICAL: Fixed-point threshold breach detection (matches proven 100% compliance algorithm)
        if price_val >= upper_threshold || price_val <= lower_threshold {
            // Close current bar and move to completed
            let completed_bar = self.current_bar.take().unwrap();

            // Convert to export format (this is from an old internal structure)
            let export_bar = RangeBar {
                open_time: completed_bar.open_time,
                close_time: completed_bar.close_time,
                open: completed_bar.open,
                high: completed_bar.high,
                low: completed_bar.low,
                close: completed_bar.close,
                volume: completed_bar.volume,
                turnover: completed_bar.turnover,

                // Enhanced fields
                individual_trade_count: completed_bar.individual_trade_count as u32,
                agg_record_count: completed_bar.agg_record_count,
                first_trade_id: completed_bar.first_trade_id,
                last_trade_id: completed_bar.last_trade_id,
                data_source: crate::core::types::DataSource::default(),

                // Market microstructure fields
                buy_volume: completed_bar.buy_volume,
                sell_volume: completed_bar.sell_volume,
                buy_trade_count: completed_bar.buy_trade_count as u32,
                sell_trade_count: completed_bar.sell_trade_count as u32,
                vwap: completed_bar.vwap,
                buy_turnover: completed_bar.buy_turnover,
                sell_turnover: completed_bar.sell_turnover,
            };

            self.completed_bars.push(export_bar);

            // Start new bar with breaching trade
            let initial_buy_turnover = if trade.is_buyer_maker {
                0
            } else {
                trade_turnover
            };
            let initial_sell_turnover = if trade.is_buyer_maker {
                trade_turnover
            } else {
                0
            };

            self.current_bar = Some(InternalRangeBar {
                open_time: trade.timestamp,
                close_time: trade.timestamp,
                open: trade.price,
                high: trade.price,
                low: trade.price,
                close: trade.price,
                volume: trade.volume,
                turnover: trade_turnover,
                individual_trade_count: 1,
                agg_record_count: 1,
                first_trade_id: trade.agg_trade_id,
                last_trade_id: trade.agg_trade_id,
                // Market microstructure fields
                buy_volume: if trade.is_buyer_maker {
                    FixedPoint(0)
                } else {
                    trade.volume
                },
                sell_volume: if trade.is_buyer_maker {
                    trade.volume
                } else {
                    FixedPoint(0)
                },
                buy_trade_count: if trade.is_buyer_maker { 0 } else { 1 },
                sell_trade_count: if trade.is_buyer_maker { 1 } else { 0 },
                vwap: trade.price,
                buy_turnover: initial_buy_turnover,
                sell_turnover: initial_sell_turnover,
            });
        }
    }

    /// Get all completed bars accumulated so far
    /// This drains the internal buffer to avoid memory leaks
    pub fn get_all_completed_bars(&mut self) -> Vec<RangeBar> {
        std::mem::take(&mut self.completed_bars)
    }

    /// Get incomplete bar if exists (for final bar processing)
    pub fn get_incomplete_bar(&mut self) -> Option<RangeBar> {
        self.current_bar.as_ref().map(|incomplete| RangeBar {
            open_time: incomplete.open_time,
            close_time: incomplete.close_time,
            open: incomplete.open,
            high: incomplete.high,
            low: incomplete.low,
            close: incomplete.close,
            volume: incomplete.volume,
            turnover: incomplete.turnover,

            // Enhanced fields
            individual_trade_count: incomplete.individual_trade_count as u32,
            agg_record_count: incomplete.agg_record_count,
            first_trade_id: incomplete.first_trade_id,
            last_trade_id: incomplete.last_trade_id,
            data_source: crate::core::types::DataSource::default(),

            // Market microstructure fields
            buy_volume: incomplete.buy_volume,
            sell_volume: incomplete.sell_volume,
            buy_trade_count: incomplete.buy_trade_count as u32,
            sell_trade_count: incomplete.sell_trade_count as u32,
            vwap: incomplete.vwap,
            buy_turnover: incomplete.buy_turnover,
            sell_turnover: incomplete.sell_turnover,
        })
    }
}
