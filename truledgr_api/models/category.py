"""Category models and schemas for transactions and budgeting."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from enum import Enum
from ulid import ULID

from . import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .transaction import Transaction


class CategoryType(str, Enum):
    """Category type enumeration (formerly TransactionType)."""
    DEBIT = "debit"
    CREDIT = "credit"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"
    DIVIDEND = "dividend"
    ADJUSTMENT = "adjustment"
    INCOME = "income"
    OTHER = "other"


class Category(BaseModel, table=True):
    """Category table for transactions and budgeting."""

    __tablename__ = "categories"

    user_id: str = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    category_type: CategoryType = Field(default=CategoryType.OTHER)
    description: Optional[str] = Field(default=None, max_length=500)
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color code
    icon: Optional[str] = Field(default=None, max_length=50)
    parent_id: Optional[str] = Field(default=None, foreign_key="categories.id", index=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category_rel")
    subcategories: List["Category"] = Relationship(back_populates="parent")
    parent: Optional["Category"] = Relationship(
        back_populates="subcategories",
        sa_relationship_kwargs={"remote_side": "Category.id"}
    )


# Pydantic schemas
class CategoryCreate(SQLModel):
    """Category creation schema."""
    name: str
    category_type: CategoryType = CategoryType.OTHER
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[str] = None


class CategoryRead(SQLModel):
    """Category read schema."""
    id: str
    user_id: str
    name: str
    category_type: CategoryType
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CategoryUpdate(SQLModel):
    """Category update schema."""
    name: Optional[str] = None
    category_type: Optional[CategoryType] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[str] = None


class CategoryTypeInfo(SQLModel):
    """Category type information."""
    type: CategoryType
    name: str
    description: str
