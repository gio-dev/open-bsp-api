---
story_key: 7-2-lifecycle-deprecation-policy
epic: epic-7
status: done
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 7-1-rest-versioned-idempotency
code_location: v2/apps/api, v2/apps/admin-web
---

# Story Lifecycle e deprecation policy publica

## Story (resumo)

Contexto completo em `epics.md`. **Foco DS:** Comunicacao sem surpresa a integradores.

**Requisitos:** FR37

## Acceptance Criteria (testaveis)

- Datas e janela em /v1/policy/deprecation, headers Deprecation, ou docs estaticos.
- CHANGELOG e versao API alinhados.

## Tasks / Subtasks

- [x] **N/A (fora de escopo DS)** ? Modelo + Alembic com `tenant_id` e RLS: esta historia nao persiste politica em tabela; `GET /v1/policy/deprecation` e estatico por versao. RLS mantem-se para dados de dominio existentes.
- [x] API `GET /v1/policy/deprecation` (publico JSON) + OpenAPI; texto em pt-BR; `info.description` menciona deprecacao e CHANGELOG.
- [x] **N/A (fora de escopo DS)** ? Admin-web: nao ha UI obrigatoria neste slice; integradores consomem endpoint + OpenAPI/CHANGELOG. UI dedicada fica para historia ou epicos de consola.
- [x] Policy gate + ATDD (`test_policy_deprecation_body_aligns_openapi_version`; `test_epic7_story72_deprecation_policy_atdd.py`; `pytestmark epic7_atdd`).
- [x] `app/core/publication.py` + `FastAPI(version=...)`: versao instalada igual a `openapi.json`/`pyproject`/CHANGELOG da API.

### Ficheiros tocados (DS)

- `v2/apps/api/app/api/routes/policy_deprecation.py`
- `v2/apps/api/app/core/publication.py`
- `v2/apps/api/app/main.py` (router policy, tag OpenAPI `policy`, descricao PT, `version` dinamica)
- `v2/apps/api/app/services/flow_engine.py` (**bundle DS:** coercao do snapshot antes do BFS; regressao `preference_kind`; nao faz parte do AC FR37 mas foi entregue no mesmo merge DS)
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/api/tests/atdd/test_epic7_story72_deprecation_policy_atdd.py`
- `v2/apps/api/CHANGELOG.md`

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

- `v2/apps/api/tests/atdd/test_epic7_story72_deprecation_policy_atdd.py`
- Policy: `tests/policy/test_openapi_gate.py` (`test_openapi_info_and_public_paths`, `test_policy_deprecation_body_aligns_openapi_version`).

## Dev Agent Record

### Checklist release ? primeira rota deprecated (futuro)

1. Acrescentar entrada em `deprecation_entries` (datas ISO8601, `replacement_hint`).
2. Documentar no `CHANGELOG.md` da API; alinhar bump de versao em `pyproject.toml`.
3. Opcional: emitir `Deprecation: true`, `Sunset`, `Link` nas respostas da rota afetada (RFC 9745 / convencoes internas).
4. Correr `api-ci` (policy + ATDD epic7).

### Completion notes (pos-CR Party Mode)

- Modelos `DeprecationEntry` e `DeprecationPolicyResponse` com `extra=forbid` (contrato fechado).
- Story e sprint em **done** depois de CR.

## References

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/project-context.md`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-7.md`

## Change Log

- 2026-04-24: **[CS+VS+AT]** materializado no fluxo por story (epicos 7-10 / F2 / F3).
- 2026-05-05: **DS** endpoint publico de politica FR37 + `CHANGELOG.md`; `info.version` lido do pacote; motor de fluxo revalida grafo antes de correr (`coerce_flow_definition`).
- 2026-05-06: estado **`review`** no fluxo (nao `done` ate code review); linhas de checklist **N/A** explicitas (template vs escopo DS).
- 2026-05-07: **CR Party Mode** fechado; `extra=forbid` nos modelos; checklist release + nota bundle `flow_engine`; **done**.
