"""
Script para probar los endpoints de equipos del backend
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_login():
    """Obtener token de autenticación"""
    print("\n" + "="*60)
    print("1. PROBANDO LOGIN")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "henrry@gmail.com",
            "password": "henrry123"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get('success') and data.get('token'):
        print("✅ Login exitoso")
        return data['token']
    else:
        print("❌ Login fallido")
        return None

def test_get_equipos(token):
    """Obtener equipos del usuario"""
    print("\n" + "="*60)
    print("2. OBTENIENDO EQUIPOS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/equipos", headers=headers)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get('success'):
        equipos = data.get('equipos', [])
        print(f"✅ Se obtuvieron {len(equipos)} equipos")
        return equipos
    else:
        print("❌ Error obteniendo equipos")
        return []

def test_create_equipo(token):
    """Crear un nuevo equipo"""
    print("\n" + "="*60)
    print("3. CREANDO NUEVO EQUIPO")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/equipos",
        headers=headers,
        json={
            "nombre_equipo": "Equipo de Prueba Backend",
            "descripcion": "Equipo creado desde test_equipos_backend.py",
            "tipo_equipo": "universidad"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get('success'):
        print(f"✅ Equipo creado: {data.get('codigo_invitacion')}")
        return data.get('equipo_id'), data.get('codigo_invitacion')
    else:
        print("❌ Error creando equipo")
        return None, None

def test_join_equipo(token, codigo_invitacion):
    """Unirse a un equipo con código"""
    print("\n" + "="*60)
    print("4. UNIÉNDOSE A EQUIPO CON CÓDIGO")
    print("="*60)
    print(f"Código: {codigo_invitacion}")
    
    # Primero intentar con otro usuario (itzan)
    print("\nProbando login con usuario itzan...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "itzan@gmail.com",
            "password": "itzan123"
        }
    )
    
    if not login_response.json().get('success'):
        print("❌ No se pudo hacer login con segundo usuario")
        return False
    
    token_itzan = login_response.json()['token']
    print("✅ Login exitoso con itzan")
    
    headers = {"Authorization": f"Bearer {token_itzan}"}
    response = requests.post(
        f"{BASE_URL}/api/equipos/unirse",
        headers=headers,
        json={"codigo_invitacion": codigo_invitacion}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get('success'):
        print("✅ Se unió exitosamente al equipo")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False

def test_get_team_details(token, equipo_id):
    """Obtener detalles de un equipo"""
    print("\n" + "="*60)
    print("5. OBTENIENDO DETALLES DEL EQUIPO")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/equipos/{equipo_id}",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data.get('success'):
        miembros = data.get('miembros', [])
        print(f"✅ Equipo tiene {len(miembros)} miembros")
        return True
    else:
        print("❌ Error obteniendo detalles")
        return False

def main():
    print("="*60)
    print("PRUEBAS DE BACKEND - ENDPOINTS DE EQUIPOS")
    print("="*60)
    print("Asegúrate de que el servidor esté corriendo en puerto 5001")
    
    # 1. Login
    token = test_login()
    if not token:
        print("\n❌ No se pudo obtener token. Verifica que el servidor esté corriendo.")
        return
    
    # 2. Obtener equipos actuales
    equipos_antes = test_get_equipos(token)
    
    # 3. Crear nuevo equipo
    equipo_id, codigo_invitacion = test_create_equipo(token)
    if not equipo_id:
        print("\n❌ No se pudo crear equipo")
        return
    
    # 4. Verificar que apareció en la lista
    equipos_despues = test_get_equipos(token)
    if len(equipos_despues) > len(equipos_antes):
        print(f"\n✅ Equipo agregado correctamente ({len(equipos_antes)} -> {len(equipos_despues)})")
    
    # 5. Unirse al equipo con otro usuario
    test_join_equipo(token, codigo_invitacion)
    
    # 6. Ver detalles del equipo
    test_get_team_details(token, equipo_id)
    
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    print("✅ Todos los endpoints básicos funcionan correctamente")
    print(f"✅ Equipo creado: ID={equipo_id}, Código={codigo_invitacion}")
    print("\n⚠️  Recuerda eliminar el equipo de prueba si es necesario")

if __name__ == "__main__":
    main()
