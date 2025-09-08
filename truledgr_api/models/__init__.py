"""Base models and common model utilities."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from ulid import ULID


def generate_ulid() -> str:
    """Generate a new ULID as a string."""
    return str(ULID())


class TimestampMixin(SQLModel):
    """Mixin to add created_at and updated_at timestamps."""
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseModel(TimestampMixin):
    """Base model with common fields."""
    id: Optional[str] = Field(default_factory=generate_ulid, primary_key=True)


# Import all models to ensure they're registered with SQLModel
from .user import User
from .auth import (
    UserSession, 
    UserOAuthAccount, 
    OAuthProvider, 
    SessionStatus,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    SessionInfo,
    OAuthAccountInfo,
    UserAuthInfo,
    RevokeSessionRequest
)
from .account import (
    Account,
    AccountType,
    AccountStatus,
    AccountCreate,
    AccountRead,
    AccountUpdate,
    AccountTypeInfo
)
from .transaction import (
    Transaction,
    TransactionStatus,
    TransactionCategory,
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
    TransactionTypeInfo,
    TransactionCategoryInfo
)
from .institution import (
    Institution,
    InstitutionType,
    InstitutionStatus,
    InstitutionCreate,
    InstitutionRead,
    InstitutionUpdate,
    InstitutionTypeInfo
)
from .category import (
    Category,
    CategoryType,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CategoryTypeInfo
)
from .payee import (
    Payee,
    PayeeCreate,
    PayeeRead,
    PayeeUpdate
)

# Export models for easy importing
__all__ = [
    "BaseModel", 
    "TimestampMixin", 
    "User",
    "UserSession",
    "UserOAuthAccount", 
    "OAuthProvider",
    "SessionStatus",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest", 
    "SessionInfo",
    "OAuthAccountInfo",
    "UserAuthInfo",
    "RevokeSessionRequest",
    "Account",
    "AccountType",
    "AccountStatus",
    "AccountCreate",
    "AccountRead",
    "AccountUpdate",
    "AccountTypeInfo",
    "Transaction",
    "TransactionStatus",
    "TransactionCategory",
    "TransactionCreate",
    "TransactionRead",
    "TransactionUpdate",
    "TransactionTypeInfo",
    "TransactionCategoryInfo",
    "Institution",
    "InstitutionType",
    "InstitutionStatus",
    "InstitutionCreate",
    "InstitutionRead",
    "InstitutionUpdate",
    "InstitutionTypeInfo",
    "Category",
    "CategoryType",
    "CategoryCreate",
    "CategoryRead",
    "CategoryUpdate",
    "CategoryTypeInfo",
    "Payee",
    "PayeeCreate",
    "PayeeRead",
    "PayeeUpdate"
]
