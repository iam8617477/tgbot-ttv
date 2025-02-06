from django.contrib import admin

from core.admin import DefaultAdmin
from .models import (
    Wallet,
    Contract,
    Block,
    Event,
)


@admin.register(Wallet)
class WalletAdmin(DefaultAdmin):
    pass


@admin.register(Contract)
class ContractAdmin(DefaultAdmin):
    pass


@admin.register(Block)
class BlockAdmin(DefaultAdmin):
    pass


@admin.register(Event)
class EventAdmin(DefaultAdmin):
    pass
