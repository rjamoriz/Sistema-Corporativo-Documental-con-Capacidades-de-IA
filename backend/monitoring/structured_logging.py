"""
Structured Logging Configuration
Logging avanzado con contexto y formato JSON
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
import traceback

# Context variables para request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
document_id_var: ContextVar[Optional[str]] = ContextVar('document_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Formatter para logs estructurados en formato JSON
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formatea log record a JSON estructurado
        """
        # Campos base
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar context variables si existen
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
        
        document_id = document_id_var.get()
        if document_id:
            log_data["document_id"] = document_id
        
        # Agregar extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # Agregar exception info si existe
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Agregar stack info si existe
        if record.stack_info:
            log_data["stack_info"] = record.stack_info
        
        return json.dumps(log_data, ensure_ascii=False)


class ContextLogger(logging.LoggerAdapter):
    """
    Logger adapter con contexto automático
    """
    
    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Procesa mensaje agregando contexto
        """
        # Agregar context variables
        extra = kwargs.get('extra', {})
        
        request_id = request_id_var.get()
        if request_id:
            extra['request_id'] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            extra['user_id'] = user_id
        
        document_id = document_id_var.get()
        if document_id:
            extra['document_id'] = document_id
        
        # Merge con extra existente
        if self.extra:
            extra.update(self.extra)
        
        kwargs['extra'] = extra
        
        return msg, kwargs
    
    def with_context(self, **context):
        """
        Crea nuevo logger con contexto adicional
        
        Usage:
            logger = logger.with_context(user_id="123", action="upload")
            logger.info("Document uploaded")
        """
        new_extra = {**self.extra, **context}
        return ContextLogger(self.logger, new_extra)


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None
):
    """
    Configura sistema de logging
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Tipo de formato ("json" o "text")
        log_file: Ruta opcional para archivo de log
    """
    # Configurar nivel
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Crear formatter
    if format_type == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Configurar handler para stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(numeric_level)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(stdout_handler)
    
    # Agregar file handler si se especifica
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)


def get_logger(name: str, **context) -> ContextLogger:
    """
    Obtiene logger con contexto
    
    Args:
        name: Nombre del logger
        **context: Contexto adicional
        
    Returns:
        ContextLogger: Logger con contexto
        
    Usage:
        logger = get_logger(__name__, service="validation")
        logger.info("Starting validation", entity_name="Test Corp")
    """
    base_logger = logging.getLogger(name)
    return ContextLogger(base_logger, context)


# ========================================
# LOGGING DECORATORS
# ========================================

def log_function_call(logger: ContextLogger):
    """
    Decorator para loggear llamadas a funciones
    
    Usage:
        @log_function_call(logger)
        async def my_function(arg1, arg2):
            ...
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            logger.info(
                f"Function {func_name} called",
                function=func_name,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            
            try:
                result = await func(*args, **kwargs)
                
                logger.info(
                    f"Function {func_name} completed successfully",
                    function=func_name
                )
                
                return result
                
            except Exception as e:
                logger.error(
                    f"Function {func_name} failed",
                    function=func_name,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_performance(logger: ContextLogger, threshold_seconds: float = 1.0):
    """
    Decorator para loggear performance
    
    Usage:
        @log_performance(logger, threshold_seconds=0.5)
        async def slow_function():
            ...
    """
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                if duration > threshold_seconds:
                    logger.warning(
                        f"Slow function execution: {func_name}",
                        function=func_name,
                        duration_seconds=round(duration, 3),
                        threshold_seconds=threshold_seconds
                    )
                else:
                    logger.debug(
                        f"Function executed: {func_name}",
                        function=func_name,
                        duration_seconds=round(duration, 3)
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function failed: {func_name}",
                    function=func_name,
                    duration_seconds=round(duration, 3),
                    error=str(e),
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


# ========================================
# AUDIT LOGGING
# ========================================

class AuditLogger:
    """
    Logger especializado para auditoría
    """
    
    def __init__(self, name: str = "audit"):
        self.logger = get_logger(name, log_type="audit")
    
    def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        status: str = "success",
        **details
    ):
        """
        Registra acción de auditoría
        
        Args:
            action: Acción realizada (create, update, delete, access, etc.)
            resource_type: Tipo de recurso (document, user, etc.)
            resource_id: ID del recurso
            user_id: ID del usuario
            status: Estado de la acción
            **details: Detalles adicionales
        """
        self.logger.info(
            f"Audit: {action} {resource_type}",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id or user_id_var.get(),
            status=status,
            **details
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **details
    ):
        """
        Registra evento de seguridad
        
        Args:
            event_type: Tipo de evento (login_failed, unauthorized_access, etc.)
            severity: Severidad (low, medium, high, critical)
            user_id: ID del usuario
            ip_address: IP del origen
            **details: Detalles adicionales
        """
        log_method = getattr(self.logger, severity.lower(), self.logger.warning)
        
        log_method(
            f"Security event: {event_type}",
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            **details
        )


# ========================================
# CONTEXT MANAGERS
# ========================================

class LogContext:
    """
    Context manager para logging con contexto temporal
    
    Usage:
        with LogContext(request_id="123", user_id="456"):
            logger.info("Processing request")  # Incluirá request_id y user_id
    """
    
    def __init__(self, **context):
        self.context = context
        self.tokens = {}
    
    def __enter__(self):
        # Guardar valores actuales y establecer nuevos
        for key, value in self.context.items():
            if key == 'request_id':
                self.tokens['request_id'] = request_id_var.set(value)
            elif key == 'user_id':
                self.tokens['user_id'] = user_id_var.set(value)
            elif key == 'document_id':
                self.tokens['document_id'] = document_id_var.set(value)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restaurar valores anteriores
        for key, token in self.tokens.items():
            if key == 'request_id':
                request_id_var.reset(token)
            elif key == 'user_id':
                user_id_var.reset(token)
            elif key == 'document_id':
                document_id_var.reset(token)


# ========================================
# INSTANCIAS GLOBALES
# ========================================

# Logger por defecto
default_logger = get_logger(__name__)

# Audit logger
audit_logger = AuditLogger()


# Export all
__all__ = [
    'StructuredFormatter',
    'ContextLogger',
    'setup_logging',
    'get_logger',
    'log_function_call',
    'log_performance',
    'AuditLogger',
    'LogContext',
    'default_logger',
    'audit_logger',
    'request_id_var',
    'user_id_var',
    'document_id_var'
]
