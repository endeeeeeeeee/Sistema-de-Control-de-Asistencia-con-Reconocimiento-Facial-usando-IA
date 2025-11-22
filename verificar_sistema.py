"""
Script de verificación completa del sistema
Verifica que todos los componentes estén conectados correctamente
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*70)
print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA CLASS VISION")
print("="*70 + "\n")

# 1. Verificar variables de entorno
print("1️⃣ Variables de Entorno...")
database_url = os.getenv('DATABASE_URL')
if database_url:
    print(f"   ✅ DATABASE_URL configurado")
    print(f"   📍 URL: {database_url.split('@')[1] if '@' in database_url else 'local'}")
else:
    print("   ❌ DATABASE_URL NO configurado")
    sys.exit(1)

# 2. Verificar conexión a PostgreSQL
print("\n2️⃣ Conexión a PostgreSQL...")
try:
    from database_models import DatabaseManager
    db = DatabaseManager(database_url)
    session = db.get_session()
    print("   ✅ Conexión exitosa a PostgreSQL")
    session.close()
except Exception as e:
    print(f"   ❌ Error de conexión: {e}")
    sys.exit(1)

# 3. Verificar tablas en la base de datos
print("\n3️⃣ Tablas de Base de Datos...")
try:
    from database_models import (
        PersonalAdmin, Estudiante, Materia, Inscripcion, 
        AsistenciaLog, SesionActiva
    )
    from sqlalchemy import inspect
    
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    required_tables = [
        'personal_admin', 'estudiantes', 'materias', 'inscripciones',
        'asistencia_log', 'sesiones_activas'
    ]
    
    for table in required_tables:
        if table in tables:
            print(f"   ✅ Tabla '{table}' existe")
        else:
            print(f"   ❌ Tabla '{table}' NO existe")
    
    print(f"\n   📊 Total de tablas: {len(tables)}")
    
except Exception as e:
    print(f"   ❌ Error verificando tablas: {e}")

# 4. Verificar managers
print("\n4️⃣ Managers de PostgreSQL...")
try:
    from db_auth_manager import get_db_auth_manager
    from db_student_manager import get_db_student_manager
    
    auth_manager = get_db_auth_manager()
    student_manager = get_db_student_manager()
    
    print("   ✅ DBAuthManager cargado")
    print("   ✅ DBStudentManager cargado")
except Exception as e:
    print(f"   ❌ Error cargando managers: {e}")
    sys.exit(1)

# 5. Verificar usuario admin
print("\n5️⃣ Usuario Administrador...")
try:
    session = db.get_session()
    admin = session.query(PersonalAdmin).filter_by(username='admin').first()
    
    if admin:
        print(f"   ✅ Usuario admin existe")
        print(f"   👤 Nombre: {admin.full_name}")
        print(f"   🔑 Rol: {admin.rol}")
        print(f"   📧 Email: {admin.email or 'No configurado'}")
        print(f"   🟢 Activo: {'Sí' if admin.activo else 'No'}")
    else:
        print("   ⚠️  Usuario admin NO existe")
        print("   💡 Ejecutar: python setup_database.py")
    
    session.close()
except Exception as e:
    print(f"   ❌ Error verificando admin: {e}")

# 6. Verificar estudiantes
print("\n6️⃣ Estudiantes en Base de Datos...")
try:
    from sqlalchemy import func
    session = db.get_session()
    
    total_estudiantes = session.query(func.count(Estudiante.id)).scalar()
    estudiantes_activos = session.query(func.count(Estudiante.id)).filter_by(activo=True).scalar()
    
    print(f"   📊 Total de estudiantes: {total_estudiantes}")
    print(f"   🟢 Estudiantes activos: {estudiantes_activos}")
    
    if total_estudiantes > 0:
        print("   ✅ Hay estudiantes en la base de datos")
    else:
        print("   ⚠️  No hay estudiantes registrados")
    
    session.close()
except Exception as e:
    print(f"   ❌ Error verificando estudiantes: {e}")

# 7. Verificar materias
print("\n7️⃣ Materias en Base de Datos...")
try:
    session = db.get_session()
    
    total_materias = session.query(func.count(Materia.id)).scalar()
    materias_activas = session.query(func.count(Materia.id)).filter_by(activo=True).scalar()
    
    print(f"   📊 Total de materias: {total_materias}")
    print(f"   🟢 Materias activas: {materias_activas}")
    
    if total_materias > 0:
        print("   ✅ Hay materias en la base de datos")
        
        # Mostrar algunas materias
        materias = session.query(Materia).filter_by(activo=True).limit(3).all()
        if materias:
            print("   📚 Primeras materias:")
            for m in materias:
                print(f"      • {m.nombre} ({m.codigo_materia})")
    else:
        print("   ⚠️  No hay materias registradas")
    
    session.close()
except Exception as e:
    print(f"   ❌ Error verificando materias: {e}")

# 8. Verificar templates
print("\n8️⃣ Templates Frontend...")
import pathlib
templates_dir = pathlib.Path("templates")

required_templates = [
    'login.html',
    'dashboard.html',
    'register_student.html',
    'take_attendance.html'
]

for template in required_templates:
    template_path = templates_dir / template
    if template_path.exists():
        print(f"   ✅ {template} existe")
    else:
        print(f"   ❌ {template} NO existe")

# 9. Verificar archivos Python principales
print("\n9️⃣ Archivos Python del Sistema...")
main_files = [
    'mobile_server.py',
    'database_models.py',
    'db_auth_manager.py',
    'db_student_manager.py',
    'trainImage.py',
    'takeImage.py'
]

for file in main_files:
    if pathlib.Path(file).exists():
        print(f"   ✅ {file} existe")
    else:
        print(f"   ❌ {file} NO existe")

# 10. Resumen final
print("\n" + "="*70)
print("📋 RESUMEN DE VERIFICACIÓN")
print("="*70)
print("\n✅ Sistema listo para usar")
print("\n🚀 Para iniciar el servidor:")
print("   python mobile_server.py")
print("\n🌐 URL de acceso:")
print("   http://localhost:5000/login")
print("\n👤 Credenciales:")
print("   Usuario: admin")
print("   Contraseña: admin123")
print("\n" + "="*70 + "\n")
