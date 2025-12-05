"""Add prospect_data_jobs table for async prospect data generation

Revision ID: 001_prospect_data_jobs
Revises:
Create Date: 2025-01-02 07:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_prospect_data_jobs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create prospect_data_jobs table for tracking async data generation."""

    # Create prospect_data_jobs table
    op.create_table(
        'prospect_data_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('prospect_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('regenerate', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('status', sa.String(50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('celery_task_id', sa.String(255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('generation_duration_ms', sa.Integer(), nullable=True),
        sa.Column('result_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        # Constraints
        sa.ForeignKeyConstraint(['prospect_id'], ['prospects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['dashboard_templates.id'], ondelete='SET NULL'),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled')",
            name='chk_prospect_data_job_status'
        ),
        sa.UniqueConstraint('celery_task_id', name='uq_prospect_data_jobs_celery_task_id')
    )

    # Create indexes
    op.create_index(
        'idx_prospect_data_jobs_prospect_id',
        'prospect_data_jobs',
        ['prospect_id']
    )
    op.create_index(
        'idx_prospect_data_jobs_status',
        'prospect_data_jobs',
        ['status']
    )
    op.create_index(
        'idx_prospect_data_jobs_celery_task_id',
        'prospect_data_jobs',
        ['celery_task_id']
    )
    op.create_index(
        'idx_prospect_data_jobs_created_at',
        'prospect_data_jobs',
        ['created_at']
    )


def downgrade() -> None:
    """Drop prospect_data_jobs table."""

    # Drop indexes first
    op.drop_index('idx_prospect_data_jobs_created_at', table_name='prospect_data_jobs')
    op.drop_index('idx_prospect_data_jobs_celery_task_id', table_name='prospect_data_jobs')
    op.drop_index('idx_prospect_data_jobs_status', table_name='prospect_data_jobs')
    op.drop_index('idx_prospect_data_jobs_prospect_id', table_name='prospect_data_jobs')

    # Drop table
    op.drop_table('prospect_data_jobs')
