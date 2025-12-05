# Foundation & Core Infrastructure Implementation Plan

**Focus Area:** Phase 0.1
**Duration:** 4 weeks (Weeks 1-4)
**Total Estimated Hours:** 400 hours

---

## Overview

Establish the foundational infrastructure for the Triton platform including FastAPI, Celery, databases, authentication, and monitoring.

---

## Epic 1.1: FastAPI Application Setup

**Priority:** Critical
**Total Hours:** 80 hours
**Week:** Week 1

### Story 1.1.1: FastAPI Application Skeleton
**Estimated:** 28 hours

**Acceptance Criteria:**
- [ ] FastAPI application starts successfully on port 8000
- [ ] Health check endpoint returns 200 OK with service status
- [ ] Root endpoint returns API metadata (version, name, description)
- [ ] CORS middleware configured for frontend development
- [ ] Project follows standard Python package structure
- [ ] Environment-based configuration loading works (dev/staging/prod)
- [ ] Application logs to stdout in structured format

**Tasks:**
- Create project directory structure - 4h
- Implement health check endpoint - 3h
- Configure CORS middleware - 2h
- Setup environment configuration with Pydantic Settings - 4h
- Create base Pydantic models for API responses - 5h
- Setup structured logging with structlog - 4h
- Write unit tests for endpoints - 4h
- Document setup in docs/API_SETUP.md - 2h

---

### Story 1.1.2: Standardized Error Handling
**Estimated:** 21 hours

**Acceptance Criteria:**
- [ ] Global exception handlers for common HTTP errors (400, 401, 404, 422, 500)
- [ ] Error response format matches specification (code, message, details, request_id)
- [ ] Request ID tracking across all requests
- [ ] Validation errors return field-level details
- [ ] Unhandled exceptions logged with stack traces
- [ ] Error responses include helpful error codes

**Tasks:**
- Create error response Pydantic models - 3h
- Implement request ID middleware - 3h
- Create global exception handlers for all error types - 5h
- Configure structured error logging - 4h
- Write error handling tests - 4h
- Document error handling patterns - 2h

---

### Story 1.1.3: JWT Authentication
**Estimated:** 31 hours

**Acceptance Criteria:**
- [ ] JWT token generation working
- [ ] JWT token validation working
- [ ] POST /api/v1/auth/login endpoint returns valid JWT
- [ ] Protected endpoints reject requests without valid token
- [ ] Token expiration enforced (24 hours)
- [ ] Token refresh mechanism implemented
- [ ] Password hashing with bcrypt
- [ ] User authentication against mock data

**Tasks:**
- Install authentication dependencies (python-jose, passlib) - 1h
- Create JWT utilities (generate, validate, decode tokens) - 6h
- Create password utilities (hash, verify) - 3h
- Create authentication request/response models - 4h
- Implement login endpoint with mock user validation - 6h
- Create authentication dependency for protected routes - 5h
- Implement token refresh endpoint - 4h
- Write authentication integration tests - 5h
- Document authentication flow - 2h

---

## Epic 1.2: Task Queue Infrastructure

**Priority:** Critical
**Total Hours:** 100 hours
**Week:** Week 1-2

### Story 1.2.1: Celery Worker Setup
**Estimated:** 35 hours

**Acceptance Criteria:**
- [ ] Redis running via Docker Compose
- [ ] Celery application configured with Redis broker
- [ ] Celery worker starts and connects to Redis
- [ ] Test task executes successfully
- [ ] Task results stored in Redis backend
- [ ] Flower monitoring dashboard accessible at http://localhost:5555
- [ ] Worker logs structured and readable

**Tasks:**
- Setup Redis via Docker Compose - 3h
- Create Celery application configuration - 5h
- Implement test task for validation - 2h
- Configure Celery worker with proper settings - 4h
- Setup Flower monitoring dashboard - 3h
- Create worker startup script - 3h
- Test task execution end-to-end - 3h
- Write Celery integration tests - 6h
- Document Celery setup and usage - 3h
- Add worker to Docker Compose - 3h

---

### Story 1.2.2: Task Queue Abstraction
**Estimated:** 33 hours

**Acceptance Criteria:**
- [ ] Abstract TaskQueue interface defined
- [ ] CeleryTaskQueue implementation working
- [ ] Task enqueueing returns task_id
- [ ] Task status retrieval working (pending, processing, completed, failed)
- [ ] Task cancellation supported
- [ ] Factory pattern for queue selection
- [ ] Example showing how to swap implementations

**Tasks:**
- Design TaskQueue abstract base class with interface - 5h
- Implement CeleryTaskQueue concrete class - 8h
- Implement task status retrieval method - 5h
- Implement task cancellation method - 4h
- Create factory pattern for queue selection - 4h
- Create usage examples and documentation - 5h
- Write unit tests with mocked queue - 6h
- Document abstraction pattern in ADR-003 - 3h

---

### Story 1.2.3: Job Tracking in PostgreSQL
**Estimated:** 32 hours

**Acceptance Criteria:**
- [ ] generation_jobs table created in PostgreSQL
- [ ] Job CRUD operations working via SQLAlchemy
- [ ] Job statuses: pending, processing, completed, failed, cancelled
- [ ] Job progress tracking with percentage and stage
- [ ] Failed jobs store error details in JSONB
- [ ] Job history queryable with filters
- [ ] GET /api/v1/jobs/{job_id} endpoint returns job status

**Tasks:**
- Design generation_jobs table schema with indexes - 4h
- Create SQLAlchemy model for GenerationJob - 3h
- Implement JobService with CRUD operations - 6h
- Implement job status update methods - 4h
- Implement job progress tracking - 4h
- Create job API endpoints (GET /api/v1/jobs/{job_id}) - 5h
- Write integration tests with test database - 5h
- Document job tracking patterns and API - 2h

---

## Epic 1.3: Database Infrastructure

**Priority:** Critical
**Total Hours:** 80 hours
**Week:** Week 3

### Story 1.3.1: PostgreSQL Database Setup
**Estimated:** 31 hours

**Acceptance Criteria:**
- [ ] PostgreSQL running via Docker Compose
- [ ] Database connection pooling configured
- [ ] Core schema migrations applied (clients, value_propositions, prospects, generation_jobs)
- [ ] SQLAlchemy ORM models created for all core entities
- [ ] Database session management working
- [ ] Connection health checks implemented

**Tasks:**
- Setup PostgreSQL Docker service with volumes - 3h
- Design core database schema (clients, value_propositions, prospects, generation_jobs, documents) - 8h
- Create Alembic migration configuration - 4h
- Write initial migration with core tables and indexes - 6h
- Create SQLAlchemy models for all core entities - 8h
- Implement database session factory and dependency - 4h
- Write database utility functions (get_db, transactions) - 5h
- Test database connections and migrations - 3h
- Document database architecture and schema - 3h

---

### Story 1.3.2: Clickhouse Database Setup
**Estimated:** 31 hours

**Acceptance Criteria:**
- [ ] Clickhouse running via Docker Compose
- [ ] Connection established from FastAPI application
- [ ] Basic table schema for prospect analytics data created
- [ ] Sample data insertion working
- [ ] Query execution tested and performant
- [ ] Connection pooling configured

**Tasks:**
- Setup Clickhouse Docker service - 4h
- Design prospect analytics data schema (clinical, utilization, claims, pharmacy tables) - 6h
- Create Clickhouse table DDL scripts - 4h
- Implement Clickhouse client utility wrapper - 5h
- Configure connection pooling for Clickhouse - 4h
- Create sample data insertion scripts - 3h
- Test query performance with sample datasets - 3h
- Document Clickhouse setup and schema - 2h

---

### Story 1.3.3: Database Migration Tooling
**Estimated:** 18 hours

**Acceptance Criteria:**
- [ ] Alembic configured for PostgreSQL migrations
- [ ] Migration generation command working
- [ ] Migration rollback tested successfully
- [ ] Migrations applied successfully in dev environment
- [ ] CI/CD pipeline runs migrations automatically
- [ ] Migration history tracked

**Tasks:**
- Configure Alembic with environment-based settings - 3h
- Create migration generation helper script - 2h
- Test migration up operations - 4h
- Test migration down (rollback) operations - 4h
- Add migration check to CI/CD pipeline - 3h
- Document migration workflow and best practices - 2h

---

## Epic 1.4: Base Agent Framework

**Priority:** High
**Total Hours:** 60 hours
**Week:** Week 3-4

### Story 1.4.1: Agno Framework Integration
**Estimated:** 28 hours

**Acceptance Criteria:**
- [ ] Agno installed and configured with AWS Bedrock
- [ ] Simple test agent executes successfully
- [ ] Agent invocation logging working
- [ ] Agent response parsing validated
- [ ] Retry mechanism for failed LLM calls implemented (max 3 retries)
- [ ] Agent execution timing tracked

**Tasks:**
- Install Agno and AWS Bedrock dependencies - 2h
- Configure AWS Bedrock model provider with credentials - 5h
- Create BaseAgentTemplate class with template pattern - 6h
- Implement test agent with simple task execution - 4h
- Add LLM call retry logic with exponential backoff - 5h
- Configure agent logging and execution metrics - 4h
- Write agent integration tests - 6h
- Document Agno setup and agent creation patterns - 3h

---

### Story 1.4.2: Pydantic Validation for Agent Outputs
**Estimated:** 19 hours

**Acceptance Criteria:**
- [ ] Base Pydantic schemas for agent outputs defined
- [ ] Validation errors trigger agent retry with feedback
- [ ] JSON extraction from markdown working
- [ ] Schema validation integrated into agent wrapper
- [ ] Max 3 retry attempts enforced
- [ ] Validation failures logged with details

**Tasks:**
- Create base Pydantic models for common agent outputs - 5h
- Implement JSON extraction utility (handles markdown, code blocks) - 4h
- Create validation wrapper for agents - 6h
- Implement retry logic with error feedback to agent - 6h
- Write validation tests with invalid outputs - 5h
- Document validation patterns and retry behavior - 2h

---

### Story 1.4.3: Agent Execution Monitoring
**Estimated:** 13 hours

**Acceptance Criteria:**
- [ ] AgentOS deployed for agent debugging
- [ ] Agent execution traces visible in AgentOS UI
- [ ] Agent response times logged per invocation
- [ ] Failed agent calls logged with error details and stack traces
- [ ] Agent metrics exported to Prometheus

**Tasks:**
- Setup AgentOS via Docker Compose - 4h
- Configure agent execution tracing - 4h
- Implement agent timing metrics collection - 3h
- Add Prometheus metrics exporter for agents - 4h
- Create Grafana dashboard for agent metrics - 4h
- Document monitoring setup and debugging workflow - 2h

---

## Epic 1.5: Monitoring & Observability

**Priority:** Medium
**Total Hours:** 40 hours
**Week:** Week 4

### Story 1.5.1: Prometheus Metrics Collection
**Estimated:** 23 hours

**Acceptance Criteria:**
- [ ] Prometheus running via Docker Compose
- [ ] FastAPI metrics exported (request count, latency, errors by endpoint)
- [ ] Celery metrics exported (task count, duration, failures)
- [ ] Custom business metrics exported (jobs created, completed, failed)
- [ ] Metrics accessible via /metrics endpoint
- [ ] Prometheus scraping all services successfully

**Tasks:**
- Setup Prometheus Docker service - 3h
- Install and configure prometheus-fastapi-instrumentator - 2h
- Configure FastAPI application metrics - 4h
- Add Celery Prometheus exporter for worker metrics - 4h
- Implement custom business metrics (job counters, durations) - 5h
- Configure Prometheus scrape targets for all services - 3h
- Document metrics collection and available metrics - 2h

---

### Story 1.5.2: Grafana Dashboards
**Estimated:** 20 hours

**Acceptance Criteria:**
- [ ] Grafana running via Docker Compose
- [ ] Prometheus data source configured
- [ ] Default dashboard showing API metrics (requests, latency, errors)
- [ ] Dashboard showing Celery worker metrics (tasks, queue depth)
- [ ] Dashboard showing agent execution metrics
- [ ] Dashboards exported as JSON for version control

**Tasks:**
- Setup Grafana Docker service - 2h
- Configure Prometheus data source in Grafana - 2h
- Create API metrics dashboard (requests, latency, status codes) - 4h
- Create Celery metrics dashboard (tasks, workers, queue) - 4h
- Create agent metrics dashboard (invocations, duration, failures) - 4h
- Export all dashboards as JSON - 2h
- Document dashboard usage and customization - 2h

---

### Story 1.5.3: Structured Logging
**Estimated:** 10 hours

**Acceptance Criteria:**
- [ ] JSON-structured logs for all services
- [ ] Log levels configurable via environment variables
- [ ] Request ID included in all API logs
- [ ] Agent execution logs include job_id and task_name
- [ ] Logs aggregated to stdout for Docker collection
- [ ] Error logs include stack traces

**Tasks:**
- Configure structlog for JSON logging across all services - 4h
- Add request ID context to all API logs - 3h
- Add job_id and task_name context to Celery task logs - 3h
- Configure log levels per environment (dev/prod) - 2h
- Document logging conventions and best practices - 2h

---

## Epic 1.6: Infrastructure as Code & Deployment

**Priority:** Medium
**Total Hours:** 40 hours
**Week:** Week 4

### Story 1.6.1: Docker Compose Full Stack Setup
**Estimated:** 24 hours

**Acceptance Criteria:**
- [ ] docker-compose.yml defines all services (API, Worker, Redis, Postgres, Clickhouse, Prometheus, Grafana, Flower, AgentOS)
- [ ] All services start successfully with single command: docker-compose up
- [ ] Environment variables configured via .env file
- [ ] Health checks defined for all services
- [ ] Volume persistence for databases
- [ ] Service dependencies and startup order configured

**Tasks:**
- Create comprehensive docker-compose.yml with all services - 6h
- Write Dockerfile for FastAPI application - 3h
- Write Dockerfile for Celery worker - 3h
- Configure service dependencies and health checks - 4h
- Create .env.example with all required variables - 2h
- Test full stack startup and connectivity - 3h
- Document Docker setup in docs/DOCKER_SETUP.md - 3h

---

### Story 1.6.2: CI/CD Pipeline
**Estimated:** 16 hours

**Acceptance Criteria:**
- [ ] GitHub Actions workflow for PR validation
- [ ] Automated tests run on every push to main/develop
- [ ] Code coverage report generated and enforced (>80%)
- [ ] Docker images built and tagged automatically
- [ ] Linting (ruff) and type checking (mypy) enforced
- [ ] Failed builds block PR merges

**Tasks:**
- Create GitHub Actions workflow file (.github/workflows/test.yml) - 4h
- Configure pytest execution in CI with coverage - 3h
- Add code coverage reporting with threshold enforcement - 3h
- Add linting (ruff) and type checking (mypy) steps - 3h
- Configure Docker image build and push to registry - 4h
- Document CI/CD pipeline and workflows - 2h

---

## Phase Summary

**Total Hours:** 400 hours

**Epic Breakdown:**
- Epic 1.1: FastAPI Application Setup - 80h
- Epic 1.2: Task Queue Infrastructure - 100h
- Epic 1.3: Database Infrastructure - 80h
- Epic 1.4: Base Agent Framework - 60h
- Epic 1.5: Monitoring & Observability - 40h
- Epic 1.6: Infrastructure as Code - 40h

**Week-by-Week:**
- Week 1: FastAPI + Start Celery (80h)
- Week 2: Complete Celery + Start Databases (100h)
- Week 3: Complete Databases + Agents (100h)
- Week 4: Complete Agents + Monitoring + Infrastructure (120h)

**Recommended Team:**
- 1 Backend Engineer (FastAPI, Celery, Agents)
- 1 DevOps Engineer (Docker, Databases, Monitoring)
- 0.5 QA Engineer (Testing, Automation)

**Success Criteria:**
- [ ] All services start with docker-compose up
- [ ] Health check responds in <50ms
- [ ] Celery processes tasks successfully
- [ ] Job tracking fully functional
- [ ] Databases accessible and migrated
- [ ] Agent framework operational
- [ ] Monitoring dashboards displaying data
- [ ] >80% code coverage
- [ ] All integration tests passing
