# Data Lineage - Quick Reference Card

**Last Updated:** December 17, 2025

---

## ⚡ Quick Setup (2 minutes)

```bash
# 1. Run setup script
./scripts/setup_lineage.sh

# 2. Verify setup
psql -U postgres -d triton_agentic -c "SELECT COUNT(*) FROM extraction_lineage;"
# Should return: 5
```

---

## 📊 What Gets Created

### Database Tables
- `extraction_lineage` - Main lineage tracking (10-25 fields)
- `roi_models` - ROI models using extractions

### Mock Data
- ✅ 1 Client (Acme Health Insurance)
- ✅ 1 Prospect (Blue Shield)
- ✅ 5 Extractions (3 from PDF, 1 from web, 1 flagged)
- ✅ 2 ROI Models
- ✅ 3 Dashboards
- ✅ Complete lineage chain

---

## 🔍 How It Works

```
Document (PDF)
  ↓ DocumentAnalysisAgent creates lineage record
Extraction (extraction_id: 3333)
  ↓ ROI Builder updates: used_in_roi_models = [7777]
ROI Model (id: 7777)
  ↓ Template Generator updates: used_in_dashboards = [9999]
Dashboard (id: 9999)
  ↓ Complete audit trail established
```

### Key Operations

**1. Create Lineage (DocumentAnalysisAgent)**
```python
lineage = {
    "extraction_id": uuid4(),
    "source_document_hash": sha256(document),
    "extraction_agent": "DocumentAnalysisAgent",
    "verification_status": "verified",
    "used_in_roi_models": [],  # Empty initially
    "used_in_dashboards": []   # Empty initially
}
```

**2. Link to ROI Model (ROI Builder)**
```sql
UPDATE extraction_lineage
SET used_in_roi_models = array_append(used_in_roi_models, '7777'::UUID)
WHERE extraction_id = '3333'::UUID;
```

**3. Link to Dashboard (Template Generator)**
```sql
UPDATE extraction_lineage
SET used_in_dashboards = array_append(used_in_dashboards, '9999'::UUID)
WHERE '7777'::UUID = ANY(used_in_roi_models);
```

---

## 🚀 Common Queries

### 1. Get Lineage for Extraction
```sql
SELECT * FROM extraction_lineage
WHERE extraction_id = '33333333-3333-3333-3333-333333333333';
```

### 2. Find Extractions from Document
```sql
SELECT * FROM extraction_lineage
WHERE source_document_hash = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2';
```

### 3. Impact Analysis (Document Changed)
```sql
SELECT * FROM find_affected_dashboards('a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2');
```

### 4. Find Flagged Extractions
```sql
SELECT * FROM extraction_lineage WHERE verification_status = 'flagged';
```

### 5. Agent Performance Analysis
```sql
SELECT
    extraction_agent,
    verification_status,
    COUNT(*) AS count,
    AVG(extraction_confidence_final) AS avg_confidence,
    AVG(retry_attempts) AS avg_retries
FROM extraction_lineage
GROUP BY extraction_agent, verification_status;
```

---

## 📡 curl API Examples (Once Implemented)

### Get Lineage for Extraction
```bash
curl http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333 | jq .
```

### Find Extractions from Document
```bash
curl http://localhost:8000/lineage/document/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6... | jq .
```

### Complete Audit Trail
```bash
curl http://localhost:8000/lineage/audit-trail/33333333-3333-3333-3333-333333333333 | jq .
```

### Impact Analysis
```bash
curl -X POST http://localhost:8000/lineage/impact-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "document_hash": "a1b2c3d4...",
    "reason": "Document found incorrect"
  }' | jq .
```

---

## 🔑 Mock Data UUIDs

### Client & Prospect
- **Client:** `11111111-1111-1111-1111-111111111111` (Acme Health Insurance)
- **Prospect:** `22222222-2222-2222-2222-222222222222` (Blue Shield)

### Extractions
- **Extraction 1:** `33333333-3333-3333-3333-333333333333` (ROI: 250%)
- **Extraction 2:** `44444444-4444-4444-4444-444444444444` (HbA1c)
- **Extraction 3:** `55555555-5555-5555-5555-555555555555` (Cost Savings)
- **Extraction 4:** `66666666-6666-6666-6666-666666666666` (Web Search)
- **Extraction 5:** `cccccccc-cccc-cccc-cccc-cccccccccccc` (Flagged)

### ROI Models
- **ROI Model 1:** `77777777-7777-7777-7777-777777777777` (Diabetes Management)
- **ROI Model 2:** `88888888-8888-8888-8888-888888888888` (Preventive Care)

### Dashboards
- **Dashboard 1:** `99999999-9999-9999-9999-999999999999` (Executive)
- **Dashboard 2:** `aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa` (Clinical)
- **Dashboard 3:** `bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb` (Preventive)

### Document
- **Hash:** `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2`
- **URL:** `s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf`

---

## 📋 Use Case Examples

### Use Case 1: Client Questions Data Source
**Question:** "Where did the 250% ROI come from?"

**Query:**
```sql
SELECT
    el.extraction_id,
    el.source_document_url,
    el.extraction_timestamp,
    el.verification_status,
    dt.name AS dashboard_name
FROM extraction_lineage el
JOIN LATERAL unnest(el.used_in_dashboards) AS dash_id ON TRUE
JOIN dashboard_templates dt ON dt.id = dash_id
WHERE '99999999-9999-9999-9999-999999999999'::UUID = ANY(el.used_in_dashboards)
  AND el.extraction_id = '33333333-3333-3333-3333-333333333333';
```

**Answer:** From `roi_analysis_2025.pdf`, extracted 2025-12-17 14:30:45, verified ✅

---

### Use Case 2: Document Found Incorrect
**Scenario:** ROI document contains wrong value (should be 200%, not 250%)

**Query:**
```sql
SELECT * FROM find_affected_dashboards(
    'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2'
);
```

**Result:**
- 3 extractions affected
- 1 ROI model needs regeneration
- 2 dashboards need updating

---

### Use Case 3: Find Low-Quality Extractions
**Query:**
```sql
SELECT
    extraction_id,
    source_document_url,
    extraction_confidence_final,
    verification_status,
    verification_issues
FROM extraction_lineage
WHERE extraction_confidence_final < 0.7
   OR verification_status = 'flagged';
```

**Result:** 1 extraction flagged (scanned PDF, confidence 0.60)

---

## 🎯 Key Benefits

✅ **Complete Traceability** - Every metric traceable to source document
✅ **Regulatory Compliance** - SOC2/HIPAA audit trail
✅ **Impact Analysis** - Find all affected dashboards when document changes
✅ **Quality Monitoring** - Track confidence scores, retry rates
✅ **Client Trust** - Show exactly where numbers came from
✅ **Error Investigation** - Debug wrong calculations

---

## 📚 Full Documentation

- **Complete Guide:** [docs/operations/DATA_LINEAGE_API_GUIDE.md](./operations/DATA_LINEAGE_API_GUIDE.md)
- **Implementation Plan:** [docs/EXTRACTION_HALLUCINATION_AND_LINEAGE_PLAN.md](./EXTRACTION_HALLUCINATION_AND_LINEAGE_PLAN.md)
- **Step-by-Step Flow:** [docs/DATA_LINEAGE_STEP_BY_STEP.md](./DATA_LINEAGE_STEP_BY_STEP.md)

---

## 🛠️ Files Created

```
triton-agentic/
├── database/
│   └── migrations/
│       ├── 001_add_extraction_lineage.sql    # Schema + functions
│       └── 002_mock_lineage_data.sql         # Test data
├── scripts/
│   └── setup_lineage.sh                      # Setup script
└── docs/
    ├── DATA_LINEAGE_QUICK_REFERENCE.md       # This file
    └── operations/
        └── DATA_LINEAGE_API_GUIDE.md         # Complete guide
```

---

## ⚠️ Important Notes

1. **PostgreSQL Required** - Lineage uses PostgreSQL (not Clickhouse)
2. **MVP Fields** - Start with 10 mandatory fields, add more later
3. **Primary Users** - 80% human (compliance), 20% agents (automation)
4. **Storage Cost** - Negligible (~$20/month for 100K extractions)
5. **Claude Limitations** - Cannot track lineage automatically (stateless)

---

**Quick Start:** `./scripts/setup_lineage.sh`
**Documentation:** `docs/operations/DATA_LINEAGE_API_GUIDE.md`
