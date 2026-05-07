#!/bin/sh
set -e

echo "=== CNIAH startup ==="
echo "Running migrations..."
python manage.py migrate --noinput

echo "Migrations OK. Running init_site..."
python init_site.py

echo "Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
