# Analytics Team & Dashboard Data Generation Implementation Plan

**Focus Area:** Phase 1.0
**Duration:** 6 weeks (Weeks 9-14)
**Total Estimated Hours:** 360 hours

---

## Overview

Implement Analytics Team with specialized agents for clinical, utilization, pricing, and pharmacy analysis. Generate pre-computed dashboard data and value proposition data stored in PostgreSQL JSONB for <10ms retrieval.

---

## Epic 3.1: Analytics Team Architecture

**Priority:** Critical
**Total Hours:** 80 hours
**Week:** Week 9

### Story 3.1.1: Analytics Team Orchestration Framework
**Estimated:** 47 hours

**Acceptance Criteria:**
- [ ] Analytics Team coordinator agent implemented
- [ ] Team supports parallel agent execution (4+ agents simultaneously)
- [ ] Agent results aggregated into single output
- [ ] Team execution metrics tracked (total time, agent times)
- [ ] Failed agent tasks retried with error handling (max 3 retries)
- [ ] Progress updates propagated to job tracking

**Tasks:**
- Design Analytics Team orchestration pattern and workflow - 8h
- Create base AnalyticsAgent class with common functionality - 6h
- Implement team coordinator agent for orchestration - 10h
- Add parallel execution support using asyncio or concurrent.futures - 8h
- Implement result aggregation and conflict resolution - 6h
- Add team execution monitoring and metrics collection - 5h
- Write team orchestration integration tests - 6h
- Document team architecture and coordination patterns - 4h

---

### Story 3.1.2: Question-to-SQL Coordinator Agent
**Estimated:** 48 hours

**Acceptance Criteria:**
- [ ] Question-to-SQL agent translates natural language analytics questions to SQL
- [ ] Agent validates SQL syntax before execution
- [ ] Agent executes queries against Clickhouse
- [ ] Agent returns formatted results ready for widget consumption
- [ ] Query execution time logged for performance monitoring
- [ ] Agent handles complex queries (JOINs, aggregations, window functions)

**Tasks:**
- Design Question-to-SQL agent instructions with SQL generation rules - 8h
- Create SQL query Pydantic schema with validation - 4h
- Implement Question-to-SQL agent using Agno framework - 12h
- Add SQL syntax validation using sqlparse or similar - 5h
- Integrate Clickhouse query execution with connection pooling - 6h
- Add query result formatting for different widget types - 4h
- Implement query optimization hints and best practices - 4h
- Write query generation tests with various question types - 6h
- Document Question-to-SQL usage and examples - 3h

---

## Epic 3.2: Specialized Analytics Agents

**Priority:** Critical
**Total Hours:** 120 hours
**Week:** Week 9-10

### Story 3.2.1: ClinicalAgent for Clinical Outcomes
**Estimated:** 30 hours

**Acceptance Criteria:**
- [ ] ClinicalAgent analyzes clinical metrics (HbA1c, blood pressure, BMI, cholesterol, glucose levels)
- [ ] Agent generates queries for baseline vs outcome comparisons
- [ ] Agent formats clinical data for KPI widgets, line charts, and tables
- [ ] Agent handles missing or incomplete clinical data gracefully
- [ ] Agent calculates clinical improvement percentages

**Tasks:**
- Design ClinicalAgent instructions and scope of analysis - 6h
- Create clinical metrics Pydantic schemas - 5h
- Implement ClinicalAgent using Agno framework - 10h
- Add clinical data query generation with Question-to-SQL coordinator - 6h
- Implement clinical metric calculations (improvements, trends) - 5h
- Write ClinicalAgent tests with sample clinical data - 6h
- Document clinical analysis patterns and metrics - 3h

---

### Story 3.2.2: UtilizationAgent for Healthcare Utilization
**Estimated:** 30 hours

**Acceptance Criteria:**
- [ ] UtilizationAgent analyzes ED visits, hospitalizations, readmissions, office visits
- [ ] Agent calculates utilization rates and trends over time
- [ ] Agent formats utilization data for bar charts, line charts, and KPIs
- [ ] Agent compares pre/post program utilization
- [ ] Agent identifies utilization hotspots and patterns

**Tasks:**
- Design UtilizationAgent instructions and analysis scope - 6h
- Create utilization metrics Pydantic schemas - 5h
- Implement UtilizationAgent using Agno framework - 10h
- Add utilization query generation for various event types - 6h
- Implement utilization rate calculations and trending - 5h
- Write UtilizationAgent tests with sample utilization data - 6h
- Document utilization analysis patterns - 3h

---

### Story 3.2.3: PricingAgent for ROI and Cost Analysis
**Estimated:** 30 hours

**Acceptance Criteria:**
- [ ] PricingAgent calculates ROI, total savings, cost avoidance, payback period
- [ ] Agent generates cost breakdown analyses (by category, by intervention)
- [ ] Agent supports multiple ROI scenarios (conservative, moderate, optimistic)
- [ ] Agent formats pricing data for ROI widgets, waterfall charts, and tables
- [ ] Agent handles different cost models and assumptions

**Tasks:**
- Design PricingAgent instructions and ROI methodology - 6h
- Create pricing and ROI metrics Pydantic schemas - 5h
- Implement PricingAgent using Agno framework - 10h
- Add ROI calculation logic with multi-scenario support - 8h
- Implement cost breakdown and savings calculations - 5h
- Write PricingAgent tests with various cost scenarios - 6h
- Document ROI calculation methodology and assumptions - 3h

---

### Story 3.2.4: PharmacyAgent for Medication Analysis
**Estimated:** 30 hours

**Acceptance Criteria:**
- [ ] PharmacyAgent analyzes medication adherence (MPR, PDC), drug costs, formulary compliance
- [ ] Agent calculates medication possession ratio (MPR) and proportion of days covered (PDC)
- [ ] Agent formats pharmacy data for adherence widgets, cost charts, and tables
- [ ] Agent handles different drug classes and therapeutic categories
- [ ] Agent identifies non-adherence patterns and cost drivers

**Tasks:**
- Design PharmacyAgent instructions and pharmacy metrics - 6h
- Create pharmacy metrics Pydantic schemas (MPR, PDC, costs) - 5h
- Implement PharmacyAgent using Agno framework - 10h
- Add pharmacy query generation for adherence and costs - 6h
- Implement adherence calculations (MPR, PDC) and cost analysis - 5h
- Write PharmacyAgent tests with sample pharmacy data - 6h
- Document pharmacy analysis patterns and formulas - 3h

---

## Epic 3.3: Value Proposition Data Generation

**Priority:** High
**Total Hours:** 60 hours
**Week:** Week 11

### Story 3.3.1: Value Prop Data Generation for Prospects
**Estimated:** 38 hours

**Acceptance Criteria:**
- [ ] Analytics Team generates data for all value prop sections
- [ ] Data pre-computed and stored in prospect_value_proposition_data table (JSONB)
- [ ] Data includes all metrics, charts, and text fields for each section
- [ ] Generation triggered automatically after prospect value prop ranking
- [ ] Generation job tracked with progress updates
- [ ] Data format matches frontend requirements

**Tasks:**
- Design prospect_value_proposition_data table schema with JSONB - 4h
- Create SQLAlchemy model with JSONB field for data storage - 3h
- Implement value prop data generation Celery task - 10h
- Orchestrate Analytics Team for value prop section generation - 8h
- Implement data formatting for each value prop section type - 6h
- Implement data storage in JSONB with compression - 5h
- Write value prop data generation integration tests - 6h
- Document value prop data format and schema - 3h

---

### Story 3.3.2: Value Prop Data Retrieval API
**Estimated:** 22 hours

**Acceptance Criteria:**
- [ ] GET /api/v1/prospects/{id}/value-proposition-data returns complete JSONB data
- [ ] Response includes all sections with populated metrics and visualizations
- [ ] Response time <10ms p95 (pre-computed data)
- [ ] Handles missing data gracefully with sensible defaults
- [ ] Supports caching for frequently accessed prospects

**Tasks:**
- Implement value prop data retrieval endpoint - 5h
- Add response caching with Redis (optional but recommended) - 4h
- Implement default value handling for missing data - 4h
- Add data freshness indicators (generated_at timestamp) - 3h
- Write API performance tests with load testing - 4h
- Document value prop data API and response format - 2h

---

## Epic 3.4: Dashboard Data Generation

**Priority:** Critical
**Total Hours:** 100 hours
**Week:** Week 12-13

### Story 3.4.1: Dashboard Widget Data Generation
**Estimated:** 57 hours

**Acceptance Criteria:**
- [ ] Analytics Team generates widget data for all approved templates
- [ ] Each widget's data_requirements translated to analytics questions and SQL queries
- [ ] Widget data formatted per widget type (kpi-card, bar-chart, line-chart, pie-chart, table, gauge, heatmap)
- [ ] Data stored in prospect_dashboard_data table (JSONB) per template
- [ ] Generation supports 5-10 templates × 8-12 widgets = 50-100 queries per prospect
- [ ] Parallel query execution for performance

**Tasks:**
- Design prospect_dashboard_data table schema with template_id foreign key - 4h
- Create SQLAlchemy model with JSONB for dashboard data - 3h
- Implement dashboard data generation Celery task - 12h
- Implement widget data_requirements parser and validator - 8h
- Orchestrate Analytics Team for widget query execution - 10h
- Implement widget data formatting for each widget type (Chart.js format) - 10h
- Add parallel query execution with connection pooling - 8h
- Write dashboard data generation integration tests - 8h
- Document dashboard data format and widget schemas - 4h

---

### Story 3.4.2: Dashboard Data Retrieval API
**Estimated:** 28 hours

**Acceptance Criteria:**
- [ ] GET /api/v1/prospects/{id}/dashboards/{template_id} returns complete dashboard JSONB
- [ ] Response includes all widget data formatted for Chart.js v4.5
- [ ] Response time <10ms p95 (pre-computed data)
- [ ] Supports multiple dashboards per prospect
- [ ] Handles missing widgets gracefully with empty states

**Tasks:**
- Implement dashboard data retrieval endpoint - 6h
- Add response caching with Redis for performance - 4h
- Implement Chart.js v4.5 data formatting - 6h
- Handle missing or failed widgets gracefully - 4h
- Add dashboard metadata (generation time, data freshness) - 3h
- Write dashboard API performance tests - 5h
- Document dashboard data API and response format - 3h

---

### Story 3.4.3: Dashboard List and Metadata API
**Estimated:** 19 hours

**Acceptance Criteria:**
- [ ] GET /api/v1/prospects/{id}/dashboards returns list of available dashboards with metadata
- [ ] Each entry includes template name, category, target_audience, widget_count, generation_status, data_freshness
- [ ] List sorted by category and target audience
- [ ] Filtering supported by category and audience
- [ ] Generation status indicates ready/generating/failed

**Tasks:**
- Implement dashboard list endpoint with metadata aggregation - 5h
- Add filtering by category and target audience - 4h
- Add generation status tracking (ready, generating, failed) - 4h
- Implement sorting and pagination - 3h
- Write dashboard list API tests - 4h
- Document dashboard list API and filtering options - 2h

---

## Phase Summary

**Total Hours:** 360 hours

**Epic Breakdown:**
- Epic 3.1: Analytics Team Architecture - 80h
- Epic 3.2: Specialized Analytics Agents - 120h
- Epic 3.3: Value Proposition Data Generation - 60h
- Epic 3.4: Dashboard Data Generation - 100h

**Week-by-Week:**
- Week 9: Analytics Team Architecture (80h)
- Week 10: Specialized Agents (60h)
- Week 11: Complete Agents + Value Prop Data (60h)
- Week 12: Dashboard Data Generation - Part 1 (60h)
- Week 13: Dashboard Data Generation - Part 2 (60h)
- Week 14: Testing, Optimization, Documentation (40h)

**Recommended Team:**
- 2 Backend Engineers (agent coordination, data generation)
- 1 Data Engineer (Clickhouse optimization, SQL queries)
- 0.5 AI/ML Engineer (agent refinement, prompt optimization)
- 0.5 QA Engineer (end-to-end testing, performance testing)

**Success Criteria:**
- [ ] Analytics Team generates value prop data in <5 minutes
- [ ] Dashboard data generation for 10 templates in <5 minutes
- [ ] Dashboard data retrieval <10ms p95
- [ ] Value prop data retrieval <10ms p95
- [ ] Question-to-SQL agent success rate >85%
- [ ] Clickhouse queries complete in <500ms p95
- [ ] Widget data correctly formatted for Chart.js
- [ ] End-to-end workflow tested: client → value prop → templates → prospect → analytics data
- [ ] All agents working in parallel coordination
- [ ] Data freshness indicators accurate
- [ ] Error handling graceful for failed queries
- [ ] Pre-computed data reduces frontend load significantly
