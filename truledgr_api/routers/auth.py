"""Authentication endpoints for login, logout, and session management."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timezone

from ..database import get_db
from ..utils.auth import (
    get_current_user, 
    create_user_session, 
    revoke_user_session,
    get_active_sessions,
    verify_password,
    get_admin_dependency,
    create_impersonation_session,
    end_impersonation_session,
    get_current_user_with_impersonation,
    get_impersonation_sessions
)
from ..models.user import User
from ..models.auth import (
    LoginRequest, 
    TokenResponse, 
    RefreshTokenRequest,
    SessionInfo,
    OAuthAccountInfo,
    UserAuthInfo,
    RevokeSessionRequest,
    UserSession,
    UserOAuthAccount,
    SessionStatus,
    ImpersonateRequest,
    ImpersonateResponse,
    EndImpersonationRequest,
    ImpersonationInfo,
    ImpersonationSession
)


router = APIRouter()

@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
async def login(
    request: LoginRequest, 
    req: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and create session."""
    # Find user
    statement = select(User).where(User.username == request.username)
    user = db.exec(statement).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID is missing"
        )
    
    # Create session
    access_token, refresh_token = create_user_session(
        db=db,
        user_id=user.id,
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent")
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=900,  # 15 minutes
        user_id=user.id
    )



@router.post("/refresh", response_model=TokenResponse, tags=["Authentication"])
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    # Verify refresh token and get user
    from ..utils.auth import verify_token
    payload = verify_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    session_token = payload.get("session_token")
    
    if not user_id or not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if session is still active
    statement = select(UserSession).where(
        UserSession.session_token == session_token,
        UserSession.status == SessionStatus.ACTIVE
    )
    session = db.exec(statement).first()
    
    if not session or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Create new access token
    from ..utils.auth import create_access_token
    access_token = create_access_token(
        data={"sub": user_id, "session_token": session_token}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Return same refresh token
        token_type="bearer",
        expires_in=900,
        user_id=user_id
    )


@router.delete("/logout", tags=["Authentication"])
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user and revoke current session."""
    # In a real implementation, you'd extract session_token from JWT
    # and revoke that specific session
    return {"message": "Successfully logged out"}



@router.get("/me", response_model=UserAuthInfo, tags=["User Profile"])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information including sessions and OAuth accounts."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID is missing"
        )
    
    # Get active sessions
    sessions = get_active_sessions(db, current_user.id)
    session_infos = []
    for session in sessions:
        if (session.id and session.created_at and session.expires_at and 
            session.last_activity):
            session_infos.append(SessionInfo(
                id=session.id,
                user_id=session.user_id,
                status=session.status,
                created_at=session.created_at,
                expires_at=session.expires_at,
                last_activity=session.last_activity,
                ip_address=session.ip_address,
                user_agent=session.user_agent
            ))
    
    # Get OAuth accounts
    statement = select(UserOAuthAccount).where(UserOAuthAccount.user_id == current_user.id)
    oauth_accounts = db.exec(statement).all()
    oauth_infos = []
    for account in oauth_accounts:
        if account.id and account.created_at:
            oauth_infos.append(OAuthAccountInfo(
                id=account.id,
                provider=account.provider,
                provider_email=account.provider_email,
                created_at=account.created_at,
                token_expires_at=account.token_expires_at
            ))
    
    return UserAuthInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        sessions=session_infos,
        oauth_accounts=oauth_infos
    )


@router.get("/sessions", response_model=List[SessionInfo], tags=["Sessions"])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active sessions for current user."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID is missing"
        )
    
    sessions = get_active_sessions(db, current_user.id)
    session_infos = []
    for session in sessions:
        if (session.id and session.created_at and session.expires_at and 
            session.last_activity):
            session_infos.append(SessionInfo(
                id=session.id,
                user_id=session.user_id,
                status=session.status,
                created_at=session.created_at,
                expires_at=session.expires_at,
                last_activity=session.last_activity,
                ip_address=session.ip_address,
                user_agent=session.user_agent
            ))
    return session_infos


@router.delete("/sessions/{session_id}", tags=["Sessions"])
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session."""
    statement = select(UserSession).where(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    )
    session = db.exec(statement).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.status = SessionStatus.REVOKED
    db.commit()
    
    return {"message": "Session revoked successfully"}


@router.delete("/sessions", tags=["Sessions"])
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke all sessions for current user."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID is missing"
        )
    
    sessions = get_active_sessions(db, current_user.id)
    
    for session in sessions:
        session.status = SessionStatus.REVOKED
    
    db.commit()
    
    return {"message": f"Revoked {len(sessions)} sessions"}


# Impersonation endpoints
@router.post("/impersonations", response_model=ImpersonateResponse, tags=["Admin"])
async def start_impersonation(
    request: ImpersonateRequest,
    req: Request,
    admin_user: User = Depends(get_admin_dependency),
    db: Session = Depends(get_db)
):
    """Start impersonating another user (admin only)."""
    if not admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin user ID is missing"
        )
    
    # Prevent self-impersonation
    if admin_user.id == request.target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot impersonate yourself"
        )
    
    access_token, refresh_token, session_id = create_impersonation_session(
        db=db,
        admin_user_id=admin_user.id,
        target_user_id=request.target_user_id,
        reason=request.reason
    )
    
    return ImpersonateResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=900,  # 15 minutes
        target_user_id=request.target_user_id,
        admin_user_id=admin_user.id,
        impersonation_session_id=session_id
    )


@router.delete("/impersonations", tags=["Admin"])
async def end_impersonation(
    request: EndImpersonationRequest,
    admin_user: User = Depends(get_admin_dependency),
    db: Session = Depends(get_db)
):
    """End an impersonation session (admin only)."""
    if not admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin user ID is missing"
        )
    
    # If no session ID provided, try to get it from current token
    session_id = request.impersonation_session_id
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impersonation session ID required"
        )
    
    end_impersonation_session(db, session_id, admin_user.id)
    
    return {"message": "Impersonation session ended successfully"}


@router.get("/impersonations", response_model=List[ImpersonationInfo], tags=["Admin"])
async def list_impersonation_sessions(
    admin_user: User = Depends(get_admin_dependency),
    db: Session = Depends(get_db)
):
    """List all impersonation sessions for current admin."""
    if not admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin user ID is missing"
        )
    
    sessions = get_impersonation_sessions(db, admin_user.id)
    
    result = []
    for session in sessions:
        if not session.id:
            continue
            
        # Get admin and target user info
        admin_stmt = select(User).where(User.id == session.admin_user_id)
        admin = db.exec(admin_stmt).first()
        
        target_stmt = select(User).where(User.id == session.target_user_id)
        target = db.exec(target_stmt).first()
        
        if admin and target and session.created_at:
            result.append(ImpersonationInfo(
                id=session.id,
                admin_user_id=session.admin_user_id,
                admin_username=admin.username,
                target_user_id=session.target_user_id,
                target_username=target.username,
                reason=session.reason,
                created_at=session.created_at,
                expires_at=session.expires_at,
                ended_at=session.ended_at,
                status=session.status
            ))
    
    return result


@router.get("/whoami", response_model=dict, tags=["Authentication"])
async def whoami(
    user_and_context: tuple[User, Optional[dict]] = Depends(get_current_user_with_impersonation),
    db: Session = Depends(get_db)
):
    """Get current user info including impersonation status."""
    user, impersonation_context = user_and_context
    
    result = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_impersonating": impersonation_context is not None
    }
    
    if impersonation_context:
        # Get admin user info
        admin_stmt = select(User).where(User.id == impersonation_context["admin_user_id"])
        admin_user = db.exec(admin_stmt).first()
        
        result["impersonation"] = {
            "admin_user_id": impersonation_context["admin_user_id"],
            "admin_username": admin_user.username if admin_user else "Unknown",
            "session_id": impersonation_context["impersonation_session_id"],
            "reason": impersonation_context.get("reason")
        }
    
    return result
