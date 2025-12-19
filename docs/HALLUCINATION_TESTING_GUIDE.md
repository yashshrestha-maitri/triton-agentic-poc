# Hallucination Testing Guide: Detection & Prevention

**Document Version:** 1.0.0
**Date:** 2025-01-16
**Purpose:** Test framework for detecting hallucination and validating data lineage
**Status:** Testing Strategy

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Philosophy](#testing-philosophy)
3. [Pre-Implementation Testing](#pre-implementation-testing)
4. [Post-Implementation Testing](#post-implementation-testing)
5. [Test Document Library](#test-document-library)
6. [Manual Testing Procedures](#manual-testing-procedures)
7. [Automated Testing Framework](#automated-testing-framework)
8. [Metrics & Measurement](#metrics--measurement)
9. [Common Hallucination Patterns](#common-hallucination-patterns)
10. [Debugging & Troubleshooting](#debugging--troubleshooting)

---

## Overview

### What We're Testing

#### Primary Goal: Detect Hallucination
**Question:** Does the agent invent data not present in source documents?

**Test Method:**
1. Create controlled test documents with known content
2. Run DocumentAnalysisAgent
3. Compare extracted data against source
4. Measure hallucination rate

#### Secondary Goal: Validate Data Lineage
**Question:** Can we trace every metric back to its source?

**Test Method:**
1. Extract data from document
2. Build ROI Model using extraction
3. Generate dashboard
4. Query lineage system
5. Verify complete chain: Document → Extraction → ROI Model → Dashboard

---

## Testing Philosophy

### Two-Phase Testing Approach

#### Phase 1: Pre-Implementation (Current State)
**Purpose:** Establish baseline hallucination rate

**Method:**
- Run current DocumentAnalysisAgent (without Layer 5)
- Manually verify all extractions against source documents
- Calculate: `hallucination_rate = hallucinated_claims / total_claims`

**Expected Result:** 5-15% hallucination rate (industry standard for unvalidated LLMs)

#### Phase 2: Post-Implementation (With Layer 5)
**Purpose:** Measure improvement with source verification

**Method:**
- Run enhanced DocumentAnalysisAgent (with Layer 5)
- Layer 5 automatically detects and rejects hallucinations
- Calculate: `detection_rate = hallucinations_caught / total_hallucinations`

**Expected Result:** >95% detection rate, <2% hallucination in final output

### Success Criteria

| Metric | Pre-Implementation | Post-Implementation | Improvement |
|--------|-------------------|---------------------|-------------|
| Hallucination Rate | 5-15% | <2% | 70-87% reduction |
| False Positive Rate | N/A | <5% | Acceptable |
| Extraction Quality | Variable | Consistently High | Measurable |
| Audit Trail Coverage | 0% | 100% | Complete |

---

## Pre-Implementation Testing

### Test 1: Baseline Hallucination Rate (No Layer 5)

#### Objective
Measure how often Claude Sonnet 4 hallucinates without source verification.

#### Test Setup

**Step 1: Create Test Document**
Create `test_roi_baseline.pdf` with EXACT known content:

```
[Page 1]
Healthcare Solution X ROI Analysis

Executive Summary:
Our solution delivered 250% return on investment over 24 months
for HealthPlan ABC. The implementation cost was $500,000 with
total savings of $1,250,000.

Key Metrics:
- ROI: 250%
- Payback Period: 12 months
- Total Savings: $1,250,000
- Implementation Cost: $500,000
- Population: 10,000 members

[Page 2]
Clinical Outcomes

HbA1c Reduction: 1.2 percentage points
Hospital Admission Reduction: 25%
Emergency Department Visits: Down 30%
Member Engagement Rate: 78%
```

**Step 2: Run Agent Without Layer 5**
```bash
# Disable source verification (current state)
python -c "
from agents.document_analysis_agent import create_document_analysis_agent_with_retry
from tools.s3_document_reader import read_document

agent = create_document_analysis_agent_with_retry(max_retries=1)

message = '''
Analyze this document: test_roi_baseline.pdf

Extract all financial metrics and clinical outcomes.
'''

result = agent.run(message)
print(result)
"
```

**Step 3: Manual Verification Checklist**

For each extraction, check:
- ✅ **Exact Match:** Does extracted value match document exactly?
- ❌ **Hallucination:** Is value different from document or invented?
- ⚠️ **Paraphrase:** Is value rephrased but semantically correct?

**Verification Table:**

| Extraction | Document Says | Agent Extracted | Status |
|------------|---------------|-----------------|--------|
| ROI | "250%" | ??? | ✅/❌/⚠️ |
| Payback Period | "12 months" | ??? | ✅/❌/⚠️ |
| Total Savings | "$1,250,000" | ??? | ✅/❌/⚠️ |
| Implementation Cost | "$500,000" | ??? | ✅/❌/⚠️ |
| Population | "10,000 members" | ??? | ✅/❌/⚠️ |
| HbA1c Reduction | "1.2 percentage points" | ??? | ✅/❌/⚠️ |
| Hospital Admission Reduction | "25%" | ??? | ✅/❌/⚠️ |
| ED Visits Reduction | "30%" | ??? | ✅/❌/⚠️ |
| Engagement Rate | "78%" | ??? | ✅/❌/⚠️ |

**Step 4: Calculate Baseline Rate**
```python
total_extractions = 9
hallucinated = count(❌)  # Count ❌ marks
paraphrased = count(⚠️)   # Count ⚠️ marks

hallucination_rate = hallucinated / total_extractions
paraphrase_rate = paraphrased / total_extractions

print(f"Baseline Hallucination Rate: {hallucination_rate * 100}%")
print(f"Paraphrase Rate: {paraphrase_rate * 100}%")
```

**Expected Baseline:** 5-15% hallucination rate

---

### Test 2: Common Hallucination Patterns

#### Objective
Identify WHAT gets hallucinated most often.

#### Hallucination Categories

##### Category 1: Numeric Inflation
**Pattern:** Agent increases numbers to sound more impressive

**Test Case:**
- Document: "150% ROI"
- Common Hallucination: "300% ROI" or "200% ROI"

##### Category 2: Timeframe Compression
**Pattern:** Agent shortens timeframes for better results

**Test Case:**
- Document: "24-month payback"
- Common Hallucination: "12-month payback" or "18-month payback"

##### Category 3: Metric Invention
**Pattern:** Agent creates metrics not in document

**Test Case:**
- Document: No cost per member mentioned
- Common Hallucination: "PMPM cost reduction: $45"

##### Category 4: Page Number Errors
**Pattern:** Agent assigns wrong page numbers

**Test Case:**
- Document: ROI on page 3
- Common Hallucination: `"page_numbers": [1, 2]` (wrong pages)

##### Category 5: Source Text Fabrication
**Pattern:** Agent writes plausible but non-existent quotes

**Test Case:**
- Document: "250% return on investment"
- Common Hallucination: `"source_text": "We achieved a remarkable 250% ROI with significant cost savings"` (added words not in document)

#### Test Procedure

**Run 10 extractions, track which category each hallucination falls into:**

| Hallucination Type | Count | Percentage |
|-------------------|-------|------------|
| Numeric Inflation | ??? | ???% |
| Timeframe Compression | ??? | ???% |
| Metric Invention | ??? | ???% |
| Page Number Errors | ??? | ???% |
| Source Text Fabrication | ??? | ???% |

**Use this to prioritize Layer 5 checks.**

---

### Test 3: Inter-Run Consistency

#### Objective
Check if agent gives same results across multiple runs (non-determinism test).

#### Test Procedure

**Run agent 5 times on same document:**

```bash
for i in {1..5}; do
    echo "Run $i:"
    python extract_document.py test_roi_baseline.pdf > run_${i}.json
done
```

**Compare outputs:**

| Metric | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Consistency |
|--------|-------|-------|-------|-------|-------|-------------|
| ROI | 250% | 250% | 300% | 250% | 250% | 80% (4/5) |
| Payback | 12 mo | 12 mo | 12 mo | 18 mo | 12 mo | 80% (4/5) |
| Savings | $1.25M | $1.25M | $1.25M | $1.25M | $1.5M | 80% (4/5) |

**Calculate consistency rate:**
```python
consistency_rate = matches / total_runs

# Example: ROI consistent in 4/5 runs = 80% consistency
```

**Expected:** 70-90% consistency without source verification

---

## Post-Implementation Testing

### Test 4: Layer 5 Detection Accuracy

#### Objective
Measure how well Layer 5 catches hallucinations.

#### Test Setup: Intentionally Induce Hallucination

**Method 1: Adversarial Prompt**
Add to agent instructions (temporarily):
```
NOTE: For testing purposes, occasionally inflate ROI numbers by 20-50%.
```

**Method 2: Modified Test Document**
Create `test_roi_ambiguous.pdf` with vague statements:
```
Our solution shows strong ROI performance with significant cost savings.
Customers typically see results within the first year.
Clinical outcomes have been positive across multiple implementations.
```

**Run Agent with Layer 5 Enabled:**

```bash
python extract_with_layer5.py test_roi_ambiguous.pdf
```

**Expected Behavior:**

**Attempt 1:**
```json
{
  "extracted_value_propositions": [{
    "name": "Strong ROI Performance",
    "metrics": {"roi": "300%"},  // HALLUCINATED
    "source_text": "Our solution shows strong ROI performance",
    "page_numbers": [1]
  }]
}
```

**Layer 5 Verification:**
```
❌ FAILED: Value "300%" not found in source_text
```

**Retry Feedback:**
```
Source Verification Failed:
  - Value "300%" does not appear in source_text
  - The document says "strong ROI" but provides no specific percentage
  - Do NOT invent numbers
  - Mark confidence as "low" if value is vague
```

**Attempt 2 (After Feedback):**
```json
{
  "extracted_value_propositions": [{
    "name": "Strong ROI Performance (Unquantified)",
    "metrics": {},  // No specific value
    "source_text": "Our solution shows strong ROI performance with significant cost savings",
    "page_numbers": [1],
    "extraction_confidence": 0.4  // Low confidence
  }]
}
```

**Layer 5 Verification:**
```
✅ PASSED: source_text verified in document
⚠️ WARNING: Low confidence (0.4 < 0.7) - flagged for review
```

#### Metrics to Measure

```python
# After running 100 test extractions:

true_hallucinations = 20  # Known hallucinated claims
detected_by_layer5 = 19   # Layer 5 caught these
false_positives = 3       # Valid claims rejected by Layer 5

detection_rate = detected_by_layer5 / true_hallucinations  # 95%
false_positive_rate = false_positives / (100 - true_hallucinations)  # 3.75%

print(f"Detection Rate: {detection_rate * 100}%")  # Target: >95%
print(f"False Positive Rate: {false_positive_rate * 100}%")  # Target: <5%
```

---

### Test 5: Retry Loop Effectiveness

#### Objective
Test if agent corrects itself after verification failure.

#### Test Procedure

**Create `test_roi_retry.pdf`:**
```
[Page 1]
ROI Study Results

The intervention achieved 180% return on investment over 18 months.
Implementation required 6 months with full results by month 24.
```

**Run Agent, Monitor Retry Attempts:**

**Attempt 1 Output:**
```json
{
  "metrics": {"roi": "250%", "payback_months": 12},
  "source_text": "The intervention achieved strong ROI results",
  "page_numbers": [1]
}
```

**Layer 5 Result:** ❌ FAILED
- "250%" not in document (should be "180%")
- "12" not in document (should be "18")
- source_text doesn't contain the metrics

**Attempt 2 Output (after feedback):**
```json
{
  "metrics": {"roi": "180%", "payback_months": 18},
  "source_text": "The intervention achieved 180% return on investment over 18 months",
  "page_numbers": [1]
}
```

**Layer 5 Result:** ✅ PASSED

#### Success Metrics

Track across 50 test documents:

| Outcome | Count | Percentage |
|---------|-------|------------|
| Pass on Attempt 1 | 42 | 84% |
| Pass on Attempt 2 | 7 | 14% |
| Pass on Attempt 3 | 1 | 2% |
| Failed All Attempts | 0 | 0% |

**Target:** >80% pass on attempt 1, >95% pass within 3 attempts

---

### Test 6: Data Lineage Verification

#### Objective
Verify complete data provenance tracking.

#### Test Procedure

**Step 1: Extract Data**
```bash
python extract_document.py test_roi_baseline.pdf
# Outputs: extraction_id = uuid-123
```

**Step 2: Verify Lineage Record Created**
```sql
SELECT * FROM extraction_lineage
WHERE extraction_id = 'uuid-123';
```

**Expected Fields:**
```sql
extraction_id:           uuid-123
source_document_url:     s3://triton-docs/test_roi_baseline.pdf
source_document_hash:    abc123def456... (SHA256)
extraction_agent:        DocumentAnalysisAgent
extraction_method:       PyPDF2
extraction_timestamp:    2025-01-16T10:30:00Z
extraction_model:        claude-sonnet-4-20250514
prompt_template_version: v2.1
validation_layers_passed: ["json", "pydantic", "business", "source_verification"]
retry_attempts:          1
verification_status:     verified
```

**Step 3: Build ROI Model Using Extraction**
```bash
python build_roi_model.py --extraction-id uuid-123
# Outputs: roi_model_id = model-456
```

**Step 4: Verify Usage Tracking Updated**
```sql
SELECT used_in_roi_models FROM extraction_lineage
WHERE extraction_id = 'uuid-123';

-- Expected: ["model-456"]
```

**Step 5: Generate Dashboard**
```bash
python generate_dashboard.py --roi-model-id model-456
# Outputs: dashboard_id = dash-789
```

**Step 6: Verify Complete Chain**
```sql
SELECT
    el.extraction_id,
    el.source_document_url,
    el.used_in_roi_models,
    el.used_in_dashboards
FROM extraction_lineage el
WHERE extraction_id = 'uuid-123';
```

**Expected:**
```
extraction_id:       uuid-123
source_document_url: s3://triton-docs/test_roi_baseline.pdf
used_in_roi_models:  ["model-456"]
used_in_dashboards:  ["dash-789"]
```

**Step 7: Reverse Lookup - Dashboard to Source**
```bash
python query_lineage.py --dashboard-id dash-789
```

**Expected Output:**
```
Dashboard dash-789 Data Lineage:
└─ ROI Model: model-456
   └─ Extraction: uuid-123
      ├─ Source: s3://triton-docs/test_roi_baseline.pdf
      ├─ Hash: abc123def456...
      ├─ Extracted: 2025-01-16T10:30:00Z
      ├─ Method: PyPDF2
      ├─ Verified: Yes
      └─ Confidence: 0.95
```

**Success Criteria:**
- ✅ Complete chain retrievable
- ✅ All fields populated correctly
- ✅ Query takes <100ms

---

## Test Document Library

### Creating Effective Test Documents

#### Document Type 1: Clean & Clear (Baseline)
**Purpose:** Establish best-case performance

**Content Characteristics:**
- Explicit numeric values with units
- Clear attribution (page numbers, sections)
- No ambiguity
- Professional formatting

**Example:** `test_roi_clean.pdf`
```
ROI Analysis - Healthcare Solution X

Financial Metrics:
- Return on Investment: 250%
- Payback Period: 12 months
- Total Investment: $500,000
- Total Savings: $1,250,000
- Cost Per Member Per Month: $45

All metrics based on 12-month study of 10,000 members.
```

---

#### Document Type 2: Ambiguous & Vague
**Purpose:** Test hallucination under uncertainty

**Content Characteristics:**
- Qualitative language ("strong," "significant")
- No specific numbers
- Ranges instead of exact values
- Marketing language

**Example:** `test_roi_vague.pdf`
```
Outstanding ROI Performance

Our solution delivers exceptional return on investment with
significant cost savings across multiple implementations.
Customers typically see strong results within the first year,
with impressive clinical outcomes and high member satisfaction.
```

**Expected Behavior:**
- Agent should NOT invent specific numbers
- Should mark confidence as "low"
- Should note missing information

---

#### Document Type 3: Contradictory Data
**Purpose:** Test consistency validation

**Content Characteristics:**
- Same metric mentioned multiple times with different values
- Conflicting statements

**Example:** `test_roi_contradictory.pdf`
```
[Page 1]
Our solution achieved 250% ROI over 24 months.

[Page 3]
Summary: The 18-month study showed 180% return on investment.
```

**Expected Behavior:**
- Agent should note contradiction
- Should provide both values with sources
- Should lower confidence score
- Should add to `missing_information`: "Contradictory ROI values found"

---

#### Document Type 4: Missing Context
**Purpose:** Test metric extraction without surrounding context

**Content Characteristics:**
- Numbers without clear attribution
- Metrics without units
- Unclear timeframes

**Example:** `test_roi_context.pdf`
```
Key Results:
- 340%
- $2.4M
- 14 months
- 25%
```

**Expected Behavior:**
- Should ask for clarification (in missing_information)
- Should provide low confidence
- Should note: "Metrics found but context unclear"

---

#### Document Type 5: Scanned/Poor Quality
**Purpose:** Test text extraction quality

**Content Characteristics:**
- Scanned PDF (not text-based)
- Poor OCR quality
- Missing characters

**Example:** `test_roi_scanned.pdf` (scanned image with text):
```
ROI: 2 0%  (missing 5)
Payback: 1  months (missing 8)
```

**Expected Behavior:**
- Hybrid PDF processing should use Claude Vision
- Should extract correctly: "250%", "18 months"
- Should note extraction_method: "Claude_Vision"

---

## Manual Testing Procedures

### Manual Test 1: Side-by-Side Comparison

#### Materials Needed
- Test document (printed or on second monitor)
- Agent output (JSON)
- Verification checklist

#### Procedure

**Step 1: Print Document**
Print `test_roi_baseline.pdf` for reference.

**Step 2: Run Agent**
```bash
python extract_document.py test_roi_baseline.pdf > output.json
```

**Step 3: Extract Claims**
Open `output.json`, list all extractions:

```
Extraction 1:
  name: "250% ROI Achievement"
  metrics: {"roi": "250%", "payback_months": 12}
  source_text: "..."
  page_numbers: [1]

Extraction 2:
  name: "Clinical Outcome Improvements"
  metrics: {"hba1c_reduction": "1.2%"}
  source_text: "..."
  page_numbers: [2]

... (continue for all extractions)
```

**Step 4: Verify Each Extraction**

For Extraction 1:
1. Find claimed source on document page 1
2. Read source_text in document
3. Check if metrics appear in source_text
4. Mark: ✅ Correct | ❌ Hallucinated | ⚠️ Paraphrased

**Step 5: Calculate Scores**
```
Total Extractions: 15
Correct: 13 (86.7%)
Hallucinated: 2 (13.3%)
Paraphrased: 0 (0%)
```

---

### Manual Test 2: Cross-Document Consistency

#### Objective
Test if agent maintains consistency when same information appears in multiple documents.

#### Procedure

**Create 3 documents with same data:**
- `doc1_roi.pdf`: "250% ROI"
- `doc2_case_study.pdf`: "250% ROI"
- `doc3_white_paper.pdf`: "250% ROI"

**Run agent on each:**
```bash
python extract_document.py doc1_roi.pdf > result1.json
python extract_document.py doc2_case_study.pdf > result2.json
python extract_document.py doc3_white_paper.pdf > result3.json
```

**Compare extractions:**

| Metric | Doc 1 | Doc 2 | Doc 3 | Consistent? |
|--------|-------|-------|-------|-------------|
| ROI | 250% | 250% | 300% | ❌ No |
| Payback | 12 mo | 12 mo | 12 mo | ✅ Yes |

**If inconsistent:**
- Layer 5 should catch this (one has hallucination)
- OR all three verified → Need to investigate why Doc 3 differs

---

## Automated Testing Framework

### Automated Test Suite Structure

```
tests/hallucination/
├── conftest.py                          # Pytest fixtures
├── test_documents/                      # Test PDFs
│   ├── baseline_clean.pdf
│   ├── baseline_vague.pdf
│   ├── baseline_contradictory.pdf
│   └── ground_truth.json               # Known correct extractions
├── test_hallucination_detection.py     # Core tests
├── test_lineage_tracking.py            # Lineage tests
└── test_metrics.py                      # Performance metrics
```

### Test 1: Ground Truth Verification (Automated)

#### Setup: Create Ground Truth File

**File:** `test_documents/ground_truth.json`

```json
{
  "test_roi_baseline.pdf": {
    "expected_extractions": [
      {
        "name": "250% ROI Achievement",
        "metrics": {
          "roi": "250%",
          "payback_months": 12,
          "total_savings": "$1,250,000"
        },
        "source_text_contains": [
          "250% return on investment",
          "12 months",
          "$1,250,000"
        ],
        "page_numbers": [1],
        "confidence_min": 0.8
      },
      {
        "name": "HbA1c Reduction Outcome",
        "metrics": {
          "hba1c_reduction": "1.2 percentage points"
        },
        "source_text_contains": [
          "HbA1c Reduction: 1.2 percentage points"
        ],
        "page_numbers": [2],
        "confidence_min": 0.8
      }
    ]
  }
}
```

#### Automated Test Code

**File:** `tests/hallucination/test_hallucination_detection.py`

```python
import pytest
import json
from pathlib import Path

def load_ground_truth():
    """Load known correct extractions."""
    with open("test_documents/ground_truth.json") as f:
        return json.load(f)

def extract_document(pdf_path):
    """
    Run DocumentAnalysisAgent on document.

    Returns:
        DocumentAnalysisResult
    """
    # Implementation here
    pass

def verify_extraction_matches_ground_truth(extraction, expected):
    """
    Compare extraction to ground truth.

    Returns:
        (is_match, errors)
    """
    errors = []

    # Check metrics match
    for key, expected_value in expected["metrics"].items():
        actual_value = extraction.metrics.get(key)
        if actual_value != expected_value:
            errors.append(f"Metric mismatch: {key} = {actual_value}, expected {expected_value}")

    # Check source_text contains expected phrases
    for phrase in expected["source_text_contains"]:
        if phrase not in extraction.source_text:
            errors.append(f"Missing phrase in source_text: '{phrase}'")

    # Check page numbers
    if extraction.page_numbers != expected["page_numbers"]:
        errors.append(f"Page number mismatch: {extraction.page_numbers} != {expected['page_numbers']}")

    # Check confidence threshold
    if extraction.extraction_confidence < expected["confidence_min"]:
        errors.append(f"Confidence too low: {extraction.extraction_confidence} < {expected['confidence_min']}")

    return (len(errors) == 0, errors)

@pytest.mark.parametrize("document,ground_truth", [
    ("test_roi_baseline.pdf", load_ground_truth()["test_roi_baseline.pdf"])
])
def test_extraction_accuracy(document, ground_truth):
    """Test that extractions match ground truth."""

    # Run extraction
    result = extract_document(f"test_documents/{document}")

    # Compare each extraction
    for expected in ground_truth["expected_extractions"]:
        # Find matching extraction by name
        actual = next(
            (e for e in result.extracted_value_propositions if e.name == expected["name"]),
            None
        )

        assert actual is not None, f"Missing expected extraction: {expected['name']}"

        # Verify match
        is_match, errors = verify_extraction_matches_ground_truth(actual, expected)

        assert is_match, f"Extraction doesn't match ground truth:\n" + "\n".join(errors)

def test_hallucination_not_present():
    """Test that common hallucinations are NOT present."""

    result = extract_document("test_documents/test_roi_baseline.pdf")

    # Known hallucination patterns
    hallucination_checks = [
        ("roi", "300%", "Agent should not inflate to 300%"),
        ("roi", "500%", "Agent should not inflate to 500%"),
        ("payback_months", 6, "Agent should not compress timeframe to 6 months"),
        ("pmpm", "$45", "Agent should not invent PMPM not in document")
    ]

    for extraction in result.extracted_value_propositions:
        for metric_key, hallucinated_value, message in hallucination_checks:
            actual_value = extraction.metrics.get(metric_key)
            assert actual_value != hallucinated_value, message

def test_layer5_catches_hallucination():
    """Test that Layer 5 rejects hallucinated claims."""

    # Create extraction with intentional hallucination
    hallucinated_extraction = {
        "name": "Inflated ROI",
        "metrics": {"roi": "500%"},  # Document says 250%
        "source_text": "250% return on investment",  # Contradicts metrics
        "page_numbers": [1]
    }

    # Run Layer 5 verification
    verification_result = verify_extraction_against_source(
        extraction=hallucinated_extraction,
        full_document_text="250% return on investment over 24 months",
        document_pages=["250% return on investment over 24 months"],
        document_metadata={}
    )

    # Should detect hallucination
    assert verification_result["is_hallucinated"] == True
    assert "500%" in str(verification_result["issues"])

def test_retry_corrects_hallucination():
    """Test that retry loop fixes hallucination after feedback."""

    # This would require running full agent with retry
    # Track attempts and verify correction happens
    pass
```

#### Running Automated Tests

```bash
# Run all hallucination tests
pytest tests/hallucination/ -v

# Run specific test
pytest tests/hallucination/test_hallucination_detection.py::test_extraction_accuracy -v

# Run with coverage
pytest tests/hallucination/ --cov=agents --cov=core/validation
```

---

### Test 2: Lineage Tracking (Automated)

**File:** `tests/hallucination/test_lineage_tracking.py`

```python
import pytest
from uuid import UUID

def test_lineage_record_created():
    """Test that lineage record is created on extraction."""

    # Extract document
    result = extract_document("test_documents/test_roi_baseline.pdf")

    # Get extraction ID
    extraction = result.extracted_value_propositions[0]
    extraction_id = extraction.extraction_id

    assert extraction_id is not None
    assert isinstance(extraction_id, UUID)

    # Query database
    lineage = query_lineage_by_id(extraction_id)

    assert lineage is not None
    assert lineage.source_document_url == "test_documents/test_roi_baseline.pdf"
    assert lineage.extraction_agent == "DocumentAnalysisAgent"
    assert lineage.verification_status == "verified"

def test_lineage_complete_chain():
    """Test end-to-end lineage tracking."""

    # Step 1: Extract
    extraction_result = extract_document("test_documents/test_roi_baseline.pdf")
    extraction_id = extraction_result.extracted_value_propositions[0].extraction_id

    # Step 2: Build ROI Model
    roi_model = build_roi_model(extraction_ids=[extraction_id])
    roi_model_id = roi_model.model_id

    # Step 3: Generate Dashboard
    dashboard = generate_dashboard(roi_model_id=roi_model_id)
    dashboard_id = dashboard.dashboard_id

    # Step 4: Verify lineage updated
    lineage = query_lineage_by_id(extraction_id)

    assert roi_model_id in lineage.used_in_roi_models
    assert dashboard_id in lineage.used_in_dashboards

    # Step 5: Reverse lookup
    audit_trail = query_audit_trail(dashboard_id)

    assert extraction_id in audit_trail.extraction_ids
    assert audit_trail.source_document_url == "test_documents/test_roi_baseline.pdf"

def test_lineage_query_performance():
    """Test that lineage queries are fast."""

    import time

    # Create 100 extractions
    extraction_ids = []
    for i in range(100):
        result = extract_document(f"test_documents/test_roi_{i}.pdf")
        extraction_ids.append(result.extracted_value_propositions[0].extraction_id)

    # Time lineage queries
    start = time.time()
    for extraction_id in extraction_ids:
        lineage = query_lineage_by_id(extraction_id)
    elapsed = time.time() - start

    avg_query_time = elapsed / 100

    # Should be < 50ms per query
    assert avg_query_time < 0.05, f"Query too slow: {avg_query_time}s per query"
```

---

## Metrics & Measurement

### Key Performance Indicators (KPIs)

#### KPI 1: Hallucination Detection Rate
**Formula:**
```python
detection_rate = hallucinations_caught / total_hallucinations

# Example: Layer 5 caught 19 out of 20 hallucinations
detection_rate = 19 / 20 = 0.95 (95%)
```

**Target:** >95%

**Measurement:**
Run 100 test documents, manually verify all extractions, calculate rate.

---

#### KPI 2: False Positive Rate
**Formula:**
```python
false_positive_rate = valid_claims_rejected / total_valid_claims

# Example: Layer 5 rejected 3 valid claims out of 80 total valid
false_positive_rate = 3 / 80 = 0.0375 (3.75%)
```

**Target:** <5%

**Measurement:**
Track when Layer 5 rejects extractions that are actually correct.

---

#### KPI 3: Extraction Quality Score
**Formula:**
```python
quality_score = (
    0.4 * accuracy_score +
    0.3 * confidence_score +
    0.2 * completeness_score +
    0.1 * consistency_score
)

where:
  accuracy_score = correct_extractions / total_extractions
  confidence_score = avg(extraction_confidence for verified extractions)
  completeness_score = required_fields_populated / total_required_fields
  consistency_score = consistent_cross_document / total_cross_document
```

**Target:** >0.9 (90%)

---

#### KPI 4: Retry Success Rate
**Formula:**
```python
retry_success_rate = passed_after_retry / total_retries

# Example: 7 out of 8 retries succeeded
retry_success_rate = 7 / 8 = 0.875 (87.5%)
```

**Target:** >80%

**Measurement:**
Track extractions that failed Layer 5 on first attempt but passed after retry.

---

#### KPI 5: Lineage Coverage
**Formula:**
```python
lineage_coverage = extractions_with_lineage / total_extractions

# Should be 100% - every extraction has lineage record
```

**Target:** 100%

---

### Measurement Dashboard

Create monitoring dashboard with real-time metrics:

```
┌─────────────────────────────────────────────────────┐
│  Hallucination Detection Dashboard                  │
├─────────────────────────────────────────────────────┤
│  Hallucination Detection Rate:  96.5%  ✅ (Target: >95%) │
│  False Positive Rate:           3.2%   ✅ (Target: <5%)  │
│  Extraction Quality Score:      0.92   ✅ (Target: >0.9) │
│  Retry Success Rate:            85%    ✅ (Target: >80%) │
│  Lineage Coverage:              100%   ✅ (Target: 100%) │
├─────────────────────────────────────────────────────┤
│  Recent Hallucinations Caught (Last 24h)            │
│  • ROI inflated from 250% to 400% (caught)          │
│  • Payback compressed from 18mo to 12mo (caught)    │
│  • PMPM invented ($45, not in doc) (caught)         │
├─────────────────────────────────────────────────────┤
│  Recent False Positives (Last 24h)                  │
│  • "1.2 percentage points" flagged (valid) ⚠️       │
│  • "24-month study" flagged (valid) ⚠️              │
└─────────────────────────────────────────────────────┘
```

---

## Common Hallucination Patterns

### Pattern Recognition Guide

#### Pattern 1: The Optimist (Numeric Inflation)
**Signature:** Agent increases numbers by 20-100%

**Examples:**
- Document: "150% ROI" → Agent: "250% ROI"
- Document: "$500K savings" → Agent: "$1M savings"

**Why It Happens:**
- Training data bias toward impressive numbers
- Context suggests "strong performance" → Agent invents specific value

**Detection:**
Layer 5 Check 3 (Numeric Value Verification) catches this.

---

#### Pattern 2: The Sprinter (Timeframe Compression)
**Signature:** Agent shortens timeframes to sound faster

**Examples:**
- Document: "24-month implementation" → Agent: "12-month implementation"
- Document: "Results in 18 months" → Agent: "Results in 6 months"

**Why It Happens:**
- "Quick results" associated with good solutions
- Agent conflates "fast" with "better"

**Detection:**
Layer 5 Check 3 (Numeric Value Verification) catches this.

---

#### Pattern 3: The Inventor (Metric Fabrication)
**Signature:** Agent creates plausible but non-existent metrics

**Examples:**
- Document mentions "cost savings" → Agent: "PMPM reduction: $45"
- Document mentions "clinical outcomes" → Agent: "HbA1c reduction: 1.5%"

**Why It Happens:**
- Agent has domain knowledge of typical metrics
- Fills in "expected" values when not explicitly stated

**Detection:**
Layer 5 Check 1 (Full Text Search) catches this - invented metric not in document.

---

#### Pattern 4: The Novelist (Source Text Embellishment)
**Signature:** Agent adds adjectives and context not in original

**Examples:**
- Document: "250% ROI"
- Agent source_text: "We achieved a remarkable 250% ROI with significant cost savings"
- Problem: "remarkable" and "significant cost savings" not in original

**Why It Happens:**
- Agent paraphrases instead of copying verbatim
- Natural language generation adds "helpful" context

**Detection:**
Layer 5 Check 1 (Full Text Search) - embellished source_text not found verbatim.

---

#### Pattern 5: The Guesser (Page Number Errors)
**Signature:** Agent assigns wrong page numbers

**Examples:**
- ROI actually on page 5 → Agent: `"page_numbers": [1, 2]`

**Why It Happens:**
- Agent doesn't track page boundaries accurately
- Guesses based on typical document structure

**Detection:**
Layer 5 Check 2 (Page Number Verification) catches this.

---

## Debugging & Troubleshooting

### Debugging Guide

#### Issue 1: High False Positive Rate (>5%)

**Symptom:** Valid extractions rejected by Layer 5

**Diagnosis Steps:**

1. **Check rejected extractions:**
```python
rejected = [e for e in extractions if e.verification_status == "failed"]
for extraction in rejected:
    print(f"Rejected: {extraction.name}")
    print(f"Issues: {extraction.verification_issues}")
```

2. **Common causes:**
- Fuzzy matching too strict (source_text requires exact match)
- Page number detection inaccurate
- Numeric format variations (e.g., "$1,250,000" vs "$1.25M")

3. **Solutions:**
- Implement fuzzy text matching (90% similarity instead of 100%)
- Allow numeric format variations
- Relax page number requirement (at least 1 match instead of all)

---

#### Issue 2: Low Detection Rate (<95%)

**Symptom:** Hallucinations passing through Layer 5

**Diagnosis Steps:**

1. **Find undetected hallucinations:**
```python
# Manual verification
for extraction in result.extracted_value_propositions:
    if extraction.verification_status == "verified":
        # Manually check if this is actually hallucinated
        is_actually_hallucinated = manual_check(extraction, document)
        if is_actually_hallucinated:
            print(f"Missed hallucination: {extraction.name}")
```

2. **Common causes:**
- Agent cleverly creates plausible source_text that passes checks
- Numeric values in source_text but in wrong context
- Paraphrasing passes as "close enough"

3. **Solutions:**
- Strengthen Check 3 (verify numbers in correct context)
- Add Check 6 (semantic similarity between description and source_text)
- Lower confidence threshold (0.8 instead of 0.7)

---

#### Issue 3: Lineage Records Missing

**Symptom:** `used_in_roi_models` not populated

**Diagnosis Steps:**

1. **Check if ROI Model Builder calls record_usage:**
```python
# In roi_model_builder_agent.py
def build_roi_model(extractions):
    model = create_model(extractions)

    # THIS LINE MISSING?
    record_extraction_usage(extraction_ids, model.model_id)

    return model
```

2. **Check database constraints:**
```sql
-- Verify extraction_id exists
SELECT COUNT(*) FROM extraction_lineage WHERE extraction_id = 'uuid-123';

-- Check for FK errors in logs
SELECT * FROM pg_stat_database WHERE datname = 'triton';
```

3. **Solutions:**
- Add usage tracking call to all consumers (ROI Model Builder, Dashboard Generator)
- Implement usage tracking as database trigger (automatic)
- Add monitoring for lineage coverage

---

### Common Error Messages

#### Error: "source_text not found in document"
**Cause:** Agent invented or heavily paraphrased the quote

**Solution:** Review prompt to emphasize VERBATIM copying

---

#### Error: "Numeric value X not found in source_text"
**Cause:** Agent put number in metrics but not in source_text

**Solution:** Check that agent includes numbers in source_text field

---

#### Error: "Page numbers [1, 2] do not contain source_text"
**Cause:** Agent guessed wrong pages OR page splitting incorrect

**Solution:**
1. Verify document_pages split correctly
2. Relax to "at least 1 page must match" instead of "all pages"

---

## Summary

### Testing Checklist

**Pre-Implementation (Current State):**
- [ ] Run baseline hallucination test (Test 1)
- [ ] Identify common patterns (Test 2)
- [ ] Measure inter-run consistency (Test 3)
- [ ] Calculate baseline rate: _____%

**Post-Implementation (With Layer 5):**
- [ ] Test detection accuracy (Test 4)
- [ ] Verify retry effectiveness (Test 5)
- [ ] Validate lineage tracking (Test 6)
- [ ] Run automated test suite
- [ ] Measure all KPIs
- [ ] Verify >95% detection rate
- [ ] Verify <5% false positive rate
- [ ] Verify 100% lineage coverage

### Quick Start

**To test if hallucination is happening NOW:**
```bash
# 1. Extract a document
python extract_document.py your_document.pdf > output.json

# 2. Manually verify against document
python verify_extraction.py your_document.pdf output.json

# 3. Get hallucination report
# Outputs: X% of claims were hallucinated
```

**To test Layer 5 effectiveness (after implementation):**
```bash
# Run automated test suite
pytest tests/hallucination/ -v --cov

# Check metrics dashboard
python generate_metrics_report.py
```

---

**Document Status:** ✅ Ready for Testing
**Next Action:** Run baseline tests to measure current hallucination rate
**Contact:** QA Team / Engineering Lead

**End of Document**
