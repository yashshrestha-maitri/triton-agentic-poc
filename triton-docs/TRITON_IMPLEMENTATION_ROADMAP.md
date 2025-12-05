# Triton Platform - Phased Implementation Roadmap

**Document Version:** 1.0
**Date:** December 2, 2025
**Status:** Planning Phase

---

## Executive Summary

This document provides a comprehensive phased implementation plan for the Triton AI-powered ROI analysis platform. The implementation is divided into three phases:

- **Phase 0.1**: Foundation & Core Infrastructure (Weeks 1-4)
- **Phase 0.2**: Client Value Proposition System (Weeks 5-8)
- **Phase 1.0**: Analytics Team & Dashboard Data Generation (Weeks 9-14)

**Total Estimated Duration:** 14 weeks
**Total Estimated Hours:** 1,240 hours

**Note:** Step 3 (ARGO data processing) and Step 6 (MARÉ presentation layer) are excluded as they are already built or outside the scope of Triton platform development.

---

## Phase Overview

| Phase | Focus Area | Duration | Total Hours | Key Deliverables |
|-------|-----------|----------|-------------|------------------|
| **0.1** | Infrastructure & Foundation | 4 weeks | 400 hours | FastAPI, Celery, Database, Auth |
| **0.2** | Value Proposition System | 4 weeks | 480 hours | Research Team agents, Template generation |
| **1.0** | Analytics & Dashboard Data | 6 weeks | 360 hours | Analytics Team agents, Data generation |

---

## Phase 0.1: Foundation & Core Infrastructure

**Duration:** 4 weeks (Weeks 1-4)
**Total Estimated Hours:** 400 hours

### Objectives

Establish the foundational infrastructure for the Triton platform, including:
- FastAPI REST API with async job processing
- Celery + Redis task queue with abstraction layer
- PostgreSQL and Clickhouse database setup
- Authentication and authorization framework
- Base agent framework and monitoring infrastructure

### Acceptance Criteria

- [ ] FastAPI application running with health check endpoints
- [ ] Celery workers processing async jobs successfully
- [ ] PostgreSQL database with core schema deployed
- [ ] Clickhouse database connected and accessible
- [ ] JWT-based authentication working for all endpoints
- [ ] Base agent framework with Agno integration functional
- [ ] Monitoring stack (Prometheus, Grafana) deployed
- [ ] All unit tests passing with >80% code coverage
- [ ] API documentation auto-generated via OpenAPI/Swagger

---

### Epic 1.1: FastAPI Application Setup

**Priority:** Critical
**Estimated Hours:** 80 hours

#### User Stories

**Story 1.1.1: As a developer, I need a FastAPI application skeleton so I can build REST endpoints**

**Acceptance Criteria:**
- FastAPI application with project structure created
- Health check endpoint (`GET /health`) returns 200 OK
- Root endpoint (`GET /`) returns API metadata
- CORS middleware configured for development
- Pydantic request/response models structure in place
- Environment-based configuration loading (dev/staging/prod)

**Tasks:**
- [ ] Create FastAPI application structure (`app/main.py`) - 4h
- [ ] Set up project directory structure (routers, models, services) - 4h
- [ ] Implement health check and root endpoints - 3h
- [ ] Configure CORS middleware - 2h
- [ ] Create base Pydantic models for API responses - 5h
- [ ] Set up environment configuration with Pydantic Settings - 4h
- [ ] Write unit tests for endpoints - 4h
- [ ] Document setup in `docs/API_SETUP.md` - 2h

**Story 1.1.2: As a developer, I need standardized error handling so API responses are consistent**

**Acceptance Criteria:**
- Global exception handlers for common errors (400, 401, 404, 500)
- Error response format matches spec (code, message, details, request_id)
- Request ID tracking across all requests
- Validation errors return 422 with field-level details
- Unhandled exceptions logged with full stack trace

**Tasks:**
- [ ] Create error response models (`api/models/errors.py`) - 3h
- [ ] Implement global exception handlers - 5h
- [ ] Add request ID middleware - 3h
- [ ] Configure logging with structured format - 4h
- [ ] Write unit tests for error handling - 4h
- [ ] Document error handling patterns - 2h

**Story 1.1.3: As an API consumer, I need authentication so only authorized users can access endpoints**

**Acceptance Criteria:**
- JWT token generation and validation working
- `/api/v1/auth/login` endpoint returns valid JWT
- Protected endpoints reject requests without valid token
- Token expiration enforced (default 24 hours)
- Token refresh mechanism implemented

**Tasks:**
- [ ] Implement JWT utilities (generate, validate, decode) - 6h
- [ ] Create authentication middleware - 5h
- [ ] Implement login endpoint with mock user validation - 4h
- [ ] Add token refresh endpoint - 4h
- [ ] Create dependency for protected routes (`get_current_user`) - 3h
- [ ] Write authentication integration tests - 5h
- [ ] Document authentication flow - 2h

---

### Epic 1.2: Task Queue Infrastructure

**Priority:** Critical
**Estimated Hours:** 100 hours

#### User Stories

**Story 1.2.1: As a developer, I need a Celery worker setup so I can process async jobs**

**Acceptance Criteria:**
- Celery application configured with Redis broker
- Worker starts successfully and connects to Redis
- Simple test task executes and completes
- Task results stored in Redis backend
- Flower monitoring dashboard accessible

**Tasks:**
- [ ] Set up Redis via Docker Compose - 3h
- [ ] Create Celery application configuration (`core/celery_app.py`) - 5h
- [ ] Implement test task (`tasks/test_task.py`) - 2h
- [ ] Configure task routing and queues - 4h
- [ ] Set up Flower for monitoring - 3h
- [ ] Write Celery worker Dockerfile - 4h
- [ ] Document Celery setup - 3h

**Story 1.2.2: As a developer, I need task queue abstraction so we can migrate to Temporal in the future**

**Acceptance Criteria:**
- Abstract `TaskQueue` interface defined
- `CeleryTaskQueue` implementation working
- Task enqueueing returns task_id
- Task status retrieval working (pending, processing, completed, failed)
- Example showing how to swap implementations

**Tasks:**
- [ ] Design `TaskQueue` abstract base class - 5h
- [ ] Implement `CeleryTaskQueue` concrete class - 8h
- [ ] Implement task status retrieval - 5h
- [ ] Create factory pattern for queue selection - 4h
- [ ] Write unit tests with mocked queue - 6h
- [ ] Document abstraction pattern in ADR - 3h

**Story 1.2.3: As a developer, I need job tracking so I can report async job status to API consumers**

**Acceptance Criteria:**
- `generation_jobs` table created in PostgreSQL
- Job CRUD operations working via SQLAlchemy
- Job statuses: `pending`, `processing`, `completed`, `failed`
- Job progress tracking with percentage and stage
- Failed jobs store error details

**Tasks:**
- [ ] Design `generation_jobs` table schema - 4h
- [ ] Create SQLAlchemy model for jobs - 3h
- [ ] Implement job CRUD service (`services/job_service.py`) - 6h
- [ ] Create job status enum and validation - 2h
- [ ] Implement progress update mechanism - 4h
- [ ] Write integration tests with test database - 5h
- [ ] Document job tracking patterns - 2h

---

### Epic 1.3: Database Infrastructure

**Priority:** Critical
**Estimated Hours:** 80 hours

#### User Stories

**Story 1.3.1: As a developer, I need PostgreSQL database setup so I can store operational data**

**Acceptance Criteria:**
- PostgreSQL running via Docker Compose
- Database connection pooling configured
- Core schema migrations applied (clients, value_propositions, prospects, generation_jobs)
- SQLAlchemy ORM models created
- Database session management working

**Tasks:**
- [ ] Set up PostgreSQL Docker service - 3h
- [ ] Design core database schema (see Appendix C for tables) - 8h
- [ ] Create Alembic migration configuration - 4h
- [ ] Write initial migration with core tables - 6h
- [ ] Create SQLAlchemy models for core entities - 8h
- [ ] Implement database session factory - 4h
- [ ] Write database utility functions (get_db, transaction management) - 5h
- [ ] Document database architecture - 3h

**Story 1.3.2: As a developer, I need Clickhouse database setup so I can store analytics data**

**Acceptance Criteria:**
- Clickhouse running via Docker Compose
- Connection established from FastAPI application
- Basic table schema for prospect analytics data created
- Sample data insertion working
- Query execution tested

**Tasks:**
- [ ] Set up Clickhouse Docker service - 4h
- [ ] Design prospect analytics data schema - 6h
- [ ] Create Clickhouse table DDL scripts - 4h
- [ ] Implement Clickhouse client utility - 5h
- [ ] Write connection pooling for Clickhouse - 4h
- [ ] Create sample data insertion script - 3h
- [ ] Test query performance with sample data - 3h
- [ ] Document Clickhouse setup - 2h

**Story 1.3.3: As a developer, I need database migration tooling so schema changes are versioned**

**Acceptance Criteria:**
- Alembic configured for PostgreSQL migrations
- Migration generation command working
- Migration rollback tested
- Migration applied successfully in dev environment
- CI/CD pipeline runs migrations automatically

**Tasks:**
- [ ] Configure Alembic with environment settings - 3h
- [ ] Create migration generation script - 2h
- [ ] Test migration up/down operations - 4h
- [ ] Add migration check to CI/CD pipeline - 3h
- [ ] Document migration workflow - 2h

---

### Epic 1.4: Base Agent Framework

**Priority:** High
**Estimated Hours:** 60 hours

#### User Stories

**Story 1.4.1: As a developer, I need Agno framework integration so I can build multi-agent systems**

**Acceptance Criteria:**
- Agno installed and configured with AWS Bedrock
- Simple test agent executes successfully
- Agent invocation logging working
- Agent response parsing validated
- Retry mechanism for failed LLM calls implemented

**Tasks:**
- [ ] Install Agno and dependencies - 2h
- [ ] Configure AWS Bedrock model provider - 5h
- [ ] Create base agent template class - 6h
- [ ] Implement test agent with simple task - 4h
- [ ] Add LLM call retry logic - 5h
- [ ] Configure agent logging and metrics - 4h
- [ ] Write agent integration tests - 6h
- [ ] Document Agno setup - 3h

**Story 1.4.2: As a developer, I need Pydantic validation for agent outputs so responses are structured**

**Acceptance Criteria:**
- Base Pydantic schemas for agent outputs defined
- Validation errors trigger agent retry
- JSON extraction from markdown working
- Schema validation integrated into agent wrapper
- Max 3 retry attempts enforced

**Tasks:**
- [ ] Create base Pydantic models for agent outputs - 5h
- [ ] Implement JSON extraction utility - 4h
- [ ] Create validation wrapper for agents - 6h
- [ ] Implement retry logic with error feedback - 6h
- [ ] Write validation tests - 5h
- [ ] Document validation patterns - 2h

**Story 1.4.3: As a developer, I need agent execution monitoring so I can debug agent behavior**

**Acceptance Criteria:**
- AgentOS deployed for agent debugging
- Agent execution traces visible in AgentOS
- Agent response times logged
- Failed agent calls logged with error details
- Agent metrics exported to Prometheus

**Tasks:**
- [ ] Set up AgentOS via Docker - 4h
- [ ] Configure agent execution tracing - 4h
- [ ] Implement agent timing metrics - 3h
- [ ] Add Prometheus metrics exporter - 4h
- [ ] Create Grafana dashboard for agent metrics - 4h
- [ ] Document monitoring setup - 2h

---

### Epic 1.5: Monitoring & Observability

**Priority:** Medium
**Estimated Hours:** 40 hours

#### User Stories

**Story 1.5.1: As a DevOps engineer, I need Prometheus metrics so I can monitor system health**

**Acceptance Criteria:**
- Prometheus running via Docker Compose
- FastAPI metrics exported (request count, latency, errors)
- Celery metrics exported (task count, duration, failures)
- Custom business metrics exported (jobs created, completed, failed)
- Metrics accessible via `/metrics` endpoint

**Tasks:**
- [ ] Set up Prometheus Docker service - 3h
- [ ] Install prometheus-fastapi-instrumentator - 2h
- [ ] Configure FastAPI metrics - 4h
- [ ] Add Celery Prometheus exporter - 4h
- [ ] Implement custom business metrics - 5h
- [ ] Configure Prometheus scrape targets - 3h
- [ ] Document metrics collection - 2h

**Story 1.5.2: As a DevOps engineer, I need Grafana dashboards so I can visualize system metrics**

**Acceptance Criteria:**
- Grafana running via Docker Compose
- Prometheus data source configured
- Default dashboard showing API metrics
- Dashboard showing Celery worker metrics
- Dashboard showing agent execution metrics

**Tasks:**
- [ ] Set up Grafana Docker service - 2h
- [ ] Configure Prometheus data source - 2h
- [ ] Create API metrics dashboard - 4h
- [ ] Create Celery metrics dashboard - 4h
- [ ] Create agent metrics dashboard - 4h
- [ ] Export dashboards as JSON - 2h
- [ ] Document dashboard usage - 2h

**Story 1.5.3: As a developer, I need structured logging so I can debug production issues**

**Acceptance Criteria:**
- JSON-structured logs for all services
- Log levels configurable via environment
- Request ID included in all logs
- Agent execution logs include job_id and task_name
- Logs aggregated in centralized location (stdout for Docker)

**Tasks:**
- [ ] Configure structlog for JSON logging - 4h
- [ ] Add request ID to all API logs - 3h
- [ ] Add job_id context to Celery task logs - 3h
- [ ] Configure log levels per environment - 2h
- [ ] Document logging conventions - 2h

---

### Epic 1.6: Infrastructure as Code & Deployment

**Priority:** Medium
**Estimated Hours:** 40 hours

#### User Stories

**Story 1.6.1: As a developer, I need Docker Compose setup so I can run the full stack locally**

**Acceptance Criteria:**
- `docker-compose.yml` defines all services (API, Worker, Redis, Postgres, Clickhouse, Prometheus, Grafana)
- All services start successfully with `docker-compose up`
- Environment variables configured via `.env` file
- Health checks defined for all services
- Volume persistence for databases

**Tasks:**
- [ ] Create docker-compose.yml with all services - 6h
- [ ] Write Dockerfile for FastAPI application - 3h
- [ ] Write Dockerfile for Celery worker - 3h
- [ ] Configure service dependencies and health checks - 4h
- [ ] Create .env.example with all required variables - 2h
- [ ] Test full stack startup - 3h
- [ ] Document Docker setup in `docs/DOCKER_SETUP.md` - 3h

**Story 1.6.2: As a developer, I need CI/CD pipeline so code is automatically tested**

**Acceptance Criteria:**
- GitHub Actions workflow for PR validation
- Automated tests run on every push
- Code coverage report generated
- Docker images built and tagged
- Linting and type checking enforced

**Tasks:**
- [ ] Create GitHub Actions workflow file - 4h
- [ ] Configure pytest in CI - 3h
- [ ] Add code coverage reporting - 3h
- [ ] Add linting (ruff) and type checking (mypy) - 3h
- [ ] Configure Docker image build and push - 4h

---

## Phase 0.2: Client Value Proposition System

**Duration:** 4 weeks (Weeks 5-8)
**Total Estimated Hours:** 480 hours

### Objectives

Implement Step 1 and Step 2 of the Triton platform workflow:
- **Step 1.2**: Client value proposition derivation (Research Team agents)
- **Step 1.3**: Iterative review and refinement (Triton Refinement Agent)
- **Step 1.4**: Dashboard template generation (Template Generator Agent)
- **Step 2**: Prospect research and value prop ranking (Research & Alignment Agent)

### Acceptance Criteria

- [ ] Research Team generates value propositions from collateral documents
- [ ] Research Team generates value propositions from autonomous web research
- [ ] Value proposition refinement loop working with user feedback
- [ ] Dashboard template generation produces 5-10 valid templates
- [ ] Prospect research agent enriches prospect data
- [ ] Value proposition ranking for prospects working
- [ ] All agent outputs validated against Pydantic schemas
- [ ] End-to-end workflow tested with sample client

---

### Epic 2.1: Document Management & Storage

**Priority:** Critical
**Estimated Hours:** 60 hours

#### User Stories

**Story 2.1.1: As a user, I need to upload client documents so they can be analyzed**

**Acceptance Criteria:**
- Document upload endpoint accepts PDF files (max 50MB)
- Documents stored in S3-compatible storage
- Document metadata stored in PostgreSQL
- Document types validated (collateral, roi_sheet, whitepaper, case_study, product_overview, other)
- Uploaded documents accessible via download URL

**Tasks:**
- [ ] Design `client_documents` table schema - 4h
- [ ] Create SQLAlchemy model for documents - 3h
- [ ] Implement S3-compatible storage abstraction - 8h
- [ ] Create document upload endpoint (`POST /api/v1/clients/{id}/documents`) - 6h
- [ ] Implement file validation (size, type) - 4h
- [ ] Create document list endpoint (`GET /api/v1/clients/{id}/documents`) - 4h
- [ ] Implement presigned URL generation for downloads - 5h
- [ ] Write integration tests with MinIO - 6h
- [ ] Document upload API - 3h

**Story 2.1.2: As a developer, I need S3 storage abstraction so we can use different providers**

**Acceptance Criteria:**
- `ObjectStorage` abstract interface defined
- `S3Storage` implementation working with AWS S3
- `MinIOStorage` implementation working for local development
- Configuration switches between providers via environment
- Upload, download, and URL generation methods working

**Tasks:**
- [ ] Design ObjectStorage interface - 4h
- [ ] Implement S3Storage class - 6h
- [ ] Implement MinIOStorage class - 5h
- [ ] Create storage factory with config-based selection - 3h
- [ ] Write storage integration tests - 6h
- [ ] Document storage abstraction - 3h

---

### Epic 2.2: Research Team - Document Analysis

**Priority:** Critical
**Estimated Hours:** 80 hours

#### User Stories

**Story 2.2.1: As a Research Team, I need a DocumentAnalysisAgent so I can extract content from PDFs**

**Acceptance Criteria:**
- DocumentAnalysisAgent extracts text from PDF documents
- Agent returns structured extraction: company_info, product_features, clinical_outcomes, roi_metrics
- Multi-document analysis supported (batch processing)
- Extraction results stored temporarily for synthesis
- Agent retry logic handles parsing failures

**Tasks:**
- [ ] Design DocumentAnalysisAgent instructions - 6h
- [ ] Create Pydantic schema for extraction output - 4h
- [ ] Implement DocumentAnalysisAgent using Agno - 10h
- [ ] Integrate PDF text extraction (PyPDF2 or pdfplumber) - 5h
- [ ] Implement batch document processing - 6h
- [ ] Add validation and retry logic - 5h
- [ ] Write agent integration tests with sample PDFs - 8h
- [ ] Document agent behavior - 3h

**Story 2.2.2: As a Research Team, I need a WebSearchAgent so I can research clients autonomously**

**Acceptance Criteria:**
- WebSearchAgent searches Google/Bing for client information
- Agent accepts company name and optional industry hint
- Agent returns structured research: company_info, product_overview, competitive_position
- Search results filtered for relevance
- Rate limiting respected for search API

**Tasks:**
- [ ] Design WebSearchAgent instructions - 5h
- [ ] Create Pydantic schema for research output - 4h
- [ ] Implement WebSearchAgent using Agno - 8h
- [ ] Integrate search API (Serper.dev or Tavily) - 6h
- [ ] Implement relevance filtering - 4h
- [ ] Add rate limiting and error handling - 4h
- [ ] Write agent integration tests - 6h
- [ ] Document web search setup - 3h

---

### Epic 2.3: Research Team - Synthesis & Validation

**Priority:** Critical
**Estimated Hours:** 100 hours

#### User Stories

**Story 2.3.1: As a Research Team, I need a SynthesisAgent so I can create value propositions**

**Acceptance Criteria:**
- SynthesisAgent combines document extraction and/or web research into value proposition
- Agent uses Livongo JSON structure as template reference
- Output matches ValuePropositionJSON schema (see Appendix B)
- Additional context from user incorporated
- Output includes all required sections (executive_value_proposition, clinical_outcomes, roi_opportunities, etc.)

**Tasks:**
- [ ] Design SynthesisAgent instructions (based on Livongo template) - 8h
- [ ] Create ValuePropositionJSON Pydantic schema - 10h
- [ ] Implement SynthesisAgent using Agno - 12h
- [ ] Implement context aggregation (documents + research + user input) - 6h
- [ ] Add section-by-section generation logic - 8h
- [ ] Implement output validation - 5h
- [ ] Write agent integration tests - 8h
- [ ] Document synthesis process - 3h

**Story 2.3.2: As a Research Team, I need a ValidationAgent so outputs are validated before storage**

**Acceptance Criteria:**
- ValidationAgent validates ValuePropositionJSON against Pydantic schema
- Validation errors returned to SynthesisAgent for correction
- Max 3 retry attempts enforced
- Successful validation stores result in PostgreSQL
- Validation errors logged with details

**Tasks:**
- [ ] Design ValidationAgent instructions - 4h
- [ ] Implement ValidationAgent using Pydantic validation - 6h
- [ ] Create validation error feedback formatter - 5h
- [ ] Implement retry loop with error feedback - 6h
- [ ] Add validation metrics and logging - 4h
- [ ] Write validation tests with invalid outputs - 6h
- [ ] Document validation patterns - 3h

**Story 2.3.3: As a user, I need value proposition derivation API so I can trigger the Research Team**

**Acceptance Criteria:**
- `POST /api/v1/clients/{id}/value-proposition/derive` endpoint working
- Request supports mode: research (autonomous/manual) or collateral
- Async job created and job_id returned immediately
- Celery task orchestrates Research Team agents
- Job status endpoint returns progress updates

**Tasks:**
- [ ] Create value proposition derivation endpoint - 6h
- [ ] Implement request validation (mode, documents, prompts) - 5h
- [ ] Create Celery task for Research Team orchestration - 10h
- [ ] Implement progress tracking for multi-step process - 6h
- [ ] Create job status endpoint - 4h
- [ ] Write end-to-end integration test - 8h
- [ ] Document API usage with examples - 4h

---

### Epic 2.4: Value Proposition Review & Refinement

**Priority:** High
**Estimated Hours:** 80 hours

#### User Stories

**Story 2.4.1: As a user, I need review UI data so I can provide feedback on value proposition sections**

**Acceptance Criteria:**
- `GET /api/v1/clients/{id}/value-proposition/review` returns sectioned value prop
- Each section has feedback_status (pending, approved, rejected)
- Feedback history tracked per section
- Current feedback round displayed

**Tasks:**
- [ ] Create review response model with section breakdown - 6h
- [ ] Implement review endpoint - 5h
- [ ] Add section status tracking to database - 4h
- [ ] Implement feedback history retrieval - 4h
- [ ] Write API tests - 4h
- [ ] Document review API - 2h

**Story 2.4.2: As a user, I need to submit feedback so the AI can refine the value proposition**

**Acceptance Criteria:**
- `POST /api/v1/clients/{id}/value-proposition/review/feedback` accepts section-level feedback
- Feedback types: approve, reject_remove, reject_change
- General feedback supported
- Async job created for refinement
- Refinement agent applies changes and returns updated value prop

**Tasks:**
- [ ] Create feedback submission endpoint - 6h
- [ ] Design feedback request model - 4h
- [ ] Create Celery task for refinement - 8h
- [ ] Implement Triton Refinement Agent - 12h
- [ ] Add feedback application logic (remove/modify sections) - 8h
- [ ] Implement version tracking for value props - 5h
- [ ] Write refinement integration tests - 6h
- [ ] Document refinement workflow - 3h

**Story 2.4.3: As a user, I need to approve the final value proposition so it's ready for template generation**

**Acceptance Criteria:**
- `POST /api/v1/clients/{id}/value-proposition/approve` marks value prop as approved
- Approved value prop cannot be modified (versioned)
- Approval timestamp and user recorded
- Only approved value props can be used for template generation

**Tasks:**
- [ ] Create approval endpoint - 4h
- [ ] Implement approval validation (all sections reviewed) - 4h
- [ ] Add approval metadata to database - 3h
- [ ] Enforce approval requirement in template generation - 3h
- [ ] Write approval tests - 3h
- [ ] Document approval flow - 2h

---

### Epic 2.5: Dashboard Template Generation

**Priority:** Critical
**Estimated Hours:** 80 hours

#### User Stories

**Story 2.5.1: As a Template Generator, I need to create 5-10 dashboard variations**

**Acceptance Criteria:**
- Template Generator Agent creates 5-10 valid dashboard templates
- Templates vary by category (roi-focused, clinical-outcomes, utilization-analysis, etc.)
- Templates vary by target audience (Health Plan, Employer, Provider, ACO)
- Each template has 6-12 widgets with valid grid positions
- Widgets include data_requirements and analytics_questions

**Tasks:**
- [ ] Design Template Generator Agent instructions - 10h
- [ ] Create DashboardTemplate Pydantic schema (with data_requirements) - 8h
- [ ] Implement Template Generator Agent - 12h
- [ ] Implement template validation (widget count, grid positions, category coverage) - 8h
- [ ] Add retry logic for invalid templates - 5h
- [ ] Write template generation tests - 8h
- [ ] Document template structure - 4h

**Story 2.5.2: As a user, I need template generation API so I can create dashboard templates**

**Acceptance Criteria:**
- `POST /api/v1/clients/{id}/dashboard-templates/generate` endpoint working
- Request requires approved value_proposition_id
- Async job created for template generation
- Generated templates stored in PostgreSQL
- Template list endpoint returns all generated templates

**Tasks:**
- [ ] Create template generation endpoint - 5h
- [ ] Implement value prop approval check - 3h
- [ ] Create Celery task for template generation - 6h
- [ ] Implement template storage in database - 5h
- [ ] Create template list endpoint - 5h
- [ ] Create template detail endpoint - 4h
- [ ] Write end-to-end template generation test - 6h
- [ ] Document template generation API - 3h

**Story 2.5.3: As a user, I need template curation so I can select/remove templates**

**Acceptance Criteria:**
- Template status: generated, approved, removed
- User can approve individual templates
- User can remove templates from list
- Only approved templates used for prospect dashboard data generation

**Tasks:**
- [ ] Add template status field to database - 3h
- [ ] Create template approval endpoint - 4h
- [ ] Create template removal endpoint - 4h
- [ ] Enforce approval requirement in analytics generation - 3h
- [ ] Write curation API tests - 4h
- [ ] Document curation workflow - 2h

---

### Epic 2.6: Prospect Research & Value Prop Ranking

**Priority:** High
**Estimated Hours:** 80 hours

#### User Stories

**Story 2.6.1: As a Research Agent, I need to enrich prospect data from web research**

**Acceptance Criteria:**
- Research & Alignment Agent researches prospect company
- Agent extracts: company_size, industry, pain_points, strategic_priorities
- Research results stored in `prospect_company_info` table
- Research triggered automatically on prospect creation

**Tasks:**
- [ ] Design prospect_company_info table schema - 4h
- [ ] Create SQLAlchemy model - 3h
- [ ] Implement Research & Alignment Agent (research mode) - 10h
- [ ] Create Pydantic schema for company info - 4h
- [ ] Implement automatic research trigger on prospect creation - 5h
- [ ] Write prospect research tests - 6h
- [ ] Document prospect research - 3h

**Story 2.6.2: As an Alignment Agent, I need to rank value props for each prospect**

**Acceptance Criteria:**
- Research & Alignment Agent ranks value props by relevance to prospect
- Ranking considers prospect pain points and strategic priorities
- Ranked value props stored in `prospect_value_propositions` table
- Top 3 value props identified for each prospect

**Tasks:**
- [ ] Design prospect_value_propositions table schema - 4h
- [ ] Create SQLAlchemy model - 3h
- [ ] Implement Research & Alignment Agent (ranking mode) - 10h
- [ ] Create Pydantic schema for ranking output - 4h
- [ ] Implement ranking storage - 5h
- [ ] Write ranking tests - 6h
- [ ] Document ranking logic - 3h

**Story 2.6.3: As a user, I need prospect CRUD API so I can manage prospects**

**Acceptance Criteria:**
- `POST /api/v1/prospects` creates prospect and triggers research
- `GET /api/v1/prospects` lists prospects with research status
- `GET /api/v1/prospects/{id}` returns prospect with ranked value props
- `PATCH /api/v1/prospects/{id}` updates prospect info
- `DELETE /api/v1/prospects/{id}` soft-deletes prospect

**Tasks:**
- [ ] Design prospects table schema - 4h
- [ ] Create SQLAlchemy model - 3h
- [ ] Implement prospect CRUD endpoints - 10h
- [ ] Integrate prospect research orchestration - 6h
- [ ] Write prospect API tests - 6h
- [ ] Document prospect API - 3h

---

## Phase 1.0: Analytics Team & Dashboard Data Generation

**Duration:** 6 weeks (Weeks 9-14)
**Total Estimated Hours:** 360 hours

### Objectives

Implement Steps 4-5 of the Triton platform workflow:
- **Step 4**: Value proposition data generation (Analytics Team)
- **Step 5**: Dashboard widget data generation (Analytics Team)
- Analytics Team architecture with specialized agents (Clinical, Utilization, Pricing, Pharmacy)
- Question-to-SQL coordinator for Clickhouse query execution
- Pre-computed JSONB storage in PostgreSQL for fast UI rendering

### Acceptance Criteria

- [ ] Analytics Team generates value proposition data for prospects
- [ ] Analytics Team generates dashboard widget data for all templates
- [ ] Question-to-SQL agent translates analytics questions to SQL queries
- [ ] All widget data pre-computed and stored in PostgreSQL JSONB
- [ ] Data generation API working with async job processing
- [ ] Dashboard data retrievable in <10ms
- [ ] End-to-end workflow tested: client → value prop → templates → prospect → analytics data

---

### Epic 3.1: Analytics Team Architecture

**Priority:** Critical
**Estimated Hours:** 80 hours

#### User Stories

**Story 3.1.1: As a developer, I need Analytics Team orchestration framework**

**Acceptance Criteria:**
- Analytics Team coordinator agent implemented
- Team supports parallel agent execution
- Agent results aggregated into single output
- Team execution metrics tracked
- Failed agent tasks retried with error handling

**Tasks:**
- [ ] Design Analytics Team orchestration pattern - 8h
- [ ] Create base AnalyticsAgent class - 6h
- [ ] Implement team coordinator agent - 10h
- [ ] Add parallel execution support - 8h
- [ ] Implement result aggregation - 6h
- [ ] Add team execution monitoring - 5h
- [ ] Write team orchestration tests - 6h
- [ ] Document team architecture - 4h

**Story 3.1.2: As a developer, I need Question-to-SQL coordinator so agents can query data**

**Acceptance Criteria:**
- Question-to-SQL agent translates natural language to SQL
- Agent validates SQL syntax before execution
- Agent executes queries against Clickhouse
- Agent returns formatted results
- Query execution time logged

**Tasks:**
- [ ] Design Question-to-SQL agent instructions - 8h
- [ ] Create SQL query Pydantic schema - 4h
- [ ] Implement Question-to-SQL agent - 12h
- [ ] Add SQL syntax validation - 5h
- [ ] Integrate Clickhouse query execution - 6h
- [ ] Add query result formatting - 4h
- [ ] Write query generation tests - 6h
- [ ] Document Question-to-SQL usage - 3h

---

### Epic 3.2: Specialized Analytics Agents

**Priority:** Critical
**Estimated Hours:** 120 hours

#### User Stories

**Story 3.2.1: As an Analytics Team, I need a ClinicalAgent for clinical outcomes analysis**

**Acceptance Criteria:**
- ClinicalAgent analyzes clinical metrics (HbA1c, blood pressure, BMI, etc.)
- Agent generates queries for baseline vs outcome comparisons
- Agent formats clinical data for KPI widgets and charts
- Agent handles missing or incomplete clinical data gracefully

**Tasks:**
- [ ] Design ClinicalAgent instructions and scope - 6h
- [ ] Create clinical metrics Pydantic schemas - 5h
- [ ] Implement ClinicalAgent - 10h
- [ ] Add clinical data query generation - 6h
- [ ] Implement clinical metric calculations - 5h
- [ ] Write ClinicalAgent tests with sample data - 6h
- [ ] Document clinical analysis patterns - 3h

**Story 3.2.2: As an Analytics Team, I need a UtilizationAgent for utilization analysis**

**Acceptance Criteria:**
- UtilizationAgent analyzes ED visits, hospitalizations, readmissions
- Agent calculates utilization rates and trends
- Agent formats utilization data for widgets
- Agent compares pre/post program utilization

**Tasks:**
- [ ] Design UtilizationAgent instructions - 6h
- [ ] Create utilization metrics schemas - 5h
- [ ] Implement UtilizationAgent - 10h
- [ ] Add utilization query generation - 6h
- [ ] Implement utilization calculations - 5h
- [ ] Write UtilizationAgent tests - 6h
- [ ] Document utilization analysis - 3h

**Story 3.2.3: As an Analytics Team, I need a PricingAgent for ROI analysis**

**Acceptance Criteria:**
- PricingAgent calculates ROI, savings, cost avoidance
- Agent generates cost breakdown analyses
- Agent supports multiple ROI scenarios (conservative, moderate, optimistic)
- Agent formats pricing data for ROI widgets

**Tasks:**
- [ ] Design PricingAgent instructions - 6h
- [ ] Create pricing metrics schemas - 5h
- [ ] Implement PricingAgent - 10h
- [ ] Add ROI calculation logic - 8h
- [ ] Implement multi-scenario support - 5h
- [ ] Write PricingAgent tests - 6h
- [ ] Document ROI calculation methodology - 3h

**Story 3.2.4: As an Analytics Team, I need a PharmacyAgent for medication analysis**

**Acceptance Criteria:**
- PharmacyAgent analyzes medication adherence, drug costs
- Agent calculates medication possession ratio (MPR)
- Agent formats pharmacy data for widgets
- Agent handles different drug classes

**Tasks:**
- [ ] Design PharmacyAgent instructions - 6h
- [ ] Create pharmacy metrics schemas - 5h
- [ ] Implement PharmacyAgent - 10h
- [ ] Add pharmacy query generation - 6h
- [ ] Implement adherence calculations - 5h
- [ ] Write PharmacyAgent tests - 6h
- [ ] Document pharmacy analysis - 3h

---

### Epic 3.3: Value Proposition Data Generation

**Priority:** High
**Estimated Hours:** 60 hours

#### User Stories

**Story 3.3.1: As a user, I need value prop data generation so prospects have populated value prop pages**

**Acceptance Criteria:**
- Analytics Team generates data for all value prop sections
- Data pre-computed and stored in `prospect_value_proposition_data` table (JSONB)
- Data includes all metrics, charts, and text fields
- Generation triggered automatically after prospect ranking
- API endpoint retrieves value prop data in <10ms

**Tasks:**
- [ ] Design prospect_value_proposition_data table - 4h
- [ ] Create SQLAlchemy model with JSONB field - 3h
- [ ] Implement value prop data generation Celery task - 10h
- [ ] Orchestrate Analytics Team for value prop sections - 8h
- [ ] Implement data storage in JSONB - 5h
- [ ] Create value prop data retrieval endpoint - 5h
- [ ] Write value prop data generation tests - 6h
- [ ] Document value prop data format - 3h

**Story 3.3.2: As a user, I need value prop data API so frontend can render value prop pages**

**Acceptance Criteria:**
- `GET /api/v1/prospects/{id}/value-proposition-data` returns JSONB data
- Response includes all sections with populated metrics
- Response <10ms (pre-computed data)
- Handles missing data gracefully with defaults

**Tasks:**
- [ ] Implement value prop data endpoint - 5h
- [ ] Add response caching - 4h
- [ ] Implement default value handling - 4h
- [ ] Write API performance tests - 4h
- [ ] Document value prop data API - 2h

---

### Epic 3.4: Dashboard Data Generation

**Priority:** Critical
**Estimated Hours:** 100 hours

#### User Stories

**Story 3.4.1: As a user, I need dashboard data generation so prospects have populated dashboards**

**Acceptance Criteria:**
- Analytics Team generates widget data for all approved templates
- Each widget's data_requirements translated to SQL queries
- Widget data formatted per widget type (kpi-card, bar-chart, line-chart, etc.)
- Data stored in `prospect_dashboard_data` table (JSONB)
- Generation supports 5-10 templates × 8-12 widgets = 50-100 queries per prospect

**Tasks:**
- [ ] Design prospect_dashboard_data table - 4h
- [ ] Create SQLAlchemy model with JSONB field - 3h
- [ ] Implement dashboard data generation Celery task - 12h
- [ ] Implement widget data_requirements parser - 8h
- [ ] Orchestrate Analytics Team for widget queries - 10h
- [ ] Implement widget data formatting per type - 10h
- [ ] Add parallel query execution - 8h
- [ ] Write dashboard data generation tests - 8h
- [ ] Document dashboard data format - 4h

**Story 3.4.2: As a user, I need dashboard data API so frontend can render dashboards instantly**

**Acceptance Criteria:**
- `GET /api/v1/prospects/{id}/dashboards/{template_id}` returns complete dashboard JSONB
- Response includes all widget data formatted for Chart.js
- Response <10ms (pre-computed data)
- Supports multiple dashboards per prospect

**Tasks:**
- [ ] Implement dashboard data endpoint - 6h
- [ ] Add response caching - 4h
- [ ] Implement Chart.js data formatting - 6h
- [ ] Handle missing widgets gracefully - 4h
- [ ] Write dashboard API tests - 5h
- [ ] Document dashboard data API - 3h

**Story 3.4.3: As a user, I need dashboard list API so I can see all available dashboards for a prospect**

**Acceptance Criteria:**
- `GET /api/v1/prospects/{id}/dashboards` returns list of dashboards with metadata
- Each entry includes template name, category, widget count, generation status
- List sorted by category and target audience

**Tasks:**
- [ ] Implement dashboard list endpoint - 5h
- [ ] Add filtering by category and audience - 4h
- [ ] Add generation status tracking - 4h
- [ ] Write dashboard list tests - 4h
- [ ] Document dashboard list API - 2h

---

## Appendix A: Database Schema Summary

### Core Tables (Phase 0.1)

**clients**
- id (UUID, PK)
- company_name (VARCHAR)
- industry (VARCHAR)
- settings (JSONB)
- status (ENUM: active, inactive, deleted)
- created_at, updated_at (TIMESTAMP)

**generation_jobs**
- id (UUID, PK)
- job_type (ENUM: value_prop_derivation, template_generation, analytics_generation)
- client_id (UUID, FK → clients)
- prospect_id (UUID, FK → prospects, nullable)
- status (ENUM: pending, processing, completed, failed)
- progress (JSONB: stage, percent_complete, current_step)
- error_details (JSONB, nullable)
- created_at, completed_at (TIMESTAMP)

**client_documents**
- id (UUID, PK)
- client_id (UUID, FK → clients)
- name (VARCHAR)
- document_type (ENUM: collateral, roi_sheet, whitepaper, case_study, product_overview, other)
- description (TEXT)
- file_size (INTEGER)
- storage_path (VARCHAR)
- uploaded_at (TIMESTAMP)

### Value Proposition Tables (Phase 0.2)

**value_propositions**
- id (UUID, PK)
- client_id (UUID, FK → clients)
- version (INTEGER)
- mode (ENUM: research, collateral)
- status (ENUM: draft, in_review, approved)
- data (JSONB) ← Full ValuePropositionJSON
- created_at, updated_at, approved_at (TIMESTAMP)

**dashboard_templates**
- id (UUID, PK)
- client_id (UUID, FK → clients)
- name (VARCHAR)
- description (TEXT)
- category (VARCHAR)
- target_audience (VARCHAR)
- status (ENUM: generated, approved, removed)
- visual_style (JSONB)
- widgets (JSONB) ← Array of DashboardWidget with data_requirements
- metadata (JSONB)
- created_at (TIMESTAMP)

**prospects**
- id (UUID, PK)
- client_id (UUID, FK → clients)
- company_name (VARCHAR)
- industry (VARCHAR)
- contact_info (JSONB)
- status (ENUM: active, inactive)
- created_at, updated_at (TIMESTAMP)

**prospect_company_info**
- id (UUID, PK)
- prospect_id (UUID, FK → prospects)
- company_size (VARCHAR)
- industry (VARCHAR)
- pain_points (JSONB)
- strategic_priorities (JSONB)
- research_data (JSONB)
- created_at (TIMESTAMP)

**prospect_value_propositions**
- id (UUID, PK)
- prospect_id (UUID, FK → prospects)
- value_proposition_id (UUID, FK → value_propositions)
- rank (INTEGER)
- relevance_score (FLOAT)
- rationale (TEXT)
- created_at (TIMESTAMP)

### Analytics Tables (Phase 1.0)

**prospect_value_proposition_data**
- id (UUID, PK)
- prospect_id (UUID, FK → prospects)
- value_proposition_id (UUID, FK → value_propositions)
- data (JSONB) ← Pre-computed value prop sections with metrics
- generated_at (TIMESTAMP)
- generated_by (VARCHAR)

**prospect_dashboard_data**
- id (UUID, PK)
- prospect_id (UUID, FK → prospects)
- template_id (UUID, FK → dashboard_templates)
- dashboard_data (JSONB) ← Complete dashboard JSON with all widget data
- generated_at (TIMESTAMP)
- generated_by (VARCHAR)

**Clickhouse Tables (Analytics Data)**
- prospect_clinical_data (member_id, date, metric_name, metric_value, ...)
- prospect_utilization_data (member_id, date, event_type, facility_type, ...)
- prospect_claims_data (member_id, claim_id, service_date, paid_amount, ...)
- prospect_pharmacy_data (member_id, fill_date, drug_name, ndc, days_supply, ...)

---

## Appendix B: Key Pydantic Schemas

### ValuePropositionJSON
```python
class ValuePropositionJSON(BaseModel):
    metadata: Metadata
    executive_value_proposition: ExecutiveValueProposition
    clinical_outcomes_foundation: ClinicalOutcomesFoundation
    roi_opportunities: ROIOpportunities
    competitive_positioning: CompetitivePositioning
    implementation_readiness: ImplementationReadiness
```

### DashboardTemplate
```python
class DashboardTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: str  # roi-focused, clinical-outcomes, utilization-analysis, etc.
    target_audience: str  # Health Plan, Employer, Provider, ACO
    visual_style: VisualStyle
    widgets: List[DashboardWidget]
    metadata: TemplateMetadata
```

### DashboardWidget (with data_requirements)
```python
class DashboardWidget(BaseModel):
    widget_id: str
    widget_type: str  # kpi-card, bar-chart, line-chart, pie-chart, table, etc.
    title: str
    description: str
    position: WidgetPosition  # row, col, row_span, col_span
    data_requirements: DataRequirements
    analytics_question: str
    chart_config: Optional[ChartConfig]

class DataRequirements(BaseModel):
    query_type: str  # aggregate, time_series, distribution, comparison, ranking
    metrics: List[MetricDefinition]
    dimensions: Optional[List[str]]
    filters: Optional[List[FilterDefinition]]
    time_range: Optional[TimeRange]

class MetricDefinition(BaseModel):
    name: str
    expression: str  # SQL expression
    data_type: str  # number, percentage, currency, string, date
    format: str  # Display format
```

---

## Appendix C: API Endpoint Summary

### Phase 0.1 Endpoints
- `GET /health` - Health check
- `POST /api/v1/auth/login` - Authenticate and get JWT
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/clients` - Create client
- `GET /api/v1/clients` - List clients
- `GET /api/v1/clients/{id}` - Get client details
- `PATCH /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client

### Phase 0.2 Endpoints
- `POST /api/v1/clients/{id}/documents` - Upload document
- `GET /api/v1/clients/{id}/documents` - List documents
- `GET /api/v1/clients/{id}/documents/{doc_id}/download` - Get download URL
- `POST /api/v1/clients/{id}/value-proposition/derive` - Derive value prop (async)
- `GET /api/v1/clients/{id}/value-proposition/jobs/{job_id}` - Get derivation job status
- `GET /api/v1/clients/{id}/value-proposition` - Get value prop
- `GET /api/v1/clients/{id}/value-proposition/review` - Get value prop for review
- `POST /api/v1/clients/{id}/value-proposition/review/feedback` - Submit feedback (async)
- `GET /api/v1/clients/{id}/value-proposition/review/jobs/{job_id}` - Get refinement job status
- `POST /api/v1/clients/{id}/value-proposition/approve` - Approve value prop
- `POST /api/v1/clients/{id}/dashboard-templates/generate` - Generate templates (async)
- `GET /api/v1/clients/{id}/dashboard-templates/jobs/{job_id}` - Get generation job status
- `GET /api/v1/clients/{id}/dashboard-templates` - List templates
- `GET /api/v1/clients/{id}/dashboard-templates/{template_id}` - Get template details
- `POST /api/v1/clients/{id}/dashboard-templates/{template_id}/approve` - Approve template
- `DELETE /api/v1/clients/{id}/dashboard-templates/{template_id}` - Remove template
- `POST /api/v1/prospects` - Create prospect (triggers research)
- `GET /api/v1/prospects` - List prospects
- `GET /api/v1/prospects/{id}` - Get prospect with ranked value props
- `PATCH /api/v1/prospects/{id}` - Update prospect
- `DELETE /api/v1/prospects/{id}` - Delete prospect

### Phase 1.0 Endpoints
- `POST /api/v1/prospects/{id}/analytics/generate` - Generate all analytics data (async)
- `GET /api/v1/prospects/{id}/analytics/jobs/{job_id}` - Get analytics job status
- `GET /api/v1/prospects/{id}/value-proposition-data` - Get value prop data
- `GET /api/v1/prospects/{id}/dashboards` - List dashboards for prospect
- `GET /api/v1/prospects/{id}/dashboards/{template_id}` - Get dashboard data

---

## Appendix D: Risk Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **LLM API Rate Limits** | High | Medium | Implement exponential backoff, queue throttling, use multiple API keys |
| **Agent Output Validation Failures** | High | Medium | Max 3 retries with error feedback, comprehensive Pydantic schemas |
| **Clickhouse Query Performance** | Medium | Low | Index optimization, query caching, parallel execution |
| **Database Migration Issues** | High | Low | Thorough testing in dev, rollback procedures, schema versioning |
| **S3 Storage Costs** | Low | Medium | Document retention policies, compression, lifecycle rules |
| **Celery Worker Failures** | High | Medium | Health checks, auto-restart, dead letter queue |

### Process Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Scope Creep** | Medium | High | Strict phase boundaries, change request process |
| **Integration Delays with MARÉ** | Medium | Medium | Early API contract definition, mock endpoints |
| **Insufficient Test Coverage** | High | Medium | Enforce >80% coverage, integration tests per epic |
| **Documentation Drift** | Low | High | Documentation updates required per PR |

---

## Appendix E: Success Metrics

### Phase 0.1 Success Metrics
- [ ] All services start successfully via `docker-compose up`
- [ ] API responds to health check in <50ms
- [ ] Celery worker processes test task in <5s
- [ ] Database migrations apply cleanly
- [ ] >80% code coverage achieved
- [ ] Prometheus metrics accessible
- [ ] Grafana dashboards display metrics

### Phase 0.2 Success Metrics
- [ ] Value proposition generated from 3 documents in <90s
- [ ] Value proposition refinement completes in <60s
- [ ] Dashboard template generation produces 5-10 valid templates in <120s
- [ ] Prospect research completes in <45s
- [ ] Value prop ranking completes in <30s
- [ ] All Pydantic validations pass on first attempt >70% of the time
- [ ] Zero schema validation errors in production

### Phase 1.0 Success Metrics
- [ ] Analytics Team generates value prop data in <5 minutes
- [ ] Dashboard data generation for 10 templates in <5 minutes
- [ ] Dashboard data retrieval <10ms (p95)
- [ ] Value prop data retrieval <10ms (p95)
- [ ] Question-to-SQL agent success rate >85%
- [ ] Clickhouse queries complete in <500ms (p95)
- [ ] End-to-end workflow (client → analytics data) completes in <15 minutes

---

## Appendix F: Team Structure Recommendations

### Recommended Team Composition

**Phase 0.1 (Foundation)**
- 1 Backend Engineer (FastAPI, Celery, databases)
- 1 DevOps Engineer (Docker, CI/CD, monitoring)
- 0.5 QA Engineer (testing, automation)

**Phase 0.2 (Agents & Value Props)**
- 2 Backend Engineers (agent development, API)
- 0.5 AI/ML Engineer (prompt engineering, LLM integration)
- 0.5 QA Engineer (agent testing)

**Phase 1.0 (Analytics Team)**
- 2 Backend Engineers (agent coordination, data generation)
- 1 Data Engineer (Clickhouse optimization, SQL)
- 0.5 AI/ML Engineer (agent refinement)
- 0.5 QA Engineer (end-to-end testing)

---

## Appendix G: Next Steps After Phase 1.0

**Post-1.0 Enhancements:**
1. **Real-time Updates**: SSE/WebSocket for job progress
2. **Advanced Caching**: Redis caching for dashboard data
3. **Batch Processing**: Multi-prospect analytics generation
4. **Template Marketplace**: Shareable template library
5. **A/B Testing**: Template performance analytics
6. **Export Functionality**: PDF/PowerPoint export for dashboards
7. **User Management**: RBAC, teams, permissions
8. **Audit Logging**: Comprehensive activity logs
9. **Performance Optimization**: Database query optimization, caching strategies
10. **Migration to Temporal**: Replace Celery with Temporal for advanced workflow orchestration

---

**End of Implementation Roadmap**
