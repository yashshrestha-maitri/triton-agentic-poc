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
from core.validation.hallucination_detector import SourceVerifier, aggregate_verification_results
from core.lineage import LineageTracker, create_tracker_from_env, compute_document_hash
from uuid import uuid4

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

                    if not validation['valid']:
                        # Business logic validation failed - prepare feedback
                        error_msg = "Document analysis validation errors:\n"
                        for error in validation['errors']:
                            error_msg += f"  - {error}\n"
                        for warning in validation['warnings']:
                            error_msg += f"  ⚠️  {warning}\n"

                        logger.warning(f"Business logic validation failed on attempt {attempt + 1}:\n{error_msg}")

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
                        continue

                    # Step 5: Source Verification (Layer 5) - Optional
                    # Only run if source_document_texts are provided
                    source_texts = run_kwargs.get('source_document_texts', {})

                    if source_texts:
                        logger.info("Running Layer 5: Source verification...")
                        verifier = SourceVerifier(fuzzy_threshold=0.85)

                        verification_issues = []

                        # Verify value propositions
                        for vp in result.extracted_value_propositions:
                            doc_text = source_texts.get(vp.source_document, '')
                            if doc_text:
                                verification = verifier.verify_text_extraction(
                                    extracted_text=vp.description,
                                    source_document_text=doc_text,
                                    source_text_provided=vp.source_text
                                )

                                if not verification.verified:
                                    issue = f"Value proposition '{vp.name}' could not be verified in source document '{vp.source_document}'"
                                    if verification.issues:
                                        issue += f": {'; '.join(verification.issues)}"
                                    verification_issues.append(issue)

                        # Verify clinical outcomes
                        for outcome in result.clinical_outcomes:
                            doc_text = source_texts.get(outcome.source_document, '')
                            if doc_text:
                                verification = verifier.verify_text_extraction(
                                    extracted_text=outcome.outcome,
                                    source_document_text=doc_text,
                                    source_text_provided=outcome.source_text
                                )

                                if not verification.verified:
                                    issue = f"Clinical outcome '{outcome.outcome[:50]}...' could not be verified in source document '{outcome.source_document}'"
                                    if verification.issues:
                                        issue += f": {'; '.join(verification.issues)}"
                                    verification_issues.append(issue)

                        # Verify financial metrics
                        for metric in result.financial_metrics:
                            doc_text = source_texts.get(metric.source_document, '')
                            if doc_text:
                                verification = verifier.verify_text_extraction(
                                    extracted_text=f"{metric.metric_name}: {metric.value}",
                                    source_document_text=doc_text,
                                    source_text_provided=metric.source_text
                                )

                                if not verification.verified:
                                    issue = f"Financial metric '{metric.metric_name}: {metric.value}' could not be verified in source document '{metric.source_document}'"
                                    if verification.issues:
                                        issue += f": {'; '.join(verification.issues)}"
                                    verification_issues.append(issue)

                        # If verification issues found, retry with feedback
                        if verification_issues:
                            logger.warning(f"Source verification failed on attempt {attempt + 1}: {len(verification_issues)} issues found")

                            error_msg = "Source Verification Issues:\n"
                            for issue in verification_issues:
                                error_msg += f"  - {issue}\n"

                            feedback_message = f"""
{message}

## PREVIOUS ATTEMPT FEEDBACK (Attempt {attempt + 1}) - SOURCE VERIFICATION FAILED

Your previous analysis had extractions that could not be verified in the source documents.
This suggests potential hallucinations or incorrect extractions.

{error_msg}

IMPORTANT: For each extraction, you MUST:
1. Include the exact verbatim quote from the source document in the 'source_text' field
2. Ensure extracted values match what is actually written in the document
3. Do NOT invent or infer values that are not explicitly stated

Generate corrected analysis output that addresses all verification issues above.
Return ONLY the JSON object, with no additional text or explanation.
"""
                            message = feedback_message
                            last_error = error_msg
                            attempt += 1
                            continue

                        logger.info("✅ Source verification passed")
                    else:
                        logger.info("ℹ️  Source verification skipped (no source_document_texts provided)")

                    # All validations passed
                    logger.info(f"✅ Document analysis successful on attempt {attempt + 1}")

                    # Step 6: Create lineage records (if tracker enabled)
                    enable_lineage = run_kwargs.get('enable_lineage', True)
                    if enable_lineage:
                        try:
                            tracker = create_tracker_from_env()
                            logger.info("Creating lineage records for extractions...")

                            # Get model name from agent or use default
                            model_name = run_kwargs.get('model_name', 'unknown')

                            # Create lineage for value propositions
                            for vp in result.extracted_value_propositions:
                                # Generate unique extraction ID if not provided
                                if not vp.extraction_id:
                                    vp.extraction_id = uuid4()

                                # Get source document text
                                doc_text = source_texts.get(vp.source_document, '')
                                if not doc_text:
                                    logger.warning(f"No source text for document {vp.source_document}, skipping lineage")
                                    continue

                                lineage = tracker.create_lineage_record(
                                    extraction_id=vp.extraction_id,
                                    source_document_url=vp.source_document,
                                    source_document_content=doc_text,
                                    extraction_agent="DocumentAnalysisAgent",
                                    extraction_model=model_name,
                                    verification_status=vp.verification_status or 'unverified',
                                    verification_issues=vp.verification_issues or [],
                                    extraction_confidence_initial=vp.extraction_confidence,
                                    extraction_confidence_final=vp.extraction_confidence,
                                    source_text=vp.source_text
                                )
                                logger.debug(f"Created lineage for value proposition: {vp.extraction_id}")

                            # Create lineage for clinical outcomes
                            for outcome in result.clinical_outcomes:
                                if not outcome.extraction_id:
                                    outcome.extraction_id = uuid4()

                                doc_text = source_texts.get(outcome.source_document, '')
                                if not doc_text:
                                    continue

                                lineage = tracker.create_lineage_record(
                                    extraction_id=outcome.extraction_id,
                                    source_document_url=outcome.source_document,
                                    source_document_content=doc_text,
                                    extraction_agent="DocumentAnalysisAgent",
                                    extraction_model=model_name,
                                    verification_status=outcome.verification_status or 'unverified',
                                    verification_issues=outcome.verification_issues or [],
                                    extraction_confidence_initial=outcome.extraction_confidence,
                                    extraction_confidence_final=outcome.extraction_confidence,
                                    source_text=outcome.source_text
                                )
                                logger.debug(f"Created lineage for clinical outcome: {outcome.extraction_id}")

                            # Create lineage for financial metrics
                            for metric in result.financial_metrics:
                                if not metric.extraction_id:
                                    metric.extraction_id = uuid4()

                                doc_text = source_texts.get(metric.source_document, '')
                                if not doc_text:
                                    continue

                                lineage = tracker.create_lineage_record(
                                    extraction_id=metric.extraction_id,
                                    source_document_url=metric.source_document,
                                    source_document_content=doc_text,
                                    extraction_agent="DocumentAnalysisAgent",
                                    extraction_model=model_name,
                                    verification_status=metric.verification_status or 'unverified',
                                    verification_issues=metric.verification_issues or [],
                                    extraction_confidence_initial=metric.extraction_confidence,
                                    extraction_confidence_final=metric.extraction_confidence,
                                    source_text=metric.source_text
                                )
                                logger.debug(f"Created lineage for financial metric: {metric.extraction_id}")

                            logger.info(f"✅ Created lineage records for {len(result.extracted_value_propositions) + len(result.clinical_outcomes) + len(result.financial_metrics)} extractions")

                        except Exception as e:
                            # Lineage creation failure should not prevent extraction success
                            logger.error(f"Failed to create lineage records: {e}")
                            logger.warning("Continuing without lineage tracking")
                    else:
                        logger.info("ℹ️  Lineage tracking disabled")

                    return result

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
