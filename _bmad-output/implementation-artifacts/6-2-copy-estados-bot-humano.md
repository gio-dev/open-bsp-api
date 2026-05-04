---
story_key: 6-2-copy-estados-bot-humano
epic: epic-6
status: done
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

- [x] Modelo de estado conversa: `bot_active` | `human_active` | transicoes com timestamp.
- [x] Atualizar motor/handoff (4.3 / 5.5) para emitir mudancas de modo quando aplicavel.
- [x] Admin-web + embed: rotulos na consola; glossario de vocabulario no embed (paridade lexical MVP); copy editavel por tenant (CMS) em historia futura.
- [x] Testes; ATDD `test_epic6_story62_bot_human_mode_atdd.py`.

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
- Modo deriva de `inbox_conversation_handoffs.handoff_state` (motor 5.5 ja persiste). Rotulos na consola sao estaticos neste MVP; copy tenant-configuravel (CMS) fica para iteracao seguinte.

## Traceability pos-CR (Party Mode 2026-04-30)

| Ponto | Resolucao |
|-------|-----------|
| OpenAPI / semantica `since` | `ConversationModeResponse` com `Field(description=...)`; doc longo no GET `/mode`; docstring em `conversation_mode.py`. |
| Recurso canonico UI | OpenAPI descreve `/mode` como derivado de handoff; mutacoes em `/handoff`. |
| Templates WhatsApp no texto AC | Fora do codigo desta story; policy de UX rastreia-se em Epic 3 / 6.3 (ver README). |
| Copia tenant-approved (FR30) | MVP: strings fixas PT na consola; CMS/defer documentado no README e aqui. |
| Timeline UX-DR4 | `since` nao substitui marcador temporal; backlog UX explicito na doc da API. |
| Paridade embed | `EmbedPanelPage` glossario FR30 + path GET `/mode` (inline code). |
| Testes / flake | Integracao com conversas **isoladas** + matriz de estados; testes unitarios em `test_conversation_mode_unit.py`. |
| Cache HTTP | `Cache-Control: private, max-age=0, must-revalidate` no GET `/mode`. |
| A11y consola | `aria-busy`, `aria-label` no loading; erro com `role="alert"` e botao **Tentar novamente** (`inbox-mode-retry`); `aria-live="polite"` no badge. |

## Testing Requirements

- ATDD API: `v2/apps/api/tests/atdd/test_epic6_story62_bot_human_mode_atdd.py`
- Integracao: `v2/apps/api/tests/integration/test_story62_conversation_mode.py`
- Unidade: `v2/apps/api/tests/test_conversation_mode_unit.py`
- OpenAPI policy: `test_me_conversations_mode_get_documents_errors`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 6.2

## Dev Agent Record

### Agent Model Used

Cursor agent.

### Completion Notes List

- `GET /v1/me/conversations/{id}/mode` com `ConversationModeResponse`; derivacao central em `app/inbox/conversation_mode.py`.
- Inbox admin: badge modo na thread; fetch invalida com PATCH handoff.
- ATDD atualizado asserts JSON; mocks Vitest epic 4 incluem `/mode`.

### File List

- `v2/apps/api/app/inbox/conversation_mode.py`
- `v2/apps/api/app/api/routes/me_inbox_handoff.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/tests/integration/test_story62_conversation_mode.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/admin-web/src/features/embed/EmbedPanelPage.tsx`
- `v2/apps/admin-web/src/features/inbox/InboxPage.tsx`
- `v2/apps/admin-web/src/atdd/epic4-story42-inbox-tags.atdd.test.tsx`
- `v2/apps/admin-web/src/atdd/epic4-story43-inbox-handoff.atdd.test.tsx`
- `v2/README.md`

---

## Change Log

- 2026-04-24: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-24: **[VS]** validada; `atdd_ready: true`.
- 2026-04-24: **[AT]** `test_epic6_story62_bot_human_mode_atdd.py`.
- 2026-04-30: **[CR/Party]** fechamento: OpenAPI `since`, `Cache-Control`, testes isolados + matriz, a11y inbox, glossario embed, README traceability, status `done`.
