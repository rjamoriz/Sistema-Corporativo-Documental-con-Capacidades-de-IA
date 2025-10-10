"""
Servicio de scoring ESG (Environmental, Social, Governance).

Integra Refinitiv/MSCI para obtener:
- Puntuaciones ESG de empresas
- Ratings ESG
- Desglose por categorías (E, S, G)
- Controversias y riesgos
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import aiohttp

from config.validation_apis import ESG_CONFIG


logger = logging.getLogger(__name__)


class ESGService:
    """Servicio para obtener scoring ESG de empresas."""

    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el servicio ESG.

        Args:
            config: Configuración opcional (usa ESG_CONFIG por defecto)
        """
        self.config = config or ESG_CONFIG
        self._session = None
        self._cache = {}  # Cache simple en memoria

    async def __aenter__(self):
        """Context manager entry."""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._session:
            await self._session.close()

    async def get_esg_score(
        self, company_name: str, isin: Optional[str] = None
    ) -> Dict:
        """
        Obtiene el scoring ESG de una empresa.

        Args:
            company_name: Nombre de la empresa
            isin: Código ISIN (opcional, mejora precisión)

        Returns:
            Dict con scoring ESG:
            {
                "company_name": str,
                "isin": str,
                "overall_score": float,  # 0-100
                "rating": str,  # AAA, AA, A, BBB, BB, B, CCC
                "environmental": Dict,
                "social": Dict,
                "governance": Dict,
                "controversies": List,
                "last_updated": str,
                "source": str
            }
        """
        logger.info(f"Obteniendo ESG score para: {company_name}")

        # Verificar cache
        cache_key = f"esg_{company_name}_{isin}"
        if cache_key in self._cache:
            cached_data, cached_at = self._cache[cache_key]
            if datetime.utcnow() - cached_at < timedelta(days=30):
                logger.info(f"Usando ESG score en cache para {company_name}")
                return cached_data

        # Consultar Refinitiv (preferido)
        if self.config["refinitiv"]["enabled"]:
            result = await self._query_refinitiv(company_name, isin)
            if result:
                self._cache[cache_key] = (result, datetime.utcnow())
                return result

        # Alternativa: MSCI
        if self.config["msci"]["enabled"]:
            result = await self._query_msci(company_name, isin)
            if result:
                self._cache[cache_key] = (result, datetime.utcnow())
                return result

        raise ValueError(f"No se pudo obtener ESG score para {company_name}")

    async def _query_refinitiv(
        self, company_name: str, isin: Optional[str]
    ) -> Optional[Dict]:
        """
        Consulta Refinitiv ESG API.

        API Doc: https://developers.refinitiv.com/esg
        """
        try:
            url = f"{self.config['refinitiv']['api_url']}/views/scores-full"
            api_key = self.config["refinitiv"]["api_key"]

            # Buscar por ISIN o nombre
            params = {}
            if isin:
                params["universe"] = isin
            else:
                params["company_name"] = company_name

            headers = {"Authorization": f"Bearer {api_key}"}

            async with self._session.get(
                url, params=params, headers=headers, timeout=15
            ) as response:
                if response.status == 404:
                    logger.warning(f"Empresa {company_name} no encontrada en Refinitiv ESG")
                    return None

                if response.status != 200:
                    logger.error(f"Refinitiv ESG API error: {response.status}")
                    return None

                data = await response.json()

                if not data.get("data"):
                    return None

                esg_data = data["data"][0]

                # Parsear respuesta
                return {
                    "company_name": esg_data["organizationName"],
                    "isin": esg_data.get("instrumentISIN"),
                    "overall_score": esg_data["esgScore"],  # 0-100
                    "rating": esg_data["esgRating"],  # A+, A, A-, B+, etc.
                    "percentile": esg_data.get("esgPercentile"),
                    "environmental": {
                        "score": esg_data["environmentScore"],
                        "pillars": {
                            "emissions": esg_data.get("emissionsScore"),
                            "resource_use": esg_data.get("resourceUseScore"),
                            "innovation": esg_data.get("environmentInnovationScore"),
                        },
                    },
                    "social": {
                        "score": esg_data["socialScore"],
                        "pillars": {
                            "workforce": esg_data.get("workforceScore"),
                            "human_rights": esg_data.get("humanRightsScore"),
                            "community": esg_data.get("communityScore"),
                            "product_responsibility": esg_data.get("productResponsibilityScore"),
                        },
                    },
                    "governance": {
                        "score": esg_data["governanceScore"],
                        "pillars": {
                            "management": esg_data.get("managementScore"),
                            "shareholders": esg_data.get("shareholdersScore"),
                            "csr_strategy": esg_data.get("csrStrategyScore"),
                        },
                    },
                    "controversies": {
                        "score": esg_data.get("controversiesScore"),
                        "count": esg_data.get("controversiesCount", 0),
                        "categories": esg_data.get("controversyCategories", []),
                    },
                    "trends": {
                        "1y_change": esg_data.get("esgScore1YearChange"),
                        "3y_change": esg_data.get("esgScore3YearChange"),
                    },
                    "source": "Refinitiv",
                    "last_updated": esg_data.get("periodEndDate"),
                    "checked_at": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error consultando Refinitiv ESG: {e}")
            return None

    async def _query_msci(
        self, company_name: str, isin: Optional[str]
    ) -> Optional[Dict]:
        """
        Consulta MSCI ESG API (alternativa).

        API Doc: https://www.msci.com/esg-ratings
        """
        try:
            url = f"{self.config['msci']['api_url']}/ratings"
            api_key = self.config["msci"]["api_key"]

            params = {}
            if isin:
                params["isin"] = isin
            else:
                params["name"] = company_name

            headers = {"X-API-Key": api_key}

            async with self._session.get(
                url, params=params, headers=headers, timeout=15
            ) as response:
                if response.status != 200:
                    logger.error(f"MSCI ESG API error: {response.status}")
                    return None

                data = await response.json()

                if not data.get("results"):
                    return None

                esg_data = data["results"][0]

                # MSCI usa ratings AAA-CCC
                return {
                    "company_name": esg_data["issuer_name"],
                    "isin": esg_data.get("isin"),
                    "overall_score": self._rating_to_score(esg_data["esg_rating"]),
                    "rating": esg_data["esg_rating"],  # AAA, AA, A, BBB, BB, B, CCC
                    "environmental": {
                        "score": self._rating_to_score(esg_data.get("env_pillar_score")),
                    },
                    "social": {
                        "score": self._rating_to_score(esg_data.get("social_pillar_score")),
                    },
                    "governance": {
                        "score": self._rating_to_score(esg_data.get("gov_pillar_score")),
                    },
                    "controversies": {
                        "count": len(esg_data.get("controversies", [])),
                    },
                    "source": "MSCI",
                    "last_updated": esg_data.get("as_of_date"),
                    "checked_at": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error consultando MSCI ESG: {e}")
            return None

    def _rating_to_score(self, rating: str) -> float:
        """
        Convierte rating ESG (AAA-CCC) a score numérico (0-100).
        """
        rating_map = {
            "AAA": 100,
            "AA": 87.5,
            "A": 75,
            "BBB": 62.5,
            "BB": 50,
            "B": 37.5,
            "CCC": 25,
        }
        return rating_map.get(rating, 50)

    async def get_esg_batch(self, companies: list[Dict]) -> list[Dict]:
        """
        Obtiene ESG scores para múltiples empresas en paralelo.

        Args:
            companies: Lista de dicts con 'company_name' y opcionalmente 'isin'

        Returns:
            Lista de resultados ESG
        """
        import asyncio

        tasks = [
            self.get_esg_score(company["company_name"], company.get("isin"))
            for company in companies
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        esg_scores = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                esg_scores.append({
                    "company_name": companies[idx]["company_name"],
                    "error": str(result),
                    "score_available": False,
                })
            else:
                esg_scores.append({
                    **result,
                    "score_available": True,
                })

        return esg_scores

    def categorize_risk(self, esg_score: float) -> Dict:
        """
        Categoriza el riesgo ESG basado en el score.

        Args:
            esg_score: Score ESG (0-100)

        Returns:
            Dict con categorización de riesgo
        """
        if esg_score >= 75:
            return {
                "level": "LOW",
                "color": "green",
                "description": "Excelente desempeño ESG, bajo riesgo",
            }
        elif esg_score >= 50:
            return {
                "level": "MEDIUM",
                "color": "yellow",
                "description": "Desempeño ESG promedio, riesgo moderado",
            }
        else:
            return {
                "level": "HIGH",
                "color": "red",
                "description": "Bajo desempeño ESG, alto riesgo",
            }
