import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("Limpiando datos de prueba...")

# Orden correcto para evitar foreign keys
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
    'asistencia_log',  # Antes de códigos_temporales
    'codigos_temporales',
]

for table in tables_order:
    cur.execute(f'DELETE FROM {table}')
    print(f"  ✅ {table}")

# Limpiar relaciones de tutores en estudiantes
cur.execute('UPDATE estudiantes SET id_tutor = NULL')
print(f"  ✅ estudiantes (id_tutor = NULL)")

# Ahora sí podemos eliminar tutores
cur.execute('DELETE FROM tutores')
print(f"  ✅ tutores")

# Resetear puntos
cur.execute('UPDATE estudiantes SET puntos_acumulados = 0, nivel = 1')
print(f"  ✅ estudiantes (puntos reseteados)")

conn.commit()
print("\n✅ Datos de prueba eliminados correctamente")
conn.close()
