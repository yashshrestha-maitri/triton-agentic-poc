# Feature-Specific Documentation

**Purpose:** Documentation for individual system features that are **architecture-agnostic**

---

## Overview

This folder contains documentation for specific features and subsystems that work independently of the overall architecture (legacy or current). These features are core building blocks used across the platform.

---

## 📚 Documentation Files

### Data & Analytics

| File | Purpose | Key Topics |
|------|---------|------------|
| [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) | Complete data flow and storage | Templates, synthetic data, `/results` endpoint |
| [ANALYTICS_AND_DASHBOARD_DATA.md](./ANALYTICS_AND_DASHBOARD_DATA.md) | Analytics and dashboard data models | Widget data, Clickhouse queries |
| [INDUSTRY_BENCHMARK_DATA_GENERATION.md](./INDUSTRY_BENCHMARK_DATA_GENERATION.md) | Industry benchmark data generation | Web search, API integration, hybrid approach, workflows |

### Prospect System

| File | Purpose | Key Topics |
|------|---------|------------|
| [PROSPECT_DATA_GENERATION.md](./PROSPECT_DATA_GENERATION.md) | Prospect dashboard data generation | Automatic data generation, database schema |
| [PROSPECT_DASHBOARD_SYSTEM.md](./PROSPECT_DASHBOARD_SYSTEM.md) | Complete prospect dashboard system | System architecture, frontend integration |

### Real-Time Events

| File | Purpose | Key Topics |
|------|---------|------------|
| [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) | Redis Pub/Sub event system | Server-Sent Events (SSE), eliminates polling |
| [MESSAGE_BROKER_TESTING.md](./MESSAGE_BROKER_TESTING.md) | Message broker testing guide | 7 test scenarios, performance comparison |

### Infrastructure

| File | Purpose | Key Topics |
|------|---------|------------|
| [FOUNDATION_AND_INFRASTRUCTURE.md](./FOUNDATION_AND_INFRASTRUCTURE.md) | Core infrastructure components | PostgreSQL, Redis, AWS services |

---

## 🎯 Feature Quick Reference

### 1. Prospect Data Generation

**What it does:** Automatically generates prospect-specific dashboard data during template creation

**Key files:**
- [PROSPECT_DATA_GENERATION.md](./PROSPECT_DATA_GENERATION.md)
- [PROSPECT_DASHBOARD_SYSTEM.md](./PROSPECT_DASHBOARD_SYSTEM.md)

**API endpoints:**
```
POST /clients/{id}/generate-templates → Triggers data generation
GET  /prospect-data/{prospect_id}     → Retrieves generated data
```

**Database tables:**
- `prospects` - Prospect information
- `prospect_dashboard_data` - Widget values (JSONB)

---

### 2. Message Broker (Real-Time Events)

**What it does:** Provides real-time job status updates via Server-Sent Events (SSE), eliminating HTTP polling

**Key files:**
- [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md)
- [MESSAGE_BROKER_TESTING.md](./MESSAGE_BROKER_TESTING.md)

**Benefits:**
- ✅ 99% reduction in HTTP requests vs polling
- ✅ Sub-second latency for status updates
- ✅ Automatic reconnection on disconnect

**API endpoints:**
```
GET /jobs/{id}/subscribe → SSE stream for real-time updates
```

**How to use:**
```javascript
const eventSource = new EventSource(`/jobs/${jobId}/subscribe`);
eventSource.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`Status: ${update.status}, Progress: ${update.progress}%`);
};
```

---

### 3. Data Flow & Storage

**What it does:** Explains how data flows through the system and where it's stored

**Key files:**
- [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md)
- [ANALYTICS_AND_DASHBOARD_DATA.md](./ANALYTICS_AND_DASHBOARD_DATA.md)

**Storage locations:**
- **Templates**: `dashboard_templates` table (PostgreSQL)
- **Prospect Data**: `prospect_dashboard_data` JSONB (PostgreSQL)
- **Analytics Data**: Clickhouse (raw prospect data)
- **Generated Files**: `results/` directory + S3

**Key endpoints:**
```
GET /templates/{template_id}            → Template structure
GET /prospect-data/{prospect_id}        → Generated widget data
GET /results/templates_{client}_{ts}.json → Full result file
```

---

### 4. Foundation & Infrastructure

**What it does:** Core infrastructure components and services

**Key file:** [FOUNDATION_AND_INFRASTRUCTURE.md](./FOUNDATION_AND_INFRASTRUCTURE.md)

**Components:**
- **PostgreSQL**: Structured data (clients, templates, prospects)
- **Clickhouse**: Analytics data (claims, utilization)
- **Redis**: Message broker, caching, job queue
- **S3**: Document storage, ROI stories
- **AWS Bedrock**: LLM inference (Claude Sonnet 4)

---

### 5. Industry Benchmark Data Generation

**What it does:** Generates and maintains fresh industry benchmark data for ROI calculations

**Key file:** [INDUSTRY_BENCHMARK_DATA_GENERATION.md](./INDUSTRY_BENCHMARK_DATA_GENERATION.md)

**Data sources:**
- **Web Search**: DuckDuckGo/Tavily search of CMS, CDC, HEDIS sites
- **Direct APIs**: CMS, CDC, NCQA data APIs (planned)
- **Internal Warehouse**: Peer benchmarks from Clickhouse (planned)
- **Hybrid Approach**: Intelligent source selection with fallback

**Key metrics:**
- Clinical benchmarks (HbA1c, blood pressure, etc.)
- Utilization rates (ED visits, readmissions)
- Cost benchmarks (ED costs, hospital stays)
- Quality measures (medication adherence, preventive care)

**Related issue:** P0 - Stale Benchmark Data (1 day fix)

---

## 🔗 Feature Integration

### How Features Work Together

```
┌─────────────────────────────────────────────────────┐
│  Template Generation (Architecture-specific)        │
│  • Legacy: Value Propositions → Templates          │
│  • Current: ROI Models → Templates                 │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  Prospect Data Generation (Feature)                 │
│  • Auto-generates widget values                     │
│  • Stores in prospect_dashboard_data JSONB          │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  Message Broker (Feature)                           │
│  • Publishes job_status_updated events              │
│  • SSE stream to frontend                           │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  Data Flow (Feature)                                │
│  • Frontend fetches via /prospect-data/{id}         │
│  • Returns JSONB data directly                      │
└─────────────────────────────────────────────────────┘
```

---

## 📖 Reading Guide

### For Frontend Developers

**Read in this order:**
1. [PROSPECT_DASHBOARD_SYSTEM.md](./PROSPECT_DASHBOARD_SYSTEM.md) - Frontend integration
2. [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) - Real-time updates
3. [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) - Data retrieval

### For Backend Developers

**Read in this order:**
1. [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) - Data storage
2. [PROSPECT_DATA_GENERATION.md](./PROSPECT_DATA_GENERATION.md) - Generation logic
3. [INDUSTRY_BENCHMARK_DATA_GENERATION.md](./INDUSTRY_BENCHMARK_DATA_GENERATION.md) - Benchmark data
4. [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) - Event system
5. [FOUNDATION_AND_INFRASTRUCTURE.md](./FOUNDATION_AND_INFRASTRUCTURE.md) - Infrastructure

### For DevOps

**Read in this order:**
1. [FOUNDATION_AND_INFRASTRUCTURE.md](./FOUNDATION_AND_INFRASTRUCTURE.md) - Infrastructure
2. [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) - Redis setup
3. See [../operations/](../operations/) for deployment guides

---

## 🧪 Testing

### Message Broker Testing

See [MESSAGE_BROKER_TESTING.md](./MESSAGE_BROKER_TESTING.md) for:
- 7 comprehensive test scenarios
- Performance comparison (polling vs SSE)
- Troubleshooting guide

**Quick test:**
```bash
# Start API server
uvicorn app:app --reload

# In another terminal
python -c "
import requests
response = requests.get('http://localhost:8000/jobs/test-job-123/subscribe', stream=True)
for line in response.iter_lines():
    print(line.decode('utf-8'))
"
```

---

## 🔗 Related Documentation

- **Current Architecture**: [../architecture-current/README.md](../architecture-current/README.md)
- **Operations & Deployment**: [../operations/README.md](../operations/README.md)
- **Legacy Architecture**: [../architecture-legacy/README.md](../architecture-legacy/README.md)
- **Main Documentation Index**: [../README.md](../README.md)

---

**Note**: These features work with both legacy and current architectures. They are building blocks that can be used regardless of the overall system design.
