"""
MT5 Connection Test - Phase 3
Tests end-to-end connectivity: Wine Python -> MT5 Terminal
"""
import sys
from datetime import datetime, timedelta
import MetaTrader5 as mt5

def test_connection():
    """Test MT5 connection and basic data fetch"""

    print("=" * 60)
    print("MT5 Connection Test - Phase 3")
    print("=" * 60)
    print()

    # Step 1: Initialize MT5
    print("[Step 1/4] Initializing MT5 connection...")
    if not mt5.initialize():
        error_code, error_msg = mt5.last_error()
        raise ConnectionError(
            f"MT5 initialization failed\n"
            f"Error code: {error_code}\n"
            f"Message: {error_msg}\n"
            f"Ensure MT5 terminal is running and logged in"
        )
    print("[OK] MT5 initialized successfully")
    print()

    # Step 2: Get terminal info
    print("[Step 2/4] Retrieving terminal information...")
    info = mt5.terminal_info()
    if info is None:
        raise RuntimeError("terminal_info() returned None - MT5 not responding")

    print(f"[OK] Connected to MT5 build {info.build}")
    print(f"  Company: {info.company}")
    print(f"  Name: {info.name}")
    print(f"  Path: {info.path}")
    print(f"  Connected: {info.connected}")
    print(f"  Trade allowed: {info.trade_allowed}")
    print()

    # Step 3: Select symbol
    print("[Step 3/4] Selecting EURUSD symbol...")
    if not mt5.symbol_select("EURUSD", True):
        error_code, error_msg = mt5.last_error()
        raise RuntimeError(
            f"Failed to select EURUSD\n"
            f"Error code: {error_code}\n"
            f"Message: {error_msg}"
        )
    print("[OK] EURUSD selected and added to Market Watch")
    print()

    # Step 4: Fetch data
    print("[Step 4/4] Fetching EURUSD M1 data (last 100 bars)...")
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_M1, start_time, end_time)

    if rates is None or len(rates) == 0:
        error_code, error_msg = mt5.last_error()
        raise RuntimeError(
            f"Failed to fetch EURUSD M1 data\n"
            f"Error code: {error_code}\n"
            f"Message: {error_msg}"
        )

    print(f"[OK] Fetched {len(rates)} bars")
    print(f"  First bar: {datetime.fromtimestamp(rates[0]['time'])}")
    print(f"  Last bar:  {datetime.fromtimestamp(rates[-1]['time'])}")
    print(f"  Latest close: {rates[-1]['close']}")
    print()

    # Step 5: Shutdown
    mt5.shutdown()
    print("[OK] MT5 shutdown cleanly")
    print()

    print("=" * 60)
    print("Phase 3 Test: PASSED")
    print("=" * 60)
    print()
    print("Next: Phase 4 - Develop data export script with RSI calculation")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(test_connection())
    except Exception as e:
        print()
        print("=" * 60)
        print("Phase 3 Test: FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
