"""
Servicio RAG (Retrieval-Augmented Generation)
Combina búsqueda de contexto con generación de LLM, incluyendo anti-alucinación y citaciones
Integrado con Arize Phoenix para observabilidad completa de LLM
"""
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import time

from sqlalchemy.ext.asyncio import AsyncSession
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from openai import AsyncOpenAI
import anthropic

from backend.core.logging_config import logger, audit_logger
from backend.core.config import settings
from backend.core.phoenix_config import get_phoenix, log_llm_call
from backend.models.schemas import RAGQuery, RAGResponse, Citation
from backend.services.search_service import search_service


class RAGService:
    """Servicio para RAG con anti-alucinación"""
    
    def __init__(self):
        # Inicializar clientes LLM
        if settings.LLM_PROVIDER == "openai":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        elif settings.LLM_PROVIDER == "anthropic":
            self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
        else:
            # Modelo local (Llama-3)
            from transformers import pipeline
            self.client = pipeline("text-generation", model=settings.LOCAL_LLM_MODEL)
            self.model = "local"
        
        # Plantillas de prompts
        self.system_prompt = """Eres un asistente experto en análisis de documentos corporativos.
Tu trabajo es responder preguntas basándote ÚNICAMENTE en el contexto proporcionado.

REGLAS CRÍTICAS:
1. Solo usa información del contexto proporcionado
2. Si la información no está en el contexto, di "No tengo información suficiente en los documentos proporcionados"
3. SIEMPRE cita la fuente cuando uses información específica usando [DOC-X]
4. No inventes ni asumas información que no esté explícita
5. Si encuentras información contradictoria, menciona ambas versiones con sus fuentes
6. Responde en español de forma clara y profesional

FORMATO DE CITACIÓN:
- Usa [DOC-1], [DOC-2], etc. para referenciar documentos
- Coloca la citación inmediatamente después de la información relevante
- Ejemplo: "El contrato fue firmado el 15 de enero de 2024 [DOC-3]"
"""
        
        self.query_prompt_template = """Contexto de documentos:

{context}

---

Pregunta del usuario: {question}

Responde basándote ÚNICAMENTE en el contexto proporcionado. Cita las fuentes usando [DOC-X]."""
        
        # Configuración de conversaciones
        self.conversations = {}  # En producción usar Redis
        self.max_conversation_length = 10
    
    async def query(
        self,
        query: RAGQuery,
        db: AsyncSession,
        user_id: UUID
    ) -> RAGResponse:
        """
        Procesa una consulta RAG
        
        Args:
            query: Consulta del usuario
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            RAGResponse: Respuesta con citaciones
        """
        try:
            conversation_id = query.conversation_id or str(uuid4())
            
            # 1. Recuperar contexto relevante mediante búsqueda híbrida
            search_results = await search_service.hybrid_search(
                query=query.question,
                db=db,
                limit=query.top_k,
                filters=query.filters,
                user_id=user_id
            )
            
            if not search_results.results:
                return RAGResponse(
                    answer="No encontré documentos relevantes para responder tu pregunta.",
                    citations=[],
                    conversation_id=conversation_id,
                    confidence=0.0
                )
            
            # 2. Preparar contexto con numeración para citaciones
            context_parts = []
            citations_map = {}
            
            for idx, result in enumerate(search_results.results, start=1):
                doc_label = f"DOC-{idx}"
                context_parts.append(f"[{doc_label}] {result.chunk_content}")
                
                citations_map[doc_label] = Citation(
                    document_id=result.document_id,
                    filename=result.filename,
                    chunk_content=result.chunk_content,
                    relevance_score=result.score,
                    doc_label=doc_label
                )
            
            context = "\n\n".join(context_parts)
            
            # 3. Obtener historial de conversación
            conversation_history = self._get_conversation_history(conversation_id)
            
            # 4. Generar respuesta con LLM
            answer, used_citations = await self._generate_answer(
                question=query.question,
                context=context,
                conversation_history=conversation_history,
                citations_map=citations_map
            )
            
            # 5. Verificar anti-alucinación
            confidence = await self._verify_answer(answer, context)
            
            # 6. Actualizar conversación
            self._update_conversation(conversation_id, query.question, answer)
            
            # 7. Log de auditoría
            audit_logger.info(
                "RAG query processed",
                extra={
                    "action": "rag_query",
                    "user_id": str(user_id),
                    "conversation_id": conversation_id,
                    "question": query.question,
                    "documents_retrieved": len(search_results.results),
                    "citations_used": len(used_citations),
                    "confidence": confidence
                }
            )
            
            return RAGResponse(
                answer=answer,
                citations=used_citations,
                conversation_id=conversation_id,
                confidence=confidence,
                documents_count=len(search_results.results)
            )
            
        except Exception as e:
            logger.error(f"Error processing RAG query: {e}", exc_info=True)
            return RAGResponse(
                answer=f"Error al procesar la consulta: {str(e)}",
                citations=[],
                conversation_id=conversation_id if 'conversation_id' in locals() else str(uuid4()),
                confidence=0.0
            )
    
    async def _generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: List[Dict],
        citations_map: Dict[str, Citation]
    ) -> tuple[str, List[Citation]]:
        """Genera respuesta usando LLM con observabilidad Phoenix"""
        try:
            # Iniciar tracking de tiempo
            start_time = time.time()
            
            # Construir prompt
            prompt = self.query_prompt_template.format(
                context=context,
                question=question
            )
            
            # Agregar historial si existe
            messages = [{"role": "system", "content": self.system_prompt}]
            
            for entry in conversation_history[-6:]:  # Últimos 3 turnos
                messages.append({"role": "user", "content": entry["question"]})
                messages.append({"role": "assistant", "content": entry["answer"]})
            
            messages.append({"role": "user", "content": prompt})
            
            # Generar respuesta según proveedor
            answer = ""
            tokens_used = 0
            
            if settings.LLM_PROVIDER == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS
                )
                answer = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                
                # Log a Phoenix para OpenAI (auto-instrumentado)
                logger.info(f"OpenAI call completed: {tokens_used} tokens")
                
            elif settings.LLM_PROVIDER == "anthropic":
                response = await self.client.messages.create(
                    model=self.model,
                    system=self.system_prompt,
                    messages=messages[1:],  # Excluir system message
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS
                )
                answer = response.content[0].text
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
                
                # Log manual a Phoenix para Anthropic
                log_llm_call(
                    prompt=prompt,
                    response=answer,
                    model=self.model,
                    provider="anthropic",
                    tokens_used=tokens_used
                )
                
            else:
                # Modelo local
                full_prompt = "\n\n".join([m["content"] for m in messages])
                response = self.client(full_prompt, max_length=settings.LLM_MAX_TOKENS)
                answer = response[0]["generated_text"]
                tokens_used = len(answer.split())  # Aproximación
                
                # Log manual a Phoenix para modelo local
                log_llm_call(
                    prompt=prompt,
                    response=answer,
                    model=self.model,
                    provider="local",
                    tokens_used=tokens_used
                )
            
            # Calcular latencia
            latency_ms = (time.time() - start_time) * 1000
            
            # Extraer citaciones usadas
            import re
            citation_pattern = r'\[DOC-\d+\]'
            used_labels = re.findall(citation_pattern, answer)
            used_citations = [citations_map[label] for label in used_labels if label in citations_map]
            
            # Log completo RAG query a Phoenix
            phoenix = get_phoenix()
            phoenix.log_rag_query(
                query=question,
                response=answer,
                chunks_used=[{
                    "document_id": str(c.document_id),
                    "filename": c.filename,
                    "score": c.relevance_score
                } for c in used_citations],
                model=self.model,
                tokens_used=tokens_used,
                latency_ms=latency_ms
            )
            
            # Log para métricas internas
            logger.info(
                f"RAG answer generated: {latency_ms:.2f}ms, {tokens_used} tokens, {len(used_citations)} citations"
            )
            
            return answer, used_citations
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}", exc_info=True)
            return "Error al generar respuesta", []
    
    async def _verify_answer(self, answer: str, context: str) -> float:
        """
        Verifica que la respuesta esté fundamentada en el contexto (anti-alucinación)
        
        Returns:
            float: Nivel de confianza (0-1)
        """
        try:
            # Estrategia 1: Verificar que las oraciones clave estén en el contexto
            from difflib import SequenceMatcher
            
            answer_sentences = answer.split('.')
            context_lower = context.lower()
            
            matching_scores = []
            for sentence in answer_sentences:
                sentence_clean = sentence.strip().lower()
                if len(sentence_clean) < 10:  # Ignorar oraciones muy cortas
                    continue
                
                # Buscar similitud con fragmentos del contexto
                max_similarity = 0
                for context_chunk in context_lower.split('\n'):
                    similarity = SequenceMatcher(None, sentence_clean, context_chunk).ratio()
                    max_similarity = max(max_similarity, similarity)
                
                matching_scores.append(max_similarity)
            
            # Confianza basada en promedio de similitud
            confidence = sum(matching_scores) / len(matching_scores) if matching_scores else 0.5
            
            # Penalizar si no hay citaciones
            if '[DOC-' not in answer:
                confidence *= 0.7
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Error verifying answer: {e}")
            return 0.5
    
    def _get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Obtiene el historial de conversación"""
        return self.conversations.get(conversation_id, [])
    
    def _update_conversation(self, conversation_id: str, question: str, answer: str):
        """Actualiza el historial de conversación"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Limitar tamaño del historial
        if len(self.conversations[conversation_id]) > self.max_conversation_length:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_conversation_length:]
    
    def get_conversation(self, conversation_id: str) -> Optional[List[Dict]]:
        """Obtiene una conversación completa"""
        return self.conversations.get(conversation_id)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Elimina una conversación"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
    
    async def summarize_document(self, document_text: str, max_length: int = 500) -> str:
        """
        Genera un resumen de un documento
        
        Args:
            document_text: Texto completo del documento
            max_length: Longitud máxima del resumen
            
        Returns:
            str: Resumen generado
        """
        try:
            prompt = f"""Resume el siguiente documento en {max_length} palabras o menos.
El resumen debe ser objetivo, capturar los puntos clave y mantener el contexto profesional.

Documento:
{document_text[:5000]}

Resumen:"""
            
            if settings.LLM_PROVIDER == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Eres un experto en resumir documentos corporativos."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=max_length * 2
                )
                summary = response.choices[0].message.content
            else:
                # Implementación similar para otros proveedores
                summary = "Resumen no disponible con el proveedor actual"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Error al generar resumen"


# Instancia singleton del servicio
rag_service = RAGService()
