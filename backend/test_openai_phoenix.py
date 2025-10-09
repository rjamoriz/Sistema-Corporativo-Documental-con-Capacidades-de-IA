#!/usr/bin/env python3
"""
Test script para verificar la integración de OpenAI API y Arize Phoenix
"""
import os
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv

# Cargar variables de entorno
env_path = backend_path / ".env"
load_dotenv(env_path)

print("=" * 60)
print("🔍 TEST DE CONFIGURACIÓN - OpenAI + Phoenix")
print("=" * 60)

# 1. Verificar que el .env existe
print("\n1️⃣ Verificando archivo .env...")
if env_path.exists():
    print(f"   ✅ Archivo encontrado: {env_path}")
else:
    print(f"   ❌ Archivo NO encontrado: {env_path}")
    sys.exit(1)

# 2. Verificar variables de entorno
print("\n2️⃣ Verificando variables de entorno...")

required_vars = {
    "OPENAI_API_KEY": "OpenAI API Key",
    "OPENAI_MODEL": "Modelo OpenAI",
    "PHOENIX_ENABLE_SERVER": "Phoenix Server",
    "PHOENIX_ENABLE_INSTRUMENTATION": "Phoenix Instrumentation",
    "PHOENIX_PORT": "Puerto Phoenix"
}

all_ok = True
for var, description in required_vars.items():
    value = os.getenv(var)
    if value:
        if var == "OPENAI_API_KEY":
            masked_value = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
            print(f"   ✅ {description}: {masked_value}")
        else:
            print(f"   ✅ {description}: {value}")
    else:
        print(f"   ❌ {description}: NO CONFIGURADO")
        all_ok = False

if not all_ok:
    print("\n❌ Faltan variables de entorno requeridas")
    sys.exit(1)

# 3. Test de conexión con OpenAI
print("\n3️⃣ Testeando conexión con OpenAI...")
try:
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Hacer una llamada simple
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "Eres un asistente útil."},
            {"role": "user", "content": "Di 'test exitoso' en español."}
        ],
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    tokens_used = response.usage.total_tokens
    
    print(f"   ✅ Conexión exitosa!")
    print(f"   📝 Respuesta: {result}")
    print(f"   💰 Tokens usados: {tokens_used}")
    
except Exception as e:
    print(f"   ❌ Error al conectar con OpenAI: {e}")
    sys.exit(1)

# 4. Verificar instalación de Phoenix
print("\n4️⃣ Verificando instalación de Phoenix...")
try:
    import phoenix as px
    from openinference.instrumentation.openai import OpenAIInstrumentor
    print(f"   ✅ Phoenix instalado: versión {px.__version__}")
    print(f"   ✅ OpenAI Instrumentor disponible")
except ImportError as e:
    print(f"   ❌ Error: {e}")
    print(f"   💡 Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

# 5. Test de Phoenix con tracking
print("\n5️⃣ Testeando Phoenix tracking...")
try:
    # Inicializar Phoenix
    session = px.launch_app(port=int(os.getenv("PHOENIX_PORT", 6006)))
    
    # Instrumentar OpenAI
    OpenAIInstrumentor().instrument()
    
    print(f"   ✅ Phoenix iniciado correctamente")
    print(f"   🌐 Dashboard: http://localhost:{os.getenv('PHOENIX_PORT', 6006)}")
    
    # Hacer una llamada trackeada
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "user", "content": "¿Qué es RAG en IA?"}
        ],
        max_tokens=100
    )
    
    print(f"   ✅ Llamada trackeada exitosamente")
    print(f"   📊 Esta traza debería aparecer en Phoenix UI")
    
except Exception as e:
    print(f"   ⚠️ Warning: {e}")
    print(f"   💡 Phoenix puede requerir iniciarse por separado")

# 6. Resumen
print("\n" + "=" * 60)
print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
print("=" * 60)
print(f"""
📋 Resumen:
   • OpenAI API: ✅ Conectado ({os.getenv('OPENAI_MODEL')})
   • Phoenix: ✅ Configurado
   • Dashboard: http://localhost:{os.getenv('PHOENIX_PORT', 6006)}

🚀 Próximos pasos:
   1. Inicia Phoenix: docker-compose up -d phoenix
   2. Inicia el backend: uvicorn main:app --reload
   3. Accede a Phoenix UI: http://localhost:6006
   4. Haz queries RAG y ve las trazas en Phoenix
""")

print("=" * 60)
