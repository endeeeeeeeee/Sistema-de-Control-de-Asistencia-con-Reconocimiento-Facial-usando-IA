# ============================================
# CLASS VISION - Script de Instalación
# Windows PowerShell
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CLASS VISION - Instalación Automática" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python no encontrado. Por favor instala Python 3.8 o superior." -ForegroundColor Red
    Write-Host "  Descarga desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Verificar versión mínima de Python
$pythonVersionNumber = (python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1)
if ([float]$pythonVersionNumber -lt 3.8) {
    Write-Host "✗ Se requiere Python 3.8 o superior. Versión actual: $pythonVersionNumber" -ForegroundColor Red
    exit 1
}

# Crear entorno virtual
Write-Host ""
Write-Host "[2/6] Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  Entorno virtual ya existe. Eliminando..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}
python -m venv .venv
Write-Host "✓ Entorno virtual creado" -ForegroundColor Green

# Activar entorno virtual
Write-Host ""
Write-Host "[3/6] Activando entorno virtual..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
Write-Host "✓ Entorno virtual activado" -ForegroundColor Green

# Actualizar pip
Write-Host ""
Write-Host "[4/6] Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip actualizado" -ForegroundColor Green

# Instalar dependencias
Write-Host ""
Write-Host "[5/6] Instalando dependencias..." -ForegroundColor Yellow
Write-Host "  Esto puede tardar varios minutos..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Error al instalar dependencias" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencias instaladas exitosamente" -ForegroundColor Green

# Crear directorios necesarios
Write-Host ""
Write-Host "[6/6] Creando estructura de directorios..." -ForegroundColor Yellow
$directories = @(
    "TrainingImage",
    "TrainingImageLabel",
    "StudentDetails",
    "Attendance",
    "UI_Image",
    "logs",
    "config"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Creado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  - Ya existe: $dir" -ForegroundColor Gray
    }
}

# Crear archivo de configuración local si no existe
if (!(Test-Path "config\local_config.json")) {
    if (Test-Path "config\default_config.json") {
        Copy-Item "config\default_config.json" "config\local_config.json"
        Write-Host "  ✓ Creado: config\local_config.json" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ Instalación Completada" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ejecutar CLASS VISION:" -ForegroundColor Yellow
Write-Host "  1. Activa el entorno virtual:" -ForegroundColor White
Write-Host "     .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Ejecuta la aplicación:" -ForegroundColor White
Write-Host "     python attendance.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentación completa en README.md" -ForegroundColor Gray
Write-Host ""
