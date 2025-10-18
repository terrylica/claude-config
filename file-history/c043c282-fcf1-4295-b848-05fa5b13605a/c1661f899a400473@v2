# v4.0.0 File-Based Config Workflow Guide

**Version**: 4.0.0
**Status**: PRODUCTION READY (GUI mode)
**Date**: 2025-10-17

---

## Overview

v4.0.0 provides **flexible parameter-based exports** via config file, enabling quick parameter changes without code editing. This is a GUI-based workflow that complements v3.0.0 Python API for headless execution.

**Use Cases**:
- ✅ Manual exports with varying parameters
- ✅ Custom indicator exports (Laguerre RSI, etc.)
- ✅ Parameter testing (ATR 32 vs 64)
- ✅ Validation workflows

**Limitations**:
- ⚠️ Requires GUI interaction (not headless)
- ⚠️ Cannot be automated via startup.ini
- ⚠️ Best for manual/semi-automated workflows

---

## Quick Start (3 Steps)

### Step 1: Generate Config File

**Method A: Use Python Script** (recommended)
```bash
cd "/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover"

python3 generate_export_config.py \
  --symbol EURUSD \
  --bars 5000 \
  --laguerre-rsi \
  --save "../Program Files/MetaTrader 5/MQL5/Files/export_config.txt"
```

**Method B: Copy Example**
```bash
BOTTLE="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5"

cp "$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Files/configs/example_laguerre_rsi.txt" \
   "$BOTTLE/drive_c/Program Files/MetaTrader 5/MQL5/Files/export_config.txt"
```

**Method C: Manual Creation**
```bash
cat > "MQL5/Files/export_config.txt" << 'EOF'
InpSymbol=EURUSD
InpTimeframe=1
InpBars=5000
InpUseLaguerreRSI=true
InpLaguerreAtrPeriod=32
InpOutputName=Export_EURUSD_M1_Laguerre.csv
EOF
```

### Step 2: Run Script via MT5 GUI

1. Open MT5
2. Open chart (Ctrl+N → Select symbol)
3. Navigator → Scripts → DataExport → ExportAligned
4. Drag script onto chart
5. Click **OK** (parameters will be overridden by config file)

### Step 3: Verify Output

```bash
ls -lh "MQL5/Files/Export_EURUSD_M1_Laguerre.csv"
# Expected: CSV with Laguerre RSI columns

# Check line count
wc -l "MQL5/Files/Export_EURUSD_M1_Laguerre.csv"
# Expected: 5001 lines (1 header + 5000 bars)

# Verify header
head -1 "MQL5/Files/Export_EURUSD_M1_Laguerre.csv"
# Expected: time,open,high,low,close,...,Laguerre_RSI_32,...
```

---

## Config File Format

### Basic Structure

```
# Comments start with #
InpParameterName=Value

# Boolean values: true or false (lowercase)
InpUseRSI=true
InpUseSMA=false

# Integer values
InpBars=5000
InpRSIPeriod=14

# String values (no quotes)
InpSymbol=EURUSD
InpOutputName=Export_EURUSD_M1.csv
```

### All Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `InpSymbol` | string | "EURUSD" | Trading symbol |
| `InpTimeframe` | int | 1 | Timeframe (1=M1, 5=M5, 60=H1, etc.) |
| `InpBars` | int | 5000 | Number of bars to export |
| `InpUseRSI` | bool | true | Enable RSI indicator |
| `InpRSIPeriod` | int | 14 | RSI period |
| `InpUseSMA` | bool | false | Enable SMA indicator |
| `InpSMAPeriod` | int | 14 | SMA period |
| `InpUseLaguerreRSI` | bool | false | Enable Laguerre RSI custom indicator |
| `InpLaguerreInstanceID` | string | "A" | Laguerre instance ID (A-Z) |
| `InpLaguerreAtrPeriod` | int | 32 | Laguerre ATR period |
| `InpLaguerreSmoothPeriod` | int | 5 | Laguerre price smoothing period |
| `InpLaguerreSmoothMethod` | int | 1 | Smoothing method (0=SMA, 1=EMA, 2=SMMA, 3=LWMA) |
| `InpOutputName` | string | "" | Custom output filename |

### Timeframe Values

| Timeframe | Value | Config |
|-----------|-------|--------|
| M1 | 1 | `InpTimeframe=1` |
| M5 | 5 | `InpTimeframe=5` |
| M15 | 15 | `InpTimeframe=15` |
| M30 | 30 | `InpTimeframe=30` |
| H1 | 60 | `InpTimeframe=60` |
| H4 | 240 | `InpTimeframe=240` |
| D1 | 1440 | `InpTimeframe=1440` |
| W1 | 10080 | `InpTimeframe=10080` |
| MN1 | 43200 | `InpTimeframe=43200` |

---

## Common Workflows

### Workflow 1: RSI Export

```bash
# Generate config
python3 generate_export_config.py --symbol EURUSD --bars 5000 --rsi \
  --save "MQL5/Files/export_config.txt"

# Run in MT5 GUI
# Navigator → Scripts → DataExport → ExportAligned → Drag to chart → OK

# Output
ls MQL5/Files/Export_EURUSD_M1_RSI.csv
```

**Output CSV**:
```
time,open,high,low,close,tick_volume,spread,real_volume,RSI_14
2025.10.17 10:00,1.16500,1.16520,1.16480,1.16510,45,0,0,58.234
...
```

### Workflow 2: SMA Export with Custom Period

```bash
# Generate config
python3 generate_export_config.py --symbol EURUSD --bars 5000 --sma --sma-period 50 \
  --save "MQL5/Files/export_config.txt"

# Run in MT5 GUI
# Output: Export_EURUSD_M1_SMA.csv with SMA_50 column
```

### Workflow 3: Laguerre RSI Export (Custom Indicator)

```bash
# Prerequisites
# 1. ATR_Adaptive_Laguerre_RSI.ex5 in Custom/PythonInterop/
# 2. Indicator compiled successfully

# Generate config
python3 generate_export_config.py \
  --symbol EURUSD \
  --bars 5000 \
  --laguerre-rsi \
  --laguerre-atr-period 32 \
  --laguerre-smooth-period 5 \
  --laguerre-smooth-method EMA \
  --save "MQL5/Files/export_config.txt"

# Run in MT5 GUI
# Output: Export_EURUSD_M1_Laguerre.csv with Laguerre RSI buffers
```

**Output CSV** (multiple buffers):
```
time,open,high,low,close,...,Laguerre_RSI_32,ATR_32,Adaptive_Period_32
2025.10.17 10:00,1.16500,...,0.652,0.00012,28.5
...
```

### Workflow 4: Multi-Indicator Export

```bash
# Generate config with multiple indicators
python3 generate_export_config.py \
  --symbol EURUSD \
  --bars 5000 \
  --rsi \
  --sma --sma-period 20 \
  --laguerre-rsi \
  --output Export_EURUSD_M1_Multi.csv \
  --save "MQL5/Files/export_config.txt"

# Run in MT5 GUI
# Output: Export_EURUSD_M1_Multi.csv with RSI_14, SMA_20, Laguerre_RSI_32 columns
```

### Workflow 5: Validation Test (100 Bars)

```bash
# Step 1: Fetch 5000 bars via v3.0.0 Python API (headless)
CX_BOTTLE="MetaTrader 5" wine python.exe export_aligned.py \
  --symbol EURUSD --period M1 --bars 5000

# Step 2: Generate config for 100-bar export with Laguerre RSI
python3 generate_export_config.py \
  --symbol EURUSD \
  --bars 100 \
  --laguerre-rsi \
  --output Export_EURUSD_M1_Validation.csv \
  --save "MQL5/Files/export_config.txt"

# Step 3: Run ExportAligned via GUI
# Output: 100 bars with Laguerre RSI values

# Step 4: Validate correlation
python validate_indicator.py \
  --csv ../../exports/Export_EURUSD_M1_Validation.csv \
  --indicator laguerre_rsi \
  --threshold 0.999
```

---

## How It Works (Under the Hood)

### MQL5 Implementation

The ExportAligned.mq5 script reads the config file in `OnStart()`:

```mql5
void OnStart()
{
  // Create working copies of input parameters
  string symbol = InpSymbol;
  ENUM_TIMEFRAMES timeframe = InpTimeframe;
  int bars = InpBars;
  // ... (13 parameters total)

  // Try to load config from file (optional)
  bool configLoaded = LoadConfigFromFile(
    symbol, timeframe, bars,
    useRSI, rsiPeriod,
    useSMA, smaPeriod,
    useLaguerreRSI, laguerreInstanceID, laguerreAtrPeriod,
    laguerreSmoothPeriod, laguerreSmoothMethod,
    outputName
  );

  if (configLoaded) {
    Print("=== Config loaded: X parameters from export_config.txt ===");
  } else {
    Print("Config file not found - using input parameters");
  }

  // Use working copies (not Inp* constants)
  // ... rest of export logic
}
```

### Config Loading Logic

```mql5
bool LoadConfigFromFile(string &symbol, ENUM_TIMEFRAMES &timeframe, ...) {
  // Open file
  int handle = FileOpen("export_config.txt", FILE_READ|FILE_TXT|FILE_ANSI);

  if (handle == INVALID_HANDLE) {
    // Config file not found - graceful degradation
    return false;
  }

  Print("=== Loading configuration from export_config.txt ===");

  // Parse key=value format
  while (!FileIsEnding(handle)) {
    string line = FileReadString(handle);

    // Skip comments and empty lines
    if (StringLen(line) == 0 || StringSubstr(line, 0, 1) == "#") continue;

    // Split on '='
    string parts[];
    int count = StringSplit(line, '=', parts);
    if (count != 2) continue;

    string key = parts[0];
    string value = parts[1];

    // Override parameters
    if (key == "InpSymbol") symbol = value;
    else if (key == "InpBars") bars = (int)StringToInteger(value);
    else if (key == "InpUseRSI") useRSI = (value == "true");
    // ... (13 parameters total)
  }

  FileClose(handle);
  return true;
}
```

### Working Copies Pattern

**Critical Insight**: MQL5 `input` variables are constants and cannot be modified. The solution is to create working copies:

```mql5
// Input parameters (constants - CANNOT be modified)
input string InpSymbol = "EURUSD";
input int InpBars = 5000;

void OnStart() {
  // Create working copies (mutable)
  string symbol = InpSymbol;
  int bars = InpBars;

  // Config file overrides working copies (NOT input constants)
  LoadConfigFromFile(symbol, bars, ...);

  // Use working copies in all subsequent code
  SymbolSelect(symbol, true);
  CopyRates(symbol, timeframe, 0, bars, rates);
}
```

---

## Troubleshooting

### Config File Not Loaded

**Symptom**: Script uses default parameters (5000 bars, RSI enabled)

**Check List**:
- [ ] File location: Must be `MQL5/Files/export_config.txt` (not `Program Files/.../MQL5/Files/`)
- [ ] File encoding: UTF-8 (not UTF-16LE)
- [ ] File syntax: `key=value` format (no spaces around `=`)
- [ ] Run from GUI: startup.ini doesn't work (v2.1.0 failed)

**Debug**:
```bash
# Check file exists
ls -lh "MQL5/Files/export_config.txt"

# Check encoding
file "MQL5/Files/export_config.txt"
# Expected: UTF-8 Unicode text

# Check syntax
cat "MQL5/Files/export_config.txt"
# Look for syntax errors
```

**Check Logs**:
```bash
# MQL5 script logs
tail -50 "MQL5/Logs/$(date +%Y%m%d).log" | grep -A 10 "ExportAligned"
# Look for: "=== Loading configuration from export_config.txt ==="
#       or: "WARNING: Could not open config file ..."
```

### Parameters Not Overriding

**Symptom**: Config file loaded but some parameters still use defaults

**Check List**:
- [ ] Parameter names correct (case-sensitive): `InpBars` not `inpBars`
- [ ] Boolean format: `true` or `false` (lowercase)
- [ ] Integer format: `5000` not `"5000"` (no quotes)
- [ ] Timeframe value: `1` not `"M1"` (use numeric value)

**Example Errors**:
```
# ❌ WRONG
inpBars=5000           # Lowercase (ignored)
InpBars="5000"         # Quoted (parsed as 0)
InpUseRSI=True         # Capital T (parsed as false)
InpTimeframe=M1        # String (parsed as 0)

# ✅ RIGHT
InpBars=5000           # Exact case
InpUseRSI=true         # Lowercase
InpTimeframe=1         # Numeric value
```

### Wrong Output Filename

**Symptom**: Output file has default name instead of `InpOutputName`

**Check**:
```
# Config file
InpOutputName=Export_EURUSD_M1_Custom.csv

# Expected output
MQL5/Files/Export_EURUSD_M1_Custom.csv
```

**Common Issue**: Special characters in filename
```
# ❌ May cause issues
InpOutputName=Export (EURUSD).csv  # Spaces, parentheses

# ✅ Safe
InpOutputName=Export_EURUSD_M1.csv  # Underscores only
```

### Indicator Not Found

**Symptom**: Laguerre RSI enabled but columns missing from output

**Check List**:
- [ ] Indicator exists: `Indicators/Custom/PythonInterop/ATR_Adaptive_Laguerre_RSI.ex5`
- [ ] Indicator compiles: Open in MetaEditor, press F7, verify "0 errors"
- [ ] Instance ID valid: A-Z only (case-sensitive)
- [ ] Parameters valid: ATR period >= 1, smooth period >= 1

**Debug**:
```bash
# Check indicator exists
ls -lh "Indicators/Custom/PythonInterop/ATR_Adaptive_Laguerre_RSI.ex5"

# Check logs for iCustom() errors
tail -50 "MQL5/Logs/$(date +%Y%m%d).log" | grep -i "error\|laguerre"
```

---

## Performance

### Execution Time

| Bars | Indicators | Time | Notes |
|------|-----------|------|-------|
| 100 | RSI | ~1s | Quick test |
| 1000 | RSI + SMA | ~2s | Medium |
| 5000 | RSI + SMA | ~5s | Standard |
| 5000 | RSI + SMA + Laguerre | ~8s | With custom indicator |
| 10000 | All | ~15s | Large dataset |

**Bottleneck**: Custom indicator calculation (Laguerre RSI ~3s overhead)

### CSV File Sizes

| Bars | Columns | Size | Notes |
|------|---------|------|-------|
| 100 | 8 (OHLCV) | ~6KB | Market data only |
| 100 | 9 (+ RSI) | ~7KB | +1 indicator |
| 5000 | 8 | ~305KB | Standard |
| 5000 | 11 (+ 3 indicators) | ~385KB | Multi-indicator |
| 10000 | 8 | ~610KB | Large dataset |

---

## Comparison: v3.0.0 vs v4.0.0

| Feature | v3.0.0 Python API | v4.0.0 File Config |
|---------|------------------|-------------------|
| **Headless** | ✅ True headless | ❌ Requires GUI |
| **Custom Indicators** | ❌ No access | ✅ Full access via iCustom() |
| **Parameterization** | ❌ Code editing | ✅ Config file |
| **Automation** | ✅ CI/CD, scripts | ⚠️ Semi-automated (GUI step) |
| **Speed** | ~6-8s (5000 bars) | ~5-8s (5000 bars) |
| **Use Case** | Automated pipelines | Manual validation, testing |
| **Production Ready** | ✅ Yes | ✅ Yes (GUI mode) |

**Recommendation**: Use both approaches complementarily
- v3.0.0 for automated market data exports
- v4.0.0 for custom indicator validation

---

## Best Practices

### Config File Management

1. **Version Control**: Store configs in `MQL5/Files/configs/` directory
   ```bash
   configs/
   ├── validation_100bars.txt
   ├── eurusd_m1_full.txt
   ├── xauusd_h1_laguerre.txt
   └── README.md
   ```

2. **Naming Convention**: Include symbol, timeframe, indicators
   ```
   config_EURUSD_M1_RSI_SMA.txt
   config_XAUUSD_H1_Laguerre.txt
   config_Validation_100bars.txt
   ```

3. **Comments**: Document purpose and parameters
   ```
   # Validation config for Python Laguerre RSI implementation
   # Use with 5000-bar historical dataset
   # Compare last 100 bars for correlation check
   InpBars=100
   ...
   ```

### Parameter Selection

1. **Always use 5000+ bars for validation** (historical warmup requirement)
2. **Use 100-200 bars for quick tests** (format verification)
3. **Match indicator periods to Python implementation** (validation consistency)
4. **Use descriptive output filenames** (include symbol, timeframe, indicators)

### Workflow Integration

**Pattern 1: v3.0.0 (market data) + v4.0.0 (custom indicators)**
```bash
# Step 1: Export market data (headless)
wine python.exe export_aligned.py --symbol EURUSD --period M1 --bars 5000

# Step 2: Export with custom indicator (GUI)
python3 generate_export_config.py --symbol EURUSD --bars 5000 --laguerre-rsi \
  --save "MQL5/Files/export_config.txt"
# Run ExportAligned via GUI

# Step 3: Validate correlation
python validate_indicator.py --csv export.csv --indicator laguerre_rsi --threshold 0.999
```

**Pattern 2: Parameter sensitivity analysis**
```bash
# Test different ATR periods
for atr in 16 32 64 128; do
  python3 generate_export_config.py \
    --symbol EURUSD --bars 5000 --laguerre-rsi \
    --laguerre-atr-period $atr \
    --output "Export_EURUSD_M1_ATR${atr}.csv" \
    --save "MQL5/Files/export_config.txt"

  # Run ExportAligned via GUI
  # Compare outputs
done
```

---

## Future Enhancements

### P1: Batch Export Script
```bash
# batch_export.sh (future)
for symbol in EURUSD USDJPY XAUUSD; do
  python3 generate_export_config.py \
    --symbol $symbol --bars 5000 --rsi --sma \
    --save "MQL5/Files/export_config.txt"

  # Auto-run via AppleScript (future)
  # Click "OK" automatically
done
```

### P2: GUI Automation (AppleScript)
```applescript
-- auto_export.applescript (future)
tell application "MetaTrader 5"
    -- Find ExportAligned in Navigator
    -- Drag to chart
    -- Click OK
end tell
```

### P3: Config Validation
```python
# validate_config.py (future)
def validate_config(config_file):
    # Check all required parameters
    # Validate ranges
    # Check indicator prerequisites
    # Return validation report
```

---

## References

### Documentation
- **Implementation Plan**: `docs/plans/HEADLESS_EXECUTION_PLAN.md` (v4.0.0 section)
- **MQL5 Source**: `Program Files/MetaTrader 5/MQL5/Scripts/DataExport/ExportAligned.mq5` (lines 27-94)
- **Config Examples**: `MQL5/Files/configs/` (5 examples)
- **Python Generator**: `users/crossover/generate_export_config.py`

### Related Guides
- **v3.0.0 Workflow**: `docs/guides/WINE_PYTHON_EXECUTION.md`
- **Validation**: `docs/reports/LAGUERRE_RSI_VALIDATION_SUCCESS.md`
- **Migration**: `docs/guides/MQL5_TO_PYTHON_MIGRATION_GUIDE.md`

---

**Version**: 1.0.0
**Status**: Production Ready (GUI mode)
**Last Updated**: 2025-10-17
**Next Review**: After 3 indicator validations
