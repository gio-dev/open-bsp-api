---
story_key: 4-3-handoff-contexto-minimo
epic: epic-4
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 4-1-inbox-split-lista-thread
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 4.3 - Handoff e contexto minimo

## Story

**Como** operador,  
**quero** **passar** de automacao **para humano** (e vice-versa) com **resumo** minimo e **fila/roteamento** quando a automacao gera handoff,  
**para** evitar o consumidor a repetir tudo (FR19, FR20).

## Acceptance Criteria

1. **Dado** regra a emitir handoff, **quando** o operador assume, **entao** ve **intencao**, **ultima saida do bot** e **estado** (aceite / queued / falhou) - nunca silencio se o pipeline falhou (UX-DR4).
2. Supervisao pode ajustar **fila/roteamento** conforme regras do tenant (FR20).
3. API expoe estado de handoff por conversa (ex. `GET .../handoff`) ou campo embutido coerente no CDA.

**Requisitos:** FR19, FR20.

## Tasks / Subtasks

- [ ] Modelo handoff (conversation_id, summary, bot_last_output, state, queue_id, ...).
- [ ] Endpoints leitura + atualizacao de fila (papeis supervisao); audit minimo se sensivel.
- [ ] Motor epico 5 emite eventos de handoff - contrato interno documentado.
- [ ] Admin-web: painel contexto na thread; estados honestos.
- [ ] Testes; ATDD `test_epic4_story43_handoff_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Handoff nao duplica historico completo - resumo e ponteiros. |
| **Mary** | FR19/FR20; PRD Marina como referencia narrativa. |
| **John** | Diferencia produto de inbox "cega". |
| **Sally** | Falha de pipeline visivel - copy clara (UX-DR4). |
| **Amelia** | Integracao com filas - idempotencia em "assumir conversa". |

## Advanced Elicitation (CS)

- **Pre-mortem:** dois operadores assumem simultaneamente - locking ou "already claimed".
- **Red team:** resumo com PII excessivo - minimizar no payload operador.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Ligacao ao motor 5.x documentada (evento ou polling). |
| **Amelia** | ATDD: GET handoff 200 com fixture. |
| **Mary** | FR20 - API de ajuste de fila ou mesmo recurso PATCH documentado. |

### Advanced Elicitation (VS)

- **Pre-mortem:** handoff sem conversa - 404 coerente.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| RLS | Handoff so no tenant da conversa. |
| UX | Sem stack trace ao operador. |

## Dev Notes - requisitos tecnicos

- Depende de **4.1**; integracao forte com **5.5** (engine) em fases posteriores.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic4_story43_handoff_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 4.3

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic4_story43_handoff_atdd.py`.
