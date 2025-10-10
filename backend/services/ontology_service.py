"""
Ontology Service
Servicio para trabajar con la ontología OWL/SKOS usando RDFLib
Sprint 2 + 3: Ontología completa con SPARQL y razonamiento
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import SKOS, XSD


logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Niveles de riesgo"""
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"


class OntologyService:
    """Servicio para trabajar con la ontología formal OWL"""
    
    def __init__(self, ontology_file: str = "ontology/tefinancia.ttl"):
        """
        Inicializa el servicio cargando la ontología OWL
        
        Args:
            ontology_file: Ruta al archivo Turtle de la ontología
        """
        self.ontology_file = Path(ontology_file)
        self.graph = Graph()
        
        # Namespaces
        self.TF = Namespace("http://tefinancia.es/ontology#")
        self.graph.bind("tf", self.TF)
        self.graph.bind("skos", SKOS)
        
        # Cargar ontología
        self._load_ontology()
        
        logger.info(f"Ontología cargada: {len(self.graph)} triples")
    
    def _load_ontology(self):
        """Carga la ontología desde el archivo Turtle"""
        if not self.ontology_file.exists():
            logger.warning(f"Ontology file not found: {self.ontology_file}")
            # Crear grafo vacío si no existe el archivo
            return
        
        try:
            self.graph.parse(self.ontology_file, format="turtle")
            logger.info(f"✅ Ontología cargada: {len(self.graph)} triples")
        except Exception as e:
            logger.error(f"Error loading ontology: {e}")
            raise
    
    def get_class_uri(self, class_name: str) -> URIRef:
        """
        Convierte un nombre de clase a URI
        
        Args:
            class_name: Nombre de la clase (ej: "PrestamoHipotecario")
        
        Returns:
            URIRef de la clase
        """
        return self.TF[class_name]
    
    def get_class_info(self, class_uri: URIRef) -> Dict:
        """
        Obtiene información completa de una clase
        
        Args:
            class_uri: URI de la clase
        
        Returns:
            Diccionario con información de la clase
        """
        info = {
            "uri": str(class_uri),
            "label": None,
            "comment": None,
            "parent_classes": [],
            "properties": {},
            "restrictions": []
        }
        
        # Label
        for label in self.graph.objects(class_uri, RDFS.label):
            if label.language == "es" or label.language is None:
                info["label"] = str(label)
                break
        
        # Comment
        for comment in self.graph.objects(class_uri, RDFS.comment):
            if comment.language == "es" or comment.language is None:
                info["comment"] = str(comment)
                break
        
        # Parent classes
        for parent in self.graph.objects(class_uri, RDFS.subClassOf):
            if isinstance(parent, URIRef):
                parent_label = self._get_label(parent)
                info["parent_classes"].append({
                    "uri": str(parent),
                    "label": parent_label
                })
        
        # Custom properties (datatype properties)
        for pred, obj in self.graph.predicate_objects(class_uri):
            if pred.startswith(self.TF):
                prop_name = str(pred).split("#")[-1]
                info["properties"][prop_name] = self._convert_literal(obj)
        
        return info
    
    def _get_label(self, uri: URIRef) -> Optional[str]:
        """Obtiene el label de una URI"""
        for label in self.graph.objects(uri, RDFS.label):
            if label.language == "es" or label.language is None:
                return str(label)
        return str(uri).split("#")[-1]
    
    def _convert_literal(self, literal: Literal) -> Any:
        """Convierte un Literal RDF a tipo Python"""
        if isinstance(literal, Literal):
            if literal.datatype == XSD.integer:
                return int(literal)
            elif literal.datatype == XSD.decimal or literal.datatype == XSD.float:
                return float(literal)
            elif literal.datatype == XSD.boolean:
                return bool(literal)
            else:
                return str(literal)
        return str(literal)
    
    def get_subclasses(self, class_uri: URIRef, direct_only: bool = True) -> List[Dict]:
        """
        Obtiene las subclases de una clase
        
        Args:
            class_uri: URI de la clase padre
            direct_only: Si True, solo subclases directas. Si False, todas las descendientes
        
        Returns:
            Lista de subclases
        """
        subclasses = []
        
        if direct_only:
            # Subclases directas
            for subclass in self.graph.subjects(RDFS.subClassOf, class_uri):
                if isinstance(subclass, URIRef) and subclass.startswith(self.TF):
                    subclasses.append({
                        "uri": str(subclass),
                        "label": self._get_label(subclass),
                        "name": str(subclass).split("#")[-1]
                    })
        else:
            # Todas las subclases (transitivo)
            query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX tf: <http://tefinancia.es/ontology#>
            
            SELECT ?subclass ?label WHERE {{
                ?subclass rdfs:subClassOf* <{class_uri}> .
                OPTIONAL {{ ?subclass rdfs:label ?label FILTER(lang(?label) = "es") }}
                FILTER(?subclass != <{class_uri}>)
            }}
            """
            
            results = self.graph.query(query)
            for row in results:
                subclasses.append({
                    "uri": str(row.subclass),
                    "label": str(row.label) if row.label else str(row.subclass).split("#")[-1],
                    "name": str(row.subclass).split("#")[-1]
                })
        
        return subclasses
    
    def classify_document(self, content: str, metadata: Dict) -> Dict:
        """
        Clasifica un documento usando la ontología
        
        Args:
            content: Contenido del documento
            metadata: Metadatos del documento
        
        Returns:
            Clasificación con URI de la clase, label, confianza
        """
        content_lower = content.lower()
        best_match = None
        best_score = 0.0
        
        # Obtener todas las clases hoja (más específicas)
        leaf_classes = self._get_leaf_classes()
        
        for class_uri in leaf_classes:
            # Obtener keywords de la clase
            keywords = self._get_keywords(class_uri)
            
            if not keywords:
                continue
            
            # Contar coincidencias
            matches = sum(1 for kw in keywords if kw.lower() in content_lower)
            
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                
                if confidence > best_score:
                    best_score = confidence
                    best_match = {
                        "uri": str(class_uri),
                        "name": str(class_uri).split("#")[-1],
                        "label": self._get_label(class_uri),
                        "confidence": round(confidence, 2),
                        "matches": matches,
                        "method": "ontology_keyword_matching"
                    }
        
        if best_match:
            # Enriquecer con propiedades de la clase
            class_info = self.get_class_info(URIRef(best_match["uri"]))
            best_match["properties"] = class_info.get("properties", {})
            return best_match
        
        # Fallback: clase genérica Documento
        return {
            "uri": str(self.TF.Documento),
            "name": "Documento",
            "label": "Documento",
            "confidence": 0.1,
            "matches": 0,
            "method": "ontology_fallback"
        }
    
    def _get_leaf_classes(self) -> List[URIRef]:
        """Obtiene todas las clases hoja (sin subclases)"""
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX tf: <http://tefinancia.es/ontology#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT DISTINCT ?class WHERE {
            ?class a owl:Class .
            ?class rdfs:subClassOf* tf:Documento .
            FILTER NOT EXISTS {
                ?subclass rdfs:subClassOf ?class .
                FILTER(?subclass != ?class)
            }
            FILTER(STRSTARTS(STR(?class), STR(tf:)))
        }
        """
        
        results = self.graph.query(query)
        return [row.class_ for row in results]
    
    def _get_keywords(self, class_uri: URIRef) -> List[str]:
        """Obtiene las keywords de una clase"""
        keywords = []
        
        # Buscar anotación tf:keyword
        for keyword in self.graph.objects(class_uri, self.TF.keyword):
            keywords.append(str(keyword))
        
        return keywords
    
    def get_required_fields(self, class_uri: URIRef) -> List[Dict]:
        """
        Obtiene los campos obligatorios de una clase según restricciones OWL
        
        Args:
            class_uri: URI de la clase
        
        Returns:
            Lista de campos obligatorios
        """
        required_fields = []
        
        # Buscar restricciones de cardinalidad mínima
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?property ?minCard WHERE {{
            <{class_uri}> rdfs:subClassOf ?restriction .
            ?restriction a owl:Restriction .
            ?restriction owl:onProperty ?property .
            ?restriction owl:minCardinality ?minCard .
            FILTER(?minCard >= 1)
        }}
        """
        
        results = self.graph.query(query)
        for row in results:
            prop_name = str(row.property).split("#")[-1]
            required_fields.append({
                "name": prop_name,
                "uri": str(row.property),
                "required": True,
                "min_cardinality": int(row.minCard)
            })
        
        # También buscar propiedades con cardinalidad exacta
        query_exact = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?property ?card WHERE {{
            <{class_uri}> rdfs:subClassOf ?restriction .
            ?restriction a owl:Restriction .
            ?restriction owl:onProperty ?property .
            ?restriction owl:cardinality ?card .
        }}
        """
        
        results = self.graph.query(query_exact)
        for row in results:
            prop_name = str(row.property).split("#")[-1]
            required_fields.append({
                "name": prop_name,
                "uri": str(row.property),
                "required": True,
                "cardinality": int(row.card)
            })
        
        return required_fields
    
    def validate_metadata(self, class_uri: URIRef, metadata: Dict) -> Tuple[bool, List[str]]:
        """
        Valida metadatos contra la ontología
        
        Args:
            class_uri: URI de la clase
            metadata: Metadatos a validar
        
        Returns:
            Tupla (es_válido, lista_errores)
        """
        errors = []
        
        # 1. Validar campos obligatorios
        required_fields = self.get_required_fields(class_uri)
        for field in required_fields:
            if field["name"] not in metadata:
                errors.append(f"Campo obligatorio faltante: {field['name']}")
        
        # 2. Validar rangos de valores (propiedades de la clase)
        class_info = self.get_class_info(class_uri)
        props = class_info.get("properties", {})
        
        # Validar importeMinimo/importeMaximo
        if "importeMinimo" in props and "importeFinanciado" in metadata:
            if metadata["importeFinanciado"] < props["importeMinimo"]:
                errors.append(
                    f"importeFinanciado ({metadata['importeFinanciado']}) menor que "
                    f"mínimo permitido ({props['importeMinimo']})"
                )
        
        if "importeMaximo" in props and "importeFinanciado" in metadata:
            if metadata["importeFinanciado"] > props["importeMaximo"]:
                errors.append(
                    f"importeFinanciado ({metadata['importeFinanciado']}) mayor que "
                    f"máximo permitido ({props['importeMaximo']})"
                )
        
        # Validar plazoMinimoMeses/plazoMaximoMeses
        if "plazoMinimoMeses" in props and "plazoMeses" in metadata:
            if metadata["plazoMeses"] < props["plazoMinimoMeses"]:
                errors.append(
                    f"plazoMeses ({metadata['plazoMeses']}) menor que "
                    f"mínimo permitido ({props['plazoMinimoMeses']})"
                )
        
        if "plazoMaximoMeses" in props and "plazoMeses" in metadata:
            if metadata["plazoMeses"] > props["plazoMaximoMeses"]:
                errors.append(
                    f"plazoMeses ({metadata['plazoMeses']}) mayor que "
                    f"máximo permitido ({props['plazoMaximoMeses']})"
                )
        
        # Validar taeMaximo
        if "taeMaximo" in props and "tae" in metadata:
            if metadata["tae"] > props["taeMaximo"]:
                errors.append(
                    f"tae ({metadata['tae']}) mayor que "
                    f"máximo permitido ({props['taeMaximo']})"
                )
        
        return len(errors) == 0, errors
    
    def infer_risk_level(self, class_uri: URIRef, metadata: Dict) -> str:
        """
        Infiere el nivel de riesgo usando reglas de la ontología
        
        Args:
            class_uri: URI de la clase
            metadata: Metadatos del documento
        
        Returns:
            Nivel de riesgo: BAJO, MEDIO, ALTO
        """
        # 1. Obtener nivel base de la clase
        class_info = self.get_class_info(class_uri)
        base_risk = class_info.get("properties", {}).get("nivelRiesgoBase", "MEDIO")
        
        # 2. Aplicar reglas de inferencia
        
        # Regla: Préstamo hipotecario con LTV > 80% es riesgo ALTO
        if "PrestamoHipotecario" in str(class_uri) and "ltv" in metadata:
            if metadata["ltv"] > 80.0:
                return RiskLevel.ALTO.value
        
        # Regla: Línea de crédito siempre es riesgo ALTO
        if "LineaCredito" in str(class_uri):
            return RiskLevel.ALTO.value
        
        # Regla: Documentos sensibles son riesgo ALTO
        if class_info.get("properties", {}).get("esSensible"):
            return RiskLevel.ALTO.value
        
        # Regla: Préstamos con TAE > 10% son riesgo ALTO
        if "tae" in metadata and metadata["tae"] > 10.0:
            return RiskLevel.ALTO.value
        
        # Regla: Préstamos con plazo > 240 meses (20 años) son riesgo MEDIO mínimo
        if "plazoMeses" in metadata and metadata["plazoMeses"] > 240:
            if base_risk == RiskLevel.BAJO.value:
                return RiskLevel.MEDIO.value
        
        return base_risk
    
    def query_sparql(self, sparql_query: str) -> List[Dict]:
        """
        Ejecuta una consulta SPARQL sobre la ontología
        
        Args:
            sparql_query: Consulta SPARQL
        
        Returns:
            Resultados como lista de diccionarios
        """
        try:
            results = self.graph.query(sparql_query)
            
            output = []
            for row in results:
                row_dict = {}
                for var in results.vars:
                    value = getattr(row, str(var))
                    if value:
                        row_dict[str(var)] = str(value)
                output.append(row_dict)
            
            return output
        except Exception as e:
            logger.error(f"SPARQL query error: {e}")
            raise
    
    def get_related_documents(self, class_uri: URIRef) -> List[Dict]:
        """
        Obtiene documentos relacionados según propiedades de objeto
        
        Args:
            class_uri: URI de la clase
        
        Returns:
            Lista de documentos relacionados
        """
        query = f"""
        PREFIX tf: <http://tefinancia.es/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?relatedClass ?relation ?label WHERE {{
            <{class_uri}> rdfs:subClassOf ?restriction .
            ?restriction owl:onProperty ?relation .
            ?restriction owl:someValuesFrom ?relatedClass .
            OPTIONAL {{ ?relatedClass rdfs:label ?label FILTER(lang(?label) = "es") }}
            FILTER(STRSTARTS(STR(?relatedClass), STR(tf:)))
        }}
        """
        
        try:
            results = self.graph.query(query)
            related = []
            
            for row in results:
                related.append({
                    "uri": str(row.relatedClass),
                    "name": str(row.relatedClass).split("#")[-1],
                    "label": str(row.label) if row.label else str(row.relatedClass).split("#")[-1],
                    "relation": str(row.relation).split("#")[-1]
                })
            
            return related
        except Exception as e:
            logger.error(f"Error getting related documents: {e}")
            return []
    
    def get_compliance_regulations(self, class_uri: URIRef) -> List[str]:
        """
        Obtiene las regulaciones aplicables a una clase
        
        Args:
            class_uri: URI de la clase
        
        Returns:
            Lista de regulaciones
        """
        regulations = []
        
        # Buscar anotación tf:regulacionAplicable
        for reg in self.graph.objects(class_uri, self.TF.regulacionAplicable):
            regulations.append(str(reg))
        
        return regulations
    
    def get_retention_years(self, class_uri: URIRef) -> int:
        """
        Obtiene los años de retención según la ontología
        
        Args:
            class_uri: URI de la clase
        
        Returns:
            Años de retención
        """
        class_info = self.get_class_info(class_uri)
        return class_info.get("properties", {}).get("retencionAnios", 5)
    
    def get_hierarchy(self) -> Dict:
        """
        Obtiene la jerarquía completa de la ontología como árbol
        
        Returns:
            Árbol jerárquico
        """
        root_uri = self.TF.Documento
        
        def build_tree(node_uri: URIRef) -> Dict:
            node = {
                "uri": str(node_uri),
                "name": str(node_uri).split("#")[-1],
                "label": self._get_label(node_uri),
                "children": []
            }
            
            # Obtener subclases directas
            subclasses = self.get_subclasses(node_uri, direct_only=True)
            
            for subclass in subclasses:
                child_uri = URIRef(subclass["uri"])
                node["children"].append(build_tree(child_uri))
            
            return node
        
        return build_tree(root_uri)
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas de la ontología
        
        Returns:
            Estadísticas (número de clases, propiedades, etc.)
        """
        # Contar clases
        query_classes = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX tf: <http://tefinancia.es/ontology#>
        
        SELECT (COUNT(DISTINCT ?class) AS ?count) WHERE {
            ?class a owl:Class .
            FILTER(STRSTARTS(STR(?class), STR(tf:)))
        }
        """
        
        # Contar object properties
        query_obj_props = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX tf: <http://tefinancia.es/ontology#>
        
        SELECT (COUNT(DISTINCT ?prop) AS ?count) WHERE {
            ?prop a owl:ObjectProperty .
            FILTER(STRSTARTS(STR(?prop), STR(tf:)))
        }
        """
        
        # Contar datatype properties
        query_data_props = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX tf: <http://tefinancia.es/ontology#>
        
        SELECT (COUNT(DISTINCT ?prop) AS ?count) WHERE {
            ?prop a owl:DatatypeProperty .
            FILTER(STRSTARTS(STR(?prop), STR(tf:)))
        }
        """
        
        num_classes = list(self.graph.query(query_classes))[0][0]
        num_obj_props = list(self.graph.query(query_obj_props))[0][0]
        num_data_props = list(self.graph.query(query_data_props))[0][0]
        
        return {
            "total_triples": len(self.graph),
            "total_classes": int(num_classes),
            "object_properties": int(num_obj_props),
            "datatype_properties": int(num_data_props),
            "leaf_classes": len(self._get_leaf_classes())
        }


# Singleton instance
try:
    ontology_service = OntologyService()
except Exception as e:
    logger.warning(f"Could not initialize OntologyService: {e}")
    ontology_service = None


# Export
__all__ = ["OntologyService", "ontology_service", "RiskLevel"]
