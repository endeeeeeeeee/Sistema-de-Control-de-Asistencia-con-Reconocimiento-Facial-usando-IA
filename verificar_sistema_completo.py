"""
Script de verificación completa del sistema
"""
from sqlalchemy import create_engine, text, inspect
import json

print("=" * 60)
print("VERIFICACIÓN COMPLETA DEL SISTEMA CLASS VISION")
print("=" * 60)

# 1. VERIFICAR BASE DE DATOS
print("\n1. VERIFICANDO BASE DE DATOS...")
try:
    engine = create_engine('postgresql://postgres:1234@localhost:5432/asistencia_nur')
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    print(f"   ✓ Conexión exitosa")
    print(f"   ✓ Tablas encontradas: {len(tables)}")
    
    for table in sorted(tables):
        columns = inspector.get_columns(table)
        print(f"      - {table} ({len(columns)} columnas)")
    
    # Verificar datos críticos
    with engine.connect() as conn:
        usuarios = conn.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
        equipos = conn.execute(text("SELECT COUNT(*) FROM equipos")).scalar()
        membresias = conn.execute(text("SELECT COUNT(*) FROM membresias")).scalar()
        asistencias = conn.execute(text("SELECT COUNT(*) FROM asistencia_log")).scalar()
        
        print(f"\n   DATOS:")
        print(f"      - Usuarios registrados: {usuarios}")
        print(f"      - Equipos creados: {equipos}")
        print(f"      - Membresías activas: {membresias}")
        print(f"      - Asistencias registradas: {asistencias}")
        
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# 2. VERIFICAR SERVIDOR
print("\n2. VERIFICANDO SERVIDOR...")
print("   ⚠ Servidor debe estar corriendo en http://127.0.0.1:5001")
print("   (Verificación manual requerida)")

# 3. VERIFICAR ARCHIVOS CRÍTICOS
print("\n3. VERIFICANDO ARCHIVOS DEL SISTEMA...")
import os
from pathlib import Path

archivos_criticos = [
    "mobile_server.py",
    "api_routes_flexible.py",
    "database_models.py",
    "config/recognition_config.json",
    "templates/dashboard_flexible.html",
    "templates/login_flexible.html",
    "templates/tomar_asistencia.html",
    "templates/reportes.html",
]

for archivo in archivos_criticos:
    path = Path(archivo)
    if path.exists():
        size = path.stat().st_size
        print(f"   ✓ {archivo} ({size:,} bytes)")
    else:
        print(f"   ✗ {archivo} - NO ENCONTRADO")

# 4. VERIFICAR CONFIGURACIÓN DE RECONOCIMIENTO
print("\n4. VERIFICANDO CONFIGURACIÓN DE RECONOCIMIENTO FACIAL...")
try:
    with open('config/recognition_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        reconocimiento = config.get('reconocimiento_facial', {})
        print(f"   ✓ Umbral mínimo: {reconocimiento.get('umbral_minimo')}")
        print(f"   ✓ Umbral máximo: {reconocimiento.get('umbral_maximo')}")
        print(f"   ✓ Descripción: {reconocimiento.get('descripcion', 'N/A')[:60]}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# 5. VERIFICAR MODELOS ENTRENADOS
print("\n5. VERIFICANDO MODELOS DE RECONOCIMIENTO FACIAL...")
training_dir = Path("TrainingImageLabel")
if training_dir.exists():
    modelos = list(training_dir.glob("*.yml"))
    print(f"   ✓ Modelos entrenados: {len(modelos)}")
    for modelo in modelos[:5]:  # Mostrar solo los primeros 5
        print(f"      - {modelo.name}")
    if len(modelos) > 5:
        print(f"      ... y {len(modelos) - 5} más")
else:
    print("   ⚠ Directorio de modelos no encontrado")

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
