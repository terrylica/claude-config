//! Test version of Historical Range Bar Visualizer - loads 1 day for validation

use std::io::Write;
use std::time::Duration;

use crossterm::event::{Event, KeyCode, KeyEventKind, poll, read};
//use crossterm::terminal::{enable_raw_mode, disable_raw_mode};
use tokio::signal;

use rangebar::data::HistoricalDataLoader;
use rangebar::range_bars::ExportRangeBarProcessor;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();

    // Parse command line arguments: [symbol] [market_type]
    let symbol = args.get(1).map(|s| s.as_str()).unwrap_or("BTCUSDT");
    let market_type = args.get(2).map(|s| s.as_str()).unwrap_or("spot");

    // Validate market type
    match market_type {
        "spot" | "um" | "cm" => {}
        _ => {
            eprintln!(
                "Error: market_type must be 'spot', 'um', or 'cm', got '{}'",
                market_type
            );
            eprintln!("Usage: {} [symbol] [market_type]", args[0]);
            eprintln!("  symbol: Trading symbol (default: BTCUSDT)");
            eprintln!("  market_type: spot (default), um (UM Futures), cm (CM Futures)");
            std::process::exit(1);
        }
    }

    println!(
        "🧪 Testing Historical Range Bar Visualizer - 1 Day {} ({} market)",
        symbol.to_uppercase(),
        market_type.to_uppercase()
    );
    println!("==============================================================================");
    println!("Controls: q=quit, +=faster, -=slower, p=pause");
    println!("");

    // Raw mode disabled for clean terminal output

    let loader = HistoricalDataLoader::new_with_market(symbol, market_type);
    let trades = loader.load_recent_day().await?;
    let mut processor = ExportRangeBarProcessor::new(250); // 250 units × 0.1 BPS = 25 BPS = 0.25%
    let mut acceleration = 1000.0; // Start at 1000x
    let mut paused = false;
    let mut trade_index = 0;
    let mut bar_count = 0;
    let mut current_bar_trades = 0;
    let mut current_bar_open: Option<f64> = None;

    println!(
        "▶️  Starting test with {} trades at {:.0}x speed...\n",
        trades.len(),
        acceleration
    );

    loop {
        // Non-blocking keyboard input
        if poll(Duration::from_millis(0))? {
            if let Event::Key(key) = read()? {
                if key.kind == KeyEventKind::Press {
                    match key.code {
                        KeyCode::Char('q') => {
                            println!("\n👋 Test completed");
                            break;
                        }
                        KeyCode::Char('+') => {
                            acceleration = (acceleration * 2.0_f64).min(50000.0_f64);
                            println!("\n🚀 Speed: {:.0}x", acceleration);
                        }
                        KeyCode::Char('-') => {
                            acceleration = (acceleration / 2.0_f64).max(10.0_f64);
                            println!("\n🐌 Speed: {:.0}x", acceleration);
                        }
                        KeyCode::Char('p') => {
                            paused = !paused;
                            println!(
                                "\n{}",
                                if paused {
                                    "⏸️  Paused"
                                } else {
                                    "▶️  Resumed"
                                }
                            );
                        }
                        _ => {}
                    }
                }
            }
        }

        // Handle Ctrl+C and trade processing
        tokio::select! {
            _ = signal::ctrl_c() => {
                println!("\n👋 Test interrupted");
                break;
            }
            _ = tokio::time::sleep(Duration::from_millis(1)) => {
                if !paused && trade_index < trades.len() {
                    let trade = &trades[trade_index];
                    current_bar_trades += 1;

                    if current_bar_open.is_none() {
                        current_bar_open = Some(trade.price.to_f64());
                    }

                    // Update building bar display
                    print!("\rBuilding bar #{}: {} trades, current: ${:.2}, open: ${:.2}",
                           bar_count + 1,
                           current_bar_trades,
                           trade.price.to_f64(),
                           current_bar_open.unwrap());
                    std::io::stdout().flush().unwrap();

                    // Process trade using continuous processor
                    processor.process_trades_continuously(&[trade.clone()]);

                    // Get any newly completed bars
                    let completed_bars = processor.get_all_completed_bars();
                    for bar in completed_bars {
                        bar_count += 1;

                        // Determine direction with colored arrows
                        let direction = if bar.close.to_f64() > bar.open.to_f64() {
                            "\x1b[32m↑\x1b[0m"  // Green up arrow
                        } else {
                            "\x1b[31m↓\x1b[0m"  // Red down arrow
                        };

                        println!("\n{} BAR {:>4} • O:{:.4} H:{:.4} L:{:.4} C:{:.4} • Vol:{:>12.2} • Trades:{:>6}",
                                direction,
                                bar_count,
                                bar.open.to_f64(),
                                bar.high.to_f64(),
                                bar.low.to_f64(),
                                bar.close.to_f64(),
                                bar.volume.to_f64(),
                                current_bar_trades);
                        current_bar_trades = 0;
                        current_bar_open = None;
                    }

                    // Time delay based on acceleration
                    if trade_index + 1 < trades.len() {
                        let current_timestamp = trades[trade_index].timestamp;
                        let next_timestamp = trades[trade_index + 1].timestamp;
                        let delta_microseconds = (next_timestamp - current_timestamp) as f64;
                        let accelerated_delay = delta_microseconds / acceleration;

                        if accelerated_delay > 100.0 { // 0.1ms minimum
                            tokio::time::sleep(Duration::from_micros(accelerated_delay as u64)).await;
                        }
                    }

                    trade_index += 1;

                    // Progress every 10k trades
                    if trade_index % 10_000 == 0 {
                        let percent = (trade_index as f64 / trades.len() as f64) * 100.0;
                        println!("\n📊 Progress: {}/{} ({:.1}%)", trade_index, trades.len(), percent);
                    }
                } else if trade_index >= trades.len() {
                    println!("\n🎉 Test data complete!");
                    break;
                }
            }
        }
    }

    println!(
        "📈 Test results: {} range bars from {} trades",
        bar_count, trade_index
    );

    // Terminal cleanup not needed without raw mode
    Ok(())
}
