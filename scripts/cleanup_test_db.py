"""Script para limpiar la base de datos de test."""
import time
import psycopg2

# Conectar a PostgreSQL
conn = psycopg2.connect(
    dbname='postgres',
    user='postgres.yrsmexabolllfvlrdgcp',
    password='Dybala2003###',
    host='aws-1-us-east-2.pooler.supabase.com',
    port='6543'
)
conn.autocommit = True
cur = conn.cursor()

# Terminar conexiones activas a test_postgres
cur.execute("""
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = 'test_postgres'
""")
terminated = cur.fetchall()
print(f'Conexiones terminadas: {terminated}')

# Esperar a que se libere
time.sleep(3)

# Intentar eliminar la base de datos
try:
    cur.execute("DROP DATABASE IF EXISTS test_postgres")
    print('Base de datos test_postgres eliminada correctamente')
except Exception as e:
    print(f'Error al eliminar: {e}')
    # Intentar de nuevo después de más tiempo
    time.sleep(5)
    cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'test_postgres'")
    time.sleep(3)
    cur.execute("DROP DATABASE IF EXISTS test_postgres")
    print('Base de datos test_postgres eliminada correctamente (segundo intento)')

conn.close()
