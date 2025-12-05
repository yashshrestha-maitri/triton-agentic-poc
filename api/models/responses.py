"""API response models for Triton Template Generation."""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")


class SuccessResponse(BaseModel):
    """Standard success response."""
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")


class TemplateGenerationRequest(BaseModel):
    """Request model for template generation."""
    client_name: str = Field(..., min_length=1, max_length=200, description="Client name")
    industry: str = Field(..., min_length=1, max_length=200, description="Industry sector")
    target_audiences: List[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of target audiences"
    )
    value_proposition: dict = Field(..., description="Value proposition data")
    max_templates: Optional[int] = Field(10, ge=5, le=10, description="Maximum number of templates to generate")

    class Config:
        json_schema_extra = {
            "example": {
                "client_name": "Livongo Health",
                "industry": "Diabetes Management",
                "target_audiences": ["Health Plan", "Broker", "Medical Management"],
                "value_proposition": {
                    "executive_value_proposition": {
                        "core_value_statement": "AI-powered diabetes management platform",
                        "primary_impact_areas": ["Clinical Outcomes", "Cost Reduction"]
                    }
                },
                "max_templates": 10
            }
        }


class TemplateSummary(BaseModel):
    """Summary information for a dashboard template."""
    id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(..., description="Template category")
    target_audience: str = Field(..., description="Target audience")
    widget_count: int = Field(..., description="Number of widgets in the template")
    source_file: str = Field(..., description="Source result file name")
    created_at: datetime = Field(..., description="Template creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "template-001",
                "name": "ROI-Focused Dashboard",
                "description": "Dashboard focused on return on investment metrics",
                "category": "roi-focused",
                "target_audience": "Health Plan",
                "widget_count": 8,
                "source_file": "templates_Livongo_Health_20231126.json",
                "created_at": "2023-11-26T10:30:45Z"
            }
        }


class TemplateListResponse(BaseModel):
    """Response model for listing templates."""
    total: int = Field(..., description="Total number of templates")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    templates: List[TemplateSummary] = Field(..., description="List of template summaries")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")
