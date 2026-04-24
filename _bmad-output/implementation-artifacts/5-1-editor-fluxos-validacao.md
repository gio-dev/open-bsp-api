---
story_key: 5-1-editor-fluxos-validacao
epic: epic-5
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

# Story 5.1 - Editor de fluxos e validacao

## Story

**Como** operador,  
**quero** **criar/editar** fluxos por **regras** (sem LLM) com **validacao** antes de testar,  
**para** FR22 com erros acionaveis (campo, linha) (UX-DR10).

## Acceptance Criteria

1. **Dado** um fluxo em draft, **quando** gravo ou valido, **entao** validacao **bloqueia** publish de draft invalido com mensagem **por campo/linha**; **nao** mostrar stack do servidor ao operador (UX-DR4).
2. Modelo de fluxo (nos, arestas, gatilho/condicao/acao) persistido com `tenant_id`.
3. API de validacao documentada (ex. `POST /v1/me/flows/validate`); OpenAPI atualizado.

**Requisitos:** FR22, UX-DR10.

## Tasks / Subtasks

- [ ] Schema de fluxo + migracao; CRUD minimo de drafts.
- [ ] Validador servidor-side com erros estruturados (path + mensagem).
- [ ] Admin-web: editor UX-DR10; erros inline.
- [ ] Testes; ATDD `test_epic5_story51_flow_editor_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Contrato de erro de validacao estavel (nao misturar com 422 generico sem detalhe). |
| **Mary** | FR22 explicito; sem LLM no core desta story. |
| **John** | Base do construtor de produto. |
| **Sally** | Mensagens por campo; sem jargao de stack (UX-DR4). |
| **Amelia** | Limite de tamanho de grafo; timeout de validacao. |

## Advanced Elicitation (CS)

- **Pre-mortem:** fluxo ciclico - validador deteta ciclos ou ADR permite com limite de passos.
- **Red team:** YAML import de fluxo - sanitizar se existir import.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Validacao obrigatoria antes de sandbox/publish nas stories seguintes. |
| **Amelia** | ATDD: POST validate retorna 200 ou 422 com payload util. |
| **Mary** | Bloqueio de publish invalido testado em integracao. |

### Advanced Elicitation (VS)

- **Socratic:** o que e "linha" sem editor visual? - indice de no ou id no contrato.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| RLS | Fluxos so no tenant. |
| UX | UX-DR10 + UX-DR4. |

## Dev Notes - requisitos tecnicos

- Depende de **4.1** para contexto de inbox na UX (lista|thread); API pode existir antes da UI completa.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic5_story51_flow_editor_atdd.py`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-5.md`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 5.1

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic5_story51_flow_editor_atdd.py`.
