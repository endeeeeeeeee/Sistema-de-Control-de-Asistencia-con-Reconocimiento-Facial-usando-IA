# 🎉 GUÍA RÁPIDA: PROBAR RECONOCIMIENTO FACIAL EN VIVO

## ✅ Sistema Implementado Exitosamente

### 📋 Estado Actual
- ✅ Servidor corriendo en: **http://localhost:5001**
- ✅ 2 usuarios con fotos faciales y modelos entrenados
- ✅ 1 equipo con 2 miembros
- ✅ Backend completo con endpoints de reconocimiento
- ✅ Frontend con interfaz de sesión en vivo

---

## 🚀 PRUEBA RÁPIDA (3 pasos)

### Paso 1: Verificar Modelos Entrenados
```powershell
Get-ChildItem "TrainingImageLabel" -Filter "*.yml"
```

Deberías ver archivos como:
- `USER-2025-002_model.yml`
- `USER-2025-003_model.yml`

### Paso 2: Abrir Sesión de Asistencia

**Opción A: URL Directa**
```
http://localhost:5001/sesion-asistencia?equipo_id=5
```

**Opción B: Desde el Dashboard**
1. Ir a: http://localhost:5001/dashboard
2. Seleccionar tu equipo
3. Agregar botón "📹 Iniciar Sesión"

### Paso 3: Probar Reconocimiento
1. Clic en "▶ Iniciar Sesión"
2. Permitir acceso a la cámara
3. Ponerte frente a la cámara
4. Esperar 2-5 segundos
5. ¡Deberías aparecer en la lista de reconocidos! ✅

---

## 🧪 PRUEBA MANUAL CON POSTMAN/CURL

### 1. Obtener Token (Login)
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tu@email.com", "password":"tu_password"}'
```

Guarda el `token` de la respuesta.

### 2. Iniciar Sesión de Asistencia
```bash
curl -X POST http://localhost:5001/api/sesiones/iniciar \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"equipo_id":5, "duracion_minutos":30}'
```

Guarda el `sesion_id` de la respuesta.

### 3. Obtener Reconocimientos
```bash
curl -X GET http://localhost:5001/api/sesiones/SESION_ID/reconocimientos \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

### 4. Detener Sesión
```bash
curl -X POST http://localhost:5001/api/sesiones/SESION_ID/detener \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## 📊 VERIFICAR EN LA BASE DE DATOS

### Sesiones Activas
```sql
SELECT * FROM codigos_temporales 
WHERE tipo = 'SESION_ASISTENCIA' 
AND usado = false 
AND NOW() < expira_en;
```

### Asistencias Registradas Hoy
```sql
SELECT 
    u.codigo_usuario,
    u.nombre_completo,
    a.hora_entrada,
    a.metodo_entrada,
    a.confianza_reconocimiento
FROM asistencia_log a
JOIN membresias m ON a.membresia_id = m.id
JOIN usuarios u ON m.usuario_id = u.id
WHERE a.fecha = CURRENT_DATE
ORDER BY a.hora_entrada DESC;
```

### Comando PowerShell:
```powershell
psql -U postgres -h localhost -p 5501 -d class_vision -c "SELECT u.codigo_usuario, u.nombre_completo, a.hora_entrada, a.confianza_reconocimiento FROM asistencia_log a JOIN membresias m ON a.membresia_id = m.id JOIN usuarios u ON m.usuario_id = u.id WHERE a.fecha = CURRENT_DATE ORDER BY a.hora_entrada DESC;"
```

---

## 🐛 TROUBLESHOOTING

### ❌ "Cámara no se activa"
**Solución:**
1. Verificar permisos del navegador (icono de cámara en la barra de direcciones)
2. Usar Chrome/Edge (mejor compatibilidad)
3. Verificar que otra app no esté usando la cámara

### ❌ "No reconoce rostros"
**Causas posibles:**
1. **Modelos no entrenados:** Verificar archivos `.yml` en `TrainingImageLabel/`
2. **Poca iluminación:** Mejorar luz de la habitación
3. **Umbral muy estricto:** Cambiar `confidence < 70` a `confidence < 85`

**Verificar modelos:**
```powershell
Get-ChildItem "TrainingImageLabel" -Filter "*.yml" | ForEach-Object { 
    Write-Host "$($_.Name) - Tamaño: $($_.Length) bytes" 
}
```

Si los archivos son muy pequeños (<1KB), reentrenar:
```powershell
python trainImage.py
```

### ❌ "Error al iniciar sesión"
**Verificar:**
1. Usuario es líder del equipo
2. No hay sesión activa previa
3. BD PostgreSQL corriendo en puerto 5501

```powershell
# Verificar BD
psql -U postgres -h localhost -p 5501 -d class_vision -c "SELECT 1;"

# Verificar rol del usuario
psql -U postgres -h localhost -p 5501 -d class_vision -c "SELECT u.nombre_completo, m.rol FROM membresias m JOIN usuarios u ON m.usuario_id = u.id WHERE m.equipo_id = 5;"
```

### ❌ "Reconoce personas equivocadas"
**Solución:**
1. Aumentar cantidad de fotos de entrenamiento (50 → 100)
2. Disminuir umbral: `confidence < 70` → `confidence < 60`
3. Mejorar calidad de fotos (mejor iluminación, diferentes ángulos)

---

## 📸 CAPTURA DE PANTALLA ESPERADA

```
┌──────────────────────────────────────────────┐
│ 📹 Sesión de Asistencia                      │
│ Equipo Demo                        [← Volver]│
└──────────────────────────────────────────────┘

┌────────────────────┐  ┌─────────────────────┐
│ 🟢 Sesión Activa   │  │ ✅ Reconocidos      │
│                    │  │                     │
│  [VIDEO EN VIVO]   │  │  [2] Presentes      │
│                    │  │  [2] Miembros       │
│                    │  │                     │
│  [⏹ Detener]       │  │     05:23           │
│                    │  │                     │
│                    │  │ ┌─────────────────┐ │
│                    │  │ │✅ Juan Pérez     │ │
│                    │  │ │  01:15:32        │ │
│                    │  │ │  [95.6%]         │ │
│                    │  │ └─────────────────┘ │
│                    │  │                     │
│                    │  │ ┌─────────────────┐ │
│                    │  │ │✅ María García   │ │
│                    │  │ │  01:15:28        │ │
│                    │  │ │  [92.3%]         │ │
│                    │  │ └─────────────────┘ │
└────────────────────┘  └─────────────────────┘
```

---

## 🎯 CHECKLIST DE PRUEBA

- [ ] Servidor corriendo en puerto 5001
- [ ] Login exitoso en el dashboard
- [ ] Acceso a la URL de sesión con equipo_id
- [ ] Botón "Iniciar Sesión" visible
- [ ] Permiso de cámara otorgado
- [ ] Video mostrándose en vivo
- [ ] Reconocimiento detectando tu rostro
- [ ] Nombre apareciendo en lista de reconocidos
- [ ] Confianza >90% mostrada
- [ ] Timer actualizándose
- [ ] Verificación en BD exitosa
- [ ] Botón "Detener" funcional
- [ ] No permite duplicados (intentar 2 veces)

---

## 📝 SIGUIENTE PASO

**Agregar botón al Dashboard:**

Editar `templates/equipo.html` o `templates/dashboard_flexible.html`:

```html
<!-- En la sección de acciones del equipo -->
<button onclick="abrirSesionAsistencia(${equipoId})" 
        class="btn btn-success">
    📹 Iniciar Sesión de Asistencia
</button>

<script>
function abrirSesionAsistencia(equipoId) {
    window.location.href = `/sesion-asistencia?equipo_id=${equipoId}`;
}
</script>
```

---

## 📞 SOPORTE

Si algo no funciona:
1. Revisar consola del navegador (F12)
2. Revisar logs del servidor (terminal)
3. Verificar archivos de documentación:
   - `RECONOCIMIENTO_FACIAL_VIVO.md`
   - `README.md`

**Servidor funcionando:** ✅
**Puerto:** 5001
**URL Dashboard:** http://localhost:5001/dashboard
**URL Sesión:** http://localhost:5001/sesion-asistencia?equipo_id=5

¡LISTO PARA PROBAR! 🚀
