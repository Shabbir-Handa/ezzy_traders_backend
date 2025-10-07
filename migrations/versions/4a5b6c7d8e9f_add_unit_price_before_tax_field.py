"""add unit_price_before_tax field to quotation_item

Revision ID: 4a5b6c7d8e9f
Revises: 3151473b9ea3
Create Date: 2025-10-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a5b6c7d8e9f'
down_revision: Union[str, Sequence[str], None] = '3151473b9ea3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unit_price_before_tax field (price after discount, before tax)
    op.add_column('quotation_item', sa.Column('unit_price_before_tax', sa.Numeric(precision=10, scale=2), nullable=False, server_default=sa.text('0')))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('quotation_item', 'unit_price_before_tax')

