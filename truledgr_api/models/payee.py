"""Payee models and schemas."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone

from . import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .account import Account
    from .transaction import Transaction


class Payee(BaseModel, table=True):
    """Payee table for transaction payees/merchants and account transfers."""

    __tablename__ = "payees"

    user_id: str = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=255)
    category: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Account payee support
    is_account_payee: bool = Field(default=False)
    account_id: Optional[str] = Field(default=None, foreign_key="accounts.id", index=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="payees")
    account: Optional["Account"] = Relationship(back_populates="payees")
    transactions: List["Transaction"] = Relationship(back_populates="payee")


# Pydantic schemas
class PayeeCreate(SQLModel):
    """Payee creation schema."""
    name: str
    category: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_account_payee: bool = False
    account_id: Optional[str] = None


class PayeeRead(SQLModel):
    """Payee read schema."""
    id: str
    user_id: str
    name: str
    category: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_account_payee: bool
    account_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PayeeUpdate(SQLModel):
    """Payee update schema."""
    name: Optional[str] = None
    category: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_account_payee: Optional[bool] = None
    account_id: Optional[str] = None
