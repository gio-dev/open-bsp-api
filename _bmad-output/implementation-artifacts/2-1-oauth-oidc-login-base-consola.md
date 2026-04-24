---
story_key: 2-1-oauth-oidc-login-base-consola
epic: epic-2
status: done
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 1-2-modelo-tenant-rls-minima-prova-isolamento
  - 1-3-perfil-definicoes-organizacao
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 2.1 - OAuth / OIDC login base na consola

## Story

**Como** utilizador,  
**quero** **iniciar sessao** com **OAuth 2.0 / OIDC** (login base) na consola,  
**para** aceder a aplicacao com identidade enterprise-grade (preparacao SSO noutra historia).

## Acceptance Criteria

1. **Dado** configuracao de IdP / cliente OAuth conforme ADR, **quando** o utilizador conclui o login, **entao** a sessao da consola reflete identidade e **tenant** ativo, com **logout** a limpar estado sensivel (NFR-SEC-04).
2. Erros de auth na UI: **sem** stack trace; copy minima + `code` alinhado a UX-DR4, UX-DR6.
3. OpenAPI documenta rotas de auth/sessao sob prefixo acordado (ex. `/v1/auth/...` ou equivalente no CDA).

**Requisitos:** FR5. **NFRs:** NFR-SEC-01, NFR-SEC-04.  
**Nota:** SSO enterprise (SAML/OIDC) e historia distinta; nao bloquear 2.1.

## Tasks / Subtasks

- [x] Fluxo OAuth/OIDC (authorize, callback, token) na API `v2/apps/api`; estado sessao (cookie ou BFF conforme CDA).
- [x] Resolver **tenant ativo** apos auth (claims + membership; sem confiar so em query string).
- [x] Admin-web: ecran login + redirect + logout; TenantShell preparado para UX-DR5.
- [x] OpenAPI atualizado; erros canonicos 1.1 preservados.
- [x] pytest integracao onde fizer sentido; ATDD em `test_epic2_story21_oauth_oidc_login_atdd.py`.

### Review Findings

- [x] [Review][Patch] TenantShell: redirect para `/login?auth_error=session_unavailable` se `fetch` falhar ou resposta nao-401 nao-OK. [`TenantShell.tsx`]
- [x] [Review][Patch] `decode_payload`: `exp` obrigatorio, inteiro, `>0`; `<=0` ou ausente = `ValueError`. Testes em `test_auth_session_cookie.py`. [`session_cookie.py`]
- [x] [Review][Patch] `oidc_callback`: `logger.warning` com `exc_info` em falhas de token exchange e verificacao de id_token. [`auth_oidc.py`]
- [x] [Review][Patch] ATDD: assercoes com paths OpenAPI concretos (`/v1/auth/oidc/login`, callback, session, logout). [`test_epic2_story21_oauth_oidc_login_atdd.py`]
- [x] [Review][Defer] Cache in-memory de metadata OIDC sem TTL/invalidacao ? melhoria futura (rotacao JWKS) ? adiado, pre-existente no desenho actual

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Contrato OpenAPI e rotas `/v1` alinhados ao CDA; nao introduzir segundo formato de erro. |
| **Mary** | FR5 + NFR-SEC-01/04; SSO explicitamente fora de escopo desta story. |
| **John** | Desbloqueia 2.2; sem login estavel, RBAC nao tem valor. |
| **Sally** | UX-DR4/6 em falhas de IdP; mensagens honestas. |
| **Amelia** | Headers dev `X-Dev-*` podem coexistir com stub ate producao; documentar transicao. |

## Advanced Elicitation (CS)

- **Pre-mortem:** token em localStorage sem hardening - mitigar com politica clara (httpOnly cookie vs SPA) no ADR desta entrega.
- **Red team:** tenant escolhido pelo cliente apos login - mitigar com servidor a validar membership antes de fixar tenant na sessao.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS** - escopo 2.1 fechado; SSO excluido.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Prefixo `/v1` e documentacao OpenAPI obrigatorios na definicao de pronto. |
| **Amelia** | ATDD 2.1 verifica presenca de rotas auth/sessao no OpenAPI - aceite como RED minimo. |
| **Mary** | Rastreio FR5 / NFR-SEC coberto pelos AC. |

### Advanced Elicitation (VS)

- **Pre-mortem:** callback URL errada em staging - checklist deploy IdP na story ou runbook.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Regressao | Contrato erro 1.1 mantido. |
| Seguranca | Logout limpa estado sensivel; sem segredos em logs. |
| Stack | So `v2/apps/`. |

## Dev Notes - requisitos tecnicos

- Depende de modelo tenant/membership minimo (1.2, 1.3) para saber **quem** e **em que org** o utilizador opera apos OIDC.
- Ver `architecture.md` (auth, D2) e `project-context.md`.
- **Env API (exemplos):** `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET` (opcional cliente publico), `OIDC_REDIRECT_URI` (recomendado: mesmo host que a SPA com proxy Vite, ex. `http://localhost:5173/v1/auth/oidc/callback`), `SESSION_SIGNING_SECRET`, `CONSOLE_POST_LOGIN_REDIRECT`, `CONSOLE_CORS_ORIGIN` (se SPA chama API noutro origin), `SESSION_COOKIE_SECURE=false` em dev HTTP.
- **Claim opcional** `OIDC_TENANT_CLAIM` (default `https://openbsp.dev/active_tenant_id`): UUID validado contra `tenant_memberships`; sem claim, um unico membership `org_admin` ou escolha deterministica se varios.
- **Stub dev:** com `AUTH_DEV_STUB=true`, headers `X-Dev-*` continuam a satisfazer `console_org_admin_context`; sem headers, cookie de sessao (Epic 2).

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic2_story21_oauth_oidc_login_atdd.py`
- Integracao: `v2/apps/api/tests/integration/test_story21_oidc_callback_session.py` (requer `DATABASE_URL` + migracao 005 + seed)
- Ver `_bmad-output/test-artifacts/V2/atdd-checklist-epic-2.md`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 2.1
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

Composer (DS Story 2.1)

### Completion Notes List

- Cookie assinado HMAC (`obsp_session`) + handshake PKCE em `obsp_oidc`; rotas `/v1/auth/oidc/login`, `callback`, `session`, `logout`.
- Tabelas `console_users`, `tenant_memberships` (Alembic 005); `platform_session` para escrita sem GUC tenant; resolucao de tenant via memberships + claim opcional.
- `console_org_admin_context`: stub dev se headers presentes; senao sessao; `/v1/me/*` alinhado.
- Admin-web: `LoginPage`, `TenantShell`, `VITE_AUTH_MODE=session` para gate; `consoleAuth` partilhado em org/WABA; logout na barra.
- Dependencias: `httpx`, `pyjwt[crypto]` (projeto).
- 2026-04-24: correcoes pos code review (TenantShell, `decode_payload` exp, logging OIDC, ATDD paths).

### File List

- `v2/apps/api/pyproject.toml`
- `v2/apps/api/alembic/versions/005_console_users_memberships.py`
- `v2/apps/api/app/core/config.py`
- `v2/apps/api/app/db/models.py`
- `v2/apps/api/app/db/session.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/app/ci_seed.py`
- `v2/apps/api/app/auth/__init__.py`
- `v2/apps/api/app/auth/session_cookie.py`
- `v2/apps/api/app/auth/oidc_flow.py`
- `v2/apps/api/app/auth/console_identity.py`
- `v2/apps/api/app/api/routes/auth_oidc.py`
- `v2/apps/api/app/tenancy/deps.py`
- `v2/apps/api/app/api/routes/me_organization.py`
- `v2/apps/api/app/api/routes/me_waba.py`
- `v2/apps/api/tests/conftest.py`
- `v2/apps/api/tests/test_auth_session_cookie.py`
- `v2/apps/api/tests/test_auth_routes.py`
- `v2/apps/api/tests/integration/test_story21_oidc_callback_session.py`
- `v2/apps/admin-web/src/App.tsx`
- `v2/apps/admin-web/src/features/auth/LoginPage.tsx`
- `v2/apps/admin-web/src/features/shell/TenantShell.tsx`
- `v2/apps/admin-web/src/lib/consoleAuth.ts`
- `v2/apps/admin-web/src/features/organization/OrganizationSettingsPage.tsx`
- `v2/apps/admin-web/src/features/waba/WabaPhoneNumberListPage.tsx`
- `v2/apps/admin-web/src/vite-env.d.ts`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/2-1-oauth-oidc-login-base-consola.md`

---

## Change Log

- 2026-04-23: **[CS]** story individual (nao batch); Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `v2/apps/api/tests/atdd/test_epic2_story21_oauth_oidc_login_atdd.py`.
- 2026-04-23: **[DS]** implementacao OIDC + sessao + admin-web; status `review`.
- 2026-04-24: **[CR]** itens de patch do code review corrigidos; story `done`.
