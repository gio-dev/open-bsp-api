"""WhatsApp Cloud API webhooks - verificacao Meta + ingestao (BSUID-ready)."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.db.session import tenant_session
from app.whatsapp.identity import resolve_inbound_identity
from app.whatsapp.webhook_ingress import enqueue_whatsapp_payload
from app.whatsapp.webhook_verify_db import match_verify_token

router = APIRouter(prefix="/webhooks", tags=["whatsapp_webhooks"])


def _hub_signature_valid(
    body: bytes,
    signature_header: str | None,
    app_secret: str,
) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = (
        "sha256="
        + hmac.new(app_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    )
    return hmac.compare_digest(expected.strip(), signature_header.strip())


class WebhookIngressAccepted(BaseModel):
    """Resposta POST webhook apos validacao e enfileiramento (quando aplicavel)."""

    status: Literal["accepted"] = "accepted"
    request_id: str = Field(description="Correlation id (UX-DR6 / CDA).")
    enqueued: int = Field(0, description="Novos eventos persistidos na fila interna.")
    deduplicated: int = Field(
        0,
        description=(
            "Eventos ja vistos (mesmo waba_id + id Meta); sem efeito duplicado."
        ),
    )
    skipped: int = Field(
        0, description="Notificacoes sem id enqueueable (ex. mensagem sem id)."
    )


@router.get(
    "/whatsapp",
    response_class=PlainTextResponse,
    summary="Verificacao webhook Meta (hub.challenge)",
    responses={
        400: {"description": "hub.mode invalido"},
        403: {"description": "verify_token incorreto"},
        503: {"description": "Base de dados indisponivel para modo tenant"},
    },
)
async def whatsapp_webhook_verify(
    hub_mode: Annotated[str, Query(alias="hub.mode")],
    hub_verify_token: Annotated[str, Query(alias="hub.verify_token")],
    hub_challenge: Annotated[str, Query(alias="hub.challenge")],
    tenant_id: Annotated[
        UUID | None,
        Query(description="UUID tenant (modo hub com segredo por tenant; Story 2.4)"),
    ] = None,
) -> PlainTextResponse:
    if hub_mode != "subscribe":
        raise HTTPException(status_code=400, detail="invalid hub.mode")
    settings = get_settings()
    if tenant_id is not None:
        if not settings.database_url:
            raise HTTPException(
                status_code=503, detail="database unavailable for tenant verify"
            )
        async with tenant_session(tenant_id) as session:
            ok = await match_verify_token(session, tenant_id, hub_verify_token)
        if not ok:
            raise HTTPException(status_code=403, detail="verify token mismatch")
        return PlainTextResponse(content=hub_challenge)
    expected = settings.whatsapp_webhook_verify_token
    if not expected or hub_verify_token != expected:
        raise HTTPException(status_code=403, detail="verify token mismatch")
    return PlainTextResponse(content=hub_challenge)


@router.post(
    "/whatsapp",
    status_code=202,
    response_model=WebhookIngressAccepted,
    summary="Ingresso webhook WhatsApp (payload Meta)",
    responses={
        400: {
            "description": "JSON invalido, object nao suportado ou timestamp em falta",
            "model": CanonicalErrorResponse,
        },
        401: {
            "description": "Assinatura X-Hub-Signature-256 invalida",
            "model": CanonicalErrorResponse,
        },
        404: {
            "description": "WABA nao registado",
            "model": CanonicalErrorResponse,
        },
        409: {
            "description": "Replay fora da janela ou mapeamento WABA ambiguo",
            "model": CanonicalErrorResponse,
        },
        413: {
            "description": "Corpo demasiado grande",
            "model": CanonicalErrorResponse,
        },
        503: {
            "description": "Segredo em falta (prod) ou BD necessaria",
            "model": CanonicalErrorResponse,
        },
    },
)
async def whatsapp_webhook_ingress(request: Request) -> WebhookIngressAccepted:
    settings = get_settings()
    max_bytes = settings.whatsapp_webhook_max_body_bytes
    body = await request.body()
    if len(body) > max_bytes:
        raise HTTPException(status_code=413, detail="webhook body too large")

    secret = settings.whatsapp_webhook_app_secret
    if not secret and not settings.auth_dev_stub:
        raise HTTPException(
            status_code=503,
            detail="WHATSAPP_WEBHOOK_APP_SECRET is required in production",
        )
    if secret:
        sig = request.headers.get("X-Hub-Signature-256")
        if not _hub_signature_valid(body, sig, secret):
            raise HTTPException(status_code=401, detail="invalid webhook signature")

    try:
        payload: dict[str, Any] = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail="invalid json body") from e

    if payload.get("object") != "whatsapp_business_account":
        raise HTTPException(status_code=400, detail="unsupported webhook object")

    for entry in payload.get("entry") or []:
        if not isinstance(entry, dict):
            continue
        for change in entry.get("changes") or []:
            if not isinstance(change, dict):
                continue
            value = change.get("value")
            if not isinstance(value, dict):
                continue
            for msg in value.get("messages") or []:
                if isinstance(msg, dict):
                    _ = resolve_inbound_identity(value, msg)

    rid = getattr(request.state, "request_id", "") or ""
    counts = await enqueue_whatsapp_payload(
        payload=payload,
        settings=settings,
        request_id=rid,
    )

    return WebhookIngressAccepted(
        request_id=rid,
        enqueued=counts["enqueued"],
        deduplicated=counts["deduplicated"],
        skipped=counts["skipped"],
    )
