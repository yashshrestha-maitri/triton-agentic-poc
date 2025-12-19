# Triton Platform - Engineering Specification

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Reference Branch:** `mare-mockup`
**Reference Repository:** [mare-frontend](https://github.com/your-org/mare-frontend)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [API Specifications](#3-api-specifications)
4. [Agent Designs & Workflows](#4-agent-designs--workflows)
5. [Database Schemas](#5-database-schemas)
6. [Test Strategy & Specifications](#6-test-strategy--specifications)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Implementation Roadmap](#8-implementation-roadmap)
9. [Appendix A: JSON Schema Definitions](#appendix-a-json-schema-definitions)
10. [Appendix B: Reference Data Examples](#appendix-b-reference-data-examples)

---

## 1. Executive Summary

### 1.1 Purpose

The Triton Platform is an AI-powered system that generates ROI analysis and value propositions for healthcare solutions. It leverages Large Language Models (LLMs) and multi-agent systems to transform client collateral and prospect data into customized insights, dashboards, and reports.

This engineering specification provides a complete technical blueprint for implementing the Triton Platform using:
- **Agno Framework** for multi-agent orchestration
- **FastAPI** for RESTful API services
- **PostgreSQL** for operational data
- **Clickhouse** for analytics data
- **Celery** for asynchronous job processing

### 1.2 Scope

This specification covers the complete Triton workflow:

- **Step 1:** Client Management & Value Proposition Setup
- **Step 2:** Prospect Creation, Research & Value Proposition Alignment
- **Step 3:** Prospect Data Upload & Processing (ARGO) - **EXCLUDED** (already built)
- **Step 4:** Value Proposition Data Generation (Analytics Team)
- **Step 5:** ROI Dashboard Data Generation (Analytics Team)
- **Step 6:** MARÉ Application Presentation Layer - **EXCLUDED** (separate initiative)

**MVP Scope:** All steps (1, 2, 4, 5) must be delivered for Triton to support a functional MARÉ Insights MVP.

### 1.3 Key Design Principles

1. **Test-Driven Development:** All agent outputs validated against expected JSON schemas
2. **Cloud Agnostic:** Abstract storage/cloud services for portability (AWS first, but adaptable)
3. **Async-First:** Long-running LLM operations handled asynchronously with job tracking
4. **Modular Agents:** Reusable agent teams across multiple workflow steps
5. **Schema Validation:** Pydantic models enforce output correctness at every stage

### 1.4 Technology Stack Summary

| Layer | Technology | Purpose | Why This Choice |
|-------|-----------|---------|-----------------|
| **API Framework** | FastAPI | REST endpoints, async support | Modern Python framework, auto-generated OpenAPI docs, excellent async support, type hints |
| **Task Queue** | Celery + Redis (abstracted) | Async job processing | Industry standard, robust retry logic, horizontal scaling. **Note:** Abstracted interface allows future migration to Temporal (see ADR-003) |
| **Agent Framework** | Agno | Multi-agent orchestration | Purpose-built for LLM agents, built-in team coordination, memory management, privacy-focused |
| **LLM Provider** | Anthropic Claude | AI reasoning engine | Best-in-class reasoning, long context windows, structured output support |
| **Operational DB** | PostgreSQL | ACID transactions, relational data | Reliability, JSONB support, mature ecosystem, strong consistency |
| **Analytics DB** | Clickhouse | Columnar analytics, time-series | Exceptional query performance on large datasets, compression, SQL compatibility |
| **Object Storage** | S3-compatible API | Document/file storage | Abstracted interface for cloud portability, industry standard |
| **Schema Validation** | Pydantic | Type safety, JSON validation | Native FastAPI integration, runtime validation, auto-generated schemas |
| **Containerization** | Docker | Deployment packaging | Environment consistency, easy local development, cloud-agnostic |
| **Monitoring** | AgentOS UI | Agent debugging, observability | Built into Agno, real-time execution tracking, conversation history |

#### Cloud Deployment Philosophy

**Opportunistic Cloud Services with Code-Level Abstraction**

This specification refers to technologies by their generic names (PostgreSQL, Redis, Clickhouse, etc.) rather than cloud-specific service names. However, **we are pragmatic about leveraging managed cloud services** when they provide operational benefits.

**Guiding Principles:**

1. **Application Code is Cloud-Agnostic**
   - All application code connects via standard protocols (PostgreSQL wire protocol, Redis protocol, S3 API, etc.)
   - No AWS SDK calls, GCP client libraries, or Azure SDKs in business logic
   - Connection strings, credentials, and endpoints configured via environment variables
   - Example: Code uses `psycopg2` or SQLAlchemy to connect to PostgreSQL - doesn't care if it's RDS, Cloud SQL, or self-hosted

2. **Infrastructure-as-Code is Cloud-Specific**
   - Terraform configurations organized in cloud-specific directories:
     - `infrastructure/aws/` - AWS-specific resources (RDS, ElastiCache, ECS, etc.)
     - `infrastructure/gcp/` - GCP-specific resources (Cloud SQL, Memorystore, GKE, etc.)
     - `infrastructure/azure/` - Azure-specific resources (if needed)
   - Each cloud directory provisions equivalent services using native managed offerings

3. **Configuration-Driven Deployment**
   - Application uses same Docker images regardless of cloud
   - Environment-specific configuration files:
     - `config/aws.production.env`
     - `config/gcp.production.env`
   - Configuration specifies connection details, not cloud provider

**Example: PostgreSQL Deployment**

```yaml
# Application connects via standard PostgreSQL connection string
DATABASE_URL=postgresql://user:pass@hostname:5432/triton

# AWS Production: hostname = RDS endpoint
DATABASE_URL=postgresql://admin:***@triton-prod.abc123.us-east-1.rds.amazonaws.com:5432/triton

# GCP Production: hostname = Cloud SQL endpoint
DATABASE_URL=postgresql://admin:***@10.1.2.3:5432/triton

# Local Development: hostname = Docker container
DATABASE_URL=postgresql://triton:triton@localhost:5432/triton
```

**Example: Redis Deployment**

```yaml
# AWS: ElastiCache endpoint
REDIS_URL=redis://triton-cache.abc123.use1.cache.amazonaws.com:6379/0

# GCP: Memorystore endpoint
REDIS_URL=redis://10.2.3.4:6379/0

# Local: Docker container
REDIS_URL=redis://localhost:6379/0
```

**Practical Cloud Service Mapping:**

| Technology | AWS Service | GCP Service | Azure Service | Local Dev |
|------------|-------------|-------------|---------------|-----------|
| PostgreSQL | RDS for PostgreSQL | Cloud SQL for PostgreSQL | Azure Database for PostgreSQL | Docker (postgres:15-alpine) |
| Redis | ElastiCache for Redis | Memorystore for Redis | Azure Cache for Redis | Docker (redis:7-alpine) |
| Clickhouse | EC2 + EBS | Compute Engine + Persistent Disk | VM + Managed Disk | Docker (clickhouse/clickhouse-server) |
| S3 Storage | S3 | Cloud Storage (S3-compatible) | Blob Storage (S3-compatible) | MinIO (Docker) |
| Container Orchestration | ECS Fargate | Cloud Run / GKE | Azure Container Apps | Docker Compose |

**Benefits of This Approach:**
- ✅ Leverage managed services for reliability, backups, scaling
- ✅ No vendor lock-in - can switch clouds without code changes
- ✅ Easier testing - local development uses same code paths
- ✅ Cost optimization - choose best-priced cloud for each deployment
- ✅ Multi-cloud deployments - run in AWS and GCP simultaneously if needed

**Implementation Guidance:**

Unless otherwise directed, this is the **final word on cloud strategy** for this project. Development teams should:
- Write code against standard protocols and interfaces
- Use environment variables for all external service configuration
- Place cloud-specific Terraform in appropriately named directories
- Test locally with Docker containers that mirror cloud service behavior
- Avoid cloud-specific SDKs in application code (exception: S3 client library is acceptable due to industry-standard API)

---

## 2. System Architecture

### 2.1 Layered Architecture Overview

The Triton Platform is structured in distinct layers, each with clear responsibilities:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL CLIENTS                                    │
│                    (MARÉ Frontend, API Consumers)                           │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │ HTTPS/REST
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                                   │
│                         (FastAPI REST API)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Responsibilities:                                                           │
│  • HTTP request/response handling                                           │
│  • Input validation & authentication                                        │
│  • Job creation & status tracking                                           │
│  • Synchronous CRUD operations                                              │
│  • Async job delegation to Celery                                           │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     ↓               ↓               ↓
         ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
         │  Synchronous    │ │   Async     │ │   Direct DB      │
         │  Operations     │ │   Jobs      │ │   Operations     │
         └────────┬────────┘ └──────┬──────┘ └────────┬─────────┘
                  │                 │                  │
                  ↓                 ↓                  ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                                     │
│                   (Celery + Redis + Agno)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Celery Task Queue:                                                          │
│  • Async job management                                                     │
│  • Retry logic & error handling                                             │
│  • Job status updates                                                       │
│  • Worker pool management                                                   │
│                                                                              │
│  Agno Agent Orchestration:                                                  │
│  • Agent lifecycle management                                               │
│  • Multi-agent team coordination                                            │
│  • LLM conversation state                                                   │
│  • Output validation & retry loops                                          │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     ↓               ↓               ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AGENT EXECUTION LAYER                               │
│                         (Agno Multi-Agent Teams)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  RESEARCH TEAM (Steps 1.2, 2.2-2.4)  │  ANALYTICS TEAM (Steps 4-5)         │
│  • WebSearchAgent                     │  • ClinicalAgent                     │
│  • DocumentAnalysisAgent              │  • UtilizationAgent                  │
│  • SynthesisAgent (coordinator,       │  • PricingAgent                      │
│    dual-mode: initial + refine)      │  • PharmacyAgent                     │
│  • ValidationAgent                    │  • QuestionToSQLAgent (coordinator)  │
│                                       │                                      │
│  SINGLE-PURPOSE AGENTS                │                                      │
│  • TemplateGeneratorAgent (Step 1.4) │                                      │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     ↓               ↓               ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA & STORAGE LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  PostgreSQL (Operational)  │  Clickhouse (Analytics)  │  S3 (Objects)       │
│  • Clients, Prospects      │  • Analytics queries     │  • PDF documents    │
│  • Value Propositions      │  • Member/claims data    │  • Collateral files │
│  • Dashboard Templates     │  • Pre-computed insights │  • Exports          │
│  • Job Status & Tracking   │  • Dashboard widget data │                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY LAYER                                     │
│                         (AgentOS UI - Dev/Debug Only)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Real-time agent execution monitoring                                     │
│  • Conversation history & LLM traces                                        │
│  • Manual agent testing interface                                           │
│  • Not in production request path                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Architecture Decision Records (ADRs)

#### ADR-001: Why FastAPI above Agno Agents?

**Context:**
We need a RESTful API for external clients while also orchestrating complex multi-agent workflows.

**Decision:**
FastAPI handles all HTTP concerns (routing, validation, responses), while Agno agents execute within Celery workers.

**Rationale:**
- **Separation of Concerns:** API layer handles web protocols; agents focus on AI logic
- **Scalability:** API and agents can scale independently
- **Standard Interface:** RESTful API provides familiar integration point for MARÉ frontend
- **Async Support:** FastAPI + Celery handle long-running LLM operations without blocking

**Consequences:**
- Clear boundary between web tier and agent execution
- Requires job status polling pattern for async operations
- Simplified agent code (no HTTP concerns)

---

#### ADR-002: Why Async with Job IDs?

**Context:**
Agent workflows involve multiple LLM calls that can take 10-60+ seconds each.

**Decision:**
All agent operations are asynchronous with job tracking via unique IDs.

**Rationale:**
- **User Experience:** Avoids HTTP timeouts and hung connections
- **Progress Tracking:** Frontend can show progress, estimated completion
- **Cancellation:** Jobs can be cancelled if needed
- **Reliability:** Failed jobs can be retried without re-submitting request

**Implementation Pattern:**
```
POST /api/v1/resource/action
  → Returns: { job_id: "uuid", status: "processing" }

GET /api/v1/jobs/{job_id}
  → Returns: { status: "processing|completed|failed", result: {...}, error: "..." }
```

**Consequences:**
- Frontend must implement polling or webhooks
- Job state management required in database
- More complex than synchronous calls, but necessary for reliability

---

#### ADR-003: Why Celery + Redis?

**Context:**
Need robust task queue for async agent execution.

**Decision:**
Use Celery with Redis as message broker for MVP, with abstracted interface for future migration flexibility.

**Rationale:**
- **Battle-Tested:** Industry standard for Python async tasks
- **Retry Logic:** Built-in exponential backoff, max retries
- **Monitoring:** Flower UI, task introspection
- **Scalability:** Horizontal worker scaling, task routing
- **Chaining:** Complex workflows (task A → task B → task C)
- **Fast to Implement:** Team familiarity, extensive documentation

**Alternatives Considered:**
- **Temporal.io:** Superior for complex workflows, durable execution, better observability. Consider for future if workflow complexity increases significantly.
- **AWS SQS:** Too AWS-specific, violates cloud-agnostic principle
- **RabbitMQ:** More complex, Celery works better with Redis
- **Dramatiq:** Simpler than Celery but smaller ecosystem

**Consequences:**
- Redis dependency (but lightweight)
- Celery worker processes consume memory
- Well-documented, mature ecosystem

**⚠️ IMPORTANT - Task Queue Abstraction Pattern:**

To enable (potential) future migration to Temporal or other workflow engines, **all async job processing MUST use an abstraction layer**. Do NOT call Celery tasks directly throughout the codebase.

**Abstraction Pattern:**

```python
# triton_platform/core/task_queue.py
from abc import ABC, abstractmethod
from typing import Any, Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskQueue(ABC):
    """Abstract interface for async task execution"""

    @abstractmethod
    async def enqueue(
        self,
        task_name: str,
        input_data: dict,
        job_id: str,
    ) -> str:
        """Enqueue a task for async execution"""
        pass

    @abstractmethod
    async def get_status(self, task_id: str) -> TaskStatus:
        """Get task status"""
        pass

    @abstractmethod
    async def get_result(self, task_id: str) -> Optional[Any]:
        """Get task result if completed"""
        pass

    @abstractmethod
    async def cancel(self, task_id: str) -> bool:
        """Cancel a running task"""
        pass

# triton_platform/core/celery_queue.py
class CeleryTaskQueue(TaskQueue):
    """Celery implementation of TaskQueue"""

    def __init__(self, celery_app):
        self.celery_app = celery_app

    async def enqueue(self, task_name: str, input_data: dict, job_id: str) -> str:
        task = self.celery_app.send_task(
            task_name,
            kwargs={"input_data": input_data, "job_id": job_id}
        )
        return task.id

    async def get_status(self, task_id: str) -> TaskStatus:
        result = AsyncResult(task_id, app=self.celery_app)
        return TaskStatus(result.status.lower())

    # ... other methods

# Usage in API layer
from triton_platform.core.task_queue import TaskQueue

@app.post("/api/v1/clients/{client_id}/value-proposition/derive")
async def derive_value_proposition(
    client_id: str,
    request: ValuePropositionRequest,
    task_queue: TaskQueue = Depends(get_task_queue),
):
    job = await Job.create(
        job_type="value_prop_derivation",
        status="pending",
        resource_id=client_id,
        input_data=request.dict()
    )

    # Use abstraction - NOT direct Celery task
    task_id = await task_queue.enqueue(
        task_name="tasks.derive_value_proposition",
        input_data=request.dict(),
        job_id=str(job.id)
    )

    await job.update(celery_task_id=task_id, status="processing")
    return {"job_id": str(job.id)}
```

**Benefits of Abstraction:**
- ✅ Swap Celery for Temporal with minimal code changes
- ✅ Easier testing (mock TaskQueue interface)
- ✅ Clear contract for what task queue must provide
- ✅ Dependency injection makes implementation swappable

**Migration Path to Temporal (if needed later):**
1. Implement `TemporalTaskQueue(TaskQueue)` class
2. Update dependency injection to provide Temporal implementation
3. Migrate tasks one-by-one (both implementations can run simultaneously)
4. Remove Celery when migration complete

**When to Consider Temporal Migration:**
- Workflow complexity increases (>5 steps with dependencies)
- Debugging Celery jobs becomes time-consuming
- Need better visibility into long-running workflows
- Workflow versioning becomes critical (deploy without breaking in-flight jobs)

---

#### ADR-004: Why Agno for Multi-Agent Systems?

**Context:**
Need framework for orchestrating teams of LLM agents with specialized roles.

**Decision:**
Use Agno framework for all agent coordination and execution.

**Rationale:**
- **Purpose-Built:** Designed specifically for multi-agent LLM systems
- **Team Coordination:** Built-in patterns for agent collaboration
- **Memory Management:** Conversation state, context passing between agents
- **Privacy-Focused:** Runs in our cloud, not external service
- **AgentOS:** Built-in monitoring UI for debugging
- **FastAPI Integration:** Agno provides native FastAPI runtime

**Alternatives Considered:**
- **LangChain:** More general-purpose, heavyweight
- **Custom Implementation:** Reinventing wheel, maintenance burden
- **Crew AI:** Less mature than Agno

**Consequences:**
- Learning curve for Agno-specific patterns
- Dependency on framework evolution
- Benefits outweigh costs: rapid development, built-in best practices

---

#### ADR-005: Why PostgreSQL + Clickhouse?

**Context:**
Need both transactional (CRUD) and analytical (aggregations) data storage.

**Decision:**
Use PostgreSQL for operational data, Clickhouse for analytics.

**Rationale:**

**PostgreSQL (Operational):**
- ACID transactions for client/prospect management
- JSONB support for flexible value proposition storage
- Mature ORM support (SQLAlchemy)
- Strong consistency guarantees
- Excellent for: Clients, prospects, job tracking, templates

**Clickhouse (Analytics):**
- Columnar storage optimized for aggregations
- 10-100x faster than Postgres for analytics queries
- Efficient compression for large datasets
- SQL compatibility (agents can query with SQL)
- Excellent for: Claims data, utilization metrics, dashboard widgets

**Alternative Considered:**
- Single database (Postgres only): Too slow for analytics at scale
- NoSQL (MongoDB): Loses SQL query capabilities needed by agents

**Consequences:**
- Two databases to manage and sync
- Clear data partitioning: CRUD vs analytics
- Optimal performance for each use case

---

#### ADR-006: Why S3-Compatible Storage Abstraction?

**Context:**
Need cloud-agnostic document storage for PDFs, collateral, exports.

**Decision:**
Use abstracted S3-compatible API (works with AWS S3, MinIO, GCS, Azure Blob).

**Rationale:**
- **Cloud Portability:** Same interface across cloud providers
- **Industry Standard:** S3 API is de facto standard
- **Local Development:** Can use MinIO locally, S3 in production
- **Cost Optimization:** Flexible provider choice

**Implementation:**
```python
# Abstracted storage interface
class ObjectStorage(ABC):
    def upload(path: str, data: bytes) -> str
    def download(path: str) -> bytes
    def get_url(path: str) -> str

# Implementations: S3Storage, GCSStorage, AzureBlobStorage, MinIOStorage
```

**Consequences:**
- Slight abstraction overhead
- Configuration per environment
- True cloud-agnostic design

---

#### ADR-007: Why Pydantic for Schema Validation?

**Context:**
Agent outputs must conform to expected JSON structures for downstream consumers.

**Decision:**
Use Pydantic models for all JSON schema validation.

**Rationale:**
- **Runtime Validation:** Catches schema errors before storing results
- **Type Safety:** Python type hints enforced at runtime
- **FastAPI Native:** Automatic request/response validation
- **Auto-Generated Schemas:** OpenAPI documentation for free
- **Validation Loop:** Agents retry if output invalid

**Implementation Pattern:**
```python
class ValuePropositionSchema(BaseModel):
    metadata: MetadataSchema
    value_proposition_priorities: List[PrioritySchema]
    clinical_outcomes: ClinicalOutcomesSchema

    class Config:
        extra = "forbid"  # Reject unknown fields

# In ValidationAgent:
def validate(data: dict) -> ValuePropositionSchema:
    try:
        return ValuePropositionSchema(**data)
    except ValidationError as e:
        raise AgentValidationError(e.errors())
```

**Consequences:**
- Schemas must be maintained as spec evolves
- Upfront investment in schema definitions
- Prevents invalid data from reaching database
- Critical for TDD approach

---

### 2.3 Request Flow Examples

#### Example 1: Value Proposition Derivation (Collateral-Based)

**Flow Diagram:**
```
┌─────────────┐
│ MARÉ Client │
└──────┬──────┘
       │ POST /api/v1/clients/{id}/value-proposition/derive
       │ Body: { mode: "collateral", document_ids: [...] }
       ↓
┌──────────────────┐
│   FastAPI        │
│   (API Layer)    │
├──────────────────┤
│ 1. Validate      │
│ 2. Create Job    │
│ 3. Enqueue Task  │
│ 4. Return Job ID │
└──────┬───────────┘
       │ { job_id: "uuid", status: "processing" }
       ↓
┌──────────────────┐
│   Celery Worker  │
├──────────────────┤
│ value_prop_      │
│ derivation_job   │
└──────┬───────────┘
       │ Initialize ResearchTeam
       ↓
┌─────────────────────────────────────────┐
│         RESEARCH TEAM                   │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │ SynthesisAgent (Team Lead)      │  │
│  └────────┬────────────────────────┘  │
│           │ Coordinates workflow       │
│           ↓                            │
│  ┌─────────────────────────────────┐  │
│  │ DocumentAnalysisAgent           │  │
│  ├─────────────────────────────────┤  │
│  │ • Fetch PDFs from S3            │  │
│  │ • Call LLM to extract content   │  │
│  │ • Return: extracted_info dict   │  │
│  └────────┬────────────────────────┘  │
│           │                            │
│           ↓                            │
│  ┌─────────────────────────────────┐  │
│  │ SynthesisAgent                  │  │
│  ├─────────────────────────────────┤  │
│  │ • Load Livongo JSON as template │  │
│  │   (structural reference only)   │  │
│  │ • Synthesize CLIENT content     │  │
│  │ • Call LLM to format JSON       │  │
│  │ • Return: draft_value_prop      │  │
│  └────────┬────────────────────────┘  │
│           │                            │
│           ↓                            │
│  ┌─────────────────────────────────┐  │
│  │ ValidationAgent                 │  │
│  ├─────────────────────────────────┤  │
│  │ • Validate Pydantic schema      │  │
│  │ • If errors → retry synthesis   │  │
│  │ • If valid → return final JSON  │  │
│  └────────┬────────────────────────┘  │
│           │                            │
└───────────┼────────────────────────────┘
            │ Valid ValuePropositionJSON
            ↓
┌──────────────────┐
│   Celery Task    │
├──────────────────┤
│ 1. Store in      │
│    PostgreSQL    │
│ 2. Update job    │
│    status        │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│   PostgreSQL     │
│   (Storage)      │
├──────────────────┤
│ value_props      │
│   INSERT {...}   │
│                  │
│ jobs             │
│   UPDATE status  │
│   = "completed"  │
└──────────────────┘

[Client polls for completion]

┌─────────────┐
│ MARÉ Client │
└──────┬──────┘
       │ GET /api/v1/jobs/{job_id}
       ↓
┌──────────────────┐
│   FastAPI        │
├──────────────────┤
│ Query job status │
└──────┬───────────┘
       │
       ↓ { status: "completed", value_proposition: {...} }
┌─────────────┐
│ MARÉ Client │
└─────────────┘
```

**Key Points:**
1. **Immediate Response:** Client gets job ID instantly, doesn't wait for LLM
2. **Team Coordination:** SynthesisAgent orchestrates other agents
3. **Validation Loop:** Output validated before storage, retries if invalid
4. **Polling:** Client polls job status until complete

**Timing Estimates:**
- API response: <100ms
- Document extraction: 5-15s per document
- Synthesis: 20-40s
- Validation: 1-2s
- Total: 30-60s depending on document count

---

#### Example 2: Analytics Dashboard Data Generation

**Flow Diagram:**
```
┌─────────────┐
│ MARÉ Client │
└──────┬──────┘
       │ POST /api/v1/prospects/{id}/analytics/dashboards/generate
       ↓
┌──────────────────┐
│   FastAPI        │
├──────────────────┤
│ 1. Validate      │
│ 2. Create Job    │
│ 3. Enqueue       │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│   Celery Worker  │
└──────┬───────────┘
       │ Initialize AnalyticsTeam
       ↓
┌─────────────────────────────────────────────────────────────┐
│                    ANALYTICS TEAM                           │
│                                                             │
│         QuestionToSQLAgent (Coordinator)                    │
│                      ↑                                      │
│         ┌────────────┼────────────┐                        │
│         │            │            │                        │
│    ┌────┴───┐   ┌───┴────┐   ┌──┴─────┐   ┌──────────┐  │
│    │Clinical│   │Pricing │   │Util.   │   │Pharmacy  │  │
│    │Agent   │   │Agent   │   │Agent   │   │Agent     │  │
│    └────┬───┘   └───┬────┘   └──┬─────┘   └────┬─────┘  │
│         │           │            │              │         │
│         │ [Parallel Execution]   │              │         │
│         ↓           ↓            ↓              ↓         │
│                                                            │
│  ClinicalAgent: "What is HbA1c control rate?"            │
│         ↓                                                 │
│  QuestionToSQLAgent:                                      │
│    - Translate to SQL                                     │
│    - Execute: SELECT avg(hba1c) FROM clinical_data       │
│    - Return: 8.2%                                         │
│         ↓                                                 │
│  ClinicalAgent: Store for KPI widget                     │
│                                                            │
│  PricingAgent: "Calculate 24-month ROI"                  │
│         ↓                                                 │
│  QuestionToSQLAgent:                                      │
│    - Calculate savings/costs from claims                  │
│    - Return: ROI = 340%                                   │
│         ↓                                                 │
│  PricingAgent: Format as { value: 340, display: "340%" } │
│                                                            │
│  [Similar for Utilization, Pharmacy agents...]           │
│                                                            │
│  All results aggregated by team                           │
└─────────────────────────────────────────────────────────┘
       │
       │ Complete dashboard JSON (all widgets formatted)
       ↓
┌──────────────────┐
│   PostgreSQL     │
├──────────────────┤
│ INSERT INTO      │
│ prospect_        │
│ dashboard_data   │
│ (prospect_id,    │
│  template_id,    │
│  dashboard_data  │
│  JSONB)          │
└──────────────────┘
       │
       ↓
┌──────────────────┐
│   PostgreSQL     │
├──────────────────┤
│ UPDATE jobs      │
│ SET status =     │
│ "completed"      │
└──────────────────┘
```

**Key Points:**
1. **Parallel Execution:** Multiple agents query Clickhouse raw data simultaneously
2. **SQL Coordination:** QuestionToSQLAgent executes queries against Clickhouse
3. **Pre-Computation:** All dashboard data formatted and stored upfront for fast UI rendering
4. **Postgres JSONB Storage:** Complete dashboard JSON per template, ready for instant retrieval (~10ms)

**Timing Estimates:**
- Dashboard templates: 5-10 per prospect type
- Widgets per dashboard: 8-12
- Total queries: 50-100 SQL queries
- Execution time: 2-5 minutes (parallel execution)

---

## 2.4 Component Interaction Matrix

| Component | Interacts With | Purpose | Protocol |
|-----------|----------------|---------|----------|
| **FastAPI** | External Clients | Receive HTTP requests | REST/HTTPS |
| **FastAPI** | PostgreSQL | CRUD operations, job status | SQLAlchemy ORM |
| **FastAPI** | Celery | Enqueue async jobs | Redis protocol |
| **Celery** | Redis | Task queue, job tracking | Redis pub/sub |
| **Celery** | Agno Agents | Invoke agent execution | Python function calls |
| **Agno Agents** | Anthropic API | LLM reasoning | HTTPS/REST |
| **Agno Agents** | PostgreSQL | Read/write operational data | SQLAlchemy ORM |
| **Agno Agents** | Clickhouse | Execute SQL queries, store results | Native TCP protocol |
| **Agno Agents** | S3 Storage | Read documents, write exports | S3 API |
| **Agno Agents** | ValidationAgent | Validate outputs | Python function calls |
| **AgentOS** | All Agents | Monitor execution, debug | WebSocket |

---

### 2.5 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA LIFECYCLE                           │
└─────────────────────────────────────────────────────────────┘

CLIENT SETUP (Step 1):
─────────────────────
Client Info → PostgreSQL (clients table)
                ↓
Documents → S3 Storage (PDFs, collateral)
                ↓
Research Team → Extract/synthesize → ValuePropositionJSON
                ↓
PostgreSQL (value_propositions table)
                ↓
Template Generator → DashboardTemplateJSON
                ↓
PostgreSQL (dashboard_templates table)


PROSPECT SETUP (Step 2):
────────────────────────
Prospect Info → PostgreSQL (prospects table)
                ↓
Research Team → Company research → CompanyInformationJSON
                ↓
PostgreSQL (prospect_company_info table)
                ↓
Research Team → Rank value props → RankedValuePropositionJSON
                ↓
PostgreSQL (prospect_value_propositions table)


DATA PROCESSING (Step 3):
──────────────────────────
Prospect data files → ARGO Engine
                ↓
Standardized analytics data → Clickhouse (prospect_data tables)


ANALYTICS GENERATION (Steps 4-5):
──────────────────────────────────
Analytics Team queries Clickhouse:
                ↓
Clickhouse (prospect_data) ──→ Analytics Team (Question-to-SQL Agent)
                ↓
Pre-computed & formatted insights:
  • Value proposition data → PostgreSQL JSONB (prospect_value_proposition_data)
  • Dashboard widget data → PostgreSQL JSONB (prospect_dashboard_data)


PRESENTATION (Step 6 - MARÉ Insights Application):
──────────────────────────────────
MARÉ Frontend requests:
                ↓
FastAPI → Query PostgreSQL JSONB → Return pre-formatted JSON (~10ms)
                ↓
MARÉ renders dashboards/reports

Population Summary (control totals):
FastAPI → Query Clickhouse (raw data) → Return aggregations
                ↓
MARÉ renders summary metrics
```

---

**End of Section 2**

---

## 3. API Specifications

**Important Note:** The API specifications outlined in this section are provided as **guidelines** to inform architectural planning and facilitate initial development discussions. They are **not hard and fast specifications**. Both the endpoints themselves and their request/response structures are anticipated based on current understanding of system requirements and are **expected to evolve** as development begins and progresses. The actual API surface area, endpoint naming, payload structures, and business logic will be refined iteratively through the development process based on:

- Real-world integration requirements with MARÉ frontend
- Agent framework capabilities and data flow patterns
- Performance considerations and optimization opportunities
- Security and authentication requirements
- Developer feedback and usability testing

Treat these specifications as a starting point for collaboration between frontend, backend, and agent development teams, with the expectation that they will be adjusted to meet practical implementation needs.

---

### 3.1 API Overview

**Base URL:** `https://api.triton.example.com/api/v1`

**Authentication:** Bearer token (JWT) - Implementation details TBD
**Content-Type:** `application/json`
**API Versioning:** URL path versioning (`/api/v1`, `/api/v2`, etc.)

#### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PATCH |
| 201 | Created | Successful POST (resource created) |
| 202 | Accepted | Async job accepted, processing |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input, validation error |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (duplicate, state issue) |
| 422 | Unprocessable Entity | Semantic validation error |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Temporary unavailability |

#### Error Response Format

All error responses follow this structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "document_ids",
        "issue": "must be a non-empty array"
      }
    ],
    "request_id": "uuid-for-tracing"
  }
}
```

---

### 3.2 Step 1 APIs: Client Management & Value Proposition Setup

#### 3.2.1 Client CRUD Operations

##### Create Client
```
POST /api/v1/clients
```

**Request Body:**
```json
{
  "company_name": "string (required, max 255 chars)",
  "industry": "string (optional, max 100 chars)",
  "settings": {
    "branding": {
      "primary_color": "#hexcolor",
      "logo_url": "https://..."
    }
  },
  "status": "active | inactive (default: active)"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "company_name": "Livongo Health",
  "industry": "Diabetes Management",
  "settings": { ... },
  "status": "active",
  "created_at": "2025-10-30T10:00:00Z",
  "updated_at": "2025-10-30T10:00:00Z"
}
```

---

##### List Clients
```
GET /api/v1/clients
```

**Query Parameters:**
- `status` (optional): Filter by status (`active`, `inactive`)
- `page` (optional, default 1): Page number
- `limit` (optional, default 20, max 100): Results per page

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid",
      "company_name": "Livongo Health",
      "industry": "Diabetes Management",
      "status": "active",
      "created_at": "2025-10-30T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

---

##### Get Client
```
GET /api/v1/clients/{client_id}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "company_name": "Livongo Health",
  "industry": "Diabetes Management",
  "settings": { ... },
  "status": "active",
  "created_at": "2025-10-30T10:00:00Z",
  "updated_at": "2025-10-30T10:00:00Z",
  "value_proposition": {
    "id": "uuid",
    "status": "approved",
    "version": 3
  },
  "dashboard_templates_count": 8
}
```

---

##### Update Client
```
PATCH /api/v1/clients/{client_id}
```

**Request Body:** (all fields optional)
```json
{
  "company_name": "string",
  "industry": "string",
  "settings": { ... },
  "status": "active | inactive"
}
```

**Response (200 OK):** Updated client object

---

##### Delete Client
```
DELETE /api/v1/clients/{client_id}
```

**Response (204 No Content)**

**Note:** Soft delete - sets status to `deleted`, preserves data

---

#### 3.2.2 Document Management

##### Upload Document
```
POST /api/v1/clients/{client_id}/documents
```

**Request (multipart/form-data):**
- `file`: PDF file (max 50MB)
- `document_type`: `collateral | roi_sheet | whitepaper | case_study | product_overview | other`
- `name`: Display name (optional, defaults to filename)
- `description`: Context about document contents (optional but recommended)
  - Example: "ROI calculator showing 18-month payback for diabetes program"
  - Example: "Clinical case study demonstrating HbA1c reduction outcomes"
  - Example: "Product overview highlighting EHR integration capabilities"

**Response (201 Created):**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "name": "Client ROI Analysis 2024.pdf",
  "document_type": "roi_sheet",
  "description": "ROI calculator for diabetes prevention program targeting pre-diabetic populations",
  "file_size": 2458624,
  "storage_path": "s3://bucket/clients/{id}/documents/{uuid}.pdf",
  "uploaded_at": "2025-10-30T10:00:00Z"
}
```

**Usage Note:** The `description` field helps DocumentAnalysisAgent understand the context and purpose of each document, improving extraction accuracy. Encourage users to provide descriptive context when uploading materials.

---

##### List Documents
```
GET /api/v1/clients/{client_id}/documents
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Livongo ROI Sheet.pdf",
      "document_type": "roi_sheet",
      "file_size": 2458624,
      "uploaded_at": "2025-10-30T10:00:00Z"
    }
  ]
}
```

---

##### Get Document Download URL
```
GET /api/v1/clients/{client_id}/documents/{document_id}/download
```

**Response (200 OK):**
```json
{
  "download_url": "https://presigned-s3-url",
  "expires_at": "2025-10-30T11:00:00Z"
}
```

---

#### 3.2.3 Value Proposition Derivation (Step 1.2)

##### Initiate Value Proposition Derivation
```
POST /api/v1/clients/{client_id}/value-proposition/derive
```

**Request Body:**
```json
{
  "mode": "research | collateral",

  // Mode A: Research-based
  // Two sub-modes: autonomous (AI-driven) or manual (user-provided prompts)

  // Research Mode - Autonomous (AI researches based on company name)
  "autonomous": true,  // If true, WebSearchAgent auto-researches the client
  "client_company_name": "Livongo Health",  // Required if autonomous=true
  "industry_hint": "diabetes management",   // Optional, helps focus research

  // Research Mode - Manual (user provides specific prompts)
  "autonomous": false,  // If false, use user-provided prompts
  "prompts": [  // Required if autonomous=false
    "Research Livongo's diabetes management solution",
    "Identify clinical outcomes and ROI drivers",
    "Focus on remote patient monitoring and continuous glucose monitoring"
  ],

  // Mode B: Collateral-based (required if mode=collateral)
  "document_ids": [
    "uuid-1",  // Client's ROI calculator spreadsheet
    "uuid-2",  // Client's clinical case study PDF
    "uuid-3"   // Client's product overview deck
  ],

  // Optional: Free-form text providing additional context (works for both modes)
  // User can explain their value prop, target audiences, key differentiators, etc.
  "additional_context": "Our solution focuses on pre-diabetic populations with a prevention-first approach. Key differentiators include integration with major EHR systems and proprietary predictive algorithms. Target ROI timeline is 18-24 months with focus on avoided progression to Type 2 diabetes."
}
```

**Mode Selection Logic:**
- `mode=research` + `autonomous=true` → AI auto-researches based on company name
- `mode=research` + `autonomous=false` → AI follows user-provided prompts
- `mode=collateral` → AI analyzes uploaded documents (autonomous flag ignored)

**Important Note:** The system uses a pre-generated Livongo JSON example (from Appendix B) as a **structural template** showing what a complete value proposition should look like. The Livongo PDF is NOT parsed during client value proposition derivation. Instead:
- Client uploads THEIR documents (ROI sheets, case studies, product info)
- Client provides THEIR additional context via free-form text
- SynthesisAgent uses the Livongo JSON structure as a reference format
- Output is generated from CLIENT's materials, formatted to match the Livongo template structure

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "created_at": "2025-10-30T10:00:00Z",
  "estimated_completion": "2025-10-30T10:01:30Z"
}
```

---

##### Get Derivation Job Status
```
GET /api/v1/clients/{client_id}/value-proposition/jobs/{job_id}
```

**Response (200 OK) - Processing:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": {
    "stage": "document_analysis | synthesis | validation",
    "percent_complete": 45,
    "current_step": "Analyzing document 2 of 3"
  },
  "created_at": "2025-10-30T10:00:00Z",
  "estimated_completion": "2025-10-30T10:01:30Z"
}
```

**Response (200 OK) - Completed:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "value_proposition": {
    "id": "uuid",
    "version": 1,
    "mode": "collateral",
    "status": "draft",
    "data": { /* ValuePropositionJSON - see Appendix A */ },
    "created_at": "2025-10-30T10:01:25Z"
  },
  "completed_at": "2025-10-30T10:01:25Z"
}
```

**Response (200 OK) - Failed:**
```json
{
  "job_id": "uuid",
  "status": "failed",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Failed to generate valid value proposition after 3 attempts",
    "details": [
      {
        "field": "clinical_outcomes.baseline_metrics",
        "issue": "Missing required field"
      }
    ]
  },
  "failed_at": "2025-10-30T10:01:25Z"
}
```

---

##### Get Current Value Proposition
```
GET /api/v1/clients/{client_id}/value-proposition
```

**Query Parameters:**
- `version` (optional): Specific version number (default: latest)

**Response (200 OK):**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "version": 3,
  "mode": "collateral",
  "status": "approved | draft | in_review",
  "data": { /* ValuePropositionJSON */ },
  "created_at": "2025-10-30T10:00:00Z",
  "updated_at": "2025-10-30T10:05:00Z"
}
```

---

#### 3.2.4 Value Proposition Review & Refinement (Step 1.3)

##### Get Value Proposition for Review
```
GET /api/v1/clients/{client_id}/value-proposition/review
```

**Response (200 OK):**
```json
{
  "value_proposition_id": "uuid",
  "version": 1,
  "status": "in_review",
  "feedback_round": 0,
  "sections": [
    {
      "section_id": "executive_value_proposition",
      "title": "Executive Value Proposition",
      "content": { /* section data */ },
      "feedback_status": "pending | approved | rejected"
    },
    {
      "section_id": "clinical_outcomes_foundation",
      "title": "Clinical Outcomes Foundation",
      "content": { /* section data */ },
      "feedback_status": "pending"
    }
    // ... more sections
  ]
}
```

---

##### Submit Review Feedback
```
POST /api/v1/clients/{client_id}/value-proposition/review/feedback
```

**Request Body:**
```json
{
  "value_proposition_id": "uuid",
  "section_feedback": [
    {
      "section_id": "executive_value_proposition",
      "action": "approve"
    },
    {
      "section_id": "roi_opportunities_tier_1",
      "action": "reject_remove",
      "rationale": "This tier doesn't align with our current product capabilities"
    },
    {
      "section_id": "clinical_outcomes_foundation",
      "action": "reject_change",
      "feedback": "Focus more on HbA1c reduction and less on hospitalization rates. Our clinical data shows 1.2% average HbA1c reduction."
    }
  ],
  "general_feedback": "Overall good structure but needs more emphasis on preventive care vs reactive interventions."
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "feedback_round": 1,
  "created_at": "2025-10-30T10:00:00Z"
}
```

---

##### Get Refinement Job Status
```
GET /api/v1/clients/{client_id}/value-proposition/review/jobs/{job_id}
```

**Response (200 OK) - Completed:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "value_proposition": {
    "id": "uuid",
    "version": 2,
    "status": "in_review",
    "feedback_round": 1,
    "data": { /* Refined ValuePropositionJSON */ },
    "changes_summary": [
      "Removed section: roi_opportunities_tier_1",
      "Modified section: clinical_outcomes_foundation - Updated HbA1c metrics",
      "Applied general feedback across relevant sections"
    ]
  },
  "completed_at": "2025-10-30T10:00:45Z"
}
```

---

##### Approve Final Value Proposition
```
POST /api/v1/clients/{client_id}/value-proposition/approve
```

**Request Body:**
```json
{
  "value_proposition_id": "uuid"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "version": 3,
  "status": "approved",
  "approved_at": "2025-10-30T10:10:00Z",
  "approved_by": "user_id"
}
```

---

#### 3.2.5 Dashboard Template Generation (Step 1.4)

##### Generate Dashboard Templates
```
POST /api/v1/clients/{client_id}/dashboard-templates/generate
```

**Request Body:**
```json
{
  "value_proposition_id": "uuid"
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "created_at": "2025-10-30T10:00:00Z",
  "estimated_completion": "2025-10-30T10:01:00Z"
}
```

---

##### Get Template Generation Job Status
```
GET /api/v1/clients/{client_id}/dashboard-templates/jobs/{job_id}
```

**Response (200 OK) - Completed:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "templates": [
    {
      "id": "uuid",
      "name": "Diabetes ROI Executive Dashboard",
      "description": "Comprehensive financial impact analysis for C-suite",
      "category": "roi-focused",
      "target_audience": "Health Plan",
      "key_features": [
        "24-month ROI projection",
        "Cost savings waterfall",
        "Payback period analysis"
      ],
      "widget_count": 8,
      "preview_url": "https://..."
    }
    // ... 4-9 more templates
  ],
  "templates_generated": 8,
  "completed_at": "2025-10-30T10:00:55Z"
}
```

---

##### List Dashboard Templates
```
GET /api/v1/clients/{client_id}/dashboard-templates
```

**Query Parameters:**
- `category` (optional): Filter by category
- `target_audience` (optional): Filter by audience
- `status` (optional): `generated | approved | removed`

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Diabetes ROI Executive Dashboard",
      "description": "Comprehensive financial impact analysis",
      "category": "roi-focused",
      "target_audience": "Health Plan",
      "key_features": ["..."],
      "widget_count": 8,
      "status": "approved",
      "created_at": "2025-10-30T10:00:00Z"
    }
  ]
}
```

---

##### Get Dashboard Template Details
```
GET /api/v1/clients/{client_id}/dashboard-templates/{template_id}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "name": "Diabetes ROI Executive Dashboard",
  "description": "Comprehensive financial impact analysis for C-suite presentations",
  "category": "roi-focused",
  "target_audience": "Health Plan",
  "key_features": [
    "24-month ROI projection with confidence intervals",
    "Cost savings waterfall by intervention type",
    "Payback period analysis"
  ],
  "widgets": [
    {
      "id": "widget-1",
      "type": "kpi_card",
      "title": "24-Month ROI",
      "data_requirements": {
        "metrics": ["total_savings", "program_cost"],
        "calculation": "((savings - cost) / cost) * 100"
      },
      "position": { "row": 1, "col": 1, "width": 3, "height": 2 }
    },
    {
      "id": "widget-2",
      "type": "waterfall_chart",
      "title": "Savings Breakdown",
      "data_requirements": {
        "metrics": ["mi_prevention", "stroke_prevention", "kidney_disease_prevention"],
        "aggregation": "sum"
      },
      "position": { "row": 1, "col": 4, "width": 9, "height": 4 }
    }
    // ... more widgets
  ],
  "visual_style": {
    "primary_color": "#2563eb",
    "accent_color": "#10b981",
    "layout": "balanced"
  },
  "recommended_use_case": "Use for C-suite and board presentations when emphasizing financial returns",
  "status": "approved",
  "created_at": "2025-10-30T10:00:00Z"
}
```

---

##### Remove Dashboard Template
```
DELETE /api/v1/clients/{client_id}/dashboard-templates/{template_id}
```

**Response (204 No Content)**

**Note:** Soft delete - sets status to `removed`

---

##### Approve Dashboard Template
```
PATCH /api/v1/clients/{client_id}/dashboard-templates/{template_id}/approve
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "status": "approved",
  "approved_at": "2025-10-30T10:05:00Z"
}
```

---

### 3.3 Step 2 APIs: Prospect Management & Research

#### 3.3.1 Prospect CRUD Operations

##### Create Prospect
```
POST /api/v1/prospects
```

**Request Body:**
```json
{
  "client_id": "uuid (required)",
  "company_name": "string (required, max 255 chars)",
  "contact_name": "string (optional)",
  "contact_email": "string (optional)",
  "contact_phone": "string (optional)",
  "notes": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "company_name": "Wellmark Blue Cross Blue Shield",
  "contact_name": "John Smith",
  "contact_email": "john.smith@wellmark.com",
  "status": "created",
  "created_at": "2025-10-30T10:00:00Z",
  "updated_at": "2025-10-30T10:00:00Z"
}
```

---

##### List Prospects
```
GET /api/v1/prospects
```

**Query Parameters:**
- `client_id` (optional): Filter by client
- `status` (optional): Filter by status
- `page`, `limit`: Pagination

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid",
      "client_id": "uuid",
      "company_name": "Wellmark BCBS",
      "status": "researched | analyzing | completed",
      "created_at": "2025-10-30T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

##### Get Prospect
```
GET /api/v1/prospects/{prospect_id}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "company_name": "Wellmark Blue Cross Blue Shield",
  "contact_name": "John Smith",
  "status": "completed",
  "company_research": {
    "status": "completed",
    "completed_at": "2025-10-30T10:02:00Z"
  },
  "value_proposition_ranking": {
    "status": "completed",
    "completed_at": "2025-10-30T10:03:00Z"
  },
  "analytics": {
    "status": "completed",
    "completed_at": "2025-10-30T10:15:00Z"
  },
  "created_at": "2025-10-30T10:00:00Z",
  "updated_at": "2025-10-30T10:15:00Z"
}
```

---

#### 3.3.2 Prospect Company Research (Step 2.2)

##### Initiate Company Research
```
POST /api/v1/prospects/{prospect_id}/research/company
```

**Request Body:**
```json
{
  "company_name": "string (optional, defaults to prospect.company_name)",
  "additional_context": "string (optional, e.g., 'Focus on Iowa market')"
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "created_at": "2025-10-30T10:00:00Z",
  "estimated_completion": "2025-10-30T10:02:00Z"
}
```

---

##### Get Company Research Job Status
```
GET /api/v1/prospects/{prospect_id}/research/jobs/{job_id}
```

**Response (200 OK) - Completed:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "company_information": {
    "data_source_metadata": {
      "sources_used": "Google Search, company website, news articles",
      "web_searches_performed": 8,
      "search_queries": [
        "Wellmark Blue Cross Blue Shield overview",
        "Wellmark BCBS covered lives Iowa",
        "Wellmark health plan services"
      ],
      "data_freshness": "2025-10-30"
    },
    "company_overview": {
      "company_name": "Wellmark Blue Cross Blue Shield",
      "description": "Leading health insurance provider in Iowa and South Dakota",
      "website": "https://www.wellmark.com",
      "founded": "1939",
      "headquarters": "Des Moines, Iowa"
    },
    "classification": {
      "core_segment": "PAYER",
      "subsegment": "Health Plan",
      "healthcare_organization_type": "Regional Health Insurance Provider"
    },
    "healthcare_specifics": {
      "covered_lives": "~2.7 million",
      "lines_of_business": ["Commercial", "Medicare Advantage", "Medicaid"],
      "contracting_model": "Direct contracts with providers",
      "data_exchange_maturity": "High - Advanced EDI and API capabilities"
    }
    // ... see Appendix B for full structure
  },
  "completed_at": "2025-10-30T10:01:45Z"
}
```

---

##### Get Company Information
```
GET /api/v1/prospects/{prospect_id}/company-information
```

**Response (200 OK):**
```json
{
  "prospect_id": "uuid",
  "data": { /* CompanyInformationJSON - see Appendix B */ },
  "created_at": "2025-10-30T10:01:45Z"
}
```

---

#### 3.3.3 Value Proposition Ranking (Step 2.4)

##### Initiate Value Proposition Ranking
```
POST /api/v1/prospects/{prospect_id}/value-proposition/rank
```

**Request Body:**
```json
{
  "client_value_proposition_id": "uuid (required)"
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "created_at": "2025-10-30T10:00:00Z",
  "estimated_completion": "2025-10-30T10:00:30Z"
}
```

---

##### Get Ranking Job Status
```
GET /api/v1/prospects/{prospect_id}/value-proposition/rank/jobs/{job_id}
```

**Response (200 OK) - Completed:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "ranked_value_proposition": {
    "id": "uuid",
    "prospect_id": "uuid",
    "metadata": {
      "document_name": "Livongo Value Proposition - Wellmark BCBS (Ranked)",
      "purpose": "Prospect-specific value proposition ranking",
      "prospect_company": "Wellmark Blue Cross Blue Shield",
      "prospect_type": "Health Plan",
      "ranking_date": "2025-10-30"
    },
    "value_proposition_priorities": [
      {
        "priority_id": "vp-1",
        "priority_name": "Financial ROI - Cost Reduction",
        "default_rank": 1,
        "rank_locked": true,
        "segment_priority": {
          "high_priority": ["Health Plan", "Broker"],
          "medium_priority": ["PBM"],
          "low_priority": []
        },
        "presentation_talking_points": [
          "Wellmark's focus on cost management aligns perfectly with demonstrated 340% ROI",
          "With 2.7M covered lives, even modest PMPM savings translate to significant impact"
        ],
        "relevance_warning": null
      },
      {
        "priority_id": "vp-2",
        "priority_name": "Clinical Quality Improvement",
        "default_rank": 2,
        "rank_locked": false,
        "segment_priority": {
          "high_priority": ["Health Plan", "Medical Management"],
          "medium_priority": ["Broker"],
          "low_priority": []
        },
        "presentation_talking_points": [
          "Wellmark's Medicare Advantage focus makes Stars ratings improvement critical",
          "Clinical outcomes directly impact member satisfaction and retention"
        ]
      }
      // ... more priorities
    ]
  },
  "completed_at": "2025-10-30T10:00:25Z"
}
```

---

##### Get Ranked Value Proposition
```
GET /api/v1/prospects/{prospect_id}/value-proposition
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "prospect_id": "uuid",
  "data": { /* RankedValuePropositionJSON */ },
  "created_at": "2025-10-30T10:00:25Z",
  "updated_at": "2025-10-30T10:05:00Z"
}
```

---

##### Manually Update Ranking
```
PATCH /api/v1/prospects/{prospect_id}/value-proposition/ranking
```

**Request Body:**
```json
{
  "priority_updates": [
    {
      "priority_id": "vp-2",
      "new_rank": 1
    },
    {
      "priority_id": "vp-1",
      "new_rank": 2
    }
  ],
  "removed_priorities": ["vp-5"]
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "updated_priorities": [ /* reordered priorities */ ],
  "updated_at": "2025-10-30T10:06:00Z"
}
```

---

### 3.4 Steps 4-5 APIs: Analytics Data Generation

#### 3.4.1 Value Proposition Data Generation (Step 4)

##### Generate Value Proposition Insights
```
POST /api/v1/prospects/{prospect_id}/analytics/value-propositions/generate
```

**Request Body:**
```json
{
  "ranked_value_proposition_id": "uuid (required)"
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "created_at": "2025-10-30T10:00:00Z",
  "estimated_completion": "2025-10-30T10:03:00Z"
}
```

---

##### Get Value Proposition Generation Job Status
```
GET /api/v1/prospects/{prospect_id}/analytics/value-propositions/jobs/{job_id}
```

**Response (200 OK) - Processing:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": {
    "priorities_analyzed": 2,
    "priorities_total": 8,
    "current_priority": "Clinical Quality Improvement",
    "current_agent": "ClinicalAgent",
    "queries_executed": 45,
    "estimated_queries_remaining": 30
  }
}
```

**Response (200 OK) - Completed:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "insights_generated": 8,
  "queries_executed": 127,
  "storage_location": "postgres.prospect_value_proposition_data",
  "completed_at": "2025-10-30T10:02:55Z"
}
```

---

##### Get Value Proposition Insights
```
GET /api/v1/prospects/{prospect_id}/analytics/value-propositions/insights
```

**Query Parameters:**
- `priority_id` (optional): Filter to specific priority

**Response (200 OK):**
```json
{
  "prospect_id": "uuid",
  "insights": [
    {
      "priority_id": "vp-1",
      "priority_name": "Financial ROI - Cost Reduction",
      "baseline_metrics": {
        "current_diabetes_cost_pmpm": 245.50,
        "uncontrolled_diabetes_members": 12847,
        "complication_rate": 0.18
      },
      "projected_impact": {
        "cost_reduction_pmpm": 67.30,
        "annual_savings": 10350000,
        "roi_percentage": 340,
        "payback_months": 14
      },
      "supporting_evidence": {
        "queries_executed": 18,
        "data_sources": ["claims_data", "member_demographics", "utilization_metrics"],
        "confidence_level": "high"
      },
      "visualization_data": {
        "savings_waterfall": [ /* chart data */ ],
        "roi_trend": [ /* chart data */ ]
      }
    }
    // ... more priorities
  ],
  "generated_at": "2025-10-30T10:02:55Z"
}
```

---

#### 3.4.2 Dashboard Data Generation (Step 5)

##### Generate Dashboard Widget Data
```
POST /api/v1/prospects/{prospect_id}/analytics/dashboards/generate
```

**Request Body:**
```json
{
  "template_ids": ["uuid-1", "uuid-2"] // optional, defaults to all approved templates
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "templates_to_process": 8,
  "estimated_widgets": 68,
  "created_at": "2025-10-30T10:00:00Z",
  "estimated_completion": "2025-10-30T10:04:00Z"
}
```

---

##### Get Dashboard Generation Job Status
```
GET /api/v1/prospects/{prospect_id}/analytics/dashboards/jobs/{job_id}
```

**Response (200 OK) - Processing:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": {
    "templates_completed": 3,
    "templates_total": 8,
    "widgets_completed": 24,
    "widgets_total": 68,
    "current_template": "Clinical Outcomes Dashboard",
    "current_agent": "ClinicalAgent",
    "queries_executed": 89
  }
}
```

**Response (200 OK) - Completed:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "templates_processed": 8,
  "widgets_generated": 68,
  "queries_executed": 234,
  "storage_location": "postgres.prospect_dashboard_data",
  "completed_at": "2025-10-30T10:03:45Z"
}
```

---

##### Get Dashboard Widget Data
```
GET /api/v1/prospects/{prospect_id}/analytics/dashboards/{template_id}/data
```

**Response (200 OK):**
```json
{
  "prospect_id": "uuid",
  "template_id": "uuid",
  "template_name": "Diabetes ROI Executive Dashboard",
  "widget_data": {
    "kpi_roi_percentage": {
      "value": 340,
      "display": "340%",
      "trend": "up",
      "comparison": "+45% vs industry avg"
    },
    "kpi_payback_period": {
      "value": 14,
      "display": "14 months",
      "trend": "down"
    },
    "chart_savings_waterfall": [
      { "category": "MI Prevention", "value": 8500000 },
      { "category": "Stroke Prevention", "value": 6200000 },
      { "category": "Kidney Disease", "value": 4800000 },
      { "category": "Program Cost", "value": -5000000 },
      { "category": "Net Savings", "value": 14500000 }
    ],
    "chart_utilization_trends": [
      { "month": "2024-01", "ed_visits": 145, "hospitalizations": 62 },
      { "month": "2024-02", "ed_visits": 138, "hospitalizations": 58 },
      // ... 24 months of data
    ]
  },
  "generated_at": "2025-10-30T10:03:45Z"
}
```

---

##### List Available Dashboards
```
GET /api/v1/prospects/{prospect_id}/analytics/dashboards
```

**Response (200 OK):**
```json
{
  "prospect_id": "uuid",
  "prospect_type": "Health Plan",
  "dashboards": [
    {
      "template_id": "uuid",
      "name": "Diabetes ROI Executive Dashboard",
      "category": "roi-focused",
      "target_audience": "Health Plan",
      "widget_count": 8,
      "data_status": "ready | generating | pending",
      "preview_url": "/analytics/dashboards/{template_id}/data"
    }
  ]
}
```

---

### 3.5 Job Management APIs

#### Get Job Status (Generic)
```
GET /api/v1/jobs/{job_id}
```

**Response (200 OK):**
```json
{
  "job_id": "uuid",
  "job_type": "value_proposition_derivation | prospect_research | analytics_generation",
  "status": "pending | processing | completed | failed",
  "resource_type": "client | prospect",
  "resource_id": "uuid",
  "progress": { /* job-specific progress */ },
  "result": { /* present if completed */ },
  "error": { /* present if failed */ },
  "created_at": "2025-10-30T10:00:00Z",
  "started_at": "2025-10-30T10:00:05Z",
  "completed_at": "2025-10-30T10:02:30Z"
}
```

---

#### List Jobs
```
GET /api/v1/jobs
```

**Query Parameters:**
- `job_type` (optional): Filter by type
- `status` (optional): Filter by status
- `resource_type` (optional): Filter by resource
- `resource_id` (optional): Filter by specific resource
- `page`, `limit`: Pagination

**Response (200 OK):**
```json
{
  "data": [
    {
      "job_id": "uuid",
      "job_type": "value_proposition_derivation",
      "status": "completed",
      "resource_type": "client",
      "resource_id": "uuid",
      "created_at": "2025-10-30T10:00:00Z",
      "completed_at": "2025-10-30T10:02:30Z"
    }
  ],
  "pagination": { ... }
}
```

---

#### Cancel Job
```
DELETE /api/v1/jobs/{job_id}
```

**Response (200 OK):**
```json
{
  "job_id": "uuid",
  "status": "cancelled",
  "cancelled_at": "2025-10-30T10:01:15Z"
}
```

---

**End of Section 3**

---

## 4. Agent Designs & Workflows

### 4.1 Agent Architecture Overview

The Triton Platform leverages two primary multi-agent teams and several single-purpose agents, all orchestrated via the Agno framework.

#### Agent Team Summary

| Team/Agent | Members | Purpose | Steps Used |
|------------|---------|---------|------------|
| **Research Team** | WebSearchAgent, DocumentAnalysisAgent, SynthesisAgent (dual-mode), ValidationAgent | Research, content generation, AND refinement | 1.2, 1.3, 2.2-2.4 |
| **Analytics Team** | ClinicalAgent, UtilizationAgent, PricingAgent, PharmacyAgent, QuestionToSQLAgent | Data querying & insights | 4, 5 |
| **TemplateGeneratorAgent** | Single agent | Dashboard template generation | 1.4 |

---

### 4.2 Research Team Architecture

**Team Pattern:** Hierarchical with SynthesisAgent as coordinator

#### Research Team Workflow Summary

The Research Team handles **client value proposition derivation** through two primary flows:

**Flow 1: Collateral-Based Derivation** (Well-Defined Path)
```
User Action:
└─> Uploads client documents (ROI sheets, case studies, product info)
└─> Provides additional context (optional free-form text)

API Request:
POST /api/v1/clients/{id}/value-proposition/derive
{
  "mode": "collateral",
  "document_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "additional_context": "Our solution focuses on..."
}

Agent Flow:
SynthesisAgent (Coordinator)
    ├─> DocumentAnalysisAgent
    │   └─> Reads CLIENT documents from S3
    │   └─> Extracts value props, clinical outcomes, ROI metrics
    │   └─> Returns structured findings
    ├─> SynthesisAgent formats findings → ValuePropositionJSON
    │   (using Livongo JSON structure as template)
    └─> ValidationAgent validates JSON schema

Output: Complete ValuePropositionJSON for client
```

**Flow 2: Research-Based Derivation** (Two Sub-Modes)
```
Sub-Mode 2A: Autonomous Research (AI-Driven)
────────────────────────────────────────────
User provides just company name, system researches autonomously

API Request:
{
  "mode": "research",
  "autonomous": true,
  "client_company_name": "Livongo Health",
  "industry_hint": "diabetes management" // optional
}

Agent Flow:
SynthesisAgent (Coordinator)
    ├─> WebSearchAgent (Autonomous Mode)
    │   └─> Performs 15-25 Google searches
    │   └─> Research Areas:
    │       • Company website, mission, products
    │       • Value proposition & messaging
    │       • Clinical outcomes & evidence
    │       • Competitive landscape (identify competitors)
    │       • Market presence (press, news, awards)
    │       • Customer evidence (case studies, testimonials)
    │       • ROI claims and success metrics
    │   └─> Derives likely value propositions based on:
    │       - How company positions itself publicly
    │       - Competitor strategies and differentiation
    │       - Industry standards and market trends
    │       - Published case studies and outcomes
    │   └─> Returns comprehensive research findings
    ├─> SynthesisAgent formats findings → ValuePropositionJSON
    └─> ValidationAgent validates JSON

Output: ValuePropositionJSON derived from public information


Sub-Mode 2B: Manual Prompts (User-Directed)
────────────────────────────────────────────
User provides specific research directions

API Request:
{
  "mode": "research",
  "autonomous": false,
  "prompts": [
    "Research Livongo's diabetes management solution",
    "Identify clinical outcomes and ROI drivers",
    "Focus on remote patient monitoring"
  ]
}

Agent Flow:
SynthesisAgent (Coordinator)
    ├─> WebSearchAgent (Manual Mode)
    │   └─> Performs 5-15 searches based on user prompts
    │   └─> Extracts information aligned with prompt intent
    │   └─> Returns focused research findings
    ├─> SynthesisAgent formats findings → ValuePropositionJSON
    └─> ValidationAgent validates JSON

Output: ValuePropositionJSON based on user-directed research
```

**Key Distinction:**
- **Collateral-Based**: Analyzes CLIENT's own materials (documents they upload)
- **Research-Based (Autonomous)**: AI researches company's public information and derives likely value props based on competitive positioning, market trends, and industry evidence
- **Research-Based (Manual)**: AI follows user-provided research directions

---

```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH TEAM                            │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │         SynthesisAgent (Team Lead)                │    │
│  │  - Coordinates workflow                            │    │
│  │  - Delegates to specialists                        │    │
│  │  - Aggregates results                              │    │
│  │  - Formats final JSON                              │    │
│  └────────────────┬──────────────────────────────────┘    │
│                   │                                         │
│         ┌─────────┼─────────┐                              │
│         ↓         ↓         ↓                              │
│  ┌───────────┐ ┌──────────────┐ ┌──────────────────┐     │
│  │WebSearch  │ │DocumentAnalysis│ │Validation        │     │
│  │Agent      │ │Agent           │ │Agent             │     │
│  │           │ │                │ │                  │     │
│  │- Search   │ │- PDF extract   │ │- Schema check    │     │
│  │- Gather   │ │- Content parse │ │- Retry if needed │     │
│  │- Summarize│ │- Synthesize    │ │- Return valid    │     │
│  └───────────┘ └──────────────┘ └──────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2.1 WebSearchAgent

**Responsibility:** Conduct Google searches, gather web intelligence, summarize findings

**Configuration:**
```python
WebSearchAgent(
    name="WebSearchAgent",
    model=Claude("claude-sonnet-4"),
    tools=[GoogleSearchTool, WebScraperTool],
    instructions=WEBSEARCH_INSTRUCTIONS
)
```

**Prompt Template Structure (Autonomous Mode):**
```
Role: You are a healthcare industry research specialist with expertise in finding
and synthesizing information about healthcare organizations and solutions.

Task: Given client company name "{client_company_name}" {industry_hint}, perform
comprehensive autonomous research to derive their likely value propositions,
competitive positioning, and go-to-market strategy.

Tools Available:
  - google_search(query: str) -> list[SearchResult]
  - scrape_webpage(url: str) -> str

Research Areas (Comprehensive):
1. **Company Information**
   - Official website (about, products, solutions pages)
   - Company mission, vision, value statements
   - Leadership team and expertise areas

2. **Product & Solution Analysis**
   - Core product offerings and features
   - Target customer segments
   - Pricing model (if public)
   - Technology differentiators

3. **Value Proposition & Messaging**
   - How company positions itself
   - Key selling points emphasized in marketing
   - Customer testimonials and case studies
   - ROI claims and success metrics

4. **Clinical & Outcomes Evidence**
   - Published clinical studies
   - White papers and research
   - Health outcome claims
   - Quality measures and benchmarks

5. **Competitive Landscape**
   - Identify 3-5 main competitors
   - How client differs from competitors
   - Unique competitive advantages
   - Market positioning

6. **Market Presence**
   - Press releases (last 12-18 months)
   - News articles and industry coverage
   - Awards and recognitions
   - Partnerships and integrations

7. **Customer Evidence**
   - Client logos and customer lists
   - Case study data (ROI, outcomes, timelines)
   - Customer testimonials
   - Implementation success stories

Search Strategy:
- Start broad: "{client_company_name}" overview
- Drill down: "{client_company_name} ROI", "{client_company_name} clinical outcomes"
- Competitive: "{client_company_name} vs [competitor]"
- Evidence: "{client_company_name} case study", "{client_company_name} white paper"
- Industry: "{industry_hint} solutions comparison", "{industry_hint} vendor analysis"

Output Format:
{
  "searches_performed": 18,
  "queries": ["query1", "query2", ...],
  "company_overview": {
    "name": "...",
    "description": "...",
    "mission": "...",
    "target_markets": ["Health Plans", "Employers"]
  },
  "value_propositions": [
    {
      "name": "Cost Reduction through Prevention",
      "description": "...",
      "evidence_type": "explicit | inferred",
      "supporting_sources": ["url1", "url2"]
    }
  ],
  "clinical_outcomes": [
    {
      "outcome": "HbA1c reduction 1.2%",
      "evidence_type": "published_study | case_study | marketing_claim",
      "source": "url"
    }
  ],
  "roi_framework": {
    "typical_roi_range": "250-400%",
    "payback_period": "12-18 months",
    "cost_savings_areas": ["Complication reduction", "ED avoidance"],
    "evidence_quality": "high | medium | low"
  },
  "competitive_positioning": {
    "main_competitors": ["Competitor A", "Competitor B"],
    "unique_advantages": ["..."],
    "market_differentiators": ["..."]
  },
  "target_audiences": ["Health Plan", "Broker", "Employer"],
  "sources": ["url1", "url2", ...]
}

Constraints:
- Perform 15-25 searches minimum for autonomous mode
- Prioritize: official sources > industry reports > press releases > news articles
- Cross-reference all quantitative claims (ROI %, outcomes, timelines)
- Clearly flag: explicit claims vs. inferred positioning vs. assumptions
- If critical information missing, make reasonable industry-standard assumptions
  and flag them clearly
```

**Prompt Template Structure (Manual Prompts Mode):**
```
Role: You are a healthcare industry research specialist with expertise in finding
and synthesizing information about healthcare organizations and solutions.

Task: Research the client's solution based on user-provided prompts:
{prompts}

Tools Available:
  - google_search(query: str) -> list[SearchResult]
  - scrape_webpage(url: str) -> str

Instructions:
1. Execute research based on each user-provided prompt
2. Formulate targeted search queries aligned with prompt intent
3. Extract relevant information addressing each prompt
4. Synthesize findings into structured summary
5. Cite all sources

Output Format:
{
  "searches_performed": 8,
  "queries": ["query1", "query2"],
  "findings": {
    "company_overview": "...",
    "key_facts": ["...", "..."],
    "value_propositions": [...],
    "clinical_outcomes": [...],
    "roi_data": {...}
  },
  "sources": ["url1", "url2"]
}

Constraints:
- Perform 5-15 searches (user-directed, more focused than autonomous)
- Prioritize official company sources, press releases, industry reports
- Cross-reference facts from multiple sources
- Flag low-confidence information
```

**Expected Output:** Structured research findings dictionary

---

#### 4.2.2 DocumentAnalysisAgent

**Responsibility:** Extract information from CLIENT's uploaded PDF documents using LLM

**Configuration:**
```python
DocumentAnalysisAgent(
    name="DocumentAnalysisAgent",
    model=Claude("claude-sonnet-4"),
    tools=[S3DocumentReader],
    instructions=DOCUMENT_ANALYSIS_INSTRUCTIONS
)
```

**Prompt Template Structure:**
```
Role: You are a document analysis specialist expert in extracting structured
information from healthcare ROI materials, white papers, and marketing collateral.

Task: Analyze the CLIENT's uploaded documents and extract key value propositions, clinical
outcomes, financial metrics, and competitive differentiators from THEIR materials.

Context: The client has uploaded N documents (ROI sheets, case studies, product info) and
may have provided additional free-form text context explaining their value proposition.
You are analyzing THEIR content to understand THEIR value proposition.

Tools Available:
  - read_document(storage_path: str) -> str (returns document text)

Instructions:
1. Read each document thoroughly
2. Identify key sections: value props, clinical data, ROI metrics, target audiences
3. Extract quantitative metrics (percentages, dollar amounts, timelines)
4. Note competitive differentiators
5. Identify target customer segments
6. Flag any missing critical information

Output Format:
{
  "documents_analyzed": 3,
  "extracted_value_propositions": [
    {
      "name": "Cost Reduction through Complication Prevention",
      "description": "...",
      "metrics": {"roi": "340%", "payback_months": 14}
    }
  ],
  "clinical_outcomes": [...],
  "target_audiences": ["Health Plan", "Broker"],
  "competitive_advantages": [...]
}

Constraints:
- Focus on evidence-based claims with data
- Note confidence level for each extracted fact
- Preserve exact numbers/percentages from source
```

**Expected Output:** Extracted document information dictionary

---

#### 4.2.3 SynthesisAgent (Team Coordinator & Refinement)

**Responsibility:** Coordinate team, synthesize findings, format final JSON, AND apply refinement feedback

**Architecture Note:** SynthesisAgent handles both initial value proposition derivation AND iterative refinement. This is the same core task (producing ValuePropositionJSON from inputs), whether those inputs are research findings or user feedback. Keeping this as one agent ensures consistency and allows refinement to reference original research context.

**Configuration:**
```python
SynthesisAgent(
    name="SynthesisAgent",
    model=Claude("claude-sonnet-4"),
    tools=[],  # Coordinates other agents
    instructions=SYNTHESIS_INSTRUCTIONS  # Adapts based on mode
)
```

**Dual-Mode Operation:**

```python
class SynthesisAgent:
    def execute(
        self,
        mode: str,  # "initial" or "refine"
        inputs: dict,
        refinement_feedback: Optional[List[dict]] = None,
        previous_version: Optional[ValuePropositionJSON] = None,
        original_research: Optional[dict] = None  # Cached from initial derivation
    ) -> ValuePropositionJSON:
        """
        Generate value proposition in initial or refinement mode.

        Initial mode: Synthesize from research/documents
        Refine mode: Apply user feedback to existing value proposition
        """
        if mode == "initial":
            return self.synthesize_initial(inputs)
        elif mode == "refine":
            return self.synthesize_refinement(
                previous_version,
                refinement_feedback,
                original_research  # Can reference for context
            )

    def synthesize_initial(self, inputs):
        # Step 1: Gather specialist inputs
        if inputs["mode"] == "research":
            if inputs.get("autonomous", False):
                # Autonomous research mode: WebSearchAgent auto-researches company
                findings = self.delegate_to(
                    WebSearchAgent,
                    {
                        "mode": "autonomous",
                        "client_company_name": inputs["client_company_name"],
                        "industry_hint": inputs.get("industry_hint"),
                        "additional_context": inputs.get("additional_context")
                    }
                )
            else:
                # Manual prompts mode: WebSearchAgent follows user prompts
                findings = self.delegate_to(
                    WebSearchAgent,
                    {
                        "mode": "manual",
                        "prompts": inputs["prompts"],
                        "additional_context": inputs.get("additional_context")
                    }
                )
        elif inputs["mode"] == "collateral":
            findings = self.delegate_to(
                DocumentAnalysisAgent,
                {
                    "document_ids": inputs["document_ids"],
                    "additional_context": inputs.get("additional_context")
                }
            )

        # Step 2: Synthesize into JSON
        draft_json = self.synthesize(findings, livongo_example)

        # Step 3: Validate
        validated = self.delegate_to(ValidationAgent, draft_json)

        return validated

    def synthesize_refinement(self, previous_vp, feedback, original_research):
        # Step 1: Build refinement prompt with feedback
        refined_json = self.refine(previous_vp, feedback, original_research)

        # Step 2: Validate
        validated = self.delegate_to(ValidationAgent, refined_json)

        return validated
```

**Prompt Template - Initial Mode:**
```
Role: You are the Research Team coordinator responsible for synthesizing CLIENT
information into a standardized ValuePropositionJSON format.

Task: Take inputs from WebSearchAgent and/or DocumentAnalysisAgent that analyzed
the CLIENT's materials and produce a complete, valid ValuePropositionJSON for THIS CLIENT.

CRITICAL: You are analyzing the CLIENT's uploaded documents and context text,
NOT the Livongo materials. The Livongo JSON provided below is ONLY a structural
reference showing the target format. Extract information from the CLIENT's materials
and format it to match this structure.

Reference Structure (structural template only):
[Livongo value proposition JSON from Appendix B - shows format/structure to follow]

Client Inputs:
- Extracted content from CLIENT's documents (ROI sheets, case studies, product info)
- Additional context provided by CLIENT: [free-form text explaining their value prop]

Instructions:
1. Review all inputs from specialist agents analyzing CLIENT materials
2. Extract CLIENT's value propositions, clinical claims, ROI data from THEIR content
3. Map CLIENT information to ValuePropositionJSON structure
4. Ensure all required sections are present (following Livongo format):
   - Executive Value Proposition
   - Clinical Outcomes Foundation
   - ROI Opportunities (Tier 1, 2, 3)
   - Financial Modeling Framework
   - Three-Scenario Framework
   - Prospect Assessment Framework
   - Clinical Evidence Base
   - Competitive Positioning
   - Risk Mitigation Framework
   - Sales Enablement Guidance
   - Limitations and Disclaimers
5. Use CLIENT's terminology, data, and claims (not Livongo's)
6. If CLIENT materials lack certain sections, fill gaps with reasonable assumptions
   based on their industry/domain, clearly flagged as assumptions
7. Output valid JSON

Output Format: ValuePropositionJSON (see Appendix A for full schema)

Constraints:
- MUST match Livongo example STRUCTURE (not content)
- Use CLIENT's data and claims, formatted to match the structure
- All numeric values must have units
- All claims must be substantiated by CLIENT materials or flagged as "assumption based on industry standards"
- Output ONLY valid JSON, no additional commentary

Example mapping:
- CLIENT says "reduce HbA1c by 1.0%" → goes in clinical_outcomes section
- CLIENT mentions "18-month ROI" → goes in financial_modeling_framework
- CLIENT provides case study data → goes in clinical_evidence_base
```

**Prompt Template - Refinement Mode:**
```
Role: You are the Research Team coordinator refining a value proposition based
on client feedback while maintaining structural consistency.

Task: Given:
- Original ValuePropositionJSON: [previous version]
- User feedback: [section-level and general feedback]
- Original research context: [cached findings] (for reference)

Produce a refined ValuePropositionJSON that incorporates all feedback.

Instructions:
1. Review original value proposition and feedback
2. Process section feedback:
   - APPROVE: Keep section unchanged
   - REJECT_REMOVE: Remove entire section
   - REJECT_CHANGE: Rewrite section based on specific feedback
3. Apply general feedback across all relevant sections
4. Reference original research if needed for accuracy
5. Maintain structural consistency with Livongo example
6. Ensure all cross-references remain valid after changes
7. Increment version number in metadata

Feedback Processing Rules:
- For REJECT_CHANGE: Focus on the specific issues mentioned
- Preserve approved sections exactly as-is
- If removing a section, adjust dependent sections accordingly
- Maintain professional tone and evidence-based language
- Keep all quantitative data unless specifically contradicted by feedback
- Can reference original research findings to support changes

Output Format: Refined ValuePropositionJSON

Constraints:
- MUST maintain valid JSON structure
- All section IDs must remain consistent
- Do not add sections unless explicitly requested
- Preserve client-specific terminology from feedback
```

**Example Refinement Workflow:**
```
Input (Refinement Mode):
  Previous VP: {...}
  Feedback: [
    {section: "roi_tier_1", action: "reject_remove"},
    {section: "clinical_outcomes", action: "reject_change",
     feedback: "Focus on HbA1c reduction (1.2% avg)"}
  ]
  Original Research: [cached findings about HbA1c from initial research]

Process:
  1. Remove roi_tier_1 section
  2. Rewrite clinical_outcomes with HbA1c emphasis
  3. Reference original research for HbA1c data points
  4. Validate output

Output: Refined VP v2
```

**Expected Output:** ValuePropositionJSON (initial or refined)

---

#### 4.2.4 ValidationAgent

**Responsibility:** Validate agent outputs against Pydantic schemas, retry if invalid

**Configuration:**
```python
ValidationAgent(
    name="ValidationAgent",
    model=None,  # No LLM needed, uses Pydantic
    tools=[PydanticValidator],
    instructions=None
)
```

**Implementation (Python):**
```python
from pydantic import ValidationError
from typing import Dict, Any

class ValidationAgent:
    def __init__(self, schema_class):
        self.schema = schema_class
        self.max_retries = 3

    def validate(self, data: Dict[str, Any], retry_count: int = 0) -> Dict[str, Any]:
        """
        Validate data against Pydantic schema.

        Returns:
            Valid dictionary if successful

        Raises:
            ValidationError if max retries exceeded
        """
        try:
            # Validate using Pydantic
            validated = self.schema(**data)
            return validated.model_dump()

        except ValidationError as e:
            if retry_count >= self.max_retries:
                raise AgentValidationError(
                    f"Validation failed after {self.max_retries} attempts",
                    errors=e.errors()
                )

            # Return to SynthesisAgent with error details
            # SynthesisAgent will retry with error feedback
            error_feedback = self.format_errors(e.errors())
            return {"validation_failed": True, "errors": error_feedback}

    def format_errors(self, errors: list) -> str:
        """Format Pydantic errors for agent feedback"""
        formatted = []
        for error in errors:
            field = " -> ".join(str(loc) for loc in error["loc"])
            formatted.append(f"Field '{field}': {error['msg']}")
        return "\n".join(formatted)
```

**Validation Retry Loop:**
```
SynthesisAgent generates draft
         ↓
ValidationAgent validates
         ↓
   ┌─────┴─────┐
   │  Valid?   │
   └─────┬─────┘
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    │         ↓
    │   Return errors to SynthesisAgent
    │         ↓
    │   SynthesisAgent refines with error context
    │         ↓
    │   ValidationAgent validates again (retry++)
    │         │
    └─────────┴──→ Repeat until valid or max retries
```

**Expected Output:** Validated JSON or validation errors

---

### 4.3 Single-Purpose Agents

#### 4.3.1 TemplateGeneratorAgent (Step 1.4)

**Responsibility:** Generate 5-10 dashboard template variations from value proposition

**Configuration:**
```python
TemplateGeneratorAgent(
    name="TemplateGeneratorAgent",
    model=Claude("claude-sonnet-4"),
    instructions=TEMPLATE_GENERATION_INSTRUCTIONS
)
```

**Prompt Template Structure:**
```
Role: You are a dashboard design specialist expert in creating data visualization
templates for healthcare ROI presentations.

Task: Given an approved ValuePropositionJSON, generate 5-10 dashboard template
variations across multiple categories and target audiences.

Input: ValuePropositionJSON

Instructions:
1. Analyze value propositions to identify key metrics and themes
2. Generate templates across categories:
   - ROI-focused (2-3 templates): Financial impact, payback, savings
   - Clinical outcomes (1-2 templates): Quality measures, health metrics
   - Operational efficiency (1-2 templates): Utilization, care management
   - Competitive positioning (1 template): Market comparisons
   - Comprehensive (1-2 templates): Combined multi-metric views
3. For each template:
   - Define 6-12 widgets (KPI cards, charts, tables)
   - Specify data requirements for each widget
   - Design layout (grid positioning)
   - Choose visual style (colors, spacing)
   - Customize for target audience
4. Ensure templates span all target audiences:
   - Health Plan
   - Broker
   - PBM
   - TPA
   - Medical Management

Widget Types Available:
- kpi_card: Single metric with trend
- line_chart: Time-series trends
- bar_chart: Categorical comparisons
- waterfall_chart: Sequential impact
- pie_chart: Composition breakdown
- table: Ranked lists or detailed data
- gauge: Progress toward goal
- heatmap: Multi-dimensional data

Output Format: Array of DashboardTemplateJSON objects (see Appendix A)

Template Structure Example:
{
  "id": "uuid",
  "name": "Diabetes ROI Executive Dashboard",
  "description": "Financial impact for C-suite",
  "category": "roi-focused",
  "target_audience": "Health Plan",
  "key_features": ["24-month ROI", "Savings waterfall", "Payback analysis"],
  "widgets": [
    {
      "id": "widget-1",
      "type": "kpi_card",
      "title": "24-Month ROI",
      "data_requirements": {
        "metrics": ["total_savings", "program_cost"],
        "calculation": "((savings - cost) / cost) * 100"
      },
      "position": {"row": 1, "col": 1, "width": 3, "height": 2}
    }
  ],
  "visual_style": {
    "primary_color": "#2563eb",
    "accent_color": "#10b981",
    "layout": "balanced"
  },
  "recommended_use_case": "C-suite and board presentations"
}

Constraints:
- Generate exactly 5-10 templates
- Each template must have 6-12 widgets
- Distribute templates across all categories
- Cover all target audiences
- Widget data_requirements must be specific and queryable
```

**Expected Output:** Array of 5-10 DashboardTemplateJSON objects

---

### 4.4 Analytics Team Architecture

**Team Pattern:** Parallel execution with QuestionToSQLAgent as coordinator

```
┌─────────────────────────────────────────────────────────────┐
│                    ANALYTICS TEAM                           │
│                                                             │
│              QuestionToSQLAgent (Coordinator)               │
│                       ↑                                     │
│         ┌─────────────┼─────────────┐                      │
│         │             │             │                      │
│    ┌────┴───┐   ┌────┴────┐   ┌───┴────┐   ┌─────────┐  │
│    │Clinical│   │Pricing  │   │Util.   │   │Pharmacy │  │
│    │Agent   │   │Agent    │   │Agent   │   │Agent    │  │
│    └────┬───┘   └────┬────┘   └───┬────┘   └────┬────┘  │
│         │            │            │             │        │
│         └────────────┴────────────┴─────────────┘        │
│                  Parallel Execution                       │
│                                                             │
│  Each agent:                                               │
│  1. Identifies data needs                                  │
│  2. Formulates natural language questions                  │
│  3. Sends questions to QuestionToSQLAgent                  │
│  4. Receives SQL results                                   │
│  5. Analyzes and stores insights                           │
└─────────────────────────────────────────────────────────────┘
```

#### 4.4.1 QuestionToSQLAgent (Coordinator)

**Responsibility:** Translate natural language questions to SQL, execute against Clickhouse

**Configuration:**
```python
QuestionToSQLAgent(
    name="QuestionToSQLAgent",
    model=Claude("claude-sonnet-4"),
    tools=[ClickhouseQueryTool],
    instructions=QUESTION_TO_SQL_INSTRUCTIONS,
    context={
        "schema": CLICKHOUSE_SCHEMA_DOCS,
        "example_queries": EXAMPLE_SQL_QUERIES
    }
)
```

**Prompt Template Structure:**
```
Role: You are a healthcare analytics SQL specialist expert in translating
analytical questions into optimized Clickhouse SQL queries.

Context: You have access to a Clickhouse database with the following schema:
[Schema documentation loaded as context]

Available Tables:
- member_demographics (member_id, age, gender, risk_score, ...)
- medical_claims (claim_id, member_id, service_date, diagnosis_codes, cost, ...)
- pharmacy_claims (claim_id, member_id, drug_name, quantity, cost, ...)
- utilization_summary (member_id, month, ed_visits, hospitalizations, ...)
- quality_metrics (member_id, measure_name, value, date, ...)

Task: Given a natural language question from a category agent, generate an
optimized SQL query to answer it.

Instructions:
1. Parse the question to understand data requirements
2. Identify relevant tables and columns
3. Generate SQL query using Clickhouse syntax
4. Optimize for performance (use appropriate indexes, aggregations)
5. Handle edge cases (nulls, missing data)
6. Execute query and return results
7. Format results for agent consumption

Question Examples:
Q: "What is the average HbA1c for members with diabetes?"
SQL:
  SELECT avg(value) as avg_hba1c
  FROM quality_metrics
  WHERE measure_name = 'HbA1c'
    AND member_id IN (
      SELECT DISTINCT member_id
      FROM medical_claims
      WHERE diagnosis_codes LIKE '%E11%'  -- Diabetes ICD-10
    )

Q: "What is the diabetes-related cost PMPM?"
SQL:
  SELECT
    sum(cost) / count(DISTINCT member_id) / 12 as pmpm
  FROM medical_claims
  WHERE diagnosis_codes LIKE '%E11%'
    AND service_date >= today() - INTERVAL 12 MONTH

Output Format:
{
  "question": "original question",
  "sql": "generated SQL",
  "results": [...],
  "row_count": 1234,
  "execution_time_ms": 45
}

Constraints:
- Use Clickhouse-specific functions (e.g., arrayJoin, groupArray)
- Optimize for columnar storage
- Limit result sets to reasonable size (< 10000 rows)
- Handle date ranges appropriately
- Use appropriate aggregations
```

**Expected Output:** SQL query results formatted as JSON

---

#### 4.4.2 ClinicalAgent

**Responsibility:** Analyze clinical outcomes, quality measures, disease management

**Configuration:**
```python
ClinicalAgent(
    name="ClinicalAgent",
    model=Claude("claude-sonnet-4"),
    instructions=CLINICAL_AGENT_INSTRUCTIONS
)
```

**Prompt Template Structure:**
```
Role: You are a clinical outcomes analyst specializing in healthcare quality
metrics, disease management, and clinical evidence.

Task: Analyze clinical data to support value propositions or populate dashboard widgets.

Context:
- You work as part of the Analytics Team
- You can ask questions to QuestionToSQLAgent to get data
- Your goal is to extract clinical insights from prospect data

Instructions for Value Prop Generation (Step 4):
1. Review ranked value propositions
2. Identify clinical claims that need data support
3. Formulate questions for QuestionToSQLAgent:
   - Baseline clinical metrics (HbA1c, blood pressure, etc.)
   - Complication rates
   - Quality measure scores (HEDIS, Stars)
   - Disease prevalence
4. Analyze results and calculate:
   - Current state metrics
   - Projected improvements based on clinical evidence
   - Confidence levels
5. Format insights for storage

Instructions for Dashboard Generation (Step 5):
1. Review dashboard template widgets
2. For each clinical widget, identify data needs
3. Formulate questions to gather:
   - KPI values (e.g., "% controlled HbA1c")
   - Trend data (e.g., "monthly quality scores")
   - Distributions (e.g., "risk stratification")
4. Format results for widget display

Question Examples:
- "What percentage of diabetic members have controlled HbA1c (<7%)?"
- "What is the baseline complication rate for diabetes members?"
- "What are the HEDIS diabetes care measure scores?"

Output Format (Value Prop):
{
  "priority_id": "vp-1",
  "clinical_analysis": {
    "baseline": {
      "hba1c_control_rate": 0.42,
      "complication_rate": 0.18,
      "member_count": 12847
    },
    "projected_impact": {
      "hba1c_improvement": 0.15,
      "complication_reduction": 0.05,
      "confidence": "high"
    }
  }
}

Output Format (Dashboard):
{
  "widget_id": "clinical_kpi_1",
  "data": {
    "value": 42,
    "display": "42% Controlled",
    "trend": "up",
    "benchmark": 38
  }
}
```

**Expected Output:** Clinical insights or widget data

---

#### 4.4.3 PricingAgent

**Responsibility:** ROI calculations, cost analysis, financial impact

**Configuration:**
```python
PricingAgent(
    name="PricingAgent",
    model=Claude("claude-sonnet-4"),
    instructions=PRICING_AGENT_INSTRUCTIONS
)
```

**Prompt Template Structure:**
```
Role: You are a healthcare financial analyst expert in ROI modeling, cost
analysis, and financial impact projections.

Task: Calculate financial metrics to support value propositions or populate
dashboard widgets.

Instructions for Value Prop Generation (Step 4):
1. Review value propositions for financial claims
2. Formulate questions to gather:
   - Current costs (PMPM, total cost of care)
   - Cost drivers (complication costs, utilization costs)
   - Member counts and eligibility
3. Calculate ROI metrics:
   - Projected savings (complication avoidance, utilization reduction)
   - Program costs
   - ROI percentage: ((savings - cost) / cost) * 100
   - Payback period: months until cumulative savings > costs
   - Net savings: savings - costs
4. Model different scenarios (conservative, moderate, aggressive)

Instructions for Dashboard Generation (Step 5):
1. Identify financial widgets in templates
2. Calculate KPIs:
   - ROI percentage
   - Payback period
   - Total savings
   - PMPM impact
3. Generate visualization data:
   - Savings waterfall components
   - ROI trend over time
   - Cost comparison charts

Question Examples:
- "What is the current diabetes-related cost PMPM?"
- "What is the total cost of diabetes complications in the last 12 months?"
- "How many members have uncontrolled diabetes?"

Calculation Examples:
ROI Calculation:
  program_cost = members * pmpm_fee * 24 months
  savings = complication_reduction * avg_complication_cost * members
  roi = ((savings - program_cost) / program_cost) * 100

Payback Period:
  monthly_savings = annual_savings / 12
  monthly_cost = program_cost / 24
  payback_months = ceil(program_cost / (monthly_savings - monthly_cost))

Output Format (Value Prop):
{
  "priority_id": "vp-1",
  "financial_analysis": {
    "baseline": {
      "diabetes_cost_pmpm": 245.50,
      "total_annual_cost": 37845000,
      "high_risk_members": 12847
    },
    "projected_impact": {
      "savings_24_month": 14500000,
      "program_cost_24_month": 3200000,
      "net_savings": 11300000,
      "roi_percentage": 340,
      "payback_months": 14
    }
  }
}
```

**Expected Output:** Financial metrics or widget data

---

#### 4.4.4 UtilizationAgent

**Responsibility:** ED visits, hospitalizations, service utilization analysis

**Configuration:**
```python
UtilizationAgent(
    name="UtilizationAgent",
    model=Claude("claude-sonnet-4"),
    instructions=UTILIZATION_AGENT_INSTRUCTIONS
)
```

**Prompt Template Structure:**
```
Role: You are a healthcare utilization analyst expert in ED visits, hospital
admissions, readmissions, and service utilization patterns.

Task: Analyze utilization data to support value propositions or dashboard widgets.

Focus Areas:
- Emergency department visit rates
- Hospital admission rates
- 30-day readmission rates
- Avoidable utilization
- Service mix analysis

Instructions: [Similar to ClinicalAgent but focused on utilization metrics]

Question Examples:
- "What is the diabetes-related ED visit rate per 1000 members?"
- "What is the avoidable hospitalization rate?"
- "What are the top reasons for ED visits among diabetic members?"

Output Format: [Similar to ClinicalAgent]
```

---

#### 4.4.5 PharmacyAgent

**Responsibility:** Drug costs, adherence, formulary analysis

**Configuration:**
```python
PharmacyAgent(
    name="PharmacyAgent",
    model=Claude("claude-sonnet-4"),
    instructions=PHARMACY_AGENT_INSTRUCTIONS
)
```

**Prompt Template Structure:**
```
Role: You are a pharmacy analyst expert in drug costs, medication adherence,
and formulary optimization.

Task: Analyze pharmacy data to support value propositions or dashboard widgets.

Focus Areas:
- Medication adherence (PDC)
- Drug costs and trends
- Formulary utilization
- Generic vs brand mix
- High-cost drug analysis

Instructions: [Similar to ClinicalAgent but focused on pharmacy metrics]

Question Examples:
- "What is the medication adherence rate for diabetes drugs?"
- "What is the average monthly cost of diabetes medications?"
- "What percentage of members are on brand vs generic medications?"

Output Format: [Similar to ClinicalAgent]
```

---

### 4.5 Agent Error Handling & Retry Logic

#### Retry Strategy

All agents implement exponential backoff retry logic for transient failures:

```python
class AgentRetryMixin:
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1.0  # seconds
        self.max_delay = 30.0

    def execute_with_retry(self, func, *args, **kwargs):
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)

            except TransientError as e:
                if attempt == self.max_retries:
                    raise

                delay = min(
                    self.base_delay * (2 ** attempt),
                    self.max_delay
                )
                time.sleep(delay)
                continue

            except PermanentError as e:
                # Don't retry permanent errors
                raise
```

#### Error Types

| Error Type | Retry? | Handling |
|------------|--------|----------|
| **LLM API Timeout** | Yes (3x) | Exponential backoff |
| **LLM Rate Limit** | Yes (3x) | Exponential backoff with longer delay |
| **Validation Error** | Yes (3x) | Return error feedback to agent for refinement |
| **Database Connection** | Yes (3x) | Reconnect with backoff |
| **SQL Syntax Error** | No | Fail job, log for debugging |
| **Document Not Found** | No | Fail job immediately |
| **Schema Mismatch** | No | Fail job, requires code fix |

#### Circuit Breaker Pattern

For external service calls (LLM API, database):

```python
class CircuitBreaker:
    """
    Prevents cascading failures by opening circuit after threshold failures
    """
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED | OPEN | HALF_OPEN

    def call(self, func):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Circuit breaker is OPEN")

        try:
            result = func()
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

---

### 4.6 Agent Workflow State Machines

#### Research Team Workflow (Steps 1.2, 2.2)

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ↓
┌──────────────┐
│  Initialize  │
│  SynthesisAgent
└──────┬──────┘
       │
       ↓
┌──────────────────────┐
│  Determine Mode      │
│  (research/collateral)│
└──────┬───────────────┘
       │
   ┌───┴────┐
   │  Mode? │
   └───┬────┘
       │
  ┌────┴─────┐
  │          │
 Research  Collateral
  │          │
  ↓          ↓
┌──────┐  ┌──────────────┐
│Web   │  │Document      │
│Search│  │Analysis      │
│Agent │  │Agent         │
└──┬───┘  └──────┬───────┘
   │             │
   └─────┬───────┘
         │
         ↓
   ┌──────────┐
   │Synthesis │
   │Agent     │
   └────┬─────┘
        │
        ↓
   ┌──────────┐
   │Validation│
   │Agent     │
   └────┬─────┘
        │
    ┌───┴────┐
    │ Valid? │
    └───┬────┘
        │
   ┌────┴─────┐
   │          │
  Yes        No
   │          │
   │          ↓
   │    ┌──────────┐
   │    │ Retry++  │
   │    │ < Max?   │
   │    └────┬─────┘
   │         │
   │    ┌────┴────┐
   │    │         │
   │   Yes       No
   │    │         │
   │    │         ↓
   │    │    ┌────────┐
   │    │    │ FAILED │
   │    │    └────────┘
   │    ↓
   │  Return to
   │  Synthesis
   │  with errors
   │    │
   └────┴─────┐
              ↓
        ┌──────────┐
        │ SUCCESS  │
        │ Store    │
        │ Result   │
        └──────────┘
```

#### Analytics Team Workflow (Steps 4-5)

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ↓
┌────────────────────┐
│ Initialize         │
│ Analytics Team     │
│ (4 category agents)│
└──────┬─────────────┘
       │
       ↓
┌────────────────────┐
│ Load Context       │
│ - Value props (S4) │
│ - Templates (S5)   │
└──────┬─────────────┘
       │
       ↓
┌────────────────────────┐
│ Parallel Agent         │
│ Execution              │
│                        │
│ ┌────────────────────┐│
│ │ ClinicalAgent      ││
│ │ - Identify needs   ││
│ │ - Ask questions    ││
│ │ - Analyze results  ││
│ └────────────────────┘│
│                        │
│ ┌────────────────────┐│
│ │ PricingAgent       ││
│ │ [same flow]        ││
│ └────────────────────┘│
│                        │
│ [UtilizationAgent]     │
│ [PharmacyAgent]        │
│                        │
│ All agents query       │
│ QuestionToSQLAgent     │
└──────┬─────────────────┘
       │
       ↓
┌────────────────────┐
│ Aggregate Results  │
│ Format as complete │
│ JSON documents     │
└──────┬─────────────┘
       │
       ↓
┌────────────────────┐
│ Store in Postgres  │
│ JSONB              │
│ - Value prop data  │
│ - Dashboard data   │
└──────┬─────────────┘
       │
       ↓
┌────────────────────┐
│ SUCCESS            │
│ Update job status  │
└────────────────────┘
```

---

**End of Section 4**

---

## 5. Database Schemas

### 5.1 Schema Overview

The Triton Platform uses two databases with distinct purposes:

| Database | Purpose | Data Types | Access Pattern |
|----------|---------|------------|----------------|
| **PostgreSQL** | Operational data, ACID transactions | Clients, prospects, jobs, value props, templates | CRUD, frequent writes, relational queries |
| **Clickhouse** | Analytics data, pre-computed insights | Member data, claims, utilization, dashboard widgets | Read-heavy, aggregations, time-series |

**Data Flow:**
```
PostgreSQL (Transactional)
  ↓
Agents execute workflows
  ↓
Clickhouse (Analytics)
  ↓
MARÉ Frontend (Presentation)
```

---

### 5.2 PostgreSQL Schemas (Operational Data)

#### 5.2.1 Clients Table

Stores client organization information.

```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    settings JSONB DEFAULT '{}',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,

    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'deleted'))
);

CREATE INDEX idx_clients_status ON clients(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_clients_company_name ON clients(company_name);
CREATE INDEX idx_clients_created_at ON clients(created_at DESC);
```

**Columns:**
- `id`: Unique identifier
- `company_name`: Client organization name
- `industry`: Healthcare sector (e.g., "Diabetes Management")
- `settings`: JSONB for flexible configuration (branding, preferences)
- `status`: active | inactive | deleted
- `deleted_at`: Soft delete timestamp

---

#### 5.2.2 Documents Table

Stores uploaded documents (PDFs, collateral).

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    storage_path TEXT NOT NULL,
    mime_type VARCHAR(100) DEFAULT 'application/pdf',
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_document_type CHECK (document_type IN ('collateral', 'roi_sheet', 'whitepaper', 'other'))
);

CREATE INDEX idx_documents_client_id ON documents(client_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at DESC);
```

**Columns:**
- `storage_path`: S3 URI or compatible storage path
- `document_type`: Category for filtering
- `file_size`: Bytes, for validation

---

#### 5.2.3 Value Propositions Table

Stores client and prospect value propositions.

```sql
CREATE TABLE value_propositions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    prospect_id UUID REFERENCES prospects(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    mode VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMP,
    approved_by UUID,

    CONSTRAINT chk_vp_owner CHECK (
        (client_id IS NOT NULL AND prospect_id IS NULL) OR
        (client_id IS NULL AND prospect_id IS NOT NULL)
    ),
    CONSTRAINT chk_mode CHECK (mode IN ('research', 'collateral', 'ranked')),
    CONSTRAINT chk_status CHECK (status IN ('draft', 'in_review', 'approved'))
);

CREATE INDEX idx_vp_client_id ON value_propositions(client_id) WHERE client_id IS NOT NULL;
CREATE INDEX idx_vp_prospect_id ON value_propositions(prospect_id) WHERE prospect_id IS NOT NULL;
CREATE INDEX idx_vp_status ON value_propositions(status);
CREATE INDEX idx_vp_version ON value_propositions(version DESC);
```

**Columns:**
- `client_id` OR `prospect_id`: One must be set (not both)
- `version`: Increments with each refinement
- `mode`: Derivation method (research/collateral) or ranked
- `data`: Full ValuePropositionJSON or RankedValuePropositionJSON
- `approved_at`: When finalized

---

#### 5.2.4 Value Proposition Feedback Table

Stores review feedback rounds.

```sql
CREATE TABLE value_proposition_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    value_proposition_id UUID NOT NULL REFERENCES value_propositions(id) ON DELETE CASCADE,
    round INTEGER NOT NULL,
    feedback_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by UUID
);

CREATE INDEX idx_vpf_value_prop_id ON value_proposition_feedback(value_proposition_id);
CREATE INDEX idx_vpf_round ON value_proposition_feedback(round);
```

**Columns:**
- `round`: Feedback iteration number (0, 1, 2, ...)
- `feedback_data`: Section-level feedback and general comments

---

#### 5.2.5 Dashboard Templates Table

Stores generated dashboard templates.

```sql
CREATE TABLE dashboard_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    target_audience VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'generated',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMP,

    CONSTRAINT chk_category CHECK (category IN (
        'roi-focused', 'clinical-outcomes', 'operational-efficiency',
        'competitive-positioning', 'comprehensive'
    )),
    CONSTRAINT chk_target_audience CHECK (target_audience IN (
        'Health Plan', 'Broker', 'PBM', 'TPA', 'Medical Management'
    )),
    CONSTRAINT chk_status CHECK (status IN ('generated', 'approved', 'removed'))
);

CREATE INDEX idx_dt_client_id ON dashboard_templates(client_id);
CREATE INDEX idx_dt_category ON dashboard_templates(category);
CREATE INDEX idx_dt_target_audience ON dashboard_templates(target_audience);
CREATE INDEX idx_dt_status ON dashboard_templates(status);
```

**Columns:**
- `data`: Full DashboardTemplateJSON with widget definitions
- `category`: Dashboard focus area
- `target_audience`: Prospect type this is designed for
- `status`: Lifecycle state

---

#### 5.2.6 Prospects Table

Stores prospect (sales opportunity) information.

```sql
CREATE TABLE prospects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    notes TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'created',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,

    CONSTRAINT chk_status CHECK (status IN (
        'created', 'researching', 'researched', 'analyzing', 'completed', 'archived'
    ))
);

CREATE INDEX idx_prospects_client_id ON prospects(client_id);
CREATE INDEX idx_prospects_status ON prospects(status);
CREATE INDEX idx_prospects_company_name ON prospects(company_name);
CREATE INDEX idx_prospects_created_at ON prospects(created_at DESC);
```

**Columns:**
- `status`: Workflow state
- `contact_*`: Sales contact information
- `notes`: Free-form notes

---

#### 5.2.7 Prospect Company Information Table

Stores researched prospect company data.

```sql
CREATE TABLE prospect_company_information (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID NOT NULL UNIQUE REFERENCES prospects(id) ON DELETE CASCADE,
    data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pci_prospect_id ON prospect_company_information(prospect_id);
CREATE INDEX idx_pci_subsegment ON prospect_company_information((data->'classification'->>'subsegment'));
```

**Columns:**
- `data`: Full CompanyInformationJSON from research
- `prospect_id`: One-to-one relationship with prospects
- JSON index on `subsegment` for filtering by prospect type

---

#### 5.2.8 Jobs Table

Tracks all async job executions.

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    resource_type VARCHAR(50),
    resource_id UUID,
    input_data JSONB,
    output_data JSONB,
    progress JSONB,
    error_data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    failed_at TIMESTAMP,

    CONSTRAINT chk_job_type CHECK (job_type IN (
        'value_proposition_derivation',
        'value_proposition_refinement',
        'dashboard_template_generation',
        'prospect_company_research',
        'value_proposition_ranking',
        'analytics_value_prop_generation',
        'analytics_dashboard_generation'
    )),
    CONSTRAINT chk_status CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    )),
    CONSTRAINT chk_resource_type CHECK (resource_type IN ('client', 'prospect', NULL))
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_type ON jobs(job_type);
CREATE INDEX idx_jobs_resource ON jobs(resource_type, resource_id);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_completed_at ON jobs(completed_at DESC) WHERE completed_at IS NOT NULL;
```

**Columns:**
- `job_type`: Identifies the agent/workflow
- `status`: Job lifecycle state
- `resource_type/resource_id`: Link to client or prospect
- `progress`: Real-time progress updates (JSONB)
- `error_data`: Error details if failed

---

#### 5.2.9 Celery Task Tracking (Optional)

If using Celery's database result backend:

```sql
-- Celery manages these tables automatically
-- Listed here for completeness

CREATE TABLE celery_taskmeta (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(155) UNIQUE,
    status VARCHAR(50),
    result BYTEA,
    date_done TIMESTAMP,
    traceback TEXT
);

CREATE TABLE celery_tasksetmeta (
    id SERIAL PRIMARY KEY,
    taskset_id VARCHAR(155) UNIQUE,
    result BYTEA,
    date_done TIMESTAMP
);
```

---

#### 5.2.10 Prospect Value Proposition Data Table

Stores pre-computed value proposition insights from Analytics Team (Step 4).

```sql
CREATE TABLE prospect_value_proposition_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id),
    value_proposition_data JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(prospect_id)
);

CREATE INDEX idx_prospect_value_prop_lookup
ON prospect_value_proposition_data(prospect_id);

CREATE INDEX idx_prospect_value_prop_jsonb
ON prospect_value_proposition_data USING GIN(value_proposition_data);
```

**Purpose:** Store complete pre-computed value proposition insights for fast runtime serving

**JSONB Structure:**
```json
{
  "value_propositions": [
    {
      "priority_id": "vp-001",
      "priority_name": "Reduce Diabetes Complications",
      "rank": 1,
      "baseline_metrics": {
        "current_hba1c_avg": 8.2,
        "uncontrolled_members": 450,
        "current_complication_rate": 0.15
      },
      "projected_impact": {
        "hba1c_improvement": 1.1,
        "complications_avoided": 68,
        "roi_percentage": 340
      },
      "supporting_evidence": {
        "queries_executed": 12,
        "data_sources": ["claims", "clinical"],
        "confidence_level": "high"
      },
      "visualizations": [
        {
          "type": "chart",
          "chart_type": "bar",
          "data": [...]
        }
      ]
    }
  ],
  "metadata": {
    "generated_at": "2024-01-15T10:30:00Z",
    "analytics_version": "1.0"
  }
}
```

**Indexes:**
- `idx_prospect_value_prop_lookup`: Fast retrieval by prospect_id
- `idx_prospect_value_prop_jsonb`: GIN index for JSONB queries if needed

**Performance:** Single indexed query returns complete value prop analysis (~10ms)

---

#### 5.2.11 Prospect Dashboard Data Table

Stores pre-computed dashboard widget data from Analytics Team (Step 5).

```sql
CREATE TABLE prospect_dashboard_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id),
    template_id UUID NOT NULL,
    dashboard_data JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(prospect_id, template_id)
);

CREATE INDEX idx_prospect_dashboard_lookup
ON prospect_dashboard_data(prospect_id, template_id);

CREATE INDEX idx_prospect_dashboard_jsonb
ON prospect_dashboard_data USING GIN(dashboard_data);
```

**Purpose:** Store complete pre-formatted dashboard data per template for instant rendering

**JSONB Structure:**
```json
{
  "template_id": "diabetes-roi-executive",
  "template_name": "Diabetes ROI Executive Dashboard",
  "widgets": {
    "kpi_roi_percentage": {
      "type": "kpi",
      "value": 340,
      "display": "340%",
      "trend": "up",
      "comparison": "vs. target 300%"
    },
    "kpi_payback_period": {
      "type": "kpi",
      "value": 14,
      "display": "14 months",
      "trend": "down"
    },
    "chart_savings_waterfall": {
      "type": "chart",
      "chart_type": "waterfall",
      "data": [
        {"category": "MI Prevention", "value": 850000},
        {"category": "Stroke Prevention", "value": 620000},
        {"category": "Program Cost", "value": -400000}
      ]
    },
    "chart_utilization_trends": {
      "type": "chart",
      "chart_type": "line",
      "data": [
        {"month": "Jan", "ed_visits": 145, "hospitalizations": 62},
        {"month": "Feb", "ed_visits": 138, "hospitalizations": 58}
      ]
    }
  },
  "metadata": {
    "generated_at": "2024-01-15T10:35:00Z",
    "analytics_version": "1.0"
  }
}
```

**Indexes:**
- `idx_prospect_dashboard_lookup`: Fast retrieval by prospect + template
- `idx_prospect_dashboard_jsonb`: GIN index for JSONB queries if needed

**Performance:** Single indexed query returns complete dashboard JSON (~10ms)

---

### 5.3 Clickhouse Schemas (Analytics Data)

**Note:** Clickhouse schemas for prospect analytics data are **already in place** via the existing ARGO platform. ARGO handles all data ingestion, transformation, and storage of healthcare analytics data into Clickhouse.

#### Existing ARGO Clickhouse Schema

The Triton Platform will **leverage existing ARGO Clickhouse schemas** for all prospect data storage and querying. These schemas include:

- **Member/Patient Demographics**
- **Medical Claims Data**
- **Pharmacy Claims Data**
- **Utilization Summaries**
- **Quality Measures (HEDIS, Stars)**
- **Risk Stratification Data**

**Integration Approach:**
1. ARGO processes uploaded prospect data files (Step 3)
2. ARGO writes standardized data to existing Clickhouse schemas
3. Triton Analytics Team (Question-to-SQL Agent) queries ARGO's Clickhouse tables during generation (Steps 4-5)
4. Pre-computed results stored in Postgres JSONB (see Sections 5.2.10 and 5.2.11)

**Key Points:**
- **No new Clickhouse schemas required** - use existing ARGO tables
- **Columnar storage** optimized for analytics workloads
- **MergeTree engines** with automatic data sorting/merging
- **Partitioning by date** for efficient time-series queries
- **Materialized views** (optional) for pre-computed aggregations

**For detailed schema documentation, refer to existing ARGO platform documentation.**

**Triton-Specific Considerations:**
- `prospect_id` field must be present in all tables to link Triton prospects to ARGO data
- Question-to-SQL Agent will generate queries against ARGO's existing table structure
- No schema modifications required for Triton MVP

---

### 5.4 Database Relationships

#### Cross-Database Relationships

```
PostgreSQL                                      Clickhouse
─────────────────────────────────────────────────────────────────────
clients (id)
    ↓
prospects (id, client_id)  ←───────────────→  prospect_id (in all tables)
    ↓                                              ↓
value_propositions (client-level)            ARGO raw data:
dashboard_templates (client-level)           - member_demographics
    ↓                                        - medical_claims
prospect_value_proposition_data              - pharmacy_claims
  (pre-computed, prospect-specific)          - utilization_summary
prospect_dashboard_data                      - quality_measures
  (pre-computed, prospect-specific)          (queried during generation)
```

**Key Points:**
- **No Foreign Keys** between PostgreSQL and Clickhouse
- **Logical Linking** via `prospect_id` UUID
- **Eventual Consistency:** Analytics data populated asynchronously
- **MVP Architecture:**
  - Clickhouse stores ARGO raw data only
  - Pre-computed results stored in Postgres JSONB for fast runtime serving
  - Analytics Team queries Clickhouse during generation, stores results in Postgres

---

### 5.5 Data Migration & Seeding

#### Initial Setup Script

```sql
-- PostgreSQL initialization
-- File: migrations/001_initial_schema.sql

BEGIN;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tables in dependency order
\i tables/clients.sql
\i tables/documents.sql
\i tables/prospects.sql
\i tables/value_propositions.sql
\i tables/value_proposition_feedback.sql
\i tables/dashboard_templates.sql
\i tables/prospect_company_information.sql
\i tables/jobs.sql

-- Create indexes
\i indexes/clients_indexes.sql
-- ... (additional index files)

-- Create triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prospects_updated_at BEFORE UPDATE ON prospects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_value_propositions_updated_at BEFORE UPDATE ON value_propositions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
```

#### Clickhouse Initialization

**Note:** Clickhouse schemas are **already managed by ARGO platform**. No Triton-specific initialization required.

**ARGO handles:**
- Database creation and management
- Table schemas for healthcare data (demographics, claims, utilization, quality measures)
- Data ingestion and transformation
- Indexing and partitioning strategies

**Triton requirements:**
- Ensure `prospect_id` field is populated when ARGO processes Triton prospect data
- Question-to-SQL Agent configured with ARGO Clickhouse connection details
- Read-only access for Triton Analytics Team agents

---

**End of Section 5**

---

## 6. Test Strategy & Specifications

### 6.1 Testing Philosophy

The Triton Platform testing strategy prioritizes **output correctness** over integration complexity. Given that:
- LLM responses are non-deterministic
- Integration tests with real LLMs are expensive
- The critical requirement is **valid, structured JSON output**

We focus on:
1. **Schema Validation:** Ensure all agent outputs match expected Pydantic schemas
2. **Mock LLM Responses:** Unit test agents with predefined LLM responses
3. **Test Fixtures:** Maintain reference JSON examples (Livongo, Wellmark) as ground truth
4. **Prompt Iteration:** Test prompt effectiveness through expected output matching

**Testing Levels:**
- ✅ **Unit Tests:** Agent logic with mocked LLMs (Primary focus)
- ✅ **Schema Tests:** Pydantic validation of all output formats
- ❌ **Integration Tests:** Skipped for cost savings (no real LLM calls)
- ❌ **End-to-End Tests:** Deferred to manual testing phase

---

### 6.2 Unit Testing with Mock LLMs

#### 6.2.1 Mock LLM Framework

**Purpose:** Test agent logic without real LLM API calls

**Implementation:**

```python
# tests/mocks/mock_llm.py

from typing import Dict, Any, Callable
from unittest.mock import Mock

class MockLLM:
    """
    Mock LLM that returns predefined responses based on prompt patterns
    """
    def __init__(self, response_map: Dict[str, Any] = None):
        """
        Args:
            response_map: Dict mapping prompt keywords to responses
        """
        self.response_map = response_map or {}
        self.call_count = 0
        self.call_history = []

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response based on prompt pattern matching
        """
        self.call_count += 1
        self.call_history.append({"prompt": prompt, "kwargs": kwargs})

        # Pattern matching
        for keyword, response in self.response_map.items():
            if keyword.lower() in prompt.lower():
                if callable(response):
                    return response(prompt)
                return response

        # Default response if no pattern match
        return self._default_response()

    def _default_response(self) -> str:
        """Default fallback response"""
        return '{"error": "No mock response defined for this prompt"}'

    def reset(self):
        """Reset call tracking"""
        self.call_count = 0
        self.call_history = []


class MockLLMFactory:
    """
    Factory for creating mock LLMs with predefined response patterns
    """
    @staticmethod
    def create_value_prop_llm() -> MockLLM:
        """LLM that returns valid ValuePropositionJSON"""
        with open('tests/fixtures/livongo_value_proposition_derived.json') as f:
            valid_response = f.read()

        return MockLLM(response_map={
            "value proposition": valid_response,
            "synthesize": valid_response,
            "clinical outcomes": valid_response
        })

    @staticmethod
    def create_company_research_llm() -> MockLLM:
        """LLM that returns valid CompanyInformationJSON"""
        with open('tests/fixtures/wellmark_company_information.json') as f:
            valid_response = f.read()

        return MockLLM(response_map={
            "wellmark": valid_response,
            "company research": valid_response,
            "prospect research": valid_response
        })

    @staticmethod
    def create_invalid_json_llm() -> MockLLM:
        """LLM that returns invalid JSON (for testing validation)"""
        return MockLLM(response_map={
            ".*": '{"incomplete": "json"'  # Invalid JSON
        })
```

---

#### 6.2.2 Research Team Tests

**Test File:** `tests/agents/test_research_team.py`

```python
import pytest
from unittest.mock import Mock, patch
from agents.research_team import ResearchTeam, SynthesisAgent
from tests.mocks.mock_llm import MockLLMFactory
from schemas.value_proposition import ValuePropositionSchema

class TestResearchTeam:
    """Test Research Team agent workflows"""

    def setup_method(self):
        """Setup before each test"""
        self.mock_llm = MockLLMFactory.create_value_prop_llm()
        self.research_team = ResearchTeam(llm=self.mock_llm)

    def test_collateral_mode_returns_valid_json(self):
        """
        Test: Collateral-based derivation produces valid ValuePropositionJSON
        Given: Mock LLM returns Livongo example
        When: Research team processes collateral
        Then: Output validates against ValuePropositionSchema
        """
        # Arrange
        document_ids = ["s3://bucket/livongo_roi_sheet.pdf"]

        # Act
        result = self.research_team.derive_value_proposition(
            mode="collateral",
            document_ids=document_ids
        )

        # Assert
        assert result is not None
        validated = ValuePropositionSchema(**result)
        assert validated.metadata is not None
        assert len(validated.value_proposition_priorities) > 0
        assert validated.clinical_outcomes is not None

    def test_research_mode_returns_valid_json(self):
        """
        Test: Research-based derivation produces valid ValuePropositionJSON
        Given: Mock LLM returns Livongo example
        When: Research team processes prompts
        Then: Output validates against ValuePropositionSchema
        """
        # Arrange
        prompts = [
            "Research Livongo's diabetes management solution",
            "Focus on clinical outcomes and ROI"
        ]

        # Act
        result = self.research_team.derive_value_proposition(
            mode="research",
            prompts=prompts
        )

        # Assert
        assert result is not None
        validated = ValuePropositionSchema(**result)
        assert validated.metadata is not None

    def test_validation_failure_triggers_retry(self):
        """
        Test: Invalid LLM output triggers validation retry
        Given: Mock LLM returns invalid JSON on first call, valid on second
        When: Validation fails
        Then: Agent retries with error feedback
        """
        # Arrange
        invalid_llm = MockLLMFactory.create_invalid_json_llm()
        valid_llm = MockLLMFactory.create_value_prop_llm()

        # Mock sequence: invalid first, then valid
        call_count = [0]
        def switching_llm(prompt):
            call_count[0] += 1
            if call_count[0] == 1:
                return invalid_llm.generate(prompt)
            return valid_llm.generate(prompt)

        mock_llm = Mock()
        mock_llm.generate = Mock(side_effect=switching_llm)

        research_team = ResearchTeam(llm=mock_llm)

        # Act
        result = research_team.derive_value_proposition(
            mode="collateral",
            document_ids=["test.pdf"]
        )

        # Assert
        assert mock_llm.generate.call_count == 2  # Initial + retry
        validated = ValuePropositionSchema(**result)
        assert validated is not None

    def test_max_retries_exceeded_raises_error(self):
        """
        Test: Agent fails after max validation retries
        Given: Mock LLM always returns invalid JSON
        When: Validation fails repeatedly
        Then: Raise AgentValidationError after 3 attempts
        """
        # Arrange
        invalid_llm = MockLLMFactory.create_invalid_json_llm()
        research_team = ResearchTeam(llm=invalid_llm, max_retries=3)

        # Act & Assert
        with pytest.raises(AgentValidationError) as exc_info:
            research_team.derive_value_proposition(
                mode="collateral",
                document_ids=["test.pdf"]
            )

        assert "Validation failed after 3 attempts" in str(exc_info.value)

    def test_synthesis_agent_uses_livongo_structure(self):
        """
        Test: SynthesisAgent follows Livongo example structure
        Given: Mock findings from document analysis
        When: Synthesis occurs
        Then: Output structure matches Livongo example keys
        """
        # Arrange
        findings = {
            "extracted_value_propositions": [
                {"name": "Cost Reduction", "roi": "340%"}
            ],
            "clinical_outcomes": [{"outcome": "HbA1c reduction", "value": "1.2%"}]
        }

        with open('tests/fixtures/livongo_value_proposition_derived.json') as f:
            import json
            livongo_example = json.load(f)

        synthesis_agent = SynthesisAgent(llm=self.mock_llm)

        # Act
        result = synthesis_agent.synthesize(findings, livongo_example)

        # Assert
        # Check that result has same top-level keys as Livongo example
        assert set(result.keys()) == set(livongo_example.keys())
```

---

#### 6.2.3 Analytics Team Tests

**Test File:** `tests/agents/test_analytics_team.py`

```python
import pytest
from unittest.mock import Mock, MagicMock
from agents.analytics_team import (
    AnalyticsTeam,
    ClinicalAgent,
    PricingAgent,
    QuestionToSQLAgent
)

class TestAnalyticsTeam:
    """Test Analytics Team workflows"""

    def setup_method(self):
        """Setup mocks before each test"""
        self.mock_clickhouse = Mock()
        self.mock_llm = Mock()

    def test_clinical_agent_generates_baseline_metrics(self):
        """
        Test: ClinicalAgent produces valid baseline metrics
        Given: Mock Clickhouse returns diabetes data
        When: Agent analyzes value proposition
        Then: Baseline metrics match expected structure
        """
        # Arrange
        self.mock_clickhouse.execute.return_value = [
            {"avg_hba1c": 8.2, "control_rate": 0.42, "member_count": 12847}
        ]

        clinical_agent = ClinicalAgent(
            llm=self.mock_llm,
            db=self.mock_clickhouse
        )

        value_prop = {
            "priority_id": "vp-1",
            "priority_name": "Clinical Quality Improvement"
        }

        # Act
        result = clinical_agent.analyze_value_prop(value_prop)

        # Assert
        assert "baseline" in result
        assert result["baseline"]["hba1c_control_rate"] == 0.42
        assert result["baseline"]["member_count"] == 12847

    def test_pricing_agent_calculates_roi(self):
        """
        Test: PricingAgent calculates ROI correctly
        Given: Cost and savings data
        When: Agent computes ROI
        Then: Formula: ((savings - cost) / cost) * 100
        """
        # Arrange
        pricing_agent = PricingAgent(
            llm=self.mock_llm,
            db=self.mock_clickhouse
        )

        data = {
            "savings_24_month": 14500000,
            "program_cost_24_month": 3200000
        }

        # Act
        roi = pricing_agent.calculate_roi(data)

        # Assert
        expected_roi = ((14500000 - 3200000) / 3200000) * 100
        assert roi["roi_percentage"] == pytest.approx(expected_roi, rel=0.01)
        assert roi["roi_percentage"] == pytest.approx(353.125, rel=0.01)

    def test_question_to_sql_agent_translates_question(self):
        """
        Test: QuestionToSQLAgent converts NL to SQL
        Given: Natural language question
        When: Agent translates
        Then: Returns valid SQL query
        """
        # Arrange
        mock_llm_response = """
        SELECT avg(value) as avg_hba1c
        FROM quality_metrics
        WHERE measure_name = 'HbA1c'
          AND member_id IN (
            SELECT DISTINCT member_id
            FROM medical_claims
            WHERE diagnosis_codes LIKE '%E11%'
          )
        """

        self.mock_llm.generate.return_value = mock_llm_response

        sql_agent = QuestionToSQLAgent(llm=self.mock_llm)

        # Act
        result = sql_agent.translate_question(
            "What is the average HbA1c for diabetic members?"
        )

        # Assert
        assert "SELECT" in result["sql"]
        assert "quality_metrics" in result["sql"]
        assert "HbA1c" in result["sql"]

    def test_analytics_team_parallel_execution(self):
        """
        Test: Analytics team runs agents in parallel
        Given: Multiple category agents
        When: Team executes
        Then: All agents complete, results aggregated
        """
        # Arrange
        team = AnalyticsTeam(
            llm=self.mock_llm,
            db=self.mock_clickhouse
        )

        value_props = [
            {"priority_id": "vp-1", "priority_name": "ROI"},
            {"priority_id": "vp-2", "priority_name": "Clinical Quality"}
        ]

        # Act
        results = team.generate_insights(value_props)

        # Assert
        assert len(results) == 2
        assert "vp-1" in [r["priority_id"] for r in results]
        assert "vp-2" in [r["priority_id"] for r in results]
```

---

### 6.3 Schema Validation Tests

#### 6.3.1 Pydantic Schema Tests

**Test File:** `tests/schemas/test_value_proposition_schema.py`

```python
import pytest
from pydantic import ValidationError
from schemas.value_proposition import ValuePropositionSchema
import json

class TestValuePropositionSchema:
    """Test ValuePropositionJSON schema validation"""

    def test_valid_livongo_example_passes(self):
        """
        Test: Livongo example validates successfully
        Given: Livongo derived value proposition JSON
        When: Validate against schema
        Then: No errors raised
        """
        # Arrange
        with open('tests/fixtures/livongo_value_proposition_derived.json') as f:
            data = json.load(f)

        # Act
        validated = ValuePropositionSchema(**data)

        # Assert
        assert validated.metadata is not None
        assert len(validated.value_proposition_priorities) > 0

    def test_missing_required_field_fails(self):
        """
        Test: Schema rejects missing required fields
        Given: VP JSON missing 'metadata'
        When: Validate
        Then: ValidationError raised
        """
        # Arrange
        data = {
            "value_proposition_priorities": [],
            # Missing 'metadata'
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ValuePropositionSchema(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("metadata",) for e in errors)

    def test_invalid_field_type_fails(self):
        """
        Test: Schema rejects wrong field types
        Given: 'version' as string instead of int
        When: Validate
        Then: ValidationError raised
        """
        # Arrange
        data = {
            "metadata": {"version": "not-a-number"},  # Should be int
            "value_proposition_priorities": []
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            ValuePropositionSchema(**data)

    def test_extra_fields_rejected(self):
        """
        Test: Schema rejects unknown fields (strict mode)
        Given: VP JSON with extra field
        When: Validate with extra='forbid'
        Then: ValidationError raised
        """
        # Arrange
        with open('tests/fixtures/livongo_value_proposition_derived.json') as f:
            data = json.load(f)

        data["unknown_field"] = "should fail"

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ValuePropositionSchema(**data)

        errors = exc_info.value.errors()
        assert any("unknown_field" in str(e) for e in errors)
```

**Test File:** `tests/schemas/test_company_information_schema.py`

```python
import pytest
from schemas.company_information import CompanyInformationSchema
import json

class TestCompanyInformationSchema:
    """Test CompanyInformationJSON schema validation"""

    def test_valid_wellmark_example_passes(self):
        """
        Test: Wellmark example validates successfully
        """
        # Arrange
        with open('tests/fixtures/wellmark_company_information.json') as f:
            data = json.load(f)

        # Act
        validated = CompanyInformationSchema(**data)

        # Assert
        assert validated.company_overview is not None
        assert validated.classification.subsegment in [
            "Health Plan", "Broker", "PBM", "TPA", "Medical Management"
        ]

    def test_subsegment_enum_validation(self):
        """
        Test: Subsegment must be one of allowed values
        Given: Invalid subsegment value
        When: Validate
        Then: ValidationError raised
        """
        # Arrange
        data = {
            "company_overview": {"company_name": "Test"},
            "classification": {
                "core_segment": "PAYER",
                "subsegment": "Invalid Type"  # Not in enum
            }
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            CompanyInformationSchema(**data)
```

---

### 6.4 Test Data & Fixtures

#### 6.4.1 Fixture Directory Structure

```
tests/
├── fixtures/
│   ├── value_propositions/
│   │   ├── livongo_value_proposition_derived.json
│   │   ├── livongo_value_proposition_derived_ranked.json
│   │   ├── livongo_value_proposition_researched.json
│   │   ├── invalid_missing_metadata.json
│   │   └── invalid_wrong_types.json
│   ├── company_information/
│   │   ├── wellmark_company_information.json
│   │   ├── livongo_company_information.json
│   │   └── invalid_missing_subsegment.json
│   ├── dashboard_templates/
│   │   ├── roi_executive_dashboard.json
│   │   ├── clinical_outcomes_dashboard.json
│   │   └── invalid_missing_widgets.json
│   └── analytics/
│       ├── value_prop_insights_sample.json
│       └── dashboard_widget_data_sample.json
├── mocks/
│   ├── mock_llm.py
│   ├── mock_clickhouse.py
│   └── mock_storage.py
├── agents/
│   ├── test_research_team.py
│   ├── test_analytics_team.py
│   └── test_refinement_agent.py
└── schemas/
    ├── test_value_proposition_schema.py
    ├── test_company_information_schema.py
    └── test_dashboard_template_schema.py
```

---

#### 6.4.2 Fixture Loading Utility

**File:** `tests/utils/fixtures.py`

```python
import json
from pathlib import Path
from typing import Dict, Any

class FixtureLoader:
    """Utility for loading test fixtures"""

    BASE_PATH = Path(__file__).parent.parent / "fixtures"

    @classmethod
    def load_json(cls, relative_path: str) -> Dict[str, Any]:
        """
        Load JSON fixture by relative path

        Args:
            relative_path: Path relative to fixtures/ directory

        Returns:
            Parsed JSON data

        Example:
            data = FixtureLoader.load_json("value_propositions/livongo_value_proposition_derived.json")
        """
        file_path = cls.BASE_PATH / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"Fixture not found: {file_path}")

        with open(file_path) as f:
            return json.load(f)

    @classmethod
    def load_livongo_value_prop(cls, mode: str = "derived") -> Dict[str, Any]:
        """Load Livongo value proposition fixture"""
        filename = f"livongo_value_proposition_{mode}.json"
        return cls.load_json(f"value_propositions/{filename}")

    @classmethod
    def load_wellmark_company_info(cls) -> Dict[str, Any]:
        """Load Wellmark company information fixture"""
        return cls.load_json("company_information/wellmark_company_information.json")

    @classmethod
    def get_all_valid_fixtures(cls, category: str) -> list[Dict[str, Any]]:
        """
        Load all valid fixtures in a category

        Args:
            category: 'value_propositions' | 'company_information' | 'dashboard_templates'

        Returns:
            List of all valid JSON fixtures (excludes files starting with 'invalid_')
        """
        category_path = cls.BASE_PATH / category
        fixtures = []

        for file_path in category_path.glob("*.json"):
            if not file_path.name.startswith("invalid_"):
                with open(file_path) as f:
                    fixtures.append(json.load(f))

        return fixtures
```

---

### 6.5 Test Coverage Requirements

#### 6.5.1 Coverage Targets

```yaml
Overall Target: 80% line coverage

By Module:
  agents/:           85%  # Core business logic
  schemas/:          95%  # Schema validation critical
  api/routes/:       75%  # API endpoints
  services/:         80%  # Business services
  utils/:            70%  # Helper functions
  models/:           90%  # Database models

Critical Paths (100% coverage required):
  - ValidationAgent.validate()
  - All Pydantic schema definitions
  - Job status transitions
  - Error handling in agents
```

---

#### 6.5.2 Running Tests

**Commands:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=triton_platform --cov-report=html --cov-report=term

# Run specific test file
pytest tests/agents/test_research_team.py

# Run tests matching pattern
pytest -k "test_validation"

# Run with verbose output
pytest -v

# Run in parallel (faster)
pytest -n auto
```

**Configuration:** `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--tb=short",
    "--disable-warnings",
]

[tool.coverage.run]
source = ["triton_platform"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

---

### 6.6 Continuous Integration (CI)

#### 6.6.1 GitHub Actions Workflow

**File:** `.github/workflows/test.yml`

```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: triton_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          flake8 triton_platform/ --count --select=E9,F63,F7,F82 --show-source --statistics
          black --check triton_platform/
          isort --check-only triton_platform/

      - name: Run type checking
        run: mypy triton_platform/

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/triton_test
          REDIS_URL: redis://localhost:6379
        run: |
          pytest --cov=triton_platform --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

      - name: Check coverage threshold
        run: |
          coverage report --fail-under=80
```

---

### 6.7 Test-Driven Development Workflow

#### 6.7.1 TDD Process for New Agents

```
1. Write Schema First
   ├─ Define Pydantic model for expected output
   ├─ Write schema validation tests
   └─ Ensure tests fail (no implementation yet)

2. Create Test Fixtures
   ├─ Add example JSON (from Livongo/Wellmark references)
   ├─ Add invalid examples for edge cases
   └─ Load fixtures in tests

3. Write Agent Tests
   ├─ Test with mock LLM returning valid fixture
   ├─ Test with invalid LLM output (validation retry)
   ├─ Test max retries exceeded (failure case)
   └─ Test expected agent behavior

4. Implement Agent
   ├─ Write minimal agent code to pass tests
   ├─ Integrate ValidationAgent
   └─ Add retry logic

5. Refine & Iterate
   ├─ Run tests
   ├─ Fix failures
   ├─ Refactor
   └─ Repeat until green
```

---

#### 6.7.2 Example TDD Session

**Scenario:** Implementing SynthesisAgent Refinement Mode (Step 1.3)

**Step 1: Write Schema Test**

```python
# tests/schemas/test_refined_value_proposition.py

def test_refined_vp_maintains_structure():
    """Refined VP must maintain same structure as original"""
    original = FixtureLoader.load_livongo_value_prop("derived")
    refined = FixtureLoader.load_json("value_propositions/refined_v2.json")

    # Both should validate against same schema
    ValuePropositionSchema(**original)
    ValuePropositionSchema(**refined)

    # Version should increment
    assert refined["metadata"]["version"] > original["metadata"]["version"]
```

**Status:** ❌ Test fails (refined_v2.json doesn't exist yet)

---

**Step 2: Create Test Fixture**

```json
// tests/fixtures/value_propositions/refined_v2.json
{
  "metadata": {
    "version": 2,
    "refinement_round": 1
  },
  "value_proposition_priorities": [
    // ... (section "roi_tier_1" removed based on feedback)
  ]
}
```

**Status:** ❌ Test still fails (SynthesisAgent refinement mode not implemented)

---

**Step 3: Write Agent Test**

```python
# tests/agents/test_synthesis_agent.py

def test_synthesis_agent_refine_mode_removes_rejected_sections():
    """SynthesisAgent in refine mode removes sections marked for removal"""
    # Arrange
    original = FixtureLoader.load_livongo_value_prop("derived")
    feedback = [
        {"section_id": "roi_tier_1", "action": "reject_remove"}
    ]

    mock_llm = MockLLMFactory.create_refinement_llm()
    agent = SynthesisAgent(llm=mock_llm)

    # Act
    refined = agent.execute(
        mode="refine",
        refinement_feedback=feedback,
        previous_version=original,
        inputs=None
    )

    # Assert
    assert "roi_tier_1" not in refined
    assert refined["metadata"]["version"] == 2
```

**Status:** ❌ Test fails (SynthesisAgent refine mode not implemented)

---

**Step 4: Implement Agent Refine Mode (Minimal)**

```python
# agents/synthesis_agent.py

class SynthesisAgent:
    def execute(self, mode, inputs=None, refinement_feedback=None,
                previous_version=None, original_research=None):
        if mode == "initial":
            return self.synthesize_initial(inputs)
        elif mode == "refine":
            return self.synthesize_refinement(
                previous_version, refinement_feedback, original_research
            )

    def synthesize_refinement(self, previous_vp, feedback, original_research):
        refined = previous_vp.copy()
        refined["metadata"]["version"] += 1

        # Remove rejected sections
        for item in feedback:
            if item["action"] == "reject_remove":
                section_id = item["section_id"]
                if section_id in refined:
                    del refined[section_id]

        return refined
```

**Status:** ✅ Test passes

---

**Step 5: Iterate (Add more tests)**

```python
def test_synthesis_agent_refine_mode_modifies_changed_sections():
    """SynthesisAgent rewrites sections marked for change"""
    # ... (add test for "reject_change" action)

def test_synthesis_agent_refine_mode_preserves_approved_sections():
    """SynthesisAgent keeps approved sections unchanged"""
    # ... (add test to ensure no modification)
```

---

### 6.8 Performance Testing

While not part of MVP, performance benchmarks for future optimization:

```python
# tests/performance/test_agent_performance.py

import pytest
import time

@pytest.mark.performance
def test_research_team_completes_under_2_minutes():
    """Research team should complete derivation in < 2 minutes"""
    start = time.time()

    research_team = ResearchTeam(llm=real_llm)  # Use real LLM
    result = research_team.derive_value_proposition(
        mode="collateral",
        document_ids=["test.pdf"]
    )

    duration = time.time() - start

    assert duration < 120  # 2 minutes
    assert result is not None

@pytest.mark.performance
def test_analytics_team_completes_under_5_minutes():
    """Analytics team should process 8 priorities in < 5 minutes"""
    start = time.time()

    analytics_team = AnalyticsTeam(llm=real_llm, db=real_db)
    results = analytics_team.generate_insights(value_props)

    duration = time.time() - start

    assert duration < 300  # 5 minutes
    assert len(results) == 8
```

**Note:** Performance tests marked with `@pytest.mark.performance` and run separately:

```bash
pytest -m performance
```

---

### 6.9 Test Maintenance

#### 6.9.1 Keeping Fixtures Updated

```python
# scripts/update_fixtures.py

"""
Script to regenerate test fixtures from live runs

Usage:
    python scripts/update_fixtures.py --agent research_team --mode collateral
"""

import argparse
import json
from agents.research_team import ResearchTeam

def update_fixture(agent_name: str, mode: str):
    """Regenerate fixture from real agent execution"""

    # Run agent with real LLM
    agent = get_agent(agent_name)
    result = agent.execute(mode=mode)

    # Validate result
    validate_against_schema(result)

    # Save to fixtures
    fixture_path = f"tests/fixtures/{agent_name}_{mode}.json"
    with open(fixture_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✅ Updated fixture: {fixture_path}")

# Run periodically to keep fixtures fresh
```

---

#### 6.9.2 Schema Evolution

When schemas change:

1. Update Pydantic models
2. Run tests (expect failures)
3. Update fixtures to match new schema
4. Run tests again (should pass)
5. Update MockLLM responses if needed

---

### 6.10 Test Checklist for New Features

Before merging any agent or feature:

```markdown
- [ ] Pydantic schema defined and tested
- [ ] Valid test fixture added (based on reference examples)
- [ ] Invalid test fixtures added (edge cases)
- [ ] Unit tests with mock LLM (3+ scenarios)
- [ ] Validation retry logic tested
- [ ] Max retries failure tested
- [ ] Error messages are clear and actionable
- [ ] Coverage > 85% for new code
- [ ] All tests pass in CI
- [ ] Code reviewed by team
```

---

**End of Section 6**

---

## 7. Deployment Architecture

### 7.1 Deployment Overview

The Triton Platform is designed for cloud-agnostic deployment with AWS as the primary target. The architecture supports both local development (Docker Compose) and production deployment (AWS ECS/Fargate).

**Deployment Environments:**
- **Local Development:** Docker Compose with local databases
- **Staging:** AWS with scaled-down resources
- **Production:** AWS with auto-scaling and high availability

---

### 7.2 Docker Architecture

#### 7.2.1 Container Strategy

**Important:** This Docker architecture is for **local development only**. Production deployments leverage managed cloud services per the cloud deployment philosophy (Section 1.4).

**Local Development - Multi-Container Application:**

```
┌─────────────────────────────────────────────────────────┐
│           Docker Containers (Local Dev Only)             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐  ┌────────────────┐               │
│  │  triton-api    │  │ celery-worker  │               │
│  │  (FastAPI)     │  │  (Agents)      │               │
│  │  Port: 8000    │  │  Parallel: 4x  │               │
│  └────────────────┘  └────────────────┘               │
│                                                          │
│  ┌────────────────┐  ┌────────────────┐               │
│  │  postgres      │  │  redis          │               │
│  │  Port: 5432    │  │  Port: 6379    │               │
│  │  (Docker)      │  │  (Docker)      │               │
│  └────────────────┘  └────────────────┘               │
│                                                          │
│  ┌────────────────┐  ┌────────────────┐               │
│  │  clickhouse    │  │  nginx          │               │
│  │  Port: 8123    │  │  Port: 80/443  │               │
│  │  (Docker)      │  │  (Docker)      │               │
│  └────────────────┘  └────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

**AWS Production Deployment:**

In production, infrastructure uses managed services:
- **PostgreSQL:** Amazon RDS for PostgreSQL (not Docker)
- **Redis:** Amazon ElastiCache for Redis (not Docker)
- **Clickhouse:** Existing ARGO Clickhouse instance (not Docker, managed separately)
- **Application containers:** ECS Fargate or EKS (triton-api, celery-worker)
- **Load Balancer:** ALB (not nginx Docker container)

**Application Code Remains Cloud-Agnostic:**
- Uses environment variables for service endpoints:
  - `DATABASE_URL=postgresql://...` (points to RDS in prod, Docker in dev)
  - `REDIS_URL=redis://...` (points to ElastiCache in prod, Docker in dev)
  - `CLICKHOUSE_URL=http://...` (points to ARGO Clickhouse in prod, Docker in dev)
- Same Docker images deploy to any environment
- Infrastructure-as-code organized by cloud provider (see Section 7.3)

---

#### 7.2.2 Docker Compose Configuration (Local Development)

**File:** `docker-compose.yml`

**Purpose:** Local development environment only. Production uses managed cloud services.

```yaml
version: '3.8'

services:
  # FastAPI Application
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: triton-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://triton:triton@postgres:5432/triton
      - REDIS_URL=redis://redis:6379/0
      - CLICKHOUSE_URL=http://clickhouse:8123
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_S3_BUCKET=${AWS_S3_BUCKET}
      - ENV=development
    volumes:
      - ./:/app
      - /app/__pycache__
    depends_on:
      - postgres
      - redis
      - clickhouse
    command: uvicorn triton_platform.main:app --host 0.0.0.0 --port 8000 --reload

  # Celery Workers
  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: triton-celery-worker
    environment:
      - DATABASE_URL=postgresql://triton:triton@postgres:5432/triton
      - REDIS_URL=redis://redis:6379/0
      - CLICKHOUSE_URL=http://clickhouse:8123
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - ENV=development
    volumes:
      - ./:/app
    depends_on:
      - postgres
      - redis
      - clickhouse
    command: celery -A triton_platform.celery_app worker --loglevel=info --concurrency=4

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: triton-postgres
    environment:
      - POSTGRES_USER=triton
      - POSTGRES_PASSWORD=triton
      - POSTGRES_DB=triton
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U triton"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: triton-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Clickhouse
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    container_name: triton-clickhouse
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse
      - ./migrations/clickhouse:/docker-entrypoint-initdb.d
    environment:
      - CLICKHOUSE_DB=triton
      - CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "localhost:8123/ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx (Reverse Proxy)
  nginx:
    image: nginx:alpine
    container_name: triton-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

  # AgentOS UI (Development Only)
  agentos:
    image: agno/agentos:latest
    container_name: triton-agentos
    ports:
      - "7777:7777"
    environment:
      - DATABASE_URL=postgresql://triton:triton@postgres:5432/triton
    depends_on:
      - postgres
    profiles:
      - development

volumes:
  postgres_data:
  redis_data:
  clickhouse_data:
```

---

#### 7.2.3 Dockerfile

**File:** `Dockerfile`

```dockerfile
# Multi-stage build for production optimization
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 triton && chown -R triton:triton /app
USER triton

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["uvicorn", "triton_platform.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

#### 7.2.4 Environment Variables

**File:** `.env.example`

```bash
# Application
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://triton:triton@postgres:5432/triton
CLICKHOUSE_URL=http://clickhouse:8123

# Redis
REDIS_URL=redis://redis:6379/0

# LLM Provider
ANTHROPIC_API_KEY=sk-ant-...

# AWS (for S3 storage)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET=triton-documents

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# AgentOS
AGENTOS_ENABLED=true
```

---

### 7.3 AWS Production Deployment

#### 7.3.1 AWS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Application Load Balancer              │    │
│  │              (ALB - Public Facing)                  │    │
│  └────────────────────┬───────────────────────────────┘    │
│                       │                                      │
│         ┌─────────────┼─────────────┐                      │
│         ↓             ↓             ↓                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ ECS Task │  │ ECS Task │  │ ECS Task │  (API)          │
│  │ Fargate  │  │ Fargate  │  │ Fargate  │                 │
│  └──────────┘  └──────────┘  └──────────┘                │
│       Auto Scaling Group (2-10 tasks)                      │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Celery   │  │ Celery   │  │ Celery   │  (Workers)      │
│  │ Worker   │  │ Worker   │  │ Worker   │                 │
│  └──────────┘  └──────────┘  └──────────┘                │
│       Auto Scaling Group (4-20 workers)                    │
│                                                              │
│  ┌─────────────────────────────────────────────────┐      │
│  │            Data Layer                            │      │
│  ├─────────────────────────────────────────────────┤      │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────┐ │      │
│  │  │ RDS        │  │ ElastiCache│  │ S3       │ │      │
│  │  │ PostgreSQL │  │ (Redis)    │  │ Buckets  │ │      │
│  │  └────────────┘  └────────────┘  └──────────┘ │      │
│  │                                                  │      │
│  │  ┌────────────────────────────────────────┐   │      │
│  │  │ Clickhouse (Self-Hosted EC2 or Cloud) │   │      │
│  │  └────────────────────────────────────────┘   │      │
│  └─────────────────────────────────────────────────┘      │
│                                                              │
│  ┌─────────────────────────────────────────────────┐      │
│  │            Monitoring & Logging                  │      │
│  ├─────────────────────────────────────────────────┤      │
│  │  CloudWatch Logs │ CloudWatch Metrics           │      │
│  │  X-Ray Tracing   │ SNS Alerts                   │      │
│  └─────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

#### 7.3.2 Infrastructure as Code (Terraform)

**File:** `terraform/main.tf`

```hcl
terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket = "triton-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "triton-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Environment = var.environment
    Project     = "Triton"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier = "triton-postgres-${var.environment}"

  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = var.db_instance_class
  allocated_storage    = 100
  storage_encrypted    = true

  db_name  = "triton"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  skip_final_snapshot = var.environment == "staging"
  final_snapshot_identifier = var.environment == "production" ? "triton-final-${timestamp()}" : null

  tags = {
    Name        = "triton-postgres"
    Environment = var.environment
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "triton-redis-${var.environment}"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379

  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  tags = {
    Name        = "triton-redis"
    Environment = var.environment
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "triton-cluster-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = var.environment
  }
}

# ECS Task Definition - API
resource "aws_ecs_task_definition" "api" {
  family                   = "triton-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "triton-api"
      image     = "${var.ecr_repository_url}:${var.image_tag}"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "ENV", value = var.environment },
        { name = "DATABASE_URL", value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.endpoint}/triton" },
        { name = "REDIS_URL", value = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:6379/0" },
        { name = "CLICKHOUSE_URL", value = var.clickhouse_url }
      ]

      secrets = [
        { name = "ANTHROPIC_API_KEY", valueFrom = "${aws_secretsmanager_secret.anthropic_key.arn}" },
        { name = "SECRET_KEY", valueFrom = "${aws_secretsmanager_secret.app_secret.arn}" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "api"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}

# ECS Service - API
resource "aws_ecs_service" "api" {
  name            = "triton-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "triton-api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.https]
}

# Auto Scaling - API
resource "aws_appautoscaling_target" "api" {
  max_capacity       = var.api_max_count
  min_capacity       = var.api_min_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "api_cpu" {
  name               = "api-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "triton-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = var.environment == "production"

  tags = {
    Environment = var.environment
  }
}

# S3 Bucket for Documents
resource "aws_s3_bucket" "documents" {
  bucket = "triton-documents-${var.environment}"

  tags = {
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/triton-api-${var.environment}"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "celery" {
  name              = "/ecs/triton-celery-${var.environment}"
  retention_in_days = var.log_retention_days
}
```

---

#### 7.3.3 Environment-Specific Variables

**File:** `terraform/variables.tf`

```hcl
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# Database
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"  # staging: db.t3.small
}

# Redis
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.medium"
}

# ECS - API
variable "api_cpu" {
  description = "CPU units for API task"
  type        = string
  default     = "1024"  # 1 vCPU
}

variable "api_memory" {
  description = "Memory for API task"
  type        = string
  default     = "2048"  # 2 GB
}

variable "api_min_count" {
  description = "Minimum API task count"
  type        = number
  default     = 2
}

variable "api_max_count" {
  description = "Maximum API task count"
  type        = number
  default     = 10
}

# ECS - Celery Workers
variable "celery_cpu" {
  description = "CPU units for Celery worker"
  type        = string
  default     = "2048"  # 2 vCPU (agents need more CPU)
}

variable "celery_memory" {
  description = "Memory for Celery worker"
  type        = string
  default     = "4096"  # 4 GB
}

variable "celery_min_count" {
  description = "Minimum Celery worker count"
  type        = number
  default     = 4
}

variable "celery_max_count" {
  description = "Maximum Celery worker count"
  type        = number
  default     = 20
}
```

---

### 7.4 Deployment Process

#### 7.4.1 CI/CD Pipeline

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to AWS

on:
  push:
    branches:
      - main
      - staging

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Set environment
        id: set-env
        run: |
          if [ "${{ github.ref }}" == "refs/heads/main" ]; then
            echo "ENV=production" >> $GITHUB_OUTPUT
          else
            echo "ENV=staging" >> $GITHUB_OUTPUT
          fi

      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: triton-platform
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster triton-cluster-${{ steps.set-env.outputs.ENV }} \
            --service triton-api \
            --force-new-deployment

      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster triton-cluster-${{ steps.set-env.outputs.ENV }} \
            --services triton-api

      - name: Notify deployment
        if: success()
        run: echo "✅ Deployment to ${{ steps.set-env.outputs.ENV }} completed"
```

---

#### 7.4.2 Database Migrations

**Migration Strategy:**

```bash
# Run migrations before deploying new code
./scripts/migrate.sh production

# migrate.sh:
#!/bin/bash
ENV=$1

# PostgreSQL migrations
alembic upgrade head

# Clickhouse migrations
clickhouse-client --host $CLICKHOUSE_HOST --query "$(cat migrations/clickhouse_002_new_table.sql)"

echo "✅ Migrations complete for $ENV"
```

---

### 7.5 Scaling & Performance

#### 7.5.1 Auto-Scaling Rules

**API Scaling:**
- **Metric:** CPU Utilization
- **Target:** 70%
- **Scale Up:** +2 tasks when CPU > 70% for 2 minutes
- **Scale Down:** -1 task when CPU < 40% for 5 minutes
- **Min:** 2 tasks (HA)
- **Max:** 10 tasks

**Celery Worker Scaling:**
- **Metric:** Queue Length (Redis)
- **Target:** < 10 pending jobs per worker
- **Scale Up:** +2 workers when queue > 40 jobs
- **Scale Down:** -1 worker when queue < 5 jobs
- **Min:** 4 workers
- **Max:** 20 workers

---

#### 7.5.2 Performance Tuning

**Celery Configuration:**

```python
# celery_config.py

broker_url = os.getenv("REDIS_URL")
result_backend = os.getenv("REDIS_URL")

# Task routing
task_routes = {
    'triton_platform.tasks.research_team.*': {'queue': 'research'},
    'triton_platform.tasks.analytics_team.*': {'queue': 'analytics'},
    'triton_platform.tasks.refinement.*': {'queue': 'refinement'},
}

# Concurrency
worker_concurrency = 4  # Per worker
worker_prefetch_multiplier = 2

# Timeouts
task_time_limit = 600  # 10 minutes hard limit
task_soft_time_limit = 540  # 9 minutes soft limit

# Retry policy
task_acks_late = True
task_reject_on_worker_lost = True

# Result expiration
result_expires = 3600  # 1 hour
```

---

### 7.6 Monitoring & Observability

#### 7.6.1 CloudWatch Metrics

**Custom Metrics:**

```python
# monitoring/metrics.py

import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def track_agent_execution(agent_name: str, duration: float, success: bool):
    """Track agent execution metrics"""
    cloudwatch.put_metric_data(
        Namespace='Triton/Agents',
        MetricData=[
            {
                'MetricName': 'ExecutionDuration',
                'Dimensions': [
                    {'Name': 'AgentName', 'Value': agent_name},
                    {'Name': 'Success', 'Value': str(success)}
                ],
                'Value': duration,
                'Unit': 'Seconds',
                'Timestamp': datetime.utcnow()
            }
        ]
    )

def track_job_status(job_type: str, status: str):
    """Track job status changes"""
    cloudwatch.put_metric_data(
        Namespace='Triton/Jobs',
        MetricData=[
            {
                'MetricName': 'JobStatusChange',
                'Dimensions': [
                    {'Name': 'JobType', 'Value': job_type},
                    {'Name': 'Status', 'Value': status}
                ],
                'Value': 1.0,
                'Unit': 'Count',
                'Timestamp': datetime.utcnow()
            }
        ]
    )
```

---

#### 7.6.2 Alerting

**CloudWatch Alarms:**

```hcl
# terraform/monitoring.tf

# API Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "api_errors" {
  alarm_name          = "triton-api-high-error-rate-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "5XXError"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "API error rate is too high"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
}

# Celery Queue Depth Alarm
resource "aws_cloudwatch_metric_alarm" "celery_queue_depth" {
  alarm_name          = "triton-celery-queue-depth-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "100"
  alarm_description   = "Celery queue has too many pending jobs"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

# Database Connection Pool Alarm
resource "aws_cloudwatch_metric_alarm" "db_connections" {
  alarm_name          = "triton-db-connections-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Database connection pool nearing capacity"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.id
  }
}
```

---

### 7.7 Security

#### 7.7.1 Security Groups

**ECS Tasks Security Group:**
- Ingress: Port 8000 from ALB only
- Egress: All (for API calls, database access)

**RDS Security Group:**
- Ingress: Port 5432 from ECS tasks only
- Egress: None

**Redis Security Group:**
- Ingress: Port 6379 from ECS tasks only
- Egress: None

---

#### 7.7.2 Secrets Management

```hcl
# terraform/secrets.tf

resource "aws_secretsmanager_secret" "anthropic_key" {
  name = "triton/${var.environment}/anthropic-api-key"
}

resource "aws_secretsmanager_secret_version" "anthropic_key" {
  secret_id     = aws_secretsmanager_secret.anthropic_key.id
  secret_string = var.anthropic_api_key
}

resource "aws_secretsmanager_secret" "app_secret" {
  name = "triton/${var.environment}/app-secret-key"
}

resource "aws_secretsmanager_secret_version" "app_secret" {
  secret_id     = aws_secretsmanager_secret.app_secret.id
  secret_string = var.app_secret_key
}
```

---

### 7.8 Disaster Recovery

#### 7.8.1 Backup Strategy

**RDS Automated Backups:**
- Daily snapshots at 3 AM UTC
- 7-day retention (staging)
- 30-day retention (production)
- Cross-region replication for production

**S3 Versioning & Lifecycle:**
- Versioning enabled on document bucket
- Lifecycle policy: Transition to Glacier after 90 days
- Permanent retention for critical documents

**Clickhouse Backups:**
- Weekly full backups to S3
- Automated via cron job on EC2 instance
- 90-day retention

---

#### 7.8.2 Recovery Procedures

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 1 hour

**Recovery Steps:**
1. Restore RDS from snapshot (30 minutes)
2. Restore Clickhouse from S3 backup (60 minutes)
3. Deploy application from Docker image (30 minutes)
4. Verify data integrity (60 minutes)
5. DNS cutover (30 minutes)

---

### 7.9 Cost Optimization

**Estimated Monthly Costs (Production):**

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **ECS Fargate (API)** | 2-10 tasks, 1 vCPU, 2 GB | $150 - $750 |
| **ECS Fargate (Celery)** | 4-20 tasks, 2 vCPU, 4 GB | $600 - $3000 |
| **RDS PostgreSQL** | db.t3.medium, 100 GB | $150 |
| **ElastiCache Redis** | cache.t3.medium | $80 |
| **Clickhouse EC2** | t3.xlarge, 500 GB EBS | $200 |
| **ALB** | Application Load Balancer | $25 |
| **S3** | 1 TB storage, 10K requests | $25 |
| **CloudWatch** | Logs + Metrics | $50 |
| **Data Transfer** | 500 GB outbound | $45 |
| **Total** |  | **$1,325 - $4,325/month** |

**Cost Optimization Strategies:**
- Use Reserved Instances for predictable workloads (save 30-50%)
- Auto-scale down during off-hours
- Use S3 Intelligent-Tiering for documents
- Monitor and optimize Clickhouse queries
- Consider Spot Instances for non-critical Celery workers

---

**End of Section 7**

---

## 8. Implementation Roadmap

### 8.1 Development Phases Overview

The Triton Platform will be built in 4 phases following test-driven development (TDD) principles:

| Phase | Focus | Duration | Key Deliverables |
|-------|-------|----------|------------------|
| **Phase 0** | Foundation & Infrastructure | 1 week | Database setup, base APIs, mock LLM framework, CI/CD |
| **Phase 1** | Step 1 - Client Value Propositions | 3 weeks | Research Team agents, value prop derivation, review & refinement |
| **Phase 2** | Step 2 - Prospect Research & Ranking | 2 weeks | Company research integration, value prop ranking |
| **Phase 3** | Steps 4-5 - Analytics Generation | 3 weeks | Analytics Team agents, dashboard data generation |

**Total Timeline:** 9 weeks (approximately 2 months)

**Development Acceleration Note:** These durations assume the development team is using **Claude Code** for AI-assisted development. Claude Code significantly accelerates:
- Schema and model definitions (Pydantic, SQLAlchemy)
- Boilerplate code generation (API endpoints, CRUD operations)
- Test case creation and TDD implementation
- Database migrations and infrastructure-as-code
- Agent prompt engineering and refinement
- Documentation generation

**Without Claude Code:** Add approximately 4-5 weeks to total timeline (traditional development pace would be ~13-14 weeks).

**Team Composition Assumption:** 2-3 full-stack developers with Claude Code proficiency

---

### 8.2 Phase 0: Foundation & Infrastructure (Week 1)

**Goal:** Establish core infrastructure, development environment, and testing framework.

**Duration:** 1 week (accelerated with Claude Code)

#### Week 1: Project Setup & Testing Framework

**Tasks:**
1. **Repository & Environment Setup**
   - Initialize Python project with Poetry
   - Configure pre-commit hooks (black, flake8, mypy)
   - Set up Docker Compose for local development
   - Configure environment variables and secrets management

2. **Database Setup**
   - Create PostgreSQL schemas (clients, prospects, jobs, value_propositions)
   - Create Clickhouse schemas (member_demographics, claims, utilization)
   - Write Alembic migrations for PostgreSQL
   - Seed test data for development

3. **FastAPI Base Application**
   - Implement base FastAPI app structure
   - Add health check endpoints
   - Configure CORS and middleware
   - Integrate SQLAlchemy for PostgreSQL
   - Integrate Clickhouse client

4. **⚠️ CRITICAL: Task Queue Abstraction Layer**
   - Implement `TaskQueue` abstract base class (see ADR-003)
   - Implement `CeleryTaskQueue` concrete implementation
   - Set up Celery + Redis configuration
   - Configure dependency injection for `TaskQueue`
   - **DO NOT call Celery directly in any API/business logic code**
   - This abstraction enables future migration to Temporal if needed

5. **Mock LLM Framework**
   - Implement `MockLLM` class with response mapping
   - Create `MockLLMFactory` with preset responses
   - Build test fixtures directory structure
   - Create initial JSON fixtures (value propositions, company info)

6. **Pydantic Schema Definitions**
   - Define all base schemas (ValuePropositionSchema, CompanyInformationSchema, etc.)
   - Add validation tests for each schema
   - Create schema documentation

7. **CI/CD Pipeline**
   - GitHub Actions workflow for tests
   - Docker build and push to ECR
   - Coverage reporting (codecov.io)
   - Pre-deployment checks

**Deliverables:**
- Working Docker Compose environment with all services
- Database schemas created and migrated
- FastAPI app running at `localhost:8000` with health checks
- Task queue abstraction layer implemented and tested
- Mock LLM framework with 10+ test fixtures
- All core Pydantic schemas with validation tests
- CI/CD pipeline running on GitHub Actions
- Test coverage > 80%

**Claude Code Acceleration:** Foundation tasks that traditionally take 2 weeks compressed to 1 week with AI-assisted code generation, schema definitions, and test creation.

---

### 8.3 Phase 1: Step 1 - Client Value Propositions (Weeks 2-4)

**Duration:** 3 weeks (accelerated with Claude Code from 4 weeks)

**Goal:** Implement complete client value proposition workflow including derivation, review, and dashboard template generation.

#### Week 2: Client Management & Research Team Foundation

**Tasks:**
1. **Client CRUD APIs**
   - `POST /api/v1/clients` - Create client
   - `GET /api/v1/clients/{client_id}` - Get client details
   - `PUT /api/v1/clients/{client_id}` - Update client
   - `GET /api/v1/clients` - List clients
   - Client settings management

2. **Document Management**
   - S3 abstraction layer (boto3 wrapper)
   - `POST /api/v1/clients/{client_id}/documents` - Upload document
   - `GET /api/v1/clients/{client_id}/documents` - List documents
   - Document metadata storage in PostgreSQL

3. **Agno Framework Integration**
   - Install and configure Agno SDK
   - Set up AgentOS connection (optional, for monitoring)
   - Create base agent classes with retry logic

**Deliverables:**
- Client CRUD APIs fully functional
- Document upload and retrieval working
- Agno framework integrated and tested

**Tests:**
- 20+ unit tests for client APIs
- 10+ tests for document management
- Integration tests with mock S3 (moto library)

#### Week 3: Research Team Agents

**Tasks:**
1. **WebSearchAgent**
   - Integrate Google Search API
   - Implement web scraping with BeautifulSoup
   - Add rate limiting and caching
   - Create prompt templates for search queries

2. **DocumentAnalysisAgent**
   - Integrate Anthropic Claude for PDF parsing
   - Extract text and tables from PDFs
   - Identify key metrics and data points
   - Structure findings as JSON

3. **SynthesisAgent (Coordinator)**
   - Combine findings from WebSearchAgent and DocumentAnalysisAgent
   - Generate structured value proposition JSON
   - Coordinate team execution flow
   - Handle partial failures gracefully

4. **ValidationAgent**
   - Validate output against ValuePropositionSchema
   - Provide feedback to SynthesisAgent for refinement
   - Retry loop (max 3 attempts)
   - Log validation failures for debugging

**Deliverables:**
- All 4 Research Team agents implemented
- Research Team can run end-to-end (research mode and collateral mode)
- Validated JSON output matches schema

**Tests:**
- 40+ unit tests for agent logic with mock LLMs
- 15+ integration tests for team workflows
- Schema validation tests for all output formats

#### Week 4: Value Proposition Derivation, Review #### Week 5: Value Proposition Derivation & Review Dashboard Templates

**Tasks:**
1. **Value Proposition Derivation API**
   - `POST /api/v1/clients/{client_id}/value-proposition/derive` - Trigger derivation
   - Celery task for async processing
   - Job status tracking
   - Error handling and retry logic

2. **Job Management**
   - `GET /api/v1/jobs/{job_id}` - Get job status
   - `GET /api/v1/clients/{client_id}/value-proposition/jobs/{job_id}` - Get value prop job
   - Progress tracking with percentage completion
   - WebSocket support for real-time updates (optional)

3. **SynthesisAgent Refinement Mode**
   - Extend SynthesisAgent to support `mode="refine"` parameter
   - Accept user feedback as structured prompts
   - Apply iterative refinements to value propositions
   - Reference original research context for accuracy
   - Track version history
   - Validate refined output via ValidationAgent

4. **Review & Refinement APIs**
   - `POST /api/v1/clients/{client_id}/value-proposition/{vp_id}/refine` - Submit feedback
   - `GET /api/v1/clients/{client_id}/value-proposition` - List all versions
   - `PUT /api/v1/clients/{client_id}/value-proposition/{vp_id}/approve` - Approve version

**Deliverables:**
- Complete value proposition derivation workflow
- Refinement process with version tracking
- Job management with progress tracking

**Tests:**
- 25+ tests for derivation workflow
- 15+ tests for refinement logic
- End-to-end tests with mock LLMs



**Tasks:**
1. **TemplateGeneratorAgent**
   - Generate 5-10 dashboard template variations
   - Each template has 4-6 widget configurations
   - Map widgets to analytics questions
   - Output as DashboardTemplateJSON

2. **Dashboard Template APIs**
   - `POST /api/v1/clients/{client_id}/dashboard-templates/generate` - Generate templates
   - `GET /api/v1/clients/{client_id}/dashboard-templates` - List templates
   - `PUT /api/v1/clients/{client_id}/dashboard-templates/{template_id}` - Update template
   - `POST /api/v1/clients/{client_id}/dashboard-templates/{template_id}/select` - Select template

**Deliverables:**
- TemplateGeneratorAgent producing valid templates
- Dashboard template management APIs
- Complete Step 1 workflow functional

**Tests:**
- 20+ tests for template generation
- 10+ tests for template APIs
- Schema validation for DashboardTemplateJSON

**Phase 1 Milestone:**
- ✅ Complete Step 1 workflow: Client onboarding → Value proposition derivation → Review/refinement → Dashboard template selection
- ✅ All APIs documented with OpenAPI/Swagger
- ✅ Test coverage > 85% for Phase 1 code

---

### 8.4 Phase 2: Step 2 - Prospect Research & Ranking (Weeks 5-6)

**Duration:** 2 weeks (accelerated with Claude Code from 3 weeks)

**Goal:** Implement prospect creation, company research, and value proposition ranking.

#### Week 5: Prospect Management & Research Reuse

**Tasks:**
1. **Prospect CRUD APIs**
   - `POST /api/v1/prospects` - Create prospect
   - `GET /api/v1/prospects/{prospect_id}` - Get prospect details
   - `PUT /api/v1/prospects/{prospect_id}` - Update prospect
   - `GET /api/v1/prospects` - List prospects
   - Link prospects to clients

2. **Reuse Research Team for Company Research**
   - Adapt WebSearchAgent for company-specific research
   - Extend DocumentAnalysisAgent for public filings (10-K, annual reports)
   - Create CompanyInformationSchema for structured output
   - Update SynthesisAgent to handle company research mode

3. **Company Research API**
   - `POST /api/v1/prospects/{prospect_id}/research/initiate` - Trigger company research
   - `GET /api/v1/prospects/{prospect_id}/research/jobs/{job_id}` - Get research job status
   - Store CompanyInformationJSON in prospects table

**Deliverables:**
- Prospect CRUD APIs functional
- Research Team adapted for company research
- Company information stored and retrievable

**Tests:**
- 15+ tests for prospect APIs
- 20+ tests for company research workflow
- Schema validation for CompanyInformationJSON

#### Week 6: Value Proposition Ranking

**Tasks:**
1. **Ranking Algorithm**
   - Create RankingAgent (uses Claude for relevance scoring)
   - Compare client value propositions with prospect priorities
   - Generate relevance scores (0-100) for each value prop
   - Produce ranked list with explanations

2. **Ranking APIs**
   - `POST /api/v1/prospects/{prospect_id}/value-proposition/rank` - Trigger ranking
   - `GET /api/v1/prospects/{prospect_id}/value-proposition/jobs/{job_id}` - Get ranking job
   - `GET /api/v1/prospects/{prospect_id}/value-proposition/ranked` - Get ranked results

3. **Selection & Approval**
   - `POST /api/v1/prospects/{prospect_id}/value-proposition/select` - Select top value prop
   - Link selected value proposition to prospect
   - Trigger analytics generation (Step 4) automatically

**Deliverables:**
- RankingAgent producing scored rankings
- Value proposition selection workflow
- Automatic trigger to Step 4 upon selection

**Tests:**
- 20+ tests for ranking logic
- 10+ tests for selection workflow
- Integration tests for complete Step 2 flow

 Polish & Integration Testing

**Tasks:**
1. **End-to-End Testing**
   - Complete workflow: Create client → Derive value prop → Create prospect → Research → Rank → Select
   - Performance testing with realistic data volumes
   - Load testing with multiple concurrent jobs

2. **API Documentation**
   - Complete OpenAPI/Swagger documentation
   - Add request/response examples
   - Create API usage guides

3. **Bug Fixes & Refinements**
   - Address issues found in testing
   - Optimize slow queries
   - Improve error messages

**Deliverables:**
- End-to-end tests passing
- API documentation complete
- Performance benchmarks documented

**Phase 2 Milestone:**
- ✅ Complete Step 2 workflow: Prospect creation → Company research → Value prop ranking → Selection
- ✅ Research Team successfully reused across Steps 1 and 2
- ✅ Test coverage maintained at > 85%

---

### 8.5 Phase 3: Steps 4-5 - Analytics Generation (Weeks 7-9)

**Duration:** 3 weeks (accelerated with Claude Code from 4 weeks)

**Goal:** Implement analytics data generation for value propositions and dashboard widgets.

#### Week 7: Analytics Team Foundation

**Tasks:**
1. **QuestionToSQLAgent (Coordinator)**
   - Translate natural language questions to Clickhouse SQL
   - Validate SQL syntax before execution
   - Execute queries and return results
   - Handle query errors gracefully

2. **Clickhouse Query Optimization**
   - Create materialized views for common aggregations
   - Add indexes for frequent query patterns
   - Optimize table partitioning
   - Test query performance

3. **Analytics Base Classes**
   - Create BaseAnalyticsAgent class
   - Shared prompt templates for analytics agents
   - Common data formatting utilities
   - Error handling and retry logic

**Deliverables:**
- QuestionToSQLAgent functional with test queries
- Clickhouse optimized for analytics workloads
- Base classes for analytics agents

**Tests:**
- 20+ tests for QuestionToSQLAgent with mock Clickhouse
- 15+ tests for SQL generation and validation
- Query performance benchmarks

#### Week 8: Specialized Analytics Agents

**Tasks:**
1. **ClinicalAgent**
   - Prompt templates for clinical questions
   - Integration with QuestionToSQLAgent
   - Generate clinical metrics (HbA1c, readmissions, outcomes)
   - Output structured JSON for dashboard widgets

2. **PricingAgent**
   - Financial analysis and ROI calculations
   - Cost trend analysis
   - Savings projections
   - Integration with QuestionToSQLAgent

3. **UtilizationAgent**
   - ED visits, hospitalizations, ambulatory care
   - Avoidable utilization analysis
   - Integration with QuestionToSQLAgent

4. **PharmacyAgent**
   - Medication adherence (PDC)
   - Drug costs and trends
   - Generic vs brand analysis
   - Integration with QuestionToSQLAgent

**Deliverables:**
- All 4 specialized analytics agents implemented
- Each agent can generate metrics for their domain
- Validated output matching expected schemas

**Tests:**
- 60+ tests for specialized agents (15 per agent)
- Integration tests with mock Clickhouse data
- Schema validation for all analytics outputs

#### Week 9: Value Proposition Data Generation (Step 4)

**Tasks:**
1. **Value Proposition Analytics Orchestration**
   - Coordinate Analytics Team to generate insights for each priority
   - Map value proposition priorities to relevant agents
   - Execute queries in parallel where possible
   - Aggregate results into ValuePropositionDataJSON

2. **Value Proposition Data API**
   - `POST /api/v1/prospects/{prospect_id}/value-proposition-data/generate` - Trigger generation
   - `GET /api/v1/prospects/{prospect_id}/value-proposition-data/jobs/{job_id}` - Get job status
   - `GET /api/v1/prospects/{prospect_id}/value-proposition-data` - Get generated data
   - Store results in Postgres prospect_value_proposition_data table (JSONB)

3. **Review & Approval**
   - `PUT /api/v1/prospects/{prospect_id}/value-proposition-data/approve` - Approve data
   - Trigger Step 5 (dashboard generation) upon approval

**Deliverables:**
- Complete Step 4 workflow functional
- Analytics Team generating insights for value propositions
- Data stored and retrievable

**Tests:**
- 25+ tests for Step 4 orchestration
- 15+ tests for API endpoints
- End-to-end tests with realistic value propositions

 Dashboard Data Generation (Step 5) & Final Polish

**Tasks:**
1. **Dashboard Data Generation**
   - Use selected dashboard template from Step 1
   - Generate data for each widget using Analytics Team
   - Map widget questions to appropriate agents
   - Store widget data as DashboardDataJSON

2. **Dashboard Data API**
   - `POST /api/v1/prospects/{prospect_id}/dashboard-data/generate` - Trigger generation
   - `GET /api/v1/prospects/{prospect_id}/dashboard-data/jobs/{job_id}` - Get job status
   - `GET /api/v1/prospects/{prospect_id}/dashboard-data` - Get dashboard data
   - Support incremental widget regeneration

3. **End-to-End Testing**
   - Complete workflow from client creation to dashboard data generation
   - Performance testing with realistic data volumes
   - Load testing with concurrent analytics jobs

4. **Final Documentation & Handoff**
   - Complete API documentation
   - Deployment runbook
   - Troubleshooting guide
   - Agent prompt tuning guide

**Deliverables:**
- Complete Step 5 workflow functional
- Full end-to-end workflow tested
- Production-ready deployment documentation

**Tests:**
- 20+ tests for Step 5 orchestration
- 10+ tests for dashboard data APIs
- Complete integration test suite

**Phase 3 Milestone:**
- ✅ Complete Steps 4-5 workflows: Value prop data generation → Dashboard data generation
- ✅ Analytics Team producing accurate, validated insights
- ✅ Test coverage maintained at > 85%
- ✅ **MVP Complete:** All steps (1, 2, 4, 5) functional end-to-end

---

### 8.6 Key Milestones & Dependencies

```mermaid
gantt
    title Triton Platform Implementation Timeline
    dateFormat  YYYY-MM-DD
    section Phase 0
    Foundation & Infrastructure    :p0, 2025-11-01, 2w
    section Phase 1
    Client Management & Research   :p1a, after p0, 1w
    Research Team Agents          :p1b, after p1a, 1w
    Value Prop Derivation         :p1c, after p1b, 1w
    Dashboard Templates           :p1d, after p1c, 1w
    section Phase 2
    Prospect Management           :p2a, after p1d, 1w
    Value Prop Ranking            :p2b, after p2a, 1w
    Integration Testing           :p2c, after p2b, 1w
    section Phase 3
    Analytics Team Foundation     :p3a, after p2c, 1w
    Specialized Agents            :p3b, after p3a, 1w
    Value Prop Data (Step 4)      :p3c, after p3b, 1w
    Dashboard Data (Step 5)       :p3d, after p3c, 1w
```

**Critical Dependencies:**
1. Phase 0 must complete before Phase 1 (foundation required)
2. Research Team (Phase 1) must be complete before reuse in Phase 2
3. Value Proposition workflow (Phase 1) must be complete before ranking (Phase 2)
4. Clickhouse schema (Phase 0) required for Analytics Team (Phase 3)
5. Dashboard template (Phase 1) required for dashboard data generation (Phase 3)

**Risk Mitigation:**
- **LLM API Rate Limits:** Implement exponential backoff and retry logic early (Phase 0)
- **Clickhouse Performance:** Optimize queries and indexes in Phase 3, Week 10
- **Schema Validation Failures:** Build robust mock LLM responses in Phase 0 to catch issues early
- **Integration Complexity:** Regular integration testing at end of each phase
- **Scope Creep:** Focus on MVP features only; defer enhancements to post-MVP backlog

---

### 8.7 Team Structure & Roles

**Recommended Team:**

| Role | Responsibilities | FTE |
|------|------------------|-----|
| **Tech Lead** | Architecture decisions, code review, agent design | 1.0 |
| **Backend Engineer** | FastAPI, Celery, database work | 1.0 |
| **ML/Agent Engineer** | Agno agents, prompt engineering, LLM integration | 1.0 |
| **QA Engineer** | Test framework, fixtures, integration tests | 0.5 |
| **DevOps Engineer** | Docker, AWS, CI/CD, monitoring | 0.5 |

**Total:** 4.0 FTE over 13 weeks

---

### 8.8 Definition of Done

Each phase is considered complete when:

1. **Functionality:**
   - All planned APIs are implemented and functional
   - All agents produce valid, schema-compliant output
   - End-to-end workflow for the phase executes successfully

2. **Testing:**
   - Unit test coverage > 85% for new code
   - All integration tests passing
   - Schema validation tests passing for all outputs

3. **Documentation:**
   - OpenAPI/Swagger docs updated
   - Code comments for complex logic
   - Agent prompt templates documented

4. **Code Quality:**
   - Pre-commit hooks passing (black, flake8, mypy)
   - No critical or high-severity security issues (Bandit scan)
   - Code review approved by Tech Lead

5. **Deployment:**
   - Docker Compose setup updated and tested
   - CI/CD pipeline passing
   - Deployed to staging environment and verified

---

### 8.9 Post-MVP Enhancements (Backlog)

Features deferred to post-MVP:

1. **Step 6 - Dashboard Rendering:** Separate application (out of scope)
2. **AgentOS UI Integration:** Full monitoring dashboard (optional)
3. **WebSocket Support:** Real-time job progress updates
4. **Multi-Tenancy:** Isolate data across organizations
5. **Advanced Caching:** Redis-based caching for frequently accessed data
6. **Agent Fine-Tuning:** Custom fine-tuned models for specialized tasks
7. **Audit Logging:** Comprehensive audit trail for all user actions
8. **Role-Based Access Control (RBAC):** Granular permissions
9. **Analytics Export:** Export dashboard data to Excel, PDF
10. **Batch Processing:** Bulk operations for multiple prospects

---

**End of Section 8**

---

## Appendix A: JSON Schema Definitions

### A.1 ValuePropositionSchema

Complete Pydantic schema for value proposition outputs from the Research Team:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ValuePropositionMetadata(BaseModel):
    """Metadata about the value proposition generation"""
    mode: str = Field(..., description="Derivation mode: 'research' or 'collateral'")
    sources: List[str] = Field(..., description="URLs or document paths used")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Agent confidence in results")

class ValuePropositionPriority(BaseModel):
    """Individual value proposition priority"""
    priority_id: str = Field(..., description="Unique identifier (e.g., 'vp_1', 'vp_2')")
    title: str = Field(..., min_length=10, max_length=200, description="Priority title")
    description: str = Field(..., min_length=50, description="Detailed description")
    clinical_focus: List[str] = Field(..., description="Clinical areas (e.g., ['Diabetes', 'Hypertension'])")
    target_population: str = Field(..., description="Target member population")
    expected_outcomes: List[str] = Field(..., min_items=1, description="Expected measurable outcomes")
    data_requirements: List[str] = Field(..., description="Data needed to support this priority")
    supporting_evidence: List[str] = Field(..., description="Evidence sources (URLs or citations)")

class ValuePropositionSchema(BaseModel):
    """Complete value proposition JSON structure"""
    metadata: ValuePropositionMetadata
    value_proposition_priorities: List[ValuePropositionPriority] = Field(..., min_items=3, max_items=10)
    executive_summary: str = Field(..., min_length=200, description="High-level summary of all priorities")

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "mode": "collateral",
                    "sources": ["s3://bucket/livongo_roi_sheet.pdf"],
                    "generated_at": "2025-01-15T10:30:00Z",
                    "confidence_score": 0.92
                },
                "value_proposition_priorities": [
                    {
                        "priority_id": "vp_1",
                        "title": "Diabetes Management & HbA1c Reduction",
                        "description": "Implement comprehensive diabetes program...",
                        "clinical_focus": ["Diabetes", "Chronic Care Management"],
                        "target_population": "Members with diabetes diagnosis (ICD-10: E11.*)",
                        "expected_outcomes": [
                            "Reduce average HbA1c by 0.8-1.2%",
                            "Decrease diabetes-related ED visits by 15%"
                        ],
                        "data_requirements": [
                            "Lab results (HbA1c, fasting glucose)",
                            "ED visit claims with diabetes diagnosis",
                            "Medication adherence (PDC for diabetes drugs)"
                        ],
                        "supporting_evidence": [
                            "https://livongo.com/roi-study-2023",
                            "Internal analysis of similar client outcomes"
                        ]
                    }
                ],
                "executive_summary": "The value proposition focuses on chronic disease management..."
            }
        }
```

---

### A.2 CompanyInformationSchema

Schema for prospect company research outputs:

```python
class CompanyPriority(BaseModel):
    """Strategic priority identified for the prospect"""
    priority_id: str = Field(..., description="Unique identifier")
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=50)
    strategic_importance: str = Field(..., description="Why this matters to the company")
    timeline: Optional[str] = Field(None, description="Expected timeline for this priority")
    budget_allocation: Optional[str] = Field(None, description="Budget info if available")

class CompanyFinancials(BaseModel):
    """Financial information about the prospect"""
    revenue: Optional[str] = Field(None, description="Annual revenue")
    revenue_growth: Optional[str] = Field(None, description="YoY growth rate")
    profitability: Optional[str] = Field(None, description="Profit margin or status")
    market_cap: Optional[str] = Field(None, description="Market capitalization (if public)")

class CompanyInformationMetadata(BaseModel):
    """Metadata for company research"""
    sources: List[str] = Field(..., description="Sources used for research")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    research_quality: Optional[str] = Field(None, description="High/Medium/Low based on source quality")

class CompanyInformationSchema(BaseModel):
    """Complete company information JSON structure"""
    metadata: CompanyInformationMetadata
    company_name: str = Field(..., min_length=2)
    industry: str = Field(..., description="Primary industry")
    size: str = Field(..., description="Employee count or size category")
    headquarters: Optional[str] = Field(None, description="Location")
    strategic_priorities: List[CompanyPriority] = Field(..., min_items=1, max_items=10)
    financials: Optional[CompanyFinancials] = None
    recent_news: List[str] = Field(default_factory=list, description="Recent news or announcements")
    competitive_landscape: Optional[str] = Field(None, description="Key competitors and positioning")

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "sources": [
                        "https://wellmark.com/about",
                        "https://www.sec.gov/edgar/...",
                        "https://news.wellmark.com/2024/strategic-plan"
                    ],
                    "generated_at": "2025-01-15T11:00:00Z",
                    "research_quality": "High"
                },
                "company_name": "Wellmark Blue Cross Blue Shield",
                "industry": "Health Insurance",
                "size": "1000-5000 employees",
                "headquarters": "Des Moines, IA",
                "strategic_priorities": [
                    {
                        "priority_id": "sp_1",
                        "title": "Value-Based Care Transformation",
                        "description": "Shift from fee-for-service to value-based reimbursement models...",
                        "strategic_importance": "Core to 2025 strategic plan",
                        "timeline": "2025-2027",
                        "budget_allocation": "$50M investment announced"
                    }
                ],
                "financials": {
                    "revenue": "$3.2B annual",
                    "revenue_growth": "4.5% YoY",
                    "profitability": "Operating margin 2.8%"
                }
            }
        }
```

---

### A.3 DashboardTemplateSchema

Schema for dashboard template configurations:

```python
class WidgetConfiguration(BaseModel):
    """Configuration for a single dashboard widget"""
    widget_id: str = Field(..., description="Unique widget identifier")
    widget_type: str = Field(..., description="Type: 'metric', 'chart', 'table', 'map'")
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., description="What this widget shows")
    analytics_question: str = Field(..., description="Question to ask Analytics Team")
    visualization_config: dict = Field(..., description="Visualization parameters (chart type, axes, etc.)")
    data_refresh_frequency: str = Field(default="daily", description="How often to refresh")
    priority_mapping: Optional[str] = Field(None, description="Which value prop priority this supports")

class DashboardTemplateMetadata(BaseModel):
    """Metadata for dashboard template"""
    template_id: str = Field(..., description="Unique template identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    layout: str = Field(default="grid", description="Layout type: grid, flex, etc.")

class DashboardTemplateSchema(BaseModel):
    """Complete dashboard template JSON structure"""
    metadata: DashboardTemplateMetadata
    template_name: str = Field(..., min_length=5, max_length=100)
    template_description: str = Field(..., description="Overview of this template")
    widgets: List[WidgetConfiguration] = Field(..., min_items=4, max_items=12)

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "template_id": "tmpl_diabetes_exec",
                    "generated_at": "2025-01-15T12:00:00Z",
                    "layout": "grid"
                },
                "template_name": "Diabetes Executive Dashboard",
                "template_description": "Executive-level view of diabetes program performance",
                "widgets": [
                    {
                        "widget_id": "w_hba1c_trend",
                        "widget_type": "chart",
                        "title": "Average HbA1c Trend",
                        "description": "12-month trend of average HbA1c levels for diabetic members",
                        "analytics_question": "What is the average HbA1c by month for the last 12 months?",
                        "visualization_config": {
                            "chart_type": "line",
                            "x_axis": "month",
                            "y_axis": "avg_hba1c",
                            "target_line": 7.0
                        },
                        "data_refresh_frequency": "weekly",
                        "priority_mapping": "vp_1"
                    },
                    {
                        "widget_id": "w_cost_savings",
                        "widget_type": "metric",
                        "title": "Projected Annual Savings",
                        "description": "Total projected annual savings from diabetes program",
                        "analytics_question": "What is the projected annual cost savings from reducing diabetes complications?",
                        "visualization_config": {
                            "format": "currency",
                            "comparison": "vs_baseline",
                            "trend_indicator": true
                        },
                        "data_refresh_frequency": "monthly",
                        "priority_mapping": "vp_1"
                    }
                ]
            }
        }
```

---

### A.4 Analytics Output Schemas

#### A.4.1 ValuePropositionDataSchema

Schema for analytics data generated for value propositions (Step 4):

```python
class BaselineMetric(BaseModel):
    """Baseline metric before intervention"""
    metric_name: str = Field(..., description="Name of the metric")
    value: float = Field(..., description="Baseline value")
    unit: str = Field(..., description="Unit of measurement")
    measurement_period: str = Field(..., description="Time period for baseline (e.g., '2024 Q1-Q4')")
    sample_size: int = Field(..., ge=1, description="Number of members in calculation")

class ProjectedImpact(BaseModel):
    """Projected impact after intervention"""
    metric_name: str = Field(..., description="Name of the metric")
    baseline_value: float = Field(..., description="Current/baseline value")
    projected_value: float = Field(..., description="Projected value after intervention")
    improvement_percentage: float = Field(..., description="Percentage improvement")
    unit: str = Field(..., description="Unit of measurement")
    confidence_level: str = Field(default="medium", description="Confidence: high/medium/low")
    assumptions: List[str] = Field(..., description="Key assumptions in projection")

class PriorityInsights(BaseModel):
    """Insights for a specific value proposition priority"""
    priority_id: str = Field(..., description="Links to ValuePropositionPriority.priority_id")
    baseline_metrics: List[BaselineMetric] = Field(..., min_items=1)
    projected_impacts: List[ProjectedImpact] = Field(..., min_items=1)
    supporting_analysis: str = Field(..., description="Narrative analysis of the data")
    data_quality_notes: Optional[str] = Field(None, description="Any data quality concerns")

class ValuePropositionDataSchema(BaseModel):
    """Complete value proposition analytics data (Step 4 output)"""
    prospect_id: str = Field(..., description="UUID of the prospect")
    value_proposition_id: str = Field(..., description="UUID of the value proposition")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    priority_insights: List[PriorityInsights] = Field(..., min_items=1)
    executive_summary: str = Field(..., min_length=200, description="Summary of all findings")

    class Config:
        json_schema_extra = {
            "example": {
                "prospect_id": "550e8400-e29b-41d4-a716-446655440000",
                "value_proposition_id": "660e8400-e29b-41d4-a716-446655440001",
                "generated_at": "2025-01-15T14:00:00Z",
                "priority_insights": [
                    {
                        "priority_id": "vp_1",
                        "baseline_metrics": [
                            {
                                "metric_name": "Average HbA1c",
                                "value": 8.2,
                                "unit": "%",
                                "measurement_period": "2024 Q1-Q4",
                                "sample_size": 12543
                            },
                            {
                                "metric_name": "Diabetes-related ED visits per 1000 members",
                                "value": 145.2,
                                "unit": "visits per 1000",
                                "measurement_period": "2024 Q1-Q4",
                                "sample_size": 12543
                            }
                        ],
                        "projected_impacts": [
                            {
                                "metric_name": "Average HbA1c",
                                "baseline_value": 8.2,
                                "projected_value": 7.4,
                                "improvement_percentage": 9.8,
                                "unit": "%",
                                "confidence_level": "high",
                                "assumptions": [
                                    "70% program engagement rate",
                                    "Based on Livongo published outcomes data",
                                    "12-month intervention period"
                                ]
                            }
                        ],
                        "supporting_analysis": "Current diabetes population shows elevated HbA1c levels...",
                        "data_quality_notes": "High quality: 95% of members have HbA1c data in last 6 months"
                    }
                ],
                "executive_summary": "Analysis of 12,543 diabetic members reveals significant opportunity..."
            }
        }
```

#### A.4.2 DashboardDataSchema

Schema for widget-specific analytics data (Step 5 output):

```python
class WidgetDataPoint(BaseModel):
    """Single data point for a widget"""
    timestamp: Optional[datetime] = None
    label: Optional[str] = None
    value: float = Field(..., description="Numeric value")
    formatted_value: Optional[str] = Field(None, description="Formatted for display (e.g., '$1.2M')")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional context")

class WidgetData(BaseModel):
    """Data for a single widget"""
    widget_id: str = Field(..., description="Links to WidgetConfiguration.widget_id")
    data_points: List[WidgetDataPoint] = Field(..., min_items=1)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    query_used: Optional[str] = Field(None, description="SQL query used (for debugging)")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")

class DashboardDataSchema(BaseModel):
    """Complete dashboard data for all widgets (Step 5 output)"""
    prospect_id: str = Field(..., description="UUID of the prospect")
    template_id: str = Field(..., description="Template being used")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    widgets_data: List[WidgetData] = Field(..., min_items=1)

    class Config:
        json_schema_extra = {
            "example": {
                "prospect_id": "550e8400-e29b-41d4-a716-446655440000",
                "template_id": "tmpl_diabetes_exec",
                "generated_at": "2025-01-15T15:00:00Z",
                "widgets_data": [
                    {
                        "widget_id": "w_hba1c_trend",
                        "data_points": [
                            {
                                "timestamp": "2024-01-01T00:00:00Z",
                                "label": "Jan 2024",
                                "value": 8.3,
                                "formatted_value": "8.3%"
                            },
                            {
                                "timestamp": "2024-02-01T00:00:00Z",
                                "label": "Feb 2024",
                                "value": 8.2,
                                "formatted_value": "8.2%"
                            }
                        ],
                        "generated_at": "2025-01-15T15:00:00Z",
                        "query_used": "SELECT toStartOfMonth(lab_date) as month, avg(hba1c_value)...",
                        "cache_ttl": 604800
                    },
                    {
                        "widget_id": "w_cost_savings",
                        "data_points": [
                            {
                                "label": "Projected Annual Savings",
                                "value": 1250000,
                                "formatted_value": "$1.25M"
                            }
                        ],
                        "generated_at": "2025-01-15T15:00:00Z"
                    }
                ]
            }
        }
```

---

### A.5 Job Schema

Generic job tracking schema used across all async operations:

```python
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, Enum):
    VALUE_PROP_DERIVATION = "value_prop_derivation"
    VALUE_PROP_REFINEMENT = "value_prop_refinement"
    TEMPLATE_GENERATION = "template_generation"
    COMPANY_RESEARCH = "company_research"
    VALUE_PROP_RANKING = "value_prop_ranking"
    VALUE_PROP_DATA_GENERATION = "value_prop_data_generation"
    DASHBOARD_DATA_GENERATION = "dashboard_data_generation"

class JobProgress(BaseModel):
    """Progress tracking for long-running jobs"""
    percentage: int = Field(0, ge=0, le=100, description="Completion percentage")
    current_step: Optional[str] = Field(None, description="Current step description")
    estimated_completion: Optional[datetime] = Field(None, description="ETA")

class JobError(BaseModel):
    """Error information for failed jobs"""
    error_code: str = Field(..., description="Error code for categorization")
    error_message: str = Field(..., description="Human-readable error message")
    stack_trace: Optional[str] = Field(None, description="Stack trace (if available)")
    retry_count: int = Field(0, description="Number of retries attempted")

class JobSchema(BaseModel):
    """Generic job tracking schema"""
    job_id: str = Field(..., description="UUID of the job")
    job_type: JobType = Field(..., description="Type of job")
    status: JobStatus = Field(default=JobStatus.PENDING)
    resource_type: Optional[str] = Field(None, description="E.g., 'client', 'prospect'")
    resource_id: Optional[str] = Field(None, description="UUID of the resource")
    input_data: Optional[dict] = Field(None, description="Input parameters")
    output_data: Optional[dict] = Field(None, description="Result data (when completed)")
    progress: Optional[JobProgress] = None
    error: Optional[JobError] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "770e8400-e29b-41d4-a716-446655440002",
                "job_type": "value_prop_derivation",
                "status": "processing",
                "resource_type": "client",
                "resource_id": "660e8400-e29b-41d4-a716-446655440001",
                "input_data": {
                    "mode": "collateral",
                    "document_ids": ["s3://bucket/livongo_roi.pdf"]
                },
                "progress": {
                    "percentage": 65,
                    "current_step": "Synthesizing findings from 3 sources",
                    "estimated_completion": "2025-01-15T10:45:00Z"
                },
                "created_at": "2025-01-15T10:30:00Z",
                "started_at": "2025-01-15T10:31:00Z"
            }
        }
```

---

**End of Appendix A**

---

## Appendix B: Reference Data Examples

### B.1 Overview

This appendix contains complete JSON examples for testing and development. These examples are based on real-world scenarios and should be stored as fixtures in the `tests/fixtures/` directory.

**Reference Implementation:**
- **Repository:** (To be determined - will contain reference implementations)
- **Branch:** `feature/triton-platform-mvp`
- **Fixture Location:** `tests/fixtures/`

---

### B.2 Livongo Value Proposition Example (Collateral Mode)

**File:** `tests/fixtures/value_propositions/livongo_value_proposition_derived.json`

This example represents a value proposition derived from Livongo marketing collateral and ROI sheets.

```json
{
  "metadata": {
    "mode": "collateral",
    "sources": [
      "s3://triton-documents/clients/livongo/Livongo_Diabetes_ROI_Sheet_2024.pdf",
      "s3://triton-documents/clients/livongo/Livongo_Product_Overview.pdf",
      "https://www.teladoc.com/health-plans/chronic-condition-management/"
    ],
    "generated_at": "2025-01-15T10:30:00Z",
    "confidence_score": 0.92
  },
  "value_proposition_priorities": [
    {
      "priority_id": "vp_1",
      "title": "Diabetes Management & HbA1c Reduction",
      "description": "Implement Livongo's comprehensive digital diabetes management program to reduce HbA1c levels through continuous glucose monitoring, personalized coaching, and AI-driven insights. The program provides members with connected meters, unlimited test strips, and 24/7 access to certified diabetes educators.",
      "clinical_focus": [
        "Diabetes Type 2",
        "Diabetes Type 1",
        "Pre-diabetes",
        "Chronic Care Management"
      ],
      "target_population": "Members with diabetes diagnosis (ICD-10: E11.*, E10.*) or HbA1c >= 6.5%",
      "expected_outcomes": [
        "Reduce average HbA1c by 0.8-1.2 percentage points within 12 months",
        "Decrease diabetes-related ED visits by 12-18%",
        "Improve medication adherence (PDC) to 75%+",
        "Reduce long-term complications (retinopathy, neuropathy, nephropathy) by 15%"
      ],
      "data_requirements": [
        "Lab results: HbA1c, fasting glucose, lipid panel (last 12 months)",
        "Medical claims: ED visits, hospitalizations with diabetes DX",
        "Pharmacy claims: Diabetes medications (insulin, metformin, GLP-1s, etc.)",
        "Medication adherence metrics (PDC for diabetes drug classes)",
        "Complication diagnoses: Retinopathy, neuropathy, nephropathy ICD codes"
      ],
      "supporting_evidence": [
        "Livongo published study: 1.1% average HbA1c reduction in 12 months (n=12,000)",
        "https://www.teladoc.com/health-plans/chronic-condition-management/diabetes/",
        "Clinical validation: JAMA Network Open 2020 study",
        "Internal client data: 15% reduction in diabetes-related ED visits at similar payer"
      ]
    },
    {
      "priority_id": "vp_2",
      "title": "Hypertension Control & Cardiovascular Risk Reduction",
      "description": "Deploy Livongo's hypertension management solution to improve blood pressure control and reduce cardiovascular events. Members receive connected blood pressure monitors, personalized action plans, and coaching to achieve target BP levels.",
      "clinical_focus": [
        "Hypertension",
        "Cardiovascular Disease",
        "Stroke Prevention",
        "Heart Failure"
      ],
      "target_population": "Members with hypertension diagnosis (ICD-10: I10.*) or systolic BP >= 140 mmHg",
      "expected_outcomes": [
        "Achieve BP control (<140/90 mmHg) for 65% of members (up from baseline ~45%)",
        "Reduce cardiovascular events (MI, stroke) by 10-15%",
        "Decrease hypertension-related ED visits by 12%",
        "Improve medication adherence to antihypertensive drugs"
      ],
      "data_requirements": [
        "Vital signs: Blood pressure readings from medical claims",
        "Medical claims: Cardiovascular events (MI, stroke, heart failure)",
        "Pharmacy claims: Antihypertensive medications (ACE inhibitors, ARBs, beta blockers, etc.)",
        "Medication adherence metrics (PDC for hypertension drugs)",
        "ED visit and hospitalization data with hypertension diagnosis"
      ],
      "supporting_evidence": [
        "Livongo HTN study: 20% improvement in BP control rates",
        "https://www.teladoc.com/health-plans/chronic-condition-management/hypertension/",
        "AHA guidelines: BP control associated with 25% reduction in CV events",
        "Published outcomes: Teladoc Health Outcomes Report 2023"
      ]
    },
    {
      "priority_id": "vp_3",
      "title": "Mental Health & Behavioral Health Integration",
      "description": "Integrate Livongo's mental health platform (myStrength) to address depression, anxiety, and stress which often co-occur with chronic conditions. Provide evidence-based CBT programs, meditation, and access to licensed therapists.",
      "clinical_focus": [
        "Depression",
        "Anxiety",
        "Stress Management",
        "Behavioral Health"
      ],
      "target_population": "Members with mental health diagnoses (ICD-10: F32.*, F41.*) or screening positive on PHQ-9/GAD-7",
      "expected_outcomes": [
        "Reduce PHQ-9 scores by 3+ points for members with depression",
        "Decrease mental health-related ED visits by 10%",
        "Improve engagement with chronic disease management programs (15% higher adherence)",
        "Reduce absenteeism and improve productivity for employed members"
      ],
      "data_requirements": [
        "Mental health claims: Therapy sessions, psychiatry visits, inpatient behavioral health",
        "Pharmacy claims: Antidepressants, anxiolytics",
        "Screening data: PHQ-9, GAD-7 scores (if available)",
        "ED visit and hospitalization data with mental health diagnosis",
        "Engagement data: Chronic disease program participation rates"
      ],
      "supporting_evidence": [
        "myStrength clinical validation: 50% reduction in depression symptoms",
        "https://www.teladoc.com/health-plans/mental-health/",
        "Published study: Digital mental health interventions show 3.5 PHQ-9 point reduction",
        "ROI analysis: $3-$6 saved per $1 invested in mental health programs"
      ]
    },
    {
      "priority_id": "vp_4",
      "title": "Weight Management & Obesity Reduction",
      "description": "Leverage Livongo's weight management program to help members achieve sustainable weight loss, reducing obesity-related comorbidities and healthcare costs. Program includes nutrition coaching, activity tracking, and behavioral change support.",
      "clinical_focus": [
        "Obesity",
        "Weight Management",
        "Pre-diabetes Prevention",
        "Metabolic Syndrome"
      ],
      "target_population": "Members with BMI >= 30 or BMI >= 27 with obesity-related conditions",
      "expected_outcomes": [
        "Average weight loss of 5-7% of body weight within 6 months",
        "Reduce progression from pre-diabetes to diabetes by 30%",
        "Decrease obesity-related complications (sleep apnea, osteoarthritis, GERD)",
        "Improve quality of life scores and functional status"
      ],
      "data_requirements": [
        "Biometric data: BMI, weight measurements from claims",
        "Lab results: Glucose, lipids, liver enzymes",
        "Medical claims: Obesity-related diagnoses and complications",
        "Pharmacy claims: Weight loss medications (if any)",
        "Diabetes progression data: HbA1c trends for pre-diabetic members"
      ],
      "supporting_evidence": [
        "Livongo weight program outcomes: Average 6.2% weight loss at 6 months",
        "DPP (Diabetes Prevention Program): 5-7% weight loss reduces diabetes incidence by 58%",
        "https://www.teladoc.com/health-plans/chronic-condition-management/weight-management/",
        "Cost impact: Obesity-related healthcare costs $1,861 higher per member annually"
      ]
    }
  ],
  "executive_summary": "The Livongo value proposition centers on comprehensive chronic disease management across diabetes, hypertension, mental health, and weight management. By leveraging digital health technology, connected devices, and personalized coaching, the program aims to improve clinical outcomes, reduce avoidable utilization, and generate ROI through reduced complications and ED visits. Key clinical targets include 0.8-1.2% HbA1c reduction for diabetics, 20% improvement in hypertension control rates, and 5-7% weight loss for obesity management. The integrated approach addresses the whole person, recognizing the interconnection between physical and mental health. Expected ROI is $3-$4 per member per month based on published outcomes and similar payer implementations."
}
```

---

### B.3 Wellmark Company Information Example (Research Mode)

**File:** `tests/fixtures/company_information/wellmark_company_research.json`

This example represents company research conducted on Wellmark Blue Cross Blue Shield as a prospect.

```json
{
  "metadata": {
    "sources": [
      "https://www.wellmark.com/about-us",
      "https://www.wellmark.com/newsroom/2024-strategic-priorities",
      "https://www.sec.gov/edgar/searchedgar/companysearch.html",
      "https://www.desmoinesregister.com/story/business/2024/wellmark-announces-value-based-care-initiative",
      "https://www.linkedin.com/company/wellmark-blue-cross-and-blue-shield/"
    ],
    "generated_at": "2025-01-15T11:00:00Z",
    "research_quality": "High"
  },
  "company_name": "Wellmark Blue Cross Blue Shield",
  "industry": "Health Insurance",
  "size": "2,000-3,000 employees",
  "headquarters": "Des Moines, Iowa",
  "strategic_priorities": [
    {
      "priority_id": "sp_1",
      "title": "Value-Based Care Transformation",
      "description": "Wellmark announced a comprehensive shift toward value-based care models, moving away from traditional fee-for-service reimbursement. The initiative aims to reward providers for quality outcomes and preventive care rather than volume of services. Focus areas include chronic disease management, preventive care incentives, and population health management. The company has committed to transitioning 50% of payments to value-based arrangements by 2026.",
      "strategic_importance": "Core to 2025-2027 strategic plan; CEO-level initiative with board oversight",
      "timeline": "2025-2027 (3-year transformation)",
      "budget_allocation": "$50M investment announced for technology infrastructure and provider partnerships"
    },
    {
      "priority_id": "sp_2",
      "title": "Digital Health & Member Engagement",
      "description": "Investment in digital health platforms to improve member engagement, self-service capabilities, and access to care. Initiatives include mobile app enhancement, telehealth expansion, and integration of wearable devices for chronic disease monitoring. Goal is to achieve 70% member digital engagement by 2026 (up from current 45%).",
      "strategic_importance": "Supports value-based care strategy and competitive differentiation",
      "timeline": "2024-2026",
      "budget_allocation": "$25M for digital platform development and integrations"
    },
    {
      "priority_id": "sp_3",
      "title": "Social Determinants of Health (SDOH) Programs",
      "description": "Wellmark is expanding efforts to address social determinants of health including food insecurity, housing instability, and transportation barriers. Programs include partnerships with community organizations, food assistance programs for diabetic members, and transportation services for medical appointments. Focus on rural Iowa and South Dakota populations.",
      "strategic_importance": "Aligns with CMS Star Ratings improvement goals and community health mission",
      "timeline": "2025-2028",
      "budget_allocation": "$15M annual funding for SDOH programs"
    },
    {
      "priority_id": "sp_4",
      "title": "Medicare Advantage Growth",
      "description": "Aggressive expansion of Medicare Advantage product offerings across Iowa and South Dakota. Goal is to grow MA membership by 25% annually, reaching 150,000 members by 2027. Focus on 4+ Star quality ratings to maximize CMS bonuses and member retention. Emphasis on comprehensive benefits including dental, vision, and wellness programs.",
      "strategic_importance": "Key growth driver; MA represents 30% of revenue with higher margins than commercial",
      "timeline": "2025-2027",
      "budget_allocation": "$40M for MA product development, marketing, and network expansion"
    },
    {
      "priority_id": "sp_5",
      "title": "Chronic Disease Management Excellence",
      "description": "Wellmark aims to become the regional leader in chronic disease outcomes, specifically targeting diabetes, hypertension, and behavioral health. Programs include enhanced care coordination, digital therapeutic partnerships, and integrated physical-behavioral health models. KPIs include HEDIS measure improvement, hospital readmission reduction, and member satisfaction scores.",
      "strategic_importance": "Directly supports value-based care contracts and Star Ratings; critical for employer retention",
      "timeline": "2025-2026",
      "budget_allocation": "$30M for care management infrastructure and vendor partnerships"
    }
  ],
  "financials": {
    "revenue": "$3.2B annual premium revenue (2024)",
    "revenue_growth": "4.5% YoY (2023-2024)",
    "profitability": "Operating margin 2.8%; Surplus ratio 3.1%",
    "market_cap": "Not publicly traded (mutual insurance company)"
  },
  "recent_news": [
    "Wellmark announces $50M value-based care initiative (Jan 2025)",
    "Partnership with local health systems to launch ACO model (Dec 2024)",
    "Expansion of telehealth services to rural Iowa communities (Nov 2024)",
    "Wellmark achieves 4.0 Star Rating for Medicare Advantage plans (Oct 2024)",
    "Launch of diabetes prevention program with community health centers (Sept 2024)"
  ],
  "competitive_landscape": "Wellmark is the dominant payer in Iowa with approximately 45% market share. Primary competitors include UnitedHealthcare (20% share), Aetna/CVS Health (12%), and regional players. Competitive advantages include strong provider relationships, brand recognition in Iowa/South Dakota, and focus on rural/agricultural communities. Key competitive threats include national payers with greater scale, employer self-insurance trends, and Medicare Advantage competition from UHC and Humana. Wellmark differentiates through local market expertise, community health focus, and personalized service model."
}
```

---

### B.4 Dashboard Template Example - Diabetes Executive Dashboard

**File:** `tests/fixtures/dashboard_templates/diabetes_executive_dashboard.json`

```json
{
  "metadata": {
    "template_id": "tmpl_diabetes_exec_001",
    "generated_at": "2025-01-15T12:00:00Z",
    "layout": "grid"
  },
  "template_name": "Diabetes Executive Dashboard",
  "template_description": "Executive-level dashboard providing comprehensive view of diabetes program performance, clinical outcomes, utilization trends, and financial impact. Designed for C-suite and VP-level stakeholders.",
  "widgets": [
    {
      "widget_id": "w_hba1c_trend",
      "widget_type": "chart",
      "title": "Average HbA1c Trend (12 Months)",
      "description": "Monthly trend of average HbA1c levels for all diabetic members, with goal line at 7.0%",
      "analytics_question": "What is the average HbA1c by month for the last 12 months for members with diabetes diagnosis?",
      "visualization_config": {
        "chart_type": "line",
        "x_axis": "month",
        "y_axis": "avg_hba1c",
        "y_axis_label": "Average HbA1c (%)",
        "target_line": 7.0,
        "target_label": "ADA Goal (<7.0%)",
        "show_data_points": true,
        "color_scheme": "clinical"
      },
      "data_refresh_frequency": "weekly",
      "priority_mapping": "vp_1"
    },
    {
      "widget_id": "w_cost_savings",
      "widget_type": "metric",
      "title": "Projected Annual Savings",
      "description": "Total projected annual cost savings from diabetes program based on reduced complications and avoidable utilization",
      "analytics_question": "What is the projected annual cost savings from reducing diabetes complications and ED visits based on current program engagement?",
      "visualization_config": {
        "format": "currency",
        "comparison": "vs_baseline",
        "trend_indicator": true,
        "show_confidence_interval": true,
        "prefix": "$",
        "precision": 0
      },
      "data_refresh_frequency": "monthly",
      "priority_mapping": "vp_1"
    },
    {
      "widget_id": "w_ed_visits_rate",
      "widget_type": "chart",
      "title": "Diabetes-Related ED Visits per 1000 Members",
      "description": "Quarterly trend of diabetes-related emergency department visits normalized per 1000 diabetic members",
      "analytics_question": "What is the rate of diabetes-related ED visits per 1000 diabetic members by quarter for the last 8 quarters?",
      "visualization_config": {
        "chart_type": "bar",
        "x_axis": "quarter",
        "y_axis": "ed_visit_rate",
        "y_axis_label": "ED Visits per 1000",
        "show_benchmark": true,
        "benchmark_value": 120,
        "benchmark_label": "National Average",
        "color_scheme": "utilization"
      },
      "data_refresh_frequency": "monthly",
      "priority_mapping": "vp_1"
    },
    {
      "widget_id": "w_medication_adherence",
      "widget_type": "metric",
      "title": "Diabetes Medication Adherence (PDC)",
      "description": "Proportion of days covered (PDC) for diabetes medications, targeting 80% or higher",
      "analytics_question": "What percentage of diabetic members have PDC >= 80% for diabetes medications in the last 12 months?",
      "visualization_config": {
        "format": "percentage",
        "comparison": "vs_target",
        "target_value": 80,
        "trend_indicator": true,
        "color_scheme": "quality",
        "precision": 1
      },
      "data_refresh_frequency": "monthly",
      "priority_mapping": "vp_1"
    },
    {
      "widget_id": "w_population_stratification",
      "widget_type": "chart",
      "title": "Diabetes Population by Risk Level",
      "description": "Distribution of diabetic members across risk strata (low, medium, high, very high) based on HbA1c, complications, and comorbidities",
      "analytics_question": "What is the distribution of diabetic members by risk stratification level (based on HbA1c >= 9%, complications, comorbidities)?",
      "visualization_config": {
        "chart_type": "pie",
        "show_labels": true,
        "show_percentages": true,
        "show_counts": true,
        "color_scheme": "risk",
        "legend_position": "right"
      },
      "data_refresh_frequency": "monthly",
      "priority_mapping": "vp_1"
    },
    {
      "widget_id": "w_complication_rates",
      "widget_type": "table",
      "title": "Diabetes Complication Rates",
      "description": "Prevalence of major diabetes complications including retinopathy, neuropathy, nephropathy, and cardiovascular disease",
      "analytics_question": "What are the prevalence rates of diabetes complications (retinopathy, neuropathy, nephropathy, CVD) among diabetic members?",
      "visualization_config": {
        "columns": ["complication_type", "prevalence_rate", "member_count", "vs_benchmark"],
        "sortable": true,
        "show_sparklines": true,
        "highlight_rows": "above_benchmark",
        "format_rules": {
          "prevalence_rate": "percentage",
          "vs_benchmark": "delta_percentage"
        }
      },
      "data_refresh_frequency": "quarterly",
      "priority_mapping": "vp_1"
    }
  ]
}
```

---

### B.5 Value Proposition Data Example (Step 4 Output)

**File:** `tests/fixtures/analytics/wellmark_livongo_value_prop_data.json`

This example shows analytics data generated for Wellmark after selecting the Livongo value proposition.

```json
{
  "prospect_id": "550e8400-e29b-41d4-a716-446655440000",
  "value_proposition_id": "660e8400-e29b-41d4-a716-446655440001",
  "generated_at": "2025-01-15T14:00:00Z",
  "priority_insights": [
    {
      "priority_id": "vp_1",
      "baseline_metrics": [
        {
          "metric_name": "Average HbA1c",
          "value": 8.2,
          "unit": "%",
          "measurement_period": "2024 Q1-Q4",
          "sample_size": 12543
        },
        {
          "metric_name": "Diabetes-related ED visits per 1000 members",
          "value": 145.2,
          "unit": "visits per 1000",
          "measurement_period": "2024 Q1-Q4",
          "sample_size": 12543
        },
        {
          "metric_name": "Medication adherence (PDC >= 80%)",
          "value": 62.3,
          "unit": "% of members",
          "measurement_period": "2024 Q1-Q4",
          "sample_size": 12543
        },
        {
          "metric_name": "Members with uncontrolled diabetes (HbA1c >= 9%)",
          "value": 28.5,
          "unit": "% of diabetic population",
          "measurement_period": "2024 Q1-Q4",
          "sample_size": 12543
        },
        {
          "metric_name": "Diabetes-related inpatient admissions per 1000",
          "value": 67.8,
          "unit": "admissions per 1000",
          "measurement_period": "2024 Q1-Q4",
          "sample_size": 12543
        }
      ],
      "projected_impacts": [
        {
          "metric_name": "Average HbA1c",
          "baseline_value": 8.2,
          "projected_value": 7.4,
          "improvement_percentage": 9.8,
          "unit": "%",
          "confidence_level": "high",
          "assumptions": [
            "70% program enrollment rate based on similar payer implementations",
            "Based on Livongo published outcomes: 1.1% average HbA1c reduction",
            "12-month intervention period with full engagement",
            "Assumes current care management programs continue"
          ]
        },
        {
          "metric_name": "Diabetes-related ED visits per 1000 members",
          "baseline_value": 145.2,
          "projected_value": 122.8,
          "improvement_percentage": 15.4,
          "unit": "visits per 1000",
          "confidence_level": "high",
          "assumptions": [
            "Based on internal analysis of similar payer: 15% ED visit reduction",
            "Assumes improved glucose control reduces hypoglycemic and hyperglycemic events",
            "12-18 month timeframe to achieve full impact",
            "Requires active care coordination integration"
          ]
        },
        {
          "metric_name": "Medication adherence (PDC >= 80%)",
          "baseline_value": 62.3,
          "projected_value": 75.0,
          "improvement_percentage": 20.4,
          "unit": "% of members",
          "confidence_level": "medium",
          "assumptions": [
            "Digital coaching and reminders improve adherence",
            "Based on Livongo published data on adherence improvement",
            "Assumes integration with pharmacy benefits for refill reminders",
            "May require 18-24 months to achieve full impact"
          ]
        },
        {
          "metric_name": "Members with uncontrolled diabetes (HbA1c >= 9%)",
          "baseline_value": 28.5,
          "projected_value": 18.0,
          "improvement_percentage": 36.8,
          "unit": "% of diabetic population",
          "confidence_level": "high",
          "assumptions": [
            "Intensive coaching targets high-risk members first",
            "Published Livongo outcomes show greater impact on uncontrolled diabetes",
            "Assumes care management escalation for non-responders",
            "12-month intervention period"
          ]
        },
        {
          "metric_name": "Diabetes-related inpatient admissions per 1000",
          "baseline_value": 67.8,
          "projected_value": 59.2,
          "improvement_percentage": 12.7,
          "unit": "admissions per 1000",
          "confidence_level": "medium",
          "assumptions": [
            "Improved HbA1c and ED visit reduction leads to fewer complications",
            "Hospitalization reduction lags clinical improvement by 6-12 months",
            "Conservative estimate based on indirect effects",
            "Requires 18-24 months to see full impact"
          ]
        }
      ],
      "supporting_analysis": "Wellmark's current diabetic population of 12,543 members shows significant opportunity for improvement. Average HbA1c of 8.2% is well above the ADA goal of <7.0%, and 28.5% of members have severely uncontrolled diabetes (HbA1c >= 9%). The diabetes-related ED visit rate of 145.2 per 1000 is 21% above the national benchmark of 120 per 1000. Medication adherence at 62.3% (PDC >= 80%) is below the HEDIS quality threshold of 80%, indicating significant gaps in medication management. Geographic analysis shows higher HbA1c levels in rural Iowa counties (average 8.5%) compared to urban areas (8.0%), suggesting access barriers that digital health can address. Age stratification reveals 35% of diabetic members are under 65 (commercial and Medicaid), while 65% are Medicare Advantage, aligning with Wellmark's MA growth strategy. The Livongo digital diabetes program directly addresses these gaps through connected glucose monitoring, unlimited test strips removing cost barriers, 24/7 coaching access serving rural populations, and AI-driven insights for medication adherence. Projected ROI is $3.2M annually based on: ED visit reduction savings ($1.8M), hospitalization reduction ($1.0M), and complication prevention ($0.4M), against program cost of $35 PMPM for enrolled members.",
      "data_quality_notes": "High quality data: 95% of members have HbA1c lab results in last 6 months due to HEDIS measure focus. ED visit and hospitalization data complete from medical claims. Medication adherence calculated using standard PDC methodology from pharmacy claims. Risk stratification uses Johns Hopkins ACG system. Some rural members may have lab results from non-network providers not captured in claims (estimated <5% data gap)."
    },
    {
      "priority_id": "vp_2",
      "baseline_metrics": [
        {
          "metric_name": "Average Systolic Blood Pressure",
          "value": 142.3,
          "unit": "mmHg",
          "measurement_period": "2024 Q1-Q4",
          "sample_size": 18765
        },
        {
          "metric_name": "BP Control Rate (<140/90)",
          "value": 47.2,
          "unit": "% of hypertensive members",
          "measurement_period": "2024 Q1-Q4",
          "sample_size": 18765
        },
        {
          "metric_name": "Cardiovascular events (MI, stroke) per 1000",
          "value": 12.5,
          "unit": "events per 1000",
          "measurement_period": "2024 Q1-Q4",
          "sample_size": 18765
        }
      ],
      "projected_impacts": [
        {
          "metric_name": "BP Control Rate (<140/90)",
          "baseline_value": 47.2,
          "projected_value": 65.0,
          "improvement_percentage": 37.7,
          "unit": "% of hypertensive members",
          "confidence_level": "high",
          "assumptions": [
            "Based on Livongo HTN published outcomes: 20% absolute improvement in control rates",
            "60% program enrollment among uncontrolled hypertensive members",
            "Connected BP monitors improve self-monitoring and engagement",
            "12-18 month intervention period"
          ]
        },
        {
          "metric_name": "Cardiovascular events (MI, stroke) per 1000",
          "baseline_value": 12.5,
          "projected_value": 10.6,
          "improvement_percentage": 15.2,
          "unit": "events per 1000",
          "confidence_level": "medium",
          "assumptions": [
            "AHA evidence: BP control reduces CV events by 25%",
            "Conservative estimate accounting for time lag and partial enrollment",
            "Requires 24+ months to see full cardiovascular impact",
            "Assumes continued statin therapy and other CV risk management"
          ]
        }
      ],
      "supporting_analysis": "Wellmark has 18,765 members with hypertension diagnosis, representing significant cardiovascular risk. BP control rate of 47.2% is well below HEDIS quality benchmarks (60%+) and national averages (54%). The connected BP monitoring approach addresses key barriers including lack of home monitoring (only 35% of members own BP devices), medication non-adherence (PDC 58% for antihypertensives), and limited provider touchpoints in rural areas. Cardiovascular event rate of 12.5 per 1000 is 18% above regional benchmark, translating to 235 potentially preventable events annually. Hypertension overlaps significantly with diabetes population (65% comorbidity), creating synergistic opportunity with diabetes program. ROI driven by CV event prevention: average cost per MI is $45K, average cost per stroke is $38K, projected savings of $850K annually.",
      "data_quality_notes": "Medium quality: BP measurements available from medical claims but may be incomplete (estimated 70% capture rate). Some members monitored in retail clinics or home settings not captured. CV event data high quality from medical claims with ICD-10 validation."
    }
  ],
  "executive_summary": "Comprehensive analysis of Wellmark's 12,543 diabetic members and 18,765 hypertensive members reveals substantial opportunity for clinical improvement and cost savings through the Livongo digital chronic disease management platform. The diabetic population shows average HbA1c of 8.2% (well above goal), 28.5% with severely uncontrolled diabetes, and ED visit rates 21% above national benchmarks. Hypertension control rates at 47.2% trail quality benchmarks by 13+ percentage points. Geographic analysis highlights rural Iowa as highest-need population, where digital health can overcome access barriers. The Livongo program directly addresses identified gaps through connected devices removing cost barriers, 24/7 coaching serving rural populations, and AI-driven personalized interventions. Conservative projections show: (1) HbA1c reduction of 0.8 points, (2) 15% reduction in diabetes-related ED visits, (3) 37% improvement in hypertension control rates, and (4) 15% reduction in cardiovascular events. Total projected annual savings of $4.05M against program costs of $1.8M (assuming 70% enrollment), yielding net savings of $2.25M and ROI of 2.25:1. High data quality and alignment with Wellmark's strategic priorities (value-based care, Medicare Advantage growth, chronic disease excellence) support strong business case. Implementation timeline: 6-month ramp-up, 12-18 months to realize full clinical impact, 24 months for maximum cardiovascular benefit. Key success factors include executive sponsorship, provider engagement, member communication campaign, and integration with existing care management programs."
}
```

---

### B.6 Dashboard Widget Data Example (Step 5 Output)

**File:** `tests/fixtures/analytics/wellmark_diabetes_dashboard_data.json`

```json
{
  "prospect_id": "550e8400-e29b-41d4-a716-446655440000",
  "template_id": "tmpl_diabetes_exec_001",
  "generated_at": "2025-01-15T15:00:00Z",
  "widgets_data": [
    {
      "widget_id": "w_hba1c_trend",
      "data_points": [
        {
          "timestamp": "2024-01-01T00:00:00Z",
          "label": "Jan 2024",
          "value": 8.3,
          "formatted_value": "8.3%",
          "metadata": {"sample_size": 12412, "stddev": 1.8}
        },
        {
          "timestamp": "2024-02-01T00:00:00Z",
          "label": "Feb 2024",
          "value": 8.25,
          "formatted_value": "8.25%",
          "metadata": {"sample_size": 12456, "stddev": 1.75}
        },
        {
          "timestamp": "2024-03-01T00:00:00Z",
          "label": "Mar 2024",
          "value": 8.28,
          "formatted_value": "8.28%",
          "metadata": {"sample_size": 12489, "stddev": 1.82}
        },
        {
          "timestamp": "2024-04-01T00:00:00Z",
          "label": "Apr 2024",
          "value": 8.22,
          "formatted_value": "8.22%",
          "metadata": {"sample_size": 12501, "stddev": 1.76}
        },
        {
          "timestamp": "2024-05-01T00:00:00Z",
          "label": "May 2024",
          "value": 8.19,
          "formatted_value": "8.19%",
          "metadata": {"sample_size": 12534, "stddev": 1.73}
        },
        {
          "timestamp": "2024-06-01T00:00:00Z",
          "label": "Jun 2024",
          "value": 8.21,
          "formatted_value": "8.21%",
          "metadata": {"sample_size": 12556, "stddev": 1.78}
        },
        {
          "timestamp": "2024-07-01T00:00:00Z",
          "label": "Jul 2024",
          "value": 8.17,
          "formatted_value": "8.17%",
          "metadata": {"sample_size": 12578, "stddev": 1.71}
        },
        {
          "timestamp": "2024-08-01T00:00:00Z",
          "label": "Aug 2024",
          "value": 8.15,
          "formatted_value": "8.15%",
          "metadata": {"sample_size": 12598, "stddev": 1.69}
        },
        {
          "timestamp": "2024-09-01T00:00:00Z",
          "label": "Sep 2024",
          "value": 8.18,
          "formatted_value": "8.18%",
          "metadata": {"sample_size": 12612, "stddev": 1.74}
        },
        {
          "timestamp": "2024-10-01T00:00:00Z",
          "label": "Oct 2024",
          "value": 8.16,
          "formatted_value": "8.16%",
          "metadata": {"sample_size": 12629, "stddev": 1.72}
        },
        {
          "timestamp": "2024-11-01T00:00:00Z",
          "label": "Nov 2024",
          "value": 8.14,
          "formatted_value": "8.14%",
          "metadata": {"sample_size": 12641, "stddev": 1.7}
        },
        {
          "timestamp": "2024-12-01T00:00:00Z",
          "label": "Dec 2024",
          "value": 8.2,
          "formatted_value": "8.2%",
          "metadata": {"sample_size": 12543, "stddev": 1.75}
        }
      ],
      "generated_at": "2025-01-15T15:00:00Z",
      "query_used": "SELECT toStartOfMonth(lab_date) as month, avg(hba1c_value) as avg_hba1c, count(distinct member_id) as sample_size, stddevPop(hba1c_value) as stddev FROM clinical_labs WHERE lab_type = 'HbA1c' AND lab_date >= '2024-01-01' AND member_id IN (SELECT member_id FROM member_demographics WHERE has_diabetes = 1) GROUP BY month ORDER BY month",
      "cache_ttl": 604800
    },
    {
      "widget_id": "w_cost_savings",
      "data_points": [
        {
          "label": "Projected Annual Savings",
          "value": 4050000,
          "formatted_value": "$4.05M",
          "metadata": {
            "confidence_interval_low": 3200000,
            "confidence_interval_high": 4900000,
            "components": {
              "ed_visit_reduction": 1800000,
              "hospitalization_reduction": 1000000,
              "complication_prevention": 400000,
              "medication_adherence_improvement": 850000
            },
            "calculation_basis": "Conservative ROI assumptions with 70% enrollment"
          }
        }
      ],
      "generated_at": "2025-01-15T15:00:00Z",
      "query_used": null,
      "cache_ttl": 2592000
    },
    {
      "widget_id": "w_ed_visits_rate",
      "data_points": [
        {
          "label": "2023 Q1",
          "value": 152.3,
          "formatted_value": "152.3",
          "metadata": {"total_visits": 478, "diabetic_population": 3138}
        },
        {
          "label": "2023 Q2",
          "value": 148.7,
          "formatted_value": "148.7",
          "metadata": {"total_visits": 471, "diabetic_population": 3168}
        },
        {
          "label": "2023 Q3",
          "value": 151.2,
          "formatted_value": "151.2",
          "metadata": {"total_visits": 483, "diabetic_population": 3195}
        },
        {
          "label": "2023 Q4",
          "value": 149.5,
          "formatted_value": "149.5",
          "metadata": {"total_visits": 481, "diabetic_population": 3217}
        },
        {
          "label": "2024 Q1",
          "value": 147.8,
          "formatted_value": "147.8",
          "metadata": {"total_visits": 465, "diabetic_population": 3146}
        },
        {
          "label": "2024 Q2",
          "value": 145.6,
          "formatted_value": "145.6",
          "metadata": {"total_visits": 458, "diabetic_population": 3146}
        },
        {
          "label": "2024 Q3",
          "value": 144.1,
          "formatted_value": "144.1",
          "metadata": {"total_visits": 454, "diabetic_population": 3150}
        },
        {
          "label": "2024 Q4",
          "value": 145.2,
          "formatted_value": "145.2",
          "metadata": {"total_visits": 456, "diabetic_population": 3141}
        }
      ],
      "generated_at": "2025-01-15T15:00:00Z",
      "query_used": "SELECT concat('Q', toString(quarter(visit_date)), ' ', toString(year(visit_date))) as quarter, (count(*) / countDistinct(member_id)) * 1000 as ed_visit_rate FROM ed_visits WHERE diabetes_related = 1 AND visit_date >= '2023-01-01' GROUP BY year(visit_date), quarter(visit_date) ORDER BY year(visit_date), quarter(visit_date)",
      "cache_ttl": 604800
    },
    {
      "widget_id": "w_medication_adherence",
      "data_points": [
        {
          "label": "Members with PDC >= 80%",
          "value": 62.3,
          "formatted_value": "62.3%",
          "metadata": {
            "numerator": 7814,
            "denominator": 12543,
            "target": 80.0,
            "vs_target": -17.7,
            "trend_6mo": "+2.1%"
          }
        }
      ],
      "generated_at": "2025-01-15T15:00:00Z",
      "query_used": "SELECT (countIf(pdc >= 0.8) / count(*)) * 100 as adherence_pct FROM (SELECT member_id, sum(days_supply) / 365.0 as pdc FROM pharmacy_claims WHERE drug_class IN ('Insulin', 'Metformin', 'GLP-1', 'SGLT2', 'DPP-4', 'Sulfonylureas') AND fill_date >= '2024-01-01' GROUP BY member_id HAVING pdc <= 3.0)",
      "cache_ttl": 2592000
    },
    {
      "widget_id": "w_population_stratification",
      "data_points": [
        {
          "label": "Low Risk",
          "value": 3256,
          "formatted_value": "3,256 (26.0%)",
          "metadata": {"percentage": 26.0, "criteria": "HbA1c <7.5%, no complications"}
        },
        {
          "label": "Medium Risk",
          "value": 4518,
          "formatted_value": "4,518 (36.0%)",
          "metadata": {"percentage": 36.0, "criteria": "HbA1c 7.5-8.9%, 0-1 complications"}
        },
        {
          "label": "High Risk",
          "value": 3134,
          "formatted_value": "3,134 (25.0%)",
          "metadata": {"percentage": 25.0, "criteria": "HbA1c 9.0-10.0% or 2+ complications"}
        },
        {
          "label": "Very High Risk",
          "value": 1635,
          "formatted_value": "1,635 (13.0%)",
          "metadata": {"percentage": 13.0, "criteria": "HbA1c >10% or 3+ complications or recent hospitalization"}
        }
      ],
      "generated_at": "2025-01-15T15:00:00Z",
      "query_used": "SELECT risk_level, count(*) as member_count FROM member_risk_stratification WHERE condition = 'diabetes' AND stratification_date >= '2024-12-01' GROUP BY risk_level ORDER BY risk_level",
      "cache_ttl": 2592000
    },
    {
      "widget_id": "w_complication_rates",
      "data_points": [
        {
          "label": "Diabetic Retinopathy",
          "value": 18.2,
          "formatted_value": "18.2%",
          "metadata": {
            "member_count": 2283,
            "benchmark": 15.5,
            "vs_benchmark": "+2.7",
            "trend_12mo": "stable"
          }
        },
        {
          "label": "Diabetic Neuropathy",
          "value": 22.5,
          "formatted_value": "22.5%",
          "metadata": {
            "member_count": 2822,
            "benchmark": 19.8,
            "vs_benchmark": "+2.7",
            "trend_12mo": "increasing"
          }
        },
        {
          "label": "Diabetic Nephropathy/CKD",
          "value": 15.8,
          "formatted_value": "15.8%",
          "metadata": {
            "member_count": 1982,
            "benchmark": 14.2,
            "vs_benchmark": "+1.6",
            "trend_12mo": "increasing"
          }
        },
        {
          "label": "Cardiovascular Disease",
          "value": 28.3,
          "formatted_value": "28.3%",
          "metadata": {
            "member_count": 3550,
            "benchmark": 25.1,
            "vs_benchmark": "+3.2",
            "trend_12mo": "stable"
          }
        },
        {
          "label": "Peripheral Vascular Disease",
          "value": 12.4,
          "formatted_value": "12.4%",
          "metadata": {
            "member_count": 1555,
            "benchmark": 11.0,
            "vs_benchmark": "+1.4",
            "trend_12mo": "stable"
          }
        }
      ],
      "generated_at": "2025-01-15T15:00:00Z",
      "query_used": "SELECT complication_type, (count(distinct member_id) / (SELECT countDistinct(member_id) FROM member_demographics WHERE has_diabetes = 1)) * 100 as prevalence_rate, count(distinct member_id) as member_count FROM diabetes_complications GROUP BY complication_type ORDER BY prevalence_rate DESC",
      "cache_ttl": 2592000
    }
  ]
}
```

---

### B.7 Reference Test Fixtures Directory Structure

Recommended directory structure for test fixtures:

```
tests/
├── fixtures/
│   ├── value_propositions/
│   │   ├── livongo_value_proposition_derived.json
│   │   ├── livongo_value_proposition_research_mode.json
│   │   ├── wellpoint_diabetes_vp.json
│   │   └── schema_validation_tests.json
│   ├── company_information/
│   │   ├── wellmark_company_research.json
│   │   ├── anthem_company_research.json
│   │   ├── cigna_company_research.json
│   │   └── schema_validation_tests.json
│   ├── dashboard_templates/
│   │   ├── diabetes_executive_dashboard.json
│   │   ├── hypertension_clinical_dashboard.json
│   │   ├── behavioral_health_dashboard.json
│   │   └── multi_condition_dashboard.json
│   ├── analytics/
│   │   ├── wellmark_livongo_value_prop_data.json
│   │   ├── wellmark_diabetes_dashboard_data.json
│   │   ├── anthem_analytics_example.json
│   │   └── clickhouse_query_examples.sql
│   └── jobs/
│       ├── job_processing_example.json
│       ├── job_failed_example.json
│       └── job_completed_example.json
```

---

**End of Appendix B**

---

## Document Complete

**Total Sections:** 8 + 2 Appendices

**Last Updated:** October 31, 2025

**Document Version:** 1.0

**Contact:** [Engineering Team Lead]

---
