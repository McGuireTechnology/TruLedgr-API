import os
import warnings
from typing import get_type_hints

_using_base_model_fallback = False
try:
    # pydantic v2 moved BaseSettings to pydantic-settings package
    from pydantic_settings import BaseSettings  # type: ignore
except Exception:
    try:
        # pydantic may still expose BaseSettings in some installs
        from pydantic import BaseSettings  # type: ignore
    except Exception:
        # Final fallback: use pydantic.BaseModel so the app can still run
        import pydantic as _pyd

        BaseSettings = _pyd.BaseModel  # type: ignore
        _using_base_model_fallback = True


class Settings(BaseSettings):
    app_name: str = "TruLedgr API"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000

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
