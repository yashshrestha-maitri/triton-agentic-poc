"""Lineage API Routes.

This module provides REST API endpoints for querying and managing data lineage.
All endpoints support complete audit trails from source documents to dashboards.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from core.lineage import LineageTracker, create_tracker_from_env, compute_document_hash
from core.lineage.models import ExtractionLineage
from core.monitoring.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/lineage", tags=["lineage"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ImpactAnalysisRequest(BaseModel):
    """Request for impact analysis."""
    document_hash: str = Field(..., description="SHA256 hash of changed document")
    reason: str = Field(..., description="Reason for analysis (e.g., 'Document found incorrect')")


class ImpactAnalysisResponse(BaseModel):
    """Response for impact analysis."""
    document_hash: str
    reason: str
    affected_extractions: int
    affected_roi_models: List[UUID]
    affected_dashboards: List[UUID]
    details: List[Dict[str, Any]]


class FlagRequest(BaseModel):
    """Request to flag extraction."""
    issues: List[str] = Field(..., min_items=1, description="List of issues found")
    flagged_by: Optional[str] = Field(None, description="Who flagged this extraction")


class VerifyRequest(BaseModel):
    """Request to verify extraction."""
    verified_by: Optional[str] = Field(None, description="Who verified this extraction")
    notes: Optional[str] = Field(None, description="Verification notes")


class AuditTrailResponse(BaseModel):
    """Complete audit trail response."""
    extraction: ExtractionLineage
    roi_models: List[Dict[str, Any]]
    dashboards: List[Dict[str, Any]]
    usage_history: List[Dict[str, Any]]


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

def get_lineage_tracker() -> LineageTracker:
    """Get lineage tracker instance (dependency injection)."""
    return create_tracker_from_env()


# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.get(
    "/{extraction_id}",
    response_model=ExtractionLineage,
    summary="Get lineage for specific extraction",
    description="Retrieve complete lineage information for a single extraction by its UUID."
)
async def get_lineage(
    extraction_id: UUID,
    tracker: LineageTracker = Depends(get_lineage_tracker)
) -> ExtractionLineage:
    """Get lineage record by extraction ID.

    **Example:**
    ```bash
    curl http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333
    ```
    """
    try:
        lineage = tracker.get_lineage_by_id(extraction_id)

        if not lineage:
            raise HTTPException(
                status_code=404,
                detail=f"Lineage record not found for extraction_id: {extraction_id}"
            )

        # Update last accessed timestamp
        tracker.update_last_accessed(extraction_id)

        return lineage

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving lineage for {extraction_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/document/{document_hash}",
    response_model=List[ExtractionLineage],
    summary="Find extractions from specific document",
    description="Find all extractions that came from a specific source document using its SHA256 hash."
)
async def find_extractions_by_document(
    document_hash: str,
    tracker: LineageTracker = Depends(get_lineage_tracker)
) -> List[ExtractionLineage]:
    """Find all extractions from a document.

    **Example:**
    ```bash
    curl "http://localhost:8000/lineage/document/a1b2c3d4e5f6..."
    ```
    """
    try:
        # Validate hash format
        if len(document_hash) != 64:
            raise HTTPException(
                status_code=400,
                detail="Invalid document_hash: must be 64-character SHA256 hex string"
            )

        extractions = tracker.find_by_document_hash(document_hash)

        if not extractions:
            raise HTTPException(
                status_code=404,
                detail=f"No extractions found for document_hash: {document_hash}"
            )

        return extractions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding extractions for document {document_hash}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/audit-trail/{extraction_id}",
    response_model=AuditTrailResponse,
    summary="Get complete audit trail",
    description="Get complete audit trail showing extraction → ROI models → dashboards."
)
async def get_audit_trail(
    extraction_id: UUID,
    tracker: LineageTracker = Depends(get_lineage_tracker)
) -> AuditTrailResponse:
    """Get complete audit trail for extraction.

    Shows the complete chain from source document through ROI models to dashboards.

    **Example:**
    ```bash
    curl http://localhost:8000/lineage/audit-trail/33333333-3333-3333-3333-333333333333
    ```
    """
    try:
        lineage = tracker.get_lineage_by_id(extraction_id)

        if not lineage:
            raise HTTPException(
                status_code=404,
                detail=f"Lineage record not found for extraction_id: {extraction_id}"
            )

        # Build audit trail
        roi_models = []
        dashboards = []

        # Get ROI model details (placeholder - would query roi_models table)
        for roi_id in lineage.used_in_roi_models:
            roi_models.append({
                "roi_model_id": str(roi_id),
                "name": f"ROI Model {roi_id}",  # Would fetch from database
                "status": "active"
            })

        # Get dashboard details (placeholder - would query dashboard_templates table)
        for dash_id in lineage.used_in_dashboards:
            dashboards.append({
                "dashboard_id": str(dash_id),
                "name": f"Dashboard {dash_id}",  # Would fetch from database
                "target_audience": "unknown"
            })

        # Usage history
        usage_history = [
            {
                "timestamp": lineage.extraction_timestamp,
                "event": "extraction_created",
                "agent": lineage.extraction_agent
            }
        ]

        if lineage.metadata and lineage.metadata.updated_at:
            usage_history.append({
                "timestamp": lineage.metadata.updated_at,
                "event": "lineage_updated",
                "agent": "system"
            })

        if lineage.last_accessed:
            usage_history.append({
                "timestamp": lineage.last_accessed,
                "event": "lineage_accessed",
                "agent": "api"
            })

        return AuditTrailResponse(
            extraction=lineage,
            roi_models=roi_models,
            dashboards=dashboards,
            usage_history=sorted(usage_history, key=lambda x: x['timestamp'], reverse=True)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit trail for {extraction_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/impact-analysis",
    response_model=ImpactAnalysisResponse,
    summary="Analyze impact of document changes",
    description="Determine which ROI models and dashboards are affected when a source document changes."
)
async def impact_analysis(
    request: ImpactAnalysisRequest,
    tracker: LineageTracker = Depends(get_lineage_tracker)
) -> ImpactAnalysisResponse:
    """Perform impact analysis for document change.

    Returns all extractions, ROI models, and dashboards affected by a document change.

    **Example:**
    ```bash
    curl -X POST http://localhost:8000/lineage/impact-analysis \\
      -H "Content-Type: application/json" \\
      -d '{
        "document_hash": "a1b2c3d4...",
        "reason": "Document found incorrect"
      }'
    ```
    """
    try:
        # Find all affected dashboards
        affected = tracker.find_affected_dashboards(request.document_hash)

        if not affected:
            raise HTTPException(
                status_code=404,
                detail=f"No affected dashboards found for document_hash: {request.document_hash}"
            )

        # Aggregate results
        roi_model_ids = set()
        dashboard_ids = set()

        for item in affected:
            if item.get('roi_model_id'):
                roi_model_ids.add(UUID(item['roi_model_id']))
            if item.get('dashboard_id'):
                dashboard_ids.add(UUID(item['dashboard_id']))

        logger.info(
            f"Impact analysis for {request.document_hash}: "
            f"{len(affected)} extractions, {len(roi_model_ids)} ROI models, "
            f"{len(dashboard_ids)} dashboards affected"
        )

        return ImpactAnalysisResponse(
            document_hash=request.document_hash,
            reason=request.reason,
            affected_extractions=len(affected),
            affected_roi_models=list(roi_model_ids),
            affected_dashboards=list(dashboard_ids),
            details=affected
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing impact analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/flagged",
    response_model=List[ExtractionLineage],
    summary="Get flagged extractions",
    description="Retrieve all extractions that have been flagged for manual review."
)
async def get_flagged_extractions(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    tracker: LineageTracker = Depends(get_lineage_tracker)
) -> List[ExtractionLineage]:
    """Get all flagged extractions needing review.

    **Example:**
    ```bash
    curl "http://localhost:8000/lineage/flagged?limit=50"
    ```
    """
    try:
        flagged = tracker.get_flagged_extractions()

        # Apply limit
        flagged = flagged[:limit]

        logger.info(f"Retrieved {len(flagged)} flagged extractions")

        return flagged

    except Exception as e:
        logger.error(f"Error retrieving flagged extractions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{extraction_id}/verify",
    response_model=Dict[str, Any],
    summary="Mark extraction as verified",
    description="Mark an extraction as verified after manual review."
)
async def verify_extraction(
    extraction_id: UUID,
    request: VerifyRequest,
    tracker: LineageTracker = Depends(get_lineage_tracker)
) -> Dict[str, Any]:
    """Mark extraction as verified.

    **Example:**
    ```bash
    curl -X PUT http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333/verify \\
      -H "Content-Type: application/json" \\
      -d '{
        "verified_by": "john.doe@example.com",
        "notes": "Verified against source document"
      }'
    ```
    """
    try:
        # Check if exists
        lineage = tracker.get_lineage_by_id(extraction_id)
        if not lineage:
            raise HTTPException(
                status_code=404,
                detail=f"Lineage record not found for extraction_id: {extraction_id}"
            )

        # Mark as verified
        tracker.mark_verified(extraction_id)

        logger.info(
            f"Marked extraction {extraction_id} as verified "
            f"by {request.verified_by or 'unknown'}"
        )

        return {
            "success": True,
            "extraction_id": str(extraction_id),
            "verification_status": "verified",
            "verified_by": request.verified_by,
            "notes": request.notes
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying extraction {extraction_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{extraction_id}/flag",
    response_model=Dict[str, Any],
    summary="Flag extraction for review",
    description="Flag an extraction for manual review due to verification issues."
)
async def flag_extraction(
    extraction_id: UUID,
    request: FlagRequest,
    tracker: LineageTracker = Depends(get_lineage_tracker)
) -> Dict[str, Any]:
    """Flag extraction for manual review.

    **Example:**
    ```bash
    curl -X PUT http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333/flag \\
      -H "Content-Type: application/json" \\
      -d '{
        "issues": ["Value not found in source document", "Confidence score too low"],
        "flagged_by": "automated_verification"
      }'
    ```
    """
    try:
        # Check if exists
        lineage = tracker.get_lineage_by_id(extraction_id)
        if not lineage:
            raise HTTPException(
                status_code=404,
                detail=f"Lineage record not found for extraction_id: {extraction_id}"
            )

        # Flag for review
        tracker.mark_for_review(extraction_id, request.issues)

        logger.info(
            f"Flagged extraction {extraction_id} for review "
            f"with {len(request.issues)} issues by {request.flagged_by or 'unknown'}"
        )

        return {
            "success": True,
            "extraction_id": str(extraction_id),
            "verification_status": "flagged",
            "issues": request.issues,
            "flagged_by": request.flagged_by,
            "manual_review_required": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error flagging extraction {extraction_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats/summary",
    response_model=Dict[str, Any],
    summary="Get lineage statistics",
    description="Get aggregate statistics about lineage tracking."
)
async def get_lineage_stats(
    tracker: LineageTracker = Depends(get_lineage_tracker)
) -> Dict[str, Any]:
    """Get lineage tracking statistics.

    **Example:**
    ```bash
    curl http://localhost:8000/lineage/stats/summary
    ```
    """
    try:
        # Get flagged count
        flagged = tracker.get_flagged_extractions()

        # For now, return basic stats
        # In production, would query database for aggregate statistics
        stats = {
            "total_extractions": "N/A",  # Would query: SELECT COUNT(*) FROM extraction_lineage
            "verified_count": "N/A",     # Would query: WHERE verification_status = 'verified'
            "flagged_count": len(flagged),
            "unverified_count": "N/A",   # Would query: WHERE verification_status = 'unverified'
            "agents_used": ["DocumentAnalysisAgent", "WebSearchAgent"],
            "message": "Connect to database to see full statistics"
        }

        return stats

    except Exception as e:
        logger.error(f"Error retrieving lineage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# HEALTH CHECK
# =============================================================================

@router.get(
    "/health",
    summary="Health check for lineage API",
    description="Check if lineage API and database connection are healthy."
)
async def health_check() -> Dict[str, str]:
    """Health check endpoint.

    **Example:**
    ```bash
    curl http://localhost:8000/lineage/health
    ```
    """
    try:
        tracker = create_tracker_from_env()
        # Try to query database
        with tracker._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result and result[0] == 1:
                    return {
                        "status": "healthy",
                        "database": "connected",
                        "message": "Lineage API is operational"
                    }

        return {
            "status": "unhealthy",
            "database": "connection_failed",
            "message": "Database connection failed"
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "message": str(e)
        }
