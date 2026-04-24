---
story_key: 3-1-webhook-entrada-verificacao-encaminhamento
epic: epic-3
status: in-progress
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
- [ ] Fila interna (ou outbox) com idempotencia / janela anti-replay.
- [ ] OpenAPI + testes integracao (revisao policy gate se aplicavel); ATDD `test_epic3_story31_webhook_ingress_atdd.py` (existente) + testes unitarios BSUID/HMAC.

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

### File List

- `v2/apps/api/app/whatsapp/bsuid.py`
- `v2/apps/api/app/whatsapp/identity.py`
- `v2/apps/api/app/whatsapp/__init__.py`
- `v2/apps/api/app/api/routes/webhooks_whatsapp.py`
- `v2/apps/api/app/core/config.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/tests/conftest.py`
- `v2/apps/api/tests/test_whatsapp_bsuid.py`
- `v2/apps/api/tests/test_whatsapp_webhook_security.py`
- `v2/apps/api/tests/atdd/test_epic3_story31_webhook_ingress_atdd.py`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic3_story31_webhook_ingress_atdd.py`.
- 2026-04-23: **[DS]** BSUID + webhook GET/POST + HMAC quando segredo configurado; testes unitarios BSUID/HMAC; story `in-progress`; WABA->tenant e fila pendentes.
