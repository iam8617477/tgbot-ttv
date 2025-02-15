import pytest

from bot.models import TelegramUser
from indexer.models import Wallet, Contract, Block, Event


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture()
def telegram_user():
    return TelegramUser.objects.create(
        telegram_id=123456789, username='test_user', first_name='Test', email='test@example.com'
    )


def test_wallet_creation(telegram_user):
    wallet = Wallet.objects.create(user=telegram_user, address='test_wallet_address')
    assert Wallet.objects.count() == 1
    wallet.refresh_from_db()
    assert wallet.user == telegram_user
    assert wallet.address == 'test_wallet_address'


def test_contract_creation():
    contract = Contract.objects.create(address='test_contract_address', name='Test Contract', decimals=18)
    assert Contract.objects.count() == 1
    contract.refresh_from_db()
    assert contract.address == 'test_contract_address'
    assert contract.name == 'Test Contract'


def test_block_creation():
    contract = Contract.objects.create(address='test_contract_address', name='Test Contract', decimals=18)
    block = Block.objects.create(contract=contract, number=12345)
    assert Block.objects.count() == 1
    block.refresh_from_db()
    assert block.contract == contract
    assert block.number == 12345
    assert block.processed is False
    assert block.error_message is None


def test_event_creation(telegram_user):
    contract = Contract.objects.create(address='test_contract_address', name='Test Contract', decimals=18)
    wallet = Wallet.objects.create(user=telegram_user, address='test_wallet_address')
    block = Block.objects.create(contract=contract, number=12345)
    event = Event.objects.create(
        transaction_id='test_transaction_id', name=Event.Name.TRANSFER, value=1000,
        contract_address=contract, to_address=wallet, block=block, unconfirmed=False
    )
    event.refresh_from_db()
    assert Event.objects.count() == 1
    assert event.transaction_id == 'test_transaction_id'
    assert event.name == Event.Name.TRANSFER
    assert event.value == '1000'
