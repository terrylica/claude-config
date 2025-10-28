#!/usr/bin/env python3
"""
Unit tests for telegram_helpers.py

Run: python test_telegram_helpers.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from telegram_helpers import ensure_valid_markdown


def test_bold_unclosed():
    """Test unclosed bold tag"""
    input_text = "Hello **world"
    expected = "Hello **world**"
    result = ensure_valid_markdown(input_text)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ test_bold_unclosed")


def test_italic_unclosed():
    """Test unclosed italic tag"""
    input_text = "Hello *world"
    expected = "Hello *world*"
    result = ensure_valid_markdown(input_text)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ test_italic_unclosed")


def test_inline_code_unclosed():
    """Test unclosed inline code"""
    input_text = "Code: `print(hello"
    expected = "Code: `print(hello`"
    result = ensure_valid_markdown(input_text)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ test_inline_code_unclosed")


def test_code_block_unclosed():
    """Test unclosed code block"""
    input_text = "```python\ndef foo():\n    pass"
    expected = "```python\ndef foo():\n    pass```"
    result = ensure_valid_markdown(input_text)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ test_code_block_unclosed")


def test_multiple_unclosed():
    """Test multiple unclosed tags"""
    input_text = "**Bold and `code"
    expected = "**Bold and `code`**"
    result = ensure_valid_markdown(input_text)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ test_multiple_unclosed")


def test_already_valid():
    """Test already valid markdown"""
    input_text = "**Bold** and *italic* and `code`"
    expected = "**Bold** and *italic* and `code`"
    result = ensure_valid_markdown(input_text)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ test_already_valid")


def test_empty_string():
    """Test empty string"""
    input_text = ""
    expected = ""
    result = ensure_valid_markdown(input_text)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ test_empty_string")


def test_no_markdown():
    """Test plain text with no markdown"""
    input_text = "Hello world"
    expected = "Hello world"
    result = ensure_valid_markdown(input_text)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ test_no_markdown")


def test_nested_bold_italic():
    """Test nested bold and italic (unclosed)"""
    input_text = "**Bold with *italic"
    # Both bold (**) and italic (*) are unclosed
    expected = "**Bold with *italic***"  # Closes italic (*) then bold (**)
    result = ensure_valid_markdown(input_text)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ test_nested_bold_italic")


def run_all_tests():
    """Run all tests"""
    print("Running telegram_helpers tests...\n")

    tests = [
        test_bold_unclosed,
        test_italic_unclosed,
        test_inline_code_unclosed,
        test_code_block_unclosed,
        test_multiple_unclosed,
        test_already_valid,
        test_empty_string,
        test_no_markdown,
        test_nested_bold_italic,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1

    print(f"\n{len(tests) - failed}/{len(tests)} tests passed")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
