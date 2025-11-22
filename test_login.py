"""
Test rápido de autenticación
"""
import hashlib
from database_models import DatabaseManager

def test_login():
    db_manager = DatabaseManager()
    session = db_manager.get_session()
    
    from database_models import PersonalAdmin
    
    # Ver todos los usuarios
    print("\n=== USUARIOS EN BD ===")
    users = session.query(PersonalAdmin).all()
    for u in users:
        print(f"Username: {u.username}, Full Name: {u.full_name}, Rol: {u.rol}")
        print(f"Password Hash: {u.password_hash[:50]}...")
    
    # Probar hash
    print("\n=== TEST DE HASH ===")
    test_password = "docente123"
    hash_sha256 = hashlib.sha256(test_password.encode()).hexdigest()
    print(f"Password: {test_password}")
    print(f"Hash SHA256: {hash_sha256}")
    
    # Buscar usuario docente
    print("\n=== VERIFICAR DOCENTE ===")
    docente = session.query(PersonalAdmin).filter_by(username='docente').first()
    if docente:
        print(f"Usuario encontrado: {docente.username}")
        print(f"Hash en BD: {docente.password_hash}")
        print(f"Hash calculado: {hash_sha256}")
        print(f"¿Coinciden? {docente.password_hash == hash_sha256}")
    else:
        print("❌ Usuario docente NO encontrado")
    
    # Probar con Ender
    print("\n=== VERIFICAR ENDER ===")
    ender = session.query(PersonalAdmin).filter_by(username='Ender').first()
    if ender:
        print(f"Usuario encontrado: {ender.username}")
        print(f"Password hash: {ender.password_hash[:50]}...")
        
        # Probar diferentes passwords
        for pwd in ['111111', 'Ender', 'ender', '123456']:
            h = hashlib.sha256(pwd.encode()).hexdigest()
            match = h == ender.password_hash
            print(f"  Password '{pwd}': {'✅ MATCH' if match else '❌ no match'}")
    else:
        print("❌ Usuario Ender NO encontrado")
    
    session.close()

if __name__ == '__main__':
    test_login()
