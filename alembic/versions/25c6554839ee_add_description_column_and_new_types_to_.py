"""Add description column and new types to Transaction table

Revision ID: 25c6554839ee
Revises: fa87971964f0
Create Date: 2024-08-28 05:33:49.574550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '25c6554839ee'
down_revision: Union[str, None] = 'fa87971964f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add description column
    op.add_column('transaction', sa.Column('description', sa.String(), nullable=True))

    # Update the type column to include new types
    op.alter_column(
        'transaction',
        'type',
        existing_type=sa.Enum('credit', 'balance', name='transaction_type'),
        type_=sa.Enum('credit', 'balance', 'debit', 'refund', name='transaction_type'),
        existing_nullable=False
    )


def downgrade():
    # Remove description column
    op.drop_column('transaction', 'description')

    # Revert the type column to original types
    op.alter_column(
        'transaction',
        'type',
        existing_type=sa.Enum('credit', 'balance', 'debit', 'refund', name='transaction_type'),
        type_=sa.Enum('credit', 'balance', name='transaction_type'),
        existing_nullable=False
    )
