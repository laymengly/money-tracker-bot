"""
CLI Helper to set, inspect, or delete Telegram Bot Webhook for Firebase deployment.
Usage:
    python set_webhook.py --url https://<your-project>.web.app
    python set_webhook.py --info
    python set_webhook.py --delete
"""

import sys
import asyncio
import argparse
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, logger
import os

TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")


async def manage_webhook(url: str = None, info: bool = False, delete: bool = False):
    if not TELEGRAM_BOT_TOKEN or "ABCdef" in TELEGRAM_BOT_TOKEN:
        print("❌ Error: Valid TELEGRAM_BOT_TOKEN is not set in .env or environment variables.")
        sys.exit(1)

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.initialize()

    if delete:
        print("⏳ Deleting Telegram webhook...")
        success = await bot.delete_webhook(drop_pending_updates=False)
        if success:
            print("✅ Webhook successfully deleted. You can now use local polling (python bot.py).")
        else:
            print("❌ Failed to delete webhook.")
        await bot.shutdown()
        return

    if info:
        print("🔍 Fetching Telegram webhook status...")
        wb_info = await bot.get_webhook_info()
        print("--------------------------------------------------")
        print(f" Webhook URL:            {wb_info.url or '(None - Polling Mode)'}")
        print(f" Has Custom Cert:        {wb_info.has_custom_certificate}")
        print(f" Pending Update Count:   {wb_info.pending_update_count}")
        print(f" Max Connections:        {wb_info.max_connections}")
        print(f" Last Error Date:        {wb_info.last_error_date}")
        print(f" Last Error Message:     {wb_info.last_error_message or 'None'}")
        print("--------------------------------------------------")
        await bot.shutdown()
        return

    if url:
        # Standardize URL
        target_url = url.strip().rstrip("/")
        if not target_url.endswith("/api/telegram-webhook"):
            target_url += "/api/telegram-webhook"

        print(f"🚀 Registering Telegram webhook: {target_url}")
        kwargs = {"url": target_url, "drop_pending_updates": True}
        if TELEGRAM_WEBHOOK_SECRET:
            kwargs["secret_token"] = TELEGRAM_WEBHOOK_SECRET
            print("🔒 Using secret token authentication.")

        success = await bot.set_webhook(**kwargs)
        if success:
            print("✅ Webhook registered successfully!")
            print(f"👉 Bot updates will now be delivered to: {target_url}")
        else:
            print("❌ Failed to set webhook.")
        await bot.shutdown()
        return

    print("ℹ️ No action specified. Use --url <URL>, --info, or --delete. Run with --help for details.")
    await bot.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Manage Telegram Bot Webhook for Firebase / Cloud deployment.")
    parser.add_argument("--url", help="Your Firebase Hosting or Cloud Functions URL (e.g., https://my-app.web.app)")
    parser.add_argument("--info", action="store_true", help="Display current webhook status and diagnostics")
    parser.add_argument("--delete", action="store_true", help="Delete the current webhook to switch back to polling")

    args = parser.parse_args()
    asyncio.run(manage_webhook(url=args.url, info=args.info, delete=args.delete))


if __name__ == "__main__":
    main()

