@echo off
REM Script para exportar la base de datos PostgreSQL
REM Genera un backup que puedes copiar al servidor

echo.
echo ============================================
echo Exportando Base de Datos PostgreSQL
echo ============================================
echo.

REM Configuración (ajusta si es necesario)
set HOST=localhost
set PORT=5501
set USER=postgres
set DATABASE=class_vision
set OUTPUT_FILE=class_vision_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sql
set OUTPUT_FILE=%OUTPUT_FILE: =0%

echo Configuracion:
echo   Host: %HOST%
echo   Puerto: %PORT%
echo   Usuario: %USER%
echo   Base de Datos: %DATABASE%
echo   Archivo de salida: %OUTPUT_FILE%
echo.

REM Verificar que pg_dump esté disponible
where pg_dump >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pg_dump no esta disponible
    echo.
    echo Solucion:
    echo 1. Asegurate de que PostgreSQL este instalado
    echo 2. Agrega PostgreSQL\bin a tu PATH
    echo    Ejemplo: C:\Program Files\PostgreSQL\14\bin
    echo.
    pause
    exit /b 1
)

echo Ingresa la contraseña de PostgreSQL cuando se solicite...
echo.

REM Ejecutar pg_dump
pg_dump -h %HOST% -p %PORT% -U %USER% -d %DATABASE% -f %OUTPUT_FILE% -F p -v

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo Exportacion completada exitosamente!
    echo ============================================
    echo.
    echo Archivo creado: %OUTPUT_FILE%
    echo.
    echo Proximos pasos:
    echo 1. Copiar el archivo al servidor:
    echo    scp %OUTPUT_FILE% itzan@192.168.30.20:/tmp/
    echo.
    echo 2. En el servidor, importar:
    echo    sudo -u postgres psql -d class_vision -f /tmp/%OUTPUT_FILE%
    echo.
) else (
    echo.
    echo ============================================
    echo ERROR al exportar base de datos
    echo ============================================
    echo.
    echo Verifica:
    echo 1. Que PostgreSQL este corriendo
    echo 2. Que el usuario y contraseña sean correctos
    echo 3. Que la base de datos 'class_vision' exista
    echo 4. Que tengas permisos para acceder a la base de datos
    echo.
)

pause

