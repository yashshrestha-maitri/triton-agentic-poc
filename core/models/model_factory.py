"""Model factory for creating LLM instances from configuration."""

from typing import Optional, Any
from core.config.settings import config
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


class ModelFactory:
    """Factory class for creating LLM model instances."""

    @staticmethod
    def create_model(
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Create a model instance based on provider and configuration.

        Args:
            provider: Model provider (openai, anthropic, google, groq, aws_bedrock)
            model_name: Specific model name/ID
            **kwargs: Additional model parameters

        Returns:
            Model instance configured for the specified provider
        """
        provider = provider or config.models.default_model_provider
        model_name = model_name or config.models.default_model_name

        logger.info(f"Creating model: {provider}/{model_name}")

        if provider == "openai":
            return ModelFactory._create_openai_model(model_name, **kwargs)
        elif provider == "anthropic":
            return ModelFactory._create_anthropic_model(model_name, **kwargs)
        elif provider == "google":
            return ModelFactory._create_google_model(model_name, **kwargs)
        elif provider == "groq":
            return ModelFactory._create_groq_model(model_name, **kwargs)
        elif provider == "aws_bedrock":
            return ModelFactory._create_aws_bedrock_model(model_name, **kwargs)
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

    @staticmethod
    def _create_openai_model(model_name: str, **kwargs) -> Any:
        """Create OpenAI model instance."""
        from agno.models.openai import OpenAIChat

        return OpenAIChat(
            id=model_name,
            api_key=config.models.openai_api_key,
            **kwargs
        )

    @staticmethod
    def _create_anthropic_model(model_name: str, **kwargs) -> Any:
        """Create Anthropic model instance."""
        from agno.models.anthropic import Claude

        return Claude(
            id=model_name,
            api_key=config.models.anthropic_api_key,
            **kwargs
        )

    @staticmethod
    def _create_google_model(model_name: str, **kwargs) -> Any:
        """Create Google AI model instance."""
        from agno.models.google import Gemini

        return Gemini(
            id=model_name,
            api_key=config.models.google_api_key,
            **kwargs
        )

    @staticmethod
    def _create_groq_model(model_name: str, **kwargs) -> Any:
        """Create Groq model instance."""
        from agno.models.groq import Groq

        return Groq(
            id=model_name,
            api_key=config.models.groq_api_key,
            **kwargs
        )

    @staticmethod
    def _create_aws_bedrock_model(model_name: str, **kwargs) -> Any:
        """Create AWS Bedrock model instance with workarounds for Agno bugs."""
        from agno.models.aws import Claude
        from typing import Dict, Any as AnyType

        # Create the model
        model = Claude(
            id=model_name,
            aws_region=config.models.aws_region,
            **kwargs
        )

        # CRITICAL FIX #1: AWS Bedrock doesn't actually support response_format despite Agno's incorrect defaults
        model.supports_native_structured_outputs = False
        model.supports_json_schema_outputs = False

        # CRITICAL FIX #2: AWS Bedrock's get_request_params() doesn't accept response_format parameter
        # but Agno's Agent class calls it with that parameter anyway.
        # Monkey-patch to accept and ignore response_format
        original_get_request_params = model.get_request_params

        def patched_get_request_params(response_format=None, **extra_kwargs) -> Dict[str, AnyType]:
            """Patched version that accepts response_format but ignores it."""
            # Call original method without response_format
            return original_get_request_params()

        model.get_request_params = patched_get_request_params

        logger.info(f"AWS Bedrock model configured with response_format workaround")

        return model


def get_default_model(**kwargs) -> Any:
    """
    Get the default model configured in settings.

    Returns:
        Default model instance
    """
    return ModelFactory.create_model(**kwargs)
