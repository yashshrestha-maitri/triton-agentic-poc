# ROI Model Research Agent Flow - Complete System Integration

**Version:** 3.0.0
**Last Updated:** 2025-12-11
**Status:** Production Architecture with Prompt Repository Integration
**Document Type:** Comprehensive Technical Specification

---


## Table of Contents

1. [Overview](#overview)
2. [Prompt Engineering Repository Integration](#prompt-engineering-repository-integration)
3. [13 ROI Model Types](#13-roi-model-types)
4. [Complete System Architecture](#complete-system-architecture)
5. [Agent Ecosystem with Prompts](#agent-ecosystem-with-prompts)
6. [End-to-End Workflows](#end-to-end-workflows)
7. [Database & Storage](#database--storage)
8. [Implementation Guide](#implementation-guide)
9. [Testing & Validation](#testing--validation)

---

## Overview

### Executive Summary

The **ROI Model Research Agent Flow** is a **three-repository system** that transforms healthcare vendor ROI narratives into quantitative, SQL-ready calculation models powering data-driven dashboards.

### Three-Repository Architecture

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'24px','fontFamily':'Monaco, Consolas, monospace'}}}%%
graph TB
    subgraph PromptRepo["mare-triton-research-prompts<br/>(Prompt Engineering)"]
        PR1[ROI Taxonomy<br/>13 Types]
        PR2[Classification Prompt<br/>roi_type.md]
        PR3[13 Model Generation Prompts<br/>B1-B13 .md files<br/>7,641 lines total]
        PR4[Base Schema<br/>_base_schema.md]
        PR5[Sample ROI Documents<br/>PDFs, Studies]
        PR6[Generated Model Examples<br/>30+ JSON files]
    end

    subgraph Backend["triton-agentic<br/>(Backend Execution)"]
        BE1[WebSearchAgent]
        BE2[DocumentAnalysisAgent]
        BE3[ROI Classification Engine]
        BE4[ROI Model Builder]
        BE5[Dashboard Generator]
        BE6[FastAPI Endpoints]
    end

    subgraph Frontend["mare-frontend<br/>(UI Presentation)"]
        FE1[ROI Model Viewer]
        FE2[Dashboard Templates]
        FE3[Mock Data<br/>53 models]
        FE4[Insights & Analytics]
    end

    PR2 --> BE3
    PR3 --> BE4
    PR4 --> BE4
    PR6 --> FE3

    BE3 --> BE4
    BE4 --> BE5
    BE5 --> BE6
    BE6 --> FE1

    PR5 -.->|Training Data| BE1
    PR5 -.->|Training Data| BE2

    style PromptRepo fill:#fff4e6,stroke:#d4a54a,stroke-width:4px
    style Backend fill:#e6f7ff,stroke:#4a90d4,stroke-width:4px
    style Frontend fill:#e1f5e1,stroke:#2d7a2d,stroke-width:4px
```

### System Components

| Repository | Role | Key Artifacts | Lines of Code |
|------------|------|---------------|---------------|
| **mare-triton-research-prompts** | Prompt Engineering & Testing | 14 prompts (7,641 lines)<br/>30+ generated models<br/>Sample ROI documents | 7,641 (prompts only) |
| **triton-agentic** | Backend Execution Engine | 4 agents<br/>FastAPI API<br/>PostgreSQL integration | ~5,000 Python |
| **mare-frontend** | UI Presentation Layer | React components<br/>ROI model viewers<br/>Dashboard templates | ~50,000 TypeScript |

---

## Prompt Engineering Repository Integration

### Repository Structure: mare-triton-research-prompts

```
mare-triton-research-prompts/
├── configuration/
│   └── roi_model_types_taxonomy.md        # Master taxonomy defining all 13 types
│
├── prompts/
│   ├── roi_type.md                        # Classification prompt (7,548 bytes)
│   └── roi_models/                        # Model generation prompts
│       ├── _base_schema.md                # Common JSON schema (22,396 bytes)
│       ├── B1_unit_price_optimization.md  # 14,448 bytes
│       ├── B2_site_of_care_shift.md       # 22,095 bytes
│       ├── B3_steerage.md                 # 16,712 bytes
│       ├── B4_payment_integrity.md        # 45,364 bytes ⭐ LARGEST
│       ├── B5_low_value_utilization.md    # 18,640 bytes
│       ├── B6_medical_management.md       # 18,426 bytes
│       ├── B7_episode_optimization.md     # 35,386 bytes
│       ├── B8_oon_mitigation.md           # 16,670 bytes
│       ├── B9_leakage_recapture.md        # 16,932 bytes
│       ├── B10_pharmacy_optimization.md   # 21,326 bytes
│       ├── B11_device_implant.md          # 17,389 bytes
│       ├── B12_admin_error.md             # 18,357 bytes
│       └── B13_incentive_steerage.md      # 17,811 bytes
│
├── sample_rois/                           # Training/test documents
│   ├── hinge_health_roi_calc_methodology.pdf
│   ├── cotiviti-payment-accuracy-solutions.pdf
│   ├── glycemic-control_JAMA2001.pdf
│   └── ... (15+ sample documents)
│
├── output/
│   ├── roi_types/                         # Classification results (JSON)
│   └── roi_models/                        # Generated models (30+ JSON files)
│       ├── hinge_health_roi_methodology_B7.json
│       ├── cotiviti_payment_accuracy_B4.json
│       ├── optum_predictive_analytics_B6.json
│       └── ... (27 more models)
│
├── README.md                              # Usage & testing guide
├── roi_research.md                        # Research strategy for finding more samples
└── b4_changes.md                          # B4 model restructuring plan
```

### Prompt Engineering Workflow

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'22px','fontFamily':'Monaco, Consolas, monospace'}}}%%
flowchart TD
    Start["**New Vendor ROI Document**<br/>PDF/Whitepaper"] --> Step1["**Step 1: Classify**<br/>Use roi_type.md prompt"]

    Step1 --> Class{"**Classification Result**"}
    Class -->|Type B7| Prompt7[Load B7_episode_optimization.md]
    Class -->|Type B4| Prompt4[Load B4_payment_integrity.md]
    Class -->|Type B10| Prompt10[Load B10_pharmacy_optimization.md]
    Class -->|Other| PromptX[Load appropriate prompt B1-B13]

    Prompt7 --> Step2["**Step 2: Generate Model**<br/>Apply prompt to document"]
    Prompt4 --> Step2
    Prompt10 --> Step2
    PromptX --> Step2

    Step2 --> JSON["**Generated JSON Model**"]
    JSON --> Val{"**Validation**"}

    Val -->|Pass| Output[Save to output/roi_models/]
    Val -->|Fail| Retry[Refine prompt or document]
    Retry --> Step2

    Output --> Frontend["Copy to mare-frontend<br/>mock data"]
    Output --> Test["Test with Claude Code CLI"]

    style Start fill:#fff4e6,stroke:#d4a54a,stroke-width:3px
    style Step1 fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
    style Step2 fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
    style JSON fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style Output fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
```

### Prompt Structure Breakdown

Each of the 13 model type prompts (B1-B13) follows this structure:

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
graph TD
    A[**Model Type Prompt**<br/>e.g., B7_episode_optimization.md] --> B[**Section 1: Instructions**<br/>~500 lines]
    A --> C[**Section 2: Domain Knowledge**<br/>~1000 lines]
    A --> D[**Section 3: Calculation Logic**<br/>~2000 lines]
    A --> E[**Section 4: Examples**<br/>~500 lines]

    B --> B1[Output format requirements]
    B --> B2[JSON schema validation]
    B --> B3[Model type-specific rules]

    C --> C1[Healthcare claims structures]
    C --> C2[ICD-10, CPT, DRG codes]
    C --> C3[Episode grouping methods]
    C --> C4[Industry benchmarks]

    D --> D1[Formula templates]
    D --> D2[SQL query patterns]
    D --> D3[Risk adjustment approaches]
    D --> D4[Configurable parameters]

    E --> E1[Sample inputs]
    E --> E2[Expected outputs]
    E --> E3[Edge case handling]

    style A fill:#fff4e6,stroke:#d4a54a,stroke-width:4px
    style B fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
    style C fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style D fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
    style E fill:#f0e6ff,stroke:#904ad4,stroke-width:3px
```

### Generated Model JSON Structure

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
graph LR
    A[**Generated ROI Model JSON**] --> B[model_metadata]
    A --> C[executive_summary]
    A --> D[data_requirements]
    A --> E[episode_definition]
    A --> F[population_identification]
    A --> G[baseline_methodology]
    A --> H[calculation_components]
    A --> I[sql_components]
    A --> J[output_metrics]
    A --> K[assumptions]
    A --> L[validation_rules]
    A --> M[confidence_factors]
    A --> N[configurable_parameters]
    A --> O[dashboard_templates]

    B --> B1[model_type_code: B1-B13]
    B --> B2[client_name]
    B --> B3[source_document]

    H --> H1[Formulas]
    H --> H2[Variables]
    H --> H3[Calculations]

    I --> I1[SQL Queries]
    I --> I2[Table Joins]
    I --> I3[Filters]

    N --> N1[time_parameters]
    N --> N2[rate_parameters]
    N --> N3[cost_parameters]
    N --> N4[threshold_parameters]

    style A fill:#fff4e6,stroke:#d4a54a,stroke-width:4px
    style H fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style I fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style N fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
```

---

## 13 ROI Model Types

### Complete Type Matrix

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'18px','fontFamily':'Monaco, Consolas, monospace'}}}%%
graph TB
    subgraph CostReduction["Cost Reduction Models (4 types)"]
        B1[**B1: Unit Price Optimization**<br/>Contract repricing, % of Medicare<br/>ROI: 150-300%<br/>Prompt: 14,448 bytes]
        B3[**B3: Provider Steering**<br/>Tiered networks, COEs<br/>ROI: 180-350%<br/>Prompt: 16,712 bytes]
        B10[**B10: Pharmacy Optimization**<br/>Formulary, rebates, adherence<br/>ROI: 250-400%<br/>Prompt: 21,326 bytes]
    end

    subgraph UtilMgmt["Utilization Management Models (5 types)"]
        B2[**B2: Site of Care Shift**<br/>HOPD→ASC, inpatient→obs<br/>ROI: 200-400%<br/>Prompt: 22,095 bytes]
        B5[**B5: Low-Value Utilization**<br/>Choosing Wisely, frequency caps<br/>ROI: 200-450%<br/>Prompt: 18,640 bytes]
        B6[**B6: Medical Management**<br/>Care coordination, readmissions<br/>ROI: 250-500%<br/>Prompt: 18,426 bytes]
        B7[**B7: Episode Optimization**<br/>Surgical pathways, MSK bundles<br/>ROI: 150-300%<br/>Prompt: 35,386 bytes]
        B9[**B9: Leakage Recapture**<br/>In-system retention, referrals<br/>ROI: 200-400%<br/>Prompt: 16,932 bytes]
    end

    subgraph AdminModels["Administrative Models (4 types)"]
        B4[**B4: Payment Integrity**<br/>Claim edits, bundling, DRG<br/>ROI: 500-1000%<br/>Prompt: 45,364 bytes ⭐]
        B8[**B8: OON Mitigation**<br/>Wrap networks, negotiations<br/>ROI: 300-600%<br/>Prompt: 16,670 bytes]
        B11[**B11: Supply Chain**<br/>Device/implant validation<br/>ROI: 400-800%<br/>Prompt: 17,389 bytes]
        B12[**B12: Admin Error**<br/>Duplicate payments, COB<br/>ROI: 600-1200%<br/>Prompt: 18,357 bytes]
    end

    subgraph BehaviorModels["Behavior Change Models (1 type)"]
        B13[**B13: Incentive Steerage**<br/>Member rewards, guarantees<br/>ROI: 100-250%<br/>Prompt: 17,811 bytes]
    end

    style CostReduction fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style UtilMgmt fill:#ffe6f0,stroke:#d44a90,stroke-width:3px
    style AdminModels fill:#e6ffe6,stroke:#4ad44a,stroke-width:3px
    style BehaviorModels fill:#f0e6ff,stroke:#904ad4,stroke-width:3px
    style B4 fill:#ffe6e6,stroke:#d44a4a,stroke-width:4px
```

### Type Classification Decision Tree

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
flowchart TD
    Start[**ROI Story Document**] --> Q1{Pharmacy/<br/>Drug focus?}

    Q1 -->|Yes| Q1a{Specialty drugs<br/>or adherence?}
    Q1a -->|Yes| B10[**B10: Pharmacy Optimization**<br/>21,326 byte prompt]
    Q1a -->|No| Q1b{Formulary or<br/>rebates?}
    Q1b -->|Yes| B10

    Q1 -->|No| Q2{Site of care<br/>keywords?}
    Q2 -->|Yes| Q2a{HOPD→ASC<br/>or IP→OBS?}
    Q2a -->|Yes| B2[**B2: Site of Care Shift**<br/>22,095 byte prompt]

    Q2 -->|No| Q3{Network/<br/>Contracting?}
    Q3 -->|Yes| Q3a{Unit price or<br/>rate negotiation?}
    Q3a -->|Yes| B1[**B1: Unit Price Optimization**<br/>14,448 byte prompt]
    Q3a -->|No| Q3b{Provider tiers<br/>or COE?}
    Q3b -->|Yes| B3[**B3: Provider Steering**<br/>16,712 byte prompt]

    Q3 -->|No| Q4{Utilization<br/>reduction?}
    Q4 -->|Yes| Q4a{Medical mgmt<br/>or care coord?}
    Q4a -->|Yes| B6[**B6: Medical Management**<br/>18,426 byte prompt]
    Q4a -->|No| Q4b{Episode or<br/>pathway?}
    Q4b -->|Yes| B7[**B7: Episode Optimization**<br/>35,386 byte prompt]
    Q4b -->|No| B5[**B5: Low-Value Utilization**<br/>18,640 byte prompt]

    Q4 -->|No| Q5{Administrative<br/>or payment?}
    Q5 -->|Yes| Q5a{Claims edits<br/>or bundling?}
    Q5a -->|Yes| B4[**B4: Payment Integrity**<br/>45,364 byte prompt ⭐]
    Q5a -->|No| Q5b{Duplicate payments<br/>or eligibility?}
    Q5b -->|Yes| B12[**B12: Admin Error**<br/>18,357 byte prompt]
    Q5b -->|No| B11[**B11: Supply Chain**<br/>17,389 byte prompt]

    Q5 -->|No| Q6{Out-of-network<br/>focus?}
    Q6 -->|Yes| B8[**B8: OON Mitigation**<br/>16,670 byte prompt]
    Q6 -->|No| Q7{Leakage or<br/>referrals?}
    Q7 -->|Yes| B9[**B9: Leakage Recapture**<br/>16,932 byte prompt]
    Q7 -->|No| Q8{Vendor incentive<br/>or rewards?}
    Q8 -->|Yes| B13[**B13: Incentive Steerage**<br/>17,811 byte prompt]
    Q8 -->|No| Default[**Closest match**<br/>confidence < 0.7]

    style Start fill:#fff4e6,stroke:#d4a54a,stroke-width:4px
    style B4 fill:#ffe6e6,stroke:#d44a4a,stroke-width:4px
    style B7 fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style B10 fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
```

---

## Complete System Architecture

### Full Stack Integration

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'18px','fontFamily':'Monaco, Consolas, monospace'}}}%%
graph TB
    subgraph PromptRepo["**mare-triton-research-prompts** (Prompt Engineering Repository)"]
        direction TB
        PR_Tax[ROI Taxonomy<br/>configuration/roi_model_types_taxonomy.md]
        PR_Class[Classification Prompt<br/>prompts/roi_type.md<br/>7,548 bytes]
        PR_Base[Base Schema<br/>prompts/roi_models/_base_schema.md<br/>22,396 bytes]

        subgraph PR_Prompts["Model Generation Prompts (7,641 lines total)"]
            PR_B1[B1: Unit Price<br/>14,448 bytes]
            PR_B2[B2: Site of Care<br/>22,095 bytes]
            PR_B3[B3: Steerage<br/>16,712 bytes]
            PR_B4[B4: Payment Integrity<br/>45,364 bytes ⭐]
            PR_B5[B5: Low-Value<br/>18,640 bytes]
            PR_B6[B6: Medical Mgmt<br/>18,426 bytes]
            PR_B7[B7: Episode Opt<br/>35,386 bytes]
            PR_B8[B8: OON<br/>16,670 bytes]
            PR_B9[B9: Leakage<br/>16,932 bytes]
            PR_B10[B10: Pharmacy<br/>21,326 bytes]
            PR_B11[B11: Supply Chain<br/>17,389 bytes]
            PR_B12[B12: Admin Error<br/>18,357 bytes]
            PR_B13[B13: Incentive<br/>17,811 bytes]
        end

        PR_Samples[Sample ROI Documents<br/>sample_rois/*.pdf<br/>15+ documents]
        PR_Output[Generated Models<br/>output/roi_models/*.json<br/>30+ models]
    end

    subgraph Backend["**triton-agentic** (Backend Execution Engine)"]
        direction TB
        BE_API[FastAPI Server<br/>app.py]

        subgraph BE_Agents["Research Agents"]
            BE_Web[WebSearchAgent<br/>agents/web_search_agent.py]
            BE_Doc[DocumentAnalysisAgent<br/>agents/document_analysis_agent.py]
            BE_Class[Classification Engine<br/>Uses roi_type.md]
            BE_Model[Model Builder<br/>Uses B1-B13 prompts]
        end

        BE_DB[(PostgreSQL<br/>Agent Memory)]
        BE_S3[(S3 Storage<br/>Documents)]

        subgraph BE_Services["Core Services"]
            BE_Val[Validation Service<br/>JSON + Pydantic + Business]
            BE_Dash[Dashboard Generator<br/>5-10 variations per model]
            BE_Query[Query Builder<br/>SQL generation]
        end
    end

    subgraph Frontend["**mare-frontend** (UI Presentation Layer)"]
        direction TB
        FE_UI[Next.js Application<br/>src/app/]

        subgraph FE_Pages["Key Pages"]
            FE_Client[Client Management<br/>/admin/client-management/]
            FE_ROI[ROI Model Viewer<br/>/admin/client-management/id/roi-models/modelId]
            FE_Insights[Insights & Analytics<br/>/prospects/id/reports/insights/]
            FE_Dash[Dashboard Templates<br/>src/components/dashboard-templates/]
        end

        FE_Mock[Mock Data<br/>src/data/mock-data/roi-models/*.json<br/>53 models]
        FE_Types[TypeScript Types<br/>src/types/roi.ts<br/>714 lines]
    end

    %% Prompt Repository Connections
    PR_Class -.->|Loaded by| BE_Class
    PR_B1 -.->|Loaded by| BE_Model
    PR_B2 -.->|Loaded by| BE_Model
    PR_B3 -.->|Loaded by| BE_Model
    PR_B4 -.->|Loaded by| BE_Model
    PR_B5 -.->|Loaded by| BE_Model
    PR_B6 -.->|Loaded by| BE_Model
    PR_B7 -.->|Loaded by| BE_Model
    PR_B8 -.->|Loaded by| BE_Model
    PR_B9 -.->|Loaded by| BE_Model
    PR_B10 -.->|Loaded by| BE_Model
    PR_B11 -.->|Loaded by| BE_Model
    PR_B12 -.->|Loaded by| BE_Model
    PR_B13 -.->|Loaded by| BE_Model
    PR_Base -.->|Referenced by| BE_Model
    PR_Output ==>|Copied to| FE_Mock

    %% Backend Flow
    BE_API --> BE_Web
    BE_API --> BE_Doc
    BE_Web --> BE_Class
    BE_Doc --> BE_Class
    BE_Class --> BE_Model
    BE_Model --> BE_Val
    BE_Val --> BE_Dash
    BE_Model --> BE_Query
    BE_Web --> BE_DB
    BE_Doc --> BE_S3

    %% Backend to Frontend
    BE_Dash ==>|JSON Models| FE_Mock
    BE_Query ==>|SQL Queries| FE_ROI

    %% Frontend Internal
    FE_Mock --> FE_ROI
    FE_ROI --> FE_Dash
    FE_Dash --> FE_Insights

    style PromptRepo fill:#fff4e6,stroke:#d4a54a,stroke-width:4px
    style Backend fill:#e6f7ff,stroke:#4a90d4,stroke-width:4px
    style Frontend fill:#e1f5e1,stroke:#2d7a2d,stroke-width:4px
    style PR_B4 fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
    style PR_Prompts fill:#ffe6cc,stroke:#d4a54a,stroke-width:2px
    style BE_Agents fill:#cce6ff,stroke:#4a90d4,stroke-width:2px
    style BE_Services fill:#cce6ff,stroke:#4a90d4,stroke-width:2px
    style FE_Pages fill:#ccf5cc,stroke:#2d7a2d,stroke-width:2px
```

---

## Agent Ecosystem with Prompts

### Research Agent Architecture

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
graph TB
    subgraph PromptLayer["Prompt Layer (mare-triton-research-prompts)"]
        P1[roi_type.md<br/>Classification Instructions]
        P2[B1-B13 Model Prompts<br/>Generation Instructions]
        P3[_base_schema.md<br/>Common Structure]
    end

    subgraph AgentLayer["Agent Layer (triton-agentic)"]
        A1[WebSearchAgent<br/>Company Research]
        A2[DocumentAnalysisAgent<br/>Collateral Extraction]
        A3[ROI Classification Agent<br/>Type Determination]
        A4[Model Builder Agent<br/>JSON Generation]
        A5[Dashboard Generator Agent<br/>Template Creation]
    end

    subgraph ToolLayer["Tool Layer"]
        T1[Google Search Tool<br/>Tavily/DuckDuckGo]
        T2[Web Scraper Tool<br/>HTML→Markdown]
        T3[S3 Document Reader<br/>PDF→Text]
        T4[Validation Tool<br/>JSON Schema Check]
        T5[SQL Generator Tool<br/>Query Templates]
    end

    subgraph StorageLayer["Storage Layer"]
        S1[(PostgreSQL<br/>Conversation Memory)]
        S2[(S3 Bucket<br/>Documents)]
        S3[(Redis Cache<br/>Temporary Results)]
    end

    %% Prompt to Agent connections
    P1 -.->|Instructs| A3
    P2 -.->|Instructs| A4
    P3 -.->|Defines| A4

    %% Agent to Tool connections
    A1 --> T1
    A1 --> T2
    A2 --> T3
    A3 --> T4
    A4 --> T4
    A4 --> T5
    A5 --> T5

    %% Agent to Storage connections
    A1 --> S1
    A2 --> S2
    A3 --> S3
    A4 --> S3

    %% Agent Flow
    A1 ==> A3
    A2 ==> A3
    A3 ==> A4
    A4 ==> A5

    style PromptLayer fill:#fff4e6,stroke:#d4a54a,stroke-width:4px
    style AgentLayer fill:#e6f7ff,stroke:#4a90d4,stroke-width:4px
    style ToolLayer fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
    style StorageLayer fill:#ffe6f0,stroke:#d44a90,stroke-width:3px
```

### Agent Lifecycle with Memory Management

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
sequenceDiagram
    participant API as FastAPI Endpoint
    participant Cache as Instruction Cache
    participant Prompt as Prompt Repository
    participant Agent as MareAgent Instance
    participant Memory as MemoryManager
    participant LLM as Claude/OpenAI
    participant DB as PostgreSQL

    Note over API,DB: Agent Creation Phase

    API->>Cache: Check for cached prompt
    alt Prompt not cached
        Cache->>Prompt: Load prompt file (B7_episode_optimization.md)
        Prompt-->>Cache: 35,386 bytes
        Cache->>Cache: Store in _instruction_cache
    end

    API->>Agent: create_agent(prompt, model)
    Agent->>Memory: Initialize MemoryManager(db)
    Memory->>DB: CREATE conversation session

    Note over API,DB: Execution Phase

    API->>Agent: run(message for ROI document analysis)
    Agent->>Memory: get_user_memories(user_id)
    Memory->>DB: SELECT * FROM user_memories WHERE user_id=?
    DB-->>Memory: [conversation history]
    Memory-->>Agent: Last 3 conversation turns

    Agent->>Agent: Build context = instructions + history + message
    Agent->>LLM: invoke(context)
    LLM-->>Agent: JSON response (10KB)

    Agent->>Memory: add_memory(user_msg, assistant_msg)
    Memory->>DB: INSERT INTO user_memories (user_id, message, response)

    Agent-->>API: Structured ROI Model JSON

    Note over API,DB: Cleanup Phase (❌ MISSING)

    API->>API: ❌ No cleanup() called
    Note over Agent,Memory: Agent + Memory persist in memory<br/>Potential leak: 2.4MB per agent

    style Agent fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
    style Memory fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
```

---

## End-to-End Workflows

### Complete ROI Model Generation Flow

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'18px','fontFamily':'Monaco, Consolas, monospace'}}}%%
flowchart TD
    Start[**User Uploads<br/>ROI Document**<br/>PDF/Whitepaper] --> API1[POST /api/research/classify]

    API1 --> Job1[Create Job<br/>job_classify_abc123]
    Job1 --> Agent1[**WebSearchAgent**<br/>Research company online]
    Job1 --> Agent2[**DocumentAnalysisAgent**<br/>Extract from uploaded PDF]

    Agent1 --> Load1[Load Classification Prompt<br/>mare-triton-research-prompts/<br/>prompts/roi_type.md<br/>7,548 bytes]
    Agent2 --> Load1

    Load1 --> Classify[**ROI Classification Agent**<br/>Analyze company + document]

    Classify --> Result1{**Classification Result**}
    Result1 -->|Type B7| SelectPrompt7[Load B7 Prompt<br/>prompts/roi_models/<br/>B7_episode_optimization.md<br/>35,386 bytes]
    Result1 -->|Type B4| SelectPrompt4[Load B4 Prompt<br/>prompts/roi_models/<br/>B4_payment_integrity.md<br/>45,364 bytes ⭐]
    Result1 -->|Type B10| SelectPrompt10[Load B10 Prompt<br/>prompts/roi_models/<br/>B10_pharmacy_optimization.md<br/>21,326 bytes]
    Result1 -->|Other| SelectPromptX[Load appropriate<br/>B1-B13 prompt]

    SelectPrompt7 --> BuildModel[**Model Builder Agent**<br/>Generate JSON structure]
    SelectPrompt4 --> BuildModel
    SelectPrompt10 --> BuildModel
    SelectPromptX --> BuildModel

    BuildModel --> Val1[**Validation Layer 1**<br/>JSON Schema Check]
    Val1 --> Val2{Valid<br/>JSON?}
    Val2 -->|No| Retry1[Retry with<br/>error feedback]
    Retry1 --> BuildModel

    Val2 -->|Yes| Val3[**Validation Layer 2**<br/>Pydantic Model Check]
    Val3 --> Val4{Valid<br/>Pydantic?}
    Val4 -->|No| Retry2[Retry with<br/>type errors]
    Retry2 --> BuildModel

    Val4 -->|Yes| Val5[**Validation Layer 3**<br/>Business Rules Check]
    Val5 --> Val6{Valid<br/>Business<br/>Rules?}
    Val6 -->|No| Retry3[Retry with<br/>business errors]
    Retry3 --> BuildModel

    Val6 -->|Yes| SaveModel[**Save ROI Model**<br/>PostgreSQL + S3]

    SaveModel --> GenDash[**Dashboard Generator Agent**<br/>Create 5-10 variations]

    GenDash --> Output1[**Employer Dashboard**<br/>Cost savings focus]
    GenDash --> Output2[**Health Plan Dashboard**<br/>Population health focus]
    GenDash --> Output3[**TPA Dashboard**<br/>Admin efficiency focus]
    GenDash --> Output4[**Broker Dashboard**<br/>ROI/payback focus]
    GenDash --> Output5[**Medical Director Dashboard**<br/>Clinical outcomes focus]

    Output1 --> Return[**Return to User**<br/>Model + Dashboards]
    Output2 --> Return
    Output3 --> Return
    Output4 --> Return
    Output5 --> Return

    Return --> Frontend[**Display in MARÉ Frontend**<br/>/admin/client-management/id/<br/>roi-models/modelId]

    style Start fill:#fff4e6,stroke:#d4a54a,stroke-width:4px
    style Load1 fill:#ffe6cc,stroke:#d4a54a,stroke-width:3px
    style SelectPrompt7 fill:#ffe6cc,stroke:#d4a54a,stroke-width:3px
    style SelectPrompt4 fill:#ffe6e6,stroke:#d44a4a,stroke-width:4px
    style SelectPrompt10 fill:#ffe6cc,stroke:#d4a54a,stroke-width:3px
    style BuildModel fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style GenDash fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
    style Frontend fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
```

### Prompt Loading & Caching Flow

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
sequenceDiagram
    participant Agent as Model Builder Agent
    participant Cache as Instruction Cache<br/>(In-Memory Dict)
    participant FS as File System<br/>(mare-triton-research-prompts)
    participant LLM as Claude Sonnet 4

    Note over Agent,LLM: First Request for B7 Model

    Agent->>Cache: Get prompt for B7
    Cache->>Cache: Check instruction cache for B7
    Cache-->>Agent: ❌ Not found

    Agent->>FS: Read prompts/roi_models/B7_episode_optimization.md
    FS-->>Agent: 35,386 bytes (full prompt)

    Agent->>Cache: Store B7 prompt in cache
    Cache->>Cache: Cache size: 35KB

    Agent->>LLM: Send prompt + ROI document
    Note over Agent,LLM: Context: 35KB prompt + 200KB document = 235KB
    LLM-->>Agent: Generated ROI Model JSON (50KB)

    Note over Agent,LLM: Second Request for B7 Model (same agent)

    Agent->>Cache: Get prompt for B7
    Cache-->>Agent: ✅ Found in cache (35KB)
    Note over Agent,Cache: No file I/O needed

    Agent->>LLM: Send cached prompt + new document
    LLM-->>Agent: Generated ROI Model JSON

    Note over Agent,LLM: Request for B4 Model (same agent)

    Agent->>Cache: Get prompt for B4
    Cache-->>Agent: ❌ Not found

    Agent->>FS: Read prompts/roi_models/B4_payment_integrity.md
    FS-->>Agent: 45,364 bytes ⭐ (largest prompt)

    Agent->>Cache: Store B4 prompt in cache
    Cache->>Cache: Cache size: 80KB (B7 + B4)
    Note over Cache: ⚠️ Cache grows indefinitely

    Agent->>LLM: Send prompt + document
    LLM-->>Agent: Generated ROI Model JSON

    style Cache fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
    style FS fill:#ffe6cc,stroke:#d4a54a,stroke-width:3px
```

---

## Database & Storage

### PostgreSQL Schema for ROI Models

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'18px','fontFamily':'Monaco, Consolas, monospace'}}}%%
erDiagram
    CLIENTS ||--o{ ROI_MODELS : has
    CLIENTS {
        uuid id PK
        string name
        string industry
        timestamp created_at
    }

    ROI_MODELS ||--o{ MODEL_VERSIONS : has
    ROI_MODELS {
        uuid id PK
        uuid client_id FK
        string model_type_code "B1-B13"
        string model_type_name
        jsonb model_data "Full JSON structure"
        string source_document
        string status "draft, approved, archived"
        timestamp created_at
        timestamp updated_at
    }

    MODEL_VERSIONS {
        uuid id PK
        uuid roi_model_id FK
        integer version_number
        jsonb model_data
        string changed_by
        timestamp created_at
    }

    ROI_MODELS ||--o{ DASHBOARD_TEMPLATES : generates
    DASHBOARD_TEMPLATES {
        uuid id PK
        uuid roi_model_id FK
        string template_name
        string target_audience "Employer, Health Plan, etc"
        jsonb template_config
        timestamp created_at
    }

    ROI_MODELS ||--o{ VALIDATION_LOGS : has
    VALIDATION_LOGS {
        uuid id PK
        uuid roi_model_id FK
        string validation_type "json, pydantic, business"
        boolean passed
        jsonb errors
        timestamp created_at
    }

    CLIENTS ||--o{ USER_MEMORIES : has
    USER_MEMORIES {
        uuid id PK
        uuid client_id FK
        string agent_name
        text user_message
        text assistant_response
        timestamp created_at
    }
```

### S3 Storage Structure

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
graph TD
    S3[S3 Bucket: triton-roi-data]

    S3 --> Clients[clients/]
    Clients --> C1[client-abc123/]
    C1 --> Docs[documents/]
    C1 --> Models[roi-models/]
    C1 --> Dash[dashboards/]

    Docs --> PDF1[roi-story.pdf]
    Docs --> PDF2[whitepaper.pdf]
    Docs --> MD1[sales-deck.md]

    Models --> JSON1[model_v1.json]
    Models --> JSON2[model_v2.json]
    Models --> SQL1[queries.sql]

    Dash --> T1[employer-dashboard.json]
    Dash --> T2[health-plan-dashboard.json]
    Dash --> T3[tpa-dashboard.json]

    S3 --> Prompts[prompts/]
    Prompts --> ClassPrompt[roi_type.md<br/>7,548 bytes]
    Prompts --> BaseSchema[_base_schema.md<br/>22,396 bytes]
    Prompts --> B1P[B1_unit_price.md<br/>14,448 bytes]
    Prompts --> B4P[B4_payment_integrity.md<br/>45,364 bytes ⭐]
    Prompts --> B7P[B7_episode_optimization.md<br/>35,386 bytes]
    Prompts --> More[... B2, B3, B5, B6, B8-B13]

    S3 --> Samples[sample-models/]
    Samples --> Ex1[hinge_health_B7.json]
    Samples --> Ex2[cotiviti_B4.json]
    Samples --> Ex3[optum_B6.json]

    style S3 fill:#fff4e6,stroke:#d4a54a,stroke-width:4px
    style Prompts fill:#ffe6cc,stroke:#d4a54a,stroke-width:3px
    style B4P fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
    style Samples fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
```

---

## Implementation Guide

### Phase 1: Set Up Prompt Repository Integration

#### Step 1.1: Clone Prompt Repository

```bash
cd /home/yashrajshres
git clone <repo-url> mare-triton-research-prompts
cd mare-triton-research-prompts

# Verify structure
ls -la prompts/roi_models/
# Should see:
# - _base_schema.md (22,396 bytes)
# - B1_unit_price_optimization.md (14,448 bytes)
# - B2_site_of_care_shift.md (22,095 bytes)
# - ... B3-B13 (7,641 lines total)
```

#### Step 1.2: Configure Prompt Loader in triton-agentic

```python
# triton-agentic/core/config/settings.py

from pathlib import Path

class Settings:
    # ... existing settings ...

    # Prompt repository path
    PROMPT_REPO_PATH = Path(__file__).parent.parent.parent.parent / "mare-triton-research-prompts"

    # Prompt file paths
    CLASSIFICATION_PROMPT_PATH = PROMPT_REPO_PATH / "prompts" / "roi_type.md"
    MODEL_PROMPTS_DIR = PROMPT_REPO_PATH / "prompts" / "roi_models"
    BASE_SCHEMA_PATH = MODEL_PROMPTS_DIR / "_base_schema.md"

    # Verify paths on startup
    def validate_prompt_paths(self):
        if not self.PROMPT_REPO_PATH.exists():
            raise FileNotFoundError(f"Prompt repository not found at {self.PROMPT_REPO_PATH}")
        if not self.CLASSIFICATION_PROMPT_PATH.exists():
            raise FileNotFoundError(f"Classification prompt not found")
        if not self.MODEL_PROMPTS_DIR.exists():
            raise FileNotFoundError(f"Model prompts directory not found")

config = Settings()
config.validate_prompt_paths()
```

#### Step 1.3: Implement Prompt Caching with Cleanup

```python
# triton-agentic/agents/base/base_agent.py

from functools import lru_cache
from pathlib import Path
from typing import Optional

class BaseAgentTemplate(ABC):
    """Abstract base class for agent templates with improved caching."""

    def __init__(self):
        """Initialize the agent template."""
        self._allowed_s3_paths = None
        self.template_dir = config.MODEL_PROMPTS_DIR
        # Use LRU cache instead of unbounded dict
        self._load_instruction_file = lru_cache(maxsize=32)(self._load_instruction_file_impl)

    def _load_instruction_file_impl(self, filename: str) -> str:
        """Load instruction file (cached implementation).

        Args:
            filename: Name of the file to load (relative to prompts directory)

        Returns:
            File contents as string
        """
        file_path = self.template_dir / filename
        if file_path.exists():
            logger.debug(f"Loading prompt file: {filename} ({file_path.stat().st_size} bytes)")
            return file_path.read_text()
        else:
            logger.warning(f"Prompt file not found: {file_path}")
            return ""

    def cleanup(self):
        """Clean up cached prompts."""
        if hasattr(self, '_load_instruction_file'):
            self._load_instruction_file.cache_clear()
            logger.debug("Cleared prompt cache")
```

### Phase 2: Implement ROI Classification Agent

```python
# triton-agentic/agents/roi_classification_agent.py

from agents.base.base_agent import BaseAgentTemplate, MareAgent
from core.config.settings import config
from core.monitoring.logger import get_logger

logger = get_logger(__name__)

class ROIClassificationAgentTemplate(BaseAgentTemplate):
    """Agent template for classifying ROI stories into 13 types."""

    def __init__(self):
        super().__init__()
        self.classification_prompt_path = config.CLASSIFICATION_PROMPT_PATH

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration."""
        return {
            "markdown": False,
            "add_history_to_context": True,
            "num_history_runs": 1,
        }

    def get_tools(self) -> List:
        """No tools needed for classification."""
        return []

    def get_instructions(self) -> str:
        """Load classification instructions from prompt repository."""
        if not self.classification_prompt_path.exists():
            raise FileNotFoundError(
                f"Classification prompt not found at {self.classification_prompt_path}"
            )

        prompt_text = self.classification_prompt_path.read_text()
        logger.info(
            f"Loaded classification prompt: {len(prompt_text)} characters, "
            f"{self.classification_prompt_path.stat().st_size} bytes"
        )

        return prompt_text

    def get_description(self) -> str:
        """Get agent description."""
        return (
            "ROI Classification Agent - Classifies healthcare ROI stories into "
            "1 of 13 distinct model types using mare-triton-research-prompts taxonomy"
        )

def create_roi_classification_agent(
    name: str = "ROIClassificationAgent",
    model: Any = None,
    **kwargs
) -> MareAgent:
    """Create ROI classification agent instance."""
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    template = ROIClassificationAgentTemplate()
    agent = template.create_agent(name=name, model=model, **kwargs)

    logger.info(f"Created {name} with classification prompt from repository")
    return agent
```

### Phase 3: Implement Model Builder Agent

```python
# triton-agentic/agents/roi_model_builder_agent.py

from agents.base.base_agent import BaseAgentTemplate, MareAgent
from core.config.settings import config
from core.monitoring.logger import get_logger

logger = get_logger(__name__)

class ROIModelBuilderAgentTemplate(BaseAgentTemplate):
    """Agent template for building ROI models from classified stories."""

    def __init__(self, model_type_code: str):
        """Initialize with specific model type.

        Args:
            model_type_code: One of B1-B13
        """
        super().__init__()
        self.model_type_code = model_type_code
        self.model_prompt_path = self._get_model_prompt_path(model_type_code)
        self.base_schema_path = config.BASE_SCHEMA_PATH

    def _get_model_prompt_path(self, model_type_code: str) -> Path:
        """Get prompt file path for model type."""
        prompt_map = {
            "B1": "B1_unit_price_optimization.md",
            "B2": "B2_site_of_care_shift.md",
            "B3": "B3_steerage.md",
            "B4": "B4_payment_integrity.md",
            "B5": "B5_low_value_utilization.md",
            "B6": "B6_medical_management.md",
            "B7": "B7_episode_optimization.md",
            "B8": "B8_oon_mitigation.md",
            "B9": "B9_leakage_recapture.md",
            "B10": "B10_pharmacy_optimization.md",
            "B11": "B11_device_implant.md",
            "B12": "B12_admin_error.md",
            "B13": "B13_incentive_steerage.md",
        }

        if model_type_code not in prompt_map:
            raise ValueError(f"Invalid model type code: {model_type_code}")

        filename = prompt_map[model_type_code]
        path = config.MODEL_PROMPTS_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"Model prompt not found: {path}")

        return path

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration."""
        return {
            "markdown": False,
            "add_history_to_context": True,
            "num_history_runs": 1,
        }

    def get_tools(self) -> List:
        """No tools needed for model building."""
        return []

    def get_instructions(self) -> str:
        """Load model-specific prompt from repository."""
        # Load base schema
        base_schema = self.base_schema_path.read_text()
        base_schema_size = self.base_schema_path.stat().st_size

        # Load model-specific prompt
        model_prompt = self.model_prompt_path.read_text()
        model_prompt_size = self.model_prompt_path.stat().st_size

        logger.info(
            f"Loaded prompts for {self.model_type_code}: "
            f"base schema ({base_schema_size} bytes) + "
            f"model prompt ({model_prompt_size} bytes) = "
            f"{base_schema_size + model_prompt_size} bytes total"
        )

        # Combine base schema + model-specific instructions
        combined_prompt = f"""
{base_schema}

---

{model_prompt}
"""

        return combined_prompt

    def get_description(self) -> str:
        """Get agent description."""
        return (
            f"ROI Model Builder Agent ({self.model_type_code}) - "
            f"Generates complete ROI model JSON using prompt from "
            f"mare-triton-research-prompts repository"
        )

def create_roi_model_builder_agent(
    model_type_code: str,
    name: str = None,
    model: Any = None,
    **kwargs
) -> MareAgent:
    """Create ROI model builder agent for specific type.

    Args:
        model_type_code: One of B1-B13
        name: Agent name (defaults to "ROIModelBuilderAgent_{type}")
        model: LLM model instance
        **kwargs: Additional agent parameters

    Returns:
        MareAgent instance configured for model building
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    if name is None:
        name = f"ROIModelBuilderAgent_{model_type_code}"

    template = ROIModelBuilderAgentTemplate(model_type_code=model_type_code)
    agent = template.create_agent(name=name, model=model, **kwargs)

    logger.info(
        f"Created {name} for {model_type_code} using prompt: "
        f"{template.model_prompt_path.name}"
    )
    return agent
```

### Phase 4: API Integration

```python
# triton-agentic/api/routes/roi_models.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from agents.roi_classification_agent import create_roi_classification_agent
from agents.roi_model_builder_agent import create_roi_model_builder_agent

router = APIRouter(prefix="/roi-models", tags=["roi_models"])

@router.post("/generate", status_code=202)
async def generate_roi_model(
    request: ROIModelGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate ROI model from story document.

    Process:
    1. Classify ROI story → determine model type (B1-B13)
    2. Load appropriate prompt from mare-triton-research-prompts
    3. Generate JSON model using Model Builder Agent
    4. Validate model (4 layers)
    5. Generate 5-10 dashboard variations

    Returns job ID for status tracking.
    """
    job_id = f"roi_model_{uuid.uuid4().hex[:12]}"

    # Create job record
    roi_model_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "request": request.dict(),
    }

    # Execute in background
    background_tasks.add_task(
        execute_roi_model_generation,
        job_id,
        request
    )

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "ROI model generation initiated"
    }

async def execute_roi_model_generation(
    job_id: str,
    request: ROIModelGenerationRequest
):
    """Execute ROI model generation workflow."""
    try:
        # Step 1: Classify ROI story
        logger.info(f"[{job_id}] Step 1: Classifying ROI story")
        classification_agent = create_roi_classification_agent()

        classification_message = f"""
Classify the following ROI story:

Company: {request.company_name}
Document: {request.roi_story_text or request.document_url}

Return JSON with model_type_code (B1-B13) and confidence score.
"""

        classification_result = classification_agent.run(classification_message)
        model_type_code = classification_result["model_type_code"]
        confidence = classification_result["confidence"]

        logger.info(
            f"[{job_id}] Classification complete: {model_type_code} "
            f"(confidence: {confidence})"
        )

        # Cleanup classification agent
        if hasattr(classification_agent, 'cleanup'):
            classification_agent.cleanup()
        del classification_agent

        # Step 2: Build ROI model
        logger.info(f"[{job_id}] Step 2: Building {model_type_code} model")
        model_builder = create_roi_model_builder_agent(
            model_type_code=model_type_code
        )

        model_message = f"""
Generate a complete ROI model for:

Company: {request.company_name}
Model Type: {model_type_code}
ROI Story: {request.roi_story_text}

Return JSON matching the schema defined in _base_schema.md.
"""

        roi_model = model_builder.run(model_message)

        logger.info(f"[{job_id}] Model generation complete")

        # Cleanup model builder agent
        if hasattr(model_builder, 'cleanup'):
            model_builder.cleanup()
        del model_builder

        # Step 3: Validate model
        logger.info(f"[{job_id}] Step 3: Validating model (4 layers)")
        validation_result = validate_roi_model(roi_model)

        if not validation_result["valid"]:
            raise ValueError(f"Model validation failed: {validation_result['errors']}")

        # Step 4: Save model
        logger.info(f"[{job_id}] Step 4: Saving model to database")
        saved_model_id = save_roi_model_to_db(roi_model, request.client_id)

        # Update job status
        roi_model_jobs[job_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "model_id": saved_model_id,
            "model_type_code": model_type_code,
            "confidence": confidence,
        })

        logger.info(f"[{job_id}] ROI model generation completed successfully")

    except Exception as e:
        logger.error(f"[{job_id}] ROI model generation failed: {e}", exc_info=True)
        roi_model_jobs[job_id].update({
            "status": "failed",
            "completed_at": datetime.utcnow(),
            "error": str(e),
        })
```

---

## Testing & Validation

### Prompt Repository Testing Workflow

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
flowchart TD
    Start[**New ROI Document**<br/>sample_rois/new_vendor.pdf] --> Test1[**Test 1: Classification**]

    Test1 --> CLI1[**Claude Code CLI**<br/>Run classification prompt<br/>on new vendor document]

    CLI1 --> Result1[**Classification Result**<br/>model_type: B7<br/>confidence: 0.89]

    Result1 --> Verify1{Correct<br/>Type?}
    Verify1 -->|No| Fix1[Update Classification Prompt<br/>prompts/roi_type.md]
    Fix1 --> Test1

    Verify1 -->|Yes| Test2[**Test 2: Model Generation**]

    Test2 --> CLI2[**Claude Code CLI**<br/>Run model generation prompt<br/>for B7 episode optimization<br/>on new vendor document]

    CLI2 --> Result2[**Generated Model JSON**<br/>50KB structure]

    Result2 --> Verify2{Valid<br/>JSON?}
    Verify2 -->|No| Fix2[Update Model Prompt<br/>prompts/roi_models/B7_episode_optimization.md]
    Fix2 --> Test2

    Verify2 -->|Yes| Verify3{Complete<br/>Fields?}
    Verify3 -->|No| Fix2

    Verify3 -->|Yes| Verify4{Realistic<br/>Values?}
    Verify4 -->|No| Fix2

    Verify4 -->|Yes| Save[**Save to output/**<br/>output/roi_models/<br/>new_vendor_B7.json]

    Save --> Copy[**Copy to Frontend**<br/>mare-frontend/src/data/<br/>mock-data/roi-models/<br/>new_vendor_B7.json]

    Copy --> Test3[**Test 3: Frontend Display**<br/>npm run dev<br/>Navigate to ROI model viewer]

    Test3 --> Verify5{Displays<br/>Correctly?}
    Verify5 -->|No| Debug[Debug frontend components]
    Debug --> Test3

    Verify5 -->|Yes| Done[**✅ Model Ready**<br/>Commit to all 3 repos]

    style Start fill:#fff4e6,stroke:#d4a54a,stroke-width:3px
    style CLI1 fill:#ffe6cc,stroke:#d4a54a,stroke-width:3px
    style CLI2 fill:#ffe6cc,stroke:#d4a54a,stroke-width:3px
    style Save fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style Copy fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
    style Done fill:#ccf5cc,stroke:#2d7a2d,stroke-width:4px
```

---

## Performance & Scalability

### Memory Management with Prompt Caching

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'18px','fontFamily':'Monaco, Consolas, monospace'}}}%%
graph TB
    subgraph Before["Before: Unbounded Cache"]
        B1[Agent 1: Load B7 prompt<br/>35KB]
        B2[Agent 2: Load B4 prompt<br/>45KB]
        B3[Agent 3: Load B10 prompt<br/>21KB]
        B4[Agent 4: Load B7 again<br/>Already cached]
        B5[Agent 5: Load B1 prompt<br/>14KB]

        B_Cache[**Memory Growth**<br/>35 + 45 + 21 + 14 = 115KB<br/>❌ Never freed]

        B1 --> B_Cache
        B2 --> B_Cache
        B3 --> B_Cache
        B5 --> B_Cache
    end

    subgraph After["After: LRU Cache (maxsize=32)"]
        A1[Agent 1: Load B7 prompt<br/>35KB]
        A2[Agent 2: Load B4 prompt<br/>45KB]
        A3[Agent 3: Load B10 prompt<br/>21KB]
        A4[Agent 4: Load B7 again<br/>Cache hit - 0 bytes]
        A5[Agent 5: Load B1 prompt<br/>14KB]
        A6[Agent 6: cleanup called]

        A_Cache[**Memory Managed**<br/>Max 32 prompts cached<br/>Automatic eviction<br/>✅ Manual cleanup available]

        A1 --> A_Cache
        A2 --> A_Cache
        A3 --> A_Cache
        A5 --> A_Cache
        A6 --> A_Free[Cache cleared<br/>Memory freed]
    end

    style Before fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
    style After fill:#e1f5e1,stroke:#2d7a2d,stroke-width:3px
    style B_Cache fill:#ffcccc,stroke:#d44a4a,stroke-width:3px
    style A_Cache fill:#ccf5cc,stroke:#2d7a2d,stroke-width:3px
```

---

## Additional Workflows & Diagrams

### Vendor Onboarding Complete Workflow

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'18px','fontFamily':'Monaco, Consolas, monospace'}}}%%
sequenceDiagram
    participant User as Sales Team
    participant UI as MARÉ Frontend
    participant API as FastAPI Backend
    participant WS as WebSearchAgent
    participant DA as DocumentAnalysisAgent
    participant RC as ROI Classification Agent
    participant MB as Model Builder Agent
    participant DB as PostgreSQL
    participant S3 as S3 Storage

    Note over User,S3: Phase 1: Vendor Discovery & Research

    User->>UI: Add new vendor prospect
    UI->>API: POST /api/prospects/create
    API->>DB: INSERT INTO prospects
    DB-->>API: prospect_id

    User->>UI: Upload vendor collateral PDF
    UI->>API: POST /api/prospects/documents/upload
    API->>S3: Store vendor_doc.pdf
    S3-->>API: document_url

    Note over User,S3: Phase 2: Automated Web Research

    API->>WS: Create WebSearchAgent
    activate WS
    WS->>WS: Load search tools
    API->>WS: run(Research vendor healthcare ROI)

    WS->>WS: Search Google for vendor
    WS->>WS: Extract company website
    WS->>WS: Find case studies
    WS->>WS: Locate ROI whitepapers

    WS->>DB: Store research findings
    WS-->>API: Research summary JSON
    deactivate WS

    Note over User,S3: Phase 3: Document Analysis

    API->>DA: Create DocumentAnalysisAgent
    activate DA
    DA->>S3: Fetch vendor_doc.pdf
    S3-->>DA: PDF content

    DA->>DA: Extract text with OCR
    DA->>DA: Identify ROI claims
    DA->>DA: Extract metrics
    DA->>DA: Find vendor promises

    DA->>DB: Store extracted data
    DA-->>API: Document analysis JSON
    deactivate DA

    Note over User,S3: Phase 4: ROI Model Classification

    API->>RC: Create ROI Classification Agent
    activate RC
    RC->>RC: Load roi_type.md prompt<br/>from mare-triton-research-prompts

    API->>RC: run(research_summary + document_analysis)

    RC->>RC: Analyze ROI mechanisms
    RC->>RC: Match to 13 model types
    RC->>RC: Calculate confidence scores

    RC-->>API: Classification result<br/>model_type: B7<br/>confidence: 0.91
    deactivate RC

    Note over User,S3: Phase 5: ROI Model Generation

    API->>MB: Create Model Builder Agent<br/>for type B7
    activate MB
    MB->>MB: Load B7_episode_optimization.md<br/>35,386 bytes
    MB->>MB: Load _base_schema.md<br/>22,396 bytes

    API->>MB: run(vendor_data + classification)

    MB->>MB: Generate model_metadata
    MB->>MB: Create calculation_components
    MB->>MB: Build SQL queries
    MB->>MB: Define configurable_parameters
    MB->>MB: Design dashboard_templates

    MB-->>API: Complete ROI Model JSON<br/>50KB structure
    deactivate MB

    Note over User,S3: Phase 6: Validation & Storage

    API->>API: Validate JSON schema
    API->>API: Validate Pydantic model
    API->>API: Validate business rules
    API->>API: Check data requirements

    API->>DB: INSERT INTO roi_models
    API->>S3: Store model JSON
    API->>DB: INSERT INTO validation_logs

    Note over User,S3: Phase 7: Dashboard Generation

    API->>API: Generate 5 dashboard variants
    API->>DB: INSERT INTO dashboard_templates

    API-->>UI: Model generation complete
    UI-->>User: Show ROI model viewer

    Note over User,S3: Total Time: 3-5 minutes per vendor
```

### Multi-Vendor Batch Processing Flow

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
flowchart TD
    Start[**User Action**<br/>Upload 10 vendor PDFs] --> Queue[**Job Queue**<br/>Create 10 batch jobs]

    Queue --> Parallel{**Parallel Processing**<br/>Max 3 concurrent}

    Parallel -->|Job 1| V1[**Vendor 1: Hinge Health**]
    Parallel -->|Job 2| V2[**Vendor 2: Cotiviti**]
    Parallel -->|Job 3| V3[**Vendor 3: Optum**]
    Parallel -->|Job 4-10| VX[**7 more vendors queued**]

    V1 --> WS1[WebSearch Agent]
    V2 --> WS2[WebSearch Agent]
    V3 --> WS3[WebSearch Agent]

    WS1 --> Class1[Classification: B7]
    WS2 --> Class2[Classification: B4]
    WS3 --> Class3[Classification: B6]

    Class1 --> Build1[Model Builder B7<br/>35KB prompt]
    Class2 --> Build2[Model Builder B4<br/>45KB prompt ⭐]
    Class3 --> Build3[Model Builder B6<br/>18KB prompt]

    Build1 --> Save1[(Save Model 1)]
    Build2 --> Save2[(Save Model 2)]
    Build3 --> Save3[(Save Model 3)]

    Save1 --> Complete1[✅ Job 1 Done<br/>3 min]
    Save2 --> Complete2[✅ Job 2 Done<br/>4 min]
    Save3 --> Complete3[✅ Job 3 Done<br/>2 min]

    Complete1 --> Next{**Queue Check**}
    Complete2 --> Next
    Complete3 --> Next

    Next -->|Jobs 4-10 remaining| V4[Process next 3 vendors]
    V4 --> WS1

    Next -->|All complete| Final[**Batch Complete**<br/>10 models generated<br/>Total time: 12-15 min]

    style Start fill:#fff4e6,stroke:#d4a54a,stroke-width:4px
    style Parallel fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style Build2 fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
    style Final fill:#e1f5e1,stroke:#2d7a2d,stroke-width:4px
```

### Dashboard Template Generation Sequence

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'18px','fontFamily':'Monaco, Consolas, monospace'}}}%%
sequenceDiagram
    participant MB as Model Builder Agent
    participant DG as Dashboard Generator
    participant TS as Template Service
    participant DB as PostgreSQL
    participant FE as Frontend

    Note over MB,FE: Input: Complete ROI Model JSON

    MB->>DG: generate_dashboards(roi_model)
    activate DG

    Note over DG: Analyze model type and audience

    DG->>DG: Extract key metrics
    DG->>DG: Identify target audiences

    Note over DG: Generate Employer Dashboard

    DG->>TS: create_template(Employer Dashboard)
    activate TS
    TS->>TS: Focus: Cost savings, payback period
    TS->>TS: Charts: Cost trend, ROI waterfall
    TS->>TS: KPIs: PMPM savings, annual savings
    TS-->>DG: employer_template.json
    deactivate TS

    Note over DG: Generate Health Plan Dashboard

    DG->>TS: create_template(Health Plan Dashboard)
    activate TS
    TS->>TS: Focus: Population health, quality
    TS->>TS: Charts: Risk stratification, outcomes
    TS->>TS: KPIs: Admits avoided, quality scores
    TS-->>DG: health_plan_template.json
    deactivate TS

    Note over DG: Generate TPA Dashboard

    DG->>TS: create_template(TPA Dashboard)
    activate TS
    TS->>TS: Focus: Admin efficiency, accuracy
    TS->>TS: Charts: Payment accuracy, error rates
    TS->>TS: KPIs: Claims processed, error savings
    TS-->>DG: tpa_template.json
    deactivate TS

    Note over DG: Generate Broker Dashboard

    DG->>TS: create_template(Broker Dashboard)
    activate TS
    TS->>TS: Focus: ROI, implementation ease
    TS->>TS: Charts: ROI timeline, payback curve
    TS->>TS: KPIs: ROI percentage, months to break-even
    TS-->>DG: broker_template.json
    deactivate TS

    Note over DG: Generate Medical Director Dashboard

    DG->>TS: create_template(Medical Director Dashboard)
    activate TS
    TS->>TS: Focus: Clinical outcomes, safety
    TS->>TS: Charts: Complication rates, readmissions
    TS->>TS: KPIs: Quality measures, safety metrics
    TS-->>DG: medical_director_template.json
    deactivate TS

    DG->>DB: INSERT 5 dashboard templates
    DG->>DG: Generate preview thumbnails

    DG-->>MB: 5 dashboards generated
    deactivate DG

    MB->>FE: Notify frontend: new templates available
    FE->>DB: FETCH dashboard templates
    DB-->>FE: 5 template JSONs
    FE->>FE: Render dashboard gallery

    Note over MB,FE: User can now select and customize dashboards
```

### Model Validation Four-Layer Architecture

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
flowchart TD
    Start[**Generated ROI Model JSON**<br/>From Model Builder Agent] --> Layer1[**Layer 1: JSON Schema Validation**]

    Layer1 --> Check1{Valid<br/>JSON?}
    Check1 -->|No| Error1[**JSON Parse Error**<br/>- Syntax errors<br/>- Invalid characters<br/>- Malformed structure]
    Error1 --> Retry1[Return error to agent<br/>with specific line numbers]
    Retry1 --> Start

    Check1 -->|Yes| Layer2[**Layer 2: Pydantic Model Validation**]

    Layer2 --> Check2{Valid<br/>Types?}
    Check2 -->|No| Error2[**Type Validation Error**<br/>- Wrong field types<br/>- Missing required fields<br/>- Extra fields not allowed]
    Error2 --> Retry2[Return error to agent<br/>with field-level details]
    Retry2 --> Start

    Check2 -->|Yes| Layer3[**Layer 3: Business Rules Validation**]

    Layer3 --> Rules[**Check Business Logic**]
    Rules --> Rule1[Calculation formulas valid?]
    Rules --> Rule2[SQL queries syntactically correct?]
    Rules --> Rule3[Parameters within realistic ranges?]
    Rules --> Rule4[Data requirements feasible?]
    Rules --> Rule5[Baseline methodology sound?]

    Rule1 --> Check3{All Rules<br/>Pass?}
    Rule2 --> Check3
    Rule3 --> Check3
    Rule4 --> Check3
    Rule5 --> Check3

    Check3 -->|No| Error3[**Business Rule Violation**<br/>- Invalid formula syntax<br/>- Unrealistic parameter values<br/>- Infeasible data requirements]
    Error3 --> Retry3[Return error to agent<br/>with business context]
    Retry3 --> Start

    Check3 -->|Yes| Layer4[**Layer 4: Domain Expert Review**]

    Layer4 --> Expert[**Healthcare ROI Specialist**]
    Expert --> Review1[Clinical accuracy?]
    Expert --> Review2[Industry benchmarks realistic?]
    Expert --> Review3[Savings calculations conservative?]
    Expert --> Review4[Risk adjustments appropriate?]

    Review1 --> Check4{Expert<br/>Approval?}
    Review2 --> Check4
    Review3 --> Check4
    Review4 --> Check4

    Check4 -->|No| Error4[**Domain Expert Feedback**<br/>- Clinical inaccuracies<br/>- Unrealistic benchmarks<br/>- Overly aggressive assumptions]
    Error4 --> Manual[Manual refinement required]

    Check4 -->|Yes| Success[**✅ Model Approved**<br/>Ready for production use]

    Success --> Save[(Save to Database)]
    Save --> Deploy[Deploy to Frontend]

    style Start fill:#fff4e6,stroke:#d4a54a,stroke-width:3px
    style Layer1 fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style Layer2 fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style Layer3 fill:#e6f7ff,stroke:#4a90d4,stroke-width:3px
    style Layer4 fill:#ffe6f0,stroke:#d44a90,stroke-width:3px
    style Success fill:#e1f5e1,stroke:#2d7a2d,stroke-width:4px
    style Error1 fill:#ffe6e6,stroke:#d44a4a,stroke-width:2px
    style Error2 fill:#ffe6e6,stroke:#d44a4a,stroke-width:2px
    style Error3 fill:#ffe6e6,stroke:#d44a4a,stroke-width:2px
    style Error4 fill:#ffcccc,stroke:#d44a4a,stroke-width:2px
```

### Real-Time Model Execution Sequence

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'18px','fontFamily':'Monaco, Consolas, monospace'}}}%%
sequenceDiagram
    participant User as End User
    participant FE as MARÉ Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Calc as Calculation Engine
    participant Claims as Claims Database

    Note over User,Claims: User selects ROI model to run

    User->>FE: Select Hinge Health B7 Model
    FE->>API: GET /api/roi-models/{model_id}
    API->>DB: SELECT model_data FROM roi_models
    DB-->>API: Complete model JSON

    User->>FE: Configure parameters<br/>baseline_period_months: 12<br/>target_population: MSK
    FE->>API: POST /api/roi-models/{model_id}/execute

    Note over API,Claims: Phase 1: Population Identification

    API->>Calc: Initialize calculation engine
    Calc->>Calc: Load model configuration
    Calc->>Claims: Execute population query

    activate Claims
    Note over Claims: SELECT member_id FROM medical_claims<br/>WHERE diagnosis IN (ICD10_MSK_CODES)<br/>AND service_date BETWEEN baseline_dates
    Claims-->>Calc: 2,847 members identified
    deactivate Claims

    Note over API,Claims: Phase 2: Baseline Calculation

    Calc->>Claims: Calculate baseline costs
    activate Claims
    Note over Claims: SELECT SUM(allowed_amount)<br/>FROM medical_claims<br/>WHERE member_id IN (population)<br/>GROUP BY member_id
    Claims-->>Calc: Baseline PMPM: $145.32
    deactivate Claims

    Note over API,Claims: Phase 3: Intervention Simulation

    Calc->>Calc: Apply intervention rates<br/>surgery_avoidance: 15%<br/>pt_substitution: 40%

    Calc->>Calc: Calculate projected costs
    Calc->>Calc: Cost per surgery: $28,500
    Calc->>Calc: Cost per PT: $850
    Calc->>Calc: Avoided surgeries: 427
    Calc->>Calc: Additional PT: 1,139

    Note over API,Claims: Phase 4: Savings Calculation

    Calc->>Calc: Gross savings calculation
    Note over Calc: Avoided surgery costs:<br/>427 × $28,500 = $12,169,500

    Calc->>Calc: Additional costs calculation
    Note over Calc: Additional PT costs:<br/>1,139 × $850 = $968,150

    Calc->>Calc: Net savings calculation
    Note over Calc: Net: $12,169,500 - $968,150<br/>= $11,201,350

    Note over API,Claims: Phase 5: Risk Adjustment

    Calc->>Calc: Apply adjustment factors
    Calc->>Calc: Selection bias: -20%
    Calc->>Calc: Regression to mean: -15%
    Calc->>Calc: Implementation lag: -10%

    Calc->>Calc: Adjusted net savings<br/>$11,201,350 × 0.55<br/>= $6,160,743

    Note over API,Claims: Phase 6: Metrics & Output

    Calc->>Calc: Calculate output metrics
    Calc->>Calc: PMPM savings: $179.84
    Calc->>Calc: ROI: 287%
    Calc->>Calc: Payback period: 4.2 months

    Calc->>DB: INSERT INTO calculation_results
    Calc-->>API: Complete results JSON

    API-->>FE: Return calculation results
    FE->>FE: Render dashboard
    FE->>FE: Display charts
    FE-->>User: Show interactive results

    Note over User,Claims: Total execution time: 2-3 seconds
```

### Error Handling & Retry Logic Flow

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'20px','fontFamily':'Monaco, Consolas, monospace'}}}%%
flowchart TD
    Start[**Agent.run called**<br/>Generate ROI model] --> Try1[**Attempt 1**<br/>Send prompt to LLM]

    Try1 --> Check1{Success?}

    Check1 -->|Yes| Validate1[Validate response]
    Validate1 --> Valid1{Valid<br/>JSON?}

    Valid1 -->|Yes| Success[**✅ Return Result**]

    Valid1 -->|No| Log1[Log validation error]
    Log1 --> Retry1{Retries < 3?}

    Check1 -->|No| Error1[**LLM Error**]
    Error1 --> ErrorType1{Error<br/>Type?}

    ErrorType1 -->|Rate Limit| Wait1[Wait with backoff<br/>2^attempt × 1s]
    Wait1 --> Retry1

    ErrorType1 -->|Timeout| Log2[Log timeout]
    Log2 --> Retry1

    ErrorType1 -->|Auth Error| Fatal1[**❌ Fatal Error**<br/>Invalid credentials]

    ErrorType1 -->|Context Length| Truncate1[Truncate input<br/>Remove history]
    Truncate1 --> Retry1

    Retry1 -->|Yes| Try2[**Attempt 2**<br/>Retry with error context]
    Retry1 -->|No| Failure[**❌ Max Retries**<br/>Return error to user]

    Try2 --> Check2{Success?}
    Check2 -->|Yes| Validate2[Validate response]
    Validate2 --> Valid2{Valid<br/>JSON?}
    Valid2 -->|Yes| Success
    Valid2 -->|No| Log3[Log validation error]
    Log3 --> Retry2{Retries < 3?}

    Check2 -->|No| Error2[**LLM Error**]
    Error2 --> ErrorType2{Error<br/>Type?}
    ErrorType2 -->|Rate Limit| Wait2[Wait with backoff<br/>2^2 × 1s = 4s]
    Wait2 --> Retry2
    ErrorType2 -->|Timeout| Retry2
    ErrorType2 -->|Auth Error| Fatal1
    ErrorType2 -->|Context Length| Truncate2[Truncate further]
    Truncate2 --> Retry2

    Retry2 -->|Yes| Try3[**Attempt 3**<br/>Final retry]
    Retry2 -->|No| Failure

    Try3 --> Check3{Success?}
    Check3 -->|Yes| Validate3[Validate response]
    Validate3 --> Valid3{Valid<br/>JSON?}
    Valid3 -->|Yes| Success
    Valid3 -->|No| Failure

    Check3 -->|No| Failure

    Failure --> Cleanup[Cleanup agent resources]
    Cleanup --> Notify[Notify user & log error]

    style Start fill:#fff4e6,stroke:#d4a54a,stroke-width:3px
    style Success fill:#e1f5e1,stroke:#2d7a2d,stroke-width:4px
    style Failure fill:#ffe6e6,stroke:#d44a4a,stroke-width:3px
    style Fatal1 fill:#ffcccc,stroke:#d44a4a,stroke-width:4px
    style Try1 fill:#e6f7ff,stroke:#4a90d4,stroke-width:2px
    style Try2 fill:#e6f7ff,stroke:#4a90d4,stroke-width:2px
    style Try3 fill:#e6f7ff,stroke:#4a90d4,stroke-width:2px
```

### Model Type Selection Intelligence

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#272822','primaryTextColor':'#F8F8F2','primaryBorderColor':'#75715E','lineColor':'#F8F8F2','secondaryColor':'#3E3D32','tertiaryColor':'#49483E','fontSize':'18px','fontFamily':'Monaco, Consolas, monospace'}}}%%
sequenceDiagram
    participant Doc as Vendor Document
    participant Extract as Text Extractor
    participant NLP as NLP Analyzer
    participant Class as Classification Agent
    participant Prompt as roi_type.md Prompt
    participant Logic as Decision Logic
    participant Result as Classification Result

    Note over Doc,Result: Input: Vendor ROI whitepaper

    Doc->>Extract: Parse PDF/HTML
    Extract->>Extract: OCR if needed
    Extract->>Extract: Extract plain text
    Extract-->>NLP: Full document text

    Note over NLP: Preprocessing & Feature Extraction

    NLP->>NLP: Tokenize sentences
    NLP->>NLP: Extract key phrases
    NLP->>NLP: Identify ROI keywords

    NLP->>NLP: Find keyword matches
    Note over NLP: Keywords found:<br/>- "episode of care" (8 times)<br/>- "surgery avoidance" (5 times)<br/>- "MSK pathway" (12 times)<br/>- "complications" (7 times)

    NLP->>NLP: Calculate keyword density
    NLP->>NLP: Extract ROI metrics
    NLP-->>Class: Preprocessed features

    Note over Class: LLM-Based Classification

    Class->>Prompt: Load classification instructions
    Prompt-->>Class: 7,548 byte prompt with:<br/>- 13 model type definitions<br/>- Keyword matching rules<br/>- Overlap resolution logic

    Class->>Class: Build LLM context
    Note over Class: Combine:<br/>prompt + document + features

    Class->>Class: Invoke Claude Sonnet 4
    Note over Class: LLM analyzes:<br/>1. Primary ROI mechanism<br/>2. Secondary value drivers<br/>3. Savings calculation type<br/>4. Target population

    Class->>Logic: Process LLM output

    Note over Logic: Decision Tree Traversal

    Logic->>Logic: Q1: Pharmacy focus?<br/>→ No (no drug keywords)
    Logic->>Logic: Q2: Site of care shift?<br/>→ No (no HOPD/ASC mention)
    Logic->>Logic: Q3: Utilization reduction?<br/>→ Yes (surgery avoidance)
    Logic->>Logic: Q4: Episode or pathway?<br/>→ Yes (episode 8x, pathway 12x)

    Logic->>Logic: Match to B7 Episode Optimization

    Note over Logic: Confidence Calculation

    Logic->>Logic: Keyword match score: 0.92
    Logic->>Logic: Mechanism alignment: 0.95
    Logic->>Logic: Exclusion check: 0.88
    Logic->>Logic: Overall confidence: 0.91

    Logic->>Result: Build classification result

    Result->>Result: model_type_code: B7
    Result->>Result: model_type_name: Episode optimization
    Result->>Result: confidence: 0.91
    Result->>Result: primary_mechanism: Standardized MSK pathways
    Result->>Result: key_phrases: episode, pathway, surgery avoidance

    Result-->>Class: Return classification

    Note over Doc,Result: Classification complete in 1-2 seconds
```

---

## Summary

### Three-Repository Integration

| Repository | Role | Key Integration Points |
|------------|------|------------------------|
| **mare-triton-research-prompts** | Prompt Engineering | Provides 7,641 lines of prompts<br/>Defines taxonomy<br/>Contains 30+ example models |
| **triton-agentic** | Execution Engine | Loads prompts dynamically<br/>Runs agents with prompts<br/>Generates new models |
| **mare-frontend** | Presentation Layer | Displays generated models<br/>Uses 53 mock models<br/>Matches prompt schema |

### Data Flow Summary

```
User uploads ROI document
  ↓
triton-agentic loads classification prompt from mare-triton-research-prompts/prompts/roi_type.md
  ↓
Classification Agent determines model type (B1-B13)
  ↓
triton-agentic loads model-specific prompt from mare-triton-research-prompts/prompts/roi_models/B{X}.md
  ↓
Model Builder Agent generates JSON using prompt
  ↓
Validation (4 layers)
  ↓
Save to PostgreSQL + S3
  ↓
Copy to mare-frontend/src/data/mock-data/roi-models/*.json
  ↓
Display in MARÉ UI
```

### Key Metrics

- **Prompt Library Size**: 7,641 lines across 14 files
- **Generated Models**: 30+ real-world examples in repository
- **Model Types**: 13 distinct healthcare ROI categories
- **Frontend Integration**: 53 models in mare-frontend mock data
- **Largest Prompt**: B4 Payment Integrity (45,364 bytes)
- **Average Prompt Size**: ~550 lines per model type

---

**END OF DOCUMENT**
