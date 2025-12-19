# Triton Platform - Complete System Flow

**Version:** 1.0.0
**Last Updated:** 2025-12-15
**Status:** Master Reference Document

---

## Executive Summary

The Triton Platform is an AI-powered healthcare ROI analysis system that transforms client value propositions and prospect data into data-driven dashboards and insights. The platform consists of three integrated engines:

- **ARGO Engine** - Intelligent data processing and enrichment
- **Triton Engine** - AI-powered research and analysis
- **MARE Application** - Frontend presentation and user interaction

This document provides a comprehensive overview of how all system components work together. For detailed technical specifications, see the linked documents below.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Six-Step Workflow Overview](#six-step-workflow-overview)
3. [ROI Model Integration](#roi-model-integration)
4. [Three-Repository Architecture](#three-repository-architecture)
5. [Quick Reference Guide](#quick-reference-guide)
6. [Detailed Documentation Links](#detailed-documentation-links)

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         TRITON PLATFORM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐ │
│  │    ARGO     │    │    TRITON    │    │       MARE       │ │
│  │   Engine    │───▶│    Engine    │───▶│   Application    │ │
│  │             │    │              │    │                  │ │
│  │ Data        │    │ AI Research  │    │ Frontend         │ │
│  │ Processing  │    │ & Analysis   │    │ Presentation     │ │
│  └─────────────┘    └──────────────┘    └──────────────────┘ │
│         │                   │                      │           │
│         ↓                   ↓                      ↓           │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐ │
│  │ Clickhouse  │    │  PostgreSQL  │    │  Next.js UI      │ │
│  │ Analytics   │    │  Structured  │    │  React           │ │
│  │ Data        │    │  Data        │    │  Components      │ │
│  └─────────────┘    └──────────────┘    └──────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Engine Responsibilities

#### ARGO Engine (Data Processing)
**Integration Point**: Step #3 - Prospect Data Upload & Processing

- Intelligent data analysis and mapping
- Field inference and standardization
- Data quality assessment (Data Grade)
- Healthcare analytics enrichment
- Output: Analytics-ready datasets in Clickhouse

**Key Characteristics**:
- Fully automated data processing
- Handles variability in source data formats
- Enriches with utilization metrics, quality measures, risk scores
- Human intervention only for Data Grade approval

**Reference**: [TRITON_PLATFORM_WORKFLOW.md - Step 3](#detailed-documentation-links)

---

#### Triton Engine (AI/LLM Component)
**Integration Points**: Steps #1, #2, #4, #5

Specialized agents for research and generation:

1. **Research & Alignment Agents** (Steps 1.2, 2.2-2.4)
   - Client value proposition research
   - Prospect company intelligence gathering
   - ROI Model classification (13 types)
   - Value proposition ranking

2. **ROI Model Builder Agent** (Step 1.2 - New Architecture)
   - Classifies ROI stories into 13 model types
   - Generates quantitative ROI models with variables and formulas
   - Uses prompt engineering repository (7,641 lines of prompts)
   - Enables mathematical ROI calculations

3. **Analytics Team Agents** (Steps 4-5)
   - Clinical Agent, Utilization Agent, Pricing Agent, Pharmacy Agent
   - Question-to-SQL Agent (coordinator)
   - Iterative data analysis from Clickhouse
   - Pre-computes dashboard and value prop insights

4. **Dashboard Template Generator** (Step 1.4)
   - Creates 5-10 dashboard variations
   - Customizes for target audiences
   - Generates from ROI Models (new) or value propositions (legacy)

**Key Innovation - ROI Model Architecture**:
- **Old**: Qualitative value propositions → Static templates
- **New**: ROI Stories → Quantitative models → Data-driven dashboards

**Reference**: [ROI_MODEL_RESEARCH_FLOW_UPDATED.md](#detailed-documentation-links)

---

#### MARE Application (Frontend)
**Integration Point**: Step #6 - Reports & Presentation

- Population Summary (real-time Clickhouse queries)
- ROI Analysis (pre-computed dashboard data from Postgres JSONB)
- Value Propositions (pre-computed insights from Postgres JSONB)
- Interactive data visualization
- Export capabilities (PNG, PDF, Copy)

**Key Characteristics**:
- Pure presentation layer (no Triton/ARGO logic)
- Fast performance via pre-computed data
- Single indexed queries (~10ms)

**Reference**: [TRITON_PLATFORM_WORKFLOW.md - Step 6](#detailed-documentation-links)

---

## Six-Step Workflow Overview

### Complete Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│  STEP 1: Client Management & Value Prop Setup (Triton)  │
├──────────────────────────────────────────────────────────┤
│  1.1: Client Information Capture                         │
│  1.2: Value Prop Derivation (Research/Collateral)       │
│       ├─ Mode A: Research-Based (Autonomous/Manual)     │
│       │   - WebSearchAgent: Web intelligence            │
│       │   - ROI Classification: 13 model types (NEW!)   │
│       │   - ROI Model Builder: Quantitative models      │
│       └─ Mode B: Collateral-Based (DocumentAnalysis)    │
│  1.3: Value Prop Review & Refinement (Iterative)        │
│  1.4: Dashboard Template Generation (5-10 variations)   │
│                                                          │
│  Output: Approved Value Prop/ROI Model + Templates      │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 2: Prospect Creation & Alignment (Triton)         │
├──────────────────────────────────────────────────────────┤
│  2.1: Prospect Creation & Initial Setup                 │
│  2.2: Prospect Company Research                         │
│       - WebSearchAgent: Google search & intel           │
│       - Extract classification (subsegment)             │
│  2.3: Prospect Value Metrics Identification             │
│  2.4: Value Prop Ranking & Alignment                    │
│       - Rank client value props for this prospect       │
│       - Match segment priorities                        │
│  2.5: Prospect Type → Dashboard Template Mapping        │
│  2.6: Manual Ranking Review (optional)                  │
│                                                          │
│  Output: Ranked Value Prop JSON + Prospect Type         │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 3: Prospect Data Upload & Processing (ARGO)       │
├──────────────────────────────────────────────────────────┤
│  3.1: Prospect Data Upload (claims, eligibility)        │
│  3.2: ARGO Data Analysis & Mapping                      │
│       - Examine file structure & types                  │
│       - Infer field meanings                            │
│       - Map to standardized schema                      │
│       - Generate Data Grade                             │
│  3.3: Data Grade Review & Approval                      │
│  3.4: Data Processing & Enrichment                      │
│       - Transform to standard layout                    │
│       - Run through analytics engine                    │
│       - Enrich with utilization & quality metrics       │
│  3.5: Output Data Model Generation                      │
│                                                          │
│  Output: Analytics-ready dataset in Clickhouse          │
└────────────────────┬─────────────────────────────────────┘
                     ↓
         ┌──────────────────────────────────────────┐
         │    PARALLEL PROCESSING (Steps 4 & 5)     │
         │    Triton Analytics Team                 │
         └──────────────┬───────────────────────────┘
                        ↓
         ┌──────────────┴──────────────────────────┐
         ↓                                         ↓
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ STEP 4: Value Prop Data Gen│   │ STEP 5: Dashboard Data Gen  │
│ (Triton Analytics Team)     │   │ (Triton Analytics Team)     │
├─────────────────────────────┤   ├─────────────────────────────┤
│ Analytics Team Agents:      │   │ Same Analytics Team:        │
│ • Clinical Agent            │   │ • Clinical Agent            │
│ • Utilization Agent         │   │ • Utilization Agent         │
│ • Pricing Agent             │   │ • Pricing Agent             │
│ • Pharmacy Agent            │   │ • Pharmacy Agent            │
│ • Question-to-SQL Agent     │   │ • Question-to-SQL Agent     │
│                             │   │                             │
│ Process:                    │   │ Process:                    │
│ • Analyze ranked value props│   │ • Analyze dashboard         │
│ • Query Clickhouse raw data │   │   templates                 │
│ • Iterative Q&A + SQL       │   │ • Query Clickhouse raw data │
│ • Format & store            │   │ • Iterative Q&A + SQL       │
│                             │   │ • Format & store            │
│ Output: Value prop insights │   │ Output: Dashboard widget    │
│ in Postgres JSONB           │   │ data in Postgres JSONB      │
└─────────────┬───────────────┘   └─────────────┬───────────────┘
              └──────────────┬────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: MARE Application - Prospect Reports            │
│    (No Triton/ARGO - Pure Frontend)                    │
├─────────────────────────────────────────────────────────┤
│ Three Main Views:                                       │
│                                                         │
│ 1. Population Summary (Real-time Clickhouse)           │
│    • Live queries for control totals                   │
│    • Population, financials, utilization               │
│                                                         │
│ 2. ROI Analysis (Postgres JSONB)                       │
│    • Pre-computed dashboard data (Step 5)              │
│    • Single indexed query (~10ms)                      │
│    • Carousel, export (Copy/PNG/PDF)                   │
│                                                         │
│ 3. Value Propositions (Postgres JSONB)                 │
│    • Pre-computed insights (Step 4)                    │
│    • Compare prospect vs client value props            │
│    • Sales team curation                               │
│                                                         │
│ Output: Interactive reports for sales presentation     │
└─────────────────────────────────────────────────────────┘
```

### Step-by-Step Summary

| Step | Name | Owner | Duration | Output |
|------|------|-------|----------|--------|
| **1** | Client Management & Value Prop Setup | Triton Engine | 5-10 min | Approved Value Prop/ROI Model + Dashboard Templates |
| **2** | Prospect Creation & Alignment | Triton Engine | 2-5 min | Ranked Value Prop JSON + Prospect Type |
| **3** | Prospect Data Upload & Processing | ARGO Engine | 5-15 min | Analytics-ready dataset in Clickhouse |
| **4** | Value Prop Data Generation | Triton Analytics Team | 2-5 min | Value prop insights in Postgres JSONB |
| **5** | ROI Dashboard Data Generation | Triton Analytics Team | 2-5 min | Dashboard widget data in Postgres JSONB |
| **6** | MARE Application Reports | MARE Frontend | Instant | Interactive reports for sales |

**Total Time: ~15-40 minutes per prospect**

---

## ROI Model Integration

### The Architectural Shift

The Triton Platform has evolved from qualitative value proposition analysis to **quantitative ROI model-driven dashboards**:

#### Old Architecture

```
Value Proposition (Text)
  ↓
Template Generator
  ↓
Static Dashboard Templates
```

**Limitations**:
- Qualitative descriptions, not calculations
- Hardcoded template structures
- No mathematical ROI formulas
- Static, not data-driven

---

#### New Architecture (ROI Model)

```
ROI Story Document (PDF/Markdown/SQL)
  ↓
ROI Classification Agent (13 types)
  ↓
ROI Model Builder (Variables + Formulas)
  ↓
Dashboard Generator (Data-driven)
  ↓
Live Dashboards (Real calculations)
```

**Benefits**:
- **Quantitative**: Mathematical ROI calculations
- **Dynamic**: Variables extracted from ROI stories
- **Flexible**: 13 distinct model types
- **Data-driven**: Uses prospect data for real calculations
- **Reusable**: ROI models work across prospects

---

### 13 ROI Model Types

ROI stories are classified into one of **13 distinct types**, each with specific variables, formulas, and data requirements:

| Code | Model Type | Category | Typical ROI Range |
|------|-----------|----------|-------------------|
| **B1** | Unit Price Optimization | Cost Reduction | 150-300% |
| **B2** | Site of Care Shift | Utilization | 200-400% |
| **B3** | Provider Steering | Cost Reduction | 180-350% |
| **B4** | Payment Integrity | Administrative | 500-1000% |
| **B5** | Low-Value Utilization Reduction | Utilization | 200-450% |
| **B6** | Medical Management | Utilization | 250-500% |
| **B7** | Episode Optimization | Utilization | 150-300% |
| **B8** | Out-of-Network Mitigation | Administrative | 300-600% |
| **B9** | Leakage Recapture | Utilization | 200-400% |
| **B10** | Pharmacy Optimization | Cost Reduction | 250-400% |
| **B11** | Supply Chain Validation | Administrative | 400-800% |
| **B12** | Admin Error Reduction | Administrative | 600-1200% |
| **B13** | Incentive Steerage | Behavior Change | 100-250% |

**Reference**: [ROI_MODEL_RESEARCH_FLOW_UPDATED.md - Section 2](#detailed-documentation-links)

---

### ROI Model Integration into Platform Workflow

ROI Models integrate into **Step 1.2** (Value Prop Derivation):

#### Step 1.2 with ROI Models

```
┌──────────────────────────────────────────────────────┐
│  Step 1.2: Value Prop Derivation (NEW: ROI Models)  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Mode A: Research-Based                             │
│  ┌────────────────────────────────────────────────┐ │
│  │ A1: Autonomous Research                        │ │
│  │   • WebSearchAgent: 15-25 web searches        │ │
│  │   • Extract company ROI claims                │ │
│  │   • ┌────────────────────────────────────┐   │ │
│  │   • │ ROI Classification Agent            │   │ │
│  │   • │  - Classify into 13 model types     │   │ │
│  │   • │  - Confidence scoring               │   │ │
│  │   • └────────────────────────────────────┘   │ │
│  │   • ┌────────────────────────────────────┐   │ │
│  │   • │ ROI Model Builder Agent             │   │ │
│  │   • │  - Load prompt (B1-B13)            │   │ │
│  │   • │  - Generate variables + formulas   │   │ │
│  │   • │  - Create SQL queries              │   │ │
│  │   • │  - Define configurable parameters  │   │ │
│  │   • └────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  OR                                                  │
│                                                      │
│  Mode B: Collateral-Based                           │
│  ┌────────────────────────────────────────────────┐ │
│  │ B1: Document Analysis                          │ │
│  │   • Upload ROI Story PDF                      │ │
│  │   • DocumentAnalysisAgent: Extract text       │ │
│  │   • Same ROI Classification + Model Builder   │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  Output:                                            │
│  • ROI Model JSON (50KB structure)                 │
│    - model_metadata                                │
│    - calculation_components (formulas)             │
│    - sql_components (queries)                      │
│    - configurable_parameters                       │
│    - dashboard_templates (5-10 variations)         │
└──────────────────────────────────────────────────────┘
```

#### What ROI Models Enable

1. **Step 1.4 - Dashboard Generation**:
   - Dashboards generated FROM ROI models
   - Data-driven widget configurations
   - Formula-based calculations

2. **Step 5 - Dashboard Data Generation**:
   - Execute ROI model formulas on prospect data
   - Populate widgets with calculated values
   - Real-time ROI calculations

3. **Step 6 - MARE Application**:
   - Display ROI models to users
   - Allow parameter adjustments
   - Recalculate dashboards on-demand

**Reference**: [ROI_MODEL_RESEARCH_FLOW_UPDATED.md - Complete Workflows](#detailed-documentation-links)

---

## Three-Repository Architecture

The ROI Model system spans **three repositories**:

### 1. mare-triton-research-prompts (Prompt Engineering)

**Location**: Separate repository
**Purpose**: Centralized prompt management and testing

```
mare-triton-research-prompts/
├── prompts/
│   ├── roi_type.md                    # Classification prompt (7,548 bytes)
│   └── roi_models/
│       ├── _base_schema.md            # Common schema (22,396 bytes)
│       ├── B1_unit_price_optimization.md  (14,448 bytes)
│       ├── B2_site_of_care_shift.md       (22,095 bytes)
│       ├── B3_steerage.md                 (16,712 bytes)
│       ├── B4_payment_integrity.md        (45,364 bytes) ⭐ LARGEST
│       ├── B5_low_value_utilization.md    (18,640 bytes)
│       ├── B6_medical_management.md       (18,426 bytes)
│       ├── B7_episode_optimization.md     (35,386 bytes)
│       ├── B8_oon_mitigation.md           (16,670 bytes)
│       ├── B9_leakage_recapture.md        (16,932 bytes)
│       ├── B10_pharmacy_optimization.md   (21,326 bytes)
│       ├── B11_device_implant.md          (17,389 bytes)
│       ├── B12_admin_error.md             (18,357 bytes)
│       └── B13_incentive_steerage.md      (17,811 bytes)
│
├── sample_rois/                       # Training documents
└── output/roi_models/                 # Generated models (30+)
```

**Total**: 7,641 lines of prompts across 14 files

---

### 2. triton-agentic (Backend Execution)

**Location**: This repository
**Purpose**: Execute agents using prompts from repository #1

```
triton-agentic/
├── agents/
│   ├── roi_classification_agent.py    # Loads roi_type.md
│   ├── roi_model_builder_agent.py     # Loads B1-B13 prompts
│   ├── web_search_agent.py            # Research company
│   └── document_analysis_agent.py     # Extract from PDFs
│
├── api/routes/
│   └── roi_models.py                  # API endpoints
│
└── core/config/
    └── settings.py                    # Prompt repository path
```

**Integration**:
- Agents dynamically load prompts from `mare-triton-research-prompts`
- Prompts cached using LRU cache (maxsize=32)
- Validation: 4-layer pipeline (JSON, Pydantic, Business, Domain)

---

### 3. mare-frontend (UI Presentation)

**Location**: Separate repository
**Purpose**: Display generated ROI models to users

```
mare-frontend/
├── src/data/mock-data/roi-models/     # 53 generated models
├── src/types/roi.ts                   # TypeScript types (714 lines)
└── src/app/.../roi-models/            # ROI model viewer pages
```

**Integration**:
- Generated models from `triton-agentic` → copied to `mare-frontend` mock data
- Frontend renders models using TypeScript types that match prompt schema

---

### Data Flow Across Repositories

```
1. User uploads ROI document
     ↓
2. triton-agentic loads classification prompt
     FROM mare-triton-research-prompts/prompts/roi_type.md
     ↓
3. Classification Agent determines model type (B1-B13)
     ↓
4. triton-agentic loads model-specific prompt
     FROM mare-triton-research-prompts/prompts/roi_models/B{X}.md
     ↓
5. Model Builder Agent generates JSON
     ↓
6. Validation (4 layers)
     ↓
7. Save to PostgreSQL + S3
     ↓
8. Copy to mare-frontend/src/data/mock-data/roi-models/*.json
     ↓
9. Display in MARÉ UI
```

**Reference**: [ROI_MODEL_RESEARCH_FLOW_UPDATED.md - Three-Repository Architecture](#detailed-documentation-links)

---

## Quick Reference Guide

### For New Developers

**Start Here**:
1. [TRITON_PLATFORM_WORKFLOW.md](./TRITON_PLATFORM_WORKFLOW.md) - Understand the 6-step workflow
2. [DATA_FLOW_EXPLANATION.md](./../features/DATA_FLOW_EXPLANATION.md) - Understand data storage
3. [ROI_MODEL_RESEARCH_FLOW_UPDATED.md](./ROI_MODEL_RESEARCH_FLOW_UPDATED.md) - Understand ROI models

**Quick Links**:
- [Setup Guide](./../operations/QUICKSTART.md)
- [API Documentation](./../operations/API_README.md)

---

### For Frontend Developers

**Integration Points**:
1. `/templates/{template_id}` - Get dashboard template structure
2. `/prospect-data/{prospect_id}` - Get generated widget data
3. `/roi-models/{model_id}` - Get ROI model details

**Key Documents**:
- [PROSPECT_DASHBOARD_SYSTEM.md](./../features/PROSPECT_DASHBOARD_SYSTEM.md)
- [MESSAGE_BROKER_IMPLEMENTATION.md](./../features/MESSAGE_BROKER_IMPLEMENTATION.md)
- [API_README.md](./../operations/API_README.md)

---

### For Backend Developers

**Key Systems**:
1. **Agents**: Research, Classification, Model Building
2. **Validation**: 4-layer pipeline
3. **Storage**: PostgreSQL (structured), Clickhouse (analytics), S3 (documents)

**Key Documents**:
- [RESEARCH_AGENT_FLOW.md](./RESEARCH_AGENT_FLOW.md)
- [ROI_MODEL_RESEARCH_FLOW_UPDATED.md](./ROI_MODEL_RESEARCH_FLOW_UPDATED.md)
- [PROSPECT_DATA_GENERATION.md](./../features/PROSPECT_DATA_GENERATION.md)

---

### For DevOps/Infrastructure

**Deployment**:
- [DOCKER_SETUP.md](./../operations/DOCKER_SETUP.md)
- [MONITORING_SETUP.md](./../operations/MONITORING_SETUP.md)

**Testing**:
- [MESSAGE_BROKER_TESTING.md](./../features/MESSAGE_BROKER_TESTING.md)
- [TESTING_AND_MONITORING_GUIDE.md](./../operations/TESTING_AND_MONITORING_GUIDE.md)

---

## Detailed Documentation Links

### Core Documentation

| Document | Purpose | Status |
|----------|---------|--------|
| [TRITON_PLATFORM_WORKFLOW.md](./TRITON_PLATFORM_WORKFLOW.md) | Complete 6-step platform workflow | ✅ Comprehensive |
| [ROI_MODEL_RESEARCH_FLOW_UPDATED.md](./ROI_MODEL_RESEARCH_FLOW_UPDATED.md) | ROI model system architecture (3 repos) | ✅ Most Recent (v3.0) |
| [RESEARCH_AGENT_FLOW.md](./RESEARCH_AGENT_FLOW.md) | Research agent detailed flows | ✅ Complete |
| [DATA_FLOW_EXPLANATION.md](./../features/DATA_FLOW_EXPLANATION.md) | Data storage and retrieval | ✅ Complete |

### API & Integration

| Document | Purpose | Status |
|----------|---------|--------|
| [API_README.md](./../operations/API_README.md) | REST API reference | ✅ Complete |
| [RESEARCH_API_GUIDE.md](./RESEARCH_API_GUIDE.md) | Research API endpoints | ✅ Complete |
| [PROSPECT_DASHBOARD_SYSTEM.md](./../features/PROSPECT_DASHBOARD_SYSTEM.md) | Frontend integration guide | ✅ Complete |
| [MESSAGE_BROKER_IMPLEMENTATION.md](./../features/MESSAGE_BROKER_IMPLEMENTATION.md) | Real-time events (no polling!) | ✅ Complete |

### Setup & Operations

| Document | Purpose | Status |
|----------|---------|--------|
| [QUICKSTART.md](./../operations/QUICKSTART.md) | 5-minute setup guide | ✅ Complete |
| [DOCKER_SETUP.md](./../operations/DOCKER_SETUP.md) | Container deployment | ✅ Complete |
| [MONITORING_SETUP.md](./../operations/MONITORING_SETUP.md) | Observability stack | ✅ Complete |
| [TESTING_AND_MONITORING_GUIDE.md](./../operations/TESTING_AND_MONITORING_GUIDE.md) | Testing best practices | ✅ Complete |

### Additional Documentation

- [WEB_SEARCH_QUICKSTART.md](./WEB_SEARCH_QUICKSTART.md) - Web search setup (2 min)
- [WEB_SEARCH_SETUP.md](./WEB_SEARCH_SETUP.md) - Detailed web search configuration
- [WEB_SEARCH_SOLUTIONS.md](./WEB_SEARCH_SOLUTIONS.md) - Search provider comparison

---

## System Metrics

### Performance Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| **Template Generation** | 3-5 min | 5-10 dashboard variations |
| **ROI Model Generation** | 3-5 min | Including classification + validation |
| **Prospect Data Processing** | 5-15 min | ARGO engine processing |
| **Dashboard Data Generation** | 2-5 min | Analytics Team pre-computation |
| **Dashboard Query** | ~10ms | Single Postgres JSONB query |
| **Population Summary** | 100-500ms | Real-time Clickhouse queries |

### Scale Metrics

| Component | Size | Notes |
|-----------|------|-------|
| **ROI Model Prompts** | 7,641 lines | 14 prompts across 13 types |
| **Generated ROI Models** | 53 models | In mare-frontend mock data |
| **Agent Cache Size** | 32 prompts | LRU cache with cleanup |
| **Dashboard Templates per Client** | 5-10 variations | Per ROI model/value prop |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0.0** | 2025-12-15 | Initial master reference document created |

---

## Contributing

When adding new features or documentation:

1. **Update this master reference** if it affects system architecture
2. **Update detailed docs** in their respective files
3. **Update `docs/README.md`** index
4. **Follow CLAUDE.md conventions** (all docs in `docs/` folder)

---

**For Questions or Updates**: Refer to [docs/README.md](./README.md) for complete documentation index.
