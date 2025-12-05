# Triton Agentic - Template Generation Agent

**Healthcare dashboard template generation agent using Agno framework with AWS Bedrock, following best practices for agentic systems.**

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate
cd triton-agentic

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - AWS credentials for Bedrock
# - PostgreSQL connection (optional for storage)
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Run the Agent

```bash
# Run template generation prototype
python triton_app.py
```

**Key Features**:
- Single-purpose agent for dashboard template generation
- Generates 5-10 template variations from value proposition
- Structured JSON output validated with Pydantic
- Easy to modify and test
- See: [agents/template_generator_agent.py](agents/template_generator_agent.py)

## 📁 Project Structure

```
triton-agentic/
├── agents/
│   ├── base/
│   │   └── base_agent.py              # Base agent template
│   ├── templates/
│   │   └── template_generation_instructions.md  # Agent instructions
│   └── template_generator_agent.py     # Template generation agent
│
├── core/
│   ├── config/
│   │   └── settings.py                # Configuration management
│   ├── models/
│   │   ├── model_factory.py           # LLM provider factory (AWS Bedrock, OpenAI)
│   │   └── template_models.py         # Pydantic models for templates
│   └── monitoring/
│       └── logger.py                  # Logging and metrics
│
├── tools/                             # Tools for agent (if needed)
│   └── value_prop_loader.py          # Load value proposition data
│
├── results/                           # Output directory
│   └── templates_result.json         # Generated templates
│
├── examples/
│   └── sample_value_proposition.json # Example input
│
├── tests/
│   └── test_template_agent.py        # Agent tests
│
├── triton_app.py                     # Main application entry point
├── .env.example                      # Environment template
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## ⚙️ Configuration

### Environment Variables

Edit `.env` with your configuration:

```env
# AWS Bedrock (Claude models)
DEFAULT_MODEL_PROVIDER=aws_bedrock
DEFAULT_MODEL_NAME=us.anthropic.claude-sonnet-4-20250514-v1:0
AWS_PROFILE=your-aws-profile
AWS_REGION=us-east-1

# Alternative: Direct API providers
# DEFAULT_MODEL_PROVIDER=anthropic
# ANTHROPIC_API_KEY=your-key-here

# Logging
LOG_LEVEL=INFO
ENABLE_METRICS=true
DEBUG_MODE=true
```

## 🎯 Usage Example

```python
from core.models.model_factory import get_default_model
from agents.template_generator_agent import create_template_generator_agent

# Create agent
model = get_default_model()
agent = create_template_generator_agent(
    name="TemplateGeneratorAgent",
    model=model
)

# Run agent with value proposition
task = """
Generate 5-10 dashboard template variations for the following client value proposition:

{value_proposition_json_here}
"""

result = agent.run(task)

# Access structured output
print(f"Generated {len(result.templates)} templates")
for template in result.templates:
    print(f"  - {template.name} ({template.category})")
```

## 📊 Output Format

The agent generates a structured JSON output:

```json
{
  "templates": [
    {
      "id": "uuid",
      "name": "Diabetes ROI Executive Dashboard",
      "description": "C-suite focused financial impact dashboard",
      "category": "roi-focused",
      "targetAudience": "Health Plan",
      "keyFeatures": ["24-month ROI", "Savings waterfall", "Payback analysis"],
      "widgets": [
        {
          "id": "w_roi_24mo",
          "type": "kpi-card",
          "title": "24-Month ROI",
          "position": {"row": 1, "col": 1, "rowSpan": 2, "colSpan": 3},
          "data": {},
          "config": {"format": "percentage", "trend": true}
        }
      ],
      "visualStyle": {
        "primaryColor": "#2563eb",
        "accentColor": "#10b981",
        "layout": "balanced"
      }
    }
  ],
  "metadata": {
    "client_id": "uuid",
    "generated_at": "2025-01-15T12:00:00Z",
    "total_templates": 7,
    "validation_passed": true
  }
}
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=agents --cov=core
```

## 🔍 Validation

The agent includes multi-layer validation:
1. **JSON Parse** - Syntax validation
2. **Pydantic Schema** - Type & field validation
3. **Business Rules** - Count, coverage, position validation

## 📝 Architecture Decisions

### Why Single Agent?
- Template generation is a self-contained task
- No need for multi-agent coordination
- All logic in comprehensive instructions (~300+ lines)
- Tools only for data access (if needed)

### Why Agno?
- Built-in structured outputs with Pydantic
- Easy retry and error handling
- Memory and conversation management
- Compatible with multiple LLM providers

### Why Claude Sonnet 4?
- Best reasoning for complex template design
- Excellent at following structured output schemas
- Long context window for value proposition analysis
- Reliable JSON generation

## 🚀 Roadmap

### Phase 1: Prototype (Current)
- [x] Single agent with basic template generation
- [x] Pydantic models matching frontend types
- [x] Structured output validation
- [ ] Example value proposition input
- [ ] Basic retry logic

### Phase 2: Production
- [ ] Integration with Celery task queue
- [ ] PostgreSQL storage for templates
- [ ] Job status tracking
- [ ] REST API endpoints
- [ ] Comprehensive testing suite

### Phase 3: Advanced Features
- [ ] Iterative refinement with user feedback
- [ ] Template learning from user selections
- [ ] Multi-language support
- [ ] Custom widget types

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](./docs) folder:

- **[Documentation Index](./docs/README.md)** - Complete documentation overview
- **[Quick Start Guide](./docs/QUICKSTART.md)** - Get started in 5 minutes
- **[API Reference](./docs/API_README.md)** - REST API endpoints
- **[Data Flow Explanation](./docs/DATA_FLOW_EXPLANATION.md)** - How data flows through the system
- **[Prospect Data Generation](./docs/PROSPECT_DATA_GENERATION.md)** - Widget data generation
- **[Message Broker Implementation](./docs/MESSAGE_BROKER_IMPLEMENTATION.md)** - Real-time events (no polling!)
- **[Docker Setup](./docs/DOCKER_SETUP.md)** - Container deployment
- **[Monitoring Setup](./docs/MONITORING_SETUP.md)** - Grafana & Prometheus

### External References

- [TRITON Engineering Spec](/home/yashrajshres/mare-frontend/TRITON_ENGINEERING_SPEC.md)
- [Template Generation Flow](/home/yashrajshres/mare-frontend/TEMPLATE_GENERATION_AGENT_FLOW.md)
- [Agno Documentation](https://github.com/agno-agi/agno)
- [Mare Data Mapper](../mare-agentic-data-mapper)

## 🤝 Contributing

This is a prototype implementation. For production deployment, follow the full Triton Platform architecture described in the engineering spec.

## 📄 License

Proprietary - MacroHealth Inc.
