"""
Database connection and session management for Triton Agentic.

Provides SQLAlchemy engine, session factory, and FastAPI dependencies.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from core.config.settings import get_config
from core.monitoring.logger import get_logger

logger = get_logger(__name__)
config = get_config()


# =============================================================================
# Engine Configuration
# =============================================================================


def create_db_engine(pool_pre_ping: bool = True) -> Engine:
    """
    Create SQLAlchemy engine with connection pooling.

    Args:
        pool_pre_ping: Enable connection health checks before use

    Returns:
        SQLAlchemy Engine instance
    """
    database_url = config.database.get_database_url()

    # Connection pool settings
    pool_size = config.database.pool_size
    max_overflow = config.database.max_overflow
    pool_timeout = config.database.pool_timeout
    pool_recycle = config.database.pool_recycle

    logger.info(
        f"Creating database engine: {config.database.postgres_host}:{config.database.postgres_port}/{config.database.postgres_db}"
    )

    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        pool_pre_ping=pool_pre_ping,
        echo=config.debug_mode,  # Log SQL queries in debug mode
        future=True,  # Use SQLAlchemy 2.0 style
    )

    # Register connection event listeners
    register_engine_events(engine)

    return engine


def create_celery_db_engine() -> Engine:
    """
    Create SQLAlchemy engine optimized for Celery workers.

    Uses NullPool to avoid connection pooling issues in multiprocessing.

    Returns:
        SQLAlchemy Engine instance
    """
    database_url = config.database.get_database_url()

    logger.info("Creating Celery database engine (NullPool)")

    engine = create_engine(
        database_url,
        poolclass=NullPool,  # No pooling for Celery workers
        echo=config.debug_mode,
        future=True,
    )

    return engine


def register_engine_events(engine: Engine) -> None:
    """
    Register SQLAlchemy engine event listeners for monitoring.

    Args:
        engine: SQLAlchemy Engine instance
    """

    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Log database connections."""
        logger.debug("Database connection established")

    @event.listens_for(engine, "close")
    def receive_close(dbapi_conn, connection_record):
        """Log database disconnections."""
        logger.debug("Database connection closed")

    @event.listens_for(engine, "checkin")
    def receive_checkin(dbapi_conn, connection_record):
        """Log connection pool checkins."""
        logger.debug("Connection returned to pool")

    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        """Log connection pool checkouts."""
        logger.debug("Connection borrowed from pool")


# =============================================================================
# Session Management
# =============================================================================


# Global engine and session factory
_engine: Engine = None
_SessionLocal: sessionmaker = None


def init_db() -> None:
    """Initialize database engine and session factory."""
    global _engine, _SessionLocal

    if _engine is None:
        _engine = create_db_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine,
            expire_on_commit=False,
        )
        logger.info("Database initialized successfully")


def get_engine() -> Engine:
    """
    Get the global database engine.

    Returns:
        SQLAlchemy Engine instance
    """
    if _engine is None:
        init_db()
    return _engine


def get_session_factory() -> sessionmaker:
    """
    Get the global session factory.

    Returns:
        SQLAlchemy sessionmaker
    """
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Yields:
        SQLAlchemy Session

    Example:
        ```python
        with get_db_session() as session:
            client = session.query(Client).first()
        ```
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        SQLAlchemy Session

    Example:
        ```python
        @app.get("/clients")
        def list_clients(db: Session = Depends(get_db)):
            return db.query(Client).all()
        ```
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# =============================================================================
# Utility Functions
# =============================================================================


def health_check() -> bool:
    """
    Check database connectivity.

    Returns:
        True if database is reachable, False otherwise
    """
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def close_db() -> None:
    """Close database engine and cleanup resources."""
    global _engine, _SessionLocal

    if _engine is not None:
        logger.info("Closing database connections")
        _engine.dispose()
        _engine = None
        _SessionLocal = None


# =============================================================================
# Celery-specific Database Session
# =============================================================================


def get_celery_db_session() -> Session:
    """
    Create a database session for Celery tasks.

    Uses NullPool to avoid connection pooling issues in multiprocessing.

    Returns:
        SQLAlchemy Session

    Example:
        ```python
        @celery_app.task
        def my_task():
            session = get_celery_db_session()
            try:
                # Use session
                client = session.query(Client).first()
                session.commit()
            finally:
                session.close()
        ```
    """
    engine = create_celery_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
