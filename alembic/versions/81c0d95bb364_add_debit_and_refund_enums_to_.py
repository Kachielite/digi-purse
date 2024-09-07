"""add debit and refund enums to transaction table

Revision ID: 81c0d95bb364
Revises: 831738979dea
Create Date: 2024-09-06 00:04:34.802242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81c0d95bb364'
down_revision: Union[str, None] = '831738979dea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add the new enum values to the existing type
    op.execute("ALTER TYPE transaction_type ADD VALUE 'debit'")
    op.execute("ALTER TYPE transaction_type ADD VALUE 'refund'")

    # Step 2: Alter the column to use the updated enum type
    op.alter_column(
        'transaction',
        'type',
        existing_type=sa.Enum('credit', 'balance', 'debit', 'refund', name='transaction_type'),
        type_=sa.Enum('credit', 'balance', 'debit', 'refund', name='transaction_type'),
        existing_nullable=False
    )


def downgrade() -> None:
    pass
