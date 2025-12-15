"""Pydantic models for Research Agent Results.

These models define the structure of research outputs that inform template generation.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class IndustryTrend(BaseModel):
    """Single industry trend observation."""
    trend: str = Field(..., min_length=10, description="Trend description")
    relevance: Literal['high', 'medium', 'low'] = Field(..., description="Relevance to value proposition")
    source: Optional[str] = Field(None, description="Source of trend information")


class MetricSuggestion(BaseModel):
    """Suggested metric with calculation details."""
    name: str = Field(..., description="Metric display name")
    description: str = Field(..., description="What this metric measures")
    formula: Optional[str] = Field(None, description="Calculation formula or logic")
    data_type: Literal['count', 'currency', 'percentage', 'number', 'ratio'] = Field(
        ..., description="Type of data"
    )
    typical_range: Optional[str] = Field(None, description="Expected value range (e.g., '0-100%')")
    importance: Literal['critical', 'important', 'nice-to-have'] = Field(
        ..., description="Priority level"
    )
    standard_benchmarks: Optional[List[str]] = Field(
        None, description="Industry standard benchmarks if available"
    )


class RegulatoryRequirement(BaseModel):
    """Healthcare regulatory requirement or standard."""
    name: str = Field(..., description="Requirement name (e.g., 'HEDIS', 'NCQA')")
    description: str = Field(..., description="Brief description")
    applicable: bool = Field(..., description="Whether this applies to the value proposition")
    related_metrics: List[str] = Field(default_factory=list, description="Related metric names")


class IndustryInsights(BaseModel):
    """Industry-specific insights and context."""
    key_trends: List[IndustryTrend] = Field(
        ..., min_items=3, max_items=8, description="3-8 relevant industry trends"
    )
    common_metrics: List[MetricSuggestion] = Field(
        ..., min_items=5, max_items=15, description="5-15 commonly used metrics"
    )
    regulatory_considerations: List[RegulatoryRequirement] = Field(
        default_factory=list, description="Relevant regulatory requirements"
    )
    competitive_landscape: str = Field(
        ..., min_length=50, description="Overview of competitive landscape"
    )
    market_maturity: Literal['emerging', 'growing', 'mature', 'declining'] = Field(
        ..., description="Market maturity level"
    )


class DashboardPattern(BaseModel):
    """Common dashboard design pattern."""
    pattern_name: str = Field(..., description="Pattern name (e.g., 'Executive Summary')")
    description: str = Field(..., description="When and how this pattern is used")
    typical_widgets: List[str] = Field(..., min_items=3, description="Common widget types")
    layout_style: Literal['dense', 'balanced', 'spacious'] = Field(..., description="Typical layout")
    target_audience: str = Field(..., description="Who typically uses this pattern")


class VisualizationRecommendation(BaseModel):
    """Recommended visualization for a specific use case."""
    use_case: str = Field(..., description="What needs to be shown")
    recommended_widget_type: str = Field(..., description="Best widget type")
    alternative_types: List[str] = Field(default_factory=list, description="Alternative widget types")
    rationale: str = Field(..., description="Why this visualization works best")


class CompetitiveIntelligence(BaseModel):
    """Competitive analysis and best practices."""
    common_dashboard_patterns: List[DashboardPattern] = Field(
        ..., min_items=3, max_items=6, description="3-6 common dashboard patterns"
    )
    popular_widget_types: List[str] = Field(
        ..., min_items=5, max_items=12, description="Most commonly used widget types"
    )
    visualization_recommendations: List[VisualizationRecommendation] = Field(
        ..., min_items=4, description="Visualization best practices"
    )
    layout_best_practices: List[str] = Field(
        ..., min_items=3, max_items=5, description="Layout design principles"
    )
    color_scheme_trends: Optional[Dict[str, str]] = Field(
        None, description="Common color schemes and their usage"
    )


class DataSource(BaseModel):
    """Required or recommended data source."""
    source_name: str = Field(..., description="Data source name")
    source_type: Literal['claims', 'clinical', 'pharmacy', 'lab', 'member', 'financial', 'external'] = Field(
        ..., description="Type of data source"
    )
    availability: Literal['typically_available', 'may_require_integration', 'client_specific'] = Field(
        ..., description="How commonly available this data is"
    )
    required_for_metrics: List[str] = Field(
        default_factory=list, description="Which metrics need this data source"
    )


class CalculationComplexity(BaseModel):
    """Assessment of metric calculation complexity."""
    metric_name: str = Field(..., description="Metric name")
    complexity_level: Literal['simple', 'moderate', 'complex', 'very_complex'] = Field(
        ..., description="Calculation complexity"
    )
    factors: List[str] = Field(..., description="What makes this complex/simple")
    estimated_development_time: Optional[str] = Field(
        None, description="Rough time estimate (e.g., '1-2 days')"
    )


class DataRequirementsAnalysis(BaseModel):
    """Analysis of data requirements for the value proposition."""
    required_data_sources: List[DataSource] = Field(
        ..., min_items=2, description="Required data sources"
    )
    suggested_metrics: List[MetricSuggestion] = Field(
        ..., min_items=8, max_items=20, description="8-20 suggested metrics"
    )
    calculation_complexity: List[CalculationComplexity] = Field(
        default_factory=list, description="Complexity assessment for key metrics"
    )
    data_integration_notes: Optional[str] = Field(
        None, description="Notes about data integration challenges"
    )
    overall_feasibility: Literal['high', 'medium', 'low'] = Field(
        ..., description="Overall data feasibility"
    )


class StakeholderQuestion(BaseModel):
    """Key question a stakeholder needs answered."""
    question: str = Field(..., description="The question")
    priority: Literal['critical', 'important', 'nice-to-have'] = Field(
        ..., description="Question priority"
    )
    suggested_widgets: List[str] = Field(
        ..., min_items=1, description="Widget types that answer this question"
    )


class AudiencePersona(BaseModel):
    """Stakeholder persona and information needs."""
    role: str = Field(..., description="Stakeholder role (e.g., 'CFO', 'Clinical Director')")
    audience_type: str = Field(
        ..., description="Audience category (e.g., 'Health Plan', 'Employer')"
    )
    key_questions: List[StakeholderQuestion] = Field(
        ..., min_items=3, max_items=8, description="3-8 key questions they need answered"
    )
    preferred_visualizations: List[str] = Field(
        ..., min_items=3, description="Preferred visualization types"
    )
    information_depth: Literal['summary', 'balanced', 'detailed'] = Field(
        ..., description="Preferred level of detail"
    )
    decision_making_focus: str = Field(
        ..., description="What they're trying to decide or understand"
    )
    typical_dashboard_categories: List[str] = Field(
        ..., description="Dashboard categories they typically need"
    )


class UseCaseBreakdown(BaseModel):
    """Breakdown of value proposition into measurable outcomes."""
    primary_use_case: str = Field(..., description="Main use case from value proposition")
    measurable_outcomes: List[str] = Field(
        ..., min_items=3, description="Specific measurable outcomes"
    )
    success_metrics: List[str] = Field(
        ..., min_items=3, description="Metrics that define success"
    )
    stakeholder_benefits: Dict[str, List[str]] = Field(
        ..., description="Benefits by stakeholder type"
    )


class TemplateGenerationGuidance(BaseModel):
    """Guidance for template generation based on research."""
    recommended_template_count: int = Field(ge=5, le=10, description="Recommended number of templates")
    recommended_categories: List[str] = Field(
        ..., min_items=3, description="Template categories to generate"
    )
    recommended_audiences: List[str] = Field(
        ..., min_items=2, description="Target audiences to cover"
    )
    key_focus_areas: List[str] = Field(
        ..., min_items=3, max_items=7, description="Main focus areas for templates"
    )
    widget_priorities: Dict[str, List[str]] = Field(
        ..., description="Priority widgets by category (e.g., {'roi-focused': ['kpi-card', ...]})"
    )
    color_scheme_recommendations: Dict[str, str] = Field(
        default_factory=dict, description="Suggested color schemes by category"
    )
    layout_recommendations: Dict[str, str] = Field(
        default_factory=dict, description="Layout suggestions by audience"
    )


class ResearchMetadata(BaseModel):
    """Metadata about the research process."""
    research_depth: Literal['quick', 'standard', 'deep'] = Field(
        ..., description="Level of research performed"
    )
    research_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When research was performed"
    )
    research_duration_seconds: Optional[float] = Field(
        None, description="Time taken for research"
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence in research results (0-1)"
    )
    sources_consulted: List[str] = Field(
        default_factory=list, description="Knowledge sources used"
    )
    model_provider: Optional[str] = Field(None, description="LLM provider used")
    model_name: Optional[str] = Field(None, description="LLM model used")
    tokens_used: Optional[int] = Field(None, description="Total tokens consumed")


class ResearchResult(BaseModel):
    """Complete research output for template generation.

    This is the top-level model returned by the research agent.
    """
    # Summary
    value_proposition_summary: str = Field(
        ..., min_length=50, max_length=500,
        description="Concise summary of the client's value proposition"
    )

    # Research sections
    industry_insights: IndustryInsights = Field(..., description="Industry context and trends")
    competitive_intelligence: CompetitiveIntelligence = Field(
        ..., description="Competitive analysis and best practices"
    )
    data_requirements: DataRequirementsAnalysis = Field(
        ..., description="Data requirements and feasibility"
    )
    audience_personas: List[AudiencePersona] = Field(
        ..., min_items=2, max_items=5, description="2-5 stakeholder personas"
    )
    use_case_breakdown: UseCaseBreakdown = Field(
        ..., description="Value proposition broken into measurable outcomes"
    )

    # Template generation guidance
    template_guidance: TemplateGenerationGuidance = Field(
        ..., description="Specific guidance for template generation"
    )

    # Metadata
    metadata: ResearchMetadata = Field(..., description="Research metadata")

    # Optional fields
    additional_notes: Optional[str] = Field(
        None, description="Any additional insights or considerations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "value_proposition_summary": "Diabetes management program delivering 24-month ROI through HbA1c reduction and reduced ER visits",
                "industry_insights": {
                    "key_trends": [
                        {
                            "trend": "Value-based care shifting focus to outcomes",
                            "relevance": "high",
                            "source": "industry_knowledge"
                        }
                    ],
                    "common_metrics": [
                        {
                            "name": "HbA1c Reduction",
                            "description": "Average reduction in HbA1c levels",
                            "formula": "AVG(baseline_hba1c - current_hba1c)",
                            "data_type": "number",
                            "typical_range": "0.5-2.0%",
                            "importance": "critical",
                            "standard_benchmarks": ["HEDIS: 0.5%+ reduction"]
                        }
                    ],
                    "regulatory_considerations": [],
                    "competitive_landscape": "Diabetes management is a mature market",
                    "market_maturity": "mature"
                },
                "competitive_intelligence": {
                    "common_dashboard_patterns": [],
                    "popular_widget_types": ["kpi-card", "line-chart", "waterfall-chart"],
                    "visualization_recommendations": [],
                    "layout_best_practices": []
                },
                "data_requirements": {
                    "required_data_sources": [],
                    "suggested_metrics": [],
                    "overall_feasibility": "high"
                },
                "audience_personas": [],
                "use_case_breakdown": {
                    "primary_use_case": "Diabetes ROI demonstration",
                    "measurable_outcomes": ["Reduced HbA1c", "Lower costs"],
                    "success_metrics": ["24-month ROI", "Cost savings"],
                    "stakeholder_benefits": {}
                },
                "template_guidance": {
                    "recommended_template_count": 7,
                    "recommended_categories": ["roi-focused", "clinical-outcomes"],
                    "recommended_audiences": ["Health Plan", "Employer"],
                    "key_focus_areas": ["Financial ROI", "Clinical outcomes"],
                    "widget_priorities": {}
                },
                "metadata": {
                    "research_depth": "standard",
                    "research_timestamp": "2025-01-15T12:00:00Z",
                    "confidence_score": 0.85,
                    "sources_consulted": ["healthcare_knowledge_base"]
                }
            }
        }


# Validation helper functions

def validate_research_completeness(result: ResearchResult) -> Dict[str, Any]:
    """Validate research result has sufficient information.

    Returns validation report with errors and warnings.
    """
    errors = []
    warnings = []

    # Check minimum requirements
    if len(result.industry_insights.key_trends) < 3:
        warnings.append("Industry insights has fewer than 3 key trends")

    if len(result.industry_insights.common_metrics) < 5:
        errors.append("Industry insights must have at least 5 common metrics")

    if len(result.competitive_intelligence.common_dashboard_patterns) < 3:
        warnings.append("Competitive intelligence has fewer than 3 dashboard patterns")

    if len(result.data_requirements.required_data_sources) < 2:
        errors.append("Data requirements must identify at least 2 data sources")

    if len(result.data_requirements.suggested_metrics) < 8:
        errors.append("Data requirements must suggest at least 8 metrics")

    if len(result.audience_personas) < 2:
        errors.append("Must have at least 2 audience personas")

    # Check template guidance
    if result.template_guidance.recommended_template_count < 5:
        errors.append("Template guidance must recommend at least 5 templates")

    if len(result.template_guidance.recommended_categories) < 3:
        errors.append("Template guidance must recommend at least 3 categories")

    # Check confidence score
    if result.metadata.confidence_score < 0.6:
        warnings.append(f"Low confidence score: {result.metadata.confidence_score}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_metric_suggestions(metrics: List[MetricSuggestion]) -> List[str]:
    """Validate metric suggestions have required information.

    Returns list of validation errors.
    """
    errors = []

    for i, metric in enumerate(metrics):
        # Check that critical/important metrics have formulas
        if metric.importance in ['critical', 'important'] and not metric.formula:
            errors.append(
                f"Metric '{metric.name}' (#{i}) marked as {metric.importance} "
                f"but missing formula/calculation logic"
            )

        # Check description quality
        if len(metric.description) < 10:
            errors.append(f"Metric '{metric.name}' (#{i}) has insufficient description")

    return errors


def validate_audience_personas(personas: List[AudiencePersona]) -> List[str]:
    """Validate audience personas have sufficient detail.

    Returns list of validation errors.
    """
    errors = []

    for persona in personas:
        # Check question count
        if len(persona.key_questions) < 3:
            errors.append(
                f"Persona '{persona.role}' has fewer than 3 key questions "
                f"(found {len(persona.key_questions)})"
            )

        # Check that critical questions have suggested widgets
        critical_questions = [q for q in persona.key_questions if q.priority == 'critical']
        for question in critical_questions:
            if not question.suggested_widgets:
                errors.append(
                    f"Critical question in persona '{persona.role}' has no suggested widgets: "
                    f"'{question.question}'"
                )

    return errors
