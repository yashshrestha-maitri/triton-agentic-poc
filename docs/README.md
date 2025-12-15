# Triton Agentic Documentation

Complete documentation for the Triton Agentic dashboard template generation system.

---

## 📚 Documentation Index

### Platform Overview

**⭐ START HERE for complete system understanding**

- **[TRITON_COMPLETE_FLOW.md](./TRITON_COMPLETE_FLOW.md)** - **Master Reference Document** ⭐
  - Complete system architecture (ARGO + Triton + MARE)
  - 6-step workflow overview
  - ROI Model integration explained
  - Three-repository architecture
  - Quick reference guide with links to all detailed docs

- **[TRITON_PLATFORM_WORKFLOW.md](./TRITON_PLATFORM_WORKFLOW.md)** - Detailed 6-step platform workflow
  - Step 1: Client Management & Value Prop Setup (Triton)
  - Step 2: Prospect Creation & Alignment (Triton)
  - Step 3: Prospect Data Upload & Processing (ARGO)
  - Step 4: Value Prop Data Generation (Triton Analytics Team)
  - Step 5: ROI Dashboard Data Generation (Triton Analytics Team)
  - Step 6: MARE Application - Reports & Presentation
  - ROI Model Architecture integration section (NEW)

- **[ROI_MODEL_RESEARCH_FLOW_UPDATED.md](./ROI_MODEL_RESEARCH_FLOW_UPDATED.md)** - ROI Model system architecture (v3.0)
  - Three-repository integration (mare-triton-research-prompts, triton-agentic, mare-frontend)
  - 13 ROI Model Types (B1-B13) with classification
  - Prompt engineering system (7,641 lines of prompts)
  - Model builder agent workflows
  - Complete validation pipeline
  - End-to-end ROI model generation flow

### Getting Started

- **[QUICKSTART.md](./QUICKSTART.md)** - Quick setup and first template generation
- **[DOCKER_SETUP.md](./DOCKER_SETUP.md)** - Docker containerization and deployment guide

### API Documentation

- **[API_README.md](./API_README.md)** - REST API reference and endpoints

### Core Features

#### Template Generation
- **[DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md)** - Complete data flow from templates to widget data
  - What `/results` endpoint provides
  - Where generated data is stored
  - How synthetic data generation works

#### Research Agents
- **[RESEARCH_AGENT_FLOW.md](./RESEARCH_AGENT_FLOW.md)** - Complete research agent system with 19 Mermaid diagrams
  - WebSearchAgent detailed flow (web search, autonomous/manual modes)
  - DocumentAnalysisAgent detailed flow (PDF/DOCX/TXT analysis)
  - API layer architecture and job management
  - 4-layer validation pipeline with retry logic
  - Tool integration (Google search, web scraper, S3 reader)
  - Data models and component specifications

- **[WEB_SEARCH_QUICKSTART.md](./WEB_SEARCH_QUICKSTART.md)** - Quick start guide (START HERE!)
  - Check current search provider
  - 2-minute setup for free search
  - Testing instructions

- **[WEB_SEARCH_SETUP.md](./WEB_SEARCH_SETUP.md)** - Detailed setup guide
  - DuckDuckGo setup (free)
  - Tavily setup (premium)
  - Troubleshooting and testing

- **[WEB_SEARCH_SOLUTIONS.md](./WEB_SEARCH_SOLUTIONS.md)** - Complete comparison guide
  - Why you need web search (vs mock mode)
  - Tavily vs alternatives comparison
  - Open source options (DuckDuckGo, SearXNG, Jina Reader)
  - Building custom search solution
  - Cost comparison and recommendation matrix

- **[RESEARCH_API_GUIDE.md](./RESEARCH_API_GUIDE.md)** - Research API reference
  - Endpoint specifications
  - Request/response examples
  - Python client usage

- **[RESEARCH_API_IMPLEMENTATION_COMPLETE.md](./RESEARCH_API_IMPLEMENTATION_COMPLETE.md)** - Implementation status
  - Completed components
  - Integration guide
  - Next steps

#### Prospect Data System
- **[PROSPECT_DATA_GENERATION.md](./PROSPECT_DATA_GENERATION.md)** - Prospect dashboard data generation
  - Automatic data generation during template creation
  - Database schema and architecture
  - API endpoints and testing procedures

- **[PROSPECT_DASHBOARD_SYSTEM.md](./PROSPECT_DASHBOARD_SYSTEM.md)** - Complete prospect dashboard system overview
  - System architecture
  - Data models and relationships
  - Frontend integration guide

#### Real-Time Events (Message Broker)
- **[MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md)** - Redis Pub/Sub event system
  - Implementation details
  - How it eliminates HTTP polling
  - API usage examples
  - Performance benefits (99% reduction in requests)

- **[MESSAGE_BROKER_TESTING.md](./MESSAGE_BROKER_TESTING.md)** - Testing guide for message broker
  - 7 comprehensive test scenarios
  - Performance comparison
  - Troubleshooting guide

### Operations & Monitoring

- **[MONITORING_SETUP.md](./MONITORING_SETUP.md)** - Prometheus, Grafana, and Flower setup
  - Metrics collection
  - Dashboard configuration
  - Alerting rules

- **[TESTING_AND_MONITORING_GUIDE.md](./TESTING_AND_MONITORING_GUIDE.md)** - Testing and monitoring best practices
  - Integration testing
  - Load testing
  - Production monitoring

### Meta Documentation

- **[DOCUMENTATION_ORGANIZATION.md](./DOCUMENTATION_ORGANIZATION.md)** - How documentation is organized
  - Folder structure conventions
  - File naming standards
  - Creating new documentation
  - Link verification

---

## 📖 Documentation by Use Case

### For New Developers

1. **⭐ Start with [TRITON_COMPLETE_FLOW.md](./TRITON_COMPLETE_FLOW.md)** - Master overview of entire system
2. Review [TRITON_PLATFORM_WORKFLOW.md](./TRITON_PLATFORM_WORKFLOW.md) - Detailed 6-step workflow
3. Check [QUICKSTART.md](./QUICKSTART.md) for hands-on setup
4. Read [API_README.md](./API_README.md) for API overview
5. Understand [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) for data storage

### For DevOps/Infrastructure

1. [DOCKER_SETUP.md](./DOCKER_SETUP.md) - Container deployment
2. [MONITORING_SETUP.md](./MONITORING_SETUP.md) - Observability stack
3. [MESSAGE_BROKER_TESTING.md](./MESSAGE_BROKER_TESTING.md) - Verify event system

### For Frontend Developers

1. [PROSPECT_DASHBOARD_SYSTEM.md](./PROSPECT_DASHBOARD_SYSTEM.md) - Frontend integration
2. [API_README.md](./API_README.md) - API endpoints
3. [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) - Real-time updates via SSE

### For Backend Developers

1. **⭐ [TRITON_COMPLETE_FLOW.md](./TRITON_COMPLETE_FLOW.md)** - System architecture overview
2. [TRITON_PLATFORM_WORKFLOW.md](./TRITON_PLATFORM_WORKFLOW.md) - Complete platform workflow
3. [ROI_MODEL_RESEARCH_FLOW_UPDATED.md](./ROI_MODEL_RESEARCH_FLOW_UPDATED.md) - ROI Model architecture
4. [RESEARCH_AGENT_FLOW.md](./RESEARCH_AGENT_FLOW.md) - Research agent detailed flows
5. [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) - Data storage and retrieval
6. [PROSPECT_DATA_GENERATION.md](./PROSPECT_DATA_GENERATION.md) - Data generation logic
7. [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) - Event system design

---

## 🔍 Quick Reference

### Key Concepts

| Concept | Description | Doc |
|---------|-------------|-----|
| **Templates** | Dashboard layout configurations | [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) |
| **Prospect Data** | Widget values for specific prospects | [PROSPECT_DATA_GENERATION.md](./PROSPECT_DATA_GENERATION.md) |
| **Synthetic Data** | Auto-generated sample data | [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) |
| **Message Broker** | Redis Pub/Sub for real-time events | [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) |
| **SSE** | Server-Sent Events for push notifications | [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) |

### API Endpoints

| Endpoint | Purpose | Doc |
|----------|---------|-----|
| `POST /clients/{id}/generate-templates` | Generate templates | [API_README.md](./API_README.md) |
| `GET /jobs/{id}` | Check job status | [API_README.md](./API_README.md) |
| `GET /jobs/{id}/subscribe` | SSE real-time updates | [MESSAGE_BROKER_IMPLEMENTATION.md](./MESSAGE_BROKER_IMPLEMENTATION.md) |
| `GET /prospect-data/{id}` | Get widget data | [PROSPECT_DATA_GENERATION.md](./PROSPECT_DATA_GENERATION.md) |
| `GET /templates/{id}` | Get template structure | [API_README.md](./API_README.md) |

### Database Tables

| Table | Purpose | Doc |
|-------|---------|-----|
| `clients` | Client information | [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) |
| `value_propositions` | Client value props | [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) |
| `dashboard_templates` | Template structures | [DATA_FLOW_EXPLANATION.md](./DATA_FLOW_EXPLANATION.md) |
| `prospects` | Dashboard viewers | [PROSPECT_DATA_GENERATION.md](./PROSPECT_DATA_GENERATION.md) |
| `prospect_dashboard_data` | Widget values | [PROSPECT_DATA_GENERATION.md](./PROSPECT_DATA_GENERATION.md) |
| `generation_jobs` | Async job tracking | [API_README.md](./API_README.md) |

---

## 🎯 Common Tasks

### Generate Templates with Data

```bash
# See QUICKSTART.md for complete workflow
# See PROSPECT_DATA_GENERATION.md for data generation details
```

### Monitor Job Progress (No Polling!)

```bash
# See MESSAGE_BROKER_IMPLEMENTATION.md for SSE usage
# See MESSAGE_BROKER_TESTING.md for testing
```

### Set Up Monitoring

```bash
# See MONITORING_SETUP.md for Grafana/Prometheus
# See TESTING_AND_MONITORING_GUIDE.md for best practices
```

### Deploy to Production

```bash
# See DOCKER_SETUP.md for container deployment
# See MONITORING_SETUP.md for observability
```

---

## 📝 Documentation Standards

All documentation in this folder follows these conventions:

- **Markdown format** - GitHub-flavored markdown
- **Code examples** - Bash, Python, JavaScript, SQL as needed
- **Clear headings** - H1 for title, H2 for sections
- **Tables** - For comparisons and reference data
- **Diagrams** - ASCII art for architecture
- **Links** - Relative links to other docs

---

## 🔄 Keeping Documentation Updated

When adding new features:

1. **Create new doc** in `docs/` folder (not root)
2. **Add to this README** in appropriate section
3. **Link from root README.md** if major feature
4. **Update CLAUDE.md** if it affects development workflow

---

## 📍 Document Locations

```
triton-agentic/
├── README.md                          # Main project README
├── CLAUDE.md                          # Claude Code instructions
├── docs/                              # All documentation here
│   ├── README.md                      # This file
│   │
│   ├── TRITON_COMPLETE_FLOW.md        # ⭐ Master reference document (NEW)
│   ├── TRITON_PLATFORM_WORKFLOW.md    # 6-step platform workflow (NEW)
│   ├── ROI_MODEL_RESEARCH_FLOW_UPDATED.md  # ROI Model architecture v3.0 (NEW)
│   │
│   ├── QUICKSTART.md
│   ├── API_README.md
│   ├── DATA_FLOW_EXPLANATION.md
│   ├── RESEARCH_AGENT_FLOW.md         # Research agent flows
│   ├── RESEARCH_API_GUIDE.md          # Research API reference
│   ├── RESEARCH_API_IMPLEMENTATION_COMPLETE.md  # Implementation status
│   ├── PROSPECT_DATA_GENERATION.md
│   ├── PROSPECT_DASHBOARD_SYSTEM.md
│   ├── MESSAGE_BROKER_IMPLEMENTATION.md
│   ├── MESSAGE_BROKER_TESTING.md
│   ├── DOCKER_SETUP.md
│   ├── MONITORING_SETUP.md
│   └── TESTING_AND_MONITORING_GUIDE.md
```

---

## 🆘 Need Help?

1. **Quick answers**: Search this README index
2. **Detailed guides**: Open the specific doc file
3. **Code examples**: Check the relevant guide
4. **Troubleshooting**: See testing and monitoring guides

For issues not covered in documentation, check:
- Docker logs: `docker logs triton-api`
- Worker logs: `docker logs triton-worker`
- Redis events: `docker exec -it triton-redis redis-cli MONITOR`
