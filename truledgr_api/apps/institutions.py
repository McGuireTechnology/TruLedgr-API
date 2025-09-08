"""Institutions subapp with all institution-related endpoints."""

from fastapi import FastAPI, Depends
from typing import Callable

from ..database import get_db
from ..routers.institutions import router as institutions_router
from .. import __version__


def create_institutions_app(db_dependency: Callable = get_db) -> FastAPI:
    """Create and configure the institutions subapp."""
    institutions_app = FastAPI(
        title="TruLedgr API - Institutions",
        description="Institution management endpoints for financial institutions with full CRUD operations.\n\n🏠 <a href='/' target='_self'>← Back to API Index</a>",
        version=__version__,
    )

    # Include institutions router
    institutions_app.include_router(institutions_router)

    return institutions_app
