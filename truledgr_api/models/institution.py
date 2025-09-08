"""Institution models and schemas."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from enum import Enum
from ulid import ULID

from . import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .account import Account


class InstitutionType(str, Enum):
    """Institution type enumeration."""
    BANK = "bank"
    CREDIT_UNION = "credit_union"
    INVESTMENT_FIRM = "investment_firm"
    INSURANCE = "insurance"
    OTHER = "other"


class InstitutionStatus(str, Enum):
    """Institution status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Institution(BaseModel, table=True):
    """Institution table."""

    __tablename__ = "institutions"

    user_id: str = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=255)
    institution_type: InstitutionType = Field(default=InstitutionType.BANK)
    status: InstitutionStatus = Field(default=InstitutionStatus.ACTIVE)
    website: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=50)
    zip_code: Optional[str] = Field(default=None, max_length=20)
    country: str = Field(default="US", max_length=2)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="institutions")
    accounts: List["Account"] = Relationship(back_populates="institution")


# Pydantic schemas
class InstitutionCreate(SQLModel):
    """Institution creation schema."""
    name: str
    institution_type: InstitutionType = InstitutionType.BANK
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "US"
    description: Optional[str] = None


class InstitutionRead(SQLModel):
    """Institution read schema."""
    id: str
    user_id: str
    name: str
    institution_type: InstitutionType
    status: InstitutionStatus
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class InstitutionUpdate(SQLModel):
    """Institution update schema."""
    name: Optional[str] = None
    institution_type: Optional[InstitutionType] = None
    status: Optional[InstitutionStatus] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None


class InstitutionTypeInfo(SQLModel):
    """Institution type information."""
    type: InstitutionType
    name: str
    description: str