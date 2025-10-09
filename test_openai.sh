#!/bin/bash

# FinancIA 2030 - Script de Inicio Rápido con OpenAI
# Este script verifica y prueba la configuración de OpenAI

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║      🚀 FINANCIA 2030 - TEST DE OPENAI + PHOENIX              ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar que estamos en el directorio correcto
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Verificando estructura de directorios..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Error: Directorio backend no encontrado${NC}"
    echo "   Por favor ejecuta este script desde la raíz del proyecto"
    exit 1
fi

echo -e "${GREEN}✅ Estructura correcta${NC}"
echo ""

# 2. Verificar .env
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Verificando archivo .env..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ Error: backend/.env no encontrado${NC}"
    echo ""
    echo "   Crea el archivo backend/.env con:"
    echo "   cp .env.example backend/.env"
    echo ""
    echo "   Luego edita backend/.env y agrega tu OPENAI_API_KEY"
    exit 1
fi

echo -e "${GREEN}✅ Archivo .env encontrado${NC}"

# Verificar que tiene OpenAI API key
if grep -q "OPENAI_API_KEY=sk-" backend/.env; then
    echo -e "${GREEN}✅ OPENAI_API_KEY configurado${NC}"
else
    echo -e "${RED}❌ Error: OPENAI_API_KEY no configurado en backend/.env${NC}"
    exit 1
fi

echo ""

# 3. Verificar Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Verificando Python..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION}${NC}"
echo ""

# 4. Instalar dependencias mínimas
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Instalando dependencias necesarias..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd backend

# Instalar solo lo esencial para el test
pip install -q python-dotenv openai arize-phoenix openinference-instrumentation-openai 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Algunas dependencias no se pudieron instalar${NC}"
    echo "   Intentando continuar..."
}

echo -e "${GREEN}✅ Dependencias instaladas${NC}"
echo ""

# 5. Ejecutar test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Ejecutando test de OpenAI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 test_openai_phoenix.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ TEST COMPLETADO EXITOSAMENTE${NC}"
echo ""
echo "🎯 Próximos pasos:"
echo ""
echo "   1. Iniciar infraestructura:"
echo "      cd infrastructure/docker"
echo "      docker-compose up -d"
echo ""
echo "   2. Iniciar backend:"
echo "      cd backend"
echo "      uvicorn main:app --reload"
echo ""
echo "   3. Acceder a Phoenix UI:"
echo "      http://localhost:6006"
echo ""
echo "   4. Ver API docs:"
echo "      http://localhost:8000/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
