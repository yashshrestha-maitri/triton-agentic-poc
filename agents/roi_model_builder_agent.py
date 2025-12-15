"""ROI Model Builder Agent for generating complete ROI Model JSON.

This agent takes a classified ROI model type (B1-B13) and research data to generate
a complete, validated ROI Model JSON with all 15 required components.

The agent loads model-specific prompt instructions from the mare-triton-research-prompts
repository and uses domain expertise to build comprehensive ROI models.
"""

from typing import Any, Dict, List, Optional
import json
import re
from pathlib import Path
from functools import lru_cache
from pydantic import ValidationError

from agents.base.base_agent import BaseAgentTemplate, MareAgent
from core.models.roi_models import (
    ROIModelJSON,
    ModelTypeCode,
    validate_roi_model,
    extract_json_from_response
)
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# MODEL-SPECIFIC PROMPT LOADING
# ============================================================================

# Mapping of model type codes to prompt filenames
MODEL_PROMPT_FILENAMES = {
    ModelTypeCode.B1: "B1_unit_price_optimization.md",
    ModelTypeCode.B2: "B2_site_of_service_optimization.md",
    ModelTypeCode.B3: "B3_value_based_care_roi.md",
    ModelTypeCode.B4: "B4_payment_integrity.md",
    ModelTypeCode.B5: "B5_prior_authorization_roi.md",
    ModelTypeCode.B6: "B6_case_management_roi.md",
    ModelTypeCode.B7: "B7_episode_optimization.md",
    ModelTypeCode.B8: "B8_pharmacy_optimization.md",
    ModelTypeCode.B9: "B9_network_steerage.md",
    ModelTypeCode.B10: "B10_utilization_management.md",
    ModelTypeCode.B11: "B11_quality_improvement_roi.md",
    ModelTypeCode.B12: "B12_population_health_roi.md",
    ModelTypeCode.B13: "B13_custom_roi_model.md"
}


@lru_cache(maxsize=32)
def load_model_prompt(model_type_code: ModelTypeCode, prompts_base_path: Optional[Path] = None) -> str:
    """
    Load model-specific prompt instructions from prompt repository.

    This function is cached to avoid repeated file reads. Prompts are typically 14-45KB each.

    Args:
        model_type_code: ROI model type (B1-B13)
        prompts_base_path: Base path to prompt repository (if None, uses config)

    Returns:
        Prompt text as string

    Raises:
        FileNotFoundError: If prompt file not found
    """
    from core.config.settings import get_config

    config = get_config()

    if prompts_base_path is None:
        # Get from config
        prompts_base_path = config.prompts.model_prompts_dir
        logger.debug(f"Using prompt repository path from config: {prompts_base_path}")

    filename = MODEL_PROMPT_FILENAMES[model_type_code]
    prompt_path = Path(prompts_base_path) / filename

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Model prompt file not found: {prompt_path}\n"
            f"Expected location: {prompts_base_path}\n"
            f"Ensure mare-triton-research-prompts repository is cloned and MODEL_PROMPTS_DIR is configured."
        )

    prompt_text = prompt_path.read_text(encoding='utf-8')
    logger.info(f"Loaded {model_type_code} prompt: {len(prompt_text):,} characters from {prompt_path.name}")

    return prompt_text


@lru_cache(maxsize=1)
def load_base_schema_prompt(prompts_base_path: Optional[Path] = None) -> str:
    """
    Load base schema documentation (shared across all model types).

    Args:
        prompts_base_path: Base path to prompt repository

    Returns:
        Base schema prompt text
    """
    from core.config.settings import get_config

    config = get_config()

    if prompts_base_path is None:
        prompts_base_path = config.prompts.model_prompts_dir
        logger.debug(f"Using prompt repository path from config: {prompts_base_path}")

    schema_path = Path(prompts_base_path) / "base_schema.md"

    if not schema_path.exists():
        logger.warning(f"Base schema file not found: {schema_path}, skipping")
        return ""

    schema_text = schema_path.read_text(encoding='utf-8')
    logger.info(f"Loaded base schema: {len(schema_text):,} characters")

    return schema_text


# ============================================================================
# ROI MODEL BUILDER AGENT TEMPLATE
# ============================================================================

class ROIModelBuilderAgentTemplate(BaseAgentTemplate):
    """Agent template for building complete ROI Model JSON."""

    def __init__(self, model_type_code: ModelTypeCode, prompts_base_path: Optional[Path] = None):
        """
        Initialize ROI model builder agent template.

        Args:
            model_type_code: ROI model type to build (B1-B13)
            prompts_base_path: Optional path to prompt repository
        """
        super().__init__()
        self.model_type_code = model_type_code
        self.prompts_base_path = prompts_base_path

        # Preload prompts at initialization
        try:
            self.model_prompt = load_model_prompt(model_type_code, prompts_base_path)
            self.base_schema = load_base_schema_prompt(prompts_base_path)
            logger.info(f"Initialized ROI Model Builder for {model_type_code}")
        except FileNotFoundError as e:
            logger.error(f"Failed to load prompts: {e}")
            raise

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration (AWS Bedrock compatible)."""
        return {
            "markdown": False,
            "add_history_to_context": True,
            "num_history_runs": 1,
        }

    def get_tools(self) -> List:
        """Get tools for model building (no tools needed - pure generation)."""
        return []

    def get_instructions(self) -> str:
        """
        Get complete instructions for ROI model building.

        Combines:
        1. Base schema documentation (component definitions)
        2. Model-specific prompt (B1-B13 specific guidance)
        3. JSON output format requirements
        """
        instructions = f"""# ROI Model Builder Agent Instructions

You are an expert healthcare ROI analyst and data modeler. Your task is to generate a COMPLETE ROI Model JSON structure based on research data and the classified ROI model type.

## Model Type: {self.model_type_code.value}

---

## BASE SCHEMA DOCUMENTATION

{self.base_schema if self.base_schema else "Base schema not loaded - proceed with model-specific guidance."}

---

## MODEL-SPECIFIC GUIDANCE

{self.model_prompt}

---

## OUTPUT FORMAT REQUIREMENTS

You MUST generate a complete JSON object with ALL 15 required components:

1. **model_metadata** - Model metadata including model_type_code, model_type_name, client_name, version, status
2. **executive_summary** - High-level summary with problem statement, solution approach, expected impact, key assumptions
3. **data_requirements** - Complete data requirements with data sources, fields, lookback periods
4. **population_identification** - Cohort identification with inclusion/exclusion criteria, SQL templates, stratification variables
5. **baseline_methodology** - Baseline calculation methodology with time periods, trend analysis method
6. **calculation_components** - Complete calculation logic with variables, formulas, calculation steps
7. **sql_components** - SQL queries for data extraction
8. **output_metrics** - Primary and secondary output metrics with calculation methods
9. **assumptions** - All model assumptions with confidence levels and sensitivity impact
10. **validation_rules** - Data validation rules with error messages and severity
11. **confidence_factors** - Factors affecting model confidence
12. **configurable_parameters** - User-configurable parameters (time, rate, cost, threshold)
13. **dashboard_templates** - Dashboard templates with widgets for different audiences
14. **episode_definition** (if applicable for B7) - Episode definition with trigger events and windows
15. **generated_at** (automatic) - Generation timestamp

### Critical Requirements

- **Completeness**: Every component must be fully populated with realistic, detailed content
- **Specificity**: Use specific ICD-10 codes, CPT codes, NDC codes (not placeholders)
- **SQL Templates**: Provide actual SQL query templates with parameter binding
- **Formulas**: Provide actual mathematical formulas with variable names
- **Validation**: Ensure calculation steps are sequential (step 1, 2, 3, ...) with proper dependencies

### Validation Layers

Your output will be validated through 4 layers:
1. **JSON Schema**: Valid JSON syntax
2. **Pydantic**: Type validation and field constraints
3. **Business Rules**: Sequential steps, unique IDs, variable references
4. **Domain Logic**: Clinical appropriateness, data feasibility

### Output Format

Return ONLY a JSON object. No explanatory text. No markdown code blocks. No additional commentary.

The JSON must be valid and complete. All string fields requiring minimum lengths must meet those requirements.

---

## Generation Process

1. **Understand the Research Data**: Analyze web search results and document analysis provided
2. **Apply Model-Specific Logic**: Follow the model-specific guidance above for {self.model_type_code.value}
3. **Generate Complete JSON**: Build all 15 components with realistic, detailed content
4. **Self-Validate**: Check that JSON is complete, variables are defined, steps are sequential
5. **Return JSON Only**: No extra text, just the JSON object

---

## Ready to Generate

When you receive research data and client information, generate the complete ROI Model JSON following all requirements above.
"""

        return instructions

    def get_description(self) -> str:
        """Get agent description."""
        return (
            f"ROIModelBuilderAgent ({self.model_type_code.value}) - Generates complete ROI Model JSON "
            f"with all 15 required components for {self.model_type_code.value} model type."
        )


# ============================================================================
# AGENT FACTORY FUNCTIONS
# ============================================================================

def create_roi_model_builder_agent(
    model_type_code: ModelTypeCode,
    name: Optional[str] = None,
    model: Any = None,
    prompts_base_path: Optional[Path] = None,
    **kwargs
) -> MareAgent:
    """
    Create an ROI model builder agent instance.

    Args:
        model_type_code: ROI model type to build (B1-B13)
        name: Agent name (if None, uses "ROIModelBuilder_{model_type}")
        model: LLM model instance (if None, uses default)
        prompts_base_path: Optional path to prompt repository
        **kwargs: Additional agent parameters

    Returns:
        MareAgent instance configured for ROI model building

    Raises:
        FileNotFoundError: If model prompts not found
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    if name is None:
        name = f"ROIModelBuilder_{model_type_code.value}"

    template = ROIModelBuilderAgentTemplate(
        model_type_code=model_type_code,
        prompts_base_path=prompts_base_path
    )

    agent = template.create_agent(
        name=name,
        model=model,
        **kwargs
    )

    logger.info(f"Created {name} for {model_type_code.value} with manual JSON parsing")
    return agent


def create_roi_model_builder_with_retry(
    model_type_code: ModelTypeCode,
    name: Optional[str] = None,
    model: Any = None,
    max_retries: int = 3,
    prompts_base_path: Optional[Path] = None,
    **kwargs
) -> MareAgent:
    """
    Create ROI model builder agent with automatic retry on validation failure.

    This wrapper adds 4-layer validation with retry:
    1. JSON extraction from response
    2. JSON parsing validation
    3. Pydantic validation (types, constraints, field presence)
    4. Business rule validation (sequential steps, variable references, etc.)

    Args:
        model_type_code: ROI model type to build (B1-B13)
        name: Agent name (if None, uses "ROIModelBuilder_{model_type}")
        model: LLM model instance (if None, uses default)
        max_retries: Maximum retry attempts (default 3)
        prompts_base_path: Optional path to prompt repository
        **kwargs: Additional agent parameters

    Returns:
        MareAgent with retry capability

    Raises:
        FileNotFoundError: If model prompts not found
        RuntimeError: If generation fails after max_retries
    """
    from core.models.model_factory import get_default_model

    if model is None:
        model = get_default_model()

    if name is None:
        name = f"ROIModelBuilder_{model_type_code.value}"

    agent = create_roi_model_builder_agent(
        model_type_code=model_type_code,
        name=name,
        model=model,
        prompts_base_path=prompts_base_path,
        **kwargs
    )

    original_run = agent.run

    def run_with_retry(message: str, **run_kwargs):
        """Run agent with 4-layer validation and retry logic."""
        attempt = 0
        last_error = None

        while attempt < max_retries:
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries}: Generating {model_type_code.value} ROI model...")

                # Run agent
                response = original_run(message, **run_kwargs)

                # Extract text content
                if hasattr(response, 'content'):
                    response_text = response.content
                else:
                    response_text = str(response)

                response_length = len(str(response_text))
                logger.debug(f"Response type: {type(response)}, length: {response_length:,} characters")

                # Expected response size: 10KB-50KB for complete ROI model
                if response_length < 5000:
                    logger.warning(f"Response seems short ({response_length} chars) for complete ROI model")

                # LAYER 1: Extract JSON
                try:
                    json_str = extract_json_from_response(response_text)
                    logger.debug(f"✅ Layer 1: JSON extracted ({len(json_str):,} characters)")
                except ValueError as e:
                    raise ValueError(f"JSON extraction failed: {e}")

                # LAYER 2: Parse JSON
                try:
                    data_dict = json.loads(json_str)
                    logger.debug(f"✅ Layer 2: JSON parsed ({len(data_dict)} top-level keys)")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON syntax: {e}")

                # LAYER 3: Validate with Pydantic
                try:
                    result = ROIModelJSON(**data_dict)
                    logger.info("✅ Layer 3: Pydantic validation passed")

                    # LAYER 4: Business rule validation
                    validation = validate_roi_model(result)

                    logger.info(f"Layer 4 validation: {len(validation['errors'])} errors, {len(validation['warnings'])} warnings")

                    if validation['valid']:
                        logger.info(f"✅ Layer 4: Business rule validation passed")
                        logger.info(f"✅ ROI model generation successful on attempt {attempt + 1}")
                        logger.info(f"Model stats: {validation['info']}")
                        return result
                    else:
                        # Validation failed - prepare feedback
                        error_msg = "ROI Model validation errors:\n"
                        for error in validation['errors']:
                            error_msg += f"  ❌ {error}\n"
                        for warning in validation['warnings']:
                            error_msg += f"  ⚠️  {warning}\n"

                        logger.warning(f"Layer 4 validation failed on attempt {attempt + 1}:\n{error_msg}")

                        feedback_message = f"""
{message}

## PREVIOUS ATTEMPT FEEDBACK (Attempt {attempt + 1})

Your previous ROI model output had validation errors. Please fix these issues:

{error_msg}

Generate corrected ROI model JSON that addresses all errors above.
Ensure all components are complete and all validation rules are satisfied.
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

                    error_summary = "\n".join(error_details)
                    logger.error(f"Layer 3: Pydantic validation failed:\n{error_summary}")

                    raise ValueError(f"Pydantic validation failed:\n{error_summary}")

            except (ValueError, json.JSONDecodeError, ValidationError) as e:
                logger.error(f"Parsing/Validation error on attempt {attempt + 1}: {e}")
                last_error = str(e)
                attempt += 1

                if attempt < max_retries:
                    message = f"""
{message}

## PREVIOUS ATTEMPT ERROR (Attempt {attempt})

An error occurred while parsing/validating your response: {str(e)}

Please fix the error and return ONLY a valid JSON object matching the ROIModelJSON schema.
Ensure ALL 15 components are present and fully populated:
1. model_metadata
2. executive_summary
3. data_requirements
4. population_identification
5. baseline_methodology
6. calculation_components
7. sql_components
8. output_metrics
9. assumptions
10. validation_rules
11. confidence_factors
12. configurable_parameters
13. dashboard_templates
14. episode_definition (if B7)

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

Please try again and ensure the output is valid JSON matching the ROIModelJSON schema with all 15 components.
"""

        # Max retries exceeded
        logger.error(f"ROI model generation failed after {max_retries} attempts. Last error: {last_error}")
        raise RuntimeError(
            f"ROI model generation for {model_type_code.value} failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

    agent.run = run_with_retry

    logger.info(f"Created {name} with 4-layer validation and retry logic (max_retries={max_retries})")

    return agent


# ============================================================================
# CONVENIENCE FUNCTION FOR END-TO-END GENERATION
# ============================================================================

def generate_roi_model_from_research(
    model_type_code: ModelTypeCode,
    client_name: str,
    research_summary: str,
    model: Any = None,
    max_retries: int = 3,
    prompts_base_path: Optional[Path] = None
) -> ROIModelJSON:
    """
    Convenience function to generate ROI model from research data.

    Args:
        model_type_code: ROI model type (B1-B13)
        client_name: Client organization name
        research_summary: Summary of research findings (web search + document analysis)
        model: LLM model instance (if None, uses default)
        max_retries: Maximum retry attempts
        prompts_base_path: Optional path to prompt repository

    Returns:
        Validated ROIModelJSON instance

    Raises:
        RuntimeError: If generation fails after retries
    """
    agent = create_roi_model_builder_with_retry(
        model_type_code=model_type_code,
        model=model,
        max_retries=max_retries,
        prompts_base_path=prompts_base_path
    )

    message = f"""
# ROI Model Generation Request

**Client Name**: {client_name}
**Model Type**: {model_type_code.value}

## Research Summary

{research_summary}

---

Generate a complete ROI Model JSON for this client based on the research summary above.
Ensure all 15 components are fully populated with realistic, detailed content appropriate for {model_type_code.value}.

Return ONLY the JSON object.
"""

    result = agent.run(message)

    logger.info(f"ROI model generated for {client_name}: {model_type_code.value}")

    return result
