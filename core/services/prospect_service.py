"""
Prospect management service.

Handles prospect creation, retrieval, and dashboard data association.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from core.database.models import Prospect, Client
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


class ProspectService:
    """Service for managing prospects and their dashboard data."""

    def __init__(self, session: Session):
        """
        Initialize prospect service.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def get_or_create_demo_prospect(self, client_id: UUID) -> Prospect:
        """
        Get or create a demo prospect for a client.

        Used for template generation to have a default prospect to link dashboard
        data to. Each client gets one demo prospect for testing/preview purposes.

        Args:
            client_id: Client UUID

        Returns:
            Prospect: Demo prospect for the client

        Raises:
            ValueError: If client does not exist
        """
        # Verify client exists
        client = self.session.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client not found: {client_id}")

        # Look for existing demo prospect
        prospect = (
            self.session.query(Prospect)
            .filter(Prospect.client_id == client_id)
            .filter(Prospect.email == "demo@triton-agentic.local")
            .first()
        )

        if prospect:
            logger.info(f"Found existing demo prospect for client {client_id}: {prospect.id}")
            return prospect

        # Create new demo prospect
        prospect = Prospect(
            client_id=client_id,
            name=f"Demo Prospect - {client.name}",
            organization=f"{client.name} Demo",
            email="demo@triton-agentic.local",
            meta_data={
                "is_demo": True,
                "purpose": "Template generation preview",
                "auto_generated": True
            }
        )

        self.session.add(prospect)
        self.session.flush()  # Get the ID without committing

        logger.info(
            f"Created demo prospect for client {client_id}: "
            f"prospect_id={prospect.id}, name={prospect.name}"
        )

        return prospect

    def get_prospect(self, prospect_id: UUID) -> Optional[Prospect]:
        """
        Get prospect by ID.

        Args:
            prospect_id: Prospect UUID

        Returns:
            Prospect or None if not found
        """
        return self.session.query(Prospect).filter(Prospect.id == prospect_id).first()

    def create_prospect(
        self,
        client_id: UUID,
        name: str,
        organization: Optional[str] = None,
        email: Optional[str] = None,
        meta_data: Optional[dict] = None
    ) -> Prospect:
        """
        Create a new prospect.

        Args:
            client_id: Client UUID
            name: Prospect name
            organization: Optional organization name
            email: Optional email address
            meta_data: Optional additional metadata

        Returns:
            Created prospect

        Raises:
            ValueError: If client does not exist
        """
        # Verify client exists
        client = self.session.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client not found: {client_id}")

        prospect = Prospect(
            client_id=client_id,
            name=name,
            organization=organization,
            email=email,
            meta_data=meta_data or {}
        )

        self.session.add(prospect)
        self.session.flush()

        logger.info(f"Created prospect: {prospect.id} - {prospect.name}")
        return prospect

    def list_prospects(
        self,
        client_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Prospect]:
        """
        List prospects with optional filtering.

        Args:
            client_id: Optional filter by client
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of prospects
        """
        query = self.session.query(Prospect)

        if client_id:
            query = query.filter(Prospect.client_id == client_id)

        prospects = query.offset(skip).limit(limit).all()
        logger.info(f"Listed {len(prospects)} prospects (client_id={client_id})")

        return prospects

    def delete_prospect(self, prospect_id: UUID) -> bool:
        """
        Delete a prospect and all associated dashboard data.

        Args:
            prospect_id: Prospect UUID

        Returns:
            True if deleted, False if not found
        """
        prospect = self.session.query(Prospect).filter(Prospect.id == prospect_id).first()

        if not prospect:
            return False

        self.session.delete(prospect)
        logger.info(f"Deleted prospect: {prospect_id}")
        return True


def get_or_create_demo_prospect(session: Session, client_id: UUID) -> Prospect:
    """
    Convenience function to get or create demo prospect.

    Args:
        session: Database session
        client_id: Client UUID

    Returns:
        Demo prospect for the client
    """
    service = ProspectService(session)
    return service.get_or_create_demo_prospect(client_id)
