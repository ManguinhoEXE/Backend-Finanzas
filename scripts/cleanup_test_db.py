"""Script para limpiar la base de datos de test.

Requiere las siguientes variables de entorno:
  DB_NAME, USER, PASSWORD, HOST, DB_PORT

Ejemplo:
  DB_NAME=postgres USER=postgres.xxx PASSWORD=xxx HOST=xxx DB_PORT=6543 python scripts/cleanup_test_db.py
"""
import os
import time
import psycopg2

DB_NAME = os.environ.get('DB_NAME', 'postgres')
USER = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')
HOST = os.environ.get('HOST')
DB_PORT = os.environ.get('DB_PORT', '6543')

if not all([USER, PASSWORD, HOST]):
    print("Error: Faltan variables de entorno. Requiere: USER, PASSWORD, HOST")
    print("Ejemplo: DB_NAME=postgres USER=postgres.xxx PASSWORD=xxx HOST=xxx DB_PORT=6543 python scripts/cleanup_test_db.py")
    exit(1)

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=DB_PORT
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = 'test_postgres'
""")
terminated = cur.fetchall()
print(f'Conexiones terminadas: {terminated}')

time.sleep(3)

try:
    cur.execute("DROP DATABASE IF EXISTS test_postgres")
    print('Base de datos test_postgres eliminada correctamente')
except Exception as e:
    print(f'Error al eliminar: {e}')
    time.sleep(5)
    cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'test_postgres'")
    time.sleep(3)
    cur.execute("DROP DATABASE IF EXISTS test_postgres")
    print('Base de datos test_postgres eliminada correctamente (segundo intento)')

conn.close()
