"""
Test completo del auth_manager
"""
from auth_manager import AuthManager

def test_auth():
    auth = AuthManager()
    
    print("\n=== TEST AUTH MANAGER ===")
    
    # Test 1: Login con usuario en minúsculas
    print("\n1. Login con 'ender' + '111111':")
    user, token = auth.login('ender', '111111')
    if user:
        print(f"✅ SUCCESS: {user}")
        print(f"Token: {token[:20]}...")
    else:
        print("❌ FAILED")
    
    # Test 2: Login con docente
    print("\n2. Login con 'docente' + 'docente123':")
    user, token = auth.login('docente', 'docente123')
    if user:
        print(f"✅ SUCCESS: {user}")
        print(f"Token: {token[:20]}...")
    else:
        print("❌ FAILED")
    
    # Test 3: Login con Ender (mayúscula)
    print("\n3. Login con 'Ender' + '111111':")
    user, token = auth.login('Ender', '111111')
    if user:
        print(f"✅ SUCCESS: {user}")
        print(f"Token: {token[:20]}...")
    else:
        print("❌ FAILED - username es case-sensitive")

if __name__ == '__main__':
    test_auth()
