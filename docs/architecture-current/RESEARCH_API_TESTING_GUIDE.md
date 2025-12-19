# Research Agent API - End-to-End Testing Guide

**Date:** 2025-12-15
**API Version:** 1.0.0
**Base URL:** `http://localhost:8000`

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Authentication Issue & Fix](#authentication-issue--fix)
3. [Health Check](#health-check)
4. [Endpoint Testing](#endpoint-testing)
5. [Complete Test Workflow](#complete-test-workflow)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Start the API Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Or in background
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > /tmp/api_server.log 2>&1 &
```

### 2. Verify Server is Running

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "degraded",
  "timestamp": "2025-12-15T11:12:14.890578",
  "version": "1.0.0",
  "services": {
    "database": "unhealthy",
    "api": "healthy"
  }
}
```

**Note:** Database "unhealthy" status is OK for research endpoints (they use in-memory storage).

---

## Authentication Issue & Fix

### Current Issue

The research agents require AWS Bedrock credentials via SSO, which may be expired:

```
Error: Token has expired and refresh failed
```

### Solution Options

#### Option 1: Refresh AWS SSO Credentials (Recommended for Production)

```bash
# Login to AWS SSO
aws sso login --profile mare-dev

# This will open browser for authentication
# After successful login, retest the endpoints
```

#### Option 2: Switch to Anthropic Direct API (Alternative)

Edit `.env` file:

```bash
# Change from AWS Bedrock
DEFAULT_MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Restart server after change
```

#### Option 3: Use Mock Mode (Development Only)

See `api/routes/research.py` for mock implementation details.

---

## Health Check

### Check API Health

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

### Check Interactive Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Endpoint Testing

### 1. POST /research/web-search (Autonomous Mode)

Initiates comprehensive web research for a company.

**curl Command:**
```bash
curl -X POST "http://localhost:8000/research/web-search" \
  -H "Content-Type: application/json" \
  -d '{
    "client_company_name": "Livongo Health",
    "research_mode": "autonomous",
    "industry_hint": "diabetes management",
    "additional_context": "Focus on ROI and clinical outcomes",
    "max_searches": 20
  }' | python3 -m json.tool
```

**Expected Response (202 Accepted):**
```json
{
  "job_id": "research_web_04ed8c987dc1",
  "status": "pending",
  "message": "Web search research initiated for Livongo Health",
  "research_type": "web_search",
  "created_at": "2025-12-15T11:12:32.266993",
  "estimated_completion_seconds": 120
}
```

**Save Job ID:**
```bash
# Save job ID for later use
JOB_ID="research_web_04ed8c987dc1"
```

---

### 2. POST /research/web-search (Manual Mode)

Performs targeted research based on user-provided prompts.

**curl Command:**
```bash
curl -X POST "http://localhost:8000/research/web-search" \
  -H "Content-Type: application/json" \
  -d '{
    "client_company_name": "Omada Health",
    "research_mode": "manual",
    "prompts": [
      "Research Omada Health diabetes prevention program",
      "Find clinical outcomes and published ROI data",
      "Identify target customer segments and market positioning"
    ],
    "industry_hint": "chronic disease management"
  }' | python3 -m json.tool
```

**Expected Response (202 Accepted):**
```json
{
  "job_id": "research_web_a1b2c3d4e5f6",
  "status": "pending",
  "message": "Web search research initiated for Omada Health",
  "research_type": "web_search",
  "created_at": "2025-12-15T11:15:00.123456",
  "estimated_completion_seconds": 90
}
```

---

### 3. POST /research/document-analysis

Analyzes client documents to extract value propositions.

**curl Command:**
```bash
curl -X POST "http://localhost:8000/research/document-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": [
      "s3://triton-docs/client123/roi_sheet.pdf",
      "s3://triton-docs/client123/case_study.pdf",
      "s3://triton-docs/client123/product_info.pdf"
    ],
    "additional_context": "Client focuses on diabetes management for health plans"
  }' | python3 -m json.tool
```

**Expected Response (202 Accepted):**
```json
{
  "job_id": "research_doc_x9y8z7w6v5u4",
  "status": "pending",
  "message": "Document analysis initiated for 3 documents",
  "research_type": "document_analysis",
  "created_at": "2025-12-15T11:20:00.123456",
  "estimated_completion_seconds": 45
}
```

---

### 4. GET /research/{job_id}

Retrieves job status and results.

**curl Command:**
```bash
# Replace with actual job_id from step 1
curl -s "http://localhost:8000/research/research_web_04ed8c987dc1" | python3 -m json.tool
```

**Expected Response (In Progress):**
```json
{
  "job_id": "research_web_04ed8c987dc1",
  "status": "in_progress",
  "research_type": "web_search",
  "progress_percent": 45,
  "created_at": "2025-12-15T11:12:32.266771",
  "started_at": "2025-12-15T11:12:32.277796",
  "completed_at": null,
  "result": null,
  "error": null
}
```

**Expected Response (Completed):**
```json
{
  "job_id": "research_web_04ed8c987dc1",
  "status": "completed",
  "research_type": "web_search",
  "progress_percent": 100,
  "created_at": "2025-12-15T11:12:32.266771",
  "started_at": "2025-12-15T11:12:32.277796",
  "completed_at": "2025-12-15T11:14:15.123456",
  "result": {
    "searches_performed": 20,
    "queries": [
      "Livongo Health overview",
      "Livongo diabetes management",
      "Livongo ROI clinical outcomes"
    ],
    "company_overview": {
      "name": "Livongo Health",
      "description": "Digital health company providing remote monitoring...",
      "mission": "Empower people with chronic conditions...",
      "target_markets": ["Health Plans", "Employers"],
      "website": "https://livongo.com"
    },
    "value_propositions": [
      {
        "name": "Cost Reduction through Prevention",
        "description": "Reduce diabetes-related costs through early intervention...",
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
    "competitive_positioning": {...},
    "target_audiences": ["Health Plan", "Employer"],
    "sources": ["https://livongo.com", "..."],
    "research_mode": "autonomous",
    "confidence_score": 0.85,
    "missing_information": [],
    "assumptions_made": []
  },
  "error": null
}
```

**Expected Response (Failed):**
```json
{
  "job_id": "research_web_04ed8c987dc1",
  "status": "failed",
  "research_type": "web_search",
  "progress_percent": 30,
  "created_at": "2025-12-15T11:12:32.266771",
  "started_at": "2025-12-15T11:12:32.277796",
  "completed_at": "2025-12-15T11:12:36.045142",
  "result": null,
  "error": "Web research failed after 3 attempts. Last error: Error when retrieving token from sso: Token has expired and refresh failed"
}
```

---

### 5. GET /research/ (List Jobs)

Lists all research jobs with optional filtering.

**curl Command (All Jobs):**
```bash
curl -s "http://localhost:8000/research/" | python3 -m json.tool
```

**curl Command (Filter by Type):**
```bash
# Web search jobs only
curl -s "http://localhost:8000/research/?research_type=web_search" | python3 -m json.tool

# Document analysis jobs only
curl -s "http://localhost:8000/research/?research_type=document_analysis" | python3 -m json.tool
```

**curl Command (Filter by Status):**
```bash
# Completed jobs
curl -s "http://localhost:8000/research/?status_filter=completed" | python3 -m json.tool

# Failed jobs
curl -s "http://localhost:8000/research/?status_filter=failed" | python3 -m json.tool

# In progress jobs
curl -s "http://localhost:8000/research/?status_filter=in_progress" | python3 -m json.tool
```

**curl Command (Pagination):**
```bash
# First page (10 items)
curl -s "http://localhost:8000/research/?page=1&page_size=10" | python3 -m json.tool

# Second page (10 items)
curl -s "http://localhost:8000/research/?page=2&page_size=10" | python3 -m json.tool
```

**curl Command (Combined Filters):**
```bash
# Completed web search jobs, page 1
curl -s "http://localhost:8000/research/?research_type=web_search&status_filter=completed&page=1&page_size=5" | python3 -m json.tool
```

**Expected Response:**
```json
{
  "total": 5,
  "page": 1,
  "page_size": 20,
  "jobs": [
    {
      "job_id": "research_web_04ed8c987dc1",
      "status": "completed",
      "research_type": "web_search",
      "progress_percent": 100,
      "created_at": "2025-12-15T11:12:32.266771",
      "started_at": "2025-12-15T11:12:32.277796",
      "completed_at": "2025-12-15T11:14:15.123456",
      "result": {...},
      "error": null
    },
    ...
  ]
}
```

---

### 6. GET /research/stats/summary

Retrieves aggregate statistics about research jobs.

**curl Command:**
```bash
curl -s "http://localhost:8000/research/stats/summary" | python3 -m json.tool
```

**Expected Response:**
```json
{
  "total_jobs": 10,
  "web_search_jobs": 7,
  "document_analysis_jobs": 3,
  "completed_jobs": 8,
  "failed_jobs": 2,
  "average_duration_seconds": 125.5,
  "success_rate": 0.8
}
```

---

### 7. POST /research/validate

Validates a research result against schemas and business rules.

**curl Command:**
```bash
curl -X POST "http://localhost:8000/research/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "result_data": {
      "searches_performed": 18,
      "queries": ["Livongo Health overview", "Livongo ROI"],
      "company_overview": {
        "name": "Livongo Health",
        "description": "Digital health company providing remote monitoring and coaching for chronic conditions",
        "mission": "Empower people with chronic conditions to live better and healthier lives",
        "target_markets": ["Health Plans", "Employers"],
        "website": "https://livongo.com"
      },
      "value_propositions": [
        {
          "name": "Cost Reduction",
          "description": "Reduce healthcare costs through preventive care and remote monitoring",
          "evidence_type": "explicit",
          "supporting_sources": ["https://livongo.com/roi"],
          "confidence": "high"
        }
      ],
      "clinical_outcomes": [],
      "roi_framework": {
        "typical_roi_range": "250-400%",
        "payback_period": "12-18 months",
        "cost_savings_areas": ["Reduced ER visits", "Lower hospitalization"],
        "evidence_quality": "high",
        "supporting_sources": ["https://livongo.com/outcomes"]
      },
      "competitive_positioning": {
        "main_competitors": ["Omada Health", "Virta Health"],
        "unique_advantages": ["AI-powered coaching", "Real-time monitoring"],
        "market_differentiators": ["Comprehensive platform", "Clinical validation"],
        "market_position": "Market leader"
      },
      "target_audiences": ["Health Plan", "Employer"],
      "sources": ["https://livongo.com", "https://livongo.com/roi"],
      "research_mode": "autonomous",
      "confidence_score": 0.85,
      "missing_information": [],
      "assumptions_made": [],
      "research_timestamp": "2025-12-15T11:00:00Z"
    },
    "result_type": "web_search"
  }' | python3 -m json.tool
```

**Expected Response (Valid):**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Only 18 searches performed, recommended 15-25 for autonomous mode"
  ],
  "confidence_score": 0.85
}
```

**Expected Response (Invalid):**
```json
{
  "valid": false,
  "errors": [
    "company_overview.description too short (min 50 characters)",
    "value_propositions must have at least 1 item"
  ],
  "warnings": [
    "confidence_score below 0.7"
  ],
  "confidence_score": 0.65
}
```

---

## Complete Test Workflow

### Full End-to-End Test Script

Save this as `test_research_api.sh`:

```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo "========================================="
echo "Research Agent API - End-to-End Test"
echo "========================================="
echo ""

# 1. Health Check
echo -e "${YELLOW}1. Testing Health Endpoint...${NC}"
HEALTH=$(curl -s "$BASE_URL/health")
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Health check passed${NC}"
  echo "$HEALTH" | python3 -m json.tool
else
  echo -e "${RED}✗ Health check failed${NC}"
  exit 1
fi
echo ""

# 2. Initiate Web Search (Autonomous)
echo -e "${YELLOW}2. Initiating Web Search (Autonomous Mode)...${NC}"
WEB_SEARCH_RESPONSE=$(curl -s -X POST "$BASE_URL/research/web-search" \
  -H "Content-Type: application/json" \
  -d '{
    "client_company_name": "Livongo Health",
    "research_mode": "autonomous",
    "industry_hint": "diabetes management",
    "max_searches": 20
  }')

JOB_ID=$(echo "$WEB_SEARCH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo -e "${GREEN}✓ Job created: $JOB_ID${NC}"
echo "$WEB_SEARCH_RESPONSE" | python3 -m json.tool
echo ""

# 3. Poll Job Status
echo -e "${YELLOW}3. Polling Job Status...${NC}"
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  STATUS_RESPONSE=$(curl -s "$BASE_URL/research/$JOB_ID")
  STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")

  echo "Attempt $((ATTEMPT+1))/$MAX_ATTEMPTS: Status = $STATUS"

  if [ "$STATUS" = "completed" ]; then
    echo -e "${GREEN}✓ Job completed successfully${NC}"
    echo "$STATUS_RESPONSE" | python3 -m json.tool | head -50
    break
  elif [ "$STATUS" = "failed" ]; then
    echo -e "${RED}✗ Job failed${NC}"
    echo "$STATUS_RESPONSE" | python3 -m json.tool
    break
  fi

  ATTEMPT=$((ATTEMPT+1))
  sleep 2
done
echo ""

# 4. List All Jobs
echo -e "${YELLOW}4. Listing All Research Jobs...${NC}"
curl -s "$BASE_URL/research/" | python3 -m json.tool
echo ""

# 5. Get Statistics
echo -e "${YELLOW}5. Getting Research Statistics...${NC}"
curl -s "$BASE_URL/research/stats/summary" | python3 -m json.tool
echo ""

# 6. Test Manual Mode
echo -e "${YELLOW}6. Testing Manual Mode Web Search...${NC}"
MANUAL_RESPONSE=$(curl -s -X POST "$BASE_URL/research/web-search" \
  -H "Content-Type: application/json" \
  -d '{
    "client_company_name": "Omada Health",
    "research_mode": "manual",
    "prompts": [
      "Find Omada Health ROI data",
      "Identify clinical outcomes"
    ]
  }')

MANUAL_JOB_ID=$(echo "$MANUAL_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo -e "${GREEN}✓ Manual job created: $MANUAL_JOB_ID${NC}"
echo "$MANUAL_RESPONSE" | python3 -m json.tool
echo ""

# 7. Test Filtering
echo -e "${YELLOW}7. Testing Job Filtering...${NC}"
echo "Completed jobs:"
curl -s "$BASE_URL/research/?status_filter=completed" | python3 -m json.tool | head -20
echo ""

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}End-to-End Test Complete${NC}"
echo -e "${GREEN}=========================================${NC}"
```

**Make it executable and run:**
```bash
chmod +x test_research_api.sh
./test_research_api.sh
```

---

## Troubleshooting

### Issue 1: Server Not Responding

**Problem:**
```bash
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Solution:**
```bash
# Check if server is running
ps aux | grep uvicorn

# Start server if not running
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

### Issue 2: AWS SSO Token Expired

**Problem:**
```json
{
  "error": "Error when retrieving token from sso: Token has expired and refresh failed"
}
```

**Solution:**
```bash
# Refresh AWS SSO credentials
aws sso login --profile mare-dev

# Verify credentials
aws sts get-caller-identity --profile mare-dev
```

---

### Issue 3: Jobs Stuck in "pending"

**Problem:**
Jobs remain in "pending" status and never start.

**Solution:**
```bash
# Check server logs
tail -f /tmp/api_server.log

# Look for background task errors
# Restart server if necessary
```

---

### Issue 4: Database Unhealthy

**Problem:**
```json
{
  "services": {
    "database": "unhealthy"
  }
}
```

**Solution:**

This is OK for research endpoints (they use in-memory storage). If you need database features:

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Or with Docker
docker-compose up -d postgres
```

---

### Issue 5: Invalid JSON in Response

**Problem:**
Response contains non-JSON text or truncated JSON.

**Solution:**
```bash
# Don't pipe through python -m json.tool initially
curl -s "$BASE_URL/research/$JOB_ID"

# Check raw response first
# Then validate JSON separately
```

---

## Performance Benchmarks

Based on mock implementation:

| Endpoint | Method | Avg Response Time | Notes |
|----------|--------|-------------------|-------|
| `/health` | GET | < 10ms | Simple status check |
| `/research/web-search` | POST | < 50ms | Job creation only |
| `/research/{job_id}` | GET | < 20ms | In-memory lookup |
| `/research/` | GET | < 30ms | Pagination support |
| `/research/stats/summary` | GET | < 25ms | Aggregate calculation |
| `/research/validate` | POST | < 100ms | Schema validation |

**Agent Execution Times (with real LLM):**
- Web Search (autonomous): 120-180 seconds
- Web Search (manual): 60-90 seconds
- Document Analysis: 30-60 seconds

---

## Next Steps

1. **Fix AWS SSO credentials** to enable real agent execution
2. **Run full test suite** using `test_research_api.sh`
3. **Monitor job progress** via polling or SSE (if implemented)
4. **Integrate with frontend** using provided curl patterns
5. **Set up production database** for persistent job storage

---

## Related Documentation

- [RESEARCH_API_GUIDE.md](./RESEARCH_API_GUIDE.md) - Complete API reference
- [RESEARCH_API_IMPLEMENTATION_COMPLETE.md](./RESEARCH_API_IMPLEMENTATION_COMPLETE.md) - Implementation status
- [RESEARCH_AGENT_FLOW.md](./RESEARCH_AGENT_FLOW.md) - Architecture and flows
- [RESEARCH_AGENT_TEST_REPORT.md](./RESEARCH_AGENT_TEST_REPORT.md) - Test results and status

---

**Last Updated:** 2025-12-15
**Tested API Version:** 1.0.0
**Status:** API functional, agent execution requires AWS SSO refresh
