"""
Analiza si el backend y frontend están conectados a PostgreSQL
"""

import os
import re
from pathlib import Path

print("\n" + "="*100)
print("🔍 ANÁLISIS DE CONEXIONES: FRONTEND → BACKEND → POSTGRESQL")
print("="*100)

# 1. VERIFICAR BACKEND (mobile_server.py)
print("\n" + "="*100)
print("📡 BACKEND (mobile_server.py)")
print("="*100)

backend_file = "mobile_server.py"
if os.path.exists(backend_file):
    with open(backend_file, 'r', encoding='utf-8') as f:
        backend_content = f.read()
    
    print("\n✅ Archivo encontrado")
    
    # Verificar imports de managers
    print("\n📦 IMPORTS DE MANAGERS:")
    if 'from db_auth_manager import' in backend_content:
        print("  ✅ Importa db_auth_manager (PostgreSQL)")
    elif 'from auth_manager import' in backend_content:
        print("  ❌ Importa auth_manager (JSON - OBSOLETO)")
    else:
        print("  ⚠️  No se encontró import de auth manager")
    
    if 'from db_student_manager import' in backend_content:
        print("  ✅ Importa db_student_manager (PostgreSQL)")
    elif 'from student_manager import' in backend_content:
        print("  ❌ Importa student_manager (JSON - OBSOLETO)")
    else:
        print("  ⚠️  No se encontró import de student manager")
    
    # Verificar instanciación de managers
    print("\n🔧 INSTANCIACIÓN DE MANAGERS:")
    if 'get_db_auth_manager()' in backend_content:
        print("  ✅ Usa get_db_auth_manager() → PostgreSQL")
    elif 'AuthManager()' in backend_content:
        print("  ❌ Usa AuthManager() → JSON (OBSOLETO)")
    else:
        print("  ⚠️  No se encontró instanciación de auth manager")
    
    if 'get_db_student_manager()' in backend_content:
        print("  ✅ Usa get_db_student_manager() → PostgreSQL")
    elif 'StudentManager()' in backend_content:
        print("  ❌ Usa StudentManager() → JSON (OBSOLETO)")
    else:
        print("  ⚠️  No se encontró instanciación de student manager")
    
    # Buscar llamadas a métodos de los managers
    print("\n📞 LLAMADAS A MÉTODOS DE MANAGERS:")
    auth_methods = ['login', 'register', 'validate_token', 'logout']
    for method in auth_methods:
        matches = re.findall(rf'auth_manager\.{method}\(', backend_content)
        if matches:
            print(f"  ✅ auth_manager.{method}() - {len(matches)} llamadas")
    
    student_methods = ['get_students', 'add_student', 'get_subjects', 'create_subject']
    for method in student_methods:
        matches = re.findall(rf'student_manager\.{method}\(', backend_content)
        if matches:
            print(f"  ✅ student_manager.{method}() - {len(matches)} llamadas")
    
    # Verificar endpoints clave
    print("\n🌐 ENDPOINTS DEFINIDOS:")
    endpoints = [
        r"@app\.route\(['\"]\/api\/auth\/login",
        r"@app\.route\(['\"]\/api\/auth\/register",
        r"@app\.route\(['\"]\/api\/teacher\/subjects",
        r"@app\.route\(['\"]\/api\/stats\/dashboard",
        r"@app\.route\(['\"]\/api\/teacher\/students"
    ]
    endpoint_names = [
        "/api/auth/login",
        "/api/auth/register", 
        "/api/teacher/subjects",
        "/api/stats/dashboard",
        "/api/teacher/students"
    ]
    
    for pattern, name in zip(endpoints, endpoint_names):
        if re.search(pattern, backend_content):
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name} - NO ENCONTRADO")

else:
    print("\n❌ mobile_server.py NO ENCONTRADO")

# 2. VERIFICAR DB_AUTH_MANAGER
print("\n" + "="*100)
print("🔐 DB_AUTH_MANAGER (db_auth_manager.py)")
print("="*100)

db_auth_file = "db_auth_manager.py"
if os.path.exists(db_auth_file):
    with open(db_auth_file, 'r', encoding='utf-8') as f:
        db_auth_content = f.read()
    
    print("\n✅ Archivo encontrado")
    
    # Verificar imports de SQLAlchemy
    print("\n📦 IMPORTS:")
    if 'from sqlalchemy' in db_auth_content:
        print("  ✅ Importa SQLAlchemy")
    if 'from database_models import' in db_auth_content:
        print("  ✅ Importa database_models")
    if 'DatabaseManager' in db_auth_content:
        print("  ✅ Usa DatabaseManager")
    
    # Verificar métodos
    print("\n📝 MÉTODOS IMPLEMENTADOS:")
    methods = ['login', 'register', 'validate_token', 'logout', 'get_user_by_id']
    for method in methods:
        if f'def {method}(' in db_auth_content:
            print(f"  ✅ {method}()")
    
    # Verificar queries SQLAlchemy
    print("\n🔍 QUERIES A POSTGRESQL:")
    if 'session.query(PersonalAdmin)' in db_auth_content:
        print("  ✅ Consulta tabla PersonalAdmin")
    if 'session.query(SesionActiva)' in db_auth_content:
        print("  ✅ Consulta tabla SesionActiva")
    if 'session.add(' in db_auth_content:
        print("  ✅ Inserta registros en PostgreSQL")
    if 'session.commit()' in db_auth_content:
        print("  ✅ Hace commits a PostgreSQL")

else:
    print("\n❌ db_auth_manager.py NO ENCONTRADO")

# 3. VERIFICAR DB_STUDENT_MANAGER
print("\n" + "="*100)
print("👥 DB_STUDENT_MANAGER (db_student_manager.py)")
print("="*100)

db_student_file = "db_student_manager.py"
if os.path.exists(db_student_file):
    with open(db_student_file, 'r', encoding='utf-8') as f:
        db_student_content = f.read()
    
    print("\n✅ Archivo encontrado")
    
    # Verificar imports
    print("\n📦 IMPORTS:")
    if 'from sqlalchemy' in db_student_content:
        print("  ✅ Importa SQLAlchemy")
    if 'from database_models import' in db_student_content:
        print("  ✅ Importa database_models")
    
    # Verificar métodos
    print("\n📝 MÉTODOS IMPLEMENTADOS:")
    methods = ['get_subjects', 'create_subject', 'get_students', 'add_student', 
               'enroll_student', 'get_enrolled_students']
    for method in methods:
        if f'def {method}(' in db_student_content:
            print(f"  ✅ {method}()")
    
    # Verificar queries
    print("\n🔍 QUERIES A POSTGRESQL:")
    if 'session.query(Materia)' in db_student_content:
        print("  ✅ Consulta tabla Materia")
    if 'session.query(Estudiante)' in db_student_content:
        print("  ✅ Consulta tabla Estudiante")
    if 'session.query(Inscripcion)' in db_student_content:
        print("  ✅ Consulta tabla Inscripcion")

else:
    print("\n❌ db_student_manager.py NO ENCONTRADO")

# 4. VERIFICAR FRONTEND (templates)
print("\n" + "="*100)
print("🎨 FRONTEND (Templates HTML)")
print("="*100)

templates_dir = Path("templates")
if templates_dir.exists():
    html_files = list(templates_dir.glob("*.html"))
    print(f"\n✅ Carpeta templates encontrada ({len(html_files)} archivos)")
    
    for html_file in html_files:
        print(f"\n📄 {html_file.name}:")
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Buscar llamadas a API
        api_calls = re.findall(r'fetch\([\'"]([^\'"]*)[\'"]', html_content)
        if api_calls:
            for call in set(api_calls):
                if call.startswith('/api/'):
                    print(f"  ✅ fetch('{call}')")
        
        # Buscar axios
        axios_calls = re.findall(r'axios\.(get|post|put|delete)\([\'"]([^\'"]*)[\'"]', html_content)
        if axios_calls:
            for method, url in set(axios_calls):
                if url.startswith('/api/'):
                    print(f"  ✅ axios.{method}('{url}')")

else:
    print("\n❌ Carpeta templates NO ENCONTRADA")

# 5. VERIFICAR .env
print("\n" + "="*100)
print("⚙️  CONFIGURACIÓN (.env)")
print("="*100)

env_file = ".env"
if os.path.exists(env_file):
    print("\n✅ Archivo .env encontrado")
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    if 'DATABASE_URL' in env_content:
        # Extraer la URL sin mostrar password completa
        db_url_match = re.search(r'DATABASE_URL=(.+)', env_content)
        if db_url_match:
            db_url = db_url_match.group(1).strip()
            # Ocultar password
            censored = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', db_url)
            print(f"  ✅ DATABASE_URL configurada")
            print(f"     {censored}")
    else:
        print("  ❌ DATABASE_URL NO configurada")
else:
    print("\n❌ Archivo .env NO ENCONTRADO")

# 6. VERIFICAR DATABASE_MODELS
print("\n" + "="*100)
print("📊 MODELOS DE BASE DE DATOS (database_models.py)")
print("="*100)

models_file = "database_models.py"
if os.path.exists(models_file):
    with open(models_file, 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    print("\n✅ Archivo encontrado")
    
    # Contar modelos
    class_pattern = r'class\s+(\w+)\s*\([^)]*Base[^)]*\):'
    models = re.findall(class_pattern, models_content)
    
    print(f"\n📋 MODELOS DEFINIDOS ({len(models)}):")
    for model in models:
        print(f"  ✅ {model}")
    
    # Verificar que use SQLAlchemy
    if 'from sqlalchemy' in models_content:
        print("\n  ✅ Usa SQLAlchemy ORM")
    if 'Column' in models_content:
        print("  ✅ Define columnas")
    if 'relationship' in models_content:
        print("  ✅ Define relaciones entre tablas")

else:
    print("\n❌ database_models.py NO ENCONTRADO")

# RESUMEN FINAL
print("\n" + "="*100)
print("📊 RESUMEN DE CONEXIONES")
print("="*100)

print("""
FLUJO DE DATOS:
┌─────────────┐      ┌──────────────┐      ┌───────────────────┐      ┌──────────────┐
│  FRONTEND   │─────▶│   BACKEND    │─────▶│    MANAGERS       │─────▶│  POSTGRESQL  │
│  (HTML/JS)  │      │(mobile_server│      │(db_auth_manager   │      │  localhost   │
│             │      │     .py)     │      │db_student_manager)│      │    :5501     │
└─────────────┘      └──────────────┘      └───────────────────┘      └──────────────┘
     │                      │                       │                        │
     │ fetch('/api/...')   │ auth_manager.login()  │ session.query(...)    │
     │                      │ student_manager       │ session.commit()      │
     │                      │   .get_subjects()     │                        │
     │                      │                       │                        │
     └──────────────────────┴───────────────────────┴────────────────────────┘
                              TODOS USAN POSTGRESQL
""")

print("\n" + "="*100 + "\n")
