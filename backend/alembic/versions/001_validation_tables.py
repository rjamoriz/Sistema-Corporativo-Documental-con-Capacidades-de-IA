"""
Migración: Crear tablas para validación de terceros

Revision ID: 001_validation_tables
Revises: 
Create Date: 2025-10-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_validation_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Crear tablas de validación."""
    
    # Tabla: sanctions_list
    op.create_table(
        'sanctions_list',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('entity_name', sa.String(length=500), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('list_id', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('program', sa.String(length=200), nullable=True),
        sa.Column('addresses', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('list_id')
    )
    op.create_index('ix_sanctions_list_id', 'sanctions_list', ['id'])
    op.create_index('ix_sanctions_list_source', 'sanctions_list', ['source'])
    op.create_index('ix_sanctions_list_entity_name', 'sanctions_list', ['entity_name'])

    # Tabla: validation_history
    op.create_table(
        'validation_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('entities_validated', sa.Integer(), nullable=True),
        sa.Column('entities_flagged', sa.Integer(), nullable=True),
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.Column('validated_by', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE')
    )
    op.create_index('ix_validation_history_id', 'validation_history', ['id'])
    op.create_index('ix_validation_history_document_id', 'validation_history', ['document_id'])
    op.create_index('ix_validation_history_validated_at', 'validation_history', ['validated_at'])

    # Tabla: validation_results
    op.create_table(
        'validation_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_name', sa.String(length=500), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('is_sanctioned', sa.Boolean(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('matches_count', sa.Integer(), nullable=True),
        sa.Column('sources_checked', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('match_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('checked_at', sa.DateTime(), nullable=True),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ondelete='CASCADE')
    )
    op.create_index('ix_validation_results_id', 'validation_results', ['id'])
    op.create_index('ix_validation_results_entity_name', 'validation_results', ['entity_name'])
    op.create_index('ix_validation_results_is_sanctioned', 'validation_results', ['is_sanctioned'])
    op.create_index('ix_validation_results_checked_at', 'validation_results', ['checked_at'])
    op.create_index('ix_validation_results_document_id', 'validation_results', ['document_id'])
    op.create_index('ix_validation_results_entity_id', 'validation_results', ['entity_id'])


def downgrade():
    """Eliminar tablas de validación."""
    op.drop_index('ix_validation_results_entity_id', table_name='validation_results')
    op.drop_index('ix_validation_results_document_id', table_name='validation_results')
    op.drop_index('ix_validation_results_checked_at', table_name='validation_results')
    op.drop_index('ix_validation_results_is_sanctioned', table_name='validation_results')
    op.drop_index('ix_validation_results_entity_name', table_name='validation_results')
    op.drop_index('ix_validation_results_id', table_name='validation_results')
    op.drop_table('validation_results')

    op.drop_index('ix_validation_history_validated_at', table_name='validation_history')
    op.drop_index('ix_validation_history_document_id', table_name='validation_history')
    op.drop_index('ix_validation_history_id', table_name='validation_history')
    op.drop_table('validation_history')

    op.drop_index('ix_sanctions_list_entity_name', table_name='sanctions_list')
    op.drop_index('ix_sanctions_list_source', table_name='sanctions_list')
    op.drop_index('ix_sanctions_list_id', table_name='sanctions_list')
    op.drop_table('sanctions_list')
