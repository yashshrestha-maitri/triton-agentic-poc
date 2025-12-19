"""Pydantic models for Value Proposition Research.

These models support WebSearchAgent and DocumentAnalysisAgent outputs
as specified in TRITON_ENGINEERING_SPEC.md Section 4.2.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from uuid import UUID


# =============================================================================
# Web Search Agent Output Models
# =============================================================================

class CompanyOverview(BaseModel):
    """Company overview from web research."""
    name: str = Field(..., description="Company name")
    description: str = Field(..., min_length=50, description="Company description")
    mission: Optional[str] = Field(None, description="Company mission statement")
    target_markets: List[str] = Field(
        default_factory=list,
        description="Target market segments (e.g., 'Health Plans', 'Employers')"
    )
    website: Optional[str] = Field(None, description="Company website URL")


class ValuePropositionEvidence(BaseModel):
    """Single value proposition with evidence."""
    name: str = Field(..., min_length=10, description="Value proposition name")
    description: str = Field(..., min_length=30, description="Detailed description")
    evidence_type: Literal['explicit', 'inferred', 'assumed'] = Field(
        ..., description="How this value prop was determined"
    )
    supporting_sources: List[str] = Field(
        default_factory=list, description="Source URLs"
    )
    confidence: Literal['high', 'medium', 'low'] = Field(
        ..., description="Confidence in this value proposition"
    )


class ClinicalOutcomeEvidence(BaseModel):
    """Clinical outcome claim with evidence."""
    outcome: str = Field(..., min_length=10, description="Outcome description")
    metric_value: Optional[str] = Field(
        None, description="Quantitative metric if available (e.g., 'HbA1c reduction 1.2%')"
    )
    evidence_type: Literal['published_study', 'case_study', 'marketing_claim', 'inferred'] = Field(
        ..., description="Type of evidence"
    )
    source: Optional[str] = Field(None, description="Source URL")
    confidence: Literal['high', 'medium', 'low'] = Field(..., description="Evidence confidence")


class ROIFramework(BaseModel):
    """ROI framework derived from research."""
    typical_roi_range: Optional[str] = Field(
        None, description="ROI range (e.g., '250-400%')"
    )
    payback_period: Optional[str] = Field(
        None, description="Payback period (e.g., '12-18 months')"
    )
    cost_savings_areas: List[str] = Field(
        default_factory=list,
        description="Areas where cost savings occur"
    )
    evidence_quality: Literal['high', 'medium', 'low'] = Field(
        ..., description="Quality of ROI evidence found"
    )
    supporting_sources: List[str] = Field(
        default_factory=list, description="Source URLs for ROI claims"
    )


class CompetitivePositioning(BaseModel):
    """Competitive landscape analysis."""
    main_competitors: List[str] = Field(
        default_factory=list, description="Main competitor companies"
    )
    unique_advantages: List[str] = Field(
        default_factory=list, description="Client's unique competitive advantages"
    )
    market_differentiators: List[str] = Field(
        default_factory=list, description="How client differs from competitors"
    )
    market_position: Optional[str] = Field(
        None, description="Market position assessment (e.g., 'Market leader', 'Challenger')"
    )


class WebSearchResult(BaseModel):
    """Output from WebSearchAgent.

    This is the structured result returned by WebSearchAgent after
    conducting web research on a healthcare company.
    """
    searches_performed: int = Field(..., ge=0, description="Number of searches conducted")
    queries: List[str] = Field(..., min_items=1, description="Search queries used")

    # Core findings
    company_overview: CompanyOverview
    value_propositions: List[ValuePropositionEvidence] = Field(
        ..., min_items=1, description="Identified value propositions"
    )
    clinical_outcomes: List[ClinicalOutcomeEvidence] = Field(
        default_factory=list, description="Clinical outcomes evidence"
    )
    roi_framework: Optional[ROIFramework] = Field(
        None, description="ROI framework if identifiable"
    )
    competitive_positioning: Optional[CompetitivePositioning] = Field(
        None, description="Competitive positioning analysis"
    )

    # Target audiences
    target_audiences: List[str] = Field(
        ..., min_items=1, description="Identified target audiences"
    )

    # Sources and metadata
    sources: List[str] = Field(..., min_items=1, description="All source URLs consulted")
    research_mode: Literal['autonomous', 'manual'] = Field(
        ..., description="Mode used for research"
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Overall confidence in research findings"
    )

    # Flags for missing information
    missing_information: List[str] = Field(
        default_factory=list,
        description="List of critical information that could not be found"
    )
    assumptions_made: List[str] = Field(
        default_factory=list,
        description="Assumptions made where evidence was lacking"
    )

    # Metadata
    research_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "searches_performed": 18,
                "queries": ["Livongo diabetes", "Livongo ROI", "Livongo clinical outcomes"],
                "company_overview": {
                    "name": "Livongo Health",
                    "description": "Digital health company focused on chronic disease management",
                    "mission": "Empower people with chronic conditions",
                    "target_markets": ["Health Plans", "Employers"],
                    "website": "https://livongo.com"
                },
                "value_propositions": [
                    {
                        "name": "Cost Reduction through Prevention",
                        "description": "Reduce diabetes-related costs through prevention",
                        "evidence_type": "explicit",
                        "supporting_sources": ["https://example.com"],
                        "confidence": "high"
                    }
                ],
                "clinical_outcomes": [],
                "roi_framework": {
                    "typical_roi_range": "250-400%",
                    "payback_period": "12-18 months",
                    "cost_savings_areas": ["Complication reduction"],
                    "evidence_quality": "high",
                    "supporting_sources": []
                },
                "competitive_positioning": {
                    "main_competitors": ["Competitor A"],
                    "unique_advantages": ["AI-powered coaching"],
                    "market_differentiators": ["Digital-first approach"],
                    "market_position": "Market leader"
                },
                "target_audiences": ["Health Plan", "Employer"],
                "sources": ["https://example.com"],
                "research_mode": "autonomous",
                "confidence_score": 0.85,
                "missing_information": [],
                "assumptions_made": [],
                "research_timestamp": "2025-01-15T12:00:00Z"
            }
        }


# =============================================================================
# Document Analysis Agent Output Models
# =============================================================================

class ExtractedValueProposition(BaseModel):
    """Value proposition extracted from client documents."""
    name: str = Field(..., min_length=10, description="Value proposition name")
    description: str = Field(..., min_length=30, description="Detailed description")
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Quantitative metrics (e.g., {'roi': '340%', 'payback_months': 14})"
    )
    source_document: str = Field(..., description="Document this was extracted from")
    page_numbers: Optional[List[int]] = Field(
        None, description="Page numbers where this appears"
    )
    confidence: Literal['high', 'medium', 'low'] = Field(
        ..., description="Extraction confidence"
    )

    # Lineage tracking fields (optional for backward compatibility)
    source_text: Optional[str] = Field(
        None,
        description="Verbatim quote from source document for traceability"
    )
    extraction_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Numeric confidence score (0.0-1.0) for verification"
    )
    verification_status: Optional[Literal['verified', 'unverified', 'flagged']] = Field(
        None,
        description="Verification status after source checking"
    )
    verification_issues: Optional[List[str]] = Field(
        None,
        description="List of verification issues if flagged"
    )
    extraction_id: Optional[UUID] = Field(
        None,
        description="UUID linking to extraction_lineage table"
    )


class ExtractedClinicalOutcome(BaseModel):
    """Clinical outcome extracted from documents."""
    outcome: str = Field(..., min_length=10, description="Outcome description")
    metric_value: Optional[str] = Field(None, description="Quantitative value")
    source_document: str = Field(..., description="Source document")
    page_numbers: Optional[List[int]] = Field(None, description="Page numbers")
    confidence: Literal['high', 'medium', 'low'] = Field(..., description="Confidence")

    # Lineage tracking fields (optional for backward compatibility)
    source_text: Optional[str] = Field(
        None,
        description="Verbatim quote from source document for traceability"
    )
    extraction_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Numeric confidence score (0.0-1.0) for verification"
    )
    verification_status: Optional[Literal['verified', 'unverified', 'flagged']] = Field(
        None,
        description="Verification status after source checking"
    )
    verification_issues: Optional[List[str]] = Field(
        None,
        description="List of verification issues if flagged"
    )
    extraction_id: Optional[UUID] = Field(
        None,
        description="UUID linking to extraction_lineage table"
    )


class ExtractedFinancialMetric(BaseModel):
    """Financial metric extracted from documents."""
    metric_name: str = Field(..., description="Metric name (e.g., 'ROI', 'Savings')")
    value: str = Field(..., description="Metric value (preserve exact format from source)")
    context: Optional[str] = Field(None, description="Context around this metric")
    source_document: str = Field(..., description="Source document")
    page_numbers: Optional[List[int]] = Field(None, description="Page numbers")

    # Lineage tracking fields (optional for backward compatibility)
    source_text: Optional[str] = Field(
        None,
        description="Verbatim quote from source document for traceability"
    )
    extraction_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Numeric confidence score (0.0-1.0) for verification"
    )
    verification_status: Optional[Literal['verified', 'unverified', 'flagged']] = Field(
        None,
        description="Verification status after source checking"
    )
    verification_issues: Optional[List[str]] = Field(
        None,
        description="List of verification issues if flagged"
    )
    extraction_id: Optional[UUID] = Field(
        None,
        description="UUID linking to extraction_lineage table"
    )


class ExtractedCompetitiveAdvantage(BaseModel):
    """Competitive advantage extracted from documents."""
    advantage: str = Field(..., min_length=10, description="Competitive advantage description")
    supporting_evidence: Optional[str] = Field(None, description="Supporting evidence")
    source_document: str = Field(..., description="Source document")


class DocumentAnalysisResult(BaseModel):
    """Output from DocumentAnalysisAgent.

    This is the structured result returned by DocumentAnalysisAgent after
    analyzing client-uploaded documents.
    """
    documents_analyzed: int = Field(..., ge=1, description="Number of documents analyzed")
    document_names: List[str] = Field(..., min_items=1, description="Document filenames")

    # Core extractions
    extracted_value_propositions: List[ExtractedValueProposition] = Field(
        ..., min_items=1, description="Value propositions found in documents"
    )
    clinical_outcomes: List[ExtractedClinicalOutcome] = Field(
        default_factory=list, description="Clinical outcomes found"
    )
    financial_metrics: List[ExtractedFinancialMetric] = Field(
        default_factory=list, description="Financial metrics extracted"
    )
    target_audiences: List[str] = Field(
        default_factory=list, description="Target audiences mentioned"
    )
    competitive_advantages: List[ExtractedCompetitiveAdvantage] = Field(
        default_factory=list, description="Competitive advantages identified"
    )

    # Additional context
    additional_context: Optional[str] = Field(
        None, description="User-provided additional context"
    )

    # Confidence and gaps
    overall_confidence: float = Field(
        ge=0.0, le=1.0, description="Overall confidence in extractions"
    )
    missing_information: List[str] = Field(
        default_factory=list, description="Critical information not found in documents"
    )

    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "documents_analyzed": 3,
                "document_names": ["roi_sheet.pdf", "case_study.pdf", "product_info.pdf"],
                "extracted_value_propositions": [
                    {
                        "name": "Cost Reduction through Prevention",
                        "description": "Reduce healthcare costs by preventing complications",
                        "metrics": {"roi": "340%", "payback_months": 14},
                        "source_document": "roi_sheet.pdf",
                        "page_numbers": [1, 2],
                        "confidence": "high"
                    }
                ],
                "clinical_outcomes": [],
                "financial_metrics": [],
                "target_audiences": ["Health Plan", "Employer"],
                "competitive_advantages": [],
                "additional_context": "Focus on diabetes management",
                "overall_confidence": 0.88,
                "missing_information": [],
                "analysis_timestamp": "2025-01-15T12:00:00Z"
            }
        }


# =============================================================================
# Validation Functions
# =============================================================================

def validate_web_search_result(result: WebSearchResult) -> Dict[str, Any]:
    """Validate WebSearchResult completeness.

    Returns validation report with errors and warnings.
    """
    errors = []
    warnings = []

    # Check minimum searches
    if result.research_mode == 'autonomous' and result.searches_performed < 15:
        warnings.append(f"Autonomous mode should perform 15-25 searches, got {result.searches_performed}")
    elif result.research_mode == 'manual' and result.searches_performed < 5:
        warnings.append(f"Manual mode should perform 5-15 searches, got {result.searches_performed}")

    # Check value propositions
    if len(result.value_propositions) < 1:
        errors.append("Must have at least 1 value proposition")

    # Check confidence for high-value findings
    high_confidence_vps = [vp for vp in result.value_propositions if vp.confidence == 'high']
    if not high_confidence_vps:
        warnings.append("No high-confidence value propositions found")

    # Check sources
    if len(result.sources) < 3:
        warnings.append(f"Only {len(result.sources)} sources consulted, recommend more for thoroughness")

    # Check for assumptions
    if result.assumptions_made:
        warnings.append(f"Made {len(result.assumptions_made)} assumptions - verify these")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_document_analysis_result(result: DocumentAnalysisResult) -> Dict[str, Any]:
    """Validate DocumentAnalysisResult completeness.

    Returns validation report with errors and warnings.
    """
    errors = []
    warnings = []

    # Check minimum extractions
    if len(result.extracted_value_propositions) < 1:
        errors.append("Must extract at least 1 value proposition from documents")

    # Check confidence
    if result.overall_confidence < 0.5:
        warnings.append(f"Low overall confidence: {result.overall_confidence}")

    # Check for high-confidence extractions
    high_conf_vps = [vp for vp in result.extracted_value_propositions if vp.confidence == 'high']
    if not high_conf_vps:
        warnings.append("No high-confidence value propositions extracted")

    # Check financial metrics
    if not result.financial_metrics:
        warnings.append("No financial metrics extracted - ROI analysis may be incomplete")

    # Check missing information
    if result.missing_information:
        warnings.append(f"Missing {len(result.missing_information)} pieces of critical information")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
