"""User model example."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from . import BaseModel
from .auth import UserSession, UserOAuthAccount

if TYPE_CHECKING:
    from .account import Account
    from .transaction import Transaction
    from .institution import Institution
    from .category import Category
    from .payee import Payee


class UserBase(SQLModel):
    """Base user fields."""
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)


class User(UserBase, BaseModel, table=True):
    """User table model."""
    
    __tablename__ = "users"
    
    hashed_password: str
    
    # Authentication relationships
    sessions: List[UserSession] = Relationship(back_populates="user")
    oauth_accounts: List[UserOAuthAccount] = Relationship(back_populates="user")
    
    # Domain relationships
    accounts: List["Account"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    institutions: List["Institution"] = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")
    payees: List["Payee"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(SQLModel):
    """User update schema."""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None


class UserRead(UserBase):
    """User read schema (public)."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
