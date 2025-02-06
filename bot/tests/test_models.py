from django.test import TestCase

import pytest
from django.utils import timezone

from bot.models import TelegramUser, Tariff, Subscription, Rate, Payment
from indexer.models import Contract


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture()
def telegram_user():
    return TelegramUser.objects.create(
        telegram_id=123456789, username='test_user', first_name='Test', email='test@example.com'
    )


def test_telegram_user_creation(telegram_user):
    assert TelegramUser.objects.count() == 1
    assert telegram_user.telegram_id == 123456789
    assert telegram_user.username == 'test_user'


def test_tariff_creation():
    tariff = Tariff.objects.create(name=Tariff.Name.STARTER, requests_per_day=100)
    assert Tariff.objects.count() == 1
    assert tariff.name == Tariff.Name.STARTER
    assert tariff.requests_per_day == 100


def test_subscription_creation(telegram_user):
    tariff = Tariff.objects.create(name=Tariff.Name.STARTER, requests_per_day=100)
    subscription = Subscription.objects.create(
        user=telegram_user, tariff=tariff, start_date=timezone.now(), end_date=timezone.now()
    )
    assert Subscription.objects.count() == 1
    assert subscription.user == telegram_user
    assert subscription.tariff == tariff


@pytest.fixture()
def contacts():
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


def test_payment_creation(telegram_user):
    tariff = Tariff.objects.create(name=Tariff.Name.STARTER, requests_per_day=100)
    payment = Payment.objects.create(
        user=telegram_user, tariff=tariff, amount=-100.50, transaction_id='payment_123'
    )
    assert Payment.objects.count() == 1
    assert payment.user == telegram_user
    assert payment.tariff == tariff
    assert payment.amount == -100.50
    assert payment.transaction_id == 'payment_123'
    assert payment.type == Payment.Type.SUBSCRIPTION
