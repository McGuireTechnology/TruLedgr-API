"""Authentication models and schemas."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from ulid import ULID

from . import BaseModel

if TYPE_CHECKING:
    from .user import User


class OAuthProvider(str, Enum):
    """Supported OAuth2 providers."""
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    APPLE = "apple"


class SessionStatus(str, Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class UserSession(BaseModel, table=True):
    """User session tracking table."""
    
    user_id: str = Field(foreign_key="users.id", index=True)
    session_token: str = Field(unique=True, index=True)
    refresh_token: Optional[str] = Field(default=None, unique=True, index=True)
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    expires_at: datetime
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Relationship
    user: Optional["User"] = Relationship(back_populates="sessions")


class UserOAuthAccount(BaseModel, table=True):
    """OAuth2 account linking table."""
    
    user_id: str = Field(foreign_key="users.id", index=True)
    provider: OAuthProvider
    provider_user_id: str
    provider_email: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    account_data: Optional[str] = None  # JSON string for additional provider data
    
    # Relationship
    user: Optional["User"] = Relationship(back_populates="oauth_accounts")


# Update User model to include relationships
# This will be imported and used in the user model
class UserAuthMixin(SQLModel):
    """Mixin to add auth relationships to User model."""
    sessions: List[UserSession] = Relationship(back_populates="user")
    oauth_accounts: List[UserOAuthAccount] = Relationship(back_populates="user")


# Authentication schemas
class LoginRequest(SQLModel):
    """Login request schema."""
    username: str
    password: str


class TokenResponse(SQLModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str


class RefreshTokenRequest(SQLModel):
    """Refresh token request schema."""
    refresh_token: str


class SessionInfo(SQLModel):
    """Session information for monitoring."""
    id: str
    user_id: str
    status: SessionStatus
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]


class OAuthAccountInfo(SQLModel):
    """OAuth account information."""
    id: str
    provider: OAuthProvider
    provider_email: Optional[str]
    created_at: datetime
    token_expires_at: Optional[datetime]


class UserAuthInfo(SQLModel):
    """User authentication information."""
    id: str
    username: str
    email: str
    sessions: List[SessionInfo]
    oauth_accounts: List[OAuthAccountInfo]


class RevokeSessionRequest(SQLModel):
    """Request to revoke a specific session."""
    session_id: str
