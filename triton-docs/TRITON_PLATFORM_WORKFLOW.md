# Triton Platform - Workflow & Architecture

## Overview
The Triton Platform is an AI-powered system that generates ROI analysis and value propositions for healthcare solutions. It leverages LLMs to transform uploaded collateral into customized dashboards and reports.

---

## High-Level Workflow

### 1. Client Management & Value Proposition Setup
**Triton Integration Point**

The client management workflow establishes the foundation for all prospect analysis. This is a two-step process that culminates in a derived client value proposition used throughout the platform.

#### Step 1.1: Client Information Capture
- **Purpose**: Establish basic client organization details
- **Key Actions**:
  - Create new client record with company details
  - Configure client-specific settings and branding
  - Manage client lifecycle (active/inactive status)
  - Set up organizational metadata

#### Step 1.2: Value Proposition Derivation (Triton Engine)
**Triton Integration Point**

After capturing client information, Triton derives the client's core value proposition using one of two modes:

##### Mode A: Research-Based Derivation
**Two Sub-Modes:**

**A1: Autonomous Research (AI-Driven)**
- **Input**: Client company name + optional industry hint
- **Process**:
  - User provides client company name (e.g., "Livongo Health")
  - WebSearchAgent performs comprehensive autonomous research (15-25 searches):
    - Company website, mission, products, value messaging
    - Clinical outcomes and published evidence
    - Competitive landscape and differentiation
    - Market presence (press releases, news, awards)
    - Customer case studies and testimonials
    - ROI claims and success metrics
  - AI derives likely value propositions based on:
    - How company positions itself publicly
    - Competitor strategies and market trends
    - Industry standards and published outcomes
  - SynthesisAgent formats findings into ValuePropositionJSON
- **Output**: AI-derived value proposition from public information
- **Use Case**: Quick value prop generation when collateral not available

**A2: Manual Prompts (User-Directed)**
- **Input**: User provides specific research prompts/directions
- **Process**:
  - User enters targeted research prompts describing what to research
  - WebSearchAgent conducts research based on user prompts (5-15 searches)
  - LLM synthesizes findings into structured value proposition
- **Output**: Value proposition based on user-directed research
- **Use Case**: User wants to control specific research areas
- **Reference Example**: `/data/mock-data/livongo_value_proposition.json`

##### Mode B: Collateral-Based Derivation
- **Input**: Client's ROI sales sheets, marketing collateral, white papers
- **Process**:
  - User uploads client collateral documents (PDFs, etc.)
  - DocumentAnalysisAgent analyzes uploaded materials using LLM
  - System references structural examples for consistency
  - LLM extracts and structures value propositions from CLIENT materials
- **Output**: AI-derived value proposition from client's own documents
- **Use Case**: Client has existing collateral to analyze
- **Reference Example**: `/data/mock-data/livongo_value_proposition_derived.json`

**Note**: The ranked version of the value proposition is generated later in Step #4 (Prospect Value Proposition Generation), where the client's base value proposition is combined with prospect-specific analytics data to produce prospect-specific rankings.

##### Value Proposition Output Structure
All modes (A1, A2, B) generate a standardized JSON structure containing:
- **Value Proposition Priorities**: List of key value drivers (unranked at client level)
- **Clinical Outcomes**: Expected health improvements and metrics
- **Financial Impact**: ROI estimates, cost savings ranges
- **Competitive Differentiators**: Unique selling points
- **Target Audiences**: Stakeholder segments (Broker, Health Plan, PBM, etc.)
- **Time to Impact**: Expected timelines for value realization
- **Confidence Levels**: Assessment of impact certainty

**Note**: The Livongo examples serve as structural templates that Triton uses to ensure consistent output format regardless of derivation mode.

---

#### Step 1.3: Value Proposition Review & Refinement (Iterative Loop)
**Triton Integration Point**

After Triton generates the initial client value proposition, an iterative review and refinement process occurs before final approval.

##### Review Interface
- **Location**: `/admin/client-management/[id]/review/livongo-value-proposition-derived`
- **Reviewers**: Client Administrators
- **Review Scope**: All sections of the generated value proposition including:
  - Executive Value Proposition
  - Clinical Outcomes Foundation
  - ROI Opportunities (Tier 1, 2, 3)
  - Financial Modeling Framework
  - Three-Scenario Framework
  - Prospect Assessment Framework
  - Clinical Evidence Base
  - Competitive Positioning
  - Risk Mitigation Framework
  - Sales Enablement Guidance
  - Limitations and Disclaimers

##### Review Actions
Client Admins can perform the following actions on each section:

1. **Approve Section**: Accept the section as-is
2. **Reject with Removal**: Request section be removed entirely
   - Must provide rationale for removal
3. **Reject with Change Request**: Request modifications to section
   - Must provide specific feedback on desired changes
4. **General Feedback**: Provide overall comments across all sections

##### Triton Refinement Process (Agent-Based)
**Triton Integration Point**

When the client admin submits their review (with rejections or change requests):

1. **Feedback Collection**: System collects:
   - Section-specific approvals/rejections
   - Section-specific feedback (remove or change)
   - General feedback comments

2. **Triton Refinement Agent**: A specialized LLM agent processes:
   - **Input**:
     - Original value proposition JSON
     - Section-level decisions (approved/rejected)
     - Section-level feedback (rationale for removal or requested changes)
     - General feedback comments
   - **Process**:
     - Agent analyzes all feedback holistically
     - Removes sections marked for removal
     - Refines sections marked for changes based on specific feedback
     - Incorporates general feedback across relevant sections
     - Maintains structural consistency with Livongo examples
   - **Output**: Refined value proposition JSON (v2)

3. **Return to Review**: Users are brought back to the review screen with refined content

4. **Iterative Cycle**: Process repeats until client admin approves all sections
   - Feedback round counter tracks iterations
   - Each round produces a new version of the value proposition

##### Final Approval
- Once all sections are approved (no rejections or change requests), the value proposition is finalized
- The approved value proposition becomes the client's base value proposition for all future prospects

**Implementation Note**: The review system tracks feedback rounds and maintains version history of refinements, allowing Triton to learn from each iteration and produce increasingly accurate results.

---

#### Step 1.4: Dashboard Template Generation & Curation
**Triton Integration Point**

After the client value proposition is approved, Triton generates a library of reusable dashboard templates that will be used later for prospect-specific ROI analysis.

##### Template Generation Interface
- **Location**: `/admin/client-management/[id]/review/dashboard-templates-derived`
- **Trigger**: User initiates template generation after value proposition approval
- **Generation Process**: Triton Dashboard Template Agent creates 5-10 dashboard variations

##### Triton Dashboard Template Agent
**Triton Integration Point**

A specialized LLM agent that generates dashboard template variations based on the approved value proposition:

- **Input**:
  - Approved client value proposition JSON
  - Client-specific industry context (e.g., diabetes management, chronic disease)
  - Target audience segments (Broker, Health Plan, PBM, TPA, Medical Management)

- **Process**:
  - Analyzes value proposition to identify key metrics and themes
  - Generates 5-10 dashboard template variations across multiple categories:
    - **ROI-Focused**: Financial impact, payback period, cost savings
    - **Clinical Outcomes**: Health metrics, quality measures, patient outcomes
    - **Operational Efficiency**: Process improvements, utilization trends, efficiency gains
    - **Competitive Positioning**: Market comparisons, competitive advantages
    - **Comprehensive**: Combined views with multiple metric categories
  - Customizes each template for specific target audiences
  - Designs visual styles (colors, layouts) appropriate for each audience
  - Defines KPI cards, chart types, and widget configurations

- **Output**: Array of DashboardTemplate JSON objects

##### Dashboard Template JSON Structure
Each template is defined in JSON format with the following structure:

```typescript
{
  id: string                    // Unique identifier
  name: string                  // Template display name
  description: string           // Purpose and key focus
  category: string              // roi-focused | clinical-outcomes | operational-efficiency | competitive-positioning | comprehensive
  targetAudience: string        // Broker | Health Plan | PBM | TPA | Medical Management
  keyFeatures: string[]         // Bullet points of what's included
  widgets: DashboardWidget[]    // Widget definitions (KPI cards, charts, tables)
  visualStyle: {
    primaryColor: string        // Brand/theme color
    accentColor: string         // Secondary color
    layout: string              // dense | balanced | spacious
  }
  recommendedUseCase: string    // Guidance on when to use
}
```

##### Template Curation (User Review)
After generation, users review templates in a gallery view with thumbnail previews:

**Actions Available**:
1. **Preview Template**: View full dashboard mockup in modal with carousel navigation
2. **Remove Template**: Delete templates that don't fit their needs
3. **Keep Template**: Retain for use in prospect ROI analysis

**No Feedback Loop**: Unlike value proposition review, there is no iterative refinement process. Users can only curate (keep/remove) templates, not request modifications.

##### Template Storage
- Curated templates are stored in JSON format (client-specific)
- Templates are cached for reuse across all prospects under this client
- Template library becomes the foundation for Step #5 (Prospect Dashboard Generation)

##### Template Reusability
The approved dashboard templates serve as:
- **Blueprints** for prospect-specific dashboards in Step #5
- **Structural guides** defining which metrics, charts, and visualizations to include
- **Visual standards** ensuring consistent branding across all prospect reports
- **Audience-specific variants** allowing customization based on prospect stakeholders

**Note**: Templates are defined at the client level but populated with prospect-specific data during Step #5 (Dashboard Generation).

---

### 2. Prospect Creation, Research & Value Proposition Alignment
**Triton Integration Point**

After client setup is complete, prospects (sales opportunities) are created and analyzed to produce prospect-specific value proposition rankings.

#### Step 2.1: Prospect Creation & Initial Setup
- **Purpose**: Create prospect record and capture basic information
- **Location**: `/prospects` (create dialog)
- **Key Actions**:
  - Create new prospect entry under a client
  - Enter basic prospect information (company name, contact details)
  - Associate prospect with parent client organization
  - Set up initial prospect metadata

#### Step 2.2: Prospect Company Research (Triton Engine)
**Triton Integration Point**

After prospect creation, Triton researches the prospect company to understand their business, needs, and value drivers.

##### Triton Client Research & Alignment Agent
**Triton Integration Point**

A unified LLM agent responsible for all research and alignment activities across both clients and prospects:

**Agent Responsibilities**:
- Client value proposition research (Step 1.2 - Mode A)
- Client collateral analysis (Step 1.2 - Mode B)
- **Prospect company research** (Step 2.2)
- **Prospect value metrics identification** (Step 2.3)
- **Client-to-Prospect value prop alignment & ranking** (Step 2.4)

##### Prospect Research Process
- **Input**:
  - Prospect company name
  - Basic information from prospect creation

- **Process**:
  - Conducts Google searches and web intelligence gathering
  - Analyzes public information about the prospect company
  - Extracts comprehensive company profile

- **Output**: Detailed prospect company information JSON

##### Prospect Company Information Structure
The research produces a standardized JSON format containing:

```json
{
  "data_source_metadata": {
    "sources_used": "string",
    "web_searches_performed": number,
    "search_queries": ["array of search queries"],
    "data_freshness": "string"
  },
  "company_overview": {
    "company_name": "string",
    "description": "string",
    "website": "string",
    "founded": "string",
    "headquarters": "string"
  },
  "classification": {
    "core_segment": "PAYER | PROVIDER | PHARMACY | EMPLOYER | OTHER",
    "subsegment": "Health Plan | Broker | PBM | TPA | Medical Management | etc.",
    "healthcare_organization_type": "string"
  },
  "business_information": {
    "revenue": "string",
    "employee_count": "string",
    "ownership_type": "string",
    "geographic_footprint": "string"
  },
  "healthcare_specifics": {
    "lines_of_business": ["array"],
    "covered_lives": "string",
    "contracting_model": "string",
    "data_exchange_maturity": "string"
  },
  "financial_metrics": {},
  "leadership": {},
  "market_position": {
    "competitive_advantages": ["array"],
    "market_challenges": ["array"],
    "partnerships": ["array"]
  },
  "population_characteristics": {}
}
```

**Reference Example**: `/data/mock-data/wellmark_company_information.json`

**Key Fields for Value Prop Alignment**:
- **`classification.core_segment`**: Primary business type (PAYER, PROVIDER, etc.)
- **`classification.subsegment`**: Specific prospect type used for dashboard template selection (Health Plan, Broker, PBM, Medical Management, etc.)
- **`healthcare_specifics`**: Details used to identify value priorities
- **`market_position`**: Challenges and advantages informing value prop ranking

---

#### Step 2.3: Prospect Value Metrics Identification (Triton Engine)
**Triton Integration Point**

Using the researched company information, Triton identifies the prospect's key value drivers and pain points.

- **Input**:
  - Prospect company information JSON (from Step 2.2)
  - Client value proposition JSON (from Step 1.3)

- **Process**:
  - Analyzes prospect's business model, challenges, and priorities
  - Identifies prospect-specific value metrics based on their segment
  - Maps prospect needs to potential value drivers
  - Determines which client value propositions are most relevant

- **Output**: Prospect value metrics and alignment analysis

---

#### Step 2.4: Value Proposition Ranking & Alignment (Triton Engine)
**Triton Integration Point**

The same Triton Research & Alignment Agent ranks the client's value propositions based on their relevance to this specific prospect.

##### Ranking Process

- **Input**:
  - Client value proposition JSON (approved, unranked from Step 1.3)
  - Prospect company information JSON (from Step 2.2)
  - Prospect value metrics (from Step 2.3)
  - Prospect type/subsegment (from classification)

- **Process**:
  - Analyzes each client value proposition's relevance to this prospect
  - Considers prospect segment priorities (e.g., Health Plan prioritizes clinical quality, Broker prioritizes ROI)
  - Evaluates alignment between:
    - Prospect's market challenges → Client's value propositions
    - Prospect's business priorities → Client's financial impact areas
    - Prospect's healthcare focus → Client's clinical outcomes
  - Assigns ranking based on alignment strength
  - Identifies prospect-specific talking points for each value prop
  - Flags low-relevance propositions with warnings

- **Output**: Ranked value proposition JSON (prospect-specific)

##### Ranked Value Proposition JSON Structure

```json
{
  "metadata": {
    "document_name": "string",
    "purpose": "string",
    "prospect_company": "string",
    "prospect_type": "Health Plan | Broker | PBM | TPA | Medical Management | etc.",
    "ranking_date": "date"
  },
  "ranking_instructions": {
    "default_behavior": "string",
    "customization_approach": "string",
    "presentation_strategy": "string"
  },
  "value_proposition_priorities": [
    {
      "priority_id": "string",
      "priority_name": "string",
      "default_rank": number,
      "rank_locked": boolean,
      "description": "string",
      "key_components": ["array"],
      "segment_priority": {
        "high_priority": ["array of prospect types"],
        "medium_priority": ["array"],
        "low_priority": ["array"]
      },
      "typical_savings_range": "string",
      "time_to_impact": "string",
      "data_requirements": ["array"],
      "presentation_talking_points": ["array"],
      "relevance_warning": {
        "status": "LOW_RELEVANCE | MODERATE_FIT | etc.",
        "recommendation": "string",
        "rationale": "string"
      }
    }
  ]
}
```

**Reference Example**: `/data/mock-data/livongo_value_proposition_derived_ranked.json`

**Key Ranking Considerations**:
1. **Segment Priority Matching**: Each value prop has `segment_priority` indicating which prospect types it resonates with most
2. **Locked Priority #1**: Typically the core financial ROI remains locked as the lead value prop
3. **Relevance Warnings**: Low-fit propositions are flagged with recommendations (consider removing or de-prioritizing)
4. **Prospect Type Alignment**: Dashboard template selection (Step 2.5) uses the prospect's subsegment to choose appropriate templates

---

#### Step 2.5: Prospect Type Identification for Dashboard Selection

**Critical Output**: The prospect's **subsegment** classification (from Step 2.2) determines which dashboard templates will be used:

- **Health Plan** → Health Plan dashboard templates
- **Broker** → Broker dashboard templates
- **PBM** → PBM dashboard templates
- **Medical Management** → Medical Management dashboard templates
- **TPA** → TPA dashboard templates

This subsegment is used in later steps (#5 and #6) to filter the client's dashboard template library and present only relevant templates for this prospect type.

---

#### Step 2.6: Manual Ranking Review (Optional)

**Location**: `/prospects/[prospect_id]/review/value-proposition-ranking`

After Triton generates the initial ranking, users can optionally:
- Review the AI-generated ranking
- Manually reorder priorities 2-N (Priority #1 typically remains locked)
- Remove low-relevance propositions
- Save final ranking for prospect

**Note**: This is optional manual curation; the AI-generated ranking from Step 2.4 can be used directly.

### 3. Prospect Data Upload & Processing (ARGO Engine)
**ARGO Integration Point**

After prospect creation and value proposition ranking, prospect-specific data is uploaded and processed to create analytics-ready datasets for ROI analysis.

#### Step 3.1: Prospect Data Upload
- **Purpose**: Upload prospect data files (claims, eligibility, utilization)
- **User**: Sales team members or prospects themselves (future capability)
- **Supported Data Types**:
  - Medical claims data
  - Pharmacy claims data
  - Eligibility/membership data
  - Utilization data
  - Other healthcare-related datasets

#### Step 3.2: ARGO Data Analysis & Mapping
**ARGO Integration Point**

ARGO (Data Mapping and Processing Engine) performs intelligent data analysis:

##### ARGO Processing Steps:

1. **Data Examination**:
   - Analyzes uploaded file structure
   - Identifies data layout and format (CSV, Excel, flat file, etc.)
   - Detects data types (dates, numeric, categorical, etc.)

2. **Field Analysis**:
   - Examines rows to determine content of each field
   - Infers field meanings (member ID, claim date, diagnosis codes, etc.)
   - Identifies data quality issues

3. **Mapping to Standard Layout**:
   - Maps detected fields to standardized input schema
   - Handles field name variations and common aliases
   - Flags unmapped or ambiguous fields

4. **Data Grade Generation**:
   - Produces quality assessment and mapping confidence scores
   - Identifies completeness, accuracy, and consistency metrics
   - Generates data profile summary

#### Step 3.3: Data Grade Review & Approval

##### Data Grade Interface
- **Location**: Prospect data management UI (likely `/prospects/[prospect_id]/files`)
- **Review Artifacts**:
  - Data quality metrics
  - Field mapping results
  - Completeness scores
  - Data anomalies or issues flagged

##### User Actions:
1. **Review Data Grade**: Examine ARGO's analysis and mapping results
2. **Approve**: Accept the data grade and proceed to processing
3. **Replace Files**: If issues detected, upload corrected files and re-run ARGO analysis
4. **Adjust Mappings** (if needed): Correct any incorrect field mappings

#### Step 3.4: Data Processing & Enrichment
**ARGO Integration Point**

Upon approval, ARGO processes the data:

1. **Data Transformation**:
   - Converts source data to standardized input layout
   - Applies data cleansing and normalization rules
   - Handles missing values and data quality issues

2. **Analytics Engine Processing**:
   - Runs data through healthcare analytics engine
   - Enriches with additional healthcare information:
     - **Utilization metrics**: ED visits, hospital admissions, readmissions, PMPM costs
     - **Quality metrics**: HEDIS measures, Stars ratings, clinical outcomes
     - **Risk stratification**: HCC scores, comorbidity analysis
     - **Cost analysis**: Total cost of care, trend analysis, benchmarking

3. **Output Data Model Generation**:
   - Produces standardized output data model
   - Data becomes available in common format for downstream analysis
   - Ready for Triton consumption in Steps #4-6

#### Step 3.5: Output Data Model

**Common Output Data Model Structure**:
- **Member/Population**: Demographics, eligibility, risk scores
- **Utilization**: Claims, encounters, service utilization
- **Clinical**: Diagnoses, procedures, labs, quality measures
- **Financial**: Costs, trends, PMPM metrics
- **Quality**: HEDIS, Stars, clinical quality indicators

**Note**: This standardized output becomes the input for Triton's value proposition generation and dashboard population in subsequent steps.

---

**ARGO Summary**:
- ARGO is fully automated for data analysis, mapping, and processing
- Human intervention only required for data grade approval or issue resolution
- Output is a consistent, analytics-ready dataset regardless of source data variability

### 4. Value Proposition Data Generation (Triton Analytics Team)
**Triton Integration Point** | **Runs in Parallel with Step #5**

After ARGO completes and the analytics data model is available, Triton's Analytics Team generates prospect-specific value proposition insights by querying the data model.

#### Triton Analytics Team Architecture

**Analytics Team Agents**: A collaborative team of specialized LLM agents, each expert in a healthcare data domain:
- **Clinical Agent**: Clinical outcomes, quality measures, disease management
- **Utilization Agent**: ED visits, hospitalizations, readmissions, service utilization
- **Pricing Agent**: Cost analysis, PMPM trends, financial impact
- **Pharmacy Agent**: Drug costs, adherence, formulary analysis

**Question-to-SQL Agent**: Coordinator agent that:
- Fields questions from all category-specific agents
- Translates natural language questions into SQL queries
- Executes queries against Clickhouse data warehouse
- Returns results back to category agents for analysis

#### Step 4.1: Value Proposition Query Planning

**Input**:
- Ranked value proposition JSON (from Step 2.4)
- ARGO output data model (from Step 3.5)
- Client value proposition structure (from Step 1.3)

**Process**:
1. Analytics Team agents analyze the ranked value propositions
2. Each agent identifies data elements needed to support their domain's value props
3. Agents formulate questions to extract relevant metrics

**Example Questions by Agent**:
- **Clinical Agent**: "What is the current HbA1c control rate? How many members have uncontrolled diabetes?"
- **Utilization Agent**: "What is the diabetes-related ED visit rate? What are the top avoidable admission categories?"
- **Pricing Agent**: "What is the current diabetes complication cost PMPM? What is the potential savings from improved control?"
- **Pharmacy Agent**: "What is the current medication adherence rate? What is the cost of diabetes medications?"

#### Step 4.2: Iterative Question-Answer-SQL Workflow

**Iterative Process**:

1. **Agent poses question** → Question-to-SQL Agent
2. **Question-to-SQL Agent**:
   - Translates question to SQL
   - Executes against Clickhouse
   - Returns data
3. **Category Agent analyzes results**:
   - Interprets data
   - May ask follow-up questions
   - Continues until sufficient data collected
4. **Repeat** for all value propositions and all agents

**Example Workflow**:
```
Clinical Agent: "What is the baseline HbA1c distribution for this population?"
  ↓
Question-to-SQL Agent: SELECT avg(hba1c), percentile(hba1c, 0.5), count(*)
                       FROM clinical_data WHERE condition = 'diabetes'
  ↓
Clinical Agent: [Analyzes: Mean HbA1c = 8.2%, 45% uncontrolled]
                "What are the complication rates for members with HbA1c > 8%?"
  ↓
Question-to-SQL Agent: SELECT complication_type, count(*)
                       FROM complications WHERE hba1c > 8 GROUP BY type
  ↓
Clinical Agent: [Completes analysis, stores results]
```

#### Step 4.3: Data Storage & Result Generation

**Storage Strategy**:
- Value proposition insights stored in **Postgres JSONB** (not Clickhouse for MVP)
- Each prospect's complete value proposition analysis stored as single JSONB document
- Organized by value proposition priority with pre-computed metrics

**Why Postgres JSONB for Value Props (MVP)**:
- Pre-formatted insights ready for UI display
- Similar reasoning to dashboard storage (Step 5.3)
- Single query for all value proposition data
- Natural fit for hierarchical value prop structure

**Stored Data Structure** (Postgres table):
```sql
CREATE TABLE prospect_value_proposition_data (
    id UUID PRIMARY KEY,
    prospect_id UUID REFERENCES prospects(id),
    client_id UUID REFERENCES clients(id),
    value_proposition_data JSONB,  -- Complete value prop insights
    generated_at TIMESTAMP,
    UNIQUE(prospect_id)
);
```

**JSONB Content** (per value proposition):
- Baseline metrics (current state)
- Impact calculations (projected improvement)
- Supporting evidence (query results, data points)
- Visualizations data (charts, graphs)

**Note**: Clickhouse contains ARGO-processed raw data which Analytics Team queries during generation. Results are stored in Postgres for fast presentation.

#### Step 4.4: Value Proposition Presentation

**Location**: `/prospects/[prospect_id]/reports/insights/value-propositions/prospect-opportunities`

**Presentation Elements**:
- Value proposition cards with data-driven metrics
- Baseline vs. projected outcomes
- Financial impact calculations based on actual prospect data
- Clinical evidence from prospect's own population
- Supporting charts and visualizations

**Reference**: `/Users/rwoollam/Development/mare-frontend/src/app/(dashboard)/prospects/[prospect_id]/reports/insights/value-propositions/prospect-opportunities/page.tsx`

**Output**: Value proposition insights data stored in Postgres JSONB, ready for UI presentation in Step #6.

---

### 5. ROI Dashboard Data Generation (Triton Analytics Team)
**Triton Integration Point** | **Runs in Parallel with Step #4**

Simultaneously with value proposition data generation, the same Analytics Team populates the dashboard templates from Step 1.4 with prospect-specific data.

#### Dashboard Data Generation Architecture

**Same Analytics Team Agents**:
- Clinical Agent
- Utilization Agent
- Pricing Agent
- Pharmacy Agent
- Question-to-SQL Agent (coordinator)

**Key Difference from Step #4**: Instead of analyzing ranked value propositions, agents analyze dashboard template definitions to determine required data.

#### Step 5.1: Dashboard Widget Query Planning

**Input**:
- Dashboard templates JSON (from Step 1.4, filtered by prospect type from Step 2.5)
- ARGO output data model (from Step 3.5)
- Prospect type classification (Health Plan, Broker, PBM, etc.)

**Process**:
1. Analytics Team agents examine each dashboard template
2. For each widget in the template, agents identify required data:
   - **KPI Cards**: Specific metrics (ROI %, payback period, savings, member count)
   - **Charts**: Time-series data, categorical breakdowns, waterfall components
   - **Tables**: Ranked lists, opportunity summaries, quality measures
3. Agents formulate questions to extract data for each widget

**Example Widget Data Requirements**:

```json
Dashboard Template: "Diabetes ROI Executive Dashboard"
Widget: "Total ROI KPI Card"
  → Pricing Agent: "Calculate 24-month ROI based on complication avoidance"

Widget: "Savings Waterfall Chart"
  → Clinical Agent: "Break down savings by complication type"
  → Pricing Agent: "Calculate savings value for each category"

Widget: "Utilization Trends Chart"
  → Utilization Agent: "Get monthly ED visit and hospitalization trends"
```

#### Step 5.2: Iterative Dashboard Data Collection

**Process** (same workflow as Step 4.2):

1. **Agent identifies widget data need** → Question-to-SQL Agent
2. **Question-to-SQL Agent**:
   - Translates data requirement to SQL
   - Executes against Clickhouse
   - Returns results
3. **Category Agent processes results**:
   - Formats data for widget type (chart, KPI, table)
   - May ask follow-up questions for additional context
   - Stores formatted data
4. **Repeat** for all widgets across all dashboard templates

**Example Workflow**:
```
Pricing Agent: "Calculate 24-month ROI for diabetes program"
  ↓
Question-to-SQL Agent:
  SELECT SUM(complication_cost_avoided) as savings,
         SUM(program_cost) as costs
  FROM roi_analysis WHERE months <= 24
  ↓
Pricing Agent: [Calculates: ROI = (savings/costs) * 100 = 340%]
              [Formats: "340%" for KPI card display]
              [Stores: {"kpi": "roi_percentage", "value": 340, "display": "340%"}]
```

#### Step 5.3: Data Storage for Dashboard Rendering

**Storage Strategy**:
- Complete dashboard data pre-computed and stored in **Postgres JSONB** (not Clickhouse)
- Each prospect + template combination stored as a single JSONB document
- Indexed for fast retrieval at runtime

**Why Postgres JSONB for Dashboards (MVP)**:
- Dashboards have high variation due to custom templates
- Pre-formatted complete JSON ready for UI rendering
- Single indexed query for entire dashboard (~10ms)
- No complex joins or aggregations at runtime
- Template structure naturally maps to JSONB document

**Stored Data Structure** (Postgres table):
```sql
CREATE TABLE prospect_dashboard_data (
    id UUID PRIMARY KEY,
    prospect_id UUID REFERENCES prospects(id),
    client_id UUID REFERENCES clients(id),
    template_id UUID,
    dashboard_data JSONB,  -- Complete dashboard JSON with all widgets
    generated_at TIMESTAMP,
    UNIQUE(prospect_id, template_id)
);

CREATE INDEX idx_prospect_dashboard_lookup
ON prospect_dashboard_data(prospect_id, template_id);
```

**Example JSONB Content** (`dashboard_data` column):
```json
{
  "template_id": "diabetes-roi-executive",
  "template_name": "Diabetes ROI Executive Dashboard",
  "widgets": {
    "kpi_roi_percentage": {"value": 340, "display": "340%", "trend": "up"},
    "kpi_payback_period": {"value": 14, "display": "14 mo"},
    "chart_savings_waterfall": [
      {"category": "MI Prevention", "value": 850000},
      {"category": "Stroke Prevention", "value": 620000}
    ],
    "chart_utilization_trends": [
      {"month": "Jan", "ed_visits": 145, "hospitalizations": 62}
    ]
  }
}
```

**Note**: Clickhouse still contains ARGO-processed raw prospect data (from Step 3) which Analytics Team queries during generation. Dashboard widget results are stored only in Postgres for MVP.

#### Step 5.4: Runtime Dashboard Rendering

**Location**: `/prospects/[prospect_id]/reports/insights/roi-analysis`

**Rendering Process**:
1. UI requests dashboard for prospect + template type
2. Backend retrieves from Postgres:
   - Single query: `SELECT dashboard_data FROM prospect_dashboard_data WHERE prospect_id = ? AND template_id = ?`
   - Returns complete pre-formatted dashboard JSON (~10ms)
3. Dashboard rendered directly from JSONB:
   - KPI cards populated with pre-computed metrics
   - Charts generated from stored data arrays
   - Styling applied per template visual design
   - Target audience customization already baked in

**Performance**:
- Fast rendering because all data pre-computed by Analytics Team (Step 5.2)
- Single indexed Postgres query (no Clickhouse queries at runtime)
- No aggregations or joins needed
- Complete dashboard data ready for UI consumption

**Reference**: `/Users/rwoollam/Development/mare-frontend/src/app/(dashboard)/prospects/[prospect_id]/reports/insights/roi-analysis/page.tsx`

#### Step 5.5: Dashboard Template Selection

**Filtering by Prospect Type**:
- Prospect's subsegment (from Step 2.2) filters templates
- Only relevant templates presented:
  - Health Plan prospect → Health Plan templates
  - Broker prospect → Broker templates
  - etc.

**Available Dashboards**:
- ROI-focused dashboards (financial impact, payback)
- Clinical outcomes dashboards (quality, health metrics)
- Operational efficiency dashboards (utilization, care management)
- Comprehensive dashboards (combined views)

**Output**: Dashboard widget data stored in Postgres JSONB, ready for UI presentation in Step #6.

---

### 6. MARE Application - Prospect Reports & Presentation
**No Triton or ARGO Integration** - Pure Frontend Presentation Layer

After Steps 4 and 5 complete and all data is pre-computed and stored in Clickhouse, the MARE application presents the results to users through three main report views under a completed prospect.

#### Overview

**Location**: `/prospects/[prospect_id]/reports`

The MARE frontend retrieves pre-computed data from Clickhouse and presents it in user-friendly views. All heavy computation has already been completed by the Analytics Team; this step is purely presentation and visualization.

#### Three Main Report Views

**1. Population Summary**
- **Purpose**: Provide real-time control totals and basic healthcare metrics overview
- **Data Source**: Real-time queries against Clickhouse analytical data (from Step 3 ARGO output)
- **Query Type**: Live queries (not pre-computed)
- **Key Metrics**:
  - **Population**: Member counts, demographics, eligibility
  - **Financials**: Total costs, PMPM, cost trends
  - **Utilization**: ED visits, hospitalizations, primary care visits
- **Use Case**: Quick snapshot of prospect's healthcare data fundamentals

**2. ROI Analysis**
- **Purpose**: Present comprehensive ROI dashboards to sales team and prospects
- **Data Source**: Pre-computed dashboard data from Postgres JSONB (Step 5)
- **Template Source**: Dashboard templates selected during Step 1 (client setup)
- **Query Performance**: Single indexed query per dashboard (~10ms)
- **Features**:
  - Carousel navigation through multiple dashboard variations (5+)
  - Filtered by prospect type (Health Plan, Broker, PBM, etc.)
  - Full export capabilities:
    - **Click to Copy**: Copy dashboard image to clipboard
    - **PNG**: Download high-resolution image
    - **PDF**: Export print-ready document
- **Dashboard Categories**:
  - ROI-focused (financial impact, payback period)
  - Clinical outcomes (quality measures, health improvements)
  - Operational efficiency (utilization trends, care management)
  - Comprehensive (combined multi-metric views)
- **Use Case**: Primary sales presentation tool with prospect-specific data

**3. Value Propositions**
- **Purpose**: Present detailed value proposition analysis comparing prospect data to client value propositions
- **Data Source**: Pre-computed value proposition insights from Postgres JSONB (Step 4)
- **Query Performance**: Single query for complete value prop analysis
- **Comparison**: Prospect's actual data (Step 4) vs. Client value prop projections (Step 1)
- **Sales Team Curation**:
  - **Re-order**: Adjust ranking based on sales strategy
  - **Remove**: Eliminate low-relevance or weak-fit propositions
  - **Finalize**: Prepare curated list for prospect pitch
- **Display Elements**:
  - Ranked value proposition cards
  - Baseline vs. projected metrics from prospect's data
  - Financial impact calculations
  - Clinical evidence from prospect's population
  - Supporting talking points
- **Use Case**: Sales team prepares and customizes pitch based on prospect-specific analysis before presenting to prospect

#### Data Retrieval Performance

**Population Summary**:
- Real-time queries against Clickhouse (ARGO-processed raw data from Step 3)
- Fast query execution on indexed analytics data
- Basic aggregations and control totals
- Use case: Quick snapshot metrics

**ROI Analysis & Value Propositions**:
- Pre-computed by Analytics Team (Steps 4-5)
- Stored in Postgres JSONB for instant retrieval
- Single indexed query per view (~10ms)
- UI simply fetches and displays stored results
- Instant navigation and rendering
- Data already formatted for presentation
- No Clickhouse queries at runtime

#### Sales Team Workflow

1. **Review Population Summary**: Understand prospect's baseline healthcare metrics
2. **Review ROI Analysis**: Examine pre-generated dashboard variations with prospect-specific data
3. **Curate Value Propositions**:
   - Compare prospect's actual performance vs. client value prop projections
   - Re-order propositions based on sales strategy
   - Remove low-relevance or weak propositions
4. **Export & Present**: Use carousel to select best dashboard(s), export for prospect presentation

---

**Step 6 Summary**: The MARE application is the presentation layer that consumes all the work done by Triton (Steps 1-2, 4-5) and ARGO (Step 3). It provides an intuitive interface for sales teams to:
- View prospect healthcare data fundamentals
- Access AI-generated ROI dashboards tailored to the prospect
- Curate and customize value propositions before pitching
- Export professional presentation materials

---

## Key Platform Concepts

### Engine Architecture

#### Triton Engine (AI/LLM Component)
**Integration Points**: Client Management (#1), Prospect Creation & Alignment (#2), Value Proposition Generation (#4), Dashboard Generation (#5), Reports & Insights (#6)

The AI/LLM component consists of specialized agents:

1. **Client Research & Alignment Agent** (Steps 1.2, 2.2-2.4):
   - Client value proposition research and collateral analysis
   - Prospect company research via Google search
   - Prospect value metrics identification
   - Client-to-prospect value proposition alignment and ranking

2. **Value Proposition Refinement Agent** (Step 1.3):
   - Iterative refinement based on client admin feedback
   - Section removal and modification per feedback

3. **Dashboard Template Generation Agent** (Step 1.4):
   - Creates 5-10 dashboard template variations
   - Customizes for different target audiences and categories

4. **Analytics Team Agents** (Steps 4-5, run in parallel):

   **Category-Specific Agents**:
   - **Clinical Agent**: Clinical outcomes, quality measures, disease management
   - **Utilization Agent**: ED visits, hospitalizations, readmissions, service utilization
   - **Pricing Agent**: Cost analysis, PMPM trends, financial impact calculations
   - **Pharmacy Agent**: Drug costs, adherence, formulary analysis

   **Coordinator Agent**:
   - **Question-to-SQL Agent**: Translates agent questions into SQL, executes queries against Clickhouse, returns results

   **Workflow**: Iterative question-answer-SQL loop where category agents pose questions, SQL agent executes queries against Clickhouse (raw data), and results are analyzed and formatted

   **Output**: Pre-computed data stored in Postgres JSONB for:
   - Value proposition insights (Step 4)
   - Dashboard widget data (Step 5)

**Note**: Step 6 (MARE Application frontend) does not involve Triton agents - it is purely a presentation layer that consumes pre-computed data.

#### ARGO Engine (Data Processing Component)
**Integration Points**: Prospect Data Upload & Processing (#3)

The intelligent data mapping and processing engine responsible for:

**Capabilities**:
1. **Intelligent Data Analysis**:
   - Examines uploaded file structures and formats
   - Analyzes row-level data to infer field meanings
   - Identifies data types and quality issues

2. **Automated Mapping**:
   - Maps source data fields to standardized input schema
   - Handles field name variations and aliases
   - Generates Data Grade (quality assessment)

3. **Data Processing & Enrichment**:
   - Transforms data to standardized layout
   - Runs through healthcare analytics engine
   - Enriches with utilization metrics, quality measures, risk scores

4. **Output Generation**:
   - Produces common output data model
   - Creates analytics-ready datasets for Triton consumption

**User Interaction**: Human intervention only required for Data Grade approval or issue resolution

**Note**: ARGO is already built and handles all prospect data processing automatically, while Triton focuses on AI-driven content generation.

#### Clickhouse Data Warehouse
**Integration Points**: Steps 3, 4, 5, 6

The analytics data warehouse used for:
- **Storing ARGO-processed prospect data** (Step 3 output)
  - Member/population data
  - Claims, utilization, clinical data
  - Quality measures and risk scores
- **Executing SQL queries from Question-to-SQL Agent** (Steps 4-5)
  - Analytics Team queries raw data during generation
  - Supports complex aggregations and analysis
- **Population Summary queries** (Step 6)
  - Real-time control totals and basic metrics

**Benefits**:
- Columnar storage optimized for analytics workloads
- Fast query performance for aggregations
- Efficient storage of time-series and healthcare data
- Supports complex ROI calculations during generation

**Note**: For MVP, Clickhouse is used for raw data storage and analytics queries during generation. Pre-computed results (dashboards, value propositions) are stored in Postgres JSONB for fast runtime serving.

### Value Proposition Derivation Modes

#### Mode A: Research-Based (Manual Review)
- User provides prompts and research direction
- Triton conducts research and synthesizes findings
- Output adheres to structural templates (Livongo examples)
- Human oversight and curation

#### Mode B: Collateral-Based (Derived)
- User uploads ROI sheets, marketing materials, collateral
- Triton analyzes documents using LLM
- Extracts and structures information automatically
- Output adheres to structural templates (Livongo examples)
- AI-driven with optional human validation

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│ #1 CLIENT MANAGEMENT & VALUE PROP SETUP (Triton)       │
├─────────────────────────────────────────────────────────┤
│ Step 1.1: Client Information Capture                   │
│ Step 1.2: Value Proposition Derivation (Triton Agent)  │
│          • Mode A: Research-Based (prompts)            │
│          • Mode B: Collateral-Based (upload ROI docs)  │
│ Step 1.3: Value Prop Review & Refinement (Triton Agent)│
│          • Iterative feedback loop with client admins  │
│          • Agent refines based on feedback until       │
│            approved                                    │
│ Step 1.4: Dashboard Template Generation (Triton Agent) │
│          • Generate 5-10 dashboard template variations │
│          • User curates (keep/remove only)             │
│ Output: Approved Value Prop JSON + Dashboard Templates │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ #2 PROSPECT CREATION & VALUE PROP ALIGNMENT (Triton)   │
├─────────────────────────────────────────────────────────┤
│ Step 2.1: Prospect Creation & Initial Setup            │
│ Step 2.2: Prospect Company Research (Triton Agent)     │
│          • Google search & intelligence gathering      │
│          • Extract company profile, classification     │
│          • Identify prospect TYPE (Health Plan, etc.)  │
│ Step 2.3: Prospect Value Metrics Identification        │
│          • Analyze business model & pain points        │
│ Step 2.4: Value Prop Ranking & Alignment (Triton Agent)│
│          • Rank client value props for this prospect   │
│          • Match segment priorities                    │
│          • Flag low-relevance propositions             │
│ Step 2.5: Prospect Type → Dashboard Template Mapping   │
│ Step 2.6: Manual Ranking Review (optional)             │
│ Output: Ranked Value Prop JSON + Prospect Type         │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ #3 PROSPECT DATA UPLOAD & PROCESSING (ARGO)            │
├─────────────────────────────────────────────────────────┤
│ Step 3.1: Prospect Data Upload (sales team/prospect)   │
│ Step 3.2: ARGO Data Analysis & Mapping                 │
│          • Examine file structure & data types         │
│          • Analyze rows to infer field meanings        │
│          • Map to standardized input layout            │
│          • Generate Data Grade (quality assessment)    │
│ Step 3.3: Data Grade Review & Approval                 │
│          • User reviews mapping & quality metrics      │
│          • Approve or replace files                    │
│ Step 3.4: Data Processing & Enrichment                 │
│          • Transform to standard layout                │
│          • Run through analytics engine                │
│          • Enrich with utilization & quality metrics   │
│ Step 3.5: Output Data Model Generation                 │
│ Output: Analytics-ready dataset in common data model   │
└────────────────────┬────────────────────────────────────┘
                     ↓
         ┌──────────────────────────────────────────┐
         │    PARALLEL PROCESSING (Steps 4 & 5)     │
         │    Triton Analytics Team                 │
         └──────────────┬───────────────────────────┘
                        ↓
         ┌──────────────┴──────────────────────────┐
         ↓                                         ↓
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ #4 VALUE PROP DATA GEN      │   │ #5 DASHBOARD DATA GEN       │
│ (Triton Analytics Team)     │   │ (Triton Analytics Team)     │
├─────────────────────────────┤   ├─────────────────────────────┤
│ Analytics Team Agents:      │   │ Same Analytics Team:        │
│ • Clinical Agent            │   │ • Clinical Agent            │
│ • Utilization Agent         │   │ • Utilization Agent         │
│ • Pricing Agent             │   │ • Pricing Agent             │
│ • Pharmacy Agent            │   │ • Pharmacy Agent            │
│ • Question-to-SQL Agent     │   │ • Question-to-SQL Agent     │
├─────────────────────────────┤   ├─────────────────────────────┤
│ Process:                    │   │ Process:                    │
│ • Analyze ranked value props│   │ • Analyze dashboard templates│
│ • Query Clickhouse raw data │   │ • Query Clickhouse raw data │
│ • Iterative Q&A + SQL       │   │ • Iterative Q&A + SQL       │
│ • Format & store in Postgres│   │ • Format & store in Postgres│
├─────────────────────────────┤   ├─────────────────────────────┤
│ Output: Value prop insights │   │ Output: Dashboard widget data│
│ stored in Postgres JSONB    │   │ stored in Postgres JSONB    │
└─────────────┬───────────────┘   └─────────────┬───────────────┘
              └──────────────┬────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│ #6 MARE APPLICATION - PROSPECT REPORTS                 │
│    (No Triton/ARGO - Pure Frontend)                    │
├─────────────────────────────────────────────────────────┤
│ Location: /prospects/[prospect_id]/reports             │
│                                                         │
│ Three Main Views:                                      │
│ 1. Population Summary (Real-time queries)             │
│    • Live queries against Clickhouse raw data          │
│    • Population, financials, utilization metrics       │
│    • Control totals and basic healthcare data          │
│                                                         │
│ 2. ROI Analysis (Postgres JSONB)                      │
│    • Pre-computed dashboard data from Postgres (Step 5)│
│    • Single indexed query per dashboard (~10ms)        │
│    • Carousel navigation, export (Copy/PNG/PDF)        │
│    • No Clickhouse queries at runtime                  │
│                                                         │
│ 3. Value Propositions (Postgres JSONB)                │
│    • Pre-computed insights from Postgres (Step 4)      │
│    • Single query for complete value prop analysis     │
│    • Compare prospect data vs client value props       │
│    • Sales team curates: re-order, remove props        │
│    • Prepare final pitch for prospect                  │
│                                                         │
│ Data Sources:                                          │
│ • Clickhouse: ARGO raw data (Step 3) for Pop Summary  │
│ • Postgres JSONB: Pre-computed results (Steps 4-5)    │
│                                                         │
│ Performance: Fast - Single queries, pre-formatted data│
└─────────────────────────────────────────────────────────┘
```

---

## Next Steps
- [ ] Detailed workflow for Client Management
- [ ] Detailed workflow for Prospect Creation
- [ ] Detailed workflow for Data Upload & Processing
- [ ] Detailed Value Proposition Generation flow
- [ ] Detailed Dashboard Generation flow
- [ ] API Architecture documentation
- [ ] Triton Engine LLM pipeline details

