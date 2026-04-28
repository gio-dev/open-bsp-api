---
story_key: 4-3-handoff-contexto-minimo
epic: epic-4
status: review
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 4-1-inbox-split-lista-thread
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 4.3 - Handoff e contexto minimo

## Story

**Como** operador,  
**quero** **passar** de automacao **para humano** (e vice-versa) com **resumo** minimo e **fila/roteamento** quando a automacao gera handoff,  
**para** evitar o consumidor a repetir tudo (FR19, FR20).

## Acceptance Criteria

1. **Dado** regra a emitir handoff, **quando** o operador assume, **entao** ve **intencao**, **ultima saida do bot** e **estado** (aceite / queued / falhou) - nunca silencio se o pipeline falhou (UX-DR4).
2. Supervisao pode ajustar **fila/roteamento** conforme regras do tenant (FR20).
3. API expoe estado de handoff por conversa (ex. `GET .../handoff`) ou campo embutido coerente no CDA.

**Requisitos:** FR19, FR20.

## Tasks / Subtasks

- [x] Modelo handoff (`inbox_conversation_handoffs`: resumo, ultima saida bot, estado, fila, claimed_by).
- [x] `GET` + `PATCH` handoff; fila apenas `org_admin`; assumir (`accept`) com `INBOX_TAG_ROLES` + `X-Dev-User-Id`; 409 se ja aceite por outro operador.
- [x] Contrato interno `app/inbox/handoff_sync.py` (`upsert_handoff_from_engine`) para Epic 5.5.
- [x] Admin-web: painel handoff na thread; estado `failed` com copy honesta; fila editavel (API aplica RBAC).
- [x] Testes integracao, ATDD API, OpenAPI gate, Vitest painel.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Handoff nao duplica historico completo - resumo e ponteiros. |
| **Mary** | FR19/FR20; PRD Marina como referencia narrativa. |
| **John** | Diferencia produto de inbox "cega". |
| **Sally** | Falha de pipeline visivel - copy clara (UX-DR4). |
| **Amelia** | Integracao com filas - idempotencia em "assumir conversa". |

## Advanced Elicitation (CS)

- **Pre-mortem:** dois operadores assumem simultaneamente - locking ou "already claimed".
- **Red team:** resumo com PII excessivo - minimizar no payload operador.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Ligacao ao motor 5.x documentada (evento ou polling). |
| **Amelia** | ATDD: GET handoff 200 com fixture. |
| **Mary** | FR20 - API de ajuste de fila ou mesmo recurso PATCH documentado. |

### Advanced Elicitation (VS)

- **Pre-mortem:** handoff sem conversa - 404 coerente.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| RLS | Handoff so no tenant da conversa. |
| UX | Sem stack trace ao operador. |

## Dev Notes - requisitos tecnicos

- Depende de **4.1**; integracao forte com **5.5** (engine) em fases posteriores.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic4_story43_handoff_atdd.py`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-4.md`
- Vitest: `v2/apps/admin-web/src/atdd/epic4-story43-inbox-handoff.atdd.test.tsx`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 4.3

## Dev Agent Record

### Agent Model Used

Composer (DS Story 4.3)

### Completion Notes List

- Estados: `automated`, `pending_handoff`, `queued`, `accepted`, `failed` (CHECK no Postgres).
- `GET` sem linha devolve defaults (`automated`, campos vazios).
- Supervisao = `org_admin` para `queue_id` (inclui `null` para limpar).

### File List

- `v2/apps/api/alembic/versions/017_inbox_handoff.py`
- `v2/apps/api/app/db/models_inbox.py`
- `v2/apps/api/app/api/routes/me_inbox_handoff.py`
- `v2/apps/api/app/inbox/handoff_sync.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/app/ci_seed.py`
- `v2/apps/api/tests/integration/test_story43_handoff.py`
- `v2/apps/api/tests/atdd/test_epic4_story43_handoff_atdd.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/admin-web/src/features/inbox/InboxPage.tsx`
- `v2/apps/admin-web/src/atdd/epic4-story42-inbox-tags.atdd.test.tsx`
- `v2/apps/admin-web/src/atdd/epic4-story43-inbox-handoff.atdd.test.tsx`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic4_story43_handoff_atdd.py`.
- 2026-04-28: **[DS]** implementacao; status `review`.
