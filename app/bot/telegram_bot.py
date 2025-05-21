from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_BLACK_LIST, TELEGRAM_WHITE_LIST

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

import re

from app.controller.main_controller import MainController


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text

    user_id = update.message.from_user.id
    user_full_name = update.message.from_user.full_name

    print(f"[{user_full_name}] 📩 Received message: {message_text} - user_id: {user_id}")

    if user_id in TELEGRAM_BLACK_LIST:
        await update.message.reply_text("🚫 You are not allowed to use this bot.")
        return

    if len(TELEGRAM_WHITE_LIST) > 0 and user_id not in TELEGRAM_WHITE_LIST:
        await update.message.reply_text("🚫 You are not allowed to use this bot.")
        return

    urls = re.findall(r'(https?://\S+)', message_text)

    if urls:
        for url in urls:
            controller = MainController(url, context, update)
            await controller.run()


class TelegramBot(object):

    def __init__(self):
        self.telegram_token = TELEGRAM_BOT_TOKEN

        self.bot = ApplicationBuilder().token(self.telegram_token).build()

        self.bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    def run(self):
        self.bot.run_polling()
