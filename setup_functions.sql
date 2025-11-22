-- Funcion para generar codigos de usuario
CREATE OR REPLACE FUNCTION generar_codigo_usuario()
RETURNS VARCHAR AS $$
DECLARE
    nuevo_codigo VARCHAR;
    contador INT;
BEGIN
    SELECT COUNT(*) + 1 INTO contador FROM usuarios;
    nuevo_codigo := 'USER-' || TO_CHAR(EXTRACT(YEAR FROM CURRENT_DATE), 'FM0000') || '-' || LPAD(contador::TEXT, 3, '0');
    RETURN nuevo_codigo;
END;
$$ LANGUAGE plpgsql;

-- Funcion para generar codigos de invitacion
CREATE OR REPLACE FUNCTION generar_codigo_invitacion()
RETURNS VARCHAR AS $$
DECLARE
    nuevo_codigo VARCHAR;
    caracteres VARCHAR := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    i INT;
    existe BOOLEAN;
BEGIN
    LOOP
        nuevo_codigo := 'TEAM-';
        FOR i IN 1..6 LOOP
            nuevo_codigo := nuevo_codigo || SUBSTR(caracteres, FLOOR(RANDOM() * LENGTH(caracteres) + 1)::INT, 1);
        END LOOP;
        
        SELECT EXISTS(SELECT 1 FROM equipos WHERE codigo_invitacion = nuevo_codigo) INTO existe;
        EXIT WHEN NOT existe;
    END LOOP;
    
    RETURN nuevo_codigo;
END;
$$ LANGUAGE plpgsql;

-- Insertar usuario admin inicial
INSERT INTO usuarios (codigo_usuario, nombre_completo, email, password_hash, telefono, activo)
VALUES (
    'USER-2025-001',
    'Administrador',
    'admin@classvision.com',
    'c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec',
    '00000000',
    TRUE
)
ON CONFLICT (email) DO NOTHING;
