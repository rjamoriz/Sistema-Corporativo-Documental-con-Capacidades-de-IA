"""
Configuración de APIs para validación de terceros.

IMPORTANTE: Las claves API deben configurarse como variables de entorno:
- OFAC_API_KEY
- EU_SANCTIONS_API_KEY
- INFOEMPRESA_API_KEY
- ESG_API_KEY
"""

import os

SANCTIONS_CONFIG = {
    "ofac": {
        "api_url": "https://sanctionssearch.ofac.treas.gov/api/v1/search",
        "api_key": os.getenv("OFAC_API_KEY", ""),
        "enabled": True,
    },
    "eu_sanctions": {
        "api_url": "https://webgate.ec.europa.eu/fsd/fsf/api/v1/search",
        "api_key": os.getenv("EU_SANCTIONS_API_KEY", ""),
        "enabled": True,
    },
    "world_bank": {
        "api_url": "https://apidocs.worldbank.org/sanctions/debarred",
        "enabled": True,
    },
    "fuzzy_threshold": 85,  # Mínimo de similitud para considerar match (0-100)
    "cache_ttl": 86400,  # 24 horas en segundos
}

BUSINESS_REGISTRY_CONFIG = {
    "infoempresa": {
        "api_url": "https://api.infoempresa.com/v1",
        "api_key": os.getenv("INFOEMPRESA_API_KEY", ""),
        "enabled": True,
    },
    "informa": {
        "api_url": "https://api.informa.es/v2",
        "api_key": os.getenv("INFORMA_API_KEY", ""),
        "enabled": False,  # Alternativa a InfoEmpresa
    },
}

ESG_CONFIG = {
    "refinitiv": {
        "api_url": "https://api.refinitiv.com/esg/v1",
        "api_key": os.getenv("REFINITIV_API_KEY", ""),
        "enabled": True,
    },
    "msci": {
        "api_url": "https://api.msci.com/esg/v1",
        "api_key": os.getenv("MSCI_API_KEY", ""),
        "enabled": False,  # Alternativa a Refinitiv
    },
}

# Configuración de sincronización automática
SYNC_CONFIG = {
    "sanctions_list_update_schedule": "0 2 * * *",  # Diario a las 2 AM
    "business_registry_cache_ttl": 604800,  # 7 días
    "esg_score_cache_ttl": 2592000,  # 30 días
}
