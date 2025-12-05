-- Triton Agentic Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- Core Client and Value Proposition Tables
-- =============================================================================

-- Clients table (organizations using the dashboard system)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meta_data JSONB,
    CONSTRAINT chk_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
);

CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_industry ON clients(industry);

-- Value propositions table (stores client value props for template generation)
CREATE TABLE value_propositions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    meta_data JSONB,
    CONSTRAINT chk_content_not_empty CHECK (LENGTH(TRIM(content)) > 0)
);

CREATE INDEX idx_vp_client_id ON value_propositions(client_id);
CREATE INDEX idx_vp_active ON value_propositions(client_id, is_active);

-- Prospects table (end-users/organizations viewing dashboards)
CREATE TABLE prospects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meta_data JSONB,
    CONSTRAINT chk_prospect_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
);

CREATE INDEX idx_prospects_client_id ON prospects(client_id);
CREATE INDEX idx_prospects_email ON prospects(email);

-- =============================================================================
-- Template Generation Tables
-- =============================================================================

-- Generation jobs table (tracks async template generation tasks)
CREATE TABLE generation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    value_proposition_id UUID REFERENCES value_propositions(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    celery_task_id VARCHAR(255) UNIQUE,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    generation_duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meta_data JSONB,
    CONSTRAINT chk_job_status CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'cancelled'
    ))
);

CREATE INDEX idx_jobs_client_id ON generation_jobs(client_id);
CREATE INDEX idx_jobs_status ON generation_jobs(status);
CREATE INDEX idx_jobs_celery_task_id ON generation_jobs(celery_task_id);
CREATE INDEX idx_jobs_created_at ON generation_jobs(created_at DESC);

-- Dashboard templates table (stores generated template configurations)
CREATE TABLE dashboard_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES generation_jobs(id) ON DELETE SET NULL,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    target_audience VARCHAR(100) NOT NULL,
    visual_style JSONB NOT NULL,
    widgets JSONB NOT NULL,  -- Array of WidgetConfiguration
    meta_data JSONB,
    status VARCHAR(50) DEFAULT 'generated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_category CHECK (category IN (
        'roi-focused', 'clinical-outcomes', 'operational-efficiency',
        'competitive-positioning', 'comprehensive'
    )),
    CONSTRAINT chk_template_status CHECK (status IN ('generated', 'approved', 'removed'))
);

CREATE INDEX idx_dt_client_id ON dashboard_templates(client_id);
CREATE INDEX idx_dt_job_id ON dashboard_templates(job_id);
CREATE INDEX idx_dt_category ON dashboard_templates(category);
CREATE INDEX idx_dt_status ON dashboard_templates(status);
CREATE INDEX idx_dt_widgets_gin ON dashboard_templates USING GIN(widgets);

-- Partial index for active templates
CREATE INDEX idx_active_templates
ON dashboard_templates(client_id, category)
WHERE status = 'approved';

-- Prospect dashboard templates table (templates with data requirements)
CREATE TABLE prospect_dashboard_templates (
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

CREATE INDEX idx_pdt_client_id ON prospect_dashboard_templates(client_id);
CREATE INDEX idx_pdt_category ON prospect_dashboard_templates(category);
CREATE INDEX idx_pdt_status ON prospect_dashboard_templates(status);
CREATE INDEX idx_pdt_widgets_gin ON prospect_dashboard_templates USING GIN(widgets);

-- Prospect data schemas table (defines available data for validation)
CREATE TABLE prospect_data_schemas (
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
    UNIQUE(client_id, schema_name)
);

CREATE INDEX idx_pds_client_id ON prospect_data_schemas(client_id);
CREATE INDEX idx_pds_active ON prospect_data_schemas(is_active);

-- Prospect dashboard data table (stores generated data for specific prospects)
CREATE TABLE prospect_dashboard_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    template_id UUID REFERENCES dashboard_templates(id) ON DELETE CASCADE,
    prospect_template_id UUID REFERENCES prospect_dashboard_templates(id) ON DELETE CASCADE,
    dashboard_data JSONB NOT NULL,  -- Complete widget data
    validation_result JSONB,  -- DataValidationResult
    generated_at TIMESTAMP NOT NULL,
    generation_duration_ms INTEGER,
    generated_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'generating',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_one_template_ref CHECK (
        (template_id IS NOT NULL AND prospect_template_id IS NULL) OR
        (template_id IS NULL AND prospect_template_id IS NOT NULL)
    ),
    CONSTRAINT chk_prospect_data_status CHECK (status IN (
        'generating', 'ready', 'stale', 'error'
    ))
);

CREATE INDEX idx_prospect_dashboard_lookup
ON prospect_dashboard_data(prospect_id, template_id);
CREATE INDEX idx_prospect_dashboard_lookup2
ON prospect_dashboard_data(prospect_id, prospect_template_id);
CREATE INDEX idx_prospect_dashboard_jsonb
ON prospect_dashboard_data USING GIN(dashboard_data);

-- =============================================================================
-- Audit and Logging Tables
-- =============================================================================

-- Agent execution logs (for monitoring and debugging)
CREATE TABLE agent_execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES generation_jobs(id) ON DELETE CASCADE,
    agent_name VARCHAR(255) NOT NULL,
    execution_time_ms INTEGER,
    token_usage JSONB,
    error_count INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    success BOOLEAN NOT NULL,
    error_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meta_data JSONB
);

CREATE INDEX idx_agent_logs_job_id ON agent_execution_logs(job_id);
CREATE INDEX idx_agent_logs_created_at ON agent_execution_logs(created_at DESC);
CREATE INDEX idx_agent_logs_success ON agent_execution_logs(success);

-- =============================================================================
-- Triggers for updated_at timestamps
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all tables with updated_at
CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_value_propositions_updated_at
    BEFORE UPDATE ON value_propositions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prospects_updated_at
    BEFORE UPDATE ON prospects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_generation_jobs_updated_at
    BEFORE UPDATE ON generation_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dashboard_templates_updated_at
    BEFORE UPDATE ON dashboard_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prospect_dashboard_data_updated_at
    BEFORE UPDATE ON prospect_dashboard_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prospect_dashboard_templates_updated_at
    BEFORE UPDATE ON prospect_dashboard_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prospect_data_schemas_updated_at
    BEFORE UPDATE ON prospect_data_schemas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Sample Data (for development)
-- =============================================================================

-- Insert sample client
INSERT INTO clients (id, name, industry, metadata) VALUES
(gen_random_uuid(), 'HealthTech Solutions', 'Healthcare Technology',
 '{"company_size": "500-1000", "region": "North America"}');

-- Insert sample value proposition
INSERT INTO value_propositions (client_id, content, metadata)
SELECT id,
'Our AI-powered clinical decision support platform reduces diagnostic errors by 35% and improves patient outcomes through real-time evidence-based recommendations. We integrate seamlessly with existing EMR systems and provide actionable insights that save physicians 2 hours per day on administrative tasks.',
'{"use_case": "clinical_decision_support"}'
FROM clients WHERE name = 'HealthTech Solutions';
