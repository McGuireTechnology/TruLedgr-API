"""Transactions subapp with all transaction-related endpoints."""

from fastapi import FastAPI, Depends
from typing import Callable

from ..database import get_db
from ..routers.transactions import router as transactions_router
from .. import __version__


def create_transactions_app(db_dependency: Callable = get_db) -> FastAPI:
    """Create and configure the transactions subapp."""
    transactions_app = FastAPI(
        title="TruLedgr API - Transactions",
        description="Transaction management endpoints for financial transactions with full CRUD operations.\n\n🏠 <a href='/' target='_self'>← Back to API Index</a>",
        version=__version__,
    )

    # Include transactions router
    transactions_app.include_router(transactions_router)

    return transactions_app
