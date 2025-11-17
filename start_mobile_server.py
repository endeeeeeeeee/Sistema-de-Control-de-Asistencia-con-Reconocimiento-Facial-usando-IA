"""
Launcher para Servidor Móvil - CLASS VISION
Universidad Nur
Ejecuta el servidor y muestra el código QR para acceso rápido
"""

import subprocess
import sys
import time
import socket
from pathlib import Path
import webbrowser
import threading

def get_local_ip():
    """Obtiene la IP local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def print_banner():
    """Imprime banner de inicio"""
    ip = get_local_ip()
    port = 5000
    
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🎓 UNIVERSIDAD NUR                              ║
║              CLASS VISION - Control Móvil                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📱 ACCESO DESDE SMARTPHONE:

   1. Conecta tu teléfono a la misma red WiFi que este PC
   
   2. Abre el navegador de tu teléfono y ve a:
      
      ➡️  http://{ip}:{port}
      
   3. O escanea el código QR que aparecerá en tu navegador

📊 PANEL DE CONTROL:

   - Navegador local: http://localhost:{port}
   - Red local: http://{ip}:{port}

⚙️  INSTRUCCIONES:

   • El servidor debe permanecer corriendo en este PC
   • Tu teléfono y este PC deben estar en la misma red
   • Usa el QR code para acceso rápido desde el móvil

═══════════════════════════════════════════════════════════════

🚀 Iniciando servidor...

"""
    print(banner)

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    try:
        import flask
        import qrcode
        print("✅ Dependencias verificadas")
        return True
    except ImportError as e:
        print(f"❌ Error: Falta instalar dependencias")
        print(f"\nEjecuta: pip install flask flask-cors qrcode[pil]")
        return False

def open_qr_browser():
    """Abre el navegador con el QR code después de 2 segundos"""
    time.sleep(3)
    ip = get_local_ip()
    webbrowser.open(f"http://{ip}:5000/api/qr")
    webbrowser.open(f"http://{ip}:5000")

def main():
    print_banner()
    
    # Verificar dependencias
    if not check_dependencies():
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    # Abrir QR en navegador en background
    browser_thread = threading.Thread(target=open_qr_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Ejecutar servidor
    try:
        subprocess.run([sys.executable, "mobile_server.py"])
    except KeyboardInterrupt:
        print("\n\n⏹️  Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}")
        input("\nPresiona Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main()
