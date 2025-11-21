"""
CLASS VISION - SQLAlchemy Models
=================================

Modelos de base de datos usando SQLAlchemy ORM para PostgreSQL.
Mapeo directo del schema SQL a clases Python.
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, DateTime, \
    TIMESTAMP, Text, DECIMAL, ARRAY, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import BYTEA, INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import UserDefinedType
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import os

Base = declarative_base()

# Tipo personalizado para POINT de PostgreSQL
class POINT(UserDefinedType):
    def get_col_spec(self):
        return "POINT"

# ============================================================================
# MODELOS
# ============================================================================

class SysConfig(Base):
    __tablename__ = 'sys_config'
    
    id = Column(Integer, primary_key=True)
    modo_operacion = Column(String(20), nullable=False)
    nombre_institucion = Column(String(200), nullable=False)
    reglas_json = Column(JSONB, nullable=False, default={})
    color_primario = Column(String(7), default='#023859')
    color_secundario = Column(String(7), default='#54ACBF')
    logo_url = Column(Text)
    horario_inicio = Column(Time, default='07:00:00')
    horario_fin = Column(Time, default='18:00:00')
    creado_en = Column(TIMESTAMP, default=datetime.now)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    actualizado_por = Column(Integer, ForeignKey('personal_admin.id'))
    
    __table_args__ = (
        CheckConstraint("modo_operacion = 'UNIVERSIDAD'"),
    )


class PersonalAdmin(Base):
    __tablename__ = 'personal_admin'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    rol = Column(String(50), nullable=False, index=True)
    email = Column(String(150))
    telefono = Column(String(20))
    foto_face_vector = Column(BYTEA)
    activo = Column(Boolean, default=True)
    ultimo_acceso = Column(TIMESTAMP)
    creado_en = Column(TIMESTAMP, default=datetime.now)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    materias = relationship('Materia', back_populates='docente')
    reportes = relationship('ReporteGenerado', back_populates='generado_por_usuario')
    historial_asistente = relationship('AsistenteHistorial', back_populates='usuario')
    
    __table_args__ = (
        CheckConstraint("rol IN ('DIRECTOR', 'DOCENTE', 'TIA_GUARDERIA', 'SECRETARIA', 'ADMIN_SISTEMA')"),
    )


class Tutor(Base):
    __tablename__ = 'tutores'
    
    id = Column(Integer, primary_key=True)
    ci = Column(String(20), unique=True, nullable=False, index=True)
    nombre_completo = Column(String(200), nullable=False)
    telefono = Column(String(20))
    email = Column(String(150))
    direccion = Column(Text)
    foto_face_vector = Column(BYTEA)
    relacion = Column(String(50))
    qr_code_pickup = Column(String(100), unique=True, index=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(TIMESTAMP, default=datetime.now)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    estudiantes = relationship('Estudiante', back_populates='tutor')
    pickups = relationship('AsistenciaLog', foreign_keys='AsistenciaLog.id_tutor_pickup')
    
    __table_args__ = (
        CheckConstraint("relacion IN ('PADRE', 'MADRE', 'TUTOR', 'ABUELO', 'TIO', 'OTRO')"),
    )


class Estudiante(Base):
    __tablename__ = 'estudiantes'
    
    id = Column(Integer, primary_key=True)
    codigo_estudiante = Column(String(50), unique=True, nullable=False, index=True)
    nombre_completo = Column(String(200), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    ci = Column(String(20))
    genero = Column(String(1))
    telefono = Column(String(20))
    email = Column(String(150))
    direccion = Column(Text)
    foto_face_vector = Column(BYTEA, nullable=False)
    id_tutor = Column(Integer, ForeignKey('tutores.id'), index=True)
    puntos_acumulados = Column(Integer, default=0)
    nivel = Column(Integer, default=1)
    activo = Column(Boolean, default=True, index=True)
    fecha_ingreso = Column(Date, default=func.current_date())
    fecha_egreso = Column(Date)
    creado_en = Column(TIMESTAMP, default=datetime.now)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    tutor = relationship('Tutor', back_populates='estudiantes')
    inscripciones = relationship('Inscripcion', back_populates='estudiante', cascade='all, delete-orphan')
    badges = relationship('EstudianteBadge', back_populates='estudiante', cascade='all, delete-orphan')
    alertas_desercion = relationship('AlertaDesercion', back_populates='estudiante', cascade='all, delete-orphan')
    ranking = relationship('RankingMensual', back_populates='estudiante', cascade='all, delete-orphan')
    justificaciones = relationship('Justificacion', back_populates='estudiante', cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint("genero IN ('M', 'F', 'O')"),
    )


class Materia(Base):
    __tablename__ = 'materias'
    
    id = Column(Integer, primary_key=True)
    codigo_materia = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    nivel = Column(String(50), index=True)
    id_docente = Column(Integer, ForeignKey('personal_admin.id'), nullable=False, index=True)
    dia_semana = Column(ARRAY(Integer))
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    requiere_asistencia = Column(Boolean, default=True)
    tolerancia_minutos = Column(Integer, default=10)
    activo = Column(Boolean, default=True)
    periodo_academico = Column(String(50))
    creado_en = Column(TIMESTAMP, default=datetime.now)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    docente = relationship('PersonalAdmin', back_populates='materias')
    inscripciones = relationship('Inscripcion', back_populates='materia', cascade='all, delete-orphan')
    estadisticas = relationship('EstadisticaDiaria', back_populates='materia', cascade='all, delete-orphan')
    codigos_temporales = relationship('CodigoTemporal', back_populates='materia')
    justificaciones = relationship('Justificacion', back_populates='materia')
    
    __table_args__ = (
        CheckConstraint("nivel IN ('MATERNAL', 'KINDER', 'PREKINDER', 'PRIMARIA', 'SECUNDARIA', 'UNIVERSIDAD')"),
    )


class Inscripcion(Base):
    __tablename__ = 'inscripciones'
    
    id = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey('estudiantes.id', ondelete='CASCADE'), nullable=False, index=True)
    id_materia = Column(Integer, ForeignKey('materias.id', ondelete='CASCADE'), nullable=False, index=True)
    puntos_acumulados = Column(Integer, default=0)
    estado = Column(String(20), default='ACTIVO', index=True)
    total_asistencias = Column(Integer, default=0)
    total_faltas = Column(Integer, default=0)
    total_tardanzas = Column(Integer, default=0)
    porcentaje_asistencia = Column(DECIMAL(5, 2), default=100.00)
    fecha_inscripcion = Column(Date, default=func.current_date())
    fecha_retiro = Column(Date)
    creado_en = Column(TIMESTAMP, default=datetime.now)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    estudiante = relationship('Estudiante', back_populates='inscripciones')
    materia = relationship('Materia', back_populates='inscripciones')
    asistencias = relationship('AsistenciaLog', back_populates='inscripcion', cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint("estado IN ('ACTIVO', 'RETIRADO', 'APROBADO', 'REPROBADO')"),
        UniqueConstraint('id_estudiante', 'id_materia'),
    )


class AsistenciaLog(Base):
    __tablename__ = 'asistencia_log'
    
    id = Column(Integer, primary_key=True)
    id_inscripcion = Column(Integer, ForeignKey('inscripciones.id', ondelete='CASCADE'), nullable=False, index=True)
    fecha = Column(Date, nullable=False, default=func.current_date(), index=True)
    hora_entrada = Column(TIMESTAMP, nullable=False, default=datetime.now)
    hora_salida = Column(TIMESTAMP)
    metodo_entrada = Column(String(50), nullable=False, index=True)
    estado = Column(String(20), nullable=False, default='PRESENTE', index=True)
    score_liveness = Column(DECIMAL(5, 2))
    ip_address = Column(INET)
    ubicacion_gps = Column(POINT)
    id_tutor_pickup = Column(Integer, ForeignKey('tutores.id'))
    hora_pickup = Column(TIMESTAMP)
    id_codigo_temporal = Column(Integer, ForeignKey('codigos_temporales.id'))
    creado_en = Column(TIMESTAMP, default=datetime.now)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    inscripcion = relationship('Inscripcion', back_populates='asistencias')
    tutor_pickup = relationship('Tutor', foreign_keys=[id_tutor_pickup], overlaps="pickups")
    codigo_temporal = relationship('CodigoTemporal', foreign_keys=[id_codigo_temporal])
    asistencia_virtual = relationship('AsistenciaVirtual', back_populates='asistencia_log', uselist=False)
    
    __table_args__ = (
        CheckConstraint("metodo_entrada IN ('RECONOCIMIENTO_FACIAL', 'QR_CODE', 'CODIGO_TEMPORAL', 'MANUAL')"),
        CheckConstraint("estado IN ('PRESENTE', 'TARDANZA', 'AUSENTE', 'JUSTIFICADO', 'VIRTUAL')"),
        Index('idx_asistencia_fecha_estado', 'fecha', 'estado'),
    )


class Justificacion(Base):
    __tablename__ = 'justificaciones'
    
    id = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey('estudiantes.id', ondelete='CASCADE'), nullable=False, index=True)
    id_materia = Column(Integer, ForeignKey('materias.id'))
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    motivo = Column(Text, nullable=False)
    tipo = Column(String(50))
    documento_url = Column(Text)
    estado = Column(String(20), default='PENDIENTE', index=True)
    aprobado_por = Column(Integer, ForeignKey('personal_admin.id'))
    fecha_aprobacion = Column(TIMESTAMP)
    comentario_aprobacion = Column(Text)
    creado_en = Column(TIMESTAMP, default=datetime.now)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    estudiante = relationship('Estudiante', back_populates='justificaciones')
    materia = relationship('Materia', back_populates='justificaciones')
    
    __table_args__ = (
        CheckConstraint("tipo IN ('MEDICO', 'FAMILIAR', 'PERSONAL', 'OTRO')"),
        CheckConstraint("estado IN ('PENDIENTE', 'APROBADO', 'RECHAZADO')"),
    )


class Badge(Base):
    __tablename__ = 'badges'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    icono_url = Column(Text)
    condicion_tipo = Column(String(50))
    condicion_valor = Column(Integer)
    puntos_otorga = Column(Integer, default=0)
    rareza = Column(String(20))
    activo = Column(Boolean, default=True)
    creado_en = Column(TIMESTAMP, default=datetime.now)
    
    # Relaciones
    estudiantes = relationship('EstudianteBadge', back_populates='badge')
    
    __table_args__ = (
        CheckConstraint("condicion_tipo IN ('ASISTENCIA_PERFECTA', 'PUNTUALIDAD_EXTREMA', 'RACHA_SEMANAL', 'PARTICIPACION', 'MEJORA_CONTINUA', 'CUSTOM')"),
        CheckConstraint("rareza IN ('COMUN', 'RARO', 'EPICO', 'LEGENDARIO')"),
    )


class EstudianteBadge(Base):
    __tablename__ = 'estudiantes_badges'
    
    id = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey('estudiantes.id', ondelete='CASCADE'), nullable=False, index=True)
    id_badge = Column(Integer, ForeignKey('badges.id', ondelete='CASCADE'), nullable=False, index=True)
    fecha_obtencion = Column(TIMESTAMP, default=datetime.now)
    periodo_academico = Column(String(50))
    metadata_json = Column(JSONB)
    
    # Relaciones
    estudiante = relationship('Estudiante', back_populates='badges')
    badge = relationship('Badge', back_populates='estudiantes')
    
    __table_args__ = (
        UniqueConstraint('id_estudiante', 'id_badge', 'periodo_academico'),
    )


class RankingMensual(Base):
    __tablename__ = 'ranking_mensual'
    
    id = Column(Integer, primary_key=True)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    id_estudiante = Column(Integer, ForeignKey('estudiantes.id', ondelete='CASCADE'), nullable=False)
    total_puntos = Column(Integer, default=0)
    total_asistencias = Column(Integer, default=0)
    porcentaje_puntualidad = Column(DECIMAL(5, 2), default=0.00)
    badges_obtenidos = Column(Integer, default=0)
    posicion = Column(Integer, index=True)
    calculado_en = Column(TIMESTAMP, default=datetime.now)
    
    # Relaciones
    estudiante = relationship('Estudiante', back_populates='ranking')
    
    __table_args__ = (
        CheckConstraint('mes BETWEEN 1 AND 12'),
        UniqueConstraint('anio', 'mes', 'id_estudiante'),
        Index('idx_ranking_periodo', 'anio', 'mes'),
    )


class AlertaDesercion(Base):
    __tablename__ = 'alertas_desercion'
    
    id = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey('estudiantes.id', ondelete='CASCADE'), nullable=False, index=True)
    nivel_riesgo = Column(String(20), nullable=False, index=True)
    probabilidad_desercion = Column(DECIMAL(5, 2), nullable=False)
    factores_json = Column(JSONB, nullable=False)
    estado = Column(String(20), default='NUEVA', index=True)
    acciones_tomadas = Column(ARRAY(Text))
    asignado_a = Column(Integer, ForeignKey('personal_admin.id'))
    fecha_seguimiento = Column(TIMESTAMP)
    detectado_en = Column(TIMESTAMP, default=datetime.now)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    estudiante = relationship('Estudiante', back_populates='alertas_desercion')
    
    __table_args__ = (
        CheckConstraint("nivel_riesgo IN ('BAJO', 'MEDIO', 'ALTO', 'CRITICO')"),
        CheckConstraint("estado IN ('NUEVA', 'EN_SEGUIMIENTO', 'RESUELTA', 'CRITICA')"),
    )


class NotificacionInterna(Base):
    __tablename__ = 'notificaciones_internas'
    
    id = Column(Integer, primary_key=True)
    destinatario_tipo = Column(String(20), nullable=False)
    destinatario_id = Column(Integer, nullable=False)
    tipo = Column(String(50), nullable=False)
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    metadata_json = Column(JSONB)
    leida = Column(Boolean, default=False, index=True)
    fecha_lectura = Column(TIMESTAMP)
    prioridad = Column(String(20), default='NORMAL')
    expira_en = Column(TIMESTAMP)
    creado_en = Column(TIMESTAMP, default=datetime.now, index=True)
    
    __table_args__ = (
        CheckConstraint("destinatario_tipo IN ('ESTUDIANTE', 'TUTOR', 'DOCENTE', 'ADMIN')"),
        CheckConstraint("tipo IN ('ASISTENCIA_CONFIRMADA', 'TARDANZA_REGISTRADA', 'FALTA_REGISTRADA', 'ALERTA_FALTAS_CONSECUTIVAS', 'BADGE_OBTENIDO', 'NUEVO_RANKING', 'JUSTIFICACION_APROBADA', 'JUSTIFICACION_RECHAZADA', 'ALERTA_DESERCION', 'PICKUP_GUARDERIA', 'CODIGO_QR_GENERADO', 'CLASE_VIRTUAL_INICIADA', 'SISTEMA')"),
        CheckConstraint("prioridad IN ('BAJA', 'NORMAL', 'ALTA', 'URGENTE')"),
        Index('idx_notificaciones_destinatario', 'destinatario_tipo', 'destinatario_id'),
        Index('idx_notificaciones_no_leidas', 'destinatario_tipo', 'destinatario_id', 'leida'),
    )


class SesionActiva(Base):
    __tablename__ = 'sesiones_activas'
    
    id = Column(Integer, primary_key=True)
    token = Column(String(100), unique=True, nullable=False, index=True)
    usuario_tipo = Column(String(20), nullable=False)
    usuario_id = Column(Integer, nullable=False)
    ip_address = Column(INET)
    user_agent = Column(Text)
    dispositivo = Column(String(100))
    fecha_inicio = Column(TIMESTAMP, default=datetime.now)
    fecha_expiracion = Column(TIMESTAMP, nullable=False, index=True)
    ultima_actividad = Column(TIMESTAMP, default=datetime.now)
    activa = Column(Boolean, default=True)
    
    __table_args__ = (
        CheckConstraint("usuario_tipo IN ('PERSONAL', 'ESTUDIANTE', 'TUTOR')"),
        Index('idx_sesiones_usuario', 'usuario_tipo', 'usuario_id'),
    )


class CodigoTemporal(Base):
    __tablename__ = 'codigos_temporales'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(100), unique=True, nullable=False, index=True)
    tipo = Column(String(50), nullable=False)
    id_materia = Column(Integer, ForeignKey('materias.id'), index=True)
    fecha_valido = Column(Date, default=func.current_date())
    valido_desde = Column(TIMESTAMP, default=datetime.now)
    valido_hasta = Column(TIMESTAMP, nullable=False, index=True)
    usado = Column(Boolean, default=False)
    fecha_uso = Column(TIMESTAMP)
    usado_por = Column(Integer)
    hash_verificacion = Column(String(255))
    max_usos = Column(Integer, default=1)
    usos_actuales = Column(Integer, default=0)
    generado_por = Column(Integer, ForeignKey('personal_admin.id'), nullable=False)
    creado_en = Column(TIMESTAMP, default=datetime.now)
    
    # Relaciones
    materia = relationship('Materia', back_populates='codigos_temporales')
    asistencias = relationship('AsistenciaLog', back_populates='codigo_temporal')
    asistencias_virtuales = relationship('AsistenciaVirtual', back_populates='codigo_temporal')
    
    __table_args__ = (
        CheckConstraint("tipo IN ('QR_CLASE_VIRTUAL', 'CODIGO_NUMERICO', 'QR_PICKUP_GUARDERIA', 'ENLACE_UNICO')"),
    )


class AsistenciaVirtual(Base):
    __tablename__ = 'asistencia_virtual'
    
    id = Column(Integer, primary_key=True)
    id_asistencia_log = Column(Integer, ForeignKey('asistencia_log.id', ondelete='CASCADE'), nullable=False)
    id_codigo_temporal = Column(Integer, ForeignKey('codigos_temporales.id'), nullable=False)
    plataforma = Column(String(50))
    duracion_minutos = Column(Integer)
    verificacion_intermitente = Column(Boolean, default=False)
    capturas_pantalla = Column(Integer, default=0)
    ip_address = Column(INET)
    user_agent = Column(Text)
    creado_en = Column(TIMESTAMP, default=datetime.now)
    
    # Relaciones
    asistencia_log = relationship('AsistenciaLog', back_populates='asistencia_virtual')
    codigo_temporal = relationship('CodigoTemporal', back_populates='asistencias_virtuales')


class EstadisticaDiaria(Base):
    __tablename__ = 'estadisticas_diarias'
    
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, index=True)
    id_materia = Column(Integer, ForeignKey('materias.id', ondelete='CASCADE'), index=True)
    total_estudiantes = Column(Integer, default=0)
    total_presentes = Column(Integer, default=0)
    total_ausentes = Column(Integer, default=0)
    total_tardanzas = Column(Integer, default=0)
    total_justificados = Column(Integer, default=0)
    total_virtuales = Column(Integer, default=0)
    porcentaje_asistencia = Column(DECIMAL(5, 2), default=0.00)
    porcentaje_puntualidad = Column(DECIMAL(5, 2), default=0.00)
    calculado_en = Column(TIMESTAMP, default=datetime.now)
    
    # Relaciones
    materia = relationship('Materia', back_populates='estadisticas')
    
    __table_args__ = (
        UniqueConstraint('fecha', 'id_materia'),
    )


class ReporteGenerado(Base):
    __tablename__ = 'reportes_generados'
    
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False, index=True)
    nombre_archivo = Column(String(200), nullable=False)
    formato = Column(String(10))
    filtros_json = Column(JSONB)
    ruta_archivo = Column(Text, nullable=False)
    tamano_bytes = Column(Integer)
    generado_por = Column(Integer, ForeignKey('personal_admin.id'), nullable=False, index=True)
    fecha_generacion = Column(TIMESTAMP, default=datetime.now)
    expira_en = Column(TIMESTAMP)
    
    # Relaciones
    generado_por_usuario = relationship('PersonalAdmin', back_populates='reportes')
    
    __table_args__ = (
        CheckConstraint("tipo IN ('ASISTENCIA_DIARIA', 'ASISTENCIA_SEMANAL', 'ASISTENCIA_MENSUAL', 'RANKING_ESTUDIANTES', 'ALERTAS_DESERCION', 'ESTADISTICAS_MATERIA', 'CUSTOM')"),
        CheckConstraint("formato IN ('PDF', 'EXCEL', 'CSV', 'JSON')"),
    )


class AuditLog(Base):
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    usuario_tipo = Column(String(20), nullable=False)
    usuario_id = Column(Integer, nullable=False)
    accion = Column(String(100), nullable=False, index=True)
    entidad = Column(String(50), nullable=False)
    entidad_id = Column(Integer)
    descripcion = Column(Text)
    datos_anteriores = Column(JSONB)
    datos_nuevos = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    timestamp = Column(TIMESTAMP, default=datetime.now, index=True)
    
    __table_args__ = (
        CheckConstraint("usuario_tipo IN ('PERSONAL', 'ESTUDIANTE', 'TUTOR', 'SISTEMA')"),
        Index('idx_audit_usuario', 'usuario_tipo', 'usuario_id'),
        Index('idx_audit_entidad', 'entidad', 'entidad_id'),
    )


class AsistenteHistorial(Base):
    __tablename__ = 'asistente_historial'
    
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('personal_admin.id'), nullable=False, index=True)
    comando_texto = Column(Text, nullable=False)
    comando_tipo = Column(String(50), index=True)
    intencion = Column(String(100))
    entidades_json = Column(JSONB)
    respuesta_texto = Column(Text)
    respuesta_tipo = Column(String(50))
    acciones_ejecutadas = Column(JSONB)
    exito = Column(Boolean, default=True)
    error_mensaje = Column(Text)
    timestamp = Column(TIMESTAMP, default=datetime.now, index=True)
    duracion_ms = Column(Integer)
    
    # Relaciones
    usuario = relationship('PersonalAdmin', back_populates='historial_asistente')
    
    __table_args__ = (
        CheckConstraint("comando_tipo IN ('CONSULTA', 'MODIFICACION', 'GENERACION', 'ANALISIS')"),
        CheckConstraint("respuesta_tipo IN ('TEXTO', 'AUDIO', 'MIXTO')"),
    )


# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

class DatabaseManager:
    """Gestor de conexiones a la base de datos"""
    
    def __init__(self, database_url=None):
        """
        Inicializa el gestor de base de datos
        
        Args:
            database_url: URL de conexión PostgreSQL
                         Por defecto usa variable de entorno DATABASE_URL
        """
        if database_url is None:
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://postgres:postgres@localhost:5501/class_vision'
            )
        
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_all_tables(self):
        """Crea todas las tablas en la base de datos"""
        Base.metadata.create_all(self.engine)
        print("✅ Tablas creadas exitosamente")
    
    def drop_all_tables(self):
        """Elimina todas las tablas (¡CUIDADO!)"""
        Base.metadata.drop_all(self.engine)
        print("⚠️ Todas las tablas eliminadas")
    
    def get_session(self):
        """
        Retorna una nueva sesión de base de datos
        
        Returns:
            Session de SQLAlchemy
        """
        return self.Session()
    
    def close(self):
        """Cierra la conexión"""
        self.engine.dispose()


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Crear gestor de BD
    db_manager = DatabaseManager()
    
    # Crear todas las tablas
    db_manager.create_all_tables()
    
    # Obtener sesión
    session = db_manager.get_session()
    
    try:
        # Ejemplo: Crear configuración inicial
        config = SysConfig(
            modo_operacion='UNIVERSIDAD',
            nombre_institucion='CLASS VISION - Universidad Nur'
        )
        session.add(config)
        
        # Ejemplo: Crear admin
        admin = PersonalAdmin(
            username='admin',
            password_hash='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            full_name='Administrador del Sistema',
            rol='ADMIN_SISTEMA'
        )
        session.add(admin)
        
        session.commit()
        print("✅ Datos iniciales creados")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
    finally:
        session.close()
