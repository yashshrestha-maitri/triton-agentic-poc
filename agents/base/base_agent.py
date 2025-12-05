"""Base agent class for all agents."""

import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional, List
from contextlib import contextmanager
from pathlib import Path

from agno.tools import Toolkit
from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.memory.manager import MemoryManager

from core.config.settings import config
from core.monitoring.logger import get_logger
from core.monitoring.logger import record_agent_execution, metrics
from core.registry.service_registry import register_agent_service, ServiceStatus, service_registry
from core.registry.service_setup import setup_mare_service

logger = get_logger(__name__)

class MareBaseAgent:
    """Base class for all agents in the Mare framework."""

    def __init__(self, *args, **kwargs):
        """Initialize the base agent with given arguments."""
        super().__init__(*args, **kwargs)
        self._mare_agent_initialized = False
        self._service_info = None
        self._setup_mare_features()

    def _setup_mare_features(self):
        """Set up Mare-specific features for the agent using shared utility."""
        self._service_info = setup_mare_service(
            instance=self,
            service_type="agent",
            register_func=register_agent_service,
            initialized_attr="_mare_agent_initialized",
            service_info_attr="_service_info"
        )
    
    @contextmanager
    def _execution_timer(self, operation: str = "execution"):
        """Context manager to time the execution of a block of code."""
        start_time = time.time()
        agent_name = getattr(self, 'name', 'unknown')

        with metrics.timer(f"agent_{operation}_duration", {"agent": agent_name}):
            try:
                yield
                success = True
            except Exception as e:
                success = False
                logger.error(f"Error during operation '{operation}' for agent '{agent_name}': {e}")
                raise
            finally:
                end_time = time.time()
                elapsed_time = end_time - start_time
                record_agent_execution(agent_name, elapsed_time, success)
            
    def run(self, message: Optional[str] = None, **kwargs):
        """Run the agent with the given message and return a response."""
        # Handle both positional and keyword argument for message
        if message is None and 'message' in kwargs:
            message = kwargs.pop('message')

        # Note: response_model is NOT passed to parent run() to avoid AWS Bedrock compatibility issues
        # Manual JSON parsing and Pydantic validation is handled in the retry wrapper instead

        with self._execution_timer("run"):
            # Call parent run method with appropriate arguments
            if message is not None:
                return super().run(message, **kwargs)
            else:
                return super().run(**kwargs)
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status."""
        return {
            "agent_id": getattr(self, 'agent_id', 'unknown'),
            "name": getattr(self, 'name', 'Unknown'),
            "status": "healthy",  # Could be enhanced with actual health checks
            "last_activity": datetime.utcnow().isoformat(),
            "service_info": self._service_info.__dict__ if self._service_info else None
        }

class MareAgent(MareBaseAgent, Agent):
    """Mare agent class that extends the base agent and Agno's Agent."""

    def __init__(self,
                  name: str,
                  model: Any,
                  agent_id: Optional[str] = None,
                  description: Optional[str] = None,
                  instructions: Optional[str] = None,
                  tools: Optional[List[Toolkit]] = None,
                  db: Optional[PostgresDb] = None,
                  knowledge: Optional[Knowledge] = None,
                  memory: Optional[MemoryManager] = None,
                  add_history_to_context: bool = True,
                  num_history_runs: int = 3,
                  **kwargs):

        # Set agent_id before calling parent constructors
        self.agent_id = agent_id or name.lower().replace(" ", "_")

        # Note: response_model parameter completely removed for AWS Bedrock compatibility
        # Manual JSON parsing and Pydantic validation happens in retry wrapper

        """Initialize the Mare agent."""
        super().__init__(
            name=name,
            model=model,
            id=self.agent_id,
            description=description,
            instructions=instructions,
            tools=tools,
            db=db,
            knowledge=knowledge,
            memory_manager=memory,
            add_history_to_context=add_history_to_context,
            num_history_runs=num_history_runs,
            debug_mode=config.debug_mode,
            **kwargs)


class BaseAgentTemplate(ABC):
    """Abstract base class for agent templates."""

    def __init__(self):
        """Initialize the agent template."""
        self._allowed_s3_paths = None  # Will be set from agent_config
        self.template_dir = Path(__file__).parent.parent / "templates"
        self._instruction_cache = {}  # Cache for loaded instruction files

    def _load_instruction_file(self, filename: str, cache_key: Optional[str] = None) -> str:
        """Load instruction file with caching support.

        Args:
            filename: Name of the file to load (relative to templates directory)
            cache_key: Optional custom cache key (defaults to filename)

        Returns:
            File contents as string, or empty string if file not found
        """
        key = cache_key or filename
        if key not in self._instruction_cache:
            file_path = self.template_dir / filename
            if file_path.exists():
                self._instruction_cache[key] = file_path.read_text()
                logger.debug(f"Loaded instruction file: {filename}")
            else:
                logger.warning(f"Instruction file not found: {file_path}")
                self._instruction_cache[key] = ""
        return self._instruction_cache[key]

    def create_agent(
        self,
        name: str,
        model: Any,
        **kwargs
    ) -> MareAgent:
        """Create an agent instance from this template."""
        config_dict = self.get_agent_config()

        # Extract agent_config for template use (don't pass to Agent)
        agent_config = kwargs.pop('agent_config', None)
        if agent_config and isinstance(agent_config, dict):
            self._allowed_s3_paths = agent_config.get('allowed_s3_paths')

        return MareAgent(
            name=name,
            model=model,
            description=self.get_description(),
            instructions=self.get_instructions(),
            tools=self.get_tools(),
            **{**config_dict, **kwargs}
        )

    @abstractmethod
    def get_agent_config(self) -> Dict[str, Any]:
        """Get the configuration for the agent."""
        pass    

    @abstractmethod
    def get_tools(self) -> List[Toolkit]:
        """Get the list of tools available to the agent."""
        pass

    @abstractmethod
    def get_instructions(self) -> str:
        """Get the instructions for the agent."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get the description of the agent."""
        pass