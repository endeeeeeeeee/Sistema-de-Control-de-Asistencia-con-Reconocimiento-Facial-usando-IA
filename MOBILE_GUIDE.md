# 📱 Guía de Control Móvil - CLASS VISION

## Universidad Nur - Sistema de Asistencia con Reconocimiento Facial

---

## 🎯 Características del Control Móvil

### ✨ Nuevo en v2.1.0

- **Control remoto desde smartphone**: Los docentes pueden tomar asistencia desde cualquier dispositivo móvil
- **Acceso mediante QR Code**: Escanea el código QR para acceso instantáneo
- **Interfaz responsive**: Optimizada para teléfonos y tablets
- **Actualización en tiempo real**: Visualiza estudiantes reconocidos al instante
- **Sin instalación en el móvil**: Solo necesitas un navegador web

---

## 🚀 Inicio Rápido

### Opción 1: Launcher Automático (Recomendado)

```bash
# Windows
start_mobile.bat
```

Este script:
1. ✅ Instala dependencias automáticamente
2. ✅ Inicia el servidor
3. ✅ Abre el navegador con el QR code
4. ✅ Muestra la URL de acceso

### Opción 2: Manual

```bash
# 1. Instalar dependencias
pip install flask flask-cors qrcode[pil]

# 2. Iniciar servidor
python start_mobile_server.py
```

---

## 📱 Acceso desde Smartphone

### Paso 1: Conectar a la misma red WiFi

Asegúrate de que:
- ✅ Tu PC y tu teléfono están en la **misma red WiFi**
- ✅ El servidor está corriendo en el PC
- ✅ El firewall permite conexiones en el puerto 5000

### Paso 2: Obtener acceso

**Opción A - Código QR (Más rápido):**
1. En tu PC, ve a: `http://localhost:5000/api/qr`
2. Escanea el código QR con tu teléfono
3. Accede automáticamente

**Opción B - URL directa:**
1. Mira la IP mostrada en la consola (ejemplo: `192.168.1.100`)
2. En tu teléfono, abre el navegador
3. Ve a: `http://[IP]:5000` (ejemplo: `http://192.168.1.100:5000`)

---

## 🎓 Uso del Sistema Móvil

### Pantalla Principal

```
┌─────────────────────────────┐
│    🎓 CLASS VISION          │
│    Universidad Nur          │
├─────────────────────────────┤
│  📊 Estado del Sistema      │
│  ┌───────┐  ┌───────┐      │
│  │   0   │  │   0   │      │
│  └───────┘  └───────┘      │
│  Estudiantes  Reconocidos   │
├─────────────────────────────┤
│  📸 Control de Asistencia   │
│  [Seleccionar materia ▼]    │
│  [▶️ Iniciar Asistencia]    │
├─────────────────────────────┤
│  ⚡ Acciones Rápidas        │
│  [📋 Ver Historial]         │
│  [🔄 Actualizar Datos]      │
└─────────────────────────────┘
```

### Tomar Asistencia

1. **Seleccionar materia** del dropdown
2. Presionar **"▶️ Iniciar Asistencia"**
3. El sistema comenzará a reconocer rostros
4. Ver estudiantes reconocidos en tiempo real
5. Presionar **"⏹️ Detener Asistencia"** al finalizar

### Visualización en Tiempo Real

Durante la toma de asistencia:
- 📊 **Estado**: Muestra "Tomando asistencia: [Materia]"
- 🔢 **Contador**: Actualiza el número de reconocidos
- ✅ **Lista**: Muestra nombres de estudiantes reconocidos
- 🔄 **Auto-refresh**: Se actualiza cada 2 segundos

---

## 🔧 Configuración Avanzada

### Cambiar Puerto

Edita `mobile_server.py`:

```python
# Línea final del archivo
start_server(port=8080, debug=False)  # Cambiar 5000 a otro puerto
```

### Permitir Acceso Externo

Por defecto, el servidor acepta conexiones desde cualquier dispositivo en tu red local. 

**⚠️ Seguridad**: No expongas el servidor a internet sin autenticación.

### Configurar Firewall (Windows)

```powershell
# Permitir puerto 5000 en Windows Firewall
netsh advfirewall firewall add rule name="CLASS VISION Mobile" dir=in action=allow protocol=TCP localport=5000
```

---

## 🛠️ Solución de Problemas

### ❌ "No puedo conectar desde mi teléfono"

**Solución:**
1. Verifica que ambos dispositivos estén en la misma red WiFi
2. Comprueba que el servidor esté corriendo (ver consola del PC)
3. Desactiva temporalmente el firewall para probar
4. Prueba con la IP directa en lugar del QR

### ❌ "El QR no funciona"

**Solución:**
1. Asegúrate de tener `qrcode[pil]` instalado: `pip install qrcode[pil]`
2. Usa la URL directa como alternativa
3. Regenera el QR accediendo a `/api/qr`

### ❌ "Error al iniciar asistencia"

**Solución:**
1. Verifica que la cámara esté conectada al PC
2. Asegúrate de que no hay otra app usando la cámara
3. Comprueba que la materia seleccionada exista
4. Revisa los logs en la consola del servidor

### ❌ "Los estudiantes no se reconocen"

**Solución:**
1. Verifica que el modelo esté entrenado (`Trainner.yml` existe)
2. Asegúrate de tener buena iluminación
3. Comprueba que los estudiantes estén registrados
4. Ajusta el threshold de confianza en `config/default_config.json`

---

## 📊 API REST Endpoints

### GET `/api/subjects`
Obtiene lista de materias disponibles

```json
{
  "subjects": ["MATEMATICA", "FISICA", "QUIMICA"]
}
```

### GET `/api/students`
Obtiene lista de estudiantes registrados

```json
{
  "students": [...],
  "total": 45
}
```

### POST `/api/start-attendance`
Inicia toma de asistencia

```json
{
  "subject": "MATEMATICA"
}
```

### POST `/api/stop-attendance`
Detiene toma de asistencia

```json
{
  "success": true,
  "recognized": ["Juan Perez", "Maria Lopez"]
}
```

### GET `/api/status`
Estado actual del sistema

```json
{
  "camera_active": true,
  "current_subject": "MATEMATICA",
  "recognized_count": 12,
  "recognized_students": [...]
}
```

### GET `/api/attendance-history/<subject>`
Historial de asistencia por materia

```json
{
  "subject": "MATEMATICA",
  "records": [...],
  "total": 150
}
```

---

## 🔐 Seguridad y Privacidad

### ✅ Buenas Prácticas

- 🔒 **Red privada**: Usa solo en redes WiFi privadas y seguras
- 🚫 **No internet**: No expongas el servidor directamente a internet
- 🔑 **Contraseñas**: Considera agregar autenticación para producción
- 📱 **HTTPS**: Para mayor seguridad, configura SSL/TLS
- 🗑️ **Datos sensibles**: No almacenes contraseñas o datos bancarios

### ⚠️ Advertencias

- El sistema está diseñado para uso en redes locales privadas
- No incluye autenticación por defecto (agrégala si es necesario)
- Los datos de asistencia se almacenan localmente en el PC

---

## 📈 Monitoreo y Logs

### Ver Logs del Servidor

Los logs se muestran en la consola donde ejecutas el servidor:

```
🎓 UNIVERSIDAD NUR - CLASS VISION
📱 Servidor Móvil Iniciado
════════════════════════════════════

🌐 Accede desde tu smartphone:
   http://192.168.1.100:5000

📱 Escanea el código QR:
   http://192.168.1.100:5000/api/qr
```

### Monitorear Actividad

```python
# En mobile_server.py, activar modo debug
start_server(port=5000, debug=True)
```

---

## 🆘 Soporte

### Contacto
- **Institución**: Universidad Nur
- **Sistema**: CLASS VISION v2.1.0
- **Desarrolladores**: Itzan Valdivia, Ender Rosales

### Reportar Problemas

1. Describe el problema detalladamente
2. Incluye la versión del sistema
3. Adjunta logs de error si es posible
4. Menciona tu sistema operativo y versión de Python

---

## 📝 Changelog v2.1.0

### Nuevas Características
- ✨ Control remoto desde smartphone
- 📱 Interfaz móvil responsive
- 🔄 Actualización en tiempo real
- 📊 Dashboard de estadísticas
- 🎯 QR code para acceso rápido
- 🎓 Branding Universidad Nur
- 🚀 Launcher automático

### Mejoras
- 🔧 API REST completa
- 📡 WebSockets para updates en tiempo real
- 🎨 UI moderna y profesional
- 📱 Optimización móvil

---

## 🎯 Roadmap Futuro

- [ ] Autenticación de usuarios
- [ ] Notificaciones push
- [ ] Modo offline
- [ ] Exportación a Excel desde móvil
- [ ] Múltiples cámaras simultáneas
- [ ] Dashboard con gráficos avanzados
- [ ] Integración con sistemas LMS
- [ ] App nativa para iOS/Android

---

**Universidad Nur © 2025** | CLASS VISION - Sistema de Control de Asistencia
