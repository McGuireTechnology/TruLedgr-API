"""Transaction models and schemas."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from enum import Enum
from ulid import ULID
from decimal import Decimal

from . import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .account import Account
    from .category import Category, CategoryType
    from .payee import Payee


class TransactionStatus(str, Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    CLEARED = "cleared"
    RECONCILED = "reconciled"
    CANCELLED = "cancelled"


class TransactionCategory(str, Enum):
    """Legacy transaction category enumeration - kept for backward compatibility."""
    FOOD_AND_DRINK = "food_and_drink"
    TRANSPORTATION = "transportation"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    BILLS_AND_UTILITIES = "bills_and_utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    TRAVEL = "travel"
    PERSONAL_CARE = "personal_care"
    HOME_IMPROVEMENT = "home_improvement"
    GIFTS_AND_DONATIONS = "gifts_and_donations"
    INVESTMENTS = "investments"
    INCOME = "income"
    TRANSFER = "transfer"
    OTHER = "other"


class Transaction(BaseModel, table=True):
    """Transaction table."""

    __tablename__ = "transactions"

    user_id: str = Field(foreign_key="users.id", index=True)
    account_id: str = Field(foreign_key="accounts.id", index=True)
    category_id: str = Field(foreign_key="categories.id", index=True)
    payee_id: Optional[str] = Field(default=None, foreign_key="payees.id", index=True)
    amount: Decimal = Field(max_digits=15, decimal_places=2)
    description: str = Field(max_length=500)
    category: TransactionCategory = Field(default=TransactionCategory.OTHER)
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    transaction_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reference_number: Optional[str] = Field(default=None, max_length=100, unique=True)
    notes: Optional[str] = Field(default=None, max_length=1000)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="transactions")
    account: Optional["Account"] = Relationship(back_populates="transactions")
    category_rel: Optional["Category"] = Relationship(back_populates="transactions")
    payee: Optional["Payee"] = Relationship(back_populates="transactions")


# Pydantic schemas
class TransactionCreate(SQLModel):
    """Transaction creation schema."""
    account_id: str
    category_id: str
    payee_id: Optional[str] = None
    amount: Decimal
    description: str
    category: TransactionCategory = TransactionCategory.OTHER
    transaction_date: Optional[datetime] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class TransactionRead(SQLModel):
    """Transaction read schema."""
    id: str
    user_id: str
    account_id: str
    category_id: str
    payee_id: Optional[str] = None
    amount: Decimal
    description: str
    category: TransactionCategory
    status: TransactionStatus
    transaction_date: datetime
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TransactionUpdate(SQLModel):
    """Transaction update schema."""
    category_id: Optional[str] = None
    payee_id: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    category: Optional[TransactionCategory] = None
    status: Optional[TransactionStatus] = None
    transaction_date: Optional[datetime] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class TransactionTypeInfo(SQLModel):
    """Transaction type information - now uses CategoryType."""
    type: "CategoryType"
    name: str
    description: str


class TransactionCategoryInfo(SQLModel):
    """Transaction category information."""
    category: TransactionCategory
    name: str
    description: str