from django.contrib import admin

from bot.models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'username', 'first_name', 'email', 'is_verified', 'is_active')
