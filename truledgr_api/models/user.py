"""User model example."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from . import BaseModel
from .auth import UserSession, UserOAuthAccount


class UserBase(SQLModel):
    """Base user fields."""
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)


class User(UserBase, BaseModel, table=True):
    """User table model."""
    
    hashed_password: str
    
    # Authentication relationships
    sessions: List[UserSession] = Relationship(back_populates="user")
    oauth_accounts: List[UserOAuthAccount] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(SQLModel):
    """User update schema."""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserRead(UserBase):
    """User read schema (public)."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
