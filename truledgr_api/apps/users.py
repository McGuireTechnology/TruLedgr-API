"""Users subapp with all user-related endpoints."""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Callable

from ..database import get_db
from ..models.user import User, UserCreate, UserRead, UserUpdate
from ..utils.auth import get_current_user
from .. import __version__


def create_users_app(db_dependency: Callable = get_db) -> FastAPI:
    """Create and configure the users subapp."""
    users_app = FastAPI(
        title="TruLedgr API - Users",
        description="User management endpoints with full CRUD operations and public signup.\n\n🏠 <a href='/' target='_self'>← Back to API Index</a>",
        version=__version__,
    )

    @users_app.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["User Profile"])
    async def signup(user: UserCreate, db: Session = Depends(db_dependency)):
        """User signup endpoint for public registration."""
        # Check if user already exists
        statement = select(User).where(User.username == user.username)
        existing_user = db.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        statement = select(User).where(User.email == user.email)
        existing_email = db.exec(statement).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user (in real app, hash the password)
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.password,  # In real app: hash_password(user.password)
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user

    @users_app.get("/me", response_model=UserRead, tags=["User Profile"])
    async def get_current_user_profile(current_user: User = Depends(get_current_user)):
        """Get current authenticated user's profile."""
        return current_user

    @users_app.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["User Management"])
    async def create_user(
        user: UserCreate, 
        current_user: User = Depends(get_current_user),
        db: Session = Depends(db_dependency)
    ):
        """Create a new user (admin endpoint)."""
        # Check if user already exists
        statement = select(User).where(User.username == user.username)
        existing_user = db.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        statement = select(User).where(User.email == user.email)
        existing_email = db.exec(statement).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user (in real app, hash the password)
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.password,  # In real app: hash_password(user.password)
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user

    @users_app.get("/", response_model=List[UserRead], tags=["User Management"])
    async def read_users(
        skip: int = 0, 
        limit: int = 100, 
        current_user: User = Depends(get_current_user),
        db: Session = Depends(db_dependency)
    ):
        """Get all users."""
        statement = select(User).offset(skip).limit(limit)
        users = db.exec(statement).all()
        return users

    @users_app.get("/{user_id}", response_model=UserRead, tags=["User Management"])
    async def read_user(
        user_id: str, 
        current_user: User = Depends(get_current_user),
        db: Session = Depends(db_dependency)
    ):
        """Get a specific user by ID."""
        statement = select(User).where(User.id == user_id)
        user = db.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @users_app.put("/{user_id}", response_model=UserRead, tags=["User Management"])
    async def update_user(
        user_id: str, 
        user_update: UserUpdate, 
        current_user: User = Depends(get_current_user),
        db: Session = Depends(db_dependency)
    ):
        """Update a user."""
        statement = select(User).where(User.id == user_id)
        db_user = db.exec(statement).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update only provided fields
        user_data = user_update.model_dump(exclude_unset=True)
        if "password" in user_data:
            # In real app: user_data["hashed_password"] = hash_password(user_data.pop("password"))
            user_data["hashed_password"] = user_data.pop("password")
        
        for field, value in user_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        
        return db_user

    @users_app.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["User Management"])
    async def delete_user(
        user_id: str, 
        current_user: User = Depends(get_current_user),
        db: Session = Depends(db_dependency)
    ):
        """Delete a user."""
        statement = select(User).where(User.id == user_id)
        user = db.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(user)
        db.commit()
        
        return None

    return users_app
