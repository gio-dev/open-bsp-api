---
story_key: 4-4-sinais-atraso-falha-health
epic: epic-4
status: done
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 4-1-inbox-split-lista-thread
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 4.4 - Sinais de atraso, falha e health

## Story

**Como** operador,  
**quero** **ver** atraso / **falha** do canal **so** do meu tenant (e acoes minimas),  
**para** confianca operacional (FR21) sem ruido cross-tenant.

## Acceptance Criteria

1. **Dado** incidente ou atraso no pipeline, **quando** abro a inbox, **entao** banner ou badge **honesto** (nao "tudo verde") com next step; **distingue** Meta vs plataforma quando taxonomia existir (preparacao FR51).
2. Dados agregados **somente** para o tenant autenticado (NFR-OPS-05 alinhado).
3. API de sinais (ex. `GET /v1/me/channel-health`) alimenta UI; OpenAPI atualizado.

**Requisitos:** FR21, FR51 (telemetria UI minima). **NFRs:** NFR-OPS-05.

## Tasks / Subtasks

- [x] Fonte de verdade: filas atrasadas, falhas Meta, erros plataforma - modelo minimo.
- [x] Endpoint tenant-scoped; sem vazar estado de outros tenants.
- [x] Admin-web: banner/badge na shell da inbox; copy honesta (UX-DR4).
- [x] Testes; ATDD `test_epic4_story44_channel_health_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Taxonomia culpa Meta vs plataforma extensivel; MVP pode ser campo unico `source`. |
| **Mary** | FR21 + preparacao FR51; anti "vanity green". |
| **John** | Reduz chamadas a suporte por falta de visibilidade. |
| **Sally** | Next step acionavel (link runbook ou estado). |
| **Amelia** | Cache curto + stale time; nao bloquear render da inbox. |

## Advanced Elicitation (CS)

- **Pre-mortem:** alerta falso positivo constante - thresholds configuraveis por tenant (fase 2).
- **Red team:** health endpoint como oraculo de existencia de tenants - 403/404 opacos.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | NFR-OPS-05 - latencia e disponibilidade do endpoint documentadas. |
| **Amelia** | ATDD: GET channel-health 200. |
| **Mary** | Distincao Meta/plataforma opcional no MVP mas campo reservado no contrato. |

### Advanced Elicitation (VS)

- **Pre-mortem:** sem incidentes - payload `ok: true` honesto vs omitir banner.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | Escopo tenant estrito. |
| UX | UX-DR4; nao esconder falha grave. |

## Dev Notes - requisitos tecnicos

- Depende de **4.1** para surfacing na inbox; pode consumir metricas de **3.2** / filas.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic4_story44_channel_health_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 4.4

## Dev Agent Record

### Agent Model Used

Composer (DS Story 4.4)

### Completion Notes List

- Agregacao `GET /v1/me/channel-health`: contagens outbound (failed meta vs plataforma, rate_limited, queued antigo >15 min) + handoffs `failed`; sinais com `source`, `severity`, `next_step`; `healthy` so true sem incidentes; RLS via `tenant_session`; `Cache-Control: private, max-age=15`.
- Admin-web: query TanStack `staleTime` 15s; banner + badge apenas quando `healthy === false` e `incidents.length > 0` (nao bloqueia inbox se payload incompleto).
- OpenAPI: gate `test_me_channel_health_get_documents_errors` (401/403/503).
- Testes: `tests/test_channel_health_signals.py` (unidade `_build_signals`); `tests/integration/test_story44_channel_health.py`; ATDD admin `epic4-story44-channel-health.atdd.test.tsx`.
- CI: `pytest -m 'not atdd'` + `pytest -m 'atdd and epic4_atdd'` verdes. Suite completa `pytest` inclui ATDD RED de epicos 5-10 (404 esperado ate DS).

### File List

- `v2/apps/api/app/services/__init__.py`
- `v2/apps/api/app/services/channel_health.py`
- `v2/apps/api/app/api/routes/me_channel_health.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/tests/test_channel_health_signals.py`
- `v2/apps/api/tests/integration/test_story44_channel_health.py`
- `v2/apps/api/tests/atdd/test_epic4_story44_channel_health_atdd.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/admin-web/src/features/inbox/InboxPage.tsx`
- `v2/apps/admin-web/src/atdd/epic4-story44-channel-health.atdd.test.tsx`
- `_bmad-output/implementation-artifacts/4-4-sinais-atraso-falha-health.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic4_story44_channel_health_atdd.py`.
- 2026-04-29: **[DS]** implementacao 4.4 API + admin-web + testes + sprint review.
- 2026-04-29: **[DONE]** `status: done`; sprint `4-4-sinais-atraso-falha-health` fechada após CI (`api-ci`, `admin-web-ci`) e CR.
