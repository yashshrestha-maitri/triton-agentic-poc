"""
Prospect dashboard data API endpoints.

Endpoints for managing generated dashboard data for specific prospects.
"""

import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from core.database.database import get_db_session
from core.database.models import DashboardTemplate, ProspectDashboardData, Prospect, ProspectDataJob
from core.services.data_generator import generate_prospect_dashboard_data
from core.services.prospect_service import ProspectService
from tasks.prospect_data_generation import generate_prospect_data_task

router = APIRouter(prefix="/prospect-data", tags=["Prospect Data"])


# =============================================================================
# Request/Response Models
# =============================================================================


class GenerateDataRequest(BaseModel):
    """Request to generate dashboard data for a prospect."""

    template_id: Optional[str] = Field(
        None,
        description="Dashboard template UUID. If omitted, generates for all client templates"
    )
    prospect_id: str = Field(..., description="Prospect UUID")
    regenerate: bool = Field(
        False, description="Force regeneration even if data exists"
    )


class ProspectDataResponse(BaseModel):
    """Response containing prospect dashboard data."""

    id: str
    prospect_id: str
    template_id: str
    dashboard_data: dict
    validation_result: Optional[dict]
    generated_at: datetime
    generation_duration_ms: int
    generated_by: str
    status: str
    created_at: datetime
    updated_at: datetime


class ProspectDataListResponse(BaseModel):
    """Response for listing prospect data records."""

    total: int
    prospect_data: list[ProspectDataResponse]


class BatchGenerateResponse(BaseModel):
    """Response for batch generation of all client templates."""

    prospect_id: str
    client_id: str
    total_templates: int
    successful: int
    failed: int
    generated_data: list[ProspectDataResponse]
    errors: list[dict] = []


class ProspectDataJobResponse(BaseModel):
    """Response for async prospect data generation job."""

    job_id: str
    prospect_id: str
    template_id: Optional[str]
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    result_summary: Optional[dict]


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_dashboard_data(request: GenerateDataRequest):
    """
    Generate dashboard data for a prospect.

    Two modes:
    1. If template_id provided: Generate for that specific template
    2. If template_id is None: Generate for ALL templates belonging to prospect's client

    This endpoint generates synthetic sample data for all widgets in template(s)
    and stores it in the prospect_dashboard_data table.

    Args:
        request: Generation request with prospect_id and optional template_id

    Returns:
        Single ProspectDataResponse if template_id provided,
        BatchGenerateResponse if generating for all client templates

    Raises:
        HTTPException: If template or prospect not found, or generation fails
    """
    with get_db_session() as session:
        try:
            prospect_id = UUID(request.prospect_id)

            # Verify prospect exists and get client_id
            prospect = (
                session.query(Prospect)
                .filter(Prospect.id == prospect_id)
                .first()
            )
            if not prospect:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Prospect not found: {request.prospect_id}",
                )

            # If template_id provided, generate for single template (existing behavior)
            if request.template_id:
                return await _generate_single_template(
                    session, request, prospect_id
                )

            # No template_id: Generate for ALL client templates
            return await _generate_all_client_templates(
                session, request, prospect, prospect_id
            )

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate data: {str(e)}",
            )


@router.post("/generate-async", response_model=ProspectDataJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_dashboard_data_async(request: GenerateDataRequest):
    """
    Generate dashboard data for a prospect asynchronously (via Celery).

    This endpoint returns immediately with a job_id. Poll GET /prospect-data/jobs/{job_id}
    to check completion status, or subscribe via SSE at /jobs/{job_id}/subscribe.

    Two modes:
    1. If template_id provided: Generate for that specific template
    2. If template_id is None: Generate for ALL templates belonging to prospect's client

    Args:
        request: Generation request with prospect_id and optional template_id

    Returns:
        Job status with job_id for polling

    Raises:
        HTTPException: If prospect not found or job submission fails
    """
    with get_db_session() as session:
        try:
            prospect_id = UUID(request.prospect_id)

            # Verify prospect exists
            prospect = (
                session.query(Prospect)
                .filter(Prospect.id == prospect_id)
                .first()
            )
            if not prospect:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Prospect not found: {request.prospect_id}",
                )

            # Verify template exists if provided
            template_id_uuid = None
            if request.template_id:
                template_id_uuid = UUID(request.template_id)
                template = (
                    session.query(DashboardTemplate)
                    .filter(DashboardTemplate.id == template_id_uuid)
                    .first()
                )
                if not template:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Template not found: {request.template_id}",
                    )

            # Create job record
            job = ProspectDataJob(
                prospect_id=prospect_id,
                template_id=template_id_uuid,
                regenerate=request.regenerate,
                status="pending",
            )
            session.add(job)
            session.commit()
            session.refresh(job)

            # Submit Celery task
            task = generate_prospect_data_task.apply_async(
                args=[
                    str(job.id),
                    str(prospect_id),
                    str(template_id_uuid) if template_id_uuid else None,
                    request.regenerate,
                ]
            )

            # Update job with celery task ID
            job.celery_task_id = task.id
            session.commit()

            return ProspectDataJobResponse(
                job_id=str(job.id),
                prospect_id=str(job.prospect_id),
                template_id=str(job.template_id) if job.template_id else None,
                status=job.status,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                error_message=job.error_message,
                result_summary=job.result_summary,
            )

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to submit job: {str(e)}",
            )


@router.get("/jobs/{job_id}", response_model=ProspectDataJobResponse)
async def get_prospect_data_job_status(job_id: str):
    """
    Check status of a prospect data generation job.

    Status values:
    - pending: Waiting in queue
    - running: Generating data
    - completed: Data generation complete (see result_summary)
    - failed: Generation failed (see error_message)
    - cancelled: Job was cancelled
    """
    with get_db_session() as session:
        try:
            job_uuid = UUID(job_id)
            job = session.query(ProspectDataJob).filter(ProspectDataJob.id == job_uuid).first()

            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Job not found: {job_id}",
                )

            return ProspectDataJobResponse(
                job_id=str(job.id),
                prospect_id=str(job.prospect_id),
                template_id=str(job.template_id) if job.template_id else None,
                status=job.status,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                error_message=job.error_message,
                result_summary=job.result_summary,
            )

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve job status: {str(e)}",
            )


async def _generate_single_template(session, request: GenerateDataRequest, prospect_id: UUID):
    """Generate data for a single template (original behavior)."""
    template_id = UUID(request.template_id)

    # Verify template exists
    template = (
        session.query(DashboardTemplate)
        .filter(DashboardTemplate.id == template_id)
        .first()
    )
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template not found: {request.template_id}",
        )

    # Check if data already exists
    existing_data = (
        session.query(ProspectDashboardData)
        .filter(ProspectDashboardData.prospect_id == prospect_id)
        .filter(ProspectDashboardData.template_id == template_id)
        .first()
    )

    if existing_data and not request.regenerate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Data already exists for prospect {request.prospect_id} "
            f"and template {request.template_id}. Use regenerate=true to overwrite.",
        )

    # Generate and save data
    db_data = _generate_and_save_template_data(
        session, template, prospect_id, existing_data
    )

    return ProspectDataResponse(
        id=str(db_data.id),
        prospect_id=str(db_data.prospect_id),
        template_id=str(db_data.template_id),
        dashboard_data=db_data.dashboard_data,
        validation_result=db_data.validation_result,
        generated_at=db_data.generated_at,
        generation_duration_ms=db_data.generation_duration_ms,
        generated_by=db_data.generated_by,
        status=db_data.status,
        created_at=db_data.created_at,
        updated_at=db_data.updated_at,
    )


async def _generate_all_client_templates(
    session, request: GenerateDataRequest, prospect, prospect_id: UUID
):
    """Generate data for ALL templates belonging to the prospect's client."""
    client_id = prospect.client_id

    # Get all templates for this client
    templates = (
        session.query(DashboardTemplate)
        .filter(DashboardTemplate.client_id == client_id)
        .all()
    )

    if not templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No templates found for client {client_id}",
        )

    generated_data = []
    errors = []
    successful = 0
    failed = 0

    # Generate data for each template
    for template in templates:
        try:
            # Check if data already exists
            existing_data = (
                session.query(ProspectDashboardData)
                .filter(ProspectDashboardData.prospect_id == prospect_id)
                .filter(ProspectDashboardData.template_id == template.id)
                .first()
            )

            # Skip if exists and regenerate not requested
            if existing_data and not request.regenerate:
                continue

            # Generate and save
            db_data = _generate_and_save_template_data(
                session, template, prospect_id, existing_data
            )

            generated_data.append(
                ProspectDataResponse(
                    id=str(db_data.id),
                    prospect_id=str(db_data.prospect_id),
                    template_id=str(db_data.template_id),
                    dashboard_data=db_data.dashboard_data,
                    validation_result=db_data.validation_result,
                    generated_at=db_data.generated_at,
                    generation_duration_ms=db_data.generation_duration_ms,
                    generated_by=db_data.generated_by,
                    status=db_data.status,
                    created_at=db_data.created_at,
                    updated_at=db_data.updated_at,
                )
            )
            successful += 1

        except Exception as e:
            failed += 1
            errors.append({
                "template_id": str(template.id),
                "template_name": template.name,
                "error": str(e)
            })

    return BatchGenerateResponse(
        prospect_id=str(prospect_id),
        client_id=str(client_id),
        total_templates=len(templates),
        successful=successful,
        failed=failed,
        generated_data=generated_data,
        errors=errors,
    )


def _generate_and_save_template_data(
    session, template, prospect_id: UUID, existing_data=None
):
    """Helper to generate and save template data."""
    # Prepare template for generator
    template_dict = {
        "id": str(template.id),
        "name": template.name,
        "widgets": template.widgets,
        "category": template.category,
        "target_audience": template.target_audience,
    }

    # Generate data
    prospect_data = generate_prospect_dashboard_data(
        template=template_dict, prospect_id=prospect_id
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
            prospect_id=prospect_id,
            template_id=template.id,
            dashboard_data=prospect_data["dashboard_data"],
            validation_result=prospect_data.get("validation_result"),
            generated_at=prospect_data["generated_at"],
            generation_duration_ms=prospect_data["generation_duration_ms"],
            generated_by=prospect_data["generated_by"],
            status=prospect_data["status"],
        )
        session.add(db_data)

    session.commit()
    session.refresh(db_data)

    return db_data


@router.get("/{prospect_id}", response_model=ProspectDataListResponse)
async def get_prospect_dashboard_data(
    prospect_id: str,
    template_id: Optional[str] = Query(None, description="Filter by template ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
):
    """
    Get all dashboard data for a prospect.

    Returns all generated dashboard data records for a specific prospect,
    optionally filtered by template or status.

    Args:
        prospect_id: Prospect UUID
        template_id: Optional template UUID filter
        status_filter: Optional status filter (ready, generating, stale, error)

    Returns:
        List of prospect data records

    Raises:
        HTTPException: If prospect not found
    """
    with get_db_session() as session:
        try:
            prospect_uuid = UUID(prospect_id)

            # Verify prospect exists
            prospect = (
                session.query(Prospect)
                .filter(Prospect.id == prospect_uuid)
                .first()
            )
            if not prospect:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Prospect not found: {prospect_id}",
                )

            # Build query
            query = session.query(ProspectDashboardData).filter(
                ProspectDashboardData.prospect_id == prospect_uuid
            )

            if template_id:
                query = query.filter(
                    ProspectDashboardData.template_id == UUID(template_id)
                )

            if status_filter:
                query = query.filter(ProspectDashboardData.status == status_filter)

            # Execute query
            data_records = query.all()

            # Convert to response
            prospect_data_list = [
                ProspectDataResponse(
                    id=str(record.id),
                    prospect_id=str(record.prospect_id),
                    template_id=str(record.template_id),
                    dashboard_data=record.dashboard_data,
                    validation_result=record.validation_result,
                    generated_at=record.generated_at,
                    generation_duration_ms=record.generation_duration_ms,
                    generated_by=record.generated_by,
                    status=record.status,
                    created_at=record.created_at,
                    updated_at=record.updated_at,
                )
                for record in data_records
            ]

            return ProspectDataListResponse(
                total=len(prospect_data_list), prospect_data=prospect_data_list
            )

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve data: {str(e)}",
            )


@router.get("/{prospect_id}/{template_id}")
async def get_specific_dashboard_data(prospect_id: str, template_id: str):
    """
    Get specific dashboard data for a prospect and template.

    Returns the dashboard data for a specific prospect-template combination.

    Args:
        prospect_id: Prospect UUID
        template_id: Template UUID

    Returns:
        Prospect data record

    Raises:
        HTTPException: If data not found
    """
    with get_db_session() as session:
        try:
            prospect_uuid = UUID(prospect_id)
            template_uuid = UUID(template_id)

            # Query specific record
            data_record = (
                session.query(ProspectDashboardData)
                .filter(ProspectDashboardData.prospect_id == prospect_uuid)
                .filter(ProspectDashboardData.template_id == template_uuid)
                .first()
            )

            if not data_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No data found for prospect {prospect_id} "
                    f"and template {template_id}",
                )

            return ProspectDataResponse(
                id=str(data_record.id),
                prospect_id=str(data_record.prospect_id),
                template_id=str(data_record.template_id),
                dashboard_data=data_record.dashboard_data,
                validation_result=data_record.validation_result,
                generated_at=data_record.generated_at,
                generation_duration_ms=data_record.generation_duration_ms,
                generated_by=data_record.generated_by,
                status=data_record.status,
                created_at=data_record.created_at,
                updated_at=data_record.updated_at,
            )

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve data: {str(e)}",
            )


@router.delete("/{prospect_id}/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard_data(prospect_id: str, template_id: str):
    """
    Delete dashboard data for a prospect and template.

    Removes the generated data, forcing regeneration on next request.

    Args:
        prospect_id: Prospect UUID
        template_id: Template UUID

    Raises:
        HTTPException: If data not found or deletion fails
    """
    with get_db_session() as session:
        try:
            prospect_uuid = UUID(prospect_id)
            template_uuid = UUID(template_id)

            # Find record
            data_record = (
                session.query(ProspectDashboardData)
                .filter(ProspectDashboardData.prospect_id == prospect_uuid)
                .filter(ProspectDashboardData.template_id == template_uuid)
                .first()
            )

            if not data_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No data found for prospect {prospect_id} "
                    f"and template {template_id}",
                )

            session.delete(data_record)
            session.commit()

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete data: {str(e)}",
            )
