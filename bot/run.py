import os
import sys
import logging

import django
from django.conf import settings
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from handlers.start_handler import start
from handlers.email_handler import email_handler
from handlers.otp_handler import handle_otp


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, email_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_otp))

    logger.info('Bot started and ready to work...')
    app.run_polling()
