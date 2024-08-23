"""Add is_blocked, phone_number, is_deleted columns to wallet table

Revision ID: 5c43f104e6fc
Revises: 
Create Date: 2024-08-23 07:35:21.065754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c43f104e6fc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('wallet', sa.Column('is_blocked', sa.Boolean(), nullable=False, default=False))
    op.add_column('wallet', sa.Column('phone_number', sa.String(), nullable=False, unique=True))
    op.add_column('wallet', sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False))


def downgrade() -> None:
    pass
