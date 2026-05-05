---
story_key: 7-1-rest-versioned-idempotency
epic: epic-7
status: done
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 2-3-chaves-api-emissao-revogacao
code_location: v2/apps/api, v2/apps/admin-web
---

# Story REST versionado e idempotencia

## Story (resumo)

Contexto completo em `epics.md`. **Foco DS:** Contrato integrador; headers e JSON de erro com correlation.

**Requisitos:** FR35, FR36, FR40; NFR-INT-01, NFR-SEC-05

## Acceptance Criteria (testaveis)

- OpenAPI /v1; mutacoes com Idempotency-Key; 401/429 com Retry-After documentados.
- Duplicados sem efeito indevido (politica 200/409 consistente).

## Tasks / Subtasks

- [x] Modelo + idempotencia: unicidade `(tenant_id, idempotency_key)` em `outbound_whatsapp_messages` + sessao tenant (RLS); sem migracao dedicada 7.1.
- [x] API `/v1/...` + OpenAPI; erros canonicos (story 1.1); `Retry-After` em 429/503 para `POST /v1/me/messages/send`; `FR36` em `FastAPI(description=...)`.
- [x] Admin-web: **N/A** nesta historia (sem UI obrigatoria).
- [x] ATDD/policy: `tests/atdd/test_epic7_story71_rest_idempotency_atdd.py` (OpenAPI + smoke duplicado com DB), `tests/policy/test_openapi_gate.py` (`messages/send`).

### Ficheiros tocados (DS)

- `v2/apps/api/app/api/routes/me_messages.py` ? `_MSG_RESPONSES` (429/503 + Retry-After), OpenAPI for `Idempotency-Key` and idempotency text.
- `v2/apps/api/app/main.py` ? global `description` (FR35/FR36); `messages` tag (7.1).
- `v2/apps/api/tests/policy/test_openapi_gate.py` ? gate for `messages/send` (202, 429, Retry-After, Idempotency-Key; `info.description` mentions `/v1`).
- `v2/apps/api/tests/atdd/test_epic7_story71_rest_idempotency_atdd.py` ? asserts on `/v1/me/messages/send`.

### Politica HTTP idempotencia (implementacao actual)

`POST /v1/me/messages/send` devolve **202** com mesmo corpo quando a chave repetida encontra fila/registo existente; **409** em conflito de corrida/`IntegrityError` sem linha recuperavel (`idempotent send conflict`). OpenAPI descreve este contrato em `openapi_extra`.

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

- **ATDD (epic7):** `v2/apps/api/tests/atdd/test_epic7_story71_rest_idempotency_atdd.py` ? contrato OpenAPI (`/v1`, `Idempotency-Key`, 401/429/503 + `Retry-After`) e, com Postgres (`api-ci`), dois `POST` com a mesma chave devolvem o mesmo `id`.
- **Policy:** `tests/policy/test_openapi_gate.py` ? gate amplo em `messages/send`.
- **Integracao (Story 3.2):** `tests/integration/test_story32_outbound_send.py` ? cenarios outbound (incl. `test_send_idempotency_returns_same_id`); mantido como suite de regresao profunda.

## References

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/project-context.md`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-7.md`

## Change Log

- 2026-04-24: **[CS+VS+AT]** materializado no fluxo por story (epicos 7-10 / F2 / F3).
- 2026-05-05: **DS** contrato OpenAPI 7.1 (`/v1`, `Idempotency-Key`, 401/429/503 + `Retry-After`, 202 documentado); ATDD/policy apertados.
- 2026-05-06: **DS** CR Party Mode: `status` e sprint **done**; ATDD com assercao 503+`Retry-After`; smoke idempotencia com DB; matriz de testes na story; tasks/quadradinhos alinhados.
