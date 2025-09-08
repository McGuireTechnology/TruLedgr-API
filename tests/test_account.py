"""Test account models and currency validation."""

import pytest
from pydantic import ValidationError

from truledgr_api.models.account import AccountCreate, AccountUpdate, AccountType


def test_valid_currency_codes():
    """Test that valid currency codes are accepted."""
    # Test USD
    account = AccountCreate(
        name="Test Account",
        currency="USD"
    )
    assert account.currency == "USD"
    
    # Test EUR
    account = AccountCreate(
        name="Test Account",
        currency="eur"  # Should be converted to uppercase
    )
    assert account.currency == "EUR"
    
    # Test GBP
    account = AccountCreate(
        name="Test Account",
        currency="GBP"
    )
    assert account.currency == "GBP"
    
    # Test JPY
    account = AccountCreate(
        name="Test Account",
        currency="jpy"  # Should be converted to uppercase
    )
    assert account.currency == "JPY"


def test_invalid_currency_codes():
    """Test that invalid currency codes are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(
            name="Test Account",
            currency="INVALID"
        )
    assert "Invalid currency code" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(
            name="Test Account",
            currency="US"  # Too short
        )
    assert "Invalid currency code" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(
            name="Test Account",
            currency="USDD"  # Too long
        )
    assert "Invalid currency code" in str(exc_info.value)


def test_account_update_currency_validation():
    """Test currency validation in AccountUpdate."""
    # Valid currency
    update = AccountUpdate(currency="CAD")
    assert update.currency == "CAD"
    
    # Invalid currency
    with pytest.raises(ValidationError) as exc_info:
        AccountUpdate(currency="FAKE")
    assert "Invalid currency code" in str(exc_info.value)
    
    # None should be allowed
    update = AccountUpdate(currency=None)
    assert update.currency is None


def test_account_creation_defaults():
    """Test default values in account creation."""
    account = AccountCreate(name="Test Account")
    assert account.currency == "USD"
    assert account.account_type == AccountType.CHECKING
    assert account.balance == 0.0
    assert account.is_primary is False
