"""
run_validation.py - End-to-End Indicator Validation Orchestrator
Version: 1.0.0
Created: 2025-10-16

Purpose: Orchestrate full validation workflow from MQL5 export to Python validation
Automates: Config generation → MT5 execution → CSV validation → DuckDB storage

Usage:
    python run_validation.py --indicator laguerre_rsi --symbol EURUSD --period M1 --bars 100
    python run_validation.py --indicator laguerre_rsi --symbol XAUUSD --period H1 --bars 5000 --params atr_period=32

Workflow:
    1. Generate MT5 config.ini for ExportAligned.mq5
    2. Execute terminal64.exe /config:config.ini (automated script run)
    3. Wait for terminal shutdown (script completion)
    4. Load exported CSV
    5. Run validate_indicator.py
    6. Store results in validation.ddb
    7. Display summary

SLO: Availability 100% (no manual steps), Correctness 100% (correlation ≥ 0.999)
"""

import sys
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime
import os


class ValidationOrchestrationError(Exception):
    """Raised when orchestration workflow fails"""
    pass


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="End-to-end indicator validation orchestration"
    )
    parser.add_argument(
        "--indicator",
        required=True,
        choices=["laguerre_rsi", "rsi"],
        help="Indicator to validate"
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading symbol (e.g., EURUSD, XAUUSD)"
    )
    parser.add_argument(
        "--period",
        required=True,
        choices=["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"],
        help="Timeframe period"
    )
    parser.add_argument(
        "--bars",
        type=int,
        default=5000,
        help="Number of bars to export (default: 5000)"
    )
    parser.add_argument(
        "--params",
        nargs="*",
        default=[],
        help="Indicator parameters in key=value format"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.999,
        help="Correlation threshold (default: 0.999)"
    )
    parser.add_argument(
        "--db",
        default="validation.ddb",
        help="DuckDB database file (default: validation.ddb)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="MT5 execution timeout in seconds (default: 300)"
    )
    parser.add_argument(
        "--keep-config",
        action="store_true",
        help="Keep generated config.ini file after execution"
    )
    return parser.parse_args()


def get_wine_paths():
    """
    Get Wine environment paths

    Returns:
        Dictionary with wine executable, wineprefix, and terminal paths

    Raises:
        ValidationOrchestrationError: If paths not found
    """
    # Detect environment
    bottle_root = Path.home() / "Library/Application Support/CrossOver/Bottles/MetaTrader 5"

    if not bottle_root.exists():
        raise ValidationOrchestrationError(
            f"CrossOver bottle not found: {bottle_root}\n"
            f"Ensure MetaTrader 5 is installed in CrossOver"
        )

    wine_exe = Path.home() / "Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine"
    if not wine_exe.exists():
        raise ValidationOrchestrationError(
            f"Wine executable not found: {wine_exe}\n"
            f"Ensure CrossOver is installed"
        )

    terminal_exe = bottle_root / "drive_c/Program Files/MetaTrader 5/terminal64.exe"
    if not terminal_exe.exists():
        raise ValidationOrchestrationError(
            f"MT5 terminal not found: {terminal_exe}\n"
            f"Ensure MetaTrader 5 is installed"
        )

    return {
        "wine": str(wine_exe),
        "wineprefix": str(bottle_root),
        "terminal": str(terminal_exe),
        "bottle_root": bottle_root
    }


def generate_config(symbol: str, period: str, bars: int, indicator: str, output_path: Path) -> Path:
    """
    Generate MT5 config.ini file

    Args:
        symbol: Trading symbol
        period: Timeframe period
        bars: Number of bars
        indicator: Indicator name
        output_path: Output config file path

    Returns:
        Path to generated config file

    Raises:
        ValidationOrchestrationError: If generation fails
    """
    print("[1/6] Generating MT5 config.ini...")

    # Map indicator to script parameters
    script_params = []
    if indicator == "laguerre_rsi":
        script_params = [
            f"InpUseLaguerreRSI:true",
            f"InpBars:{bars}"
        ]
    elif indicator == "rsi":
        script_params = [
            f"InpUseRSI:true",
            f"InpBars:{bars}"
        ]

    # Build command
    cmd = [
        sys.executable,
        "generate_mt5_config.py",
        "--script", "DataExport/ExportAligned.ex5",
        "--symbol", symbol,
        "--period", period,
        "--output", str(output_path),
        "--shutdown", "1"
    ]

    if script_params:
        cmd.extend(["--params"] + script_params)

    # Execute
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  Config generated: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        raise ValidationOrchestrationError(
            f"Config generation failed\n"
            f"Command: {' '.join(cmd)}\n"
            f"Exit code: {e.returncode}\n"
            f"Output: {e.stdout}\n"
            f"Error: {e.stderr}"
        )


def execute_mt5_script(wine_paths: dict, config_path: Path, timeout: int) -> Path:
    """
    Execute MT5 terminal with config.ini

    Args:
        wine_paths: Wine environment paths
        config_path: Config.ini file path
        timeout: Execution timeout in seconds

    Returns:
        Path to exported CSV file

    Raises:
        ValidationOrchestrationError: If execution fails or times out
    """
    print("[2/6] Executing MT5 terminal...")
    print(f"  Config: {config_path}")
    print(f"  Timeout: {timeout}s")

    # Build Wine command
    # Need to convert Unix path to Windows path for Wine
    config_win_path = str(config_path).replace(str(wine_paths["bottle_root"]) + "/drive_c/", "C:/").replace("/", "\\")

    cmd = [
        wine_paths["wine"],
        wine_paths["terminal"].replace(str(wine_paths["bottle_root"]) + "/drive_c/", "C:/").replace("/", "\\"),
        f"/config:{config_win_path}"
    ]

    env = os.environ.copy()
    env["WINEPREFIX"] = wine_paths["wineprefix"]
    env["CX_BOTTLE"] = "MetaTrader 5"

    print(f"  Command: {' '.join(cmd)}")

    # Execute
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            env=env,
            check=False,  # Don't raise on non-zero exit (terminal might return non-zero even on success)
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start_time
        print(f"  Terminal completed in {elapsed:.1f}s (exit code: {result.returncode})")

        # Check if CSV was created
        # Expected CSV path: C:/users/crossover/exports/Export_{symbol}_{period}.csv
        expected_csv = wine_paths["bottle_root"] / f"drive_c/users/crossover/exports/Export_{args.symbol}_PERIOD_{args.period}.csv"

        if not expected_csv.exists():
            raise ValidationOrchestrationError(
                f"CSV export not found: {expected_csv}\n"
                f"MT5 script may have failed\n"
                f"Check MT5 logs: {wine_paths['bottle_root']}/drive_c/Program Files/MetaTrader 5/logs/"
            )

        print(f"  CSV created: {expected_csv.name}")
        return expected_csv

    except subprocess.TimeoutExpired:
        raise ValidationOrchestrationError(
            f"MT5 execution timed out after {timeout}s\n"
            f"Script may be stuck or export is taking too long\n"
            f"Try increasing --timeout or reducing --bars"
        )
    except Exception as e:
        raise ValidationOrchestrationError(f"MT5 execution failed: {e}")


def run_validation(csv_path: Path, indicator: str, params: list, threshold: float, db_path: str) -> dict:
    """
    Run validate_indicator.py on exported CSV

    Args:
        csv_path: Path to CSV file
        indicator: Indicator name
        params: Indicator parameters
        threshold: Correlation threshold
        db_path: DuckDB database path

    Returns:
        Validation results dictionary

    Raises:
        ValidationOrchestrationError: If validation fails
    """
    print("[3/6] Running validation...")
    print(f"  CSV: {csv_path.name}")
    print(f"  Indicator: {indicator}")
    print(f"  Threshold: {threshold}")

    # Build command
    cmd = [
        sys.executable,
        "validate_indicator.py",
        "--csv", str(csv_path),
        "--indicator", indicator,
        "--threshold", str(threshold),
        "--db", db_path
    ]

    if params:
        cmd.extend(["--params"] + params)

    # Execute
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        # Print validation output
        print()
        print("  Validation Output:")
        print("  " + "-" * 66)
        for line in result.stdout.split("\n"):
            if line.strip():
                print(f"  {line}")
        print("  " + "-" * 66)
        print()

        # Check exit code
        if result.returncode != 0:
            raise ValidationOrchestrationError(
                f"Validation failed (exit code: {result.returncode})\n"
                f"One or more buffers below correlation threshold"
            )

        return {"status": "success", "exit_code": result.returncode}

    except Exception as e:
        raise ValidationOrchestrationError(f"Validation execution failed: {e}")


def display_summary(results: dict, elapsed_time: float):
    """Display validation summary"""
    print("[4/6] Validation Summary")
    print("=" * 70)
    print(f"Status: {'PASS' if results['status'] == 'success' else 'FAIL'}")
    print(f"Total time: {elapsed_time:.1f}s")
    print()
    print("Results stored in validation.ddb")
    print("Query latest results:")
    print("  SELECT * FROM latest_validations;")
    print("=" * 70)


def cleanup(config_path: Path, keep_config: bool):
    """Clean up temporary files"""
    print("[5/6] Cleanup...")
    if not keep_config and config_path.exists():
        config_path.unlink()
        print(f"  Removed: {config_path}")
    else:
        print(f"  Kept: {config_path}")


def main():
    """Main orchestration workflow"""
    global args  # Make args available to execute_mt5_script
    args = parse_args()

    print("=" * 70)
    print("Indicator Validation Orchestration")
    print("=" * 70)
    print(f"Indicator: {args.indicator}")
    print(f"Symbol:    {args.symbol}")
    print(f"Period:    {args.period}")
    print(f"Bars:      {args.bars}")
    print(f"Threshold: {args.threshold}")
    print()

    start_time = time.time()
    config_path = None

    try:
        # Get Wine environment
        wine_paths = get_wine_paths()
        print(f"Wine:      {wine_paths['wine']}")
        print(f"Terminal:  {Path(wine_paths['terminal']).name}")
        print()

        # Generate config
        config_path = Path(f"mt5_startup_{args.symbol}_{args.period}.ini")
        generate_config(args.symbol, args.period, args.bars, args.indicator, config_path)
        print()

        # Execute MT5 script
        csv_path = execute_mt5_script(wine_paths, config_path, args.timeout)
        print()

        # Run validation
        results = run_validation(csv_path, args.indicator, args.params, args.threshold, args.db)
        print()

        # Display summary
        elapsed = time.time() - start_time
        display_summary(results, elapsed)
        print()

        # Cleanup
        cleanup(config_path, args.keep_config)
        print()

        print("[6/6] Validation Complete")
        return 0

    except ValidationOrchestrationError as e:
        print(f"\nOrchestration Error: {e}")
        if config_path and config_path.exists():
            print(f"\nConfig file preserved for debugging: {config_path}")
        return 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130

    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
