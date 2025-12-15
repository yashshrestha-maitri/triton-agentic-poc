"""Research Agent for Healthcare Dashboard Context.

This agent researches industry insights, competitive intelligence, data requirements,
and audience personas to inform dashboard template generation.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import re
from pydantic import ValidationError

from agents.base.base_agent import BaseAgentTemplate, MareAgent
from core.models.research_models import ResearchResult, validate_research_completeness
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


class ResearchAgentTemplate(BaseAgentTemplate):
    """Agent template for researching healthcare dashboard context."""

    def __init__(self, research_depth: str = "standard"):
        """Initialize research agent template.

        Args:
            research_depth: Level of research detail ('quick', 'standard', 'deep')
        """
        super().__init__()
        self.research_depth = research_depth
        if research_depth not in ['quick', 'standard', 'deep']:
            logger.warning(f"Invalid research depth '{research_depth}', defaulting to 'standard'")
            self.research_depth = 'standard'

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
        """Get tools for the agent.

        Research agent doesn't need external tools in Phase 1.
        Future phases may add:
        - Web search tool
        - Knowledge base tool
        - Data source analyzer
        """
        return []  # No tools needed - agent works with JSON input directly

    def get_instructions(self) -> str:
        """Load instructions from markdown file based on research depth."""
        instructions = self._load_instruction_file("template_research_instructions.md")
        if not instructions:
            logger.warning("Research instructions file not found, using fallback")
            instructions = """
            You are a healthcare industry research specialist. Analyze the provided value proposition
            and generate comprehensive research insights to inform dashboard template design.

            Your research must cover:
            1. Industry trends and common metrics
            2. Competitive dashboard patterns and best practices
            3. Data requirements and feasibility
            4. Audience personas and their information needs
            5. Template generation guidance

            Return a structured JSON object matching the ResearchResult schema.
            """

        # Add research depth context
        depth_instructions = {
            'quick': "\n\nRESEARCH DEPTH: QUICK - Provide essential insights with minimum detail. Focus on top 3-5 items per category.",
            'standard': "\n\nRESEARCH DEPTH: STANDARD - Provide comprehensive insights with good detail. This is the recommended depth.",
            'deep': "\n\nRESEARCH DEPTH: DEEP - Provide extensive insights with maximum detail. Include all possible considerations and edge cases."
        }

        instructions += depth_instructions.get(self.research_depth, depth_instructions['standard'])

        return instructions

    def get_description(self) -> str:
        """Get agent description."""
        return (
            f"Healthcare Dashboard Research Agent (Depth: {self.research_depth}) - "
            "Analyzes value propositions to provide industry insights, competitive intelligence, "
            "data requirements, and audience personas. Outputs structured research to guide "
            "template generation."
        )


def create_research_agent(
    name: str = "ResearchAgent",
    model: Any = None,
    research_depth: str = "standard",
    **kwargs
) -> MareAgent:
    """Create a research agent instance.

    Args:
        name: Agent name
        model: LLM model instance (if None, uses default from model_factory)
        research_depth: Level of research detail ('quick', 'standard', 'deep')
        **kwargs: Additional agent parameters

    Returns:
        MareAgent instance configured for research

    Example:
        from core.models.model_factory import get_default_model

        model = get_default_model()

        # Standard research (recommended)
        agent = create_research_agent(
            name="ResearchAgent",
            model=model,
            research_depth="standard"
        )

        # Quick research (faster, less detail)
        agent = create_research_agent(
            name="QuickResearchAgent",
            model=model,
            research_depth="quick"
        )

        # Deep research (slower, maximum detail)
        agent = create_research_agent(
            name="DeepResearchAgent",
            model=model,
            research_depth="deep"
        )
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    # Create agent template with research depth
    template = ResearchAgentTemplate(research_depth=research_depth)

    # Create and return agent
    agent = template.create_agent(
        name=name,
        model=model,
        **kwargs
    )

    logger.info(f"Created {name} with research depth: {research_depth} and manual JSON parsing")

    return agent


def create_research_agent_with_retry(
    name: str = "ResearchAgent",
    model: Any = None,
    max_retries: int = 3,
    research_depth: str = "standard",
    **kwargs
) -> MareAgent:
    """Create research agent with automatic retry on validation failure.

    This wrapper adds retry logic to handle validation errors gracefully.

    Args:
        name: Agent name
        model: LLM model instance
        max_retries: Maximum retry attempts
        research_depth: Level of research detail ('quick', 'standard', 'deep')
        **kwargs: Additional agent parameters

    Returns:
        MareAgent with retry capability
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    # Create base agent with research depth
    agent = create_research_agent(
        name=name,
        model=model,
        research_depth=research_depth,
        **kwargs
    )

    # Store original run method
    original_run = agent.run

    def run_with_retry(message: str, **run_kwargs):
        """Run agent with retry logic for research."""
        attempt = 0
        last_error = None

        while attempt < max_retries:
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries}: Conducting research...")

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

                # Step 3: Validate with Pydantic model
                try:
                    result = ResearchResult(**data_dict)
                    logger.info("✅ Research Pydantic validation passed")

                    # Step 4: Business logic validation
                    validation = validate_research_completeness(result)

                    if validation['valid']:
                        logger.info(f"✅ Research successful on attempt {attempt + 1}")
                        # Update metadata
                        result.metadata.research_depth = research_depth
                        return result
                    else:
                        # Validation failed - prepare error feedback for retry
                        error_msg = "Research validation errors:\n"
                        for error in validation['errors']:
                            error_msg += f"  - {error}\n"
                        for warning in validation['warnings']:
                            error_msg += f"  ⚠️  {warning}\n"

                        logger.warning(f"Validation failed on attempt {attempt + 1}:\n{error_msg}")

                        # Add error feedback to message for next attempt
                        feedback_message = f"""
{message}

## PREVIOUS ATTEMPT FEEDBACK (Attempt {attempt + 1})

Your previous research output had validation errors. Please fix these issues:

{error_msg}

Generate a corrected research output that addresses all errors above.
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

An error occurred while parsing your research response: {str(e)}

Please fix the error and return ONLY a valid JSON object matching the required ResearchResult schema.
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

Please try again and ensure the output is valid JSON matching the ResearchResult schema.
"""

        # Max retries exceeded
        logger.error(f"Research failed after {max_retries} attempts. Last error: {last_error}")
        raise RuntimeError(
            f"Research failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

    # Replace run method with retry-enabled version
    agent.run = run_with_retry

    logger.info(f"Created {name} with retry logic (max_retries={max_retries}, depth={research_depth})")

    return agent
