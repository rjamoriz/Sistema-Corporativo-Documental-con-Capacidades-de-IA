"""
Prometheus Metrics and Monitoring
Sistema de métricas y monitoreo avanzado
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, REGISTRY
from prometheus_client.exposition import make_asgi_app
import time
import functools
from typing import Callable, Any
import logging
import asyncio

logger = logging.getLogger(__name__)

# ========================================
# VALIDATION METRICS
# ========================================

# Counter: Validaciones totales
validation_requests_total = Counter(
    'validation_requests_total',
    'Total number of validation requests',
    ['entity_type', 'source', 'status']
)

# Histogram: Duración de validaciones
validation_duration_seconds = Histogram(
    'validation_duration_seconds',
    'Duration of validation requests in seconds',
    ['service', 'operation'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Counter: Entidades flagged
entities_flagged_total = Counter(
    'entities_flagged_total',
    'Total number of entities flagged',
    ['source', 'confidence_level']
)

# Gauge: Validaciones en proceso
validations_in_progress = Gauge(
    'validations_in_progress',
    'Number of validations currently being processed'
)

# ========================================
# API METRICS
# ========================================

# Counter: Llamadas a APIs externas
api_calls_total = Counter(
    'api_calls_total',
    'Total API calls to external services',
    ['service', 'endpoint', 'status_code']
)

# Histogram: Latencia de APIs externas
api_latency_seconds = Histogram(
    'api_latency_seconds',
    'Latency of external API calls',
    ['service', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Counter: Fallos de API
api_failures_total = Counter(
    'api_failures_total',
    'Total API call failures',
    ['service', 'error_type']
)

# ========================================
# SCHEDULER METRICS
# ========================================

# Counter: Ejecuciones de tareas programadas
scheduler_task_executions_total = Counter(
    'scheduler_task_executions_total',
    'Total scheduler task executions',
    ['task_name', 'status']
)

# Histogram: Duración de tareas
scheduler_task_duration_seconds = Histogram(
    'scheduler_task_duration_seconds',
    'Duration of scheduler tasks',
    ['task_name'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
)

# Gauge: Próxima ejecución de tarea
scheduler_next_run_timestamp = Gauge(
    'scheduler_next_run_timestamp',
    'Timestamp of next scheduled task run',
    ['task_name']
)

# ========================================
# NOTIFICATION METRICS
# ========================================

# Counter: Notificaciones enviadas
notifications_sent_total = Counter(
    'notifications_sent_total',
    'Total notifications sent',
    ['channel', 'priority', 'status']
)

# Histogram: Tiempo de envío de notificaciones
notification_send_duration_seconds = Histogram(
    'notification_send_duration_seconds',
    'Duration of notification sending',
    ['channel'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Counter: Fallos de notificación
notification_failures_total = Counter(
    'notification_failures_total',
    'Total notification failures',
    ['channel', 'error_type']
)

# ========================================
# DOCUMENT PROCESSING METRICS
# ========================================

# Counter: Documentos procesados
documents_processed_total = Counter(
    'documents_processed_total',
    'Total documents processed',
    ['status', 'classification']
)

# Histogram: Tiempo de procesamiento de documentos
document_processing_duration_seconds = Histogram(
    'document_processing_duration_seconds',
    'Duration of document processing',
    ['stage'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

# Gauge: Documentos en cola
documents_in_queue = Gauge(
    'documents_in_queue',
    'Number of documents in processing queue',
    ['status']
)

# ========================================
# DATABASE METRICS
# ========================================

# Gauge: Conexiones activas a BD
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

# Gauge: Conexiones disponibles en pool
db_connections_available = Gauge(
    'db_connections_available',
    'Available database connections in pool'
)

# Histogram: Duración de queries
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Duration of database queries',
    ['table', 'operation'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# ========================================
# CACHE METRICS
# ========================================

# Counter: Cache hits/misses
cache_requests_total = Counter(
    'cache_requests_total',
    'Total cache requests',
    ['cache_name', 'result']  # result: hit, miss
)

# Gauge: Tamaño del cache
cache_size_bytes = Gauge(
    'cache_size_bytes',
    'Size of cache in bytes',
    ['cache_name']
)

# ========================================
# SYSTEM METRICS
# ========================================

# Info: Versión de la aplicación
app_info = Info(
    'app_info',
    'Application information'
)

app_info.info({
    'version': '1.0.0',
    'environment': 'production',
    'component': 'validation_system'
})

# Gauge: Health status
system_health_status = Gauge(
    'system_health_status',
    'System health status (1=healthy, 0=unhealthy)',
    ['component']
)

# ========================================
# DECORATORS PARA METRICS
# ========================================

def track_validation_time(service: str, operation: str):
    """
    Decorator para medir tiempo de validación
    
    Usage:
        @track_validation_time('sanctions', 'check_ofac')
        async def check_ofac(name: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            validations_in_progress.inc()
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                
                # Registrar métricas
                duration = time.time() - start_time
                validation_duration_seconds.labels(
                    service=service,
                    operation=operation
                ).observe(duration)
                
                # Determinar status
                status = 'success' if result else 'error'
                validation_requests_total.labels(
                    entity_type='unknown',
                    source=service,
                    status=status
                ).inc()
                
                return result
                
            except Exception as e:
                validation_requests_total.labels(
                    entity_type='unknown',
                    source=service,
                    status='error'
                ).inc()
                raise
            finally:
                validations_in_progress.dec()
        
        return wrapper
    return decorator


def track_api_call(service: str, endpoint: str):
    """
    Decorator para medir llamadas a APIs externas
    
    Usage:
        @track_api_call('ofac', '/search')
        async def call_ofac_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Métricas de éxito
                duration = time.time() - start_time
                api_latency_seconds.labels(
                    service=service,
                    endpoint=endpoint
                ).observe(duration)
                
                api_calls_total.labels(
                    service=service,
                    endpoint=endpoint,
                    status_code='200'
                ).inc()
                
                return result
                
            except Exception as e:
                # Métricas de fallo
                api_failures_total.labels(
                    service=service,
                    error_type=type(e).__name__
                ).inc()
                
                api_calls_total.labels(
                    service=service,
                    endpoint=endpoint,
                    status_code='error'
                ).inc()
                
                raise
        
        return wrapper
    return decorator


def track_scheduler_task(task_name: str):
    """
    Decorator para medir ejecución de tareas programadas
    
    Usage:
        @track_scheduler_task('sync_sanctions')
        async def sync_sanctions_lists():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Métricas de éxito
                duration = time.time() - start_time
                scheduler_task_duration_seconds.labels(
                    task_name=task_name
                ).observe(duration)
                
                scheduler_task_executions_total.labels(
                    task_name=task_name,
                    status='success'
                ).inc()
                
                logger.info(f"Task {task_name} completed in {duration:.2f}s")
                
                return result
                
            except Exception as e:
                scheduler_task_executions_total.labels(
                    task_name=task_name,
                    status='error'
                ).inc()
                
                logger.error(f"Task {task_name} failed: {e}")
                raise
        
        return wrapper
    return decorator


# ========================================
# HEALTH CHECK FUNCTIONS
# ========================================

async def check_database_health() -> bool:
    """Verifica salud de la BD"""
    try:
        from backend.core.database import async_session_maker
        
        async with async_session_maker() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        
        system_health_status.labels(component='database').set(1)
        return True
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        system_health_status.labels(component='database').set(0)
        return False


async def check_scheduler_health() -> bool:
    """Verifica salud del scheduler"""
    try:
        from backend.schedulers.validation_scheduler import validation_scheduler
        
        if validation_scheduler.scheduler.running:
            system_health_status.labels(component='scheduler').set(1)
            return True
        else:
            system_health_status.labels(component='scheduler').set(0)
            return False
            
    except Exception as e:
        logger.error(f"Scheduler health check failed: {e}")
        system_health_status.labels(component='scheduler').set(0)
        return False


async def check_external_apis_health() -> dict:
    """Verifica salud de APIs externas"""
    results = {}
    
    # OFAC API
    try:
        from backend.services.validation.sanctions_service import sanctions_service
        await sanctions_service.check_ofac("health_check")
        system_health_status.labels(component='ofac_api').set(1)
        results['ofac'] = True
    except Exception:
        system_health_status.labels(component='ofac_api').set(0)
        results['ofac'] = False
    
    return results


async def run_health_checks() -> dict:
    """
    Ejecuta todos los health checks
    
    Returns:
        dict: Resultados de los checks
    """
    results = {
        'database': await check_database_health(),
        'scheduler': await check_scheduler_health(),
        'external_apis': await check_external_apis_health()
    }
    
    return results


# ========================================
# METRICS ENDPOINT
# ========================================

def get_metrics_app():
    """
    Crea aplicación ASGI para endpoint de métricas
    
    Usage en FastAPI:
        from backend.monitoring.metrics import get_metrics_app
        app.mount("/metrics", get_metrics_app())
    """
    return make_asgi_app()


def get_metrics_text() -> bytes:
    """
    Obtiene métricas en formato texto Prometheus
    
    Returns:
        bytes: Métricas en formato Prometheus
    """
    return generate_latest(REGISTRY)


# ========================================
# BACKGROUND METRICS COLLECTOR
# ========================================

async def collect_system_metrics():
    """
    Recolecta métricas del sistema periódicamente
    Ejecutar como background task
    """
    while True:
        try:
            # Recolectar pool stats
            from backend.core.database import engine
            pool = engine.pool
            
            db_connections_active.set(pool.checkedout())
            db_connections_available.set(pool.checkedin())
            
            # Health checks
            await run_health_checks()
            
            await asyncio.sleep(30)  # Cada 30 segundos
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            await asyncio.sleep(60)


# Export all
__all__ = [
    # Metrics
    'validation_requests_total',
    'validation_duration_seconds',
    'entities_flagged_total',
    'validations_in_progress',
    'api_calls_total',
    'api_latency_seconds',
    'api_failures_total',
    'scheduler_task_executions_total',
    'scheduler_task_duration_seconds',
    'notifications_sent_total',
    'notification_send_duration_seconds',
    'documents_processed_total',
    'document_processing_duration_seconds',
    'db_query_duration_seconds',
    'cache_requests_total',
    'system_health_status',
    
    # Decorators
    'track_validation_time',
    'track_api_call',
    'track_scheduler_task',
    
    # Functions
    'get_metrics_app',
    'get_metrics_text',
    'run_health_checks',
    'collect_system_metrics'
]
