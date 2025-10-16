# Quick Start Guide

## Prerequisites

- MetaTrader 5 installed via CrossOver on macOS
- MT5 account logged in (demo or live)
- Python 3.12+ with pandas, numpy

## 1. Test Manual Execution (First Time)

```bash
# 1. Open MetaTrader 5 (if not already open)
open ~/Applications/CrossOver/MetaTrader\ 5/MetaTrader\ 5.app

# 2. In MT5: Press Ctrl+N → Scripts → Drag "ExportAligned" onto EURUSD chart
# 3. Accept defaults and click OK
# 4. Check for output:

ls -lh ~/Library/Application\ Support/CrossOver/Bottles/MetaTrader\ 5/drive_c/Program\ Files/MetaTrader\ 5/MQL5/Files/Export_*.csv
```

If CSV appears, manual execution works! ✓

## 2. Test Headless Execution

```bash
# Close MT5 first (to avoid conflicts)

# Run headless script
./scripts/mq5run

# Check output
ls -lh exports/

# Expected: 20251013_HHMMSS_Export_EURUSD_PERIOD_M1.csv
```

## 3. Validate Output

```bash
# Install Python dependencies (if not already)
uv pip install pandas numpy

# Validate CSV
python python/validate_export.py exports/$(ls -t exports/*.csv | head -1)
```

Expected output:
```
✓ All integrity checks passed
✓ RSI validation PASSED - Python implementation matches MT5
```

## 4. Advanced Usage

### Different symbol/timeframe

```bash
./scripts/mq5run --symbol XAUUSD --period PERIOD_H1 --timeout 180
```

### Adjust timeout

```bash
./scripts/mq5run --timeout 300  # 5 minutes
```

### Custom script

```bash
./scripts/mq5run --script MyCustomExport
```

## Troubleshooting

### "No CSV files found"

**Check MT5 logs**:
```bash
find ~/Library/Application\ Support/CrossOver/Bottles/MetaTrader\ 5/drive_c/Program\ Files/MetaTrader\ 5/MQL5/Logs/ -name "*.log" -type f -exec tail -20 {} \;
```

**Common causes**:
- Script not found (check name)
- Symbol not available (check spelling)
- Account not logged in
- History data not downloaded

### "MT5 execution timed out"

**Increase timeout**:
```bash
./scripts/mq5run --timeout 300
```

**Or check if MT5 hung**:
```bash
ps aux | grep terminal64
# Kill if stuck:
pkill -f terminal64.exe
```

### "Script found but didn't run"

**Check config**:
1. Is `[Experts] Enabled=1`? (mq5run sets this automatically)
2. Is script compiled? (should be .ex5 in MQL5/Scripts/)
3. Check MT5 Experts log for error messages

## Next Steps

1. Read full workflow: `AI_AGENT_WORKFLOW.md`
2. Add custom indicators: See "Adding New Indicators" section
3. Integrate with CI: See "Phase 4: Continuous Integration" section

## Getting Help

Check research findings in `../archive/historical.txt` for detailed troubleshooting and community best practices (2022-2025).
