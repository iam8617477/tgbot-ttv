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
    class Name(models.TextChoices):
        FREE_TRIAL = 'FREE_TRIAL'
        STARTER = 'STARTER'
        BASIC = 'BASIC'

    name = models.CharField(max_length=50, choices=Name.choices, default=Name.FREE_TRIAL)
    requests_per_day = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Subscription(TimestampedModel):
    user = models.ForeignKey(TelegramUser, related_name='subscriptions', on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, related_name='subscriptions', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reset_tariff = models.BooleanField(default=False)


class Rate(TimestampedModel):
    from_contract = models.ForeignKey('indexer.Contract', related_name='rates_from', on_delete=models.CASCADE)
    to_contract = models.ForeignKey('indexer.Contract', related_name='rates_to', on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=20, decimal_places=10)

    class Meta:
        unique_together = ('from_contract', 'to_contract')

    def __str__(self):
        return f"1 {self.from_contract.name} = {self.rate} {self.to_contract.name}"


class Payment(TimestampedModel):
    user = models.ForeignKey(TelegramUser, related_name='payments', on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    transaction_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'Payment of {self.amount} for user {self.user.telegram_id} (Tariff: {self.tariff.name})'
