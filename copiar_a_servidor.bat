@echo off
REM Script para copiar el proyecto al servidor Ubuntu
REM Ajusta los valores según tu configuración

REM ============================================
REM CONFIGURACIÓN - EDITA ESTOS VALORES
REM ============================================
set USUARIO_SERVIDOR=itzan
set IP_SERVIDOR=192.168.30.20
set RUTA_DESTINO=/srv/miempresa/app1_tienda/codigo

REM Ruta del proyecto (ajusta si es necesario)
set RUTA_PROYECTO=C:\Users\HP\git\Sistema de Control de Asistencia con Reconocimiento Facial usando IA

REM ============================================
REM OPCIÓN 1: Usar SCP (requiere OpenSSH en Windows)
REM ============================================
echo.
echo ============================================
echo Copiando proyecto al servidor...
echo ============================================
echo.
echo Usuario: %USUARIO_SERVIDOR%
echo Servidor: %IP_SERVIDOR%
echo Destino: %RUTA_DESTINO%
echo.
echo Esto puede tardar varios minutos...
echo.

scp -r "%RUTA_PROYECTO" %USUARIO_SERVIDOR@%IP_SERVIDOR%:%RUTA_DESTINO%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo ¡Copia completada exitosamente!
    echo ============================================
) else (
    echo.
    echo ============================================
    echo ERROR: La copia falló
    echo ============================================
    echo.
    echo Posibles soluciones:
    echo 1. Verifica que OpenSSH esté instalado en Windows
    echo 2. Verifica la conexión SSH al servidor
    echo 3. Verifica que la ruta de destino exista en el servidor
    echo 4. Verifica tus credenciales
    echo.
    echo Si SCP no funciona, usa una de las opciones alternativas:
    echo - WinSCP (interfaz gráfica)
    echo - Git Bash
    echo - WSL (Windows Subsystem for Linux)
)

pause

