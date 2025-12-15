

# Research Agent API Guide

**Version:** 1.0.0
**Base URL:** `http://localhost:8000`
**Documentation:** `http://localhost:8000/docs`

---

## Overview

The Research API provides endpoints for **WebSearchAgent** and **DocumentAnalysisAgent** operations for value proposition derivation as specified in TRITON_ENGINEERING_SPEC.md Section 4.2.

### Key Features

- 🔍 **Web Search Research** - AI-powered company research via Google search
- 📄 **Document Analysis** - Extract insights from client documents (PDF/DOCX)
- ⚡ **Async Processing** - Background job execution with status tracking
- ✅ **Validation** - Built-in result validation with business rules
- 📊 **Statistics** - Job metrics and success rates

---

## Authentication

Currently, no authentication is required (development mode).
In production, add API key or OAuth2 authentication.

---

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/research/web-search` | Initiate web search research |
| POST | `/research/document-analysis` | Initiate document analysis |
| GET | `/research/{job_id}` | Get job status and results |
| GET | `/research/` | List all research jobs |
| GET | `/research/stats/summary` | Get research statistics |
| POST | `/research/validate` | Validate research results |

---

## 1. Web Search Research

### POST `/research/web-search`

Initiate AI-powered research for a company using web search.

**Request Body:**
```json
{
  "client_company_name": "Livongo Health",
  "research_mode": "autonomous",
  "industry_hint": "diabetes management",
  "additional_context": "Focus on ROI and clinical outcomes",
  "max_searches": 20
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `client_company_name` | string | ✓ | Company name to research (2-200 chars) |
| `research_mode` | enum | ✓ | `autonomous` or `manual` |
| `industry_hint` | string |  | Industry context (max 200 chars) |
| `prompts` | array |  | Research prompts (required if mode=manual) |
| `additional_context` | string |  | Additional guidance (max 2000 chars) |
| `max_searches` | integer |  | Max searches (5-30, overrides defaults) |

**Research Modes:**

#### Autonomous Mode (Default)
- AI autonomously researches the company
- Performs 15-25 Google searches
- Research areas:
  - Company information & products
  - Value proposition & messaging
  - Clinical outcomes & evidence
  - Competitive landscape
  - ROI claims & success metrics
  - Market presence

**Example Request:**
```bash
curl -X POST "http://localhost:8000/research/web-search" \
  -H "Content-Type: application/json" \
  -d '{
    "client_company_name": "Livongo Health",
    "research_mode": "autonomous",
    "industry_hint": "diabetes management"
  }'
```

#### Manual Mode
- AI follows user-provided research prompts
- Performs 5-15 targeted searches
- More focused research

**Example Request:**
```json
{
  "client_company_name": "Omada Health",
  "research_mode": "manual",
  "prompts": [
    "Research Omada Health's diabetes prevention program",
    "Find clinical outcomes and published ROI data",
    "Identify target customer segments and market positioning"
  ]
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "research_web_a1b2c3d4e5f6",
  "status": "pending",
  "message": "Web search research initiated for Livongo Health",
  "research_type": "web_search",
  "created_at": "2025-01-15T10:30:00Z",
  "estimated_completion_seconds": 120
}
```

---

## 2. Document Analysis

### POST `/research/document-analysis`

Analyze client-uploaded documents to extract value propositions and metrics.

**Request Body:**
```json
{
  "document_ids": [
    "s3://triton-docs/client123/roi_sheet.pdf",
    "s3://triton-docs/client123/case_study.pdf",
    "s3://triton-docs/client123/product_info.pdf"
  ],
  "additional_context": "Client focuses on diabetes management for health plans"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_ids` | array | ✓ | S3 paths to documents (1-10 documents) |
| `additional_context` | string |  | Context about client (max 2000 chars) |

**Supported Document Types:**
- PDF (`.pdf`) - ROI sheets, case studies, white papers
- DOCX (`.docx`) - Product information, proposals
- TXT (`.txt`) - Plain text documents

**Example Request:**
```bash
curl -X POST "http://localhost:8000/research/document-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": [
      "s3://triton-docs/client123/roi_sheet.pdf"
    ],
    "additional_context": "Health plan focused on chronic disease management"
  }'
```

**Response (202 Accepted):**
```json
{
  "job_id": "research_doc_x9y8z7w6v5u4",
  "status": "pending",
  "message": "Document analysis initiated for 1 documents",
  "research_type": "document_analysis",
  "created_at": "2025-01-15T10:35:00Z",
  "estimated_completion_seconds": 30
}
```

---

## 3. Get Job Status

### GET `/research/{job_id}`

Get the status and results of a research job.

**Example Request:**
```bash
curl "http://localhost:8000/research/research_web_a1b2c3d4e5f6"
```

**Response (200 OK):**

**While In Progress:**
```json
{
  "job_id": "research_web_a1b2c3d4e5f6",
  "status": "in_progress",
  "research_type": "web_search",
  "progress_percent": 45,
  "created_at": "2025-01-15T10:30:00Z",
  "started_at": "2025-01-15T10:30:05Z",
  "completed_at": null,
  "result": null,
  "error": null
}
```

**When Completed:**
```json
{
  "job_id": "research_web_a1b2c3d4e5f6",
  "status": "completed",
  "research_type": "web_search",
  "progress_percent": 100,
  "created_at": "2025-01-15T10:30:00Z",
  "started_at": "2025-01-15T10:30:05Z",
  "completed_at": "2025-01-15T10:32:15Z",
  "result": {
    "searches_performed": 18,
    "queries": [
      "Livongo Health diabetes",
      "Livongo ROI clinical outcomes",
      "Livongo vs Omada comparison"
    ],
    "company_overview": {
      "name": "Livongo Health",
      "description": "Digital health company...",
      "mission": "Empower people with chronic conditions...",
      "target_markets": ["Health Plans", "Employers"],
      "website": "https://livongo.com"
    },
    "value_propositions": [
      {
        "name": "Cost Reduction through Prevention",
        "description": "Reduce diabetes-related costs...",
        "evidence_type": "explicit",
        "supporting_sources": ["https://livongo.com/roi"],
        "confidence": "high"
      }
    ],
    "clinical_outcomes": [...],
    "roi_framework": {
      "typical_roi_range": "250-400%",
      "payback_period": "12-18 months",
      "cost_savings_areas": ["Complication reduction", "ED avoidance"],
      "evidence_quality": "high"
    },
    "competitive_positioning": {
      "main_competitors": ["Omada Health", "Virta Health"],
      "unique_advantages": ["AI-powered coaching", "Real-time monitoring"],
      "market_position": "Market leader"
    },
    "target_audiences": ["Health Plan", "Employer", "PBM"],
    "sources": ["https://livongo.com", "..."],
    "research_mode": "autonomous",
    "confidence_score": 0.85,
    "missing_information": [],
    "assumptions_made": []
  },
  "error": null
}
```

**Job Statuses:**
- `pending` - Job queued, not started
- `in_progress` - Job currently executing
- `completed` - Job finished successfully
- `failed` - Job failed with error

---

## 4. List Research Jobs

### GET `/research/`

List all research jobs with filtering and pagination.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `research_type` | enum |  | Filter: `web_search` or `document_analysis` |
| `status_filter` | enum |  | Filter: `pending`, `in_progress`, `completed`, `failed` |
| `page` | integer | 1 | Page number (1-indexed) |
| `page_size` | integer | 20 | Items per page (max 100) |

**Example Request:**
```bash
# Get all web search jobs
curl "http://localhost:8000/research/?research_type=web_search&page=1&page_size=10"

# Get completed jobs
curl "http://localhost:8000/research/?status_filter=completed"
```

**Response (200 OK):**
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "jobs": [
    {
      "job_id": "research_web_a1b2c3",
      "status": "completed",
      "research_type": "web_search",
      "progress_percent": 100,
      "created_at": "2025-01-15T10:30:00Z",
      "completed_at": "2025-01-15T10:32:15Z",
      "result": {...},
      "error": null
    },
    ...
  ]
}
```

---

## 5. Research Statistics

### GET `/research/stats/summary`

Get aggregate statistics about research jobs.

**Example Request:**
```bash
curl "http://localhost:8000/research/stats/summary"
```

**Response (200 OK):**
```json
{
  "total_jobs": 150,
  "web_search_jobs": 100,
  "document_analysis_jobs": 50,
  "completed_jobs": 140,
  "failed_jobs": 5,
  "average_duration_seconds": 125.5,
  "success_rate": 0.933
}
```

---

## 6. Validate Research Results

### POST `/research/validate`

Validate a research result against schemas and business rules.

**Request Body:**
```json
{
  "result_data": {
    "searches_performed": 18,
    "queries": ["test query"],
    "company_overview": {...},
    "value_propositions": [...],
    ...
  },
  "result_type": "web_search"
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Only 12 searches performed, recommended 15-25 for autonomous mode"
  ],
  "confidence_score": 0.85
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation Error",
  "detail": "Manual research mode requires 'prompts' field",
  "status_code": 400
}
```

### 404 Not Found
```json
{
  "detail": "Research job 'invalid_job_id' not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "detail": "Failed to initiate web search: ...",
  "status_code": 500
}
```

---

## Python Client Examples

### Example 1: Web Search (Autonomous)
```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Initiate research
response = requests.post(f"{BASE_URL}/research/web-search", json={
    "client_company_name": "Livongo Health",
    "research_mode": "autonomous",
    "industry_hint": "diabetes management"
})

job_id = response.json()["job_id"]
print(f"Job created: {job_id}")

# Poll for completion
while True:
    response = requests.get(f"{BASE_URL}/research/{job_id}")
    status = response.json()

    if status["status"] == "completed":
        print("Research completed!")
        print(f"Value propositions found: {len(status['result']['value_propositions'])}")
        print(f"Confidence: {status['result']['confidence_score']}")
        break
    elif status["status"] == "failed":
        print(f"Research failed: {status['error']}")
        break

    time.sleep(2)
```

### Example 2: Document Analysis
```python
response = requests.post(f"{BASE_URL}/research/document-analysis", json={
    "document_ids": [
        "s3://triton-docs/client123/roi_sheet.pdf",
        "s3://triton-docs/client123/case_study.pdf"
    ],
    "additional_context": "Diabetes management for health plans"
})

job_id = response.json()["job_id"]

# Wait for completion
while True:
    status = requests.get(f"{BASE_URL}/research/{job_id}").json()

    if status["status"] == "completed":
        result = status["result"]
        print(f"Documents analyzed: {result['documents_analyzed']}")
        print(f"Value props extracted: {len(result['extracted_value_propositions'])}")
        break

    time.sleep(2)
```

### Example 3: List Recent Jobs
```python
response = requests.get(f"{BASE_URL}/research/", params={
    "page": 1,
    "page_size": 10,
    "status_filter": "completed"
})

data = response.json()
print(f"Total jobs: {data['total']}")

for job in data['jobs']:
    print(f"{job['job_id']}: {job['research_type']} - {job['status']}")
```

---

## Testing

### Run Test Suite
```bash
# Start API server
uvicorn app:app --reload

# In another terminal, run tests
python tests/test_research_api.py
```

### Interactive API Docs
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

---

## Production Considerations

### Current Implementation (Development)
- ✅ In-memory job storage (fast, simple)
- ✅ Background tasks (FastAPI BackgroundTasks)
- ✅ Mock research results (for testing without API keys)

### Production Upgrades Needed
1. **Persistent Storage**
   - Replace in-memory dict with Redis or PostgreSQL
   - Store job state, results, and history
   - Enable multi-server deployments

2. **Task Queue**
   - Use Celery for distributed task processing
   - Better retry logic and error handling
   - Job prioritization

3. **Real Agent Execution**
   - Implement actual WebSearchAgent execution
   - Implement actual DocumentAnalysisAgent execution
   - Configure API keys (TAVILY_API_KEY, FIRECRAWL_API_KEY, AWS credentials)

4. **Authentication & Authorization**
   - Add API key authentication
   - Rate limiting per client
   - Usage quotas

5. **Monitoring & Observability**
   - Prometheus metrics (already instrumented at `/metrics`)
   - Distributed tracing
   - Error alerting

6. **Result Caching**
   - Cache research results for duplicate requests
   - TTL-based cache invalidation
   - Reduce API costs

---

## Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Research Tool APIs
TAVILY_API_KEY=tvly-...          # For Google search
FIRECRAWL_API_KEY=fc-...         # For web scraping (optional)

# AWS S3 (for document reading)
AWS_PROFILE=your-profile
AWS_REGION=us-east-1

# Model Configuration
DEFAULT_MODEL_PROVIDER=aws_bedrock
DEFAULT_MODEL_NAME=us.anthropic.claude-sonnet-4-20250514-v1:0

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

---

## Support & Resources

- **API Documentation:** `http://localhost:8000/docs`
- **Engineering Spec:** `triton-docs/TRITON_ENGINEERING_SPEC.md` (Section 4.2)
- **Test Suite:** `tests/test_research_api.py`

---

**Last Updated:** 2025-12-08
**API Version:** 1.0.0
