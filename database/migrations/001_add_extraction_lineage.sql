-- ============================================================================
-- Migration: Add Extraction Lineage Tracking System
-- Version: 001
-- Date: 2025-12-17
-- Description: Creates extraction_lineage table and related structures for
--              tracking data provenance from document extraction to dashboard
-- ============================================================================

-- =============================================================================
-- ROI Models Table (if not exists - needed for lineage)
-- =============================================================================

CREATE TABLE IF NOT EXISTS roi_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    model_type VARCHAR(50) NOT NULL,  -- B1-B13 classification
    name VARCHAR(255) NOT NULL,
    description TEXT,
    financial_metrics JSONB,
    clinical_outcomes JSONB,
    source_extractions UUID[],  -- Array of extraction_ids
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_roi_models_client_id ON roi_models(client_id);
CREATE INDEX IF NOT EXISTS idx_roi_models_type ON roi_models(model_type);
CREATE INDEX IF NOT EXISTS idx_roi_models_source_extractions ON roi_models USING GIN(source_extractions);

-- Trigger for updated_at
CREATE TRIGGER update_roi_models_updated_at
    BEFORE UPDATE ON roi_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Extraction Lineage Table (MVP - 10 mandatory fields)
-- =============================================================================

CREATE TABLE extraction_lineage (
    -- Core Identity (2 fields)
    extraction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    extraction_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Source Tracking (2 fields)
    source_document_url TEXT NOT NULL,
    source_document_hash VARCHAR(64) NOT NULL,  -- SHA256

    -- Extraction Context (2 fields)
    extraction_agent VARCHAR(100) NOT NULL,
    extraction_model VARCHAR(100) NOT NULL,

    -- Verification Results (2 fields)
    verification_status VARCHAR(20) NOT NULL
        CHECK (verification_status IN ('verified', 'unverified', 'flagged')),
    verification_issues TEXT[] DEFAULT '{}',

    -- Usage Tracking (2 fields)
    used_in_roi_models UUID[] DEFAULT '{}',
    used_in_dashboards UUID[] DEFAULT '{}',

    -- Optional Phase 2 Fields (Quality Metrics)
    text_quality_score FLOAT,
    extraction_confidence_initial FLOAT,
    extraction_confidence_final FLOAT,
    extraction_duration_seconds FLOAT,
    prompt_template_version VARCHAR(20),
    extraction_method VARCHAR(50),  -- "PyPDF2" | "python-docx" | "Claude_Vision"

    -- Optional Phase 3 Fields (Advanced Tracking)
    validation_layers_passed TEXT[] DEFAULT '{}',
    retry_attempts INTEGER DEFAULT 1,
    last_accessed TIMESTAMP,

    -- Housekeeping
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- Indexes for Common Queries
-- =============================================================================

-- Find extractions from specific document
CREATE INDEX idx_lineage_document_hash ON extraction_lineage(source_document_hash);

-- Time-based queries
CREATE INDEX idx_lineage_timestamp ON extraction_lineage(extraction_timestamp DESC);

-- Filter by verification status
CREATE INDEX idx_lineage_verification ON extraction_lineage(verification_status);

-- Find extractions used in ROI models (GIN index for array search)
CREATE INDEX idx_lineage_roi_models ON extraction_lineage USING GIN(used_in_roi_models);

-- Find extractions used in dashboards
CREATE INDEX idx_lineage_dashboards ON extraction_lineage USING GIN(used_in_dashboards);

-- Find extractions by source document URL (for re-extraction scenarios)
CREATE INDEX idx_lineage_document_url ON extraction_lineage(source_document_url);

-- Composite index for agent performance analysis
CREATE INDEX idx_lineage_agent_verification ON extraction_lineage(extraction_agent, verification_status);

-- =============================================================================
-- Trigger for updated_at timestamp
-- =============================================================================

CREATE TRIGGER update_extraction_lineage_updated_at
    BEFORE UPDATE ON extraction_lineage
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Helper Functions
-- =============================================================================

-- Function to link extraction to ROI model
CREATE OR REPLACE FUNCTION link_extraction_to_roi_model(
    p_extraction_id UUID,
    p_roi_model_id UUID
)
RETURNS VOID AS $$
BEGIN
    UPDATE extraction_lineage
    SET
        used_in_roi_models = array_append(used_in_roi_models, p_roi_model_id),
        updated_at = NOW()
    WHERE extraction_id = p_extraction_id
      AND NOT (p_roi_model_id = ANY(used_in_roi_models));  -- Avoid duplicates
END;
$$ LANGUAGE plpgsql;

-- Function to link ROI model to dashboard
CREATE OR REPLACE FUNCTION link_roi_model_to_dashboard(
    p_roi_model_id UUID,
    p_dashboard_id UUID
)
RETURNS VOID AS $$
BEGIN
    UPDATE extraction_lineage
    SET
        used_in_dashboards = array_append(used_in_dashboards, p_dashboard_id),
        updated_at = NOW()
    WHERE p_roi_model_id = ANY(used_in_roi_models)
      AND NOT (p_dashboard_id = ANY(used_in_dashboards));  -- Avoid duplicates
END;
$$ LANGUAGE plpgsql;

-- Function to find all affected dashboards for a document
CREATE OR REPLACE FUNCTION find_affected_dashboards(
    p_document_hash VARCHAR(64)
)
RETURNS TABLE (
    extraction_id UUID,
    roi_model_id UUID,
    dashboard_id UUID
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        el.extraction_id,
        unnest(el.used_in_roi_models) AS roi_model_id,
        unnest(el.used_in_dashboards) AS dashboard_id
    FROM extraction_lineage el
    WHERE el.source_document_hash = p_document_hash;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Comments (Documentation)
-- =============================================================================

COMMENT ON TABLE extraction_lineage IS 'Tracks complete data provenance from document extraction to dashboard usage';
COMMENT ON COLUMN extraction_lineage.extraction_id IS 'Unique identifier linking to extracted data records';
COMMENT ON COLUMN extraction_lineage.source_document_hash IS 'SHA256 hash for document integrity verification';
COMMENT ON COLUMN extraction_lineage.verification_status IS 'verified: passed Layer 5 checks, unverified: skipped verification, flagged: manual review needed';
COMMENT ON COLUMN extraction_lineage.used_in_roi_models IS 'Array of ROI Model IDs that use this extraction';
COMMENT ON COLUMN extraction_lineage.used_in_dashboards IS 'Array of Dashboard IDs that display this data';

-- =============================================================================
-- Verification
-- =============================================================================

-- Verify table exists
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename = 'extraction_lineage'
    ) THEN
        RAISE NOTICE 'Migration successful: extraction_lineage table created';
    ELSE
        RAISE EXCEPTION 'Migration failed: extraction_lineage table not found';
    END IF;
END $$;
