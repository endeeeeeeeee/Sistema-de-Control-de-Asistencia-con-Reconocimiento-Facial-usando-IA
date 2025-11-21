# 👨‍🏫 Guía para Docentes - Sistema CLASS VISION
## Universidad Nur - Control de Asistencia con Reconocimiento Facial

---

## 📋 Índice
1. [Inicio Rápido](#inicio-rápido)
2. [Registro y Login](#registro-y-login)
3. [Gestión de Materias](#gestión-de-materias)
4. [Gestión de Estudiantes](#gestión-de-estudiantes)
5. [Toma de Asistencia](#toma-de-asistencia)
6. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🚀 Inicio Rápido

### Paso 1: Iniciar el Servidor
```bash
python mobile_server.py
```

El servidor se iniciará y mostrará:
```
🎓 UNIVERSIDAD NUR - CLASS VISION
📱 Servidor Móvil Iniciado

🌐 Accede desde tu smartphone:
   http://192.168.1.32:5000
```

### Paso 2: Acceder al Sistema
- **Desde tu PC**: http://localhost:5000/login
- **Desde tu teléfono**: Usa la IP mostrada, ej: http://192.168.1.32:5000/login

---

## 🔐 Registro y Login

### Primera Vez - Crear Cuenta

1. **Abre el navegador** en http://192.168.1.32:5000/login
2. **Selecciona la pestaña "Registrarse"**
3. **Completa el formulario**:
   - Usuario: Tu identificador único (ej: `profesor.juan`)
   - Contraseña: Mínimo 6 caracteres
   - Nombre completo: Tu nombre completo
4. **Haz clic en "Registrarse"**
5. **¡Listo!** Serás redirigido al dashboard automáticamente

### Ingreso Posterior

1. **Abre** http://192.168.1.32:5000/login
2. **Pestaña "Iniciar Sesión"**
3. **Ingresa** tu usuario y contraseña
4. **Haz clic en "Ingresar"**

---

## 📚 Gestión de Materias

### Agregar Nueva Materia

1. En el **Dashboard**, haz clic en **"➕ Agregar Materia"**
2. Ingresa el **nombre de la materia** (ej: MATEMÁTICAS, FÍSICA, QUÍMICA)
3. Haz clic en **"Agregar"**
4. La materia aparecerá en tu lista

### Ver Materias

En el dashboard verás todas tus materias con:
- **Nombre de la materia**
- **Cantidad de estudiantes** registrados
- **Botones de acción**:
  - 👥 **Estudiantes**: Gestionar estudiantes de la materia
  - 📸 **Asistencia**: Tomar asistencia
  - 🗑️ **Eliminar**: Borrar la materia

### Eliminar Materia

1. Haz clic en el botón **🗑️** junto a la materia
2. Confirma la eliminación
3. **Nota**: Esto NO elimina los estudiantes del sistema, solo de esa materia

---

## 👥 Gestión de Estudiantes

### Agregar Estudiante a una Materia

1. En el dashboard, haz clic en **"👥 Estudiantes"** en la materia deseada
2. En el modal que aparece, completa:
   - **Matrícula**: Código único del estudiante (ej: 3434)
   - **Nombre completo**: Nombre del estudiante
3. Haz clic en **"➕"**
4. El estudiante se agregará a la lista

### Ver Estudiantes de una Materia

1. Haz clic en **"👥 Estudiantes"**
2. Verás la lista completa con:
   - Nombre del estudiante
   - Matrícula
   - Botón para eliminar

### Eliminar Estudiante de una Materia

1. En la lista de estudiantes, haz clic en **"Eliminar"**
2. Confirma la acción
3. El estudiante será removido de esa materia específica

---

## 📸 Toma de Asistencia

### Opción 1: Desde tu PC

1. Haz clic en **"📸 Asistencia"** en la materia deseada
2. Selecciona **"💻 Desde este PC"**
3. La cámara web se activará automáticamente
4. Los estudiantes serán reconocidos en tiempo real
5. La asistencia se guardará automáticamente

### Opción 2: Desde tu Teléfono (Recomendado)

1. Haz clic en **"📸 Asistencia"** en la materia
2. Selecciona **"📱 Desde mi Teléfono"**
3. Se abrirá una nueva ventana con la **interfaz móvil**
4. En tu teléfono verás:
   - Botón **"📸 Iniciar Asistencia"**
   - Estado en tiempo real
   - Estudiantes reconocidos

#### Características del Control Móvil:
- ✅ **Diseño responsive**: Se adapta a cualquier pantalla
- ✅ **Actualizaciones en tiempo real**: Ves quién fue reconocido al instante
- ✅ **Fácil de usar**: Un solo botón para iniciar/detener
- ✅ **Contador visual**: Muestra cuántos estudiantes fueron reconocidos

### Proceso de Reconocimiento

1. **Sistema activa la cámara**
2. **Busca rostros conocidos**
3. **Compara con base de datos entrenada**
4. **Registra asistencia automáticamente**
5. **Guarda en archivo CSV**

### Ubicación de Archivos de Asistencia

Los registros se guardan en:
```
Attendance/
  └── [NOMBRE_MATERIA]/
      ├── attendance.csv              (historial completo)
      └── [MATERIA]_FECHA_HORA.csv    (sesión específica)
```

Ejemplo:
```
Attendance/
  └── MATEMATICAS/
      ├── attendance.csv
      └── MATEMATICAS_2025-11-17_14-30-00.csv
```

---

## ❓ Preguntas Frecuentes

### ¿Puedo usar el sistema desde mi teléfono completamente?

**Sí**, el sistema está diseñado para ser 100% móvil. Simplemente:
1. Inicia el servidor en la PC
2. Accede desde tu teléfono usando la IP local
3. Gestiona materias, estudiantes y toma asistencia

### ¿Qué pasa si dos docentes usan el mismo usuario?

Cada docente debe tener su **propio usuario**. Esto asegura que:
- Las materias estén separadas
- Los estudiantes no se mezclen
- El historial sea individual

### ¿Puedo tener el mismo estudiante en varias materias?

**Sí**, un estudiante puede estar registrado en múltiples materias del mismo docente.

### ¿Qué pasa si no se reconoce a un estudiante?

Posibles causas:
1. **No está registrado en esa materia**: Agrégalo desde el dashboard
2. **No tiene foto entrenada**: Usa el sistema de entrenamiento facial
3. **Mala iluminación**: Mejora la luz del ambiente
4. **Rostro cubierto**: Asegúrate que el rostro sea visible

### ¿Cómo entreno el reconocimiento facial de nuevos estudiantes?

Usa el módulo de entrenamiento incluido:
```bash
python takeImage.py
python trainImage.py
```

### ¿El sistema funciona sin internet?

**Sí**, es completamente local. Solo necesitas:
- PC con Python instalado
- Cámara web conectada
- Red WiFi local (para acceso desde teléfono)

### ¿Puedo ver el historial de asistencia?

**Sí**, los archivos CSV en `Attendance/[MATERIA]/` contienen:
- Fecha y hora de cada asistencia
- Nombre del estudiante
- Matrícula
- Estado de asistencia

### ¿Cuánto tiempo dura la sesión de login?

Las sesiones duran **8 horas**. Después de ese tiempo necesitas volver a iniciar sesión por seguridad.

### ¿Se pueden recuperar las contraseñas?

Actualmente no hay sistema de recuperación. Las contraseñas están cifradas con SHA-256 por seguridad. **Guarda tu contraseña en un lugar seguro**.

### ¿Cuántas materias puedo crear?

**Ilimitadas**. No hay restricción en la cantidad de materias o estudiantes.

---

## 🔧 Solución de Problemas

### El servidor no inicia

```bash
# Verifica que Python esté instalado
python --version

# Instala dependencias
pip install -r requirements.txt

# Inicia nuevamente
python mobile_server.py
```

### No puedo acceder desde el teléfono

1. Verifica que PC y teléfono estén en la **misma red WiFi**
2. Usa la **IP correcta** mostrada al iniciar el servidor
3. Desactiva **firewall** temporalmente si está bloqueando el puerto 5000

### El login no funciona

1. Verifica que el servidor esté corriendo
2. Abre la **consola del navegador** (F12) para ver errores
3. Asegúrate que `data/users.json` existe y tiene permisos de escritura

### La cámara no se activa

1. Verifica que la cámara esté conectada
2. Cierra otras aplicaciones que usen la cámara
3. Revisa permisos de la cámara en el sistema operativo

---

## 📞 Soporte

Para problemas técnicos o sugerencias:
- **Email**: soporte@universidadnur.edu
- **GitHub Issues**: [Repositorio del proyecto]

---

## 📄 Licencia

Sistema desarrollado para Universidad Nur.
© 2025 - Todos los derechos reservados.

---

**¡Gracias por usar CLASS VISION! 🎓**
