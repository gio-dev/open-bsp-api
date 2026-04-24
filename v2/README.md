# Open BSP - stack alvo (v2)

Monorepo: **todos os comandos de execucao, testes e CI local passam por Docker.**

| Pasta | Stack |
| ----- | ----- |
| `apps/api` | FastAPI, Uvicorn, pytest, Ruff (targets Docker: `runtime`, `ci`, `dev`) |
| `apps/admin-web` | Vite, React, Chakra, Vitest, ESLint (targets: `admin-runtime`, `admin-ci`, dev image) |

## Producao local (API + Nginx estatico)

Na pasta **`v2/`**:

```bash
docker compose up --build
```

| Servico | URL |
| ------- | ----- |
| API | http://127.0.0.1:8000 (`/v1/health`, `/docs`) |
| Admin (Nginx) | http://127.0.0.1:8080 |

## Desenvolvimento (hot-reload, sempre Docker)

```bash
cd v2
docker compose -f docker-compose.dev.yml up --build
```

| Servico | URL |
| ------- | ----- |
| API (reload) | http://127.0.0.1:8000 |
| Vite | http://127.0.0.1:5173 |

## Qualidade (Ruff, pytest, ESLint, Vitest, build) ? local via Docker

```bash
cd v2
docker compose --profile ci build api-ci admin-web-ci
docker compose --profile ci run --rm api-ci
docker compose --profile ci run --rm --no-deps admin-web-ci
```

Nao e necessario `venv` nem `npm install` no host para estes passos.

O job `api-ci` sobe o servico **`postgres`** (Compose **profile `ci`**) e define:

- **`DATABASE_URL`**: `postgresql+asyncpg://app_runtime:...@postgres:5432/openbsp_test` (API em runtime com RLS).
- **`ALEMBIC_SYNC_URL`**: `postgresql://postgres:postgres@postgres:5432/openbsp_test` (Alembic e *seed* usam este DSN *sync*; no `env.py` converte-se para `postgresql+psycopg` para o SQLAlchemy do Alembic).

Migracoes: dentro da imagem/API, `alembic upgrade head` corre antes dos testes. Integracao RLS: `pytest -m integration` quando `DATABASE_URL` e `ALEMBIC_SYNC_URL` estao definidos (como no `api-ci`).

### Resolucao de tenant (dev / ATDD, ate Epic 2)

- Definir `AUTH_DEV_STUB=true` (ja usado nos testes ATDD via `conftest`).
- Enviar o UUID do tenant no header **`X-Dev-Tenant-Id`** nas rotas `/v1/me/*` que dependem de contexto.
- **Producao:** este header deixa de ser a fonte de verdade; substituir por autenticacao OIDC e claims de organizacao (ver epico 2 no planeamento).

### Webhook WhatsApp (Epico 3 / preparacao API)

Variaveis de ambiente (API):

- `WHATSAPP_WEBHOOK_VERIFY_TOKEN` ? token Meta no GET `hub.verify_token`.
- `WHATSAPP_WEBHOOK_APP_SECRET` ? App Secret para validar `X-Hub-Signature-256` no POST; **obrigatorio em producao** (sem secret o POST nao exige HMAC, apenas para dev).
- `WHATSAPP_WEBHOOK_MAX_BODY_BYTES` ? tamanho maximo do corpo POST (default 2 MiB); acima disto responde `413`.

### Smoke (subconjunto minimo, mais rapido)

API (com Ruff, alinhado ao gate da imagem `ci`):

```bash
cd v2
docker compose --profile ci run --rm api-ci sh -c "ruff check . && ruff format --check . && pytest -q -m smoke"
```

Admin web:

```bash
cd v2
docker compose --profile ci run --rm --no-deps admin-web-ci sh -c "npm run test:smoke"
```

Convenções de pastas e nomes: `_bmad-output/test-artifacts/V2/test-framework.md`.

## CI no GitHub

Workflow `.github/workflows/ci-v2-docker.yml`: apenas `docker compose` na pasta `v2/`.

Gates (Ruff, pytest com **policy OpenAPI** e **ATDD**, ESLint, Vitest, build) e **regra de merge com ATDD vermelho** estão descritos em `_bmad-output/test-artifacts/V2/ci-pipeline.md`.

## Ficheiros Docker

- `docker-compose.yml` ? stack `runtime` (producao local)
- `docker-compose.dev.yml` ? API `dev` + Vite
- `apps/api/Dockerfile` ? targets `runtime`, `ci`, `dev`
- `apps/admin-web/Dockerfile` ? targets `admin-runtime`, `admin-ci`
- `apps/admin-web/Dockerfile.dev` ? servidor Vite para dev
