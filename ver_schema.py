"""
Explorador de Schema de Base de Datos PostgreSQL
Muestra la estructura completa de todas las tablas
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Conectar directamente con psycopg2
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("\n" + "="*100)
print("🗄️  SCHEMA COMPLETO DE LA BASE DE DATOS - CLASS VISION")
print("="*100)

# Obtener todas las tablas
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")

tables = cur.fetchall()

print(f"\n📊 Total de tablas: {len(tables)}\n")

# Para cada tabla, mostrar sus columnas
for (table_name,) in tables:
    print("="*100)
    print(f"📋 TABLA: {table_name}")
    print("="*100)
    
    # Obtener columnas
    cur.execute("""
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = cur.fetchall()
    
    print(f"\n  Columnas ({len(columns)}):")
    print("  " + "-"*96)
    print(f"  {'Columna':<30} {'Tipo':<25} {'NULL':<8} {'Default':<30}")
    print("  " + "-"*96)
    
    for col_name, data_type, max_length, nullable, default in columns:
        type_str = data_type
        if max_length:
            type_str = f"{data_type}({max_length})"
        
        null_str = "✅ Sí" if nullable == 'YES' else "❌ No"
        default_str = str(default)[:28] if default else "-"
        
        print(f"  {col_name:<30} {type_str:<25} {null_str:<8} {default_str:<30}")
    
    # Obtener constraints (primary keys, foreign keys)
    cur.execute("""
        SELECT
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        LEFT JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.table_name = %s
    """, (table_name,))
    
    constraints = cur.fetchall()
    
    if constraints:
        print("\n  Constraints:")
        print("  " + "-"*96)
        for constraint_type, column_name, foreign_table, foreign_column in constraints:
            if constraint_type == 'PRIMARY KEY':
                print(f"  🔑 PRIMARY KEY: {column_name}")
            elif constraint_type == 'FOREIGN KEY':
                print(f"  🔗 FOREIGN KEY: {column_name} → {foreign_table}.{foreign_column}")
            elif constraint_type == 'UNIQUE':
                print(f"  ⭐ UNIQUE: {column_name}")
    
    # Contar registros
    cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    count = cur.fetchone()[0]
    print(f"\n  📊 Registros: {count}")
    print()

# Resumen
print("\n" + "="*100)
print("📋 RESUMEN DE TABLAS")
print("="*100)

for (table_name,) in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    count = cur.fetchone()[0]
    print(f"  {table_name:<40} {count:>10} registros")

print("\n" + "="*100 + "\n")

cur.close()
conn.close()
