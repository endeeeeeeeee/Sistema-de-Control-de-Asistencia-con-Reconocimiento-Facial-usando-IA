# CLASS VISION - Sistema de Control de Asistencia

Sistema Profesional de Control de Asistencia con Reconocimiento Facial usando Inteligencia Artificial

**Universidad Nur**

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

[Español](README_ESPAÑOL.md) | [English](#english) | [Mobile Guide](MOBILE_GUIDE.md) | [Teacher Guide](GUIA_DOCENTES.md)

---

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración](#configuración)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Autores](#autores)

---

## Descripción

CLASS VISION es un sistema avanzado de control de asistencia que utiliza reconocimiento facial con Inteligencia Artificial para automatizar el registro de asistencia en instituciones educativas. El sistema elimina métodos tradicionales lentos y propensos a errores, proporcionando una solución moderna, eficiente y confiable.

### Ventajas del Sistema

- **Rápido**: Registro de asistencia en 30 segundos vs 10 minutos manual
- **Preciso**: Reconocimiento facial con 90-95% de precisión
- **Seguro**: Datos biométricos, imposible de falsificar
- **Analítico**: Reportes automáticos y estadísticas
- **Profesional**: Interfaz moderna y fácil de usar

---

## Características

### Inteligencia Artificial

- **Algoritmo LBPH**: Local Binary Patterns Histograms para reconocimiento facial
- **Detector Haar Cascade**: Detección de rostros en tiempo real
- **Entrenamiento Automático**: Modelo que aprende de nuevos estudiantes
- **Confianza Ajustable**: Umbral personalizable para mayor precisión

### Gestión de Estudiantes

- Registro con captura de 50 fotos por estudiante
- Base de datos PostgreSQL para gestión eficiente
- Identificación automática en tiempo real
- Histórico completo de registros

### Captura y Procesamiento

- Soporte para webcams USB y integradas
- Detección múltiple de rostros simultáneos
- Procesamiento en tiempo real (30 FPS)
- Eliminación automática de duplicados

### Reportes y Análisis

- Exportación a CSV con timestamps
- Cálculo automático de porcentajes
- Visualización en tablas profesionales
- Histórico consolidado por materia

### Interfaz Web

- Diseño responsivo y moderno
- Interfaz intuitiva para docentes
- Acceso desde PC y dispositivos móviles
- Dashboard personalizado por docente

### Características Profesionales (v2.0.0+)

- Sistema de configuración JSON
- Logging profesional con rotación
- Manejo robusto de excepciones
- Scripts de instalación automatizada
- Arquitectura orientada a objetos
- Documentación completa

### Control Móvil (v2.1.0)

- Control remoto desde smartphone
- Servidor web integrado con Flask API REST
- Interfaz responsive optimizada para móviles
- Visualización en tiempo real de reconocimientos
- Acceso rápido mediante código QR

### Sistema de Autenticación (v2.1.1)

- Login seguro de docentes
- Dashboard personalizado por usuario
- Gestión de materias y estudiantes
- Sesiones seguras con tokens (8 horas de duración)
- Aislamiento de datos por docente

---

## Requisitos

### Hardware Mínimo

- **CPU**: Intel i5 / AMD Ryzen 5 o superior
- **RAM**: 4 GB (8 GB recomendado)
- **Disco**: 5 GB libres
- **Cámara**: Webcam USB o integrada (720p+)

### Software

- **OS**: Windows 10/11, macOS 10.15+, o Ubuntu 20.04+
- **Python**: 3.8 - 3.11
- **PostgreSQL**: 12 o superior
- **Git**: Para clonar el repositorio

---

## Instalación

### Opción 1: Instalación Automatizada (Recomendado)

#### Windows (PowerShell)
```powershell
# Clonar repositorio
git clone https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA.git
cd "Sistema de Control de Asistencia con Reconocimiento Facial usando IA"

# Ejecutar instalador
.\install.ps1
```

#### Windows (CMD)
```cmd
install.bat
```

#### Linux / macOS
```bash
# Clonar repositorio
git clone https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA.git
cd "Sistema de Control de Asistencia con Reconocimiento Facial usando IA"

# Dar permisos y ejecutar
chmod +x install.sh
./install.sh
```

### Opción 2: Instalación Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA.git
cd "Sistema de Control de Asistencia con Reconocimiento Facial usando IA"

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar base de datos
# Crear archivo .env con DATABASE_URL
# Ejecutar: python setup_database.py
```

---

## Uso

### Opción A: Sistema con Autenticación (Recomendado para Docentes)

#### 1. Iniciar el Servidor Web

```bash
python start_server.py
```

#### 2. Acceder al Sistema

- **Desde PC**: http://localhost:5000/login
- **Desde teléfono**: http://[IP-MOSTRADA]:5000/login

#### 3. Registrarse o Ingresar

- Primera vez: Crear cuenta de docente
- Siguientes veces: Ingresar con usuario y contraseña

#### 4. Gestionar Clases

- Agregar materias desde el dashboard
- Registrar estudiantes en cada materia
- Tomar asistencia desde PC o móvil

**Guía completa**: Ver [GUIA_DOCENTES.md](GUIA_DOCENTES.md)

---

### Opción B: Sistema Tradicional (Sin Login)

#### 1. Iniciar la Aplicación

```bash
# Activar entorno virtual primero
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Ejecutar
python attendance.py
```

#### 2. Registrar Estudiantes

1. Click en "Inscribir un Nuevo Estudiante"
2. Ingresar número de matrícula y nombre completo
3. Click en "Capturar Rostro"
4. Posicionar rostro frente a cámara
5. Sistema captura 50 fotos automáticamente

#### 3. Entrenar el Modelo

1. Después de registrar estudiantes
2. Sistema entrena automáticamente
3. Genera modelo `Trainner.yml`

#### 4. Tomar Asistencia

**Desde PC:**
1. Click en "Tomar Asistencia"
2. Ingresar nombre de la materia
3. Sistema reconoce rostros automáticamente
4. Asistencia guardada en CSV

**Desde Smartphone:**
1. Ejecutar servidor móvil
2. Escanear código QR con teléfono
3. Seleccionar materia en interfaz móvil
4. Iniciar asistencia
5. Ver reconocimientos en tiempo real

**Ver Guía Completa de Control Móvil**: [MOBILE_GUIDE.md](MOBILE_GUIDE.md)

#### 5. Ver Registros

1. Click en "Consultar Asistencia"
2. Ver historial completo de asistencias
3. Exportar reportes en CSV

---

## Estructura del Proyecto

```
Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/
│
├── Archivos Principales
│   ├── attendance.py               # Interfaz gráfica principal
│   ├── takeImage.py                # Captura de imágenes
│   ├── trainImage.py               # Entrenamiento del modelo
│   ├── automaticAttedance.py       # Asistencia automática
│   ├── show_attendance.py          # Visualización de reportes
│   ├── mobile_server.py            # Servidor web Flask
│   └── start_server.py             # Script de inicio
│
├── Utilidades
│   └── utils/
│       ├── logger.py               # Sistema de logging
│       ├── config_manager.py       # Gestor de configuración
│       ├── exceptions.py           # Excepciones personalizadas
│       └── __init__.py
│
├── Configuración
│   └── config/
│       ├── default_config.json     # Configuración por defecto
│       ├── recognition_config.json  # Configuración de reconocimiento
│       └── README.md               # Documentación de configuración
│
├── Datos de Entrenamiento
│   ├── TrainingImage/              # Fotos de estudiantes
│   ├── TrainingImageLabel/         # Modelo entrenado
│   ├── StudentDetails/             # Datos de estudiantes
│   └── Attendance/                 # Registros de asistencia
│
├── Recursos Visuales
│   ├── UI_Image/                   # Imágenes de interfaz
│   └── haarcascade_*.xml           # Clasificadores faciales
│
├── Templates
│   └── templates/                  # Plantillas HTML
│
├── Documentación
│   ├── README.md                   # Este archivo
│   ├── README_ESPAÑOL.md           # Documentación en español
│   ├── MOBILE_GUIDE.md             # Guía de uso móvil
│   ├── GUIA_DOCENTES.md            # Guía para docentes
│   └── EVALUACION_PROFESIONAL.md   # Evaluación del proyecto
│
├── Scripts de Instalación
│   ├── install.ps1                  # PowerShell (Windows)
│   ├── install.bat                 # Batch (Windows)
│   └── install.sh                   # Bash (Linux/macOS)
│
└── Configuración del Proyecto
    ├── requirements.txt            # Dependencias Python
    ├── .gitignore                  # Exclusiones de Git
    ├── .env.example                # Ejemplo de variables de entorno
    └── __init__.py                 # Inicializador de paquete
```

---

## Configuración

CLASS VISION utiliza un sistema de configuración flexible mediante archivos JSON y variables de entorno.

### Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```env
# Flask Configuration
FLASK_DEBUG=False
FLASK_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5501/class_vision

# Security
BCRYPT_ROUNDS=12
SESSION_TIMEOUT_HOURS=8

# OpenCV
CAMERA_INDEX=0
```

### Configuración JSON

```bash
# Copiar configuración por defecto
cp config/default_config.json config/local_config.json

# Editar con tu editor favorito
notepad config/local_config.json  # Windows
nano config/local_config.json     # Linux/macOS
```

### Parámetros Importantes

```json
{
  "camera": {
    "capture_duration_seconds": 20,
    "images_per_student": 50
  },
  "recognition": {
    "confidence_threshold": 70
  },
  "tts": {
    "enabled": true,
    "language": "spanish"
  },
  "logging": {
    "enabled": true,
    "level": "INFO"
  }
}
```

Ver documentación completa en [`config/README.md`](config/README.md).

---

## Contribuir

Las contribuciones son bienvenidas. Por favor lee nuestra [Guía de Contribución](CONTRIBUTING.md) para conocer el proceso.

### Proceso Rápido

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/mi-feature`
3. Commit cambios: `git commit -m 'feat: agregar nueva característica'`
4. Push: `git push origin feature/mi-feature`
5. Abre un Pull Request

### Reportar Bugs

Abre un [Issue](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/issues) con:
- Descripción del problema
- Pasos para reproducir
- Screenshots si aplica
- Entorno (OS, Python version)

---

## Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## Autores

- **Itzan Valdivia** - [@itzanvaldivia](https://github.com/itzanvaldivia)
- **Ender Rosales** - [@endeeeeeeeee](https://github.com/endeeeeeeeee)

---

## Agradecimientos

- OpenCV por la biblioteca de visión por computadora
- Flask por el framework web
- SQLAlchemy por el ORM
- Comunidad de Python por las excelentes librerías

---

## Contacto

¿Preguntas o sugerencias? Abre un [Issue](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/issues) o contáctanos:

- Email: [Contacto](mailto:tu-email@ejemplo.com)
- Issues: [GitHub Issues](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/issues)

---

Hecho con Python y OpenCV

[Volver arriba](#class-vision---sistema-de-control-de-asistencia)
