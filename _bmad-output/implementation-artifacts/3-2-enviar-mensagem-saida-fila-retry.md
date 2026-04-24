---
story_key: 3-2-enviar-mensagem-saida-fila-retry
epic: epic-3
status: ready-for-dev
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

- [ ] `POST /v1/me/messages/send` (ou path CDA) com auth tenant + papel.
- [ ] Worker/fila para chamadas Meta; estados persistidos; idempotency onde necessario.
- [ ] Mapear 429 + Retry-After para politica de retry; metricas basicas.
- [ ] OpenAPI; testes; ATDD `test_epic3_story32_send_message_atdd.py`.

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

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic3_story32_send_message_atdd.py`.
