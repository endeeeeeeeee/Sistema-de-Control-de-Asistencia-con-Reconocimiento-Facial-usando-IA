# 🗄️ DISEÑO DE BASE DE DATOS - CLASS VISION

## 📋 ÍNDICE
1. [Contexto del Sistema](#contexto)
2. [Modos de Operación](#modos)
3. [Entidades Principales](#entidades)
4. [Funcionalidades por Modo](#funcionalidades)
5. [Estructura de Tablas](#tablas)
6. [Relaciones](#relaciones)
7. [Constraints y Validaciones](#constraints)

---

## 🎯 CONTEXTO DEL SISTEMA {#contexto}

**Sistema de Control de Asistencia con Reconocimiento Facial**

### Usuarios del Sistema:
- **Administradores del Sistema**: Control total
- **Docentes/Profesores**: Gestionan sus materias y estudiantes
- **Estudiantes**: Registran asistencia
- **Tutores/Padres**: Recogen estudiantes (modo guardería/colegio)

### Métodos de Registro de Asistencia:
1. **Reconocimiento Facial** (Cámara + IA)
2. **Código QR** (Escaneo de código temporal)
3. **Manual** (Docente marca manualmente)

---

## 🎓 MODOS DE OPERACIÓN {#modos}

### 1. MODO UNIVERSIDAD
- Estudiantes adultos e independientes
- Sin necesidad de tutores
- Enfoque en control académico
- Notificaciones solo a estudiantes y docentes
- Asistencia por reconocimiento facial o QR

### 2. MODO COLEGIO
- Estudiantes menores de edad
- **Requiere tutores/padres registrados**
- Notificaciones a tutores sobre faltas
- Justificaciones médicas con aprobación
- Control más estricto de asistencia

### 3. MODO GUARDERÍA
- Niños pequeños
- **Requiere pickup seguro con QR de tutores**
- Registro de quién recoge al niño y a qué hora
- Notificaciones inmediatas a tutores
- Mayor control de seguridad

---

## 👥 ENTIDADES PRINCIPALES {#entidades}

### 1. PERSONAL_ADMIN (Usuarios del sistema)
**¿Quiénes son?**
- Administradores del sistema
- Docentes/Profesores
- Personal administrativo

**Datos que necesitamos:**
- Usuario y contraseña (login)
- Nombre completo
- Rol (ADMIN_SISTEMA, DOCENTE, ADMINISTRATIVO)
- Email y teléfono
- Vector facial (opcional, para login facial)
- Estado activo/inactivo

### 2. ESTUDIANTES
**¿Quiénes son?**
- Niños (guardería)
- Adolescentes (colegio)
- Adultos (universidad)

**Datos que necesitamos:**
- Código único de estudiante
- Nombre completo, CI, fecha nacimiento
- Email, teléfono, dirección
- Vector facial (OBLIGATORIO para reconocimiento)
- Tutor asignado (OBLIGATORIO en guardería/colegio)
- Puntos acumulados (gamificación)
- Nivel (gamificación)

### 3. TUTORES (Padres/Apoderados)
**Necesario en:** COLEGIO y GUARDERÍA

**Datos que necesitamos:**
- CI (identificación única)
- Nombre completo
- Teléfono, email
- Relación con estudiante (madre, padre, tío, etc.)
- Vector facial (opcional, para pickup facial)
- **QR personalizado** (para pickup en guardería)

### 4. MATERIAS/CLASES
**¿Qué son?**
- Asignaturas que imparte un docente
- Cada materia tiene estudiantes inscritos

**Datos que necesitamos:**
- Código único de materia
- Nombre (ej: "PROGRAMACIÓN IV")
- Descripción
- Nivel (ej: "UNIVERSIDAD", "PRIMARIA")
- Docente asignado
- Días de la semana que se imparte
- Hora de inicio y fin
- Tolerancia de tardanza (minutos)
- Período académico (ej: "2025-2")

### 5. INSCRIPCIONES
**¿Qué es?**
- Relación entre ESTUDIANTE y MATERIA
- Un estudiante puede estar inscrito en varias materias
- Una materia tiene varios estudiantes inscritos

**Datos que necesitamos:**
- Estudiante
- Materia
- Puntos acumulados en esa materia
- Total de asistencias, faltas, tardanzas
- Porcentaje de asistencia
- Estado (ACTIVO, RETIRADO, SUSPENDIDO)

---

## ⚙️ FUNCIONALIDADES POR MODO {#funcionalidades}

### 📝 ASISTENCIA (Todos los modos)

#### Tabla: ASISTENCIA_LOG
**Registra:** Cada vez que un estudiante marca asistencia

**Campos necesarios:**
- ID de inscripción (estudiante + materia)
- Fecha
- Hora de entrada
- Hora de salida (opcional)
- Método usado: `FACIAL`, `QR`, `MANUAL`
- Estado: `PRESENTE`, `AUSENTE`, `TARDANZA`, `JUSTIFICADO`
- Score de liveness (confianza del reconocimiento facial: 0.0 - 1.0)
- IP address (de dónde se conectó)
- Ubicación GPS (opcional)
- ID del código QR usado (si fue por QR)

**Solo para GUARDERÍA:**
- ID del tutor que recogió
- Hora de pickup

---

### 📱 CÓDIGOS QR TEMPORALES

#### Tabla: CODIGOS_TEMPORALES
**¿Para qué?** Generar códigos QR que expiran

**Tipos de códigos:**
1. `QR_CLASE_VIRTUAL` - Para asistencia en clases online
2. `CODIGO_NUMERICO` - Código de 6 dígitos para ingresar manualmente
3. `QR_PICKUP_GUARDERIA` - QR del tutor para recoger al niño
4. `ENLACE_UNICO` - Link único de un solo uso

**Campos necesarios:**
- Código generado (string único)
- Tipo (ver lista arriba)
- Materia asociada (si aplica)
- Fecha válida
- Válido desde (datetime)
- Válido hasta (datetime)
- ¿Ya fue usado?
- ¿Cuántos usos permite? (max_usos)
- ¿Cuántas veces se usó? (usos_actuales)
- Hash de verificación (seguridad)
- Quién lo generó (docente)

---

### 💻 ASISTENCIA VIRTUAL

#### Tabla: ASISTENCIA_VIRTUAL
**¿Para qué?** Registro extra cuando la asistencia fue virtual (con QR)

**Campos necesarios:**
- ID de asistencia_log
- ID del código QR usado
- Plataforma (ZOOM, TEAMS, MEET, etc.)
- Duración en minutos
- ¿Hubo verificación intermitente?
- Cantidad de capturas de pantalla tomadas
- IP address
- User agent (navegador)

---

### 🔔 NOTIFICACIONES

#### Tabla: NOTIFICACIONES_INTERNAS
**¿Para qué?** Avisar a usuarios sobre eventos importantes

**Tipos de notificaciones:**
- `ASISTENCIA` - "Tu hijo faltó hoy"
- `ALERTA` - "3 faltas consecutivas"
- `GAMIFICACION` - "¡Ganaste un badge!"
- `JUSTIFICACION` - "Justificación aprobada"
- `PICKUP` - "Tu hijo fue recogido"
- `SISTEMA` - Avisos generales

**Campos necesarios:**
- Destinatario tipo (DOCENTE, ESTUDIANTE, TUTOR)
- Destinatario ID
- Tipo (ver lista arriba)
- Título
- Mensaje
- Metadata JSON (datos extra)
- ¿Leída? (booleano)
- Fecha de lectura
- Prioridad (NORMAL, ALTA, URGENTE)
- Expira en (fecha)

---

### ⚠️ ALERTAS DE DESERCIÓN (IA)

#### Tabla: ALERTAS_DESERCION
**¿Para qué?** IA detecta estudiantes en riesgo de abandonar

**Campos necesarios:**
- Estudiante
- Nivel de riesgo: `BAJO`, `MEDIO`, `ALTO`, `CRITICO`
- Probabilidad de deserción (0-100%)
- Factores de riesgo (JSON: faltas consecutivas, promedio bajo, etc.)
- Recomendaciones (JSON: acciones sugeridas)
- Estado: `ACTIVA`, `EN_SEGUIMIENTO`, `RESUELTA`, `DESCARTADA`
- Asignado a (orientador/docente)
- Fecha de detección
- Fecha de última actualización

---

### 📄 JUSTIFICACIONES

#### Tabla: JUSTIFICACIONES
**¿Para qué?** Estudiante justifica ausencias

**Tipos:**
- `MEDICO` - Certificado médico
- `PERSONAL` - Asunto personal
- `FAMILIAR` - Emergencia familiar
- `INSTITUCIONAL` - Actividad de la institución
- `OTRO`

**Campos necesarios:**
- Estudiante
- Materia (opcional, puede ser general)
- Fecha inicio - fecha fin (rango de fechas justificadas)
- Motivo (texto)
- Tipo (ver lista arriba)
- URL del documento subido (PDF, imagen)
- Estado: `PENDIENTE`, `APROBADO`, `RECHAZADO`
- Aprobado por (docente)
- Fecha de aprobación
- Comentario del aprobador

---

### 🎮 GAMIFICACIÓN

#### Tabla: BADGES (Insignias/Logros)
**¿Qué son?** Logros que los estudiantes pueden ganar

**Ejemplos:**
- "Asistencia Perfecta" - 30 días sin faltar
- "Puntualidad Extrema" - 30 días sin tardanza
- "Semana Perfecta" - 7 días perfectos
- "Estudiante Estrella" - Mejor del mes
- "En Mejora" - Mejoró su asistencia

**Campos necesarios:**
- Código único
- Nombre
- Descripción
- URL del ícono
- Tipo de condición (ASISTENCIAS, PUNTUALIDAD, MEJORA, etc.)
- Valor de la condición (ej: 30 días)
- Puntos que otorga
- Rareza: `COMUN`, `RARO`, `EPICO`, `LEGENDARIO`
- Activo/inactivo

#### Tabla: ESTUDIANTES_BADGES (Badges ganados)
**¿Qué es?** Registro de qué estudiante ganó qué badge

**Campos necesarios:**
- Estudiante
- Badge
- Fecha de obtención
- Período académico
- Metadata JSON (cómo lo ganó, detalles extra)

#### Tabla: RANKING_MENSUAL
**¿Para qué?** Top de mejores estudiantes cada mes

**Campos necesarios:**
- Año, mes
- Estudiante
- Total de puntos
- Total de asistencias
- Porcentaje de puntualidad
- Badges obtenidos (cantidad)
- Posición en el ranking

---

### 📊 ESTADÍSTICAS

#### Tabla: ESTADISTICAS_DIARIAS
**¿Para qué?** Resumen automático cada día

**Campos necesarios:**
- Fecha
- Materia (opcional, puede ser general)
- Total de estudiantes
- Total presentes
- Total ausentes
- Total tardanzas
- Total justificados
- Total virtuales
- Porcentaje de asistencia
- Porcentaje de puntualidad
- Fecha de cálculo

---

### 🎤 ASISTENTE POR VOZ

#### Tabla: ASISTENTE_HISTORIAL
**¿Para qué?** Guardar comandos de voz ejecutados

**Campos necesarios:**
- Usuario (docente/admin)
- Texto del comando ("Muéstrame asistencia de hoy")
- Tipo de comando (VOZ, TEXTO)
- Intención detectada (CONSULTAR_ASISTENCIA, GENERAR_REPORTE, etc.)
- Entidades extraídas JSON (fecha, materia, etc.)
- Texto de respuesta
- Tipo de respuesta (TEXTO, GRAFICO, TABLA)
- Acciones ejecutadas JSON
- ¿Fue exitoso?
- Mensaje de error (si falló)
- Timestamp
- Duración en ms

---

### 📋 AUDITORÍA

#### Tabla: AUDIT_LOG
**¿Para qué?** Registrar TODAS las acciones del sistema

**Campos necesarios:**
- Usuario tipo (DOCENTE, ADMIN, ESTUDIANTE)
- Usuario ID
- Acción (LOGIN, CREAR, EDITAR, ELIMINAR, APROBAR, etc.)
- Entidad afectada (Materia, Estudiante, etc.)
- ID de la entidad
- Descripción
- Datos anteriores (JSON)
- Datos nuevos (JSON)
- IP address
- User agent
- Timestamp

---

### 📑 REPORTES

#### Tabla: REPORTES_GENERADOS
**¿Para qué?** Historial de reportes exportados

**Tipos:**
- `ASISTENCIA_MENSUAL`
- `ESTUDIANTES_RIESGO`
- `RANKING_MATERIA`
- `JUSTIFICACIONES`
- `BADGES_OTORGADOS`

**Campos necesarios:**
- Tipo (ver lista arriba)
- Nombre del archivo
- Formato (PDF, EXCEL, CSV)
- Filtros aplicados JSON
- Ruta del archivo
- Tamaño en bytes
- Generado por (usuario)
- Fecha de generación
- Expira en (se borra automáticamente)

---

### ⚙️ CONFIGURACIÓN DEL SISTEMA

#### Tabla: SYS_CONFIG
**¿Para qué?** Configuración global del sistema

**Campos necesarios:**
- **Modo de operación**: `UNIVERSIDAD`, `COLEGIO`, `GUARDERIA`
- Nombre de la institución
- Reglas JSON:
  ```json
  {
    "faltas_alerta": 3,
    "tolerancia_minutos": 10,
    "puntos_por_asistencia": 10,
    "puntos_por_puntualidad": 5,
    "gamificacion_habilitada": true,
    "modo_virtual_habilitado": true,
    "codigo_qr_expiracion_minutos": 5,
    "reconocimiento_facial_obligatorio": true,
    "liveness_detection": false,
    "notificaciones_tutores": true
  }
  ```
- Color primario (hex)
- Color secundario (hex)
- URL del logo
- Horario de inicio
- Horario de fin
- Actualizado por (admin)

---

### 🔐 SESIONES

#### Tabla: SESIONES_ACTIVAS
**¿Para qué?** Control de usuarios logueados

**Campos necesarios:**
- Token único
- Usuario tipo (DOCENTE, ADMIN, ESTUDIANTE)
- Usuario ID
- IP address
- User agent
- Dispositivo
- Fecha de inicio
- Fecha de expiración
- Última actividad
- ¿Activa? (booleano)

---

## 🔗 RELACIONES PRINCIPALES {#relaciones}

```
PERSONAL_ADMIN
    ├── 1:N → MATERIAS (un docente tiene varias materias)
    ├── 1:N → SESIONES_ACTIVAS
    ├── 1:N → AUDIT_LOG
    └── 1:N → REPORTES_GENERADOS

ESTUDIANTE
    ├── N:1 → TUTOR (un estudiante tiene un tutor)
    ├── 1:N → INSCRIPCIONES (estudiante inscrito en varias materias)
    ├── 1:N → ALERTAS_DESERCION
    ├── 1:N → ESTUDIANTES_BADGES
    └── 1:N → JUSTIFICACIONES

MATERIA
    ├── N:1 → PERSONAL_ADMIN (docente)
    ├── 1:N → INSCRIPCIONES (materia tiene varios estudiantes)
    ├── 1:N → CODIGOS_TEMPORALES
    └── 1:N → ESTADISTICAS_DIARIAS

INSCRIPCION (Estudiante + Materia)
    └── 1:N → ASISTENCIA_LOG (cada inscripción tiene varias asistencias)

ASISTENCIA_LOG
    ├── N:1 → INSCRIPCION
    ├── N:1 → TUTOR (pickup en guardería)
    ├── N:1 → CODIGO_TEMPORAL (si fue por QR)
    └── 1:1 → ASISTENCIA_VIRTUAL (datos extra si fue virtual)

CODIGO_TEMPORAL
    ├── N:1 → MATERIA
    ├── N:1 → PERSONAL_ADMIN (quien generó)
    └── 1:N → ASISTENCIA_LOG (asistencias con ese QR)

TUTOR
    ├── 1:N → ESTUDIANTES
    └── 1:N → ASISTENCIA_LOG (pickups realizados)
```

---

## ✅ CONSTRAINTS Y VALIDACIONES {#constraints}

### Estados válidos:
- **Asistencia**: `PRESENTE`, `AUSENTE`, `TARDANZA`, `JUSTIFICADO`
- **Método de entrada**: `FACIAL`, `QR`, `MANUAL`
- **Tipo de código QR**: `QR_CLASE_VIRTUAL`, `CODIGO_NUMERICO`, `QR_PICKUP_GUARDERIA`, `ENLACE_UNICO`
- **Modo de operación**: `UNIVERSIDAD`, `COLEGIO`, `GUARDERIA`
- **Rol de usuario**: `ADMIN_SISTEMA`, `DOCENTE`, `ADMINISTRATIVO`
- **Nivel de riesgo**: `BAJO`, `MEDIO`, `ALTO`, `CRITICO`
- **Prioridad**: `NORMAL`, `ALTA`, `URGENTE`
- **Rareza de badge**: `COMUN`, `RARO`, `EPICO`, `LEGENDARIO`

### Reglas de negocio:
1. **Guardería/Colegio**: Estudiante DEBE tener tutor asignado
2. **Guardería**: Asistencia DEBE tener pickup registrado
3. **Tardanza**: Si hora_entrada > (hora_inicio_clase + tolerancia_minutos)
4. **Códigos QR**: Deben expirar después de X minutos
5. **Badges**: Solo se otorgan automáticamente si cumplen condición
6. **Alertas**: Se generan automáticamente al detectar patrones

---

## 🎯 PRÓXIMOS PASOS

1. ✅ Revisar este diseño
2. ⬜ Corregir/ajustar lo que necesites
3. ⬜ Crear/actualizar database_models.py
4. ⬜ Aplicar migrations
5. ⬜ Insertar datos de configuración inicial
6. ⬜ Probar el sistema

---

**¿Qué necesitas cambiar o agregar a este diseño?** 🤔
