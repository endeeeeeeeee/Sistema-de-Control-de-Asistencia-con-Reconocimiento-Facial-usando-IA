"""
Auth Manager para el nuevo sistema flexible
Gestiona autenticación de usuarios unificados
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Configuración de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=3600,   # Reciclar conexiones cada hora
    connect_args={
        "connect_timeout": 5,  # Timeout de conexión de 5 segundos
        "options": "-c statement_timeout=10000"  # Timeout de consultas de 10 segundos
    }
)
SessionLocal = sessionmaker(bind=engine)

class AuthManager:
    def __init__(self):
        self._session = None
    
    @property
    def session(self):
        """Lazy initialization de la sesión"""
        if self._session is None:
            try:
                self._session = SessionLocal()
            except Exception as e:
                print(f"⚠️ Error al crear sesión de base de datos: {e}")
                raise
        return self._session
    
    def hash_password(self, password):
        """Hash de contraseña con SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_user_code(self):
        """Generar código único de usuario"""
        query = text("SELECT generar_codigo_usuario()")
        result = self.session.execute(query)
        return result.scalar()
    
    def register(self, nombre_completo, email, password, telefono=None, ci=None, fecha_nacimiento=None, foto_face_vector=None):
        """Registrar nuevo usuario"""
        try:
            # Verificar si el email ya existe
            check_query = text("SELECT id FROM usuarios WHERE LOWER(email) = LOWER(:email)")
            existing = self.session.execute(check_query, {'email': email}).fetchone()
            
            if existing:
                return {'success': False, 'error': 'El email ya está registrado'}
            
            # Generar código de usuario
            codigo_usuario = self.generate_user_code()
            
            # Hash de contraseña
            password_hash = self.hash_password(password)
            
            # Insertar usuario
            insert_query = text("""
                INSERT INTO usuarios (
                    codigo_usuario, nombre_completo, email, password_hash, 
                    telefono, ci, fecha_nacimiento, foto_face_vector, activo
                ) VALUES (
                    :codigo, :nombre, :email, :password, 
                    :telefono, :ci, :fecha_nac, :foto, TRUE
                )
                RETURNING id, codigo_usuario
            """)
            
            result = self.session.execute(insert_query, {
                'codigo': codigo_usuario,
                'nombre': nombre_completo,
                'email': email,
                'password': password_hash,
                'telefono': telefono,
                'ci': ci,
                'fecha_nac': fecha_nacimiento,
                'foto': foto_face_vector
            })
            
            self.session.commit()
            user = result.fetchone()
            user_id = user[0]
            codigo_usuario_final = user[1]
            
            print(f"✅ Usuario registrado: {codigo_usuario_final} - {nombre_completo}")
            
            # Generar token automáticamente después del registro
            token = secrets.token_urlsafe(32)
            expira_en = datetime.now() + timedelta(hours=8)
            
            token_query = text("""
                INSERT INTO sesiones_activas (usuario_id, token, fecha_expiracion)
                VALUES (:user_id, :token, :fecha_expiracion)
                RETURNING id
            """)
            
            self.session.execute(token_query, {
                'user_id': user_id,
                'token': token,
                'fecha_expiracion': expira_en
            })
            
            self.session.commit()
            
            return {
                'success': True,
                'user_id': user_id,
                'codigo_usuario': codigo_usuario_final,
                'token': token,
                'expira_en': expira_en.isoformat(),
                'message': 'Usuario registrado exitosamente'
            }
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error en registro: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def login(self, username, password):
        """Login de usuario - acepta email o codigo_usuario"""
        try:
            password_hash = self.hash_password(password)
            
            query = text("""
                SELECT id, codigo_usuario, nombre_completo, email, activo
                FROM usuarios
                WHERE (LOWER(email) = LOWER(:username) OR LOWER(codigo_usuario) = LOWER(:username)) 
                AND password_hash = :password_hash
            """)
            
            user = self.session.execute(query, {
                'username': username,
                'password_hash': password_hash
            }).fetchone()
            
            if not user:
                print(f"❌ Usuario no encontrado o contraseña incorrecta: {username}")
                return None, None
            
            if not user[4]:  # activo
                print(f"❌ Usuario inactivo: {username}")
                return None, None
            
            # Generar token
            token = secrets.token_urlsafe(32)
            expiracion = datetime.now() + timedelta(hours=8)
            
            # Crear sesión
            session_query = text("""
                INSERT INTO sesiones_activas (usuario_id, token, fecha_expiracion, activa)
                VALUES (:user_id, :token, :expiracion, TRUE)
                RETURNING id
            """)
            
            self.session.execute(session_query, {
                'user_id': user[0],
                'token': token,
                'expiracion': expiracion
            })
            
            # Actualizar última conexión
            update_query = text("""
                UPDATE usuarios SET ultima_conexion = CURRENT_TIMESTAMP
                WHERE id = :user_id
            """)
            self.session.execute(update_query, {'user_id': user[0]})
            
            self.session.commit()
            
            print(f"✅ Login exitoso: {user[1]} - {user[2]}")
            
            user_dict = {
                'id': user[0],
                'codigo_usuario': user[1],
                'nombre_completo': user[2],
                'email': user[3]
            }
            
            return user_dict, token
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error en login: {str(e)}")
            return None, None
    
    def validate_token(self, token):
        """Validar token de sesión"""
        try:
            query = text("""
                SELECT s.usuario_id, u.codigo_usuario, u.nombre_completo, u.email
                FROM sesiones_activas s
                JOIN usuarios u ON s.usuario_id = u.id
                WHERE s.token = :token 
                AND s.activa = TRUE 
                AND s.fecha_expiracion > CURRENT_TIMESTAMP
            """)
            
            result = self.session.execute(query, {'token': token}).fetchone()
            
            if result:
                return {
                    'valid': True,
                    'user': {
                        'id': result[0],
                        'codigo_usuario': result[1],
                        'nombre_completo': result[2],
                        'email': result[3]
                    }
                }
            return {'valid': False}
            
        except Exception as e:
            print(f"❌ Error validando token: {str(e)}")
            return {'valid': False}
    
    def logout(self, token):
        """Cerrar sesión"""
        try:
            query = text("""
                UPDATE sesiones_activas 
                SET activa = FALSE 
                WHERE token = :token
            """)
            self.session.execute(query, {'token': token})
            self.session.commit()
            return {'success': True}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_user_info(self, user_id):
        """Obtener información del usuario"""
        try:
            query = text("""
                SELECT 
                    u.id, u.codigo_usuario, u.nombre_completo, u.email, 
                    u.telefono, u.fecha_registro, u.puntos_totales, u.nivel,
                    u.foto_face_vector,
                    (SELECT COUNT(*) FROM membresias WHERE usuario_id = u.id AND rol = 'lider') as equipos_creados,
                    (SELECT COUNT(*) FROM membresias WHERE usuario_id = u.id AND estado = 'activo') as equipos_totales
                FROM usuarios u
                WHERE u.id = :user_id
            """)
            
            user = self.session.execute(query, {'user_id': user_id}).fetchone()
            
            if user:
                return {
                    'success': True,
                    'user': {
                        'id': user[0],
                        'codigo_usuario': user[1],
                        'nombre_completo': user[2],
                        'email': user[3],
                        'telefono': user[4],
                        'fecha_registro': user[5].isoformat() if user[5] else None,
                        'puntos_totales': user[6],
                        'nivel': user[7],
                        'foto_face_vector': user[8],
                        'equipos_creados': user[9],
                        'equipos_totales': user[10]
                    }
                }
            return {'success': False, 'error': 'Usuario no encontrado'}
            
        except Exception as e:
            print(f"❌ Error obteniendo info: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def __del__(self):
        """Cerrar sesión de base de datos"""
        if hasattr(self, 'session'):
            self.session.close()
