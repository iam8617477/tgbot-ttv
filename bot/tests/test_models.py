import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from bot.models import TelegramUser, Tariff, Subscription, Rate, Payment, Refund
from indexer.models import Contract


@pytest.fixture()
def telegram_user(db):
    return TelegramUser.objects.create(
        telegram_id=123456789, username='test_user', first_name='Test', email='test@example.com'
    )


def test_telegram_user_creation(telegram_user):
    assert TelegramUser.objects.count() == 1
    assert telegram_user.telegram_id == 123456789
    assert telegram_user.username == 'test_user'


@pytest.fixture()
def tariff(db):
    tariff = Tariff.objects.create(name='STARTER', requests_per_day=100, amount=10.5)
    return tariff


def test_tariff_creation(tariff):
    assert Tariff.objects.count() == 1
    assert tariff.name == 'STARTER'
    assert tariff.requests_per_day == 100
    assert tariff.amount == 10.5


def test_subscription_creation(telegram_user, tariff):
    subscription = Subscription.objects.create(
        user=telegram_user, tariff=tariff, start_date=timezone.now(), end_date=timezone.now()
    )
    assert Subscription.objects.count() == 1
    assert subscription.user == telegram_user
    assert subscription.tariff == tariff


@pytest.fixture()
def contacts(db):
    contract_from = Contract.objects.create(address='from_contract', name='From Contract', decimals=18)
    contract_to = Contract.objects.create(address='to_contract', name='To Contract', decimals=18)
    return contract_from, contract_to


def test_rate_creation(contacts):
    contract_from, contract_to = contacts
    rate = Rate.objects.create(from_contract=contract_from, to_contract=contract_to, rate=1.23456789)
    assert Rate.objects.count() == 1
    assert rate.from_contract == contract_from
    assert rate.to_contract == contract_to
    assert rate.rate == 1.23456789


def test_refund_creation(db):
    refund = Refund.objects.create(
        amount=50.00, address='0x1234567890abcdef'
    )

    assert Refund.objects.count() == 1
    assert refund.amount == 50.00
    assert refund.address == '0x1234567890abcdef'
    assert refund.is_executed is False


def test_refund_amount_validation(db):
    with pytest.raises(ValueError, match='Refund amount must be positive'):
        Refund.objects.create(amount=-10.00, address='0xabcdef1234567890')


def test_payment_with_subscription(db, telegram_user, tariff):
    subscription = Subscription.objects.create(
        user=telegram_user, tariff=tariff, start_date='2024-01-01', end_date='2024-12-31'
    )

    payment = Payment.objects.create(
        user=telegram_user,
        related_model_type=ContentType.objects.get_for_model(Subscription),
        related_model_id=subscription.id,
        amount=100.50,
        type=Payment.Type.SUBSCRIPTION
    )

    assert Payment.objects.count() == 1
    assert payment.user == telegram_user
    assert payment.related_object == subscription
    assert payment.amount == 100.50
    assert payment.type == Payment.Type.SUBSCRIPTION


def test_payment_with_refund(db, telegram_user):
    refund = Refund.objects.create(
        amount=50.00, address='0x1234567890abcdef'
    )

    refund_payment = Payment.objects.create(
        user=telegram_user,
        related_model_type=ContentType.objects.get_for_model(Refund),
        related_model_id=refund.id,
        amount=-50.00,
        type=Payment.Type.REFUND
    )

    assert Payment.objects.count() == 1
    assert refund_payment.user == telegram_user
    assert refund_payment.related_object == refund
    assert refund_payment.amount == -50.00
    assert refund_payment.type == Payment.Type.REFUND
