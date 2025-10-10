#!/usr/bin/env python3
"""
MCP Server para Ontología TEFinancia
Model Context Protocol server que expone la ontología OWL a Claude Desktop

Este servidor permite a Claude:
- Consultar la jerarquía de clases
- Ejecutar consultas SPARQL
- Clasificar documentos usando ontología
- Validar metadatos contra restricciones OWL
- Inferir niveles de riesgo

Instalación en Claude Desktop:
1. Copiar este archivo a una ubicación accesible
2. Añadir configuración a claude_desktop_config.json
3. Reiniciar Claude Desktop

Uso desde Claude:
- "¿Qué clases de documentos financieros existen?"
- "Ejecuta una consulta SPARQL para encontrar préstamos hipotecarios"
- "Clasifica este documento usando la ontología"
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

# Añadir el directorio backend al path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from services.ontology_service import ontology_service
from services.taxonomy_service import taxonomy_service

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-tefinancia")

# Crear servidor MCP
server = Server("tefinancia-ontology")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    Lista de herramientas disponibles en el servidor MCP
    """
    return [
        Tool(
            name="get_ontology_classes",
            description=(
                "Obtiene la lista completa de clases de documentos financieros "
                "en la ontología TEFinancia. Retorna nombre, etiqueta, descripción "
                "y jerarquía de herencia de cada clase."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "include_properties": {
                        "type": "boolean",
                        "description": "Si True, incluye propiedades de cada clase",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="get_class_details",
            description=(
                "Obtiene información detallada de una clase específica de la ontología, "
                "incluyendo propiedades, restricciones OWL, clases padre e hijas."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "Nombre de la clase (ej: PrestamoHipotecario, TarjetaCredito)"
                    }
                },
                "required": ["class_name"]
            }
        ),
        Tool(
            name="execute_sparql",
            description=(
                "Ejecuta una consulta SPARQL sobre la ontología TEFinancia. "
                "Permite consultas complejas con filtros, agregaciones y joins. "
                "Retorna resultados en formato tabular."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Consulta SPARQL. Prefijos disponibles: "
                            "rdf, rdfs, owl, xsd, tf (ontología TEFinancia)"
                        )
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Límite de resultados (default: 100)",
                        "default": 100
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="classify_document",
            description=(
                "Clasifica un documento usando la ontología OWL. "
                "Analiza el contenido y metadatos para determinar la clase ontológica "
                "más apropiada, validar restricciones e inferir nivel de riesgo."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Contenido textual del documento"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadatos del documento (opcional)",
                        "default": {}
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="validate_metadata",
            description=(
                "Valida metadatos de un documento contra restricciones OWL "
                "de una clase específica. Verifica cardinalidad, tipos de datos, "
                "rangos numéricos y propiedades obligatorias."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "Nombre de la clase OWL"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadatos a validar"
                    }
                },
                "required": ["class_name", "metadata"]
            }
        ),
        Tool(
            name="infer_risk_level",
            description=(
                "Infiere el nivel de riesgo de un documento basándose en reglas "
                "de negocio y metadatos. Evalúa: LTV, TAE, sensibilidad de datos, "
                "tipo de producto y plazo. Retorna: BAJO, MEDIO o ALTO."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "Nombre de la clase OWL del documento"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadatos del documento"
                    }
                },
                "required": ["class_name", "metadata"]
            }
        ),
        Tool(
            name="get_ontology_hierarchy",
            description=(
                "Obtiene la jerarquía completa de clases de la ontología "
                "en formato de árbol. Útil para entender la estructura taxonómica."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "root_class": {
                        "type": "string",
                        "description": "Clase raíz (default: DocumentoCorporativo)",
                        "default": "DocumentoCorporativo"
                    }
                }
            }
        ),
        Tool(
            name="search_by_keywords",
            description=(
                "Busca clases de ontología por keywords. Usa la taxonomía JSON "
                "para búsqueda rápida jerárquica."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto para buscar keywords"
                    }
                },
                "required": ["text"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Maneja la invocación de herramientas
    """
    try:
        if name == "get_ontology_classes":
            include_properties = arguments.get("include_properties", False)
            classes = ontology_service.get_all_classes()
            
            result = []
            for class_uri, class_info in classes.items():
                class_data = {
                    "uri": str(class_uri),
                    "name": class_info.get("name"),
                    "label": class_info.get("label"),
                    "comment": class_info.get("comment"),
                    "parent_classes": [str(p) for p in class_info.get("parent_classes", [])]
                }
                
                if include_properties:
                    class_data["properties"] = [
                        {
                            "name": p.get("name"),
                            "label": p.get("label"),
                            "type": p.get("type")
                        }
                        for p in class_info.get("properties", [])
                    ]
                
                result.append(class_data)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "get_class_details":
            class_name = arguments["class_name"]
            class_uri = ontology_service.TF[class_name]
            class_info = ontology_service.get_class_info(class_uri)
            
            # Obtener restricciones
            restrictions = ontology_service.get_class_restrictions(class_uri)
            
            result = {
                "name": class_name,
                "label": class_info.get("label"),
                "comment": class_info.get("comment"),
                "parent_classes": [str(p) for p in class_info.get("parent_classes", [])],
                "subclasses": [str(s) for s in class_info.get("subclasses", [])],
                "properties": class_info.get("properties", []),
                "restrictions": restrictions,
                "required_fields": ontology_service.get_required_fields(class_uri)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "execute_sparql":
            query = arguments["query"]
            limit = arguments.get("limit", 100)
            
            # Añadir LIMIT si no existe
            if "LIMIT" not in query.upper():
                query = f"{query}\nLIMIT {limit}"
            
            results = ontology_service.execute_sparql(query)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "columns": results.get("columns", []),
                    "rows": results.get("rows", []),
                    "count": len(results.get("rows", []))
                }, indent=2, ensure_ascii=False)
            )]
        
        elif name == "classify_document":
            content = arguments["content"]
            metadata = arguments.get("metadata", {})
            
            result = ontology_service.classify_document(content, metadata)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "validate_metadata":
            class_name = arguments["class_name"]
            metadata = arguments["metadata"]
            
            class_uri = ontology_service.TF[class_name]
            is_valid, errors = ontology_service.validate_metadata(class_uri, metadata)
            
            result = {
                "is_valid": is_valid,
                "errors": errors,
                "required_fields": ontology_service.get_required_fields(class_uri)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "infer_risk_level":
            class_name = arguments["class_name"]
            metadata = arguments["metadata"]
            
            class_uri = ontology_service.TF[class_name]
            risk_level = ontology_service.infer_risk_level(class_uri, metadata)
            
            result = {
                "risk_level": risk_level,
                "class_name": class_name,
                "metadata": metadata
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "get_ontology_hierarchy":
            root_class = arguments.get("root_class", "DocumentoCorporativo")
            hierarchy = ontology_service.get_hierarchy(root_class)
            
            return [TextContent(
                type="text",
                text=json.dumps(hierarchy, indent=2, ensure_ascii=False)
            )]
        
        elif name == "search_by_keywords":
            text = arguments["text"]
            result = taxonomy_service.classify_by_keywords(text)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Error: Herramienta desconocida '{name}'"
            )]
    
    except Exception as e:
        logger.error(f"Error en herramienta {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error ejecutando {name}: {str(e)}"
        )]

async def main():
    """
    Punto de entrada principal del servidor MCP
    """
    logger.info("Iniciando MCP Server para Ontología TEFinancia")
    
    # Iniciar servidor con stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="tefinancia-ontology",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
