"""
Explorador de la Base de Datos PostgreSQL
Muestra el contenido actual de todas las tablas
"""

import os
from dotenv import load_dotenv
from database_models import DatabaseManager, PersonalAdmin, Estudiante, Materia, Inscripcion, SesionActiva

load_dotenv()

db = DatabaseManager(os.getenv('DATABASE_URL'))
session = db.get_session()

print("\n" + "="*80)
print("🗄️  EXPLORADOR DE BASE DE DATOS - CLASS VISION")
print("="*80)

# 1. PERSONAL ADMIN (Usuarios del sistema)
print("\n📋 TABLA: personal_admin (Usuarios)")
print("-" * 80)
usuarios = session.query(PersonalAdmin).all()
print(f"Total: {len(usuarios)} usuarios")
for u in usuarios:
    print(f"\n  👤 ID: {u.id}")
    print(f"     Username: {u.username}")
    print(f"     Nombre: {u.full_name}")
    print(f"     Rol: {u.rol}")
    print(f"     Activo: {'✅' if u.activo else '❌'}")
    print(f"     Email: {u.email or 'No configurado'}")

# 2. MATERIAS
print("\n" + "="*80)
print("📚 TABLA: materias")
print("-" * 80)
materias = session.query(Materia).all()
print(f"Total: {len(materias)} materias")
for m in materias:
    print(f"\n  📖 ID: {m.id}")
    print(f"     Código: {m.codigo_materia}")
    print(f"     Nombre: {m.nombre}")
    print(f"     Docente ID: {m.id_docente}")
    print(f"     Nivel: {m.nivel}")
    print(f"     Activa: {'✅' if m.activo else '❌'}")
    print(f"     Horario: {m.hora_inicio} - {m.hora_fin}")

# 3. ESTUDIANTES
print("\n" + "="*80)
print("👨‍🎓 TABLA: estudiantes")
print("-" * 80)
estudiantes = session.query(Estudiante).limit(10).all()
total_estudiantes = session.query(Estudiante).count()
print(f"Total: {total_estudiantes} estudiantes (mostrando primeros 10)")
for e in estudiantes:
    print(f"\n  🎓 ID: {e.id}")
    print(f"     Código: {e.codigo_estudiante}")
    print(f"     Nombre: {e.nombre_completo}")
    print(f"     Activo: {'✅' if e.activo else '❌'}")

# 4. INSCRIPCIONES
print("\n" + "="*80)
print("📝 TABLA: inscripciones")
print("-" * 80)
inscripciones = session.query(Inscripcion).all()
print(f"Total: {len(inscripciones)} inscripciones")
for i in inscripciones[:10]:
    est = session.query(Estudiante).filter_by(id=i.id_estudiante).first()
    mat = session.query(Materia).filter_by(id=i.id_materia).first()
    print(f"\n  ✍️  ID: {i.id}")
    print(f"     Estudiante: {est.nombre_completo if est else 'N/A'}")
    print(f"     Materia: {mat.nombre if mat else 'N/A'}")
    print(f"     Estado: {i.estado}")
    print(f"     Asistencias: {i.total_asistencias}")
    print(f"     Faltas: {i.total_faltas}")

# 5. SESIONES ACTIVAS
print("\n" + "="*80)
print("🔐 TABLA: sesiones_activas")
print("-" * 80)
sesiones = session.query(SesionActiva).filter_by(activa=True).all()
print(f"Total: {len(sesiones)} sesiones activas")
for s in sesiones:
    print(f"\n  🔑 Token: {s.token[:30]}...")
    print(f"     Usuario ID: {s.usuario_id}")
    print(f"     Usuario Tipo: {s.usuario_tipo}")
    print(f"     Activa: {'✅' if s.activa else '❌'}")
    print(f"     Expira: {s.fecha_expiracion}")

# RESUMEN
print("\n" + "="*80)
print("📊 RESUMEN")
print("="*80)
print(f"  👥 Usuarios: {len(usuarios)}")
print(f"  📚 Materias: {len(materias)}")
print(f"  🎓 Estudiantes: {total_estudiantes}")
print(f"  📝 Inscripciones: {len(inscripciones)}")
print(f"  🔐 Sesiones activas: {len(sesiones)}")
print("="*80 + "\n")

session.close()
