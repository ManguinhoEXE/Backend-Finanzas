#!/bin/bash
set -e

echo "============================================"
echo "  Finanzas Backend — Iniciando aplicacion"
echo "============================================"

# Puerto por defecto (Render usa PORT, local usa 8000)
PORT=${PORT:-8000}

# Esperar a que PostgreSQL este listo (solo si no es Supabase)
if [ "$DB_HOST" != "aws-1-us-east-2.pooler.supabase.com" ]; then
    echo "Esperando a que PostgreSQL este disponible en $DB_HOST:$PORT_DB..."
    until python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        dbname='$DB_NAME',
        user='$USER',
        password='$PASSWORD',
        host='$DB_HOST',
        port='$PORT'
    )
    conn.close()
    print('PostgreSQL conectado exitosamente.')
except psycopg2.OperationalError:
    raise SystemExit(1)
" 2>/dev/null; do
        echo "  PostgreSQL no disponible, reintentando en 2s..."
        sleep 2
    done
fi

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estaticos
echo "Recopilando archivos estaticos..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo "============================================"
echo "  Iniciando servidor en puerto $PORT..."
echo "============================================"

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
