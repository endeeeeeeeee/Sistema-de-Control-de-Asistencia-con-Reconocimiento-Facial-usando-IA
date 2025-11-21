"""
CLASS VISION - Setup Database
==============================

Script para configurar la base de datos PostgreSQL local.
Crea la base de datos, tablas e inserta datos iniciales.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from pathlib import Path

def create_database():
    """Crea la base de datos class_vision si no existe"""
    
    print("🔌 Conectando a PostgreSQL...")
    
    # Configuración de conexión (ajusta según tu instalación)
    config = {
        'host': 'localhost',
        'port': 5501,  # Tu puerto según la imagen
        'user': 'postgres',
        'password': input("🔐 Ingresa la contraseña de PostgreSQL: ")
    }
    
    try:
        # Conectar a PostgreSQL (base de datos por defecto)
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'class_vision'")
        exists = cursor.fetchone()
        
        if exists:
            print("⚠️  La base de datos 'class_vision' ya existe.")
            response = input("   ¿Deseas eliminarla y recrearla? (si/no): ")
            if response.lower() in ['si', 'sí', 's', 'y', 'yes']:
                print("🗑️  Eliminando base de datos existente...")
                cursor.execute("DROP DATABASE class_vision")
                print("   ✓ Base de datos eliminada")
            else:
                print("✅ Usando base de datos existente")
                cursor.close()
                conn.close()
                return config['password']
        
        # Crear nueva base de datos (usando template0 para evitar error de encoding)
        print("🏗️  Creando base de datos 'class_vision'...")
        cursor.execute("CREATE DATABASE class_vision ENCODING 'UTF8' TEMPLATE template0")
        print("   ✓ Base de datos creada exitosamente")
        
        cursor.close()
        conn.close()
        
        return config['password']
        
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def execute_sql_file(password):
    """Ejecuta el archivo SQL para crear las tablas"""
    
    print("\n📄 Ejecutando script SQL...")
    
    sql_file = Path(__file__).parent / 'database_complete.sql'
    
    if not sql_file.exists():
        print(f"❌ Archivo no encontrado: {sql_file}")
        sys.exit(1)
    
    try:
        # Conectar a la base de datos class_vision
        conn = psycopg2.connect(
            host='localhost',
            port=5501,
            user='postgres',
            password=password,
            database='class_vision'
        )
        
        cursor = conn.cursor()
        
        # Leer y ejecutar SQL
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("   Ejecutando comandos SQL...")
        cursor.execute(sql_content)
        conn.commit()
        
        print("   ✓ Tablas creadas exitosamente")
        
        # Verificar tablas creadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 Tablas creadas ({len(tables)}):")
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error ejecutando SQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_connection(password):
    """Prueba la conexión y muestra información de la base de datos"""
    
    print("\n🧪 Probando conexión...")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5501,
            user='postgres',
            password=password,
            database='class_vision'
        )
        
        cursor = conn.cursor()
        
        # Obtener versión de PostgreSQL
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"   ✓ PostgreSQL: {version.split(',')[0]}")
        
        # Contar registros iniciales
        cursor.execute("SELECT COUNT(*) FROM sys_config")
        config_count = cursor.fetchone()[0]
        print(f"   ✓ Configuración del sistema: {config_count} registro(s)")
        
        cursor.execute("SELECT COUNT(*) FROM personal_admin")
        admin_count = cursor.fetchone()[0]
        print(f"   ✓ Usuarios admin: {admin_count} registro(s)")
        
        cursor.execute("SELECT COUNT(*) FROM badges")
        badges_count = cursor.fetchone()[0]
        print(f"   ✓ Badges: {badges_count} registro(s)")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error de conexión: {e}")
        return False

def create_env_file(password):
    """Crea archivo .env con configuración de base de datos"""
    
    env_content = f"""# CLASS VISION - Database Configuration
# ========================================

# PostgreSQL Local
DATABASE_URL=postgresql://postgres:{password}@localhost:5501/class_vision

# Para producción (Render), actualizar con:
# DATABASE_URL=postgresql://user:password@host:port/database

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=tu_clave_secreta_aqui_cambiar_en_produccion

# Server Configuration
HOST=0.0.0.0
PORT=5000
"""
    
    env_file = Path(__file__).parent / '.env'
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n📝 Archivo .env creado: {env_file}")
    print("   ⚠️  IMPORTANTE: No subir este archivo a GitHub (ya está en .gitignore)")

def main():
    """Función principal"""
    
    print("="*70)
    print("🚀 CLASS VISION - Configuración de Base de Datos")
    print("="*70)
    print()
    
    # Paso 1: Crear base de datos
    password = create_database()
    
    # Paso 2: Ejecutar SQL
    if not execute_sql_file(password):
        print("\n❌ Falló la creación de tablas")
        sys.exit(1)
    
    # Paso 3: Probar conexión
    if not test_connection(password):
        print("\n❌ Falló la prueba de conexión")
        sys.exit(1)
    
    # Paso 4: Crear archivo .env
    create_env_file(password)
    
    # Resumen final
    print("\n" + "="*70)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*70)
    print()
    print("📋 Próximos pasos:")
    print("   1. Ejecutar migración de datos:")
    print("      python migrate_to_postgresql.py")
    print()
    print("   2. Actualizar mobile_server.py para usar PostgreSQL")
    print()
    print("   3. Probar el sistema:")
    print("      python mobile_server.py")
    print()
    print("💡 Credenciales de acceso:")
    print("   Username: admin")
    print("   Password: admin123")
    print()
    print("🌐 URL: http://localhost:5000")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
