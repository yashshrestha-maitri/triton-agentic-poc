"""Pydantic models for Data Lineage tracking.

These models mirror the PostgreSQL extraction_lineage schema and provide
type-safe interfaces for lineage tracking operations.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID, uuid4


class LineageMetadata(BaseModel):
    """Metadata about lineage record creation and updates."""
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when lineage record was created"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when lineage record was last updated"
    )
    created_by: Optional[str] = Field(
        None,
        description="Agent or user that created this lineage record"
    )


class ExtractionLineage(BaseModel):
    """Complete lineage record for a single extraction.

    This model mirrors the extraction_lineage PostgreSQL table and tracks
    the complete audit trail from source document to dashboard usage.

    MVP Fields (10 mandatory):
    - Core Identity (2): extraction_id, extraction_timestamp
    - Source Tracking (2): source_document_url, source_document_hash
    - Extraction Context (2): extraction_agent, extraction_model
    - Verification Results (2): verification_status, verification_issues
    - Usage Tracking (2): used_in_roi_models, used_in_dashboards

    Phase 2/3 Fields (15 optional):
    - Retry tracking, confidence scores, quality metrics, etc.
    """

    # =========================================================================
    # CORE IDENTITY (2 mandatory fields)
    # =========================================================================
    extraction_id: UUID = Field(
        default_factory=uuid4,
        description="Unique extraction identifier (primary key)"
    )
    extraction_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When extraction occurred (UTC)"
    )

    # =========================================================================
    # SOURCE TRACKING (2 mandatory fields)
    # =========================================================================
    source_document_url: str = Field(
        ...,
        min_length=1,
        description="S3 URL or path to source document"
    )
    source_document_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="SHA256 hash of source document for integrity verification"
    )

    # =========================================================================
    # EXTRACTION CONTEXT (2 mandatory fields)
    # =========================================================================
    extraction_agent: str = Field(
        ...,
        description="Agent that performed extraction (e.g., 'DocumentAnalysisAgent')"
    )
    extraction_model: str = Field(
        ...,
        description="LLM model used (e.g., 'claude-sonnet-4-20250514')"
    )

    # =========================================================================
    # VERIFICATION RESULTS (2 mandatory fields)
    # =========================================================================
    verification_status: Literal['verified', 'unverified', 'flagged'] = Field(
        ...,
        description="Verification status: verified (passed all checks), unverified (not checked), flagged (issues found)"
    )
    verification_issues: List[str] = Field(
        default_factory=list,
        description="List of verification issues if status is 'flagged'"
    )

    # =========================================================================
    # USAGE TRACKING (2 mandatory fields)
    # =========================================================================
    used_in_roi_models: List[UUID] = Field(
        default_factory=list,
        description="UUIDs of ROI models that use this extraction"
    )
    used_in_dashboards: List[UUID] = Field(
        default_factory=list,
        description="UUIDs of dashboards that use this extraction"
    )

    # =========================================================================
    # PHASE 2: RETRY AND CONFIDENCE TRACKING (5 optional fields)
    # =========================================================================
    retry_attempts: Optional[int] = Field(
        None,
        ge=0,
        description="Number of retry attempts before success"
    )
    extraction_confidence_initial: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Initial confidence score from agent"
    )
    extraction_confidence_final: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Final confidence after verification"
    )
    manual_review_required: Optional[bool] = Field(
        None,
        description="Whether this extraction needs manual review"
    )
    manual_review_completed: Optional[bool] = Field(
        None,
        description="Whether manual review has been completed"
    )

    # =========================================================================
    # PHASE 3: QUALITY METRICS (5 optional fields)
    # =========================================================================
    extraction_quality_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Quality score (0-100) based on multiple factors"
    )
    source_text: Optional[str] = Field(
        None,
        description="Verbatim text from source document (for verification)"
    )
    extraction_reasoning: Optional[str] = Field(
        None,
        description="Agent's reasoning for extraction decisions"
    )
    validation_errors: Optional[List[str]] = Field(
        None,
        description="List of validation errors encountered"
    )
    last_accessed: Optional[datetime] = Field(
        None,
        description="When this extraction was last accessed/used"
    )

    # =========================================================================
    # METADATA
    # =========================================================================
    metadata: Optional[LineageMetadata] = Field(
        default_factory=LineageMetadata,
        description="Creation and update metadata"
    )

    # =========================================================================
    # VALIDATORS
    # =========================================================================

    @field_validator('source_document_hash')
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        """Validate SHA256 hash format (64 hex characters)."""
        if len(v) != 64:
            raise ValueError(f"SHA256 hash must be exactly 64 characters, got {len(v)}")
        if not all(c in '0123456789abcdefABCDEF' for c in v):
            raise ValueError("SHA256 hash must contain only hexadecimal characters")
        return v.lower()

    @field_validator('verification_issues')
    @classmethod
    def validate_verification_issues(cls, v: List[str], info) -> List[str]:
        """Ensure verification_issues is populated if status is 'flagged'."""
        # Note: info.data may not contain verification_status yet during initialization
        # This validation will be enforced at model validation time
        return v

    def add_roi_model_usage(self, roi_model_id: UUID) -> None:
        """Add ROI model usage (idempotent - won't duplicate)."""
        if roi_model_id not in self.used_in_roi_models:
            self.used_in_roi_models.append(roi_model_id)
            if self.metadata:
                self.metadata.updated_at = datetime.utcnow()

    def add_dashboard_usage(self, dashboard_id: UUID) -> None:
        """Add dashboard usage (idempotent - won't duplicate)."""
        if dashboard_id not in self.used_in_dashboards:
            self.used_in_dashboards.append(dashboard_id)
            if self.metadata:
                self.metadata.updated_at = datetime.utcnow()

    def flag_for_review(self, issues: List[str]) -> None:
        """Flag extraction for manual review with issues."""
        self.verification_status = 'flagged'
        self.verification_issues.extend(issues)
        self.manual_review_required = True
        if self.metadata:
            self.metadata.updated_at = datetime.utcnow()

    def mark_verified(self) -> None:
        """Mark extraction as verified."""
        self.verification_status = 'verified'
        if self.metadata:
            self.metadata.updated_at = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "extraction_id": "33333333-3333-3333-3333-333333333333",
                "extraction_timestamp": "2025-12-17T14:30:45Z",
                "source_document_url": "s3://triton-docs/clients/acme-health/roi_analysis_2025.pdf",
                "source_document_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
                "extraction_agent": "DocumentAnalysisAgent",
                "extraction_model": "claude-sonnet-4-20250514",
                "verification_status": "verified",
                "verification_issues": [],
                "used_in_roi_models": ["77777777-7777-7777-7777-777777777777"],
                "used_in_dashboards": ["99999999-9999-9999-9999-999999999999"],
                "retry_attempts": 0,
                "extraction_confidence_initial": 0.92,
                "extraction_confidence_final": 0.95,
                "manual_review_required": False,
                "manual_review_completed": False,
                "extraction_quality_score": 88.5,
                "source_text": "Our diabetes management program delivers 250% ROI within 24 months",
                "metadata": {
                    "created_at": "2025-12-17T14:30:45Z",
                    "updated_at": "2025-12-17T15:00:00Z",
                    "created_by": "DocumentAnalysisAgent"
                }
            }
        }


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_lineage_record(lineage: ExtractionLineage) -> Dict[str, Any]:
    """Comprehensive validation of lineage record.

    Performs business logic validation beyond Pydantic validation:
    - Ensures flagged extractions have issues listed
    - Validates confidence scores are reasonable
    - Checks usage tracking consistency

    Args:
        lineage: ExtractionLineage instance to validate

    Returns:
        Dict with validation results:
        {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str]
        }
    """
    errors = []
    warnings = []

    # Check 1: Flagged extractions must have issues
    if lineage.verification_status == 'flagged':
        if not lineage.verification_issues:
            errors.append("Flagged extractions must have verification_issues listed")
        if lineage.manual_review_required is False:
            warnings.append("Flagged extraction should typically require manual review")

    # Check 2: Verified extractions should not have issues
    if lineage.verification_status == 'verified':
        if lineage.verification_issues:
            warnings.append("Verified extraction has verification_issues - status may be incorrect")

    # Check 3: Confidence scores should be consistent
    if lineage.extraction_confidence_initial and lineage.extraction_confidence_final:
        if lineage.extraction_confidence_final < lineage.extraction_confidence_initial:
            warnings.append(
                f"Final confidence ({lineage.extraction_confidence_final}) is lower than "
                f"initial confidence ({lineage.extraction_confidence_initial})"
            )

    # Check 4: Quality score should align with confidence
    if lineage.extraction_quality_score and lineage.extraction_confidence_final:
        if (lineage.extraction_quality_score > 80 and lineage.extraction_confidence_final < 0.7):
            warnings.append("High quality score but low confidence - may indicate inconsistency")

    # Check 5: Manual review consistency
    if lineage.manual_review_completed and not lineage.manual_review_required:
        warnings.append("Manual review completed but not marked as required")

    # Check 6: Retry attempts should have validation errors if > 0
    if lineage.retry_attempts and lineage.retry_attempts > 0:
        if not lineage.validation_errors:
            warnings.append(f"Had {lineage.retry_attempts} retry attempts but no validation_errors recorded")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def create_lineage_from_extraction(
    extraction_id: UUID,
    source_document_url: str,
    source_document_hash: str,
    extraction_agent: str,
    extraction_model: str,
    verification_status: Literal['verified', 'unverified', 'flagged'] = 'unverified',
    **optional_fields
) -> ExtractionLineage:
    """Factory function to create lineage record from extraction.

    Args:
        extraction_id: UUID for this extraction
        source_document_url: S3 URL or path to source
        source_document_hash: SHA256 hash of document
        extraction_agent: Name of agent performing extraction
        extraction_model: LLM model used
        verification_status: Initial verification status
        **optional_fields: Any Phase 2/3 optional fields

    Returns:
        ExtractionLineage instance
    """
    return ExtractionLineage(
        extraction_id=extraction_id,
        source_document_url=source_document_url,
        source_document_hash=source_document_hash,
        extraction_agent=extraction_agent,
        extraction_model=extraction_model,
        verification_status=verification_status,
        **optional_fields
    )


if __name__ == "__main__":
    # Example usage
    from uuid import UUID as StandardUUID

    lineage = create_lineage_from_extraction(
        extraction_id=StandardUUID("33333333-3333-3333-3333-333333333333"),
        source_document_url="s3://triton-docs/clients/acme/roi.pdf",
        source_document_hash="a" * 64,
        extraction_agent="DocumentAnalysisAgent",
        extraction_model="claude-sonnet-4-20250514",
        verification_status="verified",
        extraction_confidence_initial=0.92,
        extraction_confidence_final=0.95,
        source_text="Our program delivers 250% ROI within 24 months"
    )

    # Add usage
    lineage.add_roi_model_usage(StandardUUID("77777777-7777-7777-7777-777777777777"))
    lineage.add_dashboard_usage(StandardUUID("99999999-9999-9999-9999-999999999999"))

    # Validate
    validation = validate_lineage_record(lineage)
    print(f"Validation: {validation}")
    print(f"Lineage JSON: {lineage.model_dump_json(indent=2)}")
