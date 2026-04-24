#!/bin/sh
set -e

if [ "${DB_ENGINE:-}" = "django.db.backends.postgresql" ]; then
  echo "Waiting for PostgreSQL at ${DB_HOST:-db}:${DB_PORT:-5432}..."
  until pg_isready \
    -h "${DB_HOST:-db}" \
    -p "${DB_PORT:-5432}" \
    -U "${DB_USER:-postgres}" \
    -d "${DB_NAME:-encomiendas_db}" >/dev/null 2>&1
  do
    sleep 1
  done
fi

python manage.py migrate --noinput

exec "$@"
