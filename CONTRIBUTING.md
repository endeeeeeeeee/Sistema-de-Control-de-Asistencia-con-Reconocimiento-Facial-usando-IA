# Guía de Contribución - CLASS VISION

¡Gracias por tu interés en contribuir a CLASS VISION! Este documento proporciona directrices para contribuir al proyecto.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Guía de Estilo](#guía-de-estilo)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Reporte de Bugs](#reporte-de-bugs)
- [Sugerencias de Funcionalidades](#sugerencias-de-funcionalidades)

## 📜 Código de Conducta

Este proyecto se adhiere a un código de conducta. Al participar, se espera que mantengas un ambiente respetuoso y profesional.

## 🤝 Cómo Contribuir

### Tipos de Contribuciones

Aceptamos varios tipos de contribuciones:

- 🐛 **Reporte de bugs**
- ✨ **Nuevas funcionalidades**
- 📝 **Mejoras en documentación**
- 🎨 **Mejoras en UI/UX**
- ⚡ **Optimizaciones de rendimiento**
- 🧪 **Tests adicionales**

## 🛠️ Configuración del Entorno de Desarrollo

### Prerrequisitos

- Python 3.8 o superior
- Git
- Webcam (para testing)

### Pasos de Instalación

1. **Fork del repositorio**
   ```bash
   # Haz un fork en GitHub y luego clona tu fork
   git clone https://github.com/TU_USUARIO/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA.git
   cd "Sistema de Control de Asistencia con Reconocimiento Facial usando IA"
   ```

2. **Crear rama de desarrollo**
   ```bash
   git checkout -b feature/nombre-de-tu-feature
   ```

3. **Configurar entorno virtual**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En macOS/Linux:
   source .venv/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Si existe
   ```

5. **Configurar Git remotes**
   ```bash
   git remote add upstream https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA.git
   ```

## 📐 Guía de Estilo

### Python

Seguimos las convenciones de [PEP 8](https://pep8.org/):

```python
# ✅ Bueno
def calculate_attendance_percentage(present_days: int, total_days: int) -> float:
    """
    Calcula el porcentaje de asistencia.
    
    Args:
        present_days: Días presentes
        total_days: Total de días
        
    Returns:
        Porcentaje de asistencia (0-100)
    """
    if total_days == 0:
        return 0.0
    return (present_days / total_days) * 100
```

### Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Formato
<tipo>(<ámbito>): <descripción corta>

[cuerpo opcional]

[footer opcional]
```

**Tipos de commits:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan código)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

**Ejemplos:**
```bash
git commit -m "feat(camera): agregar soporte para múltiples cámaras"
git commit -m "fix(attendance): corregir error en cálculo de porcentajes"
git commit -m "docs(readme): actualizar instrucciones de instalación"
```

### Estructura de Código

```
utils/
├── __init__.py          # Exportaciones públicas
├── logger.py            # Sistema de logging
├── config_manager.py    # Gestor de configuración
└── exceptions.py        # Excepciones personalizadas
```

## 🔄 Proceso de Pull Request

1. **Actualizar tu fork**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Hacer cambios en tu rama**
   ```bash
   git add .
   git commit -m "feat: descripción de cambios"
   ```

3. **Push a tu fork**
   ```bash
   git push origin feature/nombre-de-tu-feature
   ```

4. **Crear Pull Request**
   - Ve a GitHub y crea un PR desde tu rama a `main`
   - Llena la plantilla de PR con:
     - **Descripción**: Qué hace el PR
     - **Motivación**: Por qué es necesario
     - **Screenshots**: Si aplica
     - **Tests**: Cómo probarlo
     - **Checklist**: Marca items completados

5. **Code Review**
   - Espera feedback de los maintainers
   - Realiza cambios solicitados
   - Una vez aprobado, será merged

## 🐛 Reporte de Bugs

Para reportar un bug, abre un [Issue](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/issues) con:

### Plantilla de Bug Report

```markdown
**Descripción del Bug**
Descripción clara del problema.

**Para Reproducir**
Pasos para reproducir:
1. Ir a '...'
2. Hacer clic en '....'
3. Ver error

**Comportamiento Esperado**
Qué esperabas que sucediera.

**Screenshots**
Si aplica, agrega screenshots.

**Entorno:**
 - OS: [ej. Windows 10]
 - Python: [ej. 3.9]
 - Versión: [ej. 1.0.0]

**Logs**
```
[Pegar logs relevantes aquí]
```

**Contexto Adicional**
Cualquier otra información relevante.
```

## ✨ Sugerencias de Funcionalidades

Para sugerir una funcionalidad, abre un [Issue](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/issues) con:

### Plantilla de Feature Request

```markdown
**¿Tu feature está relacionado con un problema?**
Descripción clara del problema. Ej. "Me frustra cuando [...]"

**Describe la solución que te gustaría**
Descripción clara de qué quieres que pase.

**Describe alternativas consideradas**
Otras soluciones o funcionalidades que consideraste.

**Contexto Adicional**
Agrega cualquier contexto, screenshots, mockups, etc.
```

## 📝 Documentación

- Agrega docstrings a todas las funciones públicas
- Actualiza README.md si cambias funcionalidad
- Agrega comentarios para código complejo
- Actualiza CHANGELOG.md

## 🧪 Testing

Antes de enviar tu PR:

```bash
# Ejecutar tests (cuando existan)
python -m pytest

# Verificar estilo de código
flake8 .

# Verificar tipos (si se usa)
mypy .
```

## 🔗 Enlaces Útiles

- [Documentación del Proyecto](README.md)
- [Issues](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/issues)
- [Pull Requests](https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA/pulls)

## 📧 Contacto

Si tienes preguntas, contacta a los maintainers:
- Itzan Valdivia
- Ender Rosales

---

**¡Gracias por contribuir a CLASS VISION! 🏛️**
