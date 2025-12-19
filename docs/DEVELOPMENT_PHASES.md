# Triton Platform - Development Phases Tracker

**Version:** 1.0.0
**Last Updated:** 2025-12-17
**Status:** Active Development
**Total Duration:** 4-6 months

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase Overview](#phase-overview)
3. [Phase Details](#phase-details)
4. [Dependencies Graph](#dependencies-graph)
5. [Timeline & Milestones](#timeline--milestones)
6. [Critical Path](#critical-path)
7. [Resource Allocation](#resource-allocation)
8. [Status Dashboard](#status-dashboard)
9. [How to Use This Document](#how-to-use-this-document)

---

## Executive Summary

The Triton Platform development is organized into **6 major phases**, each containing **4-5 sub-phases** with detailed implementation specifications. This document serves as the master tracker for all development activities.

### Development Philosophy

- **Sequential with Parallel Work**: Phases build on each other, but sub-phases within a phase can run in parallel
- **JIRA-Style Detail**: Each sub-phase is documented like a JIRA ticket with description, tasks, and acceptance criteria
- **Workflow-Focused**: Documentation emphasizes logic flow and workflows, not code implementation
- **Incremental Delivery**: Each phase produces deployable functionality

### Quick Navigation

| Phase | Name | Status | Duration | Docs |
|-------|------|--------|----------|------|
| **Phase 1** | Foundation & Infrastructure | 🟡 In Progress | 2-3 weeks | [phase-1/](./phase-1/) |
| **Phase 2** | Research Agents | 🟢 Planned | 2-3 weeks | [phase-2/](./phase-2/) |
| **Phase 3** | ROI Model System | 🟢 Planned | 3-4 weeks | [phase-3/](./phase-3/) |
| **Phase 4** | Analytics & Data Generation | 🟢 Planned | 2-3 weeks | [phase-4/](./phase-4/) |
| **Phase 5** | Data Quality & Lineage | 🟢 Planned | 2-3 weeks | [phase-5/](./phase-5/) |
| **Phase 6** | Optimization & Enterprise | 🟢 Planned | 2-3 weeks | [phase-6/](./phase-6/) |

**Legend:**
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Planned
- ✅ Complete
- ⚠️ Blocked

---

## Phase Overview

### Phase 1: Foundation & Infrastructure (Weeks 1-3)

**Goal:** Establish core infrastructure, database schema, and foundational services required for all subsequent phases.

**Key Deliverables:**
- PostgreSQL + Clickhouse + Redis setup
- Core database schema (clients, value_propositions, templates)
- Message broker (Redis Pub/Sub) with SSE
- FastAPI application structure
- Docker containerization
- Health monitoring basics

**Sub-Phases:**
- **1.1** Infrastructure Setup (3 days)
- **1.2** Database Schema Design (2 days)
- **1.3** Message Broker Implementation (2 days)
- **1.4** API Foundation (3 days)

**Success Criteria:**
- ✅ All services running in Docker
- ✅ Database migrations executable
- ✅ Message broker pushing real-time events
- ✅ API endpoints returning 200 OK
- ✅ Integration tests passing

**Dependencies:** None (foundational phase)

---

### Phase 2: Research Agents (Weeks 4-6)

**Goal:** Implement intelligent research agents for web search and document analysis to gather client intelligence and ROI information.

**Key Deliverables:**
- WebSearchAgent with DuckDuckGo/Tavily integration
- DocumentAnalysisAgent with hybrid PDF processing
- Research API layer with async job management
- 4-layer validation pipeline (JSON → Pydantic → Business → Domain)
- S3 document storage integration

**Sub-Phases:**
- **2.1** Web Search Agent (4 days)
- **2.2** Document Analysis Agent (4 days)
- **2.3** Research API Layer (2 days)
- **2.4** Agent Validation Pipeline (2 days)

**Success Criteria:**
- ✅ WebSearchAgent performs 15-25 autonomous searches
- ✅ DocumentAnalysisAgent extracts data from PDF/DOCX/TXT
- ✅ Research jobs tracked with real-time status updates
- ✅ Validation catches malformed agent outputs
- ✅ 95%+ agent success rate on test documents

**Dependencies:** Phase 1 (database, API foundation, message broker)

---

### Phase 3: ROI Model System (Weeks 7-10)

**Goal:** Build the quantitative ROI model system that classifies ROI stories into 13 types and generates mathematical models with variables and formulas.

**Key Deliverables:**
- ROI Classification Agent (13 model types: B1-B13)
- ROI Model Builder Agent with prompt engineering
- Integration with mare-triton-research-prompts repository
- 4-layer model validation pipeline
- Dashboard Template Generator (5-10 variations per model)
- PostgreSQL storage for ROI models

**Sub-Phases:**
- **3.1** ROI Classification Agent (3 days)
- **3.2** ROI Model Builder Agent (5 days)
- **3.3** Prompt Engineering System (3 days)
- **3.4** Model Validation Pipeline (3 days)
- **3.5** Dashboard Template Generation (4 days)

**Success Criteria:**
- ✅ Classification agent correctly identifies all 13 model types
- ✅ Model Builder generates valid JSON (50KB structure)
- ✅ All 13 prompts (7,641 lines) load successfully
- ✅ 4-layer validation catches schema errors
- ✅ Dashboard templates generated for each ROI model
- ✅ End-to-end test: PDF → ROI Model → Dashboard Templates

**Dependencies:** Phase 2 (document analysis for ROI story extraction)

---

### Phase 4: Analytics & Data Generation (Weeks 11-13)

**Goal:** Implement Analytics Team agents that query Clickhouse data and generate prospect-specific dashboard data and value proposition insights.

**Key Deliverables:**
- Industry Benchmark Data System (web search + API integration)
- Analytics Team Agents (Clinical, Utilization, Pricing, Pharmacy)
- Question-to-SQL Agent (coordinator)
- Prospect Data Generation pipeline
- Dashboard Data Generation pipeline
- JSONB storage in PostgreSQL

**Sub-Phases:**
- **4.1** Industry Benchmark System (3 days)
- **4.2** Analytics Team Agents (5 days)
- **4.3** Prospect Data Generation (3 days)
- **4.4** Dashboard Data Pipeline (3 days)

**Success Criteria:**
- ✅ Benchmarks fetched from CMS/CDC or web search
- ✅ Analytics agents generate SQL queries from natural language
- ✅ Prospect data auto-generated during template creation
- ✅ Dashboard widgets populated with real Clickhouse data
- ✅ Single JSONB query returns full dashboard (~10ms)
- ✅ End-to-end test: Prospect upload → Dashboard with data

**Dependencies:** Phase 3 (ROI models and templates), Phase 1 (Clickhouse setup)

---

### Phase 5: Data Quality & Lineage (Weeks 14-16)

**Goal:** Implement comprehensive data lineage tracking and hallucination prevention to ensure extraction accuracy and provide complete audit trails.

**Key Deliverables:**
- extraction_lineage table with 10-25 tracking fields
- 5-layer validation pipeline (adds source verification)
- Source text verification (requires verbatim quotes)
- Document hash tracking (detects source changes)
- Bi-directional traceability (document → dashboard, dashboard → document)
- Lineage API endpoints

**Sub-Phases:**
- **5.1** Extraction Lineage System (4 days)
- **5.2** Source Verification Layer (3 days)
- **5.3** Hallucination Prevention (3 days)
- **5.4** Audit Trail API (2 days)

**Success Criteria:**
- ✅ All extractions tracked with source_text and document_hash
- ✅ Source verification catches invented data (0% hallucinations)
- ✅ Lineage queryable from any ROI model or dashboard
- ✅ Complete audit trail: Document → Extraction → ROI Model → Dashboard
- ✅ API endpoints return lineage for compliance audits
- ✅ Adversarial hallucination tests pass (9/9 correct extractions)

**Dependencies:** Phase 2 (agents generating extractions), Phase 4 (dashboard data generation)

---

### Phase 6: Optimization & Enterprise (Weeks 17-20)

**Goal:** Optimize performance, add enterprise features, and implement comprehensive monitoring and observability.

**Key Deliverables:**
- Hybrid PDF processing (text extraction + Vision API fallback)
- Performance optimization (caching, query optimization, connection pooling)
- Prometheus + Grafana monitoring stack
- Alerting and incident response
- Enterprise features (multi-tenancy, RBAC, audit logs)
- Production deployment guides

**Sub-Phases:**
- **6.1** Hybrid PDF Processing (3 days)
- **6.2** Performance Optimization (4 days)
- **6.3** Monitoring & Observability (3 days)
- **6.4** Enterprise Features (5 days)

**Success Criteria:**
- ✅ PDF processing uses hybrid approach (67% cost savings)
- ✅ Dashboard queries < 100ms (95th percentile)
- ✅ Grafana dashboards show all key metrics
- ✅ Alerts trigger on anomalies (stale data, high latency, errors)
- ✅ Multi-tenant isolation working
- ✅ Production deployment successful
- ✅ Load testing: 100 concurrent users, < 500ms response time

**Dependencies:** Phase 1-5 (optimizing existing functionality)

---

## Phase Details

### Sub-Phase Naming Convention

Each sub-phase follows the format: **X.Y-descriptive-name.md**

Examples:
- `1.1-infrastructure-setup.md`
- `3.2-roi-model-builder-agent.md`
- `5.3-hallucination-prevention.md`

### Sub-Phase File Structure

Each sub-phase file contains:

```markdown
# Task: [Sub-Phase Name]

## Metadata
- Phase, Sub-Phase, Priority, Effort, Dependencies, Status

## Description
[2-3 paragraphs explaining what this accomplishes]

## Objectives
[Bullet list of specific objectives]

## Tasks Breakdown
[Detailed task list with steps, owner, effort]

## Acceptance Criteria
[Specific measurable outcomes - JIRA style]

## Workflow Diagram
[ASCII art showing logic flow]

## Technical Requirements
[Infrastructure, dependencies, tools needed]

## Testing Strategy
[Unit, integration, manual testing plans]

## Rollback Plan
[How to undo if something goes wrong]

## Related Documentation
[Links to reference docs]
```

---

## Dependencies Graph

```
Phase 1: Foundation & Infrastructure
  │
  ├─ 1.1 Infrastructure Setup
  ├─ 1.2 Database Schema Design
  ├─ 1.3 Message Broker Implementation
  └─ 1.4 API Foundation

          ↓ (Requires Phase 1 complete)

Phase 2: Research Agents
  │
  ├─ 2.1 Web Search Agent
  ├─ 2.2 Document Analysis Agent
  ├─ 2.3 Research API Layer
  └─ 2.4 Agent Validation Pipeline

          ↓ (Requires Phase 2 complete)

Phase 3: ROI Model System
  │
  ├─ 3.1 ROI Classification Agent
  ├─ 3.2 ROI Model Builder Agent
  ├─ 3.3 Prompt Engineering System
  ├─ 3.4 Model Validation Pipeline
  └─ 3.5 Dashboard Template Generation

          ↓ (Requires Phase 3 complete)

Phase 4: Analytics & Data Generation
  │
  ├─ 4.1 Industry Benchmark System
  ├─ 4.2 Analytics Team Agents
  ├─ 4.3 Prospect Data Generation
  └─ 4.4 Dashboard Data Pipeline

          ↓ (Requires Phase 2 + Phase 4)

Phase 5: Data Quality & Lineage
  │
  ├─ 5.1 Extraction Lineage System
  ├─ 5.2 Source Verification Layer
  ├─ 5.3 Hallucination Prevention
  └─ 5.4 Audit Trail API

          ↓ (Requires Phase 1-5)

Phase 6: Optimization & Enterprise
  │
  ├─ 6.1 Hybrid PDF Processing
  ├─ 6.2 Performance Optimization
  ├─ 6.3 Monitoring & Observability
  └─ 6.4 Enterprise Features
```

**Critical Path:** 1.1 → 1.2 → 1.3 → 1.4 → 2.2 → 3.1 → 3.2 → 4.2 → 4.4 → 5.1 → 5.2

**Parallel Opportunities:**
- Phase 1: All sub-phases can run in parallel (different team members)
- Phase 2: 2.1 and 2.2 can be developed simultaneously
- Phase 3: 3.3 (prompt engineering) can start during 3.1-3.2 development
- Phase 4: 4.1 (benchmarks) independent of other sub-phases
- Phase 6: Most optimization work can be parallelized

---

## Timeline & Milestones

### Month 1 (Weeks 1-4)

**Week 1: Foundation Setup**
- Days 1-3: Infrastructure & Docker (1.1)
- Days 4-5: Database schema (1.2)

**Week 2: API & Messaging**
- Days 1-2: Message broker (1.3)
- Days 3-5: API foundation (1.4)

**Week 3: Web Search Agent**
- Days 1-4: Web search implementation (2.1)
- Day 5: Testing & fixes

**Week 4: Document Analysis**
- Days 1-4: Document agent (2.2)
- Day 5: Integration testing

**Milestone 1 (End of Month 1):**
- ✅ Core infrastructure running
- ✅ Research agents operational
- ✅ Basic API endpoints working

---

### Month 2 (Weeks 5-8)

**Week 5: Research API Layer**
- Days 1-2: Research API (2.3)
- Days 3-4: Validation pipeline (2.4)
- Day 5: End-to-end research testing

**Week 6: ROI Classification**
- Days 1-3: Classification agent (3.1)
- Days 4-5: Prompt engineering setup (3.3 start)

**Week 7: ROI Model Builder**
- Days 1-5: Model builder agent (3.2)

**Week 8: Model Validation & Templates**
- Days 1-3: Model validation (3.4)
- Days 4-5: Template generation start (3.5)

**Milestone 2 (End of Month 2):**
- ✅ Research agents production-ready
- ✅ ROI models generating successfully
- ✅ 13 model types all working

---

### Month 3 (Weeks 9-12)

**Week 9: Dashboard Templates**
- Days 1-4: Complete template generation (3.5)
- Day 5: End-to-end ROI model testing

**Week 10: Industry Benchmarks**
- Days 1-3: Benchmark system (4.1)
- Days 4-5: Analytics team agents start (4.2)

**Week 11: Analytics Agents**
- Days 1-5: Complete analytics agents (4.2)

**Week 12: Data Generation**
- Days 1-3: Prospect data generation (4.3)
- Days 3-5: Dashboard data pipeline (4.4)

**Milestone 3 (End of Month 3):**
- ✅ ROI models → Dashboard templates working
- ✅ Analytics agents generating insights
- ✅ End-to-end prospect flow complete

---

### Month 4 (Weeks 13-16)

**Week 13: Lineage System**
- Days 1-4: Extraction lineage (5.1)
- Day 5: Database migrations

**Week 14: Source Verification**
- Days 1-3: Verification layer (5.2)
- Days 4-5: Hallucination prevention start (5.3)

**Week 15: Hallucination Prevention**
- Days 1-3: Complete prevention logic (5.3)
- Days 4-5: Audit API (5.4)

**Week 16: Lineage Testing**
- Days 1-2: Complete audit API (5.4)
- Days 3-5: Adversarial testing

**Milestone 4 (End of Month 4):**
- ✅ Complete data lineage tracking
- ✅ 0% hallucination rate achieved
- ✅ Audit trails queryable

---

### Month 5 (Weeks 17-20)

**Week 17: Hybrid PDF Processing**
- Days 1-3: Hybrid processing (6.1)
- Days 4-5: Testing & cost analysis

**Week 18: Performance Optimization**
- Days 1-4: Query optimization, caching (6.2)
- Day 5: Load testing

**Week 19: Monitoring Stack**
- Days 1-3: Prometheus + Grafana (6.3)
- Days 4-5: Alerting setup

**Week 20: Enterprise Features**
- Days 1-5: Multi-tenancy, RBAC (6.4)

**Milestone 5 (End of Month 5):**
- ✅ Production-grade performance
- ✅ Full observability stack
- ✅ Enterprise features deployed

---

### Month 6 (Weeks 21-24) - Buffer & Polish

**Week 21-22: Production Deployment**
- Staging environment setup
- Production deployment
- Smoke testing
- Monitoring validation

**Week 23-24: Buffer Time**
- Bug fixes
- Documentation updates
- Training materials
- Handoff to operations

**Final Milestone:**
- ✅ Production deployment successful
- ✅ All acceptance criteria met
- ✅ Documentation complete
- ✅ Team trained

---

## Critical Path

The **critical path** defines the minimum sequence of tasks that must be completed sequentially. Delays in critical path tasks delay the entire project.

### Critical Path Tasks (16 weeks minimum)

```
Week 1:    1.1 Infrastructure Setup (3 days) → 1.2 Database Schema (2 days)
Week 2:    1.3 Message Broker (2 days) → 1.4 API Foundation (3 days)
Week 3:    [Buffer]
Week 4:    2.2 Document Analysis Agent (4 days)
Week 5:    2.4 Agent Validation Pipeline (2 days)
Week 6:    3.1 ROI Classification Agent (3 days)
Week 7-8:  3.2 ROI Model Builder Agent (5 days)
Week 9:    3.5 Dashboard Template Generation (4 days)
Week 11:   4.2 Analytics Team Agents (5 days)
Week 12:   4.4 Dashboard Data Pipeline (3 days)
Week 13:   5.1 Extraction Lineage System (4 days)
Week 14:   5.2 Source Verification Layer (3 days)
Week 17:   6.1 Hybrid PDF Processing (3 days)
Week 18:   6.2 Performance Optimization (4 days)
Week 19:   6.3 Monitoring & Observability (3 days)
```

**Total Critical Path: 16 weeks** (4 months minimum)

**Non-Critical Path Tasks** (can run in parallel):
- 2.1 Web Search Agent (parallel with 2.2)
- 2.3 Research API Layer (can start during 2.1-2.2)
- 3.3 Prompt Engineering System (parallel with 3.1-3.2)
- 4.1 Industry Benchmark System (independent)
- 5.3 Hallucination Prevention (parallel with 5.2)
- 5.4 Audit Trail API (can start during 5.2-5.3)
- 6.4 Enterprise Features (parallel with 6.1-6.3)

---

## Resource Allocation

### Team Composition

**Core Team (5 people):**
1. **Backend Engineer 1**: Foundation, APIs, database (Phases 1, 4)
2. **Backend Engineer 2**: Agents, validation, AI integration (Phases 2, 3, 5)
3. **Data Engineer**: Clickhouse, analytics, SQL generation (Phase 4)
4. **DevOps Engineer**: Infrastructure, Docker, monitoring (Phases 1, 6)
5. **QA Engineer**: Testing, validation, quality assurance (All phases)

**Part-Time Support:**
- **Prompt Engineer**: ROI model prompts (Phase 3 only - 2 weeks)
- **Frontend Engineer**: Integration testing, mock data setup (Phases 4-5)

### Time Allocation by Phase

| Phase | Backend | Data Eng | DevOps | QA | Prompt Eng | Total |
|-------|---------|----------|--------|----|-----------:|------:|
| Phase 1 | 2 weeks | - | 2 weeks | 1 week | - | 3 weeks |
| Phase 2 | 3 weeks | - | - | 1 week | - | 3 weeks |
| Phase 3 | 3 weeks | - | - | 1 week | 2 weeks | 4 weeks |
| Phase 4 | 2 weeks | 3 weeks | - | 1 week | - | 3 weeks |
| Phase 5 | 2 weeks | 1 week | - | 1 week | - | 3 weeks |
| Phase 6 | 1 week | - | 3 weeks | 1 week | - | 3 weeks |
| **Total** | **13 weeks** | **4 weeks** | **5 weeks** | **6 weeks** | **2 weeks** | **19 weeks** |

**Buffer:** +4-8 weeks for unforeseen issues, integration testing, production deployment

---

## Status Dashboard

### Overall Progress

```
Phase 1: Foundation & Infrastructure      [██░░░░░░░░] 20% (1.1 in progress)
Phase 2: Research Agents                  [░░░░░░░░░░]  0% (Not started)
Phase 3: ROI Model System                 [░░░░░░░░░░]  0% (Not started)
Phase 4: Analytics & Data Generation      [░░░░░░░░░░]  0% (Not started)
Phase 5: Data Quality & Lineage           [░░░░░░░░░░]  0% (Not started)
Phase 6: Optimization & Enterprise        [░░░░░░░░░░]  0% (Not started)

Overall Progress: [██░░░░░░░░░░░░░░░░░░] 3% (1 of 24 sub-phases complete)
```

### Sub-Phase Status

| Sub-Phase | Status | Owner | Start Date | End Date | Notes |
|-----------|--------|-------|------------|----------|-------|
| 1.1 | 🟡 In Progress | DevOps | 2025-12-17 | 2025-12-20 | Docker setup |
| 1.2 | 🔴 Not Started | Backend 1 | - | - | - |
| 1.3 | 🔴 Not Started | Backend 1 | - | - | - |
| 1.4 | 🔴 Not Started | Backend 1 | - | - | - |
| 2.1 | 🔴 Not Started | Backend 2 | - | - | - |
| 2.2 | 🔴 Not Started | Backend 2 | - | - | - |
| 2.3 | 🔴 Not Started | Backend 1 | - | - | - |
| 2.4 | 🔴 Not Started | Backend 2 | - | - | - |
| 3.1 | 🔴 Not Started | Backend 2 | - | - | - |
| 3.2 | 🔴 Not Started | Backend 2 | - | - | - |
| 3.3 | 🔴 Not Started | Prompt Eng | - | - | - |
| 3.4 | 🔴 Not Started | Backend 2 | - | - | - |
| 3.5 | 🔴 Not Started | Backend 1 | - | - | - |
| 4.1 | 🔴 Not Started | Backend 2 | - | - | - |
| 4.2 | 🔴 Not Started | Data Eng | - | - | - |
| 4.3 | 🔴 Not Started | Backend 1 | - | - | - |
| 4.4 | 🔴 Not Started | Data Eng | - | - | - |
| 5.1 | 🔴 Not Started | Backend 1 | - | - | - |
| 5.2 | 🔴 Not Started | Backend 2 | - | - | - |
| 5.3 | 🔴 Not Started | Backend 2 | - | - | - |
| 5.4 | 🔴 Not Started | Backend 1 | - | - | - |
| 6.1 | 🔴 Not Started | Backend 2 | - | - | - |
| 6.2 | 🔴 Not Started | Backend 1 | - | - | - |
| 6.3 | 🔴 Not Started | DevOps | - | - | - |
| 6.4 | 🔴 Not Started | Backend 1 | - | - | - |

### Blockers & Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| AWS Bedrock API rate limits | HIGH | Medium | Implement exponential backoff, caching |
| Prompt engineering takes longer | Medium | High | Allocate buffer time, start early |
| Performance issues with Clickhouse | HIGH | Medium | Early load testing, query optimization |
| Hallucination prevention complex | HIGH | Medium | Extensive testing, multiple verification layers |
| Integration complexity | Medium | High | Weekly integration testing, early prototypes |

---

## How to Use This Document

### For Project Managers

1. **Track Progress**: Update "Status Dashboard" section weekly
2. **Monitor Critical Path**: Flag any delays in critical path tasks immediately
3. **Resource Allocation**: Adjust team assignments based on phase needs
4. **Risk Management**: Update "Blockers & Risks" section daily

### For Developers

1. **Find Your Work**: Check "Sub-Phase Status" table for your assigned tasks
2. **Read Sub-Phase Files**: Each sub-phase has detailed JIRA-style ticket in phase folder
3. **Follow Workflow**: Diagrams in sub-phase files show logic flow
4. **Report Progress**: Update status when sub-phase complete

### For Stakeholders

1. **View Overall Progress**: Check "Status Dashboard" for high-level view
2. **Understand Timeline**: Review "Timeline & Milestones" for delivery dates
3. **Review Deliverables**: Each phase section lists key deliverables

### For New Team Members

1. **Start Here**: Read [phase-1/README.md](./phase-1/README.md)
2. **Understand Dependencies**: Review "Dependencies Graph"
3. **Learn Architecture**: Read sub-phase files in order (1.1 → 1.2 → ...)

---

## Update History

| Date | Updated By | Changes |
|------|------------|---------|
| 2025-12-17 | Engineering Team | Initial version created |

---

## Related Documentation

- [Main Documentation Index](./README.md)
- [Phase 1: Foundation & Infrastructure](./phase-1/README.md)
- [Phase 2: Research Agents](./phase-2/README.md)
- [Phase 3: ROI Model System](./phase-3/README.md)
- [Phase 4: Analytics & Data Generation](./phase-4/README.md)
- [Phase 5: Data Quality & Lineage](./phase-5/README.md)
- [Phase 6: Optimization & Enterprise](./phase-6/README.md)

---

**Next Steps:**
1. Review this master tracker with entire team
2. Assign owners to each sub-phase
3. Set up weekly status update meetings
4. Begin Phase 1.1 (Infrastructure Setup)

---

**For Questions or Updates**: Contact project lead or update this document directly.
