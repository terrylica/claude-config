# MQL5 Data Ingestion Research (UNVALIDATED)

**Skill Type**: Research Documentation
**Status**: 🔬 RESEARCHED | ⚠️ NOT VALIDATED
**Last Updated**: 2025-10-27
**Research Context**: Exness tick data → MetaTrader 5 ingestion pipeline

---

## ⚠️ CRITICAL: VALIDATION STATUS

**THIS SKILL CONTAINS UNVALIDATED RESEARCH**

- ❌ **NOT tested** in live MetaTrader 5 environment
- ❌ **NOT validated** with real tick data imports
- ❌ **NOT benchmarked** for performance or correctness
- ✅ **Based on** official MQL5 documentation (URLs provided)

**User Responsibility**:

- You MUST validate all specifications before production use
- You MUST test with small datasets first
- You MUST verify official MQL5 documentation currency
- Author assumes NO liability for data loss or trading errors

**When to Graduate This Skill**:

- After successful MT5 test environment setup
- After validation with real exness-data-preprocess output
- After community review of format compliance
- Move validated content to operational skill: `mql5-data-ingestion`

---

## Purpose

This skill documents research findings for converting forex tick data (specifically from `exness-data-preprocess` package) into MetaTrader 5-compatible formats for:

1. **Backtesting** trading strategies on historical tick data
2. **Custom symbol creation** with real tick-level granularity
3. **Strategy Tester** execution with "Every tick based on real ticks" mode

---

## Activation Context

This skill activates when you discuss:

- Converting tick data to MT5 format
- `exness-data-preprocess` output transformation
- MetaTrader 5 custom symbol data requirements
- CSV format for `CustomTicksReplace()` or `CustomRatesUpdate()`
- Tick data validation before MT5 import

**Does NOT activate for**:

- Live trading operations (use validated operational skills)
- Production data pipelines (validate first)
- MQL5 indicator/EA development (use `mql5-article-extractor` skill)

---

## Skill Contents

### 1. Data Format Specifications

**[TICK_FORMAT.md](/Users/terryli/.claude/skills/mql5-data-ingestion-research/TICK_FORMAT.md)**

- CSV structure for tick-level data
- Required fields: `unix_ms`, `bid`, `ask`, `last`, `volume_real`
- Field validation rules and constraints

**[BAR_FORMAT.md](/Users/terryli/.claude/skills/mql5-data-ingestion-research/BAR_FORMAT.md)**

- M1 (1-minute) OHLC bar structure
- Why M1-only (MT5 aggregates higher timeframes automatically)
- Trade volume vs tick volume handling

### 2. Integration Specifications

**[VALIDATION.md](/Users/terryli/.claude/skills/mql5-data-ingestion-research/VALIDATION.md)**

- Pre-import validation checklist
- Common data quality issues
- Automated validation script patterns

**[SOURCES.md](/Users/terryli/.claude/skills/mql5-data-ingestion-research/SOURCES.md)**

- All official MQL5 documentation URLs
- Community forum references
- Version-specific considerations

---

## Key Research Findings

### Finding 1: Tick Data Must Use Millisecond Timestamps

```csv
unix_ms,bid,ask,last,volume_real
1688342627212,1.14175,1.14210,0.00000,0
```

**Why**: `MqlTick.time_msc` is primary; `time` is derived. Using seconds loses sub-second ticks.

**Source**: [`MqlTick` Structure Documentation](https://www.mql5.com/en/docs/constants/structures/mqltick)

### Finding 2: Time MUST Be Strictly Ascending

MT5's `CustomTicksReplace()` **stops processing** at first out-of-order timestamp.

**Implication**: Sort by `unix_ms` BEFORE import, or partial import occurs silently.

**Source**: [`CustomTicksReplace()` Documentation](https://www.mql5.com/en/docs/customsymbols/customticksreplace)

### Finding 3: M1 Bars Only for `CustomRatesUpdate()`

Higher timeframes (M5, H1, D1) are **automatically aggregated** by MT5 from M1 bars.

**Implication**: Don't generate H1 bars manually; provide M1 and let MT5 build the rest.

**Source**: [`CustomRatesUpdate()` Documentation](https://www.mql5.com/en/docs/customsymbols/customratesupdate)

### Finding 4: `FILE_COMMON` for Tester Compatibility

Files in `Terminal\Common\Files` are accessible to both:

- Live terminal
- Strategy Tester

**Implication**: Always use `FILE_COMMON` flag when creating import scripts.

**Source**: [`FileOpen()` Documentation](https://www.mql5.com/en/docs/files/fileopen)

---

## Recommended Workflow (Unvalidated)

### Phase 1: Data Preparation

1. Export tick data from `exness-data-preprocess`:

   ```python
   df = processor.query_ticks("EURUSD", variant="raw_spread", start_date="2024-01-01")
   ```

2. Transform to MT5 CSV format:

   ```python
   # Convert to unix_ms, ensure bid/ask/last columns
   df['unix_ms'] = (df['timestamp'].astype('int64') // 10**6)  # ns → ms
   df = df.sort_values('unix_ms')  # CRITICAL: ascending order
   df[['unix_ms', 'bid', 'ask', 'last', 'volume']].to_csv('ticks.csv', index=False)
   ```

3. Validate format (see [VALIDATION.md](/Users/terryli/.claude/skills/mql5-data-ingestion-research/VALIDATION.md))

### Phase 2: MT5 Import (Requires Validation)

```mq5
// WARNING: Illustrative only, not tested
CustomSymbolCreate("EURUSD.EXNESS", "Custom\\Exness", NULL);
SymbolSelect("EURUSD.EXNESS", true);

// Load via script (see ChatGPT dialogue for full validator)
CustomTicksReplace("EURUSD.EXNESS", from_ms, to_ms, ticks_array);
```

### Phase 3: Strategy Tester Setup

1. Open Strategy Tester
2. Select custom symbol: `EURUSD.EXNESS`
3. Choose: "Every tick based on real ticks"
4. Run backtest

---

## Known Gaps Requiring Validation

### Gap 1: Exness Tick Structure Compatibility

**Question**: Does `exness-data-preprocess` "raw_spread" variant provide:

- Separate `bid` and `ask` columns? (Required)
- Microsecond or nanosecond timestamps? (Need millisecond)
- Volume per tick? (Optional but preferred)

**Validation Needed**: Inspect actual output schema

### Gap 2: Performance at Scale

**Question**: How many ticks can `CustomTicksReplace()` handle per call?

- ChatGPT suggests 500K chunks
- No empirical testing completed

**Validation Needed**: Benchmark with real data

### Gap 3: Custom Symbol Properties

**Question**: What symbol properties must be set for forex custom symbols?

- Digits (5 for EURUSD)
- Contract size
- Tick size
- Sessions

**Validation Needed**: Test default vs explicit configuration

---

## Migration Path: Research → Production

When validated, this content should migrate to:

**New Operational Skill**: `~/.claude/skills/mql5-data-ingestion/`

**Structure**:

```
mql5-data-ingestion/
├── SKILL.md                    # Validated procedures
├── converters/
│   └── exness_to_mt5.py       # Production converter
├── validators/
│   └── tick_format.py         # Production validator
└── mql5_loaders/
    └── LoadTicks.mq5          # Tested MQL5 loader
```

**Graduation Checklist**:

- [ ] MT5 environment setup completed
- [ ] Test import with 1M+ ticks
- [ ] Backtest runs without errors
- [ ] Format validator tested on edge cases
- [ ] Documentation reviewed by MT5 expert
- [ ] Performance benchmarks documented

---

## Support & Contributions

**Questions**: Post in research notes, NOT production channels

**Validation Results**: Document findings in `VALIDATION.md` with:

- Test environment details
- Dataset characteristics (date range, tick count)
- Success/failure outcomes
- Performance metrics

**Found Errors**: Update `SOURCES.md` with corrected documentation URLs

---

## Related Skills

- `mql5-article-extractor`: Extract MQL5 community code examples
- `python/api-documentation`: Pydantic model documentation (for exness-data-preprocess)

---

## Changelog

**2025-10-27**: Initial research documentation

- Extracted MT5 tick format requirements from ChatGPT dialogue
- Documented 9 official MQL5 documentation URLs
- Created validation rules based on `CustomTicksReplace()` constraints
- Identified 3 critical findings (millisecond timestamps, ascending order, M1-only bars)
