"""Sweep periodico: reprocessar fila outbound (queued / rate_limited). Story 3.2."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import platform_session
from app.whatsapp.outbound_worker import deliver_outbound_message

log = logging.getLogger(__name__)

_ADV_K1 = 90210
_ADV_K2 = 334


async def run_outbound_sweep_once() -> None:
    """Uma passagem: candidatos due (funcao SECURITY DEFINER) + deliver por linha."""
    settings = get_settings()
    if not settings.database_url:
        return
    batch = max(1, min(settings.outbound_sweep_batch_size, 500))
    rows: list[tuple] = []
    async with platform_session() as session:
        await session.execute(
            text("SELECT pg_advisory_lock(:k1, :k2)"),
            {"k1": _ADV_K1, "k2": _ADV_K2},
        )
        try:
            res = await session.execute(
                text(
                    "SELECT message_id, p_tenant_id "
                    "FROM due_outbound_candidates(CAST(:lim AS integer))"
                ),
                {"lim": batch},
            )
            rows = list(res.all())
        finally:
            await session.execute(
                text("SELECT pg_advisory_unlock(:k1, :k2)"),
                {"k1": _ADV_K1, "k2": _ADV_K2},
            )
    for row in rows:
        mid, tid = row[0], row[1]
        try:
            await deliver_outbound_message(mid, tid)
        except Exception:
            log.exception(
                "outbound_deliver_failed_in_sweep",
                extra={"message_id": str(mid), "tenant_id": str(tid)},
            )


async def outbound_sweep_loop() -> None:
    while True:
        settings = get_settings()
        interval = settings.outbound_sweep_interval_seconds
        if interval <= 0:
            return
        await asyncio.sleep(interval)
        try:
            await run_outbound_sweep_once()
        except Exception:
            log.exception("outbound_sweep_batch_failed")
