"""
Backend API Routes - CLASS VISION
Endpoints completos para el frontend
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
import base64
import io
import json

from database_models import (
    DatabaseManager, PersonalAdmin, Estudiante, Tutor, Materia,
    Inscripcion, AsistenciaLog, CodigoTemporal, AsistenciaVirtual,
    NotificacionInterna, AlertaDesercion, Justificacion, Badge,
    EstudianteBadge, RankingMensual, EstadisticaDiaria, ReporteGenerado,
    AuditLog, AsistenteHistorial, SysConfig, SesionActiva
)

# Crear blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

def get_auth_manager():
    """Obtiene el auth manager desde el app context"""
    from flask import current_app
    return current_app.config['AUTH_MANAGER']

def get_student_manager():
    """Obtiene el student manager desde el app context"""
    from flask import current_app
    return current_app.config['STUDENT_MANAGER']

def get_db_session():
    """Obtiene una sesión de base de datos"""
    from flask import current_app
    return current_app.config['DB_MANAGER'].get_session()

def validate_token_decorator(f):
    """Decorador para validar token en endpoints"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        auth_manager = get_auth_manager()
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        # Pasar usuario a la función
        return f(user=user, *args, **kwargs)
    
    return decorated_function


# ============================================
# ENDPOINTS DE MATERIAS
# ============================================

@api_bp.route('/teacher/subjects', methods=['GET'])
@validate_token_decorator
def get_teacher_subjects(user):
    """Obtener materias del docente con estadísticas"""
    session = get_db_session()
    
    try:
        docente = session.query(PersonalAdmin).filter_by(id=user['id']).first()
        if not docente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        materias_data = []
        for materia in docente.materias:
            if not materia.activo:
                continue
            
            # Contar estudiantes inscritos
            total_estudiantes = session.query(func.count(Inscripcion.id)).filter_by(
                id_materia=materia.id,
                estado='ACTIVO'
            ).scalar() or 0
            
            materias_data.append({
                'id': materia.id,
                'codigo_materia': materia.codigo_materia,
                'nombre': materia.nombre,
                'nivel': materia.nivel,
                'dia_semana': materia.dia_semana or [],
                'hora_inicio': str(materia.hora_inicio) if materia.hora_inicio else None,
                'hora_fin': str(materia.hora_fin) if materia.hora_fin else None,
                'tolerancia_minutos': materia.tolerancia_minutos,
                'total_estudiantes': total_estudiantes
            })
        
        return jsonify({'success': True, 'subjects': materias_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/teacher/subjects', methods=['POST'])
@validate_token_decorator
def create_subject(user):
    """Crear nueva materia"""
    session = get_db_session()
    
    try:
        data = request.json
        
        docente = session.query(PersonalAdmin).filter_by(id=user['id']).first()
        if not docente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        nueva_materia = Materia(
            codigo_materia=data['codigo_materia'],
            nombre=data['nombre'],
            nivel=data.get('nivel'),
            id_docente=docente.id,
            dia_semana=data.get('dia_semana', []),
            hora_inicio=data.get('hora_inicio'),
            hora_fin=data.get('hora_fin'),
            tolerancia_minutos=data.get('tolerancia_minutos', 15),
            activo=True
        )
        
        session.add(nueva_materia)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Materia creada exitosamente',
            'materia_id': nueva_materia.id
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/subjects/<int:materia_id>/students', methods=['GET'])
@validate_token_decorator
def get_materia_students(user, materia_id):
    """Obtener estudiantes de una materia"""
    session = get_db_session()
    
    try:
        materia = session.query(Materia).filter_by(id=materia_id).first()
        if not materia or materia.id_docente != user['id']:
            return jsonify({'success': False, 'error': 'Materia no encontrada'}), 404
        
        inscripciones = session.query(Inscripcion).filter_by(
            id_materia=materia_id,
            estado='ACTIVO'
        ).all()
        
        estudiantes = []
        for inscripcion in inscripciones:
            est = inscripcion.estudiante
            estudiantes.append({
                'id': est.id,
                'codigo_estudiante': est.codigo_estudiante,
                'nombre_completo': est.nombre_completo,
                'email': est.email,
                'ci': est.ci,
                'porcentaje_asistencia': inscripcion.porcentaje_asistencia,
                'total_asistencias': inscripcion.total_asistencias,
                'total_faltas': inscripcion.total_faltas,
                'total_tardanzas': inscripcion.total_tardanzas
            })
        
        return jsonify({'success': True, 'students': estudiantes})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# ============================================
# ENDPOINTS DE ESTUDIANTES
# ============================================

@api_bp.route('/students/search', methods=['GET'])
@validate_token_decorator
def search_student(user):
    """Buscar estudiante por código para inscribir"""
    session = get_db_session()
    
    try:
        codigo = request.args.get('codigo')
        
        if not codigo:
            return jsonify({'success': False, 'error': 'Parámetro codigo requerido'}), 400
        
        estudiante = session.query(Estudiante).filter_by(codigo_estudiante=codigo).first()
        
        if not estudiante:
            return jsonify({'success': False, 'error': 'Estudiante no encontrado'}), 404
        
        # Contar materias inscritas
        total_materias = session.query(func.count(Inscripcion.id)).filter_by(
            id_estudiante=estudiante.id,
            estado='ACTIVO'
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'estudiante': {
                'id': estudiante.id,
                'codigo_estudiante': estudiante.codigo_estudiante,
                'nombre_completo': estudiante.nombre_completo,
                'email': estudiante.email,
                'telefono': estudiante.telefono,
                'ci': estudiante.ci,
                'fecha_nacimiento': str(estudiante.fecha_nacimiento) if estudiante.fecha_nacimiento else None,
                'puntos_acumulados': estudiante.puntos_acumulados,
                'nivel': estudiante.nivel,
                'total_materias': total_materias,
                'foto_preview': estudiante.foto_face_vector[:200] if estudiante.foto_face_vector else None
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/students', methods=['GET'])
@validate_token_decorator
def get_all_students(user):
    """Obtener todos los estudiantes"""
    session = get_db_session()
    
    try:
        estudiantes = session.query(Estudiante).filter_by(activo=True).all()
        
        students_data = []
        for est in estudiantes:
            # Contar materias inscritas
            total_materias = session.query(func.count(Inscripcion.id)).filter_by(
                id_estudiante=est.id,
                estado='ACTIVO'
            ).scalar() or 0
            
            students_data.append({
                'id': est.id,
                'codigo_estudiante': est.codigo_estudiante,
                'nombre_completo': est.nombre_completo,
                'ci': est.ci,
                'email': est.email,
                'fecha_nacimiento': str(est.fecha_nacimiento) if est.fecha_nacimiento else None,
                'puntos_acumulados': est.puntos_acumulados,
                'nivel': est.nivel,
                'total_materias': total_materias
            })
        
        return jsonify({'success': True, 'students': students_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/students/register', methods=['POST'])
def public_register_student():
    """Auto-registro público de estudiantes (sin autenticación)"""
    session = get_db_session()
    
    try:
        data = request.json
        
        # Verificar campos requeridos
        if not all([data.get('codigo_estudiante'), data.get('nombre_completo'), data.get('email')]):
            return jsonify({'success': False, 'error': 'Campos requeridos: codigo_estudiante, nombre_completo, email'}), 400
        
        # Verificar si ya existe
        existing = session.query(Estudiante).filter(
            or_(
                Estudiante.codigo_estudiante == data['codigo_estudiante'],
                Estudiante.email == data['email']
            )
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Ya existe un estudiante con ese código o email'}), 400
        
        # Procesar fotos base64 (múltiples capturas)
        fotos_base64 = data.get('fotos_base64', [])
        foto_principal = data.get('foto_base64', '')
        
        # Si hay múltiples fotos, usar la primera como principal
        if fotos_base64:
            foto_principal = fotos_base64[0]
        
        # Convertir fecha de nacimiento
        fecha_nac = None
        if data.get('fecha_nacimiento'):
            try:
                fecha_nac = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
            except:
                pass
        
        nuevo_estudiante = Estudiante(
            codigo_estudiante=data['codigo_estudiante'],
            nombre_completo=data['nombre_completo'],
            email=data['email'],
            telefono=data.get('telefono'),
            ci=data.get('ci'),
            fecha_nacimiento=fecha_nac,
            foto_face_vector=foto_principal[:2000] if foto_principal else None,  # Mayor capacidad para mejor reconocimiento
            activo=True,
            puntos_acumulados=0,
            nivel=1
        )
        
        # TODO: En producción, aquí se procesarían las múltiples fotos con un modelo de ML
        # para entrenar el reconocimiento facial con mejor precisión
        
        session.add(nuevo_estudiante)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Estudiante registrado exitosamente',
            'estudiante_id': nuevo_estudiante.id
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/students', methods=['POST'])
@validate_token_decorator
def enroll_student_to_subject(user):
    """Docente inscribe estudiante existente a su materia"""
    session = get_db_session()
    
    try:
        data = request.json
        codigo_estudiante = data.get('codigo_estudiante')
        materia_id = data.get('materia_id')
        
        if not codigo_estudiante or not materia_id:
            return jsonify({'success': False, 'error': 'codigo_estudiante y materia_id son requeridos'}), 400
        
        # Verificar que la materia pertenece al docente
        materia = session.query(Materia).filter_by(id=materia_id, id_docente=user['id']).first()
        if not materia:
            return jsonify({'success': False, 'error': 'Materia no encontrada'}), 404
        
        # Buscar estudiante
        estudiante = session.query(Estudiante).filter_by(codigo_estudiante=codigo_estudiante).first()
        if not estudiante:
            return jsonify({'success': False, 'error': 'Estudiante no encontrado. Debe registrarse primero en /registro-estudiante'}), 404
        
        # Verificar si ya está inscrito
        existing = session.query(Inscripcion).filter_by(
            id_estudiante=estudiante.id,
            id_materia=materia_id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Estudiante ya está inscrito en esta materia'}), 400
        
        # Crear inscripción
        inscripcion = Inscripcion(
            id_estudiante=estudiante.id,
            id_materia=materia_id,
            estado='ACTIVO'
        )
        
        session.add(inscripcion)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{estudiante.nombre_completo} inscrito exitosamente'
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# ============================================
# ENDPOINTS DE ASISTENCIA
# ============================================

@api_bp.route('/attendance/recognize', methods=['POST'])
@validate_token_decorator
def recognize_attendance(user):
    """Reconocimiento facial para asistencia"""
    session = get_db_session()
    
    try:
        data = request.json
        materia_id = data['materia_id']
        image_base64 = data['image_base64']
        
        # TODO: Implementar reconocimiento facial real
        # Por ahora simulamos reconocimiento exitoso
        
        return jsonify({
            'success': True,
            'recognized': True,
            'student_id': 1,
            'student_name': 'Estudiante Demo',
            'estado': 'PRESENTE'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/attendance/finish', methods=['POST'])
@validate_token_decorator
def finish_attendance_session(user):
    """Finalizar sesión de asistencia"""
    session = get_db_session()
    
    try:
        data = request.json
        materia_id = data['materia_id']
        attendance = data['attendance']  # Lista de asistencias
        
        hoy = date.today()
        
        for item in attendance:
            # Buscar inscripción
            inscripcion = session.query(Inscripcion).filter_by(
                id_estudiante=item['id'],
                id_materia=materia_id
            ).first()
            
            if not inscripcion:
                continue
            
            # Verificar si ya existe registro hoy
            existing = session.query(AsistenciaLog).filter_by(
                id_inscripcion=inscripcion.id,
                fecha=hoy
            ).first()
            
            if existing:
                continue  # Ya registrado
            
            # Crear registro de asistencia
            asistencia = AsistenciaLog(
                id_inscripcion=inscripcion.id,
                fecha=hoy,
                hora_entrada=datetime.now().time(),
                metodo_entrada='FACIAL',
                estado=item['estado'],
                score_confianza=95.0
            )
            
            session.add(asistencia)
            
            # Actualizar contadores en inscripción
            if item['estado'] == 'PRESENTE':
                inscripcion.total_asistencias += 1
            elif item['estado'] == 'AUSENTE':
                inscripcion.total_faltas += 1
            elif item['estado'] == 'TARDANZA':
                inscripcion.total_tardanzas += 1
            
            # Recalcular porcentaje
            total = inscripcion.total_asistencias + inscripcion.total_faltas + inscripcion.total_tardanzas
            if total > 0:
                inscripcion.porcentaje_asistencia = round(
                    (inscripcion.total_asistencias / total) * 100, 2
                )
        
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Asistencia guardada exitosamente'
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# ============================================
# ENDPOINTS DE CÓDIGOS QR
# ============================================

@api_bp.route('/codes/generate', methods=['POST'])
@validate_token_decorator
def generate_code(user):
    """Generar código QR temporal"""
    session = get_db_session()
    
    try:
        data = request.json
        tipo = data['tipo']
        materia_id = data.get('materia_id')
        duracion_minutos = data.get('duracion_minutos', 30)
        
        import secrets
        import hashlib
        
        # Generar código según tipo
        if tipo == 'CODIGO_NUMERICO':
            codigo = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        else:
            codigo = secrets.token_urlsafe(16)
        
        ahora = datetime.now()
        valido_hasta = ahora + timedelta(minutes=duracion_minutos)
        
        nuevo_codigo = CodigoTemporal(
            codigo=codigo,
            tipo=tipo,
            id_materia=materia_id,
            valido_desde=ahora,
            valido_hasta=valido_hasta,
            max_usos=100,
            usos_actuales=0,
            hash_verificacion=hashlib.sha256(codigo.encode()).hexdigest(),
            generado_por=user['id'],
            activo=True
        )
        
        session.add(nuevo_codigo)
        session.commit()
        
        # Obtener nombre de materia
        materia_nombre = None
        if materia_id:
            materia = session.query(Materia).filter_by(id=materia_id).first()
            if materia:
                materia_nombre = materia.nombre
        
        return jsonify({
            'success': True,
            'codigo': codigo,
            'tipo': tipo,
            'valido_hasta': valido_hasta.isoformat(),
            'materia_nombre': materia_nombre
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/codes/active', methods=['GET'])
@validate_token_decorator
def get_active_codes(user):
    """Obtener códigos activos"""
    session = get_db_session()
    
    try:
        ahora = datetime.now()
        
        codigos = session.query(CodigoTemporal).filter(
            CodigoTemporal.generado_por == user['id'],
            CodigoTemporal.activo == True,
            CodigoTemporal.valido_hasta > ahora
        ).order_by(CodigoTemporal.created_at.desc()).limit(20).all()
        
        codes_data = []
        for codigo in codigos:
            codes_data.append({
                'id': codigo.id,
                'codigo': codigo.codigo,
                'tipo': codigo.tipo,
                'valido_hasta': codigo.valido_hasta.isoformat(),
                'usos_actuales': codigo.usos_actuales,
                'max_usos': codigo.max_usos
            })
        
        return jsonify({'success': True, 'codes': codes_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# ============================================
# ENDPOINTS DE REPORTES
# ============================================

@api_bp.route('/reports/generate', methods=['POST'])
@validate_token_decorator
def generate_report(user):
    """Generar reporte"""
    session = get_db_session()
    
    try:
        data = request.json
        tipo = data['tipo']
        formato = data['formato']
        fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
        
        # Crear registro de reporte
        nuevo_reporte = ReporteGenerado(
            tipo=tipo,
            nombre_archivo=f"reporte_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{formato.lower()}",
            formato=formato,
            ruta_archivo=f"/reports/{tipo}_{datetime.now().timestamp()}.{formato.lower()}",
            generado_por=user['id']
        )
        
        session.add(nuevo_reporte)
        session.commit()
        
        # TODO: Generar archivo real con datos
        # Por ahora retornamos un archivo vacío
        from io import BytesIO
        from flask import send_file
        
        buffer = BytesIO()
        buffer.write(b'Reporte pendiente de implementacion')
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf' if formato == 'PDF' else 'application/vnd.ms-excel',
            as_attachment=True,
            download_name=nuevo_reporte.nombre_archivo
        )
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/reports/history', methods=['GET'])
@validate_token_decorator
def get_reports_history(user):
    """Obtener historial de reportes"""
    session = get_db_session()
    
    try:
        reportes = session.query(ReporteGenerado).filter_by(
            generado_por=user['id']
        ).order_by(ReporteGenerado.fecha_generacion.desc()).limit(50).all()
        
        reports_data = []
        for reporte in reportes:
            reports_data.append({
                'id': reporte.id,
                'tipo': reporte.tipo,
                'formato': reporte.formato,
                'nombre_archivo': reporte.nombre_archivo,
                'fecha_generacion': reporte.fecha_generacion.isoformat()
            })
        
        return jsonify({'success': True, 'reports': reports_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# ============================================
# ENDPOINTS DE CONFIGURACIÓN
# ============================================

@api_bp.route('/config', methods=['GET'])
@validate_token_decorator
def get_config(user):
    """Obtener configuración del sistema"""
    session = get_db_session()
    
    try:
        config = session.query(SysConfig).first()
        
        if not config:
            # Crear configuración por defecto
            config = SysConfig(
                modo_operacion='UNIVERSIDAD',
                nombre_institucion='Institución Educativa',
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
                colores_json={
                    'primario': '#023859',
                    'secundario': '#54ACBF',
                    'accent': '#A7EBF2'
                },
                activo=True
            )
            session.add(config)
            session.commit()
        
        return jsonify({
            'success': True,
            'modo_operacion': config.modo_operacion,
            'nombre_institucion': config.nombre_institucion,
            'reglas_json': config.reglas_json,
            'color_primario': config.color_primario,
            'color_secundario': config.color_secundario,
            'actualizado_en': config.actualizado_en.isoformat() if config.actualizado_en else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/config', methods=['PUT'])
@validate_token_decorator
def update_config(user):
    """Actualizar configuración del sistema"""
    session = get_db_session()
    
    try:
        data = request.json
        
        config = session.query(SysConfig).first()
        if not config:
            return jsonify({'success': False, 'error': 'Configuración no encontrada'}), 404
        
        if 'nombre_institucion' in data:
            config.nombre_institucion = data['nombre_institucion']
        
        if 'modo_operacion' in data:
            config.modo_operacion = data['modo_operacion']
        
        if 'reglas_json' in data:
            # Merge con reglas existentes
            current_reglas = config.reglas_json or {}
            current_reglas.update(data['reglas_json'])
            config.reglas_json = current_reglas
        
        if 'color_primario' in data:
            config.color_primario = data['color_primario']
        
        if 'color_secundario' in data:
            config.color_secundario = data['color_secundario']
        
        config.actualizado_en = datetime.now()
        session.commit()
        
        return jsonify({'success': True, 'message': 'Configuración actualizada'})
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# ============================================
# ENDPOINTS DE ESTADÍSTICAS
# ============================================

@api_bp.route('/stats/dashboard', methods=['GET'])
@validate_token_decorator
def get_dashboard_stats(user):
    """Estadísticas del dashboard"""
    session = get_db_session()
    
    try:
        docente = session.query(PersonalAdmin).filter_by(id=user['id']).first()
        if not docente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        # Total materias
        total_materias = session.query(func.count(Materia.id)).filter_by(
            id_docente=docente.id,
            activo=True
        ).scalar() or 0
        
        # Total estudiantes
        materias_ids = [m.id for m in docente.materias if m.activo]
        total_estudiantes = 0
        if materias_ids:
            total_estudiantes = session.query(
                func.count(func.distinct(Inscripcion.id_estudiante))
            ).filter(
                Inscripcion.id_materia.in_(materias_ids),
                Inscripcion.estado == 'ACTIVO'
            ).scalar() or 0
        
        # Asistencias hoy
        hoy = date.today()
        asistencias_hoy = 0
        if materias_ids:
            asistencias_hoy = session.query(func.count(AsistenciaLog.id)).join(
                Inscripcion
            ).filter(
                Inscripcion.id_materia.in_(materias_ids),
                AsistenciaLog.fecha == hoy,
                AsistenciaLog.estado.in_(['PRESENTE', 'TARDANZA'])
            ).scalar() or 0
        
        # Porcentaje promedio
        porcentaje = 0
        if materias_ids:
            avg_porcentaje = session.query(
                func.avg(Inscripcion.porcentaje_asistencia)
            ).filter(
                Inscripcion.id_materia.in_(materias_ids),
                Inscripcion.estado == 'ACTIVO'
            ).scalar()
            porcentaje = round(float(avg_porcentaje or 0), 1)
        
        return jsonify({
            'success': True,
            'total_materias': total_materias,
            'total_estudiantes': total_estudiantes,
            'asistencias_hoy': asistencias_hoy,
            'porcentaje_asistencia': porcentaje
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/stats/summary', methods=['GET'])
@validate_token_decorator
def get_summary_stats(user):
    """Estadísticas resumen para reportes"""
    session = get_db_session()
    
    try:
        docente = session.query(PersonalAdmin).filter_by(id=user['id']).first()
        
        total_reportes = session.query(func.count(ReporteGenerado.id)).filter_by(
            generado_por=user['id']
        ).scalar() or 0
        
        materias_ids = [m.id for m in docente.materias if m.activo]
        
        avg_asistencia = 0
        if materias_ids:
            avg_asistencia = session.query(
                func.avg(Inscripcion.porcentaje_asistencia)
            ).filter(
                Inscripcion.id_materia.in_(materias_ids),
                Inscripcion.estado == 'ACTIVO'
            ).scalar()
            avg_asistencia = round(float(avg_asistencia or 0), 1)
        
        total_estudiantes = 0
        if materias_ids:
            total_estudiantes = session.query(
                func.count(func.distinct(Inscripcion.id_estudiante))
            ).filter(
                Inscripcion.id_materia.in_(materias_ids),
                Inscripcion.estado == 'ACTIVO'
            ).scalar() or 0
        
        return jsonify({
            'success': True,
            'total_reportes': total_reportes,
            'promedio_asistencia': avg_asistencia,
            'total_estudiantes': total_estudiantes,
            'total_materias': len(materias_ids)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

# ============================================
# ALERTAS
# ============================================
@api_bp.route('/alertas/recientes', methods=['GET'])
@validate_token_decorator
def get_alertas_recientes(user):
    """Obtener alertas recientes de deserción"""
    session = get_db_session()
    
    try:
        # Obtener materias del docente
        materias = session.query(Materia.id).filter_by(id_docente=user['id']).all()
        materias_ids = [m[0] for m in materias]
        
        if not materias_ids:
            return jsonify({'alertas': []})
        
        # Por ahora retornar array vacío - implementar lógica de alertas después
        return jsonify({'alertas': []})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# Exportar blueprint
__all__ = ['api_bp']
