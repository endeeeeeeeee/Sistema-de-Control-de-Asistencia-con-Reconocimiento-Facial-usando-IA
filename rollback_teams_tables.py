"""
Eliminar las tablas de equipos creadas incorrectamente
y volver al schema original
"""
import psycopg2

def rollback_tables():
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            dbname="class_vision",
            user="postgres",
            password="ithan123",
            host="localhost",
            port="5501"
        )
        cursor = conn.cursor()
        
        print("=" * 60)
        print("ELIMINANDO TABLAS INCORRECTAS")
        print("=" * 60)
        
        # Eliminar las tablas creadas incorrectamente
        cursor.execute("DROP TABLE IF EXISTS miembros_equipo CASCADE")
        print("✅ Tabla miembros_equipo eliminada")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("ROLLBACK COMPLETADO")
        print("=" * 60)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    rollback_tables()
