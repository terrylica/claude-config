//! Comprehensive 25 BPS Threshold Validation
//!
//! Validates that range bars close at EXACTLY ±0.25% (25 BPS) from open price.
//! Tests with real market data to ensure threshold compliance.

use rangebar::data::HistoricalDataLoader;
use rangebar::range_bars::ExportRangeBarProcessor;
use std::collections::HashMap;

#[derive(Debug, Clone)]
struct ThresholdValidation {
    bar_index: usize,
    open: f64,
    close: f64,
    high: f64,
    low: f64,
    expected_upper: f64,
    expected_lower: f64,
    actual_movement_pct: f64,
    _threshold_bps: u32,
    breach_type: String,
    is_valid: bool,
    error_message: Option<String>,
}

impl ThresholdValidation {
    fn new(
        bar_index: usize,
        open: f64,
        close: f64,
        high: f64,
        low: f64,
        threshold_bps: u32,
    ) -> Self {
        let threshold_pct = threshold_bps as f64 / 100_000.0; // Convert 0.1 BPS units to decimal percentage (e.g., 250 → 0.0025 = 0.25%)
        let expected_upper = open * (1.0 + threshold_pct);
        let expected_lower = open * (1.0 - threshold_pct);

        // Determine which threshold was breached
        let (breach_type, actual_movement_pct, _breached_value) = if close >= expected_upper {
            ("UPPER", ((close - open) / open) * 100.0, close)
        } else if close <= expected_lower {
            ("LOWER", ((close - open) / open) * 100.0, close)
        } else {
            ("NONE", ((close - open) / open) * 100.0, close)
        };

        // Validation logic - range bars MUST breach threshold to close
        let (is_valid, error_message) = match breach_type {
            "UPPER" => {
                if close >= expected_upper && (high >= expected_upper || low <= expected_lower) {
                    (true, None)
                } else {
                    (
                        false,
                        Some(format!(
                            "Upper breach but close ({:.8}) < threshold ({:.8})",
                            close, expected_upper
                        )),
                    )
                }
            }
            "LOWER" => {
                if close <= expected_lower && (high >= expected_upper || low <= expected_lower) {
                    (true, None)
                } else {
                    (
                        false,
                        Some(format!(
                            "Lower breach but close ({:.8}) > threshold ({:.8})",
                            close, expected_lower
                        )),
                    )
                }
            }
            "NONE" => (
                false,
                Some(format!(
                    "Range bar closed without threshold breach: movement {:.4}%",
                    actual_movement_pct
                )),
            ),
            _ => unreachable!(),
        };

        Self {
            bar_index,
            open,
            close,
            high,
            low,
            expected_upper,
            expected_lower,
            actual_movement_pct,
            _threshold_bps: threshold_bps,
            breach_type: breach_type.to_string(),
            is_valid,
            error_message,
        }
    }

    fn print_validation(&self) {
        let status = if self.is_valid {
            "✅ VALID"
        } else {
            "❌ INVALID"
        };
        println!(
            "Bar #{}: {} | Open: {:.2} | Close: {:.2} | Movement: {:.4}% | Breach: {}",
            self.bar_index,
            status,
            self.open,
            self.close,
            self.actual_movement_pct,
            self.breach_type
        );

        if let Some(error) = &self.error_message {
            println!("  ERROR: {}", error);
        }

        println!(
            "  Thresholds: Upper {:.8} | Lower {:.8}",
            self.expected_upper, self.expected_lower
        );
        println!("  High: {:.8} | Low: {:.8}", self.high, self.low);
        println!();
    }
}

struct ValidationSummary {
    total_bars: usize,
    valid_bars: usize,
    invalid_bars: usize,
    upper_breaches: usize,
    lower_breaches: usize,
    no_breaches: usize,
    avg_movement_pct: f64,
    max_error_pct: f64,
    min_error_pct: f64,
}

impl ValidationSummary {
    fn new(validations: &[ThresholdValidation]) -> Self {
        let total_bars = validations.len();
        let valid_bars = validations.iter().filter(|v| v.is_valid).count();
        let invalid_bars = total_bars - valid_bars;

        let upper_breaches = validations
            .iter()
            .filter(|v| v.breach_type == "UPPER")
            .count();
        let lower_breaches = validations
            .iter()
            .filter(|v| v.breach_type == "LOWER")
            .count();
        let no_breaches = validations
            .iter()
            .filter(|v| v.breach_type == "NONE")
            .count();

        let movements: Vec<f64> = validations
            .iter()
            .map(|v| v.actual_movement_pct.abs())
            .collect();
        let avg_movement_pct = movements.iter().sum::<f64>() / movements.len() as f64;
        let max_error_pct = movements.iter().fold(0.0f64, |a, &b| a.max(b));
        let min_error_pct = movements.iter().fold(f64::INFINITY, |a, &b| a.min(b));

        Self {
            total_bars,
            valid_bars,
            invalid_bars,
            upper_breaches,
            lower_breaches,
            no_breaches,
            avg_movement_pct,
            max_error_pct,
            min_error_pct,
        }
    }

    fn print_summary(&self) {
        println!("🔍 THRESHOLD VALIDATION SUMMARY");
        println!("================================");
        println!("Total Range Bars: {}", self.total_bars);
        println!(
            "Valid Bars: {} ({:.1}%)",
            self.valid_bars,
            (self.valid_bars as f64 / self.total_bars as f64) * 100.0
        );
        println!(
            "Invalid Bars: {} ({:.1}%)",
            self.invalid_bars,
            (self.invalid_bars as f64 / self.total_bars as f64) * 100.0
        );
        println!();
        println!("Breach Distribution:");
        println!(
            "  Upper Breaches: {} ({:.1}%)",
            self.upper_breaches,
            (self.upper_breaches as f64 / self.total_bars as f64) * 100.0
        );
        println!(
            "  Lower Breaches: {} ({:.1}%)",
            self.lower_breaches,
            (self.lower_breaches as f64 / self.total_bars as f64) * 100.0
        );
        println!(
            "  No Breaches: {} ({:.1}%)",
            self.no_breaches,
            (self.no_breaches as f64 / self.total_bars as f64) * 100.0
        );
        println!();
        println!("Movement Statistics:");
        println!("  Average Movement: {:.4}%", self.avg_movement_pct);
        println!("  Max Movement: {:.4}%", self.max_error_pct);
        println!("  Min Movement: {:.4}%", self.min_error_pct);
        println!("  Expected: 0.25% (25 BPS)");
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let symbol = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "BTCUSDT".to_string());
    let threshold_bps = 250u32; // 250 units × 0.1 BPS = 25 BPS = 0.25%

    println!("🔬 25 BPS Threshold Validation for {}", symbol);
    println!("====================================");
    println!("Expected threshold: ±{} BPS (±0.25%)", threshold_bps / 10); // Convert 0.1 BPS units to BPS
    println!();

    // Load recent day of data
    let loader = HistoricalDataLoader::new(&symbol);
    let trades = loader.load_recent_day().await?;
    println!("📊 Loaded {} trades", trades.len());

    // Process trades into range bars
    let mut processor = ExportRangeBarProcessor::new(threshold_bps);
    processor.process_trades_continuously(&trades);
    let bars = processor.get_all_completed_bars();

    println!("📈 Generated {} range bars", bars.len());

    if bars.is_empty() {
        println!(
            "⚠️ No range bars generated - market too stable for {} BPS threshold",
            threshold_bps / 10
        );
        return Ok(());
    }

    // Validate each range bar
    let mut validations = Vec::new();
    let mut random_samples = HashMap::new();

    // Random sampling indices (10 bars or all if less than 10)
    let sample_size = std::cmp::min(10, bars.len());
    let sample_step = if bars.len() > sample_size {
        bars.len() / sample_size
    } else {
        1
    };

    for (i, bar) in bars.iter().enumerate() {
        let validation = ThresholdValidation::new(
            i + 1,
            bar.open.to_f64(),
            bar.close.to_f64(),
            bar.high.to_f64(),
            bar.low.to_f64(),
            threshold_bps,
        );

        // Collect samples for detailed printing
        if i % sample_step == 0 || i < 5 || i >= bars.len() - 5 {
            random_samples.insert(i, validation.clone());
        }

        validations.push(validation);
    }

    // Print sample validations
    println!("\n📋 SAMPLE VALIDATIONS (Random + First/Last 5):");
    println!("================================================");
    let mut sample_keys: Vec<_> = random_samples.keys().collect();
    sample_keys.sort();

    for &key in sample_keys {
        random_samples[&key].print_validation();
    }

    // Print summary
    let summary = ValidationSummary::new(&validations);
    summary.print_summary();

    // Critical validation
    if summary.invalid_bars > 0 {
        println!(
            "\n🚨 CRITICAL: {} bars failed threshold validation!",
            summary.invalid_bars
        );
        println!("Range bar algorithm may have regression in threshold calculation.");

        // Print first few invalid bars for debugging
        println!("\nFirst 3 invalid bars:");
        for (i, validation) in validations.iter().enumerate() {
            if !validation.is_valid {
                validation.print_validation();
                if i >= 2 {
                    break;
                }
            }
        }

        std::process::exit(1);
    } else {
        println!(
            "\n✅ SUCCESS: All {} range bars correctly breach ±{} BPS threshold!",
            bars.len(),
            threshold_bps / 10
        );
    }

    Ok(())
}
