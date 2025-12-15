"""Unit tests for WebSearch Agent."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from core.models.value_proposition_models import (
    WebSearchResult,
    CompanyOverview,
    ValuePropositionEvidence,
    ClinicalOutcomeEvidence,
    ROIFramework,
    CompetitivePositioning,
    validate_web_search_result,
)
from agents.web_search_agent import (
    WebSearchAgentTemplate,
    create_web_search_agent,
    create_web_search_agent_with_retry,
    extract_json_from_response,
)


# Test JSON Extraction
def test_extract_json_from_markdown():
    """Test JSON extraction from markdown."""
    markdown = '```json\n{"key": "value"}\n```'
    result = extract_json_from_response(markdown)
    assert result == '{"key": "value"}'


def test_extract_json_from_raw():
    """Test JSON extraction from raw text."""
    text = 'Some text {"key": "value"} more text'
    result = extract_json_from_response(text)
    assert result == '{"key": "value"}'


# Test Models
def test_web_search_result_minimal():
    """Test creating minimal valid WebSearchResult."""
    result = WebSearchResult(
        searches_performed=15,
        queries=["query1", "query2", "query3", "query4", "query5"],
        company_overview=CompanyOverview(
            name="Test Company",
            description="Test company description that is long enough to pass validation",
            target_markets=["Health Plans"]
        ),
        value_propositions=[
            ValuePropositionEvidence(
                name="Test Value Prop",
                description="Test description that is long enough",
                evidence_type="explicit",
                confidence="high"
            )
        ],
        target_audiences=["Health Plan"],
        sources=["https://example.com"],
        research_mode="autonomous",
        confidence_score=0.85
    )
    assert result.searches_performed == 15
    assert len(result.value_propositions) == 1


def test_validate_web_search_result():
    """Test validation function."""
    result = WebSearchResult(
        searches_performed=20,
        queries=["q" + str(i) for i in range(20)],
        company_overview=CompanyOverview(
            name="Company",
            description="Description that meets minimum length requirements",
            target_markets=["Health Plans"]
        ),
        value_propositions=[
            ValuePropositionEvidence(
                name="Value Prop",
                description="Description that is long enough",
                evidence_type="explicit",
                confidence="high"
            )
        ],
        target_audiences=["Health Plan"],
        sources=["https://example.com"],
        research_mode="autonomous",
        confidence_score=0.9
    )

    validation = validate_web_search_result(result)
    assert validation['valid'] is True


# Test Agent Template
def test_web_search_agent_template_autonomous():
    """Test WebSearchAgentTemplate creation in autonomous mode."""
    template = WebSearchAgentTemplate(research_mode="autonomous")
    assert template.research_mode == "autonomous"

    config = template.get_agent_config()
    assert 'markdown' in config
    assert config['markdown'] is False


def test_web_search_agent_template_manual():
    """Test WebSearchAgentTemplate creation in manual mode."""
    template = WebSearchAgentTemplate(research_mode="manual")
    assert template.research_mode == "manual"


def test_web_search_agent_template_tools():
    """Test tools are properly configured."""
    template = WebSearchAgentTemplate()
    tools = template.get_tools()
    assert len(tools) == 2  # Google search + web scraper


def test_web_search_agent_template_instructions():
    """Test instructions loading."""
    template = WebSearchAgentTemplate()
    instructions = template.get_instructions()
    assert len(instructions) > 100
    assert "healthcare" in instructions.lower()


# Test Agent Factory Functions
def test_create_web_search_agent_signature():
    """Test factory function signature."""
    import inspect
    sig = inspect.signature(create_web_search_agent)
    params = sig.parameters
    assert 'name' in params
    assert 'model' in params
    assert 'research_mode' in params
    assert params['research_mode'].default == "autonomous"


def test_create_web_search_agent_with_retry_signature():
    """Test retry factory function signature."""
    import inspect
    sig = inspect.signature(create_web_search_agent_with_retry)
    params = sig.parameters
    assert 'max_retries' in params
    assert params['max_retries'].default == 3


# Integration Tests (require LLM)
@pytest.mark.integration
@pytest.mark.skip(reason="Requires LLM model - run separately")
def test_web_search_agent_integration():
    """Integration test with real LLM."""
    from core.models.model_factory import get_default_model

    model = get_default_model()
    agent = create_web_search_agent_with_retry(
        name="TestWebSearchAgent",
        model=model,
        research_mode="manual"
    )

    message = """
    Research Livongo Health company.
    Focus on their diabetes management solution and any ROI claims.
    """

    result = agent.run(message)
    assert isinstance(result, WebSearchResult)
    assert result.company_overview.name
    assert len(result.value_propositions) >= 1
