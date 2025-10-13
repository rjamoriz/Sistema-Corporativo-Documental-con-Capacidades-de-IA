#!/bin/bash

# Script de monitoreo del backend completo
# Verifica cada 30 segundos hasta que esté listo

echo "🔍 Monitoreando inicio del backend completo..."
echo "================================================"
echo ""

ATTEMPTS=0
MAX_ATTEMPTS=20  # 20 intentos × 30 seg = 10 minutos

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    ATTEMPTS=$((ATTEMPTS + 1))
    ELAPSED=$((ATTEMPTS * 30))
    
    echo "⏱️  Intento $ATTEMPTS/$MAX_ATTEMPTS (${ELAPSED}s transcurridos)"
    
    # Verificar si el proceso está corriendo
    if ! ps aux | grep "python main.py" | grep -v grep > /dev/null; then
        echo "❌ Backend se detuvo. Revisando logs..."
        echo ""
        echo "📋 Últimas 50 líneas del log:"
        tail -50 /tmp/backend_full.log
        exit 1
    fi
    
    # Intentar conectar al backend
    RESPONSE=$(curl -s http://localhost:8000/ 2>&1)
    
    if [ $? -eq 0 ] && [[ $RESPONSE == *"FinancIA"* ]]; then
        echo ""
        echo "✅ ¡BACKEND COMPLETO LISTO!"
        echo "================================================"
        echo ""
        echo "📊 Información del servidor:"
        echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
        echo ""
        echo "🔗 URLs disponibles:"
        echo "   - API: http://localhost:8000"
        echo "   - Docs: http://localhost:8000/docs"
        echo "   - Redoc: http://localhost:8000/redoc"
        echo ""
        echo "🧪 Probar generación sintética:"
        echo "   ./test_synthetic_features.sh"
        echo ""
        exit 0
    else
        echo "   ⏳ Backend aún cargando..."
        echo "   📝 Últimas líneas del log:"
        tail -5 /tmp/backend_full.log | sed 's/^/      /'
        echo ""
    fi
    
    if [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; then
        echo "   ⏸️  Esperando 30 segundos..."
        echo ""
        sleep 30
    fi
done

echo ""
echo "⚠️  Tiempo máximo excedido (10 minutos)"
echo "📋 Log completo disponible en: /tmp/backend_full.log"
echo ""
echo "Ver log completo:"
echo "   cat /tmp/backend_full.log"
exit 1
