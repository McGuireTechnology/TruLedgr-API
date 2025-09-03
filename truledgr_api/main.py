from fastapi import FastAPI
from .config import settings
from .routers import health




def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.include_router(health.router)

    return app


app = create_app()
