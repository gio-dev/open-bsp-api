---
story_key: 4-1-inbox-split-lista-thread
epic: epic-4
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 3-1-webhook-entrada-verificacao-encaminhamento
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 4.1 - Inbox com split lista e thread

## Story

**Como** operador,  
**quero** **ver a lista** de conversas e o **fio** no **mesmo contexto** com **cabecalho** tenant / WABA / numero,  
**para** trabalhar a tarefa sem perder fio (UX passo 7 e 9).

## Acceptance Criteria

1. **Dado** permissoes a numeros/filas, **quando** abro a inbox, **entao** vejo a lista; ao selecionar, a **thread** carrega; **cabecalho** mostra contexto (UX-DR5). Abaixo de breakpoint `md`, mobile = lista fullscreen e navegacao para thread (UX spec 9).
2. Loading = skeleton + stale-while-revalidate (TanStack Query) **sem** mascarar erro (UX-DR4).
3. API lista conversas e mensagens da thread (ou equivalente no CDA) com `tenant_id` e erros canonicos 1.1.

**Requisitos:** FR17, UX-DR1, UX-DR5, UX-DR8. **NFRs:** NFR-PERF-02 (minimo verificavel no piloto).

## Tasks / Subtasks

- [ ] `GET /v1/me/conversations` (lista) + `GET /v1/me/conversations/{id}/messages` (thread) ou paths CDA equivalentes.
- [ ] Cabecalho: tenant, WABA, numero no payload ou headers de contexto documentados.
- [ ] Admin-web: layout split lista|thread; TanStack Query; skeleton; mobile navegacao.
- [ ] OpenAPI; testes integracao; ATDD `test_epic4_story41_inbox_split_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Contratos alinhados ao epico 3 (conversas alimentadas por eventos); sem N+1 descontrolado na lista. |
| **Mary** | FR17 + UX-DR1/5/8; NFR-PERF-02 para frescura minima. |
| **John** | Primeira story de valor de mesa unificada. |
| **Sally** | Erros honestos; cabecalho sempre visivel no desktop. |
| **Amelia** | Headers dev para tenant; testes com dois tenants para RLS. |

## Advanced Elicitation (CS)

- **Pre-mortem:** lista enorme sem paginacao - cursores ou limit+next obrigatorios.
- **Red team:** fuga de titulo de conversa entre tenants - todas as queries com escopo tenant.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Lista e thread como recursos distintos mas correlacionados no OpenAPI. |
| **Amelia** | ATDD: 200 em lista + 200 em mensagens da conversa de fixture. |
| **Sally** | Skeleton obrigatorio no AC - refletir em criterio de review UI. |

### Advanced Elicitation (VS)

- **Pre-mortem:** conversa sem mensagens - estado vazio claro, nao erro 500.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| RLS | So conversas do tenant. |
| UX | UX-DR4 em falhas de rede. |

## Dev Notes - requisitos tecnicos

- Depende de **3.1** (e mensagens de entrada) para dados minimos de inbox.
- Ver `architecture.md` e UX specs para split responsivo.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic4_story41_inbox_split_atdd.py`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-4.md`
- Opcional: Vitest ATDD inbox page (separado).

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 4.1

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic4_story41_inbox_split_atdd.py`.
