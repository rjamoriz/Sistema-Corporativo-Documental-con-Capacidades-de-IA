-- FinancIA 2030 - Database Initialization
-- PostgreSQL 15 with pgvector extension

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable uuid extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas if needed (optional, using public for now)
-- CREATE SCHEMA IF NOT EXISTS financia;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE financia_db TO financia;

-- Set timezone
SET timezone = 'UTC';

-- Create indexes will be handled by SQLAlchemy migrations

COMMENT ON DATABASE financia_db IS 'FinancIA 2030 - Sistema Corporativo Documental con IA';
