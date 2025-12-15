"""Research Agent API endpoints.

Provides endpoints for WebSearchAgent and DocumentAnalysisAgent operations
as specified in TRITON_ENGINEERING_SPEC.md Section 4.2.
"""

import uuid
import time
from typing import Optional, Literal
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status, BackgroundTasks
from pydantic import ValidationError

from api.models.research_requests import (
    WebSearchRequest,
    DocumentAnalysisRequest,
    ResearchJobResponse,
    ResearchJobStatusResponse,
    ResearchJobListResponse,
    ResearchStatsResponse,
    ResearchValidationRequest,
    ResearchValidationResponse,
)
from core.models.value_proposition_models import (
    WebSearchResult,
    DocumentAnalysisResult,
    validate_web_search_result,
    validate_document_analysis_result,
)
from core.monitoring.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/research", tags=["research"])

# In-memory job storage (replace with database/Redis in production)
research_jobs = {}


# =============================================================================
# Helper Functions
# =============================================================================

def execute_web_search_research(job_id: str, request: WebSearchRequest, trigger_roi_generation: bool = False):
    """Execute web search research in background.

    Args:
        job_id: Job identifier
        request: Web search request parameters
        trigger_roi_generation: If True, automatically trigger ROI model generation after completion
    """
    try:
        logger.info(f"Starting web search research job: {job_id}")
        research_jobs[job_id]["status"] = "in_progress"
        research_jobs[job_id]["started_at"] = datetime.utcnow()
        research_jobs[job_id]["progress_percent"] = 10

        # Import agent factory
        from agents.web_search_agent import create_web_search_agent_with_retry
        from core.models.model_factory import get_default_model

        # Create agent with retry logic
        model = get_default_model()
        agent = create_web_search_agent_with_retry(
            name="WebSearchAgent",
            model=model,
            research_mode=request.research_mode,
            max_retries=3
        )

        research_jobs[job_id]["progress_percent"] = 20

        # Build research message
        if request.research_mode == "autonomous":
            message = f"""
Research the healthcare company: {request.client_company_name}

Industry Context: {request.industry_hint if request.industry_hint else "General healthcare"}
Additional Context: {request.additional_context if request.additional_context else "None"}

Perform comprehensive autonomous research across all areas: company overview, products, value propositions,
clinical outcomes, ROI framework, competitive positioning, and target audiences.

Perform 15-25 comprehensive searches and return structured JSON matching WebSearchResult schema.
"""
        else:  # manual mode
            prompts_text = "\n".join(f"- {prompt}" for prompt in (request.prompts or []))
            message = f"""
Research the healthcare company: {request.client_company_name}

Industry Context: {request.industry_hint if request.industry_hint else "General healthcare"}
Additional Context: {request.additional_context if request.additional_context else "None"}

Follow these specific research prompts:
{prompts_text}

Perform 5-15 focused searches addressing these prompts and return structured JSON matching WebSearchResult schema.
"""

        # Apply max_searches override if provided
        if request.max_searches:
            message += f"\n\nIMPORTANT: Perform exactly {request.max_searches} searches (user override)."

        research_jobs[job_id]["progress_percent"] = 30

        # Execute agent
        logger.info(f"Executing WebSearchAgent for job {job_id}")
        result = agent.run(message)

        research_jobs[job_id]["progress_percent"] = 90

        # Validate result (agent already validates, but double-check)
        validation = validate_web_search_result(result)

        if not validation["valid"]:
            raise ValueError(f"Research validation failed: {validation['errors']}")

        research_jobs[job_id]["status"] = "completed"
        research_jobs[job_id]["completed_at"] = datetime.utcnow()
        research_jobs[job_id]["result"] = result.dict()
        research_jobs[job_id]["progress_percent"] = 100

        logger.info(f"Web search research job completed: {job_id}")

        # Trigger ROI model generation if requested
        if trigger_roi_generation:
            logger.info(f"Triggering ROI model generation for research job: {job_id}")
            try:
                from api.routes.roi_models import (
                    execute_roi_model_generation_job,
                    ResearchDataInput
                )

                # Prepare research data for ROI generation
                research_summary = f"""
# Web Search Research Results for {request.client_company_name}

## Company Overview
{result.company_overview}

## Primary Value Propositions
{chr(10).join(f"- {vp}" for vp in result.value_propositions)}

## Clinical Outcomes
{chr(10).join(f"- {outcome}" for outcome in result.clinical_outcomes)}

## ROI Framework
{result.roi_framework}

## Competitive Positioning
{result.competitive_positioning}

## Target Audiences
{chr(10).join(f"- {audience}" for audience in result.target_audiences)}
"""

                research_data = ResearchDataInput(
                    web_search_data=result.dict(),
                    document_analysis_data=None,
                    research_summary=research_summary
                )

                # Create ROI generation job
                roi_job_id = str(uuid.uuid4())
                from api.routes.roi_models import jobs as roi_jobs, ROIModelGenerationJobStatus

                roi_jobs[roi_job_id] = ROIModelGenerationJobStatus(
                    job_id=roi_job_id,
                    status="pending",
                    client_name=request.client_company_name,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    progress_message="Job queued for execution (triggered by research job)"
                )

                # Store ROI job ID in research job
                research_jobs[job_id]["roi_job_id"] = roi_job_id

                # Execute ROI generation synchronously (already in background)
                execute_roi_model_generation_job(
                    job_id=roi_job_id,
                    client_name=request.client_company_name,
                    research_data=research_data,
                    model_type_override=None,
                    max_retries=3,
                    save_to_file=True
                )

                logger.info(f"ROI model generation triggered: {roi_job_id} from research job: {job_id}")

            except Exception as roi_error:
                logger.error(f"Failed to trigger ROI generation for job {job_id}: {roi_error}", exc_info=True)
                research_jobs[job_id]["roi_generation_error"] = str(roi_error)

    except Exception as e:
        logger.error(f"Web search research job failed: {job_id}, error: {e}", exc_info=True)
        research_jobs[job_id]["status"] = "failed"
        research_jobs[job_id]["completed_at"] = datetime.utcnow()
        research_jobs[job_id]["error"] = str(e)


def execute_document_analysis(job_id: str, request: DocumentAnalysisRequest):
    """Execute document analysis in background.

    Args:
        job_id: Job identifier
        request: Document analysis request parameters
    """
    try:
        logger.info(f"Starting document analysis job: {job_id}")
        research_jobs[job_id]["status"] = "in_progress"
        research_jobs[job_id]["started_at"] = datetime.utcnow()
        research_jobs[job_id]["progress_percent"] = 10

        # Import agent factory
        from agents.document_analysis_agent import create_document_analysis_agent_with_retry
        from core.models.model_factory import get_default_model

        # Create agent with retry logic
        model = get_default_model()
        agent = create_document_analysis_agent_with_retry(
            name="DocumentAnalysisAgent",
            model=model,
            max_retries=3
        )

        research_jobs[job_id]["progress_percent"] = 20

        # Build analysis message
        document_list = "\n".join(f"- {doc_id}" for doc_id in request.document_ids)

        message = f"""
Analyze the following client-uploaded documents to extract value propositions, clinical outcomes,
financial metrics, and competitive advantages from THEIR materials.

Documents to analyze:
{document_list}

Additional Context: {request.additional_context if request.additional_context else "None"}

Read all documents thoroughly and extract structured information matching DocumentAnalysisResult schema.

CRITICAL: Extract information from the CLIENT's documents about THEIR solution. Focus on:
- Value propositions with quantitative metrics
- Clinical outcomes with specific measurements
- Financial metrics (ROI, savings, PMPM, etc.)
- Target audiences
- Competitive advantages

Return structured JSON matching DocumentAnalysisResult schema.
"""

        research_jobs[job_id]["progress_percent"] = 30

        # Execute agent
        logger.info(f"Executing DocumentAnalysisAgent for job {job_id} with {len(request.document_ids)} documents")
        result = agent.run(message)

        research_jobs[job_id]["progress_percent"] = 90

        # Validate result (agent already validates, but double-check)
        validation = validate_document_analysis_result(result)

        if not validation["valid"]:
            raise ValueError(f"Analysis validation failed: {validation['errors']}")

        research_jobs[job_id]["status"] = "completed"
        research_jobs[job_id]["completed_at"] = datetime.utcnow()
        research_jobs[job_id]["result"] = result.dict()
        research_jobs[job_id]["progress_percent"] = 100

        logger.info(f"Document analysis job completed: {job_id}")

    except Exception as e:
        logger.error(f"Document analysis job failed: {job_id}, error: {e}", exc_info=True)
        research_jobs[job_id]["status"] = "failed"
        research_jobs[job_id]["completed_at"] = datetime.utcnow()
        research_jobs[job_id]["error"] = str(e)


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/web-search", response_model=ResearchJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def initiate_web_search(
    request: WebSearchRequest,
    background_tasks: BackgroundTasks,
    trigger_roi_generation: bool = Query(False, description="Automatically trigger ROI model generation after research completes")
):
    """
    Initiate web search research for a company.

    This endpoint starts an asynchronous research job that uses WebSearchAgent to
    research a company via Google searches and web scraping.

    **Research Modes:**
    - **Autonomous**: AI autonomously researches the company (15-25 searches)
    - **Manual**: AI follows user-provided research prompts (5-15 searches)

    **Process:**
    1. Validates request
    2. Creates research job
    3. Executes WebSearchAgent in background
    4. Returns job ID for status tracking

    **Example Usage:**
    ```json
    {
      "client_company_name": "Livongo Health",
      "research_mode": "autonomous",
      "industry_hint": "diabetes management",
      "additional_context": "Focus on ROI and clinical outcomes"
    }
    ```

    Returns:
        ResearchJobResponse: Job ID and initial status
    """
    try:
        # Validate manual mode has prompts
        if request.research_mode == "manual" and not request.prompts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manual research mode requires 'prompts' field"
            )

        # Generate job ID
        job_id = f"research_web_{uuid.uuid4().hex[:12]}"

        # Create job record
        research_jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "research_type": "web_search",
            "request": request.dict(),
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "progress_percent": 0,
            "trigger_roi_generation": trigger_roi_generation,
            "roi_job_id": None
        }

        # Add background task
        background_tasks.add_task(execute_web_search_research, job_id, request, trigger_roi_generation)

        logger.info(f"Web search research job created: {job_id} for company: {request.client_company_name}")

        # Estimate completion time based on mode
        estimated_seconds = 120 if request.research_mode == "autonomous" else 60

        return ResearchJobResponse(
            job_id=job_id,
            status="pending",
            message=f"Web search research initiated for {request.client_company_name}",
            research_type="web_search",
            created_at=datetime.utcnow(),
            estimated_completion_seconds=estimated_seconds
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate web search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate web search: {str(e)}"
        )


@router.post("/document-analysis", response_model=ResearchJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def initiate_document_analysis(
    request: DocumentAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Initiate document analysis for client documents.

    This endpoint starts an asynchronous analysis job that uses DocumentAnalysisAgent
    to extract value propositions, metrics, and insights from client-uploaded documents.

    **Document Types Supported:**
    - PDF files (ROI sheets, case studies)
    - DOCX files (product information, white papers)
    - TXT files

    **Process:**
    1. Validates document IDs
    2. Creates analysis job
    3. Executes DocumentAnalysisAgent in background
    4. Returns job ID for status tracking

    **Example Usage:**
    ```json
    {
      "document_ids": [
        "s3://triton-docs/client123/roi_sheet.pdf",
        "s3://triton-docs/client123/case_study.pdf"
      ],
      "additional_context": "Client focuses on diabetes management"
    }
    ```

    Returns:
        ResearchJobResponse: Job ID and initial status
    """
    try:
        # Generate job ID
        job_id = f"research_doc_{uuid.uuid4().hex[:12]}"

        # Create job record
        research_jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "research_type": "document_analysis",
            "request": request.dict(),
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "progress_percent": 0
        }

        # Add background task
        background_tasks.add_task(execute_document_analysis, job_id, request)

        logger.info(f"Document analysis job created: {job_id} for {len(request.document_ids)} documents")

        # Estimate completion time based on document count
        estimated_seconds = 30 * len(request.document_ids)

        return ResearchJobResponse(
            job_id=job_id,
            status="pending",
            message=f"Document analysis initiated for {len(request.document_ids)} documents",
            research_type="document_analysis",
            created_at=datetime.utcnow(),
            estimated_completion_seconds=estimated_seconds
        )

    except Exception as e:
        logger.error(f"Failed to initiate document analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate document analysis: {str(e)}"
        )


@router.get("/{job_id}", response_model=ResearchJobStatusResponse)
async def get_research_job_status(job_id: str):
    """
    Get status and results of a research job.

    Returns the current status of a research job including:
    - Job status (pending/in_progress/completed/failed)
    - Progress percentage (if available)
    - Result data (if completed)
    - Error message (if failed)

    Args:
        job_id: Research job identifier

    Returns:
        ResearchJobStatusResponse: Job status and results

    Raises:
        HTTPException: 404 if job not found
    """
    try:
        if job_id not in research_jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Research job '{job_id}' not found"
            )

        job = research_jobs[job_id]

        return ResearchJobStatusResponse(
            job_id=job["job_id"],
            status=job["status"],
            research_type=job["research_type"],
            progress_percent=job.get("progress_percent"),
            created_at=job["created_at"],
            started_at=job.get("started_at"),
            completed_at=job.get("completed_at"),
            result=job.get("result"),
            error=job.get("error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/", response_model=ResearchJobListResponse)
async def list_research_jobs(
    research_type: Optional[Literal['web_search', 'document_analysis']] = Query(
        None, description="Filter by research type"
    ),
    status_filter: Optional[Literal['pending', 'in_progress', 'completed', 'failed']] = Query(
        None, description="Filter by status"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List all research jobs with filtering and pagination.

    Args:
        research_type: Optional filter by research type
        status_filter: Optional filter by job status
        page: Page number (1-indexed)
        page_size: Items per page (max 100)

    Returns:
        ResearchJobListResponse: Paginated list of research jobs
    """
    try:
        # Filter jobs
        filtered_jobs = list(research_jobs.values())

        if research_type:
            filtered_jobs = [j for j in filtered_jobs if j["research_type"] == research_type]

        if status_filter:
            filtered_jobs = [j for j in filtered_jobs if j["status"] == status_filter]

        # Sort by creation time (newest first)
        filtered_jobs.sort(key=lambda x: x["created_at"], reverse=True)

        # Paginate
        total = len(filtered_jobs)
        start = (page - 1) * page_size
        end = start + page_size
        page_jobs = filtered_jobs[start:end]

        # Convert to response models
        job_responses = [
            ResearchJobStatusResponse(
                job_id=job["job_id"],
                status=job["status"],
                research_type=job["research_type"],
                progress_percent=job.get("progress_percent"),
                created_at=job["created_at"],
                started_at=job.get("started_at"),
                completed_at=job.get("completed_at"),
                result=job.get("result"),
                error=job.get("error")
            )
            for job in page_jobs
        ]

        return ResearchJobListResponse(
            total=total,
            page=page,
            page_size=page_size,
            jobs=job_responses
        )

    except Exception as e:
        logger.error(f"Failed to list research jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list research jobs: {str(e)}"
        )


@router.get("/stats/summary", response_model=ResearchStatsResponse)
async def get_research_stats():
    """
    Get statistics about research jobs.

    Returns aggregate statistics including:
    - Total job counts by type
    - Completion rates
    - Average duration
    - Success rate

    Returns:
        ResearchStatsResponse: Research statistics
    """
    try:
        jobs_list = list(research_jobs.values())

        web_search_jobs = [j for j in jobs_list if j["research_type"] == "web_search"]
        document_analysis_jobs = [j for j in jobs_list if j["research_type"] == "document_analysis"]
        completed_jobs = [j for j in jobs_list if j["status"] == "completed"]
        failed_jobs = [j for j in jobs_list if j["status"] == "failed"]

        # Calculate average duration
        durations = []
        for job in completed_jobs:
            if job.get("completed_at") and job.get("started_at"):
                duration = (job["completed_at"] - job["started_at"]).total_seconds()
                durations.append(duration)

        avg_duration = sum(durations) / len(durations) if durations else None

        # Calculate success rate
        finished_jobs = len(completed_jobs) + len(failed_jobs)
        success_rate = len(completed_jobs) / finished_jobs if finished_jobs > 0 else None

        return ResearchStatsResponse(
            total_jobs=len(jobs_list),
            web_search_jobs=len(web_search_jobs),
            document_analysis_jobs=len(document_analysis_jobs),
            completed_jobs=len(completed_jobs),
            failed_jobs=len(failed_jobs),
            average_duration_seconds=avg_duration,
            success_rate=success_rate
        )

    except Exception as e:
        logger.error(f"Failed to get research stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get research stats: {str(e)}"
        )


@router.post("/validate", response_model=ResearchValidationResponse)
async def validate_research_result(request: ResearchValidationRequest):
    """
    Validate a research result.

    Validates research data against Pydantic models and business rules.
    Useful for testing and debugging research outputs.

    Args:
        request: Validation request with result data

    Returns:
        ResearchValidationResponse: Validation results
    """
    try:
        if request.result_type == "web_search":
            result = WebSearchResult(**request.result_data)
            validation = validate_web_search_result(result)
            confidence = result.confidence_score
        elif request.result_type == "document_analysis":
            result = DocumentAnalysisResult(**request.result_data)
            validation = validate_document_analysis_result(result)
            confidence = result.overall_confidence
        else:
            raise ValueError(f"Unknown result type: {request.result_type}")

        return ResearchValidationResponse(
            valid=validation["valid"],
            errors=validation.get("errors", []),
            warnings=validation.get("warnings", []),
            confidence_score=confidence
        )

    except ValidationError as e:
        return ResearchValidationResponse(
            valid=False,
            errors=[f"Pydantic validation error: {str(e)}"],
            warnings=[],
            confidence_score=0.0
        )
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
