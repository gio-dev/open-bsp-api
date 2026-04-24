---
story_key: 6-4-acessibilidade-embed
epic: epic-6
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 6-1-embed-autenticado-jwt-validacao-origem
code_location: v2/apps/admin-web
---

# Story 6.4 - Acessibilidade do embed

## Story

**Como** utilizador com necessidades a11y,  
**quero** **operar** a parte embed com **foco, contraste, teclado** e **erros acessiveis** onde o produto assume **WCAG 2.1/2.2 AA**,  
**para** FR34 e NFR-A11Y.

## Acceptance Criteria

1. **Dado** embed e roteiros prioritarios, **entao** tab order logico; focus ring; contraste AA; erros ligados a campos. **Zero** blockers criticos auditados nas jornadas prioritarias (NFR-A11Y-01 a 04, FR34).
2. Documentacao de roteiros testados + evidencia (relatorio axe/Playwright ou checklist interno).
3. Opcional API metadados (ex. `GET /v1/me/embed/a11y-status`) para CI/dashboard - **nao** substitui auditoria humana.

**Requisitos:** FR34, UX-DR9. **NFRs:** NFR-A11Y-01 a NFR-A11Y-04.

## Tasks / Subtasks

- [ ] Auditar embed (Chakra/theme, foco, ARIA, live regions para mensagens).
- [ ] Corrigir blockers criticos nas jornadas prioritarias definidas com UX/legal.
- [ ] Automacao: testes a11y smoke no admin-web/embed package se aplicavel.
- [ ] ATDD API opcional: `test_epic6_story64_embed_a11y_atdd.py` (200 ou 404 ate endpoint existir).

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | A11y e requisito de release embed; nao "best effort" se anexo legal diz AA. |
| **Mary** | FR34 + NFRs A11Y; rastrear escopo "jornadas prioritarias". |
| **John** | Risco de exclusao de utilizadores e compliance. |
| **Sally** | UX-DR9: contraste e foco em componentes Chakra customizados. |
| **Amelia** | Testes e2e com keyboard-only onde Vitest nao chega. |

## Advanced Elicitation (CS)

- **Pre-mortem:** iframe rouba foco - parent/host coordination documentada.
- **Red team:** modais sem trap focus - padrao unico de Dialog.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Lista de jornadas prioritarias fechada com PM/UX antes do merge. |
| **Amelia** | ATDD aceita 404 ate endpoint de status; gate real = testes a11y + manual. |
| **Sally** | Evidencia arquivada (screenshots/relatorio) no DoD. |

### Advanced Elicitation (VS)

- **Pre-mortem:** regressao em tema escuro - verificar contraste em ambos.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| NFR | NFR-A11Y-01..04 verificados nas jornadas escolhidas. |
| UX | Erros anunciados (live region ou aria-describedby). |

## Dev Notes - requisitos tecnicos

- Depende de **6.1** (shell embed); trabalho principal em **admin-web** ou app embed.
- Paralelizar com design system (tokens foco/contraste).

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic6_story64_embed_a11y_atdd.py` (opcional/metadado)
- Testes a11y no frontend (recomendado no DS).

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 6.4

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-24: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-24: **[VS]** validada; `atdd_ready: true`.
- 2026-04-24: **[AT]** `test_epic6_story64_embed_a11y_atdd.py`.
