---
story_key: 6-1-embed-autenticado-jwt-validacao-origem
epic: epic-6
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 2-1-oauth-oidc-login-base-consola
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 6.1 - Embed autenticado (JWT) e validacao de origem

## Story

**Como** tenant que integra,  
**quero** **incluir** o painel no workspace com **token** e **validacao** de **embed origin**,  
**para** FR29 e isolamento (sem OAuth redirect no iframe; CDA D2).

## Acceptance Criteria

1. **Dado** host e allowlist de origem, **quando** o iframe carrega com Bearer valido, **entao** a **sessao embed** funciona; se invalido, erros claros; **401** inicia fluxo de renovacao **via** host (**postMessage**) **sem loop infinito** (UX-DR7, D2 ADR).
2. API de validacao documentada (ex. `POST /v1/embed/session/validate` com `Origin` + body token).
3. NFR-SEC-01: segredos de assinatura JWT embed nao expostos ao cliente de forma indevida.

**Requisitos:** FR29, CDA D2, UX-DR7. **NFRs:** NFR-SEC-01.

## Tasks / Subtasks

- [ ] Emissao/validacao JWT embed (ou token opaco) com claims tenant + exp curtos conforme ADR.
- [ ] Allowlist `Origin` / `embed_parent` por tenant; rejeitar origem nao autorizada.
- [ ] Contrato postMessage renovacao documentado no README embed.
- [ ] OpenAPI; testes; ATDD `test_epic6_story61_embed_session_atdd.py`.
- [ ] Shell iframe admin-web ou app embed dedicada conforme CDA.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | D2 e unico: nao misturar fluxo consola OAuth com sessao iframe sem ADR. |
| **Mary** | FR29 + UX-DR7; loop 401 e risco UX e seguranca. |
| **John** | Desbloqueia B2B2C para parceiros. |
| **Sally** | Mensagens de erro comprensiveis no embed sem stack. |
| **Amelia** | CORS e Origin header testados; nao confiar so no Referer. |

## Advanced Elicitation (CS)

- **Pre-mortem:** token embed long-lived roubado - TTL curto + refresh via host confiavel.
- **Red team:** qualquer origem com token vazado - binding token a origem esperada onde possivel.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | POST validate + 200/401 coberto; postMessage fora do pytest mas documentado. |
| **Amelia** | ATDD usa Origin fixo de exemplo; DS ajusta allowlist fixture. |
| **Mary** | NFR-SEC-01 refletido em tasks de segredo. |

### Advanced Elicitation (VS)

- **Pre-mortem:** parceiro bloqueia third-party cookies - desenho nao depender de cookie cross-site indevido.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | Allowlist obrigatoria em prod. |
| UX | Sem loop infinito em 401. |

## Dev Notes - requisitos tecnicos

- Depende de **2.1** apenas como referencia de identidade plataforma; embed **nao** usa redirect OAuth no iframe.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic6_story61_embed_session_atdd.py`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-6.md`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 6.1
- `_bmad-output/planning-artifacts/architecture.md` - D2

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-24: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-24: **[VS]** validada; `atdd_ready: true`.
- 2026-04-24: **[AT]** `test_epic6_story61_embed_session_atdd.py`.
