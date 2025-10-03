//! Integration test with real Dukascopy data
//!
//! Tests the complete end-to-end flow:
//! 1. Fetch real tick data from Dukascopy HTTP endpoints
//! 2. Parse .bi5 binary format
//! 3. Construct range bars
//!
//! NOTE: This test requires internet connectivity and will fail if:
//! - Dukascopy servers are down
//! - The specific date/hour has no data
//! - Network connectivity issues

use rangebar::providers::dukascopy::{
    DukascopyFetcher, DukascopyRangeBarBuilder, ValidationStrictness,
};

#[tokio::test]
#[ignore] // Run with: cargo test --test dukascopy_real_data_test -- --ignored
async fn test_fetch_and_construct_range_bars_eurusd() {
    // Fetch real EURUSD tick data from January 15, 2025, 10:00 GMT
    // This date is in the recent past and should have data available
    let fetcher = DukascopyFetcher::new("EURUSD");

    let ticks = fetcher
        .fetch_hour(2025, 1, 15, 10)
        .await
        .expect("Failed to fetch Dukascopy data");

    println!("✓ Fetched {} ticks from Dukascopy", ticks.len());

    // Verify we got ticks
    assert!(
        ticks.len() > 0,
        "Expected ticks from Dukascopy, got none"
    );

    // Verify tick structure
    let first_tick = &ticks[0];
    println!(
        "First tick: bid={:.5}, ask={:.5}, bid_vol={:.1}, ask_vol={:.1}, ts={}",
        first_tick.bid,
        first_tick.ask,
        first_tick.bid_volume,
        first_tick.ask_volume,
        first_tick.timestamp_ms
    );

    // Verify reasonable Forex prices (EUR/USD typically 0.9 - 1.3)
    assert!(
        first_tick.bid > 0.9 && first_tick.bid < 1.3,
        "EUR/USD bid price {} outside expected range",
        first_tick.bid
    );
    assert!(
        first_tick.ask > 0.9 && first_tick.ask < 1.3,
        "EUR/USD ask price {} outside expected range",
        first_tick.ask
    );
    assert!(first_tick.bid < first_tick.ask, "Crossed market detected");

    // Construct range bars from real data
    let mut builder = DukascopyRangeBarBuilder::new(25, "EURUSD", ValidationStrictness::Strict);

    let mut completed_bars = 0;
    let mut skipped_ticks = 0;

    for tick in &ticks {
        match builder.process_tick(tick) {
            Ok(Some(bar)) => {
                completed_bars += 1;
                println!(
                    "Bar {}: O={:.5} H={:.5} L={:.5} C={:.5} V={:.2} spread_avg={:.5}",
                    completed_bars,
                    bar.base.open.to_f64(),
                    bar.base.high.to_f64(),
                    bar.base.low.to_f64(),
                    bar.base.close.to_f64(),
                    bar.base.volume.to_f64(),
                    bar.spread_stats.avg_spread().to_f64()
                );
            }
            Ok(None) => {
                // Tick processed, bar accumulating
            }
            Err(_e) => {
                skipped_ticks += 1;
            }
        }
    }

    println!("\n=== Summary ===");
    println!("Total ticks: {}", ticks.len());
    println!("Completed bars: {}", completed_bars);
    println!("Skipped ticks: {}", skipped_ticks);
    println!(
        "Error rate: {:.2}%",
        (skipped_ticks as f64 / ticks.len() as f64) * 100.0
    );

    // Get final incomplete bar
    if let Some(partial) = builder.get_incomplete_bar() {
        println!(
            "Incomplete bar: O={:.5} H={:.5} L={:.5} ticks={}",
            partial.base.open.to_f64(),
            partial.base.high.to_f64(),
            partial.base.low.to_f64(),
            partial.spread_stats.tick_count
        );
    }

    // Verify at least some bars were created (Forex is active)
    assert!(
        completed_bars > 0 || builder.get_incomplete_bar().is_some(),
        "Expected at least some bar activity from real Forex data"
    );

    // Verify error rate is reasonable (< 10% per Q22)
    let error_rate = (skipped_ticks as f64 / ticks.len() as f64) * 100.0;
    assert!(
        error_rate < 10.0,
        "Error rate {:.2}% exceeds 10% threshold",
        error_rate
    );
}

#[tokio::test]
#[ignore] // Run with: cargo test --test dukascopy_real_data_test -- --ignored
async fn test_fetch_btcusd() {
    // Test with BTC/USD (crypto, different decimal_factor)
    let fetcher = DukascopyFetcher::new("BTCUSD");

    let ticks = fetcher
        .fetch_hour(2025, 1, 15, 10)
        .await
        .expect("Failed to fetch BTC/USD data");

    println!("✓ Fetched {} BTC/USD ticks", ticks.len());

    if ticks.is_empty() {
        println!("⚠️  No BTC/USD data for this hour (may not be available)");
        return;
    }

    let first_tick = &ticks[0];
    println!(
        "First BTC/USD tick: bid=${:.1}, ask=${:.1}",
        first_tick.bid, first_tick.ask
    );

    // BTC/USD typically $20,000 - $100,000
    assert!(
        first_tick.bid > 20000.0 && first_tick.bid < 100000.0,
        "BTC/USD price {} outside expected range",
        first_tick.bid
    );
}
