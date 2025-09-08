"""Payee router with CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from ..database import get_db
from ..models.payee import Payee, PayeeCreate, PayeeRead, PayeeUpdate
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(tags=["Payees"])


@router.post("/", response_model=PayeeRead, status_code=status.HTTP_201_CREATED)
async def create_payee(
    payee: PayeeCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payee for the current user."""
    # Validate account payee logic
    if payee.is_account_payee:
        if not payee.account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="account_id is required when is_account_payee is True"
            )
        # Verify the account belongs to the current user
        from ..models.account import Account
        account = db.exec(
            select(Account).where(
                Account.id == payee.account_id,
                Account.user_id == current_user.id
            )
        ).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or does not belong to user"
            )
    elif payee.account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="account_id should only be provided when is_account_payee is True"
        )
    
    # Create new payee
    db_payee = Payee(
        user_id=current_user.id,  # type: ignore
        name=payee.name,
        category=payee.category,
        website=payee.website,
        phone=payee.phone,
        address=payee.address,
        notes=payee.notes,
        is_account_payee=payee.is_account_payee,
        account_id=payee.account_id
    )
    
    db.add(db_payee)
    db.commit()
    db.refresh(db_payee)
    
    return db_payee


@router.get("/", response_model=List[PayeeRead])
async def read_payees(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payees for the current user."""
    statement = select(Payee).where(Payee.user_id == current_user.id).offset(skip).limit(limit)
    payees = db.exec(statement).all()
    return payees


@router.get("/{payee_id}", response_model=PayeeRead)
async def read_payee(
    payee_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific payee by ID."""
    statement = select(Payee).where(
        Payee.id == payee_id,
        Payee.user_id == current_user.id
    )
    payee = db.exec(statement).first()
    
    if not payee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payee not found"
        )
    
    return payee


@router.put("/{payee_id}", response_model=PayeeRead)
async def update_payee(
    payee_id: str,
    payee_update: PayeeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific payee."""
    statement = select(Payee).where(
        Payee.id == payee_id,
        Payee.user_id == current_user.id
    )
    db_payee = db.exec(statement).first()
    
    if not db_payee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payee not found"
        )
    
    # Validate account payee logic
    update_data = payee_update.model_dump(exclude_unset=True)
    if 'is_account_payee' in update_data or 'account_id' in update_data:
        is_account_payee = update_data.get('is_account_payee', db_payee.is_account_payee)
        account_id = update_data.get('account_id', db_payee.account_id)
        
        if is_account_payee:
            if not account_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="account_id is required when is_account_payee is True"
                )
            # Verify the account belongs to the current user
            from ..models.account import Account
            account = db.exec(
                select(Account).where(
                    Account.id == account_id,
                    Account.user_id == current_user.id
                )
            ).first()
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found or does not belong to user"
                )
        elif account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="account_id should only be provided when is_account_payee is True"
            )
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_payee, field, value)
    
    db.add(db_payee)
    db.commit()
    db.refresh(db_payee)
    
    return db_payee


@router.delete("/{payee_id}")
async def delete_payee(
    payee_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific payee."""
    statement = select(Payee).where(
        Payee.id == payee_id,
        Payee.user_id == current_user.id
    )
    db_payee = db.exec(statement).first()
    
    if not db_payee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payee not found"
        )
    
    db.delete(db_payee)
    db.commit()
    
    return {"message": "Payee deleted successfully"}
