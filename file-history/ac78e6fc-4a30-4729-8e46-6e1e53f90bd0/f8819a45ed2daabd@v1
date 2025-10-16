"""
export_aligned.py - Headless MT5 Data Export with RSI
Phase 4: Data export script matching ExportAligned.mq5 functionality

Usage:
    python export_aligned.py --symbol EURUSD --period M1 --bars 5000
    python export_aligned.py --symbol XAUUSD --period H1 --bars 5000
"""
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import MetaTrader5 as mt5
import pandas as pd
import numpy as np


def calculate_rsi(prices, period=14):
    """
    Calculate RSI (Relative Strength Index)

    Formula:
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss

    Args:
        prices: pandas Series of close prices
        period: RSI period (default 14)

    Returns:
        pandas Series of RSI values
    """
    # Calculate price changes
    delta = prices.diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # Calculate exponential moving average (Wilder's smoothing)
    # alpha=1/period is the correct Wilder's method for RSI
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def parse_timeframe(period_str):
    """Convert period string to MT5 timeframe constant"""
    timeframe_map = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1,
        'W1': mt5.TIMEFRAME_W1,
        'MN1': mt5.TIMEFRAME_MN1,
    }

    if period_str not in timeframe_map:
        raise ValueError(
            f"Invalid period: {period_str}\n"
            f"Valid periods: {', '.join(timeframe_map.keys())}"
        )

    return timeframe_map[period_str]


def export_data(symbol, period_str, num_bars, output_dir="C:\\Users\\crossover\\exports"):
    """
    Export MT5 data with RSI to CSV

    Args:
        symbol: Trading symbol (e.g., 'EURUSD', 'XAUUSD')
        period_str: Timeframe string (e.g., 'M1', 'H1')
        num_bars: Number of bars to fetch
        output_dir: Output directory path

    Returns:
        Path to exported CSV file
    """
    print("=" * 70)
    print(f"MT5 Data Export - {symbol} {period_str}")
    print("=" * 70)
    print()

    # Step 1: Initialize MT5
    print(f"[1/6] Initializing MT5 connection...")
    if not mt5.initialize():
        error_code, error_msg = mt5.last_error()
        raise ConnectionError(
            f"MT5 initialization failed\n"
            f"Error code: {error_code}\n"
            f"Message: {error_msg}\n"
            f"Ensure MT5 terminal is running and logged in"
        )
    print(f"[OK] MT5 initialized")
    print()

    try:
        # Step 2: Select symbol
        print(f"[2/6] Selecting symbol {symbol}...")
        if not mt5.symbol_select(symbol, True):
            error_code, error_msg = mt5.last_error()
            raise RuntimeError(
                f"Failed to select {symbol}\n"
                f"Error code: {error_code}\n"
                f"Message: {error_msg}\n"
                f"Symbol may not exist or broker may not offer it"
            )
        print(f"[OK] {symbol} selected and added to Market Watch")
        print()

        # Step 3: Parse timeframe
        print(f"[3/6] Parsing timeframe {period_str}...")
        timeframe = parse_timeframe(period_str)
        print(f"[OK] Timeframe: {period_str}")
        print()

        # Step 4: Fetch OHLC data
        print(f"[4/6] Fetching {num_bars} bars of {symbol} {period_str} data...")

        # Fetch extra bars for RSI calculation warmup (need 14 bars minimum)
        bars_to_fetch = num_bars + 50  # Extra buffer for RSI calculation

        # Use copy_rates_from_pos - fetches from most recent bar backwards
        # This is more reliable than date ranges, especially for non-24/7 markets
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars_to_fetch)

        if rates is None or len(rates) == 0:
            error_code, error_msg = mt5.last_error()
            raise RuntimeError(
                f"Failed to fetch {symbol} {period_str} data\n"
                f"Error code: {error_code}\n"
                f"Message: {error_msg}\n"
                f"Check if symbol has data available for this timeframe"
            )

        print(f"[OK] Fetched {len(rates)} bars")
        print(f"  Date range: {datetime.fromtimestamp(rates[0]['time'])} to {datetime.fromtimestamp(rates[-1]['time'])}")
        print()

        # Step 5: Calculate RSI
        print(f"[5/6] Calculating RSI (14-period)...")

        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')

        # Calculate RSI
        df['rsi'] = calculate_rsi(df['close'], period=14)

        # Take only the requested number of bars (most recent)
        df = df.tail(num_bars)

        print(f"[OK] RSI calculated for {len(df)} bars")
        print(f"  RSI stats: min={df['rsi'].min():.2f}, max={df['rsi'].max():.2f}, mean={df['rsi'].mean():.2f}")
        print()

        # Step 6: Export to CSV
        print(f"[6/6] Exporting to CSV...")

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename matching ExportAligned.mq5 format
        filename = f"Export_{symbol}_PERIOD_{period_str}.csv"
        filepath = output_path / filename

        # Select and rename columns to match MT5 export format
        export_df = df[['time', 'open', 'high', 'low', 'close', 'tick_volume', 'rsi']].copy()
        export_df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'RSI']

        # Format time column
        export_df['Time'] = export_df['Time'].dt.strftime('%Y.%m.%d %H:%M:%S')

        # Export to CSV
        export_df.to_csv(filepath, index=False, float_format='%.5f')

        print(f"[OK] Exported to: {filepath}")
        print(f"  Rows: {len(export_df)}")
        print(f"  Columns: {', '.join(export_df.columns)}")
        print()

        return filepath

    finally:
        # Always shutdown MT5
        mt5.shutdown()
        print("[OK] MT5 shutdown cleanly")
        print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Export MT5 data with RSI calculation (headless)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export_aligned.py --symbol EURUSD --period M1 --bars 5000
  python export_aligned.py --symbol XAUUSD --period H1 --bars 5000
  python export_aligned.py --symbol GBPUSD --period H4 --bars 1000

Valid periods: M1, M5, M15, M30, H1, H4, D1, W1, MN1
        """
    )

    parser.add_argument(
        '--symbol',
        required=True,
        help='Trading symbol (e.g., EURUSD, XAUUSD)'
    )

    parser.add_argument(
        '--period',
        required=True,
        help='Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN1)'
    )

    parser.add_argument(
        '--bars',
        type=int,
        default=5000,
        help='Number of bars to export (default: 5000)'
    )

    parser.add_argument(
        '--output',
        default='C:\\Users\\crossover\\exports',
        help='Output directory (default: C:\\Users\\crossover\\exports)'
    )

    args = parser.parse_args()

    try:
        filepath = export_data(
            symbol=args.symbol.upper(),
            period_str=args.period.upper(),
            num_bars=args.bars,
            output_dir=args.output
        )

        print("=" * 70)
        print("Export completed successfully!")
        print("=" * 70)
        print()
        print(f"File: {filepath}")
        print()
        print("Next: Run validation with validate_export.py")

        return 0

    except Exception as e:
        print()
        print("=" * 70)
        print("Export FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
