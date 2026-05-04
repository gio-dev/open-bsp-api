"""POST /v1/embed/session/validate (iframe; sem cookie OAuth). Story 6.1."""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth.session_cookie import decode_payload
from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse, CanonicalValidationErrorResponse
from app.db.session import tenant_session
from app.embed.allowlist import tenant_has_embed_origin
from app.embed.origins import normalize_browser_origin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/embed", tags=["embed"])

_RESPONSES = {
    400: {"model": CanonicalErrorResponse},
    401: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


class EmbedValidateRequest(BaseModel):
    token: str = Field(min_length=1, description="Token embed (HMAC API).")


class EmbedValidateResponse(BaseModel):
    valid: bool = True
    tenant_id: UUID
    actor_user_id: UUID | None = None
    expires_at_epoch: int


def _parse_embed_payload(secret: str, token: str) -> dict[str, object]:
    return decode_payload(token, secret)


@router.post(
    "/session/validate",
    response_model=EmbedValidateResponse,
    summary="Validar sessao embed (token + Origin allowlist)",
    responses={
        200: {"description": "Token e origem aceites."},
        422: {
            "description": "Corpo JSON invalido.",
            "model": CanonicalValidationErrorResponse,
        },
        **_RESPONSES,
    },
)
async def validate_embed_session(
    request: Request,
    body: EmbedValidateRequest,
    origin: Annotated[str | None, Header()] = None,
) -> EmbedValidateResponse:
    """Valida JWT de embed e `Origin` contra lista do tenant (BD + RLS).

    O *host* deve obter o token via servidor (ex. `POST /v1/me/embed/token`);
    o segredo de assinatura nunca vai para o cliente parceiro."""
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")
    secret = settings.embed_jwt_secret
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="embed JWT secret not configured",
        )
    if not origin or not origin.strip():
        raise HTTPException(
            status_code=400,
            detail="Origin header required for embed validation",
        )
    try:
        norm_origin = normalize_browser_origin(origin)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="invalid Origin header",
        ) from None

    rid = getattr(request.state, "request_id", "")
    try:
        payload = _parse_embed_payload(secret, body.token)
    except ValueError as e:
        logger.info("embed_validate token rejected: %s request_id=%s", e, rid)
        raise HTTPException(
            status_code=401,
            detail="invalid or expired embed token",
        ) from e

    ver = payload.get("v")
    if ver != 1:
        raise HTTPException(status_code=401, detail="unsupported embed token version")
    try:
        tid = UUID(str(payload["tid"]))
    except (KeyError, ValueError) as e:
        raise HTTPException(
            status_code=401,
            detail="embed token missing tenant",
        ) from e

    uid: UUID | None = None
    raw_uid = payload.get("uid")
    if raw_uid is not None:
        try:
            uid = UUID(str(raw_uid))
        except ValueError as e:
            raise HTTPException(
                status_code=401,
                detail="embed token user id invalid",
            ) from e

    eor = payload.get("eor")
    if eor is not None:
        try:
            bound = normalize_browser_origin(str(eor))
        except ValueError as e:
            raise HTTPException(
                status_code=401,
                detail="embed token origin binding invalid",
            ) from e
        if bound != norm_origin:
            raise HTTPException(
                status_code=401,
                detail="embed origin does not match token binding",
            )

    exp = int(payload["exp"])
    async with tenant_session(tid) as session:
        ok = await tenant_has_embed_origin(session, tid, norm_origin)
        if not ok:
            logger.warning(
                "embed_validate origin denied tenant=%s origin=%s request_id=%s",
                tid,
                norm_origin,
                rid,
            )
            raise HTTPException(
                status_code=401,
                detail="embed origin not allowed for tenant",
            )

    return EmbedValidateResponse(
        valid=True,
        tenant_id=tid,
        actor_user_id=uid,
        expires_at_epoch=exp,
    )
