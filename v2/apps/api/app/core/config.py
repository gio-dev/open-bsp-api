"""Application settings (env-driven)."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: str | None = None
    """Async SQLAlchemy URL, e.g. postgresql+asyncpg://app_runtime:pass@host:5432/db"""

    auth_dev_stub: bool = False
    """True: resolve tenant from X-Dev-Tenant-Id (dev/CI; replace with real auth)."""

    allow_atdd_sandbox_flow_key: bool = False
    """Liga a chave literal `atdd-flow` sem AUTH_DEV_STUB (CI/staging *estritamente
    controlado*). Nunca em ambiente de dados reais: o stub ignora rascunho gravado e
    debilita auditoria (nao ha UUID de draft). Omissao: False."""

    sandbox_fixture_max_json_bytes: int = 256 * 1024
    """Tamanho maximo do JSON canonico de `fixture_message` (bytes); mitigacao DoS.

    (SANDBOX_FIXTURE_MAX_JSON_BYTES)
    """

    sandbox_trace_fixture_preview_chars: int = 512
    """Max caracteres do fixture incluidos em linhas do trace (resto omitido no log).

    Conteudo completo do fixture continua no corpo da resposta e, se persistido, na BD.
    """

    require_sandbox_success_before_publish: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "OPENBSP_REQUIRE_SANDBOX_BEFORE_PUBLISH",
            "require_sandbox_success_before_publish",
        ),
        description=(
            "Exige pelo menos um sandbox-run succeeded para o mesmo draft antes de "
            "publish (UUID real; atdd-flow isenta). Emergencia: "
            "OPENBSP_REQUIRE_SANDBOX_BEFORE_PUBLISH=false."
        ),
    )

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

    whatsapp_webhook_max_event_age_seconds: int = 600
    """Janela anti-replay: eventos Meta mais velhos sao rejeitados (409)."""

    whatsapp_graph_base_url: str = "https://graph.facebook.com"
    """Base URL Graph API (WHATSAPP_GRAPH_BASE_URL)."""

    whatsapp_graph_api_version: str = "v21.0"
    """Versao path Graph (WHATSAPP_GRAPH_API_VERSION)."""

    whatsapp_cloud_access_token: str | None = None
    """Token de sistema / numero para envio (WHATSAPP_CLOUD_ACCESS_TOKEN)."""

    whatsapp_cloud_api_stub: bool = False
    """True: envio sem HTTP real (WHATSAPP_CLOUD_API_STUB). CI/dev sem token."""

    outbound_sweep_interval_seconds: int = 0
    """Intervalo do sweep outbound (0 = desligado; ex.: 15 em producao)."""

    outbound_sweep_batch_size: int = 50
    """Max envios por passagem do sweep (OUTBOUND_SWEEP_BATCH_SIZE)."""


@lru_cache
def get_settings() -> Settings:
    return Settings()
