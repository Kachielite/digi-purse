"""rename phone_number column to user_phone_number and make it a foreign key

Revision ID: 65741c6ba52a
Revises: 5c43f104e6fc
Create Date: 2024-08-23 07:51:34.169374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65741c6ba52a'
down_revision: Union[str, None] = '5c43f104e6fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Rename the column from phone_number to user_phone_number
    op.alter_column('wallet', 'phone_number', new_column_name='user_phone_number')

    # Step 2: Add the foreign key constraint
    op.create_foreign_key(
        'fk_wallet_user_phone_number_users',  # Constraint name
        'wallet',                             # Source table
        'users',                              # Referenced table
        ['user_phone_number'],                # Source column(s)
        ['phone_number'],                     # Referenced column(s)
    )


def downgrade() -> None:
    # Drop the foreign key first
    op.drop_constraint('fk_wallet_user_phone_number_users', 'wallet', type_='foreignkey')

    # Rename the column back to phone_number
    op.alter_column('wallet', 'user_phone_number', new_column_name='phone_number')
