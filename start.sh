#!/bin/sh
set -e

SERVICE="${RAILWAY_SERVICE_NAME:-web}"
echo "=== CNIAH startup — service: $SERVICE ==="

# ── Worker Celery ────────────────────────────────────────────────────────────
if [ "$SERVICE" = "worker" ]; then
    echo "Starting Celery worker..."
    exec celery -A config worker \
        --loglevel=info \
        --concurrency=2
fi

# ── Web (défaut) ─────────────────────────────────────────────────────────────
echo "Running migrations..."
python manage.py migrate --noinput

echo "Running init_site..."
python init_site.py

echo "Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
