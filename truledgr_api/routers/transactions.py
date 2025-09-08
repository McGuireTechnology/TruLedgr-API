"""Transaction router with CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timezone

from ..database import get_db
from ..models.transaction import Transaction, TransactionCreate, TransactionRead, TransactionUpdate
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(tags=["Transactions"])


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction for the current user."""
    # Create new transaction
    db_transaction = Transaction(
        user_id=current_user.id,  # type: ignore
        account_id=transaction.account_id,
        category_id=transaction.category_id,
        category=transaction.category,
        amount=transaction.amount,
        description=transaction.description,
        payee_id=transaction.payee_id,
        transaction_date=transaction.transaction_date or datetime.now(timezone.utc),
        reference_number=transaction.reference_number,
        notes=transaction.notes
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.get("/", response_model=List[TransactionRead])
async def read_transactions(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all transactions for the current user."""
    statement = select(Transaction).where(Transaction.user_id == current_user.id).offset(skip).limit(limit)
    transactions = db.exec(statement).all()
    return transactions


@router.get("/{transaction_id}", response_model=TransactionRead)
async def read_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID."""
    statement = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    )
    transaction = db.exec(statement).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaction


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a transaction."""
    statement = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    )
    db_transaction = db.exec(statement).first()
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Update only provided fields
    transaction_data = transaction_update.model_dump(exclude_unset=True)
    for field, value in transaction_data.items():
        setattr(db_transaction, field, value)
    
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction."""
    statement = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    )
    transaction = db.exec(statement).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    db.delete(transaction)
    db.commit()
    
    return None
