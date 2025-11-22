"""Ejecutar SQL completo en PostgreSQL"""
import psycopg2
from pathlib import Path

try:
    # Conectar a class_vision
    conn = psycopg2.connect(
        host='localhost',
        port=5501,
        user='postgres',
        password='Comida18',
        database='class_vision'
    )
    
    cursor = conn.cursor()
    
    # Leer SQL
    sql_file = Path('database_complete.sql')
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print("📄 Ejecutando SQL...")
    cursor.execute(sql)
    conn.commit()
    
    print("✅ Tablas creadas exitosamente\n")
    
    # Verificar tablas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print(f"📊 Tablas creadas ({len(tables)}):")
    for table in tables:
        print(f"   ✓ {table[0]}")
    
    # Contar registros iniciales
    print("\n📋 Datos iniciales:")
    cursor.execute("SELECT COUNT(*) FROM personal_admin")
    print(f"   ✓ Usuarios: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM sys_config")
    print(f"   ✓ Configuración: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM badges")
    print(f"   ✓ Badges: {cursor.fetchone()[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ ¡Base de datos lista!")
    print("\n💡 Credenciales:")
    print("   username: admin")
    print("   password: admin123")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
