"""Gestao de embed por tenant (origins allowlist + emissao de token). Story 6.1."""

from __future__ import annotations

import time
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, select

from app.auth.session_cookie import encode_payload
from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse, CanonicalValidationErrorResponse
from app.db.models import TenantEmbedOrigin
from app.db.session import tenant_session
from app.embed.allowlist import tenant_has_embed_origin
from app.embed.origins import normalize_browser_origin
from app.tenancy.deps import TenantUserContext, console_org_admin_context

router = APIRouter(prefix="/me/embed", tags=["embed"])

_RESPONSES = {
    400: {"model": CanonicalErrorResponse},
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


class EmbedOriginsResponse(BaseModel):
    origins: list[str]


class EmbedOriginsPutRequest(BaseModel):
    origins: list[str] = Field(
        default_factory=list,
        description="Lista completa substitui configuracao anterior.",
    )


class EmbedMintRequest(BaseModel):
    embed_origin: str | None = Field(
        default=None,
        description=(
            "Opcional; claim `eor` no token. Tem de existir previamente na "
            "allowlist (`PUT /v1/me/embed/origins`)."
        ),
    )
    ttl_seconds: int | None = Field(default=None, ge=60, le=3600)


class EmbedMintResponse(BaseModel):
    token: str
    expires_at_epoch: int


@router.get(
    "/origins",
    response_model=EmbedOriginsResponse,
    responses={
        401: {"model": CanonicalErrorResponse},
        403: {"model": CanonicalErrorResponse},
        503: {"model": CanonicalErrorResponse},
    },
)
async def list_embed_origins(
    ctx: Annotated[TenantUserContext, Depends(console_org_admin_context)],
) -> EmbedOriginsResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")
    async with tenant_session(ctx.tenant_id) as session:
        q = (
            select(TenantEmbedOrigin.origin)
            .where(TenantEmbedOrigin.tenant_id == ctx.tenant_id)
            .order_by(TenantEmbedOrigin.origin.asc())
        )
        res = await session.execute(q)
        rows = [r[0] for r in res.all()]
    return EmbedOriginsResponse(origins=rows)


@router.put(
    "/origins",
    response_model=EmbedOriginsResponse,
    responses={
        400: {"model": CanonicalErrorResponse},
        **_RESPONSES,
    },
)
async def put_embed_origins(
    body: EmbedOriginsPutRequest,
    ctx: Annotated[TenantUserContext, Depends(console_org_admin_context)],
) -> EmbedOriginsResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")
    normed: list[str] = []
    seen: set[str] = set()
    for raw in body.origins:
        try:
            v = normalize_browser_origin(raw)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"invalid origin: {raw!r}",
            ) from e
        if v not in seen:
            seen.add(v)
            normed.append(v)
    async with tenant_session(ctx.tenant_id) as session:
        await session.execute(
            delete(TenantEmbedOrigin).where(
                TenantEmbedOrigin.tenant_id == ctx.tenant_id
            ),
        )
        for o in normed:
            session.add(
                TenantEmbedOrigin(
                    id=uuid.uuid4(),
                    tenant_id=ctx.tenant_id,
                    origin=o,
                )
            )
    return EmbedOriginsResponse(origins=normed)


@router.post(
    "/token",
    response_model=EmbedMintResponse,
    status_code=201,
    responses={
        201: {"description": "Token emitido; mostrar apenas ao host servidor."},
        400: {"model": CanonicalErrorResponse},
        401: {"model": CanonicalErrorResponse},
        403: {"model": CanonicalErrorResponse},
        422: {"model": CanonicalValidationErrorResponse},
        503: {"model": CanonicalErrorResponse},
    },
)
async def mint_embed_token(
    body: EmbedMintRequest,
    ctx: Annotated[TenantUserContext, Depends(console_org_admin_context)],
) -> EmbedMintResponse:
    settings = get_settings()
    secret = settings.embed_jwt_secret
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="embed JWT secret not configured",
        )
    ttl = (
        body.ttl_seconds
        if body.ttl_seconds is not None
        else settings.embed_token_ttl_seconds
    )
    now = int(time.time())
    exp = now + ttl
    pld: dict[str, object] = {"v": 1, "tid": str(ctx.tenant_id), "exp": exp}
    if ctx.actor_user_id:
        pld["uid"] = str(ctx.actor_user_id)
    if body.embed_origin is not None and body.embed_origin.strip():
        try:
            eor_norm = normalize_browser_origin(body.embed_origin)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail="invalid embed_origin",
            ) from e
        async with tenant_session(ctx.tenant_id) as session:
            if not await tenant_has_embed_origin(
                session,
                ctx.tenant_id,
                eor_norm,
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "embed_origin not in tenant allowlist; "
                        "add it via PUT /v1/me/embed/origins first"
                    ),
                )
        pld["eor"] = eor_norm
    tok = encode_payload(pld, secret)
    return EmbedMintResponse(token=tok, expires_at_epoch=exp)
