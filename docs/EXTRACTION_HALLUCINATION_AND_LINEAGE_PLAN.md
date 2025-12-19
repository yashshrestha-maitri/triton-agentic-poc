# Extraction Hallucination Prevention & Data Lineage Implementation Plan

**Document Version:** 1.0.0
**Date:** 2025-01-16
**Status:** Planning Phase
**Priority:** 🔴 P0 - Critical for Production

---

## Table of Contents

1. [How Lineage Tracking Prevents Extraction Hallucinations](#how-lineage-tracking-prevents-extraction-hallucinations)
2. [Executive Summary](#executive-summary)
3. [Why Explicit Lineage Tracking is Required](#why-explicit-lineage-tracking-is-required)
4. [Problem Statement](#problem-statement)
5. [Current State Analysis](#current-state-analysis)
6. [Solution Architecture](#solution-architecture)
7. [Implementation Phases](#implementation-phases)
8. [Workflow Diagrams](#workflow-diagrams)
9. [Data Models](#data-models)
10. [Validation Pipeline Updates](#validation-pipeline-updates)
11. [Testing Strategy](#testing-strategy)
12. [Success Metrics](#success-metrics)
13. [Timeline & Resources](#timeline--resources)
14. [Data Lineage Storage Requirements](#data-lineage-storage-requirements)
15. [Storage Decision Framework](#storage-decision-framework)
16. [Database Architecture Details](#database-architecture-details)
17. [Lineage Data Lifecycle](#lineage-data-lifecycle)
18. [Storage Optimization Strategies](#storage-optimization-strategies)
19. [Cost Analysis](#cost-analysis)
20. [Common Questions (FAQ)](#common-questions-faq)

---

## How Lineage Tracking Prevents Extraction Hallucinations

### The Core Problem
AI models like Claude can generate **well-formed, structurally valid data that doesn't exist in the source document**. Current 4-layer validation only checks format and types, not truthfulness.

### Prevention Mechanisms

#### 1. **Source Text Storage Forces Verbatim Quotes**
- **Mechanism**: Requires agents to provide `source_text` field with exact quote from document
- **Prevention**: Agent must find actual text, can't just invent plausible-sounding claims
- **Verification**: System searches for `source_text` in `full_document_text`
- **Example**:
  ```json
  {
    "metrics": {"roi": "340%"},
    "source_text": "Blue Shield achieved 340% ROI excluding implementation costs"
  }
  ```
  If "340%" doesn't appear in source_text, verification fails → retry with feedback

#### 2. **Document Hash Detects Source Changes**
- **Mechanism**: SHA256 hash of original document stored in `extraction_lineage` table
- **Prevention**: If document changes after extraction, hash mismatch alerts system
- **Use Case**: Client updates ROI sheet from "250%" to "300%" → lineage shows extraction is stale
- **Traceability**: Every extraction linked to exact version of source document

#### 3. **Page Number Verification Prevents Invention**
- **Mechanism**: Agent claims data is on `page_numbers: [3]`, verification checks if `source_text` actually appears on page 3
- **Prevention**: Agent can't claim "page 1" when data is on page 5 (or doesn't exist)
- **Feedback Loop**: If page numbers wrong, retry with: "Re-read document, find EXACT page"

#### 4. **Numeric Value Cross-Check**
- **Mechanism**: Extract all numbers from `metrics` dict, verify each appears in `source_text`
- **Prevention**: Can't claim `{"roi": "500%"}` if source_text only mentions "250%"
- **Example Check**:
  ```python
  metrics = {"roi": "340%", "payback_months": 14}
  # Check "340" in source_text ✅
  # Check "14" in source_text ✅
  ```

#### 5. **Confidence Score Adjustment**
- **Mechanism**: Verification reduces confidence if issues found
- **Prevention**: Even if extraction passes, low confidence flags risky data
- **Calculation**: `confidence_final = confidence_initial × confidence_adjustment`
- **Example**: If page numbers mismatch, `confidence_adjustment = 0.8` (20% penalty)

#### 6. **Retry Feedback Loop with Error Details**
- **Mechanism**: On verification failure, provide detailed feedback to agent:
  ```
  ❌ source_text not found in document
  ❌ Value "500%" not in source_text
  ❌ Page numbers [1,2] don't contain source_text

  RETRY INSTRUCTIONS:
  1. Re-read document CAREFULLY
  2. Copy EXACT text (word-for-word)
  3. Note EXACT page number
  4. Do NOT invent or paraphrase
  ```
- **Prevention**: Agent gets specific correction, not generic "try again"
- **Success Rate**: 80%+ of failures fixed on retry (based on similar systems)

#### 7. **Complete Audit Trail for Debugging**
- **Mechanism**: Track extraction journey from document → ROI model → dashboard
- **Prevention**: When hallucination detected later, can trace back to source
- **Use Case**:
  - Dashboard shows "500% ROI"
  - Trace to `roi_model.source_extractions` → `extraction_id`
  - Check `extraction_lineage.source_document_hash`
  - Re-read original document
  - Find actual value is "250%"
  - Identify which agent execution created bad extraction

#### 8. **Multi-Layer Defense**
The combination of mechanisms creates overlapping protection:

```
Layer 1: source_text required      → Can't skip providing quote
Layer 2: source_text must exist    → Quote must be real
Layer 3: page_numbers verified     → Location must be accurate
Layer 4: metrics cross-checked     → Numbers must match quote
Layer 5: confidence adjusted       → Risk scored appropriately
Layer 6: retry with feedback       → Agent gets correction guidance
Layer 7: lineage stored            → Full audit trail persists
```

**If agent tries to hallucinate**:
- ❌ Fails at Layer 2 (source_text not found)
- ❌ Fails at Layer 4 (metrics don't match)
- → Retry with specific errors
- → Agent must find real text to pass

### Real-World Example

**Scenario**: Agent analyzes `client_roi_sheet.pdf`

**Without Lineage (Current System):**
```json
{
  "name": "500% ROI in 6 Months",
  "metrics": {"roi": "500%", "payback_months": 6},
  "source_document": "client_roi_sheet.pdf",
  "page_numbers": [1],
  "confidence": "high"
}
```
✅ Passes 4-layer validation (structure valid)
❌ **Problem**: Document actually says "250% ROI in 12 months" on page 3

**With Lineage (New System):**
```json
{
  "name": "500% ROI in 6 Months",
  "metrics": {"roi": "500%", "payback_months": 6},
  "source_text": "Clients typically achieve 500% return within 6 months",
  "page_numbers": [1]
}
```

**Verification Checks:**
1. Search for `source_text` in document → ❌ NOT FOUND
2. Check if "500" in `source_text` → ✅ Found (but source_text itself is fake)
3. Check if page 1 contains `source_text` → ❌ NOT FOUND

**Result**: ❌ Verification FAILS → Agent gets feedback → Must retry with actual quote from document

**Corrected Extraction (Retry):**
```json
{
  "name": "250% ROI in 12 Months",
  "metrics": {"roi": "250%", "payback_months": 12},
  "source_text": "Our comprehensive analysis demonstrates a 250% return on investment over 12 months based on healthcare cost reduction.",
  "page_numbers": [3],
  "extraction_confidence": 0.95
}
```

**Verification Checks:**
1. Search for `source_text` → ✅ FOUND (page 3)
2. Check "250" in `source_text` → ✅ FOUND
3. Check "12" in `source_text` → ✅ FOUND
4. Check page 3 contains `source_text` → ✅ FOUND
5. Confidence ≥ 0.7 → ✅ PASSED

**Lineage Record Created:**
```sql
INSERT INTO extraction_lineage (
  extraction_id,
  source_document_url,
  source_document_hash,
  verification_status,
  retry_attempts,
  ...
) VALUES (
  'uuid-abc-123',
  's3://client-docs/roi_sheet.pdf',
  'sha256-of-document',
  'verified',
  2,  -- Failed first attempt, passed on retry
  ...
);
```

Now client sees accurate "250% ROI" in dashboard, and every metric is traceable back to source document with exact quote and page number.

### Summary Table: Prevention Mechanisms

| Mechanism | Hallucination Type Prevented | How It Works |
|-----------|----------------------------|--------------|
| **source_text Required** | All types | Forces agent to provide quote, can't skip |
| **Full Text Search** | Invented claims | Quote must exist in document |
| **Page Number Verification** | Wrong locations | Quote must appear on claimed pages |
| **Numeric Value Cross-Check** | Invented numbers | Numbers in metrics must match quote |
| **Document Hash** | Stale data | Detects if source changed after extraction |
| **Confidence Adjustment** | Uncertain claims | Reduces confidence for suspicious data |
| **Retry Feedback** | First-attempt errors | Specific corrections guide agent |
| **Complete Lineage** | Post-hoc detection | Enables debugging and root cause analysis |

### Why This Works

1. **Incentive Alignment**: Agent can't pass verification without real source text
2. **Multi-Check Defense**: Must pass ALL checks (text exists + pages match + numbers match)
3. **Feedback Loop**: Specific error messages guide correction
4. **Audit Trail**: Complete provenance enables later verification
5. **Confidence Scoring**: Risk assessment even when checks pass

**Result**: Hallucination rate drops from ~5-15% (industry baseline) to <2% (target)

**Evidence from Testing**:
- Baseline test: 0% actual hallucination (`docs/HALLUCINATION_BASELINE_TEST_REPORT.md:42`)
- Adversarial test: 0% hallucination despite hallucination traps (`docs/ADVERSARIAL_HALLUCINATION_TEST_REPORT.md:25`)
- Current system already accurate, lineage adds verification layer for production robustness

---

## Executive Summary

### The Problem
The current 4-layer validation system validates **structure** but not **truthfulness**. Claude can generate well-formed JSON with hallucinated data that passes all validation layers.

### The Solution
Implement a **5th validation layer** (Source Verification) and **Data Lineage Tracking** to:
- ✅ Verify extracted claims exist in source documents
- ✅ Track complete data provenance from extraction to ROI Model usage
- ✅ Enable audit trails and debugging capabilities
- ✅ Prevent financial metric hallucination

### Impact
- **Hallucination Prevention:** Reduces document extraction hallucination from ~5-15% to <2%
- **Data Trust:** Every metric traceable to source document with page number and quote
- **Debugging:** Can trace wrong ROI calculations back to extraction errors
- **Compliance:** Full audit trail for healthcare data requirements

---

## Why Explicit Lineage Tracking is Required

### Claude's Fundamental Limitations

Many developers ask: **"Can Claude track data lineage automatically without building this system?"**

**Answer: No.** Claude (and all LLMs) have fundamental limitations that require explicit lineage tracking infrastructure.

#### 1. Stateless API Calls - No Memory Between Requests

**Problem:** Claude has zero memory between API calls. Each request is completely independent.

```python
# Call 1: Extract data from document
response_1 = claude.extract_data(document="roi_sheet.pdf")
# Returns: {"roi": "250%"}

# Call 2: Build ROI model (minutes/hours later)
response_2 = claude.build_roi_model(extractions=response_1)
# ❌ Claude has NO MEMORY of Call 1
# ❌ Cannot remember where "250%" came from
# ❌ Cannot track which document was used
```

**Why This Matters:**
- When client asks "where did this 250% ROI come from?", Claude can't answer
- No way to trace back to source document
- No way to detect if source document has changed since extraction

#### 2. No Persistent Storage

**Problem:** Claude cannot store data between sessions. All context is lost when the conversation ends.

**What Claude Cannot Do:**
- ❌ Store document hashes for integrity checking
- ❌ Remember which extractions were used in which ROI models
- ❌ Track when data was extracted
- ❌ Maintain audit logs
- ❌ Store source text quotes for verification

**What This Means:**
Without our lineage system, there's no record of:
- What document was analyzed
- When the extraction occurred
- What model/prompt was used
- Whether verification passed
- Which dashboards use this data

#### 3. Cannot Compute Cryptographic Hashes

**Problem:** Claude cannot generate true SHA256 hashes or other cryptographic functions.

```python
# Our System
document_hash = hashlib.sha256(document_bytes).hexdigest()
# Returns: "a1b2c3d4e5f6..." (actual cryptographic hash)

# Claude's Attempt
claude.generate_hash(document)
# ❌ Cannot access document bytes
# ❌ Cannot compute real SHA256
# ❌ Could only generate fake/mock hash
```

**Why This Matters:**
- Document integrity verification requires real cryptographic hashes
- Detecting document changes requires comparing actual file hashes
- Regulatory compliance requires provable, non-spoofable hashes

#### 4. Cannot Track Usage Across Systems

**Problem:** Claude cannot monitor how data flows through our multi-agent system.

**Our System Flow:**
```
Document → DocumentAnalysisAgent → ROI Classification → ROI Model Builder → Template Generator → Dashboard
```

**What Claude Cannot Track:**
- ❌ Which extractions were used by ROI Model Builder
- ❌ Which ROI models power which dashboards
- ❌ How many times data has been accessed
- ❌ Which prospects viewed which dashboards
- ❌ When data becomes stale or needs refresh

**Why This Matters:**
- When document is found incorrect, need to identify ALL affected dashboards
- When client disputes ROI calculation, need complete audit trail
- When optimizing system, need usage analytics

#### 5. Cannot Generate True UUIDs

**Problem:** Claude cannot generate globally unique identifiers that persist across systems.

```python
# Our System
extraction_id = uuid.uuid4()
# Generates: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
# Guaranteed unique across all systems and time

# Claude's Attempt
# ❌ Could generate string that looks like UUID
# ❌ But not truly unique or persistent
# ❌ No way to link extractions across database, cache, logs
```

---

### What Claude CAN vs CANNOT Do

| Capability | Claude | Our Lineage System | Winner | Why It Matters |
|------------|--------|-------------------|--------|----------------|
| **Extract Data from Documents** | ✅ Yes | N/A | Claude | Core competency: reading and understanding |
| **Format Metadata in Response** | ✅ Yes | N/A | Claude | Can structure JSON with metadata fields |
| **Express Uncertainty** | ✅ Yes | N/A | Claude | Can say "low confidence" or "unclear" |
| **Remember Previous Extractions** | ❌ No | ✅ Yes | System | Stateless - no memory between calls |
| **Store Document Hashes** | ❌ No | ✅ Yes | System | Cannot compute or persist SHA256 |
| **Track Data Usage** | ❌ No | ✅ Yes | System | Cannot monitor cross-system flows |
| **Maintain Audit Logs** | ❌ No | ✅ Yes | System | No persistent storage |
| **Verify Source Text Later** | ❌ No | ✅ Yes | System | Cannot re-read original document |
| **Detect Document Changes** | ❌ No | ✅ Yes | System | No hash comparison capability |
| **Link Extractions to Dashboards** | ❌ No | ✅ Yes | System | Cannot track downstream usage |
| **Generate Compliance Reports** | ❌ No | ✅ Yes | System | No access to lineage database |

---

### Real-World Scenario: Why Claude Alone Fails

**Scenario:** Client disputes ROI calculation 3 months after dashboard generation.

#### Without Lineage System (Claude Only)

**Client Question:** "Where did this 340% ROI number come from?"

**What Happens:**
1. ❌ No record of which document was analyzed
2. ❌ No timestamp of when extraction occurred
3. ❌ No proof of what the document said at that time
4. ❌ Cannot verify if document has changed since
5. ❌ Cannot show which agent/model was used
6. ❌ No audit trail for compliance

**Result:** Cannot answer client question. Fails regulatory audit.

#### With Lineage System (Explicit Tracking)

**Client Question:** "Where did this 340% ROI number come from?"

**What Happens:**
1. ✅ Query: `SELECT * FROM extraction_lineage WHERE used_in_dashboards CONTAINS dashboard_id`
2. ✅ Find extraction: `extraction_id = "uuid-abc-123"`
3. ✅ Retrieve source: `source_document_url = "s3://docs/client_roi_sheet.pdf"`
4. ✅ Check integrity: `source_document_hash = "sha256:a1b2..."`
5. ✅ Find source text: `source_text = "Blue Shield achieved 340% ROI excluding implementation costs"`
6. ✅ Show page: `page_numbers = [3]`
7. ✅ Provide timestamp: `extraction_timestamp = "2025-09-15T10:23:45Z"`
8. ✅ Show verification: `verification_status = "verified"`

**Result:** Complete audit trail. Client satisfied. Regulatory compliance met.

---

### Primary Purpose: Human Trust and Compliance (80%)

**Key Insight:** Lineage tracking is primarily for **humans**, not agents.

| User Type | Use Cases | Percentage |
|-----------|-----------|------------|
| **Humans** | Compliance audits, client questions, error investigation, manual review, trust/transparency | **80%** |
| **Agents** | Auto-alerts on doc changes, auto-retry failures, auto-archive old data | **20%** |

**Why Humans Need This:**
1. **Regulatory Compliance**: SOC2, HIPAA, financial regulations require data provenance
2. **Client Trust**: Clients want to see exactly where numbers came from
3. **Error Investigation**: When something's wrong, engineers trace the problem
4. **Manual Review**: Subject matter experts verify critical extractions
5. **Legal Protection**: Provable audit trail protects company from disputes

**Why Agents Need This (Secondary):**
1. **Automated Monitoring**: Detect when source documents change
2. **Auto-Retry**: Re-extract if verification fails
3. **Data Archival**: Clean up old, unused extractions

---

### Key Takeaways

1. **Claude is stateless** → Cannot remember extractions across API calls
2. **Claude has no storage** → Cannot maintain audit logs
3. **Claude cannot hash** → Cannot verify document integrity
4. **Claude cannot track usage** → Cannot link extractions to downstream systems
5. **Our system is mandatory** → Explicit lineage tracking is not optional for production

**Bottom Line:**

> Claude is excellent at **understanding and extracting** data from documents. But it cannot **remember, verify, or track** that data over time. That's why we build explicit lineage infrastructure.

**Analogy:**
- **Claude** = Brilliant researcher who reads documents and extracts insights
- **Lineage System** = Laboratory notebook that records what was found, when, from where, and how it's been used
- **Both are required** for trustworthy, auditable AI systems

---

## Problem Statement

### Current Validation System Gaps

#### What 4-Layer Validation Does
```
Layer 1: JSON Extraction    → Can JSON be found?
Layer 2: JSON Parsing        → Is syntax valid?
Layer 3: Pydantic Validation → Do fields have correct types?
Layer 4: Business Logic      → Do values meet business rules?
```

#### What It Does NOT Check
- ❌ Does extracted claim exist in source document?
- ❌ Are page_numbers accurate?
- ❌ Are numeric values from the document or invented?
- ❌ Is source_text verbatim from the document?
- ❌ Where did this data come from originally?
- ❌ Which ROI Models depend on this extraction?

### Real-World Hallucination Example

**Scenario:** Agent analyzes `roi_sheet.pdf`

**Current System Allows:**
```json
{
  "extracted_value_propositions": [{
    "name": "500% ROI in 6 Months",
    "description": "Achieve 500% return on investment within 6 months",
    "metrics": {"roi": "500%", "payback_months": 6},
    "source_document": "roi_sheet.pdf",
    "page_numbers": [1, 2],
    "confidence": "high"
  }]
}
```

**Problem:** Document actually says "250% ROI in 12 months" on page 3, but this passes validation!

**Why It Passes:**
- ✅ Valid JSON structure
- ✅ All required fields present
- ✅ Correct data types
- ✅ Business rules met (has ≥1 value prop, description ≥30 chars)

**Missing:** No verification that "500%" and "6 months" exist in the document.

---

## Current State Analysis

### Existing Components (Working)

#### 1. Document Analysis Agent
- **File:** `agents/document_analysis_agent.py`
- **Functionality:**
  - Reads PDFs, DOCX, TXT from S3
  - Extracts value propositions, financial metrics, clinical outcomes
  - Uses Claude Sonnet 4 via AWS Bedrock
  - 4-layer validation with 3 retry attempts

#### 2. Pydantic Data Models
- **File:** `core/models/research_models.py`
- **Models:**
  - `DocumentAnalysisResult`
  - `ExtractedValueProposition`
  - `ExtractedClinicalOutcome`
  - `ExtractedFinancialMetric`

#### 3. Current Output Fields (Per Extraction)
```python
source_document: str          # ✅ Has this
page_numbers: List[int]       # ✅ Has this
confidence: str               # ✅ Has this ("high"/"medium"/"low")
```

### Missing Components (Need to Build)

#### 1. Source Verification Layer
- **Purpose:** Validate extracted claims against source documents
- **Location:** Will be added as Layer 5 in validation pipeline

#### 2. Verbatim Quote Storage
- **Field:** `source_text` (not currently in models)
- **Purpose:** Store exact text from document for verification

#### 3. Data Lineage Tracking System
- **Database:** New `extraction_lineage` table
- **Purpose:** Track complete data provenance

#### 4. Extraction Confidence Scoring
- **Field:** `extraction_confidence: float` (numerical 0.0-1.0)
- **Current:** Only string "high"/"medium"/"low"

---

## Solution Architecture

### Overview: 5-Layer Validation + Lineage Tracking

```
┌─────────────────────────────────────────────────────────────┐
│  Document Analysis Agent (Claude Sonnet 4)                  │
│  ↓                                                           │
│  Raw LLM Response (JSON with extracted claims)              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  EXISTING: 4-Layer Validation                               │
│  ├─ Layer 1: JSON Extraction                                │
│  ├─ Layer 2: JSON Parsing                                   │
│  ├─ Layer 3: Pydantic Validation                            │
│  └─ Layer 4: Business Logic Validation                      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  NEW: Layer 5 - Source Verification                         │
│  ├─ Check 1: source_text exists in full_document_text      │
│  ├─ Check 2: source_text appears on claimed page_numbers   │
│  ├─ Check 3: Numeric values in source_text                 │
│  ├─ Check 4: Confidence threshold (≥0.7)                   │
│  └─ Result: Pass → Continue | Fail → Retry with feedback   │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  NEW: Lineage Tracking                                      │
│  ├─ Generate extraction_id (UUID)                          │
│  ├─ Compute document_hash (SHA256)                         │
│  ├─ Record extraction_method (PyPDF2/Vision)               │
│  ├─ Store prompt_version, model_name, timestamp            │
│  └─ Write to extraction_lineage table                      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  Validated Extraction + Lineage Record                      │
│  ↓                                                           │
│  Stored in PostgreSQL + Available for ROI Model Builder     │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Data Model Updates (2 hours)

#### 1.1 Update Pydantic Models
**File:** `core/models/research_models.py`

**Add New Fields to `ExtractedValueProposition`:**
- `source_text: str` - Verbatim quote from document (MANDATORY)
- `extraction_confidence: float` - Numerical confidence (0.0-1.0)
- `verification_status: str` - "unverified" | "verified" | "failed"
- `verification_method: Optional[str]` - How verification was performed
- `verification_issues: List[str]` - List of verification problems found

**Apply Same Changes to:**
- `ExtractedClinicalOutcome`
- `ExtractedFinancialMetric`
- `ExtractedCompetitiveAdvantage`

**Backward Compatibility:**
- Make new fields optional with defaults
- Existing extractions won't break
- Gradual migration path

#### 1.2 Create Lineage Data Model
**New File:** `core/lineage/models.py`

**New Model: `ExtractionLineage`**

**Fields:**
- `extraction_id: UUID` - Primary key
- `source_document_url: str` - S3 path
- `source_document_hash: str` - SHA256 of original document
- `source_document_size: int` - File size in bytes
- `extraction_agent: str` - "DocumentAnalysisAgent"
- `extraction_method: str` - "PyPDF2" | "python-docx" | "Claude_Vision"
- `extraction_timestamp: datetime` - When extraction occurred
- `extraction_model: str` - "claude-sonnet-4-20250514"
- `extraction_model_provider: str` - "aws_bedrock"
- `prompt_template_version: str` - Version from mare-triton-research-prompts
- `validation_layers_passed: List[str]` - Which layers succeeded
- `retry_attempts: int` - Number of retries before success
- `text_quality_score: Optional[float]` - PDF quality score (hybrid processing)
- `extraction_duration_seconds: float` - Time taken
- `extraction_confidence_final: float` - Final confidence after verification
- `verification_status: str` - "verified" | "failed" | "skipped"
- `verification_issues: List[str]` - Issues found during verification
- `used_in_roi_models: List[UUID]` - ROI Models referencing this extraction
- `used_in_dashboards: List[UUID]` - Dashboards using this data
- `last_accessed: Optional[datetime]` - Last time data was retrieved
- `created_at: datetime` - Record creation time
- `updated_at: datetime` - Last update time

---

### Phase 2: Source Verification Implementation (4 hours)

#### 2.1 Create Hallucination Detector Module
**New File:** `core/validation/hallucination_detector.py`

**Primary Function: `verify_extraction_against_source()`**

**Input Parameters:**
- `extraction: ExtractedValueProposition` - The extracted claim
- `full_document_text: str` - Complete document text
- `document_pages: List[str]` - Text split by pages
- `document_metadata: Dict` - Document info (filename, size, etc.)

**Verification Checks:**

##### Check 1: Full Text Search
- Search for `extraction.source_text` in `full_document_text`
- **Pass:** source_text found → Continue
- **Fail:** source_text not found → Return hallucination error

##### Check 2: Page Number Verification
- Find which pages contain `extraction.source_text`
- Compare found pages with `extraction.page_numbers`
- **Pass:** At least one page_number matches → Continue
- **Fail:** No page_numbers match → Add issue to report

##### Check 3: Numeric Value Verification
- Extract all numeric values from `extraction.metrics`
- For each number, check if it appears in `extraction.source_text`
- **Examples:**
  - `{"roi": "340%"}` → Check if "340" or "340%" in source_text
  - `{"payback_months": 14}` → Check if "14" in source_text
- **Pass:** All numbers found → Continue
- **Fail:** Numbers missing → Add issue to report

##### Check 4: Confidence Threshold
- Check if `extraction.extraction_confidence >= 0.7`
- **Pass:** Confidence high enough → Continue
- **Fail:** Confidence too low → Flag for review

##### Check 5: Description Consistency
- Compare `extraction.description` with `extraction.source_text`
- Ensure description doesn't contradict source
- Use simple keyword matching (not LLM-based)

**Output:**
```python
{
    "is_hallucinated": bool,              # True if any critical check failed
    "verification_method": str,           # "multi_check"
    "confidence_adjustment": float,       # Multiplier (0.0-1.0)
    "verification_status": str,           # "verified" | "failed"
    "issues": List[str],                  # Specific problems found
    "checks_passed": List[str],           # Which checks succeeded
    "checks_failed": List[str]            # Which checks failed
}
```

#### 2.2 Integrate Verification into Agent Retry Loop
**File:** `agents/document_analysis_agent.py`

**Modification Point:** Inside `run_with_retry()` function

**Current Flow:**
```
Attempt N:
  1. Execute agent.run()
  2. Extract JSON (Layer 1)
  3. Parse JSON (Layer 2)
  4. Pydantic validation (Layer 3)
  5. Business logic validation (Layer 4)
  6. Return result OR retry
```

**New Flow with Layer 5:**
```
Attempt N:
  1. Execute agent.run()
  2. Extract JSON (Layer 1)
  3. Parse JSON (Layer 2)
  4. Pydantic validation (Layer 3)
  5. Business logic validation (Layer 4)

  6. NEW: Source Verification (Layer 5)
     For each extraction in result:
       - Call verify_extraction_against_source()
       - If is_hallucinated=True:
           * Build detailed error feedback
           * Append feedback to message
           * Increment attempt counter
           * Retry agent execution
       - If is_hallucinated=False:
           * Adjust confidence score
           * Mark verification_status="verified"
           * Continue to next extraction

  7. Return validated result
```

**Retry Feedback Format:**
```
PREVIOUS ATTEMPT FEEDBACK (Attempt N):

Source Verification Failed for extraction "500% ROI in 6 Months":
  ❌ source_text not found in document
  ❌ Value "500%" does not appear in source_text
  ❌ Page numbers [1, 2] do not contain source_text

INSTRUCTIONS FOR RETRY:
1. Re-read the document carefully
2. Copy EXACT text from the document (word-for-word)
3. Include the exact page number where you found the text
4. Do NOT invent or paraphrase - use verbatim quotes
5. If uncertain, mark confidence as "low" (<0.7)
```

---

### Phase 3: Lineage Tracking Implementation (4 hours)

#### 3.1 Create Lineage Tracker Module
**New File:** `core/lineage/lineage_tracker.py`

**Primary Function: `create_lineage_record()`**

**Input Parameters:**
- `extraction: ExtractedValueProposition` - The validated extraction
- `document_url: str` - S3 path to source document
- `document_content: bytes` - Raw document bytes (for hashing)
- `extraction_context: Dict` - Metadata about extraction process

**Workflow:**

##### Step 1: Generate Extraction ID
- Create UUID4 for this extraction
- This ID links extraction to lineage record

##### Step 2: Compute Document Hash
- Calculate SHA256 hash of document bytes
- Purpose: Detect if document changes over time
- Store hash in lineage record

##### Step 3: Gather Extraction Metadata
- Agent name: "DocumentAnalysisAgent"
- Model: From config or context
- Method: "PyPDF2" | "python-docx" | "Claude_Vision"
- Timestamp: Current UTC time
- Prompt version: From mare-triton-research-prompts repo

##### Step 4: Record Validation Journey
- List all validation layers passed: ["json", "pydantic", "business", "source_verification"]
- Record retry attempts: 1, 2, or 3
- Store confidence scores: initial and final

##### Step 5: Store Quality Metrics
- Text quality score (if hybrid PDF processing used)
- Extraction duration
- Confidence adjustment factor

##### Step 6: Initialize Usage Tracking
- `used_in_roi_models`: Empty list (populated later)
- `used_in_dashboards`: Empty list (populated later)
- `last_accessed`: NULL (updated on retrieval)

**Output:**
- `ExtractionLineage` object
- Ready to be stored in database

#### 3.2 Database Schema Design
**Migration File:** `migrations/add_extraction_lineage_table.sql`

**New Table: `extraction_lineage`**

**Schema:**
```sql
CREATE TABLE extraction_lineage (
    -- Primary identification
    extraction_id UUID PRIMARY KEY,

    -- Source document tracking
    source_document_url TEXT NOT NULL,
    source_document_hash VARCHAR(64) NOT NULL,
    source_document_size BIGINT,

    -- Extraction metadata
    extraction_agent VARCHAR(100) NOT NULL,
    extraction_method VARCHAR(50) NOT NULL,
    extraction_timestamp TIMESTAMP NOT NULL,
    extraction_model VARCHAR(100) NOT NULL,
    extraction_model_provider VARCHAR(50),
    prompt_template_version VARCHAR(20),

    -- Validation tracking
    validation_layers_passed TEXT[] NOT NULL,
    retry_attempts INTEGER DEFAULT 1,

    -- Quality metrics
    text_quality_score FLOAT,
    extraction_duration_seconds FLOAT,
    extraction_confidence_initial FLOAT,
    extraction_confidence_final FLOAT,

    -- Verification results
    verification_status VARCHAR(20) NOT NULL,
    verification_issues TEXT[],

    -- Usage tracking (populated by other systems)
    used_in_roi_models UUID[],
    used_in_dashboards UUID[],
    last_accessed TIMESTAMP,

    -- Housekeeping
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_lineage_document_hash ON extraction_lineage(source_document_hash);
CREATE INDEX idx_lineage_timestamp ON extraction_lineage(extraction_timestamp);
CREATE INDEX idx_lineage_verification ON extraction_lineage(verification_status);
CREATE INDEX idx_lineage_roi_models ON extraction_lineage USING gin(used_in_roi_models);

-- Index for finding extractions by document
CREATE INDEX idx_lineage_document_url ON extraction_lineage(source_document_url);
```

**Foreign Key Considerations:**
- `used_in_roi_models`: Array of UUIDs referencing `roi_models.model_id`
- No strict foreign key constraint (soft reference)
- Allows ROI models to be deleted without breaking lineage

#### 3.3 Lineage Storage Workflow
**File:** `agents/document_analysis_agent.py` (modified)

**After Layer 5 Verification Passes:**

##### Step 1: Create Lineage Records
```
For each validated extraction:
  1. Call create_lineage_record()
  2. Pass extraction + document metadata
  3. Receive ExtractionLineage object
```

##### Step 2: Batch Insert into Database
```
Using PostgreSQL transaction:
  1. Begin transaction
  2. Insert all ExtractionLineage records
  3. Commit if all inserts succeed
  4. Rollback if any insert fails
```

##### Step 3: Link Extractions to Lineage
```
Add extraction_id to each extraction object:
  extraction.extraction_id = lineage.extraction_id

This allows:
  - Retrieval of lineage from extraction
  - Reverse lookup (lineage → extraction)
```

##### Step 4: Return Enhanced Result
```
Return DocumentAnalysisResult with:
  - All extractions (with extraction_ids)
  - Lineage records stored in database
  - Ready for ROI Model Builder to consume
```

---

### Phase 4: Usage Tracking Integration (2 hours)

#### 4.1 Update ROI Model Builder
**File:** `agents/roi_model_builder_agent.py`

**When ROI Model Uses Extraction:**

##### Step 1: Receive Extraction with Lineage ID
```
Input: ExtractedValueProposition with extraction_id
```

##### Step 2: Record Usage
```
Function: record_extraction_usage()

Input:
  - extraction_id: UUID
  - roi_model_id: UUID

Action:
  UPDATE extraction_lineage
  SET
    used_in_roi_models = array_append(used_in_roi_models, roi_model_id),
    last_accessed = NOW(),
    updated_at = NOW()
  WHERE extraction_id = extraction_id;
```

##### Step 3: Store Bi-Directional Link
```
ROI Model stores:
  - source_extractions: List[UUID] (extraction_ids)

Enables:
  - Forward: ROI Model → Extractions it uses
  - Backward: Extraction → ROI Models using it
```

#### 4.2 Dashboard Data Generation
**File:** `tasks/prospect_data_generation.py`

**When Dashboard Uses ROI Model:**

##### Step 1: ROI Model → Dashboard Link
```
Dashboard stores:
  - roi_model_id: UUID

ROI Model has:
  - source_extractions: List[UUID]

Transitive relationship:
  Dashboard → ROI Model → Extractions
```

##### Step 2: Record Dashboard Usage
```
Function: record_dashboard_usage()

For each extraction_id in roi_model.source_extractions:
  UPDATE extraction_lineage
  SET
    used_in_dashboards = array_append(used_in_dashboards, dashboard_id),
    last_accessed = NOW()
  WHERE extraction_id = extraction_id;
```

#### 4.3 Lineage Query API
**New File:** `api/routes/lineage.py`

**Endpoints:**

##### GET `/lineage/{extraction_id}`
- Retrieve complete lineage for one extraction
- Returns: `ExtractionLineage` object

##### GET `/lineage/document/{document_hash}`
- Find all extractions from a specific document
- Returns: List of `ExtractionLineage` objects

##### GET `/lineage/roi-model/{roi_model_id}`
- Find all extractions used by an ROI Model
- Returns: List of `ExtractionLineage` objects

##### GET `/lineage/dashboard/{dashboard_id}`
- Find all extractions used by a Dashboard
- Returns: List of `ExtractionLineage` objects (via ROI Model)

##### GET `/lineage/audit-trail/{extraction_id}`
- Complete audit trail: Extraction → ROI Model → Dashboard → Prospects
- Returns: Full chain of usage

---

## Workflow Diagrams

### Diagram 1: Source Verification Flow (Layer 5)

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 4 Business Logic Validation PASSES                    │
└───────────────────────┬──────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│  LAYER 5: SOURCE VERIFICATION                                │
│                                                               │
│  For each extraction in result:                              │
│    ↓                                                          │
│  ┌─────────────────────────────────────────────────┐         │
│  │ Check 1: Full Text Search                       │         │
│  │ Question: Is source_text in full_document_text? │         │
│  └────────┬──────────────────────────┬─────────────┘         │
│           ↓ YES                      ↓ NO                    │
│      ┌─────────┐              ┌──────────────┐               │
│      │ PASS    │              │ FAIL         │               │
│      │ Continue│              │ Hallucinated │               │
│      └────┬────┘              └──────┬───────┘               │
│           ↓                          ↓                        │
│  ┌─────────────────────────────────────────────────┐         │
│  │ Check 2: Page Number Verification                │         │
│  │ Question: Does source_text appear on page_numbers?│        │
│  └────────┬──────────────────────────┬─────────────┘         │
│           ↓ YES                      ↓ NO                    │
│      ┌─────────┐              ┌──────────────┐               │
│      │ PASS    │              │ ISSUE        │               │
│      │ Continue│              │ Add to list  │               │
│      └────┬────┘              └──────┬───────┘               │
│           ↓                          ↓                        │
│  ┌─────────────────────────────────────────────────┐         │
│  │ Check 3: Numeric Value Verification              │         │
│  │ Question: Are metrics values in source_text?     │         │
│  └────────┬──────────────────────────┬─────────────┘         │
│           ↓ YES                      ↓ NO                    │
│      ┌─────────┐              ┌──────────────┐               │
│      │ PASS    │              │ ISSUE        │               │
│      │ Continue│              │ Add to list  │               │
│      └────┬────┘              └──────┬───────┘               │
│           ↓                          ↓                        │
│  ┌─────────────────────────────────────────────────┐         │
│  │ Check 4: Confidence Threshold                    │         │
│  │ Question: Is extraction_confidence >= 0.7?       │         │
│  └────────┬──────────────────────────┬─────────────┘         │
│           ↓ YES                      ↓ NO                    │
│      ┌─────────┐              ┌──────────────┐               │
│      │ PASS    │              │ ISSUE        │               │
│      │         │              │ Add to list  │               │
│      └────┬────┘              └──────┬───────┘               │
│           ↓                          ↓                        │
│  ┌─────────────────────────────────────────────────┐         │
│  │ Aggregate Results                                │         │
│  │ - Count issues                                   │         │
│  │ - Calculate confidence_adjustment                │         │
│  │ - Determine verification_status                  │         │
│  └────────┬─────────────────────────────────────────┘         │
│           ↓                                                   │
└───────────┴───────────────────────────────────────────────────┘
            ↓
     ┌──────────────┐
     │ Any critical │
     │ failures?    │
     └─────┬────┬───┘
           ↓ NO ↓ YES
    ┌──────────┐  ┌─────────────────────────────┐
    │ VERIFIED │  │ BUILD RETRY FEEDBACK        │
    │ Continue │  │ - List all issues           │
    │ to       │  │ - Provide correction guide  │
    │ Lineage  │  │ - Append to message         │
    └──────────┘  │ - Retry agent execution     │
                  └─────────────────────────────┘
```

### Diagram 2: Lineage Tracking Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 5 Verification PASSES                                 │
│  (All extractions verified)                                  │
└───────────────────────┬──────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│  LINEAGE TRACKING                                            │
│                                                               │
│  Step 1: Generate Extraction IDs                             │
│  ┌─────────────────────────────────────────────────┐         │
│  │ For each extraction:                             │         │
│  │   extraction_id = uuid4()                        │         │
│  │   extraction.extraction_id = extraction_id       │         │
│  └─────────────────────────────────────────────────┘         │
│                        ↓                                      │
│  Step 2: Compute Document Hash                               │
│  ┌─────────────────────────────────────────────────┐         │
│  │ document_hash = SHA256(document_bytes)           │         │
│  │ Purpose: Detect document changes over time       │         │
│  └─────────────────────────────────────────────────┘         │
│                        ↓                                      │
│  Step 3: Gather Extraction Context                           │
│  ┌─────────────────────────────────────────────────┐         │
│  │ context = {                                      │         │
│  │   agent: "DocumentAnalysisAgent",                │         │
│  │   model: "claude-sonnet-4-20250514",             │         │
│  │   method: "PyPDF2",                              │         │
│  │   prompt_version: "v2.1",                        │         │
│  │   timestamp: datetime.utcnow(),                  │         │
│  │   duration_seconds: 12.5,                        │         │
│  │   validation_layers: ["json", "pydantic", ...],  │         │
│  │   retry_attempts: 1,                             │         │
│  │   text_quality_score: 0.95                       │         │
│  │ }                                                │         │
│  └─────────────────────────────────────────────────┘         │
│                        ↓                                      │
│  Step 4: Create Lineage Records                              │
│  ┌─────────────────────────────────────────────────┐         │
│  │ For each extraction:                             │         │
│  │   lineage = ExtractionLineage(                   │         │
│  │     extraction_id=extraction_id,                 │         │
│  │     source_document_url=s3_path,                 │         │
│  │     source_document_hash=document_hash,          │         │
│  │     **context                                    │         │
│  │   )                                              │         │
│  └─────────────────────────────────────────────────┘         │
│                        ↓                                      │
│  Step 5: Store in Database                                   │
│  ┌─────────────────────────────────────────────────┐         │
│  │ BEGIN TRANSACTION;                               │         │
│  │   INSERT INTO extraction_lineage (...);          │         │
│  │   INSERT INTO extraction_lineage (...);          │         │
│  │   ...                                            │         │
│  │ COMMIT;                                          │         │
│  └─────────────────────────────────────────────────┘         │
│                        ↓                                      │
└────────────────────────┴──────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  RESULT                                                      │
│  - DocumentAnalysisResult (with extraction_ids)             │
│  - Lineage records stored in PostgreSQL                     │
│  - Ready for ROI Model Builder consumption                  │
└──────────────────────────────────────────────────────────────┘
```

### Diagram 3: End-to-End Data Flow with Lineage

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLIENT UPLOADS DOCUMENT                                  │
│    - roi_sheet.pdf uploaded to S3                          │
│    - Path: s3://triton-docs/client123/roi_sheet.pdf        │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. DOCUMENT ANALYSIS AGENT PROCESSES                        │
│    - Downloads from S3                                      │
│    - Extracts text with PyPDF2                              │
│    - Claude analyzes text → JSON output                     │
│    - 5-layer validation (including source verification)     │
│    - Creates lineage records                                │
│                                                              │
│    Output:                                                   │
│    ├─ ExtractedValueProposition #1 (extraction_id: uuid-1) │
│    │  └─ Lineage Record #1 (links to uuid-1)               │
│    ├─ ExtractedValueProposition #2 (extraction_id: uuid-2) │
│    │  └─ Lineage Record #2 (links to uuid-2)               │
│    └─ ...                                                    │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ROI CLASSIFICATION AGENT                                 │
│    - Receives extractions with extraction_ids               │
│    - Determines ROI Model Type (B1-B13)                     │
│    - Passes to ROI Model Builder                            │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. ROI MODEL BUILDER AGENT                                  │
│    - Uses extractions to build ROI Model                    │
│    - Records usage in lineage:                              │
│      UPDATE extraction_lineage                              │
│      SET used_in_roi_models = [roi_model_id]               │
│      WHERE extraction_id IN (uuid-1, uuid-2, ...)           │
│                                                              │
│    - Stores ROI Model with source_extractions:              │
│      roi_model.source_extractions = [uuid-1, uuid-2, ...]   │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. DASHBOARD TEMPLATE GENERATOR                             │
│    - Generates dashboard for prospect                       │
│    - Links to ROI Model (which has source_extractions)      │
│    - Records dashboard usage in lineage:                    │
│      UPDATE extraction_lineage                              │
│      SET used_in_dashboards = [dashboard_id]                │
│      WHERE extraction_id IN (uuid-1, uuid-2, ...)           │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. COMPLETE DATA LINEAGE ESTABLISHED                        │
│                                                              │
│    Document (S3)                                             │
│      ↓ extracted_by                                         │
│    Extraction (uuid-1)                                       │
│      ↓ used_in                                              │
│    ROI Model (model-id)                                      │
│      ↓ powers                                               │
│    Dashboard (dashboard-id)                                  │
│      ↓ viewed_by                                            │
│    Prospect (prospect-id)                                    │
│                                                              │
│    TRACEABILITY: Can trace any metric back to source        │
└─────────────────────────────────────────────────────────────┘
```

### Diagram 4: Retry Flow with Source Verification Feedback

```
┌──────────────────────────────────────────────────────────────┐
│ ATTEMPT 1                                                    │
│ ├─ Layer 1: JSON Extraction ✅                              │
│ ├─ Layer 2: JSON Parsing ✅                                 │
│ ├─ Layer 3: Pydantic Validation ✅                          │
│ ├─ Layer 4: Business Logic ✅                               │
│ └─ Layer 5: Source Verification ❌ FAILED                   │
│                                                              │
│    Issues Found:                                             │
│    - source_text not found in document                       │
│    - Value "500%" not in source_text                         │
│    - page_numbers [1,2] don't contain source_text           │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ BUILD RETRY FEEDBACK                                         │
│                                                              │
│ Message += """                                               │
│ ## PREVIOUS ATTEMPT FEEDBACK (Attempt 1)                     │
│                                                              │
│ Source Verification Failed for: "500% ROI in 6 Months"       │
│                                                              │
│ ❌ CRITICAL ERRORS:                                          │
│   - source_text not found in full document                   │
│   - Value "500%" does not appear in source_text you provided │
│   - page_numbers [1, 2] do not contain the source_text      │
│                                                              │
│ ⚠️  WARNINGS:                                                │
│   - extraction_confidence (0.9) seems too high given errors  │
│                                                              │
│ 📋 INSTRUCTIONS FOR RETRY:                                   │
│ 1. Re-read roi_sheet.pdf CAREFULLY                          │
│ 2. Find the EXACT location where ROI is mentioned           │
│ 3. Copy the text WORD-FOR-WORD (verbatim)                   │
│ 4. Include at least 2-3 sentences of context                │
│ 5. Note the EXACT page number                               │
│ 6. Do NOT invent or paraphrase                              │
│ 7. If unsure, set extraction_confidence < 0.7               │
│                                                              │
│ Example correct format:                                      │
│ {                                                            │
│   "source_text": "Our analysis shows a 250% return on       │
│   investment over 24 months, with payback in 12 months.",   │
│   "metrics": {"roi": "250%", "payback_months": 12},         │
│   "page_numbers": [3],                                       │
│   "extraction_confidence": 0.95                              │
│ }                                                            │
│ """                                                          │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ ATTEMPT 2 (with feedback)                                    │
│ ├─ Layer 1: JSON Extraction ✅                              │
│ ├─ Layer 2: JSON Parsing ✅                                 │
│ ├─ Layer 3: Pydantic Validation ✅                          │
│ ├─ Layer 4: Business Logic ✅                               │
│ └─ Layer 5: Source Verification ✅ PASSED                   │
│                                                              │
│    Corrected Output:                                         │
│    - source_text: "Our analysis shows a 250% ROI..."        │
│    - metrics: {"roi": "250%", "payback_months": 12}         │
│    - page_numbers: [3]                                       │
│    - All verification checks pass                            │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ SUCCESS                                                      │
│ - Extraction verified against source                         │
│ - Lineage record created                                     │
│ - Ready for ROI Model Builder                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Models

### Updated Pydantic Models

#### ExtractedValueProposition (Enhanced)
```python
class ExtractedValueProposition(BaseModel):
    # Existing fields
    name: str = Field(min_length=10)
    description: str = Field(min_length=30)
    metrics: Dict[str, Any] = {}
    source_document: str
    page_numbers: List[int]
    confidence: str  # "high" | "medium" | "low"

    # NEW FIELDS for hallucination prevention
    source_text: str = Field(
        description="Verbatim quote from source document (MANDATORY)"
    )
    extraction_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Numerical confidence score"
    )

    # NEW FIELDS for verification tracking
    verification_status: str = Field(
        default="unverified",
        description="unverified | verified | failed"
    )
    verification_method: Optional[str] = Field(
        default=None,
        description="How verification was performed"
    )
    verification_issues: List[str] = Field(
        default_factory=list,
        description="Issues found during verification"
    )

    # NEW FIELD for lineage linking
    extraction_id: Optional[UUID] = Field(
        default=None,
        description="Links to extraction_lineage table"
    )
```

#### ExtractionLineage (New Model)
```python
class ExtractionLineage(BaseModel):
    # Primary identification
    extraction_id: UUID = Field(default_factory=uuid4)

    # Source document tracking
    source_document_url: str
    source_document_hash: str  # SHA256
    source_document_size: int

    # Extraction metadata
    extraction_agent: str = "DocumentAnalysisAgent"
    extraction_method: str  # "PyPDF2" | "python-docx" | "Claude_Vision"
    extraction_timestamp: datetime
    extraction_model: str  # "claude-sonnet-4-20250514"
    extraction_model_provider: str = "aws_bedrock"

    # Prompt tracking
    prompt_template_version: str
    prompt_template_source: str = "mare-triton-research-prompts"

    # Validation journey
    validation_layers_passed: List[str]
    validation_layers_failed: List[str] = Field(default_factory=list)
    retry_attempts: int = 1

    # Quality metrics
    text_quality_score: Optional[float] = None
    extraction_duration_seconds: float
    extraction_confidence_initial: float
    extraction_confidence_final: float
    confidence_adjustment_factor: float

    # Verification results
    verification_status: str  # "verified" | "failed" | "skipped"
    verification_issues: List[str] = Field(default_factory=list)
    verification_checks_passed: List[str] = Field(default_factory=list)
    verification_checks_failed: List[str] = Field(default_factory=list)

    # Usage tracking
    used_in_roi_models: List[UUID] = Field(default_factory=list)
    used_in_dashboards: List[UUID] = Field(default_factory=list)
    last_accessed: Optional[datetime] = None
    access_count: int = 0

    # Housekeeping
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Database Schema

#### extraction_lineage Table
```sql
-- Full schema in Phase 3.2 above
-- Key indexes for performance:
-- - source_document_hash (find all extractions from document)
-- - extraction_timestamp (time-based queries)
-- - verification_status (find failed extractions)
-- - used_in_roi_models (GIN index for array search)
```

---

## Validation Pipeline Updates

### Layer 5: Source Verification Pseudocode

```python
def validate_layer_5_source_verification(
    result: DocumentAnalysisResult,
    full_document_text: str,
    document_pages: List[str],
    document_metadata: Dict
) -> Tuple[bool, List[str]]:
    """
    Layer 5: Verify extractions against source document.

    Returns:
        (is_valid, error_messages)
    """

    all_valid = True
    error_messages = []

    for extraction in result.extracted_value_propositions:
        # Run verification checks
        verification_result = verify_extraction_against_source(
            extraction=extraction,
            full_document_text=full_document_text,
            document_pages=document_pages,
            document_metadata=document_metadata
        )

        if verification_result["is_hallucinated"]:
            all_valid = False
            error_messages.append(
                f"Extraction '{extraction.name}' failed verification:\n"
                + "\n".join(f"  - {issue}" for issue in verification_result["issues"])
            )
        else:
            # Update extraction with verification results
            extraction.verification_status = verification_result["verification_status"]
            extraction.verification_method = verification_result["verification_method"]
            extraction.verification_issues = verification_result["issues"]
            extraction.extraction_confidence *= verification_result["confidence_adjustment"]

    return (all_valid, error_messages)
```

### Integration into Retry Loop

```python
def run_with_retry(message: str, **run_kwargs):
    """
    Enhanced retry loop with 5-layer validation.
    """
    attempt = 0
    last_error = None

    # Get document context for verification
    document_text = run_kwargs.get("full_document_text")
    document_pages = run_kwargs.get("document_pages")
    document_metadata = run_kwargs.get("document_metadata")

    while attempt < max_retries:
        try:
            # Execute agent
            response = agent.run(message, **run_kwargs)

            # Layer 1: JSON Extraction
            json_str = extract_json_from_response(response)

            # Layer 2: JSON Parsing
            result_dict = json.loads(json_str)

            # Layer 3: Pydantic Validation
            result = DocumentAnalysisResult(**result_dict)

            # Layer 4: Business Logic Validation
            business_validation = validate_business_rules(result)
            if not business_validation.is_valid:
                raise ValidationError(business_validation.errors)

            # Layer 5: Source Verification (NEW)
            source_verification_valid, verification_errors = validate_layer_5_source_verification(
                result=result,
                full_document_text=document_text,
                document_pages=document_pages,
                document_metadata=document_metadata
            )

            if not source_verification_valid:
                # Build detailed retry feedback
                feedback = build_verification_feedback(
                    attempt=attempt,
                    errors=verification_errors
                )
                message = message + "\n\n" + feedback
                attempt += 1
                continue

            # All validation passed
            logger.info(f"✅ Extraction successful with verification on attempt {attempt + 1}")

            # Create lineage records
            lineage_records = create_lineage_records(
                result=result,
                document_metadata=document_metadata,
                extraction_context={
                    "attempts": attempt + 1,
                    "validation_layers": ["json", "pydantic", "business", "source_verification"],
                    "duration": time.time() - start_time,
                    # ... more context
                }
            )

            # Store lineage in database
            store_lineage_records(lineage_records)

            return result

        except ValidationError as e:
            last_error = str(e)
            attempt += 1
            # ... error handling

    # Max retries exceeded
    raise RuntimeError(f"Extraction failed after {max_retries} attempts")
```

---

## Testing Strategy

### Unit Tests

#### Test: Hallucination Detector
**File:** `tests/unit/test_hallucination_detector.py`

**Test Cases:**
1. `test_source_text_found_in_document()` - Positive case
2. `test_source_text_not_in_document()` - Detect hallucination
3. `test_page_number_mismatch()` - Wrong pages
4. `test_numeric_value_not_in_source()` - Invented numbers
5. `test_confidence_threshold()` - Low confidence
6. `test_confidence_adjustment_calculation()` - Scoring logic

#### Test: Lineage Tracker
**File:** `tests/unit/test_lineage_tracker.py`

**Test Cases:**
1. `test_create_lineage_record()` - Record creation
2. `test_document_hash_computation()` - SHA256 hashing
3. `test_lineage_database_insert()` - PostgreSQL insert
4. `test_lineage_update_usage()` - ROI Model linking
5. `test_lineage_query_by_document()` - Retrieval queries

### Integration Tests

#### Test: End-to-End Verification
**File:** `tests/integration/test_document_analysis_with_verification.py`

**Test Scenario:**
1. Create test document with known content
2. Run DocumentAnalysisAgent
3. Verify Layer 5 catches invented claims
4. Verify lineage records created
5. Verify retry with feedback works

**Test Documents:**
- `test_roi_sheet_valid.pdf` - Clean, accurate data
- `test_roi_sheet_hallucination.pdf` - Agent will hallucinate (for testing detection)

#### Test: Lineage Tracking
**File:** `tests/integration/test_lineage_tracking.py`

**Test Scenario:**
1. Extract data from document
2. Verify lineage record in database
3. Build ROI Model using extraction
4. Verify `used_in_roi_models` updated
5. Generate dashboard
6. Verify `used_in_dashboards` updated
7. Query complete audit trail

### Performance Tests

#### Test: Verification Overhead
**Measure:**
- Execution time before Layer 5: X seconds
- Execution time with Layer 5: Y seconds
- Overhead: (Y - X) / X percentage

**Target:** <10% overhead

#### Test: Lineage Storage Performance
**Measure:**
- Time to insert 100 lineage records
- Time to query lineage by document_hash
- Time to update used_in_roi_models array

**Target:** All operations <100ms

---

## Success Metrics

### Hallucination Prevention Metrics

#### Primary Metrics
- **Hallucination Detection Rate:** % of hallucinated claims caught by Layer 5
  - **Target:** >95%

- **False Positive Rate:** % of valid claims incorrectly flagged as hallucinated
  - **Target:** <5%

- **Retry Success Rate:** % of extractions that pass after retry with feedback
  - **Target:** >80%

#### Secondary Metrics
- **Average Retry Attempts:** Number of retries before success
  - **Target:** <1.5 (most pass first time)

- **Verification Performance Overhead:** Time added by Layer 5
  - **Target:** <10% of total execution time

### Data Lineage Metrics

#### Tracking Coverage
- **Lineage Record Coverage:** % of extractions with lineage records
  - **Target:** 100%

- **Usage Tracking Coverage:** % of ROI Models with source_extractions populated
  - **Target:** 100%

#### Audit Trail Completeness
- **Full Chain Retrieval:** % of extractions where complete chain (Document → Extraction → ROI Model → Dashboard) can be retrieved
  - **Target:** 100%

### System Quality Metrics

#### Data Quality
- **Extraction Confidence Average:** Mean confidence score after verification
  - **Target:** >0.8

- **High Confidence Rate:** % of extractions with confidence ≥0.8
  - **Target:** >70%

#### Operational Metrics
- **Database Query Performance:** p95 latency for lineage queries
  - **Target:** <50ms

- **Storage Growth:** GB of lineage data per 1000 extractions
  - **Target:** <100MB

---

## Timeline & Resources

### Phase-by-Phase Breakdown

#### Phase 1: Data Model Updates
- **Duration:** 2 hours
- **Resources:** 1 backend developer
- **Deliverables:**
  - Updated Pydantic models
  - Database migration script
  - Model unit tests

#### Phase 2: Source Verification Implementation
- **Duration:** 4 hours
- **Resources:** 1 backend developer
- **Deliverables:**
  - `hallucination_detector.py` module
  - Layer 5 validation integration
  - Retry feedback system
  - Unit tests for verification

#### Phase 3: Lineage Tracking Implementation
- **Duration:** 4 hours
- **Resources:** 1 backend developer
- **Deliverables:**
  - `lineage_tracker.py` module
  - Database schema + migrations
  - Lineage storage workflow
  - Unit tests for lineage

#### Phase 4: Usage Tracking Integration
- **Duration:** 2 hours
- **Resources:** 1 backend developer
- **Deliverables:**
  - ROI Model Builder integration
  - Dashboard tracking
  - Lineage query API endpoints

#### Phase 5: Testing & Validation
- **Duration:** 3 hours
- **Resources:** 1 backend developer + 1 QA
- **Deliverables:**
  - Integration test suite
  - Performance benchmarks
  - Documentation updates

### Total Timeline

**Total Implementation Time:** 15 hours (2 working days)

**Team Size:** 1 backend developer (primary), 1 QA (for testing phase)

### Milestone Schedule

| Milestone | Duration | Completion Date |
|-----------|----------|----------------|
| Phase 1: Data Models | 2 hours | Day 1 Morning |
| Phase 2: Verification | 4 hours | Day 1 Afternoon |
| Phase 3: Lineage | 4 hours | Day 2 Morning |
| Phase 4: Integration | 2 hours | Day 2 Early Afternoon |
| Phase 5: Testing | 3 hours | Day 2 Late Afternoon |
| **TOTAL** | **15 hours** | **End of Day 2** |

---

## Data Lineage Storage Requirements

### Quick Answers

**Q: Do I need to store all the lineage track?**

**A: No - You can implement in phases:**

| Phase | Fields | Purpose | Storage Impact |
|-------|--------|---------|----------------|
| **MVP** | 10-12 fields | Audit trail + verification | ~200 bytes/record |
| **Phase 2** | 15-18 fields | + Quality metrics | ~300 bytes/record |
| **Full** | 25+ fields | + Usage tracking + optimization | ~500 bytes/record |

**Q: Where does it get stored in the db?**

**A: PostgreSQL `extraction_lineage` table**

- **Database:** PostgreSQL (NOT Clickhouse)
- **Table:** `extraction_lineage`
- **Why PostgreSQL:** ACID compliance, audit trail requirements, regulatory compliance
- **Indexes:** 5 indexes for common queries
- **Location:** Same database as `dashboard_templates`, `prospects`, `roi_models`

### Storage vs Implementation Trade-offs

| Approach | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **Store Everything (25 fields)** | Complete data, future-proof | Higher complexity, unused fields | ❌ Don't start here |
| **Store Minimum (10 fields)** | Simple, fast to implement | Limited debugging, no optimization data | ✅ MVP approach |
| **Phased Implementation** | Incremental complexity, learn as you go | Multiple migrations | ✅ **Recommended** |

---

## Storage Decision Framework

### What Must Be Stored (Mandatory)

These fields are **required for audit compliance and system functionality:**

```
MANDATORY FIELDS (10 fields):

1. Core Identity
   - extraction_id (UUID, primary key)
   - extraction_timestamp

2. Source Tracking
   - source_document_url
   - source_document_hash (SHA256)

3. Extraction Context
   - extraction_agent (which agent: DocumentAnalysisAgent, WebSearchAgent)
   - extraction_model (e.g., claude-sonnet-4)

4. Verification Results
   - verification_status (verified/unverified/flagged)
   - verification_issues (array of issues found)

5. Usage Tracking
   - used_in_roi_models (UUID array)
   - used_in_dashboards (UUID array)
```

**Storage Impact:** ~200 bytes per extraction record

**Why Mandatory:**
- **Audit Trail**: Healthcare/finance regulations require provable data sources
- **Error Investigation**: When ROI calculations are questioned, trace back to source
- **Impact Assessment**: If document is found incorrect, identify affected ROI models
- **Regulatory Compliance**: HIPAA/SOC2 require data lineage documentation

---

### What's Optional (Can Be Deferred)

These fields are **useful but not critical for MVP:**

```
OPTIONAL - PHASE 2 (5-8 fields):

1. Quality Metrics
   - text_quality_score (0-100, from hybrid PDF processing)
   - extraction_confidence_initial
   - extraction_confidence_final
   - extraction_duration_seconds

2. Optimization Data
   - prompt_template_version (for A/B testing)
   - extraction_method (vision_api/text_extraction)
   - extraction_model_provider (aws_bedrock/anthropic)

3. Access Tracking
   - last_accessed
   - access_count
```

**Storage Impact:** +100 bytes per record

**When to Add:**
- **Phase 2**: When optimizing extraction accuracy
- **A/B Testing**: When testing different prompts/models
- **Cost Optimization**: When analyzing extraction costs

---

### What's Advanced (Enterprise Features)

These fields are **nice-to-have for advanced use cases:**

```
ADVANCED - PHASE 3 (5-10 fields):

1. Detailed Validation
   - validation_layers_passed (array: ['json', 'pydantic', 'business', 'source'])
   - retry_attempts (how many tries before success)

2. Performance Optimization
   - source_document_size (bytes)
   - cache_hit (boolean)
   - processing_pipeline (string)

3. Collaboration Features
   - manual_review_status
   - reviewer_user_id
   - review_timestamp
   - review_notes
```

**Storage Impact:** +100-200 bytes per record

**When to Add:**
- **Manual Review Workflows**: When humans verify AI extractions
- **Performance Analysis**: When optimizing extraction speed
- **Advanced Debugging**: When investigating rare edge cases

---

## Database Architecture Details

### PostgreSQL Schema (MVP Version)

**Table Name:** `extraction_lineage`

**MVP Schema (10 mandatory fields):**

```sql
CREATE TABLE extraction_lineage (
    -- Core Identity (2 fields)
    extraction_id UUID PRIMARY KEY,
    extraction_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Source Tracking (2 fields)
    source_document_url TEXT NOT NULL,
    source_document_hash VARCHAR(64) NOT NULL,  -- SHA256

    -- Extraction Context (2 fields)
    extraction_agent VARCHAR(100) NOT NULL,
    extraction_model VARCHAR(100) NOT NULL,

    -- Verification Results (2 fields)
    verification_status VARCHAR(20) NOT NULL
        CHECK (verification_status IN ('verified', 'unverified', 'flagged')),
    verification_issues TEXT[],

    -- Usage Tracking (2 fields)
    used_in_roi_models UUID[],
    used_in_dashboards UUID[],

    -- Housekeeping
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for Common Queries
CREATE INDEX idx_lineage_document_hash ON extraction_lineage(source_document_hash);
CREATE INDEX idx_lineage_timestamp ON extraction_lineage(extraction_timestamp);
CREATE INDEX idx_lineage_verification ON extraction_lineage(verification_status);
CREATE INDEX idx_lineage_roi_models ON extraction_lineage USING GIN(used_in_roi_models);
CREATE INDEX idx_lineage_dashboards ON extraction_lineage USING GIN(used_in_dashboards);
```

**Storage Estimates:**

| Scale | Records | Storage (MVP) | Storage (Full) |
|-------|---------|---------------|----------------|
| **1 Client** | 100 extractions | 20 KB | 50 KB |
| **10 Clients** | 1,000 extractions | 200 KB | 500 KB |
| **100 Clients** | 10,000 extractions | 2 MB | 5 MB |
| **1,000 Clients** | 100,000 extractions | 20 MB | 50 MB |

**Conclusion:** Storage is negligible even at enterprise scale. Focus on mandatory fields first.

---

### Why PostgreSQL (Not Clickhouse)?

| Requirement | PostgreSQL | Clickhouse | Winner |
|-------------|------------|------------|--------|
| **ACID Compliance** | ✅ Full | ❌ Limited | PostgreSQL |
| **Audit Trail** | ✅ Perfect | ⚠️ Eventually consistent | PostgreSQL |
| **Regulatory Compliance** | ✅ SOC2/HIPAA ready | ⚠️ Requires tuning | PostgreSQL |
| **Small Record Updates** | ✅ Optimized | ❌ Not designed for | PostgreSQL |
| **Array Queries** | ✅ GIN indexes | ⚠️ Possible but slow | PostgreSQL |
| **Write Performance** | ✅ 1000s/sec | ✅ Millions/sec | Tie (both sufficient) |
| **Read Performance** | ✅ Indexed lookups | ✅ Columnar scans | Tie (both sufficient) |

**Decision:** Use PostgreSQL because lineage tracking is an **audit trail**, not analytics.

**Clickhouse Use Case:** Store raw analytics data (claims, utilization) - different from lineage.

---

## Lineage Data Lifecycle

### Workflow 1: Extraction with Lineage Creation

```
Document Analysis Job Initiated
│
├─ Step 1: Document Retrieved
│  │
│  ├─ Load document from S3
│  ├─ Calculate SHA256 hash
│  └─ Record document_url, document_hash
│
├─ Step 2: Agent Extraction
│  │
│  ├─ DocumentAnalysisAgent processes document
│  ├─ Agent attempts extraction (max 3 retries)
│  ├─ Record: extraction_agent, extraction_model, retry_attempts
│  └─ Record: extraction_timestamp, extraction_duration
│
├─ Step 3: 5-Layer Validation
│  │
│  ├─ Layer 1: JSON Extraction ✅
│  ├─ Layer 2: JSON Parsing ✅
│  ├─ Layer 3: Pydantic Validation ✅
│  ├─ Layer 4: Business Rules ✅
│  ├─ Layer 5: Source Verification ✅ or ❌
│  │
│  └─ Record: verification_status, verification_issues
│
├─ Step 4: Lineage Record Created
│  │
│  └─ INSERT INTO extraction_lineage (...)
│     - extraction_id = UUID (new)
│     - All mandatory fields populated
│     - used_in_roi_models = [] (empty initially)
│     - used_in_dashboards = [] (empty initially)
│
└─ Step 5: Return Extraction Result
   │
   └─ DocumentAnalysisResult includes extraction_id
```

**Database Transaction:**
```python
async def save_extraction_with_lineage(
    extraction_result: DocumentAnalysisResult,
    document_url: str,
    document_hash: str
) -> UUID:
    """Save extraction and create lineage record atomically."""

    async with db.transaction():
        # 1. Save extraction result
        extraction_id = await db.insert("extractions", extraction_result)

        # 2. Create lineage record
        lineage = ExtractionLineage(
            extraction_id=extraction_id,
            source_document_url=document_url,
            source_document_hash=document_hash,
            extraction_agent="DocumentAnalysisAgent",
            extraction_model="claude-sonnet-4",
            verification_status=extraction_result.verification_status,
            verification_issues=extraction_result.verification_issues,
            used_in_roi_models=[],  # Populated later
            used_in_dashboards=[]   # Populated later
        )

        await db.insert("extraction_lineage", lineage)

        return extraction_id
```

---

### Workflow 2: Usage Tracking Update

```
ROI Model Generated
│
├─ Step 1: ROI Model Uses Extractions
│  │
│  ├─ Model Builder Agent creates ROI Model
│  ├─ References extraction IDs: [extract_1, extract_2, extract_3]
│  └─ ROI Model saved with roi_model_id
│
├─ Step 2: Update Lineage Records
│  │
│  └─ For each extraction_id used:
│     │
│     └─ UPDATE extraction_lineage
│        SET used_in_roi_models = array_append(used_in_roi_models, roi_model_id)
│        WHERE extraction_id IN (extract_1, extract_2, extract_3)
│
└─ Step 3: Dashboard Generated
   │
   ├─ Dashboard uses ROI Model (roi_model_id)
   ├─ Dashboard saved with dashboard_id
   │
   └─ UPDATE extraction_lineage
      SET used_in_dashboards = array_append(used_in_dashboards, dashboard_id)
      WHERE roi_model_id = ANY(used_in_roi_models)
```

**Database Updates:**
```python
async def link_extraction_to_roi_model(
    extraction_ids: List[UUID],
    roi_model_id: UUID
):
    """Update lineage when extraction is used in ROI model."""

    await db.execute("""
        UPDATE extraction_lineage
        SET used_in_roi_models = array_append(used_in_roi_models, $1),
            updated_at = NOW()
        WHERE extraction_id = ANY($2)
    """, roi_model_id, extraction_ids)


async def link_roi_model_to_dashboard(
    roi_model_id: UUID,
    dashboard_id: UUID
):
    """Update lineage when ROI model is used in dashboard."""

    await db.execute("""
        UPDATE extraction_lineage
        SET used_in_dashboards = array_append(used_in_dashboards, $1),
            updated_at = NOW()
        WHERE $2 = ANY(used_in_roi_models)
    """, dashboard_id, roi_model_id)
```

---

### Workflow 3: Impact Analysis Query

```
Document Found Incorrect
│
├─ Step 1: Identify Source Document
│  │
│  └─ Known: source_document_url or source_document_hash
│
├─ Step 2: Find All Affected Extractions
│  │
│  └─ SELECT extraction_id, used_in_roi_models, used_in_dashboards
│     FROM extraction_lineage
│     WHERE source_document_hash = '<hash>'
│     Result: [
│       {extraction_1: [roi_1, roi_2], [dashboard_1, dashboard_2]},
│       {extraction_2: [roi_3], [dashboard_3]}
│     ]
│
├─ Step 3: Notify Affected Systems
│  │
│  ├─ Mark ROI Models for review: roi_1, roi_2, roi_3
│  ├─ Mark Dashboards for review: dashboard_1, dashboard_2, dashboard_3
│  └─ Send alerts to dashboard owners
│
└─ Step 4: Update Lineage Records
   │
   └─ UPDATE extraction_lineage
      SET verification_status = 'flagged',
          verification_issues = array_append(
              verification_issues,
              'Source document found incorrect on 2025-12-17'
          )
      WHERE source_document_hash = '<hash>'
```

**SQL Query:**
```sql
-- Find all dashboards affected by incorrect document
SELECT DISTINCT
    el.extraction_id,
    el.source_document_url,
    unnest(el.used_in_roi_models) AS roi_model_id,
    unnest(el.used_in_dashboards) AS dashboard_id,
    dt.template_name AS dashboard_name,
    p.company_name AS client_name
FROM extraction_lineage el
LEFT JOIN roi_models rm ON rm.id = ANY(el.used_in_roi_models)
LEFT JOIN dashboard_templates dt ON dt.id = ANY(el.used_in_dashboards)
LEFT JOIN prospects p ON p.id = dt.prospect_id
WHERE el.source_document_hash = '<incorrect_doc_hash>'
ORDER BY client_name, dashboard_name;
```

---

## Storage Optimization Strategies

### Strategy 1: Retention Policies

**Problem:** Lineage records accumulate over time

**Solution:** Implement time-based retention

```
Retention Policy:

Active Records (< 90 days)
├─ Storage: PostgreSQL hot storage
├─ Indexes: All 5 indexes active
└─ Access: Fast queries

Recent Records (90 days - 1 year)
├─ Storage: PostgreSQL standard storage
├─ Indexes: Partial indexes only
└─ Access: Acceptable performance

Archived Records (> 1 year)
├─ Storage: AWS S3 (JSON files)
├─ Indexes: None (full scan if needed)
├─ Access: Slow but rare
└─ Cost: $0.023/GB/month vs $0.10/GB/month

Purged Records (> 3 years)
└─ Deleted entirely (unless regulatory hold)
```

**Implementation:**
```python
async def archive_old_lineage_records():
    """Archive lineage records older than 1 year."""

    # 1. Export to S3
    old_records = await db.query("""
        SELECT * FROM extraction_lineage
        WHERE extraction_timestamp < NOW() - INTERVAL '1 year'
    """)

    s3_client.put_object(
        Bucket='triton-archives',
        Key=f'lineage/archive_{date.today()}.json',
        Body=json.dumps(old_records)
    )

    # 2. Delete from PostgreSQL
    await db.execute("""
        DELETE FROM extraction_lineage
        WHERE extraction_timestamp < NOW() - INTERVAL '1 year'
    """)
```

---

### Strategy 2: Partitioning by Time

**Problem:** Large table scans slow down queries

**Solution:** PostgreSQL table partitioning

```sql
-- Convert to partitioned table
CREATE TABLE extraction_lineage_partitioned (
    LIKE extraction_lineage INCLUDING ALL
) PARTITION BY RANGE (extraction_timestamp);

-- Create monthly partitions
CREATE TABLE extraction_lineage_2025_12
    PARTITION OF extraction_lineage_partitioned
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE TABLE extraction_lineage_2026_01
    PARTITION OF extraction_lineage_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Future partitions created automatically by cron job
```

**Benefits:**
- Queries on recent data only scan recent partitions
- Old partitions can be dropped quickly (no full table scan)
- Backup/restore can target specific time ranges

**When to Implement:** When `extraction_lineage` exceeds 1 million records

---

### Strategy 3: Compression

**Problem:** Array fields (`used_in_roi_models`, `verification_issues`) can grow large

**Solution:** PostgreSQL TOAST compression

```sql
-- TOAST (The Oversized-Attribute Storage Technique) is automatic in PostgreSQL
-- But you can tune it for array fields

ALTER TABLE extraction_lineage
    ALTER COLUMN used_in_roi_models
    SET STORAGE EXTENDED;  -- Enable compression

ALTER TABLE extraction_lineage
    ALTER COLUMN verification_issues
    SET STORAGE EXTENDED;
```

**Effect:** Arrays > 2KB are automatically compressed (up to 75% size reduction)

---

### Strategy 4: Summary Tables

**Problem:** Repeated aggregation queries (e.g., "count extractions by status")

**Solution:** Materialized views for dashboards

```sql
-- Create summary view
CREATE MATERIALIZED VIEW lineage_summary AS
SELECT
    extraction_agent,
    verification_status,
    DATE_TRUNC('day', extraction_timestamp) AS date,
    COUNT(*) AS extraction_count,
    AVG(extraction_duration_seconds) AS avg_duration,
    SUM(ARRAY_LENGTH(used_in_roi_models, 1)) AS total_roi_model_usage
FROM extraction_lineage
GROUP BY extraction_agent, verification_status, DATE_TRUNC('day', extraction_timestamp);

-- Refresh daily
CREATE INDEX idx_lineage_summary_date ON lineage_summary(date);

-- Automatic refresh via cron
REFRESH MATERIALIZED VIEW lineage_summary;
```

**Benefits:**
- Dashboard queries run on summary view (1000x faster)
- Detailed queries still hit main table
- Refresh daily during low-traffic hours

---

## Cost Analysis

### Storage Costs (AWS RDS PostgreSQL)

| Scale | Records/Month | Storage/Month | Cost/Month | Yearly Cost |
|-------|---------------|---------------|------------|-------------|
| **Small** | 1,000 | 200 KB | $0.02 | $0.24 |
| **Medium** | 10,000 | 2 MB | $0.20 | $2.40 |
| **Large** | 100,000 | 20 MB | $2.00 | $24.00 |
| **Enterprise** | 1,000,000 | 200 MB | $20.00 | $240.00 |

**Calculation:** AWS RDS storage = $0.10/GB/month (assuming gp3)

**Conclusion:** Storage cost is negligible. Even at enterprise scale (1M records/month), storage costs only $240/year.

---

### Query Performance Costs

**More significant than storage:**

| Query Type | Frequency | Cost Impact |
|------------|-----------|-------------|
| **Impact Analysis** | Rare (when docs found incorrect) | Low - OK to scan |
| **Usage Tracking** | Every ROI model generation | Medium - needs indexes |
| **Dashboard Metrics** | Every dashboard load | High - use summary views |

**Optimization Priority:**
1. ✅ Index `used_in_roi_models` (GIN index) - Most queried
2. ✅ Index `verification_status` - Dashboard filters
3. ⚠️ Materialized view for dashboard metrics - If queries slow
4. ❌ Don't over-index - Each index adds write overhead

---

### Implementation Phasing Recommendations

#### Phase 1: MVP (1-2 hours)

**Goal:** Audit trail + basic verification

**Fields to Implement:**
```python
class ExtractionLineageMVP(BaseModel):
    # Core Identity
    extraction_id: UUID
    extraction_timestamp: datetime

    # Source Tracking
    source_document_url: str
    source_document_hash: str  # SHA256

    # Extraction Context
    extraction_agent: str
    extraction_model: str

    # Verification Results
    verification_status: Literal['verified', 'unverified', 'flagged']
    verification_issues: List[str] = []

    # Usage Tracking
    used_in_roi_models: List[UUID] = []
    used_in_dashboards: List[UUID] = []
```

**Deliverable:** Can trace any extraction back to source document and forward to dashboards.

---

#### Phase 2: Quality Metrics (2-3 hours)

**Goal:** Optimize extraction accuracy

**Additional Fields:**
```python
class ExtractionLineagePhase2(ExtractionLineageMVP):
    # Quality Metrics
    text_quality_score: Optional[float] = None
    extraction_confidence_initial: Optional[float] = None
    extraction_confidence_final: Optional[float] = None
    extraction_duration_seconds: Optional[float] = None

    # Optimization Data
    prompt_template_version: Optional[str] = None
    extraction_method: Optional[str] = None
```

**Deliverable:** Can analyze which extraction strategies work best.

---

#### Phase 3: Advanced Tracking (3-4 hours)

**Goal:** Enterprise compliance + manual review workflows

**Additional Fields:**
```python
class ExtractionLineageFull(ExtractionLineagePhase2):
    # Detailed Validation
    validation_layers_passed: List[str] = []
    retry_attempts: int = 1

    # Manual Review
    manual_review_status: Optional[str] = None
    reviewer_user_id: Optional[UUID] = None
    review_timestamp: Optional[datetime] = None
    review_notes: Optional[str] = None

    # Access Tracking
    last_accessed: Optional[datetime] = None
    access_count: int = 0
```

**Deliverable:** Enterprise-grade audit trail with human oversight.

---

## Common Questions (FAQ)

### Q: Do I need lineage for every extraction?

**A: Yes, for audit compliance.**

Even extractions that are never used in ROI models should be tracked because:
1. Regulators may ask "what data did you extract from this document?"
2. You need to prove you have source verification in place
3. If document is found incorrect, you need to verify no extractions were used

**Exception:** Mock/test extractions during development can skip lineage.

---

### Q: Can I store lineage in Clickhouse instead?

**A: No, use PostgreSQL for lineage.**

| Reason | Why PostgreSQL |
|--------|----------------|
| **ACID Compliance** | Lineage is audit trail, needs strict consistency |
| **Array Updates** | Frequently append to `used_in_roi_models` array |
| **Small Records** | Clickhouse optimized for columnar scans, not row lookups |
| **Regulatory** | SOC2/HIPAA auditors expect ACID-compliant audit logs |

**Clickhouse Use Case:** Analytics queries (claims, utilization) - different from lineage.

---

### Q: What if I have millions of extractions?

**A: Implement partitioning + retention policies.**

At enterprise scale (1M+ records):
1. **Partition by month**: Queries only scan recent partitions
2. **Archive old records**: Move > 1 year old to S3
3. **Materialized views**: For dashboard metrics
4. **Separate read replica**: For analytics queries

**When to implement:** When `extraction_lineage` exceeds 1 million records OR queries take > 5 seconds.

---

### Q: Can I delete lineage records?

**A: Only after retention period expires.**

**Retention Policy:**
- **Active usage** (< 90 days): Keep in PostgreSQL
- **Recent** (90 days - 1 year): Keep in PostgreSQL (partial indexes)
- **Archived** (1-3 years): Move to S3
- **Expired** (> 3 years): Delete (unless regulatory hold)

**Exception:** If extraction is used in active ROI model, keep indefinitely (or until ROI model is archived).

**SQL:**
```sql
-- Safe to delete: Old AND not used in active ROI models
DELETE FROM extraction_lineage
WHERE extraction_timestamp < NOW() - INTERVAL '3 years'
  AND ARRAY_LENGTH(used_in_roi_models, 1) IS NULL;
```

---

### Q: How do I migrate from no lineage to lineage tracking?

**A: Phased migration approach.**

**Step 1: Deploy MVP Schema**
- Create `extraction_lineage` table (10 fields)
- Add indexes
- No data yet

**Step 2: Enable Lineage for New Extractions**
- Update DocumentAnalysisAgent to create lineage records
- Old extractions have no lineage (acceptable)

**Step 3: Optional Backfill**
- If needed, create lineage records for recent extractions
- Set `verification_status = 'unverified'` for backfilled records
- Only backfill last 90 days (older records less critical)

**Step 4: Add Phase 2/3 Fields Later**
- Schema migrations are easy with optional fields
- No impact on existing lineage records

---

### Q: What's the performance impact of lineage tracking?

**A: Minimal (<5% overhead).**

**Breakdown:**
- **Compute SHA256 hash:** ~10ms (one-time per document)
- **Create lineage record:** ~5ms (Pydantic model)
- **PostgreSQL INSERT:** ~2ms (indexed table)
- **Total overhead:** ~17ms per extraction

**Comparison:**
- DocumentAnalysisAgent execution time: ~10-20 seconds
- Lineage overhead: ~17ms
- **Percentage impact:** <0.2%

---

### Q: Should I track lineage for web search results?

**A: Yes, with modifications.**

Web search results should also have lineage, but schema differs slightly:

```python
class WebSearchLineage(BaseModel):
    extraction_id: UUID
    source_url: str  # Not S3, actual web URL
    source_content_hash: str  # Hash of scraped content
    search_query: str  # What was searched
    search_provider: str  # "duckduckgo" | "tavily"
    search_timestamp: datetime  # When scraped
    # ... rest similar to document lineage
```

**Why Track:**
- Web content changes over time (cache at time of extraction)
- Need to prove what data was visible when searched
- Enables re-validation if source changes

---

## Risk Assessment

### High-Risk Areas

#### Risk 1: Performance Degradation
- **Description:** Layer 5 verification adds overhead to every extraction
- **Mitigation:** Implement caching, optimize text search algorithms
- **Contingency:** Make Layer 5 optional via feature flag

#### Risk 2: Database Storage Growth
- **Description:** Lineage table grows rapidly with high extraction volume
- **Mitigation:** Implement retention policies, archive old records
- **Contingency:** Partition table by timestamp

#### Risk 3: False Positives in Verification
- **Description:** Valid extractions flagged as hallucinated due to text variations
- **Mitigation:** Implement fuzzy matching, allow slight variations
- **Contingency:** Manual review workflow for disputed extractions

### Medium-Risk Areas

#### Risk 4: Backward Compatibility
- **Description:** Existing extractions don't have new fields
- **Mitigation:** Make new fields optional, provide migration script
- **Contingency:** Run backfill job to update old records

#### Risk 5: Retry Loop Timeouts
- **Description:** Multiple retries cause long execution times
- **Mitigation:** Set max retry limit (3), implement timeout
- **Contingency:** Return partial results with warnings

---

## Next Steps

### Immediate Actions (This Week)

1. **Review & Approval**
   - Stakeholder review of this plan
   - Approval to proceed with implementation
   - Resource allocation confirmation
   - **Decision: MVP vs Full implementation** (see Section 13-19)

2. **Storage Planning**
   - Review storage requirements (Section 13: Data Lineage Storage Requirements)
   - Decide on field implementation (Section 14: Storage Decision Framework)
   - Review database architecture (Section 15: Database Architecture Details)
   - Plan retention policies (Section 17: Storage Optimization Strategies)

3. **Environment Setup**
   - Create feature branch: `feature/extraction-verification-lineage`
   - Set up test database (PostgreSQL, not Clickhouse - see Section 15)
   - Prepare test documents

4. **Phase 1 Implementation (MVP - 10 fields)**
   - Update Pydantic models (mandatory fields only)
   - Create database migration (see Section 15 for MVP schema)
   - Write model unit tests

### Following Week

5. **Phase 2-3 Implementation**
   - Build hallucination detector
   - Implement lineage tracker
   - Integration into agent

6. **Phase 4-5 Completion**
   - ROI Model integration
   - Comprehensive testing
   - Documentation updates

### Long-Term (Post-Implementation)

7. **Monitoring & Optimization**
   - Deploy to staging environment
   - Monitor hallucination detection rates
   - Optimize performance bottlenecks
   - Review storage costs and optimization (Section 18: Cost Analysis)

8. **Production Deployment**
   - Gradual rollout (10% → 50% → 100%)
   - Monitor metrics
   - Gather user feedback
   - Implement retention policies if needed (Section 17)

9. **Future Enhancements** (Optional - Phase 2/3)
   - Add quality metrics (Section 14: Optional fields)
   - Implement A/B testing framework
   - Add manual review workflow (Section 14: Advanced fields)

---

## Appendix

### Glossary

- **Hallucination:** AI model generating data not present in source documents
- **Lineage:** Complete history of data from origin to current usage
- **Extraction:** Single piece of data extracted from a document (value prop, metric, outcome)
- **Verification:** Process of confirming extracted data matches source
- **Confidence Score:** Numerical measure (0.0-1.0) of extraction reliability

### References

- Current 4-Layer Validation: `docs/architecture-current/RESEARCH_AGENT_FLOW.md` (lines 878-1004)
- Document Analysis Instructions: `agents/templates/document_analysis_instructions.md`
- Existing Data Models: `core/models/research_models.py`
- ROI Model Architecture: `docs/architecture-current/ROI_MODEL_RESEARCH_FLOW_UPDATED.md`

### Related Documentation

- `docs/HYBRID_PDF_PROCESSING_GUIDE.md` - PDF extraction methods
- `docs/RESEARCH_AGENT_FLOW.md` - Complete agent system architecture
- `docs/ROI_INTEGRATION_GUIDE.md` - ROI Model integration

---

**Document Status:** ✅ Ready for Review
**Next Action:** Stakeholder approval to begin Phase 1
**Contact:** Engineering Team Lead

**End of Document**
