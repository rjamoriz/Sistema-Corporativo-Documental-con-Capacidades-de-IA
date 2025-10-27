# 🎮 GPU Embedding Service

Servicio independiente para generación de embeddings acelerada por GPU NVIDIA.

## 🎯 Características

- ⚡ **Aceleración GPU**: Utiliza NVIDIA RTX para embeddings ultra-rápidos
- 📊 **FAISS Integration**: Búsqueda vectorial optimizada
- 🔄 **Batch Processing**: Procesamiento eficiente de grandes volúmenes
- 📈 **Métricas Prometheus**: Monitoreo en tiempo real
- 🔌 **API REST**: Integración sencilla con cualquier sistema
- 🚀 **Fallback CPU**: Funciona sin GPU (más lento)

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# Construir imagen
docker build -t gpu-embedding-service .

# Ejecutar con GPU
docker run --gpus all -p 8001:8001 gpu-embedding-service

# Ejecutar sin GPU (CPU fallback)
docker run -p 8001:8001 gpu-embedding-service
```

### Opción 2: Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servicio
python main.py
```

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Generate Embeddings
```bash
POST /api/v1/embeddings/generate
Content-Type: application/json

{
  "texts": ["Hello world", "Hola mundo"],
  "model_name": "paraphrase-multilingual-mpnet-base-v2",
  "normalize": true
}
```

### Batch Processing
```bash
POST /api/v1/embeddings/batch
Content-Type: application/json

{
  "texts": ["text1", "text2", ...],
  "batch_size": 32
}
```

### Similarity Search
```bash
POST /api/v1/similarity/search
Content-Type: application/json

{
  "query_text": "search query",
  "top_k": 10,
  "threshold": 0.7
}
```

### Add to Index
```bash
POST /api/v1/index/add
Content-Type: application/json

["document 1", "document 2", ...]
```

## 📊 Métricas

Accede a métricas Prometheus en:
```
GET /metrics
```

Métricas disponibles:
- `embeddings_generated_total`: Total de embeddings generados
- `embedding_duration_seconds`: Tiempo de generación
- `gpu_memory_used_bytes`: Memoria GPU utilizada
- `active_requests`: Requests activos

## 🔧 Configuración

Copia `.env.example` a `.env` y ajusta:

```env
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2
SERVICE_PORT=8001
CUDA_VISIBLE_DEVICES=0
```

## 📈 Performance

### Con GPU (NVIDIA RTX 4070)
- **Throughput**: ~1000 embeddings/segundo
- **Latencia**: <10ms por documento
- **Batch 100**: ~100ms total

### Sin GPU (CPU Fallback)
- **Throughput**: ~50 embeddings/segundo
- **Latencia**: ~200ms por documento
- **Batch 100**: ~2000ms total

## 🧪 Testing

```bash
# Test básico
curl http://localhost:8001/health

# Test embeddings
curl -X POST http://localhost:8001/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test"]}'
```

## 🔗 Integración con App Principal

Este servicio es **completamente independiente** y no afecta la app actual.

Para integrarlo:

1. **Opción A - Feature Flag**: Añadir flag `USE_GPU_EMBEDDINGS=true` en backend
2. **Opción B - API Gateway**: Rutear requests a través de gateway
3. **Opción C - Fallback**: Usar GPU si disponible, sino usar servicio actual

## 📝 Notas

- ✅ **No rompe nada**: Servicio completamente independiente
- ✅ **Opcional**: Se puede activar/desactivar
- ✅ **Compatible**: API compatible con sistema actual
- ✅ **Monitoreado**: Métricas completas disponibles

## 🐛 Troubleshooting

### GPU no detectada
```bash
# Verificar CUDA
nvidia-smi

# Verificar PyTorch
python -c "import torch; print(torch.cuda.is_available())"
```

### Out of Memory
- Reducir `batch_size`
- Usar modelo más pequeño (`all-MiniLM-L6-v2`)
- Liberar memoria: `torch.cuda.empty_cache()`

## 📚 Documentación

- [Plan de Mejora Completo](../../docs/QUANTUM_GPU_ENHANCEMENT_PLAN.md)
- [FastAPI Docs](http://localhost:8001/docs)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
