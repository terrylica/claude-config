#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyrogram>=2.0.106", "tgcrypto>=1.2.5"]
# ///
"""
Telegram Authentication Script (Non-Interactive)

Purpose: One-time authentication with Telegram using 2FA (non-interactive mode).
Version: 2.1.0
Specification: link-validation-autofix-system.yaml (Phase 0, Step 3)

Error Handling: Fail fast - raise all errors, no fallbacks or defaults.

Usage:
    # Step 1: Trigger code to be sent
    doppler run -p claude-config -c dev -- uv run auth-telegram-noninteractive.py --send-code

    # Step 2: After receiving code, authenticate
    export TELEGRAM_CODE="12345"  # Your confirmation code
    export TELEGRAM_PASSWORD="your-2fa-password"  # Optional, if 2FA enabled
    doppler run -p claude-config -c dev -- uv run auth-telegram-noninteractive.py --authenticate

Credentials (from SSoT):
    Phone: +1 604 300 8878
    Username: EonLabsOperations

Changes from v2.0.0:
    - Non-interactive: accepts code via environment variable
    - Two-step process: send code, then authenticate with code
"""

import sys
import os
from pathlib import Path

from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded


# User configuration from SSoT
PHONE_NUMBER = "+16043008878"
SESSION_NAME = "telegram_session"
SESSION_FILE = Path.cwd() / f"{SESSION_NAME}.session"


def get_api_credentials():
    """Get API credentials from environment variables."""
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        raise RuntimeError(
            "Missing Telegram API credentials.\n\n"
            "Run with: doppler run -p claude-config -c dev -- uv run auth-telegram-noninteractive.py\n"
        )

    try:
        api_id = int(api_id)
    except ValueError:
        raise RuntimeError(f"TELEGRAM_API_ID must be an integer, got: {api_id}")

    return api_id, api_hash


async def send_code_step():
    """Step 1: Send confirmation code and wait for it."""
    print("="*60)
    print("Telegram Authentication")
    print("="*60)
    print()

    # Check if already authenticated
    if SESSION_FILE.exists():
        print(f"⚠️  Session already exists: {SESSION_FILE}")
        print("Delete it to start fresh: rm telegram_session.session")
        print()
        return 1

    # Get confirmation code from environment
    code = os.getenv("TELEGRAM_CODE")
    if not code:
        print("❌ Missing TELEGRAM_CODE environment variable")
        print()
        print("Usage:")
        print("  # Telegram will send you a code, then run:")
        print("  export TELEGRAM_CODE=\"12345\"")
        print("  export TELEGRAM_PASSWORD=\"your-2fa-password\"  # If 2FA enabled")
        print("  doppler run -p claude-config -c dev -- uv run auth-telegram-noninteractive.py --send-code")
        print()
        return 1

    # Get API credentials
    try:
        api_id, api_hash = get_api_credentials()
        print("✅ API credentials found")
    except Exception as e:
        print(f"❌ {e}")
        return 1

    print(f"📱 Phone number: {PHONE_NUMBER}")
    print(f"✅ Confirmation code: {code}")
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

        print("🔐 Connecting to Telegram...")
        print()

        await app.connect()

        # Send code request
        sent_code = await app.send_code(PHONE_NUMBER)
        print("✅ Code request sent")
        print()

        # Sign in with code
        print("🔐 Authenticating with code...")
        try:
            signed_in = await app.sign_in(PHONE_NUMBER, sent_code.phone_code_hash, code)
            print("✅ Code accepted!")
            print()

        except SessionPasswordNeeded:
            # 2FA password required
            password = os.getenv("TELEGRAM_PASSWORD")
            if not password:
                print("❌ 2FA password required but TELEGRAM_PASSWORD not set")
                print()
                print("Usage:")
                print("  export TELEGRAM_PASSWORD=\"your-2fa-password\"")
                print("  doppler run -p claude-config -c dev -- uv run auth-telegram-noninteractive.py --send-code")
                print()
                await app.disconnect()
                return 1

            print("🔐 2FA enabled, checking password...")
            signed_in = await app.check_password(password)
            print("✅ 2FA password accepted!")
            print()

        # Get user info
        me = await signed_in.user

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

        await app.disconnect()

        return 0

    except Exception as e:
        print()
        print("="*60)
        print("❌ Authentication Failed")
        print("="*60)
        print()
        print(f"Error: {e}")
        print()
        return 1


async def authenticate_step():
    """Step 2: Authenticate with confirmation code."""
    print("="*60)
    print("Telegram Authentication - Step 2: Authenticate")
    print("="*60)
    print()

    # Get confirmation code
    code = os.getenv("TELEGRAM_CODE")
    if not code:
        print("❌ Missing TELEGRAM_CODE environment variable")
        print()
        print("Usage:")
        print("  export TELEGRAM_CODE=\"12345\"")
        print("  doppler run -p claude-config -c dev -- uv run auth-telegram-noninteractive.py --authenticate")
        print()
        return 1

    # Get API credentials
    try:
        api_id, api_hash = get_api_credentials()
        print("✅ API credentials found")
    except Exception as e:
        print(f"❌ {e}")
        return 1

    print(f"✅ Confirmation code: {code}")
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

        print("🔐 Authenticating...")
        print()

        await app.connect()

        # Send code
        sent_code = await app.send_code(PHONE_NUMBER)

        # Sign in with code
        try:
            signed_in = await app.sign_in(PHONE_NUMBER, sent_code.phone_code_hash, code)

            print("✅ Code accepted!")
            print()

        except SessionPasswordNeeded:
            # 2FA password required
            password = os.getenv("TELEGRAM_PASSWORD")
            if not password:
                print("❌ 2FA password required but TELEGRAM_PASSWORD not set")
                print()
                print("Usage:")
                print("  export TELEGRAM_PASSWORD=\"your-2fa-password\"")
                print("  doppler run -p claude-config -c dev -- uv run auth-telegram-noninteractive.py --authenticate")
                print()
                await app.disconnect()
                return 1

            print("🔐 2FA enabled, checking password...")
            signed_in = await app.check_password(password)
            print("✅ 2FA password accepted!")
            print()

        # Get user info
        me = await signed_in.user

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

        await app.disconnect()

        return 0

    except Exception as e:
        print()
        print("="*60)
        print("❌ Authentication Failed")
        print("="*60)
        print()
        print(f"Error: {e}")
        print()
        return 1


async def main():
    """Main entry point."""
    if "--send-code" in sys.argv:
        return await send_code_step()
    elif "--authenticate" in sys.argv:
        return await authenticate_step()
    else:
        print("Usage:")
        print("  # Step 1: Send confirmation code")
        print("  doppler run -p claude-config -c dev -- uv run auth-telegram-noninteractive.py --send-code")
        print()
        print("  # Step 2: Authenticate with code")
        print("  export TELEGRAM_CODE=\"12345\"")
        print("  export TELEGRAM_PASSWORD=\"your-password\"  # If 2FA enabled")
        print("  doppler run -p claude-config -c dev -- uv run auth-telegram-noninteractive.py --authenticate")
        print()
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
