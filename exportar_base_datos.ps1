# Script para exportar la base de datos PostgreSQL
# Genera un backup que puedes copiar al servidor

param(
    [string]$Host = "localhost",
    [int]$Port = 5501,
    [string]$User = "postgres",
    [string]$Database = "class_vision",
    [string]$OutputFile = "class_vision_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Exportando Base de Datos PostgreSQL" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuración:" -ForegroundColor Yellow
Write-Host "  Host: $Host" -ForegroundColor White
Write-Host "  Puerto: $Port" -ForegroundColor White
Write-Host "  Usuario: $User" -ForegroundColor White
Write-Host "  Base de Datos: $Database" -ForegroundColor White
Write-Host "  Archivo de salida: $OutputFile" -ForegroundColor White
Write-Host ""

# Verificar que pg_dump esté disponible
if (-not (Get-Command pg_dump -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERROR: pg_dump no está disponible" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solución:" -ForegroundColor Yellow
    Write-Host "1. Asegúrate de que PostgreSQL esté instalado" -ForegroundColor White
    Write-Host "2. Agrega PostgreSQL/bin a tu PATH" -ForegroundColor White
    Write-Host "   Ejemplo: C:\Program Files\PostgreSQL\14\bin" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Solicitar contraseña
$password = Read-Host "🔐 Ingresa la contraseña de PostgreSQL" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Configurar variable de entorno para pg_dump
$env:PGPASSWORD = $plainPassword

Write-Host ""
Write-Host "📤 Exportando base de datos..." -ForegroundColor Yellow
Write-Host "   Esto puede tardar varios minutos..." -ForegroundColor Gray
Write-Host ""

try {
    # Ejecutar pg_dump
    $process = Start-Process -FilePath "pg_dump" -ArgumentList @(
        "-h", $Host,
        "-p", $Port.ToString(),
        "-U", $User,
        "-d", $Database,
        "-f", $OutputFile,
        "-F", "p",  # Formato SQL plano
        "-v"        # Modo verbose
    ) -Wait -NoNewWindow -PassThru

    # Limpiar contraseña de memoria
    $plainPassword = $null
    $env:PGPASSWORD = $null

    if ($process.ExitCode -eq 0) {
        $fileSize = (Get-Item $OutputFile).Length / 1MB
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "✅ Exportación completada exitosamente!" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Archivo creado: $OutputFile" -ForegroundColor Cyan
        Write-Host "Tamaño: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Próximos pasos:" -ForegroundColor Yellow
        Write-Host "1. Copiar el archivo al servidor:" -ForegroundColor White
        Write-Host "   scp $OutputFile itzan@192.168.30.20:/tmp/" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "2. En el servidor, importar:" -ForegroundColor White
        Write-Host "   sudo -u postgres psql -d class_vision -f /tmp/$OutputFile" -ForegroundColor Cyan
        Write-Host ""
    } else {
        throw "pg_dump falló con código de salida: $($process.ExitCode)"
    }
} catch {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "❌ ERROR al exportar base de datos" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifica:" -ForegroundColor Yellow
    Write-Host "1. Que PostgreSQL esté corriendo" -ForegroundColor White
    Write-Host "2. Que el usuario y contraseña sean correctos" -ForegroundColor White
    Write-Host "3. Que la base de datos 'class_vision' exista" -ForegroundColor White
    Write-Host "4. Que tengas permisos para acceder a la base de datos" -ForegroundColor White
    Write-Host ""
    
    # Limpiar contraseña
    $plainPassword = $null
    $env:PGPASSWORD = $null
    
    exit 1
}

Read-Host "Presiona Enter para continuar"

