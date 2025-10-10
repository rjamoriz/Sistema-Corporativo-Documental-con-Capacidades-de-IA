"""
Servicio de validación contra listas de sanciones internacionales.

Integra:
- OFAC Sanctions List (US Treasury)
- EU Sanctions Database
- World Bank Debarred Firms
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from fuzzywuzzy import fuzz
import aiohttp

from backend.models.validation.sanctions_models import (
    SanctionsList,
    ValidationHistory,
    ValidationResult,
)
from config.validation_apis import SANCTIONS_CONFIG


logger = logging.getLogger(__name__)


class SanctionsService:
    """Servicio para validación de entidades contra listas de sanciones."""

    def __init__(self, db_session, config: Optional[Dict] = None):
        """
        Inicializa el servicio de validación de sanciones.

        Args:
            db_session: Sesión de base de datos SQLAlchemy
            config: Configuración opcional (usa SANCTIONS_CONFIG por defecto)
        """
        self.db = db_session
        self.config = config or SANCTIONS_CONFIG
        self.fuzzy_threshold = self.config.get("fuzzy_threshold", 85)
        self._session = None

    async def __aenter__(self):
        """Context manager entry."""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._session:
            await self._session.close()

    async def check_entity(
        self,
        entity_name: str,
        entity_type: str,
        country: Optional[str] = None,
        additional_info: Optional[Dict] = None,
    ) -> Dict:
        """
        Valida una entidad contra todas las listas de sanciones.

        Args:
            entity_name: Nombre de la entidad a validar
            entity_type: Tipo de entidad ('PERSON', 'COMPANY', 'VESSEL', etc.)
            country: País de la entidad (opcional)
            additional_info: Información adicional (DNI, CIF, etc.)

        Returns:
            Dict con resultado de la validación:
            {
                "is_sanctioned": bool,
                "confidence": float,
                "matches": List[Dict],
                "sources_checked": List[str],
                "checked_at": datetime
            }
        """
        logger.info(f"Validando entidad: {entity_name} (tipo: {entity_type})")

        # Ejecutar validaciones en paralelo
        results = await asyncio.gather(
            self._check_ofac(entity_name, entity_type, country, additional_info),
            self._check_eu_sanctions(entity_name, entity_type, country),
            self._check_world_bank(entity_name, entity_type),
            return_exceptions=True,
        )

        # Consolidar resultados
        all_matches = []
        sources_checked = []
        max_confidence = 0.0

        for idx, result in enumerate(results):
            source_name = ["OFAC", "EU_SANCTIONS", "WORLD_BANK"][idx]
            sources_checked.append(source_name)

            if isinstance(result, Exception):
                logger.error(f"Error validando contra {source_name}: {result}")
                continue

            if result and result.get("matches"):
                all_matches.extend(result["matches"])
                max_confidence = max(max_confidence, result.get("confidence", 0))

        # Guardar en historial
        validation_result = ValidationResult(
            entity_name=entity_name,
            entity_type=entity_type,
            is_sanctioned=len(all_matches) > 0,
            confidence=max_confidence,
            matches_count=len(all_matches),
            sources_checked=sources_checked,
            checked_at=datetime.utcnow(),
        )
        self.db.add(validation_result)
        await self.db.commit()

        return {
            "is_sanctioned": len(all_matches) > 0,
            "confidence": max_confidence,
            "matches": all_matches,
            "sources_checked": sources_checked,
            "checked_at": datetime.utcnow().isoformat(),
            "validation_id": validation_result.id,
        }

    async def _check_ofac(
        self,
        entity_name: str,
        entity_type: str,
        country: Optional[str],
        additional_info: Optional[Dict],
    ) -> Dict:
        """
        Valida contra OFAC Sanctions List.

        API Doc: https://sanctionssearch.ofac.treas.gov/
        """
        try:
            url = self.config["ofac"]["api_url"]
            api_key = self.config["ofac"]["api_key"]

            params = {
                "name": entity_name,
                "type": entity_type,
                "api_key": api_key,
            }
            if country:
                params["country"] = country

            async with self._session.get(url, params=params, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"OFAC API error: {response.status}")
                    return {"matches": [], "confidence": 0}

                data = await response.json()
                matches = []

                for entry in data.get("results", []):
                    # Calcular similitud con fuzzy matching
                    similarity = fuzz.token_set_ratio(
                        entity_name.lower(), entry["name"].lower()
                    )

                    if similarity >= self.fuzzy_threshold:
                        matches.append({
                            "source": "OFAC",
                            "name": entry["name"],
                            "type": entry.get("type"),
                            "program": entry.get("programs", []),
                            "address": entry.get("addresses", []),
                            "similarity": similarity,
                            "list_id": entry.get("id"),
                            "remarks": entry.get("remarks"),
                        })

                return {
                    "matches": matches,
                    "confidence": max([m["similarity"] for m in matches], default=0) / 100.0,
                }

        except Exception as e:
            logger.error(f"Error en validación OFAC: {e}")
            raise

    async def _check_eu_sanctions(
        self, entity_name: str, entity_type: str, country: Optional[str]
    ) -> Dict:
        """
        Valida contra EU Sanctions Database.

        API Doc: https://webgate.ec.europa.eu/fsd/fsf
        """
        try:
            url = self.config["eu_sanctions"]["api_url"]
            api_key = self.config["eu_sanctions"]["api_key"]

            payload = {
                "name": entity_name,
                "type": entity_type,
            }
            if country:
                payload["country"] = country

            headers = {"Authorization": f"Bearer {api_key}"}

            async with self._session.post(
                url, json=payload, headers=headers, timeout=10
            ) as response:
                if response.status != 200:
                    logger.error(f"EU Sanctions API error: {response.status}")
                    return {"matches": [], "confidence": 0}

                data = await response.json()
                matches = []

                for entry in data.get("results", []):
                    similarity = fuzz.token_set_ratio(
                        entity_name.lower(), entry["fullName"].lower()
                    )

                    if similarity >= self.fuzzy_threshold:
                        matches.append({
                            "source": "EU_SANCTIONS",
                            "name": entry["fullName"],
                            "type": entry.get("subjectType"),
                            "regulation": entry.get("regulation"),
                            "publication_date": entry.get("publicationDate"),
                            "similarity": similarity,
                            "entity_id": entry.get("euReferenceNumber"),
                        })

                return {
                    "matches": matches,
                    "confidence": max([m["similarity"] for m in matches], default=0) / 100.0,
                }

        except Exception as e:
            logger.error(f"Error en validación EU Sanctions: {e}")
            raise

    async def _check_world_bank(self, entity_name: str, entity_type: str) -> Dict:
        """
        Valida contra World Bank Debarred Firms List.

        API Doc: https://apidocs.worldbank.org/debarred-firms
        """
        try:
            url = self.config["world_bank"]["api_url"]

            params = {
                "format": "json",
                "firmname": entity_name,
            }

            async with self._session.get(url, params=params, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"World Bank API error: {response.status}")
                    return {"matches": [], "confidence": 0}

                data = await response.json()
                matches = []

                for entry in data.get("response", {}).get("docs", []):
                    similarity = fuzz.token_set_ratio(
                        entity_name.lower(), entry["firm_name"].lower()
                    )

                    if similarity >= self.fuzzy_threshold:
                        matches.append({
                            "source": "WORLD_BANK",
                            "name": entry["firm_name"],
                            "country": entry.get("country"),
                            "ineligibility_period": entry.get("ineligibility_period"),
                            "grounds": entry.get("grounds"),
                            "similarity": similarity,
                        })

                return {
                    "matches": matches,
                    "confidence": max([m["similarity"] for m in matches], default=0) / 100.0,
                }

        except Exception as e:
            logger.error(f"Error en validación World Bank: {e}")
            raise

    async def validate_document_entities(self, document_id: int) -> Dict:
        """
        Valida todas las entidades extraídas de un documento.

        Args:
            document_id: ID del documento

        Returns:
            Dict con resultados de validación de todas las entidades
        """
        # Obtener entidades del documento desde la base de datos
        # (asumiendo que ya fueron extraídas por NER)
        from backend.models.document import Document
        from backend.models.entity import Entity

        document = await self.db.get(Document, document_id)
        if not document:
            raise ValueError(f"Documento {document_id} no encontrado")

        entities = await self.db.query(Entity).filter(
            Entity.document_id == document_id
        ).all()

        logger.info(f"Validando {len(entities)} entidades del documento {document_id}")

        # Validar cada entidad
        validation_results = []
        for entity in entities:
            result = await self.check_entity(
                entity_name=entity.text,
                entity_type=entity.entity_type,
                country=entity.metadata.get("country") if entity.metadata else None,
            )
            validation_results.append({
                "entity_id": entity.id,
                "entity_name": entity.text,
                "entity_type": entity.entity_type,
                "validation": result,
            })

        # Guardar en historial
        history_entry = ValidationHistory(
            document_id=document_id,
            entities_validated=len(entities),
            entities_flagged=sum(1 for r in validation_results if r["validation"]["is_sanctioned"]),
            validated_at=datetime.utcnow(),
        )
        self.db.add(history_entry)
        await self.db.commit()

        return {
            "document_id": document_id,
            "total_entities": len(entities),
            "flagged_entities": sum(
                1 for r in validation_results if r["validation"]["is_sanctioned"]
            ),
            "validation_results": validation_results,
            "history_id": history_entry.id,
        }

    async def get_validation_history(
        self, document_id: Optional[int] = None, limit: int = 100
    ) -> List[Dict]:
        """
        Obtiene el historial de validaciones.

        Args:
            document_id: Filtrar por documento (opcional)
            limit: Número máximo de resultados

        Returns:
            Lista de validaciones históricas
        """
        query = self.db.query(ValidationHistory)
        if document_id:
            query = query.filter(ValidationHistory.document_id == document_id)

        history = await query.order_by(
            ValidationHistory.validated_at.desc()
        ).limit(limit).all()

        return [
            {
                "id": entry.id,
                "document_id": entry.document_id,
                "entities_validated": entry.entities_validated,
                "entities_flagged": entry.entities_flagged,
                "validated_at": entry.validated_at.isoformat(),
            }
            for entry in history
        ]
