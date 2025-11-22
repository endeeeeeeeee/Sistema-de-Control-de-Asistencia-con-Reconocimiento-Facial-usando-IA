"""
CLASS VISION - Migration Script
================================

Script para migrar datos de JSON/CSV a PostgreSQL.
Convierte el sistema actual (archivos planos) a base de datos relacional.
"""

import os
import json
import csv
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import cv2
import numpy as np
from dotenv import load_dotenv
from database_models import (
    DatabaseManager, PersonalAdmin, Estudiante, Materia, Inscripcion,
    AsistenciaLog, SysConfig, Badge, SesionActiva
)

# Cargar variables de entorno
load_dotenv()

class MigrationManager:
    """Gestor de migración de datos"""
    
    def __init__(self, workspace_path, db_manager):
        """
        Inicializa el gestor de migración
        
        Args:
            workspace_path: Ruta al workspace del proyecto
            db_manager: Instancia de DatabaseManager
        """
        self.workspace = Path(workspace_path)
        self.db_manager = db_manager
        self.session = db_manager.get_session()
        
        # Mapeos para conversión
        self.user_map = {}  # username -> PersonalAdmin.id
        self.student_map = {}  # enrollment -> Estudiante.id
        self.subject_map = {}  # subject_name -> Materia.id
    
    def migrate_all(self):
        """Ejecuta migración completa"""
        print("🚀 Iniciando migración completa...")
        
        try:
            # 1. Configuración del sistema
            print("\n1️⃣ Migrando configuración del sistema...")
            self._migrate_sys_config()
            
            # 2. Usuarios (teachers/admins)
            print("\n2️⃣ Migrando usuarios del sistema...")
            self._migrate_users()
            
            # 3. Materias/Subjects
            print("\n3️⃣ Migrando materias...")
            self._migrate_subjects()
            
            # 4. Estudiantes
            print("\n4️⃣ Migrando estudiantes...")
            self._migrate_students()
            
            # 5. Inscripciones (student-subject)
            print("\n5️⃣ Migrando inscripciones...")
            self._migrate_inscriptions()
            
            # 6. Asistencias
            print("\n6️⃣ Migrando registros de asistencia...")
            self._migrate_attendance()
            
            # 7. Badges por defecto
            print("\n7️⃣ Creando badges del sistema...")
            self._create_default_badges()
            
            # 8. Sesiones activas
            print("\n8️⃣ Migrando sesiones activas...")
            self._migrate_sessions()
            
            self.session.commit()
            print("\n✅ Migración completada exitosamente")
            
            # Mostrar resumen
            self._print_migration_summary()
            
        except Exception as e:
            self.session.rollback()
            print(f"\n❌ Error durante migración: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.session.close()
    
    def _migrate_sys_config(self):
        """Migra configuración del sistema"""
        config = SysConfig(
            modo_operacion='UNIVERSIDAD',
            nombre_institucion='CLASS VISION - Sistema de Asistencia Inteligente',
            reglas_json={
                "tolerancia_minutos": 10,
                "faltas_alerta": 3,
                "modo_virtual_habilitado": True,
                "reconocimiento_facial_obligatorio": True,
                "liveness_detection": False,
                "gamificacion_habilitada": True,
                "puntos_por_asistencia": 10,
                "puntos_por_puntualidad": 5,
                "notificaciones_tutores": False,
                "codigo_qr_expiracion_minutos": 5
            },
            color_primario='#023859',
            color_secundario='#54ACBF'
        )
        self.session.add(config)
        print("   ✓ Configuración del sistema creada")
    
    def _migrate_users(self):
        """Migra usuarios desde data/users.json"""
        users_file = self.workspace / 'data' / 'users.json'
        
        if not users_file.exists():
            print("   ⚠ Archivo users.json no encontrado, creando admin por defecto")
            self._create_default_admin()
            return
        
        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        for username, user_info in users_data.items():
            try:
                user = PersonalAdmin(
                    username=username,
                    password_hash=user_info.get('password', ''),
                    full_name=user_info.get('full_name', username),
                    rol='DOCENTE',  # Por defecto todos son docentes
                    email=user_info.get('email'),
                    activo=True
                )
                self.session.add(user)
                self.session.flush()  # Para obtener el ID
                
                self.user_map[username] = user.id
                print(f"   ✓ Usuario migrado: {username} (ID: {user.id})")
                
            except Exception as e:
                print(f"   ✗ Error migrando usuario {username}: {e}")
        
        # Si no hay usuarios, crear admin
        if not self.user_map:
            self._create_default_admin()
    
    def _create_default_admin(self):
        """Crea usuario admin por defecto"""
        admin = PersonalAdmin(
            username='admin',
            password_hash=hashlib.sha256('admin123'.encode()).hexdigest(),
            full_name='Administrador del Sistema',
            rol='ADMIN_SISTEMA',
            activo=True
        )
        self.session.add(admin)
        self.session.flush()
        self.user_map['admin'] = admin.id
        print("   ✓ Admin por defecto creado (username: admin, password: admin123)")
    
    def _migrate_subjects(self):
        """Migra materias desde data/students_by_teacher.json"""
        students_file = self.workspace / 'data' / 'students_by_teacher.json'
        
        if not students_file.exists():
            print("   ⚠ Archivo students_by_teacher.json no encontrado")
            return
        
        with open(students_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraer materias únicas
        subjects = set()
        for key in data.keys():
            if '::' in key:
                username, subject = key.split('::', 1)
                subjects.add((username, subject))
        
        for username, subject_name in subjects:
            try:
                # Obtener ID del docente
                docente_id = self.user_map.get(username)
                if not docente_id:
                    print(f"   ⚠ Docente {username} no encontrado, usando admin")
                    docente_id = self.user_map.get('admin', 1)
                
                # Crear materia
                materia = Materia(
                    codigo_materia=f"{subject_name[:3].upper()}-2025",
                    nombre=subject_name,
                    nivel='UNIVERSIDAD',
                    id_docente=docente_id,
                    hora_inicio='08:00:00',
                    hora_fin='10:00:00',
                    dia_semana=[1, 3, 5],  # Lunes, Miércoles, Viernes
                    activo=True,
                    periodo_academico='2025-2'
                )
                self.session.add(materia)
                self.session.flush()
                
                # Guardar mapeo con username::subject como key
                self.subject_map[f"{username}::{subject_name}"] = materia.id
                print(f"   ✓ Materia migrada: {subject_name} (ID: {materia.id})")
                
            except Exception as e:
                print(f"   ✗ Error migrando materia {subject_name}: {e}")
    
    def _migrate_students(self):
        """Migra estudiantes desde StudentDetails/studentdetails.csv y vectores faciales"""
        csv_file = self.workspace / 'StudentDetails' / 'studentdetails.csv'
        training_folder = self.workspace / 'TrainingImage'
        
        if not csv_file.exists():
            print("   ⚠ Archivo studentdetails.csv no encontrado")
            return
        
        seen_enrollments = set()  # Para evitar duplicados
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    enrollment = row.get('Enrollment', row.get('enrollment', ''))
                    name = row.get('Name', row.get('name', ''))
                    
                    if not enrollment or not name:
                        continue
                    
                    # Saltar duplicados
                    if enrollment in seen_enrollments:
                        print(f"   ⊗ Duplicado ignorado: {name} ({enrollment})")
                        continue
                    
                    seen_enrollments.add(enrollment)
                    
                    # Obtener vector facial
                    face_vector = self._get_face_vector_for_student(enrollment, training_folder)
                    
                    if face_vector is None:
                        print(f"   ⚠ No se encontró vector facial para {enrollment}, generando dummy")
                        face_vector = np.zeros((128,), dtype=np.float32).tobytes()
                    
                    # Crear estudiante
                    estudiante = Estudiante(
                        codigo_estudiante=enrollment,
                        nombre_completo=name,
                        fecha_nacimiento=datetime(2000, 1, 1).date(),  # Fecha dummy
                        foto_face_vector=face_vector,
                        activo=True,
                        puntos_acumulados=0,
                        nivel=1
                    )
                    self.session.add(estudiante)
                    self.session.flush()
                    
                    self.student_map[enrollment] = estudiante.id
                    print(f"   ✓ Estudiante migrado: {name} ({enrollment}) - ID: {estudiante.id}")
                    
                except Exception as e:
                    print(f"   ✗ Error migrando estudiante {enrollment}: {e}")
                    self.session.rollback()  # Rollback para continuar
    
    def _get_face_vector_for_student(self, enrollment, training_folder):
        """
        Obtiene el vector facial de un estudiante desde las imágenes de entrenamiento
        
        Args:
            enrollment: Código del estudiante
            training_folder: Carpeta con imágenes de entrenamiento
            
        Returns:
            bytes: Vector facial serializado o None si no se encuentra
        """
        # Buscar imágenes del estudiante
        pattern = f"{enrollment}_*.jpg"
        images = list(training_folder.glob(pattern))
        
        if not images:
            return None
        
        # Tomar la primera imagen y extraer características
        # En producción, esto debería usar el mismo método que el reconocimiento
        try:
            img_path = images[0]
            img = cv2.imread(str(img_path))
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Por ahora, guardar la imagen redimensionada como vector
            # En producción real, usar el LBPH o modelo de embeddings
            resized = cv2.resize(gray, (100, 100))
            vector = resized.flatten().tobytes()
            
            return vector
            
        except Exception as e:
            print(f"   ⚠ Error extrayendo vector facial para {enrollment}: {e}")
            return None
    
    def _migrate_inscriptions(self):
        """Migra inscripciones desde students_by_teacher.json"""
        students_file = self.workspace / 'data' / 'students_by_teacher.json'
        
        if not students_file.exists():
            print("   ⚠ Archivo students_by_teacher.json no encontrado")
            return
        
        with open(students_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        inscripciones_count = 0
        
        for key, value in data.items():
            if '::' not in key:
                continue
            
            materia_id = self.subject_map.get(key)
            if not materia_id:
                print(f"   ⚠ Materia no encontrada para {key}")
                continue
            
            # Obtener lista de estudiantes del objeto
            students_list = value.get('students', [])
            
            for student_info in students_list:
                try:
                    # Manejar tanto strings como dicts
                    if isinstance(student_info, str):
                        enrollment = student_info
                    elif isinstance(student_info, dict):
                        enrollment = student_info.get('enrollment', '')
                    else:
                        continue
                    
                    estudiante_id = self.student_map.get(enrollment)
                    
                    if not estudiante_id:
                        print(f"   ⚠ Estudiante {enrollment} no encontrado en mapa")
                        continue
                    
                    # Crear inscripción
                    inscripcion = Inscripcion(
                        id_estudiante=estudiante_id,
                        id_materia=materia_id,
                        estado='ACTIVO',
                        puntos_acumulados=0,
                        total_asistencias=0,
                        total_faltas=0,
                        total_tardanzas=0,
                        porcentaje_asistencia=100.00
                    )
                    self.session.add(inscripcion)
                    inscripciones_count += 1
                    
                except Exception as e:
                    print(f"   ✗ Error creando inscripción: {e}")
                    self.session.rollback()
        
        if inscripciones_count > 0:
            self.session.flush()
        print(f"   ✓ {inscripciones_count} inscripciones creadas")
    
    def _migrate_attendance(self):
        """Migra registros de asistencia desde Attendance/*.csv"""
        attendance_folder = self.workspace / 'Attendance'
        
        if not attendance_folder.exists():
            print("   ⚠ Carpeta Attendance no encontrada")
            return
        
        attendance_count = 0
        
        # Buscar todas las carpetas de materias
        for subject_folder in attendance_folder.iterdir():
            if not subject_folder.is_dir():
                continue
            
            # Buscar archivos CSV de asistencia
            for csv_file in subject_folder.glob('*.csv'):
                if csv_file.name == 'attendance.csv':
                    continue  # Saltar archivo maestro
                
                try:
                    attendance_count += self._process_attendance_file(csv_file, subject_folder.name)
                except Exception as e:
                    print(f"   ✗ Error procesando {csv_file.name}: {e}")
        
        print(f"   ✓ {attendance_count} registros de asistencia migrados")
    
    def _process_attendance_file(self, csv_file, subject_name):
        """Procesa un archivo CSV de asistencia"""
        count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    enrollment = row.get('Enrollment', row.get('enrollment', ''))
                    date_str = row.get('Date', row.get('date', ''))
                    time_str = row.get('Time', row.get('time', ''))
                    
                    if not enrollment or not date_str:
                        continue
                    
                    # Buscar inscripción
                    estudiante_id = self.student_map.get(enrollment)
                    if not estudiante_id:
                        continue
                    
                    # Buscar materia (necesitamos encontrar el key correcto)
                    inscripcion = self.session.query(Inscripcion).filter(
                        Inscripcion.id_estudiante == estudiante_id
                    ).join(Materia).filter(
                        Materia.nombre.ilike(f"%{subject_name}%")
                    ).first()
                    
                    if not inscripcion:
                        continue
                    
                    # Parsear fecha
                    try:
                        fecha = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except:
                        try:
                            fecha = datetime.strptime(date_str, '%d/%m/%Y').date()
                        except:
                            continue
                    
                    # Parsear hora
                    try:
                        hora = datetime.strptime(time_str, '%H:%M:%S')
                        hora_entrada = datetime.combine(fecha, hora.time())
                    except:
                        hora_entrada = datetime.combine(fecha, datetime.now().time())
                    
                    # Crear registro de asistencia
                    asistencia = AsistenciaLog(
                        id_inscripcion=inscripcion.id,
                        fecha=fecha,
                        hora_entrada=hora_entrada,
                        metodo_entrada='RECONOCIMIENTO_FACIAL',
                        estado='PRESENTE'
                    )
                    self.session.add(asistencia)
                    count += 1
                    
                except Exception as e:
                    print(f"   ✗ Error procesando fila: {e}")
                    continue
        
        if count > 0:
            self.session.flush()
        
        return count
    
    def _create_default_badges(self):
        """Crea badges por defecto del sistema si no existen"""
        # Verificar si ya existen badges
        existing_count = self.session.query(Badge).count()
        if existing_count > 0:
            print(f"   ⊗ Badges ya existen ({existing_count}), saltando creación")
            return
        
        badges_data = [
            {
                'codigo': 'ASISTENCIA_PERFECTA_MES',
                'nombre': 'Asistencia Perfecta',
                'descripcion': '100% de asistencia durante un mes completo',
                'condicion_tipo': 'ASISTENCIA_PERFECTA',
                'condicion_valor': 30,
                'puntos_otorga': 500,
                'rareza': 'EPICO'
            },
            {
                'codigo': 'PUNTUAL_30_DIAS',
                'nombre': 'Puntualidad Extrema',
                'descripcion': '30 días consecutivos llegando a tiempo',
                'condicion_tipo': 'PUNTUALIDAD_EXTREMA',
                'condicion_valor': 30,
                'puntos_otorga': 300,
                'rareza': 'RARO'
            },
            {
                'codigo': 'RACHA_SEMANAL',
                'nombre': 'Semana Perfecta',
                'descripcion': 'Una semana completa sin faltas',
                'condicion_tipo': 'RACHA_SEMANAL',
                'condicion_valor': 7,
                'puntos_otorga': 100,
                'rareza': 'COMUN'
            },
            {
                'codigo': 'ESTUDIANTE_ESTRELLA',
                'nombre': 'Estudiante Estrella',
                'descripcion': 'Top 10 del ranking mensual',
                'condicion_tipo': 'CUSTOM',
                'condicion_valor': 10,
                'puntos_otorga': 200,
                'rareza': 'RARO'
            },
            {
                'codigo': 'MEJORA_CONTINUA',
                'nombre': 'En Mejora',
                'descripcion': 'Mejoró su asistencia en 20% respecto al mes anterior',
                'condicion_tipo': 'MEJORA_CONTINUA',
                'condicion_valor': 20,
                'puntos_otorga': 150,
                'rareza': 'COMUN'
            }
        ]
        
        for badge_data in badges_data:
            badge = Badge(**badge_data)
            self.session.add(badge)
        
        print(f"   ✓ {len(badges_data)} badges creados")
    
    def _migrate_sessions(self):
        """Migra sesiones activas desde data/sessions.json"""
        sessions_file = self.workspace / 'data' / 'sessions.json'
        
        if not sessions_file.exists():
            print("   ⚠ Archivo sessions.json no encontrado")
            return
        
        with open(sessions_file, 'r', encoding='utf-8') as f:
            sessions_data = json.load(f)
        
        sessions_count = 0
        
        for token, session_info in sessions_data.items():
            try:
                username = session_info.get('username', '')
                usuario_id = self.user_map.get(username)
                
                if not usuario_id:
                    continue
                
                # Calcular expiración (8 horas desde ahora)
                expiracion = datetime.now() + timedelta(hours=8)
                
                sesion = SesionActiva(
                    token=token,
                    usuario_tipo='PERSONAL',
                    usuario_id=usuario_id,
                    fecha_inicio=datetime.now(),
                    fecha_expiracion=expiracion,
                    ultima_actividad=datetime.now(),
                    activa=True
                )
                self.session.add(sesion)
                sessions_count += 1
                
            except Exception as e:
                print(f"   ✗ Error migrando sesión: {e}")
        
        print(f"   ✓ {sessions_count} sesiones activas migradas")
    
    def _print_migration_summary(self):
        """Imprime resumen de la migración"""
        print("\n" + "="*60)
        print("📊 RESUMEN DE MIGRACIÓN")
        print("="*60)
        
        # Contar registros
        counts = {
            'Usuarios': self.session.query(PersonalAdmin).count(),
            'Estudiantes': self.session.query(Estudiante).count(),
            'Materias': self.session.query(Materia).count(),
            'Inscripciones': self.session.query(Inscripcion).count(),
            'Asistencias': self.session.query(AsistenciaLog).count(),
            'Badges': self.session.query(Badge).count(),
            'Sesiones Activas': self.session.query(SesionActiva).count()
        }
        
        for tabla, count in counts.items():
            print(f"{tabla:.<30} {count:>5} registros")
        
        print("="*60)


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Obtener workspace path
    if len(sys.argv) > 1:
        workspace_path = sys.argv[1]
    else:
        workspace_path = os.getcwd()
    
    print(f"📁 Workspace: {workspace_path}\n")
    
    # Confirmar migración
    response = input("⚠️  Esta operación migrará todos los datos a PostgreSQL.\n"
                    "   ¿Deseas continuar? (si/no): ")
    
    if response.lower() not in ['si', 'sí', 's', 'y', 'yes']:
        print("❌ Migración cancelada")
        sys.exit(0)
    
    # Crear gestor de BD
    print("\n🔌 Conectando a PostgreSQL...")
    db_manager = DatabaseManager()
    
    # Crear tablas si no existen
    print("🏗️  Creando estructura de tablas...")
    db_manager.create_all_tables()
    
    # Ejecutar migración
    migrator = MigrationManager(workspace_path, db_manager)
    migrator.migrate_all()
    
    print("\n🎉 ¡Migración completada!")
    print("\n💡 Próximos pasos:")
    print("   1. Verifica los datos en PostgreSQL")
    print("   2. Actualiza mobile_server.py para usar SQLAlchemy")
    print("   3. Prueba el sistema con la nueva base de datos")
