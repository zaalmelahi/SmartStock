#!/usr/bin/env bash
set -e

chmod +777 -R /app

echo "Waiting for database..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
    sleep 0.1
done
echo "✓ Database is ready"

# Collect static files (ignore if not available)
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "⚠ collectstatic not available or failed, continuing..."

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server based on environment
echo "Starting server..."
if [ "$DJANGO_ENV" = "production" ] || [ "$DJANGO_ENV" = "prod" ]; then
    echo "🚀 Starting Gunicorn (Production Mode)"
    exec gunicorn InventoryMS.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers ${GUNICORN_WORKERS:-4} \
      --threads ${GUNICORN_THREADS:-2} \
      --timeout ${GUNICORN_TIMEOUT:-120} \
      --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
      --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-50} \
      --access-logfile - \
      --error-logfile - \
      --log-level info
elif [ "$DJANGO_ENV" = "production-asgi" ] || [ "$DJANGO_ENV" = "prod-asgi" ]; then
    echo "🚀 Starting Uvicorn (Production ASGI Mode)"
    exec gunicorn InventoryMS.asgi:application \
      --bind 0.0.0.0:8000 \
      --workers ${GUNICORN_WORKERS:-4} \
      --timeout ${GUNICORN_TIMEOUT:-120} \
      --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
      --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-50} \
      --access-logfile - \
      --error-logfile - \
      --log-level info \
      --worker-class uvicorn.workers.UvicornWorker
else
    echo "🔧 Starting Django Dev Server (Development Mode)"
    echo "⚠️  WARNING: Do not use in production!"
    exec python manage.py runserver 0.0.0.0:8000
fi
