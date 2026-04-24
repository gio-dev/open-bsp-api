"""WhatsApp Cloud API webhooks - verificacao Meta + ingestao (BSUID-ready)."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.core.config import get_settings
from app.whatsapp.identity import resolve_inbound_identity

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


@router.get("/whatsapp")
async def whatsapp_webhook_verify(
    hub_mode: Annotated[str, Query(alias="hub.mode")],
    hub_verify_token: Annotated[str, Query(alias="hub.verify_token")],
    hub_challenge: Annotated[str, Query(alias="hub.challenge")],
) -> PlainTextResponse:
    if hub_mode != "subscribe":
        raise HTTPException(status_code=400, detail="invalid hub.mode")
    settings = get_settings()
    expected = settings.whatsapp_webhook_verify_token
    if not expected or hub_verify_token != expected:
        raise HTTPException(status_code=403, detail="verify token mismatch")
    return PlainTextResponse(content=hub_challenge)


@router.post("/whatsapp", status_code=202)
async def whatsapp_webhook_ingress(request: Request) -> dict[str, str]:
    settings = get_settings()
    max_bytes = settings.whatsapp_webhook_max_body_bytes
    body = await request.body()
    if len(body) > max_bytes:
        raise HTTPException(status_code=413, detail="webhook body too large")

    secret = settings.whatsapp_webhook_app_secret
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

    # Epic 3: substituir por fila/handlers; hoje apenas valida parsing + BSUID.
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

    return {"status": "accepted"}
