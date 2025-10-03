//! Dukascopy tick data fetcher and .bi5 binary format parser
//!
//! Downloads LZMA-compressed binary tick data from Dukascopy HTTP endpoints
//! and parses the 20-byte tick format.
//!
//! # Binary Format (.bi5)
//!
//! Each tick is 20 bytes (big-endian):
//! - Time offset (4 bytes, i32): milliseconds since hour start
//! - Ask price (4 bytes, i32): integer price * decimal_factor
//! - Bid price (4 bytes, i32): integer price * decimal_factor
//! - Ask volume (4 bytes, f32): available liquidity at ask
//! - Bid volume (4 bytes, f32): available liquidity at bid

use crate::data::dukascopy::config::get_instrument_info;
use crate::data::dukascopy::types::DukascopyTick;
use byteorder::{BigEndian, ReadBytesExt};
use lzma_rs::lzma_decompress;
use reqwest::Client;
use std::io::Cursor;

/// Dukascopy HTTP data fetcher
pub struct DukascopyFetcher {
    client: Client,
    instrument: String,
}

impl DukascopyFetcher {
    /// Create new fetcher for instrument
    pub fn new(instrument: &str) -> Self {
        Self {
            client: Client::new(),
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
    /// use rangebar::data::dukascopy::fetcher::DukascopyFetcher;
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
