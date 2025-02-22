from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['Enter OTP', 'Change Email']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)
