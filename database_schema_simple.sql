-- ============================================================================
-- CLASS VISION - SCHEMA SIMPLIFICADO PARA UNIVERSIDADES
-- ============================================================================
-- Solo 12 tablas esenciales para sistema universitario
-- ============================================================================

-- Limpiar esquema existente
DROP TABLE IF EXISTS asistente_historial CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS estadistica_diaria CASCADE;
DROP TABLE IF EXISTS notificacion_interna CASCADE;
DROP TABLE IF EXISTS asistencia_virtual CASCADE;
DROP TABLE IF EXISTS tutores CASCADE;

-- Las demás tablas se mantienen pero se recrean para consistencia

-- ============================================================================
-- 1. CONFIGURACIÓN DEL SISTEMA
-- ============================================================================
CREATE TABLE IF NOT EXISTS sys_config (
    id SERIAL PRIMARY KEY,
    modo_operacion VARCHAR(20) NOT NULL DEFAULT 'UNIVERSIDAD' CHECK (modo_operacion = 'UNIVERSIDAD'),
    nombre_institucion VARCHAR(200) NOT NULL,
    reglas_json JSONB NOT NULL DEFAULT '{}',
    color_primario VARCHAR(7) DEFAULT '#023859',
    color_secundario VARCHAR(7) DEFAULT '#54ACBF',
    logo_url TEXT,
    horario_inicio TIME DEFAULT '07:00:00',
    horario_fin TIME DEFAULT '18:00:00',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por INTEGER
);

-- ============================================================================
-- 2. PERSONAL ADMINISTRATIVO (DOCENTES)
-- ============================================================================
CREATE TABLE IF NOT EXISTS personal_admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20),
    role VARCHAR(20) DEFAULT 'DOCENTE' CHECK (role IN ('ADMIN', 'DOCENTE')),
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_personal_username ON personal_admin(username);
CREATE INDEX idx_personal_activo ON personal_admin(activo);

-- ============================================================================
-- 3. SESIONES ACTIVAS
-- ============================================================================
CREATE TABLE IF NOT EXISTS sesiones_activas (
    id SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES personal_admin(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_sesion_token ON sesiones_activas(token);
CREATE INDEX idx_sesion_expiracion ON sesiones_activas(fecha_expiracion);

-- ============================================================================
-- 4. ESTUDIANTES (AUTO-REGISTRO)
-- ============================================================================
CREATE TABLE IF NOT EXISTS estudiantes (
    id SERIAL PRIMARY KEY,
    codigo_estudiante VARCHAR(50) UNIQUE NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    ci VARCHAR(20) UNIQUE,
    fecha_nacimiento DATE,
    foto_face_vector BYTEA,
    foto_url TEXT,
    puntos_acumulados INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_estudiante_codigo ON estudiantes(codigo_estudiante);
CREATE INDEX idx_estudiante_email ON estudiantes(email);
CREATE INDEX idx_estudiante_activo ON estudiantes(activo);

-- ============================================================================
-- 5. MATERIAS
-- ============================================================================
CREATE TABLE IF NOT EXISTS materias (
    id SERIAL PRIMARY KEY,
    codigo_materia VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    nivel VARCHAR(50),
    id_docente INTEGER NOT NULL REFERENCES personal_admin(id) ON DELETE CASCADE,
    dia_semana VARCHAR(20)[],
    hora_inicio TIME,
    hora_fin TIME,
    tolerancia_minutos INTEGER DEFAULT 15,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_materia_codigo ON materias(codigo_materia);
CREATE INDEX idx_materia_docente ON materias(id_docente);
CREATE INDEX idx_materia_activo ON materias(activo);

-- ============================================================================
-- 6. INSCRIPCIONES (ESTUDIANTE-MATERIA)
-- ============================================================================
CREATE TABLE IF NOT EXISTS inscripciones (
    id SERIAL PRIMARY KEY,
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    id_materia INTEGER NOT NULL REFERENCES materias(id) ON DELETE CASCADE,
    estado VARCHAR(20) DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO', 'RETIRADO')),
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    porcentaje_asistencia DECIMAL(5,2) DEFAULT 100.00,
    total_asistencias INTEGER DEFAULT 0,
    total_faltas INTEGER DEFAULT 0,
    total_tardanzas INTEGER DEFAULT 0,
    UNIQUE(id_estudiante, id_materia)
);

CREATE INDEX idx_inscripcion_estudiante ON inscripciones(id_estudiante);
CREATE INDEX idx_inscripcion_materia ON inscripciones(id_materia);
CREATE INDEX idx_inscripcion_estado ON inscripciones(estado);

-- ============================================================================
-- 7. ASISTENCIA LOG
-- ============================================================================
CREATE TABLE IF NOT EXISTS asistencia_log (
    id SERIAL PRIMARY KEY,
    id_inscripcion INTEGER NOT NULL REFERENCES inscripciones(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    hora_entrada TIME,
    metodo_entrada VARCHAR(30) CHECK (metodo_entrada IN ('FACIAL', 'QR_CODE', 'CODIGO_TEMPORAL', 'MANUAL')),
    estado VARCHAR(20) CHECK (estado IN ('PRESENTE', 'TARDANZA', 'AUSENTE', 'JUSTIFICADO')),
    score_confianza DECIMAL(5,2),
    id_codigo_temporal INTEGER,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_asistencia_fecha ON asistencia_log(fecha, estado);
CREATE INDEX idx_asistencia_inscripcion ON asistencia_log(id_inscripcion);

-- ============================================================================
-- 8. CÓDIGOS TEMPORALES (QR)
-- ============================================================================
CREATE TABLE IF NOT EXISTS codigos_temporales (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    tipo VARCHAR(30) CHECK (tipo IN ('QR_CLASE_VIRTUAL', 'CODIGO_NUMERICO', 'ENLACE_UNICO')),
    id_materia INTEGER REFERENCES materias(id) ON DELETE CASCADE,
    valido_desde TIMESTAMP NOT NULL,
    valido_hasta TIMESTAMP NOT NULL,
    max_usos INTEGER DEFAULT 100,
    usos_actuales INTEGER DEFAULT 0,
    hash_verificacion VARCHAR(255),
    generado_por INTEGER REFERENCES personal_admin(id),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_codigo_hash ON codigos_temporales(hash_verificacion);
CREATE INDEX idx_codigo_valido ON codigos_temporales(valido_hasta, activo);

-- ============================================================================
-- 9. BADGES (GAMIFICACIÓN)
-- ============================================================================
CREATE TABLE IF NOT EXISTS badges (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    icono_emoji VARCHAR(10),
    color_hex VARCHAR(7),
    puntos_requeridos INTEGER DEFAULT 0,
    nivel_requerido INTEGER DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 10. ESTUDIANTE-BADGES
-- ============================================================================
CREATE TABLE IF NOT EXISTS estudiante_badges (
    id SERIAL PRIMARY KEY,
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    id_badge INTEGER NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    fecha_obtencion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_estudiante, id_badge)
);

CREATE INDEX idx_est_badge_estudiante ON estudiante_badges(id_estudiante);

-- ============================================================================
-- 11. RANKING MENSUAL
-- ============================================================================
CREATE TABLE IF NOT EXISTS ranking_mensual (
    id SERIAL PRIMARY KEY,
    mes INTEGER NOT NULL,
    anio INTEGER NOT NULL,
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    id_materia INTEGER REFERENCES materias(id) ON DELETE CASCADE,
    posicion INTEGER NOT NULL,
    puntos_totales INTEGER NOT NULL,
    porcentaje_asistencia DECIMAL(5,2),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mes, anio, id_estudiante, id_materia)
);

CREATE INDEX idx_ranking_periodo ON ranking_mensual(mes, anio);

-- ============================================================================
-- 12. ALERTAS DE DESERCIÓN
-- ============================================================================
CREATE TABLE IF NOT EXISTS alertas_desercion (
    id SERIAL PRIMARY KEY,
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    id_materia INTEGER NOT NULL REFERENCES materias(id) ON DELETE CASCADE,
    nivel_riesgo VARCHAR(10) CHECK (nivel_riesgo IN ('BAJO', 'MEDIO', 'ALTO', 'CRÍTICO')),
    faltas_consecutivas INTEGER,
    mensaje TEXT,
    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atendida BOOLEAN DEFAULT false,
    fecha_atencion TIMESTAMP
);

CREATE INDEX idx_alerta_estudiante ON alertas_desercion(id_estudiante);
CREATE INDEX idx_alerta_materia ON alertas_desercion(id_materia);
CREATE INDEX idx_alerta_atendida ON alertas_desercion(atendida);

-- ============================================================================
-- 13. REPORTES GENERADOS
-- ============================================================================
CREATE TABLE IF NOT EXISTS reportes_generados (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    formato VARCHAR(10) CHECK (formato IN ('PDF', 'EXCEL', 'CSV')),
    ruta_archivo TEXT,
    generado_por INTEGER REFERENCES personal_admin(id),
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reporte_fecha ON reportes_generados(fecha_generacion);

-- ============================================================================
-- DATOS INICIALES
-- ============================================================================

-- Configuración por defecto
INSERT INTO sys_config (modo_operacion, nombre_institucion, reglas_json, color_primario, color_secundario)
VALUES (
    'UNIVERSIDAD',
    'Sistema Universitario de Asistencia',
    '{"tolerancia_minutos": 15, "minimo_asistencia": 75, "umbral_desercion": 3, "duracion_qr": 30, "gamificacion_activa": true, "umbral_confianza": 85}'::jsonb,
    '#023859',
    '#54ACBF'
) ON CONFLICT DO NOTHING;

-- Badges por defecto
INSERT INTO badges (nombre, descripcion, icono_emoji, color_hex, puntos_requeridos, nivel_requerido)
VALUES 
    ('PUNTUAL_ORO', 'Nunca llega tarde', '🏆', '#FFD700', 100, 5),
    ('ASISTENCIA_PERFECTA', 'Asistencia 100% en el mes', '⭐', '#4CAF50', 50, 3),
    ('ESTUDIANTE_DESTACADO', 'Reconocimiento especial', '🎓', '#2196F3', 200, 8),
    ('RACHA_SEMANAL', 'Asistencia completa por 1 semana', '🔥', '#FF5722', 25, 2),
    ('NOVATO', 'Primera semana completada', '🌱', '#8BC34A', 10, 1)
ON CONFLICT (nombre) DO NOTHING;

-- ============================================================================
-- FIN DEL SCHEMA
-- ============================================================================
