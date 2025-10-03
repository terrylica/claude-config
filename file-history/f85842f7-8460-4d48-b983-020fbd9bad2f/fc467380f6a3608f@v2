//! Comprehensive range bar validation with massive real data
//!
//! Tests the fundamental CONCEPT of range bars:
//! 1. Threshold sensitivity (lower threshold = more bars)
//! 2. Volatility capture (bars form during moves)
//! 3. Non-lookahead bias (breach included in closing bar)
//! 4. Time independence (bars not clock-based)
//! 5. Statistical properties across market regimes

use rangebar::data::dukascopy::{
    DukascopyFetcher, DukascopyRangeBarBuilder, ValidationStrictness,
};
use std::collections::HashMap;

/// Fetch multiple hours of data for comprehensive testing
async fn fetch_full_day(
    instrument: &str,
    year: u32,
    month: u32,
    day: u32,
) -> Vec<rangebar::data::dukascopy::DukascopyTick> {
    let fetcher = DukascopyFetcher::new(instrument);
    let mut all_ticks = Vec::new();

    for hour in 0..24 {
        print!("Fetching hour {}...", hour);
        match fetcher.fetch_hour(year, month, day, hour).await {
            Ok(mut ticks) => {
                println!(" {} ticks", ticks.len());
                all_ticks.append(&mut ticks);
            }
            Err(e) => {
                println!(" SKIP ({})", e);
            }
        }
    }

    all_ticks
}

#[tokio::test]
#[ignore]
async fn test_threshold_sensitivity_law() {
    println!("\n=== THRESHOLD SENSITIVITY LAW ===");
    println!("Theory: Lower threshold → More bars (inverse relationship)\n");

    let fetcher = DukascopyFetcher::new("BTCUSD");

    // Fetch 6 hours of volatile data
    let mut all_ticks = Vec::new();
    for hour in [12, 13, 14, 15, 16, 17] {
        if let Ok(mut ticks) = fetcher.fetch_hour(2025, 1, 15, hour).await {
            all_ticks.append(&mut ticks);
        }
    }

    println!("Total ticks: {}\n", all_ticks.len());

    let thresholds = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100];
    let mut results = Vec::new();

    for &threshold in &thresholds {
        let mut builder = DukascopyRangeBarBuilder::new(
            threshold,
            "BTCUSD",
            ValidationStrictness::Strict,
        );

        let mut bar_count = 0;
        let mut total_ticks_in_bars = 0;
        let mut total_duration_ms = 0i64;

        for tick in &all_ticks {
            if let Ok(Some(bar)) = builder.process_tick(tick) {
                bar_count += 1;
                total_ticks_in_bars += bar.spread_stats.tick_count as usize;
                let duration = bar.base.close_time - bar.base.open_time;
                total_duration_ms += duration;
            }
        }

        let avg_ticks_per_bar = if bar_count > 0 {
            total_ticks_in_bars as f64 / bar_count as f64
        } else {
            0.0
        };

        let avg_duration_sec = if bar_count > 0 {
            (total_duration_ms / 1000) as f64 / bar_count as f64
        } else {
            0.0
        };

        results.push((threshold, bar_count, avg_ticks_per_bar, avg_duration_sec));

        println!(
            "{:3} bps: {:4} bars | avg {:.1} ticks/bar | avg {:.1}s/bar",
            threshold, bar_count, avg_ticks_per_bar, avg_duration_sec
        );
    }

    println!("\n--- Validation ---");

    // Verify inverse relationship: lower threshold = more bars
    // Allow for statistical variance when bar counts are very low (<10)
    let mut violations = 0;
    for i in 1..results.len() {
        let (thresh_prev, bars_prev, _, _) = results[i - 1];
        let (thresh_curr, bars_curr, _, _) = results[i];

        if bars_curr > bars_prev {
            // Allow violation if both have very few bars (statistical noise)
            if bars_prev > 10 || bars_curr > 10 {
                println!(
                    "  ⚠️  {} bps ({} bars) > {} bps ({} bars)",
                    thresh_curr, bars_curr, thresh_prev, bars_prev
                );
                violations += 1;
            }
        }
    }

    assert!(
        violations == 0,
        "FAILED: {} violations of inverse relationship",
        violations
    );

    println!("✓ Inverse relationship confirmed: lower threshold = more bars");

    // Verify higher thresholds = longer bars (more time, more ticks)
    for i in 1..results.len() {
        let (thresh_prev, _, ticks_prev, _) = results[i - 1];
        let (thresh_curr, _, ticks_curr, _) = results[i];

        if ticks_curr > 0.0 && ticks_prev > 0.0 {
            assert!(
                ticks_curr >= ticks_prev * 0.8, // Allow some variance
                "FAILED: {} bps should have ≥ ticks/bar than {} bps",
                thresh_curr,
                thresh_prev
            );
        }
    }

    println!("✓ Higher thresholds = longer bars (more ticks accumulated)");
}

#[tokio::test]
#[ignore]
async fn test_volatility_clustering() {
    println!("\n=== VOLATILITY CLUSTERING TEST ===");
    println!("Theory: Bars concentrate during volatile periods\n");

    let fetcher = DukascopyFetcher::new("BTCUSD");

    // Fetch 24 hours
    let mut hourly_data = Vec::new();
    for hour in 0..24 {
        if let Ok(ticks) = fetcher.fetch_hour(2025, 1, 15, hour).await {
            hourly_data.push((hour, ticks));
        }
    }

    println!("Testing with 25 bps threshold\n");

    let mut hourly_bar_counts = Vec::new();

    for (hour, ticks) in hourly_data {
        if ticks.is_empty() {
            continue;
        }

        // Calculate actual volatility
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

        let volatility_bps = if min_price > 0.0 {
            ((max_price - min_price) / min_price) * 10000.0
        } else {
            0.0
        };

        // Count bars
        let mut builder = DukascopyRangeBarBuilder::new(25, "BTCUSD", ValidationStrictness::Strict);
        let mut bar_count = 0;

        for tick in &ticks {
            if let Ok(Some(_)) = builder.process_tick(tick) {
                bar_count += 1;
            }
        }

        hourly_bar_counts.push((hour, bar_count, volatility_bps, ticks.len()));

        println!(
            "Hour {:2}: {:3} bars | {:.1} bps volatility | {} ticks",
            hour, bar_count, volatility_bps, ticks.len()
        );
    }

    println!("\n--- Validation ---");

    // Verify correlation: high volatility hours have more bars
    let high_vol_hours: Vec<_> = hourly_bar_counts
        .iter()
        .filter(|(_, _, vol, _)| *vol > 50.0)
        .collect();

    let low_vol_hours: Vec<_> = hourly_bar_counts
        .iter()
        .filter(|(_, _, vol, _)| *vol < 30.0)
        .collect();

    if !high_vol_hours.is_empty() && !low_vol_hours.is_empty() {
        let avg_bars_high_vol: f64 = high_vol_hours.iter().map(|(_, bars, _, _)| *bars as f64).sum::<f64>()
            / high_vol_hours.len() as f64;

        let avg_bars_low_vol: f64 = low_vol_hours.iter().map(|(_, bars, _, _)| *bars as f64).sum::<f64>()
            / low_vol_hours.len() as f64;

        println!(
            "High volatility hours (>50 bps): avg {:.1} bars",
            avg_bars_high_vol
        );
        println!(
            "Low volatility hours (<30 bps): avg {:.1} bars",
            avg_bars_low_vol
        );

        assert!(
            avg_bars_high_vol >= avg_bars_low_vol,
            "FAILED: High volatility should produce ≥ bars than low volatility"
        );

        println!("✓ Volatility clustering confirmed");
    } else {
        println!("⚠️  Insufficient volatility variation for clustering test");
    }
}

#[tokio::test]
#[ignore]
async fn test_breach_inclusion_rule() {
    println!("\n=== BREACH INCLUSION RULE TEST ===");
    println!("Theory: Breaching tick MUST be included in closing bar\n");

    let fetcher = DukascopyFetcher::new("BTCUSD");
    let ticks = fetcher.fetch_hour(2025, 1, 15, 14).await.unwrap();

    println!("Testing with 25 bps threshold");
    println!("Total ticks: {}\n", ticks.len());

    let mut builder = DukascopyRangeBarBuilder::new(25, "BTCUSD", ValidationStrictness::Strict);

    let mut bars_checked = 0;

    for tick in &ticks {
        if let Ok(Some(bar)) = builder.process_tick(tick) {
            bars_checked += 1;

            let open = bar.base.open.to_f64();
            let close = bar.base.close.to_f64();
            let high = bar.base.high.to_f64();
            let low = bar.base.low.to_f64();

            // Calculate thresholds from open
            let upper_threshold = open * (1.0 + 0.0025); // 25 bps
            let lower_threshold = open * (1.0 - 0.0025); // 25 bps

            // Verify the close IS at or beyond threshold (breach included)
            let close_breached = close >= upper_threshold || close <= lower_threshold;

            assert!(
                close_breached,
                "Bar {}: close={:.2} not at threshold (upper={:.2}, lower={:.2})",
                bars_checked,
                close,
                upper_threshold,
                lower_threshold
            );

            // Verify the extremes reached threshold
            let extreme_breached = high >= upper_threshold || low <= lower_threshold;

            assert!(
                extreme_breached,
                "Bar {}: extremes don't reach threshold",
                bars_checked
            );

            if bars_checked <= 3 {
                println!(
                    "Bar {}: open={:.2}, close={:.2}, range=[{:.2}, {:.2}]",
                    bars_checked, open, close, low, high
                );
                println!(
                    "  Thresholds: [{:.2}, {:.2}]",
                    lower_threshold, upper_threshold
                );
                println!("  Close breach: {}", close_breached);
            }
        }
    }

    println!("\n✓ All {} bars have breaching tick included in close", bars_checked);
}

#[tokio::test]
#[ignore]
async fn test_time_independence() {
    println!("\n=== TIME INDEPENDENCE TEST ===");
    println!("Theory: Range bars are PRICE-driven, not TIME-driven\n");

    let fetcher = DukascopyFetcher::new("BTCUSD");
    let ticks = fetcher.fetch_hour(2025, 1, 15, 14).await.unwrap();

    let mut builder = DukascopyRangeBarBuilder::new(25, "BTCUSD", ValidationStrictness::Strict);

    let mut bar_durations = Vec::new();

    for tick in &ticks {
        if let Ok(Some(bar)) = builder.process_tick(tick) {
            let duration_sec = (bar.base.close_time - bar.base.open_time) / 1_000_000;
            bar_durations.push(duration_sec);
        }
    }

    if bar_durations.is_empty() {
        println!("⚠️  No bars formed (low volatility period)");
        return;
    }

    // Calculate statistics
    let min_duration = *bar_durations.iter().min().unwrap();
    let max_duration = *bar_durations.iter().max().unwrap();
    let avg_duration = bar_durations.iter().sum::<i64>() as f64 / bar_durations.len() as f64;

    // Calculate variance
    let variance = bar_durations
        .iter()
        .map(|&d| {
            let diff = d as f64 - avg_duration;
            diff * diff
        })
        .sum::<f64>()
        / bar_durations.len() as f64;

    let std_dev = variance.sqrt();
    let cv = std_dev / avg_duration; // Coefficient of variation

    println!("Bar durations ({} bars):", bar_durations.len());
    println!("  Min: {:.1}s", min_duration as f64);
    println!("  Avg: {:.1}s", avg_duration);
    println!("  Max: {:.1}s", max_duration as f64);
    println!("  StdDev: {:.1}s", std_dev);
    println!("  CV: {:.2}", cv);

    // Show duration distribution
    println!("\nDuration histogram:");
    let mut duration_buckets: HashMap<String, usize> = HashMap::new();
    for &duration in &bar_durations {
        let bucket = if duration < 10 {
            "0-10s"
        } else if duration < 30 {
            "10-30s"
        } else if duration < 60 {
            "30-60s"
        } else if duration < 120 {
            "1-2min"
        } else if duration < 300 {
            "2-5min"
        } else {
            ">5min"
        };
        *duration_buckets.entry(bucket.to_string()).or_insert(0) += 1;
    }

    for bucket in ["0-10s", "10-30s", "30-60s", "1-2min", "2-5min", ">5min"] {
        let count = duration_buckets.get(bucket).unwrap_or(&0);
        println!("  {}: {}", bucket, count);
    }

    println!("\n--- Validation ---");

    // High coefficient of variation = time independence
    // (bars form at different rates depending on price action)
    assert!(
        cv > 0.3,
        "FAILED: CV {:.2} too low (bars too uniform in time)",
        cv
    );

    println!("✓ Time independence confirmed (CV={:.2} > 0.3)", cv);
    println!("✓ Bar formation is PRICE-driven, not clock-driven");
}

#[tokio::test]
#[ignore]
async fn test_bar_independence() {
    println!("\n=== BAR INDEPENDENCE TEST ===");
    println!("Theory: Each bar's threshold recalculated from ITS open (no carry-over)\n");

    let fetcher = DukascopyFetcher::new("BTCUSD");
    let ticks = fetcher.fetch_hour(2025, 1, 15, 14).await.unwrap();

    let mut builder = DukascopyRangeBarBuilder::new(25, "BTCUSD", ValidationStrictness::Strict);

    let mut bars = Vec::new();

    for tick in &ticks {
        if let Ok(Some(bar)) = builder.process_tick(tick) {
            bars.push(bar);
        }
    }

    if bars.len() < 2 {
        println!("⚠️  Need at least 2 bars for independence test");
        return;
    }

    println!("Testing {} bars\n", bars.len());

    for i in 1..bars.len().min(5) {
        let prev_bar = &bars[i - 1];
        let curr_bar = &bars[i];

        let prev_close = prev_bar.base.close.to_f64();
        let curr_open = curr_bar.base.open.to_f64();

        // Current bar opens at previous bar's close
        assert!(
            (prev_close - curr_open).abs() < 0.01,
            "Bar {} open should equal Bar {} close",
            i + 1,
            i
        );

        // Current bar's thresholds calculated from CURRENT open, not previous
        let curr_upper = curr_open * 1.0025;
        let curr_lower = curr_open * 0.9975;

        println!(
            "Bar {}: open={:.2}, thresholds=[{:.2}, {:.2}]",
            i + 1,
            curr_open,
            curr_lower,
            curr_upper
        );

        // Verify current bar respected ITS OWN thresholds
        let close = curr_bar.base.close.to_f64();
        let breached = close >= curr_upper || close <= curr_lower;

        assert!(
            breached,
            "Bar {} didn't breach its own threshold",
            i + 1
        );
    }

    println!("\n✓ Each bar uses thresholds from ITS open (independence confirmed)");
}

#[tokio::test]
#[ignore]
async fn test_full_day_statistics() {
    println!("\n=== FULL DAY STATISTICAL ANALYSIS ===");
    println!("Fetching 24 hours of BTCUSD data...\n");

    let all_ticks = fetch_full_day("BTCUSD", 2025, 1, 15).await;

    println!("\nTotal ticks fetched: {}", all_ticks.len());

    if all_ticks.is_empty() {
        println!("⚠️  No data available");
        return;
    }

    // Test multiple thresholds
    for threshold in [10, 25, 50] {
        println!("\n--- Threshold: {} bps ---", threshold);

        let mut builder = DukascopyRangeBarBuilder::new(
            threshold,
            "BTCUSD",
            ValidationStrictness::Strict,
        );

        let mut bars = Vec::new();
        let mut skipped = 0;

        for tick in &all_ticks {
            match builder.process_tick(tick) {
                Ok(Some(bar)) => bars.push(bar),
                Ok(None) => {}
                Err(_) => skipped += 1,
            }
        }

        println!("Bars formed: {}", bars.len());
        println!("Ticks skipped: {} ({:.2}%)", skipped, (skipped as f64 / all_ticks.len() as f64) * 100.0);

        if bars.is_empty() {
            continue;
        }

        // Volume statistics
        let total_volume: f64 = bars.iter().map(|b| b.base.volume.to_f64()).sum();
        let avg_volume = total_volume / bars.len() as f64;

        println!("Total volume: {:.1}", total_volume);
        println!("Avg volume/bar: {:.1}", avg_volume);

        // Tick count statistics
        let tick_counts: Vec<_> = bars.iter().map(|b| b.spread_stats.tick_count).collect();
        let avg_ticks = tick_counts.iter().sum::<u32>() as f64 / tick_counts.len() as f64;
        let min_ticks = *tick_counts.iter().min().unwrap();
        let max_ticks = *tick_counts.iter().max().unwrap();

        println!("Ticks/bar: min={}, avg={:.1}, max={}", min_ticks, avg_ticks, max_ticks);

        // Direction analysis
        let up_bars = bars.iter().filter(|b| b.base.close.to_f64() > b.base.open.to_f64()).count();
        let down_bars = bars.iter().filter(|b| b.base.close.to_f64() < b.base.open.to_f64()).count();

        println!("Direction: {} up, {} down ({:.1}% up)", up_bars, down_bars, (up_bars as f64 / bars.len() as f64) * 100.0);

        // Spread statistics
        let avg_spread: f64 = bars
            .iter()
            .map(|b| b.spread_stats.avg_spread().to_f64())
            .sum::<f64>()
            / bars.len() as f64;

        println!("Avg spread: ${:.2}", avg_spread);
    }
}
