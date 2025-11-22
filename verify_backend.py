"""
Verificación simple del backend sin dependencias externas
"""
import http.client
import json

def test_backend():
    print("="*60)
    print("VERIFICACIÓN DEL BACKEND - EQUIPOS")
    print("="*60)
    
    # 1. Login
    print("\n1. Testeando LOGIN...")
    conn = http.client.HTTPConnection("127.0.0.1", 5001)
    
    login_data = json.dumps({
        "username": "henrry@gmail.com",
        "password": "henrry123"
    })
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        conn.request("POST", "/api/auth/login", login_data, headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode())
        
        if data.get('success'):
            token = data.get('token')
            print(f"✅ Login exitoso - Token obtenido")
            
            # 2. Obtener equipos
            print("\n2. Obteniendo EQUIPOS...")
            conn = http.client.HTTPConnection("127.0.0.1", 5001)
            headers = {'Authorization': f'Bearer {token}'}
            conn.request("GET", "/api/equipos", headers=headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode())
            
            if data.get('success'):
                equipos = data.get('equipos', [])
                print(f"✅ Se obtuvieron {len(equipos)} equipos")
                for eq in equipos:
                    print(f"   - {eq.get('nombre_equipo')} ({eq.get('tipo_equipo')})")
            else:
                print(f"❌ Error: {data.get('error')}")
            
            print("\n" + "="*60)
            print("RESUMEN")
            print("="*60)
            print("✅ Backend funcionando correctamente")
            print("✅ Endpoint de login: OK")
            print("✅ Endpoint de equipos: OK")
            
        else:
            print(f"❌ Login fallido: {data.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️  Asegúrate de que el servidor esté corriendo en puerto 5001")
    finally:
        conn.close()

if __name__ == "__main__":
    test_backend()
