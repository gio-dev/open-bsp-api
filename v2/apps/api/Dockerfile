# API Open BSP ? multi-stage: runtime (prod), ci (ruff+pytest), dev (reload)
FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# --- CI: lint + test (sempre via Docker) ---
FROM base AS ci
COPY tests ./tests
RUN pip install --no-cache-dir ".[dev]"
CMD ["sh", "-c", "ruff check . && ruff format --check . && alembic upgrade head && python -m app.ci_seed && pytest -q -m \"not atdd or epic1_atdd\""]

# --- Dev: mesmo runtime + ferramentas de dev (volume monta o codigo) ---
FROM base AS dev
COPY tests ./tests
RUN pip install --no-cache-dir ".[dev]"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# --- Producao ---
FROM base AS runtime

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
