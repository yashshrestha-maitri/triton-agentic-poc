-- Migration: Add Prospect Dashboard Templates and Data Schemas
-- Date: 2025-11-27
-- Description: Adds tables for prospect dashboard templates with data requirements,
--              data schemas for validation, and updates prospect_dashboard_data table

-- =============================================================================
-- Create New Tables
-- =============================================================================

-- Prospect dashboard templates table (templates with data requirements)
CREATE TABLE IF NOT EXISTS prospect_dashboard_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    target_audience VARCHAR(100) NOT NULL,
    visual_style JSONB NOT NULL,
    widgets JSONB NOT NULL,  -- Array of DashboardWidgetNew with data_requirements
    metadata JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_prospect_template_category CHECK (category IN (
        'roi-focused', 'clinical-outcomes', 'operational-efficiency',
        'competitive-positioning', 'comprehensive'
    )),
    CONSTRAINT chk_prospect_template_status CHECK (status IN (
        'draft', 'approved', 'archived', 'deprecated'
    ))
);

CREATE INDEX IF NOT EXISTS idx_pdt_client_id ON prospect_dashboard_templates(client_id);
CREATE INDEX IF NOT EXISTS idx_pdt_category ON prospect_dashboard_templates(category);
CREATE INDEX IF NOT EXISTS idx_pdt_status ON prospect_dashboard_templates(status);
CREATE INDEX IF NOT EXISTS idx_pdt_widgets_gin ON prospect_dashboard_templates USING GIN(widgets);

-- Prospect data schemas table (defines available data for validation)
CREATE TABLE IF NOT EXISTS prospect_data_schemas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    schema_name VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    fields JSONB NOT NULL,  -- Array of field definitions
    available_metrics JSONB,  -- Array of pre-calculated metrics
    time_fields JSONB,  -- Array of time field names
    dimension_fields JSONB,  -- Array of dimension field names
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meta_data JSONB,
    CONSTRAINT uq_client_schema UNIQUE(client_id, schema_name)
);

CREATE INDEX IF NOT EXISTS idx_pds_client_id ON prospect_data_schemas(client_id);
CREATE INDEX IF NOT EXISTS idx_pds_active ON prospect_data_schemas(is_active);

-- =============================================================================
-- Update Existing Tables
-- =============================================================================

-- Add new columns to prospect_dashboard_data
ALTER TABLE prospect_dashboard_data
    ADD COLUMN IF NOT EXISTS prospect_template_id UUID REFERENCES prospect_dashboard_templates(id) ON DELETE CASCADE,
    ADD COLUMN IF NOT EXISTS validation_result JSONB,
    ADD COLUMN IF NOT EXISTS generated_by VARCHAR(255),
    ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'generating';

-- Make template_id nullable (can use either template_id or prospect_template_id)
ALTER TABLE prospect_dashboard_data
    ALTER COLUMN template_id DROP NOT NULL;

-- Remove old unique constraint if it exists
ALTER TABLE prospect_dashboard_data
    DROP CONSTRAINT IF EXISTS prospect_dashboard_data_prospect_id_template_id_key;

-- Add new constraints
ALTER TABLE prospect_dashboard_data
    ADD CONSTRAINT chk_one_template_ref CHECK (
        (template_id IS NOT NULL AND prospect_template_id IS NULL) OR
        (template_id IS NULL AND prospect_template_id IS NOT NULL)
    );

ALTER TABLE prospect_dashboard_data
    ADD CONSTRAINT chk_prospect_data_status CHECK (status IN (
        'generating', 'ready', 'stale', 'error'
    ));

-- Add new indexes
CREATE INDEX IF NOT EXISTS idx_prospect_dashboard_lookup2
ON prospect_dashboard_data(prospect_id, prospect_template_id);

-- =============================================================================
-- Add Triggers
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_prospect_dashboard_templates_updated_at') THEN
        CREATE TRIGGER update_prospect_dashboard_templates_updated_at
            BEFORE UPDATE ON prospect_dashboard_templates
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_prospect_data_schemas_updated_at') THEN
        CREATE TRIGGER update_prospect_data_schemas_updated_at
            BEFORE UPDATE ON prospect_data_schemas
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END$$;

-- =============================================================================
-- Insert Sample Data
-- =============================================================================

-- Insert sample prospect data schema
INSERT INTO prospect_data_schemas (client_id, schema_name, table_name, fields, available_metrics, time_fields, dimension_fields, meta_data)
SELECT
    c.id,
    'roi_analysis_schema',
    'roi_analysis_data',
    '[
        {"name": "member_id", "type": "string", "description": "Member identifier"},
        {"name": "scenario", "type": "string", "description": "Scenario type (conservative, moderate, optimistic)"},
        {"name": "total_savings", "type": "currency", "description": "Total savings amount"},
        {"name": "program_costs", "type": "currency", "description": "Program costs"},
        {"name": "savings_conservative", "type": "currency", "description": "Conservative savings estimate"},
        {"name": "savings_moderate", "type": "currency", "description": "Moderate savings estimate"},
        {"name": "savings_optimistic", "type": "currency", "description": "Optimistic savings estimate"},
        {"name": "roi_multiplier", "type": "number", "description": "ROI multiplier"},
        {"name": "date", "type": "date", "description": "Analysis date"}
    ]'::jsonb,
    '["roi_conservative", "roi_moderate", "roi_optimistic", "savings_per_member"]'::jsonb,
    '["date", "created_at", "updated_at"]'::jsonb,
    '["scenario", "member_id", "analysis_type"]'::jsonb,
    '{"version": "1.0", "source": "analytics_team"}'::jsonb
FROM clients c
WHERE c.name = 'HealthTech Solutions'
ON CONFLICT (client_id, schema_name) DO NOTHING;

-- Migration complete
COMMENT ON TABLE prospect_dashboard_templates IS 'Dashboard templates with data requirements and analytics questions for prospect dashboards';
COMMENT ON TABLE prospect_data_schemas IS 'Data schema definitions for validating template data requirements against available prospect data';
COMMENT ON COLUMN prospect_dashboard_data.prospect_template_id IS 'Reference to prospect dashboard template (mutually exclusive with template_id)';
COMMENT ON COLUMN prospect_dashboard_data.validation_result IS 'Validation result from checking template data requirements';
COMMENT ON COLUMN prospect_dashboard_data.status IS 'Data generation status: generating, ready, stale, error';
