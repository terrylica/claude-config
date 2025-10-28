#!/usr/bin/env python3
"""
Telegram Bot Safety Helpers - Rate Limiting and Markdown Validation

Provides fail-fast wrappers for Telegram API calls with:
- Rate limit handling (429 errors with exponential backoff)
- Markdown validation (close unclosed tags)
- Error propagation (no silent failures)

Specification: automation/lychee/specifications/telegram-bot-improvements.yaml
Version: 1.0.0
"""

import asyncio
import sys
from typing import Optional


async def safe_edit_message(
    query,
    text: str,
    parse_mode: str = "Markdown",
    max_retries: int = 3
) -> bool:
    """
    Edit Telegram message with rate limiting and markdown safety.

    Args:
        query: Telegram CallbackQuery object
        text: Message text to send
        parse_mode: Telegram parse mode (default: Markdown)
        max_retries: Maximum retry attempts for 429 errors

    Returns:
        True if successful

    Raises:
        telegram.error.TelegramError: On unrecoverable errors (propagated)
        RuntimeError: If max retries exhausted

    Fail-fast: All non-429 errors propagate immediately
    """
    import telegram

    # Validate and fix markdown
    safe_text = ensure_valid_markdown(text)

    # Retry loop for 429 errors only
    retry_count = 0
    while retry_count < max_retries:
        try:
            await query.edit_message_text(safe_text, parse_mode=parse_mode)
            return True

        except telegram.error.RetryAfter as e:
            # Telegram told us explicitly how long to wait
            wait_time = e.retry_after
            print(f"⚠️  Rate limit (RetryAfter): waiting {wait_time}s", file=sys.stderr)
            await asyncio.sleep(wait_time)
            retry_count += 1

        except telegram.error.TelegramError as e:
            # Check if it's a 429 without RetryAfter header
            if "429" in str(e):
                # Exponential backoff
                wait_time = 2 ** retry_count
                print(f"⚠️  Rate limit (429): backing off {wait_time}s", file=sys.stderr)
                await asyncio.sleep(wait_time)
                retry_count += 1
            else:
                # All other errors: fail-fast
                print(f"❌ Telegram error: {e}", file=sys.stderr)
                raise

    # Max retries exhausted
    error_msg = f"Failed to edit message after {max_retries} retries (rate limit)"
    print(f"❌ {error_msg}", file=sys.stderr)
    raise RuntimeError(error_msg)


async def safe_send_message(
    bot,
    chat_id: int,
    text: str,
    parse_mode: str = "Markdown",
    max_retries: int = 3,
    **kwargs
):
    """
    Send Telegram message with rate limiting and markdown safety.

    Args:
        bot: Telegram Bot instance
        chat_id: Telegram chat ID
        text: Message text
        parse_mode: Telegram parse mode (default: Markdown)
        max_retries: Maximum retry attempts for 429 errors
        **kwargs: Additional arguments passed to send_message

    Returns:
        Sent Message object

    Raises:
        telegram.error.TelegramError: On unrecoverable errors (propagated)
        RuntimeError: If max retries exhausted

    Fail-fast: All non-429 errors propagate immediately
    """
    import telegram

    # Validate and fix markdown
    safe_text = ensure_valid_markdown(text)

    # Retry loop for 429 errors only
    retry_count = 0
    while retry_count < max_retries:
        try:
            message = await bot.send_message(
                chat_id=chat_id,
                text=safe_text,
                parse_mode=parse_mode,
                **kwargs
            )
            return message

        except telegram.error.RetryAfter as e:
            wait_time = e.retry_after
            print(f"⚠️  Rate limit (RetryAfter): waiting {wait_time}s", file=sys.stderr)
            await asyncio.sleep(wait_time)
            retry_count += 1

        except telegram.error.TelegramError as e:
            if "429" in str(e):
                wait_time = 2 ** retry_count
                print(f"⚠️  Rate limit (429): backing off {wait_time}s", file=sys.stderr)
                await asyncio.sleep(wait_time)
                retry_count += 1
            else:
                # All other errors: fail-fast
                print(f"❌ Telegram error: {e}", file=sys.stderr)
                raise

    # Max retries exhausted
    error_msg = f"Failed to send message after {max_retries} retries (rate limit)"
    print(f"❌ {error_msg}", file=sys.stderr)
    raise RuntimeError(error_msg)


async def safe_edit_message_by_id(
    bot,
    chat_id: int,
    message_id: int,
    text: str,
    parse_mode: str = "Markdown",
    max_retries: int = 3
) -> bool:
    """
    Edit Telegram message by message_id with rate limiting and markdown safety.

    Args:
        bot: Telegram Bot instance
        chat_id: Telegram chat ID
        message_id: Message ID to edit
        text: Message text
        parse_mode: Telegram parse mode (default: Markdown)
        max_retries: Maximum retry attempts for 429 errors

    Returns:
        True if successful

    Raises:
        telegram.error.TelegramError: On unrecoverable errors (propagated)
        RuntimeError: If max retries exhausted

    Fail-fast: All non-429 errors propagate immediately
    """
    import telegram

    # Validate and fix markdown
    safe_text = ensure_valid_markdown(text)

    # Retry loop for 429 errors only
    retry_count = 0
    while retry_count < max_retries:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=safe_text,
                parse_mode=parse_mode
            )
            return True

        except telegram.error.RetryAfter as e:
            wait_time = e.retry_after
            print(f"⚠️  Rate limit (RetryAfter): waiting {wait_time}s", file=sys.stderr)
            await asyncio.sleep(wait_time)
            retry_count += 1

        except telegram.error.TelegramError as e:
            if "429" in str(e):
                wait_time = 2 ** retry_count
                print(f"⚠️  Rate limit (429): backing off {wait_time}s", file=sys.stderr)
                await asyncio.sleep(wait_time)
                retry_count += 1
            else:
                # All other errors: fail-fast
                print(f"❌ Telegram error: {e}", file=sys.stderr)
                raise

    # Max retries exhausted
    error_msg = f"Failed to edit message after {max_retries} retries (rate limit)"
    print(f"❌ {error_msg}", file=sys.stderr)
    raise RuntimeError(error_msg)


def ensure_valid_markdown(text: str) -> str:
    """
    Close unclosed markdown tags to prevent Telegram parse errors.

    Handles:
    - ``` (code blocks)
    - ` (inline code)
    - ** (bold)
    - * (italic)

    Args:
        text: Original text with potentially unclosed tags

    Returns:
        Text with unclosed tags closed

    Note: Closing order matters - most nested first
    """
    # Count occurrences of each markdown token
    code_block_count = text.count("```")
    total_backticks = text.count("`")

    # Code blocks use 3 backticks each
    inline_code_backticks = total_backticks - (code_block_count * 3)

    # Check if unclosed
    code_block_unclosed = code_block_count % 2
    inline_code_unclosed = inline_code_backticks % 2

    # Bold uses **
    bold_count = text.count("**")
    bold_unclosed = bold_count % 2

    # Italic uses single * (subtract ** pairs)
    total_asterisks = text.count("*")
    italic_asterisks = total_asterisks - (bold_count * 2)
    italic_unclosed = italic_asterisks % 2

    # Build closing tags (most nested first)
    closing_tags = []
    if code_block_unclosed:
        closing_tags.append("```")
    if inline_code_unclosed:
        closing_tags.append("`")
    if bold_unclosed:
        closing_tags.append("**")
    if italic_unclosed:
        closing_tags.append("*")

    if closing_tags:
        closing_str = "".join(closing_tags)
        print(f"[MARKDOWN] Closing unclosed tags: {closing_str}", file=sys.stderr)
        return text + closing_str

    return text
