"""Main application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from ..config import settings
from ..routers import health
from .. import __version__
from .users import create_users_app
from .auth import create_auth_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup - migrations should be run separately with `alembic upgrade head`
    yield
    # Shutdown (if needed)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name, 
        description="A comprehensive ledger management system.\n\n🏠 <a href='/' target='_self'>← Back to API Index</a>",
        version=__version__,
        lifespan=lifespan,
    )

    @app.get("/", response_class=HTMLResponse)
    async def root():
        """API landing page with links to all available apps and documentation."""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TruLedgr API</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                .app-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }}
                .app-card {{
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    background: #ffffff;
                    transition: transform 0.2s, box-shadow 0.2s;
                }}
                .app-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .app-title {{
                    color: #2c3e50;
                    margin: 0 0 10px 0;
                    font-size: 1.3em;
                }}
                .app-description {{
                    color: #7f8c8d;
                    margin-bottom: 15px;
                }}
                .links {{
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                }}
                .link {{
                    text-decoration: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: 500;
                    transition: background-color 0.2s;
                    font-size: 0.9em;
                }}
                .link-docs {{
                    background-color: #3498db;
                    color: white;
                }}
                .link-docs:hover {{
                    background-color: #2980b9;
                }}
                .link-redoc {{
                    background-color: #e74c3c;
                    color: white;
                }}
                .link-redoc:hover {{
                    background-color: #c0392b;
                }}
                .link-openapi {{
                    background-color: #95a5a6;
                    color: white;
                }}
                .link-openapi:hover {{
                    background-color: #7f8c8d;
                }}
                .link-signup {{
                    background-color: #27ae60;
                    color: white;
                }}
                .link-signup:hover {{
                    background-color: #229954;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    color: #7f8c8d;
                }}
                .status {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 0.8em;
                    font-weight: 500;
                    background-color: #27ae60;
                    color: white;
                    margin-left: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏦 TruLedgr API</h1>
                
                <div class="app-grid">
                    <!-- Main API -->
                    <div class="app-card">
                        <h2 class="app-title">Main API <span class="status">Active</span></h2>
                        <p class="app-description">Core application with health checks and system monitoring.</p>
                        <div class="links">
                            <a href="/docs" class="link link-docs">📖 Swagger UI</a>
                            <a href="/redoc" class="link link-redoc">📋 ReDoc</a>
                            <a href="/openapi.json" class="link link-openapi">🔧 OpenAPI Schema</a>
                        </div>
                    </div>

                    <!-- Users API -->
                    <div class="app-card">
                        <h2 class="app-title">Users API <span class="status">Active</span></h2>
                        <p class="app-description">Complete user management system with CRUD operations, authentication, and user profiles.</p>
                        <div class="links">
                            <a href="/users/docs" class="link link-docs">📖 Swagger UI</a>
                            <a href="/users/redoc" class="link link-redoc">📋 ReDoc</a>
                            <a href="/users/openapi.json" class="link link-openapi">🔧 OpenAPI Schema</a>
                        </div>
                    </div>

                    <!-- Auth API -->
                    <div class="app-card">
                        <h2 class="app-title">Authentication API <span class="status">Active</span></h2>
                        <p class="app-description">JWT-based authentication with login/logout, session monitoring, and OAuth2 provider support.</p>
                        <div class="links">
                            <a href="/auth/docs" class="link link-docs">📖 Swagger UI</a>
                            <a href="/auth/redoc" class="link link-redoc">📋 ReDoc</a>
                            <a href="/auth/openapi.json" class="link link-openapi">🔧 OpenAPI Schema</a>
                        </div>
                    </div>
                </div>

                <div class="footer">
                    <p>Built with FastAPI • Version {__version__} • <a href="https://fastapi.tiangolo.com/">Learn more about FastAPI</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content

    @app.get("/health")
    async def ping():
        return {"status": "ok", "message": "pong"}
    
    # Include health router
    app.include_router(health.router)
    
    # Mount users subapp
    users_app = create_users_app()
    app.mount("/users", users_app)
    
    # Mount auth subapp
    auth_app = create_auth_app()
    app.mount("/auth", auth_app)

    return app
