# Triton Agentic - Quick Start Guide

## 🎯 What is This?

**Triton Agentic** is a prototype implementation of the Template Generation Agent from the Triton Platform engineering spec. It generates 5-10 dashboard template variations for healthcare ROI presentations using Agno + Claude Sonnet 4.

This is modeled after the `mare-agentic-data-mapper` project structure.

## 📦 Project Structure

```
triton-agentic/
├── agents/
│   ├── base/base_agent.py                  # Base agent class
│   ├── templates/                          # Agent instructions
│   │   └── template_generation_instructions.md
│   └── template_generator_agent.py         # Main agent
│
├── core/
│   ├── config/settings.py                  # Configuration
│   ├── models/
│   │   ├── model_factory.py                # LLM provider factory
│   │   └── template_models.py              # Pydantic models
│   └── monitoring/logger.py                # Logging
│
├── results/                                # Output directory
├── triton_app.py                          # Main entry point
├── requirements.txt
└── README.md
```

## 🚀 Setup (5 minutes)

### 1. Create Virtual Environment

```bash
cd /home/yashrajshres/triton-agentic
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

Required in `.env`:
```env
DEFAULT_MODEL_PROVIDER=aws_bedrock
DEFAULT_MODEL_NAME=us.anthropic.claude-sonnet-4-20250514-v1:0
AWS_PROFILE=your-profile
AWS_REGION=us-east-1
```

### 4. Run Prototype

```bash
python triton_app.py
```

## 📊 What It Does

1. **Loads** a sample value proposition (Livongo diabetes management)
2. **Creates** a Template Generator Agent with:
   - 300+ lines of instructions
   - Pydantic schema validation
   - Automatic retry on validation errors (max 3 attempts)
3. **Generates** 5-10 dashboard templates with:
   - 6-12 widgets each
   - Multiple categories (ROI, clinical, operational, etc.)
   - Multiple target audiences
4. **Validates** output against business rules:
   - Template count (5-10)
   - Widget count per template (6-12)
   - Category coverage (all 5)
   - Audience coverage (all specified)
   - Grid position validation
5. **Saves** result to `results/templates_result.json`

## 🎨 Output Format

The agent generates a structured JSON matching the frontend TypeScript types:

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
    "client_name": "Livongo Health",
    "generated_at": "2025-01-15T12:00:00Z",
    "total_templates": 7,
    "validation_passed": true
  }
}
```

## 🔍 Key Files

### Agent Definition
**`agents/template_generator_agent.py`**
- Creates the agent instance
- Configures with Pydantic response model
- Implements retry logic with validation feedback

### Agent Instructions
**`agents/templates/template_generation_instructions.md`**
- 300+ lines of comprehensive instructions
- Widget type definitions
- Grid layout rules
- Validation requirements
- Examples

### Pydantic Models
**`core/models/template_models.py`**
- `DashboardTemplate` - Single template
- `DashboardWidget` - Single widget
- `TemplateGenerationResult` - Complete output
- Validation functions

### Main Application
**`triton_app.py`**
- Loads value proposition
- Creates agent
- Runs generation
- Validates output
- Saves results

## ⚙️ Customization

### Use Different Value Proposition

Edit `triton_app.py` around line 60 to load your own value proposition:

```python
value_proposition = {
    "executive_value_proposition": {...},
    "value_proposition_priorities": [...],
    # ... your data
}
```

### Adjust Target Audiences

Change line 40 in `triton_app.py`:

```python
target_audiences = ["Health Plan", "Broker", "PBM", "TPA", "Medical Management"]
```

### Change Model

Edit `.env`:

```env
DEFAULT_MODEL_PROVIDER=anthropic  # Use direct API instead of Bedrock
ANTHROPIC_API_KEY=your-key
```

## 🧪 Testing

```bash
# Run with different value propositions
python triton_app.py

# Check output
cat results/templates_result.json | jq '.metadata'

# Verify template count
cat results/templates_result.json | jq '.templates | length'
```

## 📈 Expected Performance

- **Generation Time**: 30-90 seconds
- **Success Rate**: >95% (with retry logic)
- **Output Size**: 50-200 KB JSON
- **Templates**: 5-10 (typically 7)
- **Widgets per Template**: 6-12 (typically 8)

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### AWS Bedrock errors
```bash
# Check AWS credentials
aws sts get-caller-identity --profile your-profile

# Verify model access
aws bedrock list-foundation-models --region us-east-1
```

### Validation errors after 3 attempts
- Check `results/templates_result.json` for partial output
- Review agent instructions in `agents/templates/`
- Increase `max_retries` in `triton_app.py`

## 🚀 Next Steps

### Phase 2: Production Integration
1. Add Celery task queue
2. Add PostgreSQL storage
3. Add job status tracking
4. Create REST API endpoints
5. Add comprehensive testing

### Phase 3: Advanced Features
1. Iterative refinement with user feedback
2. Template learning from user selections
3. Multi-language support
4. Custom widget types

## 📚 References

- **Engineering Spec**: `/home/yashrajshres/mare-frontend/TRITON_ENGINEERING_SPEC.md`
- **Flow Document**: `/home/yashrajshres/mare-frontend/TEMPLATE_GENERATION_AGENT_FLOW.md`
- **Frontend Types**: `/home/yashrajshres/mare-frontend/src/types/dashboardTemplateTypes.ts`
- **Mare Data Mapper**: `/home/yashrajshres/mare-agentic-data-mapper/`

## 💡 Architecture Notes

### Why Single Agent?
- Template generation is self-contained
- No multi-agent coordination needed
- All logic in comprehensive instructions
- Tools not needed (works with JSON input)

### Why Agno?
- Built-in structured outputs
- Pydantic validation
- Retry and error handling
- Multi-provider support (Bedrock, OpenAI, etc.)

### Why Claude Sonnet 4?
- Best reasoning for complex tasks
- Excellent JSON generation
- Long context window
- Reliable structured outputs

---

**Ready to run?**

```bash
cd /home/yashrajshres/triton-agentic
source venv/bin/activate
python triton_app.py
```
