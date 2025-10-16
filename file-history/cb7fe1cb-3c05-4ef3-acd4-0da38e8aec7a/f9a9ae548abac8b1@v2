# Data Directory

Raw input data from providers. **Never commit to git.**

## Structure

```
data/
└── binance/
    ├── spot/              # Spot market aggTrades
    │   ├── BTCUSDT/
    │   │   ├── 2024-07-01.csv.zip
    │   │   └── ...
    │   └── ...
    ├── um/                # USDT-margined futures
    └── cm/                # Coin-margined futures
```

## Naming Conventions

### Binance
- **Path**: `binance/[market]/[SYMBOL]/YYYY-MM-DD.csv.zip`
- **Example**: `binance/spot/BTCUSDT/2024-07-01.csv.zip`
- **Markets**: `spot`, `um` (UM futures), `cm` (CM futures)

## Download Methods

### Binance
Use `binance_historical_data` Python package:
```bash
python -c "from binance_historical_data import BinanceDataDumper; \
  BinanceDataDumper('spot', './data/binance').dump_data('BTCUSDT', '2024-07-01', '2024-07-31')"
```

Or use `data-structure-validator` binary for automated fetching.

## Storage Policy

- **Retention**: Keep raw data indefinitely (disk space permitting)
- **Backup**: Consider external backup for mission-critical datasets
- **Cleanup**: Manually delete old data when no longer needed
- **Git**: **NEVER** commit to git (enforced by `.gitignore`)
