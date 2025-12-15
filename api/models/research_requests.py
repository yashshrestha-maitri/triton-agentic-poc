"""Request and response models for Research Agent API endpoints.

These models define the API contracts for WebSearchAgent and DocumentAnalysisAgent
as specified in TRITON_ENGINEERING_SPEC.md Section 4.2.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# =============================================================================
# Web Search Request/Response Models
# =============================================================================

class WebSearchRequest(BaseModel):
    """Request model for web search research.

    Supports two modes:
    - Autonomous: AI autonomously researches company (15-25 searches)
    - Manual: AI follows user-provided research prompts (5-15 searches)
    """
    client_company_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Company name to research"
    )
    research_mode: Literal['autonomous', 'manual'] = Field(
        default='autonomous',
        description="Research mode: autonomous (AI-driven) or manual (user-directed)"
    )
    industry_hint: Optional[str] = Field(
        None,
        max_length=200,
        description="Industry hint for autonomous mode (e.g., 'diabetes management')"
    )
    prompts: Optional[List[str]] = Field(
        None,
        description="Research prompts for manual mode. Required if research_mode='manual'"
    )
    additional_context: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional context to guide research"
    )
    max_searches: Optional[int] = Field(
        None,
        ge=5,
        le=30,
        description="Maximum number of searches (overrides mode defaults)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "client_company_name": "Livongo Health",
                "research_mode": "autonomous",
                "industry_hint": "diabetes management",
                "additional_context": "Focus on ROI and clinical outcomes",
                "max_searches": 20
            }
        }


class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis research.

    Analyzes client-uploaded documents (ROI sheets, case studies, product info)
    to extract value propositions and metrics.
    """
    document_ids: List[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of S3 document IDs/paths to analyze"
    )
    additional_context: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional context about the client's value proposition"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "document_ids": [
                    "s3://triton-docs/client123/roi_sheet.pdf",
                    "s3://triton-docs/client123/case_study.pdf"
                ],
                "additional_context": "Client focuses on diabetes management for health plans"
            }
        }


class ResearchJobResponse(BaseModel):
    """Response model for initiated research job.

    Research operations are async, so this returns a job ID for tracking.
    """
    job_id: str = Field(..., description="Unique job identifier for tracking")
    status: str = Field(..., description="Initial job status (typically 'pending')")
    message: str = Field(..., description="Success message")
    research_type: Literal['web_search', 'document_analysis'] = Field(
        ..., description="Type of research requested"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Job creation timestamp"
    )
    estimated_completion_seconds: int = Field(
        ...,
        description="Estimated time to completion in seconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_abc123",
                "status": "pending",
                "message": "Web search research initiated successfully",
                "research_type": "web_search",
                "created_at": "2025-01-15T10:30:00Z",
                "estimated_completion_seconds": 120
            }
        }


class ResearchJobStatusResponse(BaseModel):
    """Response model for research job status check."""
    job_id: str = Field(..., description="Job identifier")
    status: Literal['pending', 'in_progress', 'completed', 'failed'] = Field(
        ..., description="Current job status"
    )
    research_type: Literal['web_search', 'document_analysis'] = Field(
        ..., description="Type of research"
    )
    progress_percent: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Progress percentage (if available)"
    )
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    result: Optional[dict] = Field(
        None,
        description="Research result (WebSearchResult or DocumentAnalysisResult) if completed"
    )
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_abc123",
                "status": "completed",
                "research_type": "web_search",
                "progress_percent": 100,
                "created_at": "2025-01-15T10:30:00Z",
                "started_at": "2025-01-15T10:30:05Z",
                "completed_at": "2025-01-15T10:32:15Z",
                "result": {
                    "searches_performed": 18,
                    "company_overview": {"name": "Livongo Health"},
                    "value_propositions": []
                },
                "error": None
            }
        }


# =============================================================================
# List and Query Models
# =============================================================================

class ResearchJobListResponse(BaseModel):
    """Response model for listing research jobs."""
    total: int = Field(..., description="Total number of jobs")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    jobs: List[ResearchJobStatusResponse] = Field(..., description="List of research jobs")


class ResearchStatsResponse(BaseModel):
    """Response model for research statistics."""
    total_jobs: int = Field(..., description="Total research jobs")
    web_search_jobs: int = Field(..., description="Web search jobs count")
    document_analysis_jobs: int = Field(..., description="Document analysis jobs count")
    completed_jobs: int = Field(..., description="Completed jobs count")
    failed_jobs: int = Field(..., description="Failed jobs count")
    average_duration_seconds: Optional[float] = Field(
        None, description="Average job duration"
    )
    success_rate: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Job success rate (0.0-1.0)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_jobs": 150,
                "web_search_jobs": 100,
                "document_analysis_jobs": 50,
                "completed_jobs": 140,
                "failed_jobs": 5,
                "average_duration_seconds": 125.5,
                "success_rate": 0.93
            }
        }


# =============================================================================
# Validation Models
# =============================================================================

class ResearchValidationRequest(BaseModel):
    """Request to validate research results."""
    result_data: dict = Field(..., description="Research result to validate")
    result_type: Literal['web_search', 'document_analysis'] = Field(
        ..., description="Type of result"
    )


class ResearchValidationResponse(BaseModel):
    """Response from research validation."""
    valid: bool = Field(..., description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Overall confidence in research quality"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "errors": [],
                "warnings": ["Only 12 searches performed, recommended 15-25 for autonomous mode"],
                "confidence_score": 0.85
            }
        }
