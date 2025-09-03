"""Auth package stub

Place provider-specific settings and wiring here (e.g., microsoft, github, google, apple).
Each provider should expose a `get_provider_settings()` function or a Settings dataclass so modules that rely on that provider import only from the provider package rather than a global settings module.
"""

# Example: define an interface for provider settings
from dataclasses import dataclass
from typing import Optional


@dataclass
class OAuthProviderSettings:
    client_id: str
    client_secret: str
    redirect_uri: Optional[str] = None


# Providers can implement get_settings() returning OAuthProviderSettings
