"""
Explica qué tablas se usan en cada parte del sistema
"""

print("\n" + "="*100)
print("📚 ¿POR QUÉ ALGUNAS TABLAS ESTÁN VACÍAS?")
print("="*100)

print("""
Las tablas vacías se llenarán cuando USES EL SISTEMA:

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ TABLAS CON DATOS (Ya migradas desde JSON)                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

✅ personal_admin (3 usuarios)      → Ya tienes: admin, Ing. Molina, tata
✅ estudiantes (17 estudiantes)     → Ya tienes: lola, ENDER, EMMA, etc.
✅ materias (2 materias)            → Ya tienes: PROGRAMACIÓN IV, SISTEMAS OPERATIVOS II
✅ inscripciones (2 inscripciones)  → Ya tienes: Alberto→PRO IV, Ender→SIS OP II
✅ sesiones_activas (3 sesiones)    → Se crean cuando haces login
✅ badges (5 badges)                → Sistema de gamificación preconfigurado
✅ sys_config (2 configs)           → Configuración del sistema


┌─────────────────────────────────────────────────────────────────────────────────────┐
│ TABLAS VACÍAS (Se llenan cuando USES el sistema)                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

❌ asistencia_log (0 registros)
   ↳ Se llenará cuando: Tomes asistencia con reconocimiento facial o QR
   ↳ Guarda: Quién asistió, a qué hora, si llegó tarde, presente/ausente
   ↳ Cómo usarla: 
      1. Ir a "Tomar Asistencia" en el dashboard
      2. Usar cámara para reconocer caras
      3. O escanear código QR del estudiante
      → Cada asistencia crea 1 registro aquí

❌ codigos_temporales (0 registros)
   ↳ Se llenará cuando: Generes códigos QR para asistencia virtual
   ↳ Guarda: Códigos temporales válidos solo por X tiempo
   ↳ Cómo usarla:
      1. Click en "Generar Código QR" en materia
      2. El código se crea automáticamente
      3. Estudiantes lo escanean para marcar asistencia
      → Cada código QR genera 1 registro aquí

❌ asistencia_virtual (0 registros)
   ↳ Se llenará cuando: Estudiantes usen códigos QR para marcar asistencia
   ↳ Guarda: IP, plataforma, duración, capturas de pantalla
   ↳ Relacionada con: codigos_temporales + asistencia_log

❌ justificaciones (0 registros)
   ↳ Se llenará cuando: Estudiantes suban justificantes de ausencia
   ↳ Guarda: Motivo, documento médico, fechas, estado (pendiente/aprobado)
   ↳ Cómo usarla:
      1. Estudiante falta a clase
      2. Sube certificado médico
      3. Docente aprueba/rechaza
      → Cada justificante crea 1 registro aquí

❌ tutores (0 registros)
   ↳ Se llenará cuando: Registres padres/tutores de estudiantes
   ↳ Guarda: Nombre, CI, teléfono, email, QR para recoger estudiante
   ↳ Cómo usarla:
      1. Ir a perfil de estudiante
      2. Click "Agregar Tutor"
      3. Llenar formulario
      → Cada padre/tutor crea 1 registro aquí

❌ audit_log (0 registros)
   ↳ Se llenará cuando: Hagas CUALQUIER acción en el sistema
   ↳ Guarda: Quién hizo qué, cuándo, IP, cambios antes/después
   ↳ Ejemplo: "admin eliminó materia MATEMÁTICAS a las 15:30"
   → Se llena automáticamente en segundo plano

❌ notificaciones_internas (0 registros)
   ↳ Se llenará cuando: El sistema genere alertas
   ↳ Guarda: Notificaciones para docentes/estudiantes
   ↳ Ejemplo: "Alberto tiene 3 faltas consecutivas"
   → El sistema las crea automáticamente

❌ alertas_desercion (0 registros)
   ↳ Se llenará cuando: IA detecte riesgo de deserción
   ↳ Guarda: Estudiantes con muchas faltas, probabilidad de abandono
   ↳ Cómo funciona:
      → Sistema analiza patrones de asistencia
      → Detecta estudiantes en riesgo
      → Genera alerta para intervención

❌ estadisticas_diarias (0 registros)
   ↳ Se llenará cuando: Pase el día y sistema calcule stats
   ↳ Guarda: Resumen diario de asistencias por materia
   ↳ Ejemplo: "21-Nov-2025: 15 presentes, 2 ausentes, 85% asistencia"
   → Se calcula automáticamente cada noche

❌ ranking_mensual (0 registros)
   ↳ Se llenará cuando: Termine el mes
   ↳ Guarda: Top estudiantes con mejor asistencia
   ↳ Usado para: Gamificación, premios, reconocimientos

❌ estudiantes_badges (0 registros)
   ↳ Se llenará cuando: Estudiante gane un badge
   ↳ Guarda: Qué badge ganó, cuándo, por qué
   ↳ Ejemplo: "Alberto ganó badge 'Puntual' por 30 días sin tardanza"

❌ reportes_generados (0 registros)
   ↳ Se llenará cuando: Generes reportes Excel/PDF
   ↳ Guarda: Archivo, fecha, filtros usados
   ↳ Cómo usarla:
      1. Click "Exportar Reporte"
      2. Seleccionar formato (Excel/PDF)
      3. Sistema guarda registro del reporte

❌ asistente_historial (0 registros)
   ↳ Se llenará cuando: Uses el asistente por voz
   ↳ Guarda: Comandos de voz, respuestas, acciones ejecutadas
   ↳ Ejemplo: "Mostrar asistencia de hoy" → ejecuta query


┌─────────────────────────────────────────────────────────────────────────────────────┐
│ VISTAS (Queries SQL preconfiguradas - Calculan datos en tiempo real)               │
└─────────────────────────────────────────────────────────────────────────────────────┘

📊 vista_dashboard_docente (2 registros)
   ↳ Muestra: Materias del docente con estadísticas
   ↳ Tiene 2 registros porque hay 2 materias
   ↳ Se usa en: Dashboard principal

📊 vista_estadisticas_estudiante (17 registros)
   ↳ Muestra: Stats de cada estudiante (puntos, badges, asistencias)
   ↳ Tiene 17 registros porque hay 17 estudiantes
   ↳ Se usa en: Perfil de estudiante, rankings

📊 vista_alertas_activas (0 registros)
   ↳ Muestra: Estudiantes en riesgo de deserción
   ↳ Vacía porque nadie ha faltado aún
   ↳ Se llenará cuando: Haya estudiantes con muchas faltas


┌─────────────────────────────────────────────────────────────────────────────────────┐
│ ¿CÓMO EMPEZAR A USAR EL SISTEMA?                                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

PASO 1: Iniciar servidor
   python mobile_server.py

PASO 2: Login
   http://127.0.0.1:5000/login
   Usuario: admin
   Password: admin123

PASO 3: Tomar primera asistencia
   Dashboard → Click materia → "Tomar Asistencia"
   → Esto llenará: asistencia_log, audit_log, estadisticas_diarias

PASO 4: Ver dashboard actualizado
   → Verás: "1 asistencia hoy", porcentajes, gráficos

¡Las tablas se llenan AUTOMÁTICAMENTE cuando uses el sistema! 🎉
""")

print("\n" + "="*100 + "\n")
