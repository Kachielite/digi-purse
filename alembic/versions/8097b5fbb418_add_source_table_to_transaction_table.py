"""Add source column to transaction table

Revision ID: 8097b5fbb418
Revises: 25c6554839ee
Create Date: 2024-08-28 06:01:36.350753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8097b5fbb418'
down_revision: Union[str, None] = '25c6554839ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add source column
    op.add_column('transaction', sa.Column('source', sa.String(), nullable=False))


def downgrade():
    # Remove source column
    op.drop_column('transaction', 'source')
