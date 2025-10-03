//! Detailed audit test for Dukascopy implementation
//!
//! Deep validation of data quality, range bar construction, and spread statistics

use rangebar::data::dukascopy::{
    DukascopyFetcher, DukascopyRangeBarBuilder, ValidationStrictness,
};

#[tokio::test]
#[ignore]
async fn audit_eurusd_detailed() {
    println!("\n=== DUKASCOPY EURUSD AUDIT ===\n");

    // Fetch data
    let fetcher = DukascopyFetcher::new("EURUSD");
    let ticks = fetcher
        .fetch_hour(2025, 1, 15, 10)
        .await
        .expect("Failed to fetch data");

    println!("✓ Fetched {} ticks", ticks.len());

    // Analyze tick quality
    let mut crossed_markets = 0;
    let mut zero_volume_ticks = 0;
    let mut spread_sum = 0.0;
    let mut min_spread = f64::MAX;
    let mut max_spread = 0.0;

    for tick in &ticks {
        if tick.bid >= tick.ask {
            crossed_markets += 1;
        }
        if tick.bid_volume == 0.0 && tick.ask_volume == 0.0 {
            zero_volume_ticks += 1;
        }
        let spread = tick.ask - tick.bid;
        spread_sum += spread;
        if spread < min_spread {
            min_spread = spread;
        }
        if spread > max_spread {
            max_spread = spread;
        }
    }

    let avg_spread = spread_sum / ticks.len() as f64;

    println!("\n--- Data Quality ---");
    println!("Crossed markets: {}", crossed_markets);
    println!("Zero volume ticks: {}", zero_volume_ticks);
    println!("Spread: min={:.5}, avg={:.5}, max={:.5}", min_spread, avg_spread, max_spread);
    println!("Spread in pips: {:.1}", avg_spread * 10000.0);

    // Test multiple thresholds
    for threshold_bps in [10, 25, 50] {
        println!("\n--- Threshold: {} bps ---", threshold_bps);

        let mut builder = DukascopyRangeBarBuilder::new(
            threshold_bps,
            "EURUSD",
            ValidationStrictness::Strict,
        );

        let mut completed_bars = 0;
        let mut skipped_ticks = 0;
        let mut bars = Vec::new();

        for tick in &ticks {
            match builder.process_tick(tick) {
                Ok(Some(bar)) => {
                    completed_bars += 1;
                    bars.push(bar);
                }
                Ok(None) => {}
                Err(_) => {
                    skipped_ticks += 1;
                }
            }
        }

        println!("Completed bars: {}", completed_bars);
        println!("Skipped ticks: {}", skipped_ticks);

        // Show first few bars
        for (i, bar) in bars.iter().take(3).enumerate() {
            println!(
                "  Bar {}: O={:.5} H={:.5} L={:.5} C={:.5} V={:.1} ticks={} spread_avg={:.5}",
                i + 1,
                bar.base.open.to_f64(),
                bar.base.high.to_f64(),
                bar.base.low.to_f64(),
                bar.base.close.to_f64(),
                bar.base.volume.to_f64(),
                bar.spread_stats.tick_count,
                bar.spread_stats.avg_spread().to_f64()
            );

            // Verify range bar invariants
            assert!(bar.base.low.to_f64() <= bar.base.open.to_f64());
            assert!(bar.base.low.to_f64() <= bar.base.close.to_f64());
            assert!(bar.base.high.to_f64() >= bar.base.open.to_f64());
            assert!(bar.base.high.to_f64() >= bar.base.close.to_f64());

            // Verify buy/sell volume is zeroed (Q10)
            assert_eq!(bar.base.buy_volume.0, 0, "Buy volume should be 0 for quote data");
            assert_eq!(bar.base.sell_volume.0, 0, "Sell volume should be 0 for quote data");

            // Verify spread stats reset per bar (Q13)
            assert!(bar.spread_stats.tick_count > 0, "Bar should have tick count");
            assert!(bar.spread_stats.avg_spread().0 > 0, "Bar should have spread");
        }

        // Get incomplete bar
        if let Some(partial) = builder.get_incomplete_bar() {
            println!(
                "  Incomplete: O={:.5} H={:.5} L={:.5} ticks={}",
                partial.base.open.to_f64(),
                partial.base.high.to_f64(),
                partial.base.low.to_f64(),
                partial.spread_stats.tick_count
            );
        }
    }

    // Verify timestamp ordering
    println!("\n--- Timestamp Validation ---");
    let mut is_ordered = true;
    for i in 1..ticks.len() {
        if ticks[i].timestamp_ms < ticks[i - 1].timestamp_ms {
            is_ordered = false;
            println!(
                "⚠️  Timestamp out of order at index {}: {} < {}",
                i, ticks[i].timestamp_ms, ticks[i - 1].timestamp_ms
            );
            break;
        }
    }
    if is_ordered {
        println!("✓ All timestamps ordered correctly");
    }

    // Verify timestamp range
    let first_ts = ticks[0].timestamp_ms;
    let last_ts = ticks[ticks.len() - 1].timestamp_ms;
    let duration_ms = last_ts - first_ts;
    println!("First timestamp: {}", first_ts);
    println!("Last timestamp: {}", last_ts);
    println!("Duration: {} ms ({:.1} minutes)", duration_ms, duration_ms as f64 / 60000.0);

    // Should be within the hour (0-3600000 ms)
    assert!(duration_ms <= 3600000, "Duration exceeds 1 hour");

    println!("\n=== AUDIT COMPLETE ===");
}

#[tokio::test]
#[ignore]
async fn audit_btcusd_vs_eurusd() {
    println!("\n=== CROSS-ASSET COMPARISON ===\n");

    // Fetch both
    let eurusd_fetcher = DukascopyFetcher::new("EURUSD");
    let btcusd_fetcher = DukascopyFetcher::new("BTCUSD");

    let eurusd_ticks = eurusd_fetcher.fetch_hour(2025, 1, 15, 10).await.unwrap();
    let btcusd_ticks = btcusd_fetcher.fetch_hour(2025, 1, 15, 10).await.unwrap();

    println!("EURUSD: {} ticks", eurusd_ticks.len());
    println!("BTCUSD: {} ticks", btcusd_ticks.len());

    // Compare tick frequencies
    println!("\nTick frequency:");
    println!("  EURUSD: {:.1} ticks/minute", eurusd_ticks.len() as f64 / 60.0);
    println!("  BTCUSD: {:.1} ticks/minute", btcusd_ticks.len() as f64 / 60.0);

    // Compare spreads
    let eurusd_spread = eurusd_ticks[0].ask - eurusd_ticks[0].bid;
    let btcusd_spread = btcusd_ticks[0].ask - btcusd_ticks[0].bid;

    println!("\nTypical spreads:");
    println!("  EURUSD: {:.5} ({:.1} pips)", eurusd_spread, eurusd_spread * 10000.0);
    println!("  BTCUSD: ${:.1}", btcusd_spread);

    // Compare spread as percentage of price
    let eurusd_spread_pct = (eurusd_spread / eurusd_ticks[0].bid) * 100.0;
    let btcusd_spread_pct = (btcusd_spread / btcusd_ticks[0].bid) * 100.0;

    println!("\nSpread as % of price:");
    println!("  EURUSD: {:.4}%", eurusd_spread_pct);
    println!("  BTCUSD: {:.4}%", btcusd_spread_pct);

    // Forex should have tighter spreads (lower %)
    assert!(eurusd_spread_pct < 0.01, "EURUSD spread should be < 0.01%");
    assert!(btcusd_spread_pct < 0.5, "BTCUSD spread should be reasonable");
}
