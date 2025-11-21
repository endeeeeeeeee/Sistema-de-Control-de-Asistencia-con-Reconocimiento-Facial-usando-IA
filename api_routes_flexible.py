"""
API Routes para Sistema Flexible de Asistencia
Soporta: Universidad, Colegio, Guardería, Empresa, Gym, etc.
"""
from flask import Blueprint, request, jsonify
from auth_manager_flexible import AuthManager
from functools import wraps
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
import os
import socket
import json

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Configuración de base de datos (lazy initialization)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')
_engine = None
_SessionLocal = None

def get_local_ip():
    """Obtener la IP local de la máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_engine():
    """Obtener engine de base de datos (lazy initialization)"""
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,  # Verificar conexiones antes de usarlas
            pool_recycle=3600,   # Reciclar conexiones cada hora
            connect_args={
                "connect_timeout": 5,  # Timeout de conexión de 5 segundos
                "options": "-c statement_timeout=10000"  # Timeout de consultas de 10 segundos
            }
        )
    return _engine

def get_db_session():
    """Obtener sesión de base de datos (lazy initialization)"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()

# Decorator para rutas protegidas
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'success': False, 'error': 'Token no proporcionado'}), 401
            
            if token.startswith('Bearer '):
                token = token[7:]
            
            auth = AuthManager()
            validation = auth.validate_token(token)
            
            if not validation['valid']:
                return jsonify({'success': False, 'error': 'Token inválido o expirado'}), 401
            
            request.current_user = validation['user']
            return f(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            # Detectar errores de conexión a la base de datos
            if 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
                return jsonify({
                    'success': False, 
                    'error': 'Error de conexión a la base de datos'
                }), 503
            return jsonify({'success': False, 'error': 'Error al validar token'}), 500
    
    return decorated

# =====================================================
# AUTENTICACIÓN
# =====================================================

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Registro de nuevo usuario"""
    try:
        data = request.json
        auth = AuthManager()
        
        result = auth.register(
            nombre_completo=data.get('nombre_completo'),
            email=data.get('email'),
            password=data.get('password'),
            telefono=data.get('telefono'),
            ci=data.get('ci'),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            foto_face_vector=data.get('foto_base64')
        )
        
        if result['success']:
            return jsonify(result), 201
        return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Login de usuario"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'Datos no proporcionados'}), 400
        
        auth = AuthManager()
        
        result = auth.login(
            email=data.get('email'),
            password=data.get('password')
        )
        
        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 401
        
    except Exception as e:
        error_msg = str(e)
        # Detectar errores de conexión a la base de datos
        if 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
            return jsonify({
                'success': False, 
                'error': 'Error de conexión a la base de datos. Por favor, contacta al administrador.'
            }), 503
        return jsonify({'success': False, 'error': error_msg}), 500

@api_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    """Cerrar sesión"""
    try:
        token = request.headers.get('Authorization').replace('Bearer ', '')
        auth = AuthManager()
        result = auth.logout(token)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Obtener información del usuario actual"""
    try:
        auth = AuthManager()
        result = auth.get_user_info(request.current_user['id'])
        if result.get('success'):
            return jsonify(result), 200
        return jsonify(result), 401
    except Exception as e:
        error_msg = str(e)
        # Detectar errores de conexión a la base de datos
        if 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
            return jsonify({
                'success': False, 
                'error': 'Error de conexión a la base de datos'
            }), 503
        return jsonify({'success': False, 'error': error_msg}), 500

# =====================================================
# EQUIPOS
# =====================================================

@api_bp.route('/equipos', methods=['GET'])
@token_required
def get_user_teams():
    """Obtener equipos del usuario"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        
        query = text("""
            SELECT 
                e.id, e.nombre_equipo, e.descripcion, e.tipo_equipo, 
                e.codigo_invitacion, e.fecha_creacion,
                m.rol, m.estado,
                u.nombre_completo as creador_nombre,
                (SELECT COUNT(*) FROM membresias WHERE equipo_id = e.id AND estado = 'activo') as total_miembros
            FROM equipos e
            JOIN membresias m ON e.id = m.equipo_id
            JOIN usuarios u ON e.creador_id = u.id
            WHERE m.usuario_id = :user_id AND m.estado = 'activo'
            ORDER BY m.fecha_union DESC
        """)
        
        equipos = session.execute(query, {'user_id': user_id}).fetchall()
        
        result = []
        for equipo in equipos:
            result.append({
                'id': equipo[0],
                'nombre_equipo': equipo[1],
                'descripcion': equipo[2],
                'tipo_equipo': equipo[3],
                'codigo_invitacion': equipo[4],
                'fecha_creacion': equipo[5].isoformat(),
                'mi_rol': equipo[6],
                'estado': equipo[7],
                'creador_nombre': equipo[8],
                'total_miembros': equipo[9]
            })
        
        session.close()
        return jsonify({'success': True, 'equipos': result}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipos', methods=['POST'])
@token_required
def create_team():
    """Crear nuevo equipo"""
    try:
        data = request.json
        session = get_db_session()
        user_id = request.current_user['id']
        
        # Generar código de invitación
        codigo_query = text("SELECT generar_codigo_invitacion()")
        codigo_invitacion = session.execute(codigo_query).scalar()
        
        # Crear equipo
        insert_query = text("""
            INSERT INTO equipos (
                nombre_equipo, descripcion, tipo_equipo, codigo_invitacion, 
                creador_id, configuracion_json
            ) VALUES (
                :nombre, :descripcion, :tipo, :codigo, :creador, '{}'::jsonb
            )
            RETURNING id, codigo_invitacion
        """)
        
        result = session.execute(insert_query, {
            'nombre': data.get('nombre_equipo'),
            'descripcion': data.get('descripcion', ''),
            'tipo': data.get('tipo_equipo', 'otro'),
            'codigo': codigo_invitacion,
            'creador': user_id
        })
        
        equipo = result.fetchone()
        
        # Agregar creador como líder
        membresia_query = text("""
            INSERT INTO membresias (usuario_id, equipo_id, rol, estado)
            VALUES (:user_id, :equipo_id, 'lider', 'activo')
        """)
        
        session.execute(membresia_query, {
            'user_id': user_id,
            'equipo_id': equipo[0]
        })
        
        session.commit()
        session.close()
        
        return jsonify({
            'success': True,
            'equipo_id': equipo[0],
            'codigo_invitacion': equipo[1],
            'message': f'Equipo creado exitosamente. Código: {equipo[1]}'
        }), 201
        
    except Exception as e:
        if 'session' in locals():
            session.rollback()
            session.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipos/unirse', methods=['POST'])
@token_required
def join_team():
    """Unirse a un equipo usando código de invitación"""
    try:
        data = request.json
        codigo = data.get('codigo_invitacion', '').strip().upper()
        session = get_db_session()
        user_id = request.current_user['id']
        
        # Verificar que el equipo existe
        equipo_query = text("""
            SELECT id, nombre_equipo FROM equipos 
            WHERE codigo_invitacion = :codigo AND activo = TRUE
        """)
        equipo = session.execute(equipo_query, {'codigo': codigo}).fetchone()
        
        if not equipo:
            session.close()
            return jsonify({'success': False, 'error': 'Código de invitación inválido'}), 404
        
        # Verificar si ya es miembro
        check_query = text("""
            SELECT id FROM membresias 
            WHERE usuario_id = :user_id AND equipo_id = :equipo_id
        """)
        existing = session.execute(check_query, {
            'user_id': user_id,
            'equipo_id': equipo[0]
        }).fetchone()
        
        if existing:
            session.close()
            return jsonify({'success': False, 'error': 'Ya eres miembro de este equipo'}), 400
        
        # Agregar como miembro
        insert_query = text("""
            INSERT INTO membresias (usuario_id, equipo_id, rol, estado)
            VALUES (:user_id, :equipo_id, 'miembro', 'activo')
        """)
        
        session.execute(insert_query, {
            'user_id': user_id,
            'equipo_id': equipo[0]
        })
        
        session.commit()
        session.close()
        
        return jsonify({
            'success': True,
            'message': f'Te uniste exitosamente a: {equipo[1]}'
        }), 200
        
    except Exception as e:
        if 'session' in locals():
            session.rollback()
            session.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipos/<int:equipo_id>', methods=['GET'])
@token_required
def get_team_details(equipo_id):
    """Obtener detalles de un equipo"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        
        # Verificar que el usuario es miembro
        check_query = text("""
            SELECT m.rol FROM membresias m
            WHERE m.usuario_id = :user_id AND m.equipo_id = :equipo_id AND m.estado = 'activo'
        """)
        membresia = session.execute(check_query, {
            'user_id': user_id,
            'equipo_id': equipo_id
        }).fetchone()
        
        if not membresia:
            session.close()
            return jsonify({'success': False, 'error': 'No eres miembro de este equipo'}), 403
        
        # Obtener detalles del equipo
        equipo_query = text("""
            SELECT 
                e.id, e.nombre_equipo, e.descripcion, e.tipo_equipo,
                e.codigo_invitacion, e.fecha_creacion, e.configuracion_json,
                u.nombre_completo as creador_nombre
            FROM equipos e
            JOIN usuarios u ON e.creador_id = u.id
            WHERE e.id = :equipo_id
        """)
        equipo = session.execute(equipo_query, {'equipo_id': equipo_id}).fetchone()
        
        # Obtener miembros con cálculo dinámico de asistencias desde asistencia_log
        miembros_query = text("""
            SELECT 
                u.id, u.codigo_usuario, u.nombre_completo, u.email,
                m.rol, m.fecha_union,
                COALESCE(COUNT(DISTINCT al.fecha), 0) as asistencias_reales,
                COALESCE(
                    (SELECT COUNT(DISTINCT fecha) 
                     FROM asistencia_log 
                     WHERE membresia_id IN (SELECT id FROM membresias WHERE equipo_id = :equipo_id)) - 
                    COUNT(DISTINCT al.fecha), 
                    0
                ) as faltas_calculadas,
                CASE 
                    WHEN (SELECT COUNT(DISTINCT fecha) FROM asistencia_log WHERE membresia_id IN (SELECT id FROM membresias WHERE equipo_id = :equipo_id)) > 0
                    THEN (COUNT(DISTINCT al.fecha) * 100.0) / (SELECT COUNT(DISTINCT fecha) FROM asistencia_log WHERE membresia_id IN (SELECT id FROM membresias WHERE equipo_id = :equipo_id))
                    ELSE 0
                END as porcentaje_calculado
            FROM membresias m
            JOIN usuarios u ON m.usuario_id = u.id
            LEFT JOIN asistencia_log al ON m.id = al.membresia_id
            WHERE m.equipo_id = :equipo_id AND m.estado = 'activo'
            GROUP BY u.id, u.codigo_usuario, u.nombre_completo, u.email, m.rol, m.fecha_union, m.id
            ORDER BY m.rol DESC, m.fecha_union ASC
        """)
        miembros = session.execute(miembros_query, {'equipo_id': equipo_id}).fetchall()
        
        result = {
            'success': True,
            'equipo': {
                'id': equipo[0],
                'nombre_equipo': equipo[1],
                'descripcion': equipo[2],
                'tipo_equipo': equipo[3],
                'codigo_invitacion': equipo[4],
                'fecha_creacion': equipo[5].isoformat(),
                'configuracion': equipo[6],
                'creador_nombre': equipo[7],
                'mi_rol': membresia[0]
            },
            'miembros': [{
                'id': m[0],
                'codigo_usuario': m[1],
                'nombre_completo': m[2],
                'email': m[3],
                'rol': m[4],
                'fecha_union': m[5].isoformat(),
                'asistencias_totales': m[6],
                'faltas_totales': m[7],
                'porcentaje_asistencia': float(m[8]) if m[8] else 0
            } for m in miembros]
        }
        
        session.close()
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipos/<int:equipo_id>', methods=['DELETE'])
@token_required
def delete_team(equipo_id):
    """Eliminar equipo (solo lider)"""
    try:
        print(f"🗑️ Intentando eliminar equipo ID: {equipo_id}")
        session = get_db_session()
        user_id = request.current_user['id']
        print(f"👤 Usuario solicitante ID: {user_id}")
        
        # Verificar que el usuario es el creador/lider
        check_query = text("""
            SELECT e.id, e.nombre_equipo, e.creador_id
            FROM equipos e
            WHERE e.id = :equipo_id
        """)
        equipo = session.execute(check_query, {
            'equipo_id': equipo_id
        }).fetchone()
        
        if not equipo:
            print(f"❌ Equipo {equipo_id} no encontrado")
            session.close()
            return jsonify({'success': False, 'error': 'Equipo no encontrado'}), 404
        
        print(f"📋 Equipo encontrado: {equipo[1]} (Creador ID: {equipo[2]})")
        
        if equipo[2] != user_id:
            print(f"❌ Usuario {user_id} no es el creador del equipo (creador: {equipo[2]})")
            session.close()
            return jsonify({'success': False, 'error': 'Solo el líder puede eliminar el equipo'}), 403
        
        # Eliminar equipo (las relaciones se eliminan en cascada)
        print(f"🗑️ Eliminando equipo {equipo_id}...")
        delete_query = text("DELETE FROM equipos WHERE id = :equipo_id")
        session.execute(delete_query, {'equipo_id': equipo_id})
        
        session.commit()
        session.close()
        
        print(f"✅ Equipo '{equipo[1]}' eliminado exitosamente")
        return jsonify({
            'success': True,
            'message': f'Equipo "{equipo[1]}" eliminado exitosamente'
        }), 200
        
    except Exception as e:
        print(f"❌ Error al eliminar equipo: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# ASISTENCIA
# =====================================================

@api_bp.route('/asistencia/marcar', methods=['POST'])
@token_required
def mark_attendance():
    """Marcar asistencia (facial, QR o manual)"""
    try:
        data = request.json
        session = get_db_session()
        user_id = request.current_user['id']
        equipo_id = data.get('equipo_id')
        metodo = data.get('metodo', 'manual')
        
        # Obtener membresía
        membresia_query = text("""
            SELECT id FROM membresias
            WHERE usuario_id = :user_id AND equipo_id = :equipo_id AND estado = 'activo'
        """)
        membresia = session.execute(membresia_query, {
            'user_id': user_id,
            'equipo_id': equipo_id
        }).fetchone()
        
        if not membresia:
            session.close()
            return jsonify({'success': False, 'error': 'No eres miembro de este equipo'}), 403
        
        # Verificar si ya marcó hoy
        check_query = text("""
            SELECT id FROM asistencia_log
            WHERE membresia_id = :membresia_id AND fecha = CURRENT_DATE
        """)
        existing = session.execute(check_query, {'membresia_id': membresia[0]}).fetchone()
        
        if existing:
            session.close()
            return jsonify({'success': False, 'error': 'Ya marcaste asistencia hoy'}), 400
        
        # Registrar asistencia
        insert_query = text("""
            INSERT INTO asistencia_log (
                membresia_id, metodo_entrada, estado, foto_verificacion
            ) VALUES (
                :membresia_id, :metodo, 'presente', :foto
            )
            RETURNING id
        """)
        
        result = session.execute(insert_query, {
            'membresia_id': membresia[0],
            'metodo': metodo,
            'foto': data.get('foto_base64')
        })
        
        asistencia_id = result.scalar()
        
        session.commit()
        session.close()
        
        return jsonify({
            'success': True,
            'asistencia_id': asistencia_id,
            'message': 'Asistencia registrada exitosamente'
        }), 201
        
    except Exception as e:
        if 'session' in locals():
            session.rollback()
            session.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# ESTADÍSTICAS
# =====================================================

@api_bp.route('/stats/dashboard', methods=['GET'])
@token_required
def get_dashboard_stats():
    """Estadísticas para el dashboard"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        
        stats_query = text("""
            SELECT 
                COUNT(DISTINCT m.equipo_id) as total_equipos,
                COUNT(DISTINCT CASE WHEN m.rol = 'lider' THEN m.equipo_id END) as equipos_lidero,
                COUNT(DISTINCT CASE WHEN a.fecha = CURRENT_DATE THEN a.id END) as asistencias_hoy
            FROM membresias m
            LEFT JOIN asistencia_log a ON m.id = a.membresia_id
            WHERE m.usuario_id = :user_id AND m.estado = 'activo'
        """)
        
        stats = session.execute(stats_query, {'user_id': user_id}).fetchone()
        
        session.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_equipos': stats[0] or 0,
                'equipos_lidero': stats[1] or 0,
                'asistencias_hoy': stats[2] or 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# QR DE UN SOLO USO
# =====================================================

@api_bp.route('/qr/generar-individual', methods=['POST'])
@token_required
def generate_individual_qr():
    """Generar QR de un solo uso para un miembro específico"""
    try:
        data = request.json
        session = get_db_session()
        lider_id = request.current_user['id']
        equipo_id = data.get('equipo_id')
        usuario_id = data.get('usuario_id')  # Usuario para quien se genera el QR
        duracion_minutos = data.get('duracion_minutos', 5)  # Por defecto 5 minutos
        
        print(f"🎫 Generando QR individual para usuario {usuario_id} en equipo {equipo_id}")
        
        # Verificar que quien genera el QR es líder o co-líder
        lider_check = text("""
            SELECT rol FROM membresias
            WHERE usuario_id = :lider_id AND equipo_id = :equipo_id 
            AND estado = 'activo' AND rol IN ('lider', 'co-lider')
        """)
        lider = session.execute(lider_check, {
            'lider_id': lider_id,
            'equipo_id': equipo_id
        }).fetchone()
        
        if not lider:
            session.close()
            return jsonify({'success': False, 'error': 'Solo líderes pueden generar QR'}), 403
        
        # Verificar que el usuario objetivo es miembro del equipo
        miembro_check = text("""
            SELECT m.id, u.nombre_completo 
            FROM membresias m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.usuario_id = :usuario_id AND m.equipo_id = :equipo_id 
            AND m.estado = 'activo'
        """)
        miembro = session.execute(miembro_check, {
            'usuario_id': usuario_id,
            'equipo_id': equipo_id
        }).fetchone()
        
        if not miembro:
            session.close()
            return jsonify({'success': False, 'error': 'Usuario no es miembro del equipo'}), 404
        
        # Verificar si ya marcó asistencia hoy
        asistencia_check = text("""
            SELECT id FROM asistencia_log
            WHERE membresia_id = :membresia_id AND fecha = CURRENT_DATE
        """)
        ya_marco = session.execute(asistencia_check, {
            'membresia_id': miembro[0]
        }).fetchone()
        
        if ya_marco:
            session.close()
            return jsonify({
                'success': False, 
                'error': f'{miembro[1]} ya marcó asistencia hoy'
            }), 400
        
        # Generar código QR único
        import secrets
        codigo_qr = f"QR-{secrets.token_urlsafe(16)}"
        
        # Guardar en tabla codigos_temporales
        insert_qr = text("""
            INSERT INTO codigos_temporales (
                codigo, tipo, usuario_id, equipo_id, expira_en, valido_hasta, usado, metadata, generado_por
            ) VALUES (
                :codigo, 'QR_CLASE_VIRTUAL', :usuario_id, :equipo_id, 
                NOW() + INTERVAL ':minutos minutes', 
                NOW() + INTERVAL ':minutos minutes',
                false, :metadata, :generado_por
            )
            RETURNING id, expira_en
        """)
        
        result = session.execute(insert_qr, {
            'codigo': codigo_qr,
            'usuario_id': usuario_id,
            'equipo_id': equipo_id,
            'minutos': duracion_minutos,
            'metadata': f'{{"nombre_usuario": "{miembro[1]}"}}',
            'generado_por': lider_id
        })
        
        qr_data = result.fetchone()
        qr_id = qr_data[0]
        expira_en = qr_data[1]
        
        session.commit()
        session.close()
        
        print(f"✅ QR generado: {codigo_qr} para {miembro[1]}")
        
        return jsonify({
            'success': True,
            'qr_code': codigo_qr,
            'qr_id': qr_id,
            'usuario_nombre': miembro[1],
            'expira_en': expira_en.isoformat(),
            'duracion_minutos': duracion_minutos,
            'message': f'QR generado para {miembro[1]}'
        }), 201
        
    except Exception as e:
        print(f"❌ Error generando QR: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/qr/validar', methods=['POST'])
def validate_qr():
    """Validar y usar QR de un solo uso (público, no requiere token)"""
    try:
        data = request.json
        codigo_qr = data.get('codigo_qr')
        
        if not codigo_qr:
            return jsonify({'success': False, 'error': 'Código QR requerido'}), 400
        
        print(f"🔍 Validando QR: {codigo_qr}")
        
        session = get_db_session()
        
        # Buscar código QR
        qr_query = text("""
            SELECT id, usuario_id, equipo_id, expira_en, usado, metadata
            FROM codigos_temporales
            WHERE codigo = :codigo AND tipo = 'QR_CLASE_VIRTUAL'
        """)
        qr = session.execute(qr_query, {'codigo': codigo_qr}).fetchone()
        
        if not qr:
            session.close()
            return jsonify({'success': False, 'error': 'Código QR inválido'}), 404
        
        qr_id, usuario_id, equipo_id, expira_en, usado, metadata = qr
        
        # Verificar si ya fue usado
        if usado:
            session.close()
            return jsonify({'success': False, 'error': 'Este QR ya fue utilizado'}), 400
        
        # Verificar si expiró
        if datetime.now() > expira_en:
            session.close()
            return jsonify({'success': False, 'error': 'Este QR ha expirado'}), 400
        
        # Obtener membresía
        membresia_query = text("""
            SELECT m.id, u.nombre_completo, e.nombre_equipo
            FROM membresias m
            JOIN usuarios u ON m.usuario_id = u.id
            JOIN equipos e ON m.equipo_id = e.id
            WHERE m.usuario_id = :usuario_id AND m.equipo_id = :equipo_id 
            AND m.estado = 'activo'
        """)
        membresia = session.execute(membresia_query, {
            'usuario_id': usuario_id,
            'equipo_id': equipo_id
        }).fetchone()
        
        if not membresia:
            session.close()
            return jsonify({'success': False, 'error': 'Membresía no encontrada'}), 404
        
        membresia_id, nombre_usuario, nombre_equipo = membresia
        
        # Verificar si ya marcó hoy
        asistencia_check = text("""
            SELECT id FROM asistencia_log
            WHERE membresia_id = :membresia_id AND fecha = CURRENT_DATE
        """)
        ya_marco = session.execute(asistencia_check, {
            'membresia_id': membresia_id
        }).fetchone()
        
        if ya_marco:
            session.close()
            return jsonify({
                'success': False, 
                'error': 'Ya marcaste asistencia hoy'
            }), 400
        
        # Marcar asistencia
        insert_asistencia = text("""
            INSERT INTO asistencia_log (
                membresia_id, metodo_entrada, estado, notas
            ) VALUES (
                :membresia_id, 'qr', 'presente', :notas
            )
            RETURNING id
        """)
        
        result = session.execute(insert_asistencia, {
            'membresia_id': membresia_id,
            'notas': f'QR de un solo uso generado por líder'
        })
        
        asistencia_id = result.scalar()
        
        # Marcar QR como usado
        update_qr = text("""
            UPDATE codigos_temporales
            SET usado = true, usado_en = NOW()
            WHERE id = :qr_id
        """)
        session.execute(update_qr, {'qr_id': qr_id})
        
        session.commit()
        session.close()
        
        print(f"✅ Asistencia marcada para {nombre_usuario} vía QR")
        
        return jsonify({
            'success': True,
            'asistencia_id': asistencia_id,
            'usuario': nombre_usuario,
            'equipo': nombre_equipo,
            'message': f'✅ Asistencia marcada para {nombre_usuario}'
        }), 200
        
    except Exception as e:
        print(f"❌ Error validando QR: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# SESIONES DE ASISTENCIA EN VIVO
# =====================================================

@api_bp.route('/sesiones/iniciar', methods=['POST'])
@token_required
def start_attendance_session():
    """Iniciar sesión de asistencia con reconocimiento facial en vivo"""
    try:
        data = request.json
        session = get_db_session()
        user_id = request.current_user['id']
        equipo_id = data.get('equipo_id')
        duracion_minutos = data.get('duracion_minutos', 30)
        
        print(f"🎬 Iniciando sesión de asistencia para equipo {equipo_id}")
        
        # Verificar que el usuario es líder
        lider_check = text("""
            SELECT rol FROM membresias
            WHERE usuario_id = :user_id AND equipo_id = :equipo_id 
            AND estado = 'activo' AND rol IN ('lider', 'co-lider')
        """)
        lider = session.execute(lider_check, {
            'user_id': user_id,
            'equipo_id': equipo_id
        }).fetchone()
        
        if not lider:
            session.close()
            return jsonify({'success': False, 'error': 'Solo líderes pueden iniciar sesiones'}), 403
        
        # Primero limpiar sesiones expiradas
        limpiar_expiradas = text("""
            UPDATE codigos_temporales
            SET usado = true, usado_en = NOW()
            WHERE tipo = 'SESION_ASISTENCIA'
            AND usado = false
            AND NOW() >= expira_en
        """)
        session.execute(limpiar_expiradas)
        session.commit()
        
        # Verificar si ya hay una sesión activa
        sesion_activa_check = text("""
            SELECT id FROM codigos_temporales
            WHERE equipo_id = :equipo_id 
            AND tipo = 'SESION_ASISTENCIA'
            AND usado = false
            AND NOW() < expira_en
        """)
        sesion_existente = session.execute(sesion_activa_check, {
            'equipo_id': equipo_id
        }).fetchone()
        
        if sesion_existente:
            session.close()
            return jsonify({'success': False, 'error': 'Ya hay una sesión activa para este equipo'}), 400
        
        # Crear sesión
        import secrets
        codigo_sesion = f"SESION-{secrets.token_urlsafe(12)}"
        
        insert_sesion = text("""
            INSERT INTO codigos_temporales (
                codigo, tipo, equipo_id, expira_en, valido_hasta, 
                usado, metadata, generado_por
            ) VALUES (
                :codigo, 'SESION_ASISTENCIA', :equipo_id, 
                NOW() + INTERVAL ':minutos minutes',
                NOW() + INTERVAL ':minutos minutes',
                false, :metadata, :generado_por
            )
            RETURNING id, expira_en
        """)
        
        result = session.execute(insert_sesion, {
            'codigo': codigo_sesion,
            'equipo_id': equipo_id,
            'minutos': duracion_minutos,
            'metadata': f'{{"duracion": {duracion_minutos}, "reconocimientos": []}}',
            'generado_por': user_id
        })
        
        sesion_data = result.fetchone()
        sesion_id = sesion_data[0]
        expira_en = sesion_data[1]
        
        session.commit()
        session.close()
        
        print(f"✅ Sesión creada: {codigo_sesion}")
        
        return jsonify({
            'success': True,
            'sesion_id': sesion_id,
            'codigo_sesion': codigo_sesion,
            'expira_en': expira_en.isoformat(),
            'duracion_minutos': duracion_minutos,
            'message': 'Sesión de asistencia iniciada'
        }), 201
        
    except Exception as e:
        print(f"❌ Error iniciando sesión: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/sesiones/<int:sesion_id>/detener', methods=['POST'])
@token_required
def stop_attendance_session(sesion_id):
    """Detener sesión de asistencia"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        
        # Verificar sesión y permisos
        sesion_check = text("""
            SELECT ct.equipo_id, ct.generado_por
            FROM codigos_temporales ct
            WHERE ct.id = :sesion_id AND ct.tipo = 'SESION_ASISTENCIA'
        """)
        sesion_data = session.execute(sesion_check, {'sesion_id': sesion_id}).fetchone()
        
        if not sesion_data:
            session.close()
            return jsonify({'success': False, 'error': 'Sesión no encontrada'}), 404
        
        # Marcar sesión como terminada
        update_sesion = text("""
            UPDATE codigos_temporales
            SET usado = true, usado_en = NOW()
            WHERE id = :sesion_id
        """)
        session.execute(update_sesion, {'sesion_id': sesion_id})
        
        session.commit()
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Sesión de asistencia detenida'
        }), 200
        
    except Exception as e:
        if 'session' in locals():
            session.rollback()
            session.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/sesiones/<int:sesion_id>/reconocimientos', methods=['GET'])
@token_required
def get_session_recognitions(sesion_id):
    """Obtener reconocimientos de una sesión"""
    try:
        session = get_db_session()
        
        # Obtener reconocimientos
        query = text("""
            SELECT 
                u.codigo_usuario, u.nombre_completo, a.hora_entrada,
                a.metodo_entrada, a.confianza_reconocimiento
            FROM asistencia_log a
            JOIN membresias m ON a.membresia_id = m.id
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE a.fecha = CURRENT_DATE
            AND m.equipo_id = (SELECT equipo_id FROM codigos_temporales WHERE id = :sesion_id)
            ORDER BY a.hora_entrada DESC
        """)
        
        reconocimientos = session.execute(query, {'sesion_id': sesion_id}).fetchall()
        
        result = [{
            'codigo_usuario': r[0],
            'nombre_completo': r[1],
            'hora_entrada': r[2].isoformat() if r[2] else None,
            'metodo': r[3],
            'confianza': float(r[4]) if r[4] else 0
        } for r in reconocimientos]
        
        session.close()
        
        return jsonify({
            'success': True,
            'reconocimientos': result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# RECONOCIMIENTO FACIAL
# =====================================================

@api_bp.route('/facial/reconocer-frame', methods=['POST'])
@token_required
def recognize_face_frame():
    """Reconocer rostro desde un frame de video"""
    try:
        import cv2
        import numpy as np
        from pathlib import Path
        import base64
        
        data = request.json
        imagen_base64 = data.get('imagen')
        sesion_id = data.get('sesion_id')
        
        if not imagen_base64 or not sesion_id:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        # Decodificar imagen
        if ',' in imagen_base64:
            imagen_base64 = imagen_base64.split(',')[1]
        
        img_data = base64.b64decode(imagen_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'success': False, 'error': 'Imagen inválida'}), 400
        
        # Verificar sesión activa
        db_session = get_db_session()
        
        sesion_check = text("""
            SELECT equipo_id FROM codigos_temporales
            WHERE id = :sesion_id 
            AND tipo = 'SESION_ASISTENCIA'
            AND usado = false
            AND NOW() < expira_en
        """)
        sesion_data = db_session.execute(sesion_check, {'sesion_id': sesion_id}).fetchone()
        
        if not sesion_data:
            db_session.close()
            return jsonify({'success': False, 'error': 'Sesión inválida o expirada'}), 400
        
        equipo_id = sesion_data[0]
        
        # Detectar rostros
        print("🔍 Iniciando detección facial...")
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
        if face_cascade.empty():
            print("❌ ERROR: No se pudo cargar haarcascade_frontalface_default.xml")
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Error al cargar clasificador Haar Cascade'
            }), 500
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print(f"📷 Imagen convertida a gris: {gray.shape}")
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        print(f"👤 Rostros detectados: {len(faces)}")
        
        if len(faces) == 0:
            db_session.close()
            return jsonify({
                'success': True,
                'reconocido': False,
                'mensaje': 'No se detectó ningún rostro'
            }), 200
        
        # Obtener miembros del equipo con modelos entrenados
        miembros_query = text("""
            SELECT u.id, u.codigo_usuario, u.nombre_completo, m.id as membresia_id
            FROM membresias m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.equipo_id = :equipo_id 
            AND m.estado = 'activo'
            AND u.foto_face_vector IS NOT NULL
        """)
        miembros = db_session.execute(miembros_query, {'equipo_id': equipo_id}).fetchall()
        print(f"👥 Miembros del equipo con modelos: {len(miembros)}")
        for miembro in miembros:
            print(f"   - {miembro[1]}: {miembro[2]}")
        
        # Intentar reconocer cada rostro
        model_dir = Path('TrainingImageLabel')
        mejor_match = None
        mejor_confianza = 100
        
        # Leer umbrales de confianza desde configuración
        # Sistema de RANGO: solo acepta valores entre UMBRAL_MINIMO y UMBRAL_MAXIMO
        # Valores menores = mejor reconocimiento (0=perfecto, 100=no match)
        # Configuración actual: 30-50 (muy estricto, solo reconocimientos excelentes)
        try:
            config_path = Path('config/recognition_config.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    reconocimiento_config = config.get('reconocimiento_facial', {})
                    UMBRAL_MINIMO = reconocimiento_config.get('umbral_minimo', 30)
                    UMBRAL_MAXIMO = reconocimiento_config.get('umbral_maximo', 50)
            else:
                UMBRAL_MINIMO = 30
                UMBRAL_MAXIMO = 50
        except:
            UMBRAL_MINIMO = 30  # Valor mínimo aceptable
            UMBRAL_MAXIMO = 50  # Valor máximo aceptable
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (200, 200))
            
            for miembro in miembros:
                try:
                    codigo_usuario = miembro[1]
                    model_path = model_dir / f"{codigo_usuario}_model.yml"
                    
                    if model_path.exists():
                        recognizer = cv2.face.LBPHFaceRecognizer_create()
                        recognizer.read(str(model_path))
                        
                        label, confidence = recognizer.predict(face_resized)
                        
                        print(f"🔍 {codigo_usuario}: confianza={confidence:.2f} (rango permitido: {UMBRAL_MINIMO}-{UMBRAL_MAXIMO})")
                        
                        # Solo considerar si está en el rango permitido
                        if UMBRAL_MINIMO <= confidence <= UMBRAL_MAXIMO:
                            if confidence < mejor_confianza:
                                mejor_confianza = confidence
                                mejor_match = miembro
                except Exception as e:
                    print(f"⚠️ Error reconociendo {codigo_usuario}: {e}")
                    continue
        
        if mejor_match:
            usuario_id, codigo_usuario, nombre_completo, membresia_id = mejor_match
            
            # Verificar si ya marcó hoy
            asistencia_check = text("""
                SELECT id FROM asistencia_log
                WHERE membresia_id = :membresia_id AND fecha = CURRENT_DATE
            """)
            ya_marco = db_session.execute(asistencia_check, {
                'membresia_id': membresia_id
            }).fetchone()
            
            if ya_marco:
                db_session.close()
                return jsonify({
                    'success': True,
                    'reconocido': True,
                    'ya_registrado': True,
                    'nombre': nombre_completo,
                    'codigo': codigo_usuario,
                    'mensaje': f'{nombre_completo} ya registró asistencia hoy'
                }), 200
            
            # Registrar asistencia
            insert_asistencia = text("""
                INSERT INTO asistencia_log (
                    membresia_id, metodo_entrada, estado
                ) VALUES (
                    :membresia_id, 'facial', 'presente'
                )
                RETURNING id
            """)
            
            result = db_session.execute(insert_asistencia, {
                'membresia_id': membresia_id
            })
            
            asistencia_id = result.scalar()
            
            db_session.commit()
            db_session.close()
            
            # Calcular porcentaje de confianza (100 = perfecto, 0 = malo)
            porcentaje_confianza = max(0, round(100 - mejor_confianza, 2))
            
            print(f"✅ Asistencia registrada: {nombre_completo} (confianza: {porcentaje_confianza}%)")
            
            return jsonify({
                'success': True,
                'reconocido': True,
                'ya_registrado': False,
                'asistencia_id': asistencia_id,
                'nombre': nombre_completo,
                'codigo': codigo_usuario,
                'confianza': porcentaje_confianza,
                'mensaje': f'✅ {nombre_completo} - Asistencia registrada ({porcentaje_confianza}% confianza)'
            }), 200
        
        db_session.close()
        
        # Si hay reconocimientos pero ninguno pasó el filtro de rango
        if mejor_confianza < 100:
            porcentaje_confianza = max(0, round(100 - mejor_confianza, 2))
            
            # Rechazado por ser demasiado perfecto (posible foto/fraude)
            if mejor_confianza < UMBRAL_MINIMO:
                print(f"🚫 RECHAZADO - Demasiado perfecto: {mejor_confianza:.2f} < {UMBRAL_MINIMO}")
                return jsonify({
                    'success': True,
                    'reconocido': False,
                    'mensaje': f'🚫 Reconocimiento sospechoso (valor {mejor_confianza:.1f} demasiado perfecto).\n\n💡 Si tiene complicaciones faciales, solicite registro manual.',
                    'motivo': 'demasiado_perfecto',
                    'mejor_confianza': round(mejor_confianza, 2),
                    'rango_requerido': f'{UMBRAL_MINIMO}-{UMBRAL_MAXIMO}'
                }), 200
            
            # Rechazado por confianza insuficiente (>50)
            print(f"⚠️ RECHAZADO - Confianza baja: {mejor_confianza:.2f} > {UMBRAL_MAXIMO}")
            return jsonify({
                'success': True,
                'reconocido': False,
                'mensaje': f'🔴 Confianza insuficiente ({mejor_confianza:.1f}). Debe estar entre {UMBRAL_MINIMO}-{UMBRAL_MAXIMO}.\n\n💡 Mejora la iluminación o solicita registro manual.',
                'mejor_confianza': round(mejor_confianza, 2),
                'porcentaje': porcentaje_confianza,
                'rango_requerido': f'{UMBRAL_MINIMO}-{UMBRAL_MAXIMO}'
            }), 200
        
        # No se detectó ningún rostro conocido
        return jsonify({
            'success': True,
            'reconocido': False,
            'mensaje': '❌ Rostro no reconocido en el sistema.\n\n💡 Solicita registro manual si tienes complicaciones faciales.'
        }), 200
        
    except Exception as e:
        print(f"❌ Error en reconocimiento: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'db_session' in locals():
            db_session.rollback()
            db_session.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/facial/guardar-fotos', methods=['POST'])
@token_required
def save_facial_photos():
    """Guardar fotos faciales y entrenar modelo (acepta lotes)"""
    try:
        import base64
        import cv2
        import numpy as np
        from pathlib import Path
        
        data = request.json
        fotos_base64 = data.get('fotos', [])
        batch_number = data.get('batch_number', 1)
        total_batches = data.get('total_batches', 1)
        is_final = data.get('is_final', True)
        
        user_id = request.current_user['id']
        codigo_usuario = request.current_user['codigo_usuario']
        
        print(f"[FACIAL] Recibiendo lote {batch_number}/{total_batches} - {len(fotos_base64)} fotos - Usuario: {codigo_usuario} - Final: {is_final}")
        
        if len(fotos_base64) < 10:
            print(f"[FACIAL ERROR] Solo {len(fotos_base64)} fotos recibidas, se necesitan al menos 10")
            return jsonify({
                'success': False, 
                'error': 'Se necesitan al menos 10 fotos'
            }), 400
        
        # Crear directorio para las fotos
        training_dir = Path('TrainingImage')
        training_dir.mkdir(exist_ok=True)
        
        user_dir = training_dir / codigo_usuario
        user_dir.mkdir(exist_ok=True)
        
        # Guardar fotos
        saved_count = 0
        # Calcular índice inicial basado en el lote actual
        start_idx = (batch_number - 1) * 10
        
        for idx, foto_base64 in enumerate(fotos_base64):
            try:
                # Remover prefijo data:image/jpeg;base64,
                if ',' in foto_base64:
                    foto_base64 = foto_base64.split(',')[1]
                
                # Decodificar base64
                img_data = base64.b64decode(foto_base64)
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    # Guardar imagen con índice global (no local al lote)
                    global_idx = start_idx + idx + 1
                    filename = user_dir / f"{codigo_usuario}_{global_idx}.jpg"
                    cv2.imwrite(str(filename), img)
                    saved_count += 1
                    
            except Exception as e:
                print(f"⚠️ Error procesando foto {idx}: {str(e)}")
                continue
        
        print(f"[FACIAL] Lote {batch_number}/{total_batches} guardado: {saved_count} fotos")
        
        # Solo entrenar modelo en el último lote
        model_trained = False
        if is_final:
            print(f"[FACIAL] ULTIMO LOTE - Iniciando entrenamiento para {codigo_usuario}")
            try:
                train_model(codigo_usuario)
                print(f"[FACIAL] MODELO ENTRENADO EXITOSAMENTE para {codigo_usuario}")
                model_trained = True
            except Exception as e:
                print(f"[FACIAL ERROR] Error al entrenar modelo: {str(e)}")
                model_trained = False
            
            # Actualizar base de datos solo en el último lote
            session = get_db_session()
            update_query = text("""
                UPDATE usuarios 
                SET foto_face_vector = :foto_path,
                    fecha_ultima_actualizacion_facial = NOW()
                WHERE id = :user_id
            """)
            
            session.execute(update_query, {
                'user_id': user_id,
                'foto_path': str(user_dir)
            })
            
            session.commit()
            session.close()
            print(f"✅ Base de datos actualizada para {codigo_usuario}")
        
        return jsonify({
            'success': True,
            'fotos_guardadas': saved_count,
            'modelo_entrenado': model_trained,
            'message': f'Se guardaron {saved_count} fotos exitosamente'
        }), 200
        
    except Exception as e:
        print(f"❌ Error guardando fotos: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def train_model(codigo_usuario):
    """Entrenar modelo de reconocimiento facial para un usuario"""
    import cv2
    import numpy as np
    from pathlib import Path
    
    # Cargar clasificador de rostros
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Preparar datos de entrenamiento
    faces = []
    labels = []
    
    user_dir = Path('TrainingImage') / codigo_usuario
    
    if not user_dir.exists():
        raise Exception(f"Directorio no encontrado: {user_dir}")
    
    # Procesar cada imagen
    for img_path in user_dir.glob('*.jpg'):
        img = cv2.imread(str(img_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detectar rostros
        detected_faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in detected_faces:
            face = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face, (200, 200))
            faces.append(face_resized)
            labels.append(codigo_usuario)
    
    if len(faces) == 0:
        raise Exception("No se detectaron rostros en las fotos")
    
    print(f"📊 Entrenando con {len(faces)} rostros detectados")
    
    # Crear y entrenar reconocedor LBPH
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    # Convertir labels a enteros (usar hash del codigo_usuario)
    label_id = hash(codigo_usuario) % 100000
    labels_int = [label_id] * len(faces)
    
    recognizer.train(faces, np.array(labels_int))
    
    # Guardar modelo
    model_dir = Path('TrainingImageLabel')
    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / f"{codigo_usuario}_model.yml"
    recognizer.save(str(model_path))
    
    print(f"✅ Modelo guardado en {model_path}")
    
    return str(model_path)

# =====================================================
# REPORTES Y EXPORTACIÓN
# =====================================================

@api_bp.route('/reportes/asistencias', methods=['GET'])
@token_required
def get_attendance_report():
    """Obtener reporte de asistencias con filtros"""
    try:
        equipo_id = request.args.get('equipo_id', type=int)
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        session = get_db_session()
        user_id = request.current_user['id']
        
        # Query base
        query = text("""
            SELECT 
                al.id,
                al.fecha,
                al.hora_entrada,
                al.metodo_entrada,
                al.estado,
                u.codigo_usuario,
                u.nombre_completo,
                e.nombre_equipo
            FROM asistencia_log al
            JOIN membresias m ON al.membresia_id = m.id
            JOIN usuarios u ON m.usuario_id = u.id
            JOIN equipos e ON m.equipo_id = e.id
            WHERE (:equipo_id IS NULL OR m.equipo_id = :equipo_id)
            AND (:fecha_inicio IS NULL OR al.fecha >= :fecha_inicio)
            AND (:fecha_fin IS NULL OR al.fecha <= :fecha_fin)
            ORDER BY al.fecha DESC, al.hora_entrada DESC
            LIMIT 1000
        """)
        
        results = session.execute(query, {
            'equipo_id': equipo_id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }).fetchall()
        
        asistencias = [{
            'id': r[0],
            'fecha': r[1].isoformat() if r[1] else None,
            'hora_entrada': str(r[2]) if r[2] else None,
            'metodo_entrada': r[3],
            'estado': r[4],
            'codigo_usuario': r[5],
            'nombre_completo': r[6],
            'equipo': r[7]
        } for r in results]
        
        session.close()
        
        return jsonify({
            'success': True,
            'total': len(asistencias),
            'asistencias': asistencias
        }), 200
        
    except Exception as e:
        print(f"❌ Error en reporte: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/reportes/export/excel', methods=['POST'])
@token_required
def export_excel():
    """Exportar asistencias a Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import send_file
        
        data = request.json
        equipo_id = data.get('equipo_id')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        session = get_db_session()
        
        query = text("""
            SELECT 
                al.fecha,
                al.hora_entrada,
                u.codigo_usuario,
                u.nombre_completo,
                e.nombre_equipo,
                al.metodo_entrada,
                al.estado
            FROM asistencia_log al
            JOIN membresias m ON al.membresia_id = m.id
            JOIN usuarios u ON m.usuario_id = u.id
            JOIN equipos e ON m.equipo_id = e.id
            WHERE (:equipo_id IS NULL OR m.equipo_id = :equipo_id)
            AND (:fecha_inicio IS NULL OR al.fecha >= :fecha_inicio)
            AND (:fecha_fin IS NULL OR al.fecha <= :fecha_fin)
            ORDER BY al.fecha DESC, al.hora_entrada DESC
        """)
        
        results = session.execute(query, {
            'equipo_id': equipo_id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }).fetchall()
        
        # Crear DataFrame
        df = pd.DataFrame(results, columns=[
            'Fecha', 'Hora Entrada', 'Código', 'Nombre', 
            'Equipo', 'Método', 'Estado'
        ])
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Asistencias')
        output.seek(0)
        
        session.close()
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'asistencias_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        print(f"❌ Error exportando Excel: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/reportes/export/pdf', methods=['POST'])
@token_required
def export_pdf():
    """Exportar asistencias a PDF"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from io import BytesIO
        from flask import send_file
        
        data = request.json
        equipo_id = data.get('equipo_id')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        session = get_db_session()
        
        query = text("""
            SELECT 
                al.fecha,
                al.hora_entrada,
                u.codigo_usuario,
                u.nombre_completo,
                e.nombre_equipo,
                al.metodo_entrada,
                al.estado
            FROM asistencia_log al
            JOIN membresias m ON al.membresia_id = m.id
            JOIN usuarios u ON m.usuario_id = u.id
            JOIN equipos e ON m.equipo_id = e.id
            WHERE (:equipo_id IS NULL OR m.equipo_id = :equipo_id)
            AND (:fecha_inicio IS NULL OR al.fecha >= :fecha_inicio)
            AND (:fecha_fin IS NULL OR al.fecha <= :fecha_fin)
            ORDER BY al.fecha DESC, al.hora_entrada DESC
            LIMIT 500
        """)
        
        results = session.execute(query, {
            'equipo_id': equipo_id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }).fetchall()
        
        # Crear PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Título
        elements.append(Paragraph("Reporte de Asistencias - CLASS VISION", title_style))
        elements.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Datos de la tabla
        table_data = [['Fecha', 'Hora', 'Código', 'Nombre', 'Método', 'Estado']]
        for r in results:
            table_data.append([
                r[0].strftime('%d/%m/%Y') if r[0] else '',
                str(r[1])[:5] if r[1] else '',
                r[2],
                r[3][:25],  # Truncar nombre
                r[5],
                r[6]
            ])
        
        # Crear tabla
        table = Table(table_data, colWidths=[1*inch, 0.8*inch, 1*inch, 2*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        session.close()
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'asistencias_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        print(f"❌ Error exportando PDF: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# GESTIÓN DE MIEMBROS
# =====================================================

@api_bp.route('/equipos/<int:equipo_id>/miembros/<int:membresia_id>', methods=['DELETE'])
@token_required
def remove_member(equipo_id, membresia_id):
    """Remover miembro del equipo"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        
        # Verificar que el usuario es líder
        lider_check = text("""
            SELECT rol FROM membresias
            WHERE equipo_id = :equipo_id AND usuario_id = :user_id AND estado = 'activo'
        """)
        lider = session.execute(lider_check, {
            'equipo_id': equipo_id,
            'user_id': user_id
        }).fetchone()
        
        if not lider or lider[0] not in ('lider', 'co-lider'):
            session.close()
            return jsonify({'success': False, 'error': 'Solo líderes pueden remover miembros'}), 403
        
        # No permitir que el líder se remueva a sí mismo
        member_check = text("""
            SELECT usuario_id, rol FROM membresias
            WHERE id = :membresia_id AND equipo_id = :equipo_id
        """)
        member = session.execute(member_check, {
            'membresia_id': membresia_id,
            'equipo_id': equipo_id
        }).fetchone()
        
        if not member:
            session.close()
            return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404
        
        if member[0] == user_id and member[1] == 'lider':
            session.close()
            return jsonify({'success': False, 'error': 'El líder no puede removerse a sí mismo'}), 400
        
        # Marcar membresía como inactiva
        update_query = text("""
            UPDATE membresias
            SET estado = 'inactivo', fecha_salida = NOW()
            WHERE id = :membresia_id AND equipo_id = :equipo_id
        """)
        session.execute(update_query, {
            'membresia_id': membresia_id,
            'equipo_id': equipo_id
        })
        
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Miembro removido exitosamente'}), 200
        
    except Exception as e:
        print(f"❌ Error removiendo miembro: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipos/<int:equipo_id>/miembros/<int:membresia_id>/rol', methods=['PUT'])
@token_required
def change_member_role(equipo_id, membresia_id):
    """Cambiar rol de un miembro (promover/degradar)"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        data = request.json
        nuevo_rol = data.get('rol')
        
        if nuevo_rol not in ('lider', 'co-lider', 'miembro'):
            return jsonify({'success': False, 'error': 'Rol inválido'}), 400
        
        # Verificar que el usuario es líder
        lider_check = text("""
            SELECT rol FROM membresias
            WHERE equipo_id = :equipo_id AND usuario_id = :user_id AND estado = 'activo'
        """)
        lider = session.execute(lider_check, {
            'equipo_id': equipo_id,
            'user_id': user_id
        }).fetchone()
        
        if not lider or lider[0] != 'lider':
            session.close()
            return jsonify({'success': False, 'error': 'Solo el líder puede cambiar roles'}), 403
        
        # Actualizar rol
        update_query = text("""
            UPDATE membresias
            SET rol = :rol
            WHERE id = :membresia_id AND equipo_id = :equipo_id AND estado = 'activo'
        """)
        result = session.execute(update_query, {
            'rol': nuevo_rol,
            'membresia_id': membresia_id,
            'equipo_id': equipo_id
        })
        
        if result.rowcount == 0:
            session.close()
            return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404
        
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': f'Rol actualizado a {nuevo_rol}'}), 200
        
    except Exception as e:
        print(f"❌ Error cambiando rol: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# GESTIÓN DE EQUIPOS
# =====================================================

@api_bp.route('/equipos/<int:equipo_id>/editar', methods=['PUT'])
@token_required
def edit_team(equipo_id):
    """Editar información del equipo"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        data = request.json
        
        # Verificar que el usuario es líder
        lider_check = text("""
            SELECT rol FROM membresias
            WHERE equipo_id = :equipo_id AND usuario_id = :user_id AND estado = 'activo'
        """)
        lider = session.execute(lider_check, {
            'equipo_id': equipo_id,
            'user_id': user_id
        }).fetchone()
        
        if not lider or lider[0] not in ('lider', 'co-lider'):
            session.close()
            return jsonify({'success': False, 'error': 'Solo líderes pueden editar el equipo'}), 403
        
        # Actualizar equipo
        updates = []
        params = {'equipo_id': equipo_id}
        
        if 'nombre_equipo' in data:
            updates.append("nombre_equipo = :nombre_equipo")
            params['nombre_equipo'] = data['nombre_equipo']
        
        if 'descripcion' in data:
            updates.append("descripcion = :descripcion")
            params['descripcion'] = data['descripcion']
        
        if not updates:
            session.close()
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400
        
        update_query = text(f"""
            UPDATE equipos
            SET {', '.join(updates)}
            WHERE id = :equipo_id
        """)
        
        session.execute(update_query, params)
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Equipo actualizado exitosamente'}), 200
        
    except Exception as e:
        print(f"❌ Error editando equipo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# QR PARA DISPOSITIVO MÓVIL
# =====================================================

@api_bp.route('/dispositivos/vincular', methods=['POST'])
@token_required
def vincular_dispositivo():
    """Generar código QR para vincular dispositivo móvil como controlador"""
    try:
        import secrets
        import qrcode
        from io import BytesIO
        import base64
        
        session = get_db_session()
        user_id = request.current_user['id']
        data = request.json
        equipo_id = data.get('equipo_id')
        
        # Generar código único
        codigo_vinculacion = f"CTRL-{secrets.token_urlsafe(16)}"
        
        # Guardar en BD
        insert_query = text("""
            INSERT INTO codigos_temporales (
                codigo, tipo, equipo_id, expira_en, valido_hasta,
                usado, metadata, generado_por
            ) VALUES (
                :codigo, 'VINCULACION_DISPOSITIVO', :equipo_id,
                NOW() + INTERVAL '15 minutes',
                NOW() + INTERVAL '15 minutes',
                false, '{}', :generado_por
            )
            RETURNING id
        """)
        
        result = session.execute(insert_query, {
            'codigo': codigo_vinculacion,
            'equipo_id': equipo_id,
            'generado_por': user_id
        })
        
        codigo_id = result.scalar()
        session.commit()
        
        # Generar QR con IP local para acceso desde móvil
        local_ip = get_local_ip()
        qr_data = f"http://{local_ip}:5001/vincular-dispositivo?codigo={codigo_vinculacion}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        session.close()
        
        return jsonify({
            'success': True,
            'codigo': codigo_vinculacion,
            'qr_base64': f'data:image/png;base64,{qr_base64}',
            'expira_en': 15  # minutos
        }), 200
        
    except Exception as e:
        print(f"❌ Error generando QR: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/dispositivos/verificar/<codigo>', methods=['GET'])
def verificar_vinculacion(codigo):
    """Verificar código de vinculación"""
    try:
        session = get_db_session()
        
        query = text("""
            SELECT ct.id, ct.equipo_id, ct.usado, ct.expira_en > NOW() as valido,
                   e.nombre_equipo
            FROM codigos_temporales ct
            JOIN equipos e ON e.id = ct.equipo_id
            WHERE ct.codigo = :codigo AND ct.tipo = 'VINCULACION_DISPOSITIVO'
        """)
        
        result = session.execute(query, {'codigo': codigo}).fetchone()
        
        if not result:
            session.close()
            return jsonify({'success': False, 'error': 'Código no encontrado'}), 404
        
        if result[2]:  # usado
            session.close()
            return jsonify({'success': False, 'error': 'Código ya utilizado'}), 400
        
        if not result[3]:  # no valido
            session.close()
            return jsonify({'success': False, 'error': 'Código expirado'}), 400
        
        # Marcar como usado
        update_query = text("""
            UPDATE codigos_temporales
            SET usado = true, usado_en = NOW()
            WHERE codigo = :codigo
        """)
        session.execute(update_query, {'codigo': codigo})
        session.commit()
        session.close()
        
        return jsonify({
            'success': True,
            'equipo_id': result[1],
            'equipo_nombre': result[4],
            'message': 'Dispositivo vinculado exitosamente'
        }), 200
        
    except Exception as e:
        print(f"❌ Error verificando vinculación: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipos/<int:equipo_id>/stats', methods=['GET'])
@token_required
def get_team_stats(equipo_id):
    """Obtener estadísticas en tiempo real del equipo"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        
        # Verificar membresía
        check_query = text("""
            SELECT id FROM membresias
            WHERE usuario_id = :user_id AND equipo_id = :equipo_id AND estado = 'activo'
        """)
        if not session.execute(check_query, {'user_id': user_id, 'equipo_id': equipo_id}).fetchone():
            session.close()
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
        
        # Asistencias hoy
        asistencias_hoy_query = text("""
            SELECT COUNT(DISTINCT al.membresia_id)
            FROM asistencia_log al
            JOIN membresias m ON al.membresia_id = m.id
            WHERE m.equipo_id = :equipo_id 
            AND al.fecha = CURRENT_DATE
            AND al.estado = 'presente'
        """)
        asistencias_hoy = session.execute(asistencias_hoy_query, {'equipo_id': equipo_id}).scalar() or 0
        
        # Total miembros activos
        total_miembros_query = text("""
            SELECT COUNT(*) FROM membresias
            WHERE equipo_id = :equipo_id AND estado = 'activo'
        """)
        total_miembros = session.execute(total_miembros_query, {'equipo_id': equipo_id}).scalar() or 0
        
        # Promedio de asistencia
        promedio_query = text("""
            SELECT AVG(porcentaje_asistencia) FROM membresias
            WHERE equipo_id = :equipo_id AND estado = 'activo'
        """)
        promedio = session.execute(promedio_query, {'equipo_id': equipo_id}).scalar() or 0
        
        # Asistencias últimos 7 días
        ultimos_7_dias_query = text("""
            SELECT DATE(al.fecha) as fecha, COUNT(DISTINCT al.membresia_id) as total
            FROM asistencia_log al
            JOIN membresias m ON al.membresia_id = m.id
            WHERE m.equipo_id = :equipo_id 
            AND al.fecha >= CURRENT_DATE - INTERVAL '7 days'
            AND al.estado = 'presente'
            GROUP BY DATE(al.fecha)
            ORDER BY fecha DESC
        """)
        ultimos_7_dias = session.execute(ultimos_7_dias_query, {'equipo_id': equipo_id}).fetchall()
        
        session.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'asistencias_hoy': asistencias_hoy,
                'total_miembros': total_miembros,
                'promedio_asistencia': round(float(promedio), 1) if promedio else 0,
                'porcentaje_hoy': round((asistencias_hoy / total_miembros * 100), 1) if total_miembros > 0 else 0,
                'ultimos_7_dias': [{
                    'fecha': str(d[0]),
                    'total': d[1]
                } for d in ultimos_7_dias]
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipos/<int:equipo_id>/miembros/by-codigo/<codigo_usuario>', methods=['DELETE'])
@token_required
def remove_member_by_code(equipo_id, codigo_usuario):
    """Remover miembro del equipo por código de usuario"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        
        # Verificar que el usuario es líder
        lider_check = text("""
            SELECT rol FROM membresias
            WHERE equipo_id = :equipo_id AND usuario_id = :user_id AND estado = 'activo'
        """)
        lider = session.execute(lider_check, {
            'equipo_id': equipo_id,
            'user_id': user_id
        }).fetchone()
        
        if not lider or lider[0] not in ('lider', 'co-lider'):
            session.close()
            return jsonify({'success': False, 'error': 'Solo líderes pueden remover miembros'}), 403
        
        # Obtener membresía por código
        member_query = text("""
            SELECT m.id, m.usuario_id, m.rol
            FROM membresias m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.equipo_id = :equipo_id 
            AND u.codigo_usuario = :codigo_usuario 
            AND m.estado = 'activo'
        """)
        member = session.execute(member_query, {
            'equipo_id': equipo_id,
            'codigo_usuario': codigo_usuario
        }).fetchone()
        
        if not member:
            session.close()
            return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404
        
        if member[1] == user_id and member[2] == 'lider':
            session.close()
            return jsonify({'success': False, 'error': 'El líder no puede removerse a sí mismo'}), 400
        
        # Marcar como inactivo
        update_query = text("""
            UPDATE membresias
            SET estado = 'inactivo', fecha_salida = NOW()
            WHERE id = :membresia_id
        """)
        session.execute(update_query, {'membresia_id': member[0]})
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Miembro removido exitosamente'}), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipos/<int:equipo_id>/miembros/by-codigo/<codigo_usuario>/rol', methods=['PUT'])
@token_required
def change_member_role_by_code(equipo_id, codigo_usuario):
    """Cambiar rol de un miembro por código de usuario"""
    try:
        session = get_db_session()
        user_id = request.current_user['id']
        data = request.json
        nuevo_rol = data.get('rol')
        
        if nuevo_rol not in ('lider', 'co-lider', 'miembro'):
            return jsonify({'success': False, 'error': 'Rol inválido'}), 400
        
        # Verificar que es líder
        lider_check = text("""
            SELECT rol FROM membresias
            WHERE equipo_id = :equipo_id AND usuario_id = :user_id AND estado = 'activo'
        """)
        lider = session.execute(lider_check, {
            'equipo_id': equipo_id,
            'user_id': user_id
        }).fetchone()
        
        if not lider or lider[0] != 'lider':
            session.close()
            return jsonify({'success': False, 'error': 'Solo el líder puede cambiar roles'}), 403
        
        # Obtener membresía
        member_query = text("""
            SELECT m.id FROM membresias m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.equipo_id = :equipo_id 
            AND u.codigo_usuario = :codigo_usuario 
            AND m.estado = 'activo'
        """)
        member = session.execute(member_query, {
            'equipo_id': equipo_id,
            'codigo_usuario': codigo_usuario
        }).fetchone()
        
        if not member:
            session.close()
            return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404
        
        # Actualizar rol
        update_query = text("""
            UPDATE membresias
            SET rol = :nuevo_rol
            WHERE id = :membresia_id
        """)
        session.execute(update_query, {
            'membresia_id': member[0],
            'nuevo_rol': nuevo_rol
        })
        
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': f'Rol cambiado a {nuevo_rol} exitosamente'}), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# CONFIGURACIÓN DEL SISTEMA
# =====================================================

@api_bp.route('/config/reconocimiento', methods=['GET'])
@token_required
def get_recognition_config():
    """Obtener configuración de reconocimiento facial"""
    try:
        config_path = Path('config/recognition_config.json')
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return jsonify({
                'success': True,
                'config': config
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Archivo de configuración no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/config/reconocimiento/umbral', methods=['PUT'])
@token_required
def update_recognition_threshold():
    """Actualizar umbral de confianza del reconocimiento facial"""
    try:
        data = request.get_json()
        nuevo_umbral = data.get('umbral_confianza')
        
        if not nuevo_umbral or not isinstance(nuevo_umbral, (int, float)):
            return jsonify({
                'success': False,
                'error': 'Umbral inválido'
            }), 400
        
        if nuevo_umbral < 30 or nuevo_umbral > 100:
            return jsonify({
                'success': False,
                'error': 'El umbral debe estar entre 30 y 100'
            }), 400
        
        config_path = Path('config/recognition_config.json')
        
        # Leer configuración actual
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {
                'reconocimiento_facial': {},
                'sistema': {
                    'version': '1.0.0',
                    'nombre': 'CLASS VISION'
                }
            }
        
        # Actualizar umbral
        config['reconocimiento_facial']['umbral_confianza'] = int(nuevo_umbral)
        
        # Guardar
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"⚙️ Umbral de confianza actualizado a: {nuevo_umbral}")
        
        return jsonify({
            'success': True,
            'message': 'Configuración actualizada correctamente',
            'nuevo_umbral': int(nuevo_umbral)
        }), 200
        
    except Exception as e:
        print(f"❌ Error actualizando configuración: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =====================================================
# EXPORT
# =====================================================

__all__ = ['api_bp']
