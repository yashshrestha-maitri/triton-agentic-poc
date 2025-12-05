"""
SQLAlchemy database models for Triton Agentic.

Maps PostgreSQL schema to Python ORM models.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


# =============================================================================
# Core Client and Value Proposition Models
# =============================================================================


class Client(Base):
    """Client organizations using the dashboard system."""

    __tablename__ = "clients"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    meta_data = Column(JSONB)

    # Relationships
    value_propositions = relationship(
        "ValueProposition", back_populates="client", cascade="all, delete-orphan"
    )
    prospects = relationship(
        "Prospect", back_populates="client", cascade="all, delete-orphan"
    )
    generation_jobs = relationship(
        "GenerationJob", back_populates="client", cascade="all, delete-orphan"
    )
    dashboard_templates = relationship(
        "DashboardTemplate", back_populates="client", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(name)) > 0", name="chk_name_not_empty"),
        Index("idx_clients_name", "name"),
        Index("idx_clients_industry", "industry"),
    )

    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name}, industry={self.industry})>"


class ValueProposition(Base):
    """Value propositions for template generation."""

    __tablename__ = "value_propositions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    meta_data = Column(JSONB)

    # Relationships
    client = relationship("Client", back_populates="value_propositions")
    generation_jobs = relationship("GenerationJob", back_populates="value_proposition")

    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(content)) > 0", name="chk_content_not_empty"),
        Index("idx_vp_client_id", "client_id"),
        Index("idx_vp_active", "client_id", "is_active"),
    )

    def __repr__(self):
        return f"<ValueProposition(id={self.id}, client_id={self.client_id}, is_active={self.is_active})>"


class Prospect(Base):
    """End-users/organizations viewing dashboards."""

    __tablename__ = "prospects"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    organization = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    meta_data = Column(JSONB)

    # Relationships
    client = relationship("Client", back_populates="prospects")
    dashboard_data = relationship(
        "ProspectDashboardData", back_populates="prospect", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(name)) > 0", name="chk_prospect_name_not_empty"),
        Index("idx_prospects_client_id", "client_id"),
        Index("idx_prospects_email", "email"),
    )

    def __repr__(self):
        return f"<Prospect(id={self.id}, name={self.name}, organization={self.organization})>"


# =============================================================================
# Template Generation Models
# =============================================================================


class GenerationJob(Base):
    """Tracks async template generation tasks."""

    __tablename__ = "generation_jobs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    value_proposition_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("value_propositions.id", ondelete="SET NULL"),
    )
    status = Column(String(50), nullable=False, default="pending")
    celery_task_id = Column(String(255), unique=True)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    generation_duration_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    meta_data = Column(JSONB)

    # Relationships
    client = relationship("Client", back_populates="generation_jobs")
    value_proposition = relationship(
        "ValueProposition", back_populates="generation_jobs"
    )
    dashboard_templates = relationship("DashboardTemplate", back_populates="job")
    agent_logs = relationship(
        "AgentExecutionLog", back_populates="job", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled')",
            name="chk_job_status",
        ),
        Index("idx_jobs_client_id", "client_id"),
        Index("idx_jobs_status", "status"),
        Index("idx_jobs_celery_task_id", "celery_task_id"),
        Index("idx_jobs_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<GenerationJob(id={self.id}, status={self.status}, client_id={self.client_id})>"


class ProspectDataJob(Base):
    """Tracks async prospect data generation tasks."""

    __tablename__ = "prospect_data_jobs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    prospect_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
    )
    template_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("dashboard_templates.id", ondelete="SET NULL"),
    )
    regenerate = Column(Boolean, default=False)
    status = Column(String(50), nullable=False, default="pending")
    celery_task_id = Column(String(255), unique=True)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    generation_duration_ms = Column(Integer)
    result_summary = Column(JSONB)  # Stats: total_templates, successful, failed, errors
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    meta_data = Column(JSONB)

    # Relationships
    prospect = relationship("Prospect")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled')",
            name="chk_prospect_data_job_status",
        ),
        Index("idx_prospect_data_jobs_prospect_id", "prospect_id"),
        Index("idx_prospect_data_jobs_status", "status"),
        Index("idx_prospect_data_jobs_celery_task_id", "celery_task_id"),
        Index("idx_prospect_data_jobs_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<ProspectDataJob(id={self.id}, status={self.status}, prospect_id={self.prospect_id})>"


class DashboardTemplate(Base):
    """Generated dashboard template configurations."""

    __tablename__ = "dashboard_templates"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="SET NULL")
    )
    client_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    target_audience = Column(String(100), nullable=False)
    visual_style = Column(JSONB, nullable=False)
    widgets = Column(JSONB, nullable=False)  # Array of WidgetConfiguration
    meta_data = Column(JSONB)
    status = Column(String(50), default="generated")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    job = relationship("GenerationJob", back_populates="dashboard_templates")
    client = relationship("Client", back_populates="dashboard_templates")
    prospect_data = relationship(
        "ProspectDashboardData", back_populates="template", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "category IN ('roi-focused', 'clinical-outcomes', 'operational-efficiency', "
            "'competitive-positioning', 'comprehensive')",
            name="chk_category",
        ),
        CheckConstraint(
            "status IN ('generated', 'approved', 'removed')", name="chk_template_status"
        ),
        Index("idx_dt_client_id", "client_id"),
        Index("idx_dt_job_id", "job_id"),
        Index("idx_dt_category", "category"),
        Index("idx_dt_status", "status"),
        Index(
            "idx_dt_widgets_gin",
            "widgets",
            postgresql_using="gin",
        ),
        Index(
            "idx_active_templates",
            "client_id",
            "category",
            postgresql_where=Column("status") == "approved",
        ),
    )

    def __repr__(self):
        return f"<DashboardTemplate(id={self.id}, name={self.name}, category={self.category})>"


class ProspectDashboardTemplate(Base):
    """Prospect dashboard templates with data requirements and analytics questions."""

    __tablename__ = "prospect_dashboard_templates"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    target_audience = Column(String(100), nullable=False)
    visual_style = Column(JSONB, nullable=False)  # VisualStyleNew
    widgets = Column(
        JSONB, nullable=False
    )  # Array of DashboardWidgetNew with data_requirements
    meta_data = Column("metadata", JSONB, nullable=False)  # TemplateMetadata
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client")
    prospect_data = relationship(
        "ProspectDashboardData",
        foreign_keys="ProspectDashboardData.prospect_template_id",
        back_populates="prospect_template",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "category IN ('roi-focused', 'clinical-outcomes', 'operational-efficiency', "
            "'competitive-positioning', 'comprehensive')",
            name="chk_prospect_template_category",
        ),
        CheckConstraint(
            "status IN ('draft', 'approved', 'archived', 'deprecated')",
            name="chk_prospect_template_status",
        ),
        Index("idx_pdt_client_id", "client_id"),
        Index("idx_pdt_category", "category"),
        Index("idx_pdt_status", "status"),
        Index("idx_pdt_widgets_gin", "widgets", postgresql_using="gin"),
    )

    def __repr__(self):
        return f"<ProspectDashboardTemplate(id={self.id}, name={self.name}, status={self.status})>"


class ProspectDashboardData(Base):
    """Stores generated data for specific prospects."""

    __tablename__ = "prospect_dashboard_data"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    prospect_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
    )
    template_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("dashboard_templates.id", ondelete="CASCADE"),
        nullable=True,  # Can be null if using prospect_template_id
    )
    prospect_template_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("prospect_dashboard_templates.id", ondelete="CASCADE"),
        nullable=True,  # Can be null if using template_id
    )
    dashboard_data = Column(JSONB, nullable=False)  # Complete widget data
    validation_result = Column(JSONB)  # DataValidationResult
    generated_at = Column(DateTime, nullable=False)
    generation_duration_ms = Column(Integer)
    generated_by = Column(String(255))
    status = Column(String(50), default="generating")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    prospect = relationship("Prospect", back_populates="dashboard_data")
    template = relationship("DashboardTemplate", back_populates="prospect_data")
    prospect_template = relationship(
        "ProspectDashboardTemplate", back_populates="prospect_data"
    )

    __table_args__ = (
        CheckConstraint(
            "(template_id IS NOT NULL AND prospect_template_id IS NULL) OR "
            "(template_id IS NULL AND prospect_template_id IS NOT NULL)",
            name="chk_one_template_ref",
        ),
        CheckConstraint(
            "status IN ('generating', 'ready', 'stale', 'error')",
            name="chk_prospect_data_status",
        ),
        Index("idx_prospect_dashboard_lookup", "prospect_id", "template_id"),
        Index("idx_prospect_dashboard_lookup2", "prospect_id", "prospect_template_id"),
        Index(
            "idx_prospect_dashboard_jsonb",
            "dashboard_data",
            postgresql_using="gin",
        ),
    )

    def __repr__(self):
        return f"<ProspectDashboardData(id={self.id}, prospect_id={self.prospect_id}, status={self.status})>"


class ProspectDataSchema(Base):
    """Defines available data schema for prospect data validation."""

    __tablename__ = "prospect_data_schemas"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    schema_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    fields = Column(JSONB, nullable=False)  # Array of field definitions
    available_metrics = Column(JSONB)  # Array of pre-calculated metrics
    time_fields = Column(JSONB)  # Array of time field names
    dimension_fields = Column(JSONB)  # Array of dimension field names
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    meta_data = Column(JSONB)

    # Relationships
    client = relationship("Client")

    __table_args__ = (
        UniqueConstraint("client_id", "schema_name", name="uq_client_schema"),
        Index("idx_pds_client_id", "client_id"),
        Index("idx_pds_active", "is_active"),
    )

    def __repr__(self):
        return f"<ProspectDataSchema(id={self.id}, schema_name={self.schema_name}, client_id={self.client_id})>"


# =============================================================================
# Audit and Logging Models
# =============================================================================


class AgentExecutionLog(Base):
    """Agent execution logs for monitoring and debugging."""

    __tablename__ = "agent_execution_logs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="CASCADE")
    )
    agent_name = Column(String(255), nullable=False)
    execution_time_ms = Column(Integer)
    token_usage = Column(JSONB)
    error_count = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    success = Column(Boolean, nullable=False)
    error_details = Column(Text)
    created_at = Column(DateTime, default=func.now())
    meta_data = Column(JSONB)

    # Relationships
    job = relationship("GenerationJob", back_populates="agent_logs")

    __table_args__ = (
        Index("idx_agent_logs_job_id", "job_id"),
        Index("idx_agent_logs_created_at", "created_at"),
        Index("idx_agent_logs_success", "success"),
    )

    def __repr__(self):
        return f"<AgentExecutionLog(id={self.id}, agent_name={self.agent_name}, success={self.success})>"
