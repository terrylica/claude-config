# EURUSD Range Bar Adversarial Audit Plan

**Purpose**: Validate temporal integrity and non-lookahead bias of Dukascopy EURUSD range bar construction

**Status**: Ready for execution
**Test File**: `tests/dukascopy_eurusd_adversarial_audit.rs`

---

## Motivation

Dukascopy integration (v2.2.0) introduces bid/ask quote data → mid-price conversion for range bars. Unlike Binance aggTrades (actual executed trades), Dukascopy provides:
- **Bid/Ask quotes** (not trades)
- **Spread statistics** (unique to quote-based data)
- **Different microstructure** (Q19-Q22 design decisions)

**Risk**: Subtle bugs in bid/ask → mid conversion or spread handling could introduce lookahead bias.

---

## Audit Strategies

### Strategy 1: Known-Answer Tests (Synthetic EURUSD)

**Approach**: Create synthetic EURUSD ticks with predetermined properties

**Tests**:
- `audit_1_synthetic_eurusd_single_bar` - Verify exact bar count with known thresholds
- `audit_2_synthetic_eurusd_threshold_sensitivity` - 25bps should produce >= bars than 100bps

**Why**: Eliminates data quality concerns, isolates algorithm logic

**Example**:
```rust
// Known: EURUSD @ 1.1000, 25bps threshold = 0.00275 move
// Tick 1: mid = 1.1000 (open bar)
// Tick 2: mid = 1.1010 (within threshold)
// Tick 3: mid = 1.10275 (BREACH → close bar)
// Expected: Exactly 1 bar, close = 1.10275
```

---

### Strategy 2: Temporal Integrity Validation

**Approach**: Verify fundamental temporal constraints

**Tests**:
- `audit_3_temporal_integrity_monotonic_timestamps` - bar[i].open_time >= bar[i-1].close_time
- `audit_4_breach_inclusion_rule` - Breaching tick MUST be in closing bar (critical!)

**Why**: Catches off-by-one errors, timestamp corruption, lookahead violations

**Critical Property**:
```
IF tick causes breach THEN tick.timestamp = bar.close_time
```

---

### Strategy 3: Edge Case Handling

**Approach**: Test error recovery and data quality filters

**Tests**:
- `audit_5_crossed_market_rejection` - bid > ask should be skipped (Q22 skip policy)
- `audit_6_spread_statistics_sanity` - EURUSD spreads < 1% (typically 0.1-2 pips)

**Why**: Validates Q22 decision (skip-on-error vs fail-fast)

**Expected Behavior**:
- Crossed market → Skip tick, log warning, continue
- Zero spread → Valid (some exchanges show 0 spread momentarily)
- Extreme spread (>10%) → Flag in Strict mode

---

### Strategy 4: Non-Lookahead Bias Verification

**Approach**: Prove threshold calculated ONLY from bar open price

**Test**:
- `audit_8_non_lookahead_bias_threshold_calculation`

**Critical Invariant**:
```
high_threshold = open + (open * threshold_bps / 10000)
low_threshold = open - (open * threshold_bps / 10000)

// NOT:
// high_threshold = high + (high * threshold_bps / 10000)  ❌ LOOKAHEAD!
```

**Scenario**:
```
Bar opens @ 1.1000
Tick moves to 1.1010 (new high)
Threshold STILL 1.1000 ± 0.00275
NOT 1.1010 ± 0.002525 ← would be lookahead bias
```

---

### Strategy 5: Real-World Statistical Properties

**Approach**: Fetch live EURUSD data, validate distributions

**Test**:
- `audit_7_real_eurusd_statistical_properties` (requires network, `--ignored` by default)

**Validation Criteria**:
1. **Threshold Sensitivity**: bars(25bps) >= bars(100bps)
2. **Spread Bounds**: avg_spread < 0.005 (50 pips max for EURUSD)
3. **Bar Count vs Volatility**: Volatile hours (EU session) > quiet hours (Asia)
4. **Temporal Monotonicity**: No timestamp regressions

**Data Source**:
```
Instrument: EURUSD
Date: 2025-01-15
Hour: 14:00 GMT (EU session - typically 500-2000 ticks/hour)
Expected: 50-200 bars @ 25bps (depending on volatility)
```

---

## Execution Plan

### Phase 1: Run Local Tests (Synthetic + Edge Cases)

```bash
cargo test --test dukascopy_eurusd_adversarial_audit
```

**Expected**: All 7 tests PASS (audit_7 skipped)

---

### Phase 2: Run Real-World Validation (Network Required)

```bash
cargo test --test dukascopy_eurusd_adversarial_audit audit_7 -- --ignored
```

**Expected**:
- Fetch ~500-2000 EURUSD ticks
- Produce 50-200 bars @ 25bps
- Spread statistics within normal bounds

---

### Phase 3: Differential Testing (Future Enhancement)

**Approach**: Compare Dukascopy implementation vs reference implementation

**Setup**:
1. Implement reference EURUSD range bar builder in Python (using pandas)
2. Use same ticks from Dukascopy
3. Compare outputs (bar count, OHLC, timestamps)

**Acceptance**:
- Bar counts match exactly
- OHLC values within 0.00001 (1 pip tolerance for floating point)
- No timestamp mismatches

---

### Phase 4: Continuous Monitoring (Production)

**Approach**: Run audit tests in CI/CD on every commit

**GitHub Actions**:
```yaml
- name: EURUSD Audit Tests
  run: cargo test --test dukascopy_eurusd_adversarial_audit
```

**Alert Conditions**:
- Any audit test fails
- Spread statistics out of bounds
- Temporal integrity violations

---

## Success Criteria

### Must Pass (P0 - Critical)
- ✅ Audit 4: Breach inclusion rule
- ✅ Audit 8: Non-lookahead bias verification

### Should Pass (P1 - High Priority)
- ✅ Audit 1-3: Synthetic known-answer tests
- ✅ Audit 5-6: Edge case handling

### Nice to Have (P2 - Optional)
- ✅ Audit 7: Real-world statistical properties (network dependent)

---

## Known Limitations

1. **No cross-validation with other providers** - Would need overlapping EURUSD data from Binance (BTCUSD as proxy?)
2. **Synthetic tests only cover happy path** - Need fuzzing for extreme edge cases
3. **Single instrument focus** - EURUSD only (but representative of forex pairs)

---

## Future Enhancements

### Enhancement 1: Property-Based Testing (Hypothesis/QuickCheck)

```rust
#[proptest]
fn prop_threshold_monotonicity(
    #[strategy(25u32..200u32)] threshold_bps: u32,
    #[strategy(valid_eurusd_ticks())] ticks: Vec<DukascopyTick>
) {
    // Property: Higher threshold → Same or fewer bars
    let bars_low = build_bars(ticks.clone(), threshold_bps);
    let bars_high = build_bars(ticks, threshold_bps * 2);
    prop_assert!(bars_high.len() <= bars_low.len());
}
```

### Enhancement 2: Chaos Engineering

- Inject random delays, missing ticks, duplicate ticks
- Verify graceful degradation
- No panics, no silent data corruption

### Enhancement 3: Multi-Instrument Validation

- Test GBPUSD, USDJPY, XAUUSD (different spreads, volatilities)
- Crypto: BTCUSD, ETHUSD (higher spreads)
- Commodities: WTI, Brent (different decimal factors)

---

## Regression Detection

### Before Each Commit

```bash
# Run full audit suite
cargo test --test dukascopy_eurusd_adversarial_audit

# Run with strict clippy
cargo clippy --all-features -- -D warnings

# Check for TODOs/FIXMEs in Dukascopy code
rg "TODO|FIXME" src/providers/dukascopy/
```

### Post-Deployment Monitoring

```python
# Automated daily validation
import dukascopy_client
from rangebar import DukascopyRangeBarBuilder

# Fetch yesterday's EURUSD data
ticks = dukascopy_client.fetch_day("EURUSD", date.today() - timedelta(days=1))

# Build range bars
bars = DukascopyRangeBarBuilder(25, "EURUSD").process_all(ticks)

# Validate statistical properties
assert 0.00001 < avg_spread(bars) < 0.005, "Spread out of bounds"
assert is_monotonic([b.open_time for b in bars]), "Timestamp violation"
assert all(b.high >= b.close >= b.low for b in bars), "OHLC integrity"
```

---

## References

- **Dukascopy Implementation**: `docs/planning/research/dukascopy-implementation-complete.md`
- **Q19-Q22 Design Decisions**: Mid-price conversion, spread stats, error recovery
- **Range Bar Algorithm**: `CLAUDE.md` - Fixed thresholds from bar OPEN
