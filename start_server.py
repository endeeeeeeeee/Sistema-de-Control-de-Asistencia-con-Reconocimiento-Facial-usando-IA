"""
Iniciar Servidor CLASS VISION
Sistema Flexible de Asistencia con Equipos
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_database():
    """Verificar conexión a la base de datos antes de iniciar"""
    print("🔍 Verificando conexión a la base de datos...")
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import OperationalError
        
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 5,
                "options": "-c statement_timeout=5000"
            }
        )
        
        # Intentar una conexión simple
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ Conexión a la base de datos exitosa\n")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        print("\n⚠️  El servidor puede iniciarse pero algunas funciones pueden no funcionar.")
        print("   Verifica que PostgreSQL esté corriendo y que DATABASE_URL sea correcta.\n")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print(" CLASS VISION - Sistema de Asistencia Flexible")
    print("=" * 60)
    print()
    
    # Verificar base de datos
    db_ok = check_database()
    
    print("Iniciando servidor...")
    print()
    print("Credenciales de prueba:")
    print("   Email: admin@classvision.com")
    print("   Password: admin123")
    print()
    print("URLs disponibles:")
    print("   - Login: http://localhost:5000/login")
    print("   - Registro: http://localhost:5000/registro")
    print("   - Dashboard: http://localhost:5000/dashboard")
    print()
    print("=" * 60)
    print()
    
    try:
        from mobile_server import app
        
        # Obtener configuración de variables de entorno
        debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        server_port = int(os.getenv('SERVER_PORT', '5000'))
        server_host = os.getenv('SERVER_HOST', '0.0.0.0')
        
        # Advertencia si debug está activado
        if debug_mode:
            print("⚠️  ADVERTENCIA: MODO DEBUG ACTIVADO")
            print("   Esto NO debe usarse en producción por razones de seguridad")
            print()
        else:
            print("✅ MODO PRODUCCIÓN (debug desactivado)")
            print()
        
        print(f"🚀 Servidor iniciado en http://{server_host}:{server_port}")
        print("   Presiona Ctrl+C para detener\n")
        app.run(
            host=server_host, 
            port=server_port, 
            debug=debug_mode, 
            threaded=True, 
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n✅ Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
