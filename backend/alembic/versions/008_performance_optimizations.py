"""
Optimizaciones de Performance
Índices, connection pooling y query optimization
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '008_performance_optimizations'
down_revision = '007_validation_system'
branch_labels = None
depends_on = None


def upgrade():
    """Aplica optimizaciones de performance"""
    
    # ========================================
    # ÍNDICES PARA VALIDATION_RESULTS
    # ========================================
    
    # Índice para búsquedas por entity_name
    op.create_index(
        'idx_validation_results_entity_name',
        'validation_results',
        ['entity_name'],
        postgresql_ops={'entity_name': 'text_pattern_ops'}  # Para LIKE queries
    )
    
    # Índice para filtrar por confidence
    op.create_index(
        'idx_validation_results_confidence',
        'validation_results',
        ['confidence'],
        postgresql_where=sa.text('confidence >= 0.7')  # Partial index para high confidence
    )
    
    # Índice compuesto para queries comunes
    op.create_index(
        'idx_validation_results_flagged_date',
        'validation_results',
        ['is_flagged', 'created_at'],
        postgresql_where=sa.text('is_flagged = true')
    )
    
    # Índice para búsquedas por documento
    op.create_index(
        'idx_validation_results_document_id',
        'validation_results',
        ['document_id']
    )
    
    # ========================================
    # ÍNDICES PARA SANCTIONS_LIST
    # ========================================
    
    # Índice GIN para búsqueda full-text
    op.execute("""
        CREATE INDEX idx_sanctions_list_name_gin 
        ON sanctions_list 
        USING gin(to_tsvector('simple', name))
    """)
    
    # Índice para filtrar por fuente
    op.create_index(
        'idx_sanctions_list_source',
        'sanctions_list',
        ['source']
    )
    
    # Índice para búsquedas por tipo
    op.create_index(
        'idx_sanctions_list_type',
        'sanctions_list',
        ['entity_type']
    )
    
    # Índice compuesto para caché lookups
    op.create_index(
        'idx_sanctions_list_source_name',
        'sanctions_list',
        ['source', 'name']
    )
    
    # ========================================
    # ÍNDICES PARA DOCUMENTS
    # ========================================
    
    # Índice para búsquedas por usuario
    op.create_index(
        'idx_documents_uploaded_by',
        'documents',
        ['uploaded_by']
    )
    
    # Índice para filtrar por estado
    op.create_index(
        'idx_documents_status',
        'documents',
        ['status']
    )
    
    # Índice compuesto para dashboard queries
    op.create_index(
        'idx_documents_status_date',
        'documents',
        ['status', 'uploaded_at']
    )
    
    # Índice para búsquedas por hash (dedup)
    op.create_index(
        'idx_documents_file_hash',
        'documents',
        ['file_hash']
    )
    
    # ========================================
    # ÍNDICES PARA DOCUMENT_CHUNKS
    # ========================================
    
    # Índice para joins con documents
    op.create_index(
        'idx_document_chunks_document_id',
        'document_chunks',
        ['document_id']
    )
    
    # Índice para búsquedas por chunk_index
    op.create_index(
        'idx_document_chunks_chunk_index',
        'document_chunks',
        ['document_id', 'chunk_index']
    )
    
    # ========================================
    # OPTIMIZACIONES DE TABLAS
    # ========================================
    
    # Habilitar autovacuum agresivo para tablas con alta escritura
    op.execute("""
        ALTER TABLE validation_results 
        SET (
            autovacuum_vacuum_scale_factor = 0.01,
            autovacuum_analyze_scale_factor = 0.005
        )
    """)
    
    op.execute("""
        ALTER TABLE sanctions_list 
        SET (
            autovacuum_vacuum_scale_factor = 0.02,
            autovacuum_analyze_scale_factor = 0.01
        )
    """)
    
    # ========================================
    # VISTAS MATERIALIZADAS
    # ========================================
    
    # Vista materializada para dashboard stats (cache)
    op.execute("""
        CREATE MATERIALIZED VIEW validation_stats_cache AS
        SELECT 
            DATE(created_at) as stat_date,
            COUNT(*) as total_validations,
            SUM(CASE WHEN is_flagged THEN 1 ELSE 0 END) as flagged_count,
            AVG(confidence) as avg_confidence,
            COUNT(DISTINCT document_id) as unique_documents
        FROM validation_results
        WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY DATE(created_at)
        ORDER BY stat_date DESC
    """)
    
    # Índice en vista materializada
    op.create_index(
        'idx_validation_stats_cache_date',
        'validation_stats_cache',
        ['stat_date']
    )
    
    # ========================================
    # FUNCIONES PARA PERFORMANCE
    # ========================================
    
    # Función para refresh de vista materializada (llamar desde scheduler)
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_validation_stats()
        RETURNS void AS $$
        BEGIN
            REFRESH MATERIALIZED VIEW CONCURRENTLY validation_stats_cache;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Función de búsqueda optimizada con cache
    op.execute("""
        CREATE OR REPLACE FUNCTION search_sanctions(
            search_term TEXT,
            max_results INT DEFAULT 10
        )
        RETURNS TABLE (
            id INTEGER,
            name TEXT,
            entity_type TEXT,
            source TEXT,
            similarity REAL
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                s.id,
                s.name,
                s.entity_type,
                s.source,
                SIMILARITY(s.name, search_term) as sim
            FROM sanctions_list s
            WHERE s.name % search_term  -- Trigram similarity
            ORDER BY sim DESC
            LIMIT max_results;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Habilitar extensión pg_trgm para búsqueda fuzzy
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    
    # Índice GiST para búsqueda fuzzy
    op.execute("""
        CREATE INDEX idx_sanctions_list_name_trgm 
        ON sanctions_list 
        USING gist(name gist_trgm_ops)
    """)
    
    print("✅ Optimizaciones de performance aplicadas")


def downgrade():
    """Revierte optimizaciones de performance"""
    
    # Eliminar funciones
    op.execute("DROP FUNCTION IF EXISTS refresh_validation_stats()")
    op.execute("DROP FUNCTION IF EXISTS search_sanctions(TEXT, INT)")
    
    # Eliminar vista materializada
    op.execute("DROP MATERIALIZED VIEW IF EXISTS validation_stats_cache")
    
    # Eliminar índices
    op.drop_index('idx_validation_results_entity_name')
    op.drop_index('idx_validation_results_confidence')
    op.drop_index('idx_validation_results_flagged_date')
    op.drop_index('idx_validation_results_document_id')
    
    op.execute("DROP INDEX IF EXISTS idx_sanctions_list_name_gin")
    op.execute("DROP INDEX IF EXISTS idx_sanctions_list_name_trgm")
    op.drop_index('idx_sanctions_list_source')
    op.drop_index('idx_sanctions_list_type')
    op.drop_index('idx_sanctions_list_source_name')
    
    op.drop_index('idx_documents_uploaded_by')
    op.drop_index('idx_documents_status')
    op.drop_index('idx_documents_status_date')
    op.drop_index('idx_documents_file_hash')
    
    op.drop_index('idx_document_chunks_document_id')
    op.drop_index('idx_document_chunks_chunk_index')
    
    # Revertir configuraciones de autovacuum
    op.execute("ALTER TABLE validation_results RESET (autovacuum_vacuum_scale_factor, autovacuum_analyze_scale_factor)")
    op.execute("ALTER TABLE sanctions_list RESET (autovacuum_vacuum_scale_factor, autovacuum_analyze_scale_factor)")
    
    print("✅ Optimizaciones de performance revertidas")
