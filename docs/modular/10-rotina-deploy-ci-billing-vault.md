# Rotina: deploy, CI, vault e billing

## Deploy contínuo (GitHub Actions)

**Arquivo**: `.github/workflows/release.yml`

Em **push** para **`main`** ou **`develop`**:

1. `supabase link --project-ref $SUPABASE_PROJECT_ID`
2. **`supabase db push`**
3. **`supabase functions deploy`**
4. Instala `postgresql-client` e executa **`.github/workflows/deploy-vault-secrets.sh`** ? sincroniza segredos necessários ao runtime (incl. URL/token das Edge Functions usados pelos triggers).
5. Se secrets Meta existem no GitHub, **`supabase secrets set`** para `META_*` e `WHATSAPP_VERIFY_TOKEN`.

**Ambiente GitHub**: `Production` para `main`, `Staging` para `develop` (expressão ternária no workflow).

## Vault e triggers

Funções `edge_function` e `dispatcher_edge_function` leem:

- `vault.decrypted_secrets` onde `name = 'edge_functions_url'`
- `vault.decrypted_secrets` onde `name = 'edge_functions_token'`

Sem isso, triggers **não** conseguem chamar Deno de forma autenticada.

## Billing

Schema separado **`billing`** (`supabase/schemas/06_billing/`):

- Produtos, planos, tiers, contas, uso, ledger, faturas, pagamentos.
- Grants específicos para `service_role` e leitura para papéis anon/authenticated onde aplicável.

O `media-preprocessor` e o `agent-client` podem interagir com medição de custo/créditos conforme implementação atual (ver migrations recentes de billing).

**Regra de projeto** (CLAUDE.md): **não editar migrations aplicadas**; novas mudanças via `supabase db diff` após editar schemas.

## Observabilidade

- **Stdout** das Edge Functions: logs via API de analytics Supabase (exemplo em `CLAUDE.md`).
- **`public.logs`**: erros aplicacionais gravados pelas funções (webhook Meta, etc.).

## Referências

- `CLAUDE.md` na raiz
- [01](./01-arquitetura-reativa-visao-geral.md) (vault)
- [06](./06-rotina-media-preprocessor.md) (custos Gemini)
