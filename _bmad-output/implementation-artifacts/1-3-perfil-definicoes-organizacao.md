---
story_key: 1-3-perfil-definicoes-organizacao
epic: epic-1
status: done
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 1-2-modelo-tenant-rls-minima-prova-isolamento
vs_note: "Preferir story 2-1-oauth-oidc-login-base-consola antes de staging público."
fr: FR1
---

# Story 1.3 ? Perfil e definições da organização (FR1)

## Story

**Como** admin do tenant,  
**quero** registar e editar perfil e definições da minha organização,  
**para** operar a conta com metadados corretos (nome, fuso horário, contacto operacional, etc.).

## Decisão de produto (VS) ? auth

**Ordem preferida para *staging* / piloto:** completar **Story 2.1 (OAuth/OIDC)** antes de expor esta funcionalidade a utilizadores externos.

**Para DS interno e ATDD antes da 2.1:** permitido **stub de desenvolvimento** com **todas** as condições:

1. Variável `AUTH_DEV_STUB=true` (ou equivalente) **só** em `docker-compose.dev` / env local ? **nunca** default em `runtime` de produção.
2. Headers documentados: `X-Dev-Tenant-Id`, `X-Dev-User-Id`, `X-Dev-Roles: org_admin` (valores separados por vírgula se necessário).
3. Task explícita no fim: ?Remover stub ou integrar JWT/OIDC da 2.1? antes de merge para `main` se política da equipa exigir.

## Acceptance Criteria

1. **Dado** um utilizador autenticado com papel que inclui admin de organização (ou *stub* acima em dev), **quando** acede à área de definições, **então** pode **ler e atualizar** os campos acordados na API **apenas** no seu `tenant_id`.
2. Alterações relevantes geram **audit log mínimo** (ator, timestamp, recurso, diff resumido sem duplicar PII desnecessária) alinhado à preparação de FR52/FR54 ? sem UI de auditoria completa (épico 10).
3. API em **`GET /v1/me/organization`** e **`PATCH /v1/me/organization`** (nomes podem ajustar-se, mas **um único recurso ?organização atual?** ? sem `tenant_id` mutável no body).
4. OpenAPI atualizado; erros 401/403 com contrato canónico (Story 1.1); 422 com validação de campos.
5. **Admin web:** rota ?Definições da organização? com formulário Chakra (UX-DR3); estados honestos (UX-DR4); mensagens por campo.

## Tasks / Subtasks

- [x] **Contrato API** (AC: 1, 3, 4)
  - [x] `GET/PATCH /v1/me/organization` com modelos Pydantic (nome, timezone IANA, email operacional; lista fechada revisável no PRD).
- [x] **Persistência** (AC: 1, 2)
  - [x] Estender tabela `tenants` **ou** `organization_profile` 1:1 com `tenant_id`; migração Alembic.
  - [x] Tabela `audit_events` mínima (append-only) ou log via serviço de domínio ? sem gravar segredos.
- [x] **Autorização** (AC: 1)
  - [x] Papel `org_admin` (enum/string) validado no contexto de utilizador; matriz completa na 2.2.
  - [x] Stub dev conforme **Decisão VS** acima.
- [x] **RLS** (AC: 1)
  - [x] Políticas coerentes com 1.2; testes integração cross-tenant.
- [x] **Admin web** (AC: 5)
  - [x] React Router lazy; Chakra form; `fetch` ou cliente HTTP; tratamento 401/403/422.
- [x] **Testes**
  - [x] pytest: happy path, isolamento, validação, audit append; Vitest: formulário + mock API.

## Party Mode (CS) ? perspetivas

| Agente | Insight |
|--------|---------|
| **John** | FR1 é primeira feature visível ao admin; auth real era risco de *scope creep* ? **VS** fechou stub condicionado. |
| **Winston** | Audit mínimo: estrutura compatível com épico 10; sem PII em excesso. |
| **Sally** | Form: labels, erros por campo, sem *stack trace*. |
| **Mary** | Papel `org_admin` stub até 2.2 ? explícito. |
| **Amelia** | **Proibido** `tenant_id` no PATCH; tenant só do contexto de segurança/RLS. |

## Advanced Elicitation (CS)

- **Pre-mortem:** ?Admin edita org errada? ? RLS + testes negativos.
- **Red team:** ?Audit com dados sensíveis? ? diff resumido / hashing quando necessário.
- **First principles:** recurso **me/organization** único.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS** com decisão de auth documentada.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Path canónico `/v1/me/organization` ? evita IDs mutáveis no URL. |
| **Mary** | AC reescritos para remover ambiguidade ?ou path alinhado?. |
| **Amelia** | Critério explícito: body **sem** `tenant_id`. |
| **John** | Ordem 2.1 vs stub ? produto decide; VS dá **duas faixas** claras. |

### Advanced Elicitation (VS)

- **Socratic:** ?O que é ?admin autenticado? antes da 2.1?? ? stub com *guardrails* ou bloquear DS ? **stub guardado** como opção.
- **Pre-mortem:** ?Stub vai para produção? ? falha de config: `AUTH_DEV_STUB` ausente em runtime image.

### Checklist BMad (síntese)

| Risco | Mitigação VS |
|-------|----------------|
| Scope auth | Decisão VS + 2.1 recomendada |
| Vago API | Paths fixos nos AC |
| Audit LGPD | diff resumido |

## Dev Notes

### UX

- [Fonte: `ux-design-specification.md` ? shell, tokens, UX-DR4, UX-DR5]

### NFRs

- NFR-SEC-02; NFR-OPS (auditoria).

## Testing Requirements

- Integração: dois tenants + stub headers em dev; testes Vitest com mock.

## References

- [Source: `epics.md` ? Story 1.3]
- [Source: `architecture.md` ? REST `/v1`, OpenAPI]
- [Source: `v2/README.md` ? Docker]

## Dev Agent Record

### Agent Model Used

### Completion Notes List

- API: `GET`/`PATCH /v1/me/organization` com `tenant_session` + stub dev (`X-Dev-Tenant-Id`).
- Admin: `OrganizationSettingsPage` (MVP visual + `data-testid` ATDD).

### File List

- `v2/apps/api/app/api/routes/me_organization.py`
- `v2/apps/admin-web/src/features/organization/OrganizationSettingsPage.tsx`

---

## Change Log

- 2026-04-23: **[CS]**; `ready-for-dev`.
- 2026-04-23: **[VS]**; decisão auth + paths API + AC endurecidos; `atdd_ready: true`.
- 2026-04-23: **[AT]** API `test_epic1_story13_organization_atdd.py`; admin `src/atdd/epic1-organization-page.atdd.test.tsx`.
- 2026-04-23: **[DS]** implementação MVP + ATDD verde no `api-ci` / `admin-web-ci`; estado **`review`** (CR pendente).
- 2026-04-23: **[CR]** 422 canónico com `errors[]`; validação IANA `timezone` + strip email/display_name; OpenAPI 401/422; integração audit/no-op/cross-tenant; admin-web alinhado ao contrato + `role="alert"`; `status: done`.
