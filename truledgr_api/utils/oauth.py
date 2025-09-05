"""OAuth provider settings and configurations."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OAuthProviderSettings:
    """Settings for OAuth2 provider configuration."""
    client_id: str
    client_secret: str
    redirect_uri: Optional[str] = None


# Providers can implement get_settings() returning OAuthProviderSettings
