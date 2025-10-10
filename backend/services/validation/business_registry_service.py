"""
Servicio de validación contra registros mercantiles.

Integra InfoEmpresas/Informa para validar:
- Existencia legal de empresas
- Estado activo/inactivo
- Datos financieros
- Indicadores de riesgo
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import aiohttp

from config.validation_apis import BUSINESS_REGISTRY_CONFIG


logger = logging.getLogger(__name__)


class BusinessRegistryService:
    """Servicio para validación de empresas en registros mercantiles."""

    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el servicio de registro mercantil.

        Args:
            config: Configuración opcional (usa BUSINESS_REGISTRY_CONFIG por defecto)
        """
        self.config = config or BUSINESS_REGISTRY_CONFIG
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

    async def check_company(
        self, cif: str, name: Optional[str] = None
    ) -> Dict:
        """
        Verifica una empresa en el registro mercantil.

        Args:
            cif: CIF/NIF de la empresa
            name: Nombre de la empresa (opcional, para validación cruzada)

        Returns:
            Dict con información de la empresa:
            {
                "cif": str,
                "name": str,
                "is_active": bool,
                "status": str,
                "capital": float,
                "incorporation_date": str,
                "financial_indicators": Dict,
                "risk_indicators": Dict,
                "source": str
            }
        """
        logger.info(f"Validando empresa: CIF={cif}, nombre={name}")

        # Verificar cache
        cache_key = f"company_{cif}"
        if cache_key in self._cache:
            cached_data, cached_at = self._cache[cache_key]
            if datetime.utcnow() - cached_at < timedelta(days=7):
                logger.info(f"Usando datos en cache para CIF {cif}")
                return cached_data

        # Consultar InfoEmpresa (preferido)
        if self.config["infoempresa"]["enabled"]:
            result = await self._query_infoempresa(cif, name)
            if result:
                self._cache[cache_key] = (result, datetime.utcnow())
                return result

        # Alternativa: Informa
        if self.config["informa"]["enabled"]:
            result = await self._query_informa(cif, name)
            if result:
                self._cache[cache_key] = (result, datetime.utcnow())
                return result

        raise ValueError(f"No se pudo validar empresa con CIF {cif}")

    async def _query_infoempresa(
        self, cif: str, name: Optional[str]
    ) -> Optional[Dict]:
        """
        Consulta InfoEmpresa API.

        API Doc: https://www.infoempresa.com/api-docs
        """
        try:
            url = f"{self.config['infoempresa']['api_url']}/company/{cif}"
            api_key = self.config["infoempresa"]["api_key"]

            headers = {"Authorization": f"Bearer {api_key}"}

            async with self._session.get(
                url, headers=headers, timeout=10
            ) as response:
                if response.status == 404:
                    logger.warning(f"Empresa con CIF {cif} no encontrada en InfoEmpresa")
                    return None

                if response.status != 200:
                    logger.error(f"InfoEmpresa API error: {response.status}")
                    return None

                data = await response.json()

                # Parsear respuesta
                return {
                    "cif": data["cif"],
                    "name": data["razon_social"],
                    "is_active": data["estado"] == "ACTIVA",
                    "status": data["estado"],
                    "capital": float(data.get("capital_social", 0)),
                    "incorporation_date": data.get("fecha_constitucion"),
                    "address": data.get("domicilio_social"),
                    "cnae": data.get("cnae"),
                    "employees": data.get("numero_empleados"),
                    "financial_indicators": {
                        "revenue": data.get("cifra_negocios"),
                        "profit": data.get("beneficio_neto"),
                        "assets": data.get("activo_total"),
                        "debt": data.get("deuda_total"),
                    },
                    "risk_indicators": {
                        "bankruptcy_risk": data.get("riesgo_concursal"),
                        "payment_behavior": data.get("comportamiento_pago"),
                        "incidents": data.get("incidencias", []),
                    },
                    "source": "InfoEmpresa",
                    "checked_at": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error consultando InfoEmpresa: {e}")
            return None

    async def _query_informa(
        self, cif: str, name: Optional[str]
    ) -> Optional[Dict]:
        """
        Consulta Informa API (alternativa).

        API Doc: https://www.informa.es/soluciones/api
        """
        try:
            url = f"{self.config['informa']['api_url']}/companies/search"
            api_key = self.config["informa"]["api_key"]

            params = {"vat": cif}
            headers = {"X-API-Key": api_key}

            async with self._session.get(
                url, params=params, headers=headers, timeout=10
            ) as response:
                if response.status != 200:
                    logger.error(f"Informa API error: {response.status}")
                    return None

                data = await response.json()
                if not data.get("results"):
                    return None

                company = data["results"][0]

                return {
                    "cif": company["vat"],
                    "name": company["company_name"],
                    "is_active": company["status"] == "active",
                    "status": company["status"],
                    "capital": float(company.get("share_capital", 0)),
                    "incorporation_date": company.get("incorporation_date"),
                    "financial_indicators": {
                        "revenue": company.get("turnover"),
                        "profit": company.get("net_income"),
                    },
                    "risk_indicators": {
                        "rating": company.get("credit_rating"),
                    },
                    "source": "Informa",
                    "checked_at": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error consultando Informa: {e}")
            return None

    async def validate_multiple_companies(
        self, companies: list[Dict[str, str]]
    ) -> list[Dict]:
        """
        Valida múltiples empresas en paralelo.

        Args:
            companies: Lista de dicts con 'cif' y opcionalmente 'name'

        Returns:
            Lista de resultados de validación
        """
        import asyncio

        tasks = [
            self.check_company(company["cif"], company.get("name"))
            for company in companies
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        validated = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                validated.append({
                    "cif": companies[idx]["cif"],
                    "error": str(result),
                    "is_valid": False,
                })
            else:
                validated.append({
                    **result,
                    "is_valid": True,
                })

        return validated
