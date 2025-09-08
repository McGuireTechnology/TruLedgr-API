# Enhanced Session Design (Alternative)

## Option 1: Add Session Type Enum (if we wanted to merge)
```python
class SessionType(str, Enum):
    REGULAR = "regular"
    IMPERSONATION = "impersonation"
    
class Session(BaseModel, table=True):
    session_type: SessionType
    user_id: str  # For regular sessions
    admin_user_id: Optional[str] = None  # For impersonation
    target_user_id: Optional[str] = None  # For impersonation
    reason: Optional[str] = None  # For impersonation
    # ... other fields
```

## Option 2: Keep Separate but Add Relationships (Current + Enhancement)
```python
class UserSession(BaseModel, table=True):
    # Current fields...
    
    # Optional: Link to impersonation if this session was created via impersonation
    impersonation_session_id: Optional[str] = Field(foreign_key="impersonation_sessions.id")

class ImpersonationSession(BaseModel, table=True):
    # Current fields...
    
    # Track any regular sessions created during impersonation
    created_sessions: List[UserSession] = Relationship()
```

## Option 3: Current Design (Recommended)
Keep them completely separate for:
- Clear separation of concerns
- Better security and audit compliance  
- Simpler queries and maintenance
- Different data retention policies
