"""
Script de testing rápido para verificar el backend
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
token = None

def print_test(name, success):
    """Imprime resultado de test"""
    status = "✅" if success else "❌"
    print(f"{status} {name}")

def test_login():
    """Test de login"""
    global token
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                'username': 'docente',
                'password': 'docente123'
            }
        )
        
        data = response.json()
        if data.get('success') and data.get('token'):
            token = data['token']
            print_test("Login", True)
            return True
        else:
            print_test("Login", False)
            print(f"  Error: {data.get('error', 'Unknown')}")
            return False
    except Exception as e:
        print_test("Login", False)
        print(f"  Exception: {e}")
        return False

def test_get_config():
    """Test de obtener configuración"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/config",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        data = response.json()
        if data.get('success'):
            print_test("GET /api/config", True)
            print(f"  Institución: {data.get('nombre_institucion')}")
            print(f"  Modo: {data.get('modo_operacion')}")
            return True
        else:
            print_test("GET /api/config", False)
            return False
    except Exception as e:
        print_test("GET /api/config", False)
        print(f"  Exception: {e}")
        return False

def test_get_subjects():
    """Test de obtener materias"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/teacher/subjects",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        data = response.json()
        if data.get('success'):
            subjects = data.get('subjects', [])
            print_test("GET /api/teacher/subjects", True)
            print(f"  Materias encontradas: {len(subjects)}")
            return True
        else:
            print_test("GET /api/teacher/subjects", False)
            return False
    except Exception as e:
        print_test("GET /api/teacher/subjects", False)
        print(f"  Exception: {e}")
        return False

def test_get_students():
    """Test de obtener estudiantes"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/students",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        data = response.json()
        if data.get('success'):
            students = data.get('students', [])
            print_test("GET /api/students", True)
            print(f"  Estudiantes encontrados: {len(students)}")
            return True
        else:
            print_test("GET /api/students", False)
            return False
    except Exception as e:
        print_test("GET /api/students", False)
        print(f"  Exception: {e}")
        return False

def test_dashboard_stats():
    """Test de estadísticas del dashboard"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/stats/dashboard",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        data = response.json()
        if data.get('success'):
            print_test("GET /api/stats/dashboard", True)
            print(f"  Materias: {data.get('total_materias', 0)}")
            print(f"  Estudiantes: {data.get('total_estudiantes', 0)}")
            print(f"  Asistencias hoy: {data.get('asistencias_hoy', 0)}")
            print(f"  Porcentaje: {data.get('porcentaje_asistencia', 0)}%")
            return True
        else:
            print_test("GET /api/stats/dashboard", False)
            return False
    except Exception as e:
        print_test("GET /api/stats/dashboard", False)
        print(f"  Exception: {e}")
        return False

def test_active_codes():
    """Test de códigos activos"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/codes/active",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        data = response.json()
        if data.get('success'):
            codes = data.get('codes', [])
            print_test("GET /api/codes/active", True)
            print(f"  Códigos activos: {len(codes)}")
            return True
        else:
            print_test("GET /api/codes/active", False)
            return False
    except Exception as e:
        print_test("GET /api/codes/active", False)
        print(f"  Exception: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    
    print("\n" + "="*60)
    print("TEST SUITE - CLASS VISION BACKEND")
    print("="*60 + "\n")
    
    print("NOTA: Asegúrate de que:")
    print("1. El servidor está corriendo: python mobile_server.py")
    print("2. La base de datos está inicializada: python init_data.py")
    print("3. Existe el usuario 'docente' con password 'docente123'\n")
    
    input("Presiona ENTER para continuar...")
    print()
    
    # Test de autenticación
    print("\n📋 TESTS DE AUTENTICACIÓN")
    print("-" * 60)
    if not test_login():
        print("\n❌ Login falló. No se pueden ejecutar más tests.")
        return
    
    # Tests de endpoints
    print("\n📋 TESTS DE ENDPOINTS")
    print("-" * 60)
    test_get_config()
    test_get_subjects()
    test_get_students()
    test_dashboard_stats()
    test_active_codes()
    
    print("\n" + "="*60)
    print("TESTS COMPLETADOS")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
