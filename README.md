# 🏛️ CLASS VISION - Sistema de Control de Asistencia

<div align="center">

![CLASS VISION Logo](UI_Image/0001.png)

**Sistema Profesional de Control de Asistencia con Reconocimiento Facial usando IA**

**Universidad Nur**

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Mobile](https://img.shields.io/badge/mobile-enabled-brightgreen.svg)]()
[![Auth](https://img.shields.io/badge/auth-secure-red.svg)]()

[🇪🇸 Español](README_ESPAÑOL.md) | [🇬🇧 English](#english) | [📱 Mobile Guide](MOBILE_GUIDE.md) | [👨‍🏫 Teacher Guide](GUIA_DOCENTES.md)

</div>

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Configuración](#️-configuración)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)
- [Autores](#-autores)

---

## 🎯 Descripción

**CLASS VISION** es un sistema avanzado de control de asistencia que utiliza **reconocimiento facial con Inteligencia Artificial** para automatizar el registro de asistencia en instituciones educativas. El sistema elimina métodos tradicionales lentos y propensos a errores, proporcionando una solución moderna, eficiente y confiable.

### ¿Por qué CLASS VISION?

- ⚡ **Rápido**: Registro de asistencia en 30 segundos vs 10 minutos manual
- 🎯 **Preciso**: Reconocimiento facial con 90-95% de precisión
- 🔒 **Seguro**: Datos biométricos, imposible de falsificar
- 📊 **Analítico**: Reportes automáticos y estadísticas
- 🎨 **Elegante**: Interfaz profesional con tema griego

---

## ✨ Características

### 🧠 Inteligencia Artificial
- **Algoritmo LBPH**: Local Binary Patterns Histograms para reconocimiento facial
- **Detector Haar Cascade**: Detección de rostros en tiempo real
- **Entrenamiento Automático**: Modelo que aprende de nuevos estudiantes
- **Confianza Ajustable**: Umbral personalizable para mayor precisión

### 👥 Gestión de Estudiantes
- ✅ Registro con captura de 50 fotos por estudiante
- ✅ Base de datos CSV fácil de gestionar
- ✅ Identificación automática en tiempo real
- ✅ Histórico completo de registros

### 📸 Captura y Procesamiento
- ✅ Soporte para webcams USB y integradas
- ✅ Detección múltiple de rostros simultáneos
- ✅ Procesamiento en tiempo real (30 FPS)
- ✅ Eliminación automática de duplicados

### 📊 Reportes y Análisis
- ✅ Exportación a CSV con timestamps
- ✅ Cálculo automático de porcentajes
- ✅ Visualización en tablas elegantes
- ✅ Histórico consolidado por materia

### 🎨 Interfaz Profesional
- ✅ Tema griego elegante y único
- ✅ Efectos visuales interactivos
- ✅ Síntesis de voz en español
- ✅ Diseño responsivo y moderno

### 🔧 Características Profesionales (v2.0.0)
- ✅ Sistema de configuración JSON
- ✅ Logging profesional con rotación
- ✅ Manejo robusto de excepciones
- ✅ Scripts de instalación automatizada
- ✅ Arquitectura orientada a objetos
- ✅ Documentación completa

### 📱 NUEVO en v2.1.0 - Control Móvil
- ✨ **Control remoto desde smartphone**: Toma asistencia desde tu teléfono
- 🌐 **Servidor web integrado**: Flask API REST completa
- 📱 **Interfaz responsive**: Diseño optimizado para móviles
- 🔄 **Tiempo real**: Visualiza reconocimientos al instante
- 📊 **QR Code**: Acceso rápido escaneando código QR
- 🎓 **Branding Universidad Nur**: Personalización institucional

### 🔐 NUEVO en v2.1.1 - Sistema de Autenticación
- 👨‍🏫 **Login de docentes**: Sistema seguro de autenticación
- 🎯 **Dashboard personalizado**: Panel de control para cada docente
- 📚 **Gestión de materias**: Organiza tus clases fácilmente
- 👥 **Gestión de estudiantes**: Agrega estudiantes por materia
- 🔒 **Sesiones seguras**: Tokens con 8 horas de duración
- 🗂️ **Datos aislados**: Cada docente ve solo sus estudiantes

---

## 💻 Requisitos

### Hardware Mínimo
- **CPU**: Intel i5 / AMD Ryzen 5 o superior
- **RAM**: 4 GB (8 GB recomendado)
- **Disco**: 5 GB libres
- **Cámara**: Webcam USB o integrada (720p+)

### Software
- **OS**: Windows 10/11, macOS 10.15+, o Ubuntu 20.04+
- **Python**: 3.8 - 3.11
- **Git**: Para clonar el repositorio

---

## 🚀 Instalación

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
```

---

## 📖 Uso

### Opción A: Sistema con Autenticación (Recomendado para Docentes)

#### 1️⃣ Iniciar el Servidor Web
```bash
python mobile_server.py
```

#### 2️⃣ Acceder al Sistema
- **Desde PC**: http://localhost:5000/login
- **Desde teléfono**: http://[IP-MOSTRADA]:5000/login

#### 3️⃣ Registrarse o Ingresar
- Primera vez: Crea tu cuenta de docente
- Siguientes veces: Ingresa con tu usuario y contraseña

#### 4️⃣ Gestionar tus Clases
- Agrega materias desde el dashboard
- Registra estudiantes en cada materia
- Toma asistencia desde PC o móvil

📖 **Guía completa**: Ver [GUIA_DOCENTES.md](GUIA_DOCENTES.md)

---

### Opción B: Sistema Tradicional (Sin Login)

### 1️⃣ Iniciar la Aplicación

```bash
# Activar entorno virtual primero
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Ejecutar
python attendance.py
```

### 2️⃣ Registrar Estudiantes

1. Click en **"Inscribir un Nuevo Héroe"**
2. Ingresar:
   - Número de Matrícula
   - Nombre completo
3. Click en **"Invocar el Rostro"**
4. Posicionar rostro frente a cámara
5. Sistema captura 50 fotos automáticamente

### 3️⃣ Entrenar el Modelo

1. Después de registrar estudiantes
2. Sistema entrena automáticamente
3. Genera modelo `Trainner.yml`

### 4️⃣ Tomar Asistencia

**Opción A - Desde PC:**
1. Click en **"Convocar el Verbo de los Héroes"**
2. Ingresar nombre de la materia
3. Sistema reconoce rostros automáticamente
4. Asistencia guardada en CSV

**Opción B - Desde Smartphone (NUEVO v2.1.0):**
1. Ejecutar: `start_mobile.bat` (Windows) o `python start_mobile_server.py`
2. Escanear QR code con tu teléfono
3. Seleccionar materia en interfaz móvil
4. Presionar "▶️ Iniciar Asistencia"
5. Ver reconocimientos en tiempo real

📱 **[Ver Guía Completa de Control Móvil](MOBILE_GUIDE.md)**

### 5️⃣ Ver Registros

1. Click en **"Consultar las Tablas del Destino"**
2. Ver historial completo de asistencias
6. Click en **"Grabar el Conocimiento"** para entrenar

### 3️⃣ Tomar Asistencia

1. Click en **"Convocar el Verbo de los Héroes"**
2. Ingresar nombre de la materia/curso
3. Click en **"Registrar Asistencia"**
4. Estudiantes se posicionan frente a cámara
5. Sistema registra automáticamente (20 segundos)
6. Ver tabla de resultados

### 4️⃣ Ver Reportes

1. Click en **"Consultar las Tablas del Destino"**
2. Ingresar nombre de la materia
3. Click en **"Ver Asistencia"**
4. Ver tabla consolidada con porcentajes

---

## 📁 Estructura del Proyecto

```
Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/
│
├── 📄 Archivos Principales
│   ├── attendance.py               # Interfaz gráfica principal
│   ├── takeImage.py                # Captura de imágenes
│   ├── trainImage.py               # Entrenamiento del modelo
│   ├── automaticAttedance.py       # Asistencia automática
│   └── show_attendance.py          # Visualización de reportes
│
├── 🛠️ Utilidades (v2.0.0)
│   └── utils/
│       ├── logger.py               # Sistema de logging
│       ├── config_manager.py       # Gestor de configuración
│       ├── exceptions.py           # Excepciones personalizadas
│       └── __init__.py
│
├── ⚙️ Configuración
│   └── config/
│       ├── default_config.json     # Configuración por defecto
│       ├── local_config.json       # Configuración personal (opcional)
│       └── README.md               # Documentación de configuración
│
├── 📸 Datos de Entrenamiento
│   ├── TrainingImage/              # Fotos de estudiantes
│   ├── TrainingImageLabel/         # Modelo entrenado
│   ├── StudentDetails/             # Datos de estudiantes
│   └── Attendance/                 # Registros de asistencia
│
├── 🎨 Recursos Visuales
│   ├── UI_Image/                   # Imágenes de interfaz
│   └── haarcascade_*.xml           # Clasificadores faciales
│
├── 📚 Documentación
│   ├── README.md                   # Este archivo
│   ├── README_ESPAÑOL.md           # Documentación en español
│   ├── CONTRIBUTING.md             # Guía de contribución
│   ├── CHANGELOG.md                # Histórico de versiones
│   └── RESUMEN_CAMBIOS.md          # Resumen de cambios
│
├── 🔧 Scripts de Instalación
│   ├── install.ps1                 # PowerShell (Windows)
│   ├── install.bat                 # Batch (Windows)
│   └── install.sh                  # Bash (Linux/macOS)
│
└── 📋 Configuración del Proyecto
    ├── requirements.txt            # Dependencias Python
    ├── .gitignore                  # Exclusiones de Git
    └── __init__.py                 # Inicializador de paquete
```

---

## ⚙️ Configuración

CLASS VISION utiliza un sistema de configuración JSON flexible.

### Crear Configuración Personalizada

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
    "capture_duration_seconds": 20,    // Tiempo de captura
    "images_per_student": 50           // Fotos por estudiante
  },
  "recognition": {
    "confidence_threshold": 70         // Umbral de confianza (0-100)
  },
  "tts": {
    "enabled": true,                   // Activar síntesis de voz
    "language": "spanish"
  },
  "logging": {
    "enabled": true,                   // Activar logs
    "level": "INFO"                    // DEBUG, INFO, WARNING, ERROR
  }
}
```

Ver documentación completa en [`config/README.md`](config/README.md).

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee nuestra [Guía de Contribución](CONTRIBUTING.md) para conocer el proceso.

### Proceso Rápido

1. **Fork** el repositorio
2. **Crea** una rama: `git checkout -b feature/mi-feature`
3. **Commit** cambios: `git commit -m 'feat: agregar nueva característica'`
4. **Push**: `git push origin feature/mi-feature`
5. **Abre** un Pull Request

### Reportar Bugs

Abre un [Issue](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/issues) con:
- Descripción del problema
- Pasos para reproducir
- Screenshots si aplica
- Entorno (OS, Python version)

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👥 Autores

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/itzanvaldivia">
        <img src="https://github.com/itzanvaldivia.png" width="100px;" alt="Itzan Valdivia"/>
        <br />
        <sub><b>Itzan Valdivia</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/endeeeeeeeee">
        <img src="https://github.com/endeeeeeeeee.png" width="100px;" alt="Ender Rosales"/>
        <br />
        <sub><b>Ender Rosales</b></sub>
      </a>
    </td>
  </tr>
</table>

---

## 🌟 Agradecimientos

- OpenCV por la biblioteca de visión por computadora
- Tkinter por la interfaz gráfica
- Comunidad de Python por las excelentes librerías

---

## 📞 Contacto

¿Preguntas o sugerencias? Abre un [Issue](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/issues) o contáctanos:

- 📧 Email: [Contacto](mailto:tu-email@ejemplo.com)
- 🐛 Issues: [GitHub Issues](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/issues)

---

<div align="center">

**🏛️ ¡Que los dioses del código bendigan este proyecto! 🏛️**

Hecho con ❤️ usando Python y OpenCV

[⬆ Volver arriba](#-class-vision---sistema-de-control-de-asistencia)

</div>
