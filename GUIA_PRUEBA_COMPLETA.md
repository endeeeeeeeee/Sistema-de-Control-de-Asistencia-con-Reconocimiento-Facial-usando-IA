# GUÍA DE PRUEBA DEL SISTEMA - CLASS VISION

## 🚀 Pasos para Probar el Sistema Completo

### 1. Preparar el Entorno

```powershell
# Activar entorno virtual (si no está activo)
.venv\Scripts\Activate.ps1

# Verificar que PostgreSQL está corriendo
# El servidor debe estar en localhost:5501
```

### 2. Inicializar Base de Datos

```powershell
# Crear datos iniciales (configuración, badges, usuarios)
python init_data.py
```

Esto creará:
- ✅ Configuración del sistema
- ✅ 5 badges por defecto
- ✅ Usuario admin (username: `admin`, password: `admin123`)
- ✅ Usuario docente demo (username: `docente`, password: `docente123`)

### 3. Iniciar el Servidor

```powershell
# Iniciar servidor Flask
python mobile_server.py
```

El servidor estará disponible en: `http://localhost:5000`

### 4. Probar con el Navegador

#### 4.1. Login
1. Abrir navegador en: `http://localhost:5000/login`
2. Ingresar credenciales:
   - **Username:** `docente`
   - **Password:** `docente123`
3. Click en "Iniciar Sesión"

#### 4.2. Dashboard
- Verás el dashboard con estadísticas
- Panel izquierdo con navegación
- Tarjetas de resumen (materias, estudiantes, asistencias)

#### 4.3. Materias
1. Click en "Materias" en el menú lateral
2. Click en "Nueva Materia" (botón azul)
3. Completar formulario:
   - Código: `MAT101`
   - Nombre: `Matemáticas I`
   - Nivel: `1er Semestre`
   - Seleccionar días (Lunes, Miércoles, Viernes)
   - Hora inicio: `08:00`
   - Hora fin: `10:00`
   - Tolerancia: `15 minutos`
4. Click en "Guardar"

#### 4.4. Estudiantes
1. Click en "Estudiantes" en el menú lateral
2. Click en "Nuevo Estudiante"
3. Completar datos:
   - Código: `EST001`
   - Nombre: `Juan Pérez`
   - CI: `12345678`
   - Email: `juan@example.com`
   - Fecha nacimiento: `2000-01-15`
4. Click en "Capturar Foto" (abrirá cámara web)
5. Tomar foto y click "Usar esta foto"
6. Click en "Registrar"

#### 4.5. Tomar Asistencia
1. Click en "Tomar Asistencia"
2. Seleccionar materia en el dropdown
3. Click en "Iniciar Asistencia"
4. La cámara se activará
5. Los estudiantes aparecerán en la lista (simulado por ahora)
6. Marcar estado: Presente/Ausente/Tardanza
7. Click en "Finalizar y Guardar"

#### 4.6. Códigos QR
1. Click en "Códigos QR"
2. Seleccionar tipo:
   - QR Clase Virtual
   - Código Numérico
   - QR Pickup Guardería
   - Enlace Único
3. Seleccionar materia
4. Establecer duración (minutos)
5. Click en "Generar Código"
6. Se mostrará el código QR generado

#### 4.7. Reportes
1. Click en "Reportes"
2. Seleccionar tipo de reporte:
   - Asistencia General
   - Por Estudiante
   - Por Materia
   - Tardanzas
   - Deserción
   - Ranking
   - Justificaciones
3. Seleccionar formato: PDF o Excel
4. Establecer rango de fechas
5. Click en "Generar Reporte"
6. Se descargará el archivo

#### 4.8. Configuración
1. Click en "Configuración"
2. Cambiar modo de operación:
   - Universidad
   - Colegio
   - Guardería
3. Configurar reglas:
   - Tolerancia de minutos
   - Porcentaje mínimo de asistencia
   - Umbral de deserción
4. Ajustar configuración facial:
   - Umbral de confianza
   - Detectar liveness
   - Guardar fotos de asistencia
5. Personalizar colores (opcional)
6. Click en "Guardar Cambios"

### 5. Probar Endpoints con Script

```powershell
# Ejecutar suite de tests automáticos
python test_backend.py
```

Esto probará:
- ✅ Login de usuario
- ✅ Obtener configuración
- ✅ Obtener materias
- ✅ Obtener estudiantes
- ✅ Estadísticas del dashboard
- ✅ Códigos activos

### 6. Probar con Postman/Insomnia

#### 6.1. Login
```http
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "username": "docente",
  "password": "docente123"
}
```

Respuesta:
```json
{
  "success": true,
  "token": "TOKEN_AQUI",
  "user": {
    "id": 1,
    "username": "docente",
    "full_name": "Profesor Demo",
    "role": "DOCENTE"
  }
}
```

#### 6.2. Obtener Estadísticas (con token)
```http
GET http://localhost:5000/api/stats/dashboard
Authorization: Bearer TOKEN_AQUI
```

#### 6.3. Crear Materia
```http
POST http://localhost:5000/api/teacher/subjects
Authorization: Bearer TOKEN_AQUI
Content-Type: application/json

{
  "codigo_materia": "CS101",
  "nombre": "Programación I",
  "nivel": "1er Semestre",
  "dia_semana": ["LUNES", "MIERCOLES", "VIERNES"],
  "hora_inicio": "08:00:00",
  "hora_fin": "10:00:00",
  "tolerancia_minutos": 15
}
```

#### 6.4. Generar Código QR
```http
POST http://localhost:5000/api/codes/generate
Authorization: Bearer TOKEN_AQUI
Content-Type: application/json

{
  "tipo": "CODIGO_NUMERICO",
  "materia_id": 1,
  "duracion_minutos": 30
}
```

### 7. Verificar Base de Datos

```powershell
# Conectar a PostgreSQL
psql -U postgres -h localhost -p 5501 -d class_vision

# Ver tablas
\dt

# Ver configuración
SELECT * FROM sys_config;

# Ver usuarios
SELECT id, username, nombre_completo, role FROM personal_admin;

# Ver badges
SELECT * FROM badge;

# Ver materias
SELECT * FROM materia;

# Ver estudiantes
SELECT * FROM estudiante;

# Salir
\q
```

## 📋 Checklist de Funcionalidades

### Frontend ✅
- [x] Login responsive con toggle de password
- [x] Dashboard con sidebar y estadísticas
- [x] Gestión de materias (crear, listar)
- [x] Gestión de estudiantes (registrar con foto)
- [x] Tomar asistencia (cámara + lista)
- [x] Generar códigos QR (4 tipos)
- [x] Generar reportes (7 tipos)
- [x] Configuración del sistema (3 modos)

### Backend ✅
- [x] Autenticación con PostgreSQL
- [x] CRUD de materias
- [x] CRUD de estudiantes
- [x] Estadísticas del dashboard
- [x] Generación de códigos QR
- [x] Configuración del sistema
- [x] Endpoints de reportes (estructura)

### Backend ⚠️ (Implementación Parcial)
- [ ] Reconocimiento facial real (actualmente simulado)
- [ ] Generación de reportes con datos reales
- [ ] Sistema de alertas de deserción
- [ ] Gamificación (badges y puntos)
- [ ] Notificaciones a tutores

## 🐛 Problemas Comunes

### Error: "No se puede conectar a PostgreSQL"
```powershell
# Verificar que PostgreSQL está corriendo
Get-Service postgresql*

# Verificar puerto
netstat -an | findstr 5501

# Revisar .env
cat .env
```

### Error: "Token inválido"
- El token expira en 8 horas
- Volver a hacer login para obtener nuevo token

### Error: "Materia no encontrada"
- Verificar que la materia existe y pertenece al docente
- Verificar el id_materia en la base de datos

### Error: "Estudiante ya existe"
- El código_estudiante debe ser único
- Usar otro código o actualizar el existente

## 📊 Datos de Prueba Sugeridos

### Materias
1. Matemáticas I (MAT101) - Lunes/Miércoles 08:00-10:00
2. Física I (FIS101) - Martes/Jueves 10:00-12:00
3. Programación I (CS101) - Lunes/Miércoles/Viernes 14:00-16:00

### Estudiantes
1. Juan Pérez (EST001) - CI: 12345678
2. María García (EST002) - CI: 87654321
3. Carlos López (EST003) - CI: 11223344

### Códigos QR
1. Código numérico para clase presencial (30 min)
2. QR para clase virtual (60 min)
3. QR para pickup guardería (15 min)

## 🔐 Usuarios de Prueba

| Username | Password    | Role    | Descripción              |
|----------|-------------|---------|--------------------------|
| admin    | admin123    | ADMIN   | Administrador del sistema|
| docente  | docente123  | DOCENTE | Profesor de demostración |

## 📝 Notas Importantes

1. **Reconocimiento Facial**: Actualmente retorna datos simulados. Para implementación real, necesitas:
   - Instalar `face-recognition` y `dlib`
   - Entrenar modelo con fotos de estudiantes
   - Guardar vectores en `Estudiante.foto_face_vector`

2. **Reportes**: La estructura está lista pero genera archivos vacíos. Necesitas:
   - Instalar `reportlab` (PDF) o `openpyxl` (Excel)
   - Implementar lógica de consultas y generación

3. **Cámara Web**: Requiere permisos del navegador. Si no funciona:
   - Verificar que el navegador tiene acceso a la cámara
   - Usar HTTPS en producción (HTTP solo funciona en localhost)

4. **Tokens**: Los tokens expiran en 8 horas. En producción considera:
   - Implementar refresh tokens
   - Usar JWT en lugar de tokens aleatorios
   - Agregar rate limiting

## 🎯 Próximos Pasos

1. **Implementar Reconocimiento Facial Real**
   - Integrar `face-recognition` library
   - Entrenar modelo con fotos reales
   - Guardar vectores faciales en PostgreSQL

2. **Completar Generación de Reportes**
   - Implementar consultas SQL complejas
   - Generar PDFs con `reportlab`
   - Generar Excel con `openpyxl`

3. **Sistema de Alertas**
   - Detectar deserción automáticamente
   - Enviar notificaciones a tutores
   - Dashboard de alertas

4. **Gamificación**
   - Sistema de puntos y niveles
   - Asignación automática de badges
   - Ranking mensual

5. **Testing**
   - Crear tests unitarios con `pytest`
   - Tests de integración
   - Tests de carga con `locust`

---

**¡El sistema está listo para probar! 🚀**

Para cualquier problema, revisa:
- `BACKEND_UPDATE_SUMMARY.md` - Resumen de endpoints
- `DISEÑO_BASE_DATOS.md` - Estructura de la base de datos
- Logs del servidor en la terminal

**Fecha:** 2025
**Versión:** 2.1.0
