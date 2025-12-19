# Lineage API - Quick Reference

**Base URL:** `http://localhost:8000/lineage`

All endpoints are now live and functional! 🚀

---

## 📖 Available Endpoints

### 1. Get Lineage for Specific Extraction
```bash
GET /lineage/{extraction_id}
```

**Example:**
```bash
curl http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333
```

**Response:**
```json
{
  "extraction_id": "33333333-3333-3333-3333-333333333333",
  "extraction_timestamp": "2025-12-17T14:30:45Z",
  "source_document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
  "source_document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
  "extraction_agent": "DocumentAnalysisAgent",
  "extraction_model": "claude-sonnet-4-20250514",
  "verification_status": "verified",
  "verification_issues": [],
  "used_in_roi_models": ["77777777-7777-7777-7777-777777777777"],
  "used_in_dashboards": ["99999999-9999-9999-9999-999999999999"],
  "extraction_confidence_final": 0.95
}
```

---

### 2. Find Extractions from Document
```bash
GET /lineage/document/{document_hash}
```

**Example:**
```bash
curl "http://localhost:8000/lineage/document/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
```

**Response:** Array of lineage records from that document

---

### 3. Get Complete Audit Trail
```bash
GET /lineage/audit-trail/{extraction_id}
```

**Example:**
```bash
curl http://localhost:8000/lineage/audit-trail/33333333-3333-3333-3333-333333333333
```

**Response:**
```json
{
  "extraction": { /* full lineage record */ },
  "roi_models": [
    {
      "roi_model_id": "77777777-7777-7777-7777-777777777777",
      "name": "Diabetes Management ROI",
      "status": "active"
    }
  ],
  "dashboards": [
    {
      "dashboard_id": "99999999-9999-9999-9999-999999999999",
      "name": "Executive Summary Dashboard",
      "target_audience": "executive"
    }
  ],
  "usage_history": [
    {
      "timestamp": "2025-12-17T14:30:45Z",
      "event": "extraction_created",
      "agent": "DocumentAnalysisAgent"
    }
  ]
}
```

---

### 4. Impact Analysis (What's Affected?)
```bash
POST /lineage/impact-analysis
```

**Example:**
```bash
curl -X POST http://localhost:8000/lineage/impact-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
    "reason": "Document found to be incorrect - ROI should be 200% not 250%"
  }'
```

**Response:**
```json
{
  "document_hash": "a1b2c3d4...",
  "reason": "Document found to be incorrect - ROI should be 200% not 250%",
  "affected_extractions": 3,
  "affected_roi_models": ["77777777-7777-7777-7777-777777777777"],
  "affected_dashboards": [
    "99999999-9999-9999-9999-999999999999",
    "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
  ],
  "details": [
    {
      "extraction_id": "33333333-3333-3333-3333-333333333333",
      "roi_model_id": "77777777-7777-7777-7777-777777777777",
      "dashboard_id": "99999999-9999-9999-9999-999999999999"
    }
  ]
}
```

**Use Case:** When a source document is found to be incorrect, this tells you exactly which ROI models and dashboards need to be regenerated.

---

### 5. Get Flagged Extractions
```bash
GET /lineage/flagged
```

**Example:**
```bash
curl "http://localhost:8000/lineage/flagged?limit=50"
```

**Response:** Array of extractions with `verification_status: "flagged"`

**Use Case:** Daily review queue for compliance/QA team

---

### 6. Mark Extraction as Verified
```bash
PUT /lineage/{extraction_id}/verify
```

**Example:**
```bash
curl -X PUT http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333/verify \
  -H "Content-Type: application/json" \
  -d '{
    "verified_by": "john.doe@acme-health.com",
    "notes": "Manually verified against source document page 3"
  }'
```

**Response:**
```json
{
  "success": true,
  "extraction_id": "33333333-3333-3333-3333-333333333333",
  "verification_status": "verified",
  "verified_by": "john.doe@acme-health.com",
  "notes": "Manually verified against source document page 3"
}
```

---

### 7. Flag Extraction for Review
```bash
PUT /lineage/{extraction_id}/flag
```

**Example:**
```bash
curl -X PUT http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333/flag \
  -H "Content-Type: application/json" \
  -d '{
    "issues": [
      "Extracted value not found in source document",
      "Confidence score below threshold (0.65)"
    ],
    "flagged_by": "automated_verification_layer5"
  }'
```

**Response:**
```json
{
  "success": true,
  "extraction_id": "33333333-3333-3333-3333-333333333333",
  "verification_status": "flagged",
  "issues": [
    "Extracted value not found in source document",
    "Confidence score below threshold (0.65)"
  ],
  "flagged_by": "automated_verification_layer5",
  "manual_review_required": true
}
```

---

### 8. Get Statistics
```bash
GET /lineage/stats/summary
```

**Example:**
```bash
curl http://localhost:8000/lineage/stats/summary
```

**Response:**
```json
{
  "total_extractions": 125,
  "verified_count": 98,
  "flagged_count": 7,
  "unverified_count": 20,
  "agents_used": ["DocumentAnalysisAgent", "WebSearchAgent"]
}
```

---

### 9. Health Check
```bash
GET /lineage/health
```

**Example:**
```bash
curl http://localhost:8000/lineage/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "Lineage API is operational"
}
```

---

## 🔧 Setup Instructions

### 1. Start PostgreSQL (if not already running)
```bash
docker-compose up -d postgres
```

### 2. Run Database Setup
```bash
./scripts/setup_lineage_docker.sh
```

This creates:
- `extraction_lineage` table with 10 MVP fields
- Helper functions: `link_extraction_to_roi_model()`, `link_roi_model_to_dashboard()`, `find_affected_dashboards()`
- 5 mock lineage records for testing

### 3. Start API Server
```bash
uvicorn app:app --reload --port 8000
```

### 4. Test the API
```bash
# Health check
curl http://localhost:8000/lineage/health

# Get mock extraction
curl http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333

# Get flagged extractions
curl http://localhost:8000/lineage/flagged
```

---

## 📊 Interactive API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You can test all endpoints interactively with sample data!

---

## 🎯 Common Workflows

### Workflow 1: Client Questions Data Source
**Question:** "Where did the 250% ROI figure come from?"

```bash
# 1. Find extraction by searching dashboards
curl http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333

# Response shows:
# - source_document_url: s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf
# - source_document_hash: a1b2c3d4...
# - extraction_timestamp: 2025-12-17T14:30:45Z
# - verification_status: verified ✅
```

**Answer:** "The 250% ROI came from your `roi_analysis_2025.pdf` document, extracted on December 17, 2025 at 2:30 PM and verified ✅"

---

### Workflow 2: Document Found Incorrect
**Scenario:** ROI document has wrong value (should be 200% not 250%)

```bash
# 1. Compute document hash (or use existing from lineage)
HASH="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"

# 2. Run impact analysis
curl -X POST http://localhost:8000/lineage/impact-analysis \
  -H "Content-Type: application/json" \
  -d "{
    \"document_hash\": \"$HASH\",
    \"reason\": \"Document contains incorrect ROI value\"
  }"

# Response shows:
# - 3 extractions affected
# - 1 ROI model needs regeneration
# - 2 dashboards need updating
```

**Action:** Regenerate affected ROI models and dashboards, flag old extractions.

---

### Workflow 3: Daily Compliance Review
**Task:** Review all flagged extractions

```bash
# 1. Get flagged extractions
curl http://localhost:8000/lineage/flagged?limit=100

# 2. For each flagged extraction, review and either:

# Option A: Verify if correct
curl -X PUT http://localhost:8000/lineage/{extraction_id}/verify \
  -H "Content-Type: application/json" \
  -d '{
    "verified_by": "compliance.team@company.com",
    "notes": "Reviewed and confirmed correct"
  }'

# Option B: Escalate if incorrect
# (trigger re-extraction workflow)
```

---

## 🔍 Query Database Directly (Alternative)

If you prefer SQL:

```bash
# Get specific extraction
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT * FROM extraction_lineage WHERE extraction_id = '33333333-3333-3333-3333-333333333333';"

# Find extractions from document
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT * FROM extraction_lineage WHERE source_document_hash = 'a1b2c3d4...';"

# Impact analysis
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT * FROM find_affected_dashboards('a1b2c3d4...');"
```

---

## 📚 Related Documentation

- **Complete API Guide:** `docs/operations/DATA_LINEAGE_API_GUIDE.md`
- **Docker Commands:** `DOCKER_LINEAGE_COMMANDS.md`
- **Quick Reference:** `docs/DATA_LINEAGE_QUICK_REFERENCE.md`
- **Implementation Plan:** `docs/EXTRACTION_HALLUCINATION_AND_LINEAGE_PLAN.md`

---

## ✅ Verification Checklist

Test all endpoints:

```bash
# 1. Health check
curl http://localhost:8000/lineage/health

# 2. Get specific lineage
curl http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333

# 3. Get audit trail
curl http://localhost:8000/lineage/audit-trail/33333333-3333-3333-3333-333333333333

# 4. Impact analysis
curl -X POST http://localhost:8000/lineage/impact-analysis \
  -H "Content-Type: application/json" \
  -d '{"document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2", "reason": "test"}'

# 5. Get flagged
curl http://localhost:8000/lineage/flagged

# 6. Get stats
curl http://localhost:8000/lineage/stats/summary
```

All endpoints should return 200 OK (or 404 if no data found).

---

**🎉 Your lineage API is ready! All endpoints are functional and documented.**
