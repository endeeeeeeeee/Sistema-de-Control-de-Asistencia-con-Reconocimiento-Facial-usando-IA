import sys
from auth_manager_flexible import AuthManager

auth = AuthManager()

print("\n" + "="*60)
print("PRUEBA DE LOGIN DIRECTO")
print("="*60)

# Test 1: Login con email de Itzan
print("\n1. Probando login con email de Itzan...")
print(f"   Email: itzan.mateo@gmail.com")
print(f"   Password: itzan123")

user, token = auth.login('itzan.mateo@gmail.com', 'itzan123')

if user:
    print(f"   ✅ LOGIN EXITOSO")
    print(f"   User: {user}")
    print(f"   Token: {token[:20]}...")
else:
    print(f"   ❌ LOGIN FALLIDO")
    print(f"   User: {user}")
    print(f"   Token: {token}")

# Test 2: Login con código de usuario
print("\n2. Probando login con código de usuario...")
print(f"   Código: USER-2025-002")
print(f"   Password: itzan123")

user2, token2 = auth.login('USER-2025-002', 'itzan123')

if user2:
    print(f"   ✅ LOGIN EXITOSO")
    print(f"   User: {user2}")
    print(f"   Token: {token2[:20]}...")
else:
    print(f"   ❌ LOGIN FALLIDO")
    print(f"   User: {user2}")
    print(f"   Token: {token2}")

# Test 3: Login con admin
print("\n3. Probando login con admin...")
print(f"   Email: admin@classvision.com")
print(f"   Password: admin123")

user3, token3 = auth.login('admin@classvision.com', 'admin123')

if user3:
    print(f"   ✅ LOGIN EXITOSO")
    print(f"   User: {user3}")
    print(f"   Token: {token3[:20]}...")
else:
    print(f"   ❌ LOGIN FALLIDO")
    print(f"   User: {user3}")
    print(f"   Token: {token3}")

print("\n" + "="*60)
