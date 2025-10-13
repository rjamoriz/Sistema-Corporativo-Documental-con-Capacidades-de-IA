#!/bin/bash
# Script de instalación de dependencias para generación de PDFs de demo

set -e  # Exit on error

echo "=============================================="
echo "📦 Instalación de Dependencias para Demo PDFs"
echo "=============================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

echo "✓ Python3 detectado: $(python3 --version)"
echo ""

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado"
    exit 1
fi

echo "✓ pip3 detectado: $(pip3 --version)"
echo ""

# Instalar reportlab
echo "📥 Instalando reportlab..."
pip3 install reportlab --quiet

# Instalar Pillow (para imágenes)
echo "📥 Instalando Pillow..."
pip3 install Pillow --quiet

echo ""
echo "=============================================="
echo "✅ Dependencias instaladas correctamente"
echo "=============================================="
echo ""
echo "Puedes generar los PDFs de demo ejecutando:"
echo "  python3 demo/scripts/generate_sample_pdfs.py"
echo ""
