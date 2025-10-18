#!/usr/bin/env python3
"""
Export Config Generator for ExportAligned.mq5 (v4.0.0)

Generates export_config.txt files for v4.0.0 file-based config workflow.

Usage:
    # RSI only
    python generate_export_config.py --symbol EURUSD --bars 5000 --rsi

    # SMA only
    python generate_export_config.py --symbol EURUSD --bars 5000 --sma --sma-period 20

    # Laguerre RSI
    python generate_export_config.py --symbol EURUSD --bars 5000 --laguerre-rsi \
        --laguerre-atr-period 32 --laguerre-smooth-period 5

    # Multi-indicator
    python generate_export_config.py --symbol EURUSD --bars 5000 --rsi --sma --laguerre-rsi

    # Custom output filename
    python generate_export_config.py --symbol XAUUSD --period H1 --bars 10000 --rsi \
        --output Export_XAUUSD_H1_RSI.csv

    # Save to file
    python generate_export_config.py --symbol EURUSD --bars 5000 --rsi \
        --save /path/to/export_config.txt
"""

import argparse
from pathlib import Path
from typing import Optional

# Timeframe mapping
TIMEFRAMES = {
    "M1": 1,
    "M5": 5,
    "M15": 15,
    "M30": 30,
    "H1": 60,
    "H4": 240,
    "D1": 1440,
    "W1": 10080,
    "MN1": 43200,
}

# Smooth method mapping
SMOOTH_METHODS = {
    "SMA": 0,
    "EMA": 1,
    "SMMA": 2,
    "LWMA": 3,
}


def generate_config(
    symbol: str = "EURUSD",
    timeframe: str = "M1",
    bars: int = 5000,
    use_rsi: bool = False,
    rsi_period: int = 14,
    use_sma: bool = False,
    sma_period: int = 14,
    use_laguerre_rsi: bool = False,
    laguerre_instance_id: str = "A",
    laguerre_atr_period: int = 32,
    laguerre_smooth_period: int = 5,
    laguerre_smooth_method: str = "EMA",
    output_name: Optional[str] = None,
) -> str:
    """
    Generate export config file content.

    Args:
        symbol: Trading symbol (e.g., "EURUSD", "XAUUSD")
        timeframe: Timeframe code (M1, M5, H1, etc.)
        bars: Number of bars to export
        use_rsi: Enable RSI indicator
        rsi_period: RSI period
        use_sma: Enable SMA indicator
        sma_period: SMA period
        use_laguerre_rsi: Enable Laguerre RSI custom indicator
        laguerre_instance_id: Laguerre RSI instance ID (A-Z)
        laguerre_atr_period: Laguerre RSI ATR period
        laguerre_smooth_period: Laguerre RSI price smoothing period
        laguerre_smooth_method: Smoothing method (SMA, EMA, SMMA, LWMA)
        output_name: Custom output filename (optional)

    Returns:
        Config file content as string
    """
    # Validate inputs
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"Invalid timeframe '{timeframe}'. Must be one of: {list(TIMEFRAMES.keys())}")

    if laguerre_smooth_method not in SMOOTH_METHODS:
        raise ValueError(f"Invalid smooth method '{laguerre_smooth_method}'. Must be one of: {list(SMOOTH_METHODS.keys())}")

    if bars < 1:
        raise ValueError(f"Bars must be >= 1, got {bars}")

    # Auto-generate output filename if not provided
    if output_name is None:
        indicators = []
        if use_rsi:
            indicators.append("RSI")
        if use_sma:
            indicators.append("SMA")
        if use_laguerre_rsi:
            indicators.append("Laguerre")

        indicator_str = "_".join(indicators) if indicators else "Market"
        output_name = f"Export_{symbol}_{timeframe}_{indicator_str}.csv"

    # Convert boolean to string
    use_rsi_str = "true" if use_rsi else "false"
    use_sma_str = "true" if use_sma else "false"
    use_laguerre_rsi_str = "true" if use_laguerre_rsi else "false"

    # Get numeric values
    timeframe_value = TIMEFRAMES[timeframe]
    smooth_method_value = SMOOTH_METHODS[laguerre_smooth_method]

    # Generate config
    config = f"""# Generated Export Config
# Symbol: {symbol}
# Timeframe: {timeframe} ({timeframe_value})
# Bars: {bars}
# Indicators: RSI={use_rsi}, SMA={use_sma}, LaguerreRSI={use_laguerre_rsi}

InpSymbol={symbol}
InpTimeframe={timeframe_value}
InpBars={bars}
InpUseRSI={use_rsi_str}
InpRSIPeriod={rsi_period}
InpUseSMA={use_sma_str}
InpSMAPeriod={sma_period}
InpUseLaguerreRSI={use_laguerre_rsi_str}
InpLaguerreInstanceID={laguerre_instance_id}
InpLaguerreAtrPeriod={laguerre_atr_period}
InpLaguerreSmoothPeriod={laguerre_smooth_period}
InpLaguerreSmoothMethod={smooth_method_value}
InpOutputName={output_name}
"""

    return config


def main():
    parser = argparse.ArgumentParser(
        description="Generate export_config.txt for ExportAligned.mq5 v4.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # RSI only (5000 bars)
    python generate_export_config.py --symbol EURUSD --bars 5000 --rsi

    # SMA only with custom period
    python generate_export_config.py --symbol EURUSD --bars 5000 --sma --sma-period 20

    # Laguerre RSI with custom parameters
    python generate_export_config.py --symbol EURUSD --bars 5000 --laguerre-rsi \\
        --laguerre-atr-period 64 --laguerre-smooth-method SMA

    # Multi-indicator export
    python generate_export_config.py --symbol XAUUSD --period H1 --bars 10000 \\
        --rsi --sma --laguerre-rsi

    # Save to specific file
    python generate_export_config.py --symbol EURUSD --bars 5000 --rsi \\
        --save "../Program Files/MetaTrader 5/MQL5/Files/export_config.txt"

    # Validation test (100 bars)
    python generate_export_config.py --symbol EURUSD --bars 100 --laguerre-rsi \\
        --output Export_EURUSD_M1_Validation.csv
        """,
    )

    # Basic parameters
    parser.add_argument("--symbol", default="EURUSD", help="Trading symbol (default: EURUSD)")
    parser.add_argument("--period", "--timeframe", default="M1", choices=list(TIMEFRAMES.keys()), help="Timeframe (default: M1)")
    parser.add_argument("--bars", type=int, default=5000, help="Number of bars to export (default: 5000)")

    # RSI parameters
    parser.add_argument("--rsi", action="store_true", help="Enable RSI indicator")
    parser.add_argument("--rsi-period", type=int, default=14, help="RSI period (default: 14)")

    # SMA parameters
    parser.add_argument("--sma", action="store_true", help="Enable SMA indicator")
    parser.add_argument("--sma-period", type=int, default=14, help="SMA period (default: 14)")

    # Laguerre RSI parameters
    parser.add_argument("--laguerre-rsi", action="store_true", help="Enable Laguerre RSI custom indicator")
    parser.add_argument("--laguerre-instance-id", default="A", help="Laguerre RSI instance ID A-Z (default: A)")
    parser.add_argument("--laguerre-atr-period", type=int, default=32, help="Laguerre ATR period (default: 32)")
    parser.add_argument("--laguerre-smooth-period", type=int, default=5, help="Laguerre smooth period (default: 5)")
    parser.add_argument("--laguerre-smooth-method", default="EMA", choices=list(SMOOTH_METHODS.keys()), help="Smoothing method (default: EMA)")

    # Output parameters
    parser.add_argument("--output", help="Custom output filename (auto-generated if not specified)")
    parser.add_argument("--save", help="Save to file path (prints to stdout if not specified)")

    args = parser.parse_args()

    # Generate config
    try:
        config = generate_config(
            symbol=args.symbol,
            timeframe=args.period,
            bars=args.bars,
            use_rsi=args.rsi,
            rsi_period=args.rsi_period,
            use_sma=args.sma,
            sma_period=args.sma_period,
            use_laguerre_rsi=args.laguerre_rsi,
            laguerre_instance_id=args.laguerre_instance_id,
            laguerre_atr_period=args.laguerre_atr_period,
            laguerre_smooth_period=args.laguerre_smooth_period,
            laguerre_smooth_method=args.laguerre_smooth_method,
            output_name=args.output,
        )

        # Save or print
        if args.save:
            output_path = Path(args.save)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(config, encoding="utf-8")
            print(f"Config saved to: {output_path}")
        else:
            print(config)

    except ValueError as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
