"""Categories subapp with all category-related endpoints."""

from fastapi import FastAPI, Depends
from typing import Callable

from ..database import get_db
from ..routers.categories import router as categories_router
from .. import __version__


def create_categories_app(db_dependency: Callable = get_db) -> FastAPI:
    """Create and configure the categories subapp."""
    categories_app = FastAPI(
        title="TruLedgr API - Categories",
        description="Category management endpoints for transaction categorization and budgeting.\n\n🏠 <a href='/' target='_self'>← Back to API Index</a>",
        version=__version__,
    )

    # Include categories router
    categories_app.include_router(categories_router)

    return categories_app
