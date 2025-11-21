"""
Sistema de Autenticación con PostgreSQL
Universidad Nur - CLASS VISION
Manejo de usuarios y sesiones con SQLAlchemy
"""

import hashlib
import secrets
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database_models import (
    DatabaseManager, PersonalAdmin, SesionActiva, Materia
)

load_dotenv()

class DBAuthManager:
    def __init__(self):
        self.db = DatabaseManager(os.getenv('DATABASE_URL'))
        
    def hash_password(self, password):
        """Hash de contraseña con SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, full_name, role='DOCENTE'):
        """Registra un nuevo docente"""
        session = self.db.get_session()
        
        try:
            # Verificar si el usuario ya existe (case-insensitive)
            from sqlalchemy import func
            existing = session.query(PersonalAdmin).filter(
                func.lower(PersonalAdmin.username) == func.lower(username)
            ).first()
            if existing:
                return None, None
            
            # Crear nuevo usuario
            new_user = PersonalAdmin(
                username=username,
                password_hash=self.hash_password(password),
                full_name=full_name,
                rol=role,
                activo=True
            )
            session.add(new_user)
            session.flush()
            
            # Generar token de sesión
            token = secrets.token_urlsafe(32)
            expiracion = datetime.now() + timedelta(hours=8)
            
            nueva_sesion = SesionActiva(
                usuario_tipo='PERSONAL',
                usuario_id=new_user.id,
                token=token,
                fecha_expiracion=expiracion,
                ip_address=None,
                user_agent=None
            )
            session.add(nueva_sesion)
            session.commit()
            
            user_data = {
                "id": new_user.id,
                "username": username,
                "full_name": full_name,
                "role": role,
                "subjects": []
            }
            
            return user_data, token
            
        except Exception as e:
            session.rollback()
            print(f"Error en registro: {e}")
            return None, None
        finally:
            session.close()
    
    def login(self, username, password):
        """Inicia sesión y genera token"""
        session = self.db.get_session()
        
        try:
            # Buscar usuario (case-insensitive)
            from sqlalchemy import func
            user = session.query(PersonalAdmin).filter(
                func.lower(PersonalAdmin.username) == func.lower(username),
                PersonalAdmin.activo == True
            ).first()
            
            print(f"\n=== AUTH MANAGER LOGIN ===")
            print(f"Username buscado: '{username}'")
            print(f"Usuario encontrado: {user.username if user else 'NO ENCONTRADO'}")
            
            if not user:
                print("❌ Usuario no encontrado o inactivo")
                return None, None
            
            # Verificar contraseña
            password_hash_calculated = self.hash_password(password)
            print(f"Password recibido: '{password}'")
            print(f"Hash calculado: {password_hash_calculated[:50]}...")
            print(f"Hash en BD:     {user.password_hash[:50]}...")
            print(f"¿Coinciden? {user.password_hash == password_hash_calculated}")
            
            if user.password_hash != password_hash_calculated:
                print("❌ Contraseña incorrecta")
                return None, None
            
            # Generar token de sesión
            token = secrets.token_urlsafe(32)
            expiracion = datetime.now() + timedelta(hours=8)
            
            # Limpiar sesiones antiguas del usuario
            session.query(SesionActiva).filter(
                SesionActiva.usuario_tipo == 'PERSONAL',
                SesionActiva.usuario_id == user.id
            ).delete()
            
            # Crear nueva sesión
            nueva_sesion = SesionActiva(
                usuario_tipo='PERSONAL',
                usuario_id=user.id,
                token=token,
                fecha_expiracion=expiracion,
                ip_address=None,
                user_agent=None
            )
            session.add(nueva_sesion)
            session.commit()
            
            # Obtener materias del docente
            materias = [m.nombre for m in user.materias]
            
            user_data = {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.rol,
                "subjects": materias
            }
            
            return user_data, token
            
        except Exception as e:
            session.rollback()
            print(f"Error en login: {e}")
            return None, None
        finally:
            session.close()
    
    def logout(self, token):
        """Cierra sesión"""
        session = self.db.get_session()
        
        try:
            sesion = session.query(SesionActiva).filter_by(token=token).first()
            if sesion:
                session.delete(sesion)
                session.commit()
                return {"success": True}
            return {"success": False, "error": "Token inválido"}
        except Exception as e:
            session.rollback()
            print(f"Error en logout: {e}")
            return {"success": False, "error": str(e)}
        finally:
            session.close()
    
    def validate_token(self, token):
        """Valida un token de sesión y retorna datos del usuario"""
        session = self.db.get_session()
        
        try:
            sesion = session.query(SesionActiva).filter_by(token=token).first()
            
            if not sesion:
                return None
            
            # Verificar expiración
            if datetime.now() > sesion.fecha_expiracion:
                session.delete(sesion)
                session.commit()
                return None
            
            # Obtener datos del usuario (por tipo y ID)
            if sesion.usuario_tipo != 'PERSONAL':
                return None
            
            user = session.query(PersonalAdmin).filter_by(id=sesion.usuario_id).first()
            if user and user.activo:
                materias = [m.nombre for m in user.materias]
                
                return {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.rol,
                    "subjects": materias
                }
            
            return None
            
        except Exception as e:
            print(f"Error validando token: {e}")
            return None
        finally:
            session.close()
    
    def get_user(self, username):
        """Obtiene información de un usuario"""
        session = self.db.get_session()
        
        try:
            user = session.query(PersonalAdmin).filter_by(username=username).first()
            
            if user:
                materias = [m.nombre for m in user.materias]
                
                return {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.rol,
                    "subjects": materias,
                    "is_active": user.activo
                }
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
        finally:
            session.close()
    
    def get_subjects(self, username):
        """Obtiene las materias de un docente"""
        session = self.db.get_session()
        
        try:
            user = session.query(PersonalAdmin).filter_by(username=username).first()
            
            if user:
                return [m.nombre for m in user.materias]
            
            return []
            
        except Exception as e:
            print(f"Error obteniendo materias: {e}")
            return []
        finally:
            session.close()
    
    def add_subject(self, username, subject_name):
        """Agrega una materia al docente (o la asigna si ya existe)"""
        session = self.db.get_session()
        
        try:
            user = session.query(PersonalAdmin).filter_by(username=username).first()
            if not user:
                return False
            
            # Buscar o crear la materia
            materia = session.query(Materia).filter_by(nombre=subject_name).first()
            if not materia:
                materia = Materia(
                    nombre=subject_name,
                    codigo=subject_name.upper().replace(' ', '_')[:20],
                    id_docente=user.id,
                    activo=True
                )
                session.add(materia)
            else:
                # Asignar al docente si no está ya asignada
                if materia.id_docente != user.id:
                    materia.id_docente = user.id
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error agregando materia: {e}")
            return False
        finally:
            session.close()

# Instancia global
_db_auth_manager = None

def get_db_auth_manager():
    """Obtiene la instancia global del DBAuthManager"""
    global _db_auth_manager
    if _db_auth_manager is None:
        _db_auth_manager = DBAuthManager()
    return _db_auth_manager
