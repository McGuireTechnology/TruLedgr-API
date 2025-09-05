import os
import warnings
from typing import get_type_hints

_using_base_model_fallback = False
try:
    # pydantic v2 moved BaseSettings to pydantic-settings package
    from pydantic_settings import BaseSettings
    from pydantic import field_validator
    _has_field_validator = True
except Exception:
    try:
        # pydantic may still expose BaseSettings in some installs
        from pydantic import BaseSettings  # type: ignore
        from pydantic import field_validator  # type: ignore
        _has_field_validator = True
    except Exception:
        # Final fallback: use pydantic.BaseModel so the app can still run
        import pydantic as _pyd

        BaseSettings = _pyd.BaseModel  # type: ignore
        _has_field_validator = False
        _using_base_model_fallback = True


class Settings(BaseSettings):
    app_name: str = "TruLedgr API"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Database settings - REQUIRED (async by default)
    database_url: str
    
    # JWT settings
    secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate database_url manually if field_validator is not available
        if not _has_field_validator and not self.database_url:
            raise ValueError(
                "DATABASE_URL is required. Please set it in your .env file. "
                "Examples:\n"
                "  For SQLite (async): DATABASE_URL=sqlite+aiosqlite:///./truledgr.db\n"
                "  For PostgreSQL (async): DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/truledgr"
            )
        # Convert to async URL if it's not already async
        self.database_url = self._ensure_async_url(self.database_url)
    
    def _ensure_async_url(self, url: str) -> str:
        """Ensure the database URL is async-compatible."""
        if url.startswith("sqlite://"):
            return url.replace("sqlite://", "sqlite+aiosqlite://")
        elif url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://")
        elif url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+aiomysql://")
        else:
            # Already async or unknown format, return as-is
            return url
    
    if _has_field_validator:
        @field_validator('database_url')
        @classmethod
        def validate_database_url(cls, v):
            if not v:
                raise ValueError(
                    "DATABASE_URL is required. Please set it in your .env file. "
                    "Examples:\n"
                    "  For SQLite (async): DATABASE_URL=sqlite+aiosqlite:///./truledgr.db\n"
                    "  For PostgreSQL (async): DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/truledgr"
                )
            return v
    
    @property
    def sync_database_url(self) -> str:
        """Convert async database URL back to sync version for compatibility."""
        if self.database_url.startswith("sqlite+aiosqlite://"):
            return self.database_url.replace("sqlite+aiosqlite://", "sqlite://")
        elif self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
        elif self.database_url.startswith("mysql+aiomysql://"):
            return self.database_url.replace("mysql+aiomysql://", "mysql://")
        else:
            # Return as-is for unknown formats
            return self.database_url

    class Config:
        env_file = ".env"


settings = Settings()

# If we fell back to BaseModel (no BaseSettings available), try to load values from a .env
if _using_base_model_fallback:
    # load .env into environment if python-dotenv is available
    if os.path.exists(".env"):
        try:
            from dotenv import load_dotenv

            load_dotenv(dotenv_path=".env", override=False)
        except Exception:
            warnings.warn("python-dotenv not installed; skipping .env loading. Install python-dotenv to enable .env support.")

    # Build kwargs for Settings from environment variables (FIELD -> FIELD uppercased)
    def _coerce_value(value: str, typ):
        try:
            if typ is bool:
                return value.lower() in ("1", "true", "yes", "on")
            if typ is int:
                return int(value)
            if typ is float:
                return float(value)
        except Exception:
            # If coercion fails, return raw string; pydantic will validate/convert if possible
            return value
        return value

    hints = get_type_hints(Settings)
    env_kwargs = {}
    for field_name, field_type in hints.items():
        env_name = field_name.upper()
        if env_name in os.environ:
            env_kwargs[field_name] = _coerce_value(os.environ[env_name], field_type)

    # Recreate the settings instance with values from env where provided
    settings = Settings(**env_kwargs)
