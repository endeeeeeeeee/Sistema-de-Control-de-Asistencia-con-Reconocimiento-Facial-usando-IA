"""
Test directo del login
"""
from db_auth_manager import get_db_auth_manager

auth = get_db_auth_manager()

print("\n" + "="*60)
print("TEST DE LOGIN DIRECTO")
print("="*60)

# Test 1
print("\n1. Login con 'Ender' y '111111':")
user, token = auth.login('Ender', '111111')
print(f"Resultado: {'✅ SUCCESS' if user else '❌ FAILED'}")
if user:
    print(f"User: {user}")

# Test 2
print("\n2. Login con 'ender' y '111111':")
user, token = auth.login('ender', '111111')
print(f"Resultado: {'✅ SUCCESS' if user else '❌ FAILED'}")
if user:
    print(f"User: {user}")

# Test 3
print("\n3. Login con 'docente' y 'docente123':")
user, token = auth.login('docente', 'docente123')
print(f"Resultado: {'✅ SUCCESS' if user else '❌ FAILED'}")
if user:
    print(f"User: {user}")

print("\n" + "="*60)
