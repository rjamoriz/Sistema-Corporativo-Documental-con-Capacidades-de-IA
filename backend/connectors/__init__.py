"""
Connectors Package - Enterprise Integration Layer

Este paquete contiene conectores para integración con sistemas enterprise:
- SharePoint Online/On-Premises
- SAP DMS (Document Management Service)
- Alfresco (futuro)
- Microsoft Exchange (futuro)
"""

from .base_connector import BaseConnector
from .sharepoint_connector import SharePointConnector
from .sap_dms_connector import SAPDMSConnector

__all__ = [
    "BaseConnector",
    "SharePointConnector",
    "SAPDMSConnector",
]

__version__ = "1.0.0"
