"""
generate_mt5_config.py - MT5 Startup Configuration Generator
Version: 1.0.0
Created: 2025-10-16

Purpose: Generate MT5 config.ini files for automated script execution
Uses [StartUp] section to run scripts without GUI interaction

Usage:
    python generate_mt5_config.py --script ExportAligned.ex5 --symbol EURUSD --period M1 --output config.ini
    python generate_mt5_config.py --script ExportAligned.ex5 --symbol XAUUSD --period H1 --params "InpUseLaguerreRSI:true"

Configuration Method:
    terminal64.exe /config:config.ini
    - Starts MT5 terminal
    - Runs specified script on symbol/timeframe
    - Closes terminal when script completes (if ShutdownTerminal=1)

References:
    - Official docs: https://www.metatrader5.com/en/terminal/help/start_advanced/start
    - Research audit: ChatGPT (OpenAI GPT-4) 2025-10-16
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional


class ConfigGenerationError(Exception):
    """Raised when config generation fails"""
    pass


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate MT5 startup config.ini for automated script execution"
    )
    parser.add_argument(
        "--script",
        required=True,
        help="Script path relative to MQL5/Scripts (e.g., DataExport/ExportAligned.ex5)"
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
        "--output",
        default="mt5_startup.ini",
        help="Output config file path (default: mt5_startup.ini)"
    )
    parser.add_argument(
        "--params",
        nargs="*",
        default=[],
        help="Script parameters in key:value format (e.g., InpUseLaguerreRSI:true InpBars:5000)"
    )
    parser.add_argument(
        "--shutdown",
        type=int,
        choices=[0, 1],
        default=1,
        help="Shutdown terminal after script completes (0=no, 1=yes, default: 1)"
    )
    parser.add_argument(
        "--login",
        help="MT5 account login (optional, uses saved credentials if omitted)"
    )
    parser.add_argument(
        "--password",
        help="MT5 account password (optional)"
    )
    parser.add_argument(
        "--server",
        help="MT5 broker server (optional)"
    )
    return parser.parse_args()


def parse_script_parameters(param_list: List[str]) -> Dict[str, str]:
    """
    Parse script parameters from key:value format

    Args:
        param_list: List of "key:value" strings

    Returns:
        Dictionary of parameter names to values

    Raises:
        ConfigGenerationError: If parameter format is invalid
    """
    params = {}
    for param in param_list:
        if ":" not in param:
            raise ConfigGenerationError(
                f"Invalid parameter format: {param}\n"
                f"Expected format: key:value (e.g., InpBars:5000)"
            )
        key, value = param.split(":", 1)
        params[key] = value
    return params


def validate_script_path(script_path: str) -> str:
    """
    Validate and format script path

    Args:
        script_path: Script path relative to MQL5/Scripts

    Returns:
        Validated script path

    Raises:
        ConfigGenerationError: If path is invalid
    """
    # Ensure .ex5 extension
    if not script_path.endswith(".ex5"):
        script_path = script_path + ".ex5"

    # Convert forward slashes to backslashes (Windows path style)
    script_path = script_path.replace("/", "\\")

    # Script path should be relative to MQL5/Scripts
    # Remove leading "Scripts\" if present (will be added by MT5)
    if script_path.startswith("Scripts\\"):
        script_path = script_path[8:]

    return script_path


def generate_config_ini(
    script: str,
    symbol: str,
    period: str,
    params: Dict[str, str],
    shutdown: int,
    login: Optional[str] = None,
    password: Optional[str] = None,
    server: Optional[str] = None
) -> str:
    """
    Generate MT5 config.ini content

    Args:
        script: Script path relative to MQL5/Scripts
        symbol: Trading symbol
        period: Timeframe period
        params: Script parameters
        shutdown: Shutdown terminal after script (0 or 1)
        login: MT5 account login (optional)
        password: MT5 account password (optional)
        server: MT5 broker server (optional)

    Returns:
        Config.ini file content as string
    """
    lines = []

    # [Common] section (optional login credentials)
    if login or password or server:
        lines.append("[Common]")
        if login:
            lines.append(f"Login={login}")
        if password:
            lines.append(f"Password={password}")
        if server:
            lines.append(f"Server={server}")
        lines.append("")

    # [StartUp] section (required for script execution)
    lines.append("[StartUp]")
    lines.append(f"Script={script}")
    lines.append(f"Symbol={symbol}")
    lines.append(f"Period={period}")

    # Add script parameters as separate Expert= lines
    # Note: MT5 doesn't have a direct way to pass input parameters via config
    # Parameters must be set via .set files or the script must use default values
    # We document them in comments for reference
    if params:
        lines.append("")
        lines.append("; Script Parameters (set via .set file or defaults):")
        for key, value in params.items():
            lines.append(f"; {key}={value}")
        lines.append("")

    # ShutdownTerminal flag
    lines.append(f"ShutdownTerminal={shutdown}")
    lines.append("")

    # Add documentation comment
    lines.insert(0, f"; MT5 Startup Configuration")
    lines.insert(1, f"; Generated by generate_mt5_config.py")
    lines.insert(2, f"; Script: {script}")
    lines.insert(3, f"; Symbol: {symbol}, Period: {period}")
    lines.insert(4, f"; Shutdown: {'Yes' if shutdown == 1 else 'No'}")
    lines.insert(5, "")

    return "\n".join(lines)


def write_config_file(content: str, output_path: str):
    """
    Write config content to file

    Args:
        content: Config.ini content
        output_path: Output file path

    Raises:
        ConfigGenerationError: If write fails
    """
    try:
        output_file = Path(output_path)
        output_file.write_text(content, encoding='utf-8')
    except Exception as e:
        raise ConfigGenerationError(f"Failed to write config file: {e}")


def main():
    """Main config generation workflow"""
    args = parse_args()

    print("=" * 70)
    print("MT5 Startup Configuration Generator")
    print("=" * 70)
    print(f"Script:   {args.script}")
    print(f"Symbol:   {args.symbol}")
    print(f"Period:   {args.period}")
    print(f"Output:   {args.output}")
    print(f"Shutdown: {'Yes' if args.shutdown == 1 else 'No'}")
    print()

    try:
        # Parse script parameters
        params = parse_script_parameters(args.params)
        if params:
            print("Parameters:")
            for key, value in params.items():
                print(f"  {key} = {value}")
            print()

        # Validate and format script path
        script_path = validate_script_path(args.script)
        print(f"Validated script path: {script_path}")
        print()

        # Generate config content
        print("Generating config.ini...")
        config_content = generate_config_ini(
            script=script_path,
            symbol=args.symbol,
            period=args.period,
            params=params,
            shutdown=args.shutdown,
            login=args.login,
            password=args.password,
            server=args.server
        )

        # Write to file
        write_config_file(config_content, args.output)
        print(f"Config written to: {args.output}")
        print()

        # Display config content
        print("Config Content:")
        print("-" * 70)
        print(config_content)
        print("-" * 70)
        print()

        # Usage instructions
        print("Usage:")
        print(f"  terminal64.exe /config:\"{Path(args.output).absolute()}\"")
        print()
        print("Notes:")
        print("  - Terminal will start, run the script, and close (if ShutdownTerminal=1)")
        print("  - Script parameters must be set via .set file or use defaults")
        print("  - Ensure MT5 terminal is not already running")
        print()

        return 0

    except ConfigGenerationError as e:
        print(f"\nConfig Generation Error: {e}")
        return 1

    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
