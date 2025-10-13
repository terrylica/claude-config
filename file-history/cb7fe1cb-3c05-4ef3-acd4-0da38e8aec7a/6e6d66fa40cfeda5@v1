//! Dukascopy HTTP client and instrument configuration
//!
//! Fetches LZMA-compressed binary tick data and provides instrument metadata.
//!
//! # Binary Format (.bi5)
//!
//! Each tick is 20 bytes (big-endian):
//! - Time offset (4 bytes, i32): milliseconds since hour start
//! - Ask price (4 bytes, i32): integer price * decimal_factor
//! - Bid price (4 bytes, i32): integer price * decimal_factor
//! - Ask volume (4 bytes, f32): available liquidity at ask
//! - Bid volume (4 bytes, f32): available liquidity at bid

use super::types::{ConversionError, DukascopyTick, InstrumentType};
use byteorder::{BigEndian, ReadBytesExt};
use lzma_rs::lzma_decompress;
use once_cell::sync::Lazy;
use reqwest::Client;
use serde::Deserialize;
use std::collections::HashMap;
use std::io::Cursor;
use std::time::Duration;

/// Embedded instrument configuration TOML (Q15)
///
/// Path: docs/planning/research/dukascopy-instrument-config.toml
/// Contains 1,607 instruments with decimal factors across asset classes.
const INSTRUMENT_CONFIG_TOML: &str = include_str!(
    "../../../docs/planning/research/dukascopy-instrument-config.toml"
);

/// Parsed instrument configuration (lazy static)
static INSTRUMENT_CONFIG: Lazy<InstrumentConfigRoot> = Lazy::new(|| {
    toml::from_str(INSTRUMENT_CONFIG_TOML)
        .expect("Failed to parse embedded instrument config TOML")
});

/// Root configuration structure
#[derive(Deserialize)]
struct InstrumentConfigRoot {
    instruments: InstrumentsRoot,
}

/// Top-level instrument categories
#[derive(Deserialize)]
struct InstrumentsRoot {
    #[serde(default)]
    forex: HashMap<String, HashMap<String, InstrumentEntry>>,

    #[serde(default)]
    crypto: HashMap<String, HashMap<String, InstrumentEntry>>,

    #[serde(default)]
    commodities: HashMap<String, HashMap<String, InstrumentEntry>>,

    #[serde(default)]
    equities: HashMap<String, HashMap<String, InstrumentEntry>>,
}

/// Individual instrument entry
#[derive(Deserialize)]
struct InstrumentEntry {
    decimal_factor: f64,
    // Other fields ignored (name, description, etc.)
}

/// Get instrument decimal factor and inferred type (Q20)
///
/// Single lookup provides both values needed for conversion and validation.
/// Type inference from config path structure eliminates manual edits (Q20).
///
/// # Arguments
///
/// * `instrument` - Instrument symbol (e.g., "EURUSD", "BTCUSD")
///
/// # Returns
///
/// Tuple of (decimal_factor, instrument_type) or error if unsupported
///
/// # Examples
///
/// ```
/// use rangebar::providers::dukascopy::client::get_instrument_info;
/// use rangebar::providers::dukascopy::types::InstrumentType;
///
/// let (factor, typ) = get_instrument_info("EURUSD").unwrap();
/// assert_eq!(factor, 100000);
/// assert_eq!(typ, InstrumentType::Forex);
/// ```
pub fn get_instrument_info(instrument: &str) -> Result<(u32, InstrumentType), ConversionError> {
    // Check forex (nested structure: forex.{subcategory}.{symbol})
    for subcategory in INSTRUMENT_CONFIG.instruments.forex.values() {
        if let Some(entry) = subcategory.get(instrument) {
            return Ok((entry.decimal_factor as u32, InstrumentType::Forex));
        }
    }

    // Check crypto (nested structure: crypto.{subcategory}.{symbol})
    for subcategory in INSTRUMENT_CONFIG.instruments.crypto.values() {
        if let Some(entry) = subcategory.get(instrument) {
            return Ok((entry.decimal_factor as u32, InstrumentType::Crypto));
        }
    }

    // Check commodities (nested structure)
    for subcategory in INSTRUMENT_CONFIG.instruments.commodities.values() {
        if let Some(entry) = subcategory.get(instrument) {
            return Ok((entry.decimal_factor as u32, InstrumentType::Commodity));
        }
    }

    // Check equities (nested structure)
    for subcategory in INSTRUMENT_CONFIG.instruments.equities.values() {
        if let Some(entry) = subcategory.get(instrument) {
            return Ok((entry.decimal_factor as u32, InstrumentType::Equity));
        }
    }

    Err(ConversionError::UnsupportedInstrument {
        instrument: instrument.to_string(),
    })
}

/// Dukascopy HTTP data fetcher
pub struct DukascopyFetcher {
    client: Client,
    instrument: String,
}

impl DukascopyFetcher {
    /// Create new fetcher for instrument
    ///
    /// # Timeout Configuration
    ///
    /// Dukascopy-specific timeout values based on empirical measurements:
    /// - Request timeout: 120s (2.8x safety margin over 42.5s observed max)
    /// - Connect timeout: 30s (separate connection establishment limit)
    ///
    /// Reference: docs/planning/dukascopy-timeout-retry-strategy.md
    pub fn new(instrument: &str) -> Self {
        // Dukascopy server characteristics (empirical data):
        // - Response time: 15-45s typical, 42.5s max observed
        // - Rate limit: Requires 2s spacing between requests
        // - Timeout: 120s total, 30s connection (2.8x safety margin)
        const DUKASCOPY_REQUEST_TIMEOUT_SECS: u64 = 120;
        const DUKASCOPY_CONNECT_TIMEOUT_SECS: u64 = 30;

        Self {
            client: Client::builder()
                .timeout(Duration::from_secs(DUKASCOPY_REQUEST_TIMEOUT_SECS))
                .connect_timeout(Duration::from_secs(DUKASCOPY_CONNECT_TIMEOUT_SECS))
                .build()
                .expect("Failed to build Dukascopy HTTP client with timeout configuration"),
            instrument: instrument.to_uppercase(),
        }
    }

    /// Fetch and parse ticks for specific hour
    ///
    /// # Arguments
    ///
    /// * `year` - Year (e.g., 2025)
    /// * `month` - Month (1-12)
    /// * `day` - Day (1-31)
    /// * `hour` - Hour (0-23)
    ///
    /// # Returns
    ///
    /// Vector of parsed DukascopyTick or error
    ///
    /// # Example
    ///
    /// ```rust,no_run
    /// use rangebar::providers::dukascopy::client::DukascopyFetcher;
    ///
    /// # async fn example() -> Result<(), Box<dyn std::error::Error>> {
    /// let fetcher = DukascopyFetcher::new("EURUSD");
    /// let ticks = fetcher.fetch_hour(2025, 1, 15, 10).await?;
    /// println!("Fetched {} ticks", ticks.len());
    /// # Ok(())
    /// # }
    /// ```
    pub async fn fetch_hour(
        &self,
        year: u32,
        month: u32,
        day: u32,
        hour: u32,
    ) -> Result<Vec<DukascopyTick>, Box<dyn std::error::Error>> {
        // Construct URL
        let url = format!(
            "https://datafeed.dukascopy.com/datafeed/{}/{}/{:02}/{:02}/{:02}h_ticks.bi5",
            self.instrument,
            year,
            month.saturating_sub(1), // Dukascopy uses 0-indexed months
            day,
            hour
        );

        // Download .bi5 file
        let response = self.client.get(&url).send().await?;

        if !response.status().is_success() {
            return Err(format!("HTTP {} for {}", response.status(), url).into());
        }

        let compressed_bytes = response.bytes().await?;

        // Decompress raw LZMA format
        let mut decompressed = Vec::new();
        lzma_decompress(&mut Cursor::new(compressed_bytes.as_ref()), &mut decompressed)?;

        // Parse binary ticks
        let (decimal_factor, _instrument_type) = get_instrument_info(&self.instrument)?;
        let base_timestamp = Self::hour_start_timestamp_ms(year, month, day, hour);

        self.parse_ticks(&decompressed, decimal_factor, base_timestamp)
    }

    /// Parse binary tick data
    fn parse_ticks(
        &self,
        data: &[u8],
        decimal_factor: u32,
        base_timestamp_ms: i64,
    ) -> Result<Vec<DukascopyTick>, Box<dyn std::error::Error>> {
        let mut cursor = Cursor::new(data);
        let mut ticks = Vec::new();

        while cursor.position() < data.len() as u64 {
            // Check if we have enough bytes for a full tick (20 bytes)
            if data.len() as u64 - cursor.position() < 20 {
                break;
            }

            // Parse 20-byte tick structure (big-endian)
            let time_offset_ms = cursor.read_i32::<BigEndian>()?;
            let ask_price_int = cursor.read_i32::<BigEndian>()?;
            let bid_price_int = cursor.read_i32::<BigEndian>()?;
            let ask_volume = cursor.read_f32::<BigEndian>()?;
            let bid_volume = cursor.read_f32::<BigEndian>()?;

            // Convert integer prices to f64 using decimal_factor
            let ask = ask_price_int as f64 / decimal_factor as f64;
            let bid = bid_price_int as f64 / decimal_factor as f64;

            // Calculate absolute timestamp
            let timestamp_ms = base_timestamp_ms + time_offset_ms as i64;

            ticks.push(DukascopyTick {
                ask,
                bid,
                ask_volume,
                bid_volume,
                timestamp_ms,
            });
        }

        Ok(ticks)
    }

    /// Calculate hour start timestamp in milliseconds
    fn hour_start_timestamp_ms(year: u32, month: u32, day: u32, hour: u32) -> i64 {
        use chrono::{NaiveDate, NaiveDateTime, NaiveTime};

        let date = NaiveDate::from_ymd_opt(year as i32, month, day)
            .expect("Invalid date");
        let time = NaiveTime::from_hms_opt(hour, 0, 0).expect("Invalid hour");
        let datetime = NaiveDateTime::new(date, time);

        datetime.and_utc().timestamp_millis()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_forex_instrument_lookup() {
        let (factor, typ) = get_instrument_info("EURUSD").unwrap();
        assert_eq!(factor, 100000);
        assert_eq!(typ, InstrumentType::Forex);
    }

    #[test]
    fn test_unsupported_instrument() {
        let result = get_instrument_info("NONEXISTENT");
        assert!(result.is_err());
        match result {
            Err(ConversionError::UnsupportedInstrument { instrument }) => {
                assert_eq!(instrument, "NONEXISTENT");
            }
            _ => panic!("Expected UnsupportedInstrument error"),
        }
    }

    #[test]
    fn test_type_specific_price_ranges() {
        // Forex: narrow range (Q18)
        let (min, max) = InstrumentType::Forex.price_range();
        assert_eq!(min, 0.01);
        assert_eq!(max, 10_000.0);

        // Crypto: wide range
        let (min, max) = InstrumentType::Crypto.price_range();
        assert_eq!(min, 0.0001);
        assert_eq!(max, 1_000_000.0);
    }

    #[test]
    fn test_hour_start_timestamp() {
        // 2025-01-15 10:00:00 GMT
        let timestamp = DukascopyFetcher::hour_start_timestamp_ms(2025, 1, 15, 10);

        // Expected: 1736935200000 (2025-01-15 10:00:00 UTC in ms)
        assert_eq!(timestamp, 1736935200000);
    }

    #[test]
    fn test_parse_ticks_empty() {
        let fetcher = DukascopyFetcher::new("EURUSD");
        let ticks = fetcher.parse_ticks(&[], 100000, 1736935200000).unwrap();
        assert_eq!(ticks.len(), 0);
    }
}
