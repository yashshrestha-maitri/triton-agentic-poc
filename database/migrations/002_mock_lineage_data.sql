-- ============================================================================
-- Mock Data: Complete Extraction Lineage Flow
-- Version: 002
-- Date: 2025-12-17
-- Description: Comprehensive mock data demonstrating full lineage tracking
--              from document → extraction → ROI model → dashboard
-- ============================================================================

-- =============================================================================
-- Step 1: Create Test Client and Prospect
-- =============================================================================

-- Insert test client
INSERT INTO clients (id, name, industry, meta_data)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'Acme Health Insurance',
    'Health Insurance',
    '{"company_size": "1000-5000", "region": "West Coast"}'
)
ON CONFLICT (id) DO NOTHING;

-- Insert test prospect
INSERT INTO prospects (id, client_id, name, organization, email)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    'Blue Shield of California',
    'Blue Shield',
    'procurement@blueshield.com'
)
ON CONFLICT (id) DO NOTHING;

-- =============================================================================
-- Step 2: Simulate Document Analysis - 3 Extractions from Single Document
-- =============================================================================

-- Extraction 1: ROI Metric (250% ROI over 18 months)
INSERT INTO extraction_lineage (
    extraction_id,
    extraction_timestamp,
    source_document_url,
    source_document_hash,
    extraction_agent,
    extraction_model,
    verification_status,
    verification_issues,
    used_in_roi_models,
    used_in_dashboards,
    text_quality_score,
    extraction_confidence_initial,
    extraction_confidence_final,
    extraction_duration_seconds,
    prompt_template_version,
    extraction_method,
    validation_layers_passed,
    retry_attempts
) VALUES (
    '33333333-3333-3333-3333-333333333333',
    NOW() - INTERVAL '2 hours',
    's3://triton-docs/clients/acme-health/roi_analysis_2025.pdf',
    'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2',
    'DocumentAnalysisAgent',
    'us.anthropic.claude-sonnet-4-20250514-v1:0',
    'verified',
    '{}',
    '{}',  -- Will be populated when ROI model uses this
    '{}',  -- Will be populated when dashboard displays this
    0.95,  -- High quality PDF
    0.92,  -- Initial confidence
    0.95,  -- Final confidence (after verification)
    12.5,  -- 12.5 seconds extraction time
    'v2.1',
    'PyPDF2',
    '{"json_extraction", "json_parsing", "pydantic_validation", "business_rules", "source_verification"}',
    1  -- Passed first attempt
);

-- Extraction 2: Clinical Outcome (HbA1c reduction)
INSERT INTO extraction_lineage (
    extraction_id,
    extraction_timestamp,
    source_document_url,
    source_document_hash,
    extraction_agent,
    extraction_model,
    verification_status,
    verification_issues,
    used_in_roi_models,
    used_in_dashboards,
    text_quality_score,
    extraction_confidence_initial,
    extraction_confidence_final,
    extraction_duration_seconds,
    prompt_template_version,
    extraction_method,
    validation_layers_passed,
    retry_attempts
) VALUES (
    '44444444-4444-4444-4444-444444444444',
    NOW() - INTERVAL '2 hours',
    's3://triton-docs/clients/acme-health/roi_analysis_2025.pdf',
    'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2',
    'DocumentAnalysisAgent',
    'us.anthropic.claude-sonnet-4-20250514-v1:0',
    'verified',
    '{}',
    '{}',
    '{}',
    0.95,
    0.88,
    0.90,
    12.5,
    'v2.1',
    'PyPDF2',
    '{"json_extraction", "json_parsing", "pydantic_validation", "business_rules", "source_verification"}',
    1
);

-- Extraction 3: Cost Savings Metric
INSERT INTO extraction_lineage (
    extraction_id,
    extraction_timestamp,
    source_document_url,
    source_document_hash,
    extraction_agent,
    extraction_model,
    verification_status,
    verification_issues,
    used_in_roi_models,
    used_in_dashboards,
    text_quality_score,
    extraction_confidence_initial,
    extraction_confidence_final,
    extraction_duration_seconds,
    prompt_template_version,
    extraction_method,
    validation_layers_passed,
    retry_attempts
) VALUES (
    '55555555-5555-5555-5555-555555555555',
    NOW() - INTERVAL '2 hours',
    's3://triton-docs/clients/acme-health/roi_analysis_2025.pdf',
    'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2',
    'DocumentAnalysisAgent',
    'us.anthropic.claude-sonnet-4-20250514-v1:0',
    'verified',
    '{}',
    '{}',
    '{}',
    0.95,
    0.90,
    0.93,
    12.5,
    'v2.1',
    'PyPDF2',
    '{"json_extraction", "json_parsing", "pydantic_validation", "business_rules", "source_verification"}',
    1
);

-- =============================================================================
-- Step 3: Web Search Extraction (Different Source)
-- =============================================================================

-- Extraction 4: Industry Benchmark from Web Search
INSERT INTO extraction_lineage (
    extraction_id,
    extraction_timestamp,
    source_document_url,
    source_document_hash,
    extraction_agent,
    extraction_model,
    verification_status,
    verification_issues,
    used_in_roi_models,
    used_in_dashboards,
    text_quality_score,
    extraction_confidence_initial,
    extraction_confidence_final,
    extraction_duration_seconds,
    prompt_template_version,
    extraction_method,
    validation_layers_passed,
    retry_attempts
) VALUES (
    '66666666-6666-6666-6666-666666666666',
    NOW() - INTERVAL '1 hour 30 minutes',
    'https://www.cms.gov/medicare/quality/2025-hedis-benchmarks',
    'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3',
    'WebSearchAgent',
    'us.anthropic.claude-sonnet-4-20250514-v1:0',
    'verified',
    '{}',
    '{}',
    '{}',
    NULL,  -- No text quality score for web content
    0.85,
    0.85,
    8.2,
    'v2.1',
    'web_scraping',
    '{"json_extraction", "json_parsing", "pydantic_validation", "business_rules", "source_verification"}',
    1
);

-- =============================================================================
-- Step 4: Create ROI Models Using Extractions
-- =============================================================================

-- ROI Model 1: Diabetes Management ROI (uses extractions 1, 2, 3)
INSERT INTO roi_models (
    id,
    client_id,
    model_type,
    name,
    description,
    financial_metrics,
    clinical_outcomes,
    source_extractions,
    metadata
) VALUES (
    '77777777-7777-7777-7777-777777777777',
    '11111111-1111-1111-1111-111111111111',
    'B3',
    'Diabetes Care Management ROI',
    'Comprehensive ROI model for diabetes intervention programs',
    '{
        "roi_percentage": "250%",
        "payback_period_months": 18,
        "annual_savings": "$1.2M per 10,000 members",
        "implementation_cost": "$500,000"
    }',
    '{
        "hba1c_reduction": "0.8% average reduction",
        "hospital_readmissions": "22% reduction in 30-day readmissions",
        "member_engagement": "68% active participation rate"
    }',
    ARRAY[
        '33333333-3333-3333-3333-333333333333'::UUID,
        '44444444-4444-4444-4444-444444444444'::UUID,
        '55555555-5555-5555-5555-555555555555'::UUID
    ],
    '{"calculation_date": "2025-12-17", "confidence": "high"}'
);

-- ROI Model 2: Preventive Care ROI (uses extraction 4 - web benchmark)
INSERT INTO roi_models (
    id,
    client_id,
    model_type,
    name,
    description,
    financial_metrics,
    clinical_outcomes,
    source_extractions,
    metadata
) VALUES (
    '88888888-8888-8888-8888-888888888888',
    '11111111-1111-1111-1111-111111111111',
    'B7',
    'Preventive Care Program ROI',
    'ROI model for preventive care and wellness programs',
    '{
        "roi_percentage": "185%",
        "payback_period_months": 24,
        "annual_savings": "$850K per 10,000 members"
    }',
    '{
        "preventive_visits": "35% increase in annual wellness visits",
        "early_detection": "42% increase in early disease detection"
    }',
    ARRAY['66666666-6666-6666-6666-666666666666'::UUID],
    '{"calculation_date": "2025-12-17", "includes_industry_benchmarks": true}'
);

-- =============================================================================
-- Step 5: Update Lineage with ROI Model Usage
-- =============================================================================

-- Link extraction 1 to ROI model 1
SELECT link_extraction_to_roi_model(
    '33333333-3333-3333-3333-333333333333',
    '77777777-7777-7777-7777-777777777777'
);

-- Link extraction 2 to ROI model 1
SELECT link_extraction_to_roi_model(
    '44444444-4444-4444-4444-444444444444',
    '77777777-7777-7777-7777-777777777777'
);

-- Link extraction 3 to ROI model 1
SELECT link_extraction_to_roi_model(
    '55555555-5555-5555-5555-555555555555',
    '77777777-7777-7777-7777-777777777777'
);

-- Link extraction 4 to ROI model 2
SELECT link_extraction_to_roi_model(
    '66666666-6666-6666-6666-666666666666',
    '88888888-8888-8888-8888-888888888888'
);

-- =============================================================================
-- Step 6: Create Dashboards Using ROI Models
-- =============================================================================

-- Dashboard 1: Executive Summary Dashboard (uses ROI Model 1)
INSERT INTO dashboard_templates (
    id,
    client_id,
    name,
    description,
    category,
    target_audience,
    visual_style,
    widgets,
    status,
    meta_data
) VALUES (
    '99999999-9999-9999-9999-999999999999',
    '11111111-1111-1111-1111-111111111111',
    'Diabetes Program Executive Dashboard',
    'High-level ROI metrics for diabetes management program',
    'roi-focused',
    'C-Suite Executives',
    '{"colorScheme": "professional", "layout": "grid"}',
    '[
        {
            "id": "widget-roi-1",
            "type": "metric",
            "title": "18-Month ROI",
            "config": {"value": "250%", "trend": "up"}
        },
        {
            "id": "widget-clinical-1",
            "type": "chart",
            "title": "HbA1c Improvement",
            "config": {"chartType": "line", "value": "0.8% reduction"}
        }
    ]',
    'approved',
    '{"roi_model_id": "77777777-7777-7777-7777-777777777777"}'
);

-- Dashboard 2: Clinical Outcomes Dashboard (uses ROI Model 1)
INSERT INTO dashboard_templates (
    id,
    client_id,
    name,
    description,
    category,
    target_audience,
    visual_style,
    widgets,
    status,
    meta_data
) VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '11111111-1111-1111-1111-111111111111',
    'Clinical Outcomes Dashboard',
    'Detailed clinical metrics and patient outcomes',
    'clinical-outcomes',
    'Medical Directors',
    '{"colorScheme": "clinical", "layout": "detailed"}',
    '[
        {
            "id": "widget-clinical-2",
            "type": "chart",
            "title": "Hospital Readmission Rates",
            "config": {"chartType": "bar", "value": "22% reduction"}
        }
    ]',
    'approved',
    '{"roi_model_id": "77777777-7777-7777-7777-777777777777"}'
);

-- Dashboard 3: Preventive Care Dashboard (uses ROI Model 2)
INSERT INTO dashboard_templates (
    id,
    client_id,
    name,
    description,
    category,
    target_audience,
    visual_style,
    widgets,
    status,
    meta_data
) VALUES (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    '11111111-1111-1111-1111-111111111111',
    'Preventive Care ROI Dashboard',
    'ROI analysis for preventive care programs',
    'roi-focused',
    'VP of Population Health',
    '{"colorScheme": "wellness", "layout": "executive"}',
    '[
        {
            "id": "widget-preventive-1",
            "type": "metric",
            "title": "24-Month ROI",
            "config": {"value": "185%"}
        }
    ]',
    'approved',
    '{"roi_model_id": "88888888-8888-8888-8888-888888888888"}'
);

-- =============================================================================
-- Step 7: Update Lineage with Dashboard Usage
-- =============================================================================

-- Link ROI Model 1 extractions to Dashboard 1
SELECT link_roi_model_to_dashboard(
    '77777777-7777-7777-7777-777777777777',
    '99999999-9999-9999-9999-999999999999'
);

-- Link ROI Model 1 extractions to Dashboard 2
SELECT link_roi_model_to_dashboard(
    '77777777-7777-7777-7777-777777777777',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
);

-- Link ROI Model 2 extractions to Dashboard 3
SELECT link_roi_model_to_dashboard(
    '88888888-8888-8888-8888-888888888888',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
);

-- =============================================================================
-- Step 8: Additional Scenario - Flagged Extraction (Manual Review)
-- =============================================================================

-- Extraction 5: Low confidence extraction requiring review
INSERT INTO extraction_lineage (
    extraction_id,
    extraction_timestamp,
    source_document_url,
    source_document_hash,
    extraction_agent,
    extraction_model,
    verification_status,
    verification_issues,
    used_in_roi_models,
    used_in_dashboards,
    text_quality_score,
    extraction_confidence_initial,
    extraction_confidence_final,
    extraction_duration_seconds,
    prompt_template_version,
    extraction_method,
    validation_layers_passed,
    retry_attempts
) VALUES (
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    NOW() - INTERVAL '30 minutes',
    's3://triton-docs/clients/acme-health/case_study_scan.pdf',
    'c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4',
    'DocumentAnalysisAgent',
    'us.anthropic.claude-sonnet-4-20250514-v1:0',
    'flagged',
    ARRAY[
        'Low text quality (scanned PDF): 0.62',
        'Page number verification failed',
        'Confidence below threshold: 0.65'
    ],
    '{}',
    '{}',
    0.62,  -- Low quality scanned PDF
    0.65,  -- Low confidence
    0.60,  -- Even lower after verification penalty
    18.3,  -- Longer extraction time due to OCR
    'v2.1',
    'Claude_Vision',  -- Used vision API due to low text quality
    '{"json_extraction", "json_parsing", "pydantic_validation", "business_rules"}',
    3  -- Required 3 attempts
);

-- =============================================================================
-- Verification Queries (for testing)
-- =============================================================================

-- Show complete lineage for extraction 1
-- SELECT * FROM extraction_lineage WHERE extraction_id = '33333333-3333-3333-3333-333333333333';

-- Find all extractions from the main document
-- SELECT * FROM extraction_lineage WHERE source_document_hash = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2';

-- Find all affected dashboards for the main document
-- SELECT * FROM find_affected_dashboards('a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2');

-- Show extractions that need manual review
-- SELECT * FROM extraction_lineage WHERE verification_status = 'flagged';

-- =============================================================================
-- Success Message
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Mock lineage data created successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Created:';
    RAISE NOTICE '  - 1 Client (Acme Health Insurance)';
    RAISE NOTICE '  - 1 Prospect (Blue Shield)';
    RAISE NOTICE '  - 5 Extractions (3 from PDF, 1 from web, 1 flagged)';
    RAISE NOTICE '  - 2 ROI Models (Diabetes, Preventive Care)';
    RAISE NOTICE '  - 3 Dashboards (Executive, Clinical, Preventive)';
    RAISE NOTICE '  - Complete lineage chain: Document → Extraction → ROI → Dashboard';
    RAISE NOTICE '========================================';
END $$;
