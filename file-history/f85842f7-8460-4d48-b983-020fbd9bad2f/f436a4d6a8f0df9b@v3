//! Test with different time periods to find bars

use rangebar::providers::dukascopy::{
    DukascopyFetcher, DukascopyRangeBarBuilder, ValidationStrictness,
};

#[tokio::test]
#[ignore]
async fn test_multiple_hours_for_bars() {
    println!("\n=== SEARCHING FOR VOLATILE PERIODS ===\n");

    let fetcher = DukascopyFetcher::new("EURUSD");

    // Try multiple hours to find volatility
    let hours = [0, 6, 12, 14, 16, 18, 20]; // Different trading sessions

    for hour in hours {
        println!("\n--- Hour {} ---", hour);

        let ticks = match fetcher.fetch_hour(2025, 1, 15, hour).await {
            Ok(t) => t,
            Err(e) => {
                println!("⚠️  No data: {}", e);
                continue;
            }
        };

        if ticks.is_empty() {
            println!("⚠️  Empty");
            continue;
        }

        // Calculate price range
        let mut min_price = f64::MAX;
        let mut max_price = f64::MIN;

        for tick in &ticks {
            let mid = (tick.bid + tick.ask) / 2.0;
            if mid < min_price {
                min_price = mid;
            }
            if mid > max_price {
                max_price = mid;
            }
        }

        let open_price = (ticks[0].bid + ticks[0].ask) / 2.0;
        let range_bps = ((max_price - min_price) / open_price) * 10000.0;

        println!("Ticks: {}", ticks.len());
        println!("Range: {:.5} to {:.5} ({:.1} bps)", min_price, max_price, range_bps);

        // Try 5 bps threshold (should definitely get bars if volatile)
        let mut builder = DukascopyRangeBarBuilder::new(5, "EURUSD", ValidationStrictness::Strict);

        let mut bar_count = 0;
        for tick in &ticks {
            if let Ok(Some(bar)) = builder.process_tick(tick) {
                bar_count += 1;
                if bar_count <= 3 {
                    println!(
                        "  Bar {}: O={:.5} C={:.5} V={:.1} ticks={}",
                        bar_count,
                        bar.base.open.to_f64(),
                        bar.base.close.to_f64(),
                        bar.base.volume.to_f64(),
                        bar.spread_stats.tick_count
                    );
                }
            }
        }

        println!("Bars at 5 bps: {}", bar_count);

        if bar_count > 0 {
            println!("✓ Found volatile period!");
            break;
        }
    }
}

#[tokio::test]
#[ignore]
async fn test_btcusd_volatility() {
    println!("\n=== BTCUSD VOLATILITY TEST ===\n");

    let fetcher = DukascopyFetcher::new("BTCUSD");
    let ticks = fetcher.fetch_hour(2025, 1, 15, 14).await.unwrap();

    println!("Fetched {} ticks", ticks.len());

    // Calculate price range
    let mut min_price = f64::MAX;
    let mut max_price = f64::MIN;

    for tick in &ticks {
        let mid = (tick.bid + tick.ask) / 2.0;
        if mid < min_price {
            min_price = mid;
        }
        if mid > max_price {
            max_price = mid;
        }
    }

    let open_price = (ticks[0].bid + ticks[0].ask) / 2.0;
    let range_bps = ((max_price - min_price) / open_price) * 10000.0;

    println!("Open: ${:.1}", open_price);
    println!("Range: ${:.1} to ${:.1}", min_price, max_price);
    println!("Range in bps: {:.1}", range_bps);

    // Test with 25 bps
    let mut builder = DukascopyRangeBarBuilder::new(25, "BTCUSD", ValidationStrictness::Strict);

    let mut bars = Vec::new();
    for tick in &ticks {
        if let Ok(Some(bar)) = builder.process_tick(tick) {
            bars.push(bar);
        }
    }

    println!("\nBars completed: {}", bars.len());

    // Show first few bars
    for (i, bar) in bars.iter().take(5).enumerate() {
        println!(
            "Bar {}: O=${:.1} H=${:.1} L=${:.1} C=${:.1} ticks={}",
            i + 1,
            bar.base.open.to_f64(),
            bar.base.high.to_f64(),
            bar.base.low.to_f64(),
            bar.base.close.to_f64(),
            bar.spread_stats.tick_count
        );

        // Verify threshold breach (25 bps)
        let open = bar.base.open.to_f64();
        let close = bar.base.close.to_f64();
        let move_pct = ((close - open).abs() / open) * 100.0;
        let move_bps = move_pct * 100.0;

        println!("  Move: {:.1} bps", move_bps);

        // Should be at least 25 bps
        assert!(
            move_bps >= 24.5, // Allow small rounding error
            "Bar {} move {:.1} bps < 25 bps threshold",
            i + 1,
            move_bps
        );
    }

    if bars.len() > 0 {
        println!("\n✓ Range bars constructing correctly with threshold validation!");
    }
}
