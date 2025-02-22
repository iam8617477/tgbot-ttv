from asgiref.sync import sync_to_async

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.email_handler import email_handler
from bot.handlers.menu_handler import show_main_menu
from bot.services.db_queries import get_or_create_telegram_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username or 'Not set'

    user, created = await get_or_create_telegram_user(telegram_id, first_name, username)

    if created:
        await update.message.reply_text(
            f'Welcome, {first_name}! Please enter your email address to complete the registration.'
        )
        return 'WAITING_FOR_EMAIL', email_handler
    else:
        if not user.email:
            await update.message.reply_text('Welcome back! Please enter your email address:')
            return 'WAITING_FOR_EMAIL', email_handler
        await update.message.reply_text(f'Welcome back, {first_name}!')
        await show_main_menu(update, context)

