"""Account router with CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from ..database import get_db
from ..models.account import Account, AccountCreate, AccountRead, AccountUpdate
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(tags=["Accounts"])


@router.post("/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new account for the current user."""
    # Create new account
    db_account = Account(
        user_id=current_user.id,  # type: ignore
        institution_id=account.institution_id,
        name=account.name,
        account_type=account.account_type,
        account_number=account.account_number,
        routing_number=account.routing_number,
        balance=account.balance,
        currency=account.currency,
        description=account.description,
        is_primary=account.is_primary
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account


@router.get("/", response_model=List[AccountRead])
async def read_accounts(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all accounts for the current user."""
    statement = select(Account).where(Account.user_id == current_user.id).offset(skip).limit(limit)
    accounts = db.exec(statement).all()
    return accounts


@router.get("/{account_id}", response_model=AccountRead)
async def read_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific account by ID."""
    statement = select(Account).where(
        Account.id == account_id,
        Account.user_id == current_user.id
    )
    account = db.exec(statement).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account


@router.put("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: str,
    account_update: AccountUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an account."""
    statement = select(Account).where(
        Account.id == account_id,
        Account.user_id == current_user.id
    )
    db_account = db.exec(statement).first()
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Update only provided fields
    account_data = account_update.model_dump(exclude_unset=True)
    for field, value in account_data.items():
        setattr(db_account, field, value)
    
    db.commit()
    db.refresh(db_account)
    
    return db_account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an account."""
    statement = select(Account).where(
        Account.id == account_id,
        Account.user_id == current_user.id
    )
    account = db.exec(statement).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    db.delete(account)
    db.commit()
    
    return None
