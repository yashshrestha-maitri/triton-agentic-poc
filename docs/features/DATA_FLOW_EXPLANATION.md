# Complete Data Flow and Generation Explanation

## Question 1: What does `/results` give?

### Answer: **File-Based Template Results (NO WIDGET DATA)**

The `/results` endpoint returns **template structure only**, NOT actual widget data values.

---

### `/results` Endpoints Overview

```bash
GET /results/                  # List all result files
GET /results/{filename}        # Get specific result file
GET /results/{filename}/download  # Download result file
GET /results/stats/summary     # Statistics across all files
```

### What You Get from `/results`

**Example Response:**
```json
{
  "filename": "templates_Livongo_Health_20250124_120000.json",
  "client_name": "Livongo Health",
  "industry": "Diabetes Management",
  "generated_at": "2024-01-15T10:30:00Z",
  "total_templates": 7,
  "validation_passed": true,
  "generation_time_seconds": 244.47,
  "file_size_bytes": 33803
}
```

### What's Inside a Result File

```json
{
  "templates": [
    {
      "id": "template-abc",
      "name": "Executive ROI Dashboard",
      "category": "roi-focused",
      "targetAudience": "Health Plan",
      "widgets": [
        {
          "id": "w_roi_headline",
          "type": "kpi-card",
          "title": "24-Month ROI",
          "position": {"row": 1, "col": 1},
          "config": {"format": "percentage"}
          // ⚠️ NO DATA VALUES HERE!
        }
      ]
    }
  ],
  "metadata": {
    "client_name": "Livongo Health",
    "total_templates": 7
  }
}
```

### Important Notes About `/results`

❌ **What /results does NOT have:**
- Actual widget data values
- Prospect-specific information
- Database connection

✅ **What /results DOES have:**
- Template structure/layout
- Widget configurations
- Generation metadata
- File-based storage in `results/` directory

---

## Question 2: Where do I get the GENERATED DATA according to template?

### Answer: **Use `/prospect-data` endpoints (Database Storage)**

---

### Complete Data Retrieval Flow

```
┌─────────────────────────────────────────┐
│  1. GET TEMPLATE STRUCTURE              │
│     GET /templates/{template_id}        │
│     Returns: Widget positions, types    │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  2. GET WIDGET DATA VALUES              │
│     GET /prospect-data/{prospect_id}    │
│     Returns: Actual numbers, charts     │
└─────────────────────────────────────────┘
```

### Step-by-Step: How to Get Generated Data

#### **Step 1: Find Your Prospect ID**

```bash
# After template generation, find the demo prospect
curl "http://localhost:8000/clients/{client_id}/prospects"

# Response:
{
  "prospects": [
    {
      "id": "prospect-123-uuid",
      "name": "Demo Prospect - Livongo Health",
      "email": "demo@triton-agentic.local",
      "meta_data": {"is_demo": true}
    }
  ]
}
```

#### **Step 2: Get All Dashboard Data for Prospect**

```bash
# Get all generated data for this prospect
curl "http://localhost:8000/prospect-data/prospect-123-uuid"

# Response:
{
  "total": 7,
  "prospect_data": [
    {
      "id": "data-xyz",
      "prospect_id": "prospect-123-uuid",
      "template_id": "template-abc",
      "dashboard_data": {
        "w_roi_headline": {
          "value": 187.5,
          "display": "187.5%",
          "trend": {"value": 12.3, "direction": "up"}
        },
        "w_total_savings": {
          "value": 245000,
          "display": "$245,000"
        }
      },
      "status": "ready",
      "generated_by": "synthetic_generator",
      "generation_duration_ms": 45
    }
  ]
}
```

#### **Step 3: Get Data for Specific Template**

```bash
# Get data for one specific template
curl "http://localhost:8000/prospect-data/prospect-123-uuid/template-abc"

# Response: Same as above, but filtered to one template
```

---

### Database Tables Explained

```sql
-- Table 1: Template STRUCTURE (what widgets to show)
dashboard_templates
├── id: template-abc
├── name: "Executive ROI Dashboard"
├── widgets: [{id: "w_roi", type: "kpi-card", ...}]  ← Structure only
└── ❌ NO DATA VALUES

-- Table 2: Widget DATA VALUES (what numbers to show)
prospect_dashboard_data
├── id: data-xyz
├── prospect_id: prospect-123
├── template_id: template-abc
├── dashboard_data: {
│     "w_roi": {"value": 187.5, "display": "187.5%"}  ← ✅ ACTUAL DATA
│   }
└── status: "ready"
```

---

## Question 3: How Does Synthetic Data Generation Work According to Template Requirements?

### Answer: **Intelligent Widget-Type Based Generation**

---

### Generation Process Flow

```
Template Widget → Inspect Type & Config → Generate Appropriate Data → Store in DB
```

### How It Reads Template Requirements

```python
# Step 1: Read widget configuration from template
widget = {
    "id": "w_roi_headline",
    "type": "kpi-card",              # ← Generator reads this
    "config": {
        "format": "percentage",      # ← Generator reads this
        "trend": true,               # ← Generator reads this
        "target": 200                # ← Generator reads this
    }
}

# Step 2: Generator analyzes requirements
generator = SyntheticDataGenerator()
data = generator.generate_widget_data(widget)

# Step 3: Returns data matching requirements
{
    "value": 187.5,                   # Percentage value (50-250 range)
    "display": "187.5%",              # Formatted as percentage
    "trend": {                        # Trend included because config.trend = true
        "value": 12.3,
        "direction": "up"
    },
    "target": 200,                    # Target included because config.target = 200
    "progress": 93.75                 # Auto-calculated: 187.5/200 * 100
}
```

---

### Widget Type Detection Logic

**Location:** `core/services/data_generator.py:41-68`

```python
def generate_widget_data(self, widget):
    widget_type = widget.get("type")      # Read widget type
    config = widget.get("config", {})     # Read configuration

    # Route to appropriate generator based on type
    if widget_type == "kpi-card":
        return self._generate_kpi_data(widget)      # Generate single value
    elif widget_type == "chart":
        chart_type = widget.get("chartType")
        if chart_type == "line":
            return self._generate_line_chart_data(widget)  # Generate time series
        elif chart_type == "bar":
            return self._generate_bar_chart_data(widget)   # Generate categories
    elif widget_type == "table":
        return self._generate_table_data(widget)    # Generate rows/columns
```

---

### Generation Logic by Widget Type

#### **1. KPI Card Generation**

**Template Requirements:**
```json
{
  "type": "kpi-card",
  "config": {
    "format": "percentage",    ← Determines value type
    "trend": true,             ← Adds trend data
    "target": 200,             ← Adds target comparison
    "suffix": "months"         ← Optional suffix
  }
}
```

**Generation Logic:** (`data_generator.py:70-109`)
```python
def _generate_kpi_data(self, widget):
    config = widget.get("config", {})
    format_type = config.get("format", "number")

    # 1. Generate value based on format
    if format_type == "percentage":
        value = random.uniform(50, 250)        # ← Percentage range
        display = f"{value}%"
    elif format_type == "currency":
        value = random.randint(10000, 500000)  # ← Currency range
        display = f"${value:,}"
    elif format_type == "number":
        value = random.randint(100, 10000)     # ← Number range
        suffix = config.get("suffix", "")
        display = f"{value:,}{suffix}"

    # 2. Add trend if configured
    if config.get("trend"):
        trend_value = random.uniform(-15, 25)   # ← Trend range: -15% to +25%
        data["trend"] = {
            "value": trend_value,
            "direction": "up" if trend_value > 0 else "down"
        }

    # 3. Add target if configured
    if config.get("target"):
        data["target"] = config["target"]
        data["progress"] = (value / config["target"]) * 100

    return data
```

**Generated Output:**
```json
{
  "value": 187.5,
  "display": "187.5%",
  "timestamp": "2025-11-28T12:00:00Z",
  "trend": {
    "value": 12.3,
    "direction": "up",
    "display": "+12.3%"
  },
  "target": 200,
  "progress": 93.75
}
```

---

#### **2. Line Chart Generation**

**Template Requirements:**
```json
{
  "type": "chart",
  "chartType": "line",
  "config": {
    "dataPoints": 12,          ← Number of time periods
    "series": [                ← Multiple data series
      {"name": "Total Savings"},
      {"name": "Program Costs"}
    ]
  }
}
```

**Generation Logic:** (`data_generator.py:111-116`)
```python
def _generate_line_chart_data(self, widget):
    config = widget.get("config", {})
    num_points = config.get("dataPoints", 12)   # ← Read from config

    # 1. Generate time labels (12 months)
    dates = [(today - timedelta(days=30*i)).strftime("%Y-%m-%d")
             for i in range(num_points)]

    # 2. Generate series for each configured series
    series_count = len(config.get("series", []))  # ← Read series count
    series_data = []

    for i in range(series_count):
        series_name = config["series"][i]["name"]  # ← Read series name

        # Generate trending data with noise
        base_value = random.randint(1000, 5000)
        trend = random.choice([-50, -20, 20, 50])  # ← Random trend direction

        values = []
        for j in range(num_points):
            noise = random.randint(-200, 200)       # ← Add randomness
            value = base_value + (j * trend) + noise
            values.append(max(0, value))

        series_data.append({"name": series_name, "data": values})

    return {"labels": dates, "series": series_data}
```

**Generated Output:**
```json
{
  "labels": ["2024-01", "2024-02", "2024-03", ...],
  "series": [
    {
      "name": "Total Savings",
      "data": [1200, 1350, 1450, 1600, ...]
    },
    {
      "name": "Program Costs",
      "data": [800, 850, 900, 950, ...]
    }
  ],
  "timestamp": "2025-11-28T12:00:00Z"
}
```

---

#### **3. Bar Chart Generation**

**Template Requirements:**
```json
{
  "type": "chart",
  "chartType": "bar",
  "config": {
    "categories": ["Q1", "Q2", "Q3", "Q4"],  ← Category names
    "series": [{"name": "Revenue"}]
  }
}
```

**Generation Logic:** (`data_generator.py:118-145`)
```python
def _generate_bar_chart_data(self, widget):
    config = widget.get("config", {})

    # 1. Read categories from config (or use defaults)
    categories = config.get("categories", [
        "Category A", "Category B", "Category C"
    ])

    # 2. Generate values for each category
    for series in config.get("series", []):
        values = [random.randint(500, 5000) for _ in categories]
        series_data.append({
            "name": series["name"],
            "data": values
        })

    return {"categories": categories, "series": series_data}
```

**Generated Output:**
```json
{
  "categories": ["Q1", "Q2", "Q3", "Q4"],
  "series": [
    {
      "name": "Revenue",
      "data": [2500, 3200, 2800, 3500]
    }
  ],
  "timestamp": "2025-11-28T12:00:00Z"
}
```

---

#### **4. Table Generation**

**Template Requirements:**
```json
{
  "type": "table",
  "config": {
    "columns": [
      {"key": "name", "label": "Category"},
      {"key": "value", "label": "Amount"},
      {"key": "change", "label": "Change %"}
    ],
    "rows": 5                    ← Number of rows
  }
}
```

**Generation Logic:** (`data_generator.py:208-241`)
```python
def _generate_table_data(self, widget):
    config = widget.get("config", {})
    columns = config.get("columns", [])    # ← Read column definitions
    num_rows = config.get("rows", 5)       # ← Read row count

    rows = []
    for i in range(num_rows):
        row = {}
        for col in columns:
            # Generate appropriate data based on column key
            if col["key"] == "name":
                row["name"] = f"Item {i+1}"
            elif col["key"] == "value":
                row["value"] = random.randint(1000, 10000)
            elif col["key"] == "change":
                row["change"] = round(random.uniform(-20, 30), 1)
        rows.append(row)

    return {"columns": columns, "rows": rows}
```

**Generated Output:**
```json
{
  "columns": [
    {"key": "name", "label": "Category"},
    {"key": "value", "label": "Amount"},
    {"key": "change", "label": "Change %"}
  ],
  "rows": [
    {"name": "Item 1", "value": 2500, "change": 12.5},
    {"name": "Item 2", "value": 3200, "change": -8.3},
    {"name": "Item 3", "value": 1800, "change": 22.1}
  ],
  "totalRows": 3,
  "timestamp": "2025-11-28T12:00:00Z"
}
```

---

### Complete Generation Workflow

```
┌────────────────────────────────────────────────────────────┐
│  1. Template Generation (Celery Task)                      │
│     - AI generates 7 templates with widget configs         │
│     - Stores in dashboard_templates table                  │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ↓
┌────────────────────────────────────────────────────────────┐
│  2. Prospect Identification                                │
│     - Get/Create demo prospect for client                  │
│     - One demo prospect per client                         │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ↓
┌────────────────────────────────────────────────────────────┐
│  3. Data Generation Loop (for each template)               │
│     For template in templates:                             │
│       ┌────────────────────────────────────┐              │
│       │ 3a. Load Template from DB          │              │
│       │     widgets = template.widgets     │              │
│       └──────────────┬─────────────────────┘              │
│                      ↓                                      │
│       ┌────────────────────────────────────┐              │
│       │ 3b. For Each Widget:               │              │
│       │   - Read widget.type               │              │
│       │   - Read widget.config             │              │
│       │   - Generate appropriate data      │              │
│       │   - Store in dictionary            │              │
│       └──────────────┬─────────────────────┘              │
│                      ↓                                      │
│       ┌────────────────────────────────────┐              │
│       │ 3c. Store in Database              │              │
│       │   INSERT INTO                      │              │
│       │   prospect_dashboard_data          │              │
│       │   VALUES (prospect_id,             │              │
│       │          template_id,              │              │
│       │          dashboard_data: {...})    │              │
│       └────────────────────────────────────┘              │
└────────────────────────────────────────────────────────────┘
```

---

## Summary: Three Different Data Stores

### 1. `/results` - File-Based (Direct API Only)
- **Location:** `results/templates_*.json` files
- **Contains:** Template structure only
- **Use Case:** Prototype/testing with direct REST API
- **❌ No Widget Data Values**

### 2. `dashboard_templates` Table (Database)
- **Contains:** Template structure (widget configs, positions)
- **Use Case:** Reusable template definitions
- **❌ No Widget Data Values**

### 3. `prospect_dashboard_data` Table (Database) ✅
- **Contains:** Actual widget data values
- **Use Case:** Prospect-specific dashboard data
- **✅ THIS IS WHERE YOUR GENERATED DATA IS!**

---

## How to Access Your Generated Data

```bash
# Step 1: Find prospect
curl "http://localhost:8000/clients/{client_id}/prospects"

# Step 2: Get all data for prospect
curl "http://localhost:8000/prospect-data/{prospect_id}"

# Step 3: Get data for specific template
curl "http://localhost:8000/prospect-data/{prospect_id}/{template_id}"
```

---

**The generated data is in `prospect_dashboard_data` table, accessible via `/prospect-data` endpoints!** 🎯
