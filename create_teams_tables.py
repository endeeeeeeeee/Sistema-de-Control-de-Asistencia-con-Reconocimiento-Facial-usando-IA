import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print('\n' + '='*60)
print('CREANDO TABLAS DE EQUIPOS (GAMIFICACIÓN)')
print('='*60)

# Crear tabla de equipos
print('\n📊 Creando tabla: equipos')
cur.execute("""
    CREATE TABLE IF NOT EXISTS equipos (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        codigo_invitacion VARCHAR(20) UNIQUE NOT NULL,
        tipo VARCHAR(50) DEFAULT 'estudio',
        descripcion TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        puntos_totales INTEGER DEFAULT 0,
        activo BOOLEAN DEFAULT TRUE
    )
""")
print('   ✅ Tabla equipos creada')

# Crear tabla de miembros de equipo
print('\n📊 Creando tabla: miembros_equipo')
cur.execute("""
    CREATE TABLE IF NOT EXISTS miembros_equipo (
        id SERIAL PRIMARY KEY,
        equipo_id INTEGER REFERENCES equipos(id) ON DELETE CASCADE,
        usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
        rol VARCHAR(20) DEFAULT 'miembro',
        fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        puntos_individuales INTEGER DEFAULT 0,
        activo BOOLEAN DEFAULT TRUE,
        UNIQUE(equipo_id, usuario_id)
    )
""")
print('   ✅ Tabla miembros_equipo creada')

# Crear índices
print('\n📊 Creando índices')
cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_equipos_codigo ON equipos(codigo_invitacion);
    CREATE INDEX IF NOT EXISTS idx_miembros_equipo ON miembros_equipo(equipo_id, usuario_id);
    CREATE INDEX IF NOT EXISTS idx_miembros_usuario ON miembros_equipo(usuario_id);
""")
print('   ✅ Índices creados')

conn.commit()

# Verificar tablas
print('\n📊 Verificando tablas creadas')
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name IN ('equipos', 'miembros_equipo')
    ORDER BY table_name
""")

for row in cur.fetchall():
    print(f'   ✓ {row[0]}')

# Mostrar estructura
print('\n📊 Estructura tabla equipos:')
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'equipos'
    ORDER BY ordinal_position
""")
for col in cur.fetchall():
    print(f'   - {col[0]} ({col[1]}) {"NULL" if col[2]=="YES" else "NOT NULL"}')

print('\n📊 Estructura tabla miembros_equipo:')
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'miembros_equipo'
    ORDER BY ordinal_position
""")
for col in cur.fetchall():
    print(f'   - {col[0]} ({col[1]}) {"NULL" if col[2]=="YES" else "NOT NULL"}')

print('\n' + '='*60)
print('TABLAS DE EQUIPOS CREADAS EXITOSAMENTE')
print('='*60)

cur.close()
conn.close()
