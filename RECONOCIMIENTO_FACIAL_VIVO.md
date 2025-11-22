# NUEVA FUNCIONALIDAD: RECONOCIMIENTO FACIAL EN VIVO

## ✅ Implementado

Se ha implementado el sistema completo de reconocimiento facial en vivo para marcar asistencia automáticamente.

## 🎯 Características

### 1. **Sesiones de Asistencia en Vivo**
- El líder puede iniciar una sesión de asistencia para su equipo
- La sesión tiene duración configurable (por defecto 30 minutos)
- Solo puede haber una sesión activa por equipo

### 2. **Reconocimiento Facial Automático**
- Activa la cámara del navegador
- Captura frames cada 2 segundos
- Detecta rostros usando Haar Cascade
- Compara con modelos entrenados en `TrainingImageLabel/`
- Umbral de confianza: 70% (configurable)

### 3. **Registro Automático de Asistencia**
- Marca asistencia automática al reconocer un rostro
- Evita registros duplicados (1 por día)
- Guarda confianza del reconocimiento en la BD
- Muestra lista en tiempo real de reconocidos

## 📁 Archivos Creados/Modificados

### Backend (`api_routes_flexible.py`)
```
POST /api/sesiones/iniciar
- Crea sesión de asistencia
- Solo líderes pueden iniciar
- Retorna sesion_id y código único

POST /api/sesiones/{sesion_id}/detener
- Finaliza sesión activa
- Marca como usada en BD

GET /api/sesiones/{sesion_id}/reconocimientos
- Obtiene lista de reconocidos en la sesión

POST /api/facial/reconocer-frame
- Recibe imagen base64 de la cámara
- Detecta rostros con OpenCV
- Compara con modelos .yml
- Registra asistencia si hay match
```

### Frontend (`templates/sesion_asistencia.html`)
- Interfaz moderna con video en vivo
- Timer de sesión
- Lista de reconocidos en tiempo real
- Estadísticas (presentes vs total miembros)
- Indicador de confianza del reconocimiento

### Servidor (`mobile_server.py`)
```
GET /sesion-asistencia
- Ruta para acceder a la página
- Query param: ?equipo_id={id}
```

## 🚀 Cómo Usar

### Para el Líder:

1. **Desde el Dashboard:**
   ```javascript
   // Agregar botón en la página del equipo
   function abrirSesionAsistencia(equipoId) {
       window.location.href = `/sesion-asistencia?equipo_id=${equipoId}`;
   }
   ```

2. **En la Página de Sesión:**
   - Clic en "▶ Iniciar Sesión"
   - Permitir acceso a la cámara
   - El reconocimiento comienza automáticamente
   - Ver lista de reconocidos en tiempo real
   - Clic en "⏹ Detener Sesión" al finalizar

### Para los Miembros:

1. Simplemente estar frente a la cámara
2. El sistema detecta y reconoce automáticamente
3. Aparecen en la lista de "Reconocidos" con:
   - ✅ Icono de confirmación
   - Nombre completo
   - Hora de registro
   - % de confianza del reconocimiento

## 🔧 Configuración

### Ajustar Umbral de Confianza
En `api_routes_flexible.py`, línea donde dice `confidence < 70`:
```python
if confidence < mejor_confianza and confidence < 70:  # Cambiar este valor
    mejor_confianza = confidence
    mejor_match = miembro
```

**Valores recomendados:**
- `50`: Muy estricto (menos falsos positivos, más falsos negativos)
- `70`: Balanceado (recomendado) ⭐
- `90`: Permisivo (más falsos positivos, menos falsos negativos)

### Ajustar Frecuencia de Reconocimiento
En `templates/sesion_asistencia.html`, línea del `setInterval`:
```javascript
reconocimientoInterval = setInterval(async () => {
    await capturarYReconocer();
}, 2000); // Cambiar este valor (en milisegundos)
```

**Valores recomendados:**
- `1000ms (1s)`: Muy rápido (consume más recursos)
- `2000ms (2s)`: Balanceado (recomendado) ⭐
- `5000ms (5s)`: Lento (consume menos recursos)

### Duración de Sesión
Al iniciar sesión:
```javascript
body: JSON.stringify({
    equipo_id: parseInt(equipoId),
    duracion_minutos: 30  // Cambiar aquí
})
```

## 📊 Base de Datos

### Tabla: `asistencia_log`
```sql
INSERT INTO asistencia_log (
    membresia_id, 
    metodo_entrada,          -- 'facial_automatico'
    estado,                  -- 'presente'
    confianza_reconocimiento -- Porcentaje de confianza
)
```

### Tabla: `codigos_temporales`
```sql
INSERT INTO codigos_temporales (
    codigo,         -- 'SESION-{random}'
    tipo,           -- 'SESION_ASISTENCIA'
    equipo_id,
    expira_en,      -- NOW() + duracion_minutos
    usado           -- false hasta que se detenga
)
```

## 🎨 Interfaz

### Colores
- **Activo:** 🟢 Verde (`#10b981`)
- **Inactivo:** 🔴 Rojo (`#ef4444`)
- **Primary:** 🔵 Índigo (`#6366f1`)

### Secciones
1. **Header:** Nombre del equipo + botón volver
2. **Cámara:** Video en vivo + controles
3. **Lista:** Reconocidos en tiempo real
4. **Stats:** Contador de presentes vs total

## 🐛 Troubleshooting

### La cámara no se activa
- Verificar permisos del navegador
- Debe ser HTTPS o localhost
- Revisar consola del navegador (F12)

### No reconoce rostros
1. Verificar que existan modelos `.yml` en `TrainingImageLabel/`
2. Verificar nombre de archivos: `{codigo_usuario}_model.yml`
3. Verificar que `haarcascade_frontalface_default.xml` existe
4. Aumentar umbral de confianza (70 → 80)

### Reconoce rostros equivocados
1. Reentrenar modelos con más fotos
2. Disminuir umbral de confianza (70 → 60)
3. Mejorar iluminación de la sala

### Reconocimiento muy lento
1. Reducir resolución de video (1280x720 → 640x480)
2. Aumentar intervalo de captura (2s → 5s)
3. Optimizar modelos (menos archivos .yml)

## 📱 Responsive

- ✅ Desktop: Grid 2 columnas (cámara + lista)
- ✅ Mobile: 1 columna apilada
- ✅ Botones grandes para touch
- ✅ Video adaptativo

## 🔐 Seguridad

- ✅ Requiere token JWT para iniciar sesión
- ✅ Solo líderes pueden crear sesiones
- ✅ Validación de sesión en cada reconocimiento
- ✅ Prevención de duplicados (1 asistencia/día)
- ✅ Expiración automática de sesiones

## 🚦 Estado Actual

- ✅ Backend completo
- ✅ Frontend completo
- ✅ Integración con BD
- ✅ Reconocimiento facial funcionando
- ⏳ **Pendiente:** Agregar botón en dashboard para abrir sesión

## 📝 Siguiente Paso

Agregar al archivo `dashboard_flexible.html` (o en la página del equipo):

```html
<!-- Botón para iniciar sesión de asistencia -->
<button onclick="abrirSesionAsistencia(EQUIPO_ID)" class="btn-success">
    📹 Iniciar Sesión de Asistencia
</button>

<script>
function abrirSesionAsistencia(equipoId) {
    window.location.href = `/sesion-asistencia?equipo_id=${equipoId}`;
}
</script>
```

## 🎉 Listo para Usar!

El sistema está completamente funcional. Solo falta integrar el botón en el dashboard para que los líderes puedan acceder fácilmente a la sesión de asistencia.

**URL de prueba:**
```
http://localhost:5001/sesion-asistencia?equipo_id=1
```

(Reemplazar `1` con el ID real del equipo)
