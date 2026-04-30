---
story_key: 5-4-versao-audit-materialidade
epic: epic-5
status: review
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 5-3-publish-permissao-ambiente
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 5.4 - Versao e audit de materialidade

## Story

**Como** auditor ou admin,  
**quero** **historico** de versoes (ou diff minimo) de alteracoes **materiais**,  
**para** FR25 (compliance e debug).

## Acceptance Criteria

1. **Dado** publish ocorre, **entao** registo **append** com identidade e timestamp; rollback one-click **fora** de escopo salvo flag de produto; diff visual TBD.
2. Listagem de versoes por fluxo ordenada e paginada.
3. API (ex. `GET /v1/me/flows/{id}/versions`) documentada.

**Requisitos:** FR25.

## Tasks / Subtasks

- [x] Tabela de versoes imutavel; referencia a snapshot JSON ou hash.
- [x] Endpoint listagem; detalhe opcional por version id.
- [x] Admin-web: timeline simples; export opcional (fora MVP / fase 2).
- [x] Testes; ATDD `test_epic5_story54_versions_audit_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Append-only: sem UPDATE de linhas historicas; correcoes = nova versao. |
| **Mary** | FR25; ligacao a narrativa de compliance PRD. |
| **John** | Suporte a investigacao pos-incidente. |
| **Sally** | Datas e autor visiveis sem poluir inbox. |
| **Amelia** | Retencao de versoes - politica por tenant (fase 2). |

## Advanced Elicitation (CS)

- **Pre-mortem:** historico cresce sem limite - paginacao e arquivo.
- **Red team:** versao com dados sensiveis - mascarar em GET se necessario.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Cada publish 5.3 cria linha de versao obrigatoriamente. |
| **Amelia** | ATDD: GET versions 200 com lista (pode vazia so com seed). |
| **Mary** | Identidade do autor = user id interno; GDPR em exports. |

### Advanced Elicitation (VS)

- **Pre-mortem:** migracao corrompe historico - backup antes de alterar schema de fluxo.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Auditoria | Append-only; relogio confiavel (UTC). |
| RLS | Versoes so do tenant do fluxo. |

## Dev Notes - requisitos tecnicos

- Depende de **5.3** para eventos de publish.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic5_story54_versions_audit_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 5.4

## Dev Agent Record

### Agent Model Used

Cursor agent (DS), 2026-04-30.

### Completion Notes List

- Migracao **`021`**: `tenant_flow_publish_versions` append-only (`GRANT SELECT, INSERT` apenas a `app_runtime`), RLS, FK para activacao (SET NULL) e draft (CASCADE).
- Cada **publish material** (nao-idempotente na 5.3) insere uma linha de versao com snapshot JSON, fingerprint SHA-256, `published_at`, `published_by_user_id`, `publish_activation_id`.
- **GET** `/v1/me/flows/{flow_id}/versions` ? ordenado por `published_at` DESC, `limit`/`offset`, filtro opcional `environment`; **GET** `.../versions/{version_id}` ? detalhe com `definition`; identidade `flow_id` alinhada ao publish (UUID de draft ou `atdd-flow`).
- Leitura de versoes: `console_tenant_user_context` (qualquer papel tenant autenticado), para auditoria alinhado a FR25.
- **Correccao menor**: `config.py` ? docstring ASCII (`Emergencia`) para UTF-8 valido sob ruff.
- **CI**: `docker compose --profile ci` em `api-ci` e `admin-web-ci` passou apos `ruff format` nos ficheiros tocados.

### File List

- `v2/apps/api/alembic/versions/021_tenant_flow_publish_versions.py`
- `v2/apps/api/app/db/models_flows.py` (`TenantFlowPublishVersion`)
- `v2/apps/api/app/api/routes/me_flows.py` (publish + GET list/detail)
- `v2/apps/api/app/core/config.py` (UTF-8 / docstring)
- `v2/apps/api/app/main.py` (tag OpenAPI flows)
- `v2/apps/api/tests/integration/test_story54_flow_versions.py`
- `v2/apps/api/tests/integration/test_story53_flow_publish.py` (versoes + idempotencia)
- `v2/apps/api/tests/test_story54_versions_http.py`
- `v2/apps/api/tests/atdd/test_epic5_story54_versions_audit_atdd.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/api/pyproject.toml` (ruff `I001` em `tests/test_story54_versions_http.py`)
- `v2/apps/admin-web/src/features/flows/FlowEditorPage.tsx`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic5_story54_versions_audit_atdd.py`.
- 2026-04-30: **[DS]** implementacao 5.4 + estado **review** no sprint/handoff.
