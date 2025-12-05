"""
API routes for generation job management.

Provides endpoints for:
- Creating template generation jobs
- Checking job status
- Listing jobs
- Cancelling jobs
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import GenerationJob, Client, ValueProposition, get_db
from core.monitoring.logger import get_logger
from tasks.template_generation import generate_templates_task

logger = get_logger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# =============================================================================
# Pydantic Models for Request/Response
# =============================================================================

from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    """Request model for creating a new generation job."""

    client_id: UUID = Field(..., description="UUID of the client")
    value_proposition_id: Optional[UUID] = Field(
        None, description="Optional UUID of specific value proposition. If not provided, uses latest active."
    )


class JobStatusResponse(BaseModel):
    """Response model for job status."""

    job_id: UUID = Field(alias='id')
    client_id: UUID
    value_proposition_id: Optional[UUID]
    status: str
    celery_task_id: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    generation_duration_ms: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class JobListResponse(BaseModel):
    """Response model for job list."""

    total: int
    page: int
    page_size: int
    jobs: List[JobStatusResponse]


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/", response_model=JobStatusResponse, status_code=status.HTTP_201_CREATED)
def create_generation_job(
    request: JobCreateRequest,
    db: Session = Depends(get_db),
) -> JobStatusResponse:
    """
    Create a new template generation job.

    This endpoint:
    1. Validates that the client and value proposition exist
    2. Creates a GenerationJob record in the database
    3. Submits a Celery task for async template generation
    4. Returns the job status

    The actual template generation happens asynchronously in the background.
    Use GET /jobs/{job_id} to check the job status.
    """
    logger.info(f"Creating generation job for client_id={request.client_id}")

    # Validate client exists
    client = db.query(Client).filter(Client.id == request.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client not found: {request.client_id}",
        )

    # Validate value proposition (if provided) or get latest active
    if request.value_proposition_id:
        value_prop = (
            db.query(ValueProposition)
            .filter(ValueProposition.id == request.value_proposition_id)
            .first()
        )
        if not value_prop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Value proposition not found: {request.value_proposition_id}",
            )
    else:
        # Get latest active value proposition for client
        value_prop = (
            db.query(ValueProposition)
            .filter(ValueProposition.client_id == request.client_id)
            .filter(ValueProposition.is_active == True)
            .order_by(ValueProposition.created_at.desc())
            .first()
        )
        if not value_prop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active value proposition found for client: {request.client_id}",
            )

    # Create job record
    job = GenerationJob(
        client_id=request.client_id,
        value_proposition_id=value_prop.id,
        status="pending",
        meta_data={
            "client_name": client.name,
            "submitted_via": "api",
        },
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(f"Created job record: job_id={job.id}")

    # Submit Celery task
    try:
        task = generate_templates_task.delay(
            job_id=str(job.id),
            client_id=str(request.client_id),
            value_proposition_id=str(value_prop.id),
        )
        job.celery_task_id = task.id
        db.commit()
        db.refresh(job)

        logger.info(f"Submitted Celery task: task_id={task.id}, job_id={job.id}")
    except Exception as e:
        logger.error(f"Failed to submit Celery task for job_id={job.id}: {e}")
        job.status = "failed"
        job.error_message = f"Failed to submit task: {str(e)}"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit generation task: {str(e)}",
        )

    return JobStatusResponse.model_validate(job)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: UUID,
    db: Session = Depends(get_db),
) -> JobStatusResponse:
    """
    Get the status of a generation job.

    Returns:
    - pending: Job is waiting to be processed
    - running: Job is currently being processed
    - completed: Job completed successfully (templates are available)
    - failed: Job failed (check error_message for details)
    - cancelled: Job was cancelled
    """
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )

    return JobStatusResponse.model_validate(job)


@router.get("/", response_model=JobListResponse)
def list_jobs(
    client_id: Optional[UUID] = Query(None, description="Filter by client ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status", alias="status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> JobListResponse:
    """
    List generation jobs with optional filtering and pagination.

    Filters:
    - client_id: Show jobs for specific client
    - status: Filter by job status (pending, running, completed, failed, cancelled)

    Results are ordered by creation date (newest first).
    """
    query = db.query(GenerationJob)

    # Apply filters
    if client_id:
        query = query.filter(GenerationJob.client_id == client_id)

    if status_filter:
        query = query.filter(GenerationJob.status == status_filter)

    # Get total count
    total = query.count()

    # Apply pagination
    jobs = (
        query.order_by(GenerationJob.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return JobListResponse(
        total=total,
        page=page,
        page_size=page_size,
        jobs=[JobStatusResponse.model_validate(job) for job in jobs],
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_job(
    job_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """
    Cancel a pending or running generation job.

    This will:
    1. Mark the job as cancelled in the database
    2. Attempt to revoke the Celery task (if it's still pending)

    Note: If the job is already running, it may complete before cancellation takes effect.
    """
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )

    if job.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job.status}",
        )

    # Update job status
    job.status = "cancelled"
    job.completed_at = datetime.utcnow()
    db.commit()

    # Attempt to revoke Celery task
    if job.celery_task_id:
        try:
            from worker import celery_app

            celery_app.control.revoke(job.celery_task_id, terminate=True)
            logger.info(f"Revoked Celery task: task_id={job.celery_task_id}")
        except Exception as e:
            logger.warning(f"Failed to revoke Celery task {job.celery_task_id}: {e}")

    logger.info(f"Cancelled job: job_id={job_id}")
