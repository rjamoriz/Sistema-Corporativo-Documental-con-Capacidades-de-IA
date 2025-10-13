#!/bin/bash

# Script para corregir imports incorrectos (from backend.xxx → from xxx)
# Solo cuando se ejecuta desde dentro de /backend/

set -e

cd /workspaces/Sistema-Corporativo-Documental-con-Capacidades-de-IA/backend

echo "🔧 Corrigiendo imports en archivos Python..."

# Lista de archivos a corregir
FILES=(
    "services/ingest_service.py"
    "services/transform_service.py"
    "services/extract_service.py"
    "services/classification_service.py"
    "services/search_service.py"
    "services/rag_service.py"
    "services/risk_service.py"
    "services/compliance_service.py"
    "services/synthetic_data_service.py"
    "workers/ingest_worker.py"
    "workers/process_worker.py"
    "workers/index_worker.py"
    "workers/__init__.py"
    "ml/ner_model.py"
    "ml/classifier.py"
    "ml/embeddings.py"
    "ml/llm_client.py"
    "ml/__init__.py"
    "api/v1/synthetic.py"
    "middleware/validation_middleware.py"
    "core/db_performance.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  📝 Corrigiendo $file"
        sed -i 's/from backend\./from /g' "$file"
    fi
done

echo "✅ Imports corregidos!"
echo ""
echo "Archivos modificados: ${#FILES[@]}"
