---
story_key: 3-1-webhook-entrada-verificacao-encaminhamento
epic: epic-3
status: review
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 1-4-waba-numeros-ambientes
  - 2-4-segredos-verificacao-webhooks
code_location: v2/apps/api
---

# Story 3.1 - Webhook de entrada, verificacao e encaminhamento

## Story

**Como** tenant com WABA,  
**quero** **receber** eventos na plataforma via **webhook** verificavel, **rejeitando reenvio** e **frescura** fora de politica,  
**para** FR11-FR13 e base do pipeline.

## Acceptance Criteria

1. **Dado** o endpoint de webhook (**GET** verificacao Meta, **POST** payload), **quando** chega payload com assinatura e tenant/WABA mapeaveis, **entao** o evento e enfileirado com **`tenant_id` resolvido antes de regras** (FR13).
2. Replay fora de janela / criterio e **rejeitado** (FR12) com telemetria; **nao** persistir efeito duplicado indevido (NFR-INT-02).
3. Detalhes tecnicos expoem **correlation** (UX-DR6) onde aplicavel.

**Requisitos:** FR11, FR12, FR13. **NFRs:** NFR-SEC-05, NFR-INT-02.

## Tasks / Subtasks

- [x] Rota GET `/v1/webhooks/whatsapp` (ou prefixo CDA): `hub.mode`, `hub.verify_token`, `hub.challenge` alinhados a Meta.
- [x] Rota POST: validar `X-Hub-Signature-256` quando `WHATSAPP_WEBHOOK_APP_SECRET` esta definido; parse do payload Meta; **identidade inbound BSUID-ready** (`user_id` / `from_user_id` / `wa_id` via `resolve_inbound_identity`). **Pendente:** mapear WABA -> `tenant_id` e enfileirar antes de motor/regras (FR13).
- [x] Fila interna (ou outbox) com idempotencia / janela anti-replay.
- [x] OpenAPI + testes integracao (revisao policy gate se aplicavel); ATDD `test_epic3_story31_webhook_ingress_atdd.py` (existente) + testes unitarios BSUID/HMAC.

### Review Findings

#### 2026-04-28 ? Code review (BMAD adversarial + Party Mode)

- [ ] [Review][Decision] **Resolucao WABA ambigua sem `phone_number_id`** ? `resolve_waba_tenant` (migracao `010`) com `p_phone_number_id` vazio escolhe uma linha por `ORDER BY ... created_at LIMIT 1`. Se existir mais do que um mapeamento para o mesmo `waba_id` (erro de dados ou modelo permissivo), o tenant pode ser o errado (pre-mortem na story). E necessario decidir: (A) manter como hoje e documentar como contrato operacional, (B) falhar com 409/422 quando houver empate, ou (C) reforcar integridade na BD (ex. unicidade por `waba_id` onde fizer sentido).

- [ ] [Review][Decision] **Eventos sem timestamp e janela anti-replay** ? `ensure_fresh_event` retorna logo se `event_at is None` ou `max_age_seconds <= 0`, logo nenhuma janela e aplicada. Para FR12/NFR-INT-02, decidir se eventos Meta sem `timestamp` devem ser **aceites** (com risco), **rejeitados** (400/409), ou **aceites com metrica** obrigatoria.

- [ ] [Review][Patch] **Story desatualizada na task WABA** ? A linha em Tasks ainda marca "**Pendente:** mapear WABA -> tenant_id" apesar de `webhook_ingress.py` + `010` implementarem resolucao e fila. Atualizar texto dos checkboxes para refletir o estado real.

- [ ] [Review][Patch] **Docstring ATDD vs comportamento real** ? `test_story_31_webhook_post_accepts_valid_signature_stub` diz "senao stub sha256=00"; sem `WHATSAPP_WEBHOOK_APP_SECRET` mas com `auth_dev_stub`, a rota **nao** compara a assinatura a `sha256=00` (bloco HMAC e saltado). Ajustar docstring para nao induzir em erro.

- [x] [Review][Defer] **Ruff/format em rotas fora do nucleo 3.1** ? `me_api_keys.py`, `me_webhook_secrets.py` listados no File List apenas por formatacao; se o PR for so de 3.1, considerar revert separado em follow-up. Deferido: pre-existente / escopo de PR.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Um unico path de ingresso documentado; sem bypass de assinatura em producao. |
| **Mary** | FR11-13 e NFR-INT-02 explicitos; taxonomia de erro replay vs assinatura invalida. |
| **John** | Desbloqueia inbox (epico 4) e motor (epico 5). |
| **Sally** | Correlation visivel a operador tecnico (UX-DR6). |
| **Amelia** | Stub de assinatura em dev apenas com flag clara; CI nao desligar verificacao sem aviso. |

## Advanced Elicitation (CS)

- **Pre-mortem:** WABA partilhado entre tenants por erro de mapping - testes negativos de resolucao.
- **Red team:** payload gigante / DoS - limites de tamanho e timeout na borda.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Tenant_id na fila sempre do servidor, nunca so do corpo bruto. |
| **Amelia** | ATDD cobre GET challenge + POST 200/202 com stub de assinatura. |
| **Mary** | Replay rejeitado - criterio documentado (timestamp/nonce ou idempotency key). |

### Advanced Elicitation (VS)

- **Pre-mortem:** Meta rota webhook - runbook de re-verificacao e secret 2.4.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | Assinatura obrigatoria em prod; segredo nunca em logs. |
| RLS | Eventos persistidos com tenant_id correto. |

## Dev Notes - requisitos tecnicos

- Depende de **1.4** (WABA/numero) e **2.4** (segredo verificacao).
- Ver `architecture.md` para filas e integracao Meta.
- **Transicao Meta (BSUID):** modulo `app/whatsapp` com `normalize_bsuid` / `is_valid_bsuid` e `InboundUserIdentity.stable_storage_key()` para priorizar BSUID sobre `wa_id` no armazenamento futuro; telefone permanece opcional no payload.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic3_story31_webhook_ingress_atdd.py`
- Unitarios: `v2/apps/api/tests/test_whatsapp_bsuid.py`, `v2/apps/api/tests/test_whatsapp_webhook_security.py`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-3.md`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 3.1

## Dev Agent Record

### Agent Model Used

_(sessao de implementacao; atualizar se necessario)_

### Completion Notes List

- **2026-04-23 [DS] ? incremento parcial:** endpoint GET/POST `/v1/webhooks/whatsapp`, validacao HMAC opcional por env, parse `whatsapp_business_account` + mensagens, resolucao de identidade alinhada a campos Meta (BSUID). Resposta POST 202 `accepted` sem fila nem `tenant_id` ainda ? proximo passo para fechar AC1 (FR13).
- **2026-04-28 [DS]:** Migracao `010` com `webhook_inbound_events` (RLS), funcao `resolve_waba_tenant` (SECURITY DEFINER), servico `webhook_ingress` (tenant por WABA + `phone_number_id`, `UNIQUE (waba_id, source_id)`, anti-replay por `whatsapp_webhook_max_event_age_seconds`, telemetria `webhook_replay_rejected` / `webhook_unknown_waba`). POST 202 com `request_id`, `enqueued`, `deduplicated`, `skipped`. Seed CI WABA `ci-atdd-waba`. Testes integracao + policy OpenAPI + ATDD enqueue; unitarios em `test_whatsapp_webhook_security.py`.

### File List

- `v2/apps/api/alembic/versions/010_webhook_inbound_events.py`
- `v2/apps/api/app/whatsapp/bsuid.py`
- `v2/apps/api/app/whatsapp/identity.py`
- `v2/apps/api/app/whatsapp/__init__.py`
- `v2/apps/api/app/whatsapp/webhook_ingress.py`
- `v2/apps/api/app/db/models_webhook_inbound.py`
- `v2/apps/api/app/api/routes/webhooks_whatsapp.py`
- `v2/apps/api/app/core/config.py`
- `v2/apps/api/app/ci_seed.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/tests/conftest.py`
- `v2/apps/api/tests/test_whatsapp_bsuid.py`
- `v2/apps/api/tests/test_whatsapp_webhook_security.py`
- `v2/apps/api/tests/integration/test_story31_webhook_ingress_queue.py`
- `v2/apps/api/tests/atdd/test_epic3_story31_webhook_ingress_atdd.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/api/app/api/routes/me_api_keys.py` (ruff format)
- `v2/apps/api/app/api/routes/me_webhook_secrets.py` (ruff format)

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic3_story31_webhook_ingress_atdd.py`.
- 2026-04-23: **[DS]** BSUID + webhook GET/POST + HMAC quando segredo configurado; testes unitarios BSUID/HMAC; story `in-progress`; WABA->tenant e fila pendentes.
- 2026-04-28: **[DS]** Fila `webhook_inbound_events`, resolucao tenant, idempotencia, anti-replay, OpenAPI/errors, ATDD + integracao + policy; story `review`.
