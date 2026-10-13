import pytest
from app.account_service import AccountService
from app.exceptions import AccountNotFound, InsufficientBalance, InvalidAmount


@pytest.fixture
def service():
	return AccountService()


def test_deposit_creates_account_and_accumulates_balance(service):
	assert service.deposit("400", 100) == 100
	assert service.deposit("400", 25) == 125
	assert service.get_balance("400") == 125


@pytest.mark.parametrize("amount", [0, -1])
def test_deposit_rejects_non_positive_amount_without_creating_account(service, amount):
	with pytest.raises(InvalidAmount):
		service.deposit("400", amount)

	assert service.get_balance("400") is None


def test_withdraw_returns_remaining_balance(service):
	service.deposit("400", 100)

	assert service.withdraw("400", 40) == 60
	assert service.get_balance("400") == 60


def test_withdraw_rejects_unknown_account(service):
	with pytest.raises(AccountNotFound):
		service.withdraw("500", 10)


def test_withdraw_rejects_insufficient_balance_without_mutating_account(service):
	service.deposit("400", 50)

	with pytest.raises(InsufficientBalance):
		service.withdraw("400", 51)

	assert service.get_balance("400") == 50


@pytest.mark.parametrize("amount", [0, -1])
def test_withdraw_rejects_non_positive_amount_without_mutating_account(service, amount):
	service.deposit("400", 50)

	with pytest.raises(InvalidAmount):
		service.withdraw("400", amount)

	assert service.get_balance("400") == 50


def test_transfer_creates_destination_and_updates_both_balances(service):
	service.deposit("400", 100)

	assert service.transfer("400", "300", 35) == (65, 35)
	assert service.get_balance("400") == 65
	assert service.get_balance("300") == 35


def test_transfer_rejects_unknown_origin_without_creating_destination(service):
	with pytest.raises(AccountNotFound):
		service.transfer("500", "300", 10)

	assert service.get_balance("300") is None


def test_transfer_rejects_insufficient_balance_without_mutating_accounts(service):
	service.deposit("400", 50)

	with pytest.raises(InsufficientBalance):
		service.transfer("400", "300", 51)

	assert service.get_balance("400") == 50
	assert service.get_balance("300") is None


@pytest.mark.parametrize("amount", [0, -1])
def test_transfer_rejects_non_positive_amount_without_mutating_accounts(service, amount):
	service.deposit("400", 50)

	with pytest.raises(InvalidAmount):
		service.transfer("400", "300", amount)

	assert service.get_balance("400") == 50
	assert service.get_balance("300") is None


def test_reset_clears_all_accounts(service):
	service.deposit("400", 100)
	service.deposit("300", 200)

	service.reset()

	assert service.get_balance("400") is None
	assert service.get_balance("300") is None
