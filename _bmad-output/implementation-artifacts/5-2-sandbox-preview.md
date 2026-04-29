---
story_key: 5-2-sandbox-preview
epic: epic-5
status: review
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 5-1-editor-fluxos-validacao
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 5.2 - Sandbox e preview

## Story

**Como** operador,  
**quero** **testar** o fluxo em **sandbox** (preview) antes de publish,  
**para** FR23.

## Acceptance Criteria

1. **Dado** fluxo validado, **quando** executo teste em sandbox com fixture (mensagem, contacto stub se necessario), **entao** resultado (sucesso, falha, log minimo) fica **traceavel** e **nao** envia a **producao** (FR4).
2. Drawer de sandbox segue direcao lista|thread + lente (UX-DR1).
3. API sandbox (ex. `POST /v1/me/flows/{id}/sandbox-run`) documentada; flag ambiente **nao-prod** obrigatoria no motor de execucao.

**Requisitos:** FR23, FR38 (preparar sandbox tenant-scoped quando existir sandbox global).

## Tasks / Subtasks

- [x] Runtime sandbox isolado (fila/worker ou modo sync dev-only documentado).
- [x] Fixture de mensagem; correlacao de run id para UI.
- [x] Admin-web: drawer preview; nao chamar endpoints de envio prod.
- [x] Testes; ATDD `test_epic5_story52_sandbox_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Barreira tecnica: credenciais Meta de sandbox vs prod separadas. |
| **Mary** | FR23 + FR4; traceabilidade explicita no AC. |
| **John** | Reduz risco de publish quebrar clientes. |
| **Sally** | UX-DR1: drawer coerente com inbox. |
| **Amelia** | Logs de sandbox rotulados; metricas separadas. |

## Advanced Elicitation (CS)

- **Pre-mortem:** sandbox dispara efeito real por bug - dupla checagem `environment=sandbox` no worker.
- **Red team:** utilizador forca header prod num run sandbox - servidor ignora cliente para side-effects.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | 5.1 valido obrigatorio antes de sandbox (ou 422 claro). |
| **Amelia** | ATDD: POST sandbox-run 200/202. |
| **Mary** | Evidencia de nao-producao testavel (mock Meta ou bucket isolado). |

### Advanced Elicitation (VS)

- **Pre-mortem:** timeout longo no sandbox - UX de cancelacao.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | Sem vazamento de dados prod para logs sandbox. |
| RLS | Runs escopados ao tenant. |

## Dev Notes - requisitos tecnicos

- Depende de **5.1**.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic5_story52_sandbox_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 5.2

## Dev Agent Record

### Agent Model Used

Composer (DS Story 5.2)

### Completion Notes List

- `POST /v1/me/flows/{flow_id}/sandbox-run?environment=sandbox` (`console_flow_editor_context`): recusa `environment!=sandbox` com 422; grafico obrigatorio valido ( mesmo validador 5.1).
- Sintese sync `simulate_sandbox_run` ? so logs locais (sem outbound/Meta).
- Persistencia opcional quando `DATABASE_URL`: tabela `tenant_flow_sandbox_runs` (019) com `trace`, `correlation_id`, `fixture`; RLS tenant.
- Chave literal `atdd-flow`: apenas com `AUTH_DEV_STUB` ou `ALLOW_ATDD_SANDBOX_FLOW_KEY` (Settings); caso contrario 422 em `flow_id`.
- Resposta inclui `persisted` (gravacao opcional pode falhar sem bloquear trace) e `fixture_fingerprint` (SHA-256 16 hex do fixture); linha correspondente no trace.
- Simulador: doc BFS/diamante; fixture completo no trace ate 8k chars.
- Admin: `SandboxFlowDrawer` na inbox (visivel apenas com ambiente sandbox), Drawer Chakra lado lista; chama apenas sandbox-run (sem `/messages/send`).
- Marker pytest `epic5_atdd` em `test_epic5_story52_sandbox_atdd.py`.

### File List

- `v2/apps/api/alembic/versions/019_tenant_flow_sandbox_runs.py`
- `v2/apps/api/app/db/models_flows.py`
- `v2/apps/api/app/services/flow_sandbox.py`
- `v2/apps/api/app/api/routes/me_flows.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/app/core/config.py`
- `v2/apps/api/tests/test_flow_sandbox.py`
- `v2/apps/api/tests/test_story52_sandbox_http.py`
- `v2/apps/api/tests/integration/test_story52_sandbox_run.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/api/tests/atdd/test_epic5_story52_sandbox_atdd.py`
- `v2/apps/admin-web/src/features/inbox/SandboxFlowDrawer.tsx`
- `v2/apps/admin-web/src/features/inbox/InboxPage.tsx`
- `v2/apps/admin-web/src/atdd/epic5-story52-sandbox-drawer.atdd.test.tsx`
- `_bmad-output/implementation-artifacts/5-2-sandbox-preview.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic5_story52_sandbox_atdd.py`.
- 2026-04-29: **[DS]** API sandbox-run sync, migracao 019, drawer inbox, testes ATDD/policy/unidade.
- 2026-04-29: **[CR]** Party Mode: `atdd-flow` so com stub/`ALLOW_ATDD_SANDBOX_FLOW_KEY`; resposta `persisted` + `fixture_fingerprint` + trace; persist falha devolve trace (log); BFS/documentacao dedal; testes HTTP environment/401/403/OpenAPI 200; integracao gravacao DB; ATDD so 200; admin drawer UX+a11y+erros categorizados.
