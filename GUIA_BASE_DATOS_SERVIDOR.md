# 🗄️ Guía: Base de Datos y Migración al Servidor

## 📍 ¿Dónde está la Base de Datos?

### **Ubicación Actual (Local)**
Tu base de datos **PostgreSQL** está corriendo **localmente en tu máquina Windows**:

- **Tipo**: PostgreSQL
- **Nombre de la base de datos**: `class_vision`
- **Host**: `localhost` (127.0.0.1)
- **Puerto**: `5501`
- **Usuario**: `postgres`
- **Contraseña**: (la que configuraste al instalar PostgreSQL)
- **URL de conexión**: `postgresql://postgres:postgres@localhost:5501/class_vision`

### **Configuración en el Código**

La conexión se configura en varios archivos:

1. **`database_models.py`** (línea 555):
   ```python
   DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')
   ```

2. **`api_routes_flexible.py`** (línea 19):
   ```python
   DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')
   ```

3. **`auth_manager_flexible.py`** (línea 13):
   ```python
   DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5501/class_vision')
   ```

### **Archivo .env (No existe aún)**

El proyecto busca un archivo `.env` en la raíz del proyecto, pero **no existe**. Si lo creas, puedes configurar la conexión ahí:

```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5501/class_vision
```

---

## 🚀 Migrar Base de Datos al Servidor Ubuntu

Para copiar tu base de datos al servidor, tienes **3 opciones**:

---

## 📤 Opción 1: Exportar e Importar con pg_dump (Recomendado)

### **Paso 1: Exportar la Base de Datos desde tu Laptop**

Abre PowerShell o CMD y ejecuta:

```powershell
# Exportar estructura y datos
pg_dump -h localhost -p 5501 -U postgres -d class_vision -F c -f class_vision_backup.dump

# O exportar como SQL (más fácil de revisar)
pg_dump -h localhost -p 5501 -U postgres -d class_vision -f class_vision_backup.sql
```

**Nota**: Te pedirá la contraseña de PostgreSQL.

### **Paso 2: Copiar el Backup al Servidor**

```powershell
# Copiar el archivo SQL al servidor
scp class_vision_backup.sql itzan@192.168.30.20:/tmp/
```

### **Paso 3: Crear Base de Datos en el Servidor**

Conéctate al servidor:

```bash
ssh itzan@192.168.30.20
```

En el servidor, ejecuta:

```bash
# Conectarse a PostgreSQL
sudo -u postgres psql

# Crear base de datos
CREATE DATABASE class_vision;

# Salir de psql
\q
```

### **Paso 4: Importar el Backup en el Servidor**

```bash
# Importar desde el archivo SQL
sudo -u postgres psql -d class_vision -f /tmp/class_vision_backup.sql

# O si usaste formato dump:
pg_restore -h localhost -U postgres -d class_vision /tmp/class_vision_backup.dump
```

---

## 📤 Opción 2: Usar pg_dump directamente al Servidor

Si tienes acceso directo desde tu laptop al PostgreSQL del servidor:

```powershell
# Exportar directamente al servidor (requiere que PostgreSQL del servidor sea accesible)
pg_dump -h 192.168.30.20 -p 5432 -U postgres -d class_vision -f class_vision_backup.sql
```

**Nota**: Esto requiere que el PostgreSQL del servidor acepte conexiones remotas.

---

## 📤 Opción 3: Recrear desde Scripts SQL

Si prefieres crear la base de datos desde cero en el servidor:

### **Paso 1: Copiar Scripts SQL al Servidor**

```powershell
# Copiar el script de creación
scp database_complete.sql itzan@192.168.30.20:/tmp/
```

### **Paso 2: Crear Base de Datos en el Servidor**

```bash
ssh itzan@192.168.30.20

# Crear base de datos
sudo -u postgres psql -c "CREATE DATABASE class_vision;"

# Ejecutar script de creación
sudo -u postgres psql -d class_vision -f /tmp/database_complete.sql
```

### **Paso 3: (Opcional) Importar Datos de Prueba**

Si tienes datos de prueba que quieres migrar, usa el método de la Opción 1.

---

## ⚙️ Configurar Conexión en el Servidor

Después de migrar la base de datos, necesitas actualizar la configuración en el servidor:

### **Crear archivo .env en el Servidor**

```bash
# En el servidor
cd /srv/miempresa/app1_tienda/codigo

# Crear archivo .env
nano .env
```

Contenido del `.env`:

```env
# Base de Datos PostgreSQL en el Servidor
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/class_vision

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=tu_clave_secreta_segura_aqui

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

**Nota**: 
- El puerto en el servidor probablemente sea `5432` (puerto por defecto de PostgreSQL)
- Ajusta la contraseña según tu configuración del servidor

---

## 🔍 Verificar la Base de Datos

### **En tu Laptop (Local)**

```powershell
# Conectarse a PostgreSQL local
psql -h localhost -p 5501 -U postgres -d class_vision

# Ver tablas
\dt

# Ver bases de datos
\l

# Salir
\q
```

### **En el Servidor**

```bash
# Conectarse a PostgreSQL en el servidor
sudo -u postgres psql -d class_vision

# Ver tablas
\dt

# Contar registros en una tabla
SELECT COUNT(*) FROM usuarios;

# Salir
\q
```

---

## 📋 Checklist de Migración

- [ ] Exportar base de datos local (`pg_dump`)
- [ ] Copiar backup al servidor (`scp`)
- [ ] Instalar PostgreSQL en el servidor (si no está instalado)
- [ ] Crear base de datos `class_vision` en el servidor
- [ ] Importar backup en el servidor (`psql` o `pg_restore`)
- [ ] Verificar que las tablas se crearon correctamente
- [ ] Crear archivo `.env` en el servidor con la nueva `DATABASE_URL`
- [ ] Probar conexión desde la aplicación en el servidor
- [ ] Verificar que los datos se migraron correctamente

---

## 🛠️ Comandos Útiles

### **Verificar que PostgreSQL está corriendo**

**Windows (PowerShell):**
```powershell
Get-Service postgresql*
```

**Linux (Servidor):**
```bash
sudo systemctl status postgresql
```

### **Iniciar/Detener PostgreSQL**

**Windows:**
```powershell
# Iniciar
Start-Service postgresql-x64-14  # Ajusta según tu versión

# Detener
Stop-Service postgresql-x64-14
```

**Linux:**
```bash
# Iniciar
sudo systemctl start postgresql

# Detener
sudo systemctl stop postgresql

# Reiniciar
sudo systemctl restart postgresql
```

### **Ver tamaño de la base de datos**

```sql
-- En psql
SELECT pg_size_pretty(pg_database_size('class_vision'));
```

### **Listar todas las tablas**

```sql
-- En psql
\dt
```

### **Ver estructura de una tabla**

```sql
-- En psql
\d nombre_tabla
```

---

## ⚠️ Consideraciones Importantes

1. **Contraseñas**: Asegúrate de usar contraseñas seguras en producción
2. **Backup**: Siempre haz backup antes de migrar
3. **Permisos**: Verifica que el usuario de la aplicación tenga permisos en la base de datos
4. **Puerto**: El puerto puede ser diferente en el servidor (5432 vs 5501)
5. **Firewall**: Asegúrate de que el firewall permita conexiones a PostgreSQL si es necesario

---

## 🔐 Seguridad en Producción

Para producción, considera:

1. **Usuario dedicado**: Crear un usuario específico para la aplicación (no usar `postgres`)
2. **Permisos limitados**: Dar solo los permisos necesarios
3. **SSL**: Habilitar conexiones SSL si es posible
4. **Firewall**: Restringir acceso a PostgreSQL solo desde la aplicación

```sql
-- Crear usuario para la aplicación
CREATE USER app_user WITH PASSWORD 'password_segura';
GRANT CONNECT ON DATABASE class_vision TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
```

---

## 📞 Solución de Problemas

### **Error: "No se puede conectar a PostgreSQL"**

1. Verifica que PostgreSQL esté corriendo
2. Verifica el puerto (5501 local, 5432 servidor)
3. Verifica usuario y contraseña
4. Verifica firewall

### **Error: "Base de datos no existe"**

```sql
-- Crear base de datos
CREATE DATABASE class_vision;
```

### **Error: "Permiso denegado"**

```sql
-- Dar permisos al usuario
GRANT ALL PRIVILEGES ON DATABASE class_vision TO postgres;
```

---

## 🎯 Resumen Rápido

**Para copiar la base de datos al servidor:**

```powershell
# 1. Exportar
pg_dump -h localhost -p 5501 -U postgres -d class_vision -f backup.sql

# 2. Copiar al servidor
scp backup.sql itzan@192.168.30.20:/tmp/

# 3. En el servidor, importar
ssh itzan@192.168.30.20
sudo -u postgres psql -d class_vision -f /tmp/backup.sql
```

