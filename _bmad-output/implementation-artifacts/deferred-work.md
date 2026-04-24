# Deferred work (accumulated)

## Deferred from: code review of 2-1-oauth-oidc-login-base-consola.md (2026-04-24)

- **Metadata OIDC in-memory sem TTL:** cache `_metadata_cache` em `oidc_flow.fetch_oidc_metadata` não invalida; aceitável no MVP, rever se IdP roda rotação de issuer/JWKS frequente.

## Deferred from: code review of 2-2-matriz-papeis-permissoes.md (2026-04-24)

- **Emails na lista de membros:** `GET /v1/me/members` devolve email em claro; aceitável para `org_admin` no MVP; rever mascaramento ou minimização se política de dados o exigir.
