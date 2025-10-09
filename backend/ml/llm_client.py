"""
Cliente unificado para LLMs (OpenAI, Anthropic, Llama local)
"""
from typing import List, Dict, Optional, AsyncGenerator
from enum import Enum
import asyncio

from openai import AsyncOpenAI
import anthropic

from backend.core.logging_config import logger
from backend.core.config import settings


class LLMProvider(str, Enum):
    """Proveedores de LLM soportados"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class LLMClient:
    """Cliente unificado para diferentes proveedores de LLM"""
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or LLMProvider(settings.LLM_PROVIDER)
        self.client = None
        self.model = None
        self._init_client()
    
    def _init_client(self):
        """Inicializa el cliente según el proveedor"""
        if self.provider == LLMProvider.OPENAI:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            logger.info(f"Initialized OpenAI client with model {self.model}")
            
        elif self.provider == LLMProvider.ANTHROPIC:
            self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
            logger.info(f"Initialized Anthropic client with model {self.model}")
            
        elif self.provider == LLMProvider.LOCAL:
            # Modelo local con transformers
            from transformers import pipeline
            self.client = pipeline(
                "text-generation",
                model=settings.LOCAL_LLM_MODEL,
                device=0 if settings.USE_GPU else -1
            )
            self.model = settings.LOCAL_LLM_MODEL
            logger.info(f"Initialized local LLM with model {self.model}")
        
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """
        Genera respuesta de chat
        
        Args:
            messages: Lista de mensajes [{"role": "user|assistant|system", "content": "..."}]
            temperature: Temperatura de generación (0-1)
            max_tokens: Máximo de tokens a generar
            stream: Streaming de respuesta
            
        Returns:
            str: Respuesta generada
        """
        if self.provider == LLMProvider.OPENAI:
            return await self._chat_openai(messages, temperature, max_tokens, stream)
        elif self.provider == LLMProvider.ANTHROPIC:
            return await self._chat_anthropic(messages, temperature, max_tokens, stream)
        elif self.provider == LLMProvider.LOCAL:
            return await self._chat_local(messages, temperature, max_tokens)
    
    async def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str:
        """Chat con OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                full_response = ""
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise
    
    async def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str:
        """Chat con Anthropic Claude"""
        try:
            # Separar system message
            system_message = ""
            filtered_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    filtered_messages.append(msg)
            
            response = await self.client.messages.create(
                model=self.model,
                system=system_message,
                messages=filtered_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise
    
    async def _chat_local(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Chat con modelo local"""
        try:
            # Construir prompt desde mensajes
            prompt = "\n\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in messages
            ])
            
            # Ejecutar en thread pool para no bloquear
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client(
                    prompt,
                    max_length=max_tokens,
                    temperature=temperature,
                    do_sample=True
                )[0]["generated_text"]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Local LLM chat error: {e}")
            raise
    
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Completar texto (modo completion)
        
        Args:
            prompt: Prompt inicial
            temperature: Temperatura
            max_tokens: Máximo de tokens
            
        Returns:
            str: Texto completado
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, temperature, max_tokens)
    
    async def summarize(
        self,
        text: str,
        max_length: int = 500,
        language: str = "spanish"
    ) -> str:
        """
        Resume un texto
        
        Args:
            text: Texto a resumir
            max_length: Longitud máxima del resumen
            language: Idioma del resumen
            
        Returns:
            str: Resumen generado
        """
        prompt = f"""Resume el siguiente texto en {language} en máximo {max_length} palabras.
Mantén los puntos clave y el contexto importante.

Texto:
{text[:10000]}

Resumen:"""
        
        return await self.complete(prompt, temperature=0.3, max_tokens=max_length * 2)
    
    async def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """
        Extrae palabras clave de un texto
        
        Args:
            text: Texto a analizar
            num_keywords: Número de palabras clave
            
        Returns:
            List[str]: Lista de palabras clave
        """
        prompt = f"""Extrae las {num_keywords} palabras clave más importantes del siguiente texto.
Devuelve solo las palabras clave separadas por comas, sin numeración ni explicaciones.

Texto:
{text[:5000]}

Palabras clave:"""
        
        response = await self.complete(prompt, temperature=0.3, max_tokens=200)
        keywords = [kw.strip() for kw in response.split(",")]
        return keywords[:num_keywords]
    
    async def classify_sentiment(self, text: str) -> Dict[str, float]:
        """
        Clasifica el sentimiento de un texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict[str, float]: Scores de sentimiento (positivo, negativo, neutral)
        """
        prompt = f"""Analiza el sentimiento del siguiente texto y proporciona scores de 0 a 1 para:
- Positivo
- Negativo
- Neutral

Responde SOLO con el formato: positivo:X.XX,negativo:X.XX,neutral:X.XX

Texto:
{text[:2000]}

Análisis:"""
        
        response = await self.complete(prompt, temperature=0.1, max_tokens=50)
        
        # Parse respuesta
        sentiments = {"positivo": 0.0, "negativo": 0.0, "neutral": 1.0}
        try:
            parts = response.strip().split(",")
            for part in parts:
                key, value = part.split(":")
                sentiments[key.strip()] = float(value.strip())
        except:
            logger.warning("Could not parse sentiment response")
        
        return sentiments
    
    def get_model_info(self) -> Dict:
        """
        Obtiene información del modelo
        
        Returns:
            Dict: Información del modelo
        """
        return {
            "provider": self.provider.value,
            "model": self.model,
            "max_tokens": getattr(settings, f"{self.provider.upper()}_MAX_TOKENS", None)
        }


# Instancia singleton del cliente
llm_client = LLMClient()
