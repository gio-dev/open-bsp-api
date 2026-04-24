---
title: ATDD Checklist - Epic 2
project: open-bsp-api
date: 2026-04-23
workflow: bmad-testarch-atdd
---

# ATDD Epic 2 - fase vermelha (por story)

## Resumo

Um modulo pytest **por story** (2.1 -> 2.4), apos **Create Story** e **Validate Story** de cada uma. Execucao: Docker em `v2/` (ver `ci-pipeline.md`).

## Estado esperado do CI

- **`api-ci`:** `pytest` com `tests/atdd/` falha ate DS implementar auth, RBAC, api-keys, webhook-secrets.

## API - ficheiros

| Story | Ficheiro |
|-------|----------|
| 2.1 | `v2/apps/api/tests/atdd/test_epic2_story21_oauth_oidc_login_atdd.py` |
| 2.2 | `v2/apps/api/tests/atdd/test_epic2_story22_matriz_papeis_atdd.py` |
| 2.3 | `v2/apps/api/tests/atdd/test_epic2_story23_chaves_api_atdd.py` |
| 2.4 | `v2/apps/api/tests/atdd/test_epic2_story24_webhook_secrets_atdd.py` |

Marcador: `@pytest.mark.atdd`.

## Ordem GREEN sugerida

1. **2.1** - OIDC/OAuth consola + sessao + OpenAPI.
2. **2.2** - memberships + 403 em recurso proibido.
3. **2.3** - POST `/v1/me/api-keys` + secret once.
4. **2.4** - rotacao segredo webhook + coexistencia.

## Stories

- `_bmad-output/implementation-artifacts/2-1-oauth-oidc-login-base-consola.md`
- `_bmad-output/implementation-artifacts/2-2-matriz-papeis-permissoes.md`
- `_bmad-output/implementation-artifacts/2-3-chaves-api-emissao-revogacao.md`
- `_bmad-output/implementation-artifacts/2-4-segredos-verificacao-webhooks.md`
