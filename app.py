"""FastAPI application for Triton Template Generation API.

This API provides endpoints for:
- Generating dashboard templates using AI agents
- Managing template results (CRUD operations)
- Listing and filtering templates
- Downloading generation results

Run with: uvicorn app:app --reload
"""

import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from api.routes import templates, jobs, clients, prospect_data, research, roi_models, lineage
from api.models.responses import ErrorResponse, HealthCheckResponse
from core.database import init_db, close_db, health_check as db_health_check
from core.monitoring.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Triton Template Generation API",
    description="""
    REST API for generating and managing dashboard templates using AI agents.

    ## Features

    * **Template Generation**: Generate 5-10 dashboard template variations using AI
    * **Template Management**: CRUD operations for managing templates
    * **Result Management**: Store, retrieve, and download generation results
    * **Filtering & Search**: Filter templates by category and target audience
    * **Statistics**: Get insights about generated templates

    ## Authentication

    Currently, no authentication is required (development mode).
    In production, add API key or OAuth2 authentication.
    """,
    version="1.0.0",
    contact={
        "name": "Triton Team",
        "email": "support@triton.example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Prometheus Metrics Instrumentation
# =============================================================================
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    from prometheus_client import Counter, Histogram, Gauge

    # Initialize instrumentator
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    # Instrument the app and expose metrics endpoint
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    # Custom metrics for Triton-specific operations
    template_generation_counter = Counter(
        'triton_template_generations_total',
        'Total template generation requests',
        ['client_id', 'status']
    )

    agent_execution_duration = Histogram(
        'triton_agent_execution_seconds',
        'Agent execution duration in seconds',
        ['agent_name', 'success'],
        buckets=(1, 5, 10, 30, 60, 120, 300)
    )

    active_jobs_gauge = Gauge(
        'triton_active_jobs',
        'Number of currently active generation jobs'
    )

    job_queue_length = Gauge(
        'triton_job_queue_length',
        'Number of pending jobs in queue'
    )

    logger.info("Prometheus metrics instrumentation enabled at /metrics")

except ImportError:
    logger.warning("prometheus-fastapi-instrumentator not installed, metrics disabled")
    logger.warning("Install with: pip install prometheus-fastapi-instrumentator")


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "status_code": 422
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "status_code": 500
        }
    )


# Health check endpoint
@app.get("/", response_model=HealthCheckResponse, tags=["health"])
async def root():
    """
    Root endpoint - API health check.

    Returns basic information about the API status and version.
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.

    Used by monitoring systems to verify API availability.
    Includes database connectivity check.
    """
    db_status = "healthy" if db_health_check() else "unhealthy"
    overall_status = "healthy" if db_status == "healthy" else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "database": db_status,
            "api": "healthy"
        }
    }


# Register routers
app.include_router(clients.router)
app.include_router(jobs.router)
app.include_router(templates.router)
app.include_router(prospect_data.router)
app.include_router(research.router)
app.include_router(roi_models.router)
app.include_router(lineage.router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Triton Template Generation API...")

    # Initialize database connection
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("API starting without database connection")

    logger.info("API documentation available at: /docs")
    logger.info("Alternative documentation at: /redoc")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down Triton Template Generation API...")

    # Close database connections
    try:
        close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
