import psycopg2
import os
import hashlib

# Use the correct DATABASE_URL with port 5501 and database class_vision
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')

def hash_password(password):
    """Hash de contraseña con SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Show all users with their emails
cur.execute('SELECT codigo_usuario, nombre_completo, email FROM usuarios')
print('\n=== USUARIOS EN LA BASE DE DATOS ===\n')
for row in cur.fetchall():
    print(f'Código: {row[0]}')
    print(f'Nombre: {row[1]}')
    print(f'Email: {row[2]}')
    print('-' * 50)

# Reset passwords for all users
users_passwords = [
    ('USER-2025-001', 'admin123', 'Administrador'),
    ('USER-2025-002', 'itzan123', 'Itzan Valdivia'),
    ('USER-2025-003', 'henrry123', 'Henrry Cavil')
]

print('\n=== RESETEANDO CONTRASEÑAS ===\n')

for codigo, password, nombre in users_passwords:
    password_hash = hash_password(password)
    cur.execute("""
        UPDATE usuarios 
        SET password_hash = %s 
        WHERE codigo_usuario = %s
    """, (password_hash, codigo))
    print(f'✅ {nombre} ({codigo}): contraseña = {password}')

conn.commit()

print('\n' + '='*60)
print('TODAS LAS CONTRASEÑAS HAN SIDO RESETEADAS')
print('='*60)
print('\n📋 CREDENCIALES DISPONIBLES:\n')

cur.execute('SELECT codigo_usuario, nombre_completo, email FROM usuarios ORDER BY id')
for row in cur.fetchall():
    # Find password for this user
    password = next((p[1] for p in users_passwords if p[0] == row[0]), 'N/A')
    print(f'👤 {row[1]}')
    print(f'   Email: {row[2]}')
    print(f'   Código: {row[0]}')
    print(f'   Contraseña: {password}')
    print()

print('='*60)
print('💡 Usa cualquiera de estos emails o códigos para login')
print('='*60)

cur.close()
conn.close()
