from bot.models import TelegramUser
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist


@sync_to_async
def get_or_create_telegram_user(telegram_id, first_name, username):
    return TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'first_name': first_name, 'username': username},
    )


@sync_to_async
def get_telegram_user_by_id(telegram_id):
    return TelegramUser.objects.get(telegram_id=telegram_id)


@sync_to_async
def create_telegram_user(telegram_id, first_name, username):
    return TelegramUser.objects.create(
        telegram_id=telegram_id,
        first_name=first_name,
        username=username
    )


@sync_to_async
def exists_telegram_user_by_email(email):
    return TelegramUser.objects.filter(email=email).exists()


@sync_to_async
def save_telegram_user(telegram_user):
    telegram_user.save()
