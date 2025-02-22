from telegram import Update
from telegram.ext import ContextTypes

from bot.forms import EmailForm
from bot.handlers.menu_handler import show_main_menu
from bot.services.db_queries import get_telegram_user_by_id, save_telegram_user, exists_telegram_user_by_email
from bot.services.email_service import send_email_verification


async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    email = update.message.text.strip()

    form = EmailForm({'email': email})
    if not form.is_valid():
        await update.message.reply_text(form.errors['email'][0])
        return

    if await exists_telegram_user_by_email(email):
        await update.message.reply_text('This email is already registered.')

    user = await get_telegram_user_by_id(telegram_id)
    user.email = email
    await save_telegram_user(user)

    await update.message.reply_text(f'Thank you! Your email {user.email} has been saved.')
    await send_email_verification(user.email)
    await show_main_menu(update, context)
