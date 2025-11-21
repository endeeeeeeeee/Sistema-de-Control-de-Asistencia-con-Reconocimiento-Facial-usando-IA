-- =====================================================
-- SISTEMA DE ASISTENCIA FLEXIBLE - NUEVA ARQUITECTURA
-- Soporta: Universidad, Colegio, Guardería, Empresa, Gym, etc.
-- =====================================================

-- Eliminar tablas antiguas si existen
DROP TABLE IF EXISTS asistencia_log CASCADE;
DROP TABLE IF EXISTS membresias CASCADE;
DROP TABLE IF EXISTS equipos CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS codigos_invitacion CASCADE;
DROP TABLE IF EXISTS sesiones_activas CASCADE;
DROP TABLE IF EXISTS badges CASCADE;
DROP TABLE IF EXISTS usuario_badges CASCADE;
DROP TABLE IF EXISTS alertas_equipo CASCADE;
DROP TABLE IF EXISTS sys_config CASCADE;

-- =====================================================
-- 1. TABLA DE USUARIOS (Unificada)
-- =====================================================
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    codigo_usuario VARCHAR(50) UNIQUE NOT NULL,  -- USER-2025-001
    nombre_completo VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Para login
    telefono VARCHAR(20),
    ci VARCHAR(50),
    fecha_nacimiento DATE,
    foto_face_vector TEXT,  -- Base64 de fotos para reconocimiento facial
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_conexion TIMESTAMP,
    puntos_totales INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    
    -- Índices
    CONSTRAINT usuarios_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_usuarios_codigo ON usuarios(codigo_usuario);
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);

-- =====================================================
-- 2. TABLA DE EQUIPOS/CLASES
-- =====================================================
CREATE TABLE equipos (
    id SERIAL PRIMARY KEY,
    nombre_equipo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo_equipo VARCHAR(50) NOT NULL,  -- universidad, colegio, guarderia, empresa, gym, otro
    codigo_invitacion VARCHAR(20) UNIQUE NOT NULL,  -- TEAM-ABC123
    creador_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    configuracion_json JSONB DEFAULT '{}',  -- Configuración específica del equipo
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Configuraciones en JSON pueden incluir:
    -- {
    --   "tolerancia_minutos": 15,
    --   "minimo_asistencia": 75,
    --   "horario": {"lunes": ["08:00-10:00"], "martes": ["08:00-10:00"]},
    --   "gamificacion": true,
    --   "qr_uso_unico": true
    -- }
    
    CONSTRAINT equipos_tipo_check CHECK (tipo_equipo IN (
        'universidad', 'colegio', 'guarderia', 'empresa', 'gym', 'otro'
    ))
);

CREATE INDEX idx_equipos_codigo ON equipos(codigo_invitacion);
CREATE INDEX idx_equipos_creador ON equipos(creador_id);
CREATE INDEX idx_equipos_tipo ON equipos(tipo_equipo);
CREATE INDEX idx_equipos_activo ON equipos(activo);

-- =====================================================
-- 3. TABLA DE MEMBRESÍAS (Relación N:N)
-- =====================================================
CREATE TABLE membresias (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    equipo_id INTEGER NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    rol VARCHAR(20) NOT NULL DEFAULT 'miembro',  -- lider, co-lider, miembro
    estado VARCHAR(20) DEFAULT 'activo',  -- activo, inactivo, suspendido
    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    puntos_equipo INTEGER DEFAULT 0,  -- Puntos específicos en este equipo
    asistencias_totales INTEGER DEFAULT 0,
    faltas_totales INTEGER DEFAULT 0,
    porcentaje_asistencia DECIMAL(5,2) DEFAULT 0.00,
    
    UNIQUE(usuario_id, equipo_id),
    
    CONSTRAINT membresias_rol_check CHECK (rol IN ('lider', 'co-lider', 'miembro')),
    CONSTRAINT membresias_estado_check CHECK (estado IN ('activo', 'inactivo', 'suspendido'))
);

CREATE INDEX idx_membresias_usuario ON membresias(usuario_id);
CREATE INDEX idx_membresias_equipo ON membresias(equipo_id);
CREATE INDEX idx_membresias_rol ON membresias(rol);
CREATE INDEX idx_membresias_estado ON membresias(estado);

-- =====================================================
-- 4. TABLA DE ASISTENCIA
-- =====================================================
CREATE TABLE asistencia_log (
    id SERIAL PRIMARY KEY,
    membresia_id INTEGER NOT NULL REFERENCES membresias(id) ON DELETE CASCADE,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    hora_entrada TIME NOT NULL DEFAULT CURRENT_TIME,
    hora_salida TIME,
    metodo_entrada VARCHAR(20) NOT NULL,  -- facial, qr, manual
    estado VARCHAR(20) DEFAULT 'presente',  -- presente, tarde, ausente, justificado
    notas TEXT,
    ip_address VARCHAR(50),
    dispositivo VARCHAR(200),
    foto_verificacion TEXT,  -- Foto capturada al marcar asistencia
    
    CONSTRAINT asistencia_metodo_check CHECK (metodo_entrada IN ('facial', 'qr', 'manual')),
    CONSTRAINT asistencia_estado_check CHECK (estado IN ('presente', 'tarde', 'ausente', 'justificado'))
);

CREATE INDEX idx_asistencia_membresia ON asistencia_log(membresia_id);
CREATE INDEX idx_asistencia_fecha ON asistencia_log(fecha);
CREATE INDEX idx_asistencia_estado ON asistencia_log(estado);

-- =====================================================
-- 5. TABLA DE CÓDIGOS TEMPORALES (QR)
-- =====================================================
CREATE TABLE codigos_temporales (
    id SERIAL PRIMARY KEY,
    equipo_id INTEGER NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    tipo VARCHAR(20) NOT NULL,  -- qr_asistencia, qr_dispositivo
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    usado_por INTEGER REFERENCES usuarios(id),
    usado_en TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT codigos_tipo_check CHECK (tipo IN ('qr_asistencia', 'qr_dispositivo'))
);

CREATE INDEX idx_codigos_equipo ON codigos_temporales(equipo_id);
CREATE INDEX idx_codigos_codigo ON codigos_temporales(codigo);
CREATE INDEX idx_codigos_activo ON codigos_temporales(activo, fecha_expiracion);

-- =====================================================
-- 6. TABLA DE SESIONES ACTIVAS
-- =====================================================
CREATE TABLE sesiones_activas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    activa BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_sesiones_usuario ON sesiones_activas(usuario_id);
CREATE INDEX idx_sesiones_token ON sesiones_activas(token);
CREATE INDEX idx_sesiones_activa ON sesiones_activas(activa);

-- =====================================================
-- 7. TABLA DE BADGES/LOGROS
-- =====================================================
CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    icono VARCHAR(50),  -- emoji o referencia a imagen
    puntos_requeridos INTEGER,
    criterio_json JSONB,  -- Criterios para obtener el badge
    color VARCHAR(20),
    nivel INTEGER DEFAULT 1,
    activo BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- 8. TABLA DE BADGES DE USUARIOS
-- =====================================================
CREATE TABLE usuario_badges (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    badge_id INTEGER NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    membresia_id INTEGER REFERENCES membresias(id) ON DELETE CASCADE,  -- Badge específico de equipo
    fecha_obtencion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(usuario_id, badge_id, membresia_id)
);

CREATE INDEX idx_usuario_badges_usuario ON usuario_badges(usuario_id);
CREATE INDEX idx_usuario_badges_membresia ON usuario_badges(membresia_id);

-- =====================================================
-- 9. TABLA DE ALERTAS POR EQUIPO
-- =====================================================
CREATE TABLE alertas_equipo (
    id SERIAL PRIMARY KEY,
    membresia_id INTEGER NOT NULL REFERENCES membresias(id) ON DELETE CASCADE,
    tipo_alerta VARCHAR(50) NOT NULL,  -- desercion, bajo_rendimiento, inactividad
    descripcion TEXT,
    nivel_severidad VARCHAR(20) DEFAULT 'media',  -- baja, media, alta
    atendida BOOLEAN DEFAULT FALSE,
    atendida_por INTEGER REFERENCES usuarios(id),
    fecha_atencion TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT alertas_nivel_check CHECK (nivel_severidad IN ('baja', 'media', 'alta'))
);

CREATE INDEX idx_alertas_membresia ON alertas_equipo(membresia_id);
CREATE INDEX idx_alertas_atendida ON alertas_equipo(atendida);

-- =====================================================
-- 10. TABLA DE CONFIGURACIÓN DEL SISTEMA
-- =====================================================
CREATE TABLE sys_config (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT,
    tipo VARCHAR(20) DEFAULT 'string',  -- string, number, boolean, json
    descripcion TEXT,
    modificable BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Insertar configuración del sistema
INSERT INTO sys_config (clave, valor, tipo, descripcion) VALUES
('sistema_nombre', 'CLASS VISION', 'string', 'Nombre del sistema'),
('version', '3.0', 'string', 'Versión del sistema'),
('modo_demo', 'false', 'boolean', 'Modo demostración activo'),
('max_equipos_por_usuario', '10', 'number', 'Máximo de equipos que puede crear un usuario');

-- Insertar badges iniciales
INSERT INTO badges (nombre, descripcion, icono, puntos_requeridos, color, nivel) VALUES
('🌟 Primera Asistencia', 'Completó su primera asistencia', '🌟', 0, '#FFD700', 1),
('🔥 Racha 7 Días', 'Asistió 7 días consecutivos', '🔥', 50, '#FF4500', 2),
('💎 Puntual Diamante', '100% puntual en el mes', '💎', 100, '#00CED1', 3),
('👑 Rey de Asistencia', '95%+ asistencia en el equipo', '👑', 200, '#FFD700', 4),
('🚀 Líder Activo', 'Creó y mantiene un equipo activo', '🚀', 150, '#4169E1', 3);

-- =====================================================
-- USUARIO DE PRUEBA
-- =====================================================
-- Password: admin123 (SHA-256: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9)
INSERT INTO usuarios (codigo_usuario, nombre_completo, email, password_hash, activo, nivel) VALUES
('USER-2025-001', 'Administrador Sistema', 'admin@classvision.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', TRUE, 5);

-- =====================================================
-- VISTAS ÚTILES
-- =====================================================

-- Vista de equipos con información del creador
CREATE VIEW v_equipos_detalle AS
SELECT 
    e.*,
    u.nombre_completo AS creador_nombre,
    u.email AS creador_email,
    (SELECT COUNT(*) FROM membresias m WHERE m.equipo_id = e.id AND m.estado = 'activo') AS total_miembros
FROM equipos e
JOIN usuarios u ON e.creador_id = u.id;

-- Vista de membresías con detalles
CREATE VIEW v_membresias_detalle AS
SELECT 
    m.*,
    u.codigo_usuario,
    u.nombre_completo,
    u.email,
    e.nombre_equipo,
    e.tipo_equipo,
    e.codigo_invitacion
FROM membresias m
JOIN usuarios u ON m.usuario_id = u.id
JOIN equipos e ON m.equipo_id = e.id;

-- Vista de asistencia con detalles completos
CREATE VIEW v_asistencia_completa AS
SELECT 
    a.*,
    m.usuario_id,
    m.equipo_id,
    m.rol,
    u.codigo_usuario,
    u.nombre_completo,
    e.nombre_equipo,
    e.tipo_equipo
FROM asistencia_log a
JOIN membresias m ON a.membresia_id = m.id
JOIN usuarios u ON m.usuario_id = u.id
JOIN equipos e ON m.equipo_id = e.id;

-- =====================================================
-- FUNCIONES ÚTILES
-- =====================================================

-- Función para generar código de usuario único
CREATE OR REPLACE FUNCTION generar_codigo_usuario()
RETURNS VARCHAR(50) AS $$
DECLARE
    nuevo_codigo VARCHAR(50);
    existe BOOLEAN;
BEGIN
    LOOP
        nuevo_codigo := 'USER-' || TO_CHAR(CURRENT_DATE, 'YYYY') || '-' || LPAD(FLOOR(RANDOM() * 9999 + 1)::TEXT, 4, '0');
        SELECT EXISTS(SELECT 1 FROM usuarios WHERE codigo_usuario = nuevo_codigo) INTO existe;
        EXIT WHEN NOT existe;
    END LOOP;
    RETURN nuevo_codigo;
END;
$$ LANGUAGE plpgsql;

-- Función para generar código de invitación único
CREATE OR REPLACE FUNCTION generar_codigo_invitacion()
RETURNS VARCHAR(20) AS $$
DECLARE
    nuevo_codigo VARCHAR(20);
    existe BOOLEAN;
    caracteres VARCHAR(36) := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';  -- Sin caracteres confusos
    i INTEGER;
BEGIN
    LOOP
        nuevo_codigo := 'TEAM-';
        FOR i IN 1..6 LOOP
            nuevo_codigo := nuevo_codigo || SUBSTR(caracteres, FLOOR(RANDOM() * LENGTH(caracteres) + 1)::INTEGER, 1);
        END LOOP;
        SELECT EXISTS(SELECT 1 FROM equipos WHERE codigo_invitacion = nuevo_codigo) INTO existe;
        EXIT WHEN NOT existe;
    END LOOP;
    RETURN nuevo_codigo;
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar estadísticas de membresía
CREATE OR REPLACE FUNCTION actualizar_estadisticas_membresia(p_membresia_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE membresias m
    SET 
        asistencias_totales = (
            SELECT COUNT(*) 
            FROM asistencia_log a 
            WHERE a.membresia_id = p_membresia_id 
            AND a.estado IN ('presente', 'tarde')
        ),
        faltas_totales = (
            SELECT COUNT(*) 
            FROM asistencia_log a 
            WHERE a.membresia_id = p_membresia_id 
            AND a.estado = 'ausente'
        ),
        porcentaje_asistencia = (
            SELECT CASE 
                WHEN COUNT(*) > 0 THEN 
                    (COUNT(*) FILTER (WHERE estado IN ('presente', 'tarde'))::DECIMAL / COUNT(*) * 100)
                ELSE 0 
            END
            FROM asistencia_log a 
            WHERE a.membresia_id = p_membresia_id
        )
    WHERE m.id = p_membresia_id;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar estadísticas automáticamente
CREATE OR REPLACE FUNCTION trigger_actualizar_estadisticas()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM actualizar_estadisticas_membresia(NEW.membresia_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_asistencia_estadisticas
AFTER INSERT OR UPDATE ON asistencia_log
FOR EACH ROW
EXECUTE FUNCTION trigger_actualizar_estadisticas();

-- =====================================================
-- COMENTARIOS
-- =====================================================

COMMENT ON TABLE usuarios IS 'Tabla unificada de todos los usuarios del sistema';
COMMENT ON TABLE equipos IS 'Equipos, clases o grupos creados por usuarios';
COMMENT ON TABLE membresias IS 'Relación N:N entre usuarios y equipos con roles';
COMMENT ON TABLE asistencia_log IS 'Registro de asistencias vinculado a membresías';

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
