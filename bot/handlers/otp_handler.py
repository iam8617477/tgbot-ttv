from telegram import Update
from telegram.ext import ContextTypes

from bot.services.cache_service import get_otp_from_cache


async def handle_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    otp = update.message.text.strip()

    cached_otp = await get_otp_from_cache(telegram_id)

    if cached_otp == otp:
        await update.message.reply_text('OTP verified successfully!')
    else:
        await update.message.reply_text('Invalid OTP. Please try again or request a new one.')
