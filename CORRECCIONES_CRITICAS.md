# 🔧 Correcciones Críticas - Guía de Implementación

Este documento contiene las correcciones más críticas identificadas en la evaluación profesional.

## 🔴 PRIORIDAD ALTA: Seguridad de Contraseñas

### Problema
El sistema usa SHA-256 simple sin salt, lo cual es inseguro para producción.

### Solución

#### Paso 1: Actualizar requirements.txt
```bash
# Agregar bcrypt
bcrypt>=4.0.0
```

#### Paso 2: Actualizar auth_manager_flexible.py

**ANTES:**
```python
def hash_password(self, password):
    """Hash de contraseña con SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()
```

**DESPUÉS:**
```python
import bcrypt

def hash_password(self, password: str) -> str:
    """
    Hash seguro de contraseña usando bcrypt
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash bcrypt codificado en string
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(self, password: str, password_hash: str) -> bool:
    """
    Verificar contraseña contra hash
    
    Args:
        password: Contraseña en texto plano
        password_hash: Hash almacenado
        
    Returns:
        True si la contraseña es correcta
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        )
    except Exception:
        return False
```

#### Paso 3: Actualizar método login()

**ANTES:**
```python
def login(self, email, password):
    password_hash = self.hash_password(password)
    # Comparar directamente
```

**DESPUÉS:**
```python
def login(self, email, password):
    # Obtener hash de la BD
    user = self.session.execute(query, {'email': email}).fetchone()
    
    if not user:
        return {'success': False, 'error': 'Email o contraseña incorrectos'}
    
    # Verificar contraseña con bcrypt
    if not self.verify_password(password, user.password_hash):
        return {'success': False, 'error': 'Email o contraseña incorrectos'}
```

#### Paso 4: Script de Migración de Contraseñas

Crear `migrate_passwords.py`:
```python
"""
Script para migrar contraseñas de SHA-256 a bcrypt
EJECUTAR UNA SOLA VEZ después de actualizar el código
"""
from database_models import DatabaseManager, PersonalAdmin
from auth_manager_flexible import AuthManager
import bcrypt

def migrate_passwords():
    """Migrar todas las contraseñas a bcrypt"""
    db = DatabaseManager()
    auth = AuthManager()
    session = db.get_session()
    
    try:
        users = session.query(PersonalAdmin).all()
        print(f"Migrando {len(users)} usuarios...")
        
        for user in users:
            # Si el hash es SHA-256 (64 caracteres hex), necesita migración
            if len(user.password_hash) == 64:
                # Solicitar nueva contraseña o usar temporal
                print(f"Usuario {user.username} necesita nueva contraseña")
                # En producción, forzar cambio de contraseña
                # Por ahora, usar contraseña temporal
                new_password = f"temp_{user.username}_change_me"
                user.password_hash = auth.hash_password(new_password)
                print(f"  ✅ Contraseña temporal asignada")
        
        session.commit()
        print("✅ Migración completada")
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    migrate_passwords()
```

---

## 🔴 PRIORIDAD ALTA: Debug Mode

### Problema
El servidor se ejecuta con `debug=True` en producción.

### Solución

#### Actualizar start_server.py

**ANTES:**
```python
app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)
```

**DESPUÉS:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Solo activar debug en desarrollo
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

if __name__ == '__main__':
    print("=" * 60)
    print(" CLASS VISION - Sistema de Asistencia Flexible")
    print("=" * 60)
    print()
    
    if DEBUG_MODE:
        print("⚠️  MODO DEBUG ACTIVADO (solo para desarrollo)")
    else:
        print("✅ MODO PRODUCCIÓN")
    
    # ... resto del código ...
    
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=DEBUG_MODE,  # Solo True en desarrollo
        threaded=True, 
        use_reloader=False
    )
```

#### Actualizar mobile_server.py

**ANTES:**
```python
def start_server(port=5001, debug=False):
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
```

**DESPUÉS:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

def start_server(port=5001, debug=None):
    """
    Inicia el servidor web
    
    Args:
        port: Puerto del servidor
        debug: Si None, usa variable de entorno FLASK_DEBUG
    """
    if debug is None:
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    if debug:
        print("⚠️  MODO DEBUG ACTIVADO")
    else:
        print("✅ MODO PRODUCCIÓN")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        threaded=True
    )
```

#### Crear .env.example

```env
# Flask Configuration
FLASK_DEBUG=False
FLASK_SECRET_KEY=change-this-to-a-random-secret-key-in-production

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5501/class_vision

# Security
BCRYPT_ROUNDS=12
SESSION_TIMEOUT_HOURS=8

# OpenCV
CAMERA_INDEX=0
```

---

## 🟡 PRIORIDAD MEDIA: Validación de Entrada

### Solución: Usar Marshmallow

#### Paso 1: Agregar a requirements.txt
```
marshmallow>=3.19.0
```

#### Paso 2: Crear validators.py
```python
"""
Validadores para endpoints de API
"""
from marshmallow import Schema, fields, validate, ValidationError

class RegisterSchema(Schema):
    username = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=50),
        error_messages={'required': 'Username es requerido'}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=100),
        error_messages={
            'required': 'Password es requerido',
            'invalid': 'Password debe tener al menos 8 caracteres'
        }
    )
    full_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=200)
    )
    email = fields.Email(
        required=True,
        error_messages={'invalid': 'Email inválido'}
    )

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
```

#### Paso 3: Usar en endpoints
```python
from validators import RegisterSchema, LoginSchema

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        schema = RegisterSchema()
        data = schema.load(request.json)
        
        # data ahora está validado
        username = data['username']
        password = data['password']
        # ... resto del código
        
    except ValidationError as err:
        return jsonify({
            'success': False, 
            'errors': err.messages
        }), 400
```

---

## 🟡 PRIORIDAD MEDIA: Rate Limiting

### Solución: Flask-Limiter

#### Paso 1: Agregar a requirements.txt
```
Flask-Limiter>=2.6.0
```

#### Paso 2: Configurar en mobile_server.py
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # En producción usar Redis
)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ... código de login
```

---

## 📋 Checklist de Implementación

### Seguridad Crítica
- [ ] Instalar bcrypt: `pip install bcrypt>=4.0.0`
- [ ] Actualizar `hash_password()` en auth_manager_flexible.py
- [ ] Agregar `verify_password()` en auth_manager_flexible.py
- [ ] Actualizar método `login()` para usar verify_password
- [ ] Actualizar db_auth_manager.py con bcrypt
- [ ] Crear script de migración de contraseñas
- [ ] Desactivar debug mode en start_server.py
- [ ] Desactivar debug mode en mobile_server.py
- [ ] Crear .env.example
- [ ] Actualizar .env con FLASK_DEBUG=False

### Validación y Rate Limiting
- [ ] Instalar marshmallow
- [ ] Crear validators.py
- [ ] Aplicar validación a endpoints críticos
- [ ] Instalar Flask-Limiter
- [ ] Configurar rate limiting
- [ ] Aplicar límites a login y registro

### Testing
- [ ] Probar login con bcrypt
- [ ] Verificar que debug=False en producción
- [ ] Probar validación de entrada
- [ ] Verificar rate limiting funciona

---

## ⚠️ Notas Importantes

1. **Migración de Contraseñas:** Después de cambiar a bcrypt, todos los usuarios necesitarán cambiar su contraseña o usar un sistema de migración.

2. **Variables de Entorno:** Nunca commitear archivos `.env` con credenciales reales.

3. **Debug Mode:** En producción, siempre usar `FLASK_DEBUG=False`.

4. **Rate Limiting:** En producción, usar Redis en lugar de memoria para rate limiting distribuido.

---

**Última actualización:** $(date)

