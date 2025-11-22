"""
Script de inicialización de datos por defecto
Crea configuración inicial, badges y usuario admin
"""

from database_models import (
    DatabaseManager, SysConfig, Badge, PersonalAdmin, SesionActiva
)
from datetime import datetime
import hashlib

def hash_password(password):
    """Hash de contraseña con SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_config(session):
    """Crear configuración por defecto"""
    
    # Verificar si ya existe
    existing = session.query(SysConfig).first()
    if existing:
        print("✅ Configuración ya existe")
        return
    
    config = SysConfig(
        modo_operacion='UNIVERSIDAD',
        nombre_institucion='Sistema Universitario de Asistencia',
        reglas_json={
            'tolerancia_minutos': 15,
            'minimo_asistencia': 75,
            'umbral_desercion': 3,
            'duracion_qr': 30,
            'permitir_justificacion': True,
            'notificacion_tutores': True,
            'gamificacion_activa': True,
            'umbral_confianza': 85,
            'umbral_liveness': 70,
            'detectar_liveness': True,
            'guardar_fotos': False
        },
        color_primario='#023859',
        color_secundario='#54ACBF'
    )
    
    session.add(config)
    session.commit()
    print("✅ Configuración creada")

def init_badges(session):
    """Crear badges por defecto"""
    
    badges_default = [
        {
            'codigo': 'ASISTENCIA_PERFECTA',
            'nombre': 'Asistencia Perfecta',
            'descripcion': 'Asistencia 100% durante todo el mes',
            'icono_url': '🏆',
            'condicion_tipo': 'ASISTENCIA_PERFECTA',
            'condicion_valor': 100,
            'puntos_otorga': 50,
            'rareza': 'EPICO'
        },
        {
            'codigo': 'PUNTUAL_ORO',
            'nombre': 'Puntual de Oro',
            'descripcion': 'Nunca llega tarde en el mes',
            'icono_url': '⏰',
            'condicion_tipo': 'PUNTUALIDAD_EXTREMA',
            'condicion_valor': 100,
            'puntos_otorga': 40,
            'rareza': 'RARO'
        },
        {
            'codigo': 'RACHA_SEMANAL',
            'nombre': 'Racha Semanal',
            'descripcion': 'Asistencia completa durante 7 días',
            'icono_url': '🔥',
            'condicion_tipo': 'RACHA_SEMANAL',
            'condicion_valor': 7,
            'puntos_otorga': 25,
            'rareza': 'COMUN'
        },
        {
            'codigo': 'PARTICIPACION',
            'nombre': 'Participación Activa',
            'descripcion': 'Alta participación en clases',
            'icono_url': '💬',
            'condicion_tipo': 'PARTICIPACION',
            'condicion_valor': 20,
            'puntos_otorga': 30,
            'rareza': 'RARO'
        },
        {
            'codigo': 'MEJORA_CONTINUA',
            'nombre': 'Mejora Continua',
            'descripcion': 'Mejora constante en asistencia',
            'icono_url': '📈',
            'condicion_tipo': 'MEJORA_CONTINUA',
            'condicion_valor': 10,
            'puntos_otorga': 35,
            'rareza': 'EPICO'
        }
    ]
    
    # Verificar si ya existen
    count = session.query(Badge).count()
    if count > 0:
        print(f"✅ Ya existen {count} badges")
        return
    
    for badge_data in badges_default:
        badge = Badge(**badge_data)
        session.add(badge)
    
    session.commit()
    print(f"✅ {len(badges_default)} badges creados")

def init_admin_user(session):
    """Crear usuario administrador por defecto"""
    
    # Verificar si ya existe
    existing = session.query(PersonalAdmin).filter_by(username='admin').first()
    if existing:
        print("✅ Usuario admin ya existe")
        return
    
    admin = PersonalAdmin(
        username='admin',
        password_hash=hash_password('admin123'),
        full_name='Administrador del Sistema',
        rol='ADMIN_SISTEMA',
        activo=True
    )
    
    session.add(admin)
    session.commit()
    print("✅ Usuario admin creado (username: admin, password: admin123)")

def init_demo_data(session):
    """Crear datos de demostración"""
    
    # Usuario docente demo
    existing = session.query(PersonalAdmin).filter_by(username='docente').first()
    if not existing:
        docente = PersonalAdmin(
            username='docente',
            password_hash=hash_password('docente123'),
            full_name='Profesor Demo',
            rol='DOCENTE',
            activo=True
        )
        session.add(docente)
        session.commit()
        print("✅ Usuario docente demo creado (username: docente, password: docente123)")
    else:
        print("✅ Usuario docente demo ya existe")

def main():
    """Ejecutar inicialización"""
    
    print("\n" + "="*60)
    print("INICIALIZACIÓN DE BASE DE DATOS - CLASS VISION")
    print("="*60 + "\n")
    
    db_manager = DatabaseManager()
    session = db_manager.get_session()
    
    try:
        init_config(session)
        init_badges(session)
        init_admin_user(session)
        init_demo_data(session)
        
        print("\n" + "="*60)
        print("✅ INICIALIZACIÓN COMPLETADA")
        print("="*60)
        print("\nCREDENCIALES POR DEFECTO:")
        print("-" * 60)
        print("Admin:   username=admin    password=admin123")
        print("Docente: username=docente  password=docente123")
        print("-" * 60)
        print("\nPuedes iniciar sesión en: http://localhost:5000/login")
        print()
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    main()
