"""Execucao preview sandbox (Story 5.2): grafo deterministico sem env Meta/producao.

O walk e BFS com cada no visitado no maximo uma vez: em grafos em diamante (dois
caminhos para o mesmo no), apenas um ramo e percorrido; preview simplificado, nao
equivale a semantica completa de um motor futuro com branching condicional real.

Workers/filas futuros devem exigir explicitamente environment=sandbox antes de
invocar este modulo ou qualquer envio, para evitar bypass acidental da politica HTTP.
"""

from __future__ import annotations

import json
from collections import deque
from typing import Any, Literal


def simulate_sandbox_run(
    definition: dict[str, Any],
    fixture_message: dict[str, Any],
    *,
    correlation_id: str,
    fixture_trace_preview_max: int = 512,
) -> tuple[Literal["succeeded", "failed"], list[str]]:
    """Simula navegacao a partir do trigger; nunca invoca redes externas."""

    trace: list[str] = [
        f"sandbox: correlation_id={correlation_id}",
        "sandbox: execution_mode=sandbox (no production WhatsApp / Meta send)",
    ]
    nodes_raw = definition.get("nodes") or []
    edges_raw = definition.get("edges") or []
    by_id = {str(n["id"]): n for n in nodes_raw if isinstance(n, dict) and "id" in n}
    adj: dict[str, list[str]] = {}
    for e in edges_raw:
        if not isinstance(e, dict):
            continue
        src, tgt = str(e.get("source", "")), str(e.get("target", ""))
        if not src or not tgt:
            continue
        adj.setdefault(src, []).append(tgt)

    triggers = [nid for nid, n in by_id.items() if str(n.get("kind")) == "trigger"]
    if len(triggers) != 1:
        trace.append("sandbox: abort: grafo deve ter um trigger antes do run")
        return "failed", trace

    start = triggers[0]
    q: deque[str] = deque([start])
    visited: list[str] = []
    seen: set[str] = set()

    fx_dump = json.dumps(
        fixture_message,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    cap = max(64, fixture_trace_preview_max)
    if len(fx_dump) > cap:
        fx_dump = (
            fx_dump[:cap]
            + f"...(truncado para log; {len(fx_dump)} chars; fixture completo no "
            "payload da resposta e gravacao opcional)"
        )
    trace.append(
        f"sandbox: fixture_message={fx_dump}",
    )

    while q:
        cur = q.popleft()
        if cur in seen:
            continue
        seen.add(cur)
        visited.append(cur)
        if cur not in by_id:
            trace.append(
                f"sandbox: abort: no {cur!r} ausente na definicao (inconsistente)",
            )
            return "failed", trace
        kind = str(by_id[cur].get("kind", "?"))
        if kind == "trigger":
            trace.append(
                f"sandbox: node {cur} (trigger): matched incoming fixture stub",
            )
        elif kind == "condition":
            trace.append(
                f"sandbox: node {cur} (condition): default branch stub",
            )
        elif kind == "action":
            trace.append(
                f"sandbox: node {cur} (action): local handle (no outbound enqueue)",
            )
        else:
            trace.append(f"sandbox: node {cur} ({kind}): noop stub")
        for nxt in adj.get(cur, ()):
            if nxt not in seen:
                q.append(nxt)

    has_action = any(str(by_id.get(nid, {}).get("kind")) == "action" for nid in visited)
    if has_action:
        trace.append("sandbox: run completed successfully (sandbox scope)")
        return "succeeded", trace

    trace.append("sandbox: no action node exercised; marking failed preview")
    return "failed", trace
