"""Authentication utilities and dependencies."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from ulid import ULID

from ..config import settings
from ..database import get_db
from ..models.user import User
from ..models.auth import UserSession, SessionStatus, ImpersonationSession


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Check if session is still active
    session_token = payload.get("session_token")
    if session_token:
        statement = select(UserSession).where(
            UserSession.session_token == session_token,
            UserSession.status == SessionStatus.ACTIVE
        )
        session = db.exec(statement).first()
        if not session or session.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
            raise credentials_exception
    
    # Get user
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    if user is None:
        raise credentials_exception
    
    return user


def create_user_session(db: Session, user_id: str, ip_address: Optional[str] = None, 
                       user_agent: Optional[str] = None) -> tuple[str, str]:
    """Create a new user session and return access and refresh tokens."""
    # Create session record
    session_token = str(ULID())
    refresh_token = str(ULID())
    
    session = UserSession(
        user_id=user_id,
        session_token=session_token,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),  # 1 hour
        last_activity=datetime.now(timezone.utc),
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user_id, "session_token": session_token},
        expires_delta=timedelta(minutes=15)
    )
    
    refresh_token_jwt = create_refresh_token(
        data={"sub": user_id, "session_token": session_token},
        expires_delta=timedelta(days=7)
    )
    
    return access_token, refresh_token_jwt


def revoke_user_session(db: Session, session_token: str):
    """Revoke a user session."""
    statement = select(UserSession).where(UserSession.session_token == session_token)
    session = db.exec(statement).first()
    if session:
        session.status = SessionStatus.REVOKED
        db.commit()


def get_active_sessions(db: Session, user_id: str) -> list[UserSession]:
    """Get all active sessions for a user."""
    statement = select(UserSession).where(
        UserSession.user_id == user_id,
        UserSession.status == SessionStatus.ACTIVE,
        UserSession.expires_at > datetime.now(timezone.utc).replace(tzinfo=None)
    )
    return list(db.exec(statement).all())


def get_admin_dependency(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure current user is an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def create_impersonation_session(
    db: Session, 
    admin_user_id: str, 
    target_user_id: str, 
    reason: Optional[str] = None
) -> tuple[str, str, str]:
    """Create an impersonation session and return tokens plus session ID."""
    # Verify target user exists and is active
    statement = select(User).where(User.id == target_user_id)
    target_user = db.exec(statement).first()
    if not target_user or not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found or inactive"
        )
    
    # Create impersonation session record
    session_token = str(ULID())
    
    impersonation_session = ImpersonationSession(
        admin_user_id=admin_user_id,
        target_user_id=target_user_id,
        session_token=session_token,
        reason=reason,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=2)  # 2 hour limit
    )
    
    db.add(impersonation_session)
    db.commit()
    db.refresh(impersonation_session)
    
    # Create tokens with impersonation context
    access_token = create_access_token(
        data={
            "sub": target_user_id, 
            "session_token": session_token,
            "impersonation": True,
            "admin_user_id": admin_user_id,
            "impersonation_session_id": impersonation_session.id
        },
        expires_delta=timedelta(minutes=15)
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": target_user_id, 
            "session_token": session_token,
            "impersonation": True,
            "admin_user_id": admin_user_id,
            "impersonation_session_id": impersonation_session.id
        },
        expires_delta=timedelta(hours=2)
    )
    
    return access_token, refresh_token, str(impersonation_session.id)


def end_impersonation_session(db: Session, session_id: str, admin_user_id: str):
    """End an impersonation session."""
    statement = select(ImpersonationSession).where(
        ImpersonationSession.id == session_id,
        ImpersonationSession.admin_user_id == admin_user_id,
        ImpersonationSession.status == SessionStatus.ACTIVE
    )
    session = db.exec(statement).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impersonation session not found"
        )
    
    session.ended_at = datetime.now(timezone.utc)
    session.status = SessionStatus.REVOKED
    db.commit()


def get_current_user_with_impersonation(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> tuple[User, Optional[dict]]:
    """Get current user and impersonation context if applicable."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Check if this is an impersonation session
    impersonation_context = None
    if payload.get("impersonation"):
        session_token = payload.get("session_token")
        impersonation_session_id = payload.get("impersonation_session_id")
        admin_user_id = payload.get("admin_user_id")
        
        if session_token and impersonation_session_id:
            # Verify impersonation session is still active
            statement = select(ImpersonationSession).where(
                ImpersonationSession.session_token == session_token,
                ImpersonationSession.status == SessionStatus.ACTIVE
            )
            imp_session = db.exec(statement).first()
            if not imp_session or imp_session.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Impersonation session expired"
                )
            
            impersonation_context = {
                "admin_user_id": admin_user_id,
                "impersonation_session_id": impersonation_session_id,
                "session_token": session_token,
                "reason": imp_session.reason
            }
    else:
        # Regular session validation
        session_token = payload.get("session_token")
        if session_token:
            statement = select(UserSession).where(
                UserSession.session_token == session_token,
                UserSession.status == SessionStatus.ACTIVE
            )
            session = db.exec(statement).first()
            if not session or session.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
                raise credentials_exception
    
    # Get user (target user in case of impersonation)
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    if user is None:
        raise credentials_exception
    
    return user, impersonation_context


def get_impersonation_sessions(db: Session, admin_user_id: str) -> list[ImpersonationSession]:
    """Get all impersonation sessions for an admin user."""
    statement = select(ImpersonationSession).where(
        ImpersonationSession.admin_user_id == admin_user_id
    )
    return list(db.exec(statement).all())
