---
story_key: 6-2-copy-estados-bot-humano
epic: epic-6
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 6-1-embed-autenticado-jwt-validacao-origem
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 6.2 - Copy e estados bot / humano

## Story

**Como** contacto final (canal) e operador (vista),  
**quero** **saber** quem fala (bot vs humano) e **transicoes** claras,  
**para** FR30 (B2B2C). Copy aprovada no tenant.

## Acceptance Criteria

1. **Dado** handoff e respostas automaticas, **entao** templates WhatsApp respeitam politica UX; no **painel**, rotulo de modo **bot/humano** e timeline (UX-DR4, PRD Marina).
2. Minimo aceitavel: operador ve modo bot/humano no painel; canal segue desenho chatbot por regras.
3. API expoe modo da conversa (ex. `GET /v1/me/conversations/{id}/mode`) ou campo embutido no recurso thread; OpenAPI atualizado.

**Requisitos:** FR30. (Cruzamento FR31-33: ver 6.3 e Epico 9.)

## Tasks / Subtasks

- [ ] Modelo de estado conversa: `bot_active` | `human_active` | transicoes com timestamp.
- [ ] Atualizar motor/handoff (4.3 / 5.5) para emitir mudancas de modo quando aplicavel.
- [ ] Admin-web + embed: rotulos e copy tenant-configuravel (storage minimo).
- [ ] Testes; ATDD `test_epic6_story62_bot_human_mode_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Modo e derivado de eventos confiaveis, nao editavel pelo operador sem audit. |
| **Mary** | FR30; ligacao a templates e politica de marca. |
| **John** | Confiança do contacto final depende de transparencia. |
| **Sally** | UX-DR4: nunca esconder que bot falhou silenciosamente. |
| **Amelia** | Sincronizar com mensagens 3.x para timeline coerente. |

## Advanced Elicitation (CS)

- **Pre-mortem:** modo errado apos reconnect - refetch ao focar painel.
- **Red team:** operador forja modo - apenas servidor define modo oficial.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | GET mode 200 com payload minimo (`mode`, `since`). |
| **Amelia** | ATDD usa conversa fixture `atdd-conv-1`. |
| **Mary** | Copy revisivel pelo tenant em AC futuro de CMS - task opcional. |

### Advanced Elicitation (VS)

- **Pre-mortem:** embed nao mostra rotulo - paridade com admin operador.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| RLS | Modo so para conversas do tenant. |
| UX | UX-DR4 em falhas de pipeline. |

## Dev Notes - requisitos tecnicos

- Depende de **6.1** para painel embed; **4.1** para lista/thread operador.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic6_story62_bot_human_mode_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 6.2

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-24: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-24: **[VS]** validada; `atdd_ready: true`.
- 2026-04-24: **[AT]** `test_epic6_story62_bot_human_mode_atdd.py`.
