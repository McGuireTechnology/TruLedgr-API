"""Main application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.utils import get_openapi
import json
import importlib
import os
from pathlib import Path

from ..config import settings
from ..routers import health
from .. import __version__


def discover_sub_apps():
    """Dynamically discover all sub-app modules and their create functions."""
    sub_apps = {}
    
    # Get the directory containing this module
    apps_dir = Path(__file__).parent
    
    # Iterate through all Python files in the apps directory
    for file_path in apps_dir.glob("*.py"):
        if file_path.name in ["__init__.py", "main.py"]:
            continue
            
        module_name = file_path.stem
        full_module_name = f"truledgr_api.apps.{module_name}"
        
        try:
            # Import the module
            module = importlib.import_module(full_module_name)
            
            # Look for create function
            create_func_name = f"create_{module_name}_app"
            if hasattr(module, create_func_name):
                create_func = getattr(module, create_func_name)
                mount_path = f"/{module_name}"
                sub_apps[module_name] = (create_func, mount_path)
                
        except Exception as e:
            print(f"Warning: Failed to import {module_name} module: {e}")
            continue
    
    return sub_apps


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
        # Dynamic sub-app configuration for landing page
        sub_app_config = {
            "users": {"emoji": "👥", "description": "Complete user management system with secure authentication and comprehensive user profiles."},
            "auth": {"emoji": "🔐", "description": "Secure JWT-based authentication with session monitoring and OAuth2 provider integration."},
            "accounts": {"emoji": "💳", "description": "Financial account management with support for checking, savings, credit cards, and investment accounts."},
            "transactions": {"emoji": "💸", "description": "Transaction tracking and management with categorization, merchant information, and reconciliation support."},
            "institutions": {"emoji": "🏛️", "description": "Financial institution management for banks, credit unions, and investment firms with contact information."},
            "categories": {"emoji": "📂", "description": "Category management for transaction categorization and budgeting with hierarchical organization."},
            "payees": {"emoji": "🏪", "description": "Payee management for transaction payees and merchants with contact information and categorization."},
        }
        
        # Generate API cards dynamically
        api_cards_html = ""
        
        # Add main API card first
        api_cards_html += """
                    <!-- Main API -->
                    <div class="app-card">
                        <h2 class="app-title">Main API <span class="status">⚙️</span></h2>
                        <p class="app-description">Core application with health checks and system monitoring for reliable API operations.</p>
                        <div class="links">
                            <a href="/docs" class="link link-docs">📖 Swagger UI</a>
                            <a href="/redoc" class="link link-redoc">📋 ReDoc</a>
                        </div>
                    </div>
        """
        
        # Generate cards for each sub-app dynamically
        for app_name, config in sub_app_config.items():
            api_cards_html += f"""
                    <!-- {app_name.title()} API -->
                    <div class="app-card">
                        <h2 class="app-title">{app_name.title()} API <span class="status">{config['emoji']}</span></h2>
                        <p class="app-description">{config['description']}</p>
                        <div class="links">
                            <a href="/{app_name}/docs" class="link link-docs">📖 Swagger UI</a>
                            <a href="/{app_name}/redoc" class="link link-redoc">📋 ReDoc</a>
                        </div>
                    </div>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TruLedgr API</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --brand-deep-blue: #1E2A38;
                    --brand-teal: #00B8A9;
                    --brand-warm-gray: #F4F5F7;
                    --brand-orange: #FF6F3C;
                    --brand-lime: #8BC34A;
                    --brand-yellow: #FFC107;
                    --text-primary: #1E2A38;
                    --text-secondary: #666666;
                    --border-color: #E5E7EB;
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background-color: var(--brand-warm-gray);
                    color: var(--text-primary);
                    line-height: 1.6;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }}
                
                h1 {{
                    font-family: 'Montserrat', sans-serif;
                    font-weight: 700;
                    font-size: 2.5rem;
                    color: var(--brand-deep-blue);
                    text-align: center;
                    margin-bottom: 20px;
                    letter-spacing: -0.02em;
                }}
                
                .subtitle {{
                    font-family: 'Inter', sans-serif;
                    font-weight: 400;
                    font-size: 1.125rem;
                    color: var(--text-secondary);
                    text-align: center;
                    margin-bottom: 40px;
                    max-width: 600px;
                    margin-left: auto;
                    margin-right: auto;
                }}
                
                .app-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 24px;
                    margin-bottom: 60px;
                }}
                
                .app-card {{
                    background: white;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
                    border: 1px solid var(--border-color);
                    transition: all 0.2s ease;
                }}
                
                .app-card:hover {{
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06);
                    transform: translateY(-2px);
                }}
                
                .app-title {{
                    font-family: 'Montserrat', sans-serif;
                    font-weight: 600;
                    font-size: 1.25rem;
                    color: var(--brand-deep-blue);
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }}
                
                .app-description {{
                    font-family: 'Inter', sans-serif;
                    font-weight: 400;
                    font-size: 0.875rem;
                    color: var(--text-secondary);
                    margin-bottom: 20px;
                    line-height: 1.5;
                }}
                
                .links {{
                    display: flex;
                    gap: 12px;
                    flex-wrap: wrap;
                }}
                
                .link {{
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 500;
                    font-size: 0.875rem;
                    text-decoration: none;
                    transition: all 0.2s ease;
                    font-family: 'Inter', sans-serif;
                }}
                
                .link-docs {{
                    background-color: var(--brand-teal);
                    color: white;
                }}
                
                .link-docs:hover {{
                    background-color: #009688;
                    transform: translateY(-1px);
                }}
                
                .link-redoc {{
                    background-color: var(--brand-orange);
                    color: white;
                }}
                
                .link-redoc:hover {{
                    background-color: #E64A19;
                    transform: translateY(-1px);
                }}
                
                .link-openapi {{
                    background-color: var(--brand-warm-gray);
                    color: var(--brand-deep-blue);
                    border: 1px solid var(--border-color);
                }}
                
                .link-openapi:hover {{
                    background-color: #E8EAED;
                    transform: translateY(-1px);
                }}
                
                .status {{
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 40px;
                    height: 40px;
                    font-size: 1.5rem;
                    margin-left: 8px;
                }}
                
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid var(--border-color);
                    color: var(--text-secondary);
                    font-size: 0.875rem;
                }}
                
                .footer a {{
                    color: var(--brand-teal);
                    text-decoration: none;
                }}
                
                .footer a:hover {{
                    text-decoration: underline;
                }}
                
                @media (max-width: 768px) {{
                    .container {{
                        padding: 20px 16px;
                    }}
                    
                    h1 {{
                        font-size: 2rem;
                    }}
                    
                    .app-grid {{
                        grid-template-columns: 1fr;
                        gap: 16px;
                    }}
                    
                    .links {{
                        flex-direction: column;
                    }}
                    
                    .link {{
                        justify-content: center;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>TruLedgr API</h1>
                <p class="subtitle">A modern personal finance management platform that balances trust and approachability</p>
                
                <div class="app-grid">
                    {api_cards_html}
                </div>

                <div class="footer">
                    <p>Version {__version__} • Copyright © 2025 McGuire Technology, LLC. All rights reserved.</p>
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
    
    # Discover and mount all sub-apps dynamically
    sub_app_creators = discover_sub_apps()
    
    # Mount all sub-apps dynamically
    for app_name, (creator_func, prefix) in sub_app_creators.items():
        try:
            sub_app = creator_func()
            app.mount(prefix, sub_app)
        except Exception as e:
            print(f"❌ Failed to mount {app_name} app: {e}")

    return app
