"""
TritonClient - HTTP client for integrating mare-api with triton-agentic service.

This file should be copied to mare-api project at: services/triton_client.py

Usage:
    from services.triton_client import TritonClient

    triton = TritonClient(base_url="http://triton-api:8000")
    client = await triton.create_client("HealthTech Inc", "Healthcare")
    job = await triton.submit_generation_job(client["id"])
"""

import asyncio
from typing import Dict, List, Optional

import httpx
from pydantic import BaseModel, Field


# =============================================================================
# Configuration
# =============================================================================


class TritonConfig(BaseModel):
    """Configuration for Triton service connection."""

    base_url: str = Field(
        default="http://triton-api:8000",
        description="Base URL of triton-agentic service"
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")


# =============================================================================
# Triton Client
# =============================================================================


class TritonClient:
    """
    HTTP client for triton-agentic service.

    Provides methods for all Triton operations:
    - Client management
    - Value proposition management
    - Async template generation
    - Template retrieval
    """

    def __init__(self, config: Optional[TritonConfig] = None):
        """
        Initialize Triton client.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or TritonConfig()

        # Build headers
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        # Create HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=headers,
        )

    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    # =========================================================================
    # Client Management
    # =========================================================================

    async def create_client(
        self,
        name: str,
        industry: Optional[str] = None,
        meta_data: Optional[Dict] = None,
    ) -> Dict:
        """
        Create a new client in Triton.

        Args:
            name: Client name (required)
            industry: Industry sector (optional)
            meta_data: Additional metadata (optional)

        Returns:
            Client object with id, name, industry, created_at, etc.

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        response = await self.client.post(
            "/clients/",
            json={"name": name, "industry": industry, "meta_data": meta_data or {}},
        )
        response.raise_for_status()
        return response.json()

    async def get_client(self, client_id: str) -> Dict:
        """
        Get client by ID.

        Args:
            client_id: Client UUID

        Returns:
            Client object

        Raises:
            httpx.HTTPStatusError: If client not found (404)
        """
        response = await self.client.get(f"/clients/{client_id}")
        response.raise_for_status()
        return response.json()

    async def list_clients(
        self, industry: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> List[Dict]:
        """
        List clients with optional filtering and pagination.

        Args:
            industry: Filter by industry (optional)
            page: Page number (default: 1)
            page_size: Items per page (default: 20, max: 100)

        Returns:
            List of client objects
        """
        params = {"page": page, "page_size": page_size}
        if industry:
            params["industry"] = industry

        response = await self.client.get("/clients/", params=params)
        response.raise_for_status()
        return response.json()

    async def get_client_with_value_props(self, client_id: str) -> Dict:
        """
        Get client with all their value propositions.

        Args:
            client_id: Client UUID

        Returns:
            Dict with 'client' and 'value_propositions' keys
        """
        response = await self.client.get(f"/clients/{client_id}/with-value-props")
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # Value Proposition Management
    # =========================================================================

    async def create_value_proposition(
        self,
        client_id: str,
        content: str,
        is_active: bool = True,
        meta_data: Optional[Dict] = None,
    ) -> Dict:
        """
        Create a value proposition for a client.

        Args:
            client_id: Client UUID
            content: Value proposition text (min 10 characters)
            is_active: Whether this value proposition is active
            meta_data: Additional metadata

        Returns:
            Value proposition object

        Raises:
            httpx.HTTPStatusError: If client not found or validation fails
        """
        response = await self.client.post(
            f"/clients/{client_id}/value-propositions",
            json={
                "content": content,
                "is_active": is_active,
                "meta_data": meta_data or {},
            },
        )
        response.raise_for_status()
        return response.json()

    async def list_value_propositions(
        self, client_id: str, active_only: bool = False
    ) -> List[Dict]:
        """
        List value propositions for a client.

        Args:
            client_id: Client UUID
            active_only: Show only active value propositions

        Returns:
            List of value proposition objects
        """
        params = {"active_only": active_only}
        response = await self.client.get(
            f"/clients/{client_id}/value-propositions", params=params
        )
        response.raise_for_status()
        return response.json()

    async def update_value_proposition(
        self, client_id: str, value_prop_id: str, is_active: bool
    ) -> Dict:
        """
        Update value proposition active status.

        Args:
            client_id: Client UUID
            value_prop_id: Value proposition UUID
            is_active: New active status

        Returns:
            Updated value proposition object
        """
        response = await self.client.patch(
            f"/clients/{client_id}/value-propositions/{value_prop_id}",
            params={"is_active": is_active},
        )
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # Template Generation (Async Jobs)
    # =========================================================================

    async def submit_generation_job(
        self, client_id: str, value_proposition_id: Optional[str] = None
    ) -> Dict:
        """
        Submit template generation job (async).

        This returns immediately with a job_id. The actual generation
        happens in the background via Celery worker.

        Poll get_job_status() to check completion, or use
        wait_for_job_completion() to block until done.

        Args:
            client_id: Client UUID
            value_proposition_id: Optional specific value prop UUID.
                                 Uses latest active if not provided.

        Returns:
            Job object with job_id, status="pending", celery_task_id

        Raises:
            httpx.HTTPStatusError: If client/value prop not found
        """
        response = await self.client.post(
            "/jobs/",
            json={
                "client_id": client_id,
                "value_proposition_id": value_proposition_id,
            },
        )
        response.raise_for_status()
        return response.json()

    async def get_job_status(self, job_id: str) -> Dict:
        """
        Get status of a generation job.

        Args:
            job_id: Job UUID

        Returns:
            Job status object with fields:
            - job_id: UUID
            - status: pending|running|completed|failed|cancelled
            - started_at: ISO timestamp or null
            - completed_at: ISO timestamp or null
            - generation_duration_ms: int or null
            - error_message: string or null

        Raises:
            httpx.HTTPStatusError: If job not found (404)
        """
        response = await self.client.get(f"/jobs/{job_id}")
        response.raise_for_status()
        return response.json()

    async def list_jobs(
        self,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """
        List generation jobs with filtering.

        Args:
            client_id: Filter by client UUID
            status: Filter by status (pending, running, completed, failed, cancelled)
            page: Page number
            page_size: Items per page

        Returns:
            Dict with 'total', 'page', 'page_size', 'jobs' keys
        """
        params = {"page": page, "page_size": page_size}
        if client_id:
            params["client_id"] = client_id
        if status:
            params["status"] = status

        response = await self.client.get("/jobs/", params=params)
        response.raise_for_status()
        return response.json()

    async def cancel_job(self, job_id: str) -> None:
        """
        Cancel a pending or running job.

        Args:
            job_id: Job UUID

        Raises:
            httpx.HTTPStatusError: If job not found or already completed
        """
        response = await self.client.delete(f"/jobs/{job_id}")
        response.raise_for_status()

    async def wait_for_job_completion(
        self, job_id: str, poll_interval: int = 2, max_wait: int = 300
    ) -> Dict:
        """
        Wait for job to complete (blocking).

        Polls job status every poll_interval seconds until completed/failed.

        Args:
            job_id: Job UUID
            poll_interval: Seconds between status checks (default: 2)
            max_wait: Maximum seconds to wait (default: 300 = 5 minutes)

        Returns:
            Final job status (status="completed")

        Raises:
            TimeoutError: If job doesn't complete within max_wait
            Exception: If job fails (includes error message)
        """
        elapsed = 0
        while elapsed < max_wait:
            status = await self.get_job_status(job_id)

            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                error_msg = status.get("error_message", "Unknown error")
                raise Exception(f"Job {job_id} failed: {error_msg}")
            elif status["status"] == "cancelled":
                raise Exception(f"Job {job_id} was cancelled")

            # Still pending/running
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(
            f"Job {job_id} did not complete within {max_wait} seconds"
        )

    # =========================================================================
    # Template Retrieval
    # =========================================================================

    async def list_templates(
        self,
        client_id: Optional[str] = None,
        job_id: Optional[str] = None,
        category: Optional[str] = None,
        target_audience: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """
        List generated templates with filtering.

        Args:
            client_id: Filter by client UUID
            job_id: Filter by generation job UUID
            category: Filter by category (roi-focused, clinical-outcomes, etc.)
            target_audience: Filter by target audience
            page: Page number
            page_size: Items per page

        Returns:
            Dict with 'total', 'page', 'page_size', 'templates' keys
        """
        params = {"page": page, "page_size": page_size}
        if client_id:
            params["client_id"] = client_id
        if job_id:
            params["job_id"] = job_id
        if category:
            params["category"] = category
        if target_audience:
            params["target_audience"] = target_audience

        response = await self.client.get("/templates/", params=params)
        response.raise_for_status()
        return response.json()

    async def get_template(self, template_id: str) -> Dict:
        """
        Get specific template by ID.

        Args:
            template_id: Template UUID

        Returns:
            Template object with full details (widgets, visual_style, etc.)

        Raises:
            httpx.HTTPStatusError: If template not found (404)
        """
        response = await self.client.get(f"/templates/{template_id}")
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # Health Check
    # =========================================================================

    async def health_check(self) -> Dict:
        """
        Check if Triton service is healthy.

        Returns:
            Health status with database and API status
        """
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()


# =============================================================================
# Dependency Injection Helper (for FastAPI)
# =============================================================================


_triton_client: Optional[TritonClient] = None


def get_triton_client() -> TritonClient:
    """
    FastAPI dependency for Triton client.

    Usage:
        @app.get("/clients")
        async def list_clients(triton: TritonClient = Depends(get_triton_client)):
            return await triton.list_clients()
    """
    global _triton_client
    if _triton_client is None:
        # Initialize with defaults or from environment
        import os

        config = TritonConfig(
            base_url=os.getenv("TRITON_API_URL", "http://triton-api:8000"),
            api_key=os.getenv("TRITON_API_KEY"),
        )
        _triton_client = TritonClient(config)
    return _triton_client


async def close_triton_client():
    """
    Cleanup function to close Triton client.

    Call this in FastAPI shutdown event:
        @app.on_event("shutdown")
        async def shutdown():
            await close_triton_client()
    """
    global _triton_client
    if _triton_client is not None:
        await _triton_client.close()
        _triton_client = None
