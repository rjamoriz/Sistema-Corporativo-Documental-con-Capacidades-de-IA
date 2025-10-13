#!/bin/bash

# Script de verificación rápida del estado del backend

echo "🔍 Verificando estado del backend..."
echo ""

# 1. Ver si el proceso está corriendo
echo "1️⃣  Proceso Python:"
if ps aux | grep "python main.py" | grep -v grep > /dev/null; then
    PID=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $2}')
    MEM=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $6}')
    MEM_MB=$((MEM / 1024))
    CPU=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $3}')
    echo "   ✅ Corriendo (PID: $PID)"
    echo "   📊 RAM: ${MEM_MB} MB"
    echo "   ⚡ CPU: ${CPU}%"
else
    echo "   ❌ No está corriendo"
    echo ""
    echo "Para reiniciar:"
    echo "   cd /workspaces/Sistema-Corporativo-Documental-con-Capacidades-de-IA/backend"
    echo "   nohup python main.py > /tmp/backend_full.log 2>&1 &"
    exit 1
fi

echo ""

# 2. Intentar conectar
echo "2️⃣  Conectividad:"
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "   ✅ Backend respondiendo!"
    echo ""
    echo "📡 Respuesta del servidor:"
    curl -s http://localhost:8000/ | jq '.' 2>/dev/null || curl -s http://localhost:8000/
    echo ""
    echo "🎉 ¡BACKEND COMPLETO LISTO!"
    echo ""
    echo "Próximos pasos:"
    echo "   - Ver docs: http://localhost:8000/docs"
    echo "   - Probar synthetic: ./test_synthetic_features.sh"
    exit 0
else
    echo "   ⏳ Aún cargando (no responde)"
fi

echo ""

# 3. Ver últimas líneas del log
echo "3️⃣  Últimas líneas del log:"
if [ -f /tmp/backend_startup.log ] && [ -s /tmp/backend_startup.log ]; then
    tail -5 /tmp/backend_startup.log | sed 's/^/   /'
elif [ -f /tmp/backend_full.log ] && [ -s /tmp/backend_full.log ]; then
    tail -5 /tmp/backend_full.log | sed 's/^/   /'
else
    echo "   (Sin output aún - cargando imports pesados)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Ejecuta este script cada 2 minutos para ver el progreso"
echo "   O ejecuta: ./monitor_backend.sh (monitoreo automático)"
echo ""
