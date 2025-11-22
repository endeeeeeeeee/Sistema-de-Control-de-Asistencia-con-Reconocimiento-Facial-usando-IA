import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print('\n' + '='*60)
print('VERIFICACIÓN DE SINCRONIZACIÓN - BASE DE DATOS')
print('='*60)

# 1. Tabla usuarios
print('\n📊 TABLA: usuarios')
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'usuarios'
    ORDER BY ordinal_position
""")
print(f"   Columnas: {cur.rowcount}")
for col in cur.fetchall():
    print(f"   - {col[0]} ({col[1]}) {'NULL' if col[2]=='YES' else 'NOT NULL'}")

# 2. Tabla sesiones_activas
print('\n📊 TABLA: sesiones_activas')
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'sesiones_activas'
    ORDER BY ordinal_position
""")
if cur.rowcount > 0:
    print(f"   Columnas: {cur.rowcount}")
    for col in cur.fetchall():
        print(f"   - {col[0]} ({col[1]}) {'NULL' if col[2]=='YES' else 'NOT NULL'}")
else:
    print("   ⚠️ Tabla no existe")

# 3. Contar usuarios activos
cur.execute("SELECT COUNT(*) FROM usuarios WHERE activo = TRUE")
count = cur.fetchone()[0]
print(f'\n👥 USUARIOS ACTIVOS: {count}')

# 4. Contar sesiones activas
try:
    cur.execute("SELECT COUNT(*) FROM sesiones_activas WHERE activa = TRUE")
    count = cur.fetchone()[0]
    print(f'🔑 SESIONES ACTIVAS: {count}')
except:
    print('🔑 SESIONES ACTIVAS: Tabla no existe')

# 5. Verificar campos críticos
print('\n✅ VERIFICACIÓN DE CAMPOS CRÍTICOS:')
cur.execute("SELECT email, codigo_usuario FROM usuarios LIMIT 1")
if cur.rowcount > 0:
    print('   ✓ email existe')
    print('   ✓ codigo_usuario existe')
    print('   ✓ Login puede usar email O codigo_usuario')
else:
    print('   ⚠️ No hay usuarios')

print('\n' + '='*60)
print('SINCRONIZACIÓN COMPLETADA')
print('='*60)

cur.close()
conn.close()
