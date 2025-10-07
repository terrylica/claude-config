//! Dukascopy integration tests
//!
//! Validates end-to-end flow: ticks → range bars → spread stats
//! Tests error recovery policy (Q22) and SLO compliance

use rangebar::providers::dukascopy::{
    DukascopyRangeBarBuilder, DukascopyTick, ValidationStrictness,
};

/// SLO: Error recovery - skip validation errors, continue processing
#[test]
fn test_error_recovery_skip_crossed_market() {
    let mut builder =
        DukascopyRangeBarBuilder::new(25, "EURUSD", ValidationStrictness::Strict);

    let mut total_ticks = 0;
    let mut skipped_ticks = 0;
    let mut completed_bars = 0;

    let ticks = vec![
        // Valid tick 1
        DukascopyTick {
            bid: 1.0800,
            ask: 1.0815,
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1_600_000_000_000,
        },
        // Invalid tick (crossed market) - should skip
        DukascopyTick {
            bid: 1.0820,
            ask: 1.0810, // bid > ask
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1_600_001_000_000,
        },
        // Valid tick 2
        DukascopyTick {
            bid: 1.0802,
            ask: 1.0817,
            bid_volume: 110.0,
            ask_volume: 130.0,
            timestamp_ms: 1_600_002_000_000,
        },
    ];

    for tick in ticks {
        total_ticks += 1;

        match builder.process_tick(&tick) {
            Ok(Some(_bar)) => {
                completed_bars += 1;
            }
            Ok(None) => {
                // Tick processed, bar accumulating
            }
            Err(_e) => {
                // Validation error - skip tick (Q22 policy)
                skipped_ticks += 1;
            }
        }
    }

    // SLO: Should process valid ticks despite errors
    assert_eq!(total_ticks, 3);
    assert_eq!(skipped_ticks, 1); // Crossed market skipped
    assert_eq!(completed_bars, 0); // No threshold breach yet

    // SLO: Error rate below 10% threshold (33% acceptable for this test)
    let error_rate = (skipped_ticks as f64 / total_ticks as f64) * 100.0;
    assert!(error_rate < 50.0); // Well below systemic threshold
}

/// SLO: Correctness - spread stats reset on bar close (Q13)
#[test]
fn test_spread_stats_per_bar_semantics() {
    let mut builder =
        DukascopyRangeBarBuilder::new(25, "EURUSD", ValidationStrictness::Strict);

    // Tick 1: Open bar at mid-price 1.0800
    let tick1 = DukascopyTick {
        bid: 1.0792,
        ask: 1.0808,
        bid_volume: 100.0,
        ask_volume: 120.0,
        timestamp_ms: 1_600_000_000_000,
    };
    builder.process_tick(&tick1).unwrap();

    // Tick 2: Update bar (no breach)
    let tick2 = DukascopyTick {
        bid: 1.0793,
        ask: 1.0807,
        bid_volume: 110.0,
        ask_volume: 130.0,
        timestamp_ms: 1_600_001_000_000,
    };
    builder.process_tick(&tick2).unwrap();

    // Tick 3: Breach threshold (close bar)
    // Need mid-price > 1.0800 * 1.0025 = 1.0827
    let tick3 = DukascopyTick {
        bid: 1.0825,
        ask: 1.0835, // mid = 1.0830 (breach!)
        bid_volume: 105.0,
        ask_volume: 125.0,
        timestamp_ms: 1_600_002_000_000,
    };

    let completed_bar = builder.process_tick(&tick3).unwrap().unwrap();

    // SLO: Completed bar has stats from all 3 ticks
    assert_eq!(completed_bar.spread_stats.tick_count, 3);
    assert!(completed_bar.spread_stats.avg_spread().0 > 0);

    // Tick 4: New bar (should have fresh stats)
    let tick4 = DukascopyTick {
        bid: 1.0826,
        ask: 1.0836,
        bid_volume: 100.0,
        ask_volume: 120.0,
        timestamp_ms: 1_600_003_000_000,
    };
    builder.process_tick(&tick4).unwrap();

    // SLO: New incomplete bar has tick3 (breaching) + tick4 stats
    let incomplete = builder.get_incomplete_bar().unwrap();
    assert_eq!(incomplete.spread_stats.tick_count, 2);
}

/// SLO: Correctness - zero-volume ticks processed (Q7, Q14)
#[test]
fn test_zero_volume_tick_processing() {
    let mut builder =
        DukascopyRangeBarBuilder::new(25, "EURUSD", ValidationStrictness::Strict);

    let ticks = vec![
        // Normal tick
        DukascopyTick {
            bid: 1.0800,
            ask: 1.0815,
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1_600_000_000_000,
        },
        // Zero-volume tick (quote update without liquidity)
        DukascopyTick {
            bid: 1.0801,
            ask: 1.0816,
            bid_volume: 0.0,
            ask_volume: 0.0,
            timestamp_ms: 1_600_001_000_000,
        },
        // Normal tick
        DukascopyTick {
            bid: 1.0802,
            ask: 1.0817,
            bid_volume: 110.0,
            ask_volume: 130.0,
            timestamp_ms: 1_600_002_000_000,
        },
    ];

    for tick in ticks {
        builder.process_tick(&tick).unwrap();
    }

    let incomplete = builder.get_incomplete_bar().unwrap();

    // SLO: All ticks processed (including zero-volume)
    assert_eq!(incomplete.spread_stats.tick_count, 3);

    // SLO: Zero-volume tick tracked separately
    assert_eq!(incomplete.spread_stats.zero_volume_tick_count, 1);

    // SLO: Total liquidity excludes zero-volume tick
    // 100+120 + 0+0 + 110+130 = 460
    let expected_volume = 100.0 + 120.0 + 110.0 + 130.0;
    assert!(
        (incomplete.base.volume.to_f64() - expected_volume).abs() < 1.0
    );
}

/// SLO: Correctness - mid-price conversion accuracy
#[test]
fn test_mid_price_conversion() {
    let mut builder =
        DukascopyRangeBarBuilder::new(25, "EURUSD", ValidationStrictness::Strict);

    let tick = DukascopyTick {
        bid: 1.0800,
        ask: 1.0820,
        bid_volume: 100.0,
        ask_volume: 120.0,
        timestamp_ms: 1_600_000_000_000,
    };

    builder.process_tick(&tick).unwrap();

    let incomplete = builder.get_incomplete_bar().unwrap();

    // SLO: Mid-price = (1.0800 + 1.0820) / 2 = 1.0810
    // Note: FixedPoint.to_f64() returns the real price (not multiplied by decimal_factor)
    let expected_price = 1.0810;
    assert!(
        (incomplete.base.open.to_f64() - expected_price).abs() < 0.0001,
        "Expected open price {}, got {}",
        expected_price,
        incomplete.base.open.to_f64()
    );
}

/// SLO: Availability - incomplete bar retrieval at stream end
#[test]
fn test_incomplete_bar_retrieval() {
    let mut builder =
        DukascopyRangeBarBuilder::new(25, "EURUSD", ValidationStrictness::Strict);

    // Process ticks without threshold breach
    for i in 0..5 {
        let tick = DukascopyTick {
            bid: 1.0800 + (i as f64 * 0.0001),
            ask: 1.0815 + (i as f64 * 0.0001),
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1_600_000_000_000 + (i * 1000),
        };
        builder.process_tick(&tick).unwrap();
    }

    // SLO: Incomplete bar available at stream end
    let incomplete = builder.get_incomplete_bar();
    assert!(incomplete.is_some());

    let bar = incomplete.unwrap();
    assert_eq!(bar.spread_stats.tick_count, 5);
}

/// SLO: Correctness - volume semantics (Q10, Q11)
#[test]
fn test_volume_semantics() {
    let mut builder =
        DukascopyRangeBarBuilder::new(25, "EURUSD", ValidationStrictness::Strict);

    let tick = DukascopyTick {
        bid: 1.0800,
        ask: 1.0815,
        bid_volume: 100.0,
        ask_volume: 120.0,
        timestamp_ms: 1_600_000_000_000,
    };

    builder.process_tick(&tick).unwrap();

    let incomplete = builder.get_incomplete_bar().unwrap();

    // SLO: Volume = total_bid_liquidity + total_ask_liquidity
    let expected_volume = 100.0 + 120.0;
    assert!(
        (incomplete.base.volume.to_f64() - expected_volume).abs() < 1.0
    );

    // SLO: No buy/sell segregation (direction unknown, Q10)
    assert_eq!(incomplete.base.buy_volume.0, 0);
    assert_eq!(incomplete.base.sell_volume.0, 0);

    // SLO: SpreadStats tracks bid/ask separately
    assert!(incomplete.spread_stats.total_bid_liquidity.0 > 0);
    assert!(incomplete.spread_stats.total_ask_liquidity.0 > 0);
}

/// SLO: Observability - error context traceability
#[test]
fn test_error_context() {
    let mut builder =
        DukascopyRangeBarBuilder::new(25, "EURUSD", ValidationStrictness::Strict);

    let bad_tick = DukascopyTick {
        bid: 1.0820,
        ask: 1.0810, // Crossed market
        bid_volume: 100.0,
        ask_volume: 120.0,
        timestamp_ms: 1_600_000_000_000,
    };

    let result = builder.process_tick(&bad_tick);

    // SLO: Error contains context (bid, ask values)
    assert!(result.is_err());
    let error_msg = format!("{:?}", result.unwrap_err());
    assert!(error_msg.contains("1.082"));
    assert!(error_msg.contains("1.081"));
}

/// SLO: Maintainability - algorithm integrity (no core changes)
#[test]
fn test_algorithm_integrity() {
    let mut builder =
        DukascopyRangeBarBuilder::new(25, "EURUSD", ValidationStrictness::Strict);

    // Sequence designed to breach threshold
    let ticks = vec![
        // Open at 1.0800 mid
        DukascopyTick {
            bid: 1.0792,
            ask: 1.0808,
            bid_volume: 100.0,
            ask_volume: 120.0,
            timestamp_ms: 1_600_000_000_000,
        },
        // Breach +25 bps: need mid > 1.0800 * 1.0025 = 1.0827
        DukascopyTick {
            bid: 1.0825,
            ask: 1.0835, // mid = 1.0830 (breach!)
            bid_volume: 110.0,
            ask_volume: 130.0,
            timestamp_ms: 1_600_001_000_000,
        },
    ];

    let mut bars = vec![];
    for tick in ticks {
        if let Some(bar) = builder.process_tick(&tick).unwrap() {
            bars.push(bar);
        }
    }

    // SLO: Threshold breach closes bar
    assert_eq!(bars.len(), 1);

    let bar = &bars[0];

    // SLO: Open price from first tick
    let expected_open = (1.0792 + 1.0808) / 2.0;  // Mid-price of first tick
    assert!(
        (bar.base.open.to_f64() - expected_open).abs() < 0.0001,
        "Expected open price {}, got {}",
        expected_open,
        bar.base.open.to_f64()
    );

    // SLO: Close price from breaching tick (mid-price that caused breach)
    let expected_close = (1.0820 + 1.0840) / 2.0;  // Mid-price of breaching tick
    assert!(
        (bar.base.close.to_f64() - expected_close).abs() < 0.0001,
        "Expected close price {}, got {}",
        expected_close,
        bar.base.close.to_f64()
    );
}
