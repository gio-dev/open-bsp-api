---
story_key: 3-2-enviar-mensagem-saida-fila-retry
epic: epic-3
status: done
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 3-1-webhook-entrada-verificacao-encaminhamento
code_location: v2/apps/api
---

# Story 3.2 - Enviar mensagem de saida com fila e retry

## Story

**Como** ator autorizado (operador, integrador via API, motor de regras),  
**quero** **enviar** mensagem WhatsApp via plataforma com politica de **retry** / **429**,  
**para** cumprir FR14 e honestidade de entrega (sem fake sent).

## Acceptance Criteria

1. **Dado** conversa e permissoes, **quando** dispara send, **entao** estado (pendente, entregue, falha) e **persistido**; **429** da Meta aplica backoff com header **Retry-After** (NFR-INT-01) quando aplicavel.
2. Erros com **correlation** e classificacao de culpa plataforma vs Meta quando possivel (FR51, UX-DR4).
3. Nunca reportar "enviado" sem confirmacao alinhada ao contrato (sem fake sent).

**Requisitos:** FR14. **NFRs:** NFR-PERF-01, NFR-INT-01, NFR-SEC-05.

## Tasks / Subtasks

- [x] `POST /v1/me/messages/send` (ou path CDA) com auth tenant + papel.
- [x] Worker/fila para chamadas Meta; estados persistidos; idempotency onde necessario.
- [x] Mapear 429 + Retry-After para politica de retry; metricas basicas.
- [x] OpenAPI; testes; ATDD `test_epic3_story32_send_message_atdd.py`.

### Review Findings

#### 2026-04-28 ? Code review (BMAD adversarial + Party Mode)

**Resolvido em 2026-04-28:**

- [x] [Review][Decision] **429 / motor de re-tentativa** ? Sweep `outbound_sweep_loop`, SQL `due_outbound_candidates` (013), env `OUTBOUND_SWEEP_INTERVAL_SECONDS` (0 em CI; 15 no servico `api` no compose), *advisory lock* por batch.
- [x] [Review][Patch] **Excecoes no envio** ? `try/except` no worker; `failed` / `upstream_fault=platform` / `send_exception`.
- [x] [Review][Decision] **Remetente ambiguo** ? 409 se varios numeros activos sem `phone_number_id`; teste de integracao.
- [x] [Review][Patch] **Graph 200 sem id** ? `missing_message_id` em `meta_send.py`; teste unario.
- [x] [Review][Defer] **Ruff Epic 2** ? escopo PR; sem alteracao nesta entrega.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Contrato de resposta alinhado a OpenAPI; erros canonicos 1.1. |
| **Mary** | FR14 + NFR-INT-01; honestidade de estado e obrigatoria no AC. |
| **John** | Valor de canal completo; depende de 3.1 para contexto de conversa. |
| **Sally** | UX-DR4 em falhas; correlation para suporte. |
| **Amelia** | Meta sandbox vs prod claramente separados (FR4 / ambientes). |

## Advanced Elicitation (CS)

- **Pre-mortem:** fila enterra falhas - alertas e DLQ ou estado falha visivel.
- **Red team:** envio para numero fora de opt-in - regras de compliance (ligacao epico 6/9).

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Persistencia de estado antes de ack ao cliente quando necessario para nao mentir. |
| **Amelia** | ATDD exige 200/201/202 e `status` ou `id` no JSON. |
| **Mary** | Retry-After documentado em OpenAPI ou ADR de integracao Meta. |

### Advanced Elicitation (VS)

- **Socratic:** o que prova que nao e fake sent? - teste de integracao com stub Meta.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | Credenciais Meta por tenant; sem vazamento em logs. |
| Performance | NFR-PERF-01 considerado no desenho da fila. |

## Dev Notes - requisitos tecnicos

- Depende de **3.1** para numeros/WABA e pipeline coerente.
- Integracao Meta Graph API conforme CDA.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic3_story32_send_message_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 3.2

## Dev Agent Record

### Agent Model Used

Cursor / Composer (implementacao assistida).

### Completion Notes List

- Tabela `outbound_whatsapp_messages` (migracao 012), RLS, idempotencia parcial por `(tenant_id, idempotency_key)`.
- `POST /v1/me/messages/send` com papel `org_admin` / `operator` / `agent`, header `Idempotency-Key`, resposta **202** com `id` e `status`; worker em background.
- Cliente Meta (`meta_send.py`): normalizacao de destino, httpx, **429** com `Retry-After`, modo stub via configuracao.
- Worker (`outbound_worker.py`): estados `queued` ? `sending` ? `sent` / `rate_limited` / `failed`; culpa `meta` vs `platform`.
- Ambiente `sandbox` aceite no body (alinhado ao seed CI).
- **2026-04-28 [pos-review]:** Migracao **013** `due_outbound_candidates`; `outbound_sweep.py` + *lifespan*; `SELECT FOR UPDATE` no worker; 409 remetente ambiguo; 200 Graph sem id => falha; excecoes Meta => `failed`; testes integracao sweep + ambiguo; pytest CI com sweep **desligado** (interval 0).
- Ajuste relacionado 3.1: ingresso exige **timestamp** parseavel nas mensagens/status antes de enfileirar (**400**); `ensure_fresh_event(None)` continua a nao levantar (anti-replay so quando ha `event_at`). Migracao **011** usa `MIN(tenant_id::text)::uuid` para compatibilidade PostgreSQL.

### File List

- `v2/docker-compose.yml`
- `v2/apps/api/alembic/versions/011_resolve_waba_tenant_status.py`
- `v2/apps/api/alembic/versions/012_outbound_whatsapp_messages.py`
- `v2/apps/api/alembic/versions/013_due_outbound_candidates.py`
- `v2/apps/api/app/core/config.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/app/db/models_outbound.py`
- `v2/apps/api/app/tenancy/rbac.py`
- `v2/apps/api/app/tenancy/deps.py`
- `v2/apps/api/app/api/routes/me_messages.py`
- `v2/apps/api/app/whatsapp/meta_send.py`
- `v2/apps/api/app/whatsapp/outbound_worker.py`
- `v2/apps/api/app/whatsapp/outbound_sweep.py`
- `v2/apps/api/app/whatsapp/webhook_ingress.py`
- `v2/apps/api/tests/conftest.py`
- `v2/apps/api/tests/test_meta_send.py`
- `v2/apps/api/tests/integration/test_story32_outbound_send.py`
- `v2/apps/api/tests/atdd/test_epic3_story32_send_message_atdd.py`
- `v2/apps/api/tests/atdd/test_epic3_story31_webhook_ingress_atdd.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic3_story32_send_message_atdd.py`.
- 2026-04-28: **[Dev]** pos-code-review: sweep 013, FOR UPDATE, 409 remetente, honestidade Graph id, `status` **done**.
