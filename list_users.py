import psycopg2
import os

# Use the correct DATABASE_URL with port 5501 and database class_vision
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# First, let's see what columns exist in usuarios table
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'usuarios'
    ORDER BY ordinal_position
""")
print('\n=== ESTRUCTURA TABLA USUARIOS ===\n')
for row in cur.fetchall():
    print(f'Columna: {row[0]} ({row[1]})')
print('\n' + '='*50 + '\n')

# Now select users with existing columns including email
cur.execute('SELECT codigo_usuario, nombre_completo, email FROM usuarios LIMIT 10')
print('\n=== USUARIOS DISPONIBLES ===\n')
for row in cur.fetchall():
    print(f'Código: {row[0]}')
    print(f'Nombre: {row[1]}')
    print(f'Email: {row[2]}')
    print('-' * 40)
cur.close()
conn.close()
