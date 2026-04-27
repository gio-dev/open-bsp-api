"""OAuth/OIDC consola: login, callback, sessao, logout (Story 2.1)."""

from __future__ import annotations

import logging
import secrets
import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from app.auth.console_identity import (
    all_memberships_for_user,
    membership_for_user_tenant,
    resolve_active_tenant_id,
    upsert_console_user,
)
from app.auth.oidc_flow import (
    build_authorize_url,
    exchange_authorization_code,
    fetch_oidc_metadata,
    pkce_pair,
    verify_id_token,
)
from app.auth.session_cookie import decode_payload, encode_payload
from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.db.session import platform_session
from app.tenancy.rbac import VALID_TENANT_ROLES

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger(__name__)

OIDC_HANDSHAKE_COOKIE = "obsp_oidc"
SESSION_VERSION = 1


class SessionResponse(BaseModel):
    user_id: UUID
    tenant_id: UUID
    email: str
    roles: list[str] = Field(default_factory=list)


def _oidc_configured(settings: Any) -> bool:
    return bool(
        settings.oidc_issuer and settings.oidc_client_id and settings.oidc_redirect_uri
    )


def _session_secret_or_503(settings: Any) -> str:
    secret = settings.session_signing_secret
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="session signing secret not configured",
        )
    return secret


def _redirect_frontend_error(settings: Any, code: str) -> RedirectResponse:
    base = settings.console_post_login_redirect or "http://localhost:5173/"
    parts = urlparse(base)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))
    q["auth_error"] = code
    new_query = urlencode(q)
    url = urlunparse(
        (
            parts.scheme,
            parts.netloc,
            parts.path or "/",
            parts.params,
            new_query,
            parts.fragment,
        )
    )
    return RedirectResponse(url, status_code=302)


def _tenant_claim_from_token(claims: dict[str, Any], claim_key: str) -> UUID | None:
    raw = claims.get(claim_key)
    if raw is None or raw == "":
        return None
    try:
        return UUID(str(raw))
    except ValueError:
        return None


@router.get(
    "/oidc/login",
    responses={
        302: {"description": "Redireciona para o IdP"},
        503: {"model": CanonicalErrorResponse},
    },
)
async def oidc_login() -> RedirectResponse:
    settings = get_settings()
    if not _oidc_configured(settings):
        raise HTTPException(status_code=503, detail="OpenID Connect not configured")
    secret = _session_secret_or_503(settings)
    meta = await fetch_oidc_metadata(settings.oidc_issuer or "")
    auth_ep = meta.get("authorization_endpoint")
    if not auth_ep:
        raise HTTPException(status_code=503, detail="IdP metadata incomplete")

    state = secrets.token_urlsafe(32)
    verifier, challenge = pkce_pair()
    now = int(time.time())
    handshake = encode_payload(
        {
            "v": 1,
            "state": state,
            "cv": verifier,
            "exp": now + 600,
        },
        secret,
    )
    url = build_authorize_url(
        auth_ep,
        settings.oidc_client_id or "",
        settings.oidc_redirect_uri or "",
        state,
        challenge,
    )
    resp = RedirectResponse(url, status_code=302)
    resp.set_cookie(
        key=OIDC_HANDSHAKE_COOKIE,
        value=handshake,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        max_age=600,
        path="/",
    )
    return resp


@router.get(
    "/oidc/callback",
    response_class=RedirectResponse,
    responses={
        302: {
            "description": (
                "Sucesso: redireciona para a consola com cookie de sessao. "
                "Falha: redireciona com query `auth_error=<code>` "
                "(ex.: idp_error, token_exchange_failed, no_org_access)."
            ),
        },
    },
)
async def oidc_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    settings = get_settings()
    if error:
        return _redirect_frontend_error(settings, "idp_error")
    if not code or not state:
        return _redirect_frontend_error(settings, "oauth_missing_params")

    if not _oidc_configured(settings):
        return _redirect_frontend_error(settings, "oidc_not_configured")

    secret = settings.session_signing_secret
    if not secret:
        return _redirect_frontend_error(settings, "server_misconfigured")

    raw_hs = request.cookies.get(OIDC_HANDSHAKE_COOKIE)
    if not raw_hs:
        return _redirect_frontend_error(settings, "oauth_state_missing")
    try:
        hs = decode_payload(raw_hs, secret)
    except ValueError:
        return _redirect_frontend_error(settings, "oauth_state_invalid")

    if hs.get("state") != state:
        return _redirect_frontend_error(settings, "oauth_state_mismatch")

    verifier = hs.get("cv")
    if not isinstance(verifier, str):
        return _redirect_frontend_error(settings, "oauth_pkce_invalid")

    meta = await fetch_oidc_metadata(settings.oidc_issuer or "")
    token_ep = meta.get("token_endpoint")
    jwks_uri = meta.get("jwks_uri")
    issuer = meta.get("issuer") or settings.oidc_issuer
    if not token_ep or not jwks_uri or not issuer:
        return _redirect_frontend_error(settings, "idp_metadata_incomplete")

    try:
        tokens = await exchange_authorization_code(
            token_ep,
            code,
            settings.oidc_redirect_uri or "",
            settings.oidc_client_id or "",
            settings.oidc_client_secret,
            verifier,
        )
    except Exception as e:
        logger.warning(
            "oidc token exchange failed: %s",
            e,
            exc_info=True,
        )
        return _redirect_frontend_error(settings, "token_exchange_failed")

    id_token = tokens.get("id_token")
    if not id_token or not isinstance(id_token, str):
        return _redirect_frontend_error(settings, "no_id_token")

    aud = settings.oidc_audience or settings.oidc_client_id
    audience: str | list[str] = aud if isinstance(aud, str) else str(aud)
    try:
        claims = verify_id_token(
            id_token,
            str(issuer),
            audience,
            str(jwks_uri),
        )
    except Exception as e:
        logger.warning(
            "oidc id_token verification failed: %s",
            e,
            exc_info=True,
        )
        return _redirect_frontend_error(settings, "id_token_invalid")

    sub = claims.get("sub")
    email = str(claims.get("email") or claims.get("preferred_username") or "")
    if not sub or not isinstance(sub, str):
        return _redirect_frontend_error(settings, "idp_claims_incomplete")

    claim_tid = _tenant_claim_from_token(claims, settings.oidc_tenant_claim)

    if not settings.database_url:
        return _redirect_frontend_error(settings, "database_unavailable")

    try:
        async with platform_session() as dbs:
            user = await upsert_console_user(dbs, sub, email or "unknown@local")
            memberships = await all_memberships_for_user(dbs, user.id)
            tenant_id = resolve_active_tenant_id(memberships, claim_tid)
            row = await membership_for_user_tenant(dbs, user.id, tenant_id)
            active_role = row.role if row else None
            if active_role not in VALID_TENANT_ROLES:
                return _redirect_frontend_error(settings, "no_org_access")
    except ValueError as e:
        err = str(e)
        if err == "no_membership":
            return _redirect_frontend_error(settings, "no_org_access")
        if err == "tenant_claim_not_in_memberships":
            return _redirect_frontend_error(settings, "tenant_claim_denied")
        return _redirect_frontend_error(settings, "membership_error")

    now = int(time.time())
    sess = encode_payload(
        {
            "v": SESSION_VERSION,
            "uid": str(user.id),
            "tid": str(tenant_id),
            "roles": [active_role],
            "email": user.email,
            "exp": now + 7 * 86400,
        },
        secret,
    )

    target = settings.console_post_login_redirect or "http://localhost:5173/"
    resp = RedirectResponse(target, status_code=302)
    resp.set_cookie(
        key=settings.session_cookie_name,
        value=sess,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        max_age=7 * 86400,
        path="/",
    )
    resp.delete_cookie(OIDC_HANDSHAKE_COOKIE, path="/")
    return resp


@router.get(
    "/session",
    response_model=SessionResponse,
    responses={
        401: {"model": CanonicalErrorResponse},
        503: {"model": CanonicalErrorResponse},
    },
)
async def auth_session(request: Request) -> SessionResponse:
    settings = get_settings()
    secret = settings.session_signing_secret
    if not secret:
        raise HTTPException(status_code=503, detail="session not configured")
    raw = request.cookies.get(settings.session_cookie_name)
    if not raw:
        raise HTTPException(status_code=401, detail="authentication required")
    try:
        payload = decode_payload(raw, secret)
    except ValueError:
        raise HTTPException(status_code=401, detail="invalid session")

    if int(payload.get("v", 0)) != SESSION_VERSION:
        raise HTTPException(status_code=401, detail="invalid session")
    try:
        uid = UUID(str(payload["uid"]))
        tid = UUID(str(payload["tid"]))
    except (KeyError, ValueError):
        raise HTTPException(status_code=401, detail="invalid session")

    roles_raw = payload.get("roles") or []
    roles = [str(r) for r in roles_raw] if isinstance(roles_raw, list) else []
    roles = [r for r in roles if r in VALID_TENANT_ROLES]
    if not roles:
        raise HTTPException(status_code=401, detail="invalid session")
    email = str(payload.get("email") or "")
    return SessionResponse(user_id=uid, tenant_id=tid, email=email, roles=roles)


@router.post(
    "/logout",
    responses={
        200: {"description": "Sessao terminada"},
    },
)
async def auth_logout(_request: Request) -> JSONResponse:
    settings = get_settings()
    resp = JSONResponse({"status": "logged_out"})
    resp.delete_cookie(settings.session_cookie_name, path="/")
    resp.delete_cookie(OIDC_HANDSHAKE_COOKIE, path="/")
    return resp
