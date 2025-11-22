@echo off
echo ============================================
echo APLICANDO CAMBIOS AL SISTEMA CLASS VISION
echo ============================================
echo.

echo Paso 1: Aplicando nuevo esquema de base de datos...
psql -U postgres -h localhost -p 5501 -d class_vision -f database_schema_simple.sql
if %errorlevel% neq 0 (
    echo ERROR: No se pudo aplicar el esquema. Verifica que PostgreSQL este corriendo.
    pause
    exit /b 1
)
echo ✅ Esquema aplicado correctamente
echo.

echo Paso 2: Inicializando datos por defecto...
python init_data.py
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron inicializar los datos
    pause
    exit /b 1
)
echo ✅ Datos inicializados
echo.

echo ============================================
echo ✅ CAMBIOS APLICADOS EXITOSAMENTE
echo ============================================
echo.
echo Ahora puedes:
echo 1. Ejecutar: python mobile_server.py
echo 2. Abrir: http://localhost:5000/registro-estudiante
echo 3. Registrar un estudiante de prueba
echo 4. Login como docente: http://localhost:5000/login
echo    Usuario: docente
echo    Contraseña: docente123
echo 5. Ir a "Estudiantes" e inscribir al estudiante por código
echo.
pause
