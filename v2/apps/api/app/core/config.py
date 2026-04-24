"""Application settings (env-driven)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: str | None = None
    """Async SQLAlchemy URL, e.g. postgresql+asyncpg://app_runtime:pass@host:5432/db"""

    auth_dev_stub: bool = False
    """True: resolve tenant from X-Dev-Tenant-Id (dev/CI; replace with real auth)."""

    session_signing_secret: str | None = None
    """HMAC secret cookie consola (SESSION_SIGNING_SECRET). Obrigatorio sem stub."""

    session_cookie_name: str = "obsp_session"
    session_cookie_secure: bool = True
    """False em dev HTTP local (SESSION_COOKIE_SECURE=false)."""

    oidc_issuer: str | None = None
    """Issuer OIDC (ex. https://tenant.eu.auth0.com). OIDC_ISSUER."""

    oidc_client_id: str | None = None
    oidc_client_secret: str | None = None
    oidc_redirect_uri: str | None = None
    """Callback registado no IdP (ex. http://api:8000/v1/auth/oidc/callback)."""

    oidc_audience: str | None = None
    """Audience do id_token; por omissao igual a oidc_client_id."""

    oidc_tenant_claim: str = "https://openbsp.dev/active_tenant_id"
    """Claim opcional no id_token (UUID) validada contra tenant_memberships."""

    console_post_login_redirect: str | None = None
    """URL da SPA apos login (ex. http://localhost:5173/)."""

    console_cors_origin: str | None = None
    """Origin da consola para CORS com credentials (ex. http://localhost:5173)."""

    whatsapp_webhook_verify_token: str | None = None
    """Token hub.verify_token na verificacao GET (WHATSAPP_WEBHOOK_VERIFY_TOKEN)."""

    whatsapp_webhook_app_secret: str | None = None
    """App Secret para X-Hub-Signature-256 no POST (WHATSAPP_WEBHOOK_APP_SECRET)."""

    whatsapp_webhook_max_body_bytes: int = 2 * 1024 * 1024
    """Max POST body size (bytes); DoS mitigation (WHATSAPP_WEBHOOK_MAX_BODY_BYTES)."""


@lru_cache
def get_settings() -> Settings:
    return Settings()
