import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, DocumentIcon } from '@heroicons/react/24/outline';
import { ragApi } from '@/lib/api-client';
import type { ChatMessage } from '@/types';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';

interface ChunkReference {
  document_id: string;
  document_filename: string;
  content: string;
  score: number;
}

const MessageBubble: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-3xl rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-primary-600 text-white'
            : 'bg-white border border-gray-200 text-gray-900'
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {message.chunks && message.chunks.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
            <p className="text-xs font-semibold text-gray-600 mb-2">
              Referencias ({message.chunks.length}):
            </p>
            {message.chunks.map((chunk, idx) => (
              <div
                key={idx}
                className="text-xs bg-gray-50 rounded p-2 border border-gray-200"
              >
                <div className="flex items-center gap-2 mb-1">
                  <DocumentIcon className="w-3 h-3 text-gray-500" />
                  <span className="font-medium text-gray-700">
                    {chunk.document_filename}
                  </span>
                  <span className="text-gray-500">
                    (Score: {chunk.score.toFixed(2)})
                  </span>
                </div>
                <p className="text-gray-600 line-clamp-2">{chunk.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export const RAGChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content:
        '¡Hola! Soy tu asistente de documentos con IA. Puedo ayudarte a responder preguntas sobre tus documentos usando Retrieval-Augmented Generation (RAG). ¿En qué puedo ayudarte?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setStreamingContent('');

    try {
      let fullResponse = '';
      let responseChunks: ChunkReference[] = [];

      await ragApi.askStream(
        {
          query: userMessage.content,
          max_chunks: 5,
          temperature: 0.7,
          stream: true,
        },
        (chunk) => {
          fullResponse += chunk;
          setStreamingContent(fullResponse);
        },
        (response) => {
          responseChunks = response.chunks_used.map((c) => ({
            document_id: c.document_id,
            document_filename: `Document ${c.document_id.slice(0, 8)}`,
            content: c.content,
            score: c.score,
          }));
        }
      );

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: fullResponse,
        chunks: responseChunks,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setStreamingContent('');
    } catch (error) {
      console.error('Error in RAG chat:', error);
      toast.error('Error al procesar tu pregunta');
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Lo siento, ocurrió un error al procesar tu pregunta. Por favor intenta de nuevo.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content:
          '¡Hola! Soy tu asistente de documentos con IA. Puedo ayudarte a responder preguntas sobre tus documentos usando Retrieval-Augmented Generation (RAG). ¿En qué puedo ayudarte?',
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      <div className="card flex-1 flex flex-col">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Chat RAG con Documentos</h2>
          <button
            onClick={handleClearChat}
            className="btn-secondary text-sm"
          >
            Limpiar chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {streamingContent && (
            <div className="flex justify-start mb-4">
              <div className="max-w-3xl rounded-lg px-4 py-3 bg-white border border-gray-200 text-gray-900">
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{streamingContent}</ReactMarkdown>
                </div>
                <div className="flex items-center gap-1 mt-2">
                  <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse delay-75"></div>
                  <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse delay-150"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Pregunta sobre tus documentos..."
            className="input flex-1"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="btn-primary disabled:opacity-50"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </form>

        <p className="text-xs text-gray-500 mt-2">
          Las respuestas se generan usando Retrieval-Augmented Generation (RAG) con tus documentos.
          Las referencias se muestran debajo de cada respuesta.
        </p>
      </div>
    </div>
  );
};
