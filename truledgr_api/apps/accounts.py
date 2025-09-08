"""Accounts subapp with all account-related endpoints."""

from fastapi import FastAPI, Depends
from typing import Callable

from ..database import get_db
from ..routers.accounts import router as accounts_router
from .. import __version__


def create_accounts_app(db_dependency: Callable = get_db) -> FastAPI:
    """Create and configure the accounts subapp."""
    accounts_app = FastAPI(
        title="TruLedgr API - Accounts",
        description="Account management endpoints for financial accounts with full CRUD operations.\n\n🏠 <a href='/' target='_self'>← Back to API Index</a>",
        version=__version__,
    )

    # Include accounts router
    accounts_app.include_router(accounts_router)

    return accounts_app
