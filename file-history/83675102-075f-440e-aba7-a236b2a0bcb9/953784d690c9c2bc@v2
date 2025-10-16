"""
Test XAUUSD symbol availability and data
"""
import MetaTrader5 as mt5
from datetime import datetime, timedelta

print("=" * 70)
print("XAUUSD Symbol Diagnostic")
print("=" * 70)
print()

# Initialize
if not mt5.initialize():
    print(f"ERROR: MT5 init failed - {mt5.last_error()}")
    exit(1)
print("[OK] MT5 initialized")
print()

try:
    # Get symbol info BEFORE selecting
    print("Checking XAUUSD info (before select)...")
    info = mt5.symbol_info("XAUUSD")
    if info is None:
        print("  Symbol not found in broker's symbol list")
    else:
        print(f"  Name: {info.name}")
        print(f"  Visible: {info.visible}")
        print(f"  Selected: {info.select}")
        print(f"  Description: {info.description}")
    print()

    # Try to select
    print("Selecting XAUUSD...")
    result = mt5.symbol_select("XAUUSD", True)
    if not result:
        error_code, error_msg = mt5.last_error()
        print(f"  FAILED: {error_code} - {error_msg}")
    else:
        print("  [OK] Selected")
    print()

    # Get symbol info AFTER selecting
    print("Checking XAUUSD info (after select)...")
    info = mt5.symbol_info("XAUUSD")
    if info is None:
        print("  ERROR: Still no symbol info")
    else:
        print(f"  Name: {info.name}")
        print(f"  Visible: {info.visible}")
        print(f"  Selected: {info.select}")
    print()

    # Try to get tick data (most recent)
    print("Testing live tick data...")
    tick = mt5.symbol_info_tick("XAUUSD")
    if tick is None:
        error_code, error_msg = mt5.last_error()
        print(f"  FAILED: {error_code} - {error_msg}")
    else:
        print(f"  [OK] Bid: {tick.bid}, Ask: {tick.ask}, Time: {datetime.fromtimestamp(tick.time)}")
    print()

    # Try small data fetch (last 10 bars only)
    print("Testing small H1 data fetch (10 bars)...")
    rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_H1, 0, 10)
    if rates is None or len(rates) == 0:
        error_code, error_msg = mt5.last_error()
        print(f"  FAILED: {error_code} - {error_msg}")
    else:
        print(f"  [OK] Got {len(rates)} bars")
        print(f"    First: {datetime.fromtimestamp(rates[0]['time'])}")
        print(f"    Last: {datetime.fromtimestamp(rates[-1]['time'])}")
    print()

    # Try date range fetch
    print("Testing date range fetch (last 7 days)...")
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    rates = mt5.copy_rates_range("XAUUSD", mt5.TIMEFRAME_H1, start_time, end_time)
    if rates is None or len(rates) == 0:
        error_code, error_msg = mt5.last_error()
        print(f"  FAILED: {error_code} - {error_msg}")
    else:
        print(f"  [OK] Got {len(rates)} bars")
        print(f"    First: {datetime.fromtimestamp(rates[0]['time'])}")
        print(f"    Last: {datetime.fromtimestamp(rates[-1]['time'])}")

finally:
    mt5.shutdown()
    print()
    print("[OK] MT5 shutdown")
