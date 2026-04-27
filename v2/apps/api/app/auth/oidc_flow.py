"""Cliente OIDC minimo: discovery, PKCE, troca de code, verificacao id_token."""

from __future__ import annotations

import base64
import hashlib
import secrets
import time
from typing import Any
from urllib.parse import urlencode

import httpx
import jwt
from jwt import PyJWKClient

_METADATA_TTL_S = 3600.0
_metadata_cache: dict[str, tuple[dict[str, Any], float]] = {}


def pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    return verifier, challenge


async def fetch_oidc_metadata(issuer: str) -> dict[str, Any]:
    key = issuer.rstrip("/")
    now = time.monotonic()
    if key in _metadata_cache:
        data, expires = _metadata_cache[key]
        if now < expires:
            return data
    url = f"{key}/.well-known/openid-configuration"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    _metadata_cache[key] = (data, now + _METADATA_TTL_S)
    return data


def build_authorize_url(
    authorization_endpoint: str,
    client_id: str,
    redirect_uri: str,
    state: str,
    code_challenge: str,
) -> str:
    q = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "openid email",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{authorization_endpoint}?{urlencode(q)}"


async def exchange_authorization_code(
    token_endpoint: str,
    code: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str | None,
    code_verifier: str,
) -> dict[str, Any]:
    data: dict[str, str] = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }
    if client_secret:
        data["client_secret"] = client_secret
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(token_endpoint, data=data)
        r.raise_for_status()
        return r.json()


def verify_id_token(
    id_token: str,
    issuer: str,
    audience: str | list[str],
    jwks_uri: str,
) -> dict[str, Any]:
    jwk_client = PyJWKClient(jwks_uri)
    signing_key = jwk_client.get_signing_key_from_jwt(id_token)
    return jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        audience=audience,
        issuer=issuer.rstrip("/"),
    )
