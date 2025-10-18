//! Historical Range Bar Visualizer with Time-Aware Playback
//!
//! Loads 3 months of historical BTCUSDT aggTrades data and replays with
//! accelerated timing to visualize range bar formation. Uses single-line
//! terminal updates until range bars complete.

use std::io::Write;
use std::time::{Duration, Instant};

use crossterm::event::{Event, KeyCode, KeyEventKind, poll, read};
use crossterm::terminal::{disable_raw_mode, enable_raw_mode};
use tokio::signal;

use rangebar::AggTrade;
use rangebar::data::HistoricalDataLoader;
use rangebar::range_bars::ExportRangeBarProcessor;

/// Format duration in microseconds to human-readable string
fn format_duration(duration_microseconds: i64) -> String {
    if duration_microseconds < 0 {
        return "0s".to_string();
    }

    let total_milliseconds = duration_microseconds / 1000;
    let total_seconds = total_milliseconds / 1000;
    let milliseconds = total_milliseconds % 1000;

    if total_seconds == 0 {
        return format!("{}ms", total_milliseconds);
    }

    let hours = total_seconds / 3600;
    let minutes = (total_seconds % 3600) / 60;
    let seconds = total_seconds % 60;

    let mut parts = Vec::new();

    if hours > 0 {
        parts.push(format!("{}h", hours));
    }
    if minutes > 0 {
        parts.push(format!("{}m", minutes));
    }
    if seconds > 0 || parts.is_empty() {
        if milliseconds > 0 && parts.is_empty() && seconds < 10 {
            // Show decimals for short durations
            parts.push(format!(
                "{:.1}s",
                seconds as f64 + milliseconds as f64 / 1000.0
            ));
        } else {
            parts.push(format!("{}s", seconds));
        }
    }

    parts.join(" ")
}

/// Time-aware playback engine with acceleration
struct PlaybackEngine {
    agg_trades: Vec<AggTrade>,
    current_index: usize,
    acceleration_factor: f64,
    paused: bool,
}

impl PlaybackEngine {
    fn new(agg_trades: Vec<AggTrade>, acceleration_factor: f64) -> Self {
        Self {
            agg_trades,
            current_index: 0,
            acceleration_factor,
            paused: false,
        }
    }

    fn set_speed(&mut self, factor: f64) -> String {
        self.acceleration_factor = factor;
        format!("🚀 Speed: {:.0}x", factor)
    }

    fn toggle_pause(&mut self) -> String {
        self.paused = !self.paused;
        if self.paused {
            "⏸️  Paused".to_string()
        } else {
            format!("▶️  Resumed at {:.0}x speed", self.acceleration_factor)
        }
    }

    async fn next_agg_trade(&mut self) -> Option<AggTrade> {
        if self.paused || self.current_index >= self.agg_trades.len() {
            return None;
        }

        let agg_trade = self.agg_trades[self.current_index].clone();

        // Calculate time delta to next aggTrade
        if self.current_index + 1 < self.agg_trades.len() {
            let current_timestamp = self.agg_trades[self.current_index].timestamp;
            let next_timestamp = self.agg_trades[self.current_index + 1].timestamp;
            let delta_microseconds = (next_timestamp - current_timestamp) as f64;

            // Apply acceleration and sleep (keep in microseconds)
            let accelerated_delay_microseconds = delta_microseconds / self.acceleration_factor;
            if accelerated_delay_microseconds > 100.0 {
                // 0.1ms minimum
                tokio::time::sleep(Duration::from_micros(accelerated_delay_microseconds as u64))
                    .await;
            }
        }

        self.current_index += 1;
        Some(agg_trade)
    }

    fn progress(&self) -> (usize, usize, f64) {
        let percent = (self.current_index as f64 / self.agg_trades.len() as f64) * 100.0;
        (self.current_index, self.agg_trades.len(), percent)
    }
}

/// Terminal display manager with rate limiting
struct TerminalDisplay {
    bar_count: u32,
    agg_trade_count: u64,
    current_bar_agg_trades: u64,
    current_bar_open: Option<f64>,
    last_update: Instant,
    last_price: f64,
    update_throttle: Duration,
    pending_updates: bool,
    up_bars: u32,
    down_bars: u32,
}

impl TerminalDisplay {
    fn new() -> Self {
        Self {
            bar_count: 0,
            agg_trade_count: 0,
            current_bar_agg_trades: 0,
            current_bar_open: None,
            last_update: Instant::now(),
            last_price: 0.0,
            update_throttle: Duration::from_millis(50), // Max 20 updates/sec
            pending_updates: false,
            up_bars: 0,
            down_bars: 0,
        }
    }

    fn update_building_bar(&mut self, price: f64) {
        self.agg_trade_count += 1;
        self.current_bar_agg_trades += 1;
        self.last_price = price;

        if self.current_bar_open.is_none() {
            self.current_bar_open = Some(price);
        }

        // Rate limit terminal updates to prevent formatting issues
        let now = Instant::now();
        if now.duration_since(self.last_update) >= self.update_throttle {
            self.render_building_bar();
            self.last_update = now;
            self.pending_updates = false;
        } else {
            self.pending_updates = true;
        }
    }

    fn render_building_bar(&self) {
        // Clear current line completely before writing new content
        print!("\r\x1b[K"); // Clear entire line
        print!(
            "Building bar #{}: {} aggTrades, current: ${:.2}, open: ${:.2}",
            self.bar_count + 1,
            self.current_bar_agg_trades,
            self.last_price,
            self.current_bar_open.unwrap_or(self.last_price)
        );
        std::io::stdout().flush().unwrap();
    }

    fn force_update(&mut self) {
        if self.pending_updates {
            self.render_building_bar();
            self.last_update = Instant::now();
            self.pending_updates = false;
        }
    }

    fn complete_range_bar(
        &mut self,
        open: f64,
        high: f64,
        low: f64,
        close: f64,
        volume: f64,
        open_time: i64,
        close_time: i64,
    ) {
        // Ensure any pending updates are rendered first
        self.force_update();

        self.bar_count += 1;

        // Determine direction and track statistics
        let (direction, is_up) = if close > open {
            ("\x1b[32m↑\x1b[0m", true) // Green up arrow
        } else {
            ("\x1b[31m↓\x1b[0m", false) // Red down arrow
        };

        if is_up {
            self.up_bars += 1;
        } else {
            self.down_bars += 1;
        }

        // Calculate duration (real market time) - now in microseconds
        let duration_microseconds = close_time - open_time;
        let duration_str = format_duration(duration_microseconds);

        // Clear current line and print completed bar with smart alignment
        println!(
            "\r\x1b[K{} BAR {:>4} • O:{:.4} H:{:.4} L:{:.4} C:{:.4} • Vol:{:>12.2} • aggTrades:{:>6} • {:>10}",
            direction,
            self.bar_count,
            open,
            high,
            low,
            close,
            volume,
            self.current_bar_agg_trades,
            duration_str
        );

        // Reset for next bar
        self.current_bar_agg_trades = 0;
        self.current_bar_open = None;
        self.last_update = Instant::now();
        self.pending_updates = false;
    }

    fn print_message(&mut self, message: &str) {
        // Clear current line and print message on new line
        self.force_update();
        println!("\r\x1b[K\n{}", message);
        self.last_update = Instant::now();
        self.pending_updates = false;
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();

    // Parse command line arguments: [symbol] [market_type]
    let symbol = args.get(1).map(|s| s.as_str()).unwrap_or("DOGEUSDT");
    let market_type = args.get(2).map(|s| s.as_str()).unwrap_or("um"); // Back to UM for performance

    // Validate market type
    match market_type {
        "spot" | "um" | "cm" => {}
        _ => {
            eprintln!(
                "Error: market_type must be 'spot', 'um', or 'cm', got '{}'",
                market_type
            );
            eprintln!("Usage: {} [symbol] [market_type]", args[0]);
            eprintln!("  symbol: Trading symbol (default: DOGEUSDT)");
            eprintln!("  market_type: spot (default), um (UM Futures), cm (CM Futures)");
            std::process::exit(1);
        }
    }

    println!(
        "🚀 Historical Range Bar Visualizer - {} ({} market, 25 BPS)",
        symbol.to_uppercase(),
        market_type.to_uppercase()
    );
    println!("=========================================================================");
    println!("Controls: q=quit, +=faster, -=slower, p=pause");
    println!("Note: Duration shows real market time (spot: hours/days, UM: minutes/hours)");
    println!("");

    // Try to enable raw mode for keyboard input (optional for speed controls)
    let raw_mode_enabled = enable_raw_mode().is_ok();
    if !raw_mode_enabled {
        println!("⚠️ Keyboard controls disabled (terminal not interactive)");
    }

    // Load 2 days back of historical aggTrades data for testing
    let loader = HistoricalDataLoader::new_with_market(symbol, market_type);
    let agg_trades = loader.load_historical_range(2).await?;

    // Initialize components
    let mut playback = PlaybackEngine::new(agg_trades, 10000.0); // 10000x acceleration
    let mut processor = ExportRangeBarProcessor::new(250); // 250 units × 0.1 BPS = 25 BPS = 0.25%
    let mut display = TerminalDisplay::new();

    println!(
        "▶️  Starting playback at {:.0}x speed...\n",
        playback.acceleration_factor
    );

    loop {
        // Handle keyboard input (non-blocking) - only if raw mode is enabled
        if raw_mode_enabled && poll(Duration::from_millis(0)).unwrap_or(false) {
            if let Ok(Event::Key(key)) = read() {
                if key.kind == KeyEventKind::Press {
                    match key.code {
                        KeyCode::Char('q') => {
                            display.print_message("👋 Exiting...");
                            if raw_mode_enabled {
                                disable_raw_mode().ok();
                            }
                            break;
                        }
                        KeyCode::Char('+') | KeyCode::Char('=') => {
                            let new_speed = (playback.acceleration_factor * 2.0).min(100000.0);
                            let message = playback.set_speed(new_speed);
                            display.print_message(&message);
                        }
                        KeyCode::Char('-') => {
                            let new_speed = (playback.acceleration_factor / 2.0).max(1.0);
                            let message = playback.set_speed(new_speed);
                            display.print_message(&message);
                        }
                        KeyCode::Char('p') => {
                            let message = playback.toggle_pause();
                            display.print_message(&message);
                        }
                        _ => {}
                    }
                }
            }
        }

        // Handle Ctrl+C
        tokio::select! {
            _ = signal::ctrl_c() => {
                display.print_message("👋 Shutting down gracefully...");
                if raw_mode_enabled {
                    disable_raw_mode().ok();
                }
                break;
            }
            agg_trade_opt = playback.next_agg_trade() => {
                if let Some(agg_trade) = agg_trade_opt {
                    display.update_building_bar(agg_trade.price.to_f64());

                    // Process aggTrade using continuous processor
                    processor.process_trades_continuously(&[agg_trade]);

                    // Get any newly completed bars
                    let completed_bars = processor.get_all_completed_bars();
                    for bar in completed_bars {
                        display.complete_range_bar(
                            bar.open.to_f64(),
                            bar.high.to_f64(),
                            bar.low.to_f64(),
                            bar.close.to_f64(),
                            bar.volume.to_f64(),
                            bar.open_time,
                            bar.close_time
                        );
                    }

                    // Progress update every 100k aggTrades
                    if display.agg_trade_count % 100_000 == 0 {
                        let (current, total, percent) = playback.progress();
                        let progress_msg = format!("📊 Progress: {}/{} aggTrades ({:.1}%)", current, total, percent);
                        display.print_message(&progress_msg);
                    }
                } else if !playback.paused {
                    // End of data - use display system for clean output
                    display.print_message("🎉 Playback completed!");
                    break;
                }
            }
        }
    }

    let final_stats = format!(
        "📊 Final: {} bars (\x1b[32m↑{}\x1b[0m \x1b[31m↓{}\x1b[0m) from {} aggTrades",
        display.bar_count, display.up_bars, display.down_bars, display.agg_trade_count
    );
    display.print_message(&final_stats);

    // Clean up terminal raw mode if it was enabled
    if raw_mode_enabled {
        disable_raw_mode().ok();
    }
    Ok(())
}
