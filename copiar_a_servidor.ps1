# Script PowerShell para copiar el proyecto al servidor Ubuntu
# Ajusta los valores según tu configuración

# ============================================
# CONFIGURACIÓN - EDITA ESTOS VALORES
# ============================================
$USUARIO_SERVIDOR = "itzan"
$IP_SERVIDOR = "192.168.30.20"
$RUTA_DESTINO = "/srv/miempresa/app1_tienda/codigo"

# Ruta del proyecto (ajusta si es necesario)
$RUTA_PROYECTO = "C:\Users\HP\git\Sistema de Control de Asistencia con Reconocimiento Facial usando IA"

# ============================================
# OPCIÓN 1: Usar SCP (requiere OpenSSH en Windows)
# ============================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Copiando proyecto al servidor..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usuario: $USUARIO_SERVIDOR" -ForegroundColor Yellow
Write-Host "Servidor: $IP_SERVIDOR" -ForegroundColor Yellow
Write-Host "Destino: $RUTA_DESTINO" -ForegroundColor Yellow
Write-Host ""
Write-Host "Esto puede tardar varios minutos..." -ForegroundColor Gray
Write-Host ""

# Verificar si scp está disponible
if (Get-Command scp -ErrorAction SilentlyContinue) {
    try {
        # Convertir ruta de Windows a formato compatible
        $rutaEscapada = $RUTA_PROYECTO -replace '\\', '/'
        
        scp -r "$RUTA_PROYECTO" "${USUARIO_SERVIDOR}@${IP_SERVIDOR}:${RUTA_DESTINO}"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "============================================" -ForegroundColor Green
            Write-Host "¡Copia completada exitosamente!" -ForegroundColor Green
            Write-Host "============================================" -ForegroundColor Green
        } else {
            throw "Error en la copia"
        }
    } catch {
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Red
        Write-Host "ERROR: La copia falló" -ForegroundColor Red
        Write-Host "============================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Error: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Posibles soluciones:" -ForegroundColor Yellow
        Write-Host "1. Verifica que OpenSSH esté instalado en Windows" -ForegroundColor White
        Write-Host "2. Verifica la conexión SSH al servidor" -ForegroundColor White
        Write-Host "3. Verifica que la ruta de destino exista en el servidor" -ForegroundColor White
        Write-Host "4. Verifica tus credenciales" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "ERROR: SCP no está disponible" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instala OpenSSH en Windows:" -ForegroundColor Yellow
    Write-Host "1. Abre PowerShell como Administrador" -ForegroundColor White
    Write-Host "2. Ejecuta: Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "O usa una alternativa:" -ForegroundColor Yellow
    Write-Host "- WinSCP (interfaz gráfica)" -ForegroundColor White
    Write-Host "- Git Bash" -ForegroundColor White
    Write-Host "- WSL (Windows Subsystem for Linux)" -ForegroundColor White
}

Read-Host "Presiona Enter para continuar"

