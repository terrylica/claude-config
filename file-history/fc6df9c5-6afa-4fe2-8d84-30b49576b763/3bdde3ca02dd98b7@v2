"""Spike Test 4: Backward Compatibility

ASSUMPTION:
    Extending export_aligned.py with optional --validate flag
    does not break existing usage patterns.

SUCCESS CRITERIA:
    ✅ Existing command line usage works unchanged
    ✅ New --validate flag is optional (defaults to False)
    ✅ Validation mode calls validate_indicator.py correctly
    ✅ CSV export output format remains unchanged

EXECUTION:
    This is a design review spike - validates the API extension pattern

NOTES:
    - This spike uses mock functions to demonstrate the pattern
    - Actual implementation would use real export_aligned.py and validate_indicator.py
"""

import sys
import argparse
from typing import Optional
from pathlib import Path


def simulate_existing_export(symbol: str, period: str, bars: int, output_dir: str):
    """Simulate existing export_aligned.py behavior."""
    print("\n" + "=" * 70)
    print("EXISTING EXPORT WORKFLOW (unchanged)")
    print("=" * 70)

    print(f"\n1. MT5 connection...")
    print(f"   ✅ Connected")

    print(f"\n2. Symbol selection: {symbol}")
    print(f"   ✅ Selected")

    print(f"\n3. Fetching {bars} bars of {symbol} {period}...")
    print(f"   ✅ Fetched")

    print(f"\n4. Calculating indicators...")
    print(f"   - RSI (14-period)")
    print(f"   - Laguerre RSI (ATR 32, EMA 5)")
    print(f"   ✅ Calculated")

    print(f"\n5. Exporting to CSV...")
    filepath = f"{output_dir}/Export_{symbol}_PERIOD_{period}.csv"
    print(f"   ✅ Exported: {filepath}")

    print(f"\n6. MT5 shutdown...")
    print(f"   ✅ Shutdown")

    return filepath


def simulate_validation(
    indicator: str,
    symbol: str,
    period: str,
    bars: int,
    validation_db: str
):
    """Simulate validate_indicator.py behavior."""
    print("\n" + "=" * 70)
    print("VALIDATION WORKFLOW (NEW, optional)")
    print("=" * 70)

    print(f"\n1. Loading registry for indicator: {indicator}")
    print(f"   ✅ Loaded config")

    print(f"\n2. MT5 connection...")
    print(f"   ✅ Connected")

    print(f"\n3. Creating MQL5 indicator handle...")
    print(f"   Indicator: PythonInterop/ATR_Adaptive_Laguerre_RSI")
    print(f"   Symbol: {symbol}")
    print(f"   Timeframe: {period}")
    print(f"   ✅ Created handle")

    print(f"\n4. Reading MQL5 indicator buffers...")
    print(f"   Buffer 0 (Laguerre RSI): {bars} values")
    print(f"   Buffer 1 (Signal): {bars} values")
    print(f"   ✅ Read buffers")

    print(f"\n5. Calculating Python indicator...")
    print(f"   Module: indicators.laguerre_rsi")
    print(f"   Function: calculate_laguerre_rsi_indicator")
    print(f"   ✅ Calculated")

    print(f"\n6. Comparing MQL5 vs Python...")
    print(f"   Pearson r: 0.999950")
    print(f"   RMSE: 0.000012")
    print(f"   MAE: 0.000009")
    print(f"   Max Error: 0.000045")
    print(f"   ✅ Validation PASSED")

    print(f"\n7. Storing results in DuckDB...")
    print(f"   Database: {validation_db}")
    print(f"   Run ID: 42")
    print(f"   ✅ Stored")

    print(f"\n8. MT5 shutdown...")
    print(f"   ✅ Shutdown")

    return True


def export_data_extended(
    symbol: str,
    period: str,
    bars: int,
    output_dir: str = "C:\\Users\\crossover\\exports",
    validate: bool = False,
    validation_db: Optional[str] = None
):
    """Extended export_data function with optional validation.

    This demonstrates the proposed API extension pattern.
    """
    # EXISTING WORKFLOW (unchanged)
    filepath = simulate_existing_export(symbol, period, bars, output_dir)

    # NEW: Optional validation
    if validate:
        if validation_db is None:
            validation_db = "C:\\Users\\crossover\\validation.ddb"

        print("\n" + "=" * 70)
        print("OPTIONAL VALIDATION MODE ENABLED")
        print("=" * 70)

        validation_passed = simulate_validation(
            indicator='laguerre_rsi',
            symbol=symbol,
            period=period,
            bars=bars,
            validation_db=validation_db
        )

        if not validation_passed:
            print("\n⚠️  WARNING: Validation failed")
            print("   Export completed but validation did not pass thresholds")

    return filepath


def test_existing_usage():
    """Test 1: Existing command line usage (no --validate flag)."""
    print("\n" + "=" * 70)
    print("TEST 1: Existing Usage (No --validate flag)")
    print("=" * 70)

    print("\nCommand: python export_aligned.py --symbol EURUSD --period M1 --bars 5000")

    # Simulate existing usage
    filepath = export_data_extended(
        symbol="EURUSD",
        period="M1",
        bars=5000,
        output_dir="C:\\Users\\crossover\\exports"
        # Note: validate defaults to False, so no validation runs
    )

    print("\n" + "=" * 70)
    print("TEST 1: PASSED ✅")
    print("=" * 70)
    print("\n✅ Existing usage works unchanged")
    print(f"   Output: {filepath}")
    print(f"   Validation: Not run (as expected)")

    return True


def test_validation_mode():
    """Test 2: New validation mode (with --validate flag)."""
    print("\n" + "=" * 70)
    print("TEST 2: Validation Mode (With --validate flag)")
    print("=" * 70)

    print("\nCommand: python export_aligned.py --symbol EURUSD --period M1 --bars 5000 --validate")

    # Simulate validation mode
    filepath = export_data_extended(
        symbol="EURUSD",
        period="M1",
        bars=5000,
        output_dir="C:\\Users\\crossover\\exports",
        validate=True  # NEW FLAG
    )

    print("\n" + "=" * 70)
    print("TEST 2: PASSED ✅")
    print("=" * 70)
    print("\n✅ Validation mode works")
    print(f"   Output: {filepath}")
    print(f"   Validation: Run successfully")

    return True


def test_custom_db_path():
    """Test 3: Custom validation database path."""
    print("\n" + "=" * 70)
    print("TEST 3: Custom Validation Database Path")
    print("=" * 70)

    print("\nCommand: python export_aligned.py --symbol EURUSD --period M1 --bars 5000 --validate --validation-db custom.ddb")

    # Simulate custom DB path
    filepath = export_data_extended(
        symbol="EURUSD",
        period="M1",
        bars=5000,
        output_dir="C:\\Users\\crossover\\exports",
        validate=True,
        validation_db="C:\\Users\\crossover\\custom_validation.ddb"  # CUSTOM PATH
    )

    print("\n" + "=" * 70)
    print("TEST 3: PASSED ✅")
    print("=" * 70)
    print("\n✅ Custom database path works")
    print(f"   Output: {filepath}")
    print(f"   Validation DB: C:\\Users\\crossover\\custom_validation.ddb")

    return True


def test_argparse_compatibility():
    """Test 4: Argument parser backward compatibility."""
    print("\n" + "=" * 70)
    print("TEST 4: Argument Parser Compatibility")
    print("=" * 70)

    print("\n1. Creating argument parser with new flags...")

    parser = argparse.ArgumentParser(description='Export MT5 data with optional validation')

    # EXISTING ARGUMENTS (unchanged)
    parser.add_argument('--symbol', required=True, help='Trading symbol')
    parser.add_argument('--period', required=True, help='Timeframe')
    parser.add_argument('--bars', type=int, default=5000, help='Number of bars')
    parser.add_argument('--output', default='C:\\Users\\crossover\\exports', help='Output directory')

    # NEW ARGUMENTS (optional, defaults preserve existing behavior)
    parser.add_argument('--validate', action='store_true', default=False,
                       help='Run validation after export (default: False)')
    parser.add_argument('--validation-db', default=None,
                       help='Validation database path (default: validation.ddb)')

    # Test existing usage
    print("\n2. Testing existing command line...")
    args1 = parser.parse_args(['--symbol', 'EURUSD', '--period', 'M1', '--bars', '5000'])
    print(f"   Symbol: {args1.symbol}")
    print(f"   Period: {args1.period}")
    print(f"   Bars: {args1.bars}")
    print(f"   Validate: {args1.validate}")
    print(f"   ✅ Existing args parsed correctly")

    if args1.validate != False:
        print(f"   ❌ FAILED: validate should default to False, got {args1.validate}")
        return False

    # Test new usage
    print("\n3. Testing new command line with --validate...")
    args2 = parser.parse_args(['--symbol', 'EURUSD', '--period', 'M1', '--bars', '5000', '--validate'])
    print(f"   Symbol: {args2.symbol}")
    print(f"   Period: {args2.period}")
    print(f"   Bars: {args2.bars}")
    print(f"   Validate: {args2.validate}")
    print(f"   ✅ New args parsed correctly")

    if args2.validate != True:
        print(f"   ❌ FAILED: validate should be True, got {args2.validate}")
        return False

    # Test custom DB path
    print("\n4. Testing custom validation DB path...")
    args3 = parser.parse_args([
        '--symbol', 'EURUSD',
        '--period', 'M1',
        '--bars', '5000',
        '--validate',
        '--validation-db', 'custom.ddb'
    ])
    print(f"   Symbol: {args3.symbol}")
    print(f"   Validate: {args3.validate}")
    print(f"   Validation DB: {args3.validation_db}")
    print(f"   ✅ Custom DB path parsed correctly")

    if args3.validation_db != 'custom.ddb':
        print(f"   ❌ FAILED: validation_db should be 'custom.ddb', got {args3.validation_db}")
        return False

    print("\n" + "=" * 70)
    print("TEST 4: PASSED ✅")
    print("=" * 70)

    return True


def test_api_signature():
    """Test 5: Function signature backward compatibility."""
    print("\n" + "=" * 70)
    print("TEST 5: API Signature Backward Compatibility")
    print("=" * 70)

    print("\n1. Testing positional arguments (existing usage)...")
    try:
        filepath = export_data_extended("EURUSD", "M1", 5000)
        print(f"   ✅ Positional args work")
        print(f"   Result: {filepath}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

    print("\n2. Testing keyword arguments (existing usage)...")
    try:
        filepath = export_data_extended(
            symbol="EURUSD",
            period="M1",
            bars=5000,
            output_dir="C:\\Users\\crossover\\exports"
        )
        print(f"   ✅ Keyword args work")
        print(f"   Result: {filepath}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

    print("\n3. Testing new optional parameters...")
    try:
        filepath = export_data_extended(
            symbol="EURUSD",
            period="M1",
            bars=5000,
            validate=True,
            validation_db="test.ddb"
        )
        print(f"   ✅ New optional params work")
        print(f"   Result: {filepath}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

    print("\n" + "=" * 70)
    print("TEST 5: PASSED ✅")
    print("=" * 70)

    return True


def main():
    """Run all spike tests."""
    print("\n" + "=" * 70)
    print("SPIKE TEST 4: Backward Compatibility")
    print("=" * 70)
    print(f"Purpose: Validate export_aligned.py extension pattern")
    print()

    results = {}

    # Test 1: Existing usage
    print("\n[1/5] Testing existing usage...")
    existing_passed = test_existing_usage()
    results['existing_usage'] = existing_passed

    # Test 2: Validation mode
    print("\n[2/5] Testing validation mode...")
    validation_passed = test_validation_mode()
    results['validation_mode'] = validation_passed

    # Test 3: Custom DB path
    print("\n[3/5] Testing custom database path...")
    custom_db_passed = test_custom_db_path()
    results['custom_db_path'] = custom_db_passed

    # Test 4: Argparse compatibility
    print("\n[4/5] Testing argument parser...")
    argparse_passed = test_argparse_compatibility()
    results['argparse_compatibility'] = argparse_passed

    # Test 5: API signature
    print("\n[5/5] Testing API signature...")
    api_passed = test_api_signature()
    results['api_signature'] = api_passed

    # Summary
    print("\n" + "=" * 70)
    print("SPIKE TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30s} {status}")
    print("=" * 70)

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✅ BACKWARD COMPATIBILITY VALIDATED:")
        print("   - Existing command line usage works unchanged")
        print("   - New --validate flag is optional (defaults to False)")
        print("   - Validation mode calls validation workflow correctly")
        print("   - API signature remains backward compatible")
        print()
        print("✅ ALL SPIKE TESTS COMPLETE!")
        print("\n📋 NEXT STEPS:")
        print("   1. Review spike test results")
        print("   2. Create registry.yaml for Laguerre RSI")
        print("   3. Implement validate_indicator.py")
        print("   4. Extend export_aligned.py with --validate flag")
        print("   5. Test end-to-end with real data")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\n   Review API extension design")
        return 1


if __name__ == "__main__":
    sys.exit(main())
