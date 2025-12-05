"""
Celery worker configuration and entry point for Triton Agentic.

This module initializes the Celery application and registers all tasks.
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from celery import Celery
from celery.signals import task_failure, task_postrun, task_prerun, task_success

from core.config.settings import get_config
from core.monitoring.logger import get_logger

# Initialize configuration and logger
config = get_config()
logger = get_logger(__name__)

# =============================================================================
# Celery Application Configuration
# =============================================================================

# Create Celery app
celery_app = Celery("triton_agentic")

# Configure Celery
celery_app.conf.update(
    # Broker and backend
    broker_url=config.celery.broker_url,
    result_backend=config.celery.result_backend,
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution
    task_track_started=config.celery.celery_task_track_started,
    task_time_limit=config.celery.celery_task_time_limit,
    task_soft_time_limit=config.celery.celery_task_soft_time_limit,
    # Worker settings
    worker_prefetch_multiplier=config.celery.celery_worker_prefetch_multiplier,
    worker_max_tasks_per_child=config.celery.celery_worker_max_tasks_per_child,
    # Result backend settings
    result_expires=3600 * 24 * 7,  # 7 days
    result_persistent=True,
    # Task routing (disabled for now - using default celery queue)
    # task_routes={
    #     "tasks.template_generation.*": {"queue": "template_generation"},
    #     "tasks.data_generation.*": {"queue": "data_generation"},
    # },
    # Task acknowledgement
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Import tasks explicitly to ensure they're registered
try:
    import tasks.template_generation
    import tasks.prospect_data_generation
    logger.info("Successfully imported tasks.template_generation")
    logger.info("Successfully imported tasks.prospect_data_generation")
except ImportError as e:
    logger.error(f"Failed to import tasks: {e}")
    raise

# Auto-discover tasks in the 'tasks' module
celery_app.autodiscover_tasks(["tasks"])

# =============================================================================
# Celery Signal Handlers for Monitoring
# =============================================================================


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Log when a task starts."""
    logger.info(f"Task started: {task.name} [task_id={task_id}]")


@task_postrun.connect
def task_postrun_handler(
    sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **extra
):
    """Log when a task completes."""
    logger.info(f"Task completed: {task.name} [task_id={task_id}, state={state}]")


@task_success.connect
def task_success_handler(sender=None, result=None, **extra):
    """Log successful task completion."""
    logger.info(f"Task succeeded: {sender.name}")


@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extra
):
    """Log task failures."""
    logger.error(
        f"Task failed: {sender.name} [task_id={task_id}]",
        extra={
            "exception": str(exception),
            "traceback": str(traceback),
            "args": args,
            "kwargs": kwargs,
        },
    )


# =============================================================================
# Celery Tasks Module
# =============================================================================

# Tasks are defined in the 'tasks/' directory and auto-discovered by Celery
# Available task modules:
# - tasks.template_generation: Template generation tasks
# - tasks.prospect_data_generation: Prospect dashboard data generation tasks

if __name__ == "__main__":
    celery_app.start()
