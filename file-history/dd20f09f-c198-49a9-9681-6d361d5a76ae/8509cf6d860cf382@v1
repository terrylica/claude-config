#!/usr/bin/env cargo

//! Range Bar Generation Comparison: Spot vs UM Futures
//!
//! This compares which market generates more range bars for the same time period,
//! using the existing ExportRangeBarProcessor to get accurate counts.

use rangebar::data::HistoricalDataLoader;
use rangebar::range_bars::ExportRangeBarProcessor;
use std::time::Instant;

#[derive(Debug)]
struct MarketStats {
    symbol: String,
    market_type: String,
    agg_trades: usize,
    range_bars: usize,
    processing_time_ms: u128,
    bars_per_1000_agg_trades: f64,
}

impl MarketStats {
    fn new(symbol: &str, market_type: &str) -> Self {
        Self {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            agg_trades: 0,
            range_bars: 0,
            processing_time_ms: 0,
            bars_per_1000_agg_trades: 0.0,
        }
    }

    fn calculate_efficiency(&mut self) {
        if self.agg_trades > 0 {
            self.bars_per_1000_agg_trades =
                (self.range_bars as f64 / self.agg_trades as f64) * 1000.0;
        }
    }
}

async fn analyze_symbol_market(
    symbol: &str,
    market_type: &str,
) -> Result<MarketStats, Box<dyn std::error::Error>> {
    let mut stats = MarketStats::new(symbol, market_type);

    println!(
        "🔄 Processing {} {} market...",
        symbol,
        market_type.to_uppercase()
    );

    let start_time = Instant::now();

    // Load data using existing infrastructure
    let loader = HistoricalDataLoader::new_with_market(symbol, market_type);
    let trades = loader.load_recent_day().await?;
    stats.agg_trades = trades.len();

    // Process through range bar processor (25 BPS threshold)
    let mut processor = ExportRangeBarProcessor::new(25);
    processor.process_trades_continuously(&trades);

    // Get the generated range bars
    let completed_bars = processor.get_all_completed_bars();
    stats.range_bars = completed_bars.len();

    stats.processing_time_ms = start_time.elapsed().as_millis();
    stats.calculate_efficiency();

    println!(
        "   ✅ {} aggTrades → {} range bars ({:.1} bars/1000 aggTrades)",
        stats.agg_trades, stats.range_bars, stats.bars_per_1000_agg_trades
    );

    Ok(stats)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("📊 Range Bar Generation Comparison: Spot vs UM Futures");
    println!("=======================================================");
    println!("🎯 Testing 25 BPS threshold on recent day data");
    println!();

    let symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT"];
    let mut all_stats = Vec::new();

    for symbol in &symbols {
        println!("🔍 Analyzing {} across both markets:", symbol);

        // Test spot market
        match analyze_symbol_market(symbol, "spot").await {
            Ok(spot_stats) => all_stats.push(spot_stats),
            Err(e) => println!("   ❌ Spot failed: {}", e),
        }

        // Test UM futures market
        match analyze_symbol_market(symbol, "um").await {
            Ok(futures_stats) => all_stats.push(futures_stats),
            Err(e) => println!("   ❌ UM futures failed: {}", e),
        }

        println!();
    }

    // Generate comparison report
    println!("📈 COMPREHENSIVE COMPARISON RESULTS");
    println!("==================================");
    println!();

    println!("  Symbol   Market │ aggTrades │ Range Bars │ Bars/1000 Trades │ Processing Time");
    println!("  ─────────────────┼───────────┼────────────┼──────────────────┼────────────────");

    // Group by symbol for easy comparison
    for symbol in &symbols {
        let spot_stats = all_stats
            .iter()
            .find(|s| s.symbol == *symbol && s.market_type == "spot");
        let futures_stats = all_stats
            .iter()
            .find(|s| s.symbol == *symbol && s.market_type == "um");

        if let Some(spot) = spot_stats {
            println!(
                "  {:8} SPOT │ {:>9} │ {:>10} │ {:>12.1} │ {:>11}ms",
                spot.symbol,
                spot.agg_trades,
                spot.range_bars,
                spot.bars_per_1000_agg_trades,
                spot.processing_time_ms
            );
        }

        if let Some(futures) = futures_stats {
            println!(
                "  {:8} UM   │ {:>9} │ {:>10} │ {:>12.1} │ {:>11}ms",
                futures.symbol,
                futures.agg_trades,
                futures.range_bars,
                futures.bars_per_1000_agg_trades,
                futures.processing_time_ms
            );
        }

        // Calculate ratio if both exist
        if let (Some(spot), Some(futures)) = (spot_stats, futures_stats) {
            let agg_ratio = futures.agg_trades as f64 / spot.agg_trades as f64;
            let bar_ratio = futures.range_bars as f64 / spot.range_bars as f64;
            let efficiency_ratio = futures.bars_per_1000_agg_trades / spot.bars_per_1000_agg_trades;

            println!("                   │           │            │                  │");
            println!(
                "  Futures/Spot     │    {:.2}x │     {:.2}x │           {:.2}x │",
                agg_ratio, bar_ratio, efficiency_ratio
            );
        }
        println!(
            "  ─────────────────┼───────────┼────────────┼──────────────────┼────────────────"
        );
    }

    println!();
    println!("🎯 **KEY INSIGHTS:**");
    println!("   • **aggTrade Count**: How much raw trading activity");
    println!("   • **Range Bar Count**: How many bars actually generated");
    println!("   • **Bars/1000 Trades**: Market efficiency at generating bars");
    println!("   • **Higher ratio**: More volatile/active price movements");

    Ok(())
}
