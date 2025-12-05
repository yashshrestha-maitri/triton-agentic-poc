"""Template Generator Agent for Dashboard Templates.

This agent generates 5-10 dashboard template variations from a client value proposition.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import re
from pydantic import ValidationError

from agents.base.base_agent import BaseAgentTemplate, MareAgent
from core.models.template_models import TemplateGenerationResult
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


def extract_json_from_response(text: str) -> str:
    """Extract JSON from LLM response that may contain markdown or extra text.

    Args:
        text: Raw text response from LLM

    Returns:
        Extracted JSON string

    Raises:
        ValueError: If no valid JSON found in response
    """
    # Convert to string if needed
    text = str(text)

    # Method 1: Try to find JSON in markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    if matches:
        logger.debug("Extracted JSON from markdown code block")
        return matches[0]

    # Method 2: Try to find raw JSON object (first { to last })
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        logger.debug("Extracted JSON from raw text")
        return text[start:end+1]

    # Method 3: If no brackets found, raise error
    raise ValueError("No JSON object found in response. Response must contain a JSON object starting with { and ending with }")


class TemplateGeneratorAgentTemplate(BaseAgentTemplate):
    """Agent template for generating dashboard templates."""

    def __init__(self, single_mode: bool = False):
        """Initialize template generator.

        Args:
            single_mode: If True, generates one template at a time. If False, generates 5-10 templates.
        """
        super().__init__()
        self.single_mode = single_mode

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration without structured output (for AWS Bedrock compatibility)."""
        return {
            # NO output_schema - AWS Bedrock doesn't support response_format
            # Manual JSON parsing happens in retry wrapper
            "markdown": False,  # Disable markdown to get pure JSON
            "add_history_to_context": True,
            "num_history_runs": 1,  # Only need immediate history for refinement
        }

    def get_tools(self) -> List:
        """Get tools for the agent. Template generator doesn't need external tools."""
        return []  # No tools needed - agent works with JSON input directly

    def get_instructions(self) -> str:
        """Load instructions from markdown file based on mode."""
        if self.single_mode:
            instructions = self._load_instruction_file("single_template_generation_instructions.md")
            if not instructions:
                logger.warning("Single template instructions file not found, using fallback")
                instructions = """
                You are a dashboard design specialist. Generate ONE dashboard template
                based on the provided category and target audience. Follow all constraints strictly.
                Return JSON with structure: {"template": {...}, "reasoning": "..."}
                """
        else:
            instructions = self._load_instruction_file("template_generation_instructions.md")
            if not instructions:
                logger.warning("Batch instructions file not found, using fallback")
                instructions = """
                You are a dashboard design specialist. Generate 5-10 dashboard template variations
                from the provided value proposition JSON. Follow all constraints strictly.
                """

        return instructions

    def get_description(self) -> str:
        """Get agent description."""
        if self.single_mode:
            return (
                "Dashboard Template Generator (Single Mode) - Creates ONE dashboard template "
                "for a specific category and audience. Generates structured JSON with widget "
                "definitions, layouts, and visual styles."
            )
        else:
            return (
                "Dashboard Template Generator - Creates 5-10 template variations for healthcare "
                "ROI dashboards based on client value propositions. Generates structured JSON "
                "with widget definitions, layouts, and visual styles."
            )


def create_template_generator_agent(
    name: str = "TemplateGeneratorAgent",
    model: Any = None,
    single_mode: bool = False,
    **kwargs
) -> MareAgent:
    """Create a template generator agent instance.

    Args:
        name: Agent name
        model: LLM model instance (if None, uses default from model_factory)
        single_mode: If True, generates one template at a time
        **kwargs: Additional agent parameters

    Returns:
        MareAgent instance configured for template generation

    Example:
        from core.models.model_factory import get_default_model

        model = get_default_model()

        # Batch mode (5-10 templates)
        agent = create_template_generator_agent(
            name="TemplateGeneratorAgent",
            model=model,
            single_mode=False
        )

        # Single mode (1 template)
        agent = create_template_generator_agent(
            name="SingleTemplateGenerator",
            model=model,
            single_mode=True
        )
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    # Create agent template with mode
    template = TemplateGeneratorAgentTemplate(single_mode=single_mode)

    # Create and return agent
    agent = template.create_agent(
        name=name,
        model=model,
        **kwargs
    )

    mode_str = "single-template" if single_mode else "batch (5-10 templates)"
    logger.info(f"Created {name} in {mode_str} mode with manual JSON parsing")

    return agent


def create_template_generator_with_retry(
    name: str = "TemplateGeneratorAgent",
    model: Any = None,
    max_retries: int = 3,
    single_mode: bool = False,
    **kwargs
) -> MareAgent:
    """Create template generator agent with automatic retry on validation failure.

    This wrapper adds retry logic to handle validation errors gracefully.

    Args:
        name: Agent name
        model: LLM model instance
        max_retries: Maximum retry attempts
        single_mode: If True, generates one template at a time
        **kwargs: Additional agent parameters

    Returns:
        MareAgent with retry capability
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    # Create base agent with mode
    agent = create_template_generator_agent(name=name, model=model, single_mode=single_mode, **kwargs)

    # Store original run method
    original_run = agent.run

    def run_with_retry(message: str, **run_kwargs):
        """Run agent with retry logic for both single and batch modes."""
        from core.models.template_models import SingleTemplateResult, validate_all, validate_grid_positions

        attempt = 0
        last_error = None

        while attempt < max_retries:
            try:
                mode_str = "template" if single_mode else "templates"
                logger.info(f"Attempt {attempt + 1}/{max_retries}: Generating {mode_str}...")

                # Run agent - returns text response (no structured output for AWS Bedrock)
                response = original_run(message, **run_kwargs)

                # Extract text content
                if hasattr(response, 'content'):
                    response_text = response.content
                else:
                    response_text = str(response)

                logger.debug(f"Response type: {type(response)}, length: {len(str(response_text))}")

                # Step 1: Extract JSON from response text
                try:
                    json_str = extract_json_from_response(response_text)
                    logger.debug("✅ JSON extracted from response")
                except ValueError as e:
                    raise ValueError(f"JSON extraction failed: {e}")

                # Step 2: Parse JSON string to dictionary
                try:
                    data_dict = json.loads(json_str)
                    logger.debug("✅ JSON parsed successfully")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON syntax: {e}")

                # Step 3: Validate with Pydantic model (different for single vs batch)
                try:
                    if single_mode:
                        result = SingleTemplateResult(**data_dict)
                        logger.info("✅ Single template Pydantic validation passed")

                        # Validate grid positions for single template
                        validate_grid_positions(result.template)
                        logger.info("✅ Grid validation passed")

                        return result
                    else:
                        result = TemplateGenerationResult(**data_dict)
                        logger.info("✅ Batch templates Pydantic validation passed")

                        # Step 4: Business logic validation (only for batch mode)
                        validation = validate_all(
                            result,
                            target_audiences=run_kwargs.get('target_audiences', [])
                        )

                        if validation['valid']:
                            logger.info(f"✅ Generation successful on attempt {attempt + 1}")
                            result.metadata.validation_passed = True
                            return result
                        else:
                            # Validation failed - prepare error feedback for retry
                            error_msg = "Validation errors:\n"
                            for error in validation['errors']:
                                error_msg += f"  - {error}\n"
                            for warning in validation['warnings']:
                                error_msg += f"  ⚠️  {warning}\n"

                            logger.warning(f"Validation failed on attempt {attempt + 1}:\n{error_msg}")

                            # Add error feedback to message for next attempt
                            feedback_message = f"""
{message}

## PREVIOUS ATTEMPT FEEDBACK (Attempt {attempt + 1})

Your previous output had validation errors. Please fix these issues:

{error_msg}

Generate a corrected output that addresses all errors above.
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
                    # Add error context for retry
                    message = f"""
{message}

## PREVIOUS ATTEMPT ERROR (Attempt {attempt})

An error occurred while parsing your response: {str(e)}

Please fix the error and return ONLY a valid JSON object matching the required schema.
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

Please try again and ensure the output is valid JSON matching the schema.
"""

        # Max retries exceeded
        logger.error(f"Failed after {max_retries} attempts. Last error: {last_error}")
        raise RuntimeError(
            f"Template generation failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

    # Replace run method with retry-enabled version
    agent.run = run_with_retry

    logger.info(f"Created {name} with retry logic (max_retries={max_retries})")

    return agent
