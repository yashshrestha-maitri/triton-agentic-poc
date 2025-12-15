"""Unit tests for Research Agent."""

import pytest
import json
from datetime import datetime
from pydantic import ValidationError

from core.models.research_models import (
    ResearchResult,
    IndustryInsights,
    CompetitiveIntelligence,
    DataRequirementsAnalysis,
    AudiencePersona,
    UseCaseBreakdown,
    TemplateGenerationGuidance,
    ResearchMetadata,
    IndustryTrend,
    MetricSuggestion,
    RegulatoryRequirement,
    DashboardPattern,
    VisualizationRecommendation,
    DataSource,
    CalculationComplexity,
    StakeholderQuestion,
    validate_research_completeness,
    validate_metric_suggestions,
    validate_audience_personas,
)
from agents.template_research_agent import (
    ResearchAgentTemplate,
    create_research_agent,
    create_research_agent_with_retry,
    extract_json_from_response,
)


# ============================================================================
# Test JSON Extraction
# ============================================================================

def test_extract_json_from_markdown():
    """Test JSON extraction from markdown code blocks."""
    markdown_response = """
Here is the research:
```json
{"key": "value", "number": 42}
```
That's the result.
"""
    result = extract_json_from_response(markdown_response)
    assert result == '{"key": "value", "number": 42}'


def test_extract_json_from_raw_text():
    """Test JSON extraction from raw text."""
    text_response = """
Some preamble text
{"key": "value", "number": 42}
Some trailing text
"""
    result = extract_json_from_response(text_response)
    assert result == '{"key": "value", "number": 42}'


def test_extract_json_no_json_found():
    """Test JSON extraction failure when no JSON present."""
    text_response = "This is just text with no JSON"
    with pytest.raises(ValueError, match="No JSON object found"):
        extract_json_from_response(text_response)


# ============================================================================
# Test Pydantic Models
# ============================================================================

def test_industry_trend_creation():
    """Test IndustryTrend model creation."""
    trend = IndustryTrend(
        trend="Value-based care models are becoming dominant",
        relevance="high",
        source="industry_knowledge"
    )
    assert trend.trend == "Value-based care models are becoming dominant"
    assert trend.relevance == "high"


def test_metric_suggestion_validation():
    """Test MetricSuggestion model validation."""
    metric = MetricSuggestion(
        name="24-Month ROI",
        description="Return on investment over 24 months",
        formula="SUM(avoided_costs) / SUM(program_costs)",
        data_type="ratio",
        typical_range="1.0-5.0",
        importance="critical",
        standard_benchmarks=["Industry average: 2.5x"]
    )
    assert metric.name == "24-Month ROI"
    assert metric.data_type == "ratio"
    assert metric.importance == "critical"


def test_metric_suggestion_invalid_importance():
    """Test MetricSuggestion with invalid importance level."""
    with pytest.raises(ValidationError):
        MetricSuggestion(
            name="Test Metric",
            description="Test description",
            data_type="count",
            importance="super-critical",  # Invalid
            formula="COUNT(*)"
        )


def test_audience_persona_creation():
    """Test AudiencePersona model creation."""
    persona = AudiencePersona(
        role="CFO",
        audience_type="Health Plan",
        key_questions=[
            StakeholderQuestion(
                question="What is the 24-month ROI?",
                priority="critical",
                suggested_widgets=["kpi-card", "line-chart"]
            )
        ],
        preferred_visualizations=["kpi-card", "waterfall-chart"],
        information_depth="summary",
        decision_making_focus="Contract renewal",
        typical_dashboard_categories=["roi-focused"]
    )
    assert persona.role == "CFO"
    assert len(persona.key_questions) == 1
    assert persona.key_questions[0].priority == "critical"


def test_research_result_minimal():
    """Test ResearchResult with minimal valid data."""
    result = ResearchResult(
        value_proposition_summary="Diabetes management program delivering ROI through HbA1c reduction",
        industry_insights=IndustryInsights(
            key_trends=[
                IndustryTrend(trend="Trend 1", relevance="high", source="industry_knowledge"),
                IndustryTrend(trend="Trend 2", relevance="medium", source="industry_knowledge"),
                IndustryTrend(trend="Trend 3", relevance="low", source="industry_knowledge"),
            ],
            common_metrics=[
                MetricSuggestion(
                    name=f"Metric {i}",
                    description=f"Description {i}",
                    data_type="count",
                    importance="important",
                    formula=f"COUNT(*)"
                ) for i in range(5)
            ],
            regulatory_considerations=[],
            competitive_landscape="Mature market with multiple players",
            market_maturity="mature"
        ),
        competitive_intelligence=CompetitiveIntelligence(
            common_dashboard_patterns=[
                DashboardPattern(
                    pattern_name="Executive Summary",
                    description="High-level overview for C-suite",
                    typical_widgets=["kpi-card", "line-chart", "waterfall-chart"],
                    layout_style="balanced",
                    target_audience="C-suite"
                ),
                DashboardPattern(
                    pattern_name="Clinical Deep Dive",
                    description="Detailed clinical metrics",
                    typical_widgets=["line-chart", "gauge-chart", "data-table"],
                    layout_style="spacious",
                    target_audience="Clinical Directors"
                ),
                DashboardPattern(
                    pattern_name="Financial Analysis",
                    description="Cost and ROI breakdown",
                    typical_widgets=["waterfall-chart", "bar-chart", "kpi-card"],
                    layout_style="balanced",
                    target_audience="Finance"
                )
            ],
            popular_widget_types=["kpi-card", "line-chart", "waterfall-chart", "bar-chart", "gauge-chart"],
            visualization_recommendations=[
                VisualizationRecommendation(
                    use_case="Show ROI over time",
                    recommended_widget_type="line-chart",
                    alternative_types=["area-chart"],
                    rationale="Line charts show progression clearly"
                ),
                VisualizationRecommendation(
                    use_case="Break down savings",
                    recommended_widget_type="waterfall-chart",
                    alternative_types=["stacked-bar-chart"],
                    rationale="Waterfall shows sequential impact"
                ),
                VisualizationRecommendation(
                    use_case="Show control rate",
                    recommended_widget_type="gauge-chart",
                    alternative_types=["kpi-card"],
                    rationale="Gauges show progress to goal"
                ),
                VisualizationRecommendation(
                    use_case="Compare categories",
                    recommended_widget_type="bar-chart",
                    alternative_types=["pie-chart"],
                    rationale="Bars facilitate comparison"
                )
            ],
            layout_best_practices=[
                "Place most critical metric in top-left",
                "Use 12-column span for tables",
                "Group related metrics together"
            ]
        ),
        data_requirements=DataRequirementsAnalysis(
            required_data_sources=[
                DataSource(
                    source_name="Medical Claims",
                    source_type="claims",
                    availability="typically_available",
                    required_for_metrics=["total_savings", "hospitalizations"]
                ),
                DataSource(
                    source_name="Clinical Data",
                    source_type="clinical",
                    availability="may_require_integration",
                    required_for_metrics=["hba1c_reduction"]
                )
            ],
            suggested_metrics=[
                MetricSuggestion(
                    name=f"Data Metric {i}",
                    description=f"Description {i}",
                    data_type="count",
                    importance="important",
                    formula=f"COUNT(*)"
                ) for i in range(8)
            ],
            overall_feasibility="high"
        ),
        audience_personas=[
            AudiencePersona(
                role="CFO",
                audience_type="Health Plan",
                key_questions=[
                    StakeholderQuestion(
                        question=f"Question {i}",
                        priority="important",
                        suggested_widgets=["kpi-card"]
                    ) for i in range(3)
                ],
                preferred_visualizations=["kpi-card", "waterfall-chart", "line-chart"],
                information_depth="summary",
                decision_making_focus="Budget allocation",
                typical_dashboard_categories=["roi-focused"]
            ),
            AudiencePersona(
                role="CMO",
                audience_type="Health Plan",
                key_questions=[
                    StakeholderQuestion(
                        question=f"Clinical Question {i}",
                        priority="critical",
                        suggested_widgets=["line-chart"]
                    ) for i in range(3)
                ],
                preferred_visualizations=["line-chart", "gauge-chart", "data-table"],
                information_depth="detailed",
                decision_making_focus="Quality improvement",
                typical_dashboard_categories=["clinical-outcomes"]
            )
        ],
        use_case_breakdown=UseCaseBreakdown(
            primary_use_case="Demonstrate diabetes management ROI",
            measurable_outcomes=["HbA1c reduction", "Cost savings", "Reduced hospitalizations"],
            success_metrics=["24-month ROI", "HbA1c improvement", "Hospital admission rate"],
            stakeholder_benefits={
                "Health Plan": ["Reduced costs", "Improved Star Ratings", "Better outcomes"]
            }
        ),
        template_guidance=TemplateGenerationGuidance(
            recommended_template_count=7,
            recommended_categories=["roi-focused", "clinical-outcomes", "operational-efficiency"],
            recommended_audiences=["Health Plan", "Employer"],
            key_focus_areas=["24-month ROI", "HbA1c improvement", "Cost savings"],
            widget_priorities={
                "roi-focused": ["kpi-card", "waterfall-chart", "line-chart"],
                "clinical-outcomes": ["kpi-card", "line-chart", "gauge-chart"]
            }
        ),
        metadata=ResearchMetadata(
            research_depth="standard",
            confidence_score=0.85,
            sources_consulted=["healthcare_knowledge_base"]
        )
    )

    assert result.value_proposition_summary is not None
    assert len(result.industry_insights.key_trends) >= 3
    assert len(result.audience_personas) >= 2


# ============================================================================
# Test Validation Functions
# ============================================================================

def test_validate_research_completeness_valid():
    """Test validation of complete research result."""
    # Use the minimal result from previous test
    result = ResearchResult(
        value_proposition_summary="Test summary for validation",
        industry_insights=IndustryInsights(
            key_trends=[IndustryTrend(trend=f"Trend {i}", relevance="high", source="test") for i in range(3)],
            common_metrics=[
                MetricSuggestion(name=f"M{i}", description="desc", data_type="count", importance="important", formula="COUNT(*)")
                for i in range(5)
            ],
            regulatory_considerations=[],
            competitive_landscape="Test landscape",
            market_maturity="mature"
        ),
        competitive_intelligence=CompetitiveIntelligence(
            common_dashboard_patterns=[
                DashboardPattern(
                    pattern_name=f"Pattern {i}",
                    description="desc",
                    typical_widgets=["kpi-card"],
                    layout_style="balanced",
                    target_audience="Test"
                ) for i in range(3)
            ],
            popular_widget_types=["kpi-card"],
            visualization_recommendations=[
                VisualizationRecommendation(
                    use_case="test",
                    recommended_widget_type="kpi-card",
                    rationale="test"
                ) for i in range(4)
            ],
            layout_best_practices=["test"]
        ),
        data_requirements=DataRequirementsAnalysis(
            required_data_sources=[
                DataSource(source_name=f"Source {i}", source_type="claims", availability="typically_available")
                for i in range(2)
            ],
            suggested_metrics=[
                MetricSuggestion(name=f"M{i}", description="desc", data_type="count", importance="important", formula="COUNT(*)")
                for i in range(8)
            ],
            overall_feasibility="high"
        ),
        audience_personas=[
            AudiencePersona(
                role=f"Role {i}",
                audience_type="Test",
                key_questions=[
                    StakeholderQuestion(question="q", priority="important", suggested_widgets=["kpi-card"])
                    for _ in range(3)
                ],
                preferred_visualizations=["kpi-card"],
                information_depth="summary",
                decision_making_focus="test",
                typical_dashboard_categories=["roi-focused"]
            ) for i in range(2)
        ],
        use_case_breakdown=UseCaseBreakdown(
            primary_use_case="test",
            measurable_outcomes=["o1", "o2", "o3"],
            success_metrics=["m1", "m2", "m3"],
            stakeholder_benefits={"Test": ["b1"]}
        ),
        template_guidance=TemplateGenerationGuidance(
            recommended_template_count=7,
            recommended_categories=["roi-focused", "clinical-outcomes", "operational-efficiency"],
            recommended_audiences=["Health Plan", "Employer"],
            key_focus_areas=["focus1", "focus2", "focus3"],
            widget_priorities={}
        ),
        metadata=ResearchMetadata(
            research_depth="standard",
            confidence_score=0.85,
            sources_consulted=["test"]
        )
    )

    validation = validate_research_completeness(result)
    assert validation['valid'] is True
    assert len(validation['errors']) == 0


def test_validate_metric_suggestions():
    """Test metric suggestion validation."""
    metrics = [
        MetricSuggestion(
            name="Critical Metric",
            description="Important metric",
            formula="SUM(value)",
            data_type="count",
            importance="critical"
        ),
        MetricSuggestion(
            name="No Formula Metric",
            description="short",  # Too short
            data_type="count",
            importance="critical"  # Critical but no formula
        )
    ]

    errors = validate_metric_suggestions(metrics)
    assert len(errors) >= 1  # Should have at least description length error


def test_validate_audience_personas():
    """Test audience persona validation."""
    personas = [
        AudiencePersona(
            role="CFO",
            audience_type="Health Plan",
            key_questions=[
                StakeholderQuestion(
                    question="What is ROI?",
                    priority="critical",
                    suggested_widgets=[]  # Critical question with no widgets
                )
            ],
            preferred_visualizations=["kpi-card"],
            information_depth="summary",
            decision_making_focus="Budget",
            typical_dashboard_categories=["roi-focused"]
        )
    ]

    errors = validate_audience_personas(personas)
    assert len(errors) >= 1  # Should have error about missing widgets for critical question


# ============================================================================
# Test Agent Creation
# ============================================================================

def test_research_agent_template_creation():
    """Test ResearchAgentTemplate instantiation."""
    template = ResearchAgentTemplate(research_depth="standard")
    assert template.research_depth == "standard"

    config = template.get_agent_config()
    assert 'markdown' in config
    assert config['markdown'] is False


def test_research_agent_template_invalid_depth():
    """Test ResearchAgentTemplate with invalid depth."""
    template = ResearchAgentTemplate(research_depth="invalid")
    assert template.research_depth == "standard"  # Should default to standard


def test_research_agent_template_instructions():
    """Test instructions loading."""
    template = ResearchAgentTemplate(research_depth="standard")
    instructions = template.get_instructions()
    assert len(instructions) > 100  # Should be substantial
    assert "RESEARCH DEPTH: STANDARD" in instructions


def test_research_agent_template_tools():
    """Test tools list (should be empty in Phase 1)."""
    template = ResearchAgentTemplate()
    tools = template.get_tools()
    assert tools == []


def test_research_agent_description():
    """Test agent description."""
    template = ResearchAgentTemplate(research_depth="deep")
    description = template.get_description()
    assert "deep" in description.lower()
    assert "research" in description.lower()


# ============================================================================
# Test Agent Factory Functions (without model)
# ============================================================================

def test_create_research_agent_signature():
    """Test create_research_agent function signature (without actual model)."""
    # This test just verifies the function exists and has expected signature
    import inspect
    sig = inspect.signature(create_research_agent)
    params = sig.parameters
    assert 'name' in params
    assert 'model' in params
    assert 'research_depth' in params
    assert params['name'].default == "ResearchAgent"
    assert params['research_depth'].default == "standard"


def test_create_research_agent_with_retry_signature():
    """Test create_research_agent_with_retry function signature."""
    import inspect
    sig = inspect.signature(create_research_agent_with_retry)
    params = sig.parameters
    assert 'name' in params
    assert 'model' in params
    assert 'max_retries' in params
    assert 'research_depth' in params
    assert params['max_retries'].default == 3


# ============================================================================
# Integration Test Markers (require LLM model)
# ============================================================================

@pytest.mark.integration
@pytest.mark.skip(reason="Requires LLM model - run separately with model configured")
def test_research_agent_integration():
    """Integration test with real LLM (skipped by default)."""
    from core.models.model_factory import get_default_model

    model = get_default_model()
    agent = create_research_agent_with_retry(
        name="TestResearchAgent",
        model=model,
        research_depth="quick"
    )

    value_prop = {
        "client_name": "Test Client",
        "industry": "Diabetes Management",
        "solution": "Reduce HbA1c and healthcare costs through digital coaching"
    }

    message = f"Research this value proposition:\n\n{json.dumps(value_prop, indent=2)}"

    result = agent.run(message)
    assert isinstance(result, ResearchResult)
    assert result.metadata.confidence_score > 0.5
