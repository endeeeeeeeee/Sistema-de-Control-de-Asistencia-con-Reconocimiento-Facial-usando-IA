#!/bin/bash

# ============================================
# CLASS VISION - Script de Instalación
# Linux / macOS
# ============================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  CLASS VISION - Instalación Automática${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Verificar Python
echo -e "${YELLOW}[1/6] Verificando Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python encontrado: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓ Python encontrado: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}✗ Python no encontrado. Por favor instala Python 3.8 o superior.${NC}"
    echo -e "${YELLOW}  Ubuntu/Debian: sudo apt-get install python3${NC}"
    echo -e "${YELLOW}  macOS: brew install python3${NC}"
    exit 1
fi

# Verificar versión mínima
PYTHON_VERSION_NUM=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if (( $(echo "$PYTHON_VERSION_NUM < 3.8" | bc -l) )); then
    echo -e "${RED}✗ Se requiere Python 3.8 o superior. Versión actual: $PYTHON_VERSION_NUM${NC}"
    exit 1
fi

# Crear entorno virtual
echo ""
echo -e "${YELLOW}[2/6] Creando entorno virtual...${NC}"
if [ -d ".venv" ]; then
    echo -e "  ${YELLOW}Entorno virtual ya existe. Eliminando...${NC}"
    rm -rf .venv
fi
$PYTHON_CMD -m venv .venv
echo -e "${GREEN}✓ Entorno virtual creado${NC}"

# Activar entorno virtual
echo ""
echo -e "${YELLOW}[3/6] Activando entorno virtual...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activado${NC}"

# Actualizar pip
echo ""
echo -e "${YELLOW}[4/6] Actualizando pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip actualizado${NC}"

# Instalar dependencias
echo ""
echo -e "${YELLOW}[5/6] Instalando dependencias...${NC}"
echo -e "  ${CYAN}Esto puede tardar varios minutos...${NC}"
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Error al instalar dependencias${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependencias instaladas exitosamente${NC}"

# Crear directorios necesarios
echo ""
echo -e "${YELLOW}[6/6] Creando estructura de directorios...${NC}"
directories=(
    "TrainingImage"
    "TrainingImageLabel"
    "StudentDetails"
    "Attendance"
    "UI_Image"
    "logs"
    "config"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "  ${GREEN}✓ Creado: $dir${NC}"
    else
        echo -e "  ${NC}- Ya existe: $dir${NC}"
    fi
done

# Crear archivo de configuración local si no existe
if [ ! -f "config/local_config.json" ]; then
    if [ -f "config/default_config.json" ]; then
        cp config/default_config.json config/local_config.json
        echo -e "  ${GREEN}✓ Creado: config/local_config.json${NC}"
    fi
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}  ✓ Instalación Completada${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}Para ejecutar CLASS VISION:${NC}"
echo -e "${NC}  1. Activa el entorno virtual:${NC}"
echo -e "${CYAN}     source .venv/bin/activate${NC}"
echo ""
echo -e "${NC}  2. Ejecuta la aplicación:${NC}"
echo -e "${CYAN}     python attendance.py${NC}"
echo ""
echo -e "${NC}Documentación completa en README.md${NC}"
echo ""
