# 🚀 INICIO RÁPIDO - CLASS VISION

## Opción 1: Script Automático (RECOMENDADO)

```powershell
python start_system.py
```

Este script automáticamente:
- ✅ Verifica Python y dependencias
- ✅ Verifica conexión a PostgreSQL
- ✅ Inicializa datos por defecto
- ✅ Inicia el servidor

## Opción 2: Manual

### Paso 1: Activar entorno virtual
```powershell
.venv\Scripts\Activate.ps1
```

### Paso 2: Inicializar datos
```powershell
python init_data.py
```

### Paso 3: Iniciar servidor
```powershell
python mobile_server.py
```

## 🌐 Acceder al Sistema

**URL:** http://localhost:5000/login

**Credenciales por defecto:**
- **Docente:** username=`docente` password=`docente123`
- **Admin:** username=`admin` password=`admin123`

## 📋 Páginas Disponibles

1. **Login** - http://localhost:5000/login
2. **Dashboard** - http://localhost:5000/dashboard
3. **Materias** - http://localhost:5000/materias
4. **Estudiantes** - http://localhost:5000/estudiantes
5. **Tomar Asistencia** - http://localhost:5000/tomar-asistencia
6. **Códigos QR** - http://localhost:5000/codigos-qr
7. **Reportes** - http://localhost:5000/reportes
8. **Configuración** - http://localhost:5000/configuracion

## 🧪 Probar Endpoints

```powershell
python test_backend.py
```

## 📚 Documentación Completa

- **GUIA_PRUEBA_COMPLETA.md** - Guía paso a paso
- **BACKEND_UPDATE_SUMMARY.md** - Lista de endpoints
- **RESUMEN_ACTUALIZACION_BACKEND.md** - Resumen de cambios

## ❓ Problemas Comunes

### "No se puede conectar a PostgreSQL"
```powershell
# Verificar que está corriendo
Get-Service postgresql*

# Verificar .env
cat .env
```

### "ModuleNotFoundError"
```powershell
# Instalar dependencias
pip install -r requirements.txt
```

### "Puerto 5000 en uso"
```powershell
# Cambiar puerto en mobile_server.py línea final:
# app.run(debug=True, host='0.0.0.0', port=5001)
```

## 🎯 Flujo de Prueba Rápida

1. Login con `docente` / `docente123`
2. Ir a Materias → Crear materia
3. Ir a Estudiantes → Registrar estudiante (con foto de cámara)
4. Ir a Tomar Asistencia → Iniciar asistencia
5. Marcar presente/ausente/tardanza
6. Finalizar y guardar

## 📊 Estado del Sistema

| Componente | Estado | Notas |
|------------|--------|-------|
| Frontend | ✅ 100% | 8 páginas completas |
| Backend API | ✅ 71% | 17/24 endpoints |
| Autenticación | ✅ 100% | PostgreSQL |
| Base de datos | ✅ 100% | 20 tablas |
| Reconocimiento facial | ⚠️ Simulado | Requiere implementación |
| Reportes | ⚠️ Parcial | Estructura lista |
| Gamificación | ❌ Pendiente | Badges creados |

## 🔐 Seguridad

- Tokens expiran en 8 horas
- Passwords con SHA-256
- CORS configurado
- Validación en cada endpoint

## 💡 Tips

1. **Primera vez:** Ejecuta `python start_system.py`
2. **Testing:** Usa `python test_backend.py`
3. **Desarrollo:** Activa debug mode en mobile_server.py
4. **Producción:** Cambiar SECRET_KEY y usar HTTPS

---

**¿Necesitas ayuda?** Revisa GUIA_PRUEBA_COMPLETA.md para instrucciones detalladas.
