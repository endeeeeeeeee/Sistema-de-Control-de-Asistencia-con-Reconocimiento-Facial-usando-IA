# 📤 Guía para Copiar el Proyecto al Servidor Ubuntu

## 🎯 Información del Servidor

- **Usuario**: `itzan`
- **IP del Servidor**: `192.168.30.20`
- **Ruta de Destino**: `/srv/miempresa/app1_tienda/codigo`
- **Ruta del Proyecto Local**: `C:\Users\HP\git\Sistema de Control de Asistencia con Reconocimiento Facial usando IA`

---

## 💻 Opción 1: Usar SCP desde PowerShell (Recomendado)

### Paso 1: Verificar que OpenSSH esté instalado

Abre PowerShell como Administrador y ejecuta:

```powershell
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'
```

Si no está instalado, instálalo:

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

### Paso 2: Ejecutar el script

1. **Opción A: Usar el script PowerShell** (Recomendado)
   ```powershell
   .\copiar_a_servidor.ps1
   ```

2. **Opción B: Comando manual**
   ```powershell
   scp -r "C:\Users\HP\git\Sistema de Control de Asistencia con Reconocimiento Facial usando IA" itzan@192.168.30.20:/srv/miempresa/app1_tienda/codigo
   ```

### Paso 3: Ingresar contraseña

Cuando te lo solicite, ingresa la contraseña del usuario `itzan` en el servidor.

---

## 🐧 Opción 2: Usar Git Bash

Si tienes Git instalado, puedes usar Git Bash:

1. Abre **Git Bash**
2. Ejecuta:

```bash
scp -r "/c/Users/HP/git/Sistema de Control de Asistencia con Reconocimiento Facial usando IA" itzan@192.168.30.20:/srv/miempresa/app1_tienda/codigo
```

**Nota**: En Git Bash, las rutas de Windows se convierten:
- `C:\Users\...` → `/c/Users/...`
- Los espacios en nombres de carpetas deben estar entre comillas

---

## 🪟 Opción 3: Usar WSL (Windows Subsystem for Linux)

Si tienes WSL instalado:

1. Abre **WSL** (Ubuntu, por ejemplo)
2. Ejecuta:

```bash
# Montar el disco C: en WSL
cd /mnt/c/Users/HP/git

# Copiar el proyecto
scp -r "Sistema de Control de Asistencia con Reconocimiento Facial usando IA" itzan@192.168.30.20:/srv/miempresa/app1_tienda/codigo
```

---

## 🖱️ Opción 4: Usar WinSCP (Interfaz Gráfica)

1. **Descarga WinSCP**: https://winscp.net/
2. **Instala y abre WinSCP**
3. **Configura la conexión**:
   - **Protocolo**: SFTP
   - **Nombre de host**: `192.168.30.20`
   - **Usuario**: `itzan`
   - **Contraseña**: (tu contraseña)
4. **Conecta** al servidor
5. **Navega** a `/srv/miempresa/app1_tienda/codigo` en el servidor
6. **Arrastra** la carpeta del proyecto desde tu PC al servidor

---

## ⚙️ Opción 5: Usar rsync (Más eficiente para actualizaciones)

Si ya copiaste el proyecto antes y solo quieres actualizar cambios:

```bash
# Desde Git Bash o WSL
rsync -avz --progress "C:\Users\HP\git\Sistema de Control de Asistencia con Reconocimiento Facial usando IA/" itzan@192.168.30.20:/srv/miempresa/app1_tienda/codigo/
```

**Ventajas de rsync**:
- Solo copia archivos modificados
- Más rápido en actualizaciones
- Muestra progreso

---

## 🔐 Configurar SSH sin contraseña (Opcional)

Para evitar ingresar la contraseña cada vez:

### En Windows (PowerShell):

```powershell
# Generar clave SSH (si no tienes una)
ssh-keygen -t rsa -b 4096

# Copiar clave al servidor
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh itzan@192.168.30.20 "cat >> ~/.ssh/authorized_keys"
```

### En Git Bash o WSL:

```bash
# Generar clave SSH (si no tienes una)
ssh-keygen -t rsa -b 4096

# Copiar clave al servidor
ssh-copy-id itzan@192.168.30.20
```

---

## ✅ Verificar la Copia

Después de copiar, verifica en el servidor:

```bash
ssh itzan@192.168.30.20
ls -la /srv/miempresa/app1_tienda/codigo
```

---

## 🚨 Solución de Problemas

### Error: "scp: command not found"
- **Solución**: Instala OpenSSH en Windows (ver Opción 1, Paso 1)

### Error: "Permission denied"
- **Solución**: Verifica que el usuario `itzan` tenga permisos de escritura en `/srv/miempresa/app1_tienda/codigo`
- En el servidor, ejecuta: `sudo chown -R itzan:itzan /srv/miempresa/app1_tienda/codigo`

### Error: "Connection refused"
- **Solución**: Verifica que el servidor esté encendido y accesible
- Prueba: `ping 192.168.30.20`
- Verifica que SSH esté corriendo en el servidor: `ssh itzan@192.168.30.20`

### Error: "No space left on device"
- **Solución**: Verifica el espacio en disco del servidor: `df -h`

### La copia es muy lenta
- **Solución**: 
  - Excluye carpetas innecesarias (ver siguiente sección)
  - Usa `rsync` en lugar de `scp`
  - Comprime antes de copiar

---

## 📦 Excluir Carpetas Innecesarias

Para copiar más rápido, puedes excluir carpetas como `__pycache__`, `.git`, etc.:

### Usando rsync:

```bash
rsync -avz --progress \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude 'venv' \
  --exclude 'node_modules' \
  --exclude '.env' \
  "C:\Users\HP\git\Sistema de Control de Asistencia con Reconocimiento Facial usando IA/" \
  itzan@192.168.30.20:/srv/miempresa/app1_tienda/codigo/
```

---

## 📝 Notas Importantes

1. **Espacios en nombres**: El nombre de tu proyecto tiene espacios, por eso está entre comillas en los comandos.

2. **Primera copia**: La primera copia puede tardar varios minutos dependiendo del tamaño del proyecto.

3. **Actualizaciones futuras**: Usa `rsync` para actualizaciones, es más eficiente.

4. **Seguridad**: Considera usar claves SSH en lugar de contraseñas.

5. **Backup**: Antes de copiar, asegúrate de tener un backup del código en el servidor si ya existe.

---

## 🎯 Comando Rápido (Copy-Paste)

**PowerShell:**
```powershell
scp -r "C:\Users\HP\git\Sistema de Control de Asistencia con Reconocimiento Facial usando IA" itzan@192.168.30.20:/srv/miempresa/app1_tienda/codigo
```

**Git Bash:**
```bash
scp -r "/c/Users/HP/git/Sistema de Control de Asistencia con Reconocimiento Facial usando IA" itzan@192.168.30.20:/srv/miempresa/app1_tienda/codigo
```

