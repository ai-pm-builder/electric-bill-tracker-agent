"""
One-time utility to discover your Telegram numeric chat_id.

Usage:
  1. Open Telegram and send any message to your bot (e.g. "hello")
  2. Run this script: python get_chat_id.py
  3. Copy the numeric chat_id and update your .env and GitHub Secret
"""

import os
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in .env")
        return

    print("Fetching recent updates from your Telegram bot...\n")

    try:
        resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
        data = resp.json()

        if not data.get("ok"):
            print(f"ERROR: Telegram API returned an error: {data}")
            return

        results = data.get("result", [])
        if not results:
            print("No recent messages found!")
            print("Please send a message to your bot in Telegram first, then re-run this script.")
            return

        # Collect unique chat IDs from all updates
        chats_found = {}
        for update in results:
            msg = update.get("message", {})
            chat = msg.get("chat", {})
            chat_id = chat.get("id")
            if chat_id and chat_id not in chats_found:
                first_name = chat.get("first_name", "")
                username = chat.get("username", "")
                chats_found[chat_id] = f"{first_name} (@{username})" if username else first_name

        if not chats_found:
            print("Could not extract chat_id from updates. Try sending a new message to the bot.")
            return

        print("=" * 50)
        print("CHAT ID(s) FOUND:")
        print("=" * 50)
        for cid, name in chats_found.items():
            print(f"  Chat ID: {cid}  ({name})")
        print("=" * 50)
        print()
        print("Next steps:")
        print("  1. Update your .env file:  TELEGRAM_CHAT_ID=<numeric_id>")
        print("  2. Update your GitHub Secret: TELEGRAM_CHAT_ID = <numeric_id>")
        print("     (Settings -> Secrets and variables -> Actions)")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
