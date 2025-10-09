# 🔍 Arize Phoenix - Observabilidad de LLMs

## 📊 Descripción

**Arize Phoenix** es una plataforma de observabilidad de código abierto diseñada específicamente para aplicaciones de LLM (Large Language Models). Permite monitorear, debuggear y mejorar sistemas RAG y agentes de IA con tracking completo de:

- ✅ **Prompts y respuestas** - Trazabilidad completa de interacciones
- ✅ **Métricas de rendimiento** - Latencia, tokens, costos
- ✅ **Calidad de respuestas** - Detección de alucinaciones, toxicidad
- ✅ **Retrieval effectiveness** - Relevancia de documentos recuperados
- ✅ **Comparación de modelos** - A/B testing de diferentes LLMs

---

## 🚀 Inicio Rápido

### 1. Iniciar Phoenix con Docker

```bash
# Iniciar con docker-compose (incluye Phoenix)
cd infrastructure/docker
docker-compose up -d phoenix

# O ejecutar Phoenix standalone
docker run -p 6006:6006 -p 4317:4317 -p 4318:4318 arizephoenix/phoenix:latest
```

### 2. Acceder a Phoenix UI

Abre tu navegador en: **http://localhost:6006**

Verás el dashboard principal con:
- 📊 **Traces** - Registro de todas las llamadas LLM
- 📈 **Evaluations** - Métricas de calidad
- 🔍 **Search** - Buscar por queries específicas
- 📝 **Projects** - Diferentes experimentos

### 3. Configurar Variables de Entorno

Crea o actualiza tu archivo `.env` en `/backend`:

```env
# OpenAI API Key (REQUERIDO)
OPENAI_API_KEY=sk-proj-your-api-key-here

# Phoenix Configuration
PHOENIX_ENABLE_SERVER=true
PHOENIX_ENABLE_INSTRUMENTATION=true
PHOENIX_HOST=http://localhost
PHOENIX_PORT=6006
PHOENIX_PROJECT_NAME=financia-2030-rag

# LLM Provider
LLM_PROVIDER=openai  # openai, anthropic, local
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000
```

### 4. Iniciar Backend con Phoenix

```bash
cd backend
source venv/bin/activate

# Instalar dependencias de Phoenix si no están
pip install arize-phoenix openinference-instrumentation-openai

# Iniciar aplicación
uvicorn main:app --reload
```

Deberías ver en los logs:
```
✅ Phoenix observability initialized
📊 Phoenix UI: http://localhost:6006
```

---

## 📖 Uso en el Código

### Instrumentación Automática (OpenAI)

Phoenix instrumenta automáticamente todas las llamadas a OpenAI:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Esta llamada será automáticamente trackeada por Phoenix
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Eres un asistente útil"},
        {"role": "user", "content": "¿Qué es RAG?"}
    ]
)
```

### Logging Manual de RAG Query

En `rag_service.py`, cada query completa se registra:

```python
from backend.core.phoenix_config import get_phoenix

phoenix = get_phoenix()
phoenix.log_rag_query(
    query="¿Cuál es el plazo del contrato?",
    response="El contrato tiene un plazo de 24 meses [DOC-1]",
    chunks_used=[{
        "document_id": "abc123",
        "filename": "contrato.pdf",
        "score": 0.89
    }],
    model="gpt-4o-mini",
    tokens_used=245,
    latency_ms=1234.5
)
```

### Logging Personalizado

```python
from backend.core.phoenix_config import log_llm_call

log_llm_call(
    prompt="Analiza este documento...",
    response="El documento contiene...",
    model="gpt-4o-mini",
    user_id="user-123",
    document_id="doc-456",
    category="LEGAL"
)
```

---

## 📊 Métricas Disponibles en Phoenix

### 1. **Traces (Trazas)**

Cada llamada LLM genera una traza con:
- 🕐 **Timestamp** - Cuándo se realizó
- ⏱️ **Latencia** - Tiempo de respuesta en ms
- 🎯 **Input** - Prompt completo
- 📝 **Output** - Respuesta del LLM
- 💰 **Tokens** - Prompt + completion tokens
- 🏷️ **Model** - gpt-4o-mini, claude-3, etc.
- 📎 **Metadata** - user_id, document_id, etc.

### 2. **Evaluations (Evaluaciones)**

Phoenix puede evaluar automáticamente:
- **Hallucination** - ¿La respuesta está fundamentada?
- **Toxicity** - ¿Contenido inapropiado?
- **Relevance** - ¿Responde a la pregunta?
- **Coherence** - ¿Es coherente la respuesta?

### 3. **Embeddings**

Visualiza embeddings en 2D/3D para:
- Ver clusters de queries similares
- Identificar outliers
- Analizar cobertura de documentos

### 4. **Retrieval Analysis**

Para sistemas RAG:
- **Precision@K** - Precisión de retrieval
- **Recall@K** - Cobertura de retrieval
- **NDCG** - Normalized Discounted Cumulative Gain
- **Hit Rate** - % de queries con al menos 1 documento relevante

---

## 🔍 Casos de Uso

### 1. Debugging de Alucinaciones

**Problema:** El LLM responde con información incorrecta.

**Solución con Phoenix:**
1. Buscar la query en Phoenix UI
2. Ver el trace completo con contexto recuperado
3. Comparar respuesta con chunks recuperados
4. Identificar si el problema es:
   - ❌ Retrieval (chunks incorrectos)
   - ❌ LLM (ignora contexto)
   - ❌ Prompt (instrucciones ambiguas)

**Ejemplo:**
```
Query: "¿Cuánto cuesta el producto X?"
Context: [DOC-1] El producto Y cuesta $100
Response: "El producto X cuesta $100" ❌ ALUCINACIÓN

Fix: Mejorar retrieval o prompt con verificación más estricta
```

### 2. Optimización de Costos

**Análisis en Phoenix:**
- Ver distribución de tokens por query
- Identificar queries que usan demasiados tokens
- Detectar contexto redundante

**Ejemplo:**
```
Antes: Promedio 1500 tokens/query = $0.003/query
Después: Optimizar contexto a 800 tokens = $0.0016/query
Ahorro: 47% en costos LLM
```

### 3. A/B Testing de Modelos

**Comparar:**
- gpt-4o-mini vs gpt-4o
- gpt-4 vs claude-3-sonnet
- Diferentes temperaturas (0.1 vs 0.7)

**Métricas:**
- Latencia promedio
- Calidad de respuestas (hallucination rate)
- Costo por query
- User satisfaction (si se recolecta feedback)

### 4. Mejora Continua de Prompts

**Workflow:**
1. Ejecutar 100 queries de prueba
2. Analizar en Phoenix qué prompts fallan
3. Iterar sobre prompt template
4. Re-ejecutar y comparar métricas

---

## 📈 Dashboard de Phoenix

### Vista Principal (Traces)

```
┌─────────────────────────────────────────────────────────┐
│ Phoenix - financia-2030-rag                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📊 Métricas Generales (últimas 24h)                   │
│  ┌──────────────┬──────────────┬──────────────┐       │
│  │ Total Traces │ Avg Latency  │ Total Tokens │       │
│  │     1,234    │    1.2s      │   245,678    │       │
│  └──────────────┴──────────────┴──────────────┘       │
│                                                         │
│  📝 Traces Recientes                                    │
│  ┌────────┬──────────┬─────────┬──────────────┐       │
│  │ Time   │ Query    │ Latency │ Status       │       │
│  ├────────┼──────────┼─────────┼──────────────┤       │
│  │ 10:30  │ ¿Cuál... │ 1.2s    │ ✅ Success  │       │
│  │ 10:29  │ Resumen..│ 2.1s    │ ✅ Success  │       │
│  │ 10:28  │ ¿Qué...  │ 0.8s    │ ⚠️ Warning  │       │
│  └────────┴──────────┴─────────┴──────────────┘       │
│                                                         │
│  [Ver Detalles] [Evaluaciones] [Exportar]             │
└─────────────────────────────────────────────────────────┘
```

### Vista de Trace Individual

```
┌─────────────────────────────────────────────────────────┐
│ Trace: abc123-def456                                    │
├─────────────────────────────────────────────────────────┤
│  🕐 Timestamp: 2025-10-09 10:30:45                      │
│  ⏱️ Latency: 1,234 ms                                   │
│  🎯 Model: gpt-4o-mini                                   │
│  💰 Tokens: 245 (150 prompt + 95 completion)           │
│                                                         │
│  📥 INPUT (Prompt)                                      │
│  ┌─────────────────────────────────────────────────┐  │
│  │ System: Eres un asistente experto...           │  │
│  │                                                 │  │
│  │ Context:                                        │  │
│  │ [DOC-1] El contrato establece un plazo de...   │  │
│  │ [DOC-2] La cláusula 5.1 indica...              │  │
│  │                                                 │  │
│  │ User: ¿Cuál es el plazo del contrato?          │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  📤 OUTPUT (Response)                                   │
│  ┌─────────────────────────────────────────────────┐  │
│  │ El contrato tiene un plazo de 24 meses [DOC-1] │  │
│  │ según se establece en la cláusula...            │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  🔍 Retrieval Context                                   │
│  ┌─────────┬──────────────────┬────────┐              │
│  │ Doc ID  │ Filename         │ Score  │              │
│  ├─────────┼──────────────────┼────────┤              │
│  │ DOC-1   │ contrato.pdf     │ 0.89   │              │
│  │ DOC-2   │ anexo_legal.pdf  │ 0.76   │              │
│  └─────────┴──────────────────┴────────┘              │
│                                                         │
│  ✅ Evaluations                                         │
│  Hallucination: LOW (0.12)                              │
│  Relevance: HIGH (0.91)                                 │
│  Coherence: HIGH (0.88)                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuración Avanzada

### Evaluadores Personalizados

Puedes configurar evaluadores custom en Phoenix:

```python
import phoenix as px
from phoenix.evals import (
    HallucinationEvaluator,
    RelevanceEvaluator,
    ToxicityEvaluator
)

# Configurar evaluadores
hallucination_eval = HallucinationEvaluator()
relevance_eval = RelevanceEvaluator()

# Aplicar a traces
evaluations = px.evaluate(
    dataframe=traces_df,
    evaluators=[hallucination_eval, relevance_eval]
)
```

### Exportar Datos

```python
import phoenix as px

# Obtener todas las traces
traces = px.get_traces(project_name="financia-2030-rag")

# Exportar a Pandas DataFrame
df = traces.to_dataframe()

# Exportar a CSV
df.to_csv("phoenix_traces_export.csv")

# Análisis personalizado
high_latency = df[df['latency_ms'] > 2000]
print(f"Queries lentas: {len(high_latency)}")
```

---

## 🎯 Best Practices

### 1. **Naming Convention**

Usa nombres descriptivos para spans:

```python
with tracer.start_as_current_span("rag_query_legal_contract") as span:
    span.set_attribute("category", "LEGAL")
    span.set_attribute("user_department", "legal")
```

### 2. **Metadata Rica**

Incluye contexto relevante:

```python
phoenix.log_rag_query(
    query=query,
    response=response,
    chunks_used=chunks,
    model=model,
    tokens_used=tokens,
    latency_ms=latency,
    # Metadata adicional
    user_id=user_id,
    document_category=category,
    risk_level=risk_level,
    compliance_status=compliance
)
```

### 3. **Sampling para Producción**

En PROD, considera sampling para reducir volumen:

```python
# Ejemplo: 10% sampling
import random

if random.random() < 0.1:
    phoenix.log_rag_query(...)
```

### 4. **Alerts y Monitoring**

Configura alertas para:
- ❗ Latencia > 5s
- ❗ Hallucination rate > 10%
- ❗ Error rate > 5%
- ❗ Cost por día > umbral

---

## 📚 Recursos Adicionales

- 📖 **Documentación oficial:** https://docs.arize.com/phoenix
- 💬 **Discord community:** https://discord.gg/arize
- 🐙 **GitHub:** https://github.com/Arize-ai/phoenix
- 🎓 **Tutorials:** https://docs.arize.com/phoenix/tutorials

---

## 🐛 Troubleshooting

### Phoenix no inicia

```bash
# Verificar que el puerto 6006 esté libre
lsof -i :6006

# Reiniciar container
docker-compose restart phoenix

# Ver logs
docker-compose logs -f phoenix
```

### No aparecen traces

**Causas comunes:**
1. ❌ `PHOENIX_ENABLE_INSTRUMENTATION=false` en .env
2. ❌ OpenAI API key inválida
3. ❌ Phoenix host incorrecto

**Solución:**
```bash
# Verificar configuración
grep PHOENIX backend/.env

# Verificar que Phoenix esté corriendo
curl http://localhost:6006/healthz

# Ver logs del backend
tail -f backend/logs/app.log
```

### Latencia alta en producción

Phoenix agrega ~5-10ms de overhead. Si es crítico:
- Usar sampling (10% de traces)
- Envío asíncrono de traces
- Aumentar batch size

---

**🎉 ¡Listo! Ahora tienes observabilidad completa de tus LLMs con Phoenix.**

**📊 Dashboard:** http://localhost:6006
