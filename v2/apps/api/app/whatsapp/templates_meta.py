"""Sincronizacao message templates + sinais canal (Graph API). Story 3.3."""

from __future__ import annotations

import logging
from typing import Any, Literal

import httpx

from app.core.config import Settings

log = logging.getLogger(__name__)

DisplayStatus = Literal[
    "draft",
    "submitted",
    "approved",
    "paused",
    "rejected",
]

_META_TO_DISPLAY: dict[str, DisplayStatus] = {
    "APPROVED": "approved",
    "APPROVED_LOW_QUALITY": "approved",
    "PENDING": "submitted",
    "PENDING_DELETION": "submitted",
    "IN_APPEAL": "submitted",
    "REJECTED": "rejected",
    "PAUSED": "paused",
    "DISABLED": "paused",
    "LIMIT_EXCEEDED": "paused",
}


def map_template_record(
    raw: dict[str, Any],
) -> tuple[DisplayStatus, str, str | None, str | None]:
    """Mapeia documento Meta para (display_status, meta_status, detail, quality)."""
    meta_st = str(raw.get("status") or "").strip().upper() or "UNKNOWN"
    detail: str | None = None
    if isinstance(raw.get("rejected_reason"), str) and raw["rejected_reason"].strip():
        detail = raw["rejected_reason"].strip()[:1024]
    elif meta_st == "APPROVED_LOW_QUALITY":
        detail = "Meta: approved with low quality flag"
    quality: str | None = None
    q = raw.get("quality_score")
    if isinstance(q, str) and q.strip():
        quality = q.strip()[:32]

    mapped = _META_TO_DISPLAY.get(meta_st)
    if mapped is None:
        display: DisplayStatus = "submitted"
        extra = (
            "Meta template status missing from payload"
            if meta_st == "UNKNOWN"
            else f"Unmapped Meta template status: {meta_st}"
        )
        detail = f"{detail}; {extra}" if detail else extra
        if len(detail) > 1024:
            detail = detail[:1021] + "..."
    else:
        display = mapped

    return display, meta_st, detail, quality


def _graph_url(settings: Settings, path: str) -> str:
    base = settings.whatsapp_graph_base_url.rstrip("/")
    ver = settings.whatsapp_graph_api_version.strip("/")
    p = path.lstrip("/")
    return f"{base}/{ver}/{p}"


async def fetch_message_templates(
    settings: Settings,
    waba_id: str,
    *,
    client: httpx.AsyncClient | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Lista templates da WABA (primeira pagina; ver nota paging no handler OpenAPI).

    Segundo valor: True se a chamada Graph foi bem-sucedida (inclui lista vazia
    legitima). False em erro HTTP/parse ? o caller nao deve apagar cache local.
    """
    if settings.whatsapp_cloud_api_stub:
        return (
            [
                {
                    "id": "stub_tpl_1",
                    "name": "ci_welcome",
                    "status": "APPROVED",
                    "language": "pt_PT",
                    "category": "UTILITY",
                },
                {
                    "id": "stub_tpl_2",
                    "name": "ci_promo",
                    "status": "PAUSED",
                    "language": "pt_PT",
                    "category": "MARKETING",
                    "rejected_reason": "LOW_QUALITY",
                },
            ],
            True,
        )

    if not settings.whatsapp_cloud_access_token:
        log.warning(
            "templates_sync_skipped_no_token",
            extra={"waba_id": waba_id},
        )
        return [], False

    url = _graph_url(settings, f"{waba_id}/message_templates")
    headers = {"Authorization": f"Bearer {settings.whatsapp_cloud_access_token}"}
    params = {"fields": "name,status,language,category,id,rejected_reason"}
    close_client = False
    hc = client
    if hc is None:
        hc = httpx.AsyncClient(timeout=30.0)
        close_client = True
    try:
        r = await hc.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, ValueError) as e:
        log.warning(
            "templates_fetch_failed",
            extra={"waba_id": waba_id, "error": str(e)},
        )
        return [], False
    finally:
        if close_client:
            await hc.aclose()

    if not isinstance(data, dict):
        log.warning(
            "templates_fetch_invalid_shape",
            extra={"waba_id": waba_id},
        )
        return [], False
    rows = data.get("data")
    if not isinstance(rows, list):
        log.warning(
            "templates_fetch_invalid_data_field",
            extra={"waba_id": waba_id},
        )
        return [], False
    out: list[dict[str, Any]] = []
    for item in rows:
        if isinstance(item, dict):
            out.append(item)
    return out, True


async def fetch_channel_signals(
    settings: Settings,
    phone_number_id: str,
    *,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Quality rating / tier quando Graph devolve (pode ficar vazio)."""
    if settings.whatsapp_cloud_api_stub:
        return {
            "quality_rating": "GREEN",
            "messaging_limit_tier": "TIER_250",
            "source": "stub",
        }

    if not settings.whatsapp_cloud_access_token:
        return {"source": "unavailable"}

    url = _graph_url(settings, phone_number_id)
    headers = {"Authorization": f"Bearer {settings.whatsapp_cloud_access_token}"}
    params = {"fields": "quality_rating,messaging_limit_tier"}
    close_client = False
    hc = client
    if hc is None:
        hc = httpx.AsyncClient(timeout=30.0)
        close_client = True
    try:
        r = await hc.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, ValueError) as e:
        log.warning(
            "channel_signals_fetch_failed",
            extra={"phone_number_id": phone_number_id, "error": str(e)},
        )
        return {"source": "unavailable"}
    finally:
        if close_client:
            await hc.aclose()

    if not isinstance(data, dict):
        return {"source": "unavailable"}
    return {
        "quality_rating": data.get("quality_rating"),
        "messaging_limit_tier": data.get("messaging_limit_tier"),
        "source": "graph",
    }
