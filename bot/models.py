from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import TimestampedModel


class TelegramUser(TimestampedModel):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    @property
    def balance(self):
        return 0


class Tariff(TimestampedModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    requests_per_day = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return self.name


class Subscription(TimestampedModel):
    user = models.ForeignKey(TelegramUser, related_name='subscriptions', on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, related_name='subscriptions', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reset_tariff = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['tariff']),
        ]


class Refund(TimestampedModel):
    address = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=20, decimal_places=10, default=0.00)
    is_executed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.amount < 0:
            raise ValueError('Refund amount must be positive')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Refund with amount {self.amount}'


class Payment(models.Model):
    class Type(models.TextChoices):
        SUBSCRIPTION = 'SUBSCRIPTION'
        REFUND = 'REFUND'

    user = models.ForeignKey('TelegramUser', related_name='payments', on_delete=models.CASCADE)
    related_model_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    related_model_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('related_model_type', 'related_model_id')
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    type = models.CharField(max_length=20, choices=Type.choices)
    is_executed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['related_model_type']),
        ]

    def __str__(self):
        return f'Payment of {self.amount} for {self.user} ({self.type})'


class Rate(TimestampedModel):
    from_contract = models.ForeignKey('indexer.Contract', related_name='rates_from', on_delete=models.CASCADE)
    to_contract = models.ForeignKey('indexer.Contract', related_name='rates_to', on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=20, decimal_places=10)

    class Meta:
        unique_together = ('from_contract', 'to_contract')
        indexes = [
            models.Index(fields=['from_contract']),
            models.Index(fields=['to_contract']),
        ]

    def __str__(self):
        return f"1 {self.from_contract.name} = {self.rate} {self.to_contract.name}"