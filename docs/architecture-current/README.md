# Current Architecture Documentation

**Status:** Active - In Production
**Version:** 3.0 (ROI Model Architecture)
**Last Updated:** 2025

---

## Overview

This folder contains documentation for the **current architecture** of the Triton platform, which is based on **ROI Model-driven dashboard generation**.

### Current Architecture Approach

```
ROI Story Document (PDF/Markdown/SQL)
  ↓
ROI Classification Agent (13 types: B1-B13)
  ↓
ROI Model Builder Agent (Variables + Formulas)
  ↓
Dashboard Generator (Data-driven widgets)
  ↓
Live Dashboards (Real ROI calculations)
```

**Characteristics:**
- **Quantitative Models**: Mathematical ROI calculations with variables and formulas
- **13 Model Types**: B1-B13 specialized types (Unit Price, Site of Care, Payment Integrity, etc.)
- **Data-Driven**: Dashboards populated from real prospect data via SQL queries
- **Dynamic Templates**: Widgets configured based on ROI model specifications
- **Automated Analysis**: AI-powered research, classification, and model building

---

## 🎯 Start Here

### For New Developers

**Read in this order:**

1. **[TRITON_COMPLETE_FLOW.md](./TRITON_COMPLETE_FLOW.md)** ⭐ - **START HERE**
   - Master reference document
   - Complete system architecture (ARGO + Triton + MARE)
   - 6-step workflow overview
   - Quick reference guide with links

2. **[TRITON_PLATFORM_WORKFLOW.md](./TRITON_PLATFORM_WORKFLOW.md)** - Detailed 6-step workflow
   - Step 1: Client Management & Value Prop Setup
   - Step 2: Prospect Creation & Alignment
   - Step 3: Prospect Data Upload & Processing (ARGO)
   - Step 4-5: Data Generation (Analytics Team)
   - Step 6: MARE Application (Frontend)

3. **[ROI_MODEL_RESEARCH_FLOW_UPDATED.md](./ROI_MODEL_RESEARCH_FLOW_UPDATED.md)** - ROI Model architecture v3.0
   - Three-repository integration
   - 13 ROI Model Types (B1-B13)
   - Prompt engineering system (7,641 lines)
   - Complete workflows and validation

---

## 📚 Documentation Files

### Core Architecture

| File | Purpose | Priority |
|------|---------|----------|
| [TRITON_COMPLETE_FLOW.md](./TRITON_COMPLETE_FLOW.md) | Master reference document | ⭐⭐⭐ |
| [TRITON_PLATFORM_WORKFLOW.md](./TRITON_PLATFORM_WORKFLOW.md) | 6-step platform workflow | ⭐⭐⭐ |
| [ROI_MODEL_RESEARCH_FLOW_UPDATED.md](./ROI_MODEL_RESEARCH_FLOW_UPDATED.md) | ROI model architecture v3.0 | ⭐⭐⭐ |

### ROI Model System

| File | Purpose | Priority |
|------|---------|----------|
| [ROI_INTEGRATION_GUIDE.md](./ROI_INTEGRATION_GUIDE.md) | ROI model integration guide | ⭐⭐ |

### Research Agents

| File | Purpose | Priority |
|------|---------|----------|
| [RESEARCH_AGENT_FLOW.md](./RESEARCH_AGENT_FLOW.md) | WebSearchAgent + DocumentAnalysisAgent flows | ⭐⭐⭐ |
| [RESEARCH_API_GUIDE.md](./RESEARCH_API_GUIDE.md) | Research API endpoint reference | ⭐⭐ |
| [RESEARCH_API_IMPLEMENTATION_COMPLETE.md](./RESEARCH_API_IMPLEMENTATION_COMPLETE.md) | Implementation status | ⭐ |
| [RESEARCH_AGENT_TEST_REPORT.md](./RESEARCH_AGENT_TEST_REPORT.md) | Agent testing results | ⭐ |
| [RESEARCH_API_TESTING_GUIDE.md](./RESEARCH_API_TESTING_GUIDE.md) | Testing procedures | ⭐ |

### Web Search Implementation

| File | Purpose | Priority |
|------|---------|----------|
| [WEB_SEARCH_QUICKSTART.md](./WEB_SEARCH_QUICKSTART.md) | Quick 2-minute setup guide | ⭐⭐ |
| [WEB_SEARCH_SETUP.md](./WEB_SEARCH_SETUP.md) | Detailed setup guide | ⭐ |
| [WEB_SEARCH_IMPLEMENTATION_SUMMARY.md](./WEB_SEARCH_IMPLEMENTATION_SUMMARY.md) | Implementation summary | ⭐ |
| [WEB_SEARCH_SOLUTIONS.md](./WEB_SEARCH_SOLUTIONS.md) | Provider comparison guide | ⭐ |

---

## 🏗️ System Architecture

### Three-Engine Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TRITON PLATFORM                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────┐   ┌────────────┐   ┌────────────────┐ │
│  │   ARGO     │   │  TRITON    │   │     MARE       │ │
│  │  Engine    │──▶│  Engine    │──▶│  Application   │ │
│  │            │   │            │   │                │ │
│  │ Data       │   │ AI/LLM     │   │ Frontend       │ │
│  │ Processing │   │ Research   │   │ Presentation   │ │
│  └────────────┘   └────────────┘   └────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 13 ROI Model Types

| Code | Model Type | Category | Typical ROI |
|------|-----------|----------|-------------|
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

---

## 🔄 6-Step Workflow

| Step | Name | Owner | Duration | Output |
|------|------|-------|----------|--------|
| **1** | Client Management & Value Prop Setup | Triton | 5-10 min | ROI Model + Templates |
| **2** | Prospect Creation & Alignment | Triton | 2-5 min | Ranked Value Props |
| **3** | Prospect Data Upload & Processing | ARGO | 5-15 min | Analytics Dataset |
| **4** | Value Prop Data Generation | Triton Analytics | 2-5 min | Value Prop Insights |
| **5** | ROI Dashboard Data Generation | Triton Analytics | 2-5 min | Dashboard Data |
| **6** | MARE Application Reports | MARE | Instant | Interactive Reports |

**Total Time:** ~15-40 minutes per prospect

---

## 🔑 Key Concepts

### ROI Models vs Value Propositions

| Aspect | Old (Value Props) | New (ROI Models) |
|--------|------------------|------------------|
| **Type** | Qualitative text | Quantitative math |
| **Templates** | Hardcoded | Data-driven |
| **Calculations** | None | Formulas + variables |
| **Flexibility** | Static | 13 distinct types |
| **Data Integration** | Manual | Automated SQL |

### Research Agents

1. **WebSearchAgent**: Autonomous web research (15-25 searches)
   - Google search via DuckDuckGo/Tavily
   - Company intelligence gathering
   - ROI claim extraction

2. **DocumentAnalysisAgent**: ROI Story document analysis
   - PDF/DOCX/TXT support
   - S3 document reading
   - Variable and formula extraction

---

## 🎓 Learning Paths

### Backend Developer Path

1. Read [TRITON_COMPLETE_FLOW.md](./TRITON_COMPLETE_FLOW.md) - System overview
2. Read [TRITON_PLATFORM_WORKFLOW.md](./TRITON_PLATFORM_WORKFLOW.md) - Detailed workflow
3. Read [ROI_MODEL_RESEARCH_FLOW_UPDATED.md](./ROI_MODEL_RESEARCH_FLOW_UPDATED.md) - ROI system
4. Read [RESEARCH_AGENT_FLOW.md](./RESEARCH_AGENT_FLOW.md) - Agent implementation

### Frontend Developer Path

1. Read [TRITON_COMPLETE_FLOW.md](./TRITON_COMPLETE_FLOW.md) - System overview
2. Read [TRITON_PLATFORM_WORKFLOW.md](./TRITON_PLATFORM_WORKFLOW.md) - Step 6 (MARE)
3. See [../features/](../features/) for data models and APIs

### DevOps Path

1. Read [TRITON_COMPLETE_FLOW.md](./TRITON_COMPLETE_FLOW.md) - System overview
2. See [../operations/](../operations/) for deployment guides

---

## 📊 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Template Generation | 3-5 min | 5-10 dashboard variations |
| ROI Model Generation | 3-5 min | Classification + validation |
| Research Searches | 15-25 | Autonomous mode |
| Dashboard Query | ~10ms | Single Postgres JSONB query |

---

## 🔗 Related Documentation

- **Features**: [../features/README.md](../features/README.md)
- **Operations**: [../operations/README.md](../operations/README.md)
- **Legacy Architecture**: [../architecture-legacy/README.md](../architecture-legacy/README.md)
- **Main Index**: [../README.md](../README.md)

---

**For Questions**: See [TRITON_COMPLETE_FLOW.md](./TRITON_COMPLETE_FLOW.md) for comprehensive overview
