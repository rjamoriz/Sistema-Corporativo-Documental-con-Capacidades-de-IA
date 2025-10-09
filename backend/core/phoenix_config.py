"""
Arize Phoenix - LLM Observability Configuration

Este módulo configura Arize Phoenix para observabilidad completa de LLMs:
- Tracking de prompts y respuestas
- Métricas de latencia y tokens
- Evaluación de calidad (hallucinations, toxicity)
- Trazabilidad completa de llamadas
- Dashboard interactivo
"""

import os
from typing import Optional
import phoenix as px
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

class PhoenixObservability:
    """Configuración de Arize Phoenix para observabilidad de LLMs"""
    
    def __init__(
        self,
        phoenix_host: str = "http://localhost:6006",
        project_name: str = "docai-rag-system",
        enable_instrumentation: bool = True
    ):
        """
        Inicializa Phoenix Observability
        
        Args:
            phoenix_host: URL del servidor Phoenix
            project_name: Nombre del proyecto para organización
            enable_instrumentation: Habilitar instrumentación automática
        """
        self.phoenix_host = phoenix_host
        self.project_name = project_name
        self.enable_instrumentation = enable_instrumentation
        self._session = None
        self._tracer_provider = None
        
    def start_phoenix_server(self) -> Optional[px.Session]:
        """
        Inicia el servidor Phoenix localmente
        
        Returns:
            Session de Phoenix o None si ya está corriendo
        """
        try:
            # Intentar conectar a servidor existente
            self._session = px.launch_app()
            print(f"✅ Phoenix UI disponible en: {self._session.url}")
            return self._session
        except Exception as e:
            print(f"⚠️ No se pudo iniciar Phoenix: {e}")
            print("💡 Tip: Ejecuta 'phoenix serve' en otra terminal")
            return None
    
    def setup_instrumentation(self):
        """
        Configura instrumentación OpenTelemetry para OpenAI
        """
        if not self.enable_instrumentation:
            return
        
        # Configurar recurso con metadata del proyecto
        resource = Resource.create({
            "service.name": self.project_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "development")
        })
        
        # Configurar TracerProvider
        self._tracer_provider = trace_sdk.TracerProvider(resource=resource)
        
        # Configurar exportador OTLP (Phoenix)
        endpoint = f"{self.phoenix_host}/v1/traces"
        span_exporter = OTLPSpanExporter(endpoint=endpoint)
        
        # Agregar processor
        span_processor = SimpleSpanProcessor(span_exporter)
        self._tracer_provider.add_span_processor(span_processor)
        
        # Establecer como provider global
        trace_api.set_tracer_provider(self._tracer_provider)
        
        # Instrumentar OpenAI automáticamente
        OpenAIInstrumentor().instrument()
        
        print(f"✅ OpenAI instrumentado con Phoenix")
        print(f"📊 Traces enviándose a: {endpoint}")
    
    def get_tracer(self, name: str = "docai-rag"):
        """
        Obtiene un tracer para instrumentación manual
        
        Args:
            name: Nombre del tracer
            
        Returns:
            Tracer de OpenTelemetry
        """
        return trace_api.get_tracer(name)
    
    def log_rag_query(
        self,
        query: str,
        response: str,
        chunks_used: list,
        model: str,
        tokens_used: int,
        latency_ms: float
    ):
        """
        Registra una query RAG completa con contexto
        
        Args:
            query: Query del usuario
            response: Respuesta del LLM
            chunks_used: Lista de chunks recuperados
            model: Modelo utilizado
            tokens_used: Tokens consumidos
            latency_ms: Latencia en milisegundos
        """
        tracer = self.get_tracer()
        
        with tracer.start_as_current_span("rag_query") as span:
            # Atributos de la query
            span.set_attribute("llm.query", query)
            span.set_attribute("llm.response", response)
            span.set_attribute("llm.model", model)
            span.set_attribute("llm.tokens_used", tokens_used)
            span.set_attribute("llm.latency_ms", latency_ms)
            
            # Contexto de retrieval
            span.set_attribute("retrieval.num_chunks", len(chunks_used))
            span.set_attribute("retrieval.chunks", str(chunks_used))
            
            # Métricas de calidad (se pueden evaluar después)
            span.set_attribute("llm.response_length", len(response))
            span.set_attribute("llm.query_length", len(query))
    
    def shutdown(self):
        """Cierra conexiones y limpia recursos"""
        if self._tracer_provider:
            self._tracer_provider.shutdown()
        if self._session:
            self._session.close()
        print("✅ Phoenix observability cerrado correctamente")


# Singleton para uso global
_phoenix_instance: Optional[PhoenixObservability] = None

def get_phoenix() -> PhoenixObservability:
    """Obtiene la instancia singleton de Phoenix"""
    global _phoenix_instance
    if _phoenix_instance is None:
        phoenix_host = os.getenv("PHOENIX_HOST", "http://localhost:6006")
        _phoenix_instance = PhoenixObservability(phoenix_host=phoenix_host)
    return _phoenix_instance

def initialize_phoenix(
    start_server: bool = True,
    enable_instrumentation: bool = True
) -> PhoenixObservability:
    """
    Inicializa Phoenix Observability
    
    Args:
        start_server: Iniciar servidor Phoenix localmente
        enable_instrumentation: Habilitar instrumentación automática
        
    Returns:
        Instancia configurada de PhoenixObservability
    """
    phoenix = get_phoenix()
    phoenix.enable_instrumentation = enable_instrumentation
    
    if start_server:
        phoenix.start_phoenix_server()
    
    if enable_instrumentation:
        phoenix.setup_instrumentation()
    
    return phoenix


# Función helper para logging rápido
def log_llm_call(
    prompt: str,
    response: str,
    model: str = "gpt-4o-mini",
    **kwargs
):
    """
    Helper rápido para logging de llamadas LLM
    
    Args:
        prompt: Prompt enviado
        response: Respuesta recibida
        model: Modelo utilizado
        **kwargs: Metadatos adicionales
    """
    phoenix = get_phoenix()
    tracer = phoenix.get_tracer()
    
    with tracer.start_as_current_span("llm_call") as span:
        span.set_attribute("llm.prompt", prompt)
        span.set_attribute("llm.response", response)
        span.set_attribute("llm.model", model)
        
        for key, value in kwargs.items():
            span.set_attribute(f"llm.{key}", str(value))
