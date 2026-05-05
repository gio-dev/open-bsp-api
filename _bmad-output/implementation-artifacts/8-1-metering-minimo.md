---
story_key: 8-1-metering-minimo
epic: epic-8
status: done
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 3-2-enviar-mensagem-saida-fila-retry
code_location: v2/apps/api, v2/apps/admin-web
---

# Story Metering minimo

## Story (resumo)

Contexto completo em `epics.md`. **Foco DS:** Fair use e billing preparacao.

**Requisitos:** FR41; NFR-FAIR-03

## Acceptance Criteria (testaveis)

- Eventos agregados por tenant; contrato de operacoes-chave.
- GET /v1/me/usage/summary.

## Tasks / Subtasks

- [x] Modelo + Alembic com `tenant_id` e RLS onde houver dados.
- [x] API `/v1/...` + OpenAPI; erros canonicos (story 1.1).
- [x] Admin-web quando houver UI (Chakra, UX-DR): N/A (API + persistencia).
- [x] pytest integracao; ATDD em `v2/apps/api/tests/atdd/test_epic8_story81_metering_atdd.py`

## Implemented (DS 2026-05)

- Migracao **026** `tenant_metering_daily`; RLS + `app_runtime`; upsert concorrente via SQL.
- Metricas MVP: `inbound_messages` (primeiro enqueue de mensagem Meta), `outbound_messages_accepted` (Graph aceite na fila).
- `GET /v1/me/usage/summary` (org_admin); query `since`/`until` (UTC date); janela predefinida 30 dias; max 366 dias.

## Party Mode (CS)

| Agente | Insight |
|--------|---------|
| **Winston** | OpenAPI e RLS; sem segunda forma de erro JSON. |
| **Mary** | Rastrear FR/NFR citados; dependencias no frontmatter. |
| **John** | Ordenar DS; flags se epico predecessor incompleto. |
| **Sally** | UX-DR4; sem stack ao operador. |
| **Amelia** | Docker CI; marcar `@pytest.mark.atdd`. |

## Advanced Elicitation (CS)

- **Pre-mortem:** dados de outro tenant visiveis - testes negativos RLS.
- **Red team:** segredos ou PII em audit/logs - mascarar e politica de retencao.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS** (batch epicos 7-10 / F2 / F3; rever pos-detalhe DS).

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Paths e contratos alinhados ao CDA. |
| **Amelia** | ATDD RED ligado ao ficheiro indicado. |
| **Mary** | AC cobrem FR citados. |

### Checklist BMad (sintese)

| Categoria | OK |
|-----------|-----|
| Regressao | Contrato erro 1.1 |
| RLS | `tenant_id` |
| Seguranca | RBAC em rotas sensiveis |

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic8_story81_metering_atdd.py` (`epic8_atdd`).
- Integracao (RLS + 403): `v2/apps/api/tests/integration/test_story81_usage_metering.py`.
- Policy: `v2/apps/api/tests/policy/test_openapi_gate.py` (incl. `usage/summary` em `info.description`).

## Dev Agent Record (pos-CR Party Mode)

- Resposta JSON com schema fechado (`ConfigDict(extra="forbid")` em `UsageMetricTotal` / `UsageSummaryResponse`).
- `info.description` global referencia `GET /v1/me/usage/summary` (FR41); tag OpenAPI `usage` verificada no ATDD.
- ATDD reforcado: chaves do corpo, metricas conhecidas, path OpenAPI, `403` para `operator`, `400` para intervalo invalido.
- Integracao: agregados nao cruzam tenant; `operator` nao le resumo.

## References

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/project-context.md`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-8.md`

## Change Log

- 2026-05-08: **CR Party Mode** fechado: ATDD + integracao RLS/RBAC, schema fechado, gate OpenAPI `usage/summary`; **done**.
- 2026-05-06: **[DS]** migracao 026, incrementos ingestao outbound, `GET .../usage/summary`, gate OpenAPI, `epic8_atdd`.
- 2026-04-24: **[CS+VS+AT]** materializado no fluxo por story (epicos 7-10 / F2 / F3).
