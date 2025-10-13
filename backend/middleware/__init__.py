"""
Middleware Package
Contiene middlewares para procesamiento automático de documentos
"""
from .validation_middleware import validation_middleware

__all__ = ["validation_middleware"]
