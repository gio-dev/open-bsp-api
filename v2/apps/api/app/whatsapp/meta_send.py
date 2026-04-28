"""Envio WhatsApp Cloud API (saida). Story 3.2."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings, get_settings

log = logging.getLogger(__name__)

_E164_RE = re.compile(r"^\+?[1-9]\d{6,14}$")


def normalize_whatsapp_to(raw: str) -> str:
    """Normaliza destino para E.164 sem espacos (Meta)."""
    s = "".join(raw.strip().split())
    if not s:
        raise ValueError("empty recipient")
    if s.startswith("+"):
        s = s[1:]
    if not s.isdigit():
        raise ValueError("recipient must be digits (E.164)")
    if not _E164_RE.match("+" + s):
        raise ValueError("invalid E.164 recipient")
    return s


@dataclass(frozen=True)
class MetaSendResult:
    ok: bool
    meta_message_id: str | None = None
    http_status: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    retry_after_seconds: int | None = None


async def send_whatsapp_text(
    *,
    phone_number_id: str,
    to_digits: str,
    body: str,
    settings: Settings | None = None,
    client: httpx.AsyncClient | None = None,
) -> MetaSendResult:
    """POST Graph API messages; trata 429 com Retry-After."""
    st = settings or get_settings()
    if st.whatsapp_cloud_api_stub:
        mid = f"wamid.stub.{phone_number_id[:8]}.{abs(hash(body)) % 10_000_000:07d}"
        log.info(
            "outbound_meta_stub_send",
            extra={"phone_number_id": phone_number_id, "stub": True},
        )
        return MetaSendResult(ok=True, meta_message_id=mid, http_status=200)

    if not st.whatsapp_cloud_access_token:
        return MetaSendResult(
            ok=False,
            http_status=None,
            error_code="missing_token",
            error_message="WHATSAPP_CLOUD_ACCESS_TOKEN not configured",
        )

    token = st.whatsapp_cloud_access_token
    url = (
        f"{st.whatsapp_graph_base_url.rstrip('/')}/"
        f"{st.whatsapp_graph_api_version}/{phone_number_id}/messages"
    )
    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_digits,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    own_client = client is None
    hc = client or httpx.AsyncClient(timeout=30.0)
    try:
        resp = await hc.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            mids = (data.get("messages") or [{}])[0]
            mid = mids.get("id") if isinstance(mids, dict) else None
            if not isinstance(mid, str) or not mid.strip():
                log.warning(
                    "outbound_meta_missing_message_id",
                    extra={"phone_number_id": phone_number_id},
                )
                return MetaSendResult(
                    ok=False,
                    http_status=200,
                    error_code="missing_message_id",
                    error_message="Graph API returned 200 without messages[0].id",
                )
            return MetaSendResult(
                ok=True,
                meta_message_id=mid.strip(),
                http_status=200,
            )
        if resp.status_code == 429:
            retry_raw = resp.headers.get("Retry-After")
            retry_s: int | None = None
            if retry_raw:
                try:
                    retry_s = max(1, int(retry_raw.strip()))
                except ValueError:
                    retry_s = 60
            else:
                retry_s = 60
            log.warning(
                "outbound_meta_429",
                extra={
                    "phone_number_id": phone_number_id,
                    "retry_after_seconds": retry_s,
                },
            )
            return MetaSendResult(
                ok=False,
                http_status=429,
                error_code="rate_limited",
                error_message="Meta rate limit",
                retry_after_seconds=retry_s,
            )
        try:
            err = resp.json()
            err_msg = str(err.get("error", {}).get("message", resp.text))[:1024]
            err_code = str(err.get("error", {}).get("code", resp.status_code))
        except Exception:
            err_msg = resp.text[:1024] if resp.text else "unknown error"
            err_code = str(resp.status_code)
        log.warning(
            "outbound_meta_error",
            extra={
                "http_status": resp.status_code,
                "error_code": err_code,
            },
        )
        return MetaSendResult(
            ok=False,
            http_status=resp.status_code,
            error_code=err_code,
            error_message=err_msg,
        )
    finally:
        if own_client:
            await hc.aclose()
