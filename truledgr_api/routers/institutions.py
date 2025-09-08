"""Institution router with CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from ..database import get_db
from ..models.institution import Institution, InstitutionCreate, InstitutionRead, InstitutionUpdate
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(tags=["Institutions"])


@router.post("/", response_model=InstitutionRead, status_code=status.HTTP_201_CREATED)
async def create_institution(
    institution: InstitutionCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new institution for the current user."""
    # Create new institution
    db_institution = Institution(
        user_id=current_user.id,  # type: ignore
        name=institution.name,
        institution_type=institution.institution_type,
        website=institution.website,
        phone=institution.phone,
        address=institution.address,
        city=institution.city,
        state=institution.state,
        zip_code=institution.zip_code,
        country=institution.country,
        description=institution.description
    )
    
    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)
    
    return db_institution


@router.get("/", response_model=List[InstitutionRead])
async def read_institutions(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all institutions for the current user."""
    statement = select(Institution).where(Institution.user_id == current_user.id).offset(skip).limit(limit)
    institutions = db.exec(statement).all()
    return institutions


@router.get("/{institution_id}", response_model=InstitutionRead)
async def read_institution(
    institution_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific institution by ID."""
    statement = select(Institution).where(Institution.id == institution_id, Institution.user_id == current_user.id)
    institution = db.exec(statement).first()
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )
    return institution


@router.put("/{institution_id}", response_model=InstitutionRead)
async def update_institution(
    institution_id: str,
    institution_update: InstitutionUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an institution."""
    statement = select(Institution).where(
        Institution.id == institution_id,
        Institution.user_id == current_user.id
    )
    db_institution = db.exec(statement).first()
    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )
    
    # Update only provided fields
    institution_data = institution_update.model_dump(exclude_unset=True)
    for field, value in institution_data.items():
        setattr(db_institution, field, value)
    
    db.commit()
    db.refresh(db_institution)
    
    return db_institution


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_institution(
    institution_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an institution."""
    statement = select(Institution).where(
        Institution.id == institution_id,
        Institution.user_id == current_user.id
    )
    institution = db.exec(statement).first()
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )
    
    db.delete(institution)
    db.commit()
    
    return None
