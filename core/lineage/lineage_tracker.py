"""Lineage Tracker for creating and updating extraction lineage records.

This module provides the interface between agents and the PostgreSQL lineage database.
It handles creating lineage records, updating usage tracking, and managing lineage lifecycle.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

from core.lineage.models import ExtractionLineage, create_lineage_from_extraction
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


class LineageTracker:
    """Tracks extraction lineage in PostgreSQL database.

    This class provides methods to:
    - Create new lineage records when extractions occur
    - Update usage tracking when extractions are used in ROI models/dashboards
    - Query lineage history and impact analysis
    - Mark extractions for review or as verified
    """

    def __init__(self, connection_string: str):
        """Initialize lineage tracker.

        Args:
            connection_string: PostgreSQL connection string
                Example: "postgresql://triton:password@localhost:5432/triton_db"
        """
        self.connection_string = connection_string

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def create_lineage_record(
        self,
        extraction_id: UUID,
        source_document_url: str,
        source_document_content: str,
        extraction_agent: str,
        extraction_model: str,
        verification_status: str = 'unverified',
        verification_issues: Optional[List[str]] = None,
        **optional_fields
    ) -> ExtractionLineage:
        """Create new lineage record in database.

        Args:
            extraction_id: Unique extraction identifier
            source_document_url: S3 URL or path to source document
            source_document_content: Full text content of document (for hashing)
            extraction_agent: Name of agent performing extraction
            extraction_model: LLM model used
            verification_status: Initial verification status
            verification_issues: List of verification issues (if flagged)
            **optional_fields: Any Phase 2/3 optional fields

        Returns:
            ExtractionLineage instance
        """
        # Compute SHA256 hash of source document
        source_document_hash = hashlib.sha256(
            source_document_content.encode('utf-8')
        ).hexdigest()

        # Create Pydantic model
        lineage = create_lineage_from_extraction(
            extraction_id=extraction_id,
            source_document_url=source_document_url,
            source_document_hash=source_document_hash,
            extraction_agent=extraction_agent,
            extraction_model=extraction_model,
            verification_status=verification_status,
            verification_issues=verification_issues or [],
            **optional_fields
        )

        # Insert into database
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO extraction_lineage (
                        extraction_id,
                        extraction_timestamp,
                        source_document_url,
                        source_document_hash,
                        extraction_agent,
                        extraction_model,
                        verification_status,
                        verification_issues,
                        used_in_roi_models,
                        used_in_dashboards,
                        retry_attempts,
                        extraction_confidence_initial,
                        extraction_confidence_final,
                        manual_review_required,
                        manual_review_completed,
                        extraction_quality_score,
                        source_text,
                        extraction_reasoning,
                        validation_errors
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    str(lineage.extraction_id),
                    lineage.extraction_timestamp,
                    lineage.source_document_url,
                    lineage.source_document_hash,
                    lineage.extraction_agent,
                    lineage.extraction_model,
                    lineage.verification_status,
                    lineage.verification_issues,
                    [str(uuid) for uuid in lineage.used_in_roi_models],
                    [str(uuid) for uuid in lineage.used_in_dashboards],
                    lineage.retry_attempts,
                    lineage.extraction_confidence_initial,
                    lineage.extraction_confidence_final,
                    lineage.manual_review_required,
                    lineage.manual_review_completed,
                    lineage.extraction_quality_score,
                    lineage.source_text,
                    lineage.extraction_reasoning,
                    lineage.validation_errors
                ))

        logger.info(f"Created lineage record {extraction_id}")
        return lineage

    def link_to_roi_model(
        self,
        extraction_id: UUID,
        roi_model_id: UUID
    ) -> None:
        """Link extraction to ROI model (updates used_in_roi_models).

        Args:
            extraction_id: Extraction UUID
            roi_model_id: ROI model UUID
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Use helper function from database
                cur.execute(
                    "SELECT link_extraction_to_roi_model(%s, %s)",
                    (str(extraction_id), str(roi_model_id))
                )

        logger.info(f"Linked extraction {extraction_id} to ROI model {roi_model_id}")

    def link_to_dashboard(
        self,
        roi_model_id: UUID,
        dashboard_id: UUID
    ) -> int:
        """Link ROI model to dashboard (updates used_in_dashboards for all extractions).

        Args:
            roi_model_id: ROI model UUID
            dashboard_id: Dashboard UUID

        Returns:
            Number of lineage records updated
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Use helper function from database
                cur.execute(
                    "SELECT link_roi_model_to_dashboard(%s, %s)",
                    (str(roi_model_id), str(dashboard_id))
                )
                result = cur.fetchone()
                count = result[0] if result else 0

        logger.info(f"Linked ROI model {roi_model_id} to dashboard {dashboard_id} ({count} extractions updated)")
        return count

    def get_lineage_by_id(
        self,
        extraction_id: UUID
    ) -> Optional[ExtractionLineage]:
        """Get lineage record by extraction ID.

        Args:
            extraction_id: Extraction UUID

        Returns:
            ExtractionLineage instance or None if not found
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM extraction_lineage WHERE extraction_id = %s",
                    (str(extraction_id),)
                )
                row = cur.fetchone()

        if not row:
            return None

        # Convert to Pydantic model
        return self._row_to_lineage(dict(row))

    def find_by_document_hash(
        self,
        document_hash: str
    ) -> List[ExtractionLineage]:
        """Find all extractions from a specific document.

        Args:
            document_hash: SHA256 hash of source document

        Returns:
            List of ExtractionLineage instances
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM extraction_lineage WHERE source_document_hash = %s",
                    (document_hash,)
                )
                rows = cur.fetchall()

        return [self._row_to_lineage(dict(row)) for row in rows]

    def find_affected_dashboards(
        self,
        document_hash: str
    ) -> List[Dict[str, Any]]:
        """Find all dashboards affected by a document change.

        Args:
            document_hash: SHA256 hash of changed document

        Returns:
            List of dicts with extraction_id, roi_model_id, dashboard_id
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM find_affected_dashboards(%s)",
                    (document_hash,)
                )
                rows = cur.fetchall()

        return [dict(row) for row in rows]

    def mark_for_review(
        self,
        extraction_id: UUID,
        issues: List[str]
    ) -> None:
        """Mark extraction as needing manual review.

        Args:
            extraction_id: Extraction UUID
            issues: List of verification issues
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE extraction_lineage
                    SET
                        verification_status = 'flagged',
                        verification_issues = %s,
                        manual_review_required = TRUE,
                        updated_at = NOW()
                    WHERE extraction_id = %s
                """, (issues, str(extraction_id)))

        logger.info(f"Marked extraction {extraction_id} for review with {len(issues)} issues")

    def mark_verified(
        self,
        extraction_id: UUID
    ) -> None:
        """Mark extraction as verified.

        Args:
            extraction_id: Extraction UUID
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE extraction_lineage
                    SET
                        verification_status = 'verified',
                        manual_review_completed = TRUE,
                        updated_at = NOW()
                    WHERE extraction_id = %s
                """, (str(extraction_id),))

        logger.info(f"Marked extraction {extraction_id} as verified")

    def get_flagged_extractions(self) -> List[ExtractionLineage]:
        """Get all extractions flagged for review.

        Returns:
            List of flagged ExtractionLineage instances
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM extraction_lineage WHERE verification_status = 'flagged' ORDER BY extraction_timestamp DESC"
                )
                rows = cur.fetchall()

        return [self._row_to_lineage(dict(row)) for row in rows]

    def update_last_accessed(
        self,
        extraction_id: UUID
    ) -> None:
        """Update last_accessed timestamp.

        Args:
            extraction_id: Extraction UUID
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE extraction_lineage
                    SET last_accessed = NOW()
                    WHERE extraction_id = %s
                """, (str(extraction_id),))

    def _row_to_lineage(self, row: Dict[str, Any]) -> ExtractionLineage:
        """Convert database row to ExtractionLineage model.

        Args:
            row: Database row as dict

        Returns:
            ExtractionLineage instance
        """
        # Convert UUID strings to UUID objects
        row['extraction_id'] = UUID(row['extraction_id'])
        row['used_in_roi_models'] = [UUID(uuid_str) for uuid_str in (row.get('used_in_roi_models') or [])]
        row['used_in_dashboards'] = [UUID(uuid_str) for uuid_str in (row.get('used_in_dashboards') or [])]

        # Remove database-only fields
        row.pop('created_at', None)
        row.pop('updated_at', None)

        return ExtractionLineage(**row)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_tracker_from_env() -> LineageTracker:
    """Create lineage tracker from environment variables.

    Expects DATABASE_URL environment variable with PostgreSQL connection string.

    Returns:
        LineageTracker instance
    """
    import os
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        # Fallback to Docker default
        database_url = "postgresql://triton:triton_password@localhost:5432/triton_db"
        logger.warning(f"DATABASE_URL not set, using default: {database_url}")

    return LineageTracker(connection_string=database_url)


def compute_document_hash(document_text: str) -> str:
    """Compute SHA256 hash of document text.

    Args:
        document_text: Full text content of document

    Returns:
        SHA256 hash as hex string (64 characters)
    """
    return hashlib.sha256(document_text.encode('utf-8')).hexdigest()


if __name__ == "__main__":
    # Example usage
    tracker = create_tracker_from_env()

    # Create lineage record
    extraction_id = uuid4()
    doc_content = "Our diabetes management program delivers 250% ROI within 24 months"

    lineage = tracker.create_lineage_record(
        extraction_id=extraction_id,
        source_document_url="s3://triton-docs/clients/acme/roi.pdf",
        source_document_content=doc_content,
        extraction_agent="DocumentAnalysisAgent",
        extraction_model="claude-sonnet-4-20250514",
        verification_status="verified",
        extraction_confidence_initial=0.92,
        extraction_confidence_final=0.95,
        source_text="delivers 250% ROI within 24 months"
    )

    print(f"Created lineage record: {lineage.extraction_id}")

    # Link to ROI model
    roi_model_id = uuid4()
    tracker.link_to_roi_model(extraction_id, roi_model_id)

    # Link to dashboard
    dashboard_id = uuid4()
    count = tracker.link_to_dashboard(roi_model_id, dashboard_id)
    print(f"Linked to dashboard ({count} extractions updated)")

    # Find by document hash
    doc_hash = compute_document_hash(doc_content)
    extractions = tracker.find_by_document_hash(doc_hash)
    print(f"Found {len(extractions)} extractions for document {doc_hash}")

    # Impact analysis
    affected = tracker.find_affected_dashboards(doc_hash)
    print(f"Found {len(affected)} affected dashboards")
