"""Alembic migration environment (sync URL via ALEMBIC_SYNC_URL)."""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def _sqlalchemy_sync_url(raw: str) -> str:
    """SQLAlchemy 2 defaults postgresql:// to psycopg2; we use psycopg3."""
    if raw.startswith("postgresql+") or raw.startswith("postgres+"):
        return raw
    if raw.startswith("postgresql://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql://")
    if raw.startswith("postgres://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgres://")
    return raw


def run_migrations_offline() -> None:
    raw = os.environ.get("ALEMBIC_SYNC_URL") or config.get_main_option("sqlalchemy.url")
    url = _sqlalchemy_sync_url(raw)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    raw = os.environ.get("ALEMBIC_SYNC_URL") or config.get_main_option("sqlalchemy.url")
    url = _sqlalchemy_sync_url(raw)
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
