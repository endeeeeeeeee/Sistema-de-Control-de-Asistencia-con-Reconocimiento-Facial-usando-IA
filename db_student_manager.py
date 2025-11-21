"""
Gestor de Estudiantes con PostgreSQL
Universidad Nur - CLASS VISION
Manejo de estudiantes, materias e inscripciones con SQLAlchemy
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from database_models import (
    DatabaseManager, Estudiante, Materia, Inscripcion, PersonalAdmin
)

load_dotenv()

class DBStudentManager:
    def __init__(self):
        self.db = DatabaseManager(os.getenv('DATABASE_URL'))
    
    def add_student_to_subject(self, username, subject_name, enrollment, name):
        """Agrega un estudiante a una materia específica del docente"""
        session = self.db.get_session()
        
        try:
            # Buscar docente
            docente = session.query(PersonalAdmin).filter_by(username=username).first()
            if not docente:
                return {"success": False, "error": "Docente no encontrado"}
            
            # Buscar o crear materia
            materia = session.query(Materia).filter_by(
                nombre=subject_name,
                id_docente=docente.id
            ).first()
            
            if not materia:
                materia = Materia(
                    nombre=subject_name,
                    codigo=subject_name.upper().replace(' ', '_')[:20],
                    id_docente=docente.id,
                    activo=True
                )
                session.add(materia)
                session.flush()
            
            # Buscar o crear estudiante
            estudiante = session.query(Estudiante).filter_by(
                codigo_estudiante=enrollment
            ).first()
            
            if not estudiante:
                estudiante = Estudiante(
                    codigo_estudiante=enrollment,
                    nombre_completo=name,
                    fecha_nacimiento=datetime(2000, 1, 1).date(),
                    activo=True,
                    puntos_acumulados=0,
                    nivel=1
                )
                session.add(estudiante)
                session.flush()
            
            # Verificar si ya está inscrito
            inscripcion_existente = session.query(Inscripcion).filter_by(
                id_estudiante=estudiante.id,
                id_materia=materia.id
            ).first()
            
            if inscripcion_existente:
                return {"success": False, "error": "Estudiante ya registrado en esta materia"}
            
            # Crear inscripción
            inscripcion = Inscripcion(
                id_estudiante=estudiante.id,
                id_materia=materia.id,
                estado='ACTIVO',
                puntos_acumulados=0,
                total_asistencias=0,
                total_faltas=0,
                total_tardanzas=0,
                porcentaje_asistencia=100.0
            )
            session.add(inscripcion)
            session.commit()
            
            return {"success": True, "message": "Estudiante agregado exitosamente"}
            
        except Exception as e:
            session.rollback()
            print(f"Error agregando estudiante: {e}")
            return {"success": False, "error": str(e)}
        finally:
            session.close()
    
    def remove_student_from_subject(self, username, subject_name, enrollment):
        """Elimina un estudiante de una materia"""
        session = self.db.get_session()
        
        try:
            # Buscar docente
            docente = session.query(PersonalAdmin).filter_by(username=username).first()
            if not docente:
                return {"success": False, "error": "Docente no encontrado"}
            
            # Buscar materia
            materia = session.query(Materia).filter_by(
                nombre=subject_name,
                id_docente=docente.id
            ).first()
            
            if not materia:
                return {"success": False, "error": "Materia no encontrada"}
            
            # Buscar estudiante
            estudiante = session.query(Estudiante).filter_by(
                codigo_estudiante=enrollment
            ).first()
            
            if not estudiante:
                return {"success": False, "error": "Estudiante no encontrado"}
            
            # Buscar inscripción
            inscripcion = session.query(Inscripcion).filter_by(
                id_estudiante=estudiante.id,
                id_materia=materia.id
            ).first()
            
            if inscripcion:
                # Marcar como inactivo en lugar de eliminar
                inscripcion.estado = 'INACTIVO'
                session.commit()
                return {"success": True, "message": "Estudiante eliminado"}
            
            return {"success": False, "error": "Estudiante no está inscrito en esta materia"}
            
        except Exception as e:
            session.rollback()
            print(f"Error eliminando estudiante: {e}")
            return {"success": False, "error": str(e)}
        finally:
            session.close()
    
    def get_students_by_subject(self, username, subject_name):
        """Obtiene todos los estudiantes de una materia específica"""
        session = self.db.get_session()
        
        try:
            # Buscar docente
            docente = session.query(PersonalAdmin).filter_by(username=username).first()
            if not docente:
                return []
            
            # Buscar materia
            materia = session.query(Materia).filter_by(
                nombre=subject_name,
                id_docente=docente.id
            ).first()
            
            if not materia:
                return []
            
            # Obtener inscripciones activas
            inscripciones = session.query(Inscripcion).filter_by(
                id_materia=materia.id,
                estado='ACTIVO'
            ).all()
            
            students = []
            for inscripcion in inscripciones:
                estudiante = inscripcion.estudiante
                students.append({
                    "enrollment": estudiante.codigo_estudiante,
                    "name": estudiante.nombre_completo,
                    "id": estudiante.id
                })
            
            return students
            
        except Exception as e:
            print(f"Error obteniendo estudiantes: {e}")
            return []
        finally:
            session.close()
    
    def get_all_students_by_teacher(self, username):
        """Obtiene todos los estudiantes de todas las materias de un docente"""
        session = self.db.get_session()
        
        try:
            # Buscar docente
            docente = session.query(PersonalAdmin).filter_by(username=username).first()
            if not docente:
                return {}
            
            result = {}
            
            # Obtener todas las materias del docente
            materias = session.query(Materia).filter_by(id_docente=docente.id).all()
            
            for materia in materias:
                inscripciones = session.query(Inscripcion).filter_by(
                    id_materia=materia.id,
                    estado='ACTIVO'
                ).all()
                
                students = []
                for inscripcion in inscripciones:
                    estudiante = inscripcion.estudiante
                    students.append({
                        "enrollment": estudiante.codigo_estudiante,
                        "name": estudiante.nombre_completo,
                        "id": estudiante.id
                    })
                
                result[materia.nombre] = students
            
            return result
            
        except Exception as e:
            print(f"Error obteniendo todos los estudiantes: {e}")
            return {}
        finally:
            session.close()
    
    def get_student_count(self, username, subject_name=None):
        """Cuenta estudiantes (total o por materia)"""
        session = self.db.get_session()
        
        try:
            # Buscar docente
            docente = session.query(PersonalAdmin).filter_by(username=username).first()
            if not docente:
                return 0
            
            if subject_name:
                # Contar por materia específica
                materia = session.query(Materia).filter_by(
                    nombre=subject_name,
                    id_docente=docente.id
                ).first()
                
                if not materia:
                    return 0
                
                count = session.query(Inscripcion).filter_by(
                    id_materia=materia.id,
                    estado='ACTIVO'
                ).count()
                
                return count
            else:
                # Contar todos los estudiantes únicos del docente
                materias_ids = [m.id for m in docente.materias]
                
                if not materias_ids:
                    return 0
                
                # Contar estudiantes únicos
                estudiantes_ids = set()
                inscripciones = session.query(Inscripcion).filter(
                    Inscripcion.id_materia.in_(materias_ids),
                    Inscripcion.estado == 'ACTIVO'
                ).all()
                
                for inscripcion in inscripciones:
                    estudiantes_ids.add(inscripcion.id_estudiante)
                
                return len(estudiantes_ids)
            
        except Exception as e:
            print(f"Error contando estudiantes: {e}")
            return 0
        finally:
            session.close()
    
    def get_all_students(self):
        """Obtiene todos los estudiantes registrados en el sistema"""
        session = self.db.get_session()
        
        try:
            estudiantes = session.query(Estudiante).filter_by(activo=True).all()
            
            students = []
            for estudiante in estudiantes:
                students.append({
                    "Enrollment": estudiante.codigo_estudiante,
                    "Name": estudiante.nombre_completo,
                    "id": estudiante.id
                })
            
            return students
            
        except Exception as e:
            print(f"Error obteniendo todos los estudiantes: {e}")
            return []
        finally:
            session.close()

# Instancia global
_db_student_manager = None

def get_db_student_manager():
    """Obtiene la instancia global del DBStudentManager"""
    global _db_student_manager
    if _db_student_manager is None:
        _db_student_manager = DBStudentManager()
    return _db_student_manager
