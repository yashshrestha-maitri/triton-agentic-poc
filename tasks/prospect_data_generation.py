"""
Celery tasks for prospect dashboard data generation.

This module contains tasks that:
1. Load prospect and client context from PostgreSQL
2. Load dashboard templates for the client
3. Generate synthetic data for all widgets in each template
4. Store generated data in prospect_dashboard_data table
5. Track job status and publish events to Redis
"""

import time
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from celery import Task
from sqlalchemy.orm import Session

from core.database.database import get_celery_db_session
from core.database.models import (
    DashboardTemplate,
    Prospect,
    ProspectDashboardData,
    ProspectDataJob,
)
from core.monitoring.logger import get_logger
from core.services.data_generator import generate_prospect_dashboard_data
from core.services.event_publisher import get_event_publisher
from worker import celery_app

logger = get_logger(__name__)


# =============================================================================
# Custom Task Class with Error Handling
# =============================================================================


class ProspectDataGenerationTask(Task):
    """Custom Celery task class with error handling and retries."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 60}  # Retry after 60 seconds
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes between retries
    retry_jitter = True


# =============================================================================
# Prospect Data Generation Task
# =============================================================================


@celery_app.task(
    bind=True,
    base=ProspectDataGenerationTask,
    name="tasks.prospect_data_generation.generate_prospect_data",
)
def generate_prospect_data_task(
    self,
    job_id: str,
    prospect_id: str,
    template_id: Optional[str] = None,
    regenerate: bool = False,
) -> Dict:
    """
    Generate dashboard data for a prospect.

    Two modes:
    1. If template_id provided: Generate for that specific template
    2. If template_id is None: Generate for ALL templates belonging to prospect's client

    Args:
        self: Celery task instance (bound)
        job_id: UUID of the prospect data job
        prospect_id: UUID of the prospect
        template_id: Optional UUID of specific template
        regenerate: Force regeneration even if data exists

    Returns:
        Dict with job results (prospect_data_ids, total_templates, etc.)

    Raises:
        Exception: On database errors or generation failures
    """
    start_time = time.time()
    session: Session = None

    try:
        # Create database session
        session = get_celery_db_session()

        logger.info(
            f"Starting prospect data generation task [job_id={job_id}, prospect_id={prospect_id}, "
            f"template_id={template_id}, regenerate={regenerate}]"
        )

        # Update job status to running
        job = session.query(ProspectDataJob).filter(ProspectDataJob.id == UUID(job_id)).first()
        if not job:
            raise ValueError(f"Prospect data job not found: {job_id}")

        job.status = "running"
        job.started_at = datetime.utcnow()
        job.celery_task_id = self.request.id
        session.commit()

        # Publish job started event
        try:
            publisher = get_event_publisher()
            publisher.publish_job_event(
                "job:started",
                {
                    "job_id": job_id,
                    "prospect_id": prospect_id,
                    "status": "running",
                    "started_at": job.started_at.isoformat(),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to publish job:started event: {e}")

        # =============================================================================
        # Step 1: Load prospect and client context
        # =============================================================================

        prospect = session.query(Prospect).filter(Prospect.id == UUID(prospect_id)).first()
        if not prospect:
            raise ValueError(f"Prospect not found: {prospect_id}")

        client_id = prospect.client_id
        logger.info(f"Loaded prospect: {prospect.name} (client_id={client_id})")

        # =============================================================================
        # Step 2: Determine templates to generate
        # =============================================================================

        if template_id:
            # Single template mode
            templates = [
                session.query(DashboardTemplate)
                .filter(DashboardTemplate.id == UUID(template_id))
                .first()
            ]
            if not templates[0]:
                raise ValueError(f"Template not found: {template_id}")
            logger.info(f"Single template mode: {templates[0].name}")
        else:
            # All client templates mode
            templates = (
                session.query(DashboardTemplate)
                .filter(DashboardTemplate.client_id == client_id)
                .all()
            )
            if not templates:
                raise ValueError(f"No templates found for client {client_id}")
            logger.info(f"Batch mode: {len(templates)} templates found for client")

        # =============================================================================
        # Step 3: Generate data for each template
        # =============================================================================

        generated_data_ids = []
        template_ids = []
        errors = []
        successful = 0
        failed = 0

        for idx, template in enumerate(templates, 1):
            try:
                logger.info(
                    f"Processing template {idx}/{len(templates)}: {template.name} "
                    f"(template_id={template.id})"
                )

                # Check if data already exists
                existing_data = (
                    session.query(ProspectDashboardData)
                    .filter(ProspectDashboardData.prospect_id == UUID(prospect_id))
                    .filter(ProspectDashboardData.template_id == template.id)
                    .first()
                )

                # Skip if exists and regenerate not requested
                if existing_data and not regenerate:
                    logger.info(f"Data already exists for template {template.id}, skipping...")
                    continue

                # Prepare template data for generator
                template_dict = {
                    "id": str(template.id),
                    "name": template.name,
                    "widgets": template.widgets,
                    "category": template.category,
                    "target_audience": template.target_audience,
                }

                # Generate widget data
                logger.info(f"Generating widget data for: {template.name}")
                prospect_data = generate_prospect_dashboard_data(
                    template=template_dict, prospect_id=UUID(prospect_id)
                )

                # Update existing or create new
                if existing_data:
                    existing_data.dashboard_data = prospect_data["dashboard_data"]
                    existing_data.validation_result = prospect_data.get("validation_result")
                    existing_data.generated_at = prospect_data["generated_at"]
                    existing_data.generation_duration_ms = prospect_data["generation_duration_ms"]
                    existing_data.generated_by = prospect_data["generated_by"]
                    existing_data.status = prospect_data["status"]
                    db_data = existing_data
                else:
                    db_data = ProspectDashboardData(
                        prospect_id=UUID(prospect_id),
                        template_id=template.id,
                        dashboard_data=prospect_data["dashboard_data"],
                        validation_result=prospect_data.get("validation_result"),
                        generated_at=prospect_data["generated_at"],
                        generation_duration_ms=prospect_data["generation_duration_ms"],
                        generated_by=prospect_data["generated_by"],
                        status=prospect_data["status"],
                    )
                    session.add(db_data)

                session.flush()
                generated_data_ids.append(str(db_data.id))
                template_ids.append(str(template.id))
                successful += 1

                logger.info(
                    f"✅ Generated data for template {template.name}: "
                    f"data_id={db_data.id}, template_id={template.id}, widgets={len(template.widgets)}"
                )

            except Exception as e:
                failed += 1
                error_details = {
                    "template_id": str(template.id),
                    "template_name": template.name,
                    "error": str(e),
                }
                errors.append(error_details)
                logger.error(
                    f"Failed to generate data for template {template.name}: {e}",
                    exc_info=True,
                )
                # Continue with other templates

        session.commit()

        logger.info(
            f"Data generation completed: {successful} successful, {failed} failed "
            f"out of {len(templates)} templates"
        )

        # =============================================================================
        # Step 4: Update job status to completed
        # =============================================================================

        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.generation_duration_ms = int((time.time() - start_time) * 1000)
        job.result_summary = {
            "total_templates": len(templates),
            "successful": successful,
            "failed": failed,
            "generated_data_ids": generated_data_ids,
            "template_ids": template_ids,
            "errors": errors,
        }
        session.commit()

        # Publish job completed event
        try:
            publisher = get_event_publisher()
            publisher.publish_job_event(
                "job:completed",
                {
                    "job_id": job_id,
                    "prospect_id": prospect_id,
                    "status": "completed",
                    "total_templates": len(templates),
                    "successful": successful,
                    "failed": failed,
                    "generation_duration_ms": job.generation_duration_ms,
                    "completed_at": job.completed_at.isoformat(),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to publish job:completed event: {e}")

        logger.info(
            f"Prospect data generation completed successfully [job_id={job_id}, "
            f"prospect_id={prospect_id}, successful={successful}/{len(templates)}, "
            f"duration={job.generation_duration_ms}ms]"
        )

        return {
            "job_id": job_id,
            "prospect_id": prospect_id,
            "client_id": str(client_id),
            "status": "completed",
            "total_templates": len(templates),
            "successful": successful,
            "failed": failed,
            "generated_data_ids": generated_data_ids,
            "template_ids": template_ids,
            "errors": errors,
            "generation_duration_ms": job.generation_duration_ms,
        }

    except Exception as e:
        logger.error(
            f"Prospect data generation failed [job_id={job_id}]: {str(e)}", exc_info=True
        )

        # Update job status to failed
        if session and job:
            try:
                job.status = "failed"
                job.completed_at = datetime.utcnow()
                job.error_message = str(e)
                job.generation_duration_ms = int((time.time() - start_time) * 1000)

                # Publish job failed event
                try:
                    publisher = get_event_publisher()
                    publisher.publish_job_event(
                        "job:failed",
                        {
                            "job_id": job_id,
                            "prospect_id": prospect_id,
                            "status": "failed",
                            "error_message": str(e),
                            "generation_duration_ms": job.generation_duration_ms,
                            "completed_at": job.completed_at.isoformat(),
                        },
                    )
                except Exception as publish_error:
                    logger.warning(f"Failed to publish job:failed event: {publish_error}")

                session.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update job status: {commit_error}")
                session.rollback()

        raise

    finally:
        # Clean up database session
        if session:
            session.close()
