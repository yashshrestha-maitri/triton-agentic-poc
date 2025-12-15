"""
ROI Model API Routes

This module provides API endpoints for ROI model generation, combining:
1. Research data input (WebSearchResult + DocumentAnalysisResult)
2. ROI Classification (determine B1-B13 model type)
3. ROI Model Generation (complete 15-component ROI model)

Endpoints support both synchronous and asynchronous (background job) execution.
"""

from typing import Optional, Dict, Any
from pathlib import Path
import json
import asyncio
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field

from core.monitoring.logger import get_logger
from core.models.roi_models import ROIModelJSON, ModelTypeCode
from agents.roi_classification_agent import (
    create_roi_classification_agent_with_retry,
    ROIClassificationResult
)
from agents.roi_model_builder_agent import create_roi_model_builder_with_retry

logger = get_logger(__name__)

router = APIRouter(prefix="/api/roi-models", tags=["ROI Models"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ResearchDataInput(BaseModel):
    """Research data input for ROI model generation"""
    web_search_data: Optional[Dict[str, Any]] = Field(None, description="Web search results JSON")
    document_analysis_data: Optional[Dict[str, Any]] = Field(None, description="Document analysis results JSON")
    research_summary: str = Field(..., min_length=100, description="Combined research summary (required)")


class ROIModelGenerationRequest(BaseModel):
    """Request to generate ROI model from research data"""
    client_name: str = Field(..., min_length=1, description="Client organization name")
    research_data: ResearchDataInput = Field(..., description="Research data input")
    model_type_override: Optional[ModelTypeCode] = Field(None, description="Override automatic classification")
    max_retries: int = Field(default=3, ge=1, le=5, description="Max retries for agent execution")
    save_to_file: bool = Field(default=True, description="Save generated model to results directory")


class ROIModelGenerationJobStatus(BaseModel):
    """Status of ROI model generation job"""
    job_id: str = Field(..., description="Unique job ID")
    status: str = Field(..., description="Job status: pending, classifying, generating, completed, failed")
    client_name: str = Field(..., description="Client name")
    created_at: datetime = Field(..., description="Job creation time")
    updated_at: datetime = Field(..., description="Last update time")
    progress_message: Optional[str] = Field(None, description="Current progress message")
    classification_result: Optional[Dict[str, Any]] = Field(None, description="Classification result (when available)")
    roi_model: Optional[Dict[str, Any]] = Field(None, description="Generated ROI model (when completed)")
    error_message: Optional[str] = Field(None, description="Error message (if failed)")
    file_path: Optional[str] = Field(None, description="Saved file path (if save_to_file=True)")


class ROIModelGenerationResponse(BaseModel):
    """Response from ROI model generation"""
    job_id: str = Field(..., description="Job ID for tracking")
    status: str = Field(..., description="Initial status")
    message: str = Field(..., description="Response message")


# ============================================================================
# JOB TRACKING (IN-MEMORY STORAGE)
# ============================================================================

# In-memory job storage (for prototype - use Redis/PostgreSQL in production)
jobs: Dict[str, ROIModelGenerationJobStatus] = {}


def update_job_status(
    job_id: str,
    status: str,
    progress_message: Optional[str] = None,
    classification_result: Optional[ROIClassificationResult] = None,
    roi_model: Optional[ROIModelJSON] = None,
    error_message: Optional[str] = None,
    file_path: Optional[str] = None
):
    """Update job status in storage"""
    if job_id not in jobs:
        logger.error(f"Job {job_id} not found in storage")
        return

    jobs[job_id].status = status
    jobs[job_id].updated_at = datetime.now()

    if progress_message:
        jobs[job_id].progress_message = progress_message

    if classification_result:
        jobs[job_id].classification_result = classification_result.model_dump()

    if roi_model:
        jobs[job_id].roi_model = json.loads(roi_model.model_dump_json())

    if error_message:
        jobs[job_id].error_message = error_message

    if file_path:
        jobs[job_id].file_path = file_path

    logger.info(f"Job {job_id} updated: {status} - {progress_message}")


def save_roi_model_to_file(roi_model: ROIModelJSON, client_name: str, job_id: str) -> str:
    """Save ROI model to results directory"""
    results_dir = Path(__file__).parent.parent.parent / "results" / "roi_models"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize client name for filename
    safe_client_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in client_name)
    safe_client_name = safe_client_name.replace(' ', '_')

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"roi_model_{safe_client_name}_{roi_model.model_metadata.model_type_code.value}_{timestamp}_{job_id[:8]}.json"

    file_path = results_dir / filename

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json.loads(roi_model.model_dump_json()), f, indent=2, ensure_ascii=False)

    logger.info(f"ROI model saved to {file_path}")

    return str(file_path)


# ============================================================================
# BACKGROUND JOB EXECUTION
# ============================================================================

def execute_roi_model_generation_job(
    job_id: str,
    client_name: str,
    research_data: ResearchDataInput,
    model_type_override: Optional[ModelTypeCode],
    max_retries: int,
    save_to_file: bool
):
    """
    Background job to execute complete ROI model generation workflow:
    1. Classify ROI model type (unless overridden)
    2. Generate complete ROI model JSON
    3. Save to file (if requested)
    """
    try:
        # STEP 1: ROI Classification (unless overridden)
        if model_type_override:
            logger.info(f"Job {job_id}: Using model type override: {model_type_override}")
            update_job_status(
                job_id,
                status="generating",
                progress_message=f"Using specified model type: {model_type_override}"
            )
            model_type_code = model_type_override
            classification_result = None
        else:
            logger.info(f"Job {job_id}: Starting ROI classification")
            update_job_status(
                job_id,
                status="classifying",
                progress_message="Classifying ROI model type from research data"
            )

            # Create classification agent
            classification_agent = create_roi_classification_agent_with_retry(
                max_retries=max_retries
            )

            # Prepare classification message
            classification_message = f"""
# ROI Model Classification Request

**Client Name**: {client_name}

## Research Summary

{research_data.research_summary}

{"## Web Search Data" if research_data.web_search_data else ""}
{json.dumps(research_data.web_search_data, indent=2) if research_data.web_search_data else ""}

{"## Document Analysis Data" if research_data.document_analysis_data else ""}
{json.dumps(research_data.document_analysis_data, indent=2) if research_data.document_analysis_data else ""}

---

Analyze the research data above and classify the appropriate ROI model type (B1-B13).
Return ONLY the JSON object matching ROIClassificationResult schema.
"""

            # Run classification
            classification_result = classification_agent.run(classification_message)
            model_type_code = classification_result.recommended_model_type

            logger.info(f"Job {job_id}: Classification complete - {model_type_code}")
            update_job_status(
                job_id,
                status="generating",
                progress_message=f"Classification complete: {model_type_code} ({classification_result.model_type_name})",
                classification_result=classification_result
            )

        # STEP 2: ROI Model Generation
        logger.info(f"Job {job_id}: Starting ROI model generation for {model_type_code}")

        # Create model builder agent
        model_builder_agent = create_roi_model_builder_with_retry(
            model_type_code=model_type_code,
            max_retries=max_retries
        )

        # Prepare generation message
        generation_message = f"""
# ROI Model Generation Request

**Client Name**: {client_name}
**Model Type**: {model_type_code}

## Research Summary

{research_data.research_summary}

{"## Classification Result" if classification_result else ""}
{json.dumps(classification_result.model_dump() if classification_result else {}, indent=2)}

---

Generate a complete ROI Model JSON for this client based on the research summary and classification above.
Ensure all 15 components are fully populated with realistic, detailed content appropriate for {model_type_code}.

Return ONLY the JSON object matching ROIModelJSON schema.
"""

        # Run model generation
        roi_model = model_builder_agent.run(generation_message)

        logger.info(f"Job {job_id}: ROI model generation complete")

        # STEP 3: Save to file (if requested)
        file_path = None
        if save_to_file:
            file_path = save_roi_model_to_file(roi_model, client_name, job_id)
            logger.info(f"Job {job_id}: ROI model saved to {file_path}")

        # STEP 4: Update job as completed
        update_job_status(
            job_id,
            status="completed",
            progress_message="ROI model generation completed successfully",
            roi_model=roi_model,
            file_path=file_path
        )

        logger.info(f"Job {job_id}: Completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id}: Failed with error: {e}", exc_info=True)
        update_job_status(
            job_id,
            status="failed",
            progress_message="ROI model generation failed",
            error_message=str(e)
        )


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/generate", response_model=ROIModelGenerationResponse)
async def generate_roi_model(
    request: ROIModelGenerationRequest,
    background_tasks: BackgroundTasks
) -> ROIModelGenerationResponse:
    """
    Generate complete ROI model from research data (asynchronous).

    This endpoint starts a background job that:
    1. Classifies the ROI model type (B1-B13) from research data
    2. Generates a complete 15-component ROI Model JSON
    3. Optionally saves the model to the results directory

    Returns a job_id for tracking progress via GET /api/roi-models/{job_id}/status

    **Example Request:**
    ```json
    {
      "client_name": "Acme Healthcare",
      "research_data": {
        "research_summary": "Vendor offers MSK episode management with virtual PT...",
        "web_search_data": {...},
        "document_analysis_data": {...}
      },
      "max_retries": 3,
      "save_to_file": true
    }
    ```
    """
    job_id = str(uuid4())

    # Create job record
    jobs[job_id] = ROIModelGenerationJobStatus(
        job_id=job_id,
        status="pending",
        client_name=request.client_name,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        progress_message="Job queued for execution"
    )

    # Start background task
    background_tasks.add_task(
        execute_roi_model_generation_job,
        job_id=job_id,
        client_name=request.client_name,
        research_data=request.research_data,
        model_type_override=request.model_type_override,
        max_retries=request.max_retries,
        save_to_file=request.save_to_file
    )

    logger.info(f"Created ROI model generation job {job_id} for client: {request.client_name}")

    return ROIModelGenerationResponse(
        job_id=job_id,
        status="pending",
        message=f"ROI model generation job created. Track progress at /api/roi-models/{job_id}/status"
    )


@router.get("/{job_id}/status", response_model=ROIModelGenerationJobStatus)
async def get_job_status(job_id: str) -> ROIModelGenerationJobStatus:
    """
    Get status of ROI model generation job.

    Returns current job status including:
    - Job status (pending, classifying, generating, completed, failed)
    - Progress messages
    - Classification result (when available)
    - Generated ROI model (when completed)
    - Error messages (if failed)

    **Job Status Flow:**
    - `pending` → `classifying` → `generating` → `completed`
    - Or: `pending` → `failed` (if error occurs)
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return jobs[job_id]


@router.get("/", response_model=Dict[str, Any])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200, description="Max results to return")
) -> Dict[str, Any]:
    """
    List ROI model generation jobs.

    Query parameters:
    - `status`: Filter by job status (pending, classifying, generating, completed, failed)
    - `limit`: Maximum number of results (default 50)

    Returns list of jobs sorted by creation time (newest first).
    """
    job_list = list(jobs.values())

    # Filter by status if provided
    if status:
        job_list = [job for job in job_list if job.status == status]

    # Sort by creation time (newest first)
    job_list.sort(key=lambda j: j.created_at, reverse=True)

    # Apply limit
    job_list = job_list[:limit]

    return {
        "total": len(jobs),
        "filtered": len(job_list),
        "jobs": [job.model_dump() for job in job_list]
    }


@router.delete("/{job_id}")
async def delete_job(job_id: str) -> Dict[str, str]:
    """
    Delete a job from storage.

    Note: This only removes the job record from memory, not any saved files.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    del jobs[job_id]
    logger.info(f"Deleted job {job_id}")

    return {"message": f"Job {job_id} deleted successfully"}


@router.get("/results/files", response_model=Dict[str, Any])
async def list_saved_models() -> Dict[str, Any]:
    """
    List saved ROI model files in the results directory.

    Returns list of ROI model JSON files with metadata.
    """
    results_dir = Path(__file__).parent.parent.parent / "results" / "roi_models"

    if not results_dir.exists():
        return {"total": 0, "files": []}

    files = []
    for file_path in results_dir.glob("roi_model_*.json"):
        try:
            stat = file_path.stat()
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                model_metadata = data.get('model_metadata', {})

            files.append({
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "model_type": model_metadata.get('model_type_code'),
                "client_name": model_metadata.get('client_name')
            })
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            continue

    # Sort by creation time (newest first)
    files.sort(key=lambda f: f['created_at'], reverse=True)

    return {
        "total": len(files),
        "results_directory": str(results_dir),
        "files": files
    }


@router.get("/results/files/{filename}")
async def get_saved_model(filename: str) -> Dict[str, Any]:
    """
    Get contents of a saved ROI model file.

    Returns the complete ROI model JSON.
    """
    results_dir = Path(__file__).parent.parent.parent / "results" / "roi_models"
    file_path = results_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    # Security check: ensure file is within results directory
    if not str(file_path.resolve()).startswith(str(results_dir.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
