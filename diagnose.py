"""
Script de diagnóstico de conexión
"""

import sys
import os

print("\n" + "="*70)
print("DIAGNÓSTICO DE CONEXIÓN - CLASS VISION")
print("="*70 + "\n")

# 1. Verificar variables de entorno
print("[1] Variables de entorno:")
print("-" * 70)

from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL: {db_url}")

# 2. Probar conexión con psycopg2
print("\n[2] Probando conexión con psycopg2:")
print("-" * 70)

try:
    import psycopg2
    conn = psycopg2.connect(db_url)
    print("✅ Conexión exitosa con psycopg2")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ PostgreSQL version: {version[0][:50]}...")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Error con psycopg2: {e}")

# 3. Probar con SQLAlchemy
print("\n[3] Probando conexión con SQLAlchemy:")
print("-" * 70)

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    result = session.execute("SELECT 1")
    print("✅ Conexión exitosa con SQLAlchemy")
    
    session.close()
except Exception as e:
    print(f"❌ Error con SQLAlchemy: {e}")

# 4. Probar DatabaseManager
print("\n[4] Probando DatabaseManager:")
print("-" * 70)

try:
    from database_models import DatabaseManager
    
    db = DatabaseManager()
    session = db.get_session()
    
    from database_models import SysConfig
    count = session.query(SysConfig).count()
    
    print(f"✅ DatabaseManager funciona correctamente")
    print(f"✅ Registros en sys_config: {count}")
    
    session.close()
except Exception as e:
    print(f"❌ Error con DatabaseManager: {e}")
    import traceback
    traceback.print_exc()

# 5. Probar auth_manager
print("\n[5] Probando auth_manager:")
print("-" * 70)

try:
    from db_auth_manager import get_db_auth_manager
    
    auth = get_db_auth_manager()
    
    # Intentar login con usuario demo
    user, token = auth.login('docente', 'docente123')
    
    if user:
        print(f"✅ Login exitoso")
        print(f"   Usuario: {user.get('username')}")
        print(f"   Nombre: {user.get('full_name')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Token: {token[:20]}...")
    else:
        print("❌ Login falló - usuario no encontrado o contraseña incorrecta")
        
except Exception as e:
    print(f"❌ Error con auth_manager: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("DIAGNÓSTICO COMPLETADO")
print("="*70 + "\n")
