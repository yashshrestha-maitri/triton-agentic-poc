"""
API routes for client and value proposition management.

Provides endpoints for:
- Creating and managing clients
- Creating and managing value propositions
- Listing clients and their value propositions
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.database import Client, ValueProposition, get_db
from core.monitoring.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/clients", tags=["Clients"])


# =============================================================================
# Pydantic Models for Request/Response
# =============================================================================


class ClientCreateRequest(BaseModel):
    """Request model for creating a new client."""

    name: str = Field(..., min_length=1, description="Client name")
    industry: Optional[str] = Field(None, description="Industry sector")
    meta_data: Optional[dict] = Field(None, description="Additional metadata")


class ClientResponse(BaseModel):
    """Response model for client data."""

    id: UUID
    name: str
    industry: Optional[str]
    created_at: datetime
    updated_at: datetime
    meta_data: Optional[dict]

    class Config:
        from_attributes = True


class ValuePropositionCreateRequest(BaseModel):
    """Request model for creating a new value proposition."""

    content: str = Field(..., min_length=10, description="Value proposition content")
    is_active: bool = Field(True, description="Whether this value proposition is active")
    meta_data: Optional[dict] = Field(None, description="Additional metadata")


class ValuePropositionResponse(BaseModel):
    """Response model for value proposition data."""

    id: UUID
    client_id: UUID
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    meta_data: Optional[dict]

    class Config:
        from_attributes = True


class ClientWithValuePropsResponse(BaseModel):
    """Response model for client with value propositions."""

    client: ClientResponse
    value_propositions: List[ValuePropositionResponse]


# =============================================================================
# Client Endpoints
# =============================================================================


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    request: ClientCreateRequest,
    db: Session = Depends(get_db),
) -> ClientResponse:
    """
    Create a new client.

    A client represents an organization using the dashboard template system.
    """
    logger.info(f"Creating new client: {request.name}")

    client = Client(
        name=request.name,
        industry=request.industry,
        meta_data=request.meta_data,
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    logger.info(f"Created client: id={client.id}, name={client.name}")

    return ClientResponse.model_validate(client)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
) -> ClientResponse:
    """Get a specific client by ID."""
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client not found: {client_id}",
        )

    return ClientResponse.model_validate(client)


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    industry: Optional[str] = Query(None, description="Filter by industry"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> List[ClientResponse]:
    """
    List all clients with optional filtering and pagination.
    """
    query = db.query(Client)

    if industry:
        query = query.filter(Client.industry == industry)

    clients = (
        query.order_by(Client.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return [ClientResponse.model_validate(client) for client in clients]


@router.get("/{client_id}/with-value-props", response_model=ClientWithValuePropsResponse)
def get_client_with_value_props(
    client_id: UUID,
    db: Session = Depends(get_db),
) -> ClientWithValuePropsResponse:
    """Get a client along with all their value propositions."""
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client not found: {client_id}",
        )

    value_props = (
        db.query(ValueProposition)
        .filter(ValueProposition.client_id == client_id)
        .order_by(ValueProposition.created_at.desc())
        .all()
    )

    return ClientWithValuePropsResponse(
        client=ClientResponse.model_validate(client),
        value_propositions=[ValuePropositionResponse.model_validate(vp) for vp in value_props],
    )


# =============================================================================
# Value Proposition Endpoints
# =============================================================================


@router.post(
    "/{client_id}/value-propositions",
    response_model=ValuePropositionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_value_proposition(
    client_id: UUID,
    request: ValuePropositionCreateRequest,
    db: Session = Depends(get_db),
) -> ValuePropositionResponse:
    """
    Create a new value proposition for a client.

    Value propositions are used as input context for template generation.
    """
    # Validate client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client not found: {client_id}",
        )

    logger.info(f"Creating value proposition for client_id={client_id}")

    value_prop = ValueProposition(
        client_id=client_id,
        content=request.content,
        is_active=request.is_active,
        meta_data=request.meta_data,
    )

    db.add(value_prop)
    db.commit()
    db.refresh(value_prop)

    logger.info(f"Created value proposition: id={value_prop.id}")

    return ValuePropositionResponse.model_validate(value_prop)


@router.get(
    "/{client_id}/value-propositions",
    response_model=List[ValuePropositionResponse],
)
def list_value_propositions(
    client_id: UUID,
    active_only: bool = Query(False, description="Show only active value propositions"),
    db: Session = Depends(get_db),
) -> List[ValuePropositionResponse]:
    """List all value propositions for a client."""
    # Validate client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client not found: {client_id}",
        )

    query = db.query(ValueProposition).filter(ValueProposition.client_id == client_id)

    if active_only:
        query = query.filter(ValueProposition.is_active == True)

    value_props = query.order_by(ValueProposition.created_at.desc()).all()

    return [ValuePropositionResponse.model_validate(vp) for vp in value_props]


@router.patch(
    "/{client_id}/value-propositions/{value_prop_id}",
    response_model=ValuePropositionResponse,
)
def update_value_proposition(
    client_id: UUID,
    value_prop_id: UUID,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
) -> ValuePropositionResponse:
    """
    Update a value proposition (currently only supports toggling active status).
    """
    value_prop = (
        db.query(ValueProposition)
        .filter(ValueProposition.id == value_prop_id)
        .filter(ValueProposition.client_id == client_id)
        .first()
    )

    if not value_prop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Value proposition not found: {value_prop_id}",
        )

    if is_active is not None:
        value_prop.is_active = is_active
        db.commit()
        db.refresh(value_prop)

    return ValuePropositionResponse.model_validate(value_prop)
