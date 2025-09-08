"""Payees subapp with all payee-related endpoints."""

from fastapi import FastAPI, Depends
from typing import Callable

from ..database import get_db
from ..routers.payees import router as payees_router
from .. import __version__


def create_payees_app(db_dependency: Callable = get_db) -> FastAPI:
    """Create and configure the payees subapp."""
    payees_app = FastAPI(
        title="TruLedgr API - Payees",
        description="Payee management endpoints for transaction payees/merchants.\n\n🏠 <a href='/' target='_self'>← Back to API Index</a>",
        version=__version__,
    )

    # Include payees router
    payees_app.include_router(payees_router)

    return payees_app
