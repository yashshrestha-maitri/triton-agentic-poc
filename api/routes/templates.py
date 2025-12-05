"""Template API endpoints - database-driven."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database.database import get_db
from core.database.models import DashboardTemplate
from core.monitoring.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/templates", tags=["templates"])


def template_to_dict(template: DashboardTemplate) -> dict:
    """
    Convert DashboardTemplate ORM model to API response dict.

    Args:
        template: DashboardTemplate instance

    Returns:
        dict: Template in API format
    """
    return {
        "id": str(template.id),
        "job_id": str(template.job_id) if template.job_id else None,
        "client_id": str(template.client_id) if template.client_id else None,
        "name": template.name,
        "description": template.description,
        "category": template.category,
        "target_audience": template.target_audience,
        "visual_style": template.visual_style,
        "widgets": template.widgets,
        "meta_data": template.meta_data,
        "status": template.status,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None,
    }


@router.get("/", response_model=dict)
async def list_templates(
    db: Session = Depends(get_db),
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    target_audience: Optional[str] = Query(None, description="Filter by target audience"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List dashboard templates with filtering and pagination.

    Args:
        db: Database session
        client_id: Optional client UUID filter
        job_id: Optional job UUID filter
        category: Optional category filter
        target_audience: Optional target audience filter
        page: Page number (1-indexed)
        page_size: Items per page (max 100)

    Returns:
        dict: Paginated list of templates
    """
    try:
        # Build query
        query = db.query(DashboardTemplate)

        # Apply filters
        if client_id:
            query = query.filter(DashboardTemplate.client_id == UUID(client_id))
        if job_id:
            query = query.filter(DashboardTemplate.job_id == UUID(job_id))
        if category:
            query = query.filter(DashboardTemplate.category == category)
        if target_audience:
            query = query.filter(DashboardTemplate.target_audience == target_audience)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        templates = query.order_by(DashboardTemplate.created_at.desc()).offset(offset).limit(page_size).all()

        # Convert to dict
        template_dicts = [template_to_dict(t) for t in templates]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "templates": template_dicts
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to list templates: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific template by ID.

    Args:
        template_id: Template UUID
        db: Database session

    Returns:
        dict: Complete template details

    Raises:
        HTTPException: If template not found (404)
    """
    try:
        # Convert to UUID
        template_uuid = UUID(template_id)

        # Query database
        template = db.query(DashboardTemplate).filter(
            DashboardTemplate.id == template_uuid
        ).first()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID '{template_id}' not found"
            )

        return template_to_dict(template)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {template_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve template: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve template: {str(e)}"
        )


@router.get("/categories/list", response_model=List[str])
async def list_categories():
    """
    Get list of all available template categories.

    Returns:
        List[str]: Available categories
    """
    return [
        'roi-focused',
        'clinical-outcomes',
        'operational-efficiency',
        'competitive-positioning',
        'comprehensive'
    ]


@router.get("/audiences/list", response_model=List[str])
async def list_audiences(db: Session = Depends(get_db)):
    """
    Get list of all target audiences from database templates.

    Args:
        db: Database session

    Returns:
        List[str]: Target audiences
    """
    try:
        # Query distinct target audiences
        audiences = db.query(DashboardTemplate.target_audience).distinct().all()

        # Extract and sort
        audience_list = sorted([a[0] for a in audiences if a[0]])

        return audience_list

    except Exception as e:
        logger.error(f"Failed to list audiences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list audiences: {str(e)}"
        )
