#!/bin/sh
set -e
if [ -n "$ALEMBIC_SYNC_URL" ]; then
  echo "Running database migrations (alembic upgrade head)..."
  alembic upgrade head
fi
exec "$@"
