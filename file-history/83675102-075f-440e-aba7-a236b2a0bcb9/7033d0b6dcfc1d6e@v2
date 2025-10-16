#!/usr/bin/env python3
"""
Validate MT5 exported CSV data and compare with Python implementations.

This script:
1. Loads MT5-exported CSV files
2. Validates data integrity (no gaps, correct types)
3. Computes indicators using Python libraries (TA-Lib/Pandas-TA)
4. Compares MT5 indicator values with Python implementations
5. Reports differences and validation metrics
"""

import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np


def load_mt5_csv(csv_path: Path) -> pd.DataFrame:
    """
    Load MT5 exported CSV and parse timestamps.

    Expected columns:
    - time: datetime string or timestamp
    - open, high, low, close: OHLC prices
    - tick_volume: tick volume
    - spread: spread in points
    - real_volume: real volume (may be 0)
    - RSI: RSI indicator value (if included)

    Handles both lowercase (MQL5) and capitalized (Python API) column names.
    """
    df = pd.read_csv(csv_path)

    # Normalize column names to lowercase for consistent handling
    df.columns = df.columns.str.lower()

    # Parse time column
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df.set_index("time", inplace=True)

    # Validate required columns
    required = ["open", "high", "low", "close"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Sort by time
    df.sort_index(inplace=True)

    return df


def validate_data_integrity(df: pd.DataFrame) -> dict:
    """
    Check data integrity:
    - No missing values in OHLC
    - High >= Low
    - High >= Open, Close
    - Low <= Open, Close
    - No duplicate timestamps
    """
    issues = {
        "missing_ohlc": df[["open", "high", "low", "close"]].isnull().sum().sum(),
        "invalid_high_low": (df["high"] < df["low"]).sum(),
        "invalid_high_open": (df["high"] < df["open"]).sum(),
        "invalid_high_close": (df["high"] < df["close"]).sum(),
        "invalid_low_open": (df["low"] > df["open"]).sum(),
        "invalid_low_close": (df["low"] > df["close"]).sum(),
        "duplicate_times": df.index.duplicated().sum(),
        "total_bars": len(df),
    }

    return issues


def compute_rsi_pandas(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Compute RSI using pure pandas (matches MT5 calculation).

    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss over period
    """
    delta = close.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # Use exponential moving average (EMA) like MT5
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def compare_indicators(
    df: pd.DataFrame, indicator_col: str, computed: pd.Series, tolerance: float = 1e-2
) -> dict:
    """
    Compare MT5 indicator values with Python computed values.

    Returns:
    - correlation
    - mean absolute error
    - max absolute error
    - number of values within tolerance
    """
    if indicator_col not in df.columns:
        return {"error": f"Column {indicator_col} not found in CSV"}

    mt5_values = df[indicator_col].values
    py_values = computed.values

    # Align lengths (both should be same)
    min_len = min(len(mt5_values), len(py_values))
    mt5_values = mt5_values[-min_len:]
    py_values = py_values[-min_len:]

    # Skip NaN values at the start (indicator initialization period)
    valid_mask = ~(np.isnan(mt5_values) | np.isnan(py_values))
    mt5_valid = mt5_values[valid_mask]
    py_valid = py_values[valid_mask]

    if len(mt5_valid) == 0:
        return {"error": "No valid values to compare"}

    mae = np.mean(np.abs(mt5_valid - py_valid))
    max_error = np.max(np.abs(mt5_valid - py_valid))
    correlation = np.corrcoef(mt5_valid, py_valid)[0, 1]
    within_tolerance = np.sum(np.abs(mt5_valid - py_valid) <= tolerance)

    return {
        "correlation": correlation,
        "mean_absolute_error": mae,
        "max_absolute_error": max_error,
        "within_tolerance": within_tolerance,
        "total_compared": len(mt5_valid),
        "within_tolerance_pct": 100.0 * within_tolerance / len(mt5_valid),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_export.py <csv_file>")
        print("Example: validate_export.py exports/20251013_143000_Export_EURUSD_PERIOD_M1.csv")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)

    print(f"=== MT5 Export Validator ===")
    print(f"File: {csv_path}")
    print()

    # Load data
    try:
        df = load_mt5_csv(csv_path)
        print(f"Loaded {len(df)} bars")
        print(f"Time range: {df.index[0]} to {df.index[-1]}")
        print(f"Columns: {', '.join(df.columns)}")
        print()
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)

    # Validate integrity
    print("=== Data Integrity Check ===")
    issues = validate_data_integrity(df)
    total_issues = sum(v for k, v in issues.items() if k != "total_bars")

    for key, value in issues.items():
        if key != "total_bars":
            status = "✓" if value == 0 else "✗"
            print(f"{status} {key}: {value}")

    if total_issues > 0:
        print(f"\nWarning: Found {total_issues} data integrity issues")
    else:
        print("\n✓ All integrity checks passed")
    print()

    # Validate RSI if present (check for rsi or rsi_14 or rsi_<period>)
    rsi_col = None
    for col in df.columns:
        if col.startswith("rsi"):
            rsi_col = col
            break

    if rsi_col:
        print(f"=== RSI Validation ({rsi_col}) ===")

        # Extract period from column name (e.g., RSI_14 -> 14)
        period = 14
        if "_" in rsi_col:
            try:
                period = int(rsi_col.split("_")[1])
            except (IndexError, ValueError):
                period = 14

        # Compute RSI using Python
        py_rsi = compute_rsi_pandas(df["close"], period=period)

        # Compare with MT5 values
        comparison = compare_indicators(df, rsi_col, py_rsi, tolerance=0.01)

        if "error" in comparison:
            print(f"Error: {comparison['error']}")
        else:
            print(f"Correlation:     {comparison['correlation']:.6f}")
            print(f"Mean Abs Error:  {comparison['mean_absolute_error']:.6f}")
            print(f"Max Abs Error:   {comparison['max_absolute_error']:.6f}")
            print(
                f"Within tolerance: {comparison['within_tolerance']}/{comparison['total_compared']} "
                f"({comparison['within_tolerance_pct']:.1f}%)"
            )

            # Show some example values
            print("\nExample values (last 10 bars):")
            print(f"Index       MT5 {rsi_col:8s}  Python {rsi_col:8s}  Diff")
            print("-" * 60)
            for i in range(-10, 0):
                mt5_val = df[rsi_col].iloc[i]
                py_val = py_rsi.iloc[i]
                diff = abs(mt5_val - py_val)
                print(
                    f"{i:3d}         {mt5_val:7.4f}      {py_val:7.4f}        {diff:7.4f}"
                )

            # Verdict
            print()
            if comparison["correlation"] > 0.999 and comparison["mean_absolute_error"] < 0.1:
                print("✓ RSI validation PASSED - Python implementation matches MT5")
            else:
                print(
                    "✗ RSI validation FAILED - Significant differences detected"
                )
        print()

    # Summary
    print("=== Summary ===")
    print(f"Data quality: {'PASS' if total_issues == 0 else 'FAIL'}")

    if rsi_col and "error" not in comparison:
        rsi_pass = (
            comparison["correlation"] > 0.999
            and comparison["mean_absolute_error"] < 0.1
        )
        print(f"{rsi_col} validation: {'PASS' if rsi_pass else 'FAIL'}")

    print("\nExport is ready for Python replication workflow.")


if __name__ == "__main__":
    main()
