# Data Lineage API Guide - Complete Reference

**Date:** December 17, 2025
**Version:** 1.0
**Purpose:** Comprehensive guide for querying and understanding data lineage tracking

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Database Setup](#database-setup)
3. [How Data Lineage Works](#how-data-lineage-works)
4. [Complete Flow Example](#complete-flow-example)
5. [curl API Examples](#curl-api-examples)
6. [SQL Query Examples](#sql-query-examples)
7. [Common Use Cases](#common-use-cases)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Run Database Migrations

```bash
# Navigate to project root
cd /home/yashrajshres/triton-agentic

# Run schema migration
psql -U postgres -d triton_agentic -f database/migrations/001_add_extraction_lineage.sql

# Load mock data
psql -U postgres -d triton_agentic -f database/migrations/002_mock_lineage_data.sql
```

### 2. Verify Setup

```bash
# Check if extraction_lineage table exists
psql -U postgres -d triton_agentic -c "SELECT COUNT(*) FROM extraction_lineage;"

# Should return: 5 (5 mock extractions created)
```

### 3. Test API (once implemented)

```bash
# Get lineage for specific extraction
curl http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333
```

---

## Database Setup

### Prerequisites

- PostgreSQL 14+
- Existing Triton Agentic database
- `pgcrypto` extension enabled

### File Structure

```
triton-agentic/
├── database/
│   ├── schema.sql                    # Main schema
│   └── migrations/
│       ├── 001_add_extraction_lineage.sql   # Lineage table + functions
│       └── 002_mock_lineage_data.sql        # Test data
└── docs/
    └── operations/
        └── DATA_LINEAGE_API_GUIDE.md        # This file
```

### What Gets Created

#### Tables
- `extraction_lineage` - Main lineage tracking table
- `roi_models` - ROI models that use extractions

#### Indexes (7 total)
- `idx_lineage_document_hash` - Find extractions by document
- `idx_lineage_timestamp` - Time-based queries
- `idx_lineage_verification` - Filter by status
- `idx_lineage_roi_models` - Find by ROI model usage (GIN)
- `idx_lineage_dashboards` - Find by dashboard usage (GIN)
- `idx_lineage_document_url` - Find by source URL
- `idx_lineage_agent_verification` - Agent performance analysis

#### Functions (3 total)
- `link_extraction_to_roi_model()` - Link extraction to ROI model
- `link_roi_model_to_dashboard()` - Link ROI model to dashboard
- `find_affected_dashboards()` - Impact analysis query

---

## How Data Lineage Works

### The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: DOCUMENT UPLOADED                                       │
│ s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf     │
│ SHA256: a1b2c3d4...                                             │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: DOCUMENT ANALYSIS AGENT                                 │
│ - Extracts 3 data points from document                          │
│ - Creates lineage record for EACH extraction                    │
│ - Records: source_document_hash, agent, model, timestamp        │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
                ┌────────┴────────┐
                ↓                 ↓
┌───────────────────────┐  ┌───────────────────────┐
│ Extraction 1          │  │ Extraction 2          │
│ - ROI: 250%           │  │ - HbA1c: -0.8%        │
│ - extraction_id: 3333 │  │ - extraction_id: 4444 │
│ - used_in_roi: []     │  │ - used_in_roi: []     │
│ - used_in_dash: []    │  │ - used_in_dash: []    │
└───────────────────────┘  └───────────────────────┘
                ↓                 ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: ROI CLASSIFICATION AGENT                                │
│ - Analyzes extractions → Classifies as B3 (Diabetes Management) │
│ - No lineage changes                                             │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: ROI MODEL BUILDER AGENT                                 │
│ - Creates ROI Model (id: 7777)                                  │
│ - Uses extraction 3333 and 4444                                 │
│ - Updates lineage:                                              │
│   UPDATE extraction_lineage                                     │
│   SET used_in_roi_models = ['7777']                             │
│   WHERE extraction_id IN ('3333', '4444')                       │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
                Lineage now shows:
                Extraction 3333: used_in_roi_models = ['7777']
                Extraction 4444: used_in_roi_models = ['7777']
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: TEMPLATE GENERATOR AGENT                                │
│ - Creates Dashboard (id: 9999)                                  │
│ - Dashboard uses ROI Model 7777                                 │
│ - Updates lineage:                                              │
│   UPDATE extraction_lineage                                     │
│   SET used_in_dashboards = ['9999']                             │
│   WHERE '7777' = ANY(used_in_roi_models)                        │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
                Lineage now shows:
                Extraction 3333: used_in_roi_models = ['7777']
                                 used_in_dashboards = ['9999']
                Extraction 4444: used_in_roi_models = ['7777']
                                 used_in_dashboards = ['9999']
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ COMPLETE AUDIT TRAIL ESTABLISHED                                │
│                                                                  │
│ Document (SHA256: a1b2c3d4...)                                  │
│   ↓ extracted_by: DocumentAnalysisAgent                         │
│ Extraction 3333 (ROI: 250%)                                     │
│   ↓ used_in: ROI Model 7777                                     │
│ ROI Model 7777 (Diabetes Management)                            │
│   ↓ powers: Dashboard 9999                                      │
│ Dashboard 9999 (Executive Dashboard)                            │
│   ↓ viewed_by: Blue Shield prospect                             │
│                                                                  │
│ ✅ Complete traceability: Dashboard → Document                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Concepts

#### 1. When Lineage Records Are Created

**Created by DocumentAnalysisAgent (Step 2):**
- `extraction_id` - NEW UUID generated
- `source_document_url` - S3 path
- `source_document_hash` - SHA256 of document bytes
- `extraction_agent` - "DocumentAnalysisAgent"
- `extraction_model` - Model version used
- `verification_status` - "verified" | "unverified" | "flagged"
- `used_in_roi_models` - Empty array `[]`
- `used_in_dashboards` - Empty array `[]`

#### 2. When Lineage Records Are Updated

**Updated by ROI Model Builder (Step 4):**
```sql
-- Appends ROI model ID to used_in_roi_models array
UPDATE extraction_lineage
SET used_in_roi_models = array_append(used_in_roi_models, '7777'::UUID)
WHERE extraction_id = '3333'::UUID;
```

**Updated by Template Generator (Step 5):**
```sql
-- Appends dashboard ID to used_in_dashboards array
UPDATE extraction_lineage
SET used_in_dashboards = array_append(used_in_dashboards, '9999'::UUID)
WHERE '7777'::UUID = ANY(used_in_roi_models);
```

#### 3. Why SHA256 Hash?

**Purpose:** Detect if source document changes after extraction

**Example:**
```python
# Original extraction
document_hash = "a1b2c3d4..."  # Hash of roi_analysis_2025.pdf
extraction = extract_data(document)
lineage.source_document_hash = document_hash

# 3 months later: Client updates document
new_hash = "x9y8z7w6..."  # Different hash!

# Query lineage
if new_hash != lineage.source_document_hash:
    alert("⚠️ Source document changed! Extraction may be stale.")
```

---

## Complete Flow Example

### Scenario: Blue Shield Views Dashboard

**Question:** "Where did the 250% ROI number come from?"

#### Step 1: Identify Dashboard
```sql
SELECT id, name, meta_data->>'roi_model_id' AS roi_model_id
FROM dashboard_templates
WHERE id = '99999999-9999-9999-9999-999999999999';
```

**Result:**
```
id: 99999999-9999-9999-9999-999999999999
name: Diabetes Program Executive Dashboard
roi_model_id: 77777777-7777-7777-7777-777777777777
```

#### Step 2: Find Extractions Used by ROI Model
```sql
SELECT
    el.extraction_id,
    el.source_document_url,
    el.source_document_hash,
    el.extraction_timestamp,
    el.verification_status
FROM extraction_lineage el
WHERE '77777777-7777-7777-7777-777777777777'::UUID = ANY(el.used_in_roi_models);
```

**Result:**
```
extraction_id: 33333333-3333-3333-3333-333333333333
source_document_url: s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf
source_document_hash: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...
extraction_timestamp: 2025-12-17 14:30:45
verification_status: verified
```

#### Step 3: Show Complete Lineage
```sql
SELECT
    el.extraction_id,
    el.source_document_url,
    el.extraction_agent,
    el.extraction_model,
    el.verification_status,
    el.extraction_timestamp,
    unnest(el.used_in_roi_models) AS roi_model_id,
    unnest(el.used_in_dashboards) AS dashboard_id,
    dt.name AS dashboard_name
FROM extraction_lineage el
LEFT JOIN dashboard_templates dt ON dt.id = ANY(el.used_in_dashboards)
WHERE el.extraction_id = '33333333-3333-3333-3333-333333333333';
```

**Result:**
```
extraction_id: 33333333-3333-3333-3333-333333333333
source_document_url: s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf
extraction_agent: DocumentAnalysisAgent
extraction_model: us.anthropic.claude-sonnet-4-20250514-v1:0
verification_status: verified
extraction_timestamp: 2025-12-17 14:30:45
roi_model_id: 77777777-7777-7777-7777-777777777777
dashboard_id: 99999999-9999-9999-9999-999999999999
dashboard_name: Diabetes Program Executive Dashboard
```

**Answer:** "The 250% ROI came from `roi_analysis_2025.pdf` (page 3), extracted by DocumentAnalysisAgent on 2025-12-17 at 14:30:45, verified against source, used in Diabetes ROI Model 7777, displayed in Executive Dashboard 9999."

---

## curl API Examples

### Prerequisites

```bash
# Ensure API is running
uvicorn app:app --reload --port 8000

# Or
python app.py
```

### 1. Get Lineage for Specific Extraction

```bash
curl -X GET "http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response:**
```json
{
  "extraction_id": "33333333-3333-3333-3333-333333333333",
  "extraction_timestamp": "2025-12-17T14:30:45Z",
  "source_document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
  "source_document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
  "extraction_agent": "DocumentAnalysisAgent",
  "extraction_model": "us.anthropic.claude-sonnet-4-20250514-v1:0",
  "verification_status": "verified",
  "verification_issues": [],
  "used_in_roi_models": ["77777777-7777-7777-7777-777777777777"],
  "used_in_dashboards": [
    "99999999-9999-9999-9999-999999999999",
    "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
  ],
  "text_quality_score": 0.95,
  "extraction_confidence_final": 0.95,
  "extraction_duration_seconds": 12.5,
  "retry_attempts": 1
}
```

### 2. Find All Extractions from Document

```bash
curl -X GET "http://localhost:8000/lineage/document/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response:**
```json
{
  "document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
  "document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
  "total_extractions": 3,
  "extractions": [
    {
      "extraction_id": "33333333-3333-3333-3333-333333333333",
      "verification_status": "verified",
      "used_in_roi_models": ["77777777-7777-7777-7777-777777777777"],
      "used_in_dashboards": ["99999999-9999-9999-9999-999999999999"]
    },
    {
      "extraction_id": "44444444-4444-4444-4444-444444444444",
      "verification_status": "verified",
      "used_in_roi_models": ["77777777-7777-7777-7777-777777777777"],
      "used_in_dashboards": ["99999999-9999-9999-9999-999999999999"]
    },
    {
      "extraction_id": "55555555-5555-5555-5555-555555555555",
      "verification_status": "verified",
      "used_in_roi_models": ["77777777-7777-7777-7777-777777777777"],
      "used_in_dashboards": ["99999999-9999-9999-9999-999999999999"]
    }
  ]
}
```

### 3. Find Extractions Used in ROI Model

```bash
curl -X GET "http://localhost:8000/lineage/roi-model/77777777-7777-7777-7777-777777777777" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response:**
```json
{
  "roi_model_id": "77777777-7777-7777-7777-777777777777",
  "roi_model_name": "Diabetes Care Management ROI",
  "total_extractions": 3,
  "extractions": [
    {
      "extraction_id": "33333333-3333-3333-3333-333333333333",
      "source_document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
      "verification_status": "verified",
      "extraction_confidence": 0.95
    },
    {
      "extraction_id": "44444444-4444-4444-4444-444444444444",
      "source_document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
      "verification_status": "verified",
      "extraction_confidence": 0.90
    },
    {
      "extraction_id": "55555555-5555-5555-5555-555555555555",
      "source_document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
      "verification_status": "verified",
      "extraction_confidence": 0.93
    }
  ]
}
```

### 4. Find Extractions Used in Dashboard

```bash
curl -X GET "http://localhost:8000/lineage/dashboard/99999999-9999-9999-9999-999999999999" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response:**
```json
{
  "dashboard_id": "99999999-9999-9999-9999-999999999999",
  "dashboard_name": "Diabetes Program Executive Dashboard",
  "total_extractions": 3,
  "extractions": [
    {
      "extraction_id": "33333333-3333-3333-3333-333333333333",
      "source_document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
      "extraction_timestamp": "2025-12-17T14:30:45Z",
      "verification_status": "verified"
    }
  ],
  "source_documents": [
    {
      "document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
      "document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
      "extraction_count": 3
    }
  ]
}
```

### 5. Complete Audit Trail (Document → Dashboard)

```bash
curl -X GET "http://localhost:8000/lineage/audit-trail/33333333-3333-3333-3333-333333333333" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response:**
```json
{
  "extraction_id": "33333333-3333-3333-3333-333333333333",
  "audit_trail": {
    "step_1_document": {
      "source_document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
      "source_document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...",
      "extraction_timestamp": "2025-12-17T14:30:45Z"
    },
    "step_2_extraction": {
      "extraction_agent": "DocumentAnalysisAgent",
      "extraction_model": "us.anthropic.claude-sonnet-4-20250514-v1:0",
      "verification_status": "verified",
      "extraction_confidence": 0.95
    },
    "step_3_roi_models": [
      {
        "roi_model_id": "77777777-7777-7777-7777-777777777777",
        "roi_model_name": "Diabetes Care Management ROI",
        "roi_model_type": "B3"
      }
    ],
    "step_4_dashboards": [
      {
        "dashboard_id": "99999999-9999-9999-9999-999999999999",
        "dashboard_name": "Diabetes Program Executive Dashboard",
        "dashboard_category": "roi-focused"
      },
      {
        "dashboard_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "dashboard_name": "Clinical Outcomes Dashboard",
        "dashboard_category": "clinical-outcomes"
      }
    ]
  },
  "traceability": "Document → Extraction → ROI Model → 2 Dashboards"
}
```

### 6. Find Flagged Extractions (Needs Review)

```bash
curl -X GET "http://localhost:8000/lineage/flagged" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response:**
```json
{
  "total_flagged": 1,
  "extractions": [
    {
      "extraction_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
      "source_document_url": "s3://triton-docs/clients/acme-health/case_study_scan.pdf",
      "extraction_timestamp": "2025-12-17T16:00:00Z",
      "verification_status": "flagged",
      "verification_issues": [
        "Low text quality (scanned PDF): 0.62",
        "Page number verification failed",
        "Confidence below threshold: 0.65"
      ],
      "extraction_confidence_final": 0.60,
      "retry_attempts": 3,
      "action_required": "Manual review recommended"
    }
  ]
}
```

### 7. Impact Analysis (Document Changed)

```bash
curl -X POST "http://localhost:8000/lineage/impact-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
    "reason": "Document found incorrect - ROI should be 200%, not 250%"
  }' | jq .
```

**Expected Response:**
```json
{
  "document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
  "document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
  "impact_summary": {
    "affected_extractions": 3,
    "affected_roi_models": 1,
    "affected_dashboards": 2,
    "affected_prospects": 1
  },
  "affected_resources": {
    "extractions": [
      "33333333-3333-3333-3333-333333333333",
      "44444444-4444-4444-4444-444444444444",
      "55555555-5555-5555-5555-555555555555"
    ],
    "roi_models": [
      {
        "roi_model_id": "77777777-7777-7777-7777-777777777777",
        "name": "Diabetes Care Management ROI"
      }
    ],
    "dashboards": [
      {
        "dashboard_id": "99999999-9999-9999-9999-999999999999",
        "name": "Diabetes Program Executive Dashboard"
      },
      {
        "dashboard_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "name": "Clinical Outcomes Dashboard"
      }
    ]
  },
  "recommended_actions": [
    "1. Flag all 3 extractions for re-extraction",
    "2. Regenerate ROI Model 77777777-7777-7777-7777-777777777777",
    "3. Update 2 dashboards with corrected data",
    "4. Notify Blue Shield prospect of data correction"
  ]
}
```

---

## SQL Query Examples

### Direct Database Queries (for debugging/admin)

#### 1. Show All Lineage Records

```sql
SELECT
    extraction_id,
    LEFT(source_document_url, 50) AS document,
    extraction_agent,
    verification_status,
    array_length(used_in_roi_models, 1) AS roi_count,
    array_length(used_in_dashboards, 1) AS dashboard_count,
    extraction_timestamp
FROM extraction_lineage
ORDER BY extraction_timestamp DESC;
```

#### 2. Find Extractions from Specific Document

```sql
SELECT
    extraction_id,
    extraction_timestamp,
    verification_status,
    extraction_confidence_final,
    used_in_roi_models,
    used_in_dashboards
FROM extraction_lineage
WHERE source_document_hash = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2';
```

#### 3. Find All Affected Dashboards for Document

```sql
SELECT * FROM find_affected_dashboards(
    'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2'
);
```

#### 4. Agent Performance Analysis

```sql
SELECT
    extraction_agent,
    verification_status,
    COUNT(*) AS extraction_count,
    AVG(extraction_confidence_final) AS avg_confidence,
    AVG(extraction_duration_seconds) AS avg_duration,
    AVG(retry_attempts) AS avg_retries
FROM extraction_lineage
GROUP BY extraction_agent, verification_status
ORDER BY extraction_agent, verification_status;
```

**Expected Result:**
```
extraction_agent         | verification_status | count | avg_confidence | avg_duration | avg_retries
-------------------------|---------------------|-------|----------------|--------------|------------
DocumentAnalysisAgent    | verified            |   4   |     0.93       |    12.88     |    1.00
DocumentAnalysisAgent    | flagged             |   1   |     0.60       |    18.30     |    3.00
WebSearchAgent           | verified            |   1   |     0.85       |     8.20     |    1.00
```

#### 5. Find Low Confidence Extractions

```sql
SELECT
    extraction_id,
    source_document_url,
    extraction_confidence_final,
    verification_status,
    verification_issues,
    used_in_roi_models,
    used_in_dashboards
FROM extraction_lineage
WHERE extraction_confidence_final < 0.7
ORDER BY extraction_confidence_final ASC;
```

#### 6. Find Unused Extractions (Not in Any ROI Model)

```sql
SELECT
    extraction_id,
    source_document_url,
    extraction_timestamp,
    verification_status,
    extraction_confidence_final
FROM extraction_lineage
WHERE array_length(used_in_roi_models, 1) IS NULL
ORDER BY extraction_timestamp DESC;
```

#### 7. Complete Audit Trail Query

```sql
SELECT
    el.extraction_id,
    el.source_document_url,
    el.extraction_agent,
    el.verification_status,
    rm.name AS roi_model_name,
    dt.name AS dashboard_name,
    dt.target_audience
FROM extraction_lineage el
LEFT JOIN LATERAL unnest(el.used_in_roi_models) AS roi_id ON TRUE
LEFT JOIN roi_models rm ON rm.id = roi_id
LEFT JOIN LATERAL unnest(el.used_in_dashboards) AS dash_id ON TRUE
LEFT JOIN dashboard_templates dt ON dt.id = dash_id
WHERE el.extraction_id = '33333333-3333-3333-3333-333333333333';
```

---

## Common Use Cases

### Use Case 1: Client Questions Data Source

**Scenario:** Client asks "Where did the 250% ROI come from?"

**Solution:**
```bash
# Step 1: Find extraction in dashboard
curl http://localhost:8000/lineage/dashboard/99999999-9999-9999-9999-999999999999

# Step 2: Get audit trail for extraction
curl http://localhost:8000/lineage/audit-trail/33333333-3333-3333-3333-333333333333
```

**Answer:** "From `roi_analysis_2025.pdf` page 3, extracted on [timestamp], verified against source."

---

### Use Case 2: Document Found Incorrect

**Scenario:** Document contains wrong data, need to identify impact.

**Solution:**
```bash
# Run impact analysis
curl -X POST http://localhost:8000/lineage/impact-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "document_hash": "a1b2c3d4...",
    "reason": "Document contains incorrect data"
  }'
```

**Result:** List of all affected ROI models and dashboards that need updating.

---

### Use Case 3: Compliance Audit

**Scenario:** SOC2 auditor asks "Can you prove data provenance?"

**Solution:**
```sql
-- Generate complete audit report
SELECT
    el.source_document_url AS original_source,
    el.extraction_timestamp AS when_extracted,
    el.extraction_agent AS extracted_by,
    el.verification_status AS verification,
    rm.name AS used_in_roi_model,
    dt.name AS displayed_in_dashboard,
    p.name AS viewed_by_prospect
FROM extraction_lineage el
LEFT JOIN LATERAL unnest(el.used_in_roi_models) AS roi_id ON TRUE
LEFT JOIN roi_models rm ON rm.id = roi_id
LEFT JOIN LATERAL unnest(el.used_in_dashboards) AS dash_id ON TRUE
LEFT JOIN dashboard_templates dt ON dt.id = dash_id
LEFT JOIN prospect_dashboard_data pdd ON pdd.template_id = dt.id
LEFT JOIN prospects p ON p.id = pdd.prospect_id
WHERE el.extraction_id = '33333333-3333-3333-3333-333333333333';
```

---

### Use Case 4: Debugging Failed Extraction

**Scenario:** Extraction has low confidence, need to understand why.

**Solution:**
```sql
SELECT
    extraction_id,
    source_document_url,
    extraction_confidence_final,
    text_quality_score,
    extraction_method,
    retry_attempts,
    verification_status,
    verification_issues
FROM extraction_lineage
WHERE verification_status = 'flagged'
   OR extraction_confidence_final < 0.7;
```

---

### Use Case 5: Performance Optimization

**Scenario:** Identify which extraction methods are most reliable.

**Solution:**
```sql
SELECT
    extraction_method,
    COUNT(*) AS total_extractions,
    AVG(extraction_confidence_final) AS avg_confidence,
    AVG(extraction_duration_seconds) AS avg_duration,
    AVG(retry_attempts) AS avg_retries,
    SUM(CASE WHEN verification_status = 'verified' THEN 1 ELSE 0 END) AS verified_count,
    SUM(CASE WHEN verification_status = 'flagged' THEN 1 ELSE 0 END) AS flagged_count
FROM extraction_lineage
GROUP BY extraction_method
ORDER BY avg_confidence DESC;
```

**Expected Result:**
```
extraction_method | total | avg_conf | avg_dur | avg_retries | verified | flagged
------------------|-------|----------|---------|-------------|----------|--------
PyPDF2            |   3   |   0.93   |  12.50  |    1.00     |    3     |   0
web_scraping      |   1   |   0.85   |   8.20  |    1.00     |    1     |   0
Claude_Vision     |   1   |   0.60   |  18.30  |    3.00     |    0     |   1
```

**Insight:** PyPDF2 is most reliable. Claude_Vision needed for scanned PDFs but has lower confidence.

---

## Troubleshooting

### Issue 1: "extraction_lineage table does not exist"

**Cause:** Migrations not run.

**Solution:**
```bash
psql -U postgres -d triton_agentic -f database/migrations/001_add_extraction_lineage.sql
```

---

### Issue 2: "No lineage data found"

**Cause:** Mock data not loaded.

**Solution:**
```bash
psql -U postgres -d triton_agentic -f database/migrations/002_mock_lineage_data.sql
```

---

### Issue 3: API returns 404 for lineage endpoints

**Cause:** API routes not implemented yet.

**Solution:** Implement lineage API routes in `api/routes/lineage.py` (see Phase 4 of implementation plan).

---

### Issue 4: Array operations slow

**Cause:** Missing GIN indexes.

**Solution:** Verify indexes exist:
```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'extraction_lineage';
```

---

### Issue 5: Lineage not linking to ROI models

**Cause:** `link_extraction_to_roi_model()` function not called.

**Solution:** Ensure ROI Model Builder calls:
```python
await db.execute(
    "SELECT link_extraction_to_roi_model($1, $2)",
    extraction_id,
    roi_model_id
)
```

---

## Next Steps

1. ✅ **Database Setup** - Migrations complete
2. ✅ **Mock Data** - Test data loaded
3. ⏳ **API Implementation** - Create `/lineage/*` endpoints in `api/routes/lineage.py`
4. ⏳ **Agent Integration** - Update DocumentAnalysisAgent to create lineage records
5. ⏳ **Frontend UI** - Add lineage panel to dashboard view

---

## Summary

**What You Have Now:**
- ✅ Database schema with `extraction_lineage` table
- ✅ Helper functions for linking data
- ✅ Mock data showing complete flow
- ✅ 7 indexes for fast queries
- ✅ SQL query examples
- ✅ curl API examples (for future implementation)

**How It Works:**
1. **DocumentAnalysisAgent** creates lineage record (10 mandatory fields)
2. **ROI Model Builder** updates `used_in_roi_models` array
3. **Template Generator** updates `used_in_dashboards` array
4. **Complete audit trail** from document → extraction → ROI → dashboard

**Primary Purpose:**
- 80% **Human** (compliance, trust, debugging)
- 20% **Agent** (automated monitoring, alerts)

**Key Benefit:**
> Every metric in every dashboard is traceable back to its source document with page number, timestamp, and verification status.

---

**End of Guide**
