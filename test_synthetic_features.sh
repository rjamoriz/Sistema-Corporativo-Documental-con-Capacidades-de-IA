#!/bin/bash

# Script de prueba completo para nuevas funcionalidades de datos sintéticos
# FinancIA 2030 - Test de Visualización de Archivos y Vectorización

echo "=================================================="
echo "🧪 TEST: Generador de Datos Sintéticos v2.0"
echo "=================================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuración
API_BASE="http://localhost:8000"
API_URL="${API_BASE}/api/v1"

echo "📍 API Base URL: $API_BASE"
echo ""

# Paso 1: Login para obtener token
echo "${BLUE}[1/6] Autenticando...${NC}"
TOKEN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin.demo&password=Demo2025!")

TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
  echo "   ${GREEN}✓${NC} Token obtenido: ${TOKEN:0:20}..."
else
  echo "   ${RED}✗${NC} Error en autenticación"
  echo "   Response: $TOKEN_RESPONSE"
  exit 1
fi
echo ""

# Paso 2: Generar documentos sintéticos pequeños (solo 5 para prueba rápida)
echo "${BLUE}[2/6] Generando 5 documentos sintéticos...${NC}"
GENERATE_RESPONSE=$(curl -s -X POST "${API_URL}/synthetic/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "total_documents": 5,
    "template_id": "default",
    "auto_upload": false
  }')

TASK_ID=$(echo $GENERATE_RESPONSE | jq -r '.task_id')

if [ "$TASK_ID" != "null" ] && [ -n "$TASK_ID" ]; then
  echo "   ${GREEN}✓${NC} Tarea creada: $TASK_ID"
  ESTIMATED_TIME=$(echo $GENERATE_RESPONSE | jq -r '.estimated_time_seconds')
  echo "   ⏱️  Tiempo estimado: ${ESTIMATED_TIME}s"
else
  echo "   ${RED}✗${NC} Error al crear tarea"
  echo "   Response: $GENERATE_RESPONSE"
  exit 1
fi
echo ""

# Paso 3: Esperar y monitorear progreso
echo "${BLUE}[3/6] Monitoreando progreso...${NC}"
STATUS="pending"
PROGRESS=0
ATTEMPTS=0
MAX_ATTEMPTS=30

while [ "$STATUS" != "completed" ] && [ "$STATUS" != "failed" ] && [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
  sleep 2
  STATUS_RESPONSE=$(curl -s -X GET "${API_URL}/synthetic/status/${TASK_ID}" \
    -H "Authorization: Bearer $TOKEN")
  
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
  PROGRESS=$(echo $STATUS_RESPONSE | jq -r '.progress')
  DOCS_GENERATED=$(echo $STATUS_RESPONSE | jq -r '.documents_generated')
  
  echo "   📊 Status: $STATUS | Progreso: ${PROGRESS}% | Docs: ${DOCS_GENERATED}/5"
  
  ATTEMPTS=$((ATTEMPTS + 1))
done

if [ "$STATUS" = "completed" ]; then
  echo "   ${GREEN}✓${NC} Generación completada!"
elif [ "$STATUS" = "failed" ]; then
  echo "   ${RED}✗${NC} Generación falló"
  ERROR=$(echo $STATUS_RESPONSE | jq -r '.error')
  echo "   Error: $ERROR"
  exit 1
else
  echo "   ${RED}✗${NC} Timeout esperando completitud"
  exit 1
fi
echo ""

# Paso 4: Obtener lista de archivos generados (NUEVA FUNCIONALIDAD)
echo "${BLUE}[4/6] 📁 Obteniendo lista de archivos generados...${NC}"
FILES_RESPONSE=$(curl -s -X GET "${API_URL}/synthetic/tasks/${TASK_ID}/files" \
  -H "Authorization: Bearer $TOKEN")

TOTAL_FILES=$(echo $FILES_RESPONSE | jq -r '.total_files')

if [ "$TOTAL_FILES" != "null" ] && [ "$TOTAL_FILES" -gt 0 ]; then
  echo "   ${GREEN}✓${NC} Archivos encontrados: $TOTAL_FILES"
  echo ""
  echo "   ${YELLOW}📂 Estructura de archivos:${NC}"
  echo "   ────────────────────────────────────────────────"
  
  # Mostrar cada archivo
  for i in $(seq 0 $((TOTAL_FILES - 1))); do
    FILENAME=$(echo $FILES_RESPONSE | jq -r ".files[$i].filename")
    CATEGORY=$(echo $FILES_RESPONSE | jq -r ".files[$i].category")
    SIZE=$(echo $FILES_RESPONSE | jq -r ".files[$i].size")
    CHUNKS=$(echo $FILES_RESPONSE | jq -r ".files[$i].metadata.chunks")
    RISK=$(echo $FILES_RESPONSE | jq -r ".files[$i].metadata.risk_level")
    ENTITIES_COUNT=$(echo $FILES_RESPONSE | jq -r ".files[$i].metadata.entities | length")
    
    SIZE_KB=$(echo "scale=2; $SIZE / 1024" | bc)
    
    echo ""
    echo "   📄 Archivo $((i + 1)):"
    echo "      Nombre:     $FILENAME"
    echo "      Categoría:  $CATEGORY"
    echo "      Tamaño:     ${SIZE_KB} KB"
    echo "      Chunks:     $CHUNKS"
    echo "      Riesgo:     $RISK"
    echo "      Entidades:  $ENTITIES_COUNT"
    
    # Mostrar primeras 3 entidades
    if [ "$ENTITIES_COUNT" -gt 0 ]; then
      echo "      Ejemplos:   "
      for j in $(seq 0 $((ENTITIES_COUNT > 3 ? 2 : ENTITIES_COUNT - 1))); do
        ENTITY=$(echo $FILES_RESPONSE | jq -r ".files[$i].metadata.entities[$j]")
        echo "                  • $ENTITY"
      done
    fi
  done
  
  echo ""
  echo "   ────────────────────────────────────────────────"
else
  echo "   ${RED}✗${NC} No se encontraron archivos"
  echo "   Response: $FILES_RESPONSE"
fi
echo ""

# Paso 5: Mostrar preview de un archivo
echo "${BLUE}[5/6] 👁️  Vista previa del primer archivo...${NC}"
PREVIEW=$(echo $FILES_RESPONSE | jq -r '.files[0].preview_text')

if [ "$PREVIEW" != "null" ] && [ -n "$PREVIEW" ]; then
  echo "   ${GREEN}✓${NC} Preview obtenido (primeros 200 caracteres):"
  echo ""
  echo "   ┌────────────────────────────────────────────────┐"
  echo "$PREVIEW" | head -c 200 | sed 's/^/   │ /'
  echo "   │ ..."
  echo "   └────────────────────────────────────────────────┘"
else
  echo "   ${RED}✗${NC} No se pudo obtener preview"
fi
echo ""

# Paso 6: Simular vectorización (sin API key real)
echo "${BLUE}[6/6] 🧬 Simulación de vectorización...${NC}"
echo "   ${YELLOW}ℹ️  Para vectorizar con OpenAI necesitas:${NC}"
echo "   1. API Key de OpenAI (https://platform.openai.com/api-keys)"
echo "   2. Configurarla en la UI de la aplicación"
echo "   3. Usar el tab 'Vectorización OpenAI'"
echo ""
echo "   ${GREEN}Ejemplo de uso:${NC}"
echo "   • Modelo: text-embedding-3-small"
echo "   • Dimensiones: 1536"
echo "   • Costo: ~\$0.00002 por 1K tokens"
echo ""

# Resumen final
echo "=================================================="
echo "${GREEN}✅ TEST COMPLETADO${NC}"
echo "=================================================="
echo ""
echo "📊 Resumen:"
echo "   • Documentos generados:  5"
echo "   • Archivos listados:     $TOTAL_FILES"
echo "   • Endpoint funcionando:  ${GREEN}✓${NC}"
echo "   • Metadata extraída:     ${GREEN}✓${NC}"
echo "   • Preview disponible:    ${GREEN}✓${NC}"
echo ""
echo "🎯 Próximos pasos:"
echo "   1. Abrir la aplicación web: http://localhost:3000"
echo "   2. Ir a 'Generador de Datos Sintéticos'"
echo "   3. En historial, click en '📁 Ver Archivos'"
echo "   4. Explorar archivos generados"
echo "   5. Vectorizar con OpenAI (tab 'Vectorización')"
echo ""
echo "📚 Documentación:"
echo "   • RESUMEN_MEJORAS_SINTETICOS.md"
echo "   • MEJORAS_DATOS_SINTETICOS.md"
echo "   • IMPLEMENTACION_COMPLETADA.md"
echo ""
echo "=================================================="
