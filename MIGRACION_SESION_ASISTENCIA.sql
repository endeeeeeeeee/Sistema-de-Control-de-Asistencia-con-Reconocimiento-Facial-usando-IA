-- ============================================================================
-- MIGRACIÓN: AGREGAR TIPO SESION_ASISTENCIA A codigos_temporales
-- ============================================================================
-- Fecha: 2025-11-20
-- Descripción: Agrega el tipo 'SESION_ASISTENCIA' a la restricción CHECK
--              de la tabla codigos_temporales para soportar sesiones de
--              asistencia con reconocimiento facial en vivo.
-- ============================================================================

-- 1. Eliminar restricción CHECK antigua
ALTER TABLE codigos_temporales 
DROP CONSTRAINT IF EXISTS codigos_temporales_tipo_check;

-- 2. Agregar nueva restricción CHECK con SESION_ASISTENCIA
ALTER TABLE codigos_temporales 
ADD CONSTRAINT codigos_temporales_tipo_check 
CHECK (tipo IN (
    'QR_CLASE_VIRTUAL',
    'CODIGO_NUMERICO',
    'QR_PICKUP_GUARDERIA',
    'ENLACE_UNICO',
    'SESION_ASISTENCIA'
));

-- 3. Verificar que la restricción se aplicó correctamente
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'codigos_temporales'::regclass 
  AND conname = 'codigos_temporales_tipo_check';

-- ============================================================================
-- NOTAS:
-- ============================================================================
-- El tipo SESION_ASISTENCIA se utiliza para:
-- - Crear sesiones de asistencia con reconocimiento facial
-- - Controlar la duración de las sesiones (por defecto 30 minutos)
-- - Rastrear qué usuarios fueron reconocidos durante la sesión
-- - Prevenir sesiones duplicadas por equipo
-- 
-- Campos importantes para SESION_ASISTENCIA:
-- - codigo: Identificador único de la sesión (ej: SESION-abc123...)
-- - equipo_id: ID del equipo para el cual se creó la sesión
-- - generado_por: ID del líder que inició la sesión
-- - expira_en: Timestamp de expiración de la sesión
-- - usado: false mientras está activa, true cuando se detiene
-- - metadata: JSON con información de la sesión (reconocimientos, duración)
-- ============================================================================
