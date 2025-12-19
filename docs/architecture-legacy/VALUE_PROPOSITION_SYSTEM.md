# Value Proposition System Implementation Plan

**Focus Area:** Phase 0.2
**Duration:** 4 weeks (Weeks 5-8)
**Total Estimated Hours:** 480 hours

---

## Overview

Implement client value proposition derivation, iterative refinement, dashboard template generation, and prospect research with value prop ranking.

---

## Epic 2.1: Document Management & Storage

**Priority:** Critical
**Total Hours:** 60 hours
**Week:** Week 5

### Story 2.1.1: Document Upload and Management
**Estimated:** 32 hours

**Acceptance Criteria:**
- [ ] Document upload endpoint accepts PDF files (max 50MB)
- [ ] Documents stored in S3-compatible storage (AWS S3 or MinIO)
- [ ] Document metadata stored in PostgreSQL client_documents table
- [ ] Document types validated (collateral, roi_sheet, whitepaper, case_study, product_overview, other)
- [ ] Uploaded documents accessible via presigned download URLs
- [ ] Document listing endpoint with pagination

**Tasks:**
- Design client_documents table schema with metadata fields - 4h
- Create SQLAlchemy model for ClientDocument - 3h
- Implement document upload endpoint (POST /api/v1/clients/{id}/documents) - 6h
- Implement file validation (size limits, MIME types, malware scanning) - 4h
- Create document list endpoint with pagination (GET /api/v1/clients/{id}/documents) - 4h
- Implement presigned URL generation for secure downloads - 5h
- Write integration tests with MinIO for local testing - 6h
- Document upload API with examples - 3h

---

### Story 2.1.2: S3 Storage Abstraction
**Estimated:** 28 hours

**Acceptance Criteria:**
- [ ] ObjectStorage abstract interface defined
- [ ] S3Storage implementation working with AWS S3
- [ ] MinIOStorage implementation working for local development
- [ ] Configuration switches between providers via environment variable
- [ ] Upload, download, and URL generation methods working
- [ ] Error handling for storage failures

**Tasks:**
- Design ObjectStorage abstract base class interface - 4h
- Implement S3Storage class for AWS S3 - 6h
- Implement MinIOStorage class for local development - 5h
- Create storage factory with environment-based provider selection - 3h
- Implement error handling and retry logic for storage operations - 4h
- Write storage integration tests for both implementations - 6h
- Document storage abstraction pattern and configuration - 3h

---

## Epic 2.2: Research Team - Document Analysis & Web Research

**Priority:** Critical
**Total Hours:** 80 hours
**Week:** Week 5-6

### Story 2.2.1: DocumentAnalysisAgent
**Estimated:** 47 hours

**Acceptance Criteria:**
- [ ] DocumentAnalysisAgent extracts text and structured content from PDFs
- [ ] Agent returns structured extraction: company_info, product_features, clinical_outcomes, roi_metrics
- [ ] Multi-document analysis supported (batch processing)
- [ ] Extraction results stored temporarily for synthesis
- [ ] Agent retry logic handles parsing failures (max 3 attempts)
- [ ] PDF text extraction working with complex layouts

**Tasks:**
- Design DocumentAnalysisAgent instructions and prompts - 6h
- Create Pydantic schema for document extraction output - 4h
- Implement DocumentAnalysisAgent using Agno framework - 10h
- Integrate PDF text extraction library (PyPDF2 or pdfplumber) - 5h
- Implement batch document processing with parallel execution - 6h
- Add validation and retry logic for extraction failures - 5h
- Write agent integration tests with sample PDF documents - 8h
- Document agent behavior and output schema - 3h

---

### Story 2.2.2: WebSearchAgent for Autonomous Research
**Estimated:** 33 hours

**Acceptance Criteria:**
- [ ] WebSearchAgent searches Google/Bing for client information
- [ ] Agent accepts company name and optional industry hint
- [ ] Agent returns structured research: company_info, product_overview, competitive_position, key_metrics
- [ ] Search results filtered for relevance and recency
- [ ] Rate limiting respected for search API
- [ ] Multiple sources synthesized into coherent output

**Tasks:**
- Design WebSearchAgent instructions and research strategy - 5h
- Create Pydantic schema for research output - 4h
- Implement WebSearchAgent using Agno framework - 8h
- Integrate search API (Serper.dev, Tavily, or Google Custom Search) - 6h
- Implement relevance filtering and result ranking - 4h
- Add rate limiting and error handling for API calls - 4h
- Write agent integration tests with mocked search results - 6h
- Document web search setup and API key configuration - 3h

---

## Epic 2.3: Research Team - Synthesis & Validation

**Priority:** Critical
**Total Hours:** 100 hours
**Week:** Week 6

### Story 2.3.1: SynthesisAgent for Value Proposition Creation
**Estimated:** 60 hours

**Acceptance Criteria:**
- [ ] SynthesisAgent combines document extraction and/or web research into value proposition
- [ ] Agent uses Livongo JSON structure as template reference (Appendix B)
- [ ] Output matches ValuePropositionJSON schema with all required sections
- [ ] Additional user context incorporated into synthesis
- [ ] Output includes: executive_value_proposition, clinical_outcomes, roi_opportunities, competitive_positioning, implementation_readiness
- [ ] Agent handles missing data gracefully with placeholders

**Tasks:**
- Design SynthesisAgent instructions based on Livongo template structure - 8h
- Create comprehensive ValuePropositionJSON Pydantic schema (all sections) - 10h
- Implement SynthesisAgent using Agno framework - 12h
- Implement context aggregation (documents + research + user_input) - 6h
- Add section-by-section generation logic with prompts - 8h
- Implement output validation against Pydantic schema - 5h
- Write agent integration tests with various input combinations - 8h
- Document synthesis process and template structure - 3h

---

### Story 2.3.2: ValidationAgent for Output Quality
**Estimated:** 34 hours

**Acceptance Criteria:**
- [ ] ValidationAgent validates ValuePropositionJSON against Pydantic schema
- [ ] Validation errors returned to SynthesisAgent for correction
- [ ] Max 3 retry attempts enforced
- [ ] Successful validation stores result in PostgreSQL value_propositions table
- [ ] Validation errors logged with field-level details
- [ ] Business logic validation (completeness, coherence)

**Tasks:**
- Design ValidationAgent instructions and validation rules - 4h
- Implement ValidationAgent using Pydantic validation - 6h
- Create validation error feedback formatter for agent consumption - 5h
- Implement retry loop with incremental error feedback - 6h
- Add validation metrics and logging (success rate, retry counts) - 4h
- Write validation tests with intentionally invalid outputs - 6h
- Document validation patterns and error recovery - 3h

---

### Story 2.3.3: Value Proposition Derivation API
**Estimated:** 43 hours

**Acceptance Criteria:**
- [ ] POST /api/v1/clients/{id}/value-proposition/derive endpoint working
- [ ] Request supports mode: research (autonomous/manual) or collateral
- [ ] Async job created and job_id returned immediately (202 Accepted)
- [ ] Celery task orchestrates Research Team agents (DocumentAnalysis → WebSearch → Synthesis → Validation)
- [ ] Job status endpoint returns progress updates (GET /api/v1/clients/{id}/value-proposition/jobs/{job_id})
- [ ] Completed job returns full ValuePropositionJSON

**Tasks:**
- Create value proposition derivation request models - 6h
- Implement derivation endpoint with mode selection - 6h
- Implement request validation (mode, documents, prompts, context) - 5h
- Create Celery task for Research Team orchestration - 10h
- Implement progress tracking for multi-step process (stages, percent) - 6h
- Create job status retrieval endpoint - 4h
- Write end-to-end integration test (upload docs → derive → poll status) - 8h
- Document API usage with examples for both modes - 4h

---

## Epic 2.4: Value Proposition Review & Refinement

**Priority:** High
**Total Hours:** 80 hours
**Week:** Week 7

### Story 2.4.1: Review Interface Data
**Estimated:** 25 hours

**Acceptance Criteria:**
- [ ] GET /api/v1/clients/{id}/value-proposition/review returns sectioned value prop
- [ ] Each section has feedback_status (pending, approved, rejected)
- [ ] Feedback history tracked per section in database
- [ ] Current feedback round displayed
- [ ] Section-level metadata included (word count, completeness score)

**Tasks:**
- Design value_proposition_feedback table schema - 4h
- Create review response model with section breakdown - 6h
- Implement review endpoint with section extraction - 5h
- Add section status tracking to database - 4h
- Implement feedback history retrieval - 4h
- Write API tests for review endpoint - 4h
- Document review API and response structure - 2h

---

### Story 2.4.2: Feedback Submission and Refinement
**Estimated:** 52 hours

**Acceptance Criteria:**
- [ ] POST /api/v1/clients/{id}/value-proposition/review/feedback accepts section-level feedback
- [ ] Feedback types: approve, reject_remove, reject_change with rationale
- [ ] General feedback supported for cross-section improvements
- [ ] Async job created for refinement (Triton Refinement Agent)
- [ ] Refinement agent applies changes and returns updated value prop
- [ ] Version tracking for value propositions (v1, v2, v3...)
- [ ] Maximum 3 feedback rounds enforced

**Tasks:**
- Design feedback request model with section feedback array - 4h
- Create feedback submission endpoint - 6h
- Implement Triton Refinement Agent with change application logic - 12h
- Create Celery task for refinement orchestration - 8h
- Implement section removal logic (reject_remove) - 4h
- Implement section modification logic (reject_change) - 5h
- Implement version tracking for value propositions - 5h
- Write refinement integration tests with feedback scenarios - 6h
- Document refinement workflow and feedback format - 3h

---

### Story 2.4.3: Value Proposition Approval
**Estimated:** 19 hours

**Acceptance Criteria:**
- [ ] POST /api/v1/clients/{id}/value-proposition/approve marks value prop as approved
- [ ] Approved value prop becomes immutable (versioned)
- [ ] Approval timestamp and approver user_id recorded
- [ ] Only approved value props can be used for template generation
- [ ] Approval validation checks all sections reviewed

**Tasks:**
- Create approval endpoint - 4h
- Implement approval validation (all sections approved) - 4h
- Add approval metadata to value_propositions table - 3h
- Enforce approval requirement in template generation workflow - 3h
- Write approval tests with validation scenarios - 3h
- Document approval flow and requirements - 2h

---

## Epic 2.5: Dashboard Template Generation

**Priority:** Critical
**Total Hours:** 80 hours
**Week:** Week 7-8

### Story 2.5.1: Template Generator Agent
**Estimated:** 53 hours

**Acceptance Criteria:**
- [ ] Template Generator Agent creates 5-10 valid dashboard templates
- [ ] Templates vary by category (roi-focused, clinical-outcomes, utilization-analysis, pharmacy-outcomes, comparative-analysis)
- [ ] Templates vary by target audience (Health Plan, Employer, Provider, ACO)
- [ ] Each template has 6-12 widgets with valid 12-column grid positions
- [ ] Widgets include data_requirements (metrics, filters, time_range) and analytics_questions
- [ ] Templates stored in dashboard_templates table with JSONB

**Tasks:**
- Design Template Generator Agent instructions with widget types and layout rules - 10h
- Create DashboardTemplate Pydantic schema with data_requirements - 8h
- Implement Template Generator Agent using Agno framework - 12h
- Implement template validation (widget count, grid positions, category coverage, audience coverage) - 8h
- Add retry logic for invalid templates with error feedback - 5h
- Write template generation tests with value prop variations - 8h
- Document template structure and data_requirements format - 4h

---

### Story 2.5.2: Template Generation API
**Estimated:** 37 hours

**Acceptance Criteria:**
- [ ] POST /api/v1/clients/{id}/dashboard-templates/generate endpoint working
- [ ] Request requires approved value_proposition_id
- [ ] Async job created for template generation
- [ ] Generated templates stored in PostgreSQL dashboard_templates table
- [ ] Template list endpoint returns all templates (GET /api/v1/clients/{id}/dashboard-templates)
- [ ] Template detail endpoint returns single template (GET /api/v1/clients/{id}/dashboard-templates/{template_id})

**Tasks:**
- Create template generation endpoint with value prop requirement - 5h
- Implement value prop approval check before generation - 3h
- Create Celery task for template generation - 6h
- Implement template storage in database with JSONB - 5h
- Create template list endpoint with filtering (category, audience) - 5h
- Create template detail endpoint with full widget data - 4h
- Write end-to-end template generation test - 6h
- Document template generation API with examples - 3h

---

### Story 2.5.3: Template Curation
**Estimated:** 20 hours

**Acceptance Criteria:**
- [ ] Template status: generated, approved, removed
- [ ] User can approve individual templates (POST /api/v1/clients/{id}/dashboard-templates/{template_id}/approve)
- [ ] User can remove templates from list (DELETE /api/v1/clients/{id}/dashboard-templates/{template_id})
- [ ] Only approved templates used for prospect dashboard data generation
- [ ] Curation actions logged for audit trail

**Tasks:**
- Add template status field to dashboard_templates table - 3h
- Create template approval endpoint - 4h
- Create template removal endpoint (soft delete) - 4h
- Enforce approval requirement in analytics generation - 3h
- Add audit logging for template curation actions - 2h
- Write curation API tests - 4h
- Document curation workflow and requirements - 2h

---

## Epic 2.6: Prospect Research & Value Prop Ranking

**Priority:** High
**Total Hours:** 80 hours
**Week:** Week 8

### Story 2.6.1: Prospect CRUD Operations
**Estimated:** 32 hours

**Acceptance Criteria:**
- [ ] POST /api/v1/prospects creates prospect and triggers research
- [ ] GET /api/v1/prospects lists prospects with research status and pagination
- [ ] GET /api/v1/prospects/{id} returns prospect with ranked value props
- [ ] PATCH /api/v1/prospects/{id} updates prospect info
- [ ] DELETE /api/v1/prospects/{id} soft-deletes prospect
- [ ] Prospect status tracking (active, inactive, deleted)

**Tasks:**
- Design prospects table schema with metadata - 4h
- Create SQLAlchemy model for Prospect - 3h
- Implement prospect creation endpoint with validation - 5h
- Implement prospect list endpoint with filtering and pagination - 5h
- Implement prospect detail endpoint with value prop rankings - 5h
- Implement prospect update endpoint - 4h
- Implement prospect soft delete - 3h
- Write prospect CRUD API tests - 6h
- Document prospect API - 3h

---

### Story 2.6.2: Research & Alignment Agent for Prospect Enrichment
**Estimated:** 38 hours

**Acceptance Criteria:**
- [ ] Research & Alignment Agent researches prospect company (research mode)
- [ ] Agent extracts: company_size, industry, pain_points, strategic_priorities, recent_initiatives
- [ ] Research results stored in prospect_company_info table with JSONB
- [ ] Research triggered automatically on prospect creation
- [ ] Research job tracked with status updates

**Tasks:**
- Design prospect_company_info table schema with JSONB - 4h
- Create SQLAlchemy model for ProspectCompanyInfo - 3h
- Design Research & Alignment Agent instructions (research mode) - 6h
- Implement Research & Alignment Agent (research mode) using Agno - 10h
- Create Pydantic schema for company info output - 4h
- Implement automatic research trigger on prospect creation - 5h
- Write prospect research integration tests - 6h
- Document prospect research process and output - 3h

---

### Story 2.6.3: Value Proposition Ranking
**Estimated:** 35 hours

**Acceptance Criteria:**
- [ ] Research & Alignment Agent ranks value props by relevance to prospect (alignment mode)
- [ ] Ranking considers prospect pain points, strategic priorities, industry fit
- [ ] Ranked value props stored in prospect_value_propositions table
- [ ] Top 3 value props identified for each prospect
- [ ] Ranking scores and rationale provided
- [ ] Re-ranking supported when prospect info changes

**Tasks:**
- Design prospect_value_propositions table schema with rank and score - 4h
- Create SQLAlchemy model for ProspectValueProposition - 3h
- Design Research & Alignment Agent instructions (alignment mode) - 6h
- Implement Research & Alignment Agent (alignment mode) using Agno - 10h
- Create Pydantic schema for ranking output with rationale - 4h
- Implement ranking storage and retrieval - 5h
- Write ranking integration tests with various prospect scenarios - 6h
- Document ranking logic and scoring methodology - 3h

---

## Phase Summary

**Total Hours:** 480 hours

**Epic Breakdown:**
- Epic 2.1: Document Management & Storage - 60h
- Epic 2.2: Research Team - Document Analysis & Web Research - 80h
- Epic 2.3: Research Team - Synthesis & Validation - 100h
- Epic 2.4: Value Proposition Review & Refinement - 80h
- Epic 2.5: Dashboard Template Generation - 80h
- Epic 2.6: Prospect Research & Value Prop Ranking - 80h

**Week-by-Week:**
- Week 5: Document Management + Document Analysis (100h)
- Week 6: Web Research + Synthesis + Validation (120h)
- Week 7: Review/Refinement + Start Templates (120h)
- Week 8: Complete Templates + Prospects (140h)

**Recommended Team:**
- 2 Backend Engineers (agents, API endpoints)
- 0.5 AI/ML Engineer (prompt engineering, LLM optimization)
- 0.5 QA Engineer (agent testing, integration tests)

**Success Criteria:**
- [ ] Value proposition generated from collateral in <90s
- [ ] Value proposition generated from autonomous research in <120s
- [ ] Refinement cycle completes in <60s
- [ ] Template generation produces 5-10 valid templates
- [ ] Prospect research completes in <45s
- [ ] Value prop ranking accurate and coherent
- [ ] All Pydantic validations pass >70% on first attempt
- [ ] End-to-end workflow tested successfully
