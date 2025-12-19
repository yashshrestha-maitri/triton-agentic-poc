# Data Lineage Step-by-Step: What Gets Added at Each Process

**Purpose:** Show exactly what lineage data is created/updated at each stage from document analysis to dashboard generation

**Related Documents:**
- [EXTRACTION_HALLUCINATION_AND_LINEAGE_PLAN.md](./EXTRACTION_HALLUCINATION_AND_LINEAGE_PLAN.md) - Complete implementation plan
- [DATA_LINEAGE_TRACKING.md](./features/DATA_LINEAGE_TRACKING.md) - Storage requirements guide
- [ROI_MODEL_RESEARCH_FLOW_UPDATED.md](./architecture-current/ROI_MODEL_RESEARCH_FLOW_UPDATED.md) - ROI Model architecture

---

## Overview: Lineage Data Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    LINEAGE RECORD LIFECYCLE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Document Analysis Agent                                │
│  └─ CREATES lineage record with 10 mandatory fields            │
│                                                                 │
│  Step 2: Web Search Agent (if needed)                          │
│  └─ CREATES separate lineage record for web search data       │
│                                                                 │
│  Step 3: ROI Classification Agent                              │
│  └─ No lineage changes (just reads extractions)               │
│                                                                 │
│  Step 4: ROI Model Builder Agent                               │
│  └─ UPDATES: used_in_roi_models array                         │
│                                                                 │
│  Step 5: Template Generator Agent                              │
│  └─ UPDATES: used_in_dashboards array (via ROI Model link)    │
│                                                                 │
│  Step 6: Prospect Data Generation                              │
│  └─ UPDATES: last_accessed timestamp                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Document Analysis Agent

### When It Runs
- User uploads document (PDF, DOCX, TXT) to S3
- Research API endpoint: `POST /research/document-analysis`
- Agent analyzes document and extracts value propositions, metrics, outcomes

### What Gets CREATED

**Lineage Record Status:** ✅ **FULLY CREATED**

```python
# All 10 mandatory fields populated at this stage

extraction_lineage = {
    # FIELD 1: extraction_id
    "extraction_id": "uuid-abc-123-def-456",  # NEW UUID generated

    # FIELD 2: extraction_timestamp
    "extraction_timestamp": "2025-12-17T16:30:45Z",  # Current UTC time

    # FIELD 3: source_document_url
    "source_document_url": "s3://triton-docs/client_123/roi_sheet.pdf",  # S3 path

    # FIELD 4: source_document_hash
    "source_document_hash": "sha256:a1b2c3d4e5f6...",  # SHA256 of PDF bytes

    # FIELD 5: extraction_agent
    "extraction_agent": "DocumentAnalysisAgent",  # Agent name

    # FIELD 6: extraction_model
    "extraction_model": "us.anthropic.claude-sonnet-4-20250514-v1:0",  # Model ID

    # FIELD 7: verification_status
    "verification_status": "verified",  # Result of Layer 5 verification

    # FIELD 8: verification_issues
    "verification_issues": [],  # Empty if verified, or ["issue 1", "issue 2"]

    # FIELD 9: used_in_roi_models
    "used_in_roi_models": [],  # EMPTY - populated later in Step 4

    # FIELD 10: used_in_dashboards
    "used_in_dashboards": [],  # EMPTY - populated later in Step 5

    # HOUSEKEEPING
    "created_at": "2025-12-17T16:30:45Z",
    "updated_at": "2025-12-17T16:30:45Z"
}
```

### How It's Populated

**Step 1.1: Document Retrieval**
```python
# Load document from S3
document_bytes = s3_client.get_object(
    Bucket='triton-docs',
    Key='client_123/roi_sheet.pdf'
)['Body'].read()

# Compute SHA256 hash
document_hash = hashlib.sha256(document_bytes).hexdigest()
# → "a1b2c3d4e5f6..."

# Store for lineage
source_document_url = "s3://triton-docs/client_123/roi_sheet.pdf"
source_document_hash = f"sha256:{document_hash}"
```

**Step 1.2: Agent Execution**
```python
# Extract text from document
document_text = extract_text_from_pdf(document_bytes)

# Run DocumentAnalysisAgent
result = await document_analysis_agent.run(
    document_text=document_text,
    document_url=source_document_url
)

# Result includes:
# - extracted_value_propositions (with source_text, metrics, etc.)
# - clinical_outcomes
# - financial_metrics
# - overall_confidence
```

**Step 1.3: 5-Layer Validation**
```python
# Layer 1-4: JSON extraction, parsing, Pydantic, business rules
# Layer 5: Source verification
verification_result = verify_extraction_against_source(
    extraction=result.extracted_value_propositions[0],
    full_document_text=document_text,
    document_pages=document_pages
)

# verification_result = {
#   "is_hallucinated": False,
#   "verification_status": "verified",
#   "verification_issues": [],
#   "confidence_adjustment": 1.0
# }
```

**Step 1.4: Lineage Record Creation**
```python
# Generate extraction ID
extraction_id = uuid4()

# Create lineage record
lineage = ExtractionLineage(
    extraction_id=extraction_id,
    extraction_timestamp=datetime.utcnow(),
    source_document_url=source_document_url,
    source_document_hash=source_document_hash,
    extraction_agent="DocumentAnalysisAgent",
    extraction_model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    verification_status=verification_result["verification_status"],
    verification_issues=verification_result["verification_issues"],
    used_in_roi_models=[],  # Empty for now
    used_in_dashboards=[]   # Empty for now
)

# Store in PostgreSQL
await db.insert("extraction_lineage", lineage)

# Link extraction to lineage
result.extracted_value_propositions[0].extraction_id = extraction_id
```

### Database State After Step 1

```sql
-- extraction_lineage table
SELECT * FROM extraction_lineage WHERE extraction_id = 'uuid-abc-123-def-456';

-- Result:
extraction_id              | uuid-abc-123-def-456
extraction_timestamp       | 2025-12-17 16:30:45
source_document_url        | s3://triton-docs/client_123/roi_sheet.pdf
source_document_hash       | sha256:a1b2c3d4e5f6...
extraction_agent           | DocumentAnalysisAgent
extraction_model           | us.anthropic.claude-sonnet-4-20250514-v1:0
verification_status        | verified
verification_issues        | {}  -- Empty array
used_in_roi_models         | {}  -- Empty array ← TO BE POPULATED
used_in_dashboards         | {}  -- Empty array ← TO BE POPULATED
created_at                 | 2025-12-17 16:30:45
updated_at                 | 2025-12-17 16:30:45
```

---

## Step 2: Web Search Agent (Parallel to Step 1)

### When It Runs
- Research API endpoint: `POST /research/web-search`
- Used for finding industry benchmark data
- Searches DuckDuckGo/Tavily for CMS, CDC, HEDIS data
- **Runs in parallel** with DocumentAnalysisAgent (separate job)

### What Gets CREATED

**Lineage Record Status:** ✅ **FULLY CREATED** (separate from document lineage)

```python
# Separate lineage record for web search results

web_search_lineage = {
    # FIELD 1: extraction_id
    "extraction_id": "uuid-xyz-789-ghi-012",  # DIFFERENT UUID from document

    # FIELD 2: extraction_timestamp
    "extraction_timestamp": "2025-12-17T16:31:20Z",  # When search performed

    # FIELD 3: source_document_url
    "source_document_url": "https://www.cms.gov/medicare/quality/initiatives/hospital-compare",  # Web URL

    # FIELD 4: source_document_hash
    "source_document_hash": "sha256:b2c3d4e5f6g7...",  # SHA256 of scraped HTML

    # FIELD 5: extraction_agent
    "extraction_agent": "WebSearchAgent",  # Different agent

    # FIELD 6: extraction_model
    "extraction_model": "us.anthropic.claude-sonnet-4-20250514-v1:0",  # Same model

    # FIELD 7: verification_status
    "verification_status": "verified",  # Verified against scraped content

    # FIELD 8: verification_issues
    "verification_issues": [],

    # FIELD 9: used_in_roi_models
    "used_in_roi_models": [],  # EMPTY - populated later

    # FIELD 10: used_in_dashboards
    "used_in_dashboards": [],  # EMPTY - populated later

    # HOUSEKEEPING
    "created_at": "2025-12-17T16:31:20Z",
    "updated_at": "2025-12-17T16:31:20Z"
}
```

### How It's Populated

**Step 2.1: Web Search Execution**
```python
# Search for benchmark data
search_query = "hospital readmission rates CMS 2024"
search_results = await google_search_tool.search(
    query=search_query,
    provider="duckduckgo"  # or "tavily"
)

# search_results = [
#   {"url": "https://cms.gov/...", "title": "...", "snippet": "..."},
#   ...
# ]
```

**Step 2.2: Web Page Scraping**
```python
# Scrape top result
scraped_content = await web_scraper.scrape(
    url="https://www.cms.gov/medicare/quality/initiatives/hospital-compare"
)

# Compute hash of scraped content
content_hash = hashlib.sha256(scraped_content.encode()).hexdigest()
# → "b2c3d4e5f6g7..."
```

**Step 2.3: Agent Extraction**
```python
# Run WebSearchAgent to extract structured data
result = await web_search_agent.run(
    scraped_content=scraped_content,
    search_query=search_query,
    source_url="https://www.cms.gov/..."
)

# Result includes:
# - extracted_metrics: [{"metric_name": "30-day readmission rate", "value": "15.2%", ...}]
# - source_text: "The national 30-day readmission rate is 15.2%..."
# - confidence: 0.92
```

**Step 2.4: Lineage Record Creation**
```python
# Generate extraction ID
extraction_id = uuid4()

# Create lineage record (web search variant)
lineage = ExtractionLineage(
    extraction_id=extraction_id,
    extraction_timestamp=datetime.utcnow(),
    source_document_url="https://www.cms.gov/...",  # Web URL, not S3
    source_document_hash=f"sha256:{content_hash}",
    extraction_agent="WebSearchAgent",  # Different agent
    extraction_model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    verification_status="verified",
    verification_issues=[],
    used_in_roi_models=[],
    used_in_dashboards=[]
)

# Store in PostgreSQL
await db.insert("extraction_lineage", lineage)
```

### Database State After Step 2

```sql
-- Now have TWO lineage records

-- Record 1: From DocumentAnalysisAgent
SELECT * FROM extraction_lineage WHERE extraction_agent = 'DocumentAnalysisAgent';
-- uuid-abc-123-def-456 | s3://triton-docs/client_123/roi_sheet.pdf

-- Record 2: From WebSearchAgent
SELECT * FROM extraction_lineage WHERE extraction_agent = 'WebSearchAgent';
-- uuid-xyz-789-ghi-012 | https://www.cms.gov/medicare/quality/...
```

---

## Step 3: ROI Classification Agent

### When It Runs
- After Step 1 and Step 2 complete
- Receives extractions from both DocumentAnalysisAgent and WebSearchAgent
- Determines which ROI Model Type (B1-B13) to use

### What Gets CHANGED

**Lineage Record Status:** ❌ **NO CHANGES**

This agent only **reads** extractions, doesn't modify lineage records.

```python
# ROI Classification Agent receives:
extractions = [
    ExtractedValueProposition(
        extraction_id="uuid-abc-123-def-456",  # From DocumentAnalysisAgent
        name="Cost Reduction Through Preventive Care",
        metrics={"roi": "250%", "payback_months": 12},
        ...
    ),
    ExtractedFinancialMetric(
        extraction_id="uuid-xyz-789-ghi-012",  # From WebSearchAgent
        metric_name="National Readmission Rate",
        value="15.2%",
        ...
    )
]

# Agent determines ROI Model Type
classification_result = await roi_classification_agent.run(extractions)
# → roi_model_type = "B3" (Cost Reduction Model)

# NO LINEAGE UPDATES - just classification
```

### Database State After Step 3

```sql
-- No changes to extraction_lineage table
SELECT * FROM extraction_lineage;
-- Same 2 records as after Step 2
```

---

## Step 4: ROI Model Builder Agent

### When It Runs
- After Step 3 classification completes
- Builds ROI Model using extractions
- Saves ROI Model to database

### What Gets UPDATED

**Lineage Record Status:** ✅ **UPDATED: used_in_roi_models**

```python
# ROI Model Builder receives:
# - roi_model_type = "B3"
# - extractions with extraction_ids

# Build ROI Model
roi_model = await roi_model_builder_agent.run(
    roi_model_type="B3",
    extractions=extractions,
    client_id="client_123",
    prospect_id="prospect_456"
)

# Save ROI Model
roi_model_id = await db.insert("roi_models", {
    "model_id": "roi_model_789",
    "model_type": "B3",
    "source_extractions": [
        "uuid-abc-123-def-456",  # From DocumentAnalysisAgent
        "uuid-xyz-789-ghi-012"   # From WebSearchAgent
    ],
    "client_id": "client_123",
    "prospect_id": "prospect_456",
    "created_at": datetime.utcnow()
})
```

### Lineage Update Logic

**Step 4.1: Link Extractions to ROI Model**
```python
# Update lineage for EACH extraction used
async def link_extraction_to_roi_model(
    extraction_ids: List[UUID],
    roi_model_id: UUID
):
    """Update used_in_roi_models array."""

    await db.execute("""
        UPDATE extraction_lineage
        SET
            used_in_roi_models = array_append(used_in_roi_models, $1),
            updated_at = NOW()
        WHERE extraction_id = ANY($2)
    """, roi_model_id, extraction_ids)

# Execute
await link_extraction_to_roi_model(
    extraction_ids=["uuid-abc-123-def-456", "uuid-xyz-789-ghi-012"],
    roi_model_id="roi_model_789"
)
```

### Database State After Step 4

```sql
-- extraction_lineage table NOW UPDATED

-- Record 1: Document extraction
SELECT * FROM extraction_lineage WHERE extraction_id = 'uuid-abc-123-def-456';

extraction_id              | uuid-abc-123-def-456
...
used_in_roi_models         | {roi_model_789}  ← UPDATED! (was empty)
used_in_dashboards         | {}               ← Still empty
updated_at                 | 2025-12-17 16:32:15  ← Updated timestamp

-- Record 2: Web search extraction
SELECT * FROM extraction_lineage WHERE extraction_id = 'uuid-xyz-789-ghi-012';

extraction_id              | uuid-xyz-789-ghi-012
...
used_in_roi_models         | {roi_model_789}  ← UPDATED! (was empty)
used_in_dashboards         | {}               ← Still empty
updated_at                 | 2025-12-17 16:32:15  ← Updated timestamp
```

**Bi-Directional Linking Established:**
```
Forward:  ROI Model → source_extractions → [extraction IDs]
Backward: Extraction → used_in_roi_models → [ROI Model IDs]
```

---

## Step 5: Template Generator Agent

### When It Runs
- After ROI Model is built
- Generates dashboard template variations
- Links template to ROI Model (not directly to extractions)

### What Gets UPDATED

**Lineage Record Status:** ✅ **UPDATED: used_in_dashboards** (indirectly via ROI Model)

```python
# Template Generator receives:
# - roi_model_id = "roi_model_789"
# - prospect_id = "prospect_456"

# Generate dashboard template
template = await template_generator_agent.run(
    roi_model_id="roi_model_789",
    prospect_id="prospect_456",
    client_id="client_123"
)

# Save dashboard template
dashboard_id = await db.insert("dashboard_templates", {
    "template_id": "dashboard_abc",
    "template_name": "Cost Reduction Dashboard",
    "roi_model_id": "roi_model_789",  # Links to ROI Model
    "prospect_id": "prospect_456",
    "widgets": [...],
    "created_at": datetime.utcnow()
})
```

### Lineage Update Logic

**Step 5.1: Find Extractions via ROI Model**
```python
# Dashboard doesn't directly know extraction IDs
# Must go through ROI Model

async def link_roi_model_to_dashboard(
    roi_model_id: UUID,
    dashboard_id: UUID
):
    """Update used_in_dashboards for all extractions in ROI Model."""

    await db.execute("""
        UPDATE extraction_lineage
        SET
            used_in_dashboards = array_append(used_in_dashboards, $1),
            updated_at = NOW()
        WHERE $2 = ANY(used_in_roi_models)
    """, dashboard_id, roi_model_id)

# Execute
await link_roi_model_to_dashboard(
    roi_model_id="roi_model_789",
    dashboard_id="dashboard_abc"
)
```

### Database State After Step 5

```sql
-- extraction_lineage table NOW FULLY POPULATED

-- Record 1: Document extraction
SELECT * FROM extraction_lineage WHERE extraction_id = 'uuid-abc-123-def-456';

extraction_id              | uuid-abc-123-def-456
extraction_timestamp       | 2025-12-17 16:30:45
source_document_url        | s3://triton-docs/client_123/roi_sheet.pdf
source_document_hash       | sha256:a1b2c3d4e5f6...
extraction_agent           | DocumentAnalysisAgent
extraction_model           | us.anthropic.claude-sonnet-4-20250514-v1:0
verification_status        | verified
verification_issues        | {}
used_in_roi_models         | {roi_model_789}     ← Populated in Step 4
used_in_dashboards         | {dashboard_abc}     ← UPDATED! (was empty)
created_at                 | 2025-12-17 16:30:45
updated_at                 | 2025-12-17 16:33:10 ← Updated timestamp

-- Record 2: Web search extraction
SELECT * FROM extraction_lineage WHERE extraction_id = 'uuid-xyz-789-ghi-012';

extraction_id              | uuid-xyz-789-ghi-012
...
used_in_roi_models         | {roi_model_789}     ← Populated in Step 4
used_in_dashboards         | {dashboard_abc}     ← UPDATED! (was empty)
updated_at                 | 2025-12-17 16:33:10 ← Updated timestamp
```

**Complete Traceability Established:**
```
Extraction (uuid-abc-123)
  → used_in_roi_models: [roi_model_789]
    → used_in_dashboards: [dashboard_abc]

ROI Model (roi_model_789)
  → source_extractions: [uuid-abc-123, uuid-xyz-789]

Dashboard (dashboard_abc)
  → roi_model_id: roi_model_789
```

---

## Step 6: Prospect Data Generation (Optional)

### When It Runs
- When dashboard is loaded by frontend
- Generates prospect-specific widget data
- May re-access extractions for data refresh

### What Gets UPDATED

**Lineage Record Status:** ✅ **UPDATED: last_accessed** (if Phase 2/3 fields implemented)

```python
# When prospect views dashboard
prospect_data = await generate_prospect_dashboard_data(
    dashboard_id="dashboard_abc",
    prospect_id="prospect_456"
)

# System retrieves extractions
extractions = await db.query("""
    SELECT el.*
    FROM extraction_lineage el
    WHERE 'dashboard_abc' = ANY(el.used_in_dashboards)
""")
# → Returns: [uuid-abc-123-def-456, uuid-xyz-789-ghi-012]

# OPTIONAL: Update last_accessed (Phase 2/3 feature)
await db.execute("""
    UPDATE extraction_lineage
    SET
        last_accessed = NOW(),
        access_count = access_count + 1
    WHERE 'dashboard_abc' = ANY(used_in_dashboards)
""")
```

### Database State After Step 6 (Phase 2/3 only)

```sql
-- If Phase 2/3 fields implemented:

SELECT extraction_id, last_accessed, access_count
FROM extraction_lineage
WHERE 'dashboard_abc' = ANY(used_in_dashboards);

-- Result:
uuid-abc-123-def-456 | 2025-12-17 16:45:00 | 1
uuid-xyz-789-ghi-012 | 2025-12-17 16:45:00 | 1
```

---

## Complete Lineage Timeline

### Single Extraction Journey

```
TIME    | PROCESS                       | LINEAGE FIELD UPDATED
--------|-------------------------------|----------------------------------
16:30   | DocumentAnalysisAgent runs    | ✅ ALL 10 mandatory fields created
        |                               |    - extraction_id: uuid-abc-123
        |                               |    - source_document_url: s3://...
        |                               |    - extraction_agent: DocumentAnalysisAgent
        |                               |    - verification_status: verified
        |                               |    - used_in_roi_models: []
        |                               |    - used_in_dashboards: []
--------|-------------------------------|----------------------------------
16:31   | WebSearchAgent runs           | ✅ NEW lineage record created
        |                               |    - extraction_id: uuid-xyz-789
        |                               |    - source_document_url: https://cms.gov...
        |                               |    - extraction_agent: WebSearchAgent
--------|-------------------------------|----------------------------------
16:32   | ROI Classification Agent      | ❌ NO CHANGES (read-only)
--------|-------------------------------|----------------------------------
16:32   | ROI Model Builder Agent       | ✅ UPDATES both extractions:
        |                               |    - used_in_roi_models: [roi_model_789]
        |                               |    - updated_at: 2025-12-17 16:32:15
--------|-------------------------------|----------------------------------
16:33   | Template Generator Agent      | ✅ UPDATES both extractions:
        |                               |    - used_in_dashboards: [dashboard_abc]
        |                               |    - updated_at: 2025-12-17 16:33:10
--------|-------------------------------|----------------------------------
16:45   | Prospect views dashboard      | ✅ UPDATES (Phase 2/3 only):
        |                               |    - last_accessed: 2025-12-17 16:45:00
        |                               |    - access_count: 1
--------|-------------------------------|----------------------------------
```

---

## Summary Tables

### Fields Populated by Each Agent

| Agent | Creates Record? | Fields Populated | Fields Updated |
|-------|-----------------|------------------|----------------|
| **DocumentAnalysisAgent** | ✅ Yes | All 10 mandatory fields | None |
| **WebSearchAgent** | ✅ Yes | All 10 mandatory fields | None |
| **ROI Classification Agent** | ❌ No | None | None |
| **ROI Model Builder Agent** | ❌ No | None | `used_in_roi_models` |
| **Template Generator Agent** | ❌ No | None | `used_in_dashboards` |
| **Prospect Data Generation** | ❌ No | None | `last_accessed`, `access_count` (Phase 2/3) |

---

### Mandatory Fields Population Timeline

| Field | Step 1 (Document) | Step 2 (Web) | Step 4 (ROI) | Step 5 (Template) |
|-------|-------------------|--------------|--------------|-------------------|
| `extraction_id` | ✅ Created | ✅ Created | - | - |
| `extraction_timestamp` | ✅ Created | ✅ Created | - | - |
| `source_document_url` | ✅ Created | ✅ Created | - | - |
| `source_document_hash` | ✅ Created | ✅ Created | - | - |
| `extraction_agent` | ✅ Created | ✅ Created | - | - |
| `extraction_model` | ✅ Created | ✅ Created | - | - |
| `verification_status` | ✅ Created | ✅ Created | - | - |
| `verification_issues` | ✅ Created | ✅ Created | - | - |
| `used_in_roi_models` | [] Empty | [] Empty | ✅ Updated | - |
| `used_in_dashboards` | [] Empty | [] Empty | [] Empty | ✅ Updated |

---

## Implementation Code Examples

### Step 1: Document Analysis with Lineage Creation

```python
async def analyze_document_with_lineage(
    document_url: str,
    document_bytes: bytes
) -> DocumentAnalysisResult:
    """
    Analyze document and create lineage record.
    """

    # 1. Compute document hash
    document_hash = hashlib.sha256(document_bytes).hexdigest()

    # 2. Extract text
    document_text = extract_text_from_pdf(document_bytes)

    # 3. Run DocumentAnalysisAgent
    result = await document_analysis_agent.run(
        document_text=document_text,
        document_url=document_url
    )

    # 4. Create lineage records for each extraction
    for extraction in result.extracted_value_propositions:
        extraction_id = uuid4()

        lineage = ExtractionLineage(
            extraction_id=extraction_id,
            extraction_timestamp=datetime.utcnow(),
            source_document_url=document_url,
            source_document_hash=f"sha256:{document_hash}",
            extraction_agent="DocumentAnalysisAgent",
            extraction_model=config.DEFAULT_MODEL_NAME,
            verification_status=extraction.verification_status,
            verification_issues=extraction.verification_issues,
            used_in_roi_models=[],  # Empty initially
            used_in_dashboards=[]   # Empty initially
        )

        await db.insert("extraction_lineage", lineage)
        extraction.extraction_id = extraction_id

    return result
```

---

### Step 4: ROI Model Builder with Lineage Update

```python
async def build_roi_model_with_lineage(
    roi_model_type: str,
    extractions: List[ExtractedValueProposition],
    client_id: str,
    prospect_id: str
) -> str:
    """
    Build ROI Model and update extraction lineage.
    """

    # 1. Build ROI Model
    roi_model = await roi_model_builder_agent.run(
        roi_model_type=roi_model_type,
        extractions=extractions,
        client_id=client_id,
        prospect_id=prospect_id
    )

    # 2. Save ROI Model
    extraction_ids = [e.extraction_id for e in extractions]

    roi_model_id = await db.insert("roi_models", {
        "model_id": str(uuid4()),
        "model_type": roi_model_type,
        "source_extractions": extraction_ids,  # Store extraction IDs
        "client_id": client_id,
        "prospect_id": prospect_id,
        "created_at": datetime.utcnow()
    })

    # 3. Update lineage: Link extractions to ROI Model
    await db.execute("""
        UPDATE extraction_lineage
        SET
            used_in_roi_models = array_append(used_in_roi_models, $1),
            updated_at = NOW()
        WHERE extraction_id = ANY($2)
    """, roi_model_id, extraction_ids)

    return roi_model_id
```

---

### Step 5: Template Generation with Lineage Update

```python
async def generate_dashboard_with_lineage(
    roi_model_id: str,
    prospect_id: str,
    client_id: str
) -> str:
    """
    Generate dashboard template and update extraction lineage.
    """

    # 1. Generate template
    template = await template_generator_agent.run(
        roi_model_id=roi_model_id,
        prospect_id=prospect_id,
        client_id=client_id
    )

    # 2. Save dashboard template
    dashboard_id = await db.insert("dashboard_templates", {
        "template_id": str(uuid4()),
        "template_name": template.name,
        "roi_model_id": roi_model_id,  # Link to ROI Model
        "prospect_id": prospect_id,
        "widgets": template.widgets,
        "created_at": datetime.utcnow()
    })

    # 3. Update lineage: Link extractions to dashboard
    # Note: Uses ROI Model as intermediary
    await db.execute("""
        UPDATE extraction_lineage
        SET
            used_in_dashboards = array_append(used_in_dashboards, $1),
            updated_at = NOW()
        WHERE $2 = ANY(used_in_roi_models)
    """, dashboard_id, roi_model_id)

    return dashboard_id
```

---

## Querying Lineage Data

### Query 1: Find All Extractions in a Dashboard

```sql
-- Given dashboard_id, find all extractions
SELECT
    el.extraction_id,
    el.source_document_url,
    el.extraction_agent,
    el.verification_status
FROM extraction_lineage el
WHERE 'dashboard_abc' = ANY(el.used_in_dashboards);
```

**Result:**
```
uuid-abc-123-def-456 | s3://triton-docs/client_123/roi_sheet.pdf | DocumentAnalysisAgent | verified
uuid-xyz-789-ghi-012 | https://www.cms.gov/... | WebSearchAgent | verified
```

---

### Query 2: Find All Dashboards Using a Document

```sql
-- Given source_document_hash, find affected dashboards
SELECT DISTINCT
    unnest(el.used_in_dashboards) AS dashboard_id,
    dt.template_name,
    p.company_name AS prospect_name
FROM extraction_lineage el
LEFT JOIN dashboard_templates dt ON dt.template_id = ANY(el.used_in_dashboards)
LEFT JOIN prospects p ON p.id = dt.prospect_id
WHERE el.source_document_hash = 'sha256:a1b2c3d4e5f6...';
```

**Result:**
```
dashboard_abc | Cost Reduction Dashboard | Blue Shield Regional
dashboard_def | Clinical Outcomes Dashboard | Anthem Northeast
```

---

### Query 3: Complete Audit Trail

```sql
-- Trace extraction from source to dashboards
SELECT
    el.extraction_id,
    el.source_document_url AS "Source",
    el.extraction_agent AS "Extracted By",
    el.extraction_timestamp AS "When",
    el.verification_status AS "Verified?",
    unnest(el.used_in_roi_models) AS "ROI Model",
    unnest(el.used_in_dashboards) AS "Dashboard"
FROM extraction_lineage el
WHERE el.extraction_id = 'uuid-abc-123-def-456';
```

**Result:**
```
extraction_id           | uuid-abc-123-def-456
Source                  | s3://triton-docs/client_123/roi_sheet.pdf
Extracted By            | DocumentAnalysisAgent
When                    | 2025-12-17 16:30:45
Verified?               | verified
ROI Model               | roi_model_789
Dashboard               | dashboard_abc
```

---

## Key Takeaways

### 1. **Two Agents Create Lineage Records**
- **DocumentAnalysisAgent**: Creates lineage for PDF/DOCX/TXT extractions
- **WebSearchAgent**: Creates separate lineage for web search results

### 2. **Two Agents Update Lineage Records**
- **ROI Model Builder**: Updates `used_in_roi_models` array
- **Template Generator**: Updates `used_in_dashboards` array

### 3. **One Agent Doesn't Touch Lineage**
- **ROI Classification Agent**: Read-only, no lineage changes

### 4. **Arrays Enable Many-to-Many Relationships**
- Single extraction can be used in multiple ROI Models
- Single extraction can appear in multiple dashboards
- PostgreSQL GIN indexes make array queries fast

### 5. **Bi-Directional Traceability**
```
Forward:  Document → Extraction → ROI Model → Dashboard
Backward: Dashboard → ROI Model → Extraction → Document
```

---

## Next Steps

1. **Review this flow** - Confirm it matches your system architecture
2. **Implement Step 1** - DocumentAnalysisAgent lineage creation (see Section 15 of EXTRACTION_HALLUCINATION_AND_LINEAGE_PLAN.md)
3. **Implement Step 2** - WebSearchAgent lineage creation
4. **Implement Step 4** - ROI Model Builder lineage updates
5. **Implement Step 5** - Template Generator lineage updates
6. **Test end-to-end** - Verify complete audit trail works

---

**Document Status:** ✅ Complete
**Last Updated:** December 17, 2025
**Related Docs:**
- [EXTRACTION_HALLUCINATION_AND_LINEAGE_PLAN.md](./EXTRACTION_HALLUCINATION_AND_LINEAGE_PLAN.md)
- [DATA_LINEAGE_TRACKING.md](./features/DATA_LINEAGE_TRACKING.md)
