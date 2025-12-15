"""Configuration settings for Mare Agno."""
from pydantic import Field
from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path


class DatabaseConfig(BaseSettings):
    """PostgreSQL database configuration."""
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    # PostgreSQL configuration
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="triton", env="POSTGRES_USER")
    postgres_password: str = Field(default="triton_password", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="triton_db", env="POSTGRES_DB")
    postgres_schema: str = Field(default="public", env="POSTGRES_SCHEMA")

    # Connection pool settings
    pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    def get_database_url(self) -> str:
        """Get database URL for SQLAlchemy/Alembic."""
        return self.postgres_url


class RedshiftConfig(BaseSettings):
    """Redshift database configuration."""
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    # Redshift connection settings
    redshift_host: Optional[str] = Field(default=None, env="REDSHIFT_HOST")
    redshift_port: int = Field(default=5439, env="REDSHIFT_PORT")
    redshift_database: Optional[str] = Field(default=None, env="REDSHIFT_DATABASE")
    redshift_user: Optional[str] = Field(default=None, env="REDSHIFT_USER")
    redshift_password: Optional[str] = Field(default=None, env="REDSHIFT_PASSWORD")
    redshift_schema: str = Field(default="public", env="REDSHIFT_SCHEMA")

    # Data API settings (for serverless access without direct connection)
    redshift_cluster_id: Optional[str] = Field(default=None, env="REDSHIFT_CLUSTER_ID")
    redshift_secret_arn: Optional[str] = Field(default=None, env="REDSHIFT_SECRET_ARN")

    # IAM role for COPY command
    redshift_iam_role: Optional[str] = Field(default=None, env="REDSHIFT_IAM_ROLE_ARN")

    # Connection pool settings
    redshift_min_connections: int = Field(default=1, env="REDSHIFT_MIN_CONNECTIONS")
    redshift_max_connections: int = Field(default=5, env="REDSHIFT_MAX_CONNECTIONS")
    redshift_connection_timeout: int = Field(default=30, env="REDSHIFT_CONNECTION_TIMEOUT")

    @property
    def redshift_url(self) -> Optional[str]:
        """Get Redshift connection URL."""
        if not all([self.redshift_host, self.redshift_user, self.redshift_password, self.redshift_database]):
            return None
        return f"postgresql://{self.redshift_user}:{self.redshift_password}@{self.redshift_host}:{self.redshift_port}/{self.redshift_database}"


class ModelConfig(BaseSettings):
    """Model configuration."""
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")

    default_model_provider: str = Field(default="anthropic", env="DEFAULT_MODEL_PROVIDER")
    default_model_name: str = Field(default="claude-sonnet-4-5-20250929-v1:0", env="DEFAULT_MODEL_NAME")

    aws_profile: Optional[str] = Field(default="mare-dev", env="AWS_PROFILE")
    aws_region: Optional[str] = Field(default="us-east-1", env="AWS_REGION")

class KnowledgeConfig(BaseSettings):
    """Knowledge base configuration."""

class PromptRepositoryConfig(BaseSettings):
    """Prompt repository configuration for ROI model generation."""
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    # Prompt repository path
    prompts_repo_path: Optional[str] = Field(default=None, env="PROMPTS_REPO_PATH")

    @property
    def model_prompts_dir(self) -> Path:
        """Get directory containing ROI model prompts (B1-B13)."""
        if self.prompts_repo_path:
            base_path = Path(self.prompts_repo_path)
        else:
            # Default: assume mare-triton-research-prompts is sibling directory
            base_path = Path(__file__).parent.parent.parent.parent / "mare-triton-research-prompts"

        prompts_dir = base_path / "prompts" / "roi_models"

        if not prompts_dir.exists():
            # Fallback to local prompts directory
            prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "roi_models"

        return prompts_dir

    @property
    def classification_prompt_path(self) -> Path:
        """Get path to ROI classification prompt."""
        if self.prompts_repo_path:
            base_path = Path(self.prompts_repo_path)
        else:
            base_path = Path(__file__).parent.parent.parent.parent / "mare-triton-research-prompts"

        prompt_path = base_path / "prompts" / "roi_type.md"

        if not prompt_path.exists():
            # Fallback to local templates
            prompt_path = Path(__file__).parent.parent.parent / "agents" / "templates" / "roi_classification_instructions.md"

        return prompt_path

class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration."""
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    log_dir: str = Field(default="logs", env="LOG_DIR")


class SecurityConfig(BaseSettings):
    """Security configuration."""


class CeleryConfig(BaseSettings):
    """Celery task queue configuration."""
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    # Redis broker configuration
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # Celery settings
    celery_task_track_started: bool = Field(default=True, env="CELERY_TASK_TRACK_STARTED")
    celery_task_time_limit: int = Field(default=1800, env="CELERY_TASK_TIME_LIMIT")  # 30 minutes
    celery_task_soft_time_limit: int = Field(default=1500, env="CELERY_TASK_SOFT_TIME_LIMIT")  # 25 minutes
    celery_worker_prefetch_multiplier: int = Field(default=1, env="CELERY_WORKER_PREFETCH_MULTIPLIER")
    celery_worker_max_tasks_per_child: int = Field(default=100, env="CELERY_WORKER_MAX_TASKS_PER_CHILD")

    @property
    def broker_url(self) -> str:
        """Get Celery broker URL (Redis)."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def result_backend(self) -> str:
        """Get Celery result backend URL (Redis)."""
        return self.broker_url


class MareConfig(BaseSettings):
    """Main configuration for Agno Mare."""
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG_MODE")
    debug_mode: bool = Field(default=True, env="DEBUG_MODE")  # Alias for compatibility

    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redshift: RedshiftConfig = Field(default_factory=RedshiftConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    prompts: PromptRepositoryConfig = Field(default_factory=PromptRepositoryConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    celery: CeleryConfig = Field(default_factory=CeleryConfig)

    # application settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

def get_config() -> MareConfig:
    """Get the global configuration instance."""
    return MareConfig()


# Global configuration instance
config = get_config()