//! Tick validation and conversion to synthetic aggTrades
//!
//! Converts Dukascopy ticks (quote data) to AggTrade format (trade data)
//! using mid-price as synthetic trade price. Preserves range bar algorithm
//! integrity while handling semantic differences between quotes and trades.

use crate::core::fixed_point::FixedPoint;
use crate::core::timestamp::normalize_timestamp;
use crate::core::types::AggTrade;
use crate::providers::dukascopy::client::get_instrument_info;
use crate::providers::dukascopy::types::{
    ConversionError, DukascopyTick, InstrumentType, ValidationStrictness,
};

/// Validate tick data (Q12)
///
/// Validation levels (configurable strictness):
/// - Permissive: Basic checks (bid > 0, ask > 0, bid < ask)
/// - Strict: + Spread < 10% (catches obvious errors) [DEFAULT]
/// - Paranoid: + Spread < 1% (flags suspicious patterns)
///
/// # Arguments
///
/// * `tick` - Dukascopy tick to validate
/// * `strictness` - Validation level
///
/// # Returns
///
/// Ok(()) if valid, Err with specific validation failure otherwise
///
/// # Error Recovery (Q22)
///
/// Validation errors are SKIP-type (log + continue, not fatal).
/// Caller should track error rate and abort if >10% errors detected.
pub fn validate_tick(
    tick: &DukascopyTick,
    strictness: ValidationStrictness,
) -> Result<(), ConversionError> {
    // Critical checks (all levels)
    if tick.bid <= 0.0 {
        return Err(ConversionError::InvalidBid { bid: tick.bid });
    }

    if tick.ask <= 0.0 {
        return Err(ConversionError::InvalidAsk { ask: tick.ask });
    }

    if tick.bid >= tick.ask {
        return Err(ConversionError::CrossedMarket {
            bid: tick.bid,
            ask: tick.ask,
        });
    }

    // Strictness-dependent checks
    match strictness {
        ValidationStrictness::Permissive => Ok(()),

        ValidationStrictness::Strict => {
            let spread_pct = ((tick.ask - tick.bid) / tick.bid) * 100.0;
            if spread_pct > 10.0 {
                return Err(ConversionError::ExcessiveSpread {
                    spread_pct,
                    threshold_pct: 10.0,
                });
            }
            Ok(())
        }

        ValidationStrictness::Paranoid => {
            let spread_pct = ((tick.ask - tick.bid) / tick.bid) * 100.0;
            if spread_pct > 1.0 {
                return Err(ConversionError::SuspiciousSpread {
                    spread_pct,
                    threshold_pct: 1.0,
                });
            }
            Ok(())
        }
    }
}

/// Validate original price against instrument type range (Q18)
///
/// Type-specific ranges catch unrealistic market prices:
/// - Forex: 0.01 - 10,000 (narrow, all major pairs fit)
/// - Crypto: 0.0001 - 1,000,000 (wide, SHIB to BTC)
/// - Commodity: 0.01 - 100,000
/// - Equity: 0.01 - 100,000
///
/// # Arguments
///
/// * `price` - Original price BEFORE decimal factor conversion
/// * `instrument_type` - Asset class for range validation
///
/// # Returns
///
/// Ok(()) if price is within expected range, Err otherwise
pub fn validate_price(
    price: f64,
    instrument_type: InstrumentType,
) -> Result<(), ConversionError> {
    let (min, max) = instrument_type.price_range();

    if price < min || price > max {
        return Err(ConversionError::InvalidPriceRange {
            price,
            instrument_type,
            min,
            max,
        });
    }

    Ok(())
}

/// Convert Dukascopy tick to synthetic AggTrade
///
/// Mid-price conversion (academic standard):
/// - price = (bid + ask) / 2.0
/// - volume = bid_volume + ask_volume (could be 0.0, Q14)
/// - is_buyer_maker = false (direction unknown for quotes, Q10)
///
/// # Arguments
///
/// * `tick` - Dukascopy tick (quote data)
/// * `instrument` - Instrument symbol for config lookup
/// * `id` - Synthetic aggTrade ID
/// * `strictness` - Validation level
///
/// # Returns
///
/// AggTrade with mid-price as trade price, or validation error
///
/// # Error Handling
///
/// Raises errors immediately (no fallbacks, no defaults per requirement).
/// - Config errors (UnsupportedInstrument): FATAL → abort
/// - Validation errors (CrossedMarket, etc.): SKIP → log + continue
pub fn tick_to_synthetic_trade(
    tick: &DukascopyTick,
    instrument: &str,
    id: i64,
    strictness: ValidationStrictness,
) -> Result<AggTrade, ConversionError> {
    // 1. Validate tick (raise on error)
    validate_tick(tick, strictness)?;

    // 2. Get instrument type for validation (raise if unsupported)
    let (_decimal_factor, instrument_type) = get_instrument_info(instrument)?;

    // 3. Calculate mid-price (market consensus price)
    let mid_price = (tick.ask + tick.bid) / 2.0;

    // 4. Validate mid-price is reasonable for instrument type (raise on error)
    validate_price(mid_price, instrument_type)?;

    // 5. Aggregate liquidity (NOT traded volume, could be 0.0)
    let total_liquidity = (tick.ask_volume + tick.bid_volume) as f64;

    // 6. Direction UNKNOWN for quote data (no buy/sell inference, Q10)
    let is_buyer_maker = false; // Arbitrary default (not used for segregation)

    // 7. Construct synthetic AggTrade
    // Note: DukascopyTick prices are already in real format (f64), not integer-encoded.
    // decimal_factor is only needed when parsing raw .bi5 binary format.
    //
    // Format f64 with 8 decimals to match FixedPoint precision and avoid parse errors
    let price_str = format!("{:.8}", mid_price);
    let volume_str = format!("{:.8}", total_liquidity);

    Ok(AggTrade {
        agg_trade_id: id,
        price: FixedPoint::from_str(&price_str)
            .map_err(|e| ConversionError::FixedPointConversion {
                value: price_str.clone(),
                error: format!("{:?}", e)
            })?,
        volume: FixedPoint::from_str(&volume_str)
            .map_err(|e| ConversionError::FixedPointConversion {
                value: volume_str.clone(),
                error: format!("{:?}", e)
            })?,
        first_trade_id: id,
        last_trade_id: id,
        timestamp: normalize_timestamp(tick.timestamp_ms as u64),
        is_buyer_maker,
        is_best_match: None, // N/A for Dukascopy
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_tick_crossed_market() {
        let tick = DukascopyTick {
            bid: 1.0815,
            ask: 1.0800, // bid > ask (crossed)
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1000000,
        };

        let result = validate_tick(&tick, ValidationStrictness::Permissive);
        assert!(result.is_err());
        match result {
            Err(ConversionError::CrossedMarket { bid, ask }) => {
                assert_eq!(bid, 1.0815);
                assert_eq!(ask, 1.0800);
            }
            _ => panic!("Expected CrossedMarket error"),
        }
    }

    #[test]
    fn test_validate_tick_excessive_spread() {
        let tick = DukascopyTick {
            bid: 1.0000,
            ask: 1.2000, // 20% spread
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1000000,
        };

        // Permissive: passes
        assert!(validate_tick(&tick, ValidationStrictness::Permissive).is_ok());

        // Strict: fails (>10%)
        let result = validate_tick(&tick, ValidationStrictness::Strict);
        assert!(result.is_err());
        match result {
            Err(ConversionError::ExcessiveSpread { spread_pct, .. }) => {
                assert!((spread_pct - 20.0).abs() < 0.01);
            }
            _ => panic!("Expected ExcessiveSpread error"),
        }
    }

    #[test]
    fn test_mid_price_conversion() {
        let tick = DukascopyTick {
            bid: 1.0800,
            ask: 1.0820,
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1_600_000_000_000, // ms
        };

        let trade = tick_to_synthetic_trade(
            &tick,
            "EURUSD",
            1,
            ValidationStrictness::Strict,
        )
        .unwrap();

        // Mid-price = (1.0800 + 1.0820) / 2 = 1.0810
        // Note: DukascopyTick prices are in real format (f64), not multiplied by decimal_factor
        let expected_price = 1.0810;
        assert!((trade.price.to_f64() - expected_price).abs() < 0.0001);

        // Volume = 100 + 120 = 220
        assert!((trade.volume.to_f64() - 220.0).abs() < 1.0);

        // Direction unknown
        assert!(!trade.is_buyer_maker);

        // Timestamp normalized to microseconds
        assert_eq!(trade.timestamp, 1_600_000_000_000_000);
    }

    #[test]
    fn test_zero_volume_handling() {
        let tick = DukascopyTick {
            bid: 1.0800,
            ask: 1.0815,
            bid_volume: 0.0, // Zero volume (Q7, Q14)
            ask_volume: 0.0,
            timestamp_ms: 1_600_000_000_000,
        };

        let trade = tick_to_synthetic_trade(
            &tick,
            "EURUSD",
            1,
            ValidationStrictness::Strict,
        )
        .unwrap();

        // Volume should be 0 (actual value, no fabrication)
        assert_eq!(trade.volume.0, 0);
    }

    #[test]
    fn test_unsupported_instrument() {
        let tick = DukascopyTick {
            bid: 1.0800,
            ask: 1.0815,
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1_600_000_000_000,
        };

        let result = tick_to_synthetic_trade(
            &tick,
            "NONEXISTENT",
            1,
            ValidationStrictness::Strict,
        );

        assert!(result.is_err());
        match result {
            Err(ConversionError::UnsupportedInstrument { instrument }) => {
                assert_eq!(instrument, "NONEXISTENT");
            }
            _ => panic!("Expected UnsupportedInstrument error"),
        }
    }
}
