import os
import sys

import django
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from django.conf import settings
from asgiref.sync import sync_to_async

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

from bot.models import TelegramUser


@sync_to_async
def get_or_create_telegram_user(telegram_id, first_name, username):
    return TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'first_name': first_name, 'username': username},
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username or 'Not set'

    user, created = await get_or_create_telegram_user(telegram_id, first_name, username)

    if created:
        logger.info(f'New user registered: {first_name} (ID: {telegram_id})')
        await update.message.reply_text(
            f'Welcome, {first_name}! You are now registered. Your username is: '
            f"{username if username != 'Not set' else 'not set'}."
        )
    else:
        logger.info(f'User {first_name} (ID: {telegram_id}) has restarted the bot.')
        await update.message.reply_text(f'Welcome back, {first_name}!')

if __name__ == '__main__':
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))

    logger.info('Bot started and ready to work...')
    app.run_polling()

