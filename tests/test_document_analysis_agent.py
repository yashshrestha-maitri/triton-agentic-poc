"""Unit tests for DocumentAnalysis Agent."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from core.models.value_proposition_models import (
    DocumentAnalysisResult,
    ExtractedValueProposition,
    ExtractedClinicalOutcome,
    ExtractedFinancialMetric,
    validate_document_analysis_result,
)
from agents.document_analysis_agent import (
    DocumentAnalysisAgentTemplate,
    create_document_analysis_agent,
    create_document_analysis_agent_with_retry,
    extract_json_from_response,
)


# Test JSON Extraction
def test_extract_json_from_markdown():
    """Test JSON extraction from markdown."""
    markdown = '```json\n{"documents_analyzed": 1}\n```'
    result = extract_json_from_response(markdown)
    assert result == '{"documents_analyzed": 1}'


# Test Models
def test_document_analysis_result_minimal():
    """Test creating minimal valid DocumentAnalysisResult."""
    result = DocumentAnalysisResult(
        documents_analyzed=1,
        document_names=["test.pdf"],
        extracted_value_propositions=[
            ExtractedValueProposition(
                name="Test Value Proposition",
                description="Test description that is long enough",
                source_document="test.pdf",
                confidence="high"
            )
        ],
        overall_confidence=0.85
    )
    assert result.documents_analyzed == 1
    assert len(result.extracted_value_propositions) == 1


def test_validate_document_analysis_result():
    """Test validation function."""
    result = DocumentAnalysisResult(
        documents_analyzed=2,
        document_names=["doc1.pdf", "doc2.pdf"],
        extracted_value_propositions=[
            ExtractedValueProposition(
                name="Value Prop 1",
                description="Description that meets requirements",
                source_document="doc1.pdf",
                confidence="high"
            )
        ],
        financial_metrics=[
            ExtractedFinancialMetric(
                metric_name="ROI",
                value="340%",
                source_document="doc1.pdf"
            )
        ],
        overall_confidence=0.88
    )

    validation = validate_document_analysis_result(result)
    assert validation['valid'] is True


# Test Agent Template
def test_document_analysis_agent_template():
    """Test DocumentAnalysisAgentTemplate creation."""
    template = DocumentAnalysisAgentTemplate()

    config = template.get_agent_config()
    assert 'markdown' in config
    assert config['markdown'] is False


def test_document_analysis_agent_template_tools():
    """Test tools are properly configured."""
    template = DocumentAnalysisAgentTemplate()
    tools = template.get_tools()
    assert len(tools) == 1  # S3 document reader


def test_document_analysis_agent_template_instructions():
    """Test instructions loading."""
    template = DocumentAnalysisAgentTemplate()
    instructions = template.get_instructions()
    assert len(instructions) > 100
    assert "document" in instructions.lower()


# Test Agent Factory Functions
def test_create_document_analysis_agent_signature():
    """Test factory function signature."""
    import inspect
    sig = inspect.signature(create_document_analysis_agent)
    params = sig.parameters
    assert 'name' in params
    assert 'model' in params


def test_create_document_analysis_agent_with_retry_signature():
    """Test retry factory function signature."""
    import inspect
    sig = inspect.signature(create_document_analysis_agent_with_retry)
    params = sig.parameters
    assert 'max_retries' in params
    assert params['max_retries'].default == 3


# Integration Tests (require LLM and S3)
@pytest.mark.integration
@pytest.mark.skip(reason="Requires LLM model and S3 - run separately")
def test_document_analysis_agent_integration():
    """Integration test with real LLM and S3."""
    from core.models.model_factory import get_default_model

    model = get_default_model()
    agent = create_document_analysis_agent_with_retry(
        name="TestDocAnalysisAgent",
        model=model
    )

    message = """
    Analyze the following documents:
    - s3://triton-test/client123/roi_sheet.pdf
    - s3://triton-test/client123/case_study.pdf

    Extract value propositions, clinical outcomes, and financial metrics.
    """

    result = agent.run(message)
    assert isinstance(result, DocumentAnalysisResult)
    assert result.documents_analyzed >= 1
    assert len(result.extracted_value_propositions) >= 1
