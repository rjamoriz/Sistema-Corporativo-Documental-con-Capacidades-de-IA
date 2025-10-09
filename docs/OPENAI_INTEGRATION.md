# ✅ Integración de OpenAI API Completada

**Fecha:** 9 de octubre de 2025  
**Estado:** ✅ CONFIGURADO Y TESTEADO EXITOSAMENTE

---

## 🎯 Lo que se ha configurado:

### 1. **OpenAI API Token Integrado**
- ✅ Token agregado al archivo `backend/.env`
- ✅ Token verificado y funcionando
- ✅ Modelo configurado: `gpt-4o-mini`
- ✅ Test exitoso: primera llamada completada (31 tokens)

### 2. **Variables de Entorno Configuradas**

Archivo: `backend/.env`

```env
# OpenAI API - CONFIGURADO
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-API-KEY-HERE
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000

# LLM Provider
LLM_PROVIDER=openai

# Arize Phoenix - Observabilidad
PHOENIX_ENABLE_SERVER=true
PHOENIX_ENABLE_INSTRUMENTATION=true
PHOENIX_HOST=http://localhost
PHOENIX_PORT=6006
PHOENIX_PROJECT_NAME=financia-2030-rag
```

### 3. **Seguridad Configurada**
- ✅ Archivo `.gitignore` creado (el `.env` NO se subirá a GitHub)
- ✅ Token protegido localmente
- ⚠️ **IMPORTANTE:** Nunca compartas este token públicamente

### 4. **Test de Conexión**
- ✅ Script de test creado: `backend/test_openai_phoenix.py`
- ✅ Conexión con OpenAI verificada
- ✅ Respuesta recibida: "Test exitoso."
- ✅ Tokens consumidos: 31 tokens

---

## 🚀 Cómo usar el sistema ahora:

### Opción 1: Usar solo OpenAI (sin infraestructura completa)

```bash
# 1. Ir al directorio backend
cd backend

# 2. Instalar dependencias básicas (si no lo has hecho)
pip install python-dotenv openai fastapi uvicorn

# 3. Crear un script de prueba simple
python << 'EOF'
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Eres un asistente financiero experto."},
        {"role": "user", "content": "¿Qué es un RAG en sistemas de IA?"}
    ]
)

print(response.choices[0].message.content)
EOF
```

### Opción 2: Iniciar sistema completo con Phoenix

```bash
# 1. Iniciar infraestructura Docker (incluye Phoenix)
cd infrastructure/docker
docker-compose up -d

# 2. Esperar a que los servicios estén listos
docker-compose ps

# 3. Iniciar backend
cd ../../backend
source venv/bin/activate  # Si usas venv
pip install -r requirements.txt
uvicorn main:app --reload

# 4. Acceder a las interfaces
# Backend API: http://localhost:8000/docs
# Phoenix UI: http://localhost:6006
# Frontend: http://localhost:3000 (si lo inicias)
```

### Opción 3: Solo probar RAG sin infraestructura

Crea un archivo `test_rag_simple.py`:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simular un contexto RAG
context = """
[DOC-1] El contrato tiene un plazo de 24 meses renovables.
[DOC-2] La cláusula 5.1 establece una penalización del 10% por cancelación anticipada.
[DOC-3] El monto total del contrato es de €50,000.
"""

query = "¿Cuál es el plazo del contrato y cuánto cuesta?"

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Eres un asistente que responde SOLO basándote en el contexto proporcionado. Siempre cita las fuentes con [DOC-X]."
        },
        {
            "role": "user",
            "content": f"Contexto:\n{context}\n\nPregunta: {query}"
        }
    ],
    temperature=0.1,
    max_tokens=200
)

print("=" * 60)
print("RESPUESTA RAG:")
print("=" * 60)
print(response.choices[0].message.content)
print("=" * 60)
print(f"Tokens usados: {response.usage.total_tokens}")
print(f"Costo aprox: ${response.usage.total_tokens * 0.00000015:.6f}")
```

Ejecutar:
```bash
cd backend
python test_rag_simple.py
```

---

## 📊 Costos de OpenAI

Con el modelo **gpt-4o-mini**:

| Concepto | Precio | Ejemplo |
|----------|--------|---------|
| Input tokens | $0.150 / 1M tokens | 1,000 tokens = $0.00015 |
| Output tokens | $0.600 / 1M tokens | 1,000 tokens = $0.00060 |
| Query típica RAG | ~500 tokens | ~$0.0003 por query |
| 1,000 queries | ~500k tokens | ~$0.30 |
| 10,000 queries | ~5M tokens | ~$3.00 |

**Estimación para tu caso de uso (100k docs/año):**
- ~10,000 queries/mes
- Costo mensual: ~$3-5 USD
- Costo anual: ~$36-60 USD

---

## 🔍 Verificar el funcionamiento

### 1. Test rápido de OpenAI
```bash
cd backend
python test_openai_phoenix.py
```

Deberías ver:
```
✅ Conexión exitosa!
📝 Respuesta: Test exitoso.
💰 Tokens usados: 31
```

### 2. Ver el token configurado (enmascarado)
```bash
cd backend
grep OPENAI_API_KEY .env | head -c 50
```

### 3. Verificar que `.env` NO está en git
```bash
git status
# No debería aparecer backend/.env
```

---

## 📚 Próximos pasos recomendados:

### 1. **Probar RAG completo**
```bash
# Iniciar solo los servicios necesarios para RAG
cd infrastructure/docker
docker-compose up -d postgres opensearch redis phoenix

# Iniciar backend
cd ../../backend
uvicorn main:app --reload
```

### 2. **Acceder a Phoenix Dashboard**
- URL: http://localhost:6006
- Aquí verás todas las llamadas LLM en tiempo real

### 3. **Hacer una query de prueba**
```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es el plazo del contrato?",
    "category": "LEGAL"
  }'
```

### 4. **Ver la traza en Phoenix**
- Ir a http://localhost:6006
- Ver la traza completa con:
  - Prompt enviado
  - Respuesta recibida
  - Tokens usados
  - Latencia
  - Contexto recuperado

---

## 🐛 Troubleshooting

### Problema: "OpenAI API key not found"
**Solución:**
```bash
# Verificar que el archivo existe
ls -la backend/.env

# Verificar que tiene el token
grep OPENAI_API_KEY backend/.env
```

### Problema: "Rate limit exceeded"
**Solución:**
- Espera 60 segundos (límite de OpenAI)
- O reduce la frecuencia de llamadas
- O aumenta los límites en tu cuenta OpenAI

### Problema: Phoenix no se inicia
**Solución:**
```bash
# Ver logs de Phoenix
cd infrastructure/docker
docker-compose logs -f phoenix

# Reiniciar Phoenix
docker-compose restart phoenix
```

### Problema: "Invalid API key"
**Solución:**
1. Verifica el token en: https://platform.openai.com/api-keys
2. Asegúrate de que está activo y no ha expirado
3. Genera un nuevo token si es necesario
4. Actualiza `backend/.env` con el nuevo token

---

## ✅ Checklist de verificación

- [x] ✅ OpenAI API token configurado en `.env`
- [x] ✅ Token verificado y funcionando
- [x] ✅ `.gitignore` configurado (token protegido)
- [x] ✅ Phoenix configurado para observabilidad
- [x] ✅ Test de conexión exitoso
- [x] ✅ Modelo `gpt-4o-mini` funcionando
- [ ] ⏳ Infraestructura Docker iniciada (pendiente)
- [ ] ⏳ Primera query RAG completa (pendiente)
- [ ] ⏳ Verificar trazas en Phoenix UI (pendiente)

---

## 📖 Documentación relacionada

- 📘 **OpenAI API:** https://platform.openai.com/docs
- 🔍 **Phoenix Observability:** `docs/PHOENIX_OBSERVABILITY.md`
- 🚀 **Quick Start:** `QUICKSTART.md`
- 📊 **Arquitectura:** `docs/ARCHITECTURE.md`

---

**🎉 ¡Todo listo! Tu sistema ya tiene OpenAI integrado y funcionando.**

**Próximo paso:** Iniciar la infraestructura con `docker-compose up -d` y hacer tu primera query RAG.
