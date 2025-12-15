"""ROI Classification Agent for determining appropriate ROI model type.

This agent analyzes research data (web search results + document analysis) to classify
the appropriate ROI model type (B1-B13) based on the vendor's value proposition,
clinical focus, and data requirements.
"""

from typing import Any, Dict, List, Optional
import json
import re
from pydantic import BaseModel, ValidationError, Field

from agents.base.base_agent import BaseAgentTemplate, MareAgent
from core.models.roi_models import ModelTypeCode
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# ROI CLASSIFICATION RESULT MODEL
# ============================================================================

class ROIClassificationReasoning(BaseModel):
    """Reasoning for ROI model classification"""
    primary_factors: List[str] = Field(..., min_items=1, description="Primary factors supporting this classification")
    clinical_domain_match: str = Field(..., min_length=20, description="How clinical domain matches model type")
    data_requirements_match: str = Field(..., min_length=20, description="How data requirements match model type")
    intervention_type_match: str = Field(..., min_length=20, description="How intervention type matches model type")
    confidence_level: str = Field(..., pattern="^(high|medium|low)$", description="Confidence in classification")


class AlternativeModel(BaseModel):
    """Alternative ROI model suggestion"""
    model_type_code: ModelTypeCode = Field(..., description="Alternative model type")
    rationale: str = Field(..., min_length=20, description="Why this could also be appropriate")
    applicability_score: float = Field(..., ge=0, le=1, description="Applicability score (0-1)")


class ROIClassificationResult(BaseModel):
    """Result of ROI model type classification"""
    recommended_model_type: ModelTypeCode = Field(..., description="Recommended ROI model type (B1-B13)")
    model_type_name: str = Field(..., description="Human-readable model type name")
    reasoning: ROIClassificationReasoning = Field(..., description="Detailed reasoning for classification")
    alternative_models: List[AlternativeModel] = Field(default_factory=list, description="Alternative model types to consider")
    key_value_drivers: List[str] = Field(..., min_items=1, description="Key value drivers from research")
    clinical_focus_areas: List[str] = Field(..., min_items=1, description="Clinical focus areas")
    estimated_complexity: str = Field(..., pattern="^(low|medium|high)$", description="Implementation complexity")


def extract_json_from_response(text: str) -> str:
    """Extract JSON from LLM response that may contain markdown or extra text."""
    text = str(text)

    # Try markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    if matches:
        logger.debug("Extracted JSON from markdown code block")
        return matches[0]

    # Try raw JSON
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        logger.debug("Extracted JSON from raw text")
        return text[start:end+1]

    raise ValueError("No JSON object found in response")


def validate_roi_classification(result: ROIClassificationResult) -> Dict[str, Any]:
    """
    Validate ROI classification result

    Args:
        result: ROIClassificationResult to validate

    Returns:
        Dict with validation results: {"valid": bool, "errors": List[str], "warnings": List[str]}
    """
    errors = []
    warnings = []

    try:
        # Check 1: Verify model type code matches model type name
        model_type_mapping = {
            ModelTypeCode.B1: "Unit Price Optimization",
            ModelTypeCode.B2: "Site of Service Optimization",
            ModelTypeCode.B3: "Value-Based Care ROI",
            ModelTypeCode.B4: "Payment Integrity",
            ModelTypeCode.B5: "Prior Authorization ROI",
            ModelTypeCode.B6: "Case Management ROI",
            ModelTypeCode.B7: "Episode Optimization",
            ModelTypeCode.B8: "Pharmacy Optimization",
            ModelTypeCode.B9: "Network Steerage",
            ModelTypeCode.B10: "Utilization Management",
            ModelTypeCode.B11: "Quality Improvement ROI",
            ModelTypeCode.B12: "Population Health ROI",
            ModelTypeCode.B13: "Custom ROI Model"
        }

        expected_name = model_type_mapping.get(result.recommended_model_type)
        if expected_name and result.model_type_name != expected_name:
            warnings.append(
                f"Model type name '{result.model_type_name}' does not match expected "
                f"'{expected_name}' for {result.recommended_model_type}"
            )

        # Check 2: Verify alternative models are different from recommended
        for alt in result.alternative_models:
            if alt.model_type_code == result.recommended_model_type:
                errors.append(
                    f"Alternative model {alt.model_type_code} is same as recommended model"
                )

        # Check 3: Verify alternative models have reasonable scores
        for alt in result.alternative_models:
            if alt.applicability_score > 0.9:
                warnings.append(
                    f"Alternative model {alt.model_type_code} has very high score ({alt.applicability_score}) "
                    "- consider if it should be the primary recommendation"
                )

        # Check 4: Verify confidence level matches reasoning
        if result.reasoning.confidence_level == "high":
            if len(result.reasoning.primary_factors) < 3:
                warnings.append(
                    "Confidence is 'high' but only 2 or fewer primary factors provided"
                )

        # Check 5: Verify key value drivers are non-empty
        if not result.key_value_drivers:
            errors.append("At least one key value driver required")

        # Check 6: Verify clinical focus areas are non-empty
        if not result.clinical_focus_areas:
            errors.append("At least one clinical focus area required")

    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


# ============================================================================
# ROI CLASSIFICATION AGENT TEMPLATE
# ============================================================================

class ROIClassificationAgentTemplate(BaseAgentTemplate):
    """Agent template for ROI model type classification."""

    def __init__(self):
        """Initialize ROI classification agent template."""
        super().__init__()

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration (AWS Bedrock compatible)."""
        return {
            "markdown": False,
            "add_history_to_context": True,
            "num_history_runs": 1,
        }

    def get_tools(self) -> List:
        """Get tools for classification (no tools needed - pure analysis)."""
        return []

    def get_instructions(self) -> str:
        """Load ROI classification instructions from prompt repository."""
        instructions = self._load_instruction_file("roi_classification_instructions.md")

        if not instructions:
            logger.warning("ROI classification instructions file not found, using fallback")
            instructions = """
# ROI Classification Agent Instructions

You are an expert ROI analyst specializing in healthcare analytics. Your task is to analyze
research data about a healthcare vendor and classify the appropriate ROI model type (B1-B13).

## Available ROI Model Types

**B1: Unit Price Optimization** - Focus on reducing unit costs for specific procedures or services
**B2: Site of Service Optimization** - Optimizing where care is delivered for cost/quality balance
**B3: Value-Based Care ROI** - Measuring impact of value-based payment arrangements
**B4: Payment Integrity** - Detecting and preventing improper payments
**B5: Prior Authorization ROI** - Measuring impact of prior auth programs
**B6: Case Management ROI** - ROI from case/care management interventions
**B7: Episode Optimization** - Optimizing costs across full episodes of care
**B8: Pharmacy Optimization** - Optimizing drug utilization and costs
**B9: Network Steerage** - Steering members to high-value providers
**B10: Utilization Management** - Managing service utilization appropriately
**B11: Quality Improvement ROI** - ROI from quality improvement initiatives
**B12: Population Health ROI** - Measuring population health program impact
**B13: Custom ROI Model** - Hybrid or specialized ROI model

## Classification Process

1. Analyze the vendor's value proposition from web research
2. Analyze the document analysis results for clinical focus
3. Identify key value drivers (cost reduction, quality improvement, utilization management, etc.)
4. Determine clinical domain (MSK, maternity, chronic disease, pharmacy, etc.)
5. Match intervention type to appropriate ROI model
6. Provide detailed reasoning with confidence level
7. Suggest alternative models if applicable

## Output Format

Return a JSON object matching ROIClassificationResult schema with:
- recommended_model_type: The primary ROI model type (B1-B13)
- model_type_name: Human-readable name
- reasoning: Detailed reasoning including clinical domain match, data requirements match, intervention type match
- alternative_models: Alternative model types with rationale and applicability scores
- key_value_drivers: List of key value drivers identified
- clinical_focus_areas: List of clinical focus areas
- estimated_complexity: Implementation complexity (low/medium/high)

Return ONLY the JSON object, no additional text or explanation.
"""

        return instructions

    def get_description(self) -> str:
        """Get agent description."""
        return (
            "ROIClassificationAgent - Analyzes research data to classify appropriate ROI model type (B1-B13) "
            "based on vendor value proposition, clinical focus, and intervention type."
        )


# ============================================================================
# AGENT FACTORY FUNCTIONS
# ============================================================================

def create_roi_classification_agent(
    name: str = "ROIClassificationAgent",
    model: Any = None,
    **kwargs
) -> MareAgent:
    """Create an ROI classification agent instance.

    Args:
        name: Agent name
        model: LLM model instance (if None, uses default)
        **kwargs: Additional agent parameters

    Returns:
        MareAgent instance configured for ROI classification
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    template = ROIClassificationAgentTemplate()

    agent = template.create_agent(
        name=name,
        model=model,
        **kwargs
    )

    logger.info(f"Created {name} with manual JSON parsing")
    return agent


def create_roi_classification_agent_with_retry(
    name: str = "ROIClassificationAgent",
    model: Any = None,
    max_retries: int = 3,
    **kwargs
) -> MareAgent:
    """Create ROI classification agent with automatic retry on validation failure.

    Args:
        name: Agent name
        model: LLM model instance
        max_retries: Maximum retry attempts
        **kwargs: Additional agent parameters

    Returns:
        MareAgent with retry capability
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    agent = create_roi_classification_agent(
        name=name,
        model=model,
        **kwargs
    )

    original_run = agent.run

    def run_with_retry(message: str, **run_kwargs):
        """Run agent with retry logic."""
        attempt = 0
        last_error = None

        while attempt < max_retries:
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries}: Classifying ROI model type...")

                # Run agent
                response = original_run(message, **run_kwargs)

                # Extract text content
                if hasattr(response, 'content'):
                    response_text = response.content
                else:
                    response_text = str(response)

                logger.debug(f"Response type: {type(response)}, length: {len(str(response_text))}")

                # Step 1: Extract JSON
                try:
                    json_str = extract_json_from_response(response_text)
                    logger.debug("✅ JSON extracted")
                except ValueError as e:
                    raise ValueError(f"JSON extraction failed: {e}")

                # Step 2: Parse JSON
                try:
                    data_dict = json.loads(json_str)
                    logger.debug("✅ JSON parsed")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON syntax: {e}")

                # Step 3: Validate with Pydantic
                try:
                    result = ROIClassificationResult(**data_dict)
                    logger.info("✅ Pydantic validation passed")

                    # Step 4: Business logic validation
                    validation = validate_roi_classification(result)

                    if validation['valid']:
                        logger.info(f"✅ Classification successful on attempt {attempt + 1}: {result.recommended_model_type}")
                        return result
                    else:
                        # Validation failed - prepare feedback
                        error_msg = "Classification validation errors:\n"
                        for error in validation['errors']:
                            error_msg += f"  - {error}\n"
                        for warning in validation['warnings']:
                            error_msg += f"  ⚠️  {warning}\n"

                        logger.warning(f"Validation failed on attempt {attempt + 1}:\n{error_msg}")

                        feedback_message = f"""
{message}

## PREVIOUS ATTEMPT FEEDBACK (Attempt {attempt + 1})

Your previous classification output had validation errors. Please fix these issues:

{error_msg}

Generate corrected classification output that addresses all errors above.
Return ONLY the JSON object, with no additional text or explanation.
"""
                        message = feedback_message
                        last_error = error_msg
                        attempt += 1

                except ValidationError as e:
                    error_details = []
                    for error in e.errors():
                        loc = " -> ".join(str(x) for x in error['loc'])
                        error_details.append(f"{loc}: {error['msg']}")
                    raise ValueError(f"Pydantic validation failed:\n" + "\n".join(error_details))

            except (ValueError, json.JSONDecodeError, ValidationError) as e:
                logger.error(f"Parsing/Validation error on attempt {attempt + 1}: {e}")
                last_error = str(e)
                attempt += 1

                if attempt < max_retries:
                    message = f"""
{message}

## PREVIOUS ATTEMPT ERROR (Attempt {attempt})

An error occurred while parsing your response: {str(e)}

Please fix the error and return ONLY a valid JSON object matching the ROIClassificationResult schema.
Do not include any explanatory text, markdown formatting, or additional commentary.
Return ONLY the raw JSON object.
"""

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                last_error = str(e)
                attempt += 1

                if attempt < max_retries:
                    message = f"""
{message}

## PREVIOUS ATTEMPT ERROR (Attempt {attempt})

An unexpected error occurred: {str(e)}

Please try again and ensure the output is valid JSON matching the ROIClassificationResult schema.
"""

        # Max retries exceeded
        logger.error(f"Classification failed after {max_retries} attempts. Last error: {last_error}")
        raise RuntimeError(
            f"ROI classification failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

    agent.run = run_with_retry

    logger.info(f"Created {name} with retry logic (max_retries={max_retries})")

    return agent
