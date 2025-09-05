"""Authentication subapp with login, logout, and session management endpoints."""

from fastapi import FastAPI, Depends
from typing import Callable

from ..database import get_db
from ..routers.auth import router as auth_router
from .. import __version__


def create_auth_app(db_dependency: Callable = get_db) -> FastAPI:
    """Create and configure the authentication subapp."""
    auth_app = FastAPI(
        title="TruLedgr API - Authentication",
        description="Authentication endpoints for login, logout, session management, and OAuth.\n\n🏠 <a href='/' target='_self'>← Back to API Index</a>",
        version=__version__,
    )

    # Include auth router
    auth_app.include_router(auth_router)

    return auth_app
