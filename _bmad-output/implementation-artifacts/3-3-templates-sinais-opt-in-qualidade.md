---
story_key: 3-3-templates-sinais-opt-in-qualidade
epic: epic-3
status: done
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 3-2-enviar-mensagem-saida-fila-retry
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 3.3 - Templates e sinais de opt-in e qualidade

## Story

**Como** admin do tenant,  
**quero** **acompanhar** o ciclo de templates e **sinais** de opt-in, quality rating e limites relevantes,  
**para** operar dentro das politicas Meta (FR15, FR16).

## Acceptance Criteria

1. **Dado** integracao com API Meta, **quando** o admin ve a lista de templates e status, **entao** estados minimos (rascunho, submetido, aprovado, pausado) estao mapeados e justificam acoes (ex.: pausa por baixa qualidade) ao nivel alcancavel pelo piloto.
2. Dashboard de sinais **nao** e vanity: liga a incidentes / volume quando dados existem (cruzamento minimo FR21).
3. API expoe listagem (e sincronizacao se aplicavel) alinhada ao CDA; OpenAPI atualizado.

**Requisitos:** FR15, FR16, FR21 (cruzamento minimo).

## Tasks / Subtasks

- [x] `GET /v1/me/message-templates` (ou path CDA) com sync/cache conforme desenho.
- [x] Mapear estados Meta para modelo interno; refresh documentado.
- [x] Admin-web: vista de templates e sinais (se UI nesta story); skeleton + erros honestos (UX-DR4).
- [x] Testes; ATDD `test_epic3_story33_templates_signals_atdd.py`.

### Review Findings

#### 2026-04-28 ? Code review (BMAD adversarial + Party Mode)

**Resolvido em 2026-04-28:**

- [x] [Review][Patch] **Refresh vs falha Graph** ? `fetch_message_templates` devolve `(lista, ok)`; `ok=False` nao apaga cache; `tpl_ok` gate no handler + log `template_refresh_skipped_fetch_failed`.
- [x] [Review][Decision] **Varias linhas / ambiente** ? 409 quando `len(candidates) > 1`; query `waba_id` + `phone_number_id`; teste integracao.
- [x] [Review][Patch] **UNKNOWN / codigo Meta novo** ? `map_template_record`: `submitted` + detalhe; testes `test_templates_meta.py`.
- [x] [Review][Defer] **Paging Graph** ? mantido em `deferred-work.md`; OpenAPI `summary`/`description` mencionam primeira pagina.

- [x] [Review][Dismiss] RLS + tenant_id.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Cache vs source of truth Meta; invalidacao e limites de rate. |
| **Mary** | FR15/FR16; anti-vanity explicito no AC. |
| **John** | Operadores precisam ver porque template esta pausado. |
| **Sally** | Estados claros; sem metricas que parecam sucesso quando ha bloqueio Meta. |
| **Amelia** | Testes com stub Graph; tenant isolado. |

## Advanced Elicitation (CS)

- **Pre-mortem:** lista stale apos mudanca Meta - TTL ou botao sync + feedback.
- **Red team:** enumeracao de nomes de template entre tenants - sempre com `tenant_id`.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Estados minimos do AC refletidos no modelo ou documentados como fase 2. |
| **Amelia** | ATDD exige GET 200 em `/v1/me/message-templates` com headers dev. |
| **Mary** | Ligacao a FR21 documentada quando dados de canal existirem. |

### Advanced Elicitation (VS)

- **Pre-mortem:** piloto sem quality rating API - fallback honesto na UI ("dados indisponiveis").

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| RLS | Templates e sinais sempre escopados ao tenant. |
| UX | UX-DR4; sem charts vazios apresentados como sucesso. |

## Dev Notes - requisitos tecnicos

- Depende de **3.2** para coerencia de envio e credenciais de canal.
- Opcional: Vitest ATDD para pagina admin de templates (separado deste gate API).

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic3_story33_templates_signals_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 3.3

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent).

### Completion Notes List

- Migração `014` com `whatsapp_message_templates`, `whatsapp_channel_snapshots`, RLS e grants.
- `GET /v1/me/message-templates`: cache, `?refresh=true` (org_admin); `(templates, fetch_ok)` evita wipe em falha Graph; 409 multi-linha; queries `waba_id`, `phone_number_id`.
- `map_template_record`: status Meta desconhecido ? `submitted` + `status_detail`.
- Após refresh com sucesso: `await session.flush()` ( `autoflush=False` em `tenant_session`).
- Integração: fixture limpa cache; testes refresh-fail + multi-linha; `test_templates_meta.py` (unit).

### File List

- `v2/apps/api/alembic/versions/014_whatsapp_message_templates.py`
- `v2/apps/api/app/db/models_message_templates.py`
- `v2/apps/api/app/whatsapp/templates_meta.py`
- `v2/apps/api/app/api/routes/me_message_templates.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/tests/integration/test_story33_message_templates.py`
- `v2/apps/api/tests/atdd/test_epic3_story33_templates_signals_atdd.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/api/tests/test_templates_meta.py`
- `v2/apps/admin-web/src/features/templates/MessageTemplatesPage.tsx` (+ rota/nav em `App.tsx`)
- `v2/apps/admin-web/src/atdd/epic3-story33-templates-page.atdd.test.tsx`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic3_story33_templates_signals_atdd.py`.
- 2026-04-28: **[DS]** implementação API + admin-web + testes; CI verde.
- 2026-04-28: **Pos-review:** `fetch_ok`, 409 multi-linha, map UNKNOWN?submitted; `status: done`.
