from django.contrib import admin

from core.admin import DefaultAdmin
from .models import (
    TelegramUser,
    Tariff,
    Subscription,
    Rate,
    Payment
)


@admin.register(TelegramUser)
class TelegramUserAdmin(DefaultAdmin):
    pass


@admin.register(Tariff)
class TariffAdmin(DefaultAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(DefaultAdmin):
    pass


@admin.register(Rate)
class RateAdmin(DefaultAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(DefaultAdmin):
    pass
