"""WebSearch Agent for Value Proposition Research.

This agent researches healthcare companies via web search to derive value propositions,
competitive positioning, and ROI frameworks as specified in TRITON_ENGINEERING_SPEC.md Section 4.2.1.
"""

from typing import Any, Dict, List, Optional
import json
import re
from pydantic import ValidationError

from agents.base.base_agent import BaseAgentTemplate, MareAgent
from core.models.value_proposition_models import WebSearchResult, validate_web_search_result
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


class WebSearchAgentTemplate(BaseAgentTemplate):
    """Agent template for web research of healthcare companies."""

    def __init__(self, research_mode: str = "autonomous"):
        """Initialize web search agent template.

        Args:
            research_mode: 'autonomous' (15-25 searches) or 'manual' (5-15 searches)
        """
        super().__init__()
        self.research_mode = research_mode
        if research_mode not in ['autonomous', 'manual']:
            logger.warning(f"Invalid research mode '{research_mode}', defaulting to 'autonomous'")
            self.research_mode = 'autonomous'

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration (AWS Bedrock compatible)."""
        return {
            "markdown": False,
            "add_history_to_context": True,
            "num_history_runs": 1,
        }

    def get_tools(self) -> List:
        """Get tools for web research."""
        from tools.google_search_tool import create_google_search_tool
        from tools.web_scraper_tool import create_web_scraper_tool

        return [create_google_search_tool(), create_web_scraper_tool()]

    def get_instructions(self) -> str:
        """Load web search instructions."""
        instructions = self._load_instruction_file("web_search_instructions.md")
        if not instructions:
            logger.warning("Web search instructions file not found, using fallback")
            instructions = """
            You are a healthcare industry research specialist. Perform comprehensive web research
            on the provided company to derive value propositions, competitive positioning, and ROI frameworks.
            Return structured JSON matching WebSearchResult schema.
            """

        # Add mode-specific context
        mode_context = {
            'autonomous': "\n\nMODE: AUTONOMOUS - Perform 15-25 comprehensive searches across all research areas.",
            'manual': "\n\nMODE: MANUAL - Follow user-provided prompts. Perform 5-15 focused searches."
        }
        instructions += mode_context.get(self.research_mode, mode_context['autonomous'])

        return instructions

    def get_description(self) -> str:
        """Get agent description."""
        return (
            f"WebSearchAgent ({self.research_mode} mode) - Researches healthcare companies "
            "via web search to derive value propositions, competitive positioning, ROI frameworks, "
            "and clinical outcomes evidence."
        )


def create_web_search_agent(
    name: str = "WebSearchAgent",
    model: Any = None,
    research_mode: str = "autonomous",
    **kwargs
) -> MareAgent:
    """Create a web search agent instance.

    Args:
        name: Agent name
        model: LLM model instance (if None, uses default)
        research_mode: 'autonomous' or 'manual'
        **kwargs: Additional agent parameters

    Returns:
        MareAgent instance configured for web research
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    template = WebSearchAgentTemplate(research_mode=research_mode)

    agent = template.create_agent(
        name=name,
        model=model,
        **kwargs
    )

    logger.info(f"Created {name} in {research_mode} mode with manual JSON parsing")
    return agent


def create_web_search_agent_with_retry(
    name: str = "WebSearchAgent",
    model: Any = None,
    max_retries: int = 3,
    research_mode: str = "autonomous",
    **kwargs
) -> MareAgent:
    """Create web search agent with automatic retry on validation failure.

    Args:
        name: Agent name
        model: LLM model instance
        max_retries: Maximum retry attempts
        research_mode: 'autonomous' or 'manual'
        **kwargs: Additional agent parameters

    Returns:
        MareAgent with retry capability
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    agent = create_web_search_agent(
        name=name,
        model=model,
        research_mode=research_mode,
        **kwargs
    )

    original_run = agent.run

    def run_with_retry(message: str, **run_kwargs):
        """Run agent with retry logic."""
        attempt = 0
        last_error = None

        while attempt < max_retries:
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries}: Conducting web research...")

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
                    result = WebSearchResult(**data_dict)
                    logger.info("✅ Pydantic validation passed")

                    # Step 4: Business logic validation
                    validation = validate_web_search_result(result)

                    if validation['valid']:
                        logger.info(f"✅ Research successful on attempt {attempt + 1}")
                        return result
                    else:
                        # Validation failed - prepare feedback
                        error_msg = "Research validation errors:\n"
                        for error in validation['errors']:
                            error_msg += f"  - {error}\n"
                        for warning in validation['warnings']:
                            error_msg += f"  ⚠️  {warning}\n"

                        logger.warning(f"Validation failed on attempt {attempt + 1}:\n{error_msg}")

                        feedback_message = f"""
{message}

## PREVIOUS ATTEMPT FEEDBACK (Attempt {attempt + 1})

Your previous research output had validation errors. Please fix these issues:

{error_msg}

Generate corrected research output that addresses all errors above.
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

Please fix the error and return ONLY a valid JSON object matching the WebSearchResult schema.
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

Please try again and ensure the output is valid JSON matching the WebSearchResult schema.
"""

        # Max retries exceeded
        logger.error(f"Research failed after {max_retries} attempts. Last error: {last_error}")
        raise RuntimeError(
            f"Web research failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

    agent.run = run_with_retry

    logger.info(f"Created {name} with retry logic (max_retries={max_retries}, mode={research_mode})")

    return agent
