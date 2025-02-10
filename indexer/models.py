from django.db import models

from core.models import TimestampedModel


class Wallet(TimestampedModel):
    user = models.ForeignKey('bot.TelegramUser', related_name='wallets', on_delete=models.CASCADE)
    address = models.CharField(max_length=255, unique=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]


class Contract(TimestampedModel):
    address = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    decimals = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Block(TimestampedModel):
    contract = models.ForeignKey(Contract, related_name='blocks', on_delete=models.CASCADE)
    block_id = models.BigIntegerField()

    class Meta:
        unique_together = ('contract', 'block_id')
        indexes = [
            models.Index(fields=['contract']),
        ]

    def __str__(self):
        return f'Block {self.block_id} for Contract {self.contract.address}'


class Event(TimestampedModel):
    class Name(models.TextChoices):
        TRANSFER = 'TRANSFER'

    transaction_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, choices=Name.choices, default=Name.TRANSFER)
    value = models.BigIntegerField()
    contract_address = models.ForeignKey(Contract, related_name='events', on_delete=models.CASCADE)
    to_address = models.ForeignKey(Wallet, related_name='events', on_delete=models.CASCADE)
    block = models.ForeignKey(Block, related_name='events', on_delete=models.CASCADE)
    unconfirmed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['contract_address']),
            models.Index(fields=['to_address']),
            models.Index(fields=['block']),
        ]

    def __str__(self):
        return f'Event {self.name} ({self.transaction_id}) in Block {self.block.block_id}'
