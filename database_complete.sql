-- ============================================================================
-- CLASS VISION - Sistema de Control de Asistencia con IA
-- Base de Datos Completa - PostgreSQL 14+
-- Soporta: GUARDERÍA, COLEGIO, UNIVERSIDAD
-- Características: Multi-modal, Gamificación, Predicción deserción, Virtual
-- ============================================================================

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. CONFIGURACIÓN DEL SISTEMA
-- ============================================================================

CREATE TABLE sys_config (
    id SERIAL PRIMARY KEY,
    modo_operacion VARCHAR(20) NOT NULL CHECK (modo_operacion IN ('GUARDERIA', 'COLEGIO', 'UNIVERSIDAD')),
    nombre_institucion VARCHAR(200) NOT NULL,
    
    -- Reglas dinámicas (editables por asistente virtual)
    reglas_json JSONB NOT NULL DEFAULT '{
        "tolerancia_minutos": 10,
        "faltas_alerta": 3,
        "modo_virtual_habilitado": true,
        "reconocimiento_facial_obligatorio": true,
        "liveness_detection": false,
        "gamificacion_habilitada": true,
        "puntos_por_asistencia": 10,
        "puntos_por_puntualidad": 5,
        "notificaciones_tutores": true,
        "codigo_qr_expiracion_minutos": 5
    }'::jsonb,
    
    -- Colores y branding
    color_primario VARCHAR(7) DEFAULT '#023859',
    color_secundario VARCHAR(7) DEFAULT '#54ACBF',
    logo_url TEXT,
    
    -- Configuración de horarios
    horario_inicio TIME DEFAULT '07:00:00',
    horario_fin TIME DEFAULT '18:00:00',
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW(),
    actualizado_por INTEGER -- Será FK después
);

-- ============================================================================
-- 2. USUARIOS DEL SISTEMA
-- ============================================================================

CREATE TABLE personal_admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- SHA-256
    full_name VARCHAR(200) NOT NULL,
    
    rol VARCHAR(50) NOT NULL CHECK (rol IN (
        'DIRECTOR', 
        'DOCENTE', 
        'TIA_GUARDERIA', 
        'SECRETARIA',
        'ADMIN_SISTEMA'
    )),
    
    -- Información de contacto
    email VARCHAR(150),
    telefono VARCHAR(20),
    
    -- Face recognition (opcional para docentes)
    foto_face_vector BYTEA,
    
    -- Estado
    activo BOOLEAN DEFAULT TRUE,
    ultimo_acceso TIMESTAMP,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_personal_username ON personal_admin(username);
CREATE INDEX idx_personal_rol ON personal_admin(rol);

-- ============================================================================
-- 3. TUTORES/PADRES
-- ============================================================================

CREATE TABLE tutores (
    id SERIAL PRIMARY KEY,
    ci VARCHAR(20) UNIQUE NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    
    -- Información de contacto
    telefono VARCHAR(20),
    email VARCHAR(150),
    direccion TEXT,
    
    -- Face recognition para recoger niños en guardería
    foto_face_vector BYTEA,
    
    -- Relación con estudiante
    relacion VARCHAR(50) CHECK (relacion IN ('PADRE', 'MADRE', 'TUTOR', 'ABUELO', 'TIO', 'OTRO')),
    
    -- QR para pickup en guardería
    qr_code_pickup VARCHAR(100) UNIQUE,
    
    -- Estado
    activo BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tutores_ci ON tutores(ci);
CREATE INDEX idx_tutores_qr ON tutores(qr_code_pickup);

-- ============================================================================
-- 4. ESTUDIANTES
-- ============================================================================

CREATE TABLE estudiantes (
    id SERIAL PRIMARY KEY,
    codigo_estudiante VARCHAR(50) UNIQUE NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    
    -- Información personal
    fecha_nacimiento DATE NOT NULL,
    ci VARCHAR(20),
    genero CHAR(1) CHECK (genero IN ('M', 'F', 'O')),
    
    -- Información de contacto
    telefono VARCHAR(20),
    email VARCHAR(150),
    direccion TEXT,
    
    -- Face recognition (múltiples vectores para mejor precisión)
    foto_face_vector BYTEA NOT NULL,
    
    -- Relación con tutor (NULL para universidad)
    id_tutor INTEGER REFERENCES tutores(id),
    
    -- Gamificación
    puntos_acumulados INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    
    -- Estado académico
    activo BOOLEAN DEFAULT TRUE,
    fecha_ingreso DATE DEFAULT CURRENT_DATE,
    fecha_egreso DATE,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_estudiantes_codigo ON estudiantes(codigo_estudiante);
CREATE INDEX idx_estudiantes_tutor ON estudiantes(id_tutor);
CREATE INDEX idx_estudiantes_activo ON estudiantes(activo);

-- ============================================================================
-- 5. MATERIAS/CLASES
-- ============================================================================

CREATE TABLE materias (
    id SERIAL PRIMARY KEY,
    codigo_materia VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    
    -- Nivel educativo
    nivel VARCHAR(50) CHECK (nivel IN (
        'MATERNAL', 'KINDER', 'PREKINDER', -- Guardería
        'PRIMARIA', 'SECUNDARIA', -- Colegio
        'UNIVERSIDAD' -- Universidad
    )),
    
    -- Docente responsable
    id_docente INTEGER NOT NULL REFERENCES personal_admin(id),
    
    -- Horario
    dia_semana INTEGER[] CHECK (dia_semana <@ ARRAY[1,2,3,4,5,6,7]), -- 1=Lunes, 7=Domingo
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    
    -- Configuración de asistencia
    requiere_asistencia BOOLEAN DEFAULT TRUE,
    tolerancia_minutos INTEGER DEFAULT 10,
    
    -- Estado
    activo BOOLEAN DEFAULT TRUE,
    periodo_academico VARCHAR(50), -- "2025-1", "2025-2"
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_materias_docente ON materias(id_docente);
CREATE INDEX idx_materias_nivel ON materias(nivel);
CREATE INDEX idx_materias_codigo ON materias(codigo_materia);

-- ============================================================================
-- 6. INSCRIPCIONES (Estudiante-Materia)
-- ============================================================================

CREATE TABLE inscripciones (
    id SERIAL PRIMARY KEY,
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    id_materia INTEGER NOT NULL REFERENCES materias(id) ON DELETE CASCADE,
    
    -- Puntos específicos de esta materia
    puntos_acumulados INTEGER DEFAULT 0,
    
    -- Estado
    estado VARCHAR(20) DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'RETIRADO', 'APROBADO', 'REPROBADO')),
    
    -- Estadísticas rápidas (desnormalizadas para performance)
    total_asistencias INTEGER DEFAULT 0,
    total_faltas INTEGER DEFAULT 0,
    total_tardanzas INTEGER DEFAULT 0,
    porcentaje_asistencia DECIMAL(5,2) DEFAULT 100.00,
    
    -- Metadata
    fecha_inscripcion DATE DEFAULT CURRENT_DATE,
    fecha_retiro DATE,
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(id_estudiante, id_materia)
);

CREATE INDEX idx_inscripciones_estudiante ON inscripciones(id_estudiante);
CREATE INDEX idx_inscripciones_materia ON inscripciones(id_materia);
CREATE INDEX idx_inscripciones_estado ON inscripciones(estado);

-- ============================================================================
-- 7. ASISTENCIA LOG (Registro Principal)
-- ============================================================================

CREATE TABLE asistencia_log (
    id SERIAL PRIMARY KEY,
    id_inscripcion INTEGER NOT NULL REFERENCES inscripciones(id) ON DELETE CASCADE,
    
    -- Información temporal
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    hora_entrada TIMESTAMP NOT NULL DEFAULT NOW(),
    hora_salida TIMESTAMP,
    
    -- Método de entrada
    metodo_entrada VARCHAR(50) NOT NULL CHECK (metodo_entrada IN (
        'RECONOCIMIENTO_FACIAL',
        'QR_CODE',
        'CODIGO_TEMPORAL',
        'MANUAL'
    )),
    
    -- Estado de asistencia
    estado VARCHAR(20) NOT NULL DEFAULT 'PRESENTE' CHECK (estado IN (
        'PRESENTE',
        'TARDANZA',
        'AUSENTE',
        'JUSTIFICADO',
        'VIRTUAL'
    )),
    
    -- Anti-fraude
    score_liveness DECIMAL(5,2), -- 0.00 a 100.00
    ip_address INET,
    ubicacion_gps POINT, -- Para móvil
    
    -- Guardería específico
    id_tutor_pickup INTEGER REFERENCES tutores(id), -- Quién recogió al niño
    hora_pickup TIMESTAMP,
    
    -- Virtual mode (FK se agrega después)
    id_codigo_temporal INTEGER,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_asistencia_inscripcion ON asistencia_log(id_inscripcion);
CREATE INDEX idx_asistencia_fecha ON asistencia_log(fecha);
CREATE INDEX idx_asistencia_estado ON asistencia_log(estado);
CREATE INDEX idx_asistencia_metodo ON asistencia_log(metodo_entrada);

-- ============================================================================
-- 8. JUSTIFICACIONES
-- ============================================================================

CREATE TABLE justificaciones (
    id SERIAL PRIMARY KEY,
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    id_materia INTEGER REFERENCES materias(id),
    
    -- Información de la justificación
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    motivo TEXT NOT NULL,
    tipo VARCHAR(50) CHECK (tipo IN ('MEDICO', 'FAMILIAR', 'PERSONAL', 'OTRO')),
    
    -- Documento adjunto
    documento_url TEXT,
    
    -- Aprobación
    estado VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'APROBADO', 'RECHAZADO')),
    aprobado_por INTEGER REFERENCES personal_admin(id),
    fecha_aprobacion TIMESTAMP,
    comentario_aprobacion TEXT,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_justificaciones_estudiante ON justificaciones(id_estudiante);
CREATE INDEX idx_justificaciones_estado ON justificaciones(estado);

-- ============================================================================
-- 9. BADGES/INSIGNIAS (Gamificación)
-- ============================================================================

CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    icono_url TEXT,
    
    -- Condiciones para obtener
    condicion_tipo VARCHAR(50) CHECK (condicion_tipo IN (
        'ASISTENCIA_PERFECTA', -- 100% en un mes
        'PUNTUALIDAD_EXTREMA', -- 30 días seguidos puntual
        'RACHA_SEMANAL', -- 1 semana perfecta
        'PARTICIPACION', -- Más de X participaciones
        'MEJORA_CONTINUA', -- Mejora en asistencia
        'CUSTOM' -- Definido por admin
    )),
    condicion_valor INTEGER, -- Valor numérico de la condición
    
    -- Recompensa
    puntos_otorga INTEGER DEFAULT 0,
    
    -- Rareza
    rareza VARCHAR(20) CHECK (rareza IN ('COMUN', 'RARO', 'EPICO', 'LEGENDARIO')),
    
    -- Estado
    activo BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_badges_codigo ON badges(codigo);

-- ============================================================================
-- 10. ESTUDIANTES_BADGES (Logros Obtenidos)
-- ============================================================================

CREATE TABLE estudiantes_badges (
    id SERIAL PRIMARY KEY,
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    id_badge INTEGER NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    
    -- Información del logro
    fecha_obtencion TIMESTAMP DEFAULT NOW(),
    periodo_academico VARCHAR(50),
    
    -- Metadata adicional
    metadata_json JSONB, -- Info sobre cómo se obtuvo
    
    UNIQUE(id_estudiante, id_badge, periodo_academico)
);

CREATE INDEX idx_estudiantes_badges_estudiante ON estudiantes_badges(id_estudiante);
CREATE INDEX idx_estudiantes_badges_badge ON estudiantes_badges(id_badge);

-- ============================================================================
-- 11. RANKING MENSUAL
-- ============================================================================

CREATE TABLE ranking_mensual (
    id SERIAL PRIMARY KEY,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    
    -- Métricas
    total_puntos INTEGER DEFAULT 0,
    total_asistencias INTEGER DEFAULT 0,
    porcentaje_puntualidad DECIMAL(5,2) DEFAULT 0.00,
    badges_obtenidos INTEGER DEFAULT 0,
    
    -- Posición
    posicion INTEGER,
    
    -- Metadata
    calculado_en TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(anio, mes, id_estudiante)
);

CREATE INDEX idx_ranking_periodo ON ranking_mensual(anio, mes);
CREATE INDEX idx_ranking_posicion ON ranking_mensual(posicion);

-- ============================================================================
-- 12. ALERTAS DE DESERCIÓN (AI Prediction)
-- ============================================================================

CREATE TABLE alertas_desercion (
    id SERIAL PRIMARY KEY,
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    
    -- Nivel de riesgo (calculado por AI)
    nivel_riesgo VARCHAR(20) NOT NULL CHECK (nivel_riesgo IN ('BAJO', 'MEDIO', 'ALTO', 'CRITICO')),
    probabilidad_desercion DECIMAL(5,2) NOT NULL, -- 0.00 a 100.00
    
    -- Factores que contribuyen
    factores_json JSONB NOT NULL, -- Array de factores detectados
    /*
    Ejemplo:
    {
        "faltas_consecutivas": 5,
        "porcentaje_asistencia": 45.5,
        "tendencia": "descendente",
        "promedio_notas": 55.0,
        "factores": ["ausentismo_alto", "bajo_rendimiento", "falta_participacion"]
    }
    */
    
    -- Acciones tomadas
    estado VARCHAR(20) DEFAULT 'NUEVA' CHECK (estado IN ('NUEVA', 'EN_SEGUIMIENTO', 'RESUELTA', 'CRITICA')),
    acciones_tomadas TEXT[],
    
    -- Asignación
    asignado_a INTEGER REFERENCES personal_admin(id),
    fecha_seguimiento TIMESTAMP,
    
    -- Metadata
    detectado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alertas_estudiante ON alertas_desercion(id_estudiante);
CREATE INDEX idx_alertas_nivel ON alertas_desercion(nivel_riesgo);
CREATE INDEX idx_alertas_estado ON alertas_desercion(estado);

-- ============================================================================
-- 13. NOTIFICACIONES INTERNAS (In-App Only)
-- ============================================================================

CREATE TABLE notificaciones_internas (
    id SERIAL PRIMARY KEY,
    
    -- Destinatario
    destinatario_tipo VARCHAR(20) NOT NULL CHECK (destinatario_tipo IN ('ESTUDIANTE', 'TUTOR', 'DOCENTE', 'ADMIN')),
    destinatario_id INTEGER NOT NULL, -- ID de la tabla correspondiente
    
    -- Contenido
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN (
        'ASISTENCIA_CONFIRMADA',
        'TARDANZA_REGISTRADA',
        'FALTA_REGISTRADA',
        'ALERTA_FALTAS_CONSECUTIVAS',
        'BADGE_OBTENIDO',
        'NUEVO_RANKING',
        'JUSTIFICACION_APROBADA',
        'JUSTIFICACION_RECHAZADA',
        'ALERTA_DESERCION',
        'PICKUP_GUARDERIA',
        'CODIGO_QR_GENERADO',
        'CLASE_VIRTUAL_INICIADA',
        'SISTEMA'
    )),
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    
    -- Metadata adicional
    metadata_json JSONB, -- Info contextual (IDs, enlaces, etc.)
    
    -- Estado
    leida BOOLEAN DEFAULT FALSE,
    fecha_lectura TIMESTAMP,
    
    -- Prioridad
    prioridad VARCHAR(20) DEFAULT 'NORMAL' CHECK (prioridad IN ('BAJA', 'NORMAL', 'ALTA', 'URGENTE')),
    
    -- Expiración (para limpiar notificaciones antiguas)
    expira_en TIMESTAMP,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notificaciones_destinatario ON notificaciones_internas(destinatario_tipo, destinatario_id);
CREATE INDEX idx_notificaciones_leida ON notificaciones_internas(leida);
CREATE INDEX idx_notificaciones_creado ON notificaciones_internas(creado_en);

-- ============================================================================
-- 14. SESIONES ACTIVAS
-- ============================================================================

CREATE TABLE sesiones_activas (
    id SERIAL PRIMARY KEY,
    token VARCHAR(100) UNIQUE NOT NULL,
    
    -- Usuario
    usuario_tipo VARCHAR(20) NOT NULL CHECK (usuario_tipo IN ('PERSONAL', 'ESTUDIANTE', 'TUTOR')),
    usuario_id INTEGER NOT NULL,
    
    -- Información de sesión
    ip_address INET,
    user_agent TEXT,
    dispositivo VARCHAR(100),
    
    -- Tiempo
    fecha_inicio TIMESTAMP DEFAULT NOW(),
    fecha_expiracion TIMESTAMP NOT NULL,
    ultima_actividad TIMESTAMP DEFAULT NOW(),
    
    -- Estado
    activa BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_sesiones_token ON sesiones_activas(token);
CREATE INDEX idx_sesiones_usuario ON sesiones_activas(usuario_tipo, usuario_id);
CREATE INDEX idx_sesiones_expiracion ON sesiones_activas(fecha_expiracion);

-- ============================================================================
-- 15. CÓDIGOS TEMPORALES (QR / Códigos para Virtual)
-- ============================================================================

CREATE TABLE codigos_temporales (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    
    -- Tipo de código
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN (
        'QR_CLASE_VIRTUAL', -- Para asistencia virtual
        'CODIGO_NUMERICO', -- Código de 6 dígitos
        'QR_PICKUP_GUARDERIA', -- Para recoger niños
        'ENLACE_UNICO' -- Link único de un solo uso
    )),
    
    -- Alcance
    id_materia INTEGER REFERENCES materias(id),
    fecha_valido DATE DEFAULT CURRENT_DATE,
    
    -- Validez temporal
    valido_desde TIMESTAMP DEFAULT NOW(),
    valido_hasta TIMESTAMP NOT NULL,
    
    -- Estado
    usado BOOLEAN DEFAULT FALSE,
    fecha_uso TIMESTAMP,
    usado_por INTEGER, -- ID del estudiante que lo usó
    
    -- Seguridad
    hash_verificacion VARCHAR(255), -- Para validar autenticidad
    max_usos INTEGER DEFAULT 1, -- -1 = ilimitado
    usos_actuales INTEGER DEFAULT 0,
    
    -- Metadata
    generado_por INTEGER NOT NULL REFERENCES personal_admin(id),
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_codigos_codigo ON codigos_temporales(codigo);
CREATE INDEX idx_codigos_valido ON codigos_temporales(valido_hasta);
CREATE INDEX idx_codigos_materia ON codigos_temporales(id_materia);

-- ============================================================================
-- 16. ASISTENCIA VIRTUAL (Log Específico)
-- ============================================================================

CREATE TABLE asistencia_virtual (
    id SERIAL PRIMARY KEY,
    id_asistencia_log INTEGER NOT NULL REFERENCES asistencia_log(id) ON DELETE CASCADE,
    id_codigo_temporal INTEGER NOT NULL REFERENCES codigos_temporales(id),
    
    -- Información de conexión virtual
    plataforma VARCHAR(50), -- 'ZOOM', 'MEET', 'TEAMS', 'PROPIO'
    duracion_minutos INTEGER,
    
    -- Verificación de participación
    verificacion_intermitente BOOLEAN DEFAULT FALSE, -- ¿Se verificó que seguía conectado?
    capturas_pantalla INTEGER DEFAULT 0, -- Número de verificaciones
    
    -- Metadata
    ip_address INET,
    user_agent TEXT,
    
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_asistencia_virtual_log ON asistencia_virtual(id_asistencia_log);
CREATE INDEX idx_asistencia_virtual_codigo ON asistencia_virtual(id_codigo_temporal);

-- ============================================================================
-- 17. ESTADÍSTICAS DIARIAS (Pre-calculadas)
-- ============================================================================

CREATE TABLE estadisticas_diarias (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    id_materia INTEGER REFERENCES materias(id) ON DELETE CASCADE,
    
    -- Contadores
    total_estudiantes INTEGER DEFAULT 0,
    total_presentes INTEGER DEFAULT 0,
    total_ausentes INTEGER DEFAULT 0,
    total_tardanzas INTEGER DEFAULT 0,
    total_justificados INTEGER DEFAULT 0,
    total_virtuales INTEGER DEFAULT 0,
    
    -- Porcentajes
    porcentaje_asistencia DECIMAL(5,2) DEFAULT 0.00,
    porcentaje_puntualidad DECIMAL(5,2) DEFAULT 0.00,
    
    -- Metadata
    calculado_en TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(fecha, id_materia)
);

CREATE INDEX idx_estadisticas_fecha ON estadisticas_diarias(fecha);
CREATE INDEX idx_estadisticas_materia ON estadisticas_diarias(id_materia);

-- ============================================================================
-- 18. REPORTES GENERADOS
-- ============================================================================

CREATE TABLE reportes_generados (
    id SERIAL PRIMARY KEY,
    
    -- Información del reporte
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN (
        'ASISTENCIA_DIARIA',
        'ASISTENCIA_SEMANAL',
        'ASISTENCIA_MENSUAL',
        'RANKING_ESTUDIANTES',
        'ALERTAS_DESERCION',
        'ESTADISTICAS_MATERIA',
        'CUSTOM'
    )),
    nombre_archivo VARCHAR(200) NOT NULL,
    formato VARCHAR(10) CHECK (formato IN ('PDF', 'EXCEL', 'CSV', 'JSON')),
    
    -- Filtros aplicados
    filtros_json JSONB,
    
    -- Archivo
    ruta_archivo TEXT NOT NULL,
    tamano_bytes BIGINT,
    
    -- Generación
    generado_por INTEGER NOT NULL REFERENCES personal_admin(id),
    fecha_generacion TIMESTAMP DEFAULT NOW(),
    
    -- Expiración automática
    expira_en TIMESTAMP
);

CREATE INDEX idx_reportes_tipo ON reportes_generados(tipo);
CREATE INDEX idx_reportes_generado_por ON reportes_generados(generado_por);

-- ============================================================================
-- 19. AUDIT LOG (Auditoría Completa)
-- ============================================================================

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    
    -- Quién hizo la acción
    usuario_tipo VARCHAR(20) NOT NULL CHECK (usuario_tipo IN ('PERSONAL', 'ESTUDIANTE', 'TUTOR', 'SISTEMA')),
    usuario_id INTEGER NOT NULL,
    
    -- Qué hizo
    accion VARCHAR(100) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', etc.
    entidad VARCHAR(50) NOT NULL, -- 'estudiantes', 'asistencia_log', 'sys_config', etc.
    entidad_id INTEGER,
    
    -- Detalles
    descripcion TEXT,
    datos_anteriores JSONB, -- Estado antes del cambio
    datos_nuevos JSONB, -- Estado después del cambio
    
    -- Contexto técnico
    ip_address INET,
    user_agent TEXT,
    
    -- Metadata
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_usuario ON audit_log(usuario_tipo, usuario_id);
CREATE INDEX idx_audit_entidad ON audit_log(entidad, entidad_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_accion ON audit_log(accion);

-- ============================================================================
-- 20. HISTORIAL DE COMANDOS DEL ASISTENTE VIRTUAL
-- ============================================================================

CREATE TABLE asistente_historial (
    id SERIAL PRIMARY KEY,
    
    -- Usuario que dio el comando
    id_usuario INTEGER NOT NULL REFERENCES personal_admin(id),
    
    -- Comando procesado
    comando_texto TEXT NOT NULL,
    comando_tipo VARCHAR(50) CHECK (comando_tipo IN (
        'CONSULTA', -- "¿Cuántos estudiantes asistieron hoy?"
        'MODIFICACION', -- "Cambia la tolerancia a 15 minutos"
        'GENERACION', -- "Genera reporte semanal"
        'ANALISIS' -- "¿Quién tiene riesgo de deserción?"
    )),
    
    -- Intención detectada (NLP)
    intencion VARCHAR(100),
    entidades_json JSONB, -- Entidades extraídas del comando
    
    -- Respuesta
    respuesta_texto TEXT,
    respuesta_tipo VARCHAR(50) CHECK (respuesta_tipo IN ('TEXTO', 'AUDIO', 'MIXTO')),
    
    -- Acciones ejecutadas
    acciones_ejecutadas JSONB, -- Array de acciones que se realizaron
    exito BOOLEAN DEFAULT TRUE,
    error_mensaje TEXT,
    
    -- Metadata
    timestamp TIMESTAMP DEFAULT NOW(),
    duracion_ms INTEGER -- Tiempo de procesamiento
);

CREATE INDEX idx_asistente_usuario ON asistente_historial(id_usuario);
CREATE INDEX idx_asistente_timestamp ON asistente_historial(timestamp);
CREATE INDEX idx_asistente_tipo ON asistente_historial(comando_tipo);

-- ============================================================================
-- TRIGGERS Y FUNCIONES
-- ============================================================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a todas las tablas con actualizado_en
CREATE TRIGGER trigger_actualizar_sys_config
    BEFORE UPDATE ON sys_config
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trigger_actualizar_personal
    BEFORE UPDATE ON personal_admin
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trigger_actualizar_tutores
    BEFORE UPDATE ON tutores
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trigger_actualizar_estudiantes
    BEFORE UPDATE ON estudiantes
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trigger_actualizar_materias
    BEFORE UPDATE ON materias
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trigger_actualizar_inscripciones
    BEFORE UPDATE ON inscripciones
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- Función para calcular estadísticas de inscripción automáticamente
CREATE OR REPLACE FUNCTION actualizar_stats_inscripcion()
RETURNS TRIGGER AS $$
DECLARE
    total INTEGER;
    presentes INTEGER;
    tardanzas INTEGER;
BEGIN
    -- Contar asistencias
    SELECT COUNT(*) INTO total
    FROM asistencia_log al
    WHERE al.id_inscripcion = NEW.id_inscripcion;
    
    SELECT COUNT(*) INTO presentes
    FROM asistencia_log al
    WHERE al.id_inscripcion = NEW.id_inscripcion
    AND al.estado IN ('PRESENTE', 'VIRTUAL');
    
    SELECT COUNT(*) INTO tardanzas
    FROM asistencia_log al
    WHERE al.id_inscripcion = NEW.id_inscripcion
    AND al.estado = 'TARDANZA';
    
    -- Actualizar inscripción
    UPDATE inscripciones
    SET 
        total_asistencias = presentes + tardanzas,
        total_faltas = total - presentes - tardanzas,
        total_tardanzas = tardanzas,
        porcentaje_asistencia = CASE 
            WHEN total > 0 THEN ((presentes + tardanzas)::DECIMAL / total::DECIMAL * 100)
            ELSE 100.00
        END
    WHERE id = NEW.id_inscripcion;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_stats_asistencia
    AFTER INSERT OR UPDATE ON asistencia_log
    FOR EACH ROW EXECUTE FUNCTION actualizar_stats_inscripcion();

-- Función para otorgar puntos automáticamente
CREATE OR REPLACE FUNCTION otorgar_puntos_asistencia()
RETURNS TRIGGER AS $$
DECLARE
    puntos_base INTEGER;
    puntos_extra INTEGER := 0;
    config_record RECORD;
BEGIN
    -- Obtener configuración
    SELECT * INTO config_record FROM sys_config LIMIT 1;
    
    IF NEW.estado IN ('PRESENTE', 'VIRTUAL') THEN
        puntos_base := (config_record.reglas_json->>'puntos_por_asistencia')::INTEGER;
        
        -- Bonus por puntualidad
        IF NEW.estado = 'PRESENTE' AND 
           EXTRACT(MINUTE FROM (NEW.hora_entrada - (SELECT hora_inicio FROM materias m 
                                JOIN inscripciones i ON i.id_materia = m.id 
                                WHERE i.id = NEW.id_inscripcion))) <= (config_record.reglas_json->>'tolerancia_minutos')::INTEGER THEN
            puntos_extra := (config_record.reglas_json->>'puntos_por_puntualidad')::INTEGER;
        END IF;
        
        -- Actualizar puntos del estudiante
        UPDATE estudiantes e
        SET puntos_acumulados = puntos_acumulados + puntos_base + puntos_extra
        FROM inscripciones i
        WHERE i.id = NEW.id_inscripcion
        AND e.id = i.id_estudiante;
        
        -- Actualizar puntos de la inscripción
        UPDATE inscripciones
        SET puntos_acumulados = puntos_acumulados + puntos_base + puntos_extra
        WHERE id = NEW.id_inscripcion;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_puntos_asistencia
    AFTER INSERT ON asistencia_log
    FOR EACH ROW EXECUTE FUNCTION otorgar_puntos_asistencia();

-- Función para crear notificación automática
CREATE OR REPLACE FUNCTION crear_notificacion_asistencia()
RETURNS TRIGGER AS $$
DECLARE
    estudiante_record RECORD;
    tutor_id INTEGER;
    mensaje_texto TEXT;
    tipo_notif VARCHAR(50);
BEGIN
    -- Obtener información del estudiante
    SELECT e.*, i.id_tutor INTO estudiante_record
    FROM estudiantes e
    JOIN inscripciones i ON i.id_estudiante = e.id
    WHERE i.id = NEW.id_inscripcion;
    
    -- Determinar tipo y mensaje
    CASE NEW.estado
        WHEN 'PRESENTE' THEN
            tipo_notif := 'ASISTENCIA_CONFIRMADA';
            mensaje_texto := 'Asistencia confirmada exitosamente';
        WHEN 'TARDANZA' THEN
            tipo_notif := 'TARDANZA_REGISTRADA';
            mensaje_texto := 'Llegada tarde registrada';
        WHEN 'AUSENTE' THEN
            tipo_notif := 'FALTA_REGISTRADA';
            mensaje_texto := 'Falta registrada';
        WHEN 'VIRTUAL' THEN
            tipo_notif := 'ASISTENCIA_CONFIRMADA';
            mensaje_texto := 'Asistencia virtual confirmada';
        ELSE
            RETURN NEW;
    END CASE;
    
    -- Notificar al estudiante
    INSERT INTO notificaciones_internas (
        destinatario_tipo, destinatario_id, tipo, titulo, mensaje, metadata_json
    ) VALUES (
        'ESTUDIANTE', estudiante_record.id, tipo_notif,
        tipo_notif, mensaje_texto,
        jsonb_build_object('id_asistencia', NEW.id, 'fecha', NEW.fecha)
    );
    
    -- Notificar al tutor si existe
    IF estudiante_record.id_tutor IS NOT NULL THEN
        INSERT INTO notificaciones_internas (
            destinatario_tipo, destinatario_id, tipo, titulo, mensaje, metadata_json
        ) VALUES (
            'TUTOR', estudiante_record.id_tutor, tipo_notif,
            estudiante_record.nombre_completo || ' - ' || tipo_notif,
            mensaje_texto,
            jsonb_build_object('id_estudiante', estudiante_record.id, 'fecha', NEW.fecha)
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_notificacion_asistencia
    AFTER INSERT ON asistencia_log
    FOR EACH ROW EXECUTE FUNCTION crear_notificacion_asistencia();

-- ============================================================================
-- VISTAS ÚTILES
-- ============================================================================

-- Vista: Estadísticas por estudiante
CREATE OR REPLACE VIEW vista_estadisticas_estudiante AS
SELECT 
    e.id,
    e.codigo_estudiante,
    e.nombre_completo,
    e.puntos_acumulados,
    e.nivel,
    COUNT(DISTINCT i.id_materia) as total_materias,
    COALESCE(SUM(i.total_asistencias), 0) as total_asistencias,
    COALESCE(SUM(i.total_faltas), 0) as total_faltas,
    COALESCE(SUM(i.total_tardanzas), 0) as total_tardanzas,
    COALESCE(AVG(i.porcentaje_asistencia), 0) as promedio_asistencia,
    COUNT(DISTINCT eb.id_badge) as total_badges
FROM estudiantes e
LEFT JOIN inscripciones i ON i.id_estudiante = e.id
LEFT JOIN estudiantes_badges eb ON eb.id_estudiante = e.id
WHERE e.activo = TRUE
GROUP BY e.id, e.codigo_estudiante, e.nombre_completo, e.puntos_acumulados, e.nivel;

-- Vista: Dashboard del docente
CREATE OR REPLACE VIEW vista_dashboard_docente AS
SELECT 
    m.id as id_materia,
    m.nombre as nombre_materia,
    m.codigo_materia,
    p.full_name as nombre_docente,
    COUNT(DISTINCT i.id_estudiante) as total_estudiantes,
    COUNT(DISTINCT CASE 
        WHEN al.fecha = CURRENT_DATE AND al.estado IN ('PRESENTE', 'VIRTUAL') 
        THEN al.id 
    END) as asistencias_hoy,
    COALESCE(AVG(i.porcentaje_asistencia), 0) as promedio_asistencia_materia
FROM materias m
JOIN personal_admin p ON p.id = m.id_docente
LEFT JOIN inscripciones i ON i.id_materia = m.id AND i.estado = 'ACTIVO'
LEFT JOIN asistencia_log al ON al.id_inscripcion = i.id
WHERE m.activo = TRUE
GROUP BY m.id, m.nombre, m.codigo_materia, p.full_name;

-- Vista: Alertas activas
CREATE OR REPLACE VIEW vista_alertas_activas AS
SELECT 
    ad.id,
    e.codigo_estudiante,
    e.nombre_completo,
    ad.nivel_riesgo,
    ad.probabilidad_desercion,
    ad.estado,
    p.full_name as asignado_a_nombre,
    ad.detectado_en
FROM alertas_desercion ad
JOIN estudiantes e ON e.id = ad.id_estudiante
LEFT JOIN personal_admin p ON p.id = ad.asignado_a
WHERE ad.estado IN ('NUEVA', 'EN_SEGUIMIENTO', 'CRITICA')
ORDER BY 
    CASE ad.nivel_riesgo
        WHEN 'CRITICO' THEN 1
        WHEN 'ALTO' THEN 2
        WHEN 'MEDIO' THEN 3
        WHEN 'BAJO' THEN 4
    END,
    ad.probabilidad_desercion DESC;

-- ============================================================================
-- FOREIGN KEYS ADICIONALES (después de crear todas las tablas)
-- ============================================================================

-- Agregar FK de sys_config a personal_admin
ALTER TABLE sys_config
ADD CONSTRAINT fk_sys_config_personal
FOREIGN KEY (actualizado_por) REFERENCES personal_admin(id);

-- Agregar FK de asistencia_log a codigos_temporales
ALTER TABLE asistencia_log
ADD CONSTRAINT fk_asistencia_codigo_temporal
FOREIGN KEY (id_codigo_temporal) REFERENCES codigos_temporales(id);

-- ============================================================================
-- DATOS INICIALES
-- ============================================================================

-- Admin por defecto PRIMERO (password: admin123)
INSERT INTO personal_admin (username, password_hash, full_name, rol)
VALUES ('admin', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Administrador del Sistema', 'ADMIN_SISTEMA');

-- Configuración por defecto DESPUÉS
INSERT INTO sys_config (modo_operacion, nombre_institucion) 
VALUES ('UNIVERSIDAD', 'CLASS VISION - Sistema Inteligente de Asistencia');

-- Badges por defecto
INSERT INTO badges (codigo, nombre, descripcion, condicion_tipo, condicion_valor, puntos_otorga, rareza) VALUES
('ASISTENCIA_PERFECTA_MES', 'Asistencia Perfecta', '100% de asistencia durante un mes completo', 'ASISTENCIA_PERFECTA', 30, 500, 'EPICO'),
('PUNTUAL_30_DIAS', 'Puntualidad Extrema', '30 días consecutivos llegando a tiempo', 'PUNTUALIDAD_EXTREMA', 30, 300, 'RARO'),
('RACHA_SEMANAL', 'Semana Perfecta', 'Una semana completa sin faltas', 'RACHA_SEMANAL', 7, 100, 'COMUN'),
('ESTUDIANTE_ESTRELLA', 'Estudiante Estrella', 'Top 10 del ranking mensual', 'CUSTOM', 10, 200, 'RARO'),
('MEJORA_CONTINUA', 'En Mejora', 'Mejoró su asistencia en 20% respecto al mes anterior', 'MEJORA_CONTINUA', 20, 150, 'COMUN');

-- ============================================================================
-- INDICES ADICIONALES PARA PERFORMANCE
-- ============================================================================

-- Índices compuestos para queries comunes
CREATE INDEX idx_asistencia_fecha_estado ON asistencia_log(fecha, estado);
CREATE INDEX idx_inscripciones_activas ON inscripciones(id_estudiante, estado) WHERE estado = 'ACTIVO';
CREATE INDEX idx_notificaciones_no_leidas ON notificaciones_internas(destinatario_tipo, destinatario_id, leida) WHERE leida = FALSE;

-- Índices para búsquedas de texto (requieren extensión pg_trgm)
-- Descomentar si se instala pg_trgm:
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX idx_estudiantes_nombre_trgm ON estudiantes USING gin(nombre_completo gin_trgm_ops);
-- CREATE INDEX idx_personal_nombre_trgm ON personal_admin USING gin(full_name gin_trgm_ops);

-- ============================================================================
-- COMENTARIOS EN TABLAS (Documentación)
-- ============================================================================

COMMENT ON TABLE sys_config IS 'Configuración global del sistema, editable mediante asistente virtual';
COMMENT ON TABLE personal_admin IS 'Personal administrativo: directores, docentes, secretarias';
COMMENT ON TABLE tutores IS 'Padres/tutores de estudiantes, con face recognition para pickup en guardería';
COMMENT ON TABLE estudiantes IS 'Estudiantes del sistema con vectores faciales para reconocimiento';
COMMENT ON TABLE materias IS 'Clases/asignaturas con horarios y configuración';
COMMENT ON TABLE inscripciones IS 'Relación estudiante-materia con estadísticas';
COMMENT ON TABLE asistencia_log IS 'Registro principal de asistencias con múltiples métodos';
COMMENT ON TABLE badges IS 'Insignias/logros del sistema de gamificación';
COMMENT ON TABLE alertas_desercion IS 'Predicciones de IA sobre riesgo de deserción';
COMMENT ON TABLE notificaciones_internas IS 'Centro de notificaciones in-app (sin email/WhatsApp)';
COMMENT ON TABLE codigos_temporales IS 'QR y códigos para asistencia virtual';
COMMENT ON TABLE asistente_historial IS 'Historial de comandos del asistente virtual tipo Siri';

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================

-- Para verificar la creación exitosa:
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
