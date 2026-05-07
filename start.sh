#!/bin/sh
set -e

SERVICE="${RAILWAY_SERVICE_NAME:-web}"
echo "=== CNIAH startup — service: $SERVICE ==="

# ── Worker Celery ────────────────────────────────────────────────────────────
if [ "$SERVICE" = "worker" ]; then
    echo "Starting health check server on port ${PORT:-8080}..."
    python3 -c "
import http.server, os
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(s):
        s.send_response(200)
        s.end_headers()
        s.wfile.write(b'worker ok')
    def log_message(*a): pass
http.server.HTTPServer(('', int(os.getenv('PORT', 8080))), H).serve_forever()
" &
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
