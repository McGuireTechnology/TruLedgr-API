"""Category router with CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from ..database import get_db
from ..models.category import Category, CategoryCreate, CategoryRead, CategoryUpdate
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(tags=["Categories"])


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new category for the current user."""
    # Create new category
    db_category = Category(
        user_id=current_user.id,  # type: ignore
        name=category.name,
        category_type=category.category_type,
        description=category.description,
        color=category.color,
        icon=category.icon,
        parent_id=category.parent_id
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.get("/", response_model=List[CategoryRead])
async def read_categories(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all categories for the current user."""
    statement = select(Category).where(Category.user_id == current_user.id).offset(skip).limit(limit)
    categories = db.exec(statement).all()
    return categories


@router.get("/{category_id}", response_model=CategoryRead)
async def read_category(
    category_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific category by ID."""
    statement = select(Category).where(Category.id == category_id, Category.user_id == current_user.id)
    category = db.exec(statement).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: str,
    category_update: CategoryUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a category."""
    statement = select(Category).where(
        Category.id == category_id,
        Category.user_id == current_user.id
    )
    db_category = db.exec(statement).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Update only provided fields
    category_data = category_update.model_dump(exclude_unset=True)
    for field, value in category_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a category."""
    statement = select(Category).where(
        Category.id == category_id,
        Category.user_id == current_user.id
    )
    category = db.exec(statement).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    db.delete(category)
    db.commit()
    
    return None
