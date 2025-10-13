"""
Database Performance Configuration
Connection pooling y query optimization
"""
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import time
import logging

from core.config import settings

logger = logging.getLogger(__name__)


# ========================================
# CONNECTION POOL CONFIGURATION
# ========================================

def create_optimized_engine():
    """
    Crea engine con connection pooling optimizado
    
    Pool settings:
    - pool_size: Número de conexiones permanentes (20)
    - max_overflow: Conexiones adicionales temporales (10)
    - pool_timeout: Timeout para obtener conexión (30s)
    - pool_recycle: Reciclar conexiones cada hora (3600s)
    - pool_pre_ping: Verificar conexión antes de usar
    """
    engine = create_async_engine(
        settings.DATABASE_URL,
        
        # Connection pooling
        poolclass=QueuePool,
        pool_size=20,              # Conexiones permanentes
        max_overflow=10,           # Conexiones overflow
        pool_timeout=30,           # Timeout en segundos
        pool_recycle=3600,         # Reciclar cada hora
        pool_pre_ping=True,        # Verificar antes de usar
        
        # Query execution settings
        echo=False,                # No log SQL en producción
        echo_pool=False,           # No log pool events
        
        # Connection arguments
        connect_args={
            "server_settings": {
                "application_name": "FinancIA_DMS",
                "jit": "on",                    # JIT compilation
            },
            "command_timeout": 60,              # Query timeout
            "timeout": 10,                      # Connection timeout
        },
        
        # Execution options
        execution_options={
            "isolation_level": "READ COMMITTED"
        }
    )
    
    return engine


# ========================================
# QUERY OPTIMIZATION HOOKS
# ========================================

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    """
    Hook para logging de queries lentas
    """
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    """
    Hook para detectar queries lentas
    """
    total = time.time() - conn.info['query_start_time'].pop(-1)
    
    # Log queries > 1 segundo
    if total > 1.0:
        logger.warning(
            f"Slow query detected: {total:.2f}s\n"
            f"Statement: {statement[:200]}\n"
            f"Params: {params}"
        )


# ========================================
# SESSION FACTORY CON OPTIMIZACIONES
# ========================================

def create_session_factory(engine):
    """
    Crea session factory con configuración optimizada
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # No expirar objetos al commit
        autoflush=False,         # Control manual de flush
        autocommit=False,
    )


# ========================================
# QUERY OPTIMIZATION HELPERS
# ========================================

async def explain_analyze_query(session: AsyncSession, query: str) -> dict:
    """
    Ejecuta EXPLAIN ANALYZE para una query
    
    Args:
        session: Sesión de BD
        query: Query SQL a analizar
        
    Returns:
        dict: Resultado del análisis
    """
    result = await session.execute(
        text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")
    )
    
    analysis = result.scalar()
    return analysis


async def optimize_table(session: AsyncSession, table_name: str):
    """
    Ejecuta VACUUM ANALYZE en una tabla
    
    Args:
        session: Sesión de BD
        table_name: Nombre de la tabla
    """
    await session.execute(text(f"VACUUM ANALYZE {table_name}"))
    logger.info(f"Table {table_name} optimized")


async def get_table_stats(session: AsyncSession, table_name: str) -> dict:
    """
    Obtiene estadísticas de una tabla
    
    Args:
        session: Sesión de BD
        table_name: Nombre de la tabla
        
    Returns:
        dict: Estadísticas de la tabla
    """
    result = await session.execute(text(f"""
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        WHERE tablename = :table_name
    """), {"table_name": table_name})
    
    row = result.fetchone()
    if row:
        return {
            "schema": row[0],
            "table": row[1],
            "inserts": row[2],
            "updates": row[3],
            "deletes": row[4],
            "live_tuples": row[5],
            "dead_tuples": row[6],
            "last_vacuum": row[7],
            "last_autovacuum": row[8],
            "last_analyze": row[9],
            "last_autoanalyze": row[10]
        }
    return {}


async def get_index_usage(session: AsyncSession, table_name: str) -> list:
    """
    Obtiene estadísticas de uso de índices
    
    Args:
        session: Sesión de BD
        table_name: Nombre de la tabla
        
    Returns:
        list: Lista de índices y su uso
    """
    result = await session.execute(text("""
        SELECT 
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes
        WHERE tablename = :table_name
        ORDER BY idx_scan DESC
    """), {"table_name": table_name})
    
    indexes = []
    for row in result:
        indexes.append({
            "index_name": row[0],
            "scans": row[1],
            "tuples_read": row[2],
            "tuples_fetched": row[3]
        })
    
    return indexes


async def find_missing_indexes(session: AsyncSession) -> list:
    """
    Encuentra tablas que podrían beneficiarse de índices
    
    Returns:
        list: Sugerencias de índices
    """
    result = await session.execute(text("""
        SELECT 
            schemaname,
            tablename,
            seq_scan,
            seq_tup_read,
            idx_scan,
            seq_tup_read / seq_scan as avg_seq_read
        FROM pg_stat_user_tables
        WHERE seq_scan > 0
        AND schemaname = 'public'
        ORDER BY seq_tup_read DESC
        LIMIT 10
    """))
    
    suggestions = []
    for row in result:
        if row[5] > 1000:  # Promedio > 1000 tuplas por scan secuencial
            suggestions.append({
                "schema": row[0],
                "table": row[1],
                "sequential_scans": row[2],
                "tuples_read": row[3],
                "index_scans": row[4],
                "avg_tuples_per_scan": row[5],
                "recommendation": f"Consider adding index on {row[1]}"
            })
    
    return suggestions


# ========================================
# CACHE CONFIGURATION
# ========================================

class QueryCache:
    """
    Simple query cache para resultados frecuentes
    """
    
    def __init__(self, ttl: int = 300):
        """
        Args:
            ttl: Time to live en segundos (default 5 min)
        """
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str):
        """Obtiene valor del cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value):
        """Almacena valor en cache"""
        self.cache[key] = (value, time.time())
    
    def invalidate(self, key: str):
        """Invalida entrada del cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Limpia todo el cache"""
        self.cache.clear()


# Instancia global de cache
query_cache = QueryCache(ttl=300)


# ========================================
# BATCH OPERATIONS
# ========================================

async def bulk_insert_optimized(
    session: AsyncSession,
    model,
    records: list,
    batch_size: int = 1000
):
    """
    Inserción masiva optimizada
    
    Args:
        session: Sesión de BD
        model: Modelo SQLAlchemy
        records: Lista de diccionarios con datos
        batch_size: Tamaño del batch
    """
    total = len(records)
    inserted = 0
    
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        
        # Usar bulk_insert_mappings para mejor performance
        session.bulk_insert_mappings(model, batch)
        
        inserted += len(batch)
        logger.info(f"Inserted {inserted}/{total} records")
    
    await session.commit()
    logger.info(f"Bulk insert completed: {total} records")


async def bulk_update_optimized(
    session: AsyncSession,
    model,
    records: list,
    batch_size: int = 1000
):
    """
    Actualización masiva optimizada
    
    Args:
        session: Sesión de BD
        model: Modelo SQLAlchemy
        records: Lista de diccionarios con datos (debe incluir id)
        batch_size: Tamaño del batch
    """
    total = len(records)
    updated = 0
    
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        
        # Usar bulk_update_mappings
        session.bulk_update_mappings(model, batch)
        
        updated += len(batch)
        logger.info(f"Updated {updated}/{total} records")
    
    await session.commit()
    logger.info(f"Bulk update completed: {total} records")


# ========================================
# MONITORING
# ========================================

async def get_connection_pool_stats(engine) -> dict:
    """
    Obtiene estadísticas del connection pool
    
    Returns:
        dict: Estadísticas del pool
    """
    pool = engine.pool
    
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.size() + pool.overflow()
    }


async def health_check(session: AsyncSession) -> bool:
    """
    Verifica salud de la conexión a BD
    
    Returns:
        bool: True si la conexión es saludable
    """
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Export optimized configuration
__all__ = [
    'create_optimized_engine',
    'create_session_factory',
    'explain_analyze_query',
    'optimize_table',
    'get_table_stats',
    'get_index_usage',
    'find_missing_indexes',
    'QueryCache',
    'query_cache',
    'bulk_insert_optimized',
    'bulk_update_optimized',
    'get_connection_pool_stats',
    'health_check'
]
