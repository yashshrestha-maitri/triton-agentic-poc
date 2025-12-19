# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Triton Agentic** is a healthcare dashboard template generation system using AI agents. It generates 5-10 dashboard template variations from client value propositions using the Agno framework with AWS Bedrock (Claude Sonnet 4).

This is a prototype implementation modeled after `mare-agentic-data-mapper` project structure.

## Development Commands

### Setup and Installation
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials and API keys
```

### Running the Application
```bash
# Run template generation prototype (console application)
python triton_app.py

# Run REST API server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
# Or: python app.py

# API documentation available at:
# - http://localhost:8000/docs (Swagger UI)
# - http://localhost:8000/redoc (ReDoc)
```

### Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=agents --cov=core

# Run specific test
pytest tests/test_template_agent.py::test_specific_function
```

## Architecture

### Agent System Architecture

The system uses a **single-agent architecture** with comprehensive instructions rather than multi-agent coordination. Key design decision: Template generation is self-contained and doesn't require agent orchestration.

**Agent Creation Flow:**
1. `create_template_generator_agent()` creates base agent from `TemplateGeneratorAgentTemplate`
2. `create_template_generator_with_retry()` wraps agent with retry logic
3. Retry wrapper handles: JSON extraction → JSON parsing → Pydantic validation → Business rule validation
4. On validation failure, error feedback is provided to agent for correction (max 3 retries)

**Critical AWS Bedrock Workarounds:**
- AWS Bedrock (via Agno) does NOT support `response_format` or structured outputs despite Agno's defaults
- `model_factory.py` patches AWS Bedrock model to disable structured output support and accept/ignore `response_format` parameter
- Agent uses manual JSON parsing with `extract_json_from_response()` instead of Agno's structured outputs
- This allows the same agent code to work with both Bedrock and direct API providers

### Model Provider System

**Multi-Provider Factory Pattern:**
- `ModelFactory` in `core/models/model_factory.py` creates model instances for: OpenAI, Anthropic, Google, Groq, AWS Bedrock
- Default provider/model configured via `.env` (`DEFAULT_MODEL_PROVIDER`, `DEFAULT_MODEL_NAME`)
- AWS Bedrock requires monkey-patching to work around Agno framework bugs (see `_create_aws_bedrock_model()`)

### Configuration System

**Layered Configuration (Pydantic Settings):**
- `core/config/settings.py` defines config hierarchy: `MareConfig` → `ModelConfig`, `DatabaseConfig`, `RedshiftConfig`, `MonitoringConfig`
- All configs load from `.env` with typed validation
- Global singleton: `config = get_config()`
- AWS configuration supports both profile-based and credential-based auth

### Template Models and Validation

**4-Layer Validation System:**
1. **JSON Extraction**: `extract_json_from_response()` extracts JSON from markdown/text
2. **JSON Parsing**: Standard `json.loads()` validates syntax
3. **Pydantic Validation**: `TemplateGenerationResult` model validates types, constraints, field presence
4. **Business Logic**: `validate_all()` checks template count (5-10), widget count (6-12), category coverage, audience coverage, grid positions

**Model Hierarchy:**
- `TemplateGenerationResult` (root) → `templates[]`, `metadata`, `unmapped_*`
- `DashboardTemplate` → `widgets[]`, `visualStyle`, `category`, `targetAudience`
- `DashboardWidget` → `position`, `type`, `chartType`, `config`
- `WidgetPosition` → 12-column grid validation

Models in `core/models/template_models.py` match frontend TypeScript types exactly (`src/types/dashboardTemplateTypes.ts`).

### REST API Architecture

**FastAPI Application (`app.py`):**
- Two main routers: `templates.router` (template CRUD), `results.router` (result management)
- Global exception handlers for validation errors and unexpected errors
- CORS enabled for development (restrict in production)
- Health check endpoints: `/` and `/health`

**Template Endpoints (`api/routes/templates.py`):**
- `POST /templates/generate` - Generates templates via agent, saves to `results/` directory
- `GET /templates/` - Lists all templates with pagination/filtering (scans all result files)
- `GET /templates/{template_id}` - Retrieves specific template (searches across files)
- `DELETE /templates/{template_id}` - Removes template from result file

**Result Endpoints (`api/routes/results.py`):**
- `GET /results/` - Lists result files with metadata
- `GET /results/{filename}` - Returns full result JSON
- `GET /results/{filename}/download` - Downloads result file
- `GET /results/stats/summary` - Aggregates statistics across all results

**Storage:** JSON files in `results/` directory (filename pattern: `templates_{client_name}_{timestamp}.json`)

### Base Agent Template System

**Template Pattern for Agent Creation:**
- Abstract `BaseAgentTemplate` class in `agents/base/base_agent.py` defines agent creation interface
- Template methods: `get_agent_config()`, `get_tools()`, `get_instructions()`, `get_description()`
- `_load_instruction_file()` loads markdown instructions from `agents/templates/` with caching
- Agents are created via `template.create_agent(name, model)` → returns `MareAgent` instance

**MareAgent Class:**
- Extends Agno's `Agent` with Mare-specific features: service registration, metrics, execution timing
- `_execution_timer()` context manager tracks agent performance
- Health status tracking via `get_health_status()`

## Key Files and Their Roles

### Core Agent Files
- **`agents/template_generator_agent.py`**: Agent factory functions and retry wrapper logic
- **`agents/templates/template_generation_instructions.md`**: 300+ lines of comprehensive agent instructions (widget types, grid rules, validation requirements)
- **`agents/base/base_agent.py`**: Base template pattern and MareAgent wrapper

### Core Infrastructure
- **`core/models/model_factory.py`**: LLM provider abstraction with AWS Bedrock workarounds
- **`core/models/template_models.py`**: Pydantic models and validation functions
- **`core/config/settings.py`**: Configuration management with environment variable loading
- **`core/monitoring/logger.py`**: Logging and metrics collection

### API Layer
- **`app.py`**: FastAPI application entry point with exception handlers
- **`api/routes/templates.py`**: Template generation and CRUD endpoints
- **`api/routes/results.py`**: Result file management and statistics
- **`api/models/responses.py`**: Request/response Pydantic models

### Application Entry Points
- **`triton_app.py`**: Console application for prototype testing (loads sample value proposition, runs agent, saves results)
- **`app.py`**: REST API server

## Environment Configuration

**Required Environment Variables:**
```env
# Model Configuration
DEFAULT_MODEL_PROVIDER=aws_bedrock  # or: anthropic, openai, google, groq
DEFAULT_MODEL_NAME=us.anthropic.claude-sonnet-4-20250514-v1:0

# AWS Bedrock (if using aws_bedrock provider)
AWS_PROFILE=your-profile
AWS_REGION=us-east-1

# Direct API Keys (if not using Bedrock)
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...

# Logging
LOG_LEVEL=INFO
DEBUG_MODE=true
ENABLE_METRICS=true

# API Server (optional)
API_HOST=0.0.0.0
API_PORT=8000
```

## Important Implementation Details

### AWS Bedrock Compatibility

**Critical Issue:** Agno framework incorrectly assumes AWS Bedrock supports structured outputs. Workarounds implemented:

1. **Model Factory Patching** (`core/models/model_factory.py:93-123`):
   - Sets `supports_native_structured_outputs = False`
   - Sets `supports_json_schema_outputs = False`
   - Monkey-patches `get_request_params()` to accept and ignore `response_format` parameter

2. **Manual JSON Processing** (`agents/template_generator_agent.py:170-294`):
   - Extract JSON from text response (handles markdown code blocks)
   - Parse JSON string to dict
   - Validate with Pydantic manually
   - Retry with error feedback if validation fails

### Retry Logic with Validation Feedback

The `create_template_generator_with_retry()` wrapper provides intelligent retry:
- On validation error: Appends error details to message, re-invokes agent with corrections
- On JSON parsing error: Instructs agent to return only raw JSON
- Max 3 attempts with cumulative feedback
- Each retry includes previous attempt's errors and guidance

### Grid Position Validation

Widgets use 12-column grid (like Bootstrap). Validation in `core/models/template_models.py:190-218`:
- Column span must not exceed 12: `col + colSpan ≤ 13`
- Widgets cannot overlap: Tracks occupied `(row, col)` cells
- Each widget occupies `rowSpan × colSpan` cells

## Output Format

Generated templates are saved to `results/templates_{client_name}_{timestamp}.json` with structure:
```json
{
  "templates": [/* 5-10 DashboardTemplate objects */],
  "metadata": {
    "client_name": "...",
    "industry": "...",
    "generated_at": "ISO timestamp",
    "total_templates": 7,
    "validation_passed": true,
    "generation_time_seconds": 45.2
  },
  "unmapped_categories": [],
  "unmapped_audiences": []
}
```

## Testing Strategy

- Unit tests in `tests/test_template_agent.py`
- Integration test via `python triton_app.py` (generates real templates)
- API testing via interactive docs at `/docs` when running `uvicorn app:app`
- Validation testing: Modify `triton_app.py` value proposition to test edge cases

## Documentation Conventions

**IMPORTANT: All documentation files (*.md) must be created in the `docs/` folder structure, NOT in the project root.**

### Documentation Structure

Documentation is organized into **four main folders** based on purpose:

```
triton-agentic/
├── README.md                              # Main project README (root only)
├── CLAUDE.md                              # Claude Code instructions (root only)
│
└── docs/                                  # All documentation here
    ├── README.md                          # Main documentation index
    │
    ├── architecture-current/              # ✅ CURRENT ARCHITECTURE (ROI Models)
    │   ├── README.md                      # Current architecture overview
    │   ├── TRITON_COMPLETE_FLOW.md        # ⭐ Master reference
    │   ├── ROI_MODEL_RESEARCH_FLOW_UPDATED.md
    │   ├── RESEARCH_AGENT_FLOW.md         # Research agents
    │   └── ... (ROI model & research docs)
    │
    ├── architecture-legacy/               # 📚 LEGACY (Reference Only)
    │   ├── README.md                      # Legacy context
    │   ├── VALUE_PROPOSITION_SYSTEM.md
    │   └── ... (old architecture docs)
    │
    ├── features/                          # ✅ FEATURE-SPECIFIC DOCS
    │   ├── README.md                      # Feature index
    │   ├── PROSPECT_DATA_GENERATION.md
    │   ├── MESSAGE_BROKER_IMPLEMENTATION.md
    │   ├── DATA_FLOW_EXPLANATION.md
    │   └── ... (architecture-agnostic features)
    │
    └── operations/                        # ✅ OPERATIONS & DEPLOYMENT
        ├── README.md                      # Operations guide
        ├── QUICKSTART.md
        ├── API_README.md
        ├── DOCKER_SETUP.md
        └── ... (setup, testing, deployment)
```

### Rules for Documentation

1. **New Documentation Files - Choose the Right Folder:**
   - **Current Architecture** (ROI models, research agents): `docs/architecture-current/FILE.md`
   - **Legacy Reference** (old value prop system): `docs/architecture-legacy/FILE.md`
   - **Features** (architecture-agnostic): `docs/features/FILE.md`
   - **Operations** (setup, deployment, testing): `docs/operations/FILE.md`
   - NEVER create in project root (except README.md and CLAUDE.md)

2. **Naming Convention:**
   - Use UPPERCASE_SNAKE_CASE for documentation files
   - Be descriptive: `MESSAGE_BROKER_TESTING.md` not `TEST.md`

3. **Update Indexes:**
   - Add new doc to subfolder `README.md` (e.g., `docs/features/README.md`)
   - Add entry to main `docs/README.md` index
   - Update root `README.md` if major feature

4. **Internal Links:**
   - Use relative paths from current location
   - Example from root: `[Docs](./docs/README.md)`
   - Example from subfolder: `[Feature](./features/DATA_FLOW.md)`
   - Cross-folder: `[Operations](../operations/QUICKSTART.md)`

### Examples

**✅ Correct:**
```bash
# Create new ROI model documentation
Write file: /home/yashrajshres/triton-agentic/docs/architecture-current/ROI_MODEL_BUILDER.md

# Create new feature documentation
Write file: /home/yashrajshres/triton-agentic/docs/features/CACHING_SYSTEM.md

# Create new operations guide
Write file: /home/yashrajshres/triton-agentic/docs/operations/KUBERNETES_DEPLOYMENT.md

# Update appropriate README
Edit file: /home/yashrajshres/triton-agentic/docs/architecture-current/README.md
```

**❌ Incorrect:**
```bash
# Don't create in root
Write file: /home/yashrajshres/triton-agentic/ROI_MODEL_BUILDER.md

# Don't create in wrong folder (architecture doc in features/)
Write file: /home/yashrajshres/triton-agentic/docs/features/ROI_MODEL_BUILDER.md
```

### When Creating New Documentation

1. **Determine folder** based on content type:
   - Current architecture? → `architecture-current/`
   - Feature documentation? → `features/`
   - Setup/deployment? → `operations/`
   - Legacy reference? → `architecture-legacy/`

2. **Create file** in appropriate subfolder

3. **Update indexes:**
   - Add to subfolder's `README.md`
   - Add to main `docs/README.md`
   - Update root `README.md` if major feature

4. **Use proper formatting:**
   - Clear headings (H1 for title, H2 for sections)
   - Code examples with syntax highlighting
   - Tables for reference data
   - Diagrams where helpful

### Documentation Folder Purpose Guide

| Folder | When to Use | Examples |
|--------|-------------|----------|
| `architecture-current/` | ROI models, research agents, current system design | ROI_MODEL_BUILDER.md, RESEARCH_API.md |
| `architecture-legacy/` | Historical reference, deprecated systems | VALUE_PROPOSITION_SYSTEM.md |
| `features/` | Specific features that work across architectures | MESSAGE_BROKER.md, CACHING.md |
| `operations/` | Setup, deployment, testing, monitoring | QUICKSTART.md, DOCKER_SETUP.md |

## Production Considerations

Current implementation is prototype/development. For production:
- Add authentication to FastAPI (API keys or OAuth2)
- Replace JSON file storage with PostgreSQL (schema defined in `DatabaseConfig`)
- Add Celery task queue for async generation (referenced in README roadmap)
- Implement rate limiting on API endpoints
- Configure CORS with specific allowed origins (currently allows all)
- Use production ASGI server: `gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker`
