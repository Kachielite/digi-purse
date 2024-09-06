"""add transaction pin to user table

Revision ID: 831738979dea
Revises: 8097b5fbb418
Create Date: 2024-09-05 21:19:09.969705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '831738979dea'
down_revision: Union[str, None] = '8097b5fbb418'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('transaction_pin', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'transaction_pin')
