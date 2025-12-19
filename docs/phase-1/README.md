# Phase 1: Foundation & Infrastructure

**Status:** 🟡 In Progress
**Duration:** 2-3 weeks
**Team:** Backend Engineer 1, DevOps Engineer, QA Engineer
**Dependencies:** None (foundational phase)

---

## Table of Contents

1. [Phase Overview](#phase-overview)
2. [Objectives](#objectives)
3. [Sub-Phases](#sub-phases)
4. [Workflow Diagram](#workflow-diagram)
5. [Success Criteria](#success-criteria)
6. [Deliverables](#deliverables)
7. [Technical Stack](#technical-stack)
8. [Prerequisites](#prerequisites)
9. [Getting Started](#getting-started)
10. [Reference Documentation](#reference-documentation)

---

## Phase Overview

Phase 1 establishes the foundational infrastructure required for the entire Triton platform. This phase focuses on setting up core services, database schemas, messaging infrastructure, and the API framework that all subsequent phases will build upon.

**Why This Phase is Critical:**
- Provides the runtime environment for all applications
- Establishes data persistence layer (PostgreSQL + Clickhouse)
- Implements real-time communication (Redis Pub/Sub + SSE)
- Creates API structure that agents and analytics will use
- Sets up containerization for consistent deployments

**Key Principle:** Get the foundation solid before building features. Any shortcuts here will cause technical debt in later phases.

---

## Objectives

### Primary Objectives

1. **Containerized Infrastructure**
   - All services running in Docker containers
   - Docker Compose orchestration configured
   - Development and production profiles
   - Health checks for all services

2. **Data Persistence**
   - PostgreSQL for structured data (clients, templates, ROI models)
   - Clickhouse for analytics data (claims, utilization)
   - Redis for caching and message broker
   - Database migrations framework (Alembic)

3. **Real-Time Communication**
   - Redis Pub/Sub message broker
   - Server-Sent Events (SSE) endpoints
   - Job status tracking
   - 99% reduction in HTTP polling

4. **API Framework**
   - FastAPI application structure
   - Route organization by domain
   - Global exception handling
   - Health monitoring endpoints
   - API documentation (Swagger/ReDoc)

### Secondary Objectives

- Logging framework (structured logging)
- Environment configuration management
- Basic security (CORS, API keys placeholder)
- Development vs production settings
- Docker volume management for data persistence

---

## Sub-Phases

| Sub-Phase | Name | Duration | Owner | Status | Dependencies |
|-----------|------|----------|-------|--------|--------------|
| **1.1** | Infrastructure Setup | 3 days | DevOps | 🟡 In Progress | None |
| **1.2** | Database Schema Design | 2 days | Backend 1 | 🔴 Not Started | 1.1 |
| **1.3** | Message Broker Implementation | 2 days | Backend 1 | 🔴 Not Started | 1.1, 1.2 |
| **1.4** | API Foundation | 3 days | Backend 1 | 🔴 Not Started | 1.1, 1.2, 1.3 |

### Sub-Phase Details

#### 1.1: Infrastructure Setup
**File:** [1.1-infrastructure-setup.md](./1.1-infrastructure-setup.md)

Sets up Docker containers for all infrastructure services:
- PostgreSQL (structured data)
- Clickhouse (analytics data)
- Redis (cache + message broker)
- S3 (or LocalStack for development)

**Key Tasks:**
- Write Docker Compose configuration
- Configure service networking
- Set up health checks
- Create development scripts

**Acceptance Criteria:**
- ✅ `docker-compose up` starts all services
- ✅ All services pass health checks
- ✅ Services can communicate with each other
- ✅ Data persists after container restart

---

#### 1.2: Database Schema Design
**File:** [1.2-database-schema.md](./1.2-database-schema.md)

Designs and implements core database schemas for PostgreSQL and Clickhouse:
- PostgreSQL: Clients, value propositions, templates, prospects, ROI models
- Clickhouse: Claims data, utilization events, cost analysis
- Migration framework setup (Alembic)

**Key Tasks:**
- Design PostgreSQL schema (10-12 tables)
- Design Clickhouse schema (4-5 tables)
- Create initial migrations
- Implement database connection pooling

**Acceptance Criteria:**
- ✅ All tables created with proper indexes
- ✅ Foreign key relationships defined
- ✅ Migrations run successfully
- ✅ Connection pooling configured (max 20 connections)

---

#### 1.3: Message Broker Implementation
**File:** [1.3-message-broker-implementation.md](./1.3-message-broker-implementation.md)

Implements Redis Pub/Sub for real-time job status updates:
- Redis publisher (publishes job events)
- Redis subscriber (listens for events)
- SSE endpoint (streams events to frontend)
- Job status tracking

**Key Tasks:**
- Implement Redis pub/sub wrapper
- Create SSE streaming endpoint
- Build job status manager
- Add event types (started, progress, completed, failed)

**Acceptance Criteria:**
- ✅ Events published to Redis channels
- ✅ SSE endpoint streams events in real-time
- ✅ Frontend receives updates without polling
- ✅ 99% reduction in HTTP requests vs polling

---

#### 1.4: API Foundation
**File:** [1.4-api-foundation.md](./1.4-api-foundation.md)

Creates FastAPI application structure with routing, exception handling, and documentation:
- FastAPI app initialization
- Route organization (by domain)
- Global exception handlers
- Health and monitoring endpoints

**Key Tasks:**
- Create FastAPI application
- Set up router structure
- Implement exception handling
- Add health check endpoints
- Configure CORS
- Generate API documentation

**Acceptance Criteria:**
- ✅ API starts and serves requests
- ✅ Health endpoint returns 200 OK
- ✅ Swagger UI accessible at /docs
- ✅ Global exception handling catches errors
- ✅ CORS configured for development

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1 WORKFLOW                         │
└─────────────────────────────────────────────────────────────┘

Sub-Phase 1.1: Infrastructure Setup (Days 1-3)
┌──────────────────────────────────────────────────────────┐
│ Start                                                    │
│   ↓                                                      │
│ [Create Docker Compose]                                 │
│   ├─ PostgreSQL container (port 5432)                   │
│   ├─ Clickhouse container (port 9000)                   │
│   ├─ Redis container (port 6379)                        │
│   └─ LocalStack/S3 (port 4566)                         │
│   ↓                                                      │
│ [Configure Networking]                                   │
│   ├─ Create triton-network                             │
│   ├─ Assign IPs to services                            │
│   └─ Set up service discovery                          │
│   ↓                                                      │
│ [Add Health Checks]                                      │
│   ├─ PostgreSQL: pg_isready                            │
│   ├─ Clickhouse: HTTP /ping                            │
│   └─ Redis: redis-cli PING                             │
│   ↓                                                      │
│ [Test & Validate]                                        │
│   └─ docker-compose up → All healthy ✅                │
└──────────────────────────────────────────────────────────┘
                      ↓
Sub-Phase 1.2: Database Schema Design (Days 4-5)
┌──────────────────────────────────────────────────────────┐
│ [Design PostgreSQL Schema]                               │
│   ├─ clients table                                      │
│   ├─ value_propositions table                           │
│   ├─ dashboard_templates table                          │
│   ├─ prospects table                                    │
│   ├─ prospect_dashboard_data table (JSONB)              │
│   ├─ roi_models table                                   │
│   ├─ generation_jobs table                              │
│   └─ extraction_lineage table                           │
│   ↓                                                      │
│ [Design Clickhouse Schema]                               │
│   ├─ claims table (partitioned by month)                │
│   ├─ utilization_events table                           │
│   └─ cost_analysis table                                │
│   ↓                                                      │
│ [Create Migrations]                                      │
│   ├─ alembic init                                       │
│   ├─ 001_initial_schema.py                             │
│   └─ Run migrations ✅                                  │
└──────────────────────────────────────────────────────────┘
                      ↓
Sub-Phase 1.3: Message Broker Implementation (Days 6-7)
┌──────────────────────────────────────────────────────────┐
│ [Implement Publisher]                                    │
│   ├─ RedisPublisher class                              │
│   ├─ publish_job_event() method                        │
│   └─ Event types: started, progress, completed, failed │
│   ↓                                                      │
│ [Implement Subscriber]                                   │
│   ├─ RedisSubscriber class                             │
│   ├─ subscribe_to_channel() method                     │
│   └─ Event queue management                            │
│   ↓                                                      │
│ [Create SSE Endpoint]                                    │
│   ├─ GET /jobs/{job_id}/subscribe                      │
│   ├─ Stream events via Server-Sent Events              │
│   └─ Auto-reconnect logic                              │
│   ↓                                                      │
│ [Test Real-Time Updates]                                 │
│   └─ Frontend receives updates (no polling) ✅          │
└──────────────────────────────────────────────────────────┘
                      ↓
Sub-Phase 1.4: API Foundation (Days 8-10)
┌──────────────────────────────────────────────────────────┐
│ [Create FastAPI App]                                     │
│   ├─ app.py (main application)                          │
│   ├─ api/ (routes folder)                               │
│   └─ core/ (config, models, utils)                      │
│   ↓                                                      │
│ [Set Up Routers]                                         │
│   ├─ api/routes/templates.py                            │
│   ├─ api/routes/results.py                              │
│   ├─ api/routes/research.py (placeholder)               │
│   └─ api/routes/roi_models.py (placeholder)             │
│   ↓                                                      │
│ [Add Exception Handling]                                 │
│   ├─ Global exception handler                           │
│   ├─ ValidationError handler                            │
│   └─ Custom TritonException class                       │
│   ↓                                                      │
│ [Add Health Endpoints]                                   │
│   ├─ GET / → {"status": "ok"}                           │
│   ├─ GET /health → Health check with service status     │
│   └─ GET /docs → Swagger UI                             │
│   ↓                                                      │
│ [Configure & Test]                                       │
│   ├─ CORS configuration                                 │
│   ├─ Environment variables                              │
│   └─ Integration tests ✅                               │
└──────────────────────────────────────────────────────────┘
                      ↓
                   Phase 1 Complete ✅

Output:
├─ Docker environment running
├─ Database schemas deployed
├─ Message broker operational
├─ API serving requests
└─ Ready for Phase 2 (Research Agents)
```

---

## Success Criteria

### Must-Have (Blocking for Phase 2)

✅ **Infrastructure:**
- All Docker containers start with `docker-compose up`
- Services pass health checks within 30 seconds
- Services restart automatically on failure
- Data persists after container restart

✅ **Database:**
- PostgreSQL schema with 10+ tables deployed
- Clickhouse schema with analytics tables deployed
- Database migrations run successfully
- Connection pooling configured (20 connections max)

✅ **Message Broker:**
- Redis Pub/Sub publishing events
- SSE endpoint streaming real-time updates
- Frontend receives updates without polling
- Event delivery latency < 100ms

✅ **API:**
- FastAPI application starts on port 8000
- Health endpoint returns 200 OK with service status
- Swagger UI accessible at http://localhost:8000/docs
- Global exception handling catches all errors
- CORS configured for development

### Nice-to-Have (Can defer to Phase 6)

- Prometheus metrics endpoint
- Rate limiting on API endpoints
- API key authentication
- Grafana dashboard
- Automated backup scripts

---

## Deliverables

### Configuration Files

| File | Purpose | Owner |
|------|---------|-------|
| `docker-compose.yml` | Service orchestration | DevOps |
| `.env.example` | Environment template | DevOps |
| `alembic.ini` | Database migrations config | Backend 1 |
| `requirements.txt` | Python dependencies | Backend 1 |

### Code Modules

| Module | Purpose | Owner |
|--------|---------|-------|
| `core/config/settings.py` | Configuration management | Backend 1 |
| `core/database/connection.py` | Database connection pooling | Backend 1 |
| `core/messaging/redis_client.py` | Redis pub/sub wrapper | Backend 1 |
| `core/messaging/sse.py` | Server-Sent Events implementation | Backend 1 |
| `app.py` | FastAPI application entry point | Backend 1 |
| `api/routes/` | API route handlers | Backend 1 |

### Database Migrations

| Migration | Purpose | Owner |
|-----------|---------|-------|
| `001_initial_schema.py` | Core PostgreSQL tables | Backend 1 |
| `002_clickhouse_schema.sql` | Analytics tables | Backend 1 |

### Documentation

| Document | Purpose | Owner |
|----------|---------|-------|
| `1.1-infrastructure-setup.md` | Infrastructure guide | DevOps |
| `1.2-database-schema.md` | Schema design doc | Backend 1 |
| `1.3-message-broker-implementation.md` | Messaging guide | Backend 1 |
| `1.4-api-foundation.md` | API structure doc | Backend 1 |

---

## Technical Stack

### Core Services

| Service | Version | Purpose | Port |
|---------|---------|---------|------|
| **PostgreSQL** | 14+ | Structured data storage | 5432 |
| **Clickhouse** | 23+ | Analytics data warehouse | 9000, 8123 |
| **Redis** | 7+ | Cache + message broker | 6379 |
| **LocalStack** | Latest | S3 emulation (dev) | 4566 |

### Application Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Application runtime |
| **FastAPI** | 0.100+ | Web framework |
| **SQLAlchemy** | 2.0+ | PostgreSQL ORM |
| **Alembic** | 1.12+ | Database migrations |
| **Redis-py** | 5.0+ | Redis client |
| **Clickhouse-driver** | 0.2+ | Clickhouse client |
| **Pydantic** | 2.0+ | Data validation |
| **Uvicorn** | 0.23+ | ASGI server |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **pytest** | Testing framework |
| **black** | Code formatting |
| **mypy** | Static type checking |

---

## Prerequisites

### System Requirements

- **OS**: Linux, macOS, or WSL2 (Windows)
- **RAM**: Minimum 8GB, recommended 16GB
- **Disk**: 20GB free space
- **CPU**: 4 cores recommended

### Software Requirements

```bash
# Required
docker --version          # 20.10+
docker-compose --version  # 2.0+
python --version          # 3.11+

# Optional (for local development)
psql --version            # PostgreSQL client
redis-cli --version       # Redis client
clickhouse-client --version # Clickhouse client
```

### Access Requirements

- **AWS Account**: For S3 and Bedrock (Phase 2+)
- **GitHub Access**: To clone repository
- **Network**: Ports 5432, 6379, 8000, 9000 available

---

## Getting Started

### Quick Start (5 minutes)

```bash
# 1. Clone repository (if not already)
git clone <repository-url>
cd triton-agentic

# 2. Copy environment template
cp .env.example .env

# 3. Start infrastructure
docker-compose up -d

# 4. Verify services are healthy
docker-compose ps

# 5. Check logs
docker-compose logs -f
```

### Detailed Setup

For step-by-step instructions, see:
- [1.1 Infrastructure Setup](./1.1-infrastructure-setup.md)
- [1.2 Database Schema](./1.2-database-schema.md)
- [1.3 Message Broker](./1.3-message-broker-implementation.md)
- [1.4 API Foundation](./1.4-api-foundation.md)

---

## Reference Documentation

### Phase 1 Sub-Phase Files

- [1.1 Infrastructure Setup](./1.1-infrastructure-setup.md) - JIRA-style ticket
- [1.2 Database Schema Design](./1.2-database-schema.md) - JIRA-style ticket
- [1.3 Message Broker Implementation](./1.3-message-broker-implementation.md) - JIRA-style ticket
- [1.4 API Foundation](./1.4-api-foundation.md) - JIRA-style ticket

### Existing Reference Docs (Moved to Phase 1)

- [DOCKER_SETUP.md](./DOCKER_SETUP.md) - Detailed Docker deployment guide
- [FOUNDATION_AND_INFRASTRUCTURE.md](./FOUNDATION_AND_INFRASTRUCTURE.md) - Infrastructure overview
- [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) - Message broker detailed design
- [MESSAGE_BROKER_TESTING.md](./MESSAGE_BROKER_TESTING.md) - Testing procedures

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Clickhouse Documentation](https://clickhouse.com/docs/)
- [Redis Pub/Sub Guide](https://redis.io/docs/manual/pubsub/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

## Next Phase

Once Phase 1 is complete (all acceptance criteria met), proceed to:

**[Phase 2: Research Agents](../phase-2/README.md)**
- Build WebSearchAgent for autonomous web intelligence
- Build DocumentAnalysisAgent for PDF/DOCX extraction
- Create research API layer with job management
- Implement 4-layer agent validation pipeline

---

## Support & Questions

- **Slack Channel**: #triton-phase-1
- **Project Manager**: [Name]
- **Tech Lead**: [Name]
- **DevOps Lead**: [Name]

---

**Last Updated:** 2025-12-17
**Next Review:** Weekly during Phase 1 execution
