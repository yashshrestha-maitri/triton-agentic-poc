"""
Celery tasks for dashboard template generation.

This module contains tasks that:
1. Load client and value proposition context from PostgreSQL
2. Invoke the template generation agent
3. Save generated templates back to PostgreSQL
4. Track job status and execution logs
"""

import time
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from celery import Task
from sqlalchemy.orm import Session

from agents.template_generator_agent import create_template_generator_with_retry
from core.database.database import get_celery_db_session
from core.database.models import (
    AgentExecutionLog,
    Client,
    DashboardTemplate,
    GenerationJob,
    ValueProposition,
    ProspectDashboardData,
)
from core.models.template_models import SingleTemplateResult, TemplateGenerationResult
from core.monitoring.logger import get_logger
from core.services.prospect_service import get_or_create_demo_prospect
from core.services.data_generator import generate_prospect_dashboard_data
from core.services.event_publisher import get_event_publisher
from worker import celery_app

logger = get_logger(__name__)


# =============================================================================
# Custom Task Class with Error Handling
# =============================================================================


class TemplateGenerationTask(Task):
    """Custom Celery task class with error handling and retries."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 60}  # Retry after 60 seconds
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes between retries
    retry_jitter = True


# =============================================================================
# Template Generation Task
# =============================================================================


@celery_app.task(
    bind=True,
    base=TemplateGenerationTask,
    name="tasks.template_generation.generate_templates",
)
def generate_templates_task(
    self,
    job_id: str,
    client_id: str,
    value_proposition_id: Optional[str] = None,
) -> Dict:
    """
    Generate dashboard templates for a client based on their value proposition.

    This task:
    1. Loads client and value proposition from PostgreSQL
    2. Invokes the template generation agent with context
    3. Validates and saves generated templates to PostgreSQL
    4. Updates job status and logs execution metrics

    Args:
        self: Celery task instance (bound)
        job_id: UUID of the generation job
        client_id: UUID of the client
        value_proposition_id: Optional UUID of specific value proposition

    Returns:
        Dict with job results (template_ids, generation_time, etc.)

    Raises:
        Exception: On database errors, agent failures, or validation errors
    """
    start_time = time.time()
    session: Session = None

    try:
        # Create database session
        session = get_celery_db_session()

        logger.info(
            f"Starting template generation task [job_id={job_id}, client_id={client_id}, "
            f"value_proposition_id={value_proposition_id}]"
        )

        # Update job status to running
        job = session.query(GenerationJob).filter(GenerationJob.id == UUID(job_id)).first()
        if not job:
            raise ValueError(f"Generation job not found: {job_id}")

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
                    "client_id": client_id,
                    "status": "running",
                    "started_at": job.started_at.isoformat(),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to publish job:started event: {e}")

        # =============================================================================
        # Step 1: Load context from PostgreSQL
        # =============================================================================

        client = session.query(Client).filter(Client.id == UUID(client_id)).first()
        if not client:
            raise ValueError(f"Client not found: {client_id}")

        # Get value proposition (use specific one or most recent active)
        if value_proposition_id:
            value_prop = (
                session.query(ValueProposition)
                .filter(ValueProposition.id == UUID(value_proposition_id))
                .first()
            )
        else:
            value_prop = (
                session.query(ValueProposition)
                .filter(ValueProposition.client_id == UUID(client_id))
                .filter(ValueProposition.is_active == True)
                .order_by(ValueProposition.created_at.desc())
                .first()
            )

        if not value_prop:
            raise ValueError(f"No value proposition found for client: {client_id}")

        logger.info(
            f"Loaded context: client={client.name}, industry={client.industry}, "
            f"value_prop_id={value_prop.id}"
        )

        # =============================================================================
        # Step 1.5: Delete existing templates for this client (OVERRIDE)
        # =============================================================================

        logger.info(f"Checking for existing templates for client {client_id}...")

        # Query existing templates for this client
        existing_templates = (
            session.query(DashboardTemplate)
            .filter(DashboardTemplate.client_id == UUID(client_id))
            .all()
        )

        if existing_templates:
            logger.info(f"Found {len(existing_templates)} existing templates for client {client_id} - deleting...")

            # Delete associated prospect dashboard data first (foreign key constraint)
            for template in existing_templates:
                # Delete prospect data linked to this template
                prospect_data_count = (
                    session.query(ProspectDashboardData)
                    .filter(ProspectDashboardData.template_id == template.id)
                    .delete(synchronize_session=False)
                )
                if prospect_data_count > 0:
                    logger.info(f"Deleted {prospect_data_count} prospect data records for template {template.id}")

            # Now delete the templates
            deleted_count = (
                session.query(DashboardTemplate)
                .filter(DashboardTemplate.client_id == UUID(client_id))
                .delete(synchronize_session=False)
            )

            session.commit()
            logger.info(f"✅ Deleted {deleted_count} existing templates for client {client_id}")
        else:
            logger.info(f"No existing templates found for client {client_id} - proceeding with generation")

        # =============================================================================
        # Step 2: Generate templates ONE AT A TIME (reduces JSON errors)
        # =============================================================================

        # Create single-template generator
        agent = create_template_generator_with_retry(single_mode=True, max_retries=3)

        # Define template distribution (7 templates total)
        template_plan = [
            {"category": "roi-focused", "audience": "Health Plan"},
            {"category": "roi-focused", "audience": "Broker"},
            {"category": "clinical-outcomes", "audience": "Health Plan"},
            {"category": "clinical-outcomes", "audience": "Medical Management"},
            {"category": "operational-efficiency", "audience": "Medical Management"},
            {"category": "competitive-positioning", "audience": "Broker"},
            {"category": "comprehensive", "audience": "TPA"},
        ]

        logger.info(f"Generating {len(template_plan)} templates one at a time...")
        agent_start = time.time()

        all_templates = []
        generated_names = []

        for idx, plan in enumerate(template_plan, 1):
            try:
                logger.info(
                    f"Generating template {idx}/{len(template_plan)}: "
                    f"category={plan['category']}, audience={plan['audience']}"
                )

                # Build prompt for single template
                prompt = f"""Generate ONE dashboard template for the following client:

**Client Information:**
- Client Name: {client.name}
- Industry: {client.industry or 'Healthcare'}
- Value Proposition: {value_prop.content}

**Template Requirements:**
- Template Number: {idx} of {len(template_plan)}
- Category: {plan['category']}
- Target Audience: {plan['audience']}
- Already Generated: {', '.join(generated_names) if generated_names else 'None'}

**Important:** Make this template unique and different from the already generated templates. Focus on {plan['category']} metrics for {plan['audience']} audience.

Return ONLY the JSON object with structure: {{"template": {{...}}, "reasoning": "..."}}
"""

                # Run agent for single template
                template_response = agent.run(prompt)

                # The response is already a SingleTemplateResult from retry wrapper
                if hasattr(template_response, 'template'):
                    single_template = template_response.template
                else:
                    single_template = template_response

                all_templates.append(single_template)
                generated_names.append(single_template.name)

                logger.info(f"✅ Template {idx} generated: {single_template.name}")

            except Exception as e:
                logger.error(f"Failed to generate template {idx}: {e}")
                # Continue with next template instead of failing entire job
                continue

        agent_duration_ms = int((time.time() - agent_start) * 1000)
        logger.info(
            f"Template generation completed: {len(all_templates)}/{len(template_plan)} successful in {agent_duration_ms}ms"
        )

        # =============================================================================
        # Step 3: Validate results
        # =============================================================================

        if not all_templates:
            raise ValueError("No templates were successfully generated")

        if len(all_templates) < 5:
            logger.warning(f"Only {len(all_templates)} templates generated (minimum is 5)")

        logger.info(f"Successfully generated {len(all_templates)} templates")

        # =============================================================================
        # Step 4: Save templates to PostgreSQL
        # =============================================================================

        template_ids = []

        for template_data in all_templates:
            db_template = DashboardTemplate(
                job_id=UUID(job_id),
                client_id=UUID(client_id),
                name=template_data.name,
                description=template_data.description,
                category=template_data.category,
                target_audience=template_data.targetAudience,
                visual_style=template_data.visualStyle.model_dump(),
                widgets=[w.model_dump() for w in template_data.widgets],
                meta_data={
                    "generated_by": "triton_agentic",
                    "agent_version": "1.0",
                    "generation_duration_ms": agent_duration_ms,
                },
                status="generated",
            )
            session.add(db_template)
            session.flush()  # Get the ID
            template_ids.append(str(db_template.id))

        session.commit()
        logger.info(f"Saved {len(template_ids)} templates to database")

        # =============================================================================
        # Step 5: Generate and store prospect dashboard data
        # =============================================================================

        # Get or create demo prospect for this client
        try:
            demo_prospect = get_or_create_demo_prospect(session, UUID(client_id))
            logger.info(f"Using demo prospect: {demo_prospect.id} - {demo_prospect.name}")

            # Generate dashboard data for each template
            prospect_data_ids = []
            for idx, template_id in enumerate(template_ids, 1):
                try:
                    # Load template from database
                    db_template = (
                        session.query(DashboardTemplate)
                        .filter(DashboardTemplate.id == UUID(template_id))
                        .first()
                    )

                    if not db_template:
                        logger.warning(f"Template not found for data generation: {template_id}")
                        continue

                    # Prepare template data for generator
                    template_dict = {
                        "id": str(db_template.id),
                        "name": db_template.name,
                        "widgets": db_template.widgets,
                        "category": db_template.category,
                        "target_audience": db_template.target_audience,
                    }

                    # Generate widget data
                    logger.info(f"Generating widget data for template {idx}/{len(template_ids)}: {db_template.name}")
                    prospect_data = generate_prospect_dashboard_data(
                        template=template_dict,
                        prospect_id=demo_prospect.id
                    )

                    # Store in database
                    db_prospect_data = ProspectDashboardData(
                        prospect_id=demo_prospect.id,
                        template_id=UUID(template_id),
                        dashboard_data=prospect_data["dashboard_data"],
                        validation_result=prospect_data.get("validation_result"),
                        generated_at=prospect_data["generated_at"],
                        generation_duration_ms=prospect_data["generation_duration_ms"],
                        generated_by=prospect_data["generated_by"],
                        status=prospect_data["status"],
                    )

                    session.add(db_prospect_data)
                    session.flush()
                    prospect_data_ids.append(str(db_prospect_data.id))

                    logger.info(f"✅ Generated data for template {db_template.name}: data_id={db_prospect_data.id}")

                except Exception as e:
                    logger.error(f"Failed to generate data for template {template_id}: {e}", exc_info=True)
                    # Continue with other templates
                    continue

            session.commit()
            logger.info(
                f"Generated and stored prospect data: {len(prospect_data_ids)} "
                f"dashboard data records for prospect {demo_prospect.id}"
            )

        except Exception as e:
            logger.error(f"Failed to generate prospect data: {e}", exc_info=True)
            # Don't fail the job if prospect data generation fails
            # Templates are already saved successfully

        # =============================================================================
        # Step 6: Log agent execution
        # =============================================================================

        execution_log = AgentExecutionLog(
            job_id=UUID(job_id),
            agent_name="template_generator",
            execution_time_ms=agent_duration_ms,
            token_usage={},  # Can be populated if agent exposes token usage
            error_count=0,
            retry_count=0,
            success=True,
            meta_data={
                "templates_generated": len(template_ids),
                "template_ids": template_ids,
            },
        )
        session.add(execution_log)

        # =============================================================================
        # Step 7: Update job status to completed
        # =============================================================================

        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.generation_duration_ms = int((time.time() - start_time) * 1000)
        session.commit()

        # Publish job completed event
        try:
            publisher = get_event_publisher()
            publisher.publish_job_event(
                "job:completed",
                {
                    "job_id": job_id,
                    "client_id": client_id,
                    "status": "completed",
                    "template_ids": template_ids,
                    "template_count": len(template_ids),
                    "generation_duration_ms": job.generation_duration_ms,
                    "completed_at": job.completed_at.isoformat(),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to publish job:completed event: {e}")

        logger.info(
            f"Template generation completed successfully [job_id={job_id}, "
            f"templates={len(template_ids)}, duration={job.generation_duration_ms}ms]"
        )

        return {
            "job_id": job_id,
            "client_id": client_id,
            "status": "completed",
            "template_ids": template_ids,
            "template_count": len(template_ids),
            "generation_duration_ms": job.generation_duration_ms,
        }

    except Exception as e:
        logger.error(f"Template generation failed [job_id={job_id}]: {str(e)}", exc_info=True)

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
                            "client_id": client_id,
                            "status": "failed",
                            "error_message": str(e),
                            "generation_duration_ms": job.generation_duration_ms,
                            "completed_at": job.completed_at.isoformat(),
                        },
                    )
                except Exception as publish_error:
                    logger.warning(f"Failed to publish job:failed event: {publish_error}")

                # Log failure
                execution_log = AgentExecutionLog(
                    job_id=UUID(job_id),
                    agent_name="template_generator",
                    execution_time_ms=job.generation_duration_ms,
                    error_count=1,
                    retry_count=self.request.retries,
                    success=False,
                    error_details=str(e),
                    meta_data={"exception_type": type(e).__name__},
                )
                session.add(execution_log)
                session.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update job status: {commit_error}")
                session.rollback()

        raise

    finally:
        # Clean up database session
        if session:
            session.close()
