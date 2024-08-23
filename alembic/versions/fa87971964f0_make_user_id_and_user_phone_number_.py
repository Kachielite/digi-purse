"""make user_id and user_phone_number unique

Revision ID: fa87971964f0
Revises: 65741c6ba52a
Create Date: 2024-08-23 10:00:56.384253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fa87971964f0'
down_revision: Union[str, None] = '65741c6ba52a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique constraints to user_id and user_phone_number
    op.create_unique_constraint('uq_wallet_user_id', 'wallet', ['user_id'])
    op.create_unique_constraint('uq_wallet_user_phone_number', 'wallet', ['user_phone_number'])


def downgrade() -> None:
    # Drop the unique constraints
    op.drop_constraint('uq_wallet_user_id', 'wallet', type_='unique')
    op.drop_constraint('uq_wallet_user_phone_number', 'wallet', type_='unique')
