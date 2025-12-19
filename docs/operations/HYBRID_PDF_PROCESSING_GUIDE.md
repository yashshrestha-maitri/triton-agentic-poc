
# Hybrid PDF Processing Implementation Guide

**Version:** 1.0
**Date:** December 16, 2025
**Model:** Claude Sonnet 4 (`us.anthropic.claude-sonnet-4-20250514-v1:0`)

---

## 📋 Quick Reference Summary

### Execution Time & Token Costs

| Method | Extraction Time | Extraction Cost | Analysis Tokens | Analysis Cost | Total Cost |
|--------|-----------------|-----------------|-----------------|---------------|------------|
| **Traditional (PyPDF2)** | 1-3 seconds | **$0.00** (FREE) | 5K-20K tokens | $0.015-0.060 | **$0.015-0.060** |
| **Vision API** | 5-15 seconds | $0.054 (18K tokens) | 5K-20K tokens | $0.015-0.060 | **$0.069-0.114** |
| **Hybrid (70/30 split)** | Variable | Blended | Blended | Blended | **~$0.05** avg |

### Key Metrics

- **Traditional Extraction**: FREE (PyPDF2 local processing, no API calls)
- **Vision API**: ~1,800 tokens per page (10-page PDF = 18,000 tokens)
- **Document Analysis**: Always required, 5K-20K tokens regardless of extraction method
- **Success Rate**: Traditional 60-70%, Vision 95%+, Hybrid 95%+
- **Cost Savings**: Hybrid approach saves **41%** vs vision-only
- **Quality Threshold**: Documents scoring <70/100 use vision fallback

### Complete Pipeline (PDF → ROI Model)

| Step | Process | Time | Tokens | Cost |
|------|---------|------|--------|------|
| 1. PDF Extraction | PyPDF2 or Vision API | 1-15s | 0 or 18K | $0.00-0.054 |
| 2. Document Analysis | Extract value props | 5-10s | 5K-20K | $0.015-0.060 |
| 3. ROI Classification | Classify B1-B13 | 3-8s | 3K-10K | $0.010-0.030 |
| 4. ROI Model Builder | Generate 15 components | 30-60s | 50K-100K | $0.150-0.300 |
| **Total Pipeline** | **End-to-end** | **40-90s** | **58K-148K** | **$0.175-0.444** |

### When to Use Each Method

- **Traditional (PyPDF2)**: Native PDF text, quality score ≥70, <100 pages
- **Vision API**: Scanned PDFs, quality score <70, complex layouts
- **Hybrid**: Automatic decision based on quality assessment (RECOMMENDED)

---

## Executive Summary

This guide provides a complete implementation of **hybrid PDF processing** that combines traditional text extraction (PyPDF2) with Claude Vision API fallback for optimal cost, performance, and reliability.

**Key Benefits:**
- ✅ **Fast & Cheap**: Traditional extraction for normal PDFs (95% of cases)
- ✅ **Reliable**: Vision API fallback for scanned/complex PDFs (5% of cases)
- ✅ **Cost-Optimized**: Only use expensive vision tokens when necessary
- ✅ **Production-Ready**: Complete with metrics, logging, and error handling

**Performance Targets:**
- Traditional extraction (PyPDF2): ~1-3 seconds, **FREE** (local processing)
- Traditional + Analysis: $0.015-0.060 per document (5K-20K tokens for Claude analysis)
- Vision extraction + Analysis: ~5-15 seconds, $0.069-0.114 per document
- Overall success rate: >98% (up from 60-70% with traditional-only)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview) - Processing flow and decision logic
2. [Cost Analysis](#cost-analysis) - Token costs, pricing, and savings
3. [Data Flow: PDF to ROI Classification](#data-flow-pdf-to-roi-classification) - Complete pipeline
4. [Text Quality Assessment](#text-quality-assessment) - Quality scoring workflow
5. [Implementation Workflow](#implementation-workflow) - High-level workflow and components
6. [Configuration](#configuration) - Environment variables and tuning
7. [Testing Strategy](#testing-strategy) - Test scenarios and commands
8. [Monitoring & Metrics](#monitoring--metrics) - Tracking and observability
9. [Troubleshooting](#troubleshooting) - Common issues and solutions
10. [Best Practices](#best-practices) - Production recommendations
11. [Appendix](#appendix) - Cost calculators and reference tables

---

## Architecture Overview

### Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PDF Document Input                            │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Traditional Text Extraction (PyPDF2)                   │
│  • Fast: 1-3 seconds                                            │
│  • FREE: No tokens consumed (local Python processing)           │
│  • Success Rate: 60-70% of documents                            │
│  • Note: Tokens consumed later when text sent to Claude         │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Text Quality Assessment                                │
│  • Check text density (chars per page)                          │
│  • Detect extraction confidence                                 │
│  • Identify scanned PDF markers                                 │
│  • Calculate quality score (0-100)                              │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
                    Quality Score >= 70?
                             │
                ┌────────────┴────────────┐
               YES                        NO
                ↓                          ↓
┌───────────────────────────┐  ┌─────────────────────────────────┐
│  Return Text              │  │  Step 3: Vision API Fallback    │
│  ✅ Fast path             │  │  • Slower: 5-15 seconds         │
│  💰 FREE extraction       │  │  • Expensive: ~18K tokens       │
│  📊 60-70% of docs        │  │  • (1,800 tokens/page × 10)     │
│  📝 Analysis: 5K-20K      │  │  • High reliability: 95%+       │
└───────────────────────────┘  │  • Handles scanned PDFs         │
                               └─────────────┬───────────────────┘
                                             ↓
                               ┌─────────────────────────────────┐
                               │  Return Extracted Text          │
                               │  ⚠️  Slow path                  │
                               │  💰💰 High cost                │
                               │  📝 Analysis: +5K-20K tokens    │
                               │  📊 30-40% of docs              │
                               └─────────────────────────────────┘
```

### Decision Logic

```python
if quality_score >= 70:
    return traditional_text  # Fast path (60-70% of documents)
elif quality_score >= 50:
    return traditional_text  # Acceptable quality (20-25% of documents)
else:
    return vision_api_text   # Fallback for poor extraction (5-15% of documents)
```

---

## Cost Analysis

### Token Consumption Breakdown

**IMPORTANT:** Traditional PDF extraction (PyPDF2) is **FREE** - it's just Python code reading the PDF. Tokens are only consumed when sending extracted text to Claude for analysis.

#### Traditional Text Extraction Pipeline
1. **PyPDF2 Extraction**: 1-3 seconds, **$0.00** (free local processing)
2. **Claude Analysis**: 5,000-20,000 tokens for analysis
   - **Cost**: $0.015 - $0.060 (input tokens at $0.003/1K)
   - **Total pipeline cost**: $0.015 - $0.060 per document

#### Vision API Extraction Pipeline
1. **Claude Vision API**: ~1,800 tokens per page
   - **10-page PDF**: ~18,000 tokens
   - **Cost**: $0.054 for extraction (at $0.003/1K)
2. **Claude Analysis**: Additional 5,000-20,000 tokens
   - **Cost**: $0.015 - $0.060 for analysis
   - **Total pipeline cost**: $0.069 - $0.114 per document
   - **Processing time**: 5-15 seconds
   - **Success rate**: 95%+

### Cost Comparison Example

**Scenario: 1,000 PDF documents processed**

#### Traditional-Only Approach
```
Success rate: 70%
Successful: 700 × $0.040 = $28.00 (extraction FREE + $0.040 analysis avg)
Failed: 300 documents need manual processing
Total cost: $28.00 + manual labor
```

#### Vision-Only Approach
```
Success rate: 95%
Successful: 950 × $0.090 = $85.50 (extraction $0.054 + $0.036 analysis avg)
Failed: 50 documents need manual processing
Total cost: $85.50 + minimal manual labor
```

#### Hybrid Approach (RECOMMENDED)
```
Traditional (70%): 700 × $0.040 = $28.00 (extraction FREE + analysis)
Vision fallback (25%): 250 × $0.090 = $22.50 (extraction + analysis)
Failed (5%): 50 documents need manual processing
Total cost: $50.50 + minimal manual labor

💰 Savings vs Vision-Only: $35.00 (41% reduction)
✅ Success rate: 95% (vs 70% traditional-only)
✅ Extraction savings: Traditional extraction is FREE (PyPDF2 local processing)
```

### Monthly Cost Projections

| Volume | Traditional-Only | Vision-Only | Hybrid | Savings |
|--------|------------------|-------------|--------|---------|
| 1K docs/month | $28.00 + labor | $85.50 | $50.50 | $35.00 (41%) |
| 10K docs/month | $280.00 + labor | $855.00 | $505.00 | $350.00 (41%) |
| 100K docs/month | $2,800.00 + labor | $8,550.00 | $5,050.00 | $3,500.00 (41%) |

**Note:** Traditional-only has high manual labor costs due to 30% failure rate

### Understanding the Two-Step Process

**It's important to understand that PDF processing involves TWO separate steps:**

```
┌──────────────────────────────────────────────────────────────┐
│  STEP 1: PDF TEXT EXTRACTION                                 │
│  ════════════════════════════════════════════════════════    │
│                                                              │
│  Traditional (PyPDF2):                                       │
│  • Runs locally in Python                                   │
│  • NO tokens consumed                                        │
│  • FREE                                                      │
│  • Time: 1-3 seconds                                         │
│                                                              │
│  Vision API:                                                 │
│  • Sends PDF to Claude Vision                                │
│  • Consumes ~1,800 tokens/page                               │
│  • Cost: $0.054 for 10-page PDF                             │
│  • Time: 5-15 seconds                                        │
└──────────────────────────────────────────────────────────────┘
                             ↓
           Extracted Text (5,000-20,000 characters)
                             ↓
┌──────────────────────────────────────────────────────────────┐
│  STEP 2: DOCUMENT ANALYSIS (Always Required)                │
│  ════════════════════════════════════════════════════════    │
│                                                              │
│  • Send extracted text to DocumentAnalysisAgent              │
│  • Claude analyzes for value props, ROI metrics, etc.       │
│  • Consumes 5,000-20,000 tokens                             │
│  • Cost: $0.015-0.060                                        │
│  • This step is ALWAYS required regardless of method        │
└──────────────────────────────────────────────────────────────┘
```

**Key Insight:** The traditional method saves money on extraction (FREE vs $0.054), but BOTH methods require the analysis step ($0.015-0.060). The hybrid approach optimizes by using free extraction when possible, falling back to vision only when necessary.

---

## Data Flow: PDF to ROI Classification

This section shows the complete data flow from PDF extraction through ROI model classification.

### PDF Parser Output

```python
# Output from S3DocumentReader.read_document()
extracted_text = """
Healthcare Value Proposition Document

Company: Acme Virtual MSK Care
Product: Digital Physical Therapy Platform

Executive Summary:
Our virtual musculoskeletal (MSK) care platform reduces orthopedic surgery rates by 30%
through evidence-based digital physical therapy. We provide personalized exercise programs,
real-time progress tracking, and on-demand access to licensed physical therapists.

Clinical Outcomes:
- 30% reduction in orthopedic surgical procedures
- 85% patient engagement rate
- 4.8/5.0 patient satisfaction score
- Average pain reduction: 65% after 8 weeks

Financial Impact:
- ROI: 3.2:1 over 12 months
- Average cost savings: $8,500 per avoided surgery
- 45% reduction in imaging orders (MRI, X-ray)
- Typical health plan savings: $2.1M annually for 100,000 members

Target Audience: Health Plans, Self-Insured Employers, TPAs

Key Value Drivers:
1. Surgical avoidance through conservative treatment
2. Reduced downstream costs (imaging, medications, complications)
3. Improved member satisfaction and engagement
4. Lower absenteeism and faster return to work
"""
```

### ROI Classifier Input Payload

The extracted text is then formatted into a classification request:

```python
# Message sent to ROIClassificationAgent
classification_message = """
# ROI Model Classification Request

**Client Name**: Acme Virtual MSK Care

## Research Summary

Our virtual musculoskeletal (MSK) care platform reduces orthopedic surgery rates by 30%
through evidence-based digital physical therapy. We provide personalized exercise programs,
real-time progress tracking, and on-demand access to licensed physical therapists.

Clinical Outcomes:
- 30% reduction in orthopedic surgical procedures
- 85% patient engagement rate
- 4.8/5.0 patient satisfaction score
- Average pain reduction: 65% after 8 weeks

Financial Impact:
- ROI: 3.2:1 over 12 months
- Average cost savings: $8,500 per avoided surgery
- 45% reduction in imaging orders (MRI, X-ray)
- Typical health plan savings: $2.1M annually for 100,000 members

Target Audience: Health Plans, Self-Insured Employers, TPAs

Key Value Drivers:
1. Surgical avoidance through conservative treatment
2. Reduced downstream costs (imaging, medications, complications)
3. Improved member satisfaction and engagement
4. Lower absenteeism and faster return to work

## Web Search Data
{
  "company_overview": "Digital MSK care platform...",
  "clinical_evidence": [...],
  "pricing_model": "PMPM or case rate",
  "competitors": ["Hinge Health", "Sword Health"]
}

## Document Analysis Data
{
  "value_propositions": ["Surgical avoidance", "Cost reduction"],
  "clinical_outcomes": ["30% surgery reduction", "65% pain reduction"],
  "roi_metrics": ["3.2:1 ROI", "$8,500 per avoided surgery"]
}

---

Analyze the research data above and classify the appropriate ROI model type (B1-B13).
Return ONLY the JSON object matching ROIClassificationResult schema.
"""
```

### ROI Classifier Output

The classifier returns a complete classification result:

```json
{
  "recommended_model_type": "B7",
  "model_type_name": "Episode Optimization",
  "reasoning": {
    "primary_factors": [
      "Focus on MSK episode management and surgical avoidance",
      "Tracks outcomes across full episode from initial presentation to resolution",
      "Measures cost savings from conservative treatment vs surgical pathways"
    ],
    "clinical_domain_match": "MSK episodes are well-defined with clear trigger events (pain presentation) and measurable outcomes (surgery avoidance, pain reduction). Episode-based ROI model aligns with intervention spanning diagnosis through treatment completion.",
    "data_requirements_match": "Requires claims data for surgery rates, imaging, PT visits, and episode costs - all standard for episode-based ROI calculations. 12-month lookback period matches typical MSK episode duration.",
    "intervention_type_match": "Virtual PT platform intervenes at episode level to redirect surgical pathways to conservative care. Classic episode optimization use case targeting high-cost procedures with lower-cost alternatives.",
    "confidence_level": "high"
  },
  "alternative_models": [
    {
      "model_type_code": "B10",
      "rationale": "Could be modeled as utilization management (reducing unnecessary surgeries and imaging)",
      "applicability_score": 0.65
    },
    {
      "model_type_code": "B2",
      "rationale": "Site of service optimization aspect (virtual care vs in-person PT)",
      "applicability_score": 0.45
    }
  ],
  "key_value_drivers": [
    "Surgical avoidance",
    "Reduced imaging utilization",
    "Lower episode costs",
    "Improved clinical outcomes",
    "Enhanced member engagement"
  ],
  "clinical_focus_areas": [
    "Musculoskeletal disorders",
    "Orthopedic surgery prevention",
    "Physical therapy",
    "Pain management"
  ],
  "estimated_complexity": "medium"
}
```

### Complete Pipeline Summary

```
┌─────────────────────────────────────────────────────────────┐
│  1. PDF Document (S3)                                       │
│     • 10 pages, 500KB                                       │
│     • Client ROI case study                                 │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  2. PDF Extraction (Hybrid Processing)                      │
│     • Try PyPDF2 first (FREE)                               │
│     • Quality assessment (0-100 score)                      │
│     • Vision fallback if needed ($0.054)                    │
│     • Output: 5,000-20,000 characters of text               │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Document Analysis Agent                                 │
│     • Analyzes extracted text                               │
│     • Identifies value props, ROI metrics, clinical data    │
│     • Cost: $0.015-0.060 (5K-20K tokens)                    │
│     • Output: DocumentAnalysisResult JSON                   │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  4. ROI Classification Agent                                │
│     • Input: Research summary + document analysis           │
│     • Classifies ROI model type (B1-B13)                    │
│     • Cost: $0.010-0.030 (3K-10K tokens)                    │
│     • Output: ROIClassificationResult (model type + reason) │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  5. ROI Model Builder Agent                                 │
│     • Input: Classification + research data                 │
│     • Generates complete 15-component ROI model             │
│     • Cost: $0.150-0.300 (50K-100K tokens)                  │
│     • Output: Complete ROIModelJSON                         │
└─────────────────────────────────────────────────────────────┘
```

**Total Pipeline Cost (per document):**
- Best case (traditional extraction): $0.175 - $0.390
- Worst case (vision extraction): $0.229 - $0.444

---

## Text Quality Assessment

### Quality Assessment Algorithm

The quality assessment determines whether traditional text extraction is sufficient or if Vision API fallback is needed.

#### Assessment Criteria

```python
def assess_text_quality(text: str, page_count: int, file_size_bytes: int) -> dict:
    """
    Assess the quality of extracted text to determine if Vision API fallback is needed.

    Returns:
        {
            'quality_score': 0-100,
            'needs_vision_fallback': bool,
            'confidence': 'high' | 'medium' | 'low',
            'issues': [list of detected issues],
            'metrics': {detailed metrics}
        }
    """
```

#### Quality Score Calculation (0-100)

**Component Scores:**

1. **Text Density (40 points)**
   - Measures characters per page
   - Target: >500 chars/page = full points
   - Formula: `min(chars_per_page / 500 * 40, 40)`

2. **Extraction Confidence (30 points)**
   - Detects common extraction failures
   - Checks for:
     - Excessive special characters (>20% = -10 points)
     - Very short lines (<10 chars = -5 points)
     - Missing word boundaries (-10 points)
     - Garbled encoding (-15 points)

3. **Content Structure (20 points)**
   - Validates document structure
   - Checks for:
     - Paragraph breaks (+10 points)
     - Sentence structure (+5 points)
     - Proper punctuation (+5 points)

4. **Scanned PDF Detection (10 points)**
   - Identifies likely scanned documents
   - Deducts points for:
     - Large file size but little text (-5 points)
     - Image-heavy indicators (-5 points)

#### Quality Assessment Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│         TEXT QUALITY ASSESSMENT WORKFLOW (0-100 Score)          │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  INPUT: Extracted Text + Metadata                               │
│  • text: string (extracted via PyPDF2)                          │
│  • page_count: int                                              │
│  • file_size_bytes: int                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  COMPONENT 1: Text Density (40 points max)                      │
│  ════════════════════════════════════════                       │
│                                                                 │
│  Calculate: chars_per_page = text_length / page_count           │
│                                                                 │
│  Scoring:                                                       │
│  • ≥500 chars/page → 40 points                                 │
│  • 300-500 chars/page → 24-40 points                           │
│  • 100-300 chars/page → 8-24 points                            │
│  • <100 chars/page → 0-8 points                                │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  COMPONENT 2: Extraction Confidence (30 points max)             │
│  ════════════════════════════════════════                       │
│                                                                 │
│  Check for extraction issues (start with 30, deduct points):   │
│                                                                 │
│  • Special character ratio >30% → -15 points                   │
│  • Special character ratio >20% → -10 points                   │
│  • Short lines ratio >30% → -10 points                         │
│  • Short lines ratio >20% → -5 points                          │
│  • Long words (>20 chars) >5% → -10 points                     │
│  • Garbled encoding detected → -15 points                      │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  COMPONENT 3: Content Structure (20 points max)                 │
│  ════════════════════════════════════════                       │
│                                                                 │
│  Check document structure:                                      │
│                                                                 │
│  • Paragraph breaks (\\n\\n):                                    │
│    - >2 per page → +10 points                                  │
│    - Some present → +5 points                                  │
│    - None → 0 points                                           │
│                                                                 │
│  • Sentence endings (. ! ?):                                   │
│    - >5 per page → +5 points                                   │
│    - Some present → +2 points                                  │
│    - None → 0 points                                           │
│                                                                 │
│  • Punctuation ratio (1-10%):                                  │
│    - Normal range → +5 points                                  │
│    - Outside range → 0 points                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  COMPONENT 4: Scanned PDF Detection (10 point penalty max)     │
│  ════════════════════════════════════════                       │
│                                                                 │
│  Check for scanned document indicators:                         │
│                                                                 │
│  • bytes_per_char >1000 + low text → -5 points                │
│  • text_length <200 chars/page → -5 points                     │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  FINAL CALCULATION                                              │
│  ════════════════════════════════════════                       │
│                                                                 │
│  quality_score = Component1 + Component2 + Component3           │
│                  - Component4_penalties                          │
│                                                                 │
│  quality_score = max(0, min(100, quality_score))               │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  DECISION LOGIC                                                 │
│  ════════════════════════════════════════                       │
│                                                                 │
│  IF quality_score >= 70:                                       │
│    ✅ Use traditional extraction (no fallback needed)          │
│    confidence = 'high' if score >= 80                          │
│    confidence = 'medium' if 70 <= score < 80                   │
│                                                                 │
│  ELSE (quality_score < 70):                                    │
│    ⚠️  Vision API fallback required                            │
│    confidence = 'low'                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT: Quality Assessment Result                              │
│  {                                                              │
│    quality_score: 0-100,                                       │
│    needs_vision_fallback: boolean,                             │
│    confidence: 'high' | 'medium' | 'low',                      │
│    issues: [list of detected problems],                        │
│    metrics: {detailed component scores}                        │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Quality Score Interpretation

| Score Range | Interpretation | Action |
|-------------|----------------|--------|
| 90-100 | Excellent extraction | ✅ Use traditional text |
| 80-89 | Good extraction | ✅ Use traditional text |
| 70-79 | Acceptable extraction | ✅ Use traditional text |
| 60-69 | Marginal extraction | ⚠️ Consider vision fallback |
| 50-59 | Poor extraction | ❌ Use vision fallback |
| 0-49 | Failed extraction | ❌ Use vision fallback |

---

## Implementation Workflow

### High-Level Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      HYBRID PDF PROCESSING                       │
│                         WORKFLOW                                │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│  INPUT: PDF Document from S3                                  │
│  • Path: s3://bucket/key/document.pdf                         │
│  • Size: Variable (10KB - 50MB)                               │
│  • Pages: Variable (1-500 pages)                              │
└───────────────────────┬───────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 1: Download from S3                                     │
│  • boto3.get_object(Bucket, Key)                              │
│  • Read content into memory                                    │
│  • Track file_size for quality assessment                     │
│  • Time: <1 second                                            │
└───────────────────────┬───────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 2: Traditional Text Extraction (PyPDF2)                 │
│  • Import PyPDF2, create PdfReader                            │
│  • Extract text from all pages                                │
│  • Count pages for quality assessment                         │
│  • Time: 1-3 seconds                                          │
│  • Cost: $0.00 (FREE - local processing)                      │
└───────────────────────┬───────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────────┐
│  STEP 3: Quality Assessment (0-100 Score)                     │
│  • Calculate text density (chars per page)                     │
│  • Check extraction confidence (special chars, encoding)       │
│  • Validate content structure (paragraphs, sentences)         │
│  • Detect scanned PDF indicators                              │
│  • Time: <0.1 seconds                                         │
│  • Output: quality_score, confidence, issues[]                │
└───────────────────────┬───────────────────────────────────────┘
                        ↓
              ┌─────────┴─────────┐
              │ Score >= 70?      │
              └─────────┬─────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
       YES                             NO
        │                               │
        ↓                               ↓
┌──────────────────────┐   ┌──────────────────────────────────┐
│  OPTION A:           │   │  OPTION B:                       │
│  Use Traditional     │   │  Vision API Fallback             │
│  ════════════════    │   │  ════════════════                │
│                      │   │                                  │
│  • Return text       │   │  • Check page count <= MAX_PAGES │
│  • No further cost   │   │  • Encode PDF to base64          │
│  • Fast (0s)         │   │  • Call Claude Vision API        │
│  • 60-70% of docs    │   │  • Extract text from response    │
│                      │   │  • Time: 5-15 seconds            │
│                      │   │  • Cost: $0.054 (18K tokens)     │
│                      │   │  • 25-30% of docs                │
└──────────┬───────────┘   └──────────┬───────────────────────┘
           │                          │
           └────────────┬─────────────┘
                        ↓
┌───────────────────────────────────────────────────────────────┐
│  OUTPUT: Extracted Text (5,000-20,000 characters)             │
│  • Plain text string                                          │
│  • Structured content (headings, paragraphs, lists)          │
│  • Ready for Document Analysis Agent                          │
└───────────────────────┬───────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────────┐
│  NEXT STEP: Send to DocumentAnalysisAgent                     │
│  • Analyze for value propositions                             │
│  • Extract ROI metrics, clinical outcomes                     │
│  • Cost: $0.015-0.060 (5K-20K tokens)                         │
│  • This step ALWAYS required regardless of extraction method  │
└───────────────────────────────────────────────────────────────┘
```

### Implementation Components

The hybrid PDF processing system consists of three main components working together:

```
┌─────────────────────────────────────────────────────────────────┐
│              COMPONENT 1: S3DocumentReader Class                │
│                 (tools/s3_document_reader.py)                   │
└─────────────────────────┬───────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│  Responsibilities:                                              │
│  • Download documents from S3                                   │
│  • Detect file type (.pdf, .docx, .txt)                        │
│  • Route to appropriate extraction method                       │
│  • Return extracted text + performance metrics                 │
│                                                                 │
│  Key Methods:                                                   │
│  • read_document(storage_path) → str                           │
│  • _extract_pdf_text_hybrid(content) → (text, metrics)         │
│  • _extract_pdf_text_traditional(content) → (text, pages)      │
│  • _extract_pdf_text_vision(content) → text                    │
│  • _assess_text_quality(text, pages, size) → assessment        │
│                                                                 │
│  Configuration (from .env):                                     │
│  • PDF_QUALITY_THRESHOLD=70                                    │
│  • ENABLE_VISION_FALLBACK=true                                 │
│  • MAX_VISION_PAGES=100                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│           COMPONENT 2: PyPDF2 Traditional Extraction            │
│                      (Python library)                           │
└─────────────────────────┬───────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│  Method: _extract_pdf_text_traditional()                        │
│                                                                 │
│  Process:                                                       │
│  1. Load PDF bytes into PyPDF2.PdfReader                       │
│  2. Count total pages                                          │
│  3. Loop through each page                                     │
│  4. Extract text with page.extract_text()                      │
│  5. Concatenate all page text                                  │
│                                                                 │
│  Performance:                                                   │
│  • Time: 1-3 seconds for 10-page PDF                           │
│  • Cost: $0.00 (FREE - no API calls)                           │
│  • Success rate: 60-70% (depends on PDF quality)               │
│                                                                 │
│  Returns:                                                       │
│  • (extracted_text: str, page_count: int)                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│          COMPONENT 3: Claude Vision API Extraction              │
│                   (AWS Bedrock/Claude Sonnet 4)                 │
└─────────────────────────┬───────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│  Method: _extract_pdf_text_vision()                             │
│                                                                 │
│  Process:                                                       │
│  1. Encode PDF to base64                                       │
│  2. Create vision API request with document content type       │
│  3. Send to Claude with extraction instructions                │
│  4. Parse response text                                        │
│                                                                 │
│  Request Format:                                                │
│  {                                                              │
│    "role": "user",                                             │
│    "content": [                                                │
│      {"type": "document",                                      │
│       "source": {"type": "base64",                             │
│                  "media_type": "application/pdf",              │
│                  "data": base64_encoded_pdf}},                 │
│      {"type": "text",                                          │
│       "text": "Extract ALL text from this PDF..."}            │
│    ]                                                           │
│  }                                                              │
│                                                                 │
│  Performance:                                                   │
│  • Time: 5-15 seconds for 10-page PDF                          │
│  • Cost: ~$0.054 (18,000 tokens at $0.003/1K)                 │
│  • Success rate: 95%+ (handles scanned PDFs)                   │
│                                                                 │
│  Returns:                                                       │
│  • extracted_text: str                                         │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration & Testing Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                CONFIGURATION (.env file)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  PDF_QUALITY_THRESHOLD=70                                       │
│  • Documents scoring <70 use vision fallback                    │
│  • Range: 0-100                                                 │
│  • Recommended: 70 (balanced)                                   │
│                                                                 │
│  ENABLE_VISION_FALLBACK=true                                    │
│  • Set to false to always use traditional extraction            │
│  • Recommended: true (enable smart fallback)                    │
│                                                                 │
│  MAX_VISION_PAGES=100                                           │
│  • Documents >100 pages use traditional regardless              │
│  • Prevents excessive vision API costs                          │
│  • Recommended: 100 (cost control)                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    TESTING SCENARIOS                            │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Scenario 1: High-Quality PDF (Traditional Path)               │
│  ════════════════════════════════════════════                   │
│  • Test file: 10 pages, 5,000 chars/page                       │
│  • Expected quality score: 90+                                  │
│  • Expected method: 'traditional'                               │
│  • Expected time: 1-3 seconds                                   │
│  • Expected cost: ~$0.003                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Scenario 2: Scanned PDF (Vision Fallback)                     │
│  ════════════════════════════════════════════                   │
│  • Test file: 10 pages, scanned images                         │
│  • Expected quality score: <50                                  │
│  • Expected method: 'vision_fallback'                           │
│  • Expected time: 8-12 seconds                                  │
│  • Expected cost: ~$0.054                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Scenario 3: Mixed Content PDF (Marginal Quality)              │
│  ════════════════════════════════════════════                   │
│  • Test file: 10 pages, some scanned, some text               │
│  • Expected quality score: 60-75                                │
│  • Expected method: depends on threshold                        │
│  • Expected time: varies                                        │
│  • Expected cost: varies                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Scenario 4: Large Document (Traditional Forced)               │
│  ════════════════════════════════════════════                   │
│  • Test file: 150 pages                                        │
│  • Expected quality score: any                                  │
│  • Expected method: 'traditional_forced'                        │
│  • Expected note: "Document too large for vision API"          │
│  • Expected cost: ~$0.015                                       │
└─────────────────────────────────────────────────────────────────┘
```

**Test Command:**
```bash
pytest tests/test_hybrid_pdf_processing.py -v
```

---

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# PDF Quality Threshold (0-100)
# Documents scoring below this threshold will use vision fallback
# Recommended: 70 (balances cost and quality)
PDF_QUALITY_THRESHOLD=70

# Enable/Disable Vision API Fallback
# Set to false to always use traditional extraction
ENABLE_VISION_FALLBACK=true

# Maximum Pages for Vision Processing
# Documents with more pages will use traditional extraction even if quality is low
# Recommended: 100 (keeps costs manageable)
MAX_VISION_PAGES=100
```

### Configuration Tuning

#### Conservative (Minimize Vision API Usage)
```bash
PDF_QUALITY_THRESHOLD=50  # Only use vision for severely degraded PDFs
ENABLE_VISION_FALLBACK=true
MAX_VISION_PAGES=50       # Lower page limit
```

**Expected Result:**
- Vision API usage: 5-10% of documents
- Cost savings: 75% vs vision-only
- Success rate: 85-90%

#### Balanced (Recommended)
```bash
PDF_QUALITY_THRESHOLD=70  # Standard threshold
ENABLE_VISION_FALLBACK=true
MAX_VISION_PAGES=100      # Reasonable page limit
```

**Expected Result:**
- Vision API usage: 20-30% of documents
- Cost savings: 65-70% vs vision-only
- Success rate: 95%+

#### Aggressive (Maximize Accuracy)
```bash
PDF_QUALITY_THRESHOLD=85  # High quality bar
ENABLE_VISION_FALLBACK=true
MAX_VISION_PAGES=200      # Higher page limit
```

**Expected Result:**
- Vision API usage: 40-50% of documents
- Cost savings: 40-50% vs vision-only
- Success rate: 98%+

---

## Testing Strategy

### Unit Tests

```bash
# Test quality assessment logic
pytest tests/test_hybrid_pdf_processing.py::TestTextQualityAssessment -v

# Test cost tracking
pytest tests/test_hybrid_pdf_processing.py::TestCostTracking -v
```

### Integration Tests

```bash
# Test with real PDFs from S3
pytest tests/test_hybrid_pdf_processing.py::TestHybridPDFProcessing -v --integration
```

### Test Cases

#### 1. High-Quality PDF (Traditional Path)
**Test File:** `test_high_quality.pdf` (10 pages, 5,000 chars/page)
**Expected:**
- Quality Score: 90+
- Method: `traditional`
- Processing Time: 1-3 seconds
- Cost: ~$0.003

#### 2. Scanned PDF (Vision Fallback)
**Test File:** `test_scanned.pdf` (10 pages, scanned images)
**Expected:**
- Quality Score: <50
- Method: `vision_fallback`
- Processing Time: 8-12 seconds
- Cost: ~$0.05

#### 3. Mixed Content PDF (Marginal Quality)
**Test File:** `test_mixed.pdf` (10 pages, some scanned, some text)
**Expected:**
- Quality Score: 60-75 (threshold dependent)
- Method: `traditional` or `vision_fallback` based on config
- Processing Time: Varies
- Cost: Varies

#### 4. Large Document (Traditional Forced)
**Test File:** `test_large.pdf` (150 pages)
**Expected:**
- Quality Score: Any
- Method: `traditional_forced`
- Note: "Document too large for vision API"
- Cost: ~$0.015

---

## Monitoring & Metrics

### Key Metrics to Track

#### Processing Metrics

```python
{
    "pdf_processing": {
        "method": "traditional | vision_fallback | traditional_forced",
        "processing_time_seconds": 2.34,
        "traditional_time_seconds": 1.20,  # If vision used
        "vision_time_seconds": 1.14,       # If vision used
        "quality_score": 68.5,
        "page_count": 15
    }
}
```

#### Cost Metrics

```python
{
    "cost_tracking": {
        "estimated_tokens": 18000,
        "estimated_cost_usd": 0.054,
        "file_size_bytes": 2500000,
        "cost_per_page": 0.0036
    }
}
```

#### Quality Metrics

```python
{
    "quality_assessment": {
        "confidence": "high | medium | low",
        "issues": ["Low text density: 250 chars/page"],
        "metrics": {
            "chars_per_page": 250,
            "text_density_score": 20,
            "extraction_confidence_score": 25,
            "structure_score": 15,
            "scanned_penalty": 5,
            "special_char_ratio": 0.15,
            "bytes_per_char": 1250
        }
    }
}
```

### Grafana Dashboard Queries

#### Vision API Usage Rate

```promql
# Percentage of documents using vision fallback
sum(rate(pdf_processing_total{method="vision_fallback"}[5m]))
/
sum(rate(pdf_processing_total[5m])) * 100
```

#### Average Cost Per Document

```promql
# Average cost per PDF processed
avg(pdf_processing_cost_usd)
```

#### Processing Time by Method

```promql
# Average processing time by extraction method
avg(pdf_processing_duration_seconds) by (method)
```

#### Quality Score Distribution

```promql
# Histogram of quality scores
histogram_quantile(0.95, pdf_quality_score_bucket)
```

### Logging Examples

#### Traditional Extraction (Fast Path)
```
2025-12-16 10:15:23 [INFO] Reading document: s3://triton-docs/client-123/roi_analysis.pdf
2025-12-16 10:15:23 [INFO] Downloaded 500000 bytes in 0.35s
2025-12-16 10:15:24 [INFO] Traditional extraction: quality_score=85.0, confidence=high, chars=12500, time=1.20s
2025-12-16 10:15:24 [INFO] PDF processing: method=traditional, time=1.20s, chars=12500, cost=$0.0038
```

#### Vision Fallback (Slow Path)
```
2025-12-16 10:20:45 [INFO] Reading document: s3://triton-docs/client-456/scanned_report.pdf
2025-12-16 10:20:45 [INFO] Downloaded 2500000 bytes in 0.45s
2025-12-16 10:20:47 [INFO] Traditional extraction: quality_score=42.0, confidence=low, chars=850, time=1.50s
2025-12-16 10:20:47 [WARNING] Quality issues detected: ['Very low text density: 85 chars/page', 'Likely scanned PDF: 2941 bytes/char']
2025-12-16 10:20:47 [INFO] Quality score 42.0 below threshold 70. Using vision fallback.
2025-12-16 10:20:55 [INFO] Vision extraction: chars=18500, time=8.20s, estimated_tokens=18000, cost=$0.0540
2025-12-16 10:20:55 [INFO] PDF processing: method=vision_fallback, time=9.70s, chars=18500, cost=$0.0540
```

---

## Troubleshooting

### Common Issues

#### 1. Vision API Not Working

**Symptoms:**
- Error: "vision API dependencies not installed"
- Falls back to traditional extraction even for poor quality

**Solutions:**
```bash
# Ensure AWS Bedrock is configured
aws configure --profile mare-dev

# Verify Claude model supports vision
# Model: us.anthropic.claude-sonnet-4-20250514-v1:0 ✅ Supports vision

# Check environment variables
echo $AWS_PROFILE
echo $DEFAULT_MODEL_NAME
```

#### 2. All Documents Using Vision (High Cost)

**Symptoms:**
- Most documents marked as `method=vision_fallback`
- Costs higher than expected

**Solutions:**
```bash
# Lower the quality threshold
PDF_QUALITY_THRESHOLD=50  # Instead of 70

# Check if test documents are actually scanned PDFs
# Use pdfinfo to check:
pdfinfo suspicious_document.pdf | grep Pages
```

#### 3. Quality Assessment Too Strict

**Symptoms:**
- Good quality PDFs being sent to vision fallback
- Quality scores unexpectedly low

**Solutions:**
```python
# Enable debug logging to see quality metrics
import logging
logging.getLogger("tools.s3_document_reader").setLevel(logging.DEBUG)

# Check the detailed metrics
assessment = reader._assess_text_quality(text, pages, size)
print(assessment['metrics'])
```

#### 4. Vision API Timeout

**Symptoms:**
- Error: "Vision API extraction failed: timeout"
- Large documents failing

**Solutions:**
```bash
# Reduce max vision pages
MAX_VISION_PAGES=50  # Instead of 100

# Or increase timeouts in model configuration
CELERY_TASK_TIME_LIMIT=3600  # 60 minutes instead of 30
```

### Performance Issues

#### Slow Processing

**Check:**
1. Network latency to S3
2. Model invocation time (AWS Bedrock)
3. File size (large PDFs take longer)

**Solutions:**
- Use S3 Transfer Acceleration
- Increase Celery worker concurrency
- Split large documents into smaller chunks

#### High Costs

**Check:**
1. Vision fallback percentage (`grep "vision_fallback" logs/`)
2. Average document size
3. Quality threshold setting

**Solutions:**
- Tune `PDF_QUALITY_THRESHOLD` higher
- Reduce `MAX_VISION_PAGES` limit
- Pre-filter documents (exclude known scanned PDFs)

---

## Best Practices

### 1. Start Conservative
- Begin with `PDF_QUALITY_THRESHOLD=50`
- Monitor vision fallback rate for 1 week
- Adjust threshold based on actual failure rates

### 2. Monitor Costs
- Track daily costs: `sum(pdf_processing_cost_usd)`
- Set up alerts for unexpected spikes
- Review high-cost documents monthly

### 3. Quality Over Cost
- Don't sacrifice accuracy to save money
- Failed extractions require manual work (expensive!)
- A 5% vision usage rate is healthy

### 4. Test Thoroughly
- Test with sample documents before production
- Include scanned PDFs in test suite
- Validate extracted text quality

### 5. Document Edge Cases
- Keep examples of problematic PDFs
- Note which documents required vision fallback
- Update quality assessment logic as needed

---

## Appendix

### Token Cost Calculator

```python
def calculate_pdf_processing_cost(
    page_count: int,
    chars_extracted: int,
    method: str = "traditional"
) -> dict:
    """Calculate estimated processing cost."""

    if method == "traditional":
        # Text tokens: ~1 token per 4 characters
        estimated_tokens = chars_extracted // 4
        cost_per_1k = 0.003  # Input tokens

    elif method == "vision":
        # Vision tokens: ~1,800 per page
        estimated_tokens = page_count * 1800
        cost_per_1k = 0.003

    total_cost = estimated_tokens / 1000 * cost_per_1k

    return {
        "estimated_tokens": estimated_tokens,
        "cost_per_1k_tokens": cost_per_1k,
        "total_cost_usd": total_cost,
        "cost_per_page": total_cost / max(page_count, 1)
    }


# Example usage
print(calculate_pdf_processing_cost(10, 12000, "traditional"))
# Output: {'estimated_tokens': 3000, 'cost_per_1k_tokens': 0.003, 'total_cost_usd': 0.009, 'cost_per_page': 0.0009}

print(calculate_pdf_processing_cost(10, 18000, "vision"))
# Output: {'estimated_tokens': 18000, 'cost_per_1k_tokens': 0.003, 'total_cost_usd': 0.054, 'cost_per_page': 0.0054}
```

### Quality Score Thresholds

| Threshold | Vision Usage % | Cost Savings | Success Rate | Use Case |
|-----------|----------------|--------------|--------------|----------|
| 50 | 5-10% | 75% | 85-90% | Cost-critical (MVP) |
| 60 | 15-20% | 70% | 92-95% | Balanced budget |
| 70 | 25-35% | 65% | 95-97% | **Recommended** |
| 80 | 40-50% | 50% | 97-98% | High accuracy |
| 90 | 60-70% | 30% | 98-99% | Maximum accuracy |

### File Size Guidelines

| File Size | Page Est. | Recommended Approach | Reason |
|-----------|-----------|----------------------|--------|
| < 1 MB | 1-20 | Traditional first | Fast, cost-effective |
| 1-5 MB | 20-100 | Hybrid recommended | Balance cost/quality |
| 5-20 MB | 100-500 | Traditional preferred | Vision too expensive |
| > 20 MB | 500+ | Traditional only | Vision not practical |

---

## Changelog

### v1.0 (December 16, 2025)
- Initial hybrid PDF processing implementation
- Quality assessment algorithm (4-component scoring)
- Cost tracking and metrics
- Vision API fallback support
- Configuration options
- Comprehensive testing guide

---

## References

- [Claude Vision API Documentation](https://docs.anthropic.com/claude/docs/vision)
- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [RESEARCH_AGENT_FLOW.md](../architecture-current/RESEARCH_AGENT_FLOW.md) - Current PDF processing approach

---

**Questions or Issues?**
- Check logs: `docker logs triton-worker -f | grep "PDF processing"`
- Test quality assessment: `pytest tests/test_hybrid_pdf_processing.py -v`
- Review metrics: Grafana dashboard at `http://localhost:3000`
