"""Spike Test 1: MT5 Python API Custom Indicator Access

CRITICAL ASSUMPTION:
    Can we use mt5.create_indicator() + mt5.copy_buffer() to read
    custom indicator (ATR_Adaptive_Laguerre_RSI) buffer values?

SUCCESS CRITERIA:
    ✅ Successfully create indicator handle
    ✅ Read buffer 0 (Laguerre RSI values)
    ✅ Read buffer 1 (Signal classification)
    ✅ Values are reasonable (0.0 to 1.0 for RSI)

FAILURE FALLBACK:
    If mt5.create_indicator() doesn't work with custom indicators,
    we'll need to create LaguerreRSIModule.mqh + extend ExportAligned.mq5

EXECUTION:
    CX_BOTTLE="MetaTrader 5" \
    WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5" \
    wine "C:\\Program Files\\Python312\\python.exe" \
      "C:\\users\\crossover\\spike_1_mt5_indicator_access.py"
"""

import sys
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime


def test_builtin_indicator():
    """Test with built-in indicator (RSI) as baseline."""
    print("\n" + "=" * 70)
    print("TEST 1: Built-in Indicator (RSI) - Baseline")
    print("=" * 70)

    symbol = "EURUSD"
    timeframe = mt5.TIMEFRAME_M1
    bars = 100

    # Create RSI indicator handle
    print(f"\n1. Creating RSI indicator handle...")
    print(f"   Symbol: {symbol}")
    print(f"   Timeframe: M1")
    print(f"   Period: 14")

    handle = mt5.create_indicator(
        symbol=symbol,
        timeframe=timeframe,
        indicator_name="RSI",
        parameters=[14, 0]  # period=14, applied_price=PRICE_CLOSE
    )

    if handle is None or handle == -1:
        error_code, error_msg = mt5.last_error()
        print(f"   ❌ FAILED: {error_msg} (code {error_code})")
        return False

    print(f"   ✅ SUCCESS: Handle = {handle}")

    # Read buffer
    print(f"\n2. Reading RSI buffer (buffer index 0)...")
    buffer = mt5.copy_buffer(handle, 0, 0, bars)

    if buffer is None or len(buffer) == 0:
        error_code, error_msg = mt5.last_error()
        print(f"   ❌ FAILED: {error_msg} (code {error_code})")
        mt5.release_indicator(handle)
        return False

    print(f"   ✅ SUCCESS: Read {len(buffer)} values")
    print(f"   Sample values: {buffer[:5]}")
    print(f"   Range: min={buffer.min():.2f}, max={buffer.max():.2f}, mean={buffer.mean():.2f}")

    # Validate RSI range (should be 0-100)
    if buffer.min() < 0 or buffer.max() > 100:
        print(f"   ⚠️  WARNING: RSI values outside expected range [0, 100]")
        mt5.release_indicator(handle)
        return False

    # Release handle
    print(f"\n3. Releasing indicator handle...")
    mt5.release_indicator(handle)
    print(f"   ✅ SUCCESS: Handle released")

    print("\n" + "=" * 70)
    print("TEST 1: PASSED ✅")
    print("=" * 70)

    return True


def test_custom_indicator():
    """Test with custom indicator (ATR_Adaptive_Laguerre_RSI) - CRITICAL TEST."""
    print("\n" + "=" * 70)
    print("TEST 2: Custom Indicator (ATR Adaptive Laguerre RSI) - CRITICAL")
    print("=" * 70)

    symbol = "EURUSD"
    timeframe = mt5.TIMEFRAME_M1
    bars = 100

    # Test multiple indicator path formats
    indicator_paths = [
        # Format 1: Relative path from MQL5/Indicators
        "PythonInterop\\ATR_Adaptive_Laguerre_RSI",
        # Format 2: Full path within Custom folder
        "Custom\\PythonInterop\\ATR_Adaptive_Laguerre_RSI",
        # Format 3: Absolute path (if needed)
        "..\\..\\Program Files\\MetaTrader 5\\MQL5\\Indicators\\PythonInterop\\ATR_Adaptive_Laguerre_RSI",
    ]

    # MQL5 indicator parameters (in order from ATR_Adaptive_Laguerre_RSI.mq5 line 18-24)
    # input string             inpInstanceID  = "A";            // Instance ID
    # input int                inpAtrPeriod   = 32;             // ATR period
    # input ENUM_APPLIED_PRICE inpRsiPrice    = PRICE_CLOSE;    // Price
    # input int                inpRsiMaPeriod = 5;              // Price smoothing period
    # input ENUM_MA_METHOD     inpRsiMaType   = MODE_EMA;       // Price smoothing method
    # input double             inpLevelUp     = 0.85;           // Level up
    # input double             inpLevelDown   = 0.15;           // Level down
    parameters = [
        "A",      # inpInstanceID (string)
        32,       # inpAtrPeriod (int)
        0,        # inpRsiPrice (PRICE_CLOSE = 0)
        5,        # inpRsiMaPeriod (int)
        1,        # inpRsiMaType (MODE_EMA = 1)
        0.85,     # inpLevelUp (double)
        0.15      # inpLevelDown (double)
    ]

    success = False
    for path in indicator_paths:
        print(f"\n1. Attempting indicator path: {path}")
        print(f"   Symbol: {symbol}")
        print(f"   Timeframe: M1")
        print(f"   Parameters: {parameters}")

        handle = mt5.create_indicator(
            symbol=symbol,
            timeframe=timeframe,
            indicator_name=path,
            parameters=parameters
        )

        if handle is None or handle == -1:
            error_code, error_msg = mt5.last_error()
            print(f"   ❌ FAILED: {error_msg} (code {error_code})")
            continue

        print(f"   ✅ SUCCESS: Handle = {handle}")

        # Read buffer 0 (Laguerre RSI values)
        print(f"\n2. Reading buffer 0 (Laguerre RSI values)...")
        buffer_0 = mt5.copy_buffer(handle, 0, 0, bars)

        if buffer_0 is None or len(buffer_0) == 0:
            error_code, error_msg = mt5.last_error()
            print(f"   ❌ FAILED: {error_msg} (code {error_code})")
            mt5.release_indicator(handle)
            continue

        print(f"   ✅ SUCCESS: Read {len(buffer_0)} values")
        print(f"   Sample values: {buffer_0[:5]}")
        print(f"   Range: min={buffer_0.min():.6f}, max={buffer_0.max():.6f}, mean={buffer_0.mean():.6f}")

        # Validate Laguerre RSI range (should be 0.0 to 1.0)
        if buffer_0.min() < 0.0 or buffer_0.max() > 1.0:
            print(f"   ⚠️  WARNING: Laguerre RSI values outside expected range [0.0, 1.0]")
            mt5.release_indicator(handle)
            continue

        # Read buffer 1 (Signal classification)
        print(f"\n3. Reading buffer 1 (Signal classification)...")
        buffer_1 = mt5.copy_buffer(handle, 1, 0, bars)

        if buffer_1 is None or len(buffer_1) == 0:
            error_code, error_msg = mt5.last_error()
            print(f"   ❌ FAILED: {error_msg} (code {error_code})")
            mt5.release_indicator(handle)
            continue

        print(f"   ✅ SUCCESS: Read {len(buffer_1)} values")
        print(f"   Sample values: {buffer_1[:5]}")
        print(f"   Unique values: {np.unique(buffer_1)}")

        # Validate signal range (should be 0, 1, or 2)
        unique_signals = np.unique(buffer_1)
        if not all(s in [0.0, 1.0, 2.0] for s in unique_signals):
            print(f"   ⚠️  WARNING: Signal values unexpected: {unique_signals}")
            mt5.release_indicator(handle)
            continue

        # Read buffer 2 (Smoothed prices) - optional, but good to test
        print(f"\n4. Reading buffer 2 (Smoothed prices)...")
        buffer_2 = mt5.copy_buffer(handle, 2, 0, bars)

        if buffer_2 is None or len(buffer_2) == 0:
            error_code, error_msg = mt5.last_error()
            print(f"   ⚠️  WARNING: Buffer 2 not available: {error_msg} (code {error_code})")
            # Not a failure - buffer 2 is optional
        else:
            print(f"   ✅ SUCCESS: Read {len(buffer_2)} values")
            print(f"   Sample values: {buffer_2[:5]}")
            print(f"   Range: min={buffer_2.min():.5f}, max={buffer_2.max():.5f}")

        # Release handle
        print(f"\n5. Releasing indicator handle...")
        mt5.release_indicator(handle)
        print(f"   ✅ SUCCESS: Handle released")

        success = True
        break  # Success! No need to try other paths

    if success:
        print("\n" + "=" * 70)
        print("TEST 2: PASSED ✅")
        print("=" * 70)
        print(f"\n🎉 CRITICAL ASSUMPTION VALIDATED!")
        print(f"   Working indicator path: {path}")
        print(f"   Buffer 0 (Laguerre RSI): {len(buffer_0)} values, range [{buffer_0.min():.6f}, {buffer_0.max():.6f}]")
        print(f"   Buffer 1 (Signal): {len(buffer_1)} values, unique {unique_signals}")
    else:
        print("\n" + "=" * 70)
        print("TEST 2: FAILED ❌")
        print("=" * 70)
        print(f"\n💥 CRITICAL ASSUMPTION FAILED!")
        print(f"   Unable to read custom indicator buffers via mt5.create_indicator()")
        print(f"   Fallback required: Create LaguerreRSIModule.mqh + extend ExportAligned.mq5")

    return success


def main():
    """Run all spike tests."""
    print("\n" + "=" * 70)
    print("SPIKE TEST 1: MT5 Python API Custom Indicator Access")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Purpose: Validate mt5.create_indicator() + mt5.copy_buffer() with custom indicators")
    print()

    # Initialize MT5
    print("[1/4] Initializing MT5 connection...")
    if not mt5.initialize():
        error_code, error_msg = mt5.last_error()
        print(f"❌ MT5 initialization failed: {error_msg} (code {error_code})")
        print("   Ensure MT5 terminal is running and logged in")
        return 1

    print(f"✅ MT5 initialized")
    print(f"   Version: {mt5.version()}")
    print(f"   Build: {mt5.terminal_info().build}")

    # Select symbol
    print("\n[2/4] Selecting symbol EURUSD...")
    if not mt5.symbol_select("EURUSD", True):
        error_code, error_msg = mt5.last_error()
        print(f"❌ Failed to select EURUSD: {error_msg} (code {error_code})")
        mt5.shutdown()
        return 1

    print(f"✅ EURUSD selected")

    # Run tests
    try:
        print("\n[3/4] Running baseline test (built-in RSI indicator)...")
        baseline_passed = test_builtin_indicator()

        if not baseline_passed:
            print("\n⚠️  Baseline test failed - MT5 Python API may have issues")
            print("   Stopping spike tests")
            return 1

        print("\n[4/4] Running critical test (custom Laguerre RSI indicator)...")
        critical_passed = test_custom_indicator()

        # Summary
        print("\n" + "=" * 70)
        print("SPIKE TEST SUMMARY")
        print("=" * 70)
        print(f"Baseline (Built-in RSI):         {'✅ PASSED' if baseline_passed else '❌ FAILED'}")
        print(f"Critical (Custom Laguerre RSI):  {'✅ PASSED' if critical_passed else '❌ FAILED'}")
        print("=" * 70)

        if baseline_passed and critical_passed:
            print("\n🎉 ALL TESTS PASSED! 🎉")
            print("\n✅ CRITICAL ASSUMPTION VALIDATED:")
            print("   - mt5.create_indicator() works with custom indicators")
            print("   - mt5.copy_buffer() successfully reads indicator buffers")
            print("   - Universal validation architecture is VIABLE")
            print()
            print("✅ PROCEED TO NEXT SPIKE TEST (Registry Pattern)")
            return 0
        else:
            print("\n💥 CRITICAL TEST FAILED!")
            print("\n❌ FALLBACK REQUIRED:")
            print("   1. Create LaguerreRSIModule.mqh (pattern from RSIModule.mqh)")
            print("   2. Extend ExportAligned.mq5 to use LaguerreRSIModule")
            print("   3. Use MQL5 CSV export instead of mt5.copy_buffer()")
            print()
            print("❌ UNIVERSAL ARCHITECTURE REQUIRES MODIFICATION")
            return 1

    finally:
        # Always shutdown MT5
        print("\n[Cleanup] Shutting down MT5...")
        mt5.shutdown()
        print("✅ MT5 shutdown cleanly")


if __name__ == "__main__":
    sys.exit(main())
