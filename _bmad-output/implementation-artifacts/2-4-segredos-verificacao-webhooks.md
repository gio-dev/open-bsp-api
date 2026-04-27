---
story_key: 2-4-segredos-verificacao-webhooks
epic: epic-2
status: done
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 2-3-chaves-api-emissao-revogacao
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 2.4 - Segredos de verificacao de webhooks

## Story

**Como** **operador** autorizado,  
**quero** **rodar o segredo** de verificacao de **webhook** com **janela de coexistencia**,  
**para** Meta e integracoes continuarem a validar callbacks (FR9).

## Acceptance Criteria

1. **Dado** webhook com segredo v1 e v2 ativos na transicao, **quando** eventos com assinatura valida chegam, **entao** sao aceites; assinatura invalida rejeitada; apos janela, v1 deixa de ser aceite.
2. UI Integracoes comunica estado da rotacao claramente (UX-DR4).
3. Endpoint de rotacao exposto e documentado (ex. `POST /v1/me/webhook-secrets/rotate`).

**Requisitos:** FR9, FR11 preparacao. **NFRs:** NFR-INT-01, NFR-SEC-05.

## Tasks / Subtasks

- [x] Modelo segredo(s) por tenant/WABA conforme CDA; dois valores ativos durante janela.
- [x] Servico de rotacao + politica de expiracao v1.
- [x] Validacao de assinatura em ingresso webhook (epico 3 reutiliza); esta story entrega **gestao** do segredo e endpoint rotate.
- [x] OpenAPI; testes; ATDD `test_epic2_story24_webhook_secrets_atdd.py`.

### Post-review correcoes (2026-04-24)

- [x] UI `IntegrationsPage`: copy do token Meta + truncado de `id` sem `?` espurio.
- [x] ATDD: `GET /v1/me/webhook-secrets` no OpenAPI.
- [x] Rate limit em `POST .../rotate` em ambientes sem `AUTH_DEV_STUB` (min. 2s por tenant); desligado em pytest e com stub.
- [x] Migração `009`: indice unico parcial ? no maximo um `invalid_after IS NULL` por `tenant_id`.
- [x] Integração: `test_after_coexistence_window_old_verify_token_rejected` (SQL a expirar token antigo; hub 403/200).

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Coexistencia evita downtime Meta; relogar com NFR-INT-01. |
| **Mary** | FR9 + preparacao FR11; dependencia clara do canal WhatsApp. |
| **John** | Completa credenciais de integracao do epico 2. |
| **Amelia** | Rotacao testavel com dev stub; sem segredos em respostas GET. |
| **Sally** | Copy honesta sobre prazo em que v1 deixa de funcionar. |

## Advanced Elicitation (CS)

- **Pre-mortem:** rotacao a meio de pico - UX com aviso e confirmacao.
- **Red team:** replay com segredo antigo apos janela - teste automatizado rejeita.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Dois segredos ativos e testes de assinatura alinhados ao design Meta. |
| **Amelia** | ATDD RED: POST rotate retorna 200/201 apos DS. |
| **Mary** | NFR-SEC-05 em validacao de callbacks - epico 3 confirma end-to-end. |

### Advanced Elicitation (VS)

- **Pre-mortem:** WABA sem segredo - 400 claro na primeira configuracao.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | Segredos nunca em logs plain; rotacao auditada. |
| Integracao | Epico 3 consome mesma fonte de verificacao. |

## Dev Notes - requisitos tecnicos

- Depende de **2.3** pelo padrao de credenciais e permissoes de operador.
- Alinhar com Story 3.1 para GET verify + POST payload Meta.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic2_story24_webhook_secrets_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 2.4

## Dev Agent Record

### Agent Model Used

? (implementacao em sessao de desenvolvimento)

### Completion Notes List

- Tabela `webhook_verify_secrets` (RLS), modelo `WebhookVerifySecret`, API `GET /v1/me/webhook-secrets` e `POST /v1/me/webhook-secrets/rotate` (201 com token plain uma vez, coexistencia v1/v2); GET nao expoe segredos.
- Verificacao Meta GET: com `tenant_id` na query, match via DB; sem `tenant_id`, comportamento legado com `WHATSAPP_WEBHOOK_VERIFY_TOKEN` (ATDD 3.1/CI).
- Admin Integracoes: bloco "Meta webhook verify token" (rotacao, copia de `tenant_id`, listagem de estado).
- CI: `api-ci` e `admin-web-ci` a verde; ESLint `MembersPage` (apiPath estavel) sem warning.

### File List

- `v2/apps/api/alembic/versions/008_webhook_verify_secrets_rls.py`
- `v2/apps/api/alembic/versions/009_wvs_one_open_invalid_after.py`
- `v2/apps/api/app/db/models.py` ? `WebhookVerifySecret`
- `v2/apps/api/app/whatsapp/webhook_verify_db.py`
- `v2/apps/api/app/api/routes/me_webhook_secrets.py`
- `v2/apps/api/app/api/routes/webhooks_whatsapp.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/tests/atdd/test_epic2_story24_webhook_secrets_atdd.py`
- `v2/apps/api/tests/integration/test_story24_webhook_verify.py`
- `v2/apps/api/tests/test_rbac_story24_webhook_secrets.py`
- `v2/apps/admin-web/src/features/integrations/IntegrationsPage.tsx`
- `v2/apps/admin-web/src/features/team/MembersPage.tsx` (fix eslint useCallback)
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic2_story24_webhook_secrets_atdd.py`.
- 2026-04-27: **[DS]** implementacao; sprint `2-4` -> `done`; story `status: done`; fix ESLint `MembersPage`.
- 2026-04-24: **[PR]** correcoes pos code review (UI, ATDD, rate limit prod, mig. 009, teste integracao coexistencia).
