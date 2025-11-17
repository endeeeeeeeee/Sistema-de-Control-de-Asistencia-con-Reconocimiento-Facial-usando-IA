@echo off
REM ============================================
REM CLASS VISION - Script de Instalación
REM Windows Batch
REM ============================================

echo ========================================
echo   CLASS VISION - Instalacion Automatica
echo ========================================
echo.

REM Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Por favor instala Python 3.8 o superior.
    echo         Descarga desde: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python encontrado

REM Crear entorno virtual
echo.
echo [2/6] Creando entorno virtual...
if exist .venv (
    echo   Entorno virtual ya existe. Eliminando...
    rmdir /s /q .venv
)
python -m venv .venv
echo [OK] Entorno virtual creado

REM Activar entorno virtual
echo.
echo [3/6] Activando entorno virtual...
call .venv\Scripts\activate.bat
echo [OK] Entorno virtual activado

REM Actualizar pip
echo.
echo [4/6] Actualizando pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip actualizado

REM Instalar dependencias
echo.
echo [5/6] Instalando dependencias...
echo   Esto puede tardar varios minutos...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Error al instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

REM Crear directorios
echo.
echo [6/6] Creando estructura de directorios...
if not exist TrainingImage mkdir TrainingImage
if not exist TrainingImageLabel mkdir TrainingImageLabel
if not exist StudentDetails mkdir StudentDetails
if not exist Attendance mkdir Attendance
if not exist UI_Image mkdir UI_Image
if not exist logs mkdir logs
if not exist config mkdir config
echo [OK] Directorios creados

REM Crear configuración local
if not exist config\local_config.json (
    if exist config\default_config.json (
        copy config\default_config.json config\local_config.json >nul
        echo [OK] Creado: config\local_config.json
    )
)

echo.
echo ========================================
echo   Instalacion Completada
echo ========================================
echo.
echo Para ejecutar CLASS VISION:
echo   1. Activa el entorno virtual:
echo      .venv\Scripts\activate.bat
echo.
echo   2. Ejecuta la aplicacion:
echo      python attendance.py
echo.
pause
