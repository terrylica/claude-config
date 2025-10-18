# ExportAligned Config File Examples

This directory contains example configuration files for the v4.0.0 file-based config workflow.

## How to Use

1. **Copy example to active config location**:
   ```bash
   cp configs/example_rsi_only.txt export_config.txt
   ```

2. **Run ExportAligned via MT5 GUI**:
   - Open MT5
   - Navigator → Scripts → DataExport → ExportAligned
   - Drag onto chart
   - Click OK (parameters will be overridden by config file)

3. **Output**:
   - CSV file created in `MQL5/Files/`
   - Filename specified in `InpOutputName` parameter

## Available Examples

### Basic Indicators

**example_rsi_only.txt**
- RSI indicator only
- Default period: 14
- Output: RSI_14 column

**example_sma_only.txt**
- Simple Moving Average only
- Default period: 14
- Output: SMA_14 column

### Custom Indicators

**example_laguerre_rsi.txt**
- ATR Adaptive Laguerre RSI
- ATR period: 32
- Smooth period: 5
- Smooth method: EMA (1)
- Output: Multiple Laguerre RSI buffers

**example_multi_indicator.txt**
- RSI + SMA + Laguerre RSI
- All indicators enabled
- Output: All indicator columns

### Validation

**example_validation_100bars.txt**
- 100 bars for quick validation
- Use AFTER fetching 5000-bar dataset
- Compare last 100 bars with Python implementation

## Parameter Reference

### Symbol & Timeframe

```
InpSymbol=EURUSD           # Symbol name
InpTimeframe=1             # PERIOD_M1 (1), PERIOD_M5 (5), PERIOD_H1 (60), etc.
InpBars=5000               # Number of bars to export
```

### RSI Parameters

```
InpUseRSI=true             # Enable RSI
InpRSIPeriod=14            # RSI period
```

### SMA Parameters

```
InpUseSMA=true             # Enable SMA
InpSMAPeriod=14            # SMA period
```

### Laguerre RSI Parameters

```
InpUseLaguerreRSI=true     # Enable Laguerre RSI
InpLaguerreInstanceID=A    # Instance ID (A-Z)
InpLaguerreAtrPeriod=32    # ATR period
InpLaguerreSmoothPeriod=5  # Price smoothing period
InpLaguerreSmoothMethod=1  # 0=SMA, 1=EMA, 2=SMMA, 3=LWMA
```

### Output

```
InpOutputName=Export_EURUSD_M1_Custom.csv  # Custom filename
```

## Timeframe Values

| Period | Value | Example Config |
|--------|-------|----------------|
| M1 | 1 | `InpTimeframe=1` |
| M5 | 5 | `InpTimeframe=5` |
| M15 | 15 | `InpTimeframe=15` |
| M30 | 30 | `InpTimeframe=30` |
| H1 | 60 | `InpTimeframe=60` |
| H4 | 240 | `InpTimeframe=240` |
| D1 | 1440 | `InpTimeframe=1440` |

## Smooth Method Values

| Method | Value | Description |
|--------|-------|-------------|
| SMA | 0 | Simple Moving Average |
| EMA | 1 | Exponential Moving Average |
| SMMA | 2 | Smoothed Moving Average |
| LWMA | 3 | Linear Weighted Moving Average |

## Tips

1. **Always use 5000+ bars for validation**:
   - Provides historical warmup
   - Prevents 0.95 correlation failures

2. **Test configs with small datasets first**:
   - Use 100 bars for quick tests
   - Verify output format before large exports

3. **Name output files descriptively**:
   - Include symbol, timeframe, indicators
   - Example: `Export_EURUSD_M1_RSI_SMA.csv`

4. **Keep configs in version control**:
   - Track parameter changes over time
   - Document validation parameters used

## Troubleshooting

**Config not loaded**:
- Check file location: Must be `MQL5/Files/export_config.txt`
- Check file encoding: UTF-8 (not UTF-16LE)
- Check syntax: `key=value` format (no spaces around `=`)
- Check logs: `MQL5/Logs/YYYYMMDD.log` for error messages

**Parameters not overriding**:
- Verify config copied to correct location
- Check parameter names (case-sensitive)
- Run script via GUI (not startup.ini)

**Wrong output**:
- Check `InpOutputName` parameter
- Verify indicator enabled (`InpUse*=true`)
- Check indicator prerequisites (e.g., Laguerre RSI in Custom/PythonInterop/)

---

**Version**: 1.0.0
**Last Updated**: 2025-10-17
**See Also**: `docs/plans/HEADLESS_EXECUTION_PLAN.md` (v4.0.0 section)
