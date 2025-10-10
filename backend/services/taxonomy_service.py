"""
Taxonomy Service
Servicio para trabajar con la taxonomía jerárquica de documentos
Sprint 1: Taxonomía JSON con 3 niveles de profundidad
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum


class TaxonomyService:
    """Servicio para navegación y consulta de la taxonomía jerárquica"""
    
    def __init__(self, taxonomy_file: str = "backend/config/taxonomy.json"):
        """
        Inicializa el servicio cargando la taxonomía desde JSON
        
        Args:
            taxonomy_file: Ruta al archivo JSON de taxonomía
        """
        self.taxonomy_file = Path(taxonomy_file)
        self.taxonomy: Dict = {}
        self.metadata: Dict = {}
        self._load_taxonomy()
    
    def _load_taxonomy(self):
        """Carga la taxonomía desde el archivo JSON"""
        if not self.taxonomy_file.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {self.taxonomy_file}")
        
        with open(self.taxonomy_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.taxonomy = data.get("taxonomy", {})
            self.metadata = data.get("metadata", {})
    
    def get_class(self, class_id: str) -> Optional[Dict]:
        """
        Obtiene información completa de una clase
        
        Args:
            class_id: Identificador de la clase (ej: "PRESTAMO_PERSONAL")
        
        Returns:
            Diccionario con información de la clase o None si no existe
        """
        return self.taxonomy.get(class_id)
    
    def get_hierarchy(self) -> Dict:
        """
        Obtiene la jerarquía completa como árbol
        
        Returns:
            Árbol jerárquico con todos los nodos
        """
        def build_tree(node_id: str) -> Dict:
            node = self.taxonomy.get(node_id)
            if not node:
                return {}
            
            tree = {
                "id": node_id,
                "label": node.get("label"),
                "level": node.get("level"),
                "description": node.get("description"),
                "children": []
            }
            
            # Recursivamente agregar hijos
            for child_id in node.get("children", []):
                tree["children"].append(build_tree(child_id))
            
            return tree
        
        return build_tree("DOCUMENTO")
    
    def get_children(self, class_id: str) -> List[Dict]:
        """
        Obtiene las clases hijas de una clase
        
        Args:
            class_id: Identificador de la clase padre
        
        Returns:
            Lista de clases hijas
        """
        parent = self.get_class(class_id)
        if not parent:
            return []
        
        children = []
        for child_id in parent.get("children", []):
            child = self.get_class(child_id)
            if child:
                children.append({
                    "id": child_id,
                    "label": child.get("label"),
                    "level": child.get("level"),
                    "description": child.get("description")
                })
        
        return children
    
    def get_parent(self, class_id: str) -> Optional[Dict]:
        """
        Obtiene la clase padre de una clase
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            Información de la clase padre o None
        """
        node = self.get_class(class_id)
        if not node or "parent" not in node:
            return None
        
        parent_id = node.get("parent")
        parent = self.get_class(parent_id)
        
        if parent:
            return {
                "id": parent_id,
                "label": parent.get("label"),
                "level": parent.get("level"),
                "description": parent.get("description")
            }
        
        return None
    
    def get_ancestors(self, class_id: str) -> List[Dict]:
        """
        Obtiene todos los ancestros (padres, abuelos, etc.) de una clase
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            Lista de ancestros desde el más cercano al más lejano
        """
        ancestors = []
        current_id = class_id
        
        while True:
            parent = self.get_parent(current_id)
            if not parent:
                break
            ancestors.append(parent)
            current_id = parent["id"]
        
        return ancestors
    
    def get_path(self, class_id: str) -> str:
        """
        Obtiene el path completo de una clase (ej: "Documento > Contractual > Financiación > Préstamo Personal")
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            String con el path completo
        """
        node = self.get_class(class_id)
        if not node:
            return ""
        
        ancestors = self.get_ancestors(class_id)
        ancestors.reverse()
        
        path_parts = [a["label"] for a in ancestors]
        path_parts.append(node.get("label"))
        
        return " > ".join(path_parts)
    
    def get_required_fields(self, class_id: str) -> List[Dict]:
        """
        Obtiene los campos obligatorios de una clase
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            Lista de campos obligatorios con sus propiedades
        """
        node = self.get_class(class_id)
        if not node:
            return []
        
        required = node.get("required_fields", [])
        return [{"name": field, "required": True} for field in required]
    
    def get_optional_fields(self, class_id: str) -> List[Dict]:
        """
        Obtiene los campos opcionales de una clase
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            Lista de campos opcionales
        """
        node = self.get_class(class_id)
        if not node:
            return []
        
        optional = node.get("optional_fields", [])
        return [{"name": field, "required": False} for field in optional]
    
    def get_all_fields(self, class_id: str) -> Dict[str, List[Dict]]:
        """
        Obtiene todos los campos (obligatorios + opcionales) de una clase
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            Diccionario con campos required y optional
        """
        return {
            "required": self.get_required_fields(class_id),
            "optional": self.get_optional_fields(class_id)
        }
    
    def validate_metadata(self, class_id: str, metadata: Dict) -> Tuple[bool, List[str]]:
        """
        Valida que los metadatos cumplan con los requisitos de la clase
        
        Args:
            class_id: Identificador de la clase
            metadata: Diccionario con metadatos del documento
        
        Returns:
            Tupla (es_valido, lista_errores)
        """
        node = self.get_class(class_id)
        if not node:
            return False, [f"Clase no encontrada: {class_id}"]
        
        errors = []
        required_fields = node.get("required_fields", [])
        
        # Verificar campos obligatorios
        for field in required_fields:
            if field not in metadata or metadata[field] is None:
                errors.append(f"Campo obligatorio faltante: {field}")
        
        # Verificar reglas de validación si existen
        validation_rules = node.get("validation_rules", {})
        
        if validation_rules and "importe_financiado" in metadata:
            importe = metadata.get("importe_financiado")
            if importe:
                if "importe_minimo" in validation_rules and importe < validation_rules["importe_minimo"]:
                    errors.append(
                        f"Importe {importe} menor que mínimo permitido {validation_rules['importe_minimo']}"
                    )
                if "importe_maximo" in validation_rules and importe > validation_rules["importe_maximo"]:
                    errors.append(
                        f"Importe {importe} mayor que máximo permitido {validation_rules['importe_maximo']}"
                    )
        
        if validation_rules and "plazo_meses" in metadata:
            plazo = metadata.get("plazo_meses")
            if plazo:
                if "plazo_minimo_meses" in validation_rules and plazo < validation_rules["plazo_minimo_meses"]:
                    errors.append(
                        f"Plazo {plazo} menor que mínimo permitido {validation_rules['plazo_minimo_meses']}"
                    )
                if "plazo_maximo_meses" in validation_rules and plazo > validation_rules["plazo_maximo_meses"]:
                    errors.append(
                        f"Plazo {plazo} mayor que máximo permitido {validation_rules['plazo_maximo_meses']}"
                    )
        
        return len(errors) == 0, errors
    
    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """
        Busca clases que contengan una palabra clave
        
        Args:
            keyword: Palabra clave a buscar (case-insensitive)
        
        Returns:
            Lista de clases que coinciden
        """
        keyword_lower = keyword.lower()
        results = []
        
        for class_id, node in self.taxonomy.items():
            keywords = node.get("keywords", [])
            label = node.get("label", "").lower()
            description = node.get("description", "").lower()
            
            # Buscar en keywords, label y description
            if (keyword_lower in label or 
                keyword_lower in description or
                any(keyword_lower in kw.lower() for kw in keywords)):
                
                results.append({
                    "id": class_id,
                    "label": node.get("label"),
                    "level": node.get("level"),
                    "description": node.get("description"),
                    "path": self.get_path(class_id)
                })
        
        return results
    
    def get_risk_level(self, class_id: str) -> str:
        """
        Obtiene el nivel de riesgo de una clase
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            Nivel de riesgo: "BAJO", "MEDIO", "ALTO" o "DESCONOCIDO"
        """
        node = self.get_class(class_id)
        if not node:
            return "DESCONOCIDO"
        
        return node.get("risk_level", "MEDIO")
    
    def get_retention_years(self, class_id: str) -> int:
        """
        Obtiene el periodo de retención en años
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            Años de retención requeridos
        """
        node = self.get_class(class_id)
        if not node:
            return 5  # Default
        
        return node.get("retention_years", 5)
    
    def is_sensitive(self, class_id: str) -> bool:
        """
        Verifica si una clase contiene datos sensibles
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            True si contiene datos sensibles
        """
        node = self.get_class(class_id)
        if not node:
            return False
        
        return node.get("is_sensitive", False)
    
    def get_compliance_regulations(self, class_id: str) -> List[str]:
        """
        Obtiene las regulaciones de compliance aplicables
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            Lista de regulaciones (ej: ["GDPR", "MiFID II"])
        """
        node = self.get_class(class_id)
        if not node:
            return []
        
        return node.get("compliance_regulations", [])
    
    def get_related_documents(self, class_id: str) -> List[str]:
        """
        Obtiene documentos relacionados típicamente asociados
        
        Args:
            class_id: Identificador de la clase
        
        Returns:
            Lista de IDs de clases relacionadas
        """
        node = self.get_class(class_id)
        if not node:
            return []
        
        return node.get("related_documents", [])
    
    def get_leaf_classes(self) -> List[Dict]:
        """
        Obtiene todas las clases hoja (sin hijos) - las más específicas
        
        Returns:
            Lista de clases hoja
        """
        leaves = []
        
        for class_id, node in self.taxonomy.items():
            if not node.get("children"):
                leaves.append({
                    "id": class_id,
                    "label": node.get("label"),
                    "level": node.get("level"),
                    "path": self.get_path(class_id)
                })
        
        return leaves
    
    def classify_by_keywords(self, text: str, top_n: int = 3) -> List[Dict]:
        """
        Clasifica un texto basándose en coincidencias de keywords
        Simple scoring basado en número de keywords encontradas
        
        Args:
            text: Texto a clasificar
            top_n: Número de resultados a devolver
        
        Returns:
            Lista de clasificaciones ordenadas por score
        """
        text_lower = text.lower()
        scores = []
        
        # Solo considerar clases hoja (más específicas)
        leaf_classes = self.get_leaf_classes()
        
        for leaf in leaf_classes:
            class_id = leaf["id"]
            node = self.get_class(class_id)
            keywords = node.get("keywords", [])
            
            # Contar keywords encontradas
            matches = sum(1 for kw in keywords if kw.lower() in text_lower)
            
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0) if keywords else 0
                
                scores.append({
                    "class_id": class_id,
                    "label": node.get("label"),
                    "path": self.get_path(class_id),
                    "confidence": round(confidence, 2),
                    "matches": matches,
                    "method": "keyword_matching"
                })
        
        # Ordenar por matches y devolver top N
        scores.sort(key=lambda x: (x["matches"], x["confidence"]), reverse=True)
        return scores[:top_n]
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas de la taxonomía
        
        Returns:
            Diccionario con estadísticas
        """
        total_classes = len(self.taxonomy)
        levels = {}
        risk_counts = {"BAJO": 0, "MEDIO": 0, "ALTO": 0}
        sensitive_count = 0
        
        for node in self.taxonomy.values():
            level = node.get("level", 0)
            levels[level] = levels.get(level, 0) + 1
            
            risk = node.get("risk_level")
            if risk in risk_counts:
                risk_counts[risk] += 1
            
            if node.get("is_sensitive"):
                sensitive_count += 1
        
        return {
            "total_classes": total_classes,
            "classes_by_level": levels,
            "classes_by_risk": risk_counts,
            "sensitive_classes": sensitive_count,
            "max_depth": max(levels.keys()) if levels else 0,
            "leaf_classes": len(self.get_leaf_classes())
        }


# Singleton instance
taxonomy_service = TaxonomyService()


# Export para uso en otros módulos
__all__ = ["TaxonomyService", "taxonomy_service"]
