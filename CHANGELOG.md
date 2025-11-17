# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [2.0.0] - 2025-11-17

### 🎉 Added (Agregado)
- **Sistema de configuración profesional** con archivos JSON
  - `config/default_config.json`: Configuración por defecto
  - `config/local_config.json`: Configuración local personalizable
  - Gestor de configuración centralizado (`utils/config_manager.py`)

- **Sistema de logging robusto**
  - Logging a archivo con rotación automática
  - Niveles de log configurables (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Formato consistente con timestamps
  - Directorio `logs/` para almacenar históricos

- **Excepciones personalizadas** para mejor manejo de errores
  - `ClassVisionError`: Excepción base
  - `CameraError`: Errores de cámara
  - `ModelError`: Errores del modelo de IA
  - `ConfigError`: Errores de configuración
  - `StudentDataError`: Errores de datos de estudiantes
  - `AttendanceError`: Errores de asistencia
  - `ValidationError`: Errores de validación

- **Estructura de utilidades**
  - Módulo `utils/` con herramientas reutilizables
  - Logger centralizado
  - Gestor de configuración

- **Mejoras en Git**
  - `.gitignore` profesional y específico del proyecto
  - Archivos `.gitkeep` para mantener estructura de directorios
  - Exclusión de datos sensibles (estudiantes, asistencia)
  - Exclusión de modelos entrenados (se regeneran localmente)

- **Documentación profesional**
  - `CONTRIBUTING.md`: Guía de contribución
  - `CHANGELOG.md`: Histórico de cambios
  - `config/README.md`: Documentación de configuración
  - Ejemplo de datos: `StudentDetails/studentdetails_example.csv`

- **Rama de desarrollo**
  - `feature/professional-improvements`: Rama para mejoras

### 🔄 Changed (Cambiado)
- **Refactorización del código principal**
  - `attendance.py`: Refactorizado a clase `ClassVisionApp`
  - Mejor organización y separación de responsabilidades
  - Uso de Path (pathlib) en lugar de strings para rutas
  - Configuración de rutas centralizada usando constantes

- **Mejoras en el tema griego**
  - Diccionario `THEME` para colores consistentes
  - Efectos hover más suaves en interfaz
  - Mejor organización de componentes visuales

### 🐛 Fixed (Corregido)
- Inicialización del motor TTS con manejo robusto de errores
- Mejor manejo de excepciones en captura de cámara
- Corrección en carga de imágenes (uso de `self` para mantener referencias)

### 🔒 Security (Seguridad)
- **Datos sensibles protegidos en .gitignore**
  - Archivos CSV de estudiantes no se suben a Git
  - Registros de asistencia excluidos de control de versiones
  - Solo archivos de ejemplo se incluyen en repositorio

### 📚 Documentation (Documentación)
- Guía completa de contribución
- Documentación de configuración
- Changelog estructurado
- Comentarios y docstrings mejorados

---

## [1.0.0] - 2025-10-20

### Added
- Interfaz gráfica con tema griego
- Sistema de reconocimiento facial usando LBPH
- Captura y entrenamiento de imágenes
- Toma automática de asistencia
- Visualización de registros
- Síntesis de voz en español
- Documentación en inglés y español

### Features
- Registro de estudiantes con captura de fotos
- Entrenamiento de modelo de reconocimiento facial
- Asistencia automática por cámara
- Exportación a CSV
- Interfaz temática griega elegante

---

## Leyenda de Tipos de Cambios

- `Added`: Nuevas funcionalidades
- `Changed`: Cambios en funcionalidades existentes
- `Deprecated`: Funcionalidades obsoletas (aún funcionan)
- `Removed`: Funcionalidades eliminadas
- `Fixed`: Correcciones de bugs
- `Security`: Cambios relacionados con seguridad

---

**Formato de versiones: [MAJOR.MINOR.PATCH]**
- **MAJOR**: Cambios incompatibles con versiones anteriores
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Correcciones de bugs compatibles
