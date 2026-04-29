---
story_key: 5-1-editor-fluxos-validacao
epic: epic-5
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

# Story 5.1 - Editor de fluxos e validacao

## Story

**Como** operador,  
**quero** **criar/editar** fluxos por **regras** (sem LLM) com **validacao** antes de testar,  
**para** FR22 com erros acionaveis (campo, linha) (UX-DR10).

## Acceptance Criteria

1. **Dado** um fluxo em draft, **quando** gravo ou valido, **entao** validacao **bloqueia** publish de draft invalido com mensagem **por campo/linha**; **nao** mostrar stack do servidor ao operador (UX-DR4).
2. Modelo de fluxo (nos, arestas, gatilho/condicao/acao) persistido com `tenant_id`.
3. API de validacao documentada (ex. `POST /v1/me/flows/validate`); OpenAPI atualizado.

**Requisitos:** FR22, UX-DR10.

## Tasks / Subtasks

- [x] Schema de fluxo + migracao; CRUD minimo de drafts.
- [x] Validador servidor-side com erros estruturados (path + mensagem).
- [x] Admin-web: editor UX-DR10; erros inline.
- [x] Testes; ATDD `test_epic5_story51_flow_editor_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Contrato de erro de validacao estavel (nao misturar com 422 generico sem detalhe). |
| **Mary** | FR22 explicito; sem LLM no core desta story. |
| **John** | Base do construtor de produto. |
| **Sally** | Mensagens por campo; sem jargao de stack (UX-DR4). |
| **Amelia** | Limite de tamanho de grafo; timeout de validacao. |

## Advanced Elicitation (CS)

- **Pre-mortem:** fluxo ciclico - validador deteta ciclos ou ADR permite com limite de passos.
- **Red team:** YAML import de fluxo - sanitizar se existir import.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Validacao obrigatoria antes de sandbox/publish nas stories seguintes. |
| **Amelia** | ATDD: POST validate retorna 200 ou 422 com payload util. |
| **Mary** | Bloqueio de publish invalido testado em integracao. |

### Advanced Elicitation (VS)

- **Socratic:** o que e "linha" sem editor visual? - indice de no ou id no contrato.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| RLS | Fluxos so no tenant. |
| UX | UX-DR10 + UX-DR4. |

## Dev Notes - requisitos tecnicos

- Depende de **4.1** para contexto de inbox na UX (lista|thread); API pode existir antes da UI completa.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic5_story51_flow_editor_atdd.py`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-5.md`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 5.1

## Dev Agent Record

### Agent Model Used

Composer (DS Story 5.1)

### Completion Notes List

- Tabela `tenant_flow_drafts` (018) + modelo `TenantFlowDraft` com JSONB `definition` `{"nodes":[],"edges":[]}`, RLS por `tenant_id`.
- RBAC `FLOW_EDITOR_ROLES` (`org_admin`, `operator`); deps `console_flow_editor_context`.
- Validador `app/services/flow_validation.py`: Pydantic + regras (1 trigger, DAG sem ciclos, nos alcancaveis, max 200 nos, pelo menos uma action alcancavel); `POST /v1/me/flows/validate` -> 200 `valid:true` ou 422 canonico `errors[]` com `field` path-style.
- CRUD `GET/POST /v1/me/flows`, `GET/PATCH /v1/me/flows/{flow_id}` com `valid` calculado na resposta; create 201.
- OpenAPI gate (policy) para validate + drafts paths.
- Admin: `FlowEditorPage` (`/flows/editor`) ? JSON do grafo, Validar / Gravar; erros por campo via `parseCanonicalValidationBody`.
- Correcao Pydantic v2: `ValidationError` import de `pydantic` (nao `pydantic.errors`).

### File List

- `v2/apps/api/alembic/versions/018_tenant_flow_drafts.py`
- `v2/apps/api/app/db/models_flows.py`
- `v2/apps/api/app/services/flow_validation.py`
- `v2/apps/api/app/api/routes/me_flows.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/app/tenancy/rbac.py`
- `v2/apps/api/app/tenancy/deps.py`
- `v2/apps/api/pyproject.toml`
- `v2/apps/api/tests/test_flow_validation.py`
- `v2/apps/api/tests/test_story51_flow_validate_http.py`
- `v2/apps/api/tests/integration/test_story51_flows.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/api/tests/atdd/test_epic5_story51_flow_editor_atdd.py`
- `v2/apps/admin-web/src/features/flows/FlowEditorPage.tsx`
- `v2/apps/admin-web/src/lib/canonicalApiError.ts`
- `v2/apps/admin-web/src/App.tsx`
- `v2/apps/admin-web/src/atdd/epic5-story51-flow-editor.atdd.test.tsx`
- `_bmad-output/implementation-artifacts/5-1-editor-fluxos-validacao.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic5_story51_flow_editor_atdd.py`.
- 2026-04-29: **[DS]** migracao 018, API flows + validate, admin FlowEditorPage, testes (unidade, HTTP, policy, ATDD epic5, integracao CI).
- 2026-04-29: **[CR]** Party Mode: validacao em POST/PATCH, 503 anonimo, nos `extra=forbid`, erros por `nodes.{id}`, OpenAPI examples, testes 401/403/integracao; UI banners + `aria-live` + tratamento canonico de erro.
- 2026-04-29: **[DONE]** `status: done`; sprint `5-1-editor-fluxos-validacao` fechada.
