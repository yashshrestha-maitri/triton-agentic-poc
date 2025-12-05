"""
Redis Pub/Sub event publisher for job status updates.

Publishes job lifecycle events to Redis channels for real-time notifications.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional

import redis

from core.config.settings import config
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


class EventPublisher:
    """
    Publishes job events to Redis Pub/Sub channels.

    Events are published to two channels:
    - triton:jobs:all - All job events (for global listeners)
    - triton:jobs:{job_id} - Job-specific events (for targeted listeners)
    """

    def __init__(self):
        """Initialize Redis publisher connection."""
        try:
            # Build Redis connection URL
            auth = f":{config.celery.redis_password}@" if config.celery.redis_password else ""
            redis_url = f"redis://{auth}{config.celery.redis_host}:{config.celery.redis_port}/{config.celery.redis_db}"

            # Create Redis client (synchronous for Celery workers)
            self.redis_client = redis.Redis(
                host=config.celery.redis_host,
                port=config.celery.redis_port,
                db=config.celery.redis_db,
                password=config.celery.redis_password if config.celery.redis_password else None,
                decode_responses=True,  # Automatically decode bytes to strings
            )

            # Test connection
            self.redis_client.ping()
            logger.info(
                f"Event publisher connected to Redis at "
                f"{config.celery.redis_host}:{config.celery.redis_port}"
            )

        except Exception as e:
            logger.error(f"Failed to connect to Redis for event publishing: {e}")
            raise

    def publish_job_event(self, event_type: str, job_data: Dict[str, Any]) -> None:
        """
        Publish job status event to Redis Pub/Sub channels.

        Args:
            event_type: Type of event (e.g., "job:started", "job:completed", "job:failed")
            job_data: Event payload data (must include job_id)

        Publishes to:
            - triton:jobs:all - All job events
            - triton:jobs:{job_id} - Specific job events
        """
        try:
            # Build event payload
            event_payload = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                **job_data,
            }

            # Serialize to JSON
            event_json = json.dumps(event_payload)

            # Publish to general channel (all jobs)
            subscribers_all = self.redis_client.publish("triton:jobs:all", event_json)

            # Publish to job-specific channel
            job_id = job_data.get("job_id")
            subscribers_job = 0
            if job_id:
                subscribers_job = self.redis_client.publish(
                    f"triton:jobs:{job_id}", event_json
                )

            logger.info(
                f"Published event '{event_type}' for job {job_id} "
                f"(all: {subscribers_all} subscribers, job: {subscribers_job} subscribers)"
            )

        except Exception as e:
            logger.error(f"Failed to publish event '{event_type}': {e}", exc_info=True)
            # Don't raise - event publishing should not break job execution

    def publish_template_generated(
        self, job_id: str, client_id: str, template_ids: list[str]
    ) -> None:
        """
        Convenience method: Publish template generation completion event.

        Args:
            job_id: Job UUID
            client_id: Client UUID
            template_ids: List of generated template UUIDs
        """
        self.publish_job_event(
            "job:completed",
            {
                "job_id": job_id,
                "client_id": client_id,
                "status": "completed",
                "template_ids": template_ids,
                "template_count": len(template_ids),
            },
        )

    def publish_job_failed(
        self, job_id: str, client_id: str, error_message: str
    ) -> None:
        """
        Convenience method: Publish job failure event.

        Args:
            job_id: Job UUID
            client_id: Client UUID
            error_message: Error description
        """
        self.publish_job_event(
            "job:failed",
            {
                "job_id": job_id,
                "client_id": client_id,
                "status": "failed",
                "error_message": error_message,
            },
        )

    def publish_data_generated(
        self, job_id: str, client_id: str, prospect_id: str, data_record_count: int
    ) -> None:
        """
        Publish prospect data generation completion event.

        Args:
            job_id: Job UUID
            client_id: Client UUID
            prospect_id: Prospect UUID
            data_record_count: Number of data records generated
        """
        self.publish_job_event(
            "data:generated",
            {
                "job_id": job_id,
                "client_id": client_id,
                "prospect_id": prospect_id,
                "data_record_count": data_record_count,
            },
        )

    def close(self) -> None:
        """Close Redis connection."""
        try:
            self.redis_client.close()
            logger.info("Event publisher connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")


# =============================================================================
# Global Singleton Instance
# =============================================================================

_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """
    Get singleton event publisher instance.

    Returns:
        EventPublisher instance (creates if not exists)
    """
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()
    return _publisher


def close_event_publisher() -> None:
    """Close global event publisher connection."""
    global _publisher
    if _publisher is not None:
        _publisher.close()
        _publisher = None
