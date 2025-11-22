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

# Reset password for admin user
new_password = "admin123"
password_hash = hash_password(new_password)

cur.execute("""
    UPDATE usuarios 
    SET password_hash = %s 
    WHERE codigo_usuario = 'USER-2025-001'
""", (password_hash,))

conn.commit()

print('\n✅ Contraseña actualizada exitosamente!\n')
print('='*50)
print('CREDENCIALES DE ADMINISTRADOR:')
print('='*50)
print(f'Código de Usuario: USER-2025-001')
print(f'Contraseña: {new_password}')
print('='*50)
print('\n💡 Usa estas credenciales para iniciar sesión en http://127.0.0.1:5001/login\n')

cur.close()
conn.close()
