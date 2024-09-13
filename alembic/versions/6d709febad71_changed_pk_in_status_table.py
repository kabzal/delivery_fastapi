"""changed PK in status table

Revision ID: 6d709febad71
Revises: 5e937253a163
Create Date: 2024-09-12 18:06:04.969986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d709febad71'
down_revision: Union[str, None] = '5e937253a163'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_delivery_status_current_id', table_name='delivery_status_current')
    op.create_index(op.f('ix_delivery_status_current_internal_id'), 'delivery_status_current', ['internal_id'], unique=False)
    op.drop_column('delivery_status_current', 'id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('delivery_status_current', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.drop_index(op.f('ix_delivery_status_current_internal_id'), table_name='delivery_status_current')
    op.create_index('ix_delivery_status_current_id', 'delivery_status_current', ['id'], unique=False)
    # ### end Alembic commands ###
