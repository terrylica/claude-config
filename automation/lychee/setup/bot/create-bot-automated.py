#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyrogram>=2.0.106", "tgcrypto>=1.2.5"]
# ///
"""
Automated Telegram Bot Creation Script

Purpose: Fully automated bot creation via BotFather using Pyrogram.
Version: 2.0.0
Specification: link-validation-autofix-system.yaml (Phase 0, Step 4)

Error Handling: Fail fast - raise all errors, no fallbacks or defaults.

Usage:
    doppler run -p claude-config -c dev -- uv run create-bot-automated.py

Prerequisites:
    - Authenticated session: telegram_session.session
    - Telegram account: EonLabsOperations (+1 604 300 8878)

Outputs:
    - Bot token → Doppler (TELEGRAM_BOT_TOKEN)
    - Chat ID → Doppler (TELEGRAM_CHAT_ID)

Changes from v1.0.0:
    - Switched from pytdbot to Pyrogram (pytdbot lacks user auth support)
    - Uses Pyrogram's simpler message sending API
    - Automated BotFather interaction via message parsing
"""

import sys
import os
import re
import asyncio
import subprocess
from pathlib import Path

from pyrogram import Client
from pyrogram.errors import FloodWait


# Configuration
SESSION_NAME = "telegram_session"
SESSION_FILE = Path.cwd() / f"{SESSION_NAME}.session"
BOTFATHER_USERNAME = "BotFather"
BOT_NAME = "Lychee Link Autofix Bot"
BOT_USERNAME = "lychee_link_autofix_bot"  # Must be unique globally


def get_api_credentials():
    """Get API credentials from environment variables."""
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        raise RuntimeError(
            "Missing Telegram API credentials.\n\n"
            "Run with: doppler run -p claude-config -c dev -- uv run create-bot-automated.py\n"
        )

    try:
        api_id = int(api_id)
    except ValueError:
        raise RuntimeError(f"TELEGRAM_API_ID must be an integer, got: {api_id}")

    return api_id, api_hash


def extract_bot_token(text: str) -> str:
    """Extract bot token from BotFather response.

    Token format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
    """
    pattern = r"(\d+:[A-Za-z0-9_-]+)"
    match = re.search(pattern, text)

    if not match:
        raise ValueError(f"Failed to extract bot token from response: {text}")

    return match.group(1)


def store_in_doppler(key: str, value: str) -> None:
    """Store secret in Doppler."""
    result = subprocess.run(
        [
            "doppler", "secrets", "set",
            f"{key}={value}",
            "-p", "claude-config",
            "-c", "dev",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to store {key} in Doppler: {result.stderr}")

    print(f"✅ {key} stored in Doppler")
    print()


async def main():
    """Create Telegram bot via BotFather automation."""
    print("="*60)
    print("Automated Bot Creation")
    print("="*60)
    print()

    # Check session exists
    if not SESSION_FILE.exists():
        print("❌ Session file not found")
        print(f"Expected: {SESSION_FILE}")
        print()
        print("Run authentication first:")
        print("  doppler run -p claude-config -c dev -- uv run auth-telegram.py")
        print()
        return 1

    # Get API credentials
    try:
        api_id, api_hash = get_api_credentials()
        print("✅ API credentials found")
    except Exception as e:
        print(f"❌ {e}")
        return 1

    print(f"✅ Session found: {SESSION_FILE}")
    print()

    try:
        # Create Pyrogram client
        app = Client(
            name=SESSION_NAME,
            api_id=api_id,
            api_hash=api_hash,
            workdir=str(Path.cwd()),
        )

        print("🔌 Connecting to Telegram...")

        async with app:
            print("✅ Connected")
            print()

            # Find BotFather
            print(f"🔍 Finding @{BOTFATHER_USERNAME}...")
            botfather = await app.resolve_peer(BOTFATHER_USERNAME)
            print(f"✅ Found @{BOTFATHER_USERNAME}")
            print()

            # Send /newbot command
            print("📤 Sending /newbot command...")
            await app.send_message(BOTFATHER_USERNAME, "/newbot")
            await asyncio.sleep(2)
            print("✅ Command sent")
            print()

            # Send bot name
            print(f"📤 Sending bot name: {BOT_NAME}")
            await app.send_message(BOTFATHER_USERNAME, BOT_NAME)
            await asyncio.sleep(2)
            print("✅ Name sent")
            print()

            # Send bot username
            print(f"📤 Sending bot username: {BOT_USERNAME}")
            await app.send_message(BOTFATHER_USERNAME, BOT_USERNAME)
            await asyncio.sleep(3)
            print("✅ Username sent")
            print()

            # Get recent messages from BotFather to find token
            print("🔍 Retrieving bot token from BotFather...")

            bot_token = None
            async for message in app.get_chat_history(BOTFATHER_USERNAME, limit=10):
                if message.text:
                    try:
                        bot_token = extract_bot_token(message.text)
                        break
                    except ValueError:
                        continue

            if not bot_token:
                raise RuntimeError(
                    "Bot token not found in BotFather response.\n"
                    f"Bot username '{BOT_USERNAME}' may already exist or be invalid.\n"
                    "Try a different username or check Telegram for errors."
                )

            print(f"✅ Bot token retrieved: {bot_token[:10]}...")
            print()

            # Store token in Doppler
            print("💾 Storing bot token in Doppler...")
            store_in_doppler("TELEGRAM_BOT_TOKEN", bot_token)

            # Get user's chat ID (for sending notifications to self)
            print("🔍 Getting your chat ID...")
            me = await app.get_me()
            my_chat_id = me.id
            print(f"✅ Your chat ID: {my_chat_id}")
            print()

            # Store chat ID in Doppler
            print("💾 Storing chat ID in Doppler...")
            store_in_doppler("TELEGRAM_CHAT_ID", str(my_chat_id))

            # Send test message to self
            print("📤 Sending test message to self...")
            await app.send_message("me", "✅ Bot creation complete! This is your chat ID for notifications.")
            await asyncio.sleep(1)
            print("✅ Test message sent")
            print()

            print("="*60)
            print("✅ Bot Creation Successful")
            print("="*60)
            print()
            print(f"Bot Name: {BOT_NAME}")
            print(f"Bot Username: @{BOT_USERNAME}")
            print(f"Bot Token: {bot_token[:10]}... (stored in Doppler)")
            print(f"Your Chat ID: {my_chat_id} (stored in Doppler)")
            print()
            print("Next steps:")
            print("  1. Setup ngrok tunnel (Phase 0, Step 5)")
            print("  2. Register webhook with Telegram")
            print()

        return 0

    except KeyboardInterrupt:
        print()
        print("❌ Bot creation cancelled by user")
        return 1

    except FloodWait as e:
        print()
        print("="*60)
        print("❌ Rate Limited by Telegram")
        print("="*60)
        print()
        print(f"Wait {e.value} seconds and try again")
        print()
        return 1

    except Exception as e:
        print()
        print("="*60)
        print("❌ Bot Creation Failed")
        print("="*60)
        print()
        print(f"Error: {e}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
