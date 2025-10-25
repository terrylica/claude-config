#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyrogram>=2.0.106", "tgcrypto>=1.2.5"]
# ///
"""
Telegram Authentication Script

Purpose: One-time authentication with Telegram using 2FA.
Version: 2.0.0
Specification: link-validation-autofix-system.yaml (Phase 0, Step 3)

Error Handling: Fail fast - raise all errors, no fallbacks or defaults.

Usage:
    doppler run -p claude-config -c dev -- uv run auth-telegram.py

Credentials (from SSoT):
    Phone: +1 604 300 8878
    Username: EonLabsOperations

Changes from v1.0.0:
    - Switched from pytdbot to Pyrogram (pytdbot lacks user auth support)
    - Pyrogram automatically handles phone/code/2FA prompts
    - Session saved as telegram_session.session
"""

import sys
import os
from pathlib import Path

from pyrogram import Client


# User configuration from SSoT
PHONE_NUMBER = "+16043008878"  # No spaces for API
SESSION_NAME = "telegram_session"
SESSION_FILE = Path.cwd() / f"{SESSION_NAME}.session"


def get_api_credentials():
    """Get API credentials from environment variables."""
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        raise RuntimeError(
            "Missing Telegram API credentials.\n\n"
            "Run with: doppler run -p claude-config -c dev -- uv run auth-telegram.py\n"
        )

    try:
        api_id = int(api_id)
    except ValueError:
        raise RuntimeError(f"TELEGRAM_API_ID must be an integer, got: {api_id}")

    return api_id, api_hash


async def main():
    """Authenticate with Telegram and save session."""
    print("="*60)
    print("Telegram Authentication")
    print("="*60)
    print()

    # Check if already authenticated
    if SESSION_FILE.exists():
        print(f"⚠️  Session already exists: {SESSION_FILE}")
        response = input("Overwrite? (yes/no): ").strip().lower()
        if response != "yes":
            print("Authentication cancelled.")
            return 1
        # Remove old session
        SESSION_FILE.unlink()
        print()

    # Get API credentials
    try:
        api_id, api_hash = get_api_credentials()
        print("✅ API credentials found")
    except Exception as e:
        print(f"❌ {e}")
        return 1

    print(f"📱 Phone number: {PHONE_NUMBER}")
    print()

    try:
        # Create Pyrogram client
        app = Client(
            name=SESSION_NAME,
            api_id=api_id,
            api_hash=api_hash,
            phone_number=PHONE_NUMBER,
            workdir=str(Path.cwd()),
        )

        print("🔐 Starting authentication...")
        print()
        print("Pyrogram will prompt you for:")
        print("  1. Verification code (sent to Telegram app)")
        print("  2. 2FA password (if enabled)")
        print()

        # Start client - Pyrogram handles all interactive prompts
        async with app:
            me = await app.get_me()

            print()
            print("="*60)
            print("✅ Authentication Successful")
            print("="*60)
            print()
            print(f"Logged in as: {me.first_name} (@{me.username or 'no username'})")
            print(f"User ID: {me.id}")
            print(f"Phone: {me.phone_number}")
            print()
            print(f"Session saved to: {SESSION_FILE}")
            print()
            print("Next step: Run create-bot-automated.py")
            print()

        return 0

    except KeyboardInterrupt:
        print()
        print("❌ Authentication cancelled by user")
        return 1

    except Exception as e:
        print()
        print("="*60)
        print("❌ Authentication Failed")
        print("="*60)
        print()
        print(f"Error: {e}")
        print()
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
