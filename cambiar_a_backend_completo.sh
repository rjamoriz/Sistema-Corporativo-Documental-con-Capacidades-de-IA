#!/bin/bash

# Script para cambiar del backend demo al backend completo
# Autor: FinancIA 2030
# Fecha: 13 Octubre 2025

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   FinancIA 2030 - Cambio a Backend Completo              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Paso 1: Detener backend demo
echo -e "${YELLOW}[1/5] Deteniendo backend demo...${NC}"
PID_DEMO=$(ps aux | grep "main_demo.py" | grep -v grep | awk '{print $2}')
if [ -n "$PID_DEMO" ]; then
    kill $PID_DEMO
    sleep 2
    echo -e "${GREEN}✓ Backend demo detenido (PID: $PID_DEMO)${NC}"
else
    echo -e "${YELLOW}⚠ Backend demo no estaba corriendo${NC}"
fi
echo ""

# Paso 2: Verificar Python y pip
echo -e "${YELLOW}[2/5] Verificando entorno Python...${NC}"
cd /workspaces/Sistema-Corporativo-Documental-con-Capacidades-de-IA/backend
python --version
pip --version
echo -e "${GREEN}✓ Python y pip disponibles${NC}"
echo ""

# Paso 3: Instalar dependencias faltantes
echo -e "${YELLOW}[3/5] Instalando dependencias necesarias...${NC}"
echo -e "${BLUE}Instalando sentence-transformers...${NC}"
pip install -q sentence-transformers

echo -e "${BLUE}Instalando spacy...${NC}"
pip install -q spacy

echo -e "${BLUE}Descargando modelo español de spacy...${NC}"
python -m spacy download es_core_news_md

echo -e "${GREEN}✓ Dependencias instaladas correctamente${NC}"
echo ""

# Paso 4: Verificar instalaciones
echo -e "${YELLOW}[4/5] Verificando instalaciones...${NC}"
pip list | grep -E "(sentence-transformers|spacy|torch)" || true
echo ""

# Paso 5: Iniciar backend completo
echo -e "${YELLOW}[5/5] Iniciando backend completo...${NC}"
echo -e "${BLUE}Ejecutando: python main.py${NC}"
echo -e "${GREEN}Backend estará disponible en: http://localhost:8000${NC}"
echo -e "${GREEN}Documentación API: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Nota: Este proceso quedará corriendo en este terminal.${NC}"
echo -e "${YELLOW}Para detenerlo, presiona Ctrl+C${NC}"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Backend completo iniciándose...${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Iniciar backend completo
python main.py
