@echo off
title CLASS VISION - Servidor Móvil Universidad Nur
color 0A

echo.
echo ============================================================
echo            UNIVERSIDAD NUR - CLASS VISION
echo            Servidor de Control Móvil
echo ============================================================
echo.
echo Instalando dependencias necesarias...
echo.

pip install flask flask-cors qrcode[pil] pillow

echo.
echo ============================================================
echo Iniciando servidor móvil...
echo ============================================================
echo.

python start_mobile_server.py

pause
