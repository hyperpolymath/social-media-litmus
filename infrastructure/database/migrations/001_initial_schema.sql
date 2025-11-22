-- Migration: 001_initial_schema
-- Description: Create initial database schema with TimescaleDB support
-- Author: Claude
-- Date: 2025-11-22

-- Apply the main schema
\i /docker-entrypoint-initdb.d/schema.sql

-- Migration metadata
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    checksum VARCHAR(64)
);

INSERT INTO schema_migrations (version, name, checksum) VALUES
    (1, 'initial_schema', 'initial');
