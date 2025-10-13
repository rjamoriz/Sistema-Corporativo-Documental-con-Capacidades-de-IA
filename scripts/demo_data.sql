-- ============================================
-- Demo Data for FinancIA DMS
-- Script para poblar la BD con datos realistas
-- ============================================

-- Limpiar datos existentes (solo para demo)
TRUNCATE TABLE validation_results CASCADE;
TRUNCATE TABLE sanctions_list CASCADE;
TRUNCATE TABLE document_chunks CASCADE;
TRUNCATE TABLE documents CASCADE;
TRUNCATE TABLE users CASCADE;

-- ============================================
-- 1. USUARIOS DE DEMO
-- ============================================

INSERT INTO users (id, email, password_hash, full_name, role, department, created_at) VALUES
(1, 'admin@financia.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyE3HOaVQcLG', 'Admin Demo', 'admin', 'IT', NOW()),
(2, 'compliance@financia.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyE3HOaVQcLG', 'María García', 'manager', 'Compliance', NOW()),
(3, 'legal@financia.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyE3HOaVQcLG', 'Juan Pérez', 'analyst', 'Legal', NOW()),
(4, 'finance@financia.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyE3HOaVQcLG', 'Ana Martínez', 'analyst', 'Finance', NOW()),
(5, 'user@financia.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyE3HOaVQcLG', 'Carlos López', 'user', 'Operations', NOW());

-- Password para todos: DemoPass123!

-- ============================================
-- 2. LISTAS DE SANCIONES (Simuladas)
-- ============================================

-- Personas en listas de sanciones
INSERT INTO sanctions_list (name, entity_type, source, country, program, added_date) VALUES
('Vladimir Petrov', 'PERSON', 'OFAC', 'Russia', 'Ukraine-Related Sanctions', '2022-03-01'),
('Ali Hassan', 'PERSON', 'EU_SANCTIONS', 'Syria', 'Syrian Regime Sanctions', '2020-06-15'),
('Kim Jong-un', 'PERSON', 'OFAC', 'North Korea', 'North Korea Sanctions Program', '2017-09-21'),
('Bashar Al-Assad', 'PERSON', 'EU_SANCTIONS', 'Syria', 'Syrian Regime Sanctions', '2011-05-23');

-- Empresas en listas de sanciones
INSERT INTO sanctions_list (name, entity_type, source, country, program, added_date) VALUES
('Rosneft Oil Company', 'COMPANY', 'OFAC', 'Russia', 'Ukraine-Related Sanctions', '2022-02-24'),
('Gazprom Bank', 'COMPANY', 'EU_SANCTIONS', 'Russia', 'Sectoral Sanctions', '2022-03-15'),
('Bank of Pyongyang', 'COMPANY', 'OFAC', 'North Korea', 'North Korea Sanctions Program', '2018-11-01'),
('Syrian Petroleum Company', 'COMPANY', 'EU_SANCTIONS', 'Syria', 'Syrian Oil Sanctions', '2012-03-01');

-- ============================================
-- 3. DOCUMENTOS DE DEMO
-- ============================================

-- Contrato LIMPIO (sin problemas)
INSERT INTO documents (
    id, filename, file_path, file_size, mime_type, file_hash,
    uploaded_by, status, classification, classification_confidence,
    metadata_, uploaded_at
) VALUES (
    gen_random_uuid(),
    'contrato_proveedor_acme_2024.pdf',
    'demo/contracts/acme.pdf',
    2458624,
    'application/pdf',
    'abc123def456',
    1,
    'COMPLETED',
    'CONTRACT',
    0.95,
    '{"category": "contracts", "validation_completed": true}',
    NOW() - INTERVAL '5 days'
);

-- Contrato con ENTIDAD FLAGGED
INSERT INTO documents (
    id, filename, file_path, file_size, mime_type, file_hash,
    uploaded_by, status, classification, classification_confidence,
    metadata_, uploaded_at
) VALUES (
    gen_random_uuid(),
    'contrato_suministro_rosneft_2024.pdf',
    'demo/contracts/rosneft.pdf',
    3145728,
    'application/pdf',
    'def456ghi789',
    2,
    'COMPLETED',
    'CONTRACT',
    0.92,
    '{"category": "contracts", "validation_completed": true, "flagged": true}',
    NOW() - INTERVAL '2 days'
);

-- Factura LIMPIA
INSERT INTO documents (
    id, filename, file_path, file_size, mime_type, file_hash,
    uploaded_by, status, classification, classification_confidence,
    metadata_, uploaded_at
) VALUES (
    gen_random_uuid(),
    'factura_microsoft_042024.pdf',
    'demo/invoices/microsoft.pdf',
    524288,
    'application/pdf',
    'ghi789jkl012',
    4,
    'COMPLETED',
    'INVOICE',
    0.98,
    '{"category": "invoices", "validation_completed": true}',
    NOW() - INTERVAL '10 days'
);

-- Informe con RIESGO ALTO
INSERT INTO documents (
    id, filename, file_path, file_size, mime_type, file_hash,
    uploaded_by, status, classification, classification_confidence,
    metadata_, uploaded_at
) VALUES (
    gen_random_uuid(),
    'informe_auditoria_compliance_q1_2024.pdf',
    'demo/reports/audit.pdf',
    5242880,
    'application/pdf',
    'jkl012mno345',
    2,
    'COMPLETED',
    'REPORT',
    0.89,
    '{"category": "reports", "validation_completed": true, "risk_level": "HIGH"}',
    NOW() - INTERVAL '15 days'
);

-- Contrato EN PROCESO
INSERT INTO documents (
    id, filename, file_path, file_size, mime_type, file_hash,
    uploaded_by, status, classification, classification_confidence,
    metadata_, uploaded_at
) VALUES (
    gen_random_uuid(),
    'contrato_servicios_techcorp_2024.pdf',
    'demo/contracts/techcorp.pdf',
    1835008,
    'application/pdf',
    'mno345pqr678',
    3,
    'PROCESSING',
    NULL,
    NULL,
    '{"category": "contracts"}',
    NOW() - INTERVAL '1 hour'
);

-- ============================================
-- 4. RESULTADOS DE VALIDACIÓN
-- ============================================

-- Validación LIMPIA (Acme Corp)
INSERT INTO validation_results (
    document_id,
    entity_name,
    entity_type,
    source,
    confidence,
    is_flagged,
    match_details,
    created_at
) VALUES (
    (SELECT id FROM documents WHERE filename = 'contrato_proveedor_acme_2024.pdf'),
    'Acme Corporation',
    'COMPANY',
    'OFAC',
    0.0,
    false,
    '{"checked": true, "no_match": true}',
    NOW() - INTERVAL '5 days'
);

-- Validación FLAGGED (Rosneft)
INSERT INTO validation_results (
    document_id,
    entity_name,
    entity_type,
    source,
    confidence,
    is_flagged,
    match_details,
    created_at
) VALUES (
    (SELECT id FROM documents WHERE filename = 'contrato_suministro_rosneft_2024.pdf'),
    'Rosneft Oil Company',
    'COMPANY',
    'OFAC',
    0.96,
    true,
    '{"matched": true, "list_entry": "Rosneft Oil Company", "program": "Ukraine-Related Sanctions", "country": "Russia"}',
    NOW() - INTERVAL '2 days'
);

-- Validación LIMPIA (Microsoft)
INSERT INTO validation_results (
    document_id,
    entity_name,
    entity_type,
    source,
    confidence,
    is_flagged,
    match_details,
    created_at
) VALUES (
    (SELECT id FROM documents WHERE filename = 'factura_microsoft_042024.pdf'),
    'Microsoft Corporation',
    'COMPANY',
    'OFAC',
    0.0,
    false,
    '{"checked": true, "no_match": true}',
    NOW() - INTERVAL '10 days'
);

-- ============================================
-- 5. CHUNKS DE DOCUMENTOS (para búsqueda)
-- ============================================

-- Chunks del contrato Acme
INSERT INTO document_chunks (
    document_id,
    chunk_index,
    content,
    metadata_
) VALUES (
    (SELECT id FROM documents WHERE filename = 'contrato_proveedor_acme_2024.pdf'),
    0,
    'CONTRATO DE PRESTACIÓN DE SERVICIOS. Entre Acme Corporation (en adelante "EL PROVEEDOR") y FinancIA Corp (en adelante "EL CLIENTE")...',
    '{"entities": [{"text": "Acme Corporation", "type": "ORGANIZATION"}, {"text": "FinancIA Corp", "type": "ORGANIZATION"}], "page": 1}'
);

-- Chunks del contrato Rosneft (FLAGGED)
INSERT INTO document_chunks (
    document_id,
    chunk_index,
    content,
    metadata_
) VALUES (
    (SELECT id FROM documents WHERE filename = 'contrato_suministro_rosneft_2024.pdf'),
    0,
    'ACUERDO DE SUMINISTRO DE PETRÓLEO. Entre Rosneft Oil Company (en adelante "EL PROVEEDOR") ubicada en Moscú, Rusia...',
    '{"entities": [{"text": "Rosneft Oil Company", "type": "ORGANIZATION"}, {"text": "Moscú", "type": "LOCATION"}, {"text": "Rusia", "type": "LOCATION"}], "page": 1}'
);

-- ============================================
-- 6. DATOS HISTÓRICOS PARA DASHBOARD
-- ============================================

-- Generar validaciones de los últimos 30 días
DO $$
DECLARE
    i INTEGER;
    doc_id UUID;
    entity_names TEXT[] := ARRAY[
        'ABC Corporation',
        'XYZ Industries',
        'Global Trading Ltd',
        'Tech Solutions Inc',
        'Green Energy Corp',
        'Finance Partners SA'
    ];
    entity_name TEXT;
BEGIN
    FOR i IN 1..200 LOOP
        -- Documento aleatorio
        doc_id := (SELECT id FROM documents ORDER BY RANDOM() LIMIT 1);
        
        -- Entidad aleatoria
        entity_name := entity_names[1 + floor(random() * array_length(entity_names, 1))];
        
        -- 95% no flagged, 5% flagged
        INSERT INTO validation_results (
            document_id,
            entity_name,
            entity_type,
            source,
            confidence,
            is_flagged,
            match_details,
            created_at
        ) VALUES (
            doc_id,
            entity_name,
            CASE WHEN random() > 0.5 THEN 'COMPANY' ELSE 'PERSON' END,
            CASE 
                WHEN random() > 0.66 THEN 'OFAC'
                WHEN random() > 0.33 THEN 'EU_SANCTIONS'
                ELSE 'WORLD_BANK'
            END,
            CASE WHEN random() > 0.95 THEN 0.85 + (random() * 0.15) ELSE random() * 0.3 END,
            random() > 0.95,  -- 5% flagged
            '{"checked": true}',
            NOW() - (random() * INTERVAL '30 days')
        );
    END LOOP;
END $$;

-- ============================================
-- 7. REFRESH VISTA MATERIALIZADA
-- ============================================

REFRESH MATERIALIZED VIEW validation_stats_cache;

-- ============================================
-- 8. ANÁLISIS Y VERIFICACIÓN
-- ============================================

-- Estadísticas de demo
SELECT 
    'Total usuarios' AS metric,
    COUNT(*)::TEXT AS value
FROM users
UNION ALL
SELECT 
    'Total documentos',
    COUNT(*)::TEXT
FROM documents
UNION ALL
SELECT 
    'Total validaciones',
    COUNT(*)::TEXT
FROM validation_results
UNION ALL
SELECT 
    'Entidades flagged',
    COUNT(*)::TEXT
FROM validation_results
WHERE is_flagged = true
UNION ALL
SELECT 
    'Entidades en listas',
    COUNT(*)::TEXT
FROM sanctions_list;

-- ============================================
-- NOTAS
-- ============================================

-- Usuarios de demo:
-- - admin@financia.com (Admin)
-- - compliance@financia.com (Compliance Manager)
-- - legal@financia.com (Legal Analyst)
-- - finance@financia.com (Finance Analyst)
-- - user@financia.com (Regular User)
-- 
-- Password para todos: DemoPass123!
--
-- Escenarios:
-- 1. Documento limpio: contrato_proveedor_acme_2024.pdf
-- 2. Documento flagged: contrato_suministro_rosneft_2024.pdf
-- 3. Documento en proceso: contrato_servicios_techcorp_2024.pdf
-- 4. Dashboard con 200+ validaciones históricas
--
-- Para ejecutar:
-- psql -U postgres -d financia_dms -f demo_data.sql
