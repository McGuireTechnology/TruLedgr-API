"""Account models and schemas."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from enum import Enum
import pycountry
from pydantic import field_validator

from . import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .transaction import Transaction
    from .institution import Institution
    from .payee import Payee


class AccountType(str, Enum):
    """Account type enumeration."""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    OTHER = "other"


class AccountStatus(str, Enum):
    """Account status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    PENDING = "pending"


class Account(BaseModel, table=True):
    """Account table."""

    __tablename__ = "accounts"

    user_id: str = Field(foreign_key="users.id", index=True)
    institution_id: Optional[str] = Field(default=None, foreign_key="institutions.id", index=True)
    account_type: AccountType = Field(default=AccountType.CHECKING)
    name: str = Field(max_length=255)
    account_number: Optional[str] = Field(default=None, max_length=100)
    routing_number: Optional[str] = Field(default=None, max_length=50)
    balance: float = Field(default=0.0)
    currency: str = Field(default="USD", max_length=3)
    status: AccountStatus = Field(default=AccountStatus.ACTIVE)
    description: Optional[str] = Field(default=None, max_length=500)
    is_primary: bool = Field(default=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="accounts")
    institution: Optional["Institution"] = Relationship(back_populates="accounts")
    transactions: List["Transaction"] = Relationship(back_populates="account")
    payees: List["Payee"] = Relationship(back_populates="account")


# Pydantic schemas
class AccountCreate(SQLModel):
    """Account creation schema."""
    institution_id: Optional[str] = None
    account_type: AccountType = AccountType.CHECKING
    name: str
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    balance: float = 0.0
    currency: str = "USD"
    description: Optional[str] = None
    is_primary: bool = False

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code using pycountry."""
        if not v:
            return v
        
        # Convert to uppercase for consistency
        v = v.upper()
        
        # Check if it's a valid currency code
        try:
            currency = pycountry.currencies.get(alpha_3=v)
            if currency is None:
                raise ValueError(f"Invalid currency code: {v}")
        except LookupError:
            raise ValueError(f"Invalid currency code: {v}")
        
        return v


class AccountRead(SQLModel):
    """Account read schema."""
    id: str
    user_id: str
    institution_id: Optional[str] = None
    account_type: AccountType
    name: str
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    balance: float
    currency: str
    status: AccountStatus
    description: Optional[str] = None
    is_primary: bool
    created_at: datetime
    updated_at: datetime


class AccountUpdate(SQLModel):
    """Account update schema."""
    institution_id: Optional[str] = None
    account_type: Optional[AccountType] = None
    name: Optional[str] = None
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    balance: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[AccountStatus] = None
    description: Optional[str] = None
    is_primary: Optional[bool] = None

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        """Validate currency code using pycountry."""
        if v is None:
            return v
        
        # Convert to uppercase for consistency
        v = v.upper()
        
        # Check if it's a valid currency code
        try:
            currency = pycountry.currencies.get(alpha_3=v)
            if currency is None:
                raise ValueError(f"Invalid currency code: {v}")
        except LookupError:
            raise ValueError(f"Invalid currency code: {v}")
        
        return v


class AccountTypeInfo(SQLModel):
    """Account type information."""
    type: AccountType
    name: str
    description: str