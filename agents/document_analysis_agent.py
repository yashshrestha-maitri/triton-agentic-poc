"""DocumentAnalysis Agent for Client Document Analysis.

This agent analyzes client-uploaded documents (ROI sheets, case studies, white papers) to extract
value propositions, clinical outcomes, and financial metrics as specified in TRITON_ENGINEERING_SPEC.md Section 4.2.2.
"""

from typing import Any, Dict, List, Optional
import json
import re
from pydantic import ValidationError

from agents.base.base_agent import BaseAgentTemplate, MareAgent
from core.models.value_proposition_models import DocumentAnalysisResult, validate_document_analysis_result
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


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


class DocumentAnalysisAgentTemplate(BaseAgentTemplate):
    """Agent template for analyzing client documents."""

    def __init__(self):
        """Initialize document analysis agent template."""
        super().__init__()

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration (AWS Bedrock compatible)."""
        return {
            "markdown": False,
            "add_history_to_context": True,
            "num_history_runs": 1,
        }

    def get_tools(self) -> List:
        """Get tools for document analysis."""
        from tools.s3_document_reader import create_s3_document_reader
        return [create_s3_document_reader()]

    def get_instructions(self) -> str:
        """Load document analysis instructions."""
        instructions = self._load_instruction_file("document_analysis_instructions.md")
        if not instructions:
            logger.warning("Document analysis instructions file not found, using fallback")
            instructions = """
            You are a document analysis specialist expert in extracting structured information
            from healthcare ROI materials, case studies, and white papers.

            Analyze the CLIENT's uploaded documents and extract value propositions, clinical outcomes,
            financial metrics, and competitive differentiators from THEIR materials.

            Return structured JSON matching DocumentAnalysisResult schema.
            """

        return instructions

    def get_description(self) -> str:
        """Get agent description."""
        return (
            "DocumentAnalysisAgent - Analyzes client-uploaded documents (ROI sheets, case studies, "
            "white papers) to extract value propositions, clinical outcomes, financial metrics, "
            "and competitive advantages."
        )


def create_document_analysis_agent(
    name: str = "DocumentAnalysisAgent",
    model: Any = None,
    **kwargs
) -> MareAgent:
    """Create a document analysis agent instance.

    Args:
        name: Agent name
        model: LLM model instance (if None, uses default)
        **kwargs: Additional agent parameters

    Returns:
        MareAgent instance configured for document analysis
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    template = DocumentAnalysisAgentTemplate()

    agent = template.create_agent(
        name=name,
        model=model,
        **kwargs
    )

    logger.info(f"Created {name} with manual JSON parsing")
    return agent


def create_document_analysis_agent_with_retry(
    name: str = "DocumentAnalysisAgent",
    model: Any = None,
    max_retries: int = 3,
    **kwargs
) -> MareAgent:
    """Create document analysis agent with automatic retry on validation failure.

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

    agent = create_document_analysis_agent(
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
                logger.info(f"Attempt {attempt + 1}/{max_retries}: Analyzing documents...")

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
                    result = DocumentAnalysisResult(**data_dict)
                    logger.info("✅ Pydantic validation passed")

                    # Step 4: Business logic validation
                    validation = validate_document_analysis_result(result)

                    if validation['valid']:
                        logger.info(f"✅ Document analysis successful on attempt {attempt + 1}")
                        return result
                    else:
                        # Validation failed - prepare feedback
                        error_msg = "Document analysis validation errors:\n"
                        for error in validation['errors']:
                            error_msg += f"  - {error}\n"
                        for warning in validation['warnings']:
                            error_msg += f"  ⚠️  {warning}\n"

                        logger.warning(f"Validation failed on attempt {attempt + 1}:\n{error_msg}")

                        feedback_message = f"""
{message}

## PREVIOUS ATTEMPT FEEDBACK (Attempt {attempt + 1})

Your previous analysis output had validation errors. Please fix these issues:

{error_msg}

Generate corrected analysis output that addresses all errors above.
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

Please fix the error and return ONLY a valid JSON object matching the DocumentAnalysisResult schema.
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

Please try again and ensure the output is valid JSON matching the DocumentAnalysisResult schema.
"""

        # Max retries exceeded
        logger.error(f"Document analysis failed after {max_retries} attempts. Last error: {last_error}")
        raise RuntimeError(
            f"Document analysis failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

    agent.run = run_with_retry

    logger.info(f"Created {name} with retry logic (max_retries={max_retries})")

    return agent
