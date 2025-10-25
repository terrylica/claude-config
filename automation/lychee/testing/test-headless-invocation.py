#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Test Headless Claude Code Invocation

Purpose: Verify Claude Code can be invoked via subprocess for auto-fix.
Version: 1.0.0

Usage:
    uv run test-headless-invocation.py
"""

import subprocess
import json
import sys


def test_headless_text_mode():
    """Test basic headless invocation with text output."""
    print("=" * 60)
    print("Test 1: Headless Text Mode")
    print("=" * 60)
    print()

    result = subprocess.run(
        ["claude", "-p", "What is 2+2? Answer in one word only."],
        capture_output=True,
        text=True,
        timeout=30
    )

    print(f"Exit code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    if result.stderr:
        print(f"Stderr: {result.stderr}")

    return result.returncode == 0


def test_headless_json_mode():
    """Test headless invocation with JSON output."""
    print()
    print("=" * 60)
    print("Test 2: Headless JSON Mode")
    print("=" * 60)
    print()

    result = subprocess.run(
        [
            "claude", "-p",
            "What is 3+3? Answer in one word only.",
            "--output-format", "json"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )

    print(f"Exit code: {result.returncode}")

    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print("JSON parsed successfully!")
            print(f"Response: {data.get('result', 'N/A')}")
            print(f"Cost: ${data.get('total_cost_usd', 'N/A')}")
            return True
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw stdout: {result.stdout}")
            return False
    else:
        print(f"Command failed with stderr: {result.stderr}")
        return False


def test_file_operation():
    """Test headless invocation that uses file tools."""
    print()
    print("=" * 60)
    print("Test 3: File Operation (Read this script)")
    print("=" * 60)
    print()

    result = subprocess.run(
        [
            "claude", "-p",
            "Read the file at /Users/terryli/.claude/automation/lychee/test-headless-invocation.py and tell me what it does in 10 words or less.",
            "--output-format", "json",
            "--allowedTools", "Read"
        ],
        capture_output=True,
        text=True,
        timeout=60
    )

    print(f"Exit code: {result.returncode}")

    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print("JSON parsed successfully!")
            print(f"Response: {data.get('result', 'N/A')}")
            return True
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return False
    else:
        print(f"Command failed with stderr: {result.stderr}")
        return False


def main():
    """Run all tests."""
    print("Testing Claude Code Headless Invocation")
    print()

    tests = [
        ("Text Mode", test_headless_text_mode),
        ("JSON Mode", test_headless_json_mode),
        ("File Operation", test_file_operation),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"Test '{name}' raised exception: {e}")
            results.append((name, False))

    print()
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    all_passed = all(passed for _, passed in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
