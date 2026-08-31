"""
Telegram Session Generator Script
Run this script once interactively in terminal to generate a persistent StringSession.
The output string can be safely placed into the TELEGRAM_SESSION environment variable.
Never commit the session string to git.
"""
import asyncio
import os
import sys

# Ensure Telethon can be imported
try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
except ImportError:
    print("Error: Telethon is not installed. Please run: pip install telethon")
    sys.exit(1)


async def main():
    print("=" * 70)
    print("TELEGRAM USER SESSION GENERATOR (MTProto StringSession)")
    print("=" * 70)
    print("This utility securely authenticates your personal Telegram account once")
    print("and produces an encrypted base64 session string for TELEGRAM_SESSION.")
    print("This allows monitoring private channels you are a member of.")
    print("=" * 70)

    api_id = os.getenv("TELEGRAM_API_ID")
    if not api_id:
        val = input("Enter your TELEGRAM_API_ID (from my.telegram.org): ").strip()
        api_id = int(val) if val else None

    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not api_hash:
        api_hash = input("Enter your TELEGRAM_API_HASH (from my.telegram.org): ").strip()

    if not api_id or not api_hash:
        print("Error: TELEGRAM_API_ID and TELEGRAM_API_HASH are mandatory.")
        return

    print("\nConnecting to Telegram MTProto...")
    async with TelegramClient(StringSession(), int(api_id), api_hash) as client:
        session_str = client.session.save()
        me = await client.get_me()
        print("\n" + "=" * 70)
        print(f"SUCCESSFULLY AUTHENTICATED AS: {me.first_name} (@{me.username}) [ID: {me.id}]")
        print("=" * 70)
        print("\nCopy the session string below and save it as TELEGRAM_SESSION in your .env file:")
        print("-" * 70)
        print(session_str)
        print("-" * 70)
        print("\nDO NOT SHARE OR COMMIT THIS STRING TO SOURCE CONTROL.\n")


if __name__ == "__main__":
    asyncio.run(main())
