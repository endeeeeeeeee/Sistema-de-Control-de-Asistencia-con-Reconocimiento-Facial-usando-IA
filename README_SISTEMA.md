# CLASS VISION - Universidad Nur
## Sistema de Control de Asistencia con Reconocimiento Facial

### 🎯 Descripción
Sistema profesional de control de asistencia con reconocimiento facial basado en PostgreSQL, desarrollado específicamente para la Universidad Nur.

### 🏗️ Arquitectura
- **Backend**: Flask + SQLAlchemy + PostgreSQL
- **Frontend**: HTML5 + JavaScript (Vanilla)
- **IA**: OpenCV + LBPH Face Recognition
- **Asistente Virtual**: Procesamiento de lenguaje natural

### 📊 Base de Datos
- **Motor**: PostgreSQL 14+
- **Tablas**: 20 tablas normalizadas
- **ORM**: SQLAlchemy 2.x
- **Modelos**: `database_models.py`

### 🔐 Autenticación
- Sistema de tokens con expiración (8 horas)
- Roles: ADMIN_SISTEMA, DOCENTE, DIRECTOR, SECRETARIA
- Almacenamiento seguro en tabla `sesiones_activas`

### 📁 Estructura del Proyecto

```
├── mobile_server.py              # Servidor Flask principal
├── database_models.py            # Modelos SQLAlchemy
├── db_auth_manager.py           # Autenticación PostgreSQL
├── db_student_manager.py        # Gestión de estudiantes
├── assistant_virtual.py         # Asistente virtual tipo Siri
├── automatic_attendance_headless.py  # Motor de reconocimiento facial
├── trainImage.py                # Entrenamiento del modelo
├── takeImage.py                 # Captura de rostros
├── templates/
│   ├── login.html              # Login con diseño moderno
│   ├── dashboard.html          # Dashboard principal
│   ├── register_student.html   # Registro de estudiantes
│   └── take_attendance.html    # Toma de asistencia
├── database_complete.sql        # Schema completo PostgreSQL
├── migrate_to_postgresql.py     # Script de migración
└── .env                        # Variables de entorno
```

### 🚀 Inicio Rápido

#### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 2. Configurar PostgreSQL
```bash
# Crear base de datos
createdb -U postgres class_vision

# Ejecutar schema
psql -U postgres -d class_vision -f database_complete.sql
```

#### 3. Configurar Variables de Entorno
Crear archivo `.env`:
```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/class_vision
```

#### 4. Migrar Datos (opcional)
```bash
python migrate_to_postgresql.py
```

#### 5. Iniciar Servidor
```bash
python mobile_server.py
# o usar: start.bat
```

### 🌐 Acceso
- **URL Local**: http://localhost:5000
- **Login**: http://localhost:5000/login
- **Dashboard**: http://localhost:5000/dashboard

### 👤 Credenciales por Defecto
- Usuario: `admin`
- Contraseña: `admin123`
- Rol: ADMIN_SISTEMA

### 📱 Funcionalidades Principales

#### Para Docentes
- ✅ Gestión de materias
- ✅ Inscripción de estudiantes
- ✅ Toma de asistencia con reconocimiento facial
- ✅ Visualización de estadísticas en tiempo real
- ✅ Generación de reportes
- ✅ Asistente virtual para consultas

#### Para Administradores
- ✅ Gestión de usuarios (docentes)
- ✅ Configuración del sistema
- ✅ Visualización de estadísticas globales
- ✅ Gestión de badges y gamificación
- ✅ Alertas de deserción

#### Características Avanzadas
- 🎮 Sistema de gamificación con badges
- 📊 Ranking mensual de asistencia
- 🚨 Detección automática de riesgo de deserción
- 📱 Acceso móvil responsive
- 🎤 Asistente virtual por voz
- 📍 Geolocalización GPS (opcional)
- 🔔 Sistema de notificaciones internas

### 🎨 Diseño
- **Paleta de Colores**:
  - Azul Claro: `#A7EBF2`
  - Azul Medio: `#54ACBF`
  - Azul: `#26658C`
  - Azul Oscuro: `#023859`
  - Azul Marino: `#011C40`
- **Responsive**: Adaptado para móviles y tablets
- **Moderno**: Diseño limpio y profesional

### 🔧 API Endpoints

#### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/logout` - Cerrar sesión
- `POST /api/auth/validate` - Validar token

#### Materias
- `GET /api/teacher/subjects` - Listar materias del docente
- `POST /api/teacher/subjects` - Crear nueva materia
- `DELETE /api/teacher/subjects` - Eliminar materia

#### Estudiantes
- `GET /api/teacher/students/<subject>` - Listar estudiantes por materia
- `POST /api/teacher/students/<subject>` - Agregar estudiante
- `DELETE /api/teacher/students/<subject>` - Eliminar estudiante
- `GET /api/students` - Listar todos los estudiantes

#### Estadísticas
- `GET /api/stats/dashboard` - Estadísticas del dashboard
- `GET /api/attendance-history/<subject>` - Historial de asistencias

#### Asistencia
- `POST /api/start-attendance` - Iniciar toma de asistencia
- `POST /api/stop-attendance` - Detener toma de asistencia
- `POST /api/recognize-frame` - Reconocer rostro en frame

### 📦 Dependencias Principales
```
Flask==3.0.0
SQLAlchemy==2.0.44
psycopg2-binary==2.9.11
opencv-python==4.8.1.78
opencv-contrib-python==4.8.1.78
numpy==1.24.3
pandas==2.0.3
python-dotenv==1.2.1
flask-cors==4.0.0
```

### 🗄️ Tablas de Base de Datos

#### Principales
- `personal_admin` - Usuarios del sistema (docentes, admins)
- `estudiantes` - Información de estudiantes
- `materias` - Materias/Asignaturas
- `inscripciones` - Relación estudiante-materia
- `asistencia_log` - Registro de asistencias
- `sesiones_activas` - Tokens de autenticación

#### Gamificación
- `badges` - Insignias disponibles
- `estudiantes_badges` - Badges obtenidos
- `ranking_mensual` - Ranking de estudiantes

#### Gestión
- `alertas_desercion` - Alertas de riesgo
- `notificaciones_internas` - Sistema de notificaciones
- `estadisticas_diarias` - Estadísticas por materia
- `reportes_generados` - Reportes del sistema

#### Auditoría
- `audit_log` - Registro de acciones
- `asistente_historial` - Historial del asistente virtual

### 🔒 Seguridad
- ✅ Contraseñas hasheadas con SHA-256
- ✅ Tokens de sesión con expiración
- ✅ Validación de permisos por rol
- ✅ Auditoría completa de acciones
- ✅ CORS configurado para producción

### 📈 Métricas y KPIs
- Porcentaje de asistencia por materia
- Ranking de puntualidad
- Detección de patrones de deserción
- Estadísticas de uso del sistema
- Reportes personalizados

### 🚀 Despliegue en Producción

#### Render.com (Recomendado)
1. Crear cuenta en Render.com
2. Crear PostgreSQL database (Plan gratuito: 500MB)
3. Crear Web Service vinculado al repositorio GitHub
4. Configurar variables de entorno:
   - `DATABASE_URL`: URL de PostgreSQL de Render
   - `FLASK_ENV`: production
5. Comando de inicio: `python mobile_server.py`

#### Requisitos de Producción
- Python 3.11+
- PostgreSQL 14+
- 512MB RAM mínimo
- 1GB almacenamiento

### 📚 Documentación Adicional
- `MIGRACION_POSTGRESQL.md` - Guía de migración
- `GUIA_DOCENTES.md` - Manual para docentes
- `MOBILE_GUIDE.md` - Guía de acceso móvil

### 🤝 Contribuciones
Este es un proyecto académico desarrollado para la Universidad Nur. Para contribuciones o mejoras, contactar al equipo de desarrollo.

### 📄 Licencia
Proyecto académico - Universidad Nur © 2025

### 👨‍💻 Desarrollo
- **Versión**: 2.0 (PostgreSQL)
- **Fecha**: Noviembre 2025
- **Stack**: Python + Flask + PostgreSQL + OpenCV
