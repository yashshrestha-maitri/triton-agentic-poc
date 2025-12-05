# Prospect Dashboard Template System with Data Requirements

Complete guide to storing, validating, and using prospect dashboard templates with data requirements and analytics questions.

---

## Overview

The Prospect Dashboard Template System extends the basic template generation with:
- **Data Requirements**: SQL expressions and metrics for each widget
- **Analytics Questions**: Natural language descriptions of what each widget answers
- **Data Validation**: Automatic validation of template requirements against available data schemas
- **Prospect Data Storage**: Validated data storage for specific prospects

---

## Architecture

### Database Schema

```
clients
  └── prospect_dashboard_templates (new format with data_requirements)
  └── prospect_data_schemas (defines available data)
  └── prospects
        └── prospect_dashboard_data (validated generated data)
```

### Key Models

1. **ProspectDashboardTemplate** - Template with data requirements
2. **ProspectDataSchema** - Available data schema for validation
3. **ProspectDashboardData** - Generated data for specific prospects
4. **DataValidationResult** - Validation results

---

## Template Format

### New Template Structure

```json
{
  "id": "template-uuid",
  "client_id": "client-uuid",
  "name": "Three-Scenario ROI Comparison",
  "description": "Side-by-side comparison of ROI scenarios",
  "category": "roi-focused",
  "target_audience": "Health Plan",
  "visual_style": {
    "primary_color": "#c62828",
    "accent_color": "#6a1b9a",
    "layout": "balanced"
  },
  "widgets": [
    {
      "widget_id": "w_scenario_1_roi",
      "widget_type": "kpi-card",
      "title": "Conservative Scenario ROI",
      "description": "Conservative ROI estimate based on minimal adoption",
      "position": { "row": 1, "col": 1, "row_span": 1, "col_span": 1 },
      "size": { "min_width": 1, "min_height": 1 },
      "data_requirements": {
        "query_type": "aggregate",
        "metrics": [
          {
            "name": "roi_conservative",
            "expression": "(SUM(savings_conservative) / SUM(program_costs) - 1) * 100",
            "data_type": "percentage",
            "format": "0.0x"
          }
        ],
        "filters": [
          { "field": "scenario", "operator": "eq", "value": "conservative" }
        ]
      },
      "analytics_question": "What is the ROI for the conservative scenario?",
      "chart_config": {
        "icon": "tabler-trending-up",
        "show_trend": false,
        "subtitle": "2.6x ROI"
      }
    }
  ],
  "metadata": {
    "generated_by": "llm",
    "llm_model": "claude-3-5-sonnet-20241022",
    "generation_timestamp": "2025-01-15T10:30:00Z",
    "key_features": [
      "Conservative scenario: 2.6x ROI, $2,828 savings",
      "Moderate scenario: 3.4x ROI, $3,624 savings",
      "Optimistic scenario: 4.1x ROI, $4,477 savings"
    ],
    "recommended_use_case": "Financial planning and risk assessment"
  },
  "status": "approved",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T14:20:00Z"
}
```

### Data Requirements Structure

Each widget must specify:

```python
data_requirements = {
    "query_type": "aggregate | time_series | distribution | comparison | ranking",
    "dimensions": ["field1", "field2"],  # Group by fields
    "metrics": [
        {
            "name": "metric_name",
            "expression": "SQL expression",
            "data_type": "number | percentage | currency | string | date",
            "format": "display format"
        }
    ],
    "filters": [
        {
            "field": "field_name",
            "operator": "eq | ne | gt | lt | gte | lte | in | not_in | like | between",
            "value": "filter_value"
        }
    ],
    "time_range": {
        "type": "relative | absolute | rolling",
        "value": "last_30_days | last_6_months | etc."
    }
}
```

---

## Data Schema Definition

Define available data for validation:

```python
from core.models.prospect_dashboard_models import ProspectDataSchema

schema = ProspectDataSchema(
    client_id="client-uuid",
    schema_name="roi_analysis_schema",
    table_name="roi_analysis_data",
    fields=[
        {"name": "member_id", "type": "string", "description": "Member identifier"},
        {"name": "scenario", "type": "string", "description": "Scenario type"},
        {"name": "total_savings", "type": "currency", "description": "Total savings"},
        {"name": "program_costs", "type": "currency", "description": "Program costs"},
        {"name": "roi_multiplier", "type": "number", "description": "ROI multiplier"},
        {"name": "date", "type": "date", "description": "Analysis date"}
    ],
    available_metrics=["roi_conservative", "roi_moderate", "roi_optimistic"],
    time_fields=["date", "created_at"],
    dimension_fields=["scenario", "member_id"],
    is_active=True
)
```

---

## Usage Workflow

### 1. Store Template in New Format

```python
from core.models.prospect_dashboard_models import ProspectDashboardTemplate
from core.database.database import get_db_session
from core.database.models import ProspectDashboardTemplate as DBProspectTemplate

# Create template
template = ProspectDashboardTemplate(
    client_id="client-uuid",
    name="Three-Scenario ROI Comparison",
    description="Side-by-side comparison of ROI scenarios",
    category="roi-focused",
    target_audience="Health Plan",
    visual_style={
        "primary_color": "#c62828",
        "accent_color": "#6a1b9a",
        "layout": "balanced"
    },
    widgets=[...],  # List of DashboardWidgetNew
    metadata={
        "generated_by": "llm",
        "llm_model": "claude-sonnet-4",
        "key_features": ["Conservative: 2.6x ROI", "Moderate: 3.4x ROI"],
        "recommended_use_case": "Financial planning"
    },
    status="draft"
)

# Save to database
session = get_db_session()
db_template = DBProspectTemplate(
    client_id=template.client_id,
    name=template.name,
    description=template.description,
    category=template.category,
    target_audience=template.target_audience,
    visual_style=template.visual_style.model_dump(),
    widgets=[w.model_dump() for w in template.widgets],
    metadata=template.metadata.model_dump(),
    status=template.status
)
session.add(db_template)
session.commit()
```

### 2. Validate Template Against Data Schema

```python
from core.models.prospect_dashboard_models import validate_template_against_data_schema

# Load template and schema
template = session.query(DBProspectTemplate).filter_by(id=template_id).first()
schema = session.query(DBProspectDataSchema).filter_by(client_id=client_id, is_active=True).first()

# Convert to Pydantic
template_pydantic = ProspectDashboardTemplate(**{
    **template.__dict__,
    "widgets": [DashboardWidgetNew(**w) for w in template.widgets]
})
schema_pydantic = ProspectDataSchema(**schema.__dict__)

# Validate
validation_result = validate_template_against_data_schema(template_pydantic, schema_pydantic)

if validation_result.is_valid:
    print("✅ Template validated successfully!")
    template.status = "approved"
else:
    print(f"❌ Validation failed:")
    print(f"  Missing fields: {validation_result.missing_fields}")
    print(f"  Missing metrics: {validation_result.missing_metrics}")
    print(f"  Failed widgets: {validation_result.failed_widgets}")

session.commit()
```

### 3. Generate and Store Prospect Data

```python
from core.database.models import ProspectDashboardData
from datetime import datetime

# Generate data for prospect (placeholder - real implementation would query actual data)
prospect_data = {
    "w_scenario_1_roi": {
        "value": 2.6,
        "display": "2.6x ROI",
        "trend": "+15%"
    },
    "w_scenario_2_roi": {
        "value": 3.4,
        "display": "3.4x ROI",
        "trend": "+22%"
    }
}

# Store with validation result
db_data = ProspectDashboardData(
    prospect_id=prospect_id,
    prospect_template_id=template_id,
    dashboard_data=prospect_data,
    validation_result=validation_result.model_dump(),
    generated_at=datetime.utcnow(),
    generated_by="analytics_team",
    status="ready"
)
session.add(db_data)
session.commit()
```

### 4. Convert Old Templates to New Format

```python
from core.models.prospect_dashboard_models import convert_old_template_to_new_format

# Load old template
old_template = session.query(DashboardTemplate).filter_by(id=old_id).first()

# Convert
new_template = convert_old_template_to_new_format(
    old_template=old_template.__dict__,
    default_data_requirements={
        "query_type": "aggregate",
        "metrics": [{
            "name": "default_metric",
            "expression": "COUNT(*)",
            "data_type": "number"
        }]
    }
)

# Save
db_new_template = DBProspectTemplate(
    client_id=new_template.client_id,
    name=new_template.name,
    description=new_template.description,
    category=new_template.category,
    target_audience=new_template.target_audience,
    visual_style=new_template.visual_style.model_dump(),
    widgets=[w.model_dump() for w in new_template.widgets],
    metadata=new_template.metadata.model_dump(),
    status="draft"
)
session.add(db_new_template)
session.commit()
```

---

## API Endpoints (To Be Implemented)

### POST /api/v1/prospect-templates
Create a new prospect dashboard template

### GET /api/v1/prospect-templates
List all prospect dashboard templates

### GET /api/v1/prospect-templates/{template_id}
Get specific prospect dashboard template

### POST /api/v1/prospect-templates/{template_id}/validate
Validate template against data schema

### POST /api/v1/prospect-data-schemas
Create or update data schema

### POST /api/v1/prospect-data
Store validated prospect dashboard data

### GET /api/v1/prospect-data/{prospect_id}
Get dashboard data for a prospect

---

## Python Examples

### Example: Complete Workflow

```python
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from core.database.database import get_db_session
from core.database.models import (
    ProspectDashboardTemplate as DBProspectTemplate,
    ProspectDataSchema as DBProspectDataSchema,
    ProspectDashboardData as DBProspectData
)
from core.models.prospect_dashboard_models import (
    ProspectDashboardTemplate,
    ProspectDataSchema,
    DashboardWidgetNew,
    DataRequirements,
    MetricDefinition,
    FilterDefinition,
    WidgetPosition,
    VisualStyleNew,
    TemplateMetadata,
    validate_template_against_data_schema
)

# Step 1: Create template
template = ProspectDashboardTemplate(
    client_id="client-livongo-diabetes",
    name="Three-Scenario ROI Comparison",
    description="Side-by-side comparison of conservative, moderate, and optimistic ROI scenarios",
    category="roi-focused",
    target_audience="Health Plan",
    visual_style=VisualStyleNew(
        primary_color="#c62828",
        accent_color="#6a1b9a",
        layout="balanced"
    ),
    widgets=[
        DashboardWidgetNew(
            widget_id="w_scenario_1_roi",
            widget_type="kpi-card",
            title="Conservative Scenario ROI",
            description="Conservative ROI estimate",
            position=WidgetPosition(row=1, col=1, row_span=1, col_span=1),
            data_requirements=DataRequirements(
                query_type="aggregate",
                metrics=[
                    MetricDefinition(
                        name="roi_conservative",
                        expression="(SUM(savings_conservative) / SUM(program_costs) - 1) * 100",
                        data_type="percentage",
                        format="0.0x"
                    )
                ],
                filters=[FilterDefinition(field="scenario", operator="eq", value="conservative")]
            ),
            analytics_question="What is the ROI for the conservative scenario?"
        )
    ],
    metadata=TemplateMetadata(
        generated_by="llm",
        llm_model="claude-sonnet-4",
        key_features=["Conservative: 2.6x ROI"],
        recommended_use_case="Financial planning"
    ),
    status="draft"
)

# Step 2: Define data schema
schema = ProspectDataSchema(
    client_id="client-livongo-diabetes",
    schema_name="roi_analysis_schema",
    table_name="roi_analysis_data",
    fields=[
        {"name": "scenario", "type": "string"},
        {"name": "savings_conservative", "type": "currency"},
        {"name": "program_costs", "type": "currency"}
    ],
    available_metrics=["roi_conservative"],
    time_fields=["date"],
    dimension_fields=["scenario"]
)

# Step 3: Validate
validation_result = validate_template_against_data_schema(template, schema)
if validation_result.is_valid:
    template.status = "approved"

# Step 4: Save to database
session = get_db_session()
db_template = DBProspectTemplate(
    client_id=UUID(template.client_id),
    name=template.name,
    description=template.description,
    category=template.category,
    target_audience=template.target_audience,
    visual_style=template.visual_style.model_dump(),
    widgets=[w.model_dump() for w in template.widgets],
    metadata=template.metadata.model_dump(),
    status=template.status
)
session.add(db_template)
session.commit()

print(f"✅ Template saved: {db_template.id}")
print(f"✅ Validation: {validation_result.is_valid}")
```

---

## Testing

### Run Template Validation Test

```bash
python -c "
from core.models.prospect_dashboard_models import *

# Create test template
template = ProspectDashboardTemplate(...)

# Create test schema
schema = ProspectDataSchema(...)

# Validate
result = validate_template_against_data_schema(template, schema)
print(f'Valid: {result.is_valid}')
print(f'Errors: {result.missing_fields}')
"
```

### Query Templates

```sql
-- List all prospect templates
SELECT id, name, category, status, target_audience
FROM prospect_dashboard_templates
WHERE client_id = 'client-uuid';

-- Get templates with data requirements
SELECT id, name,
       jsonb_array_length(widgets) as widget_count,
       widgets->0->'data_requirements'->>'query_type' as first_widget_query_type
FROM prospect_dashboard_templates;

-- Find templates missing data schemas
SELECT pdt.id, pdt.name
FROM prospect_dashboard_templates pdt
LEFT JOIN prospect_data_schemas pds ON pdt.client_id = pds.client_id
WHERE pds.id IS NULL;
```

---

## Benefits

### 1. **Explicit Data Requirements**
- Every widget declares exactly what data it needs
- SQL expressions are stored with the template
- Easy to validate before deployment

### 2. **Analytics Questions**
- Each widget answers a specific business question
- Natural language makes templates self-documenting
- Helps non-technical stakeholders understand dashboards

### 3. **Automatic Validation**
- Templates are validated against data schemas
- Catches missing fields/metrics before runtime
- Ensures data availability

### 4. **Flexible Storage**
- Templates can reference either old or new format
- Gradual migration path
- Backwards compatible

---

## Migration Path

### From Old Format to New Format

1. **Keep existing templates** in `dashboard_templates` table
2. **Create new templates** in `prospect_dashboard_templates` table
3. **prospect_dashboard_data** supports both formats via `template_id` OR `prospect_template_id`
4. **Gradual conversion** using `convert_old_template_to_new_format()`

---

## Summary

### Files Created

1. **`core/models/prospect_dashboard_models.py`** - Pydantic models
2. **`core/database/models.py`** - Updated with new tables
3. **`database/schema.sql`** - Updated with new tables
4. **`database/migrations/001_add_prospect_dashboard_templates.sql`** - Migration
5. **`PROSPECT_DASHBOARD_SYSTEM.md`** - This documentation

### Database Tables

1. **`prospect_dashboard_templates`** - Templates with data requirements
2. **`prospect_data_schemas`** - Available data schemas
3. **`prospect_dashboard_data`** - Updated to support both formats

### Next Steps

1. ✅ Create Pydantic models
2. ✅ Create database schema
3. ✅ Run migration
4. ⏳ Create API endpoints
5. ⏳ Create validation service
6. ⏳ Create example templates

---

**System is ready to store templates in the new format with validation!** 🎉
