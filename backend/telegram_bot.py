import os
import logging
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import httpx
import json
import datetime

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# FastAPI server URL
FASTAPI_URL = "http://localhost:18880"

# Telegram Bot Token (replace with your actual token)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "") # TODO: Replace with actual token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the command /start is issued."""
    await update.message.reply_text("Hi! I'm your PulseBoard Bot. How can I help you today?")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks the health of the FastAPI backend."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FASTAPI_URL}/health")
            response.raise_for_status()
            status_data = response.json()
            await update.message.reply_text(f"Backend Status: {status_data['status']} - Database: {status_data['database']}")
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(f"Error checking backend status: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        await update.message.reply_text(f"Error connecting to backend: {e}")

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Retrieves the latest dashboard data (signals, events, emails)."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FASTAPI_URL}/api/dashboard-data")
            response.raise_for_status()
            dashboard_data = response.json()

            message = "📊 *Latest PulseBoard Data* 📊\\n\\n"

            if dashboard_data.get("signals"):
                message += "*Signals:*\\n"
                for s in dashboard_data["signals"]:
                    message += f"- \\[{s['timestamp'].split('.')[0].replace('T', ' ')}\\] {s['type']} from {s['source']}\\n"
                message += "\\n"

            if dashboard_data.get("events"):
                message += "*Events:*\\n"
                for e in dashboard_data["events"]:
                    message += f"- \\[{e['timestamp'].split('.')[0].replace('T', ' ')}\\] {e['name']} \\({e.get('description', 'N/A')}\\) from {e['source']}\\n"
                message += "\\n"

            if dashboard_data.get("emails"):
                message += "*Emails:*\\n"
                for em in dashboard_data["emails"]:
                    message += f"- \\[{em['timestamp'].split('.')[0].replace('T', ' ')}\\] From: {em['sender']}, Subject: {em['subject']}\\n"
                message += "\\n"
            
            if not any([dashboard_data.get("signals"), dashboard_data.get("events"), dashboard_data.get("emails")]):
                message += "No data available yet."

            await update.message.reply_markdown_v2(message)

    except httpx.HTTPStatusError as e:
        await update.message.reply_text(f"Error fetching latest data: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        await update.message.reply_text(f"Error connecting to backend: {e}")
    except Exception as e:
        logger.error(f"Error in latest command: {e}")
        await update.message.reply_text(f"An unexpected error occurred: {e}")


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds a new signal to the PulseBoard. Usage: /add <type> <source> <data_json>"""
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /add <type> <source> <data_json>")
        return

    signal_type = args[0]
    source = args[1]
    data_str = " ".join(args[2:])

    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        await update.message.reply_text("Invalid JSON for data. Please provide valid JSON.")
        return

    signal_data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "type": signal_type,
        "source": source,
        "data": data
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{FASTAPI_URL}/api/signals", json=signal_data)
            response.raise_for_status()
            await update.message.reply_text(f"Signal added successfully: {response.json()['message']}")
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(f"Error adding signal: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        await update.message.reply_text(f"Error connecting to backend: {e}")
    except Exception as e:
        logger.error(f"Error in add command: {e}")
        await update.message.reply_text(f"An unexpected error occurred: {e}")

def main() -> None:
    """Starts the bot."""
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("TELEGRAM_BOT_TOKEN is not set. Please set the environment variable or replace the placeholder.")
        print("TELEGRAM_BOT_TOKEN is not set. Please set the environment variable or replace the placeholder.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("latest", latest))
    application.add_handler(CommandHandler("add", add))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
