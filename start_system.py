"""
Script de inicio rápido - CLASS VISION
Verifica dependencias, inicializa base de datos y arranca el servidor
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(text):
    """Imprime encabezado decorado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_step(number, text):
    """Imprime paso numerado"""
    print(f"\n[{number}] {text}")
    print("-" * 70)

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"✅ {text}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"❌ {text}")

def print_warning(text):
    """Imprime advertencia"""
    print(f"⚠️  {text}")

def check_python_version():
    """Verificar versión de Python"""
    print_step(1, "Verificando Python")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Se requiere Python 3.8 o superior")
        return False
    
    print_success("Versión de Python correcta")
    return True

def check_venv():
    """Verificar que estamos en un entorno virtual"""
    print_step(2, "Verificando entorno virtual")
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print_success("Entorno virtual activo")
        return True
    else:
        print_warning("No estás en un entorno virtual")
        print("  Recomendación: Activa el entorno virtual primero")
        print("  Comando: .venv\\Scripts\\Activate.ps1")
        
        response = input("\n¿Continuar de todos modos? (s/n): ")
        return response.lower() == 's'

def check_dependencies():
    """Verificar dependencias principales"""
    print_step(3, "Verificando dependencias")
    
    dependencies = [
        'flask',
        'flask_cors',
        'sqlalchemy',
        'psycopg2',
        'pandas',
        'opencv-python',
        'qrcode',
        'requests'
    ]
    
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep}")
            missing.append(dep)
    
    if missing:
        print_error(f"Faltan {len(missing)} dependencias")
        print("\nInstalando dependencias faltantes...")
        
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install'] + missing,
                check=True,
                capture_output=True
            )
            print_success("Dependencias instaladas")
            return True
        except subprocess.CalledProcessError as e:
            print_error("Error instalando dependencias")
            print(f"  {e}")
            return False
    else:
        print_success("Todas las dependencias están instaladas")
        return True

def check_database():
    """Verificar conexión a la base de datos"""
    print_step(4, "Verificando conexión a PostgreSQL")
    
    try:
        from database_models import DatabaseManager
        
        db = DatabaseManager()
        session = db.get_session()
        
        # Intentar una consulta simple
        from database_models import SysConfig
        count = session.query(SysConfig).count()
        
        session.close()
        
        print_success(f"Conexión exitosa (registros en sys_config: {count})")
        return True
        
    except Exception as e:
        print_error("No se pudo conectar a la base de datos")
        print(f"  Error: {e}")
        print("\n  Verificar:")
        print("  1. PostgreSQL está corriendo")
        print("  2. El archivo .env tiene las credenciales correctas")
        print("  3. La base de datos 'class_vision' existe")
        return False

def init_database():
    """Inicializar base de datos con datos por defecto"""
    print_step(5, "Inicializando datos por defecto")
    
    try:
        from database_models import DatabaseManager, SysConfig
        
        db = DatabaseManager()
        session = db.get_session()
        
        # Verificar si ya está inicializada
        config = session.query(SysConfig).first()
        
        if config:
            print_warning("Base de datos ya tiene datos iniciales")
            session.close()
            
            response = input("¿Reinicializar? (s/n): ")
            if response.lower() != 's':
                print("  Omitiendo inicialización")
                return True
        
        session.close()
        
        # Ejecutar script de inicialización
        print("Ejecutando init_data.py...")
        result = subprocess.run(
            [sys.executable, 'init_data.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Datos inicializados correctamente")
            print("\n" + result.stdout)
            return True
        else:
            print_error("Error en la inicialización")
            print(result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def start_server():
    """Iniciar servidor Flask"""
    print_step(6, "Iniciando servidor Flask")
    
    print("\n" + "="*70)
    print("  🚀 SERVIDOR CLASS VISION")
    print("="*70)
    print("\n  URL: http://localhost:5000")
    print("  Página de login: http://localhost:5000/login")
    print("\n  Usuarios demo:")
    print("  - Admin:   username=admin    password=admin123")
    print("  - Docente: username=docente  password=docente123")
    print("\n  Presiona Ctrl+C para detener el servidor")
    print("="*70 + "\n")
    
    try:
        subprocess.run([sys.executable, 'mobile_server.py'])
    except KeyboardInterrupt:
        print("\n\n✅ Servidor detenido")

def main():
    """Función principal"""
    
    print_header("CLASS VISION - INICIO RÁPIDO")
    
    # Verificaciones
    if not check_python_version():
        return
    
    if not check_venv():
        return
    
    if not check_dependencies():
        return
    
    if not check_database():
        print("\n⚠️  No se puede continuar sin conexión a la base de datos")
        return
    
    # Inicialización
    if not init_database():
        print("\n⚠️  Advertencia: Los datos iniciales pueden no estar disponibles")
        response = input("¿Continuar de todos modos? (s/n): ")
        if response.lower() != 's':
            return
    
    # Iniciar servidor
    print_header("LISTO PARA INICIAR")
    response = input("¿Iniciar servidor ahora? (s/n): ")
    
    if response.lower() == 's':
        start_server()
    else:
        print("\n✅ Todo listo. Para iniciar el servidor ejecuta:")
        print("   python mobile_server.py")
        print("\n✅ Para probar los endpoints ejecuta:")
        print("   python test_backend.py")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
