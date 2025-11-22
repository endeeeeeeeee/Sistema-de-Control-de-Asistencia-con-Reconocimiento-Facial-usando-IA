"""
Limpia TODOS los datos de TODAS las tablas
Deja solo la estructura de la base de datos
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("\n" + "="*100)
print("🗑️  LIMPIANDO TODA LA BASE DE DATOS")
print("="*100)

# Orden correcto para evitar foreign key violations
tables_order = [
    'audit_log',
    'asistente_historial',
    'reportes_generados',
    'estadisticas_diarias',
    'ranking_mensual',
    'estudiantes_badges',
    'alertas_desercion',
    'justificaciones',
    'notificaciones_internas',
    'asistencia_virtual',
    'asistencia_log',
    'codigos_temporales',
    'inscripciones',           # Antes de estudiantes y materias
    'materias',                # Antes de personal_admin
    'badges',                  # Independiente
    'sesiones_activas',        # Antes de personal_admin
    'sys_config',              # Antes de personal_admin
]

print("\n🗑️  Eliminando datos de tablas con foreign keys...")
for table in tables_order:
    cur.execute(f'DELETE FROM {table}')
    count = cur.rowcount
    print(f"  ✅ {table:<30} ({count} registros eliminados)")

# Limpiar relaciones antes de eliminar tutores y estudiantes
print("\n🗑️  Limpiando relaciones...")
cur.execute('UPDATE estudiantes SET id_tutor = NULL')
print(f"  ✅ estudiantes.id_tutor = NULL")

cur.execute('DELETE FROM tutores')
count = cur.rowcount
print(f"  ✅ tutores                        ({count} registros eliminados)")

cur.execute('DELETE FROM estudiantes')
count = cur.rowcount
print(f"  ✅ estudiantes                    ({count} registros eliminados)")

cur.execute('DELETE FROM personal_admin')
count = cur.rowcount
print(f"  ✅ personal_admin                 ({count} registros eliminados)")

conn.commit()

# Verificar que todo esté vacío
print("\n" + "="*100)
print("📊 VERIFICANDO LIMPIEZA")
print("="*100)

cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")

tables = cur.fetchall()
total_registros = 0

print("\n📋 Estado de las tablas:")
for (table_name,) in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    count = cur.fetchone()[0]
    total_registros += count
    
    if count > 0:
        print(f"  ⚠️  {table_name:<30} {count:>5} registros (NO LIMPIADA)")
    else:
        print(f"  ✅ {table_name:<30} {count:>5} registros")

print("\n" + "="*100)
if total_registros == 0:
    print("✅ BASE DE DATOS COMPLETAMENTE LIMPIA")
    print("📊 Todas las tablas están vacías")
    print("🏗️  Estructura preservada y lista para redefinir")
else:
    print(f"⚠️  Aún quedan {total_registros} registros en algunas tablas")

print("="*100 + "\n")

cur.close()
conn.close()
