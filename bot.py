"""
Harvest Telegram Bot — Your personal AI Chief of Staff as a phone contact.
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import config
from harvest import chat

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("harvest.bot")


def is_authorized(user_id: int) -> bool:
    """Only Manny can talk to Harvest."""
    if not config.ALLOWED_USER_IDS:
        return True  # No restriction if not configured
    return user_id in config.ALLOWED_USER_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    await update.message.reply_text(
        "Good morning. I'm Harvest, your Chief of Staff.\n\n"
        "Ask me anything about your businesses, deals, finances, or projects.\n\n"
        "Try: 'What should I focus on today?'"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    user_message = update.message.text
    user_id = str(update.effective_user.id)

    log.info(f"[{update.effective_user.first_name}] {user_message[:100]}")

    # Show typing indicator
    await update.message.chat.send_action("typing")

    try:
        response = await chat(user_message, user_id)

        # Telegram has a 4096 char limit per message
        if len(response) > 4000:
            # Split into chunks
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        log.error(f"Error handling message: {e}")
        await update.message.reply_text(
            "I hit an error processing that. Let me try again — rephrase your question?"
        )


def run_bot():
    """Start the Telegram bot."""
    if not config.TELEGRAM_TOKEN:
        log.error("TELEGRAM_TOKEN not set")
        return

    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log.info("Harvest bot starting...")
    app.run_polling(drop_pending_updates=True)
